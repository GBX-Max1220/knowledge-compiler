"""Tests for decompose_objects.py — fixture-based normalized YAML input and output verification."""
import pytest
import os
import sys
import yaml
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def normalized_file():
    """Create a temp book structure: books/testbook/normalized/section.yaml + sources/books/testbook/objects/
    
    The decompose function expects paths like books/{source}/normalized/{section}.yaml
    relative to base_dir (which is the temp root).
    """
    tmpdir = tempfile.mkdtemp()
    norm_dir = os.path.join(tmpdir, "books", "testbook", "normalized")
    os.makedirs(norm_dir)

    # Also create sources path for output (decompose writes to sources/books/{source}/objects/)
    sources_obj = os.path.join(tmpdir, "sources", "books", "testbook", "objects")
    os.makedirs(sources_obj)

    docs = [
        {
            "id": "concept.test_a",
            "type": "Concept",
            "canonical_name": "Test Concept A",
            "semantic_type": "Entity",
            "source": {"book": "Test", "edition": 1, "chapter": 1, "section": "1.0", "book_page": 1},
            "definition": "First test concept.",
            "relationships": [],
        },
        {
            "id": "concept.test_b",
            "type": "Concept",
            "canonical_name": "Test Concept B",
            "semantic_type": "Entity",
            "source": {"book": "Test", "edition": 1, "chapter": 1, "section": "1.0", "book_page": 1},
            "definition": "Second test concept.",
            "relationships": [{"predicate": "is_a", "target": "concept.test_a"}],
        },
    ]
    norm_path = os.path.join(norm_dir, "01_01.yaml")
    with open(norm_path, "w", encoding="utf-8") as f:
        yaml.dump_all(docs, f)

    yield tmpdir, norm_path

    import shutil
    shutil.rmtree(tmpdir)


class TestDecompose:
    """Tests for the decompose pipeline stage."""

    def test_decompose_creates_files(self, normalized_file):
        """Decompose should create one YAML file per object."""
        tmpdir, norm_path = normalized_file

        from scripts.decompose_objects import decompose_file
        count, entries = decompose_file(norm_path, tmpdir)

        assert count == 2, f"Expected 2 objects, got {count}"

        # Check files exist in sources/books/testbook/objects/
        expected_files = [
            os.path.join(tmpdir, "sources", "books", "testbook", "objects", "Concept", "concept.test_a.yaml"),
            os.path.join(tmpdir, "sources", "books", "testbook", "objects", "Concept", "concept.test_b.yaml"),
        ]
        for fpath in expected_files:
            assert os.path.exists(fpath), f"Expected file not found: {fpath}"

    def test_decompose_preserves_content(self, normalized_file):
        """Decompose should preserve all fields from the normalized YAML."""
        tmpdir, norm_path = normalized_file

        from scripts.decompose_objects import decompose_file
        decompose_file(norm_path, tmpdir)

        obj_path = os.path.join(tmpdir, "sources", "books", "testbook", "objects", "Concept", "concept.test_a.yaml")
        with open(obj_path, encoding="utf-8") as f:
            obj = yaml.safe_load(f)

        assert obj["canonical_name"] == "Test Concept A"
        assert obj["definition"] == "First test concept."

    def test_decompose_handles_relationships(self, normalized_file):
        """Decompose should preserve relationship data."""
        tmpdir, norm_path = normalized_file

        from scripts.decompose_objects import decompose_file
        decompose_file(norm_path, tmpdir)

        obj_path = os.path.join(tmpdir, "sources", "books", "testbook", "objects", "Concept", "concept.test_b.yaml")
        with open(obj_path, encoding="utf-8") as f:
            obj = yaml.safe_load(f)

        assert len(obj["relationships"]) == 1
        assert obj["relationships"][0]["predicate"] == "is_a"
        assert obj["relationships"][0]["target"] == "concept.test_a"

    def test_decompose_writes_registry(self, normalized_file):
        """Decompose should update or create a registry."""
        tmpdir, norm_path = normalized_file

        from scripts.decompose_objects import decompose_file
        decompose_file(norm_path, tmpdir)

        reg_path = os.path.join(tmpdir, "sources", "books", "testbook", "registry.yaml")
        assert os.path.exists(reg_path)

        with open(reg_path, encoding="utf-8") as f:
            reg = yaml.safe_load(f)

        assert reg["registry"]["Test Concept A"] == "concept.test_a"
        assert reg["registry"]["Test Concept B"] == "concept.test_b"
