import pytest
from fastapi.testclient import TestClient

from main import app
from agent_sdk.models import TaskStatus
from agent_sdk.security import SecurityConfig, validate_task_security
from agent_sdk.task_router import TaskRouter
from agent_sdk.executor import TaskExecutor


client = TestClient(app)


class TestAPI:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_create_task(self):
        payload = {
            "description": "Create a simple task",
            "max_iterations": 3,
            "review_required": True,
            "sandbox_mode": True,
            "branch_isolation": True,
        }
        response = client.post("/task", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "task_id" in data
        assert data["status"] == TaskStatus.PENDING
        assert data["description"] == payload["description"]

    def test_get_task_status_not_found(self):
        response = client.get("/task/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_get_task_result_not_found(self):
        response = client.get("/task/00000000-0000-0000-0000-000000000000/result")
        assert response.status_code == 404


class TestSecurity:
    def test_security_config_defaults(self):
        config = SecurityConfig()
        assert config.max_iterations == 3
        assert config.review_required is True
        assert config.sandbox_mode is True
        assert config.branch_isolation is True

    def test_security_config_custom(self):
        config = SecurityConfig(
            max_iterations=5,
            review_required=False,
            sandbox_mode=False,
            branch_isolation=False,
        )
        assert config.max_iterations == 5
        assert config.review_required is False
        assert config.sandbox_mode is False
        assert config.branch_isolation is False

    def test_validate_task_security_valid(self):
        config = SecurityConfig()
        is_valid, error = validate_task_security("Create a task", config)
        assert is_valid is True
        assert error is None

    def test_validate_task_security_dangerous(self):
        config = SecurityConfig()
        is_valid, error = validate_task_security("Delete all files", config)
        assert is_valid is False
        assert "Dangerous pattern detected" in error

    def test_validate_task_security_max_iterations(self):
        config = SecurityConfig(max_iterations=15)
        is_valid, error = validate_task_security("Do something", config)
        assert is_valid is False
        assert "Max iterations must be between 1 and 10" in error


class TestTaskRouter:
    def test_simple_task_decomposition(self):
        router = TaskRouter()
        dag = router.parse_and_decompose("Get the data")
        assert len(dag.tasks) == 1
        assert dag.tasks[0].name == "Execute Task"

    def test_complex_task_decomposition(self):
        router = TaskRouter()
        dag = router.parse_and_decompose("Build and deploy the application")
        assert len(dag.tasks) == 4

    def test_estimate_complexity(self):
        router = TaskRouter()
        score = router.estimate_complexity("Create a simple task")
        assert score >= 1


class TestTaskExecutor:
    @pytest.mark.asyncio
    async def test_executor_initialization(self):
        executor = TaskExecutor()
        assert executor.task_status == {}
        assert executor.task_results == {}

    @pytest.mark.asyncio
    async def test_get_status_not_found(self):
        executor = TaskExecutor()
        status = await executor.get_status("nonexistent")
        assert status is None

    @pytest.mark.asyncio
    async def test_get_result_not_found(self):
        executor = TaskExecutor()
        result = await executor.get_result("nonexistent")
        assert result is None
