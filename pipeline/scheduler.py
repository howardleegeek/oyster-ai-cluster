#!/usr/bin/env python3
"""Night Shift Scheduler - 夜间自动调度器"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import List, Dict, Optional

from pipeline.code_queue import CodeQueue

DB_PATH = Path(__file__).parent / "pipeline.db"
CRON_LOG_PATH = Path(__file__).parent / "night_shift.log"


# 高风险文件模式（自动标记为 needs_human）
HIGH_RISK_PATTERNS = [
    "**/secrets/**",
    "**/.env*",
    "**/credentials*",
    "**/keys/**",
    "**/*.pem",
    "**/*.key",
    "**/auth/**",
    "**/security/**",
    "**/wallet/**",
    "**/crypto/**",
]


@contextmanager
def get_db():
    """Context manager for database connection"""
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


def init_scheduler_tables():
    """初始化调度器相关表"""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS scheduler_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id TEXT NOT NULL,
                run_type TEXT NOT NULL CHECK(run_type IN ('night_batch', 'ci_scan')),
                started_at TEXT NOT NULL,
                finished_at TEXT,
                jobs_claimed INTEGER DEFAULT 0,
                jobs_completed INTEGER DEFAULT 0,
                jobs_failed INTEGER DEFAULT 0,
                error TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_scheduler_worker ON scheduler_runs(worker_id);
            CREATE INDEX IF NOT EXISTS idx_scheduler_date ON scheduler_runs(started_at);

            CREATE TABLE IF NOT EXISTS nightly_prs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pr_url TEXT NOT NULL UNIQUE,
                repo TEXT NOT NULL,
                created_at TEXT NOT NULL,
                job_id TEXT,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending','in_progress','completed','failed'))
            );
            CREATE INDEX IF NOT EXISTS idx_nightly_prs_repo ON nightly_prs(repo);
            CREATE INDEX IF NOT EXISTS idx_nightly_prs_date ON nightly_prs(created_at);
        """)


class BatchResult:
    """批量执行结果"""

    def __init__(
        self,
        worker_id: str,
        run_type: str,
        jobs_claimed: int = 0,
        jobs_completed: int = 0,
        jobs_failed: int = 0,
        error: Optional[str] = None,
    ):
        self.worker_id = worker_id
        self.run_type = run_type
        self.jobs_claimed = jobs_claimed
        self.jobs_completed = jobs_completed
        self.jobs_failed = jobs_failed
        self.error = error
        self.started_at = datetime.utcnow().isoformat()
        self.finished_at = None

    def finish(self):
        """标记为完成"""
        self.finished_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "worker_id": self.worker_id,
            "run_type": self.run_type,
            "jobs_claimed": self.jobs_claimed,
            "jobs_completed": self.jobs_completed,
            "jobs_failed": self.jobs_failed,
            "error": self.error,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }


class NightShiftScheduler:
    """夜间调度器

    负责在夜间（1:00-6:00）批量处理待修复任务，并监控 CI 失败。
    """

    # 保险丝配置
    MAX_PRS_PER_NIGHT = 5
    MAX_CONCURRENT_PER_REPO = 2

    # 时间窗口 (24/7 全天候)
    NIGHT_START = "00:00"
    NIGHT_END = "23:59"
    CI_SCAN_INTERVAL = 900  # 15 分钟

    def __init__(self, queue: Optional[CodeQueue] = None):
        """初始化 NightShiftScheduler

        Args:
            queue: CodeQueue 实例，默认创建新实例
        """
        init_scheduler_tables()
        self.queue = queue or CodeQueue()

    def should_run(self) -> bool:
        """判断是否应该运行

        Returns:
            should_run: 是否应该运行
        """
        now = datetime.utcnow()
        current_time = now.strftime("%H:%M")

        # 检查是否在夜间窗口
        is_night_time = self.NIGHT_START <= current_time < self.NIGHT_END

        # 检查保险丝
        has_capacity = self.check_fuse()

        return is_night_time and has_capacity

    def should_scan_ci(self, last_scan_time: Optional[str] = None) -> bool:
        """判断是否应该扫描 CI 失败

        Args:
            last_scan_time: 上次扫描时间

        Returns:
            should_scan: 是否应该扫描
        """
        now = datetime.utcnow()

        if last_scan_time is None:
            return True

        last_scan = datetime.fromisoformat(last_scan_time)
        elapsed = (now - last_scan).total_seconds()

        return elapsed >= self.CI_SCAN_INTERVAL

    def check_fuse(self) -> bool:
        """检查保险丝状态

        Returns:
            has_capacity: 是否有容量运行
        """
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

        with get_db() as conn:
            # 检查今晚创建的 PR 数量
            row = conn.execute(
                """SELECT COUNT(*) as cnt
                   FROM nightly_prs
                   WHERE created_at >= ?""",
                (today_start,),
            ).fetchone()

            prs_tonight = row["cnt"] if row else 0

            if prs_tonight >= self.MAX_PRS_PER_NIGHT:
                return False

            # 检查每个仓库的并发数
            repo_rows = conn.execute(
                """SELECT repo, COUNT(*) as cnt
                   FROM nightly_prs
                   WHERE created_at >= ? AND status IN ('pending', 'in_progress')
                   GROUP BY repo""",
                (today_start,),
            ).fetchall()

            for repo_row in repo_rows:
                if repo_row["cnt"] >= self.MAX_CONCURRENT_PER_REPO:
                    return False

        return True

    def scan_backlog(self) -> List[dict]:
        """扫描待处理任务

        Returns:
            tasks: 待处理任务列表
        """
        # 获取排队中的高优先级任务
        jobs = self.queue.list_jobs(state="queued", limit=50)

        # 过滤出适合夜间处理的任务
        # 优先处理：failing_ci > github_issue > todo_scan > manual
        source_priority = {
            "failing_ci": 0,
            "github_issue": 1,
            "todo_scan": 2,
            "manual": 3,
        }

        jobs.sort(key=lambda j: source_priority.get(j["source"], 99))

        return jobs[:10]  # 最多返回 10 个任务

    def scan_ci_failures(self, repo: Optional[str] = None) -> List[dict]:
        """扫描 CI 失败任务

        Args:
            repo: 仓库名称，None 表示扫描所有仓库

        Returns:
            ci_jobs: CI 失败任务列表
        """
        jobs = self.queue.list_jobs(state="queued", source="failing_ci", limit=20)

        # 如果指定了仓库，进行过滤
        if repo:
            jobs = [j for j in jobs if self._extract_repo_from_job(j) == repo]

        return jobs

    def _extract_repo_from_job(self, job: dict) -> Optional[str]:
        """从任务中提取仓库名称

        Args:
            job: 任务字典

        Returns:
            repo: 仓库名称
        """
        try:
            payload = json.loads(job.get("payload", "{}"))
            return payload.get("repo") or payload.get("project")
        except (json.JSONDecodeError, TypeError):
            return None

    def is_high_risk_file(self, file_path: str) -> bool:
        """检查是否为高风险文件

        Args:
            file_path: 文件路径

        Returns:
            is_risky: 是否为高风险文件
        """
        import fnmatch

        for pattern in HIGH_RISK_PATTERNS:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False

    def run_batch(self, worker_id: str, max_jobs: int = 3) -> BatchResult:
        """批量运行任务

        Args:
            worker_id: worker 标识
            max_jobs: 最多认领的任务数

        Returns:
            result: 批量执行结果
        """
        result = BatchResult(worker_id, "night_batch")

        try:
            # 检查保险丝
            if not self.check_fuse():
                result.error = "Fuse triggered: no capacity"
                result.finish()
                return result

            # 记录运行开始
            run_id = self._record_run_start(worker_id, "night_batch")

            # 扫描待处理任务
            backlog = self.scan_backlog()

            if not backlog:
                result.error = "No jobs in backlog"
                result.finish()
                return result

            # 认领任务
            claimed_jobs = self.queue.claim(
                worker_id, max_jobs=min(max_jobs, len(backlog))
            )
            result.jobs_claimed = len(claimed_jobs)

            # 处理每个任务
            for job in claimed_jobs:
                job_id = job["id"]
                repo = self._extract_repo_from_job(job)

                # 检查是否为高风险任务
                payload = json.loads(job.get("payload", "{}"))
                files_to_modify = payload.get("files", [])
                is_high_risk = any(self.is_high_risk_file(f) for f in files_to_modify)

                try:
                    if is_high_risk:
                        # 高风险任务直接标记为 needs_human
                        self.queue.release(
                            job_id, "needs_human", error="High risk file detected"
                        )
                        result.jobs_failed += 1
                    else:
                        # 正常处理任务
                        # 这里应该调用 code_pipeline 来实际执行
                        # 目前简化为标记为完成
                        self.queue.release(job_id, "done")
                        result.jobs_completed += 1

                        # 记录 PR
                        if repo:
                            self.record_pr(f"pr://{repo}/{job_id}", repo, job_id)

                except Exception as e:
                    self.queue.release(job_id, "failed", error=str(e))
                    result.jobs_failed += 1

            result.finish()
            self._record_run_complete(run_id, result)

        except Exception as e:
            result.error = str(e)
            result.finish()

        return result

    def run_ci_scan(self, worker_id: str, max_jobs: int = 2) -> BatchResult:
        """运行 CI 失败扫描

        Args:
            worker_id: worker 标识
            max_jobs: 最多认领的任务数

        Returns:
            result: 批量执行结果
        """
        result = BatchResult(worker_id, "ci_scan")

        try:
            # 记录运行开始
            run_id = self._record_run_start(worker_id, "ci_scan")

            # 扫描 CI 失败任务
            ci_jobs = self.scan_ci_failures()

            if not ci_jobs:
                result.error = "No CI failures found"
                result.finish()
                return result

            # 认领任务
            claimed_jobs = self.queue.claim(
                worker_id, max_jobs=min(max_jobs, len(ci_jobs))
            )
            result.jobs_claimed = len(claimed_jobs)

            # 处理每个任务
            for job in claimed_jobs:
                job_id = job["id"]
                repo = self._extract_repo_from_job(job)

                try:
                    # 处理 CI 失败任务
                    # 这里应该调用 code_pipeline 来实际执行
                    # 目前简化为标记为完成
                    self.queue.release(job_id, "done")
                    result.jobs_completed += 1

                    # 记录 PR
                    if repo:
                        self.record_pr(f"pr://{repo}/{job_id}", repo, job_id)

                except Exception as e:
                    self.queue.release(job_id, "failed", error=str(e))
                    result.jobs_failed += 1

            result.finish()
            self._record_run_complete(run_id, result)

        except Exception as e:
            result.error = str(e)
            result.finish()

        return result

    def record_pr(self, pr_url: str, repo: str, job_id: Optional[str] = None):
        """记录 PR（更新保险丝）

        Args:
            pr_url: PR URL
            repo: 仓库名称
            job_id: 关联的任务 ID
        """
        now = datetime.utcnow().isoformat()

        with get_db() as conn:
            # 使用 INSERT OR IGNORE 避免重复
            conn.execute(
                """INSERT OR IGNORE INTO nightly_prs (pr_url, repo, created_at, job_id)
                   VALUES (?, ?, ?, ?)""",
                (pr_url, repo, now, job_id),
            )

    def update_pr_status(self, pr_url: str, status: str):
        """更新 PR 状态

        Args:
            pr_url: PR URL
            status: 新状态 ('pending', 'in_progress', 'completed', 'failed')
        """
        with get_db() as conn:
            conn.execute(
                """UPDATE nightly_prs
                   SET status = ?
                   WHERE pr_url = ?""",
                (status, pr_url),
            )

    def _record_run_start(self, worker_id: str, run_type: str) -> int:
        """记录运行开始

        Args:
            worker_id: worker 标识
            run_type: 运行类型

        Returns:
            run_id: 运行记录 ID
        """
        with get_db() as conn:
            cur = conn.execute(
                """INSERT INTO scheduler_runs (worker_id, run_type, started_at)
                   VALUES (?, ?, ?)""",
                (worker_id, run_type, datetime.utcnow().isoformat()),
            )
            return cur.lastrowid

    def _record_run_complete(self, run_id: int, result: BatchResult):
        """记录运行完成

        Args:
            run_id: 运行记录 ID
            result: 批量执行结果
        """
        with get_db() as conn:
            conn.execute(
                """UPDATE scheduler_runs
                   SET finished_at = ?,
                       jobs_claimed = ?,
                       jobs_completed = ?,
                       jobs_failed = ?,
                       error = ?
                   WHERE id = ?""",
                (
                    result.finished_at,
                    result.jobs_claimed,
                    result.jobs_completed,
                    result.jobs_failed,
                    result.error,
                    run_id,
                ),
            )

    def get_stats(self) -> Dict:
        """获取统计信息

        Returns:
            stats: 统计信息字典
        """
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        night_start = now.replace(hour=1, minute=0, second=0, microsecond=0).isoformat()

        with get_db() as conn:
            # 今晚的 PR 统计
            pr_row = conn.execute(
                """SELECT COUNT(*) as total,
                          SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                          SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                          SUM(CASE WHEN status IN ('pending', 'in_progress') THEN 1 ELSE 0 END) as pending
                   FROM nightly_prs
                   WHERE created_at >= ?""",
                (today_start,),
            ).fetchone()

            pr_stats = dict(pr_row) if pr_row else {}

            # 今晚的运行统计
            run_rows = conn.execute(
                """SELECT run_type, COUNT(*) as cnt,
                          SUM(jobs_claimed) as claimed,
                          SUM(jobs_completed) as completed,
                          SUM(jobs_failed) as failed
                   FROM scheduler_runs
                   WHERE started_at >= ?
                   GROUP BY run_type""",
                (night_start,),
            ).fetchall()

            run_stats = {}
            for row in run_rows:
                run_stats[row["run_type"]] = {
                    "runs": row["cnt"],
                    "claimed": row["claimed"] or 0,
                    "completed": row["completed"] or 0,
                    "failed": row["failed"] or 0,
                }

            # 保险丝状态
            has_capacity = self.check_fuse()

            # 队列统计
            queue_stats = self.queue.get_stats()

            return {
                "fuse": {
                    "has_capacity": has_capacity,
                    "max_prs_per_night": self.MAX_PRS_PER_NIGHT,
                    "max_concurrent_per_repo": self.MAX_CONCURRENT_PER_REPO,
                    "prs_created_tonight": pr_stats.get("total", 0),
                    "prs_pending": pr_stats.get("pending", 0),
                    "prs_completed": pr_stats.get("completed", 0),
                    "prs_failed": pr_stats.get("failed", 0),
                },
                "runs": run_stats,
                "queue": queue_stats,
                "timestamp": now.isoformat(),
            }

    def get_last_ci_scan_time(self) -> Optional[str]:
        """获取上次 CI 扫描时间

        Returns:
            scan_time: 上次扫描时间，None 表示从未扫描
        """
        with get_db() as conn:
            row = conn.execute(
                """SELECT started_at
                   FROM scheduler_runs
                   WHERE run_type = 'ci_scan'
                   ORDER BY started_at DESC
                   LIMIT 1"""
            ).fetchone()

            return row["started_at"] if row else None

    def cleanup_old_records(self, days: int = 30):
        """清理旧记录

        Args:
            days: 保留天数
        """
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

        with get_db() as conn:
            # 清理旧的 scheduler_runs
            conn.execute(
                """DELETE FROM scheduler_runs
                   WHERE started_at < ?""",
                (cutoff,),
            )

            # 清理旧的 nightly_prs
            conn.execute(
                """DELETE FROM nightly_prs
                   WHERE created_at < ? AND status IN ('completed', 'failed')""",
                (cutoff,),
            )


def main():
    """主函数 - 用于测试"""
    import sys

    scheduler = NightShiftScheduler()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "should_run":
            print(f"Should run: {scheduler.should_run()}")

        elif cmd == "stats":
            stats = scheduler.get_stats()
            print(json.dumps(stats, indent=2))

        elif cmd == "run_batch":
            worker_id = sys.argv[2] if len(sys.argv) > 2 else "night_worker"
            max_jobs = int(sys.argv[3]) if len(sys.argv) > 3 else 3
            result = scheduler.run_batch(worker_id, max_jobs)
            print(json.dumps(result.to_dict(), indent=2))

        elif cmd == "scan_ci":
            worker_id = sys.argv[2] if len(sys.argv) > 2 else "ci_worker"
            max_jobs = int(sys.argv[3]) if len(sys.argv) > 3 else 2
            result = scheduler.run_ci_scan(worker_id, max_jobs)
            print(json.dumps(result.to_dict(), indent=2))

        elif cmd == "scan_backlog":
            backlog = scheduler.scan_backlog()
            print(f"Found {len(backlog)} jobs in backlog")
            for job in backlog[:5]:
                print(f"  - {job['id']}: {job['source']}")

        else:
            print(f"Unknown command: {cmd}")
            sys.exit(1)
    else:
        # 默认显示统计
        stats = scheduler.get_stats()
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
