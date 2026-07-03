"""
Knowledge Compiler — File-Based Task Queue

Manages batch processing of sections through the pipeline.
Each task is a JSON file in books/{source}/.queue/stage/{section}.json

States:
  pending    → queued, not started
  running    → currently being processed
  completed  → finished successfully
  failed     → finished with error (retryable)
  skipped    → no content to process
"""

import json
import os
from datetime import datetime
from typing import Optional


STAGES = ["extract", "generate", "decompose", "validate"]
TERMINAL = ["completed", "skipped"]


class TaskQueue:
    """File-based queue for section processing tasks."""

    def __init__(self, book_dir: str):
        self.book_dir = book_dir
        self.queue_dir = os.path.join(book_dir, ".queue")
        os.makedirs(self.queue_dir, exist_ok=True)

    def _task_path(self, stage: str, section_id: str) -> str:
        return os.path.join(self.queue_dir, stage, f"{section_id}.json")

    def init_section(self, section_id: str, file_id: str):
        """Create pending tasks for all stages for one section."""
        for stage in STAGES:
            path = self._task_path(stage, section_id)
            if not os.path.exists(path):
                os.makedirs(os.path.dirname(path), exist_ok=True)
                task = {
                    "section": section_id,
                    "file_id": file_id,
                    "stage": stage,
                    "status": "pending",
                    "created": datetime.now().isoformat(),
                    "updated": datetime.now().isoformat(),
                    "retries": 0,
                    "max_retries": 3,
                    "error": None,
                    "output": None,
                }
                with open(path, "w") as f:
                    json.dump(task, f, indent=2)

    def get_status(self, section_id: str, stage: str) -> Optional[str]:
        """Get the status of a task."""
        path = self._task_path(stage, section_id)
        if not os.path.exists(path):
            return None
        with open(path) as f:
            task = json.load(f)
        return task.get("status")

    def set_running(self, section_id: str, stage: str):
        """Mark a task as running."""
        path = self._task_path(stage, section_id)
        if os.path.exists(path):
            with open(path) as f:
                task = json.load(f)
            task["status"] = "running"
            task["updated"] = datetime.now().isoformat()
            with open(path, "w") as f:
                json.dump(task, f, indent=2)

    def set_completed(self, section_id: str, stage: str, output: str = ""):
        """Mark a task as completed."""
        path = self._task_path(stage, section_id)
        if os.path.exists(path):
            with open(path) as f:
                task = json.load(f)
            task["status"] = "completed"
            task["updated"] = datetime.now().isoformat()
            task["output"] = output
            with open(path, "w") as f:
                json.dump(task, f, indent=2)

    def set_failed(self, section_id: str, stage: str, error: str):
        """Mark a task as failed. Will be retried if retries < max_retries."""
        path = self._task_path(stage, section_id)
        if os.path.exists(path):
            with open(path) as f:
                task = json.load(f)
            task["status"] = "failed"
            task["updated"] = datetime.now().isoformat()
            task["error"] = error
            task["retries"] += 1
            # Auto-retry: if retries < max_retries, reset to pending
            if task["retries"] < task["max_retries"]:
                task["status"] = "pending"
            with open(path, "w") as f:
                json.dump(task, f, indent=2)

    def set_skipped(self, section_id: str, stage: str, reason: str = ""):
        """Mark a task as skipped (no content to process)."""
        path = self._task_path(stage, section_id)
        if os.path.exists(path):
            with open(path) as f:
                task = json.load(f)
            task["status"] = "skipped"
            task["updated"] = datetime.now().isoformat()
            task["error"] = reason
            with open(path, "w") as f:
                json.dump(task, f, indent=2)

    def get_pending(self, stage: Optional[str] = None):
        """Get all pending tasks, optionally filtered by stage."""
        tasks = []
        stages = [stage] if stage else STAGES
        for s in stages:
            dir_path = os.path.join(self.queue_dir, s)
            if not os.path.exists(dir_path):
                continue
            for f in sorted(os.listdir(dir_path)):
                if not f.endswith(".json"):
                    continue
                with open(os.path.join(dir_path, f)) as fh:
                    task = json.load(fh)
                if task["status"] == "pending":
                    tasks.append(task)
        return tasks

    def summary(self) -> dict:
        """Return a summary of all task states."""
        counts = {}
        for stage in STAGES:
            dir_path = os.path.join(self.queue_dir, stage)
            if not os.path.exists(dir_path):
                counts[stage] = {}
                continue
            stage_counts = {}
            for f in os.listdir(dir_path):
                if not f.endswith(".json"):
                    continue
                with open(os.path.join(dir_path, f)) as fh:
                    task = json.load(fh)
                status = task["status"]
                stage_counts[status] = stage_counts.get(status, 0) + 1
            counts[stage] = stage_counts
        return counts

    def retry_failed(self, stage: Optional[str] = None):
        """Reset all failed tasks back to pending for retry."""
        stages = [stage] if stage else STAGES
        count = 0
        for s in stages:
            dir_path = os.path.join(self.queue_dir, s)
            if not os.path.exists(dir_path):
                continue
            for f in os.listdir(dir_path):
                if not f.endswith(".json"):
                    continue
                path = os.path.join(dir_path, f)
                with open(path) as fh:
                    task = json.load(fh)
                if task["status"] == "failed" and task["retries"] < task["max_retries"]:
                    task["status"] = "pending"
                    task["updated"] = datetime.now().isoformat()
                    with open(path, "w") as fh:
                        json.dump(task, fh, indent=2)
                    count += 1
        return count

    def init_all_sections(self, sections: list):
        """Initialize the queue for all sections."""
        for sec_id, file_id in sections:
            self.init_section(sec_id, file_id)

    def print_summary(self):
        """Print a human-readable summary."""
        s = self.summary()
        total = sum(sum(sc.values()) for sc in s.values())
        print(f"\nQueue Summary ({total} tasks)")
        print(f"{'Stage':15s} {'Pending':8s} {'Running':8s} {'Done':8s} {'Failed':8s} {'Skipped':8s}")
        print("-" * 65)
        grand = {"pending": 0, "running": 0, "completed": 0, "failed": 0, "skipped": 0}
        for stage, counts in s.items():
            p = counts.get("pending", 0)
            r = counts.get("running", 0)
            c = counts.get("completed", 0)
            f = counts.get("failed", 0)
            sk = counts.get("skipped", 0)
            print(f"{stage:15s} {p:<8d} {r:<8d} {c:<8d} {f:<8d} {sk:<8d}")
            grand["pending"] += p
            grand["running"] += r
            grand["completed"] += c
            grand["failed"] += f
            grand["skipped"] += sk
        print("-" * 65)
        print(f"{'TOTAL':15s} {grand['pending']:<8d} {grand['running']:<8d} {grand['completed']:<8d} {grand['failed']:<8d} {grand['skipped']:<8d}")
        print()

        if grand["failed"] > 0:
            print(f"⚠ {grand['failed']} tasks failed. Run 'knowledge-compiler retry acsm12' to retry.")
        if grand["pending"] > 0:
            print(f"⏳ {grand['pending']} tasks pending. Run 'knowledge-compiler build acsm12' to continue.")
