#!/usr/bin/env python3
"""
Morning Brief Script
Generates daily task summary and emits event.
"""

import os
import sys
from datetime import datetime


# Add scripts dir to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# ai_os/scripts is under infrastructure, so go up twice to get to infra root
ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, SCRIPT_DIR)

from emit_event import append_event, now_iso_local


TODAY = datetime.now().strftime("%Y-%m-%d")


# ai_os is at ROOT/ai_os
AI_OS_DIR = os.path.join(ROOT, "ai_os")
TASK_FILES = [os.path.join(AI_OS_DIR, "TASKS_GLOBAL.md")]
projects_dir = os.path.join(AI_OS_DIR, "projects")
if os.path.isdir(projects_dir):
    for p in os.listdir(projects_dir):
        f = os.path.join(projects_dir, p, "TASKS.md")
        if os.path.isfile(f):
            TASK_FILES.append(f)


def extract_open_tasks(md: str):
    out = []
    for line in md.splitlines():
        if line.strip().startswith("- [ ]"):
            out.append(line.strip())
    return out


all_tasks = []
for f in TASK_FILES:
    with open(f, "r", encoding="utf-8") as fh:
        tasks = extract_open_tasks(fh.read())
    if tasks:
        all_tasks.append((f.replace(ROOT + "/", ""), tasks))


logdir = os.path.join(AI_OS_DIR, "logs", "daily")
os.makedirs(logdir, exist_ok=True)
outfile_rel = f"ai_os/logs/daily/{TODAY}_morning.md"
outfile = os.path.join(logdir, f"{TODAY}_morning.md")


with open(outfile, "w", encoding="utf-8") as w:
    w.write(f"# Morning Brief | {TODAY}\n\n")
    if not all_tasks:
        w.write("No open tasks. ✅\n")
    else:
        for fname, tasks in all_tasks:
            w.write(f"## {fname}\n")
            for t in tasks[:50]:
                w.write(f"{t}\n")
            if len(tasks) > 50:
                w.write(f"- ... (+{len(tasks) - 50} more)\n")
            w.write("\n")


# Emit event
event = {
    "ts": now_iso_local(),
    "actor": "agent",
    "project": "GLOBAL",
    "type": "brief.morning",
    "summary": f"Generated morning brief for {TODAY}.",
    "refs": {"artifact_path": outfile_rel},
}
append_event(event)


print(outfile)
