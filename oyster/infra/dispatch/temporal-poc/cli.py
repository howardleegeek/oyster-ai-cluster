"""
Temporal CLI for Dispatch System POC
=====================================

Replaces: dispatch.py start/status/collect/report commands
Lines: ~100 (vs ~1000+ in dispatch.py CLI code)

Usage:
    python3 cli.py start <project>    # Start a project workflow
    python3 cli.py status <project>   # Check workflow status
    python3 cli.py demo               # Run demo with fake specs
"""

import asyncio
import json
import sys
import os
from pathlib import Path

from temporalio.client import Client

from workflows import BatchWorkflow, TaskSpec
import yaml


def parse_spec_metadata(spec_path):
    text = Path(spec_path).read_text()
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                meta = {}
            content = parts[2].strip()
            return meta, content
    return {}, text


def load_specs_for_project(project) -> list[TaskSpec]:
    base_dir = Path("~/Downloads/oyster/specs").expanduser()
    paths_to_try = [
        base_dir / project,
        base_dir / project / "PROJECTS" / "SPEC",
        Path("~/Downloads/specs").expanduser() / project,
        base_dir,
    ]
    specs_path = None
    for p in paths_to_try:
        if p.exists() and (list(p.glob("S*.md")) or list(p.glob("P*.md"))):
            specs_path = p
            break

    if not specs_path:
        print(f"Error: No specs found for project {project}")
        return []

    tasks = []
    for spec_file in sorted(specs_path.glob("*.md")):
        if not (spec_file.stem.startswith("S") or spec_file.stem.startswith("P")):
            continue

        task_id = spec_file.stem
        meta, content = parse_spec_metadata(spec_file)

        tasks.append(
            TaskSpec(
                task_id=meta.get("task_id", task_id),
                project=project,
                spec_file=str(spec_file),
                spec_content=content,
                depends_on=meta.get("depends_on", []),
                estimated_minutes=meta.get("estimated_minutes", 30),
                max_retries=3,  # Reduced from 10 to prevent retry amplification storms
            )
        )
    return tasks


TEMPORAL_HOST = os.environ.get("TEMPORAL_HOST", "localhost:7233")
TASK_QUEUE = os.environ.get("TASK_QUEUE", "dispatch-tasks")


async def start_project(project: str, specs: list[TaskSpec]):
    """Start a project workflow."""
    client = await Client.connect(TEMPORAL_HOST)

    handle = await client.start_workflow(
        BatchWorkflow.run,
        specs,
        id=f"project-{project}",
        task_queue=TASK_QUEUE,
    )

    print(f"Started workflow: {handle.id}")
    print(f"View at: http://localhost:8088/namespaces/default/workflows/{handle.id}")
    return handle


async def get_status(project: str):
    """Get workflow status."""
    client = await Client.connect(TEMPORAL_HOST)

    handle = client.get_workflow_handle(f"project-{project}")
    desc = await handle.describe()

    print(f"Workflow: {desc.id}")
    print(f"Status:   {desc.status.name}")
    print(f"Started:  {desc.start_time}")

    if desc.status.name == "COMPLETED":
        result = await handle.result()
        print(f"Result:   {json.dumps(result, indent=2)}")


async def demo():
    """Run a demo with fake specs to prove Temporal works."""
    specs = [
        TaskSpec(
            task_id="S01-auth",
            project="demo",
            spec_file="specs/demo/S01-auth.md",
            spec_content="Implement user authentication",
            depends_on=[],
            estimated_minutes=5,
        ),
        TaskSpec(
            task_id="S02-models",
            project="demo",
            spec_file="specs/demo/S02-models.md",
            spec_content="Create database models",
            depends_on=[],
            estimated_minutes=5,
        ),
        TaskSpec(
            task_id="S03-api",
            project="demo",
            spec_file="specs/demo/S03-api.md",
            spec_content="Build REST API endpoints",
            depends_on=["S01-auth", "S02-models"],  # DAG: depends on S01 + S02
            estimated_minutes=5,
        ),
        TaskSpec(
            task_id="S04-tests",
            project="demo",
            spec_file="specs/demo/S04-tests.md",
            spec_content="Write integration tests",
            depends_on=["S03-api"],  # DAG: depends on S03
            estimated_minutes=5,
        ),
    ]

    print("=== Temporal Dispatch POC Demo ===")
    print(f"Project: demo")
    print(f"Tasks: {len(specs)}")
    print(f"DAG: S01,S02 (parallel) -> S03 -> S04")
    print()

    handle = await start_project("demo", specs)
    print()
    print("Waiting for completion...")

    result = await handle.result()
    print()
    print(f"=== Results ===")
    print(f"Completed: {result['completed']}/{result['total']}")
    print(f"Failed: {result['failed']}/{result['total']}")
    print(f"Details: {json.dumps(result, indent=2)}")


async def stress_test(num_tasks: int = 20):
    """Run a stress test with N tasks to validate Temporal stability."""
    # Build a realistic DAG:
    #   Layer 0: 6 independent tasks (infra setup)
    #   Layer 1: 8 tasks depending on layer 0 (core features)
    #   Layer 2: 4 tasks depending on layer 1 (integration)
    #   Layer 3: 2 tasks depending on layer 2 (testing)
    task_names = [
        # Layer 0 - no deps (6 tasks)
        ("S01-db-schema", "Create database schema", []),
        ("S02-auth-model", "User authentication models", []),
        ("S03-config", "Configuration management", []),
        ("S04-logging", "Logging infrastructure", []),
        ("S05-cache", "Cache layer setup", []),
        ("S06-queue", "Message queue setup", []),
        # Layer 1 - depends on layer 0 (8 tasks)
        ("S07-user-api", "User CRUD API", ["S01-db-schema", "S02-auth-model"]),
        ("S08-product-api", "Product catalog API", ["S01-db-schema"]),
        ("S09-order-api", "Order processing API", ["S01-db-schema", "S06-queue"]),
        ("S10-payment", "Payment integration", ["S02-auth-model", "S03-config"]),
        ("S11-search", "Search service", ["S01-db-schema", "S05-cache"]),
        ("S12-notifications", "Notification service", ["S04-logging", "S06-queue"]),
        ("S13-file-upload", "File upload service", ["S03-config"]),
        ("S14-analytics", "Analytics tracking", ["S04-logging", "S05-cache"]),
        # Layer 2 - depends on layer 1 (4 tasks)
        (
            "S15-checkout",
            "Checkout flow",
            ["S07-user-api", "S09-order-api", "S10-payment"],
        ),
        (
            "S16-dashboard",
            "Admin dashboard",
            ["S07-user-api", "S08-product-api", "S14-analytics"],
        ),
        (
            "S17-email-flow",
            "Email notification flow",
            ["S12-notifications", "S07-user-api"],
        ),
        (
            "S18-review-system",
            "Product review system",
            ["S08-product-api", "S07-user-api"],
        ),
        # Layer 3 - depends on layer 2 (2 tasks)
        ("S19-e2e-tests", "End-to-end tests", ["S15-checkout", "S16-dashboard"]),
        ("S20-perf-tests", "Performance tests", ["S15-checkout", "S11-search"]),
    ]

    specs = [
        TaskSpec(
            task_id=tid,
            project="stress-test",
            spec_file=f"specs/stress/{tid}.md",
            spec_content=desc,
            depends_on=deps,
            estimated_minutes=5,
        )
        for tid, desc, deps in task_names[:num_tasks]
    ]

    print(f"=== Temporal Stress Test: {num_tasks} Tasks ===")
    print(f"DAG Layers:")
    print(
        f"  Layer 0: {sum(1 for _, _, d in task_names[:num_tasks] if not d)} independent tasks"
    )
    print(
        f"  Layer 1: {sum(1 for _, _, d in task_names[:num_tasks] if d and all(dep.startswith(('S01','S02','S03','S04','S05','S06')) for dep in d))} core feature tasks"
    )
    print(
        f"  Layer 2: {sum(1 for _, _, d in task_names[:num_tasks] if d and any(dep.startswith(('S07','S08','S09','S10','S11','S12','S13','S14')) for dep in d))} integration tasks"
    )
    print(
        f"  Layer 3: {sum(1 for _, _, d in task_names[:num_tasks] if d and any(dep.startswith(('S15','S16','S17','S18')) for dep in d))} test tasks"
    )
    print()

    import time

    t0 = time.time()
    handle = await start_project("stress-test", specs)
    print()
    print("Waiting for all tasks to complete...")
    print()

    result = await handle.result()
    elapsed = time.time() - t0

    print(f"=== Stress Test Results ===")
    print(f"Total tasks:  {result['total']}")
    print(f"Completed:    {result['completed']}/{result['total']}")
    print(f"Failed:       {result['failed']}/{result['total']}")
    print(f"Wall time:    {elapsed:.1f}s")
    print()

    # Show per-task results
    for r in result.get("results", []):
        status_icon = "✓" if r.get("status") == "completed" else "✗"
        dur = r.get("duration_seconds", 0)
        print(
            f"  {status_icon} {r['task_id']:20s}  {r.get('status', '?'):10s}  {dur:.1f}s"
        )

    print()
    if result["failed"] == 0:
        print(f"ALL {result['total']} TASKS PASSED - Temporal is stable!")
    else:
        print(f"WARNING: {result['failed']} tasks failed - check details above")


async def live(project: str):
    """Live dashboard — shows all tasks for a project with auto-refresh."""
    client = await Client.connect(TEMPORAL_HOST)

    import time as _time

    while True:
        # Clear screen
        print("\033[2J\033[H", end="")

        now = _time.strftime("%H:%M:%S")
        print(f"╔══════════════════════════════════════════════════════════════╗")
        print(f"║  📊 SHELL DISPATCH — {project:20s}    {now}      ║")
        print(f"╚══════════════════════════════════════════════════════════════╝")
        print()

        running = []
        completed = []
        failed = []
        blocked = []
        other = []

        query = f'WorkflowType="TaskWorkflow"'
        async for wf in client.list_workflows(query):
            if f"spec-{project}-" not in wf.id:
                continue
            # Extract task_id from workflow_id
            remainder = wf.id[len(f"spec-{project}-"):]
            parts = remainder.rsplit("-", 1)
            if len(parts) == 2 and len(parts[1]) == 8 and all(c in '0123456789abcdef' for c in parts[1]):
                task_id = parts[0]
            else:
                task_id = remainder

            status = wf.status.name if wf.status else "?"
            entry = (task_id, status, wf.id)

            if status == "RUNNING":
                running.append(entry)
            elif status == "COMPLETED":
                completed.append(entry)
            elif status == "FAILED":
                failed.append(entry)
            else:
                other.append(entry)

        total = len(running) + len(completed) + len(failed) + len(other)

        # Summary bar
        print(f"  ⚡ Running: {len(running):3d}  ✅ Done: {len(completed):3d}  ❌ Failed: {len(failed):3d}  📦 Total: {total}")
        if total > 0:
            pct = len(completed) / total * 100
            bar_len = 40
            filled = int(bar_len * len(completed) / total)
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f"  [{bar}] {pct:.0f}%")
        print()

        # Running tasks
        if running:
            print(f"  ⚡ RUNNING ({len(running)}):")
            for task_id, status, wid in sorted(running):
                print(f"     ▶ {task_id}")
            print()

        # Failed tasks
        if failed:
            print(f"  ❌ FAILED ({len(failed)}):")
            for task_id, status, wid in sorted(failed)[:10]:
                print(f"     ✗ {task_id}")
            if len(failed) > 10:
                print(f"     ... +{len(failed) - 10} more")
            print()

        # Recently completed (last 10)
        if completed:
            print(f"  ✅ COMPLETED ({len(completed)}):")
            for task_id, status, wid in sorted(completed)[-10:]:
                print(f"     ✓ {task_id}")
            if len(completed) > 10:
                print(f"     ... +{len(completed) - 10} more")

        print()
        print(f"  Press Ctrl+C to exit. Refreshing every 10s...")

        try:
            await asyncio.sleep(10)
        except KeyboardInterrupt:
            break


async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 cli.py <start|status|live|demo|stress> [project]")
        return

    cmd = sys.argv[1]

    if cmd == "demo":
        await demo()
    elif cmd == "stress":
        num = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        await stress_test(num)
    elif cmd == "live" and len(sys.argv) > 2:
        await live(sys.argv[2])
    elif cmd == "start" and len(sys.argv) > 2:
        project = sys.argv[2]
        # Load actual specs
        specs = load_specs_for_project(project)
        if not specs:
            return

        # Filter out already-completed tasks by querying Temporal history
        if "--exclude-completed" in sys.argv:
            from temporalio.client import Client as TClient
            client = await TClient.connect(TEMPORAL_HOST)
            completed = set()
            async for wf in client.list_workflows(limit=5000):
                if wf.status and wf.status.name == 'COMPLETED' and wf.workflow_type == 'TaskWorkflow':
                    # workflow id format: spec-{project}-{task_id}-{run_suffix}
                    # or: spec-{project}-{task_id}
                    wid = wf.id
                    if wid.startswith(f"spec-{project}-"):
                        # Extract task_id: remove prefix and optional run suffix
                        remainder = wid[len(f"spec-{project}-"):]
                        # task_id may contain hyphens, run suffix is last segment if it looks like a UUID prefix
                        parts = remainder.rsplit("-", 1)
                        if len(parts) == 2 and len(parts[1]) == 8 and all(c in '0123456789abcdef' for c in parts[1]):
                            completed.add(parts[0])
                        else:
                            completed.add(remainder)
            before = len(specs)
            specs = [s for s in specs if s.task_id not in completed]
            print(
                f"Filtered: {before} total, {before - len(specs)} already completed, {len(specs)} remaining"
            )

        import time

        run_id = f"{project}-{int(time.time())}"
        print(f"Submitting {len(specs)} tasks (run={run_id}).")
        handle = await start_project(run_id, specs)
    elif cmd == "status" and len(sys.argv) > 2:
        await get_status(sys.argv[2])
    else:
        print("Usage: python3 cli.py <start|status|live|demo|stress> [project]")


if __name__ == "__main__":
    asyncio.run(main())
