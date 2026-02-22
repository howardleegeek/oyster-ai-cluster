#!/usr/bin/env python3
"""
Lightweight stress-test harness for asynchronous workflow start functions.
"""

import asyncio
import time
from typing import Any, Callable, Optional, List, Dict


async def _worker(
    index: int,
    sem: asyncio.Semaphore,
    start_workflow: Callable[[Any], Any],
    payload_factory: Optional[Callable[[int], Any]],
    per_task_timeout: Optional[float],
    results: List[Dict[str, Any]],
):
    async with sem:
        payload = payload_factory(index) if payload_factory else None
        t0 = time.perf_counter()
        try:
            if per_task_timeout is not None:
                await asyncio.wait_for(
                    start_workflow(payload), timeout=per_task_timeout
                )
            else:
                await start_workflow(payload)
            latency = time.perf_counter() - t0
            results.append(
                {"index": index, "latency": latency, "success": True, "error": None}
            )
        except Exception as e:
            latency = time.perf_counter() - t0
            results.append(
                {"index": index, "latency": latency, "success": False, "error": str(e)}
            )


async def run_stress_test(
    concurrency: int = 50,
    total_tasks: int = 50,
    start_workflow_func: Optional[Callable[[Any], Any]] = None,
    payload_factory: Optional[Callable[[int], Any]] = None,
    per_task_timeout: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Run a stress test issuing `total_tasks` workflow starts with up to `concurrency` concurrent workers.
    - start_workflow_func: async function accepting a single payload, e.g., async def start(payload): ...
    - payload_factory: function(index) -> payload
    Returns a summary dict and per-task results.
    """
    if start_workflow_func is None:
        raise ValueError("start_workflow_func must be provided")

    sem = asyncio.Semaphore(max(1, int(concurrency)))
    results: List[Dict[str, Any]] = []
    tasks = [
        asyncio.create_task(
            _worker(
                i, sem, start_workflow_func, payload_factory, per_task_timeout, results
            )
        )
        for i in range(int(total_tasks))
    ]

    await asyncio.gather(*tasks)

    successes = sum(1 for r in results if r.get("success"))
    failures = total_tasks - successes

    return {
        "total_tasks": int(total_tasks),
        "concurrency": int(concurrency),
        "successes": successes,
        "failures": failures,
        "latencies": [r.get("latency") for r in results],
        "results": results,
    }


def run_stress_test_sync(*args, **kwargs):
    return asyncio.run(run_stress_test(*args, **kwargs))


if __name__ == "__main__":

    async def _demo():
        async def dummy(payload):
            await asyncio.sleep(0.01)

        res = await run_stress_test(
            concurrency=5, total_tasks=20, start_workflow_func=dummy
        )
        print(res)

    asyncio.run(_demo())
