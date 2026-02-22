#!/usr/bin/env python3
"""
Storage Audit Script
Scans inbox for stale files (>3 days) and emits event.
"""

import os
import sys
from datetime import datetime, timedelta


# Add scripts dir to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# ai_os/scripts is under infrastructure, so go up twice to get to infra root
ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, SCRIPT_DIR)

from emit_event import append_event, now_iso_local


cutoff = datetime.now() - timedelta(days=3)


violations = []
AI_OS_DIR = os.path.join(ROOT, "ai_os")
projects_dir = os.path.join(AI_OS_DIR, "projects")
for p in os.listdir(projects_dir):
    inbox = os.path.join(projects_dir, p, "inbox")
    if not os.path.isdir(inbox):
        continue
    for root, _, files in os.walk(inbox):
        for fn in files:
            path = os.path.join(root, fn)
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if mtime < cutoff:
                violations.append(
                    (p, path.replace(ROOT + "/", ""), mtime.strftime("%Y-%m-%d"))
                )


outdir = os.path.join(AI_OS_DIR, "logs", "weekly")
os.makedirs(outdir, exist_ok=True)
today = datetime.now().strftime("%Y-%m-%d")
outfile_rel = f"ai_os/logs/weekly/{today}_storage_audit.md"
outfile = os.path.join(outdir, f"{today}_storage_audit.md")


with open(outfile, "w", encoding="utf-8") as w:
    w.write(f"# Storage Audit | {today}\n\n")
    if not violations:
        w.write("No stale inbox artifacts (>3 days). ✅\n")
    else:
        w.write("## Stale inbox artifacts (>3 days)\n")
        for proj, path, dt in violations:
            w.write(f"- [{proj}] {path} (last modified: {dt})\n")


# Emit event
event = {
    "ts": now_iso_local(),
    "actor": "agent",
    "project": "GLOBAL",
    "type": "audit.storage",
    "summary": f"Ran storage audit; stale_count={len(violations)}.",
    "refs": {"artifact_path": outfile_rel},
    "meta": {"stale_count": str(len(violations))},
}
append_event(event)


print(outfile)
