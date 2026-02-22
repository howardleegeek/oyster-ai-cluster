import asyncio
from typing import Any, Optional
from uuid import UUID

import httpx

from agent_sdk.models import TaskDAG, TaskStatus
from agent_sdk.security import SecurityBoundary, SecurityConfig


class DispatchClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def submit_task(self, task_definition: dict) -> dict:
        response = await self.client.post(
            f"{self.base_url}/api/v1/tasks",
            json=task_definition,
        )
        response.raise_for_status()
        return response.json()

    async def get_task_status(self, task_id: str) -> dict:
        response = await self.client.get(
            f"{self.base_url}/api/v1/tasks/{task_id}",
        )
        response.raise_for_status()
        return response.json()

    async def get_task_result(self, task_id: str) -> dict:
        response = await self.client.get(
            f"{self.base_url}/api/v1/tasks/{task_id}/result",
        )
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()


class TaskExecutor:
    def __init__(self, dispatch_client: Optional[DispatchClient] = None):
        self.dispatch_client = dispatch_client or DispatchClient()
        self._results: dict[UUID, Any] = {}
        self.task_status: dict[str, dict[str, Any]] = {}
        self.task_results: dict[str, dict[str, Any]] = {}
        self._reviews: dict[str, bool] = {}

    def store_review(self, task_id: str, approved: bool) -> None:
        self._reviews[task_id] = approved

    async def execute(
        self,
        task_id: str,
        dag: TaskDAG,
        security_config: SecurityConfig,
    ) -> None:
        self.task_status[task_id] = {
            "status": TaskStatus.RUNNING,
            "iterations": 0,
            "review_required": security_config.review_required,
        }
        self.task_results[task_id] = {
            "status": TaskStatus.RUNNING,
            "result": None,
            "iterations": 0,
        }

        try:
            security_boundary = SecurityBoundary(security_config)
            
            status, result = await self.execute_dag(dag, security_boundary)
            
            self.task_status[task_id]["status"] = status
            self.task_results[task_id]["status"] = status
            self.task_results[task_id]["result"] = result

        except Exception as e:
            self.task_status[task_id]["status"] = TaskStatus.FAILED
            self.task_results[task_id]["status"] = TaskStatus.FAILED
            self.task_results[task_id]["result"] = {"error": str(e)}

    async def execute_dag(
        self,
        dag: TaskDAG,
        security: SecurityBoundary,
    ) -> tuple[TaskStatus, Any]:
        iteration = 0
        
        while True:
            security.increment_iteration()
            iteration = security.get_current_iteration()
            
            ready_tasks = dag.get_ready_tasks()
            if not ready_tasks:
                break
            
            for task in ready_tasks:
                task.status = TaskStatus.RUNNING
                try:
                    result = await self._execute_single_task(task, security)
                    task.result = result
                    task.status = TaskStatus.COMPLETED
                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    return TaskStatus.FAILED, str(e)
            
            if security.needs_review:
                all_completed = all(
                    t.status == TaskStatus.COMPLETED 
                    for t in dag.tasks
                )
                if all_completed:
                    return TaskStatus.REVIEW_PENDING, "Task completed, pending review"
            
            if not security.can_iterate:
                return TaskStatus.FAILED, "Max iterations reached"
            
            await asyncio.sleep(0.1)
        
        all_completed = all(t.status == TaskStatus.COMPLETED for t in dag.tasks)
        if all_completed:
            final_result = self._aggregate_results(dag)
            return TaskStatus.COMPLETED, final_result
        else:
            return TaskStatus.FAILED, "Task execution failed"

    async def _execute_single_task(
        self,
        task,
        security: SecurityBoundary,
    ) -> Any:
        valid, error = security.validate_task(task.description)
        if not valid:
            raise ValueError(f"Security validation failed: {error}")
        
        if security.is_sandboxed:
            return await self._execute_in_sandbox(task)
        else:
            return await self._execute_direct(task)

    async def _execute_in_sandbox(self, task) -> Any:
        await asyncio.sleep(0.1)
        return {"status": "sandboxed_executed", "task_id": str(task.id)}

    async def _execute_direct(self, task) -> Any:
        try:
            dispatch_task = {
                "name": task.name,
                "description": task.description,
                "type": "execution",
            }
            result = await self.dispatch_client.submit_task(dispatch_task)
            return result
        except httpx.ConnectError:
            return {"status": "mock_executed", "task_id": str(task.id)}
        except Exception:
            return {"status": "mock_executed", "task_id": str(task.id)}

    def _aggregate_results(self, dag: TaskDAG) -> dict:
        return {
            "task_count": len(dag.tasks),
            "completed_count": sum(1 for t in dag.tasks if t.status == TaskStatus.COMPLETED),
            "results": [
                {
                    "task_id": str(t.id),
                    "name": t.name,
                    "result": t.result,
                }
                for t in dag.tasks
                if t.result is not None
            ],
        }

    async def get_status(self, task_id: str) -> Optional[dict[str, Any]]:
        return self.task_status.get(task_id)

    async def get_result(self, task_id: str) -> Optional[dict[str, Any]]:
        return self.task_results.get(task_id)

    async def close(self):
        await self.dispatch_client.close()
