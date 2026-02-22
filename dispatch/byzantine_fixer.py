#!/usr/bin/env python3
"""
Byzantine Analysis & Fixer for Dispatch System
检测并修复系统拜占庭问题（不一致状态、孤立数据、时间戳缺失等）
"""

import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Optional, Dict, List, Any
from pathlib import Path
import json


@contextmanager
def get_db(db_path):
    """Context manager for database connection"""
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class ByzantineFixer:
    """检测并修复系统不一致问题"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def check_all(self) -> dict:
        """执行全部检查"""
        return {
            "orphaned_tasks": self.find_orphaned_tasks(),
            "duplicate_ids": self.find_duplicates(),
            "stuck_tasks": self.find_stuck_tasks(),
            "running_without_node": self.find_running_without_node(),
            "completed_without_time": self.find_completed_without_time(),
            "negative_slots": self.find_negative_slots(),
            "stale_locks": self.find_stale_locks(),
        }

    def find_orphaned_tasks(self) -> List[Dict]:
        """无 project 的任务"""
        with get_db(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE project IS NULL OR project = ''"
            ).fetchall()
            return [dict(r) for r in rows]

    def find_duplicates(self) -> List[Dict]:
        """重复 ID"""
        with get_db(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT id, COUNT(*) as count, GROUP_CONCAT(project) as projects
                FROM tasks
                GROUP BY id HAVING COUNT(*) > 1
                """
            ).fetchall()
            return [dict(r) for r in rows]

    def find_stuck_tasks(self, hours: int = 24) -> List[Dict]:
        """卡住的任务 (>24h)"""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        with get_db(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT * FROM tasks
                WHERE status = 'running'
                AND started_at IS NOT NULL
                AND datetime(started_at) < ?
                ORDER BY started_at
                """,
                (cutoff,),
            ).fetchall()
            return [dict(r) for r in rows]

    def find_running_without_node(self) -> List[Dict]:
        """运行中但无节点"""
        with get_db(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT * FROM tasks
                WHERE status IN ('claimed', 'running')
                AND (node IS NULL OR node = '')
                """
            ).fetchall()
            return [dict(r) for r in rows]

    def find_completed_without_time(self) -> List[Dict]:
        """已完成但无完成时间"""
        with get_db(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT * FROM tasks
                WHERE status = 'completed'
                AND (completed_at IS NULL OR completed_at = '')
                ORDER BY id
                """
            ).fetchall()
            return [dict(r) for r in rows]

    def find_negative_slots(self) -> List[Dict]:
        """负 slots 节点"""
        with get_db(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT name, slots, running_count FROM nodes
                WHERE slots < 0
                """
            ).fetchall()
            return [dict(r) for r in rows]

    def find_stale_locks(self, hours: int = 24) -> List[Dict]:
        """陈旧文件锁"""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        with get_db(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT * FROM file_locks
                WHERE datetime(locked_at) < ?
                ORDER BY locked_at
                """,
                (cutoff,),
            ).fetchall()
            return [dict(r) for r in rows]

    def fix_completed_without_timestamp(self) -> int:
        """修复已完成但无时间戳的任务

        策略:
        - 如果有 started_at，使用 started_at + 预估时长（默认1小时）
        - 否则使用当前时间
        """
        tasks = self.find_completed_without_time()
        fixed = 0

        with get_db(self.db_path) as conn:
            for task in tasks:
                completed_at = datetime.now().isoformat()

                if task.get("started_at"):
                    try:
                        started = datetime.fromisoformat(task["started_at"])
                        # 默认预估时长1小时，除非有 duration_seconds
                        duration = task.get("duration_seconds", 3600)
                        completed_at = (started + timedelta(seconds=duration)).isoformat()
                    except (ValueError, TypeError):
                        # started_at 无效，使用当前时间
                        pass

                conn.execute(
                    "UPDATE tasks SET completed_at = ? WHERE id = ?",
                    (completed_at, task["id"]),
                )
                fixed += 1

            conn.commit()

        return fixed

    def fix_stale_locks(self, hours: int = 24) -> int:
        """清理陈旧文件锁"""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()

        with get_db(self.db_path) as conn:
            cursor = conn.execute(
                """
                DELETE FROM file_locks
                WHERE datetime(locked_at) < ?
                """,
                (cutoff,),
            )
            deleted = cursor.rowcount
            conn.commit()

        return deleted

    def fix_stuck_tasks(self, hours: int = 24) -> int:
        """修复卡住的任务

        策略: 标记为 failed，添加错误信息
        """
        tasks = self.find_stuck_tasks(hours)
        fixed = 0

        with get_db(self.db_path) as conn:
            for task in tasks:
                # 释放节点资源
                if task.get("node"):
                    conn.execute(
                        "UPDATE nodes SET running_count = running_count - 1 WHERE name = ?",
                        (task["node"],),
                    )

                # 标记任务为失败
                conn.execute(
                    "UPDATE tasks SET status = 'failed', error = 'byzantine_timeout' WHERE id = ?",
                    (task["id"],),
                )
                fixed += 1

            conn.commit()

        return fixed

    def auto_fix(self) -> Dict[str, int]:
        """自动修复所有可修复的问题"""
        results = {
            "completed_without_time": self.fix_completed_without_timestamp(),
            "stale_locks": self.fix_stale_locks(),
            "stuck_tasks": self.fix_stuck_tasks(),
        }
        return results

    def generate_report(self) -> str:
        """生成拜占庭分析报告"""
        checks = self.check_all()

        report_lines = ["=" * 80]
        report_lines.append("BYZANTINE ANALYSIS REPORT")
        report_lines.append(f"Generated at: {datetime.now().isoformat()}")
        report_lines.append("=" * 80)
        report_lines.append("")

        # Summary table
        report_lines.append("# Summary")
        report_lines.append("")
        report_lines.append("| # | Issue Type | Count | Status |")
        report_lines.append("|---|------------|-------|--------|")

        issues = [
            ("Orphaned Tasks", checks["orphaned_tasks"]),
            ("Duplicate IDs", checks["duplicate_ids"]),
            ("Stuck Tasks (>24h)", checks["stuck_tasks"]),
            ("Running Without Node", checks["running_without_node"]),
            ("Completed Without Time", checks["completed_without_time"]),
            ("Negative Slots", checks["negative_slots"]),
            ("Stale Locks (>24h)", checks["stale_locks"]),
        ]

        for i, (name, items) in enumerate(issues, 1):
            status = "✅" if len(items) == 0 else "⚠️" if len(items) < 5 else "❌"
            report_lines.append(f"| {i} | {name} | {len(items)} | {status} |")

        report_lines.append("")
        report_lines.append("# Details")
        report_lines.append("")

        # Details for each issue type
        if checks["orphaned_tasks"]:
            report_lines.append("## Orphaned Tasks (no project)")
            for task in checks["orphaned_tasks"]:
                report_lines.append(f"  - {task['id']}")
            report_lines.append("")

        if checks["duplicate_ids"]:
            report_lines.append("## Duplicate IDs")
            for dup in checks["duplicate_ids"]:
                report_lines.append(f"  - {dup['id']} appears {dup['count']} times in {dup['projects']}")
            report_lines.append("")

        if checks["stuck_tasks"]:
            report_lines.append("## Stuck Tasks (running > 24h)")
            for task in checks["stuck_tasks"]:
                started = task.get("started_at", "unknown")
                report_lines.append(f"  - {task['id']} on node {task.get('node', 'N/A')} started at {started}")
            report_lines.append("")

        if checks["running_without_node"]:
            report_lines.append("## Tasks Running Without Node")
            for task in checks["running_without_node"]:
                report_lines.append(f"  - {task['id']} status={task['status']}")
            report_lines.append("")

        if checks["completed_without_time"]:
            report_lines.append("## Completed Tasks Without Timestamp")
            for task in checks["completed_without_time"]:
                report_lines.append(f"  - {task['id']} started={task.get('started_at', 'N/A')}")
            report_lines.append("")

        if checks["negative_slots"]:
            report_lines.append("## Nodes with Negative Slots")
            for node in checks["negative_slots"]:
                report_lines.append(f"  - {node['name']}: slots={node['slots']}, running={node['running_count']}")
            report_lines.append("")

        if checks["stale_locks"]:
            report_lines.append("## Stale File Locks (> 24h)")
            for lock in checks["stale_locks"]:
                report_lines.append(f"  - {lock['file_path']} locked by {lock['task_id']} at {lock['locked_at']}")
            report_lines.append("")

        # Health score
        total_issues = sum(len(items) for _, items in issues)
        if total_issues == 0:
            health = "HEALTHY"
        elif total_issues < 5:
            health = "WARN"
        else:
            health = "CRITICAL"

        report_lines.append("# Health Status")
        report_lines.append(f"System Health: {health}")
        report_lines.append(f"Total Issues: {total_issues}")
        report_lines.append("")
        report_lines.append("=" * 80)

        return "\n".join(report_lines)

    def print_report(self):
        """打印报告到控制台"""
        print(self.generate_report())


def create_fixer(db_path: str = "dispatch.db") -> ByzantineFixer:
    """创建 ByzantineFixer 实例"""
    return ByzantineFixer(db_path)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Byzantine Analysis & Fixer")
    parser.add_argument("--db", default="dispatch.db", help="Database path")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues")
    parser.add_argument("--report", action="store_true", help="Generate report")
    parser.add_argument("--check", action="store_true", help="Run checks and print summary")

    args = parser.parse_args()

    fixer = create_fixer(args.db)

    if args.check or args.report:
        fixer.print_report()

    if args.fix:
        print("\nAuto-fixing issues...")
        results = fixer.auto_fix()
        print("Fix results:")
        for issue_type, count in results.items():
            print(f"  - {issue_type}: {count}")
        print("\nRe-running checks...")
        fixer.print_report()


if __name__ == "__main__":
    main()
