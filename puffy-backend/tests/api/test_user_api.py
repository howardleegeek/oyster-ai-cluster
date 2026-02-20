"""API tests for User endpoints."""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import status


@pytest.mark.api
class TestUserSignInAPI:
    """Test cases for /user/sign-in endpoint."""

    def test_sign_in_returns_session_and_message(self, test_client):
        """Test that sign-in returns session_id and message."""
        response = test_client.get("/user/sign-in")

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "session_id" in data
        assert "message" in data
        assert isinstance(data["session_id"], str)
        assert isinstance(data["message"], str)


@pytest.mark.api
class TestUserMeAPI:
    """Test cases for /user/me endpoint."""

    def test_get_current_user_without_auth(self, test_client):
        """Test that /user/me requires authentication."""
        response = test_client.get("/user/me")
        # HTTPBearer returns 403 when no Authorization header is provided
        assert response.status_code == status.HTTP_403_FORBIDDEN
