#!/usr/bin/env python3
"""
Knowledge Compiler — CLI Entry Point

Usage:
    knowledge-compiler build acsm12          # Build full book (prompt mode)
    knowledge-compiler build acsm12 --auto   # Build with OpenAI API
    knowledge-compiler status acsm12         # Show queue status
    knowledge-compiler retry acsm12          # Retry failed tasks
    knowledge-compiler validate acsm12       # Run validation
    knowledge-compiler release acsm12 v0.1   # Tag a release
"""

import argparse
import os
import sys
import yaml

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler.queue import TaskQueue
from scripts.validate import run_validation, print_report


BASE_DIR = os.getcwd()


def load_book_config(book: str) -> dict:
    """Load book configuration from books/{book}/compiler.yaml or manifest.yaml."""
    manifest_path = os.path.join(BASE_DIR, "books", book, "manifest.yaml")
    if not os.path.exists(manifest_path):
        print(f"ERROR: Book not found at books/{book}/")
        sys.exit(1)
    
    with open(manifest_path) as f:
        return yaml.safe_load(f)


def get_sections(manifest: dict) -> list:
    """Extract (section_id, file_id) pairs from manifest."""
    sections = []
    for ch in manifest.get("chapters", []):
        for sec in ch.get("sections", []):
            sec_id = sec.get("id", "")
            if not sec_id:
                continue
            parts = str(sec_id).split(".")
            file_id = f"{int(parts[0]):02d}_{int(parts[1]):02d}"
            sections.append((sec_id, file_id))
    return sections


def cmd_build(args):
    """Build command: queue tasks and prepare for execution."""
    manifest = load_book_config(args.book)
    sections = get_sections(manifest)
    book_dir = os.path.join(BASE_DIR, "books", args.book)
    queue = TaskQueue(book_dir)

    if args.init:
        queue.init_all_sections(sections)
        print(f"Initialized queue for {len(sections)} sections.")
    
    if args.auto:
        print(f"Auto mode selected. Provider: {args.provider}")
        print("This requires a configured API provider and is not yet implemented.")
        print("For now, use prompt mode (default): run the .prompt files manually.")
    else:
        # Prompt mode: write .prompt files for manual Reasonix CLI execution
        from compiler.providers.reasonix import ReasonixProvider
        from compiler.providers import ProviderConfig
        
        queue.init_all_sections(sections)
        provider = ReasonixProvider(ProviderConfig(name="reasonix", model="deepseek-v4-flash"))
        
        prompt_dir = os.path.join(book_dir, ".prompts")
        provider.set_prompt_dir(prompt_dir)
        
        # Queue only sections not yet completed
        pending = queue.get_pending("extract")
        print(f"Sections queued for extraction: {len(pending)}")
        
        # Write extraction prompts for each pending section
        count = 0
        for task in pending:
            sec_id = task["section"]
            file_id = task["file_id"]
            chunk_path = os.path.join(book_dir, "chunks", f"{file_id}.md")
            
            if not os.path.exists(chunk_path):
                queue.set_skipped(sec_id, "extract", "chunk file not found")
                continue
            
            with open(chunk_path, "r", encoding="utf-8") as f:
                chunk_text = f.read()
            
            # Read prompt 02
            prompt_path = os.path.join(BASE_DIR, "prompts", "02_extract.md")
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_text = f.read()
            
            # Write .prompt file
            result = provider.generate(prompt_text, chunk_text, 
                system_hint="You are an ontology extraction engine.")
            
            if result.success:
                queue.set_running(sec_id, "extract")
                # Map: prompt file → extraction output path
                extraction_path = os.path.join(book_dir, "extraction", f"{file_id}.yaml")
                queue.set_completed(sec_id, "extract", extraction_path)
                count += 1
        
        print(f"Written {count} extraction prompt files to {prompt_dir}/")
        print(f"\nNext steps:")
        print(f"  1. Run each .prompt file through Reasonix CLI")
        print(f"  2. Save output to books/{args.book}/extraction/")
        print(f"  3. Run: knowledge-compiler build {args.book} --stage generate")
    
    queue.print_summary()


def cmd_status(args):
    """Show queue status."""
    book_dir = os.path.join(BASE_DIR, "books", args.book)
    if not os.path.exists(book_dir):
        print(f"Book not found: books/{args.book}")
        sys.exit(1)
    
    queue = TaskQueue(book_dir)
    queue.print_summary()


def cmd_retry(args):
    """Retry failed tasks."""
    book_dir = os.path.join(BASE_DIR, "books", args.book)
    queue = TaskQueue(book_dir)
    count = queue.retry_failed(args.stage)
    print(f"Reset {count} failed tasks to pending.")
    queue.print_summary()


def cmd_validate(args):
    """Run validation and print report."""
    book_dir = os.path.join(BASE_DIR, "books", args.book)
    if not os.path.exists(book_dir):
        print(f"Book not found: books/{args.book}")
        sys.exit(1)
    
    report = run_validation(book_dir)
    print_report(report)
    
    if args.report:
        from scripts.validate import save_md_report, save_json_report
        report_path = os.path.join(book_dir, args.report)
        save_md_report(report, report_path)
    
    if args.json:
        from scripts.validate import save_json_report
        json_path = os.path.join(book_dir, args.json)
        save_json_report(report, json_path)


def cmd_release(args):
    """Tag a release for a book."""
    book_dir = os.path.join(BASE_DIR, "books", args.book)
    version = args.version
    
    release_dir = os.path.join(book_dir, "releases", version)
    os.makedirs(release_dir, exist_ok=True)
    
    # Write release metadata
    import json
    from datetime import datetime
    release = {
        "book": args.book,
        "version": version,
        "date": datetime.now().isoformat(),
        "tag": args.tag or f"{args.book}-{version}",
        "chapters": args.chapters or [],
        "description": args.description or "",
    }
    
    path = os.path.join(release_dir, "release.json")
    with open(path, "w") as f:
        json.dump(release, f, indent=2)
    
    print(f"Release {version} for {args.book} created at {path}")
    print(f"Tag: {release['tag']}")


def main():
    parser = argparse.ArgumentParser(description="Knowledge Compiler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # build
    build_p = subparsers.add_parser("build", help="Build a book")
    build_p.add_argument("book", help="Book name (directory under books/)")
    build_p.add_argument("--auto", action="store_true", help="Auto mode: use API provider")
    build_p.add_argument("--provider", default="openai", choices=["openai", "claude", "reasonix"])
    build_p.add_argument("--model", default="gpt-4o-mini")
    build_p.add_argument("--init", action="store_true", help="Initialize task queue")
    build_p.add_argument("--stage", choices=["extract", "generate", "decompose", "validate"],
                        help="Run a specific stage only")

    # status
    status_p = subparsers.add_parser("status", help="Show build status")
    status_p.add_argument("book", help="Book name")

    # retry
    retry_p = subparsers.add_parser("retry", help="Retry failed tasks")
    retry_p.add_argument("book", help="Book name")
    retry_p.add_argument("--stage", choices=["extract", "generate", "decompose", "validate"],
                        help="Retry only this stage")

    # validate
    val_p = subparsers.add_parser("validate", help="Validate generated objects")
    val_p.add_argument("book", help="Book name")
    val_p.add_argument("--report", help="Save MD report path")
    val_p.add_argument("--json", help="Save JSON report path")

    # release
    rel_p = subparsers.add_parser("release", help="Tag a release")
    rel_p.add_argument("book", help="Book name")
    rel_p.add_argument("version", help="Version tag (e.g. v0.1)")
    rel_p.add_argument("--tag", help="Git tag (default: {book}-{version})")
    rel_p.add_argument("--chapters", nargs="+", help="Chapters included")
    rel_p.add_argument("--description", help="Release description")

    args = parser.parse_args()

    commands = {
        "build": cmd_build,
        "status": cmd_status,
        "retry": cmd_retry,
        "validate": cmd_validate,
        "release": cmd_release,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
