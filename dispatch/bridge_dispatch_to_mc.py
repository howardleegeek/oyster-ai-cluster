#!/usr/bin/env python3
"""Bridge dispatch task status into Mission Control.

This runs as a lightweight poller:
- Reads dispatch SQLite state (dispatch.db)
- Mirrors tasks into a Mission Control board (by slug)

It avoids committing secrets by:
- Reading the Mission Control local auth token from env first
- Falling back to parsing openclaw-mission-control/.env locally
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import time
import shutil
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_MC_BASE_URL = "http://localhost:8100/api/v1"
DEFAULT_BOARD_SLUG = "dispatch-status"

# Avoid spamming logs on persistent 4xx errors.
_LOGGED_HTTP_ERRORS: set[str] = set()

# Cache board id lookups to avoid extra API calls.
_BOARD_ID_CACHE: dict[str, str] = {}


@dataclass(frozen=True)
class DispatchTaskRow:
    id: str
    project: str
    spec_file: str
    status: str
    node: str | None
    pid: int | None
    attempt: int | None
    started_at: str | None
    completed_at: str | None
    error: str | None


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _find_repo_root(start: Path) -> Path | None:
    current = start
    for _ in range(6):
        if (current / "openclaw-mission-control" / ".env").exists():
            return current
        current = current.parent
    return None


def _load_mc_token() -> str:
    token = (
        os.environ.get("MC_TOKEN") or os.environ.get("LOCAL_AUTH_TOKEN") or ""
    ).strip()
    if token:
        return token

    # Best-effort fallback: read from the local Mission Control .env file.
    repo_root = _find_repo_root(Path(__file__).resolve())
    if repo_root is None:
        repo_root = Path.home() / "Downloads"
    env_path = repo_root / "openclaw-mission-control" / ".env"
    raw = _read_text(env_path) or ""
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if line.startswith("LOCAL_AUTH_TOKEN="):
            value = line.split("=", 1)[1].strip()
            if value:
                return value
    raise RuntimeError(
        "Mission Control token missing. Set MC_TOKEN or ensure openclaw-mission-control/.env exists."
    )


def _mc_base_url() -> str:
    base = (os.environ.get("MC_BASE_URL") or DEFAULT_MC_BASE_URL).strip().rstrip("/")
    if not base:
        return DEFAULT_MC_BASE_URL
    return base


def _dispatch_db_path() -> Path:
    configured = (os.environ.get("DISPATCH_DB") or "").strip()
    if configured:
        return Path(configured)
    here = Path(__file__).resolve().parent
    return here / "dispatch.db"


def _dispatch_status_to_mc(status: str) -> str:
    normalized = (status or "").strip().lower()
    if normalized in {"pending", "claimed"}:
        return "inbox"
    if normalized in {"running"}:
        return "in_progress"
    if normalized in {"completed"}:
        return "done"
    if normalized in {"failed"}:
        return "review"
    return "inbox"


def _title(row: DispatchTaskRow) -> str:
    return f"[dispatch] {row.project} {row.id}"


def _description(row: DispatchTaskRow) -> str:
    parts: list[str] = []
    parts.append(f"dispatch_task_id: {row.id}")
    parts.append(f"project: {row.project}")
    parts.append(f"status: {row.status}")
    parts.append(f"spec_file: {row.spec_file}")
    if row.node:
        parts.append(f"node: {row.node}")
    if row.pid is not None:
        parts.append(f"pid: {row.pid}")
    if row.attempt is not None:
        parts.append(f"attempt: {row.attempt}")
    if row.started_at:
        parts.append(f"started_at: {row.started_at}")
    if row.completed_at:
        parts.append(f"completed_at: {row.completed_at}")
    if row.error:
        err = row.error.strip().replace("\n", " ")
        if len(err) > 800:
            err = err[:800] + "..."
        parts.append("")
        parts.append("error:")
        parts.append(err)
    return "\n".join(parts)


def _review_comment(row: DispatchTaskRow) -> str:
    """Generate a short non-empty comment for transitions into `review`.

    Mission Control requires a comment when a task enters review.
    """
    node = (row.node or "").strip() or "unknown"
    attempt = row.attempt if row.attempt is not None else 0
    err = (row.error or "").strip().replace("\n", " ")
    if len(err) > 360:
        err = err[:360] + "..."
    if err:
        return f"dispatch failed (node={node} attempt={attempt}): {err}"
    return f"dispatch failed (node={node} attempt={attempt}); see task description for details."


def _mc_request(
    method: str,
    path: str,
    *,
    token: str,
    params: dict[str, str] | None = None,
    json_body: dict[str, Any] | None = None,
    timeout_s: int = 30,
) -> dict[str, Any]:
    base = _mc_base_url()
    url = f"{base}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    data = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, method=method.upper(), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw) if raw else {}


def _mc_find_board_id(*, token: str, slug: str) -> str:
    cached = _BOARD_ID_CACHE.get(slug)
    if isinstance(cached, str) and cached:
        return cached

    offset = 0
    while True:
        payload = _mc_request(
            "GET",
            "/boards",
            token=token,
            params={"limit": "100", "offset": str(offset)},
        )
        items = payload.get("items") or []
        if not isinstance(items, list):
            raise RuntimeError("Invalid /boards response")
        for it in items:
            if isinstance(it, dict) and it.get("slug") == slug:
                board_id = it.get("id")
                if isinstance(board_id, str) and board_id:
                    _BOARD_ID_CACHE[slug] = board_id
                    return board_id
        total = payload.get("total")
        if isinstance(total, int) and offset + len(items) >= total:
            break
        if not items:
            break
        offset += len(items)
    raise RuntimeError(f"Board not found by slug: {slug}")


def _mc_list_tasks(*, token: str, board_id: str) -> list[dict[str, Any]]:
    all_items: list[dict[str, Any]] = []
    offset = 0
    while True:
        payload = _mc_request(
            "GET",
            f"/boards/{board_id}/tasks",
            token=token,
            params={"limit": "200", "offset": str(offset)},
        )
        items = payload.get("items") or []
        if not isinstance(items, list):
            break
        for it in items:
            if isinstance(it, dict):
                all_items.append(it)
        total = payload.get("total")
        if isinstance(total, int) and offset + len(items) >= total:
            break
        if not items:
            break
        offset += len(items)
    return all_items


def _dispatch_list_tasks(db_path: Path) -> list[DispatchTaskRow]:
    if not db_path.exists():
        raise RuntimeError(f"dispatch db not found: {db_path}")

    # Open read-only via a local snapshot.
    #
    # Rationale:
    # - dispatch.db is WAL-backed + actively written.
    # - readers over virtiofs can occasionally hit short open windows.
    #
    # Taking a best-effort snapshot into /tmp avoids most reader flakiness.

    def _connect_ro(path: Path) -> sqlite3.Connection:
        return sqlite3.connect(
            f"file:{path.as_posix()}?mode=ro&immutable=1",
            uri=True,
            timeout=2.0,
        )

    snap_dir = Path("/tmp") / "dispatch-snapshot"
    snap_dir.mkdir(parents=True, exist_ok=True)
    snap = snap_dir / "dispatch.db"
    snap_wal = snap_dir / "dispatch.db-wal"
    snap_shm = snap_dir / "dispatch.db-shm"

    wal = Path(str(db_path) + "-wal")
    shm = Path(str(db_path) + "-shm")

    last_exc: Exception | None = None
    conn: sqlite3.Connection | None = None
    for attempt in range(12):
        try:
            tmp = snap.with_name(snap.name + f".tmp.{os.getpid()}")
            shutil.copyfile(db_path, tmp)
            os.replace(tmp, snap)

            if wal.exists():
                tmp_wal = snap_wal.with_name(snap_wal.name + f".tmp.{os.getpid()}")
                shutil.copyfile(wal, tmp_wal)
                os.replace(tmp_wal, snap_wal)
            else:
                try:
                    snap_wal.unlink()
                except FileNotFoundError:
                    pass

            if shm.exists():
                tmp_shm = snap_shm.with_name(snap_shm.name + f".tmp.{os.getpid()}")
                shutil.copyfile(shm, tmp_shm)
                os.replace(tmp_shm, snap_shm)
            else:
                try:
                    snap_shm.unlink()
                except FileNotFoundError:
                    pass

            conn = _connect_ro(snap)
            break
        except (OSError, sqlite3.OperationalError) as exc:
            last_exc = exc
            time.sleep(min(1.0, 0.1 * (attempt + 1)))

    if conn is None:
        raise sqlite3.OperationalError(
            str(last_exc) if last_exc else "unable to open database file"
        )

    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT id, project, spec_file, status, node, pid, attempt, started_at, completed_at, error
            FROM tasks
            ORDER BY created_at DESC
            """.strip(),
        ).fetchall()
        out: list[DispatchTaskRow] = []
        for r in rows:
            out.append(
                DispatchTaskRow(
                    id=str(r["id"]),
                    project=str(r["project"]),
                    spec_file=str(r["spec_file"]),
                    status=str(r["status"]),
                    node=r["node"],
                    pid=r["pid"],
                    attempt=r["attempt"],
                    started_at=r["started_at"],
                    completed_at=r["completed_at"],
                    error=r["error"],
                )
            )
        return out
    finally:
        conn.close()


def sync_once(*, limit: int | None = None) -> tuple[int, int, int]:
    token = _load_mc_token()
    board_slug = (
        os.environ.get("MC_DISPATCH_BOARD_SLUG") or DEFAULT_BOARD_SLUG
    ).strip()

    board_id = _mc_find_board_id(token=token, slug=board_slug)
    existing = _mc_list_tasks(token=token, board_id=board_id)

    existing_by_title: dict[str, dict[str, Any]] = {}
    for it in existing:
        title = it.get("title")
        if isinstance(title, str) and title:
            existing_by_title[title] = it

    rows = _dispatch_list_tasks(_dispatch_db_path())
    if isinstance(limit, int) and limit > 0:
        rows = rows[:limit]

    created = 0
    updated = 0
    unchanged = 0

    desired_titles = {_title(r) for r in rows}

    for row in rows:
        title = _title(row)
        desired_status = _dispatch_status_to_mc(row.status)
        desired_desc = _description(row)

        existing_task = existing_by_title.get(title)
        if existing_task is None:
            try:
                _mc_request(
                    "POST",
                    f"/boards/{board_id}/tasks",
                    token=token,
                    json_body={
                        "title": title,
                        "description": desired_desc,
                        "status": desired_status,
                        "priority": "medium",
                    },
                )
                created += 1
            except urllib.error.HTTPError as exc:
                key = f"{exc.code}:create:{title}"
                if key not in _LOGGED_HTTP_ERRORS:
                    _LOGGED_HTTP_ERRORS.add(key)
                    try:
                        body = exc.read().decode("utf-8", errors="ignore").strip()
                    except Exception:
                        body = ""
                    if len(body) > 1200:
                        body = body[:1200] + "..."
                    print(
                        "dispatch->mc create_failed "
                        + f"status_code={exc.code} title={title!r} desired_status={desired_status} "
                        + f"body={body!r}",
                        flush=True,
                    )
            continue

        task_id = existing_task.get("id")
        if not isinstance(task_id, str) or not task_id:
            continue
        current_status = existing_task.get("status")
        current_desc = existing_task.get("description")
        if not isinstance(current_desc, str):
            current_desc = ""

        if current_status == desired_status and current_desc == desired_desc:
            unchanged += 1
            continue

        patch: dict[str, Any] = {}
        if current_status != desired_status:
            patch["status"] = desired_status
            if desired_status == "review":
                patch["comment"] = _review_comment(row)
        if current_desc != desired_desc:
            patch["description"] = desired_desc
        if not patch:
            unchanged += 1
            continue

        try:
            _mc_request(
                "PATCH",
                f"/boards/{board_id}/tasks/{task_id}",
                token=token,
                json_body=patch,
            )
            updated += 1
        except urllib.error.HTTPError as exc:
            key = f"{exc.code}:{task_id}"
            if key not in _LOGGED_HTTP_ERRORS:
                _LOGGED_HTTP_ERRORS.add(key)
                try:
                    body = exc.read().decode("utf-8", errors="ignore").strip()
                except Exception:
                    body = ""
                if len(body) > 1200:
                    body = body[:1200] + "..."
                print(
                    "dispatch->mc patch_failed "
                    + f"status_code={exc.code} task_id={task_id} title={title!r} "
                    + f"desired_status={desired_status} body={body!r}",
                    flush=True,
                )
            # Continue syncing other tasks.
            continue

    # Cleanup: tasks that exist in Mission Control but no longer exist in dispatch.db
    # (e.g., DB reset or project switched). Mark them done so the dashboard doesn't
    # show phantom "running" work.
    cleanup_limit_raw = (os.environ.get("MC_STALE_CLEANUP_LIMIT") or "200").strip()
    try:
        cleanup_limit = int(cleanup_limit_raw) if cleanup_limit_raw else 200
    except Exception:
        cleanup_limit = 200

    archived_marker = "archived_by_dispatch_bridge: true"
    archived_at = datetime.now(timezone.utc).isoformat()

    def _status_rank(value: object) -> int:
        v = (value or "").strip() if isinstance(value, str) else ""
        if v == "in_progress":
            return 0
        if v == "review":
            return 1
        if v == "inbox":
            return 2
        return 3

    stale: list[tuple[int, str, dict[str, Any]]] = []
    for title, task in existing_by_title.items():
        if not title.startswith("[dispatch] "):
            continue
        if title in desired_titles:
            continue
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id:
            continue
        status_value = task.get("status")
        if status_value == "done":
            continue
        stale.append((_status_rank(status_value), title, task))

    stale.sort(key=lambda it: it[0])

    cleaned = 0
    for _rank, title, task in stale:
        if cleanup_limit > 0 and cleaned >= cleanup_limit:
            break
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id:
            continue
        current_desc = task.get("description")
        if not isinstance(current_desc, str):
            current_desc = ""
        if archived_marker in current_desc:
            # Still ensure it is not in progress.
            new_desc = current_desc
        else:
            suffix = (
                "\n\n"
                + archived_marker
                + "\narchived_at: "
                + archived_at
                + "\narchived_reason: not_found_in_dispatch_db\n"
            )
            new_desc = (
                (current_desc + suffix) if current_desc.strip() else suffix.lstrip("\n")
            )

        try:
            _mc_request(
                "PATCH",
                f"/boards/{board_id}/tasks/{task_id}",
                token=token,
                json_body={
                    "status": "done",
                    "description": new_desc,
                },
            )
            updated += 1
            cleaned += 1
        except urllib.error.HTTPError as exc:
            key = f"{exc.code}:stale:{task_id}"
            if key not in _LOGGED_HTTP_ERRORS:
                _LOGGED_HTTP_ERRORS.add(key)
                try:
                    body = exc.read().decode("utf-8", errors="ignore").strip()
                except Exception:
                    body = ""
                if len(body) > 1200:
                    body = body[:1200] + "..."
                print(
                    "dispatch->mc stale_cleanup_failed "
                    + f"status_code={exc.code} task_id={task_id} title={title!r} "
                    + f"body={body!r}",
                    flush=True,
                )

    return created, updated, unchanged


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bridge dispatch status into Mission Control"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single sync iteration and exit",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of most-recent dispatch tasks mirrored",
    )
    args = parser.parse_args()

    interval_s = int((os.environ.get("MC_SYNC_INTERVAL_S") or "30").strip() or "30")
    while True:
        started = time.time()
        try:
            created, updated, unchanged = sync_once(limit=args.limit)
            dt = round(time.time() - started, 2)
            print(
                f"dispatch->mc ok created={created} updated={updated} unchanged={unchanged} took_s={dt}",
                flush=True,
            )
            if args.once:
                return
        except Exception as exc:
            dt = round(time.time() - started, 2)
            if isinstance(exc, urllib.error.HTTPError):
                try:
                    body = exc.read().decode("utf-8", errors="ignore").strip()
                except Exception:
                    body = ""
                if len(body) > 1200:
                    body = body[:1200] + "..."
                print(
                    f"dispatch->mc http_error took_s={dt} status_code={exc.code} url={exc.url} body={body!r}",
                    flush=True,
                )
            else:
                print(
                    f"dispatch->mc error took_s={dt} error={type(exc).__name__}: {exc}",
                    flush=True,
                )
            if args.once:
                raise
        time.sleep(max(5, interval_s))


if __name__ == "__main__":
    main()
