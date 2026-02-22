#!/usr/bin/env python3
"""
Memory Learner - Scheduled job to learn from dispatch tasks

This module periodically:
1. Checks for recently completed/failed tasks
2. Extracts patterns and lessons
3. Stores them in memory for future reference
"""

import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add dispatch to path
sys.path.insert(0, str(Path(__file__).parent))

from memory_store import MemoryStore


def learn_from_recent_tasks(db_path: str, hours: int = 24):
    """Learn from tasks completed in the last N hours"""
    store = MemoryStore()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Get tasks from last N hours
    cutoff = datetime.now() - timedelta(hours=hours)

    tasks = conn.execute(
        """
        SELECT id, status, error, node, duration_seconds, spec_file
        FROM tasks 
        WHERE completed_at > ?
        AND status IN ('completed', 'failed')
        ORDER BY completed_at DESC
    """,
        (cutoff.isoformat(),),
    ).fetchall()

    conn.close()

    learned = 0

    for task in tasks:
        # Extract key info
        content = f"Task {task['id']}: status={task['status']}"

        if task["duration_seconds"]:
            content += f", duration={task['duration_seconds']:.1f}s"

        if task["node"]:
            content += f", node={task['node']}"

        if task["error"]:
            content += f", error={task['error'][:100]}"

        # Determine memory type
        mem_type = "task" if task["status"] == "completed" else "error"

        # Add to memory
        store.add(
            content,
            mem_type,
            {
                "task_id": task["id"],
                "status": task["status"],
                "node": task["node"],
                "error": task["error"],
                "learned_at": datetime.now().isoformat(),
            },
        )

        learned += 1

    return learned


def get_memory_recommendations(problem: str, limit: int = 3):
    """Get memory-powered recommendations for a problem"""
    store = MemoryStore()

    # Search for similar problems
    results = store.search(problem, memory_type="error", limit=limit)

    recommendations = []
    for r in results:
        recommendations.append(
            {
                "similar_problem": r["content"],
                "score": r["score"],
                "metadata": r.get("metadata", {}),
            }
        )

    return recommendations


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Memory Learner")
    parser.add_argument("--learn", action="store_true", help="Learn from recent tasks")
    parser.add_argument("--hours", type=int, default=24, help="Hours to look back")
    parser.add_argument("--recommend", type=str, help="Get recommendations for problem")
    parser.add_argument("--stats", action="store_true", help="Show memory stats")

    args = parser.parse_args()

    if args.learn:
        db_path = Path.home() / "Downloads" / "dispatch" / "dispatch.db"
        learned = learn_from_recent_tasks(str(db_path), args.hours)
        print(f"Learned from {learned} tasks")

    elif args.recommend:
        recommendations = get_memory_recommendations(args.recommend)
        print(json.dumps(recommendations, indent=2))

    elif args.stats:
        store = MemoryStore()
        stats = store.get_stats()
        print(json.dumps(stats, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
