#!/usr/bin/env python3
"""
Weekly Review Script
Generates system governance report from event stream.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from collections import Counter


# Add scripts dir to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# ai_os/scripts is under infrastructure, so go up twice to get to infra root
ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, SCRIPT_DIR)

from emit_event import append_event, now_iso_local


AI_OS_DIR = os.path.join(ROOT, "ai_os")
EVENTS_DIR = os.path.join(AI_OS_DIR, "events")
OUT_DIR = os.path.join(AI_OS_DIR, "logs", "weekly")
os.makedirs(OUT_DIR, exist_ok=True)


today = datetime.now().date()
start = today - timedelta(days=7)


def iter_event_files():
    if not os.path.isdir(EVENTS_DIR):
        return
    for fn in sorted(os.listdir(EVENTS_DIR)):
        if fn.endswith(".ndjson"):
            yield os.path.join(EVENTS_DIR, fn)


def parse_ts(ts: str):
    # ISO8601 w/ offset -> datetime
    return datetime.fromisoformat(ts)


events = []
for path in iter_event_files():
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
                dt = parse_ts(e["ts"]).date()
                if dt >= start and dt <= today:
                    events.append(e)
            except Exception:
                continue


by_type = Counter(e.get("type", "unknown") for e in events)
by_project = Counter(e.get("project", "unknown") for e in events)


# crude artifact/task counts (best-effort)
artifact_events = [e for e in events if (e.get("type", "").startswith("artifact."))]
task_events = [e for e in events if (e.get("type", "").startswith("task."))]


outfile_date = today.strftime("%Y-%m-%d")
outfile_rel = f"ai_os/logs/weekly/{outfile_date}_weekly_review.md"
outfile = os.path.join(OUT_DIR, f"{outfile_date}_weekly_review.md")


with open(outfile, "w", encoding="utf-8") as w:
    w.write(f"# Weekly Review | {outfile_date}\n\n")
    w.write(f"Window: {start.isoformat()} → {today.isoformat()}\n\n")

    w.write("## Summary\n")
    w.write(f"- Total events: {len(events)}\n")
    w.write(f"- Artifact events: {len(artifact_events)}\n")
    w.write(f"- Task events: {len(task_events)}\n\n")

    w.write("## Events by Type\n")
    for k, v in by_type.most_common():
        w.write(f"- {k}: {v}\n")
    w.write("\n")

    w.write("## Events by Project\n")
    for k, v in by_project.most_common():
        w.write(f"- {k}: {v}\n")
    w.write("\n")

    # top refs
    w.write("## Notable Artifacts (last 20)\n")
    for e in artifact_events[-20:]:
        refs = e.get("refs", {})
        ap = refs.get("artifact_path", "-")
        w.write(f"- [{e.get('project')}] {e.get('summary')} -> {ap}\n")


# Emit event
append_event(
    {
        "ts": now_iso_local(),
        "actor": "agent",
        "project": "GLOBAL",
        "type": "review.weekly",
        "summary": f"Generated weekly review for {outfile_date}.",
        "refs": {"artifact_path": outfile_rel},
        "meta": {
            "window_start": start.isoformat(),
            "window_end": today.isoformat(),
            "events": str(len(events)),
        },
    }
)


print(outfile)
