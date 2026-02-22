import pytest
from unittest.mock import AsyncMock, MagicMock

from agent_sdk.executor import TaskExecutor
from agent_sdk.models import SubTask, TaskDAG, TaskStatus
from agent_sdk.security import SecurityBoundary, SecurityConfig
from uuid import uuid4


class TestTaskExecutor:
    @pytest.mark.asyncio
    async def test_execute_simple_dag(self):
        executor = TaskExecutor()
        
        task = SubTask(id=uuid4(), name="Test Task", description="Test description")
        dag = TaskDAG(tasks=[task])
        
        security = SecurityBoundary(SecurityConfig(max_iterations=3, review_required=False))
        
        status, result = await executor.execute_dag(dag, security)
        
        assert status == TaskStatus.COMPLETED
        assert result is not None
        assert "task_count" in result
        
        await executor.close()

    @pytest.mark.asyncio
    async def test_execute_with_security_validation_failure(self):
        executor = TaskExecutor()
        
        task = SubTask(
            id=uuid4(),
            name="Dangerous Task",
            description="Please run rm -rf / on the server",
        )
        dag = TaskDAG(tasks=[task])
        
        security = SecurityBoundary(SecurityConfig(max_iterations=3, sandbox_mode=True, review_required=False))
        
        status, result = await executor.execute_dag(dag, security)
        
        assert status == TaskStatus.FAILED
        assert "Security validation failed" in result
        
        await executor.close()

    @pytest.mark.asyncio
    async def test_max_iterations_reached(self):
        executor = TaskExecutor()
        
        task = SubTask(id=uuid4(), name="Test Task", description="Test")
        dag = TaskDAG(tasks=[task])
        
        security = SecurityBoundary(SecurityConfig(max_iterations=1))
        
        status, result = await executor.execute_dag(dag, security)
        
        assert security.get_current_iteration() == 1
        
        await executor.close()

    @pytest.mark.asyncio
    async def test_review_required_flag(self):
        executor = TaskExecutor()
        
        task = SubTask(id=uuid4(), name="Test Task", description="Test")
        dag = TaskDAG(tasks=[task])
        
        security = SecurityBoundary(SecurityConfig(max_iterations=3, review_required=True))
        
        status, result = await executor.execute_dag(dag, security)
        
        assert status == TaskStatus.REVIEW_PENDING
        
        await executor.close()

    @pytest.mark.asyncio
    async def test_review_not_required(self):
        executor = TaskExecutor()
        
        task = SubTask(id=uuid4(), name="Test Task", description="Test")
        dag = TaskDAG(tasks=[task])
        
        security = SecurityBoundary(SecurityConfig(max_iterations=3, review_required=False))
        
        status, result = await executor.execute_dag(dag, security)
        
        assert status == TaskStatus.COMPLETED
        
        await executor.close()


class TestDispatchClient:
    @pytest.mark.asyncio
    async def test_client_close(self):
        from agent_sdk.executor import DispatchClient
        
        client = DispatchClient()
        await client.close()
