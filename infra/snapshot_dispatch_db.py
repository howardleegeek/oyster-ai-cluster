#!/usr/bin/env python3
"""Maintain a readable snapshot of dispatch.db for dashboards.

Why:
- The primary dispatch.db is WAL-backed and actively written.
- Readers over virtiofs (docker/colima) can occasionally hit short open windows.

This script periodically copies dispatch.db (+ -wal/-shm when present) into a
stable snapshot directory, using temp files + atomic replace.

Expected environment:
- DISPATCH_DB_SRC: path to source dispatch.db (default: /dispatch/dispatch.db)
- DISPATCH_DB_DST_DIR: destination directory (default: /dispatch-snapshot)
- SNAPSHOT_INTERVAL_S: seconds between snapshots (default: 2)
"""

from __future__ import annotations

import os
import shutil
import time
from pathlib import Path


def _env(name: str, default: str) -> str:
    return (os.environ.get(name) or default).strip()


def _atomic_copy(src: Path, dst: Path) -> None:
    tmp = dst.with_name(dst.name + ".tmp")
    shutil.copyfile(src, tmp)
    os.replace(tmp, dst)


def main() -> int:
    src_db = Path(_env("DISPATCH_DB_SRC", "/dispatch/dispatch.db"))
    dst_dir = Path(_env("DISPATCH_DB_DST_DIR", "/dispatch-snapshot"))
    interval_s = float(_env("SNAPSHOT_INTERVAL_S", "2") or "2")

    dst_dir.mkdir(parents=True, exist_ok=True)

    while True:
        started = time.time()
        try:
            if src_db.exists():
                _atomic_copy(src_db, dst_dir / "dispatch.db")

            src_wal = Path(str(src_db) + "-wal")
            src_shm = Path(str(src_db) + "-shm")
            if src_wal.exists():
                _atomic_copy(src_wal, dst_dir / "dispatch.db-wal")
            if src_shm.exists():
                _atomic_copy(src_shm, dst_dir / "dispatch.db-shm")

            dt = round(time.time() - started, 3)
            print(f"snapshot ok took_s={dt}", flush=True)
        except Exception as exc:
            dt = round(time.time() - started, 3)
            print(
                f"snapshot error took_s={dt} error={type(exc).__name__}: {exc}",
                flush=True,
            )

        sleep_s = max(0.25, interval_s - (time.time() - started))
        time.sleep(sleep_s)


if __name__ == "__main__":
    raise SystemExit(main())
