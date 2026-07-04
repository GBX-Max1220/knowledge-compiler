#!/usr/bin/env python3
"""
Decompose per-section normalized YAML into per-object files.

Reads:  books/{source}/normalized/{section_id}.yaml  (multiple YAML docs)
Writes: books/{source}/objects/{Type}/{id}.yaml       (one file per object)
Updates: books/{source}/registry.yaml                  (name → ID mapping)

Usage:
    python scripts/decompose_objects.py books/acsm12/normalized/01_02.yaml
    python scripts/decompose_objects.py books/acsm12/normalized/  (batch)
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import yaml
import re
from pathlib import Path


def decompose_file(normalized_path, base_dir):
    """Split a single normalized YAML file into per-object files."""
    
    # Determine source from path
    rel_path = os.path.relpath(normalized_path, base_dir)
    parts = rel_path.replace("\\", "/").split("/")
    # e.g. books/acsm12/normalized/01_02.yaml
    if len(parts) < 3:
        print(f"  WARNING: cannot determine source from {rel_path}")
        return 0, []
    
    source = parts[1]
    section_id = Path(parts[-1]).stem  # e.g. "01_02"
    
    objects_dir = os.path.join(base_dir, "sources", "books", source, "objects")
    registry_path = os.path.join(base_dir, "sources", "books", source, "registry.yaml")
    
    # Read normalized file
    with open(normalized_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Parse YAML documents separated by "---"
    # yaml.safe_load_all handles this
    docs = list(yaml.safe_load_all(content))
    
    count = 0
    new_registry_entries = {}
    
    for doc in docs:
        if doc is None:
            continue
        
        # Normalize null list fields to empty lists
        list_fields = ["attributes", "purpose", "related_concepts", "aliases", "signs", "steps", "inputs", "outputs", "exceptions", "children"]
        for f in list_fields:
            if f in doc and doc[f] is None:
                doc[f] = []
        
        obj_id = doc.get("id")
        obj_type = doc.get("type")
        canonical_name = doc.get("canonical_name")
        
        if not obj_id or not obj_type:
            print(f"  WARNING: skipping doc with missing id/type in {section_id}")
            continue
        
        # Determine type directory
        type_dir = os.path.join(objects_dir, obj_type)
        os.makedirs(type_dir, exist_ok=True)
        
        # Write object file
        obj_path = os.path.join(type_dir, f"{obj_id}.yaml")
        with open(obj_path, "w", encoding="utf-8") as f:
            yaml.dump(doc, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"  ✓ {obj_type}/{obj_id}.yaml")
        count += 1
        
        # Register canonical name
        if canonical_name:
            new_registry_entries[canonical_name] = obj_id
    
    # Update registry
    registry = {}
    if os.path.exists(registry_path):
        with open(registry_path, "r", encoding="utf-8") as f:
            existing = yaml.safe_load(f) or {}
            registry = existing.get("registry", {})
    
    # Merge new entries (existing entries keep their first mapping)
    changed = False
    for name, oid in new_registry_entries.items():
        if name not in registry:
            registry[name] = oid
            changed = True
        elif registry[name] != oid:
            print(f"  ⚠ CONFLICT: '{name}' already mapped to {registry[name]}, skipping {oid}")
    
    if changed:
        with open(registry_path, "w", encoding="utf-8") as f:
            yaml.dump({"registry": dict(sorted(registry.items()))}, f,
                      default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"  ✓ registry.yaml updated ({len(new_registry_entries)} new entries)")
    
    return count, list(new_registry_entries.keys())


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/decompose_objects.py <normalized_path> [base_dir]")
        sys.exit(1)
    
    norm_path = sys.argv[1]
    base_dir = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
    
    if os.path.isdir(norm_path):
        # Batch mode: process all .yaml files in directory
        yaml_files = sorted([f for f in os.listdir(norm_path) if f.endswith(".yaml")])
        if not yaml_files:
            print(f"No .yaml files found in {norm_path}")
            sys.exit(0)
        
        total = 0
        all_entries = []
        for f in yaml_files:
            fpath = os.path.join(norm_path, f)
            print(f"\n--- {f} ---")
            c, entries = decompose_file(fpath, base_dir)
            total += c
            all_entries.extend(entries)
        
        print(f"\nDone. {total} objects written, {len(set(all_entries))} registry entries added.")
    
    elif os.path.isfile(norm_path):
        c, entries = decompose_file(norm_path, base_dir)
        print(f"\nDone. {c} objects written, {len(entries)} registry entries added.")
    
    else:
        print(f"Path not found: {norm_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
