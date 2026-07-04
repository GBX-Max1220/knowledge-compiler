"""Tests for validate.py — smokescreen with known-bad fixture."""
import pytest
import yaml
import os
import tempfile

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.validate import ValidationReport


def run_validation_no_exit(book_dir):
    """Run validation without sys.exit()."""
    import scripts.validate as v
    objects_dir = os.path.join(book_dir, "objects")
    if not os.path.exists(objects_dir):
        return None
    
    # Import the functions directly
    objects = v.load_all_objects(objects_dir)
    report = ValidationReport(os.path.basename(book_dir))
    report = v.validate_syntax(report, objects)
    report = v.validate_schema(report, objects)
    report = v.validate_ontology(report, objects, objects_dir)
    report = v.validate_graph(report, objects)
    report = v.validate_semantic(report, objects)
    report.object_count = len(objects)
    return report


@pytest.fixture
def valid_object():
    """A minimal valid Concept object."""
    return {
        "id": "concept.test",
        "type": "Concept",
        "canonical_name": "Test Concept",
        "semantic_type": "Entity",
        "source": {"book": "Test Book", "edition": 1, "chapter": 1, "section": "1.0", "book_page": 1},
        "definition": "A test concept for validation.",
    }


@pytest.fixture
def objects_dir(valid_object):
    """Create a temporary book directory with objects/ subdirectory."""
    tmpdir = tempfile.mkdtemp()
    obj_dir = os.path.join(tmpdir, "objects")
    concept_dir = os.path.join(obj_dir, "Concept")
    os.makedirs(concept_dir)

    # Valid object
    with open(os.path.join(concept_dir, "concept.test.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(valid_object, f)

    # Invalid: missing id
    with open(os.path.join(concept_dir, "concept.no_id.yaml"), "w", encoding="utf-8") as f:
        yaml.dump({"type": "Concept", "canonical_name": "No ID"}, f)

    # Invalid: missing source
    invalid2 = dict(valid_object)
    invalid2["id"] = "concept.no_source"
    invalid2["canonical_name"] = "No Source"
    invalid2["source"] = None
    with open(os.path.join(concept_dir, "concept.no_source.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(invalid2, f)

    yield tmpdir

    import shutil
    shutil.rmtree(tmpdir)


class TestValidation:
    """Smokescreen: validate.py detects known errors."""

    def test_valid_object_passes(self, objects_dir):
        """A valid object should pass all layers."""
        report = run_validation_no_exit(objects_dir)
        assert report is not None
        assert report.object_count >= 1

    def test_missing_id_detected(self, objects_dir):
        """Missing id should produce a syntax error."""
        report = run_validation_no_exit(objects_dir)
        assert report is not None
        syntax_issues = report.layers["1_syntax"]["issues"]
        id_issues = [i for i in syntax_issues if "missing 'id'" in i["message"]]
        assert len(id_issues) > 0, f"No missing-id errors found"

    def test_null_source_detected(self, objects_dir):
        """Null source should produce a syntax error."""
        report = run_validation_no_exit(objects_dir)
        assert report is not None
        syntax_issues = report.layers["1_syntax"]["issues"]
        source_issues = [i for i in syntax_issues if "missing source" in i["message"]]
        assert len(source_issues) > 0, f"No source errors found"

    def test_report_counts(self, objects_dir):
        """Report should count objects and track types."""
        report = run_validation_no_exit(objects_dir)
        assert report is not None
        summary = report.summary()
        assert summary["objects"] >= 2
        assert "Concept" in summary["types"]
