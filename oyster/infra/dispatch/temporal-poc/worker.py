"""
Temporal Worker for Dispatch System
====================================

Run on each worker node:
    python3 worker.py

Two modes controlled by WORKER_ROLE env:
- "activity" (default): Edge nodes — only runs activities (run_coding_task).
  Workflows stay on the stable Mac/server. If a spot node gets reclaimed,
  only the activity retries, not the entire project workflow.
- "full": Mac/stable server — runs both workflows AND activities.

The worker automatically:
- Connects to Temporal server
- Polls for tasks (Pull model - no SSH needed)
- Executes activities (and optionally workflows)
- Heartbeats (replaces guardian health checks)
- Retries on failure (replaces reaper)
"""

import asyncio
import os
from datetime import timedelta

from temporalio.client import Client
from temporalio.service import KeepAliveConfig
from temporalio.worker import Worker

from activities import run_coding_task, check_dependency_merged, send_to_repair_factory, start_task_workflow, wait_for_task_workflow


TEMPORAL_HOST = os.environ.get("TEMPORAL_HOST", "localhost:7233")
TASK_QUEUE = os.environ.get("TASK_QUEUE", "dispatch-tasks")
WORKER_NAME = os.environ.get("WORKER_NAME", os.uname().nodename)
MAX_CONCURRENT = int(
    os.environ.get("MAX_CONCURRENT", "4")
)  # Cloud nodes override to 20 via env
WORKER_ROLE = os.environ.get("WORKER_ROLE", "activity")


async def main():
    print(f"Connecting to Temporal at {TEMPORAL_HOST}...", flush=True)
    # Fix: Configure gRPC keep-alive for cross-Tailscale stability
    # Without this, HTTP/2 KeepAliveTimedOut kills activities mid-execution
    client = await Client.connect(
        TEMPORAL_HOST,
        keep_alive_config=KeepAliveConfig(
            interval_millis=30000,  # ping every 30s
            timeout_millis=15000,  # 15s timeout for pong
        ),
    )

    # All workers run both workflows and activities now.
    # TaskWorkflow (child) needs to run on any node that picks up the task.
    # BatchWorkflow (parent) is lightweight orchestration only.
    from workflows import BatchWorkflow, TaskWorkflow

    workflows = [BatchWorkflow, TaskWorkflow]
    print(f"Role: FULL (BatchWorkflow + TaskWorkflow + activities)", flush=True)

    print(f"Starting worker '{WORKER_NAME}' on queue '{TASK_QUEUE}'", flush=True)
    print(f"Max concurrent activities: {MAX_CONCURRENT}", flush=True)
    print(f"Waiting for tasks... (Ctrl+C to stop)", flush=True)

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=workflows,
        activities=[run_coding_task, check_dependency_merged, send_to_repair_factory, start_task_workflow, wait_for_task_workflow],
        max_concurrent_activities=MAX_CONCURRENT,
        identity=WORKER_NAME,
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
