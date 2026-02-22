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
