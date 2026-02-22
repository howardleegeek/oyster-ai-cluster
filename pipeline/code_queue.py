#!/usr/bin/env python3
"""Code Task Queue Manager"""

import sqlite3
import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import List, Dict, Optional

DB_PATH = Path(__file__).parent / "pipeline.db"


@contextmanager
def get_db():
    """Context manager for database connection"""
    conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


class CodeQueue:
    """代码任务队列管理器"""

    def __init__(self, db_path: Optional[str] = None):
        """初始化 CodeQueue

        Args:
            db_path: 数据库路径，默认使用 pipeline.db
        """
        self.db_path = db_path or str(DB_PATH)

    @contextmanager
    def _get_db(self):
        """Internal database context manager"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def enqueue(
        self,
        job_type: str,
        source: str,
        payload: dict,
        priority: int = 2,
        workspace_path: str = None,
        artifact_links: dict = None
    ) -> str:
        """入队，返回 job_id

        Args:
            job_type: 任务类型 ('content' 或 'code')
            source: 任务来源 ('github_issue', 'todo_scan', 'failing_ci', 'manual')
            payload: 任务负载数据 (JSON dict)
            priority: 优先级 (1-5, 越小越优先)
            workspace_path: 工作区路径
            artifact_links: 工件链接 (dict)

        Returns:
            job_id: 任务 ID
        """
        job_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        with self._get_db() as conn:
            conn.execute(
                """INSERT INTO code_jobs
                   (id, type, source, priority, state, payload, workspace_path,
                    artifact_links, created_at, updated_at)
                   VALUES (?, ?, ?, ?, 'queued', ?, ?, ?, ?, ?)""",
                (
                    job_id,
                    job_type,
                    source,
                    priority,
                    json.dumps(payload),
                    workspace_path,
                    json.dumps(artifact_links or {}),
                    now,
                    now,
                ),
            )
        return job_id

    def claim(self, worker_id: str, max_jobs: int = 3, timeout_minutes: int = 30) -> List[dict]:
        """worker 认领任务（带锁）

        Args:
            worker_id: worker 标识
            max_jobs: 最多认领的任务数
            timeout_minutes: 锁超时时间（分钟）

        Returns:
            jobs: 认领的任务列表
        """
        lock_expires = (datetime.utcnow() + timedelta(minutes=timeout_minutes)).isoformat()
        now = datetime.utcnow().isoformat()
        jobs_claimed = []

        with self._get_db() as conn:
            # 查询可认领的任务（queued 或 lock 过期的 running 任务）
            cursor = conn.execute(
                """SELECT * FROM code_jobs
                   WHERE state IN ('queued', 'running')
                     AND (lock_owner IS NULL OR lock_expires_at < ?)
                   ORDER BY priority ASC, created_at ASC
                   LIMIT ?""",
                (now, max_jobs),
            )

            rows = cursor.fetchall()
            for row in rows:
                job = dict(row)
                job_id = job["id"]

                # 更新任务状态为 running 并加锁
                conn.execute(
                    """UPDATE code_jobs
                       SET state = 'running',
                           lock_owner = ?,
                           lock_expires_at = ?,
                           started_at = COALESCE(started_at, ?),
                           updated_at = ?
                       WHERE id = ?""",
                    (worker_id, lock_expires, now, now, job_id),
                )

                # 重新查询获取更新后的数据
                updated = conn.execute(
                    "SELECT * FROM code_jobs WHERE id = ?", (job_id,)
                ).fetchone()
                if updated:
                    jobs_claimed.append(dict(updated))

        return jobs_claimed

    def release(
        self,
        job_id: str,
        state: str,
        error: str = None,
        artifact_links: dict = None
    ) -> bool:
        """释放任务（完成/失败）

        Args:
            job_id: 任务 ID
            state: 最终状态 ('done', 'failed', 'needs_human', 'blocked')
            error: 错误信息（如果有）
            artifact_links: 更新的工件链接

        Returns:
            success: 是否成功更新
        """
        now = datetime.utcnow().isoformat()

        with self._get_db() as conn:
            # 检查任务是否存在
            job = conn.execute(
                "SELECT * FROM code_jobs WHERE id = ?", (job_id,)
            ).fetchone()
            if not job:
                return False

            job_dict = dict(job)

            # 如果失败，增加重试计数
            retry_count = job_dict["retry_count"]
            if state == "failed":
                retry_count += 1
                max_retries = job_dict.get("max_retries", 2)
                # 如果超过最大重试次数，转为 needs_human
                if retry_count >= max_retries:
                    state = "needs_human"

            # 合并 artifact_links
            existing_links = json.loads(job_dict.get("artifact_links") or "{}")
            if artifact_links:
                existing_links.update(artifact_links)

            # 更新任务
            conn.execute(
                """UPDATE code_jobs
                   SET state = ?,
                       lock_owner = NULL,
                       lock_expires_at = NULL,
                       completed_at = CASE WHEN ? IN ('done', 'failed', 'needs_human') THEN ? ELSE completed_at END,
                       error = ?,
                       artifact_links = ?,
                       retry_count = ?,
                       updated_at = ?
                   WHERE id = ?""",
                (
                    state,
                    state,
                    now,
                    error,
                    json.dumps(existing_links),
                    retry_count,
                    now,
                    job_id,
                ),
            )
            return True

    def get_queued_count(self) -> int:
        """获取排队数量

        Returns:
            count: 排队中的任务数
        """
        with self._get_db() as conn:
            row = conn.execute(
                "SELECT COUNT(*) as cnt FROM code_jobs WHERE state = 'queued'"
            ).fetchone()
            return row["cnt"] if row else 0

    def get_stats(self) -> dict:
        """获取队列统计

        Returns:
            stats: 统计信息字典
        """
        with self._get_db() as conn:
            # 按状态统计
            rows = conn.execute(
                """SELECT state, COUNT(*) as cnt
                   FROM code_jobs
                   GROUP BY state"""
            ).fetchall()
            by_state = {r["state"]: r["cnt"] for r in rows}

            # 按类型统计
            type_rows = conn.execute(
                """SELECT type, COUNT(*) as cnt
                   FROM code_jobs
                   GROUP BY type"""
            ).fetchall()
            by_type = {r["type"]: r["cnt"] for r in type_rows}

            # 按来源统计
            source_rows = conn.execute(
                """SELECT source, COUNT(*) as cnt
                   FROM code_jobs
                   GROUP BY source"""
            ).fetchall()
            by_source = {r["source"]: r["cnt"] for r in source_rows}

            return {
                "by_state": by_state,
                "by_type": by_type,
                "by_source": by_source,
                "total": sum(by_state.values()),
            }

    def get_job(self, job_id: str) -> Optional[dict]:
        """获取单个任务

        Args:
            job_id: 任务 ID

        Returns:
            job: 任务数据，不存在则返回 None
        """
        with self._get_db() as conn:
            row = conn.execute(
                "SELECT * FROM code_jobs WHERE id = ?", (job_id,)
            ).fetchone()
            return dict(row) if row else None

    def list_jobs(
        self,
        state: Optional[str] = None,
        job_type: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """列出任务

        Args:
            state: 按状态过滤
            job_type: 按类型过滤
            source: 按来源过滤
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            jobs: 任务列表
        """
        conditions = []
        params = []

        if state:
            conditions.append("state = ?")
            params.append(state)
        if job_type:
            conditions.append("type = ?")
            params.append(job_type)
        if source:
            conditions.append("source = ?")
            params.append(source)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        params.extend([limit, offset])

        with self._get_db() as conn:
            rows = conn.execute(
                f"""SELECT * FROM code_jobs
                   {where_clause}
                   ORDER BY created_at DESC
                   LIMIT ? OFFSET ?""",
                params,
            ).fetchall()
            return [dict(r) for r in rows]

    def renew_lock(self, job_id: str, worker_id: str, timeout_minutes: int = 30) -> bool:
        """续期任务锁

        Args:
            job_id: 任务 ID
            worker_id: worker 标识
            timeout_minutes: 锁超时时间（分钟）

        Returns:
            success: 是否成功续期
        """
        lock_expires = (datetime.utcnow() + timedelta(minutes=timeout_minutes)).isoformat()
        now = datetime.utcnow().isoformat()

        with self._get_db() as conn:
            # 只能续期自己持有的锁
            cursor = conn.execute(
                """UPDATE code_jobs
                   SET lock_expires_at = ?, updated_at = ?
                   WHERE id = ? AND lock_owner = ?""",
                (lock_expires, now, job_id, worker_id),
            )
            return cursor.rowcount > 0

    def cleanup_expired_locks(self, timeout_minutes: int = 60) -> int:
        """清理过期锁

        Args:
            timeout_minutes: 锁超时时间（分钟）

        Returns:
            count: 清理的任务数
        """
        now = datetime.utcnow().isoformat()

        with self._get_db() as conn:
            # 将锁过期的 running 任务改回 queued
            cursor = conn.execute(
                """UPDATE code_jobs
                   SET state = 'queued',
                       lock_owner = NULL,
                       lock_expires_at = NULL,
                       updated_at = ?
                   WHERE state = 'running'
                     AND lock_expires_at < ?""",
                (now, now),
            )
            return cursor.rowcount

    def reset_job(self, job_id: str, state: str = "queued") -> bool:
        """重置任务状态

        Args:
            job_id: 任务 ID
            state: 目标状态 (默认 'queued')

        Returns:
            success: 是否成功重置
        """
        now = datetime.utcnow().isoformat()

        with self._get_db() as conn:
            cursor = conn.execute(
                """UPDATE code_jobs
                   SET state = ?,
                       lock_owner = NULL,
                       lock_expires_at = NULL,
                       started_at = NULL,
                       completed_at = NULL,
                       error = NULL,
                       retry_count = 0,
                       updated_at = ?
                   WHERE id = ?""",
                (state, now, job_id),
            )
            return cursor.rowcount > 0
