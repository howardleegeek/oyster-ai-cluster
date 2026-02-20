"""API test fixtures and utilities."""

import pytest
from typing import Dict
from unittest.mock import MagicMock


@pytest.fixture
def create_test_user(test_client) -> Dict:
    """Helper to create a test user and return auth headers."""
    # First, sign in to get session and message
    sign_in_response = test_client.get("/user/sign-in")
    assert sign_in_response.status_code == 200

    session_data = sign_in_response.json()
    session_id = session_data["session_id"]
    message = session_data["message"]

    return {
        "session_id": session_id,
        "message": message,
        "address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    }
