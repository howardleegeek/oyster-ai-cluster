#!/usr/bin/env python3
"""Pipeline 数据库管理"""

import sqlite3
import json
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime

DB_PATH = Path(__file__).parent / "pipeline.db"


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                current_layer TEXT DEFAULT 'L1',
                status TEXT DEFAULT 'RUNNING' CHECK(status IN ('RUNNING','DONE','FAILED')),
                retry_count INTEGER DEFAULT 0,
                config JSON
            );
            CREATE TABLE IF NOT EXISTS layer_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL REFERENCES runs(id),
                layer TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('RUNNING','PASS','FAIL','SKIPPED')),
                attempt INTEGER DEFAULT 1,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                report JSON,
                error TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_runs_project ON runs(project);
            CREATE INDEX IF NOT EXISTS idx_lr_run ON layer_results(run_id);
        """)


@contextmanager
def get_db():
    conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def create_run(project: str, config: dict = None) -> int:
    # 转换config为可JSON序列化的简单dict
    def to_serializable(obj):
        if hasattr(obj, "__dict__"):
            return to_serializable(obj.__dict__)
        elif isinstance(obj, dict):
            return {k: to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [to_serializable(i) for i in obj]
        else:
            return obj

    config_json = json.dumps(to_serializable(config) or {})
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO runs (project, started_at, config) VALUES (?, ?, ?)",
            (project, datetime.utcnow().isoformat(), config_json),
        )
        return cur.lastrowid


def update_run(run_id: int, **kwargs):
    with get_db() as conn:
        sets = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [run_id]
        conn.execute(f"UPDATE runs SET {sets} WHERE id=?", vals)


def get_run(run_id: int) -> dict:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        return dict(row) if row else None


def get_latest_run(project: str) -> dict:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM runs WHERE project=? ORDER BY id DESC LIMIT 1", (project,)
        ).fetchone()
        return dict(row) if row else None


def save_layer_result(
    run_id: int,
    layer: str,
    status: str,
    attempt: int = 1,
    report: dict = None,
    error: str = None,
):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO layer_results (run_id, layer, status, attempt, started_at, finished_at, report, error)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                run_id,
                layer,
                status,
                attempt,
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat() if status != "RUNNING" else None,
                json.dumps(report or {}),
                error,
            ),
        )


def get_layer_results(run_id: int) -> list:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM layer_results WHERE run_id=? ORDER BY id", (run_id,)
        ).fetchall()
        return [dict(r) for r in rows]
