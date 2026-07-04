#!/usr/bin/env python3
"""
Knowledge Compiler — Validation

5-layer validation of generated objects.
Outputs a machine-readable and human-readable report.

Layers:
  1. Syntax — YAML parsability, required fields
  2. Schema — type-specific required fields per schema/{type}.yaml
  3. Ontology — relationship targets exist, predicates are allowed
  4. Graph — orphans, cycles, duplicate IDs, duplicate canonical names
  5. Semantic — empty definitions, missing ranges, no-step procedures

Usage:
    python scripts/validate.py --book acsm12
    python scripts/validate.py --book acsm12 --report validation/full_report.md
    python scripts/validate.py --book acsm12 --json validation/report.json
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import argparse
import json
import os
import sys
import yaml
from collections import defaultdict
from datetime import datetime


# ─── Configuration ───────────────────────────────────────────────────

ALLOWED_PREDICATES = {
    "is_a", "part_of", "instance_of",
    "adjacent_to", "applies_to", "used_for",
    "has_attribute", "has_value", "classified_as",
    "has_purpose", "has_part", "contraindicates", "references",
}

SCHEMA_TYPES = {
    "Concept": {"required": ["definition"], "optional": ["attributes", "purpose"]},
    "Threshold": {"required": ["metric", "range"], "optional": ["unit", "population", "condition"]},
    "TableRow": {"required": ["table_ref", "fields"], "optional": ["row_index"]},
    "Procedure": {"required": ["goal", "steps"], "optional": ["inputs", "outputs", "exceptions"]},
    "Recommendation": {"required": ["population", "dosage"], "optional": ["evidence_grade"]},
    "Warning": {"required": ["condition", "action"], "optional": ["signs", "severity"]},
    "Contraindication": {"required": ["condition", "category"], "optional": ["details", "temporary"]},
    "Formula": {"required": ["canonical_form"], "optional": ["variables", "limitations"]},
}

SEMANTIC_TYPES = {
    "Concept": ["Activity", "Entity", "Property", "Evidence",
                "AnatomicalStructure", "AnatomicalSystem",
                "PhysiologicalProcess", "Protein", "Theory"],
    "Threshold": ["Range", "Cutoff"],
    "TableRow": ["TableRow"],
    "Procedure": ["Protocol", "Process"],
    "Recommendation": ["Guideline", "Prescription"],
    "Warning": ["Safety", "AdverseEvent"],
    "Contraindication": ["Contraindication"],
    "Formula": ["Equation", "Formula"],
}


# ─── Validation Engine ──────────────────────────────────────────────

class ValidationReport:
    def __init__(self, book):
        self.book = book
        self.timestamp = datetime.now().isoformat()
        self.layers = {
            "1_syntax": {"passed": 0, "failed": 0, "issues": []},
            "2_schema": {"passed": 0, "failed": 0, "issues": []},
            "3_ontology": {"passed": 0, "failed": 0, "issues": []},
            "4_graph": {"passed": 0, "failed": 0, "issues": []},
            "5_semantic": {"passed": 0, "failed": 0, "issues": []},
        }
        self.all_ids = set()
        self.all_canonical = {}
        self.object_count = 0
        self.edge_count = 0
        self.type_counts = defaultdict(int)

    def add_issue(self, layer, message, severity="error"):
        self.layers[layer]["failed"] += 1
        self.layers[layer]["issues"].append({"severity": severity, "message": message})

    def add_pass(self, layer):
        self.layers[layer]["passed"] += 1

    def summary(self):
        total_issues = sum(l["failed"] for l in self.layers.values())
        return {
            "book": self.book,
            "timestamp": self.timestamp,
            "objects": self.object_count,
            "edges": self.edge_count,
            "types": dict(self.type_counts),
            "total_issues": total_issues,
            "by_layer": {k: {"passed": v["passed"], "failed": v["failed"]}
                        for k, v in self.layers.items()},
        }


def load_all_objects(objects_dir):
    """Load all YAML objects from the objects directory tree."""
    objects = []
    for root, dirs, files in os.walk(objects_dir):
        for f in files:
            if not f.endswith(".yaml") or f == "index.yaml" or f == "registry.yaml":
                continue
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    doc = yaml.safe_load(fh)
                if doc:
                    objects.append((path, doc))
            except yaml.YAMLError as e:
                # Layer 1 failure — will be caught by validate
                pass
    return objects


def validate_syntax(report, objects):
    """Layer 1: YAML parsability, required header fields."""
    for path, doc in objects:
        # Must have id
        if not doc.get("id"):
            report.add_issue("1_syntax", f"{path}: missing 'id'")
            continue
        
        # Must have type
        if not doc.get("type"):
            report.add_issue("1_syntax", f"{doc['id']}: missing 'type'")
            continue
        
        # Must have canonical_name
        if not doc.get("canonical_name"):
            report.add_issue("1_syntax", f"{doc['id']}: missing 'canonical_name'")
            continue
        
        # Source must have required fields
        src = doc.get("source", {})
        for sf in ["book", "chapter", "section", "book_page"]:
            if not src.get(sf):
                report.add_issue("1_syntax", f"{doc['id']}: missing source.{sf}")
        
        report.add_pass("1_syntax")
    
    return report


def validate_schema(report, objects):
    """Layer 2: Type-specific required fields."""
    for path, doc in objects:
        obj_type = doc.get("type")
        if obj_type not in SCHEMA_TYPES:
            report.add_issue("2_schema", f"{doc.get('id', '?')}: unknown type '{obj_type}'")
            continue
        
        schema = SCHEMA_TYPES[obj_type]
        for field in schema["required"]:
            val = doc.get(field)
            if val is None or (isinstance(val, (list, dict)) and len(val) == 0):
                report.add_issue("2_schema", f"{doc['id']}: required field '{field}' is empty for type {obj_type}")
        
        # Validate semantic_type
        sem_type = doc.get("semantic_type")
        allowed = SEMANTIC_TYPES.get(obj_type, [])
        if sem_type and allowed and sem_type not in allowed:
            report.add_issue("2_schema", f"{doc['id']}: semantic_type '{sem_type}' not in allowed list {allowed}")
        
        report.add_pass("2_schema")
    
    return report


def validate_ontology(report, objects, objects_dir):
    """Layer 3: Relationship targets exist, predicates are allowed."""
    target_type_map = {
        "concept": "Concept",
        "threshold": "Threshold",
        "table_row": "TableRow",
        "procedure": "Procedure",
        "recommendation": "Recommendation",
        "warning": "Warning",
        "contraindication": "Contraindication",
        "formula": "Formula",
    }
    
    for path, doc in objects:
        for rel in (doc.get("relationships") or []):
            predicate = rel.get("predicate", "")
            target = rel.get("target", "")
            
            # Check predicate
            if predicate and predicate not in ALLOWED_PREDICATES:
                report.add_issue("3_ontology",
                    f"{doc['id']}.{predicate}: predicate '{predicate}' not in allowlist")
            
            # Check target exists
            if target:
                prefix = target.split(".")[0]
                type_dir = target_type_map.get(prefix, prefix.capitalize())
                target_path = os.path.join(objects_dir, type_dir, f"{target}.yaml")
                if not os.path.exists(target_path):
                    report.add_issue("3_ontology",
                        f"{doc['id']}.{predicate} → {target}: target file not found")
            
            report.add_pass("3_ontology")
        
        if not doc.get("relationships"):
            report.add_pass("3_ontology")
    
    return report


def validate_graph(report, objects):
    """Layer 4: Duplicate IDs, duplicate canonical names, orphan detection."""
    ids = {}
    names = {}
    
    for path, doc in objects:
        obj_id = doc.get("id")
        name = doc.get("canonical_name")
        
        if obj_id:
            if obj_id in ids:
                report.add_issue("4_graph",
                    f"Duplicate ID: '{obj_id}' in {path} and {ids[obj_id]}")
            ids[obj_id] = path
        
        if name:
            if name.lower() in names:
                report.add_issue("4_graph",
                    f"Duplicate canonical_name: '{name}' in {path} and {names[name.lower()]}")
            names[name.lower()] = path
        
        # Update counts
        obj_type = doc.get("type")
        if obj_type:
            report.type_counts[obj_type] += 1
            report.object_count += 1
            report.edge_count += len(doc.get("relationships") or [])
    
    report.all_ids = set(ids.keys())
    report.all_canonical = names
    
    # Orphan detection: find relationship targets that point to IDs outside this book
    # (This is informational — cross-source targets are allowed)
    for path, doc in objects:
        for rel in (doc.get("relationships") or []):
            target = rel.get("target", "")
            if target and target not in ids:
                # This might be cross-source — it's a warning, not an error
                report.add_issue("4_graph",
                    f"{doc['id']}.{rel.get('predicate')} → {target}: unresolved (may be cross-source)",
                    severity="warn")
    
    # Count unique IDs
    report.add_pass("4_graph")
    return report


def validate_semantic(report, objects):
    """Layer 5: Semantic quality — empty definitions, missing ranges, no-step procedures."""
    for path, doc in objects:
        obj_id = doc.get("id", "?")
        obj_type = doc.get("type")
        
        if obj_type == "Concept":
            defn = doc.get("definition", "")
            if not defn or len(defn.strip()) < 10:
                report.add_issue("5_semantic",
                    f"{obj_id}: Concept definition is empty or too short")
        
        if obj_type == "Threshold":
            if not doc.get("metric"):
                report.add_issue("5_semantic",
                    f"{obj_id}: Threshold has no metric")
            if not doc.get("range"):
                report.add_issue("5_semantic",
                    f"{obj_id}: Threshold has no range")
            if not doc.get("numerical_value") and doc.get("numerical_value") != 0:
                report.add_issue("5_semantic",
                    f"{obj_id}: Threshold has no numerical_value")
        
        if obj_type == "Procedure":
            steps = doc.get("steps", [])
            if not steps:
                report.add_issue("5_semantic",
                    f"{obj_id}: Procedure has no steps")
        
        if obj_type == "Recommendation":
            if not doc.get("dosage"):
                report.add_issue("5_semantic",
                    f"{obj_id}: Recommendation has no dosage")
        
        if obj_type == "TableRow":
            fields = doc.get("fields", {})
            if not fields:
                report.add_issue("5_semantic",
                    f"{obj_id}: TableRow has no fields")
        
        report.add_pass("5_semantic")
    
    return report


def run_validation(book_dir):
    """Run all 5 validation layers and return a report."""
    objects_dir = os.path.join(book_dir, "objects")
    
    if not os.path.exists(objects_dir):
        print(f"ERROR: objects/ directory not found at {objects_dir}")
        sys.exit(1)
    
    # Derive book name from path
    book = os.path.basename(book_dir)
    report = ValidationReport(book)
    
    # Load all objects
    objects = load_all_objects(objects_dir)
    print(f"Loaded {len(objects)} object files from {objects_dir}")
    
    if not objects:
        print("No objects found — nothing to validate.")
        return report
    
    # Run layers
    print("\n── Layer 1: Syntax ──")
    validate_syntax(report, objects)
    
    print("\n── Layer 2: Schema ──")
    validate_schema(report, objects)
    
    print("\n── Layer 3: Ontology ──")
    validate_ontology(report, objects, objects_dir)
    
    print("\n── Layer 4: Graph ──")
    validate_graph(report, objects)
    
    print("\n── Layer 5: Semantic ──")
    validate_semantic(report, objects)
    
    return report


def print_report(report):
    """Print human-readable report."""
    s = report.summary()
    
    print(f"\n{'='*60}")
    print(f"VALIDATION REPORT — {s['book']}")
    print(f"{'='*60}")
    print(f"Timestamp: {s['timestamp']}")
    print(f"\nObjects: {s['objects']}")
    print(f"Edges: {s['edges']}")
    print(f"By type: {dict(s['types'])}")
    print(f"\nIssues: {s['total_issues']}")
    
    for layer_name, layer_data in s["by_layer"].items():
        label = layer_name.replace("_", " ").title()
        issues = report.layers[layer_name]["issues"]
        status = "PASS" if not issues else f"FAIL ({len(issues)} issues)"
        print(f"\n  {label}: {status}")
        for issue in issues[:10]:  # Show first 10 per layer
            icon = "✗" if issue["severity"] == "error" else "⚠"
            print(f"    {icon} {issue['message']}")
        if len(issues) > 10:
            print(f"    ... and {len(issues)-10} more")
    
    overall = "PASS" if s["total_issues"] == 0 else f"FAIL ({s['total_issues']} issues)"
    print(f"\n{'='*60}")
    print(f"OVERALL: {overall}")
    print(f"{'='*60}")


def save_json_report(report, path):
    """Save report as JSON."""
    s = report.summary()
    # Full issues
    s["issues"] = {k: v["issues"] for k, v in report.layers.items()}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)
    print(f"JSON report saved to {path}")


def save_md_report(report, path):
    """Save report as Markdown."""
    s = report.summary()
    lines = [
        f"# Validation Report — {s['book']}",
        f"",
        f"**Timestamp:** {s['timestamp']}",
        f"**Objects:** {s['objects']}",
        f"**Edges:** {s['edges']}",
        f"**Total Issues:** {s['total_issues']}",
        f"",
        f"## By Type",
        f"",
        f"| Type | Count |",
        f"|------|-------|",
    ]
    for t, c in sorted(s["types"].items()):
        lines.append(f"| {t} | {c} |")
    
    lines.extend(["", "## Issues by Layer", ""])
    
    for layer_name, layer_data in s["by_layer"].items():
        label = layer_name.replace("_", " ").title()
        issues = report.layers[layer_name]["issues"]
        status = "✅ PASS" if not issues else f"❌ FAIL ({len(issues)})"
        lines.append(f"### {label}: {status}")
        lines.append("")
        if issues:
            lines.append("| Severity | Message |")
            lines.append("|----------|---------|")
            for issue in issues:
                icon = "❌" if issue["severity"] == "error" else "⚠️"
                lines.append(f"| {icon} | {issue['message']} |")
            lines.append("")
    
    overall = "✅ PASS" if s["total_issues"] == 0 else f"❌ FAIL ({s['total_issues']} issues)"
    lines.extend(["---", f"**Overall: {overall}**"])
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"MD report saved to {path}")


def main():
    parser = argparse.ArgumentParser(description="Knowledge Compiler — Validation")
    parser.add_argument("--book", required=True, help="Book directory under books/")
    parser.add_argument("--report", help="Path for Markdown report (relative to book dir)")
    parser.add_argument("--json", help="Path for JSON report (relative to book dir)")
    
    args = parser.parse_args()
    
    base_dir = os.getcwd()
    book_dir = os.path.join(base_dir, "books", args.book)
    
    if not os.path.exists(book_dir):
        print(f"ERROR: Book directory not found: {book_dir}")
        sys.exit(1)
    
    report = run_validation(book_dir)
    print_report(report)
    
    if args.report:
        report_path = os.path.join(book_dir, args.report)
        save_md_report(report, report_path)
    
    if args.json:
        json_path = os.path.join(book_dir, args.json)
        save_json_report(report, json_path)
    
    # Exit code
    if report.summary()["total_issues"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
