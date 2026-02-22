#!/usr/bin/env python3
"""
emit_event.py - Append-only NDJSON event emitter for AI OS.


Usage:
  python3 ai_os/scripts/emit_event.py \
    --project GLOBAL \
    --type session.start \
    --summary "Started infra governance session" \
    --ref artifact_path=ai_os/flight_rules.md \
    --meta priority=P1 due=2026-02-16
"""

import argparse
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVENTS_DIR = os.path.join(ROOT, "events")


def now_iso_local() -> str:
    # local time with offset, ISO 8601
    dt = datetime.now().astimezone()
    return dt.isoformat(timespec="seconds")


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def ym_key(ts_iso: str) -> str:
    # ts like 2026-02-14T22:31:05-08:00 -> 2026-02
    return ts_iso[:7]


def parse_kv_list(items) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if not items:
        return out
    for it in items:
        if "=" not in it:
            raise ValueError(f"Expected key=value, got: {it}")
        k, v = it.split("=", 1)
        out[k] = v
    return out


def append_event(event: Dict[str, Any]) -> str:
    ensure_dir(EVENTS_DIR)
    month = ym_key(event["ts"])
    path = os.path.join(EVENTS_DIR, f"{month}.ndjson")
    # append-only single-line JSON
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--actor", default="agent", choices=["user", "agent"])
    ap.add_argument("--project", required=True)
    ap.add_argument("--type", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--session_id", default=None)
    ap.add_argument("--artifact_type", default=None)
    ap.add_argument("--artifact_path", default=None)
    ap.add_argument("--task_ref", default=None)
    ap.add_argument(
        "--ref", action="append", default=[], help="refs key=value (repeatable)"
    )
    ap.add_argument(
        "--meta", action="append", default=[], help="meta key=value (repeatable)"
    )
    args = ap.parse_args()

    ts = now_iso_local()
    refs = parse_kv_list(args.ref)
    meta = parse_kv_list(args.meta)

    # convenience: if artifact_path passed, mirror into refs
    if args.artifact_path:
        refs.setdefault("artifact_path", args.artifact_path)

    event: Dict[str, Any] = {
        "ts": ts,
        "actor": args.actor,
        "project": args.project,
        "type": args.type,
        "summary": args.summary,
        "refs": refs,
    }

    # optional fields
    if args.session_id:
        event["session_id"] = args.session_id
    if args.artifact_type:
        event["artifact_type"] = args.artifact_type
    if args.task_ref:
        event["task_ref"] = args.task_ref
    if meta:
        event["meta"] = meta

    out = append_event(event)
    print(out)


if __name__ == "__main__":
    main()
