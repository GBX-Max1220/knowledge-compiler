#!/usr/bin/env python3
"""
Knowledge Compiler — Batch Process

Orchestrates the full pipeline for one book:
  manifest → chunks → extraction → object generation → decompose → registry → validate

Usage:
    python scripts/batch_process.py --book acsm12
    python scripts/batch_process.py --book acsm12 --resume
    python scripts/batch_process.py --book acsm12 --force
    python scripts/batch_process.py --book acsm12 --section 01_02

Pipeline stages:
  0. pending         — chunk exists, ready for extraction
  1. extracted       — extraction file written
  2. generated       — normalized YAML written
  3. decomposed      — objects split into per-ID files, registry updated
  4. validated       — all checks passed
  5. completed       — fully processed
"""

import argparse
import hashlib
import json
import os
import sys
import yaml
from datetime import datetime
from pathlib import Path


# ─── Configuration ───────────────────────────────────────────────────

STAGES = ["pending", "extracted", "generated", "decomposed", "validated", "completed"]

SCHEMA_TYPES = {
    "Concept": ["definition"],
    "Threshold": ["metric", "range"],
    "TableRow": ["table_ref", "fields"],
    "Procedure": ["goal", "steps"],
    "Recommendation": ["population", "dosage"],
    "Warning": ["condition", "action"],
    "Contraindication": ["condition", "category"],
    "Formula": ["canonical_form"],
}


# ─── Helpers ─────────────────────────────────────────────────────────

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def dump_yaml(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level:5s}] {msg}")


def sec_to_file_id(sec_id):
    """Convert '1.2' to '01_02'."""
    parts = str(sec_id).split(".")
    return f"{int(parts[0]):02d}_{int(parts[1]):02d}"


# ─── Status Tracking ─────────────────────────────────────────────────

def get_section_status(manifest, section_id):
    """Read the current status of a section from manifest."""
    for ch in manifest.get("chapters", []):
        for sec in ch.get("sections", []):
            if sec.get("id") == section_id:
                return sec.get("status", "pending")
    return None


def set_section_status(manifest_path, section_id, new_status):
    """Update a section's status in manifest.yaml."""
    with open(manifest_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Simple line-based replacement: find the section and update status
    # We match: "id: \"{section_id}\"" then find the next "status:" and replace
    lines = text.split("\n")
    in_target = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped == f'id: "{section_id}"':
            in_target = True
        if in_target and stripped.startswith("status:"):
            indent = len(line) - len(line.lstrip())
            new_lines.append(f"{' ' * indent}status: {new_status}")
            in_target = False
            continue
        new_lines.append(line)

    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))


# ─── Pipeline Stages ────────────────────────────────────────────────

def stage_extract(book_dir, manifest, section_id, file_id):
    """
    Stage 1: Prepare extraction.
    Extraction itself requires an AI call (via prompt 02).
    This stage marks the section as ready and prepares the extraction stub.
    
    Returns True if the extraction file already exists (user/AI has done it).
    """
    extraction_file = os.path.join(book_dir, "extraction", f"{file_id}.yaml")
    if os.path.exists(extraction_file):
        with open(extraction_file, "r") as f:
            content = f.read().strip()
        if content:
            log(f"  Extraction exists: {section_id} ({file_id})", "DONE")
            return True
    
    log(f"  Extraction needed: {section_id} — run prompt 02_extract.md on {file_id}", "WAIT")
    return False


def stage_generate(book_dir, manifest, section_id, file_id):
    """
    Stage 2: Generate normalized YAML from extraction.
    Requires an AI call (via prompt 03_object_generate.md).
    """
    normalized_file = os.path.join(book_dir, "normalized", f"{file_id}.yaml")
    if os.path.exists(normalized_file):
        with open(normalized_file, "r") as f:
            content = f.read().strip()
        if content:
            docs = list(yaml.safe_load_all(content))
            real_docs = [d for d in docs if d is not None]
            if real_docs:
                log(f"  Generated: {section_id} ({len(real_docs)} objects)", "DONE")
                return True
    
    log(f"  Generation needed: {section_id} — run prompt 03_object_generate.md on {file_id}", "WAIT")
    return False


def stage_decompose(book_dir, manifest, section_id, file_id):
    """
    Stage 3: Decompose normalized YAML into per-object files.
    This is mechanical — no AI needed.
    """
    normalized_file = os.path.join(book_dir, "normalized", f"{file_id}.yaml")
    objects_dir = os.path.join(book_dir, "objects")
    registry_file = os.path.join(book_dir, "registry.yaml")
    
    if not os.path.exists(normalized_file):
        log(f"  Cannot decompose: {section_id} — normalized file missing", "ERROR")
        return False
    
    with open(normalized_file, "r") as f:
        content = f.read().strip()
    
    docs = list(yaml.safe_load_all(content))
    real_docs = [d for d in docs if d is not None]
    
    if not real_docs:
        log(f"  No objects to decompose in {section_id}", "WARN")
        return True
    
    count = 0
    new_registry = {}
    
    for doc in real_docs:
        obj_id = doc.get("id")
        obj_type = doc.get("type")
        canonical_name = doc.get("canonical_name")
        
        if not obj_id or not obj_type:
            log(f"  Skipping doc with missing id/type in {section_id}", "WARN")
            continue
        
        type_dir = os.path.join(objects_dir, obj_type)
        os.makedirs(type_dir, exist_ok=True)
        
        obj_path = os.path.join(type_dir, f"{obj_id}.yaml")
        dump_yaml(obj_path, doc)
        count += 1
        
        if canonical_name:
            new_registry[canonical_name] = obj_id
    
    # Update registry
    registry = {}
    if os.path.exists(registry_file):
        existing = load_yaml(registry_file) or {}
        registry = existing.get("registry", {})
    
    changed = False
    for name, oid in new_registry.items():
        if name not in registry:
            registry[name] = oid
            changed = True
        elif registry[name] != oid:
            log(f"  Registry conflict: '{name}' → {registry[name]} vs {oid}", "WARN")
    
    if changed:
        dump_yaml(registry_file, {"registry": dict(sorted(registry.items()))})
        log(f"  Registry updated ({len(new_registry)} entries from {section_id})", "DONE")
    
    log(f"  Decomposed: {section_id} → {count} objects", "DONE")
    return True


def stage_validate_section(book_dir, manifest, section_id):
    """
    Stage 4: Validate one section's objects.
    Returns (pass_count, fail_count, errors).
    """
    objects_dir = os.path.join(book_dir, "objects")
    errors = []
    section_objects = []
    
    # Find objects belonging to this section by checking source.section
    for root, dirs, files in os.walk(objects_dir):
        for f in files:
            if not f.endswith(".yaml") or f == "index.yaml" or f == "registry.yaml":
                continue
            path = os.path.join(root, f)
            try:
                with open(path) as fh:
                    doc = yaml.safe_load(fh)
                if doc and doc.get("source", {}).get("section") == section_id:
                    section_objects.append((path, doc))
            except yaml.YAMLError as e:
                errors.append(f"YAML parse error: {f} — {e}")
    
    for path, doc in section_objects:
        obj_id = doc.get("id", "?")
        obj_type = doc.get("type")
        
        # Layer 1: Syntax (already parsed if we're here)
        
        # Layer 2: Schema
        required = SCHEMA_TYPES.get(obj_type, [])
        for field in required:
            if not doc.get(field):
                errors.append(f"{obj_id}: missing required field '{field}' for type {obj_type}")
        
        # Layer 3: Ontology — relationship targets exist
        for rel in (doc.get("relationships") or []):
            target = rel.get("target", "")
            if not target:
                continue
            target_type_part = target.split(".")[0].capitalize()
            target_dir = os.path.join(objects_dir, target_type_part)
            target_path = os.path.join(target_dir, f"{target}.yaml")
            if not os.path.exists(target_path):
                errors.append(f"{obj_id}.{rel.get('predicate')} → {target}: target not found")
        
        # Layer 4: Source completeness
        src = doc.get("source", {})
        for field in ["chapter", "section", "book_page"]:
            if not src.get(field):
                errors.append(f"{obj_id}: missing source.{field}")
        
        # Layer 5: Semantic — empty critical fields
        if obj_type == "Concept" and not doc.get("definition"):
            errors.append(f"{obj_id}: Concept with empty definition")
        if obj_type == "Threshold" and not doc.get("metric"):
            errors.append(f"{obj_id}: Threshold with no metric")
        if obj_type == "Procedure" and not doc.get("steps"):
            errors.append(f"{obj_id}: Procedure with no steps")
    
    pass_count = len(section_objects)
    fail_count = len(errors)
    return pass_count, fail_count, errors


def stage_complete(book_dir, manifest_path, section_id):
    """Stage 5: Mark section as completed."""
    set_section_status(manifest_path, section_id, "completed")
    log(f"  Completed: {section_id}", "DONE")


# ─── Orchestrator ───────────────────────────────────────────────────

def process_section(book_dir, manifest_path, manifest, section_id, file_id, stages, force=False):
    """Run the requested stages for one section."""
    
    current_status = get_section_status(manifest, section_id)
    log(f"Section {section_id} ({file_id}) — status: {current_status}", "STAT")
    
    for stage in stages:
        if not force:
            stage_idx = STAGES.index(stage)
            status_idx = STAGES.index(current_status) if current_status in STAGES else -1
            if status_idx >= stage_idx:
                continue
        
        log(f"  Stage: {stage}")
        
        if stage == "extracted":
            ok = stage_extract(book_dir, manifest, section_id, file_id)
            if ok:
                set_section_status(manifest_path, section_id, "extracted")
        
        elif stage == "generated":
            ok = stage_generate(book_dir, manifest, section_id, file_id)
            if ok:
                set_section_status(manifest_path, section_id, "generated")
        
        elif stage == "decomposed":
            ok = stage_decompose(book_dir, manifest, section_id, file_id)
            if ok:
                set_section_status(manifest_path, section_id, "decomposed")
        
        elif stage == "validated":
            passed, failed, errors = stage_validate_section(book_dir, manifest, section_id)
            if errors:
                log(f"  Validation errors for {section_id}:", "FAIL")
                for e in errors:
                    log(f"    ✗ {e}", "FAIL")
            log(f"  Validation: {passed} objects, {failed} errors", "DONE")
            if not errors:
                set_section_status(manifest_path, section_id, "validated")
        
        elif stage == "completed":
            if current_status == "validated" or force:
                stage_complete(book_dir, manifest_path, section_id)


def determine_stages(start_from):
    """Given a starting stage, determine which stages to run."""
    if start_from == "pending":
        return STAGES[1:]  # extracted → generated → decomposed → validated → completed
    start_idx = STAGES.index(start_from) if start_from in STAGES else 0
    return STAGES[start_idx+1:]


def main():
    parser = argparse.ArgumentParser(description="Knowledge Compiler — Batch Process")
    parser.add_argument("--book", required=True, help="Book directory under books/")
    parser.add_argument("--section", help="Single section to process (e.g. 01_02)")
    parser.add_argument("--resume", action="store_true", help="Resume from last completed stage")
    parser.add_argument("--force", action="store_true", help="Re-run all stages regardless of status")
    parser.add_argument("--from-stage", choices=STAGES, default="pending",
                        help="Start from this stage (default: pending)")
    parser.add_argument("--stages", nargs="+", choices=STAGES[1:],
                        help="Specific stages to run")
    
    args = parser.parse_args()
    
    base_dir = os.getcwd()
    book_dir = os.path.join(base_dir, "sources", "books", args.book)
    if not os.path.exists(book_dir):
        book_dir = os.path.join(base_dir, "books", args.book)
    manifest_path = os.path.join(book_dir, "manifest.yaml")
    
    if not os.path.exists(manifest_path):
        log(f"Manifest not found: {manifest_path}", "ERROR")
        sys.exit(1)
    
    manifest = load_yaml(manifest_path)
    
    # Determine which stages to run
    if args.stages:
        stages = args.stages
    elif args.from_stage:
        stages = determine_stages(args.from_stage)
    else:
        stages = STAGES[1:]  # all
    
    log(f"Pipeline stages: {' → '.join(stages)}")
    
    # Collect sections
    sections = []
    for ch in manifest.get("chapters", []):
        for sec in ch.get("sections", []):
            sec_id = sec.get("id", "")
            if sec_id:
                # Convert "1.2" to "01_02" for file names
                parts = str(sec_id).split(".")
                file_id = f"{int(parts[0]):02d}_{int(parts[1]):02d}"
                sections.append((sec_id, file_id))
    
    if args.section:
        sections = [s for s in sections if s[1] == args.section]
        if not sections:
            log(f"Section not found: {args.section}", "ERROR")
            sys.exit(1)
    
    log(f"Total sections to process: {len(sections)}")
    
    # Check which stages need AI (will be flagged, not run automatically)
    ai_stages = {"extracted", "generated"}
    needs_ai = [s for s in stages if s in ai_stages]
    if needs_ai:
        log(f"NOTE: Stages {needs_ai} require an AI call (prompts/02_extract.md, prompts/03_object_generate.md)", "INFO")
        log(f"      batch_process.py will prepare inputs and check for outputs.", "INFO")
    
    for sec_id, file_id in sections:
        log(f"{'='*60}")
        process_section(book_dir, manifest_path, manifest, sec_id, file_id, stages, force=args.force)
    
    # Summary
    statuses = {}
    for sec_id, file_id in sections:
        s = get_section_status(manifest, sec_id) or "unknown"
        statuses[s] = statuses.get(s, 0) + 1
    
    log(f"{'='*60}")
    log(f"SUMMARY for {args.book}:")
    for s, n in sorted(statuses.items()):
        log(f"  {s:15s}: {n:4d}")
    log(f"  {'total':15s}: {len(sections):4d}")
    log("Done.")


if __name__ == "__main__":
    main()
