import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from src.main import app
    return TestClient(app)


@pytest.fixture
def mock_dispatch_client():
    from unittest.mock import AsyncMock, MagicMock
    client = MagicMock()
    client.submit_task = AsyncMock(return_value={"task_id": "test-123"})
    client.get_task_status = AsyncMock(return_value={"status": "completed"})
    client.get_task_result = AsyncMock(return_value={"result": "success"})
    client.close = AsyncMock()
    return client


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestTaskEndpoints:
    def test_create_task(self, client):
        response = client.post(
            "/task",
            json={
                "description": "Test task description",
                "context": {"key": "value"},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "pending"
        assert data["description"] == "Test task description"

    def test_create_task_with_security_config(self, client):
        response = client.post(
            "/task",
            json={
                "description": "Test task with security",
                "max_iterations": 5,
                "review_required": False,
                "sandbox_mode": True,
                "branch_isolation": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "task_id" in data

    def test_get_task_not_found(self, client):
        response = client.get("/task/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_get_task_result_not_found(self, client):
        response = client.get("/task/00000000-0000-0000-0000-000000000000/result")
        assert response.status_code == 404

    def test_execute_task_not_found(self, client):
        response = client.post("/task/00000000-0000-0000-0000-000000000000/execute")
        assert response.status_code == 404

    def test_review_task_not_found(self, client):
        response = client.post("/task/00000000-0000-0000-0000-000000000000/review", json={"approved": True})
        assert response.status_code == 404


class TestTaskFlow:
    def test_full_task_flow(self, client):
        create_response = client.post(
            "/task",
            json={"description": "Create a simple task"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["task_id"]
        
        get_response = client.get(f"/task/{task_id}")
        assert get_response.status_code == 200
        assert get_response.json()["status"] == "pending"
        
        execute_response = client.post(f"/task/{task_id}/execute")
        assert execute_response.status_code == 200
        
        result_response = client.get(f"/task/{task_id}/result")
        assert result_response.status_code == 200
