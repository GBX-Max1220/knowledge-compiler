#!/usr/bin/env python3
"""
Reasonix Runner — processes the task queue for v0.1.

Usage (from Reasonix CLI):
    python scripts/run_queue.py acsm12 extract    # Run all pending extractions
    python scripts/run_queue.py acsm12 generate   # Run all pending generations
    python scripts/run_queue.py acsm12 decompose  # Mechanical, no AI needed
    python scripts/run_queue.py acsm12 validate   # Validate all objects

Each command processes pending tasks sequentially, writing results to
the appropriate output directory.

Prerequisites:
    - books/acsm12/chunks/01_XX.md files exist (they do)
    - prompts/02_extract.md and prompts/03_object_generate.md are frozen (they are)
"""

import os
import sys
import yaml

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_prompt(stage):
    """Load the prompt file for a given stage."""
    prompt_map = {
        "extract": "02_extract.md",
        "generate": "03_object_generate.md",
    }
    prompt_file = prompt_map.get(stage)
    if not prompt_file:
        return ""
    
    path = os.path.join(BASE, "prompts", prompt_file)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def run_extract(book_dir, section_id, file_id, prompt_text):
    """Run extraction for one section."""
    chunk_path = os.path.join(book_dir, "chunks", f"{file_id}.md")
    output_path = os.path.join(book_dir, "extraction", f"{file_id}.yaml")
    
    if not os.path.exists(chunk_path):
        print(f"  SKIP {file_id}: chunk not found")
        return False
    
    with open(chunk_path, "r", encoding="utf-8") as f:
        chunk_text = f.read()
    
    # Print the full prompt + input for Reasonix to process
    print(f"=== EXTRACT {file_id} ===")
    print(f"PROMPT: {prompt_text}")
    print(f"INPUT: {chunk_text}")
    print(f"=== END {file_id} ===")
    print()
    print(f"Save the output to: {output_path}")
    print()
    
    return True  # Reasonix will save the output manually


def run_generate(book_dir, section_id, file_id, prompt_text):
    """Run generation for one section."""
    extraction_path = os.path.join(book_dir, "extraction", f"{file_id}.yaml")
    output_path = os.path.join(book_dir, "normalized", f"{file_id}.yaml")
    
    if not os.path.exists(extraction_path):
        print(f"  SKIP {file_id}: extraction not found")
        return False
    
    with open(extraction_path, "r", encoding="utf-8") as f:
        extraction_text = f.read()
    
    print(f"=== GENERATE {file_id} ===")
    print(f"PROMPT: {prompt_text}")
    print(f"INPUT: {extraction_text}")
    print(f"=== END {file_id} ===")
    print()
    print(f"Save the output to: {output_path}")
    print()
    
    return True


def run_decompose(book_dir):
    """Decompose all normalized files into objects."""
    from compiler.queue import TaskQueue
    queue = TaskQueue(book_dir)
    
    import glob
    norm_files = sorted(glob.glob(os.path.join(book_dir, "normalized", "*.yaml")))
    for f in norm_files:
        file_id = os.path.basename(f).replace(".yaml", "")
        sec_id = file_id.replace("_", ".")  # "01_02" → "01.02"
        print(f"Decomposing {file_id}...")
        
        # Call decompose script
        import subprocess
        result = subprocess.run(
            [sys.executable, os.path.join(BASE, "scripts", "decompose_objects.py"), f],
            capture_output=True, text=True, cwd=BASE,
        )
        if result.returncode == 0:
            queue.set_completed(sec_id, "decompose", f"decomposed from {file_id}")
        else:
            queue.set_failed(sec_id, "decompose", result.stderr[:200])
    
    print(f"Decompose complete. Run 'knowledge-compiler validate acsm12' to check.")


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/run_queue.py <book> <stage>")
        print("  stage: extract | generate | decompose | validate")
        sys.exit(1)
    
    book = sys.argv[1]
    stage = sys.argv[2]
    book_dir = os.path.join(BASE, "books", book)
    
    from compiler.queue import TaskQueue
    queue = TaskQueue(book_dir)
    
    if stage == "decompose":
        run_decompose(book_dir)
        return
    
    if stage == "validate":
        from scripts.validate import run_validation, print_report
        report = run_validation(book_dir)
        print_report(report)
        return
    
    prompt_text = load_prompt(stage)
    if not prompt_text:
        print(f"Unknown stage: {stage}")
        sys.exit(1)
    
    pending = queue.get_pending(stage)
    print(f"Processing {len(pending)} pending {stage} tasks...")
    
    for task in pending:
        sec_id = task["section"]
        file_id = task["file_id"]
        
        queue.set_running(sec_id, stage)
        
        if stage == "extract":
            ok = run_extract(book_dir, sec_id, file_id, prompt_text)
        elif stage == "generate":
            ok = run_generate(book_dir, sec_id, file_id, prompt_text)
        
        if ok:
            print(f"  → Output to books/{book}/{stage}/{file_id}.yaml")
    

if __name__ == "__main__":
    main()
