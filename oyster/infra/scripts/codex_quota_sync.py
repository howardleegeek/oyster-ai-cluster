#!/usr/bin/env python3
"""Sync Codex quota (5h + weekly) into shared handoff files.

Data source priority:
1) Latest token_count/rate_limits event from ~/.codex/sessions
2) ~/.codex/archived_sessions as fallback
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HOME = Path.home()
SYNC_DIR = HOME / "Library" / "Application Support" / "CodexClaudeSync"
SESSIONS_DIR = HOME / ".codex" / "sessions"
ARCHIVED_DIR = HOME / ".codex" / "archived_sessions"

OUTPUT_JSON = SYNC_DIR / "codex_quota_status.json"
OUTPUT_MD = SYNC_DIR / "codex_quota_status.md"
HANDOFF_MD = SYNC_DIR / "handoff.md"
PROGRESS_LOG = SYNC_DIR / "progress.log"

MARKER_START = "<!-- CODEX_QUOTA_STATUS:START -->"
MARKER_END = "<!-- CODEX_QUOTA_STATUS:END -->"


@dataclass
class QuotaSnapshot:
    event_ts: str
    source_file: str
    info: dict[str, Any]
    rate_limits: dict[str, Any]


def _parse_iso(ts: str | None) -> datetime:
    if not ts:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return datetime.fromtimestamp(0, tz=timezone.utc)


def _iter_jsonl_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(root.rglob("*.jsonl"))


def _find_latest_snapshot() -> QuotaSnapshot | None:
    latest: tuple[datetime, QuotaSnapshot] | None = None
    for base in (SESSIONS_DIR, ARCHIVED_DIR):
        for jsonl in _iter_jsonl_files(base):
            try:
                with jsonl.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if obj.get("type") != "event_msg":
                            continue
                        payload = obj.get("payload") or {}
                        if payload.get("type") != "token_count":
                            continue
                        rate_limits = payload.get("rate_limits") or {}
                        if not rate_limits:
                            continue
                        info = payload.get("info") or {}
                        ts = obj.get("timestamp")
                        dt = _parse_iso(ts)
                        snap = QuotaSnapshot(
                            event_ts=ts or "",
                            source_file=str(jsonl),
                            info=info,
                            rate_limits=rate_limits,
                        )
                        if latest is None or dt > latest[0]:
                            latest = (dt, snap)
            except OSError:
                continue
    return latest[1] if latest else None


def _safe_pct_left(used_percent: Any) -> float | None:
    try:
        used = float(used_percent)
    except (TypeError, ValueError):
        return None
    left = 100.0 - used
    if left < 0:
        return 0.0
    if left > 100:
        return 100.0
    return round(left, 1)


def _safe_pct_used(used_percent: Any) -> float | None:
    try:
        return round(float(used_percent), 1)
    except (TypeError, ValueError):
        return None


def _epoch_to_local_str(value: Any) -> str | None:
    try:
        epoch = int(value)
    except (TypeError, ValueError):
        return None
    return datetime.fromtimestamp(epoch, tz=timezone.utc).astimezone().strftime(
        "%Y-%m-%d %H:%M:%S %Z"
    )


def _fmt_num(n: Any) -> str:
    try:
        x = float(n)
    except (TypeError, ValueError):
        return "N/A"
    if x >= 1000000:
        return f"{x/1000000:.1f}M"
    if x >= 1000:
        return f"{x/1000:.1f}K"
    return str(int(x))


def _build_payload(snapshot: QuotaSnapshot) -> dict[str, Any]:
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    primary = snapshot.rate_limits.get("primary") or {}
    secondary = snapshot.rate_limits.get("secondary") or {}
    info = snapshot.info or {}
    total_usage = info.get("total_token_usage") or {}
    last_usage = info.get("last_token_usage") or {}

    context_window = info.get("model_context_window")
    context_last_total = last_usage.get("total_tokens")
    context_left_pct: float | None = None
    try:
        if context_window and context_last_total is not None:
            context_left_pct = round(
                max(
                    0.0,
                    min(100.0, 100.0 - (float(context_last_total) / float(context_window) * 100.0)),
                ),
                1,
            )
    except (TypeError, ValueError, ZeroDivisionError):
        context_left_pct = None

    return {
        "updated_at_local": now,
        "event_timestamp": snapshot.event_ts,
        "source_file": snapshot.source_file,
        "five_hour": {
            "used_percent": _safe_pct_used(primary.get("used_percent")),
            "left_percent": _safe_pct_left(primary.get("used_percent")),
            "window_minutes": primary.get("window_minutes"),
            "resets_at_epoch": primary.get("resets_at"),
            "resets_at_local": _epoch_to_local_str(primary.get("resets_at")),
        },
        "weekly": {
            "used_percent": _safe_pct_used(secondary.get("used_percent")),
            "left_percent": _safe_pct_left(secondary.get("used_percent")),
            "window_minutes": secondary.get("window_minutes"),
            "resets_at_epoch": secondary.get("resets_at"),
            "resets_at_local": _epoch_to_local_str(secondary.get("resets_at")),
        },
        "context_window": {
            "model_context_window": context_window,
            "last_turn_tokens": context_last_total,
            "session_total_tokens": total_usage.get("total_tokens"),
            "left_percent_estimated": context_left_pct,
        },
    }


def _build_markdown(payload: dict[str, Any]) -> str:
    five = payload.get("five_hour") or {}
    week = payload.get("weekly") or {}
    ctx = payload.get("context_window") or {}
    return "\n".join(
        [
            "# Codex Quota Status (Auto)",
            "",
            f"- Updated: {payload.get('updated_at_local', 'N/A')}",
            f"- Event TS: {payload.get('event_timestamp', 'N/A')}",
            f"- Source: `{payload.get('source_file', 'N/A')}`",
            "",
            "| Metric | Used | Left | Reset |",
            "|---|---:|---:|---|",
            f"| 5h | {five.get('used_percent', 'N/A')}% | {five.get('left_percent', 'N/A')}% | {five.get('resets_at_local', 'N/A')} |",
            f"| Weekly | {week.get('used_percent', 'N/A')}% | {week.get('left_percent', 'N/A')}% | {week.get('resets_at_local', 'N/A')} |",
            f"| Context Window (last turn) | {_fmt_num(ctx.get('last_turn_tokens'))} used | {ctx.get('left_percent_estimated', 'N/A')}% left | model max {_fmt_num(ctx.get('model_context_window'))} |",
            "",
        ]
    ) + "\n"


def _build_handoff_block(payload: dict[str, Any]) -> str:
    five = payload.get("five_hour") or {}
    week = payload.get("weekly") or {}
    ctx = payload.get("context_window") or {}
    return "\n".join(
        [
            "## Codex 额度状态 (AUTO)",
            f"- 更新时间: {payload.get('updated_at_local', 'N/A')}",
            f"- 5h 额度: {five.get('left_percent', 'N/A')}% left ({five.get('used_percent', 'N/A')}% used), reset: {five.get('resets_at_local', 'N/A')}",
            f"- Weekly 额度: {week.get('left_percent', 'N/A')}% left ({week.get('used_percent', 'N/A')}% used), reset: {week.get('resets_at_local', 'N/A')}",
            f"- Context(本轮): {_fmt_num(ctx.get('last_turn_tokens'))}/{_fmt_num(ctx.get('model_context_window'))} used, left est. {ctx.get('left_percent_estimated', 'N/A')}%",
            f"- 详情文件: `{OUTPUT_JSON}` | `{OUTPUT_MD}`",
        ]
    )


def _upsert_handoff(block: str) -> None:
    try:
        current = HANDOFF_MD.read_text(encoding="utf-8")
    except OSError:
        return
    wrapped = f"{MARKER_START}\n{block}\n{MARKER_END}"
    if MARKER_START in current and MARKER_END in current:
        pre = current.split(MARKER_START, 1)[0]
        post = current.split(MARKER_END, 1)[1]
        updated = pre + wrapped + post
    else:
        anchor = current.find("---")
        if anchor != -1:
            insert_at = current.find("\n", anchor)
            if insert_at == -1:
                insert_at = len(current)
            updated = current[: insert_at + 1] + "\n" + wrapped + "\n\n" + current[insert_at + 1 :]
        else:
            updated = wrapped + "\n\n" + current
    HANDOFF_MD.write_text(updated, encoding="utf-8")


def _append_progress(payload: dict[str, Any]) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    five = payload.get("five_hour") or {}
    week = payload.get("weekly") or {}
    five_left = five.get("left_percent", "N/A")
    week_left = week.get("left_percent", "N/A")
    line = (
        f"[{ts}] DEPUTY QUOTA: 5h_left={five_left}% weekly_left={week_left}%\n"
    )
    try:
        if PROGRESS_LOG.exists():
            existing = PROGRESS_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()
            for prev in reversed(existing[-80:]):
                if "DEPUTY QUOTA:" not in prev:
                    continue
                if f"5h_left={five_left}%" in prev and f"weekly_left={week_left}%" in prev:
                    return
                break
        with PROGRESS_LOG.open("a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass


def main() -> int:
    SYNC_DIR.mkdir(parents=True, exist_ok=True)
    snapshot = _find_latest_snapshot()
    if not snapshot:
        OUTPUT_JSON.write_text(
            json.dumps(
                {
                    "updated_at_local": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
                    "error": "No token_count/rate_limits events found in ~/.codex/sessions or archived_sessions",
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return 1

    payload = _build_payload(snapshot)
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(_build_markdown(payload), encoding="utf-8")
    _upsert_handoff(_build_handoff_block(payload))
    _append_progress(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
