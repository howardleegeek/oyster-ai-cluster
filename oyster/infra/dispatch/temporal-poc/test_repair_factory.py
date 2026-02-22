import asyncio
import os
from temporalio.client import Client
from workflows import TaskWorkflow, TaskSpec


async def main():
    client = await Client.connect("localhost:7233")

    spec = TaskSpec(
        task_id="T99-repair-test",
        project="demo",
        spec_file="specs/demo/T99-repair-test.md",
        spec_content="Fail immediately.",
        depends_on=[],
        estimated_minutes=0,
        max_retries=1,
    )

    try:
        handle = await client.start_workflow(
            TaskWorkflow.run, spec, id="repair-test-wf-1", task_queue="dispatch-tasks"
        )
        print("Started workflow. Waiting for result...")
        result = await handle.result()
        print("Result:", result)
    except Exception as e:
        print("Workflow failed:", e)


if __name__ == "__main__":
    asyncio.run(main())
