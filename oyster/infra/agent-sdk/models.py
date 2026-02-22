from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVIEW_PENDING = "review_pending"


class SubTask(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    dependencies: list[UUID] = Field(default_factory=list)


class TaskDAG(BaseModel):
    tasks: list[SubTask] = Field(default_factory=list)

    def get_ready_tasks(self) -> list[SubTask]:
        ready = []
        for task in self.tasks:
            if task.status != TaskStatus.PENDING:
                continue
            deps = [t for t in self.tasks if t.id in task.dependencies]
            if all(d.status == TaskStatus.COMPLETED for d in deps):
                ready.append(task)
        return ready

    def get_topological_order(self) -> list[SubTask]:
        visited = set()
        result = []
        
        def visit(task: SubTask):
            if task.id in visited:
                return
            visited.add(task.id)
            for dep_id in task.dependencies:
                for t in self.tasks:
                    if t.id == dep_id:
                        visit(t)
                        break
            result.append(task)
        
        for task in self.tasks:
            visit(task)
        
        return result


class TaskRequest(BaseModel):
    description: str
    context: Optional[dict[str, Any]] = Field(default_factory=dict)
    max_iterations: Optional[int] = None
    review_required: Optional[bool] = None
    sandbox_mode: Optional[bool] = None
    branch_isolation: Optional[bool] = None


class TaskResponse(BaseModel):
    task_id: UUID
    status: TaskStatus
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskDetailResponse(TaskResponse):
    dag: Optional[TaskDAG] = None
    iterations: int = 0
    security_config: Optional[dict[str, Any]] = None


class TaskResultResponse(BaseModel):
    task_id: UUID
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    completed_at: Optional[datetime] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    description: str
    iterations: int = 0
    review_required: bool = False
