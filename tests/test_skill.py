"""Tests for knowledge_compiler/skill.py — registry loading and object lookup."""
import pytest
import os
import sys
import yaml
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from knowledge_compiler import Skill, UnknownObjectError


@pytest.fixture
def book_dir():
    """Create a minimal book directory with registry and objects."""
    tmpdir = tempfile.mkdtemp()

    # Registry
    registry = {
        "registry": {
            "Test Concept": "concept.test",
            "Threshold Value": "threshold.test_value",
        }
    }
    with open(os.path.join(tmpdir, "registry.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(registry, f)

    # Objects
    concept_dir = os.path.join(tmpdir, "objects", "Concept")
    threshold_dir = os.path.join(tmpdir, "objects", "Threshold")
    os.makedirs(concept_dir)
    os.makedirs(threshold_dir)

    concept_obj = {
        "id": "concept.test",
        "type": "Concept",
        "canonical_name": "Test Concept",
        "semantic_type": "Entity",
        "source": {"book": "Test", "edition": 1, "chapter": 1, "section": "1.0", "book_page": 1},
        "definition": "A test concept.",
    }
    with open(os.path.join(concept_dir, "concept.test.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(concept_obj, f)

    threshold_obj = {
        "id": "threshold.test_value",
        "type": "Threshold",
        "canonical_name": "Threshold Value",
        "semantic_type": "Range",
        "source": {"book": "Test", "edition": 1, "chapter": 1, "section": "1.0", "book_page": 1},
        "range": "0-100",
        "metric": "Test",
        "numerical_value": 50,
    }
    with open(os.path.join(threshold_dir, "threshold.test_value.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(threshold_obj, f)

    yield tmpdir

    import shutil
    shutil.rmtree(tmpdir)


class TestSkill:
    """Tests for the Skill API."""

    def test_load_registry(self, book_dir):
        """Skill loads registry on init."""
        skill = Skill(book_dir)
        assert len(skill.registry) == 2
        assert skill.registry["Test Concept"] == "concept.test"

    def test_get_by_id(self, book_dir):
        """get() with object ID returns the correct object."""
        skill = Skill(book_dir)
        obj = skill.get("concept.test")
        assert obj["canonical_name"] == "Test Concept"
        assert obj["type"] == "Concept"

    def test_get_by_canonical_name(self, book_dir):
        """get() with canonical name resolves via registry."""
        skill = Skill(book_dir)
        obj = skill.get("Test Concept")
        assert obj["id"] == "concept.test"

    def test_get_by_name_case(self, book_dir):
        """get() with canonical name works regardless of case difference."""
        skill = Skill(book_dir)
        obj = skill.get("Test Concept")
        assert obj["id"] == "concept.test"

    def test_get_threshold(self, book_dir):
        """Threshold objects load with type-specific fields."""
        skill = Skill(book_dir)
        obj = skill.get("threshold.test_value")
        assert obj["range"] == "0-100"
        assert obj["numerical_value"] == 50

    def test_get_unknown_id_raises(self, book_dir):
        """get() with unknown ID raises UnknownObjectError."""
        skill = Skill(book_dir)
        with pytest.raises(UnknownObjectError):
            skill.get("nonexistent.object")

    def test_resolve(self, book_dir):
        """resolve() returns the correct object ID."""
        skill = Skill(book_dir)
        assert skill.resolve("Test Concept") == "concept.test"
        assert skill.resolve("Nonexistent") is None

    def test_list_objects(self, book_dir):
        """list_objects() returns all (id, type) pairs."""
        skill = Skill(book_dir)
        objects = skill.list_objects()
        assert len(objects) == 2
        ids = [o[0] for o in objects]
        assert "concept.test" in ids
        assert "threshold.test_value" in ids

    def test_list_types(self, book_dir):
        """list_types() returns counts by type."""
        skill = Skill(book_dir)
        types = skill.list_types()
        assert types.get("Concept") == 1
        assert types.get("Threshold") == 1
