#!/usr/bin/env python3
from pathlib import Path
import os
import json

DISPATCH_DIR = Path(os.environ.get("DISPATCH_DIR", str(Path.home() / "dispatch")))

print("=== Scanning task dirs ===")
for subdir in DISPATCH_DIR.iterdir():
    if subdir.is_dir() and not subdir.name.startswith("."):
        tasks_dir = subdir / "tasks"
        if tasks_dir.exists():
            print(f"Found tasks dir: {tasks_dir}")

            # Check each task
            for task_dir in tasks_dir.iterdir():
                if task_dir.is_dir():
                    spec_file = task_dir / "spec.md"
                    status_file = task_dir / "status.json"

                    if spec_file.exists():
                        status = "unknown"
                        if status_file.exists():
                            try:
                                with open(status_file) as f:
                                    status_data = json.load(f)
                                status = status_data.get("status", "unknown")
                            except:
                                status = "error"

                        print(f"  Task: {task_dir.name}, status: {status}")
