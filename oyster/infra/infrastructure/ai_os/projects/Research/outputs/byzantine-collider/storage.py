#!/usr/bin/env python3
"""
拜占庭对撞器 - 持久化存储 (SQLite)
"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

# 数据目录
DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "byzantine_collider.db"


def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 碰撞记录表
    c.execute("""
        CREATE TABLE IF NOT EXISTS collisions (
            id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            rounds INTEGER,
            template TEXT,
            llm TEXT,
            status TEXT,
            result TEXT,
            created_at TEXT,
            completed_at TEXT
        )
    """)

    # 调研记录表
    c.execute("""
        CREATE TABLE IF NOT EXISTS researches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            report TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_collision(
    collision_id: str,
    topic: str,
    rounds: int,
    template: str = "default",
    llm: str = "zhipu",
    status: str = "running",
    result: dict = None,
):
    """保存碰撞记录"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        INSERT OR REPLACE INTO collisions 
        (id, topic, rounds, template, llm, status, result, created_at, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            collision_id,
            topic,
            rounds,
            template,
            llm,
            status,
            json.dumps(result, ensure_ascii=False) if result else None,
            datetime.now().isoformat(),
            datetime.now().isoformat() if status == "completed" else None,
        ),
    )

    conn.commit()
    conn.close()


def get_collision(collision_id: str) -> Optional[dict]:
    """获取碰撞记录"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT * FROM collisions WHERE id = ?", (collision_id,))
    row = c.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "topic": row[1],
            "rounds": row[2],
            "template": row[3],
            "llm": row[4],
            "status": row[5],
            "result": json.loads(row[6]) if row[6] else None,
            "created_at": row[7],
            "completed_at": row[8],
        }
    return None


def list_collisions(limit: int = 50, status: str = None) -> list:
    """列出碰撞记录"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if status:
        c.execute(
            """
            SELECT * FROM collisions 
            ORDER BY created_at DESC 
            LIMIT ?
        """,
            (limit,),
        )
    else:
        c.execute(
            """
            SELECT * FROM collisions 
            WHERE status = ?
            ORDER BY created_at DESC 
            LIMIT ?
        """,
            (status, limit),
        )

    rows = c.fetchall()
    conn.close()

    return [
        {"id": r[0], "topic": r[1], "rounds": r[2], "status": r[5], "created_at": r[7]}
        for r in rows
    ]


def save_research(query: str, report: dict) -> int:
    """保存调研记录"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO researches (query, report, created_at)
        VALUES (?, ?, ?)
    """,
        (query, json.dumps(report, ensure_ascii=False), datetime.now().isoformat()),
    )

    id = c.lastrowid
    conn.commit()
    conn.close()

    return id


# 初始化
init_db()
