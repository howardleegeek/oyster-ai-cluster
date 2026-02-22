import asyncio
import unittest
import random

from temporal_stress import run_stress_test


class TestStressTemporal(unittest.TestCase):
    def test_run_stress_basic(self):
        async def _run():
            async def mock_start(payload):
                # simulate a tiny workload
                await asyncio.sleep(random.uniform(0.001, 0.01))

            res = await run_stress_test(
                concurrency=5,
                total_tasks=20,
                start_workflow_func=mock_start,
                payload_factory=lambda idx: {"id": idx},
                per_task_timeout=1.0,
            )
            self.assertEqual(res["total_tasks"], 20)
            self.assertIn("latencies", res)
            self.assertEqual(len(res["latencies"]), 20)
            self.assertGreaterEqual(res["successes"], 0)
            self.assertEqual(res["successes"] + res["failures"], 20)

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
