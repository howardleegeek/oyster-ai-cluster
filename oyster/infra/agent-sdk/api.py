from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from agent_sdk.executor import TaskExecutor
from agent_sdk.models import (
    TaskDAG,
    TaskDetailResponse,
    TaskRequest,
    TaskResponse,
    TaskResultResponse,
    TaskStatus,
)
from agent_sdk.security import SecurityBoundary, SecurityConfig, validate_task_security
from agent_sdk.task_router import TaskRouter

router = APIRouter(prefix="/task", tags=["tasks"])


class TaskStore:
    def __init__(self):
        self._tasks: dict[UUID, dict] = {}

    def create_task(
        self,
        task_id: UUID,
        description: str,
        security_config: SecurityConfig,
    ) -> None:
        self._tasks[task_id] = {
            "task_id": task_id,
            "description": description,
            "status": TaskStatus.PENDING,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "dag": None,
            "iterations": 0,
            "security_config": {
                "max_iterations": security_config.max_iterations,
                "review_required": security_config.review_required,
                "sandbox_mode": security_config.sandbox_mode,
                "branch_isolation": security_config.branch_isolation,
            },
            "result": None,
            "error": None,
        }

    def get_task(self, task_id: UUID) -> Optional[dict]:
        return self._tasks.get(task_id)

    def update_task(self, task_id: UUID, **kwargs) -> None:
        if task_id in self._tasks:
            self._tasks[task_id].update(kwargs)
            self._tasks[task_id]["updated_at"] = datetime.utcnow()


task_store = TaskStore()
task_router = TaskRouter()
task_executor = TaskExecutor()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(request: TaskRequest) -> TaskResponse:
    task_id = uuid4()
    
    security_config = SecurityConfig.from_request(
        max_iterations=request.max_iterations,
        review_required=request.review_required,
        sandbox_mode=request.sandbox_mode,
        branch_isolation=request.branch_isolation,
    )
    
    security_boundary = SecurityBoundary(security_config)
    valid, error = security_boundary.validate_task(request.description)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    
    task_store.create_task(task_id, request.description, security_config)
    
    dag = task_router.parse_and_decompose(request.description, request.context)
    task_store.update_task(task_id, dag=dag.model_dump(), status=TaskStatus.PENDING)
    
    return TaskResponse(
        task_id=task_id,
        status=TaskStatus.PENDING,
        description=request.description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@router.get("/{task_id}", response_model=TaskDetailResponse)
async def get_task(task_id: UUID) -> TaskDetailResponse:
    task = task_store.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    
    dag = TaskDAG(**task["dag"]) if task.get("dag") else None
    
    return TaskDetailResponse(
        task_id=task["task_id"],
        status=task["status"],
        description=task["description"],
        created_at=task["created_at"],
        updated_at=task["updated_at"],
        dag=dag,
        iterations=task.get("iterations", 0),
        security_config=task.get("security_config"),
    )


@router.get("/{task_id}/result", response_model=TaskResultResponse)
async def get_task_result(task_id: UUID) -> TaskResultResponse:
    task = task_store.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    
    if task["status"] in [TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.REVIEW_PENDING]:
        return TaskResultResponse(
            task_id=task["task_id"],
            status=task["status"],
            result=None,
            error=None,
            completed_at=None,
        )
    
    return TaskResultResponse(
        task_id=task["task_id"],
        status=task["status"],
        result=task.get("result"),
        error=task.get("error"),
        completed_at=task.get("updated_at"),
    )


@router.post("/{task_id}/execute")
async def execute_task(task_id: UUID) -> TaskResponse:
    task = task_store.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    
    if task["status"] not in [TaskStatus.PENDING, TaskStatus.REVIEW_PENDING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task {task_id} is not in executable state",
        )
    
    security_config = SecurityConfig(**task["security_config"])
    security_boundary = SecurityBoundary(security_config)
    
    dag = TaskDAG(**task["dag"])
    
    task_store.update_task(task_id, status=TaskStatus.RUNNING)
    
    status_result, result = await task_executor.execute_dag(dag, security_boundary)
    
    task_store.update_task(
        task_id,
        status=status_result,
        result=result,
        iterations=security_boundary.get_current_iteration(),
    )
    
    updated_task = task_store.get_task(task_id)
    
    return TaskResponse(
        task_id=task_id,
        status=updated_task["status"],
        description=task["description"],
        created_at=task["created_at"],
        updated_at=updated_task["updated_at"],
    )


@router.post("/{task_id}/review")
async def approve_task(task_id: UUID, approved: bool = True) -> TaskResponse:
    task = task_store.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    
    if task["status"] != TaskStatus.REVIEW_PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task {task_id} is not pending review",
        )
    
    if approved:
        task_store.update_task(task_id, status=TaskStatus.COMPLETED)
    else:
        task_store.update_task(task_id, status=TaskStatus.CANCELLED)
    
    updated_task = task_store.get_task(task_id)
    
    return TaskResponse(
        task_id=task_id,
        status=updated_task["status"],
        description=task["description"],
        created_at=task["created_at"],
        updated_at=updated_task["updated_at"],
    )
