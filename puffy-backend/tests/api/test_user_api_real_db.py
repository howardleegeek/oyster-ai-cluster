"""API integration tests with real database access.

These tests use the real MySQL database configured in .env file.
Run with: pytest tests/api/test_user_api_real_db.py -v

Skipped by default because they require a running MySQL database.
"""

import pytest
from fastapi import status

# Skip all tests in this module — they require a real MySQL database
pytestmark = pytest.mark.skip(reason="Requires running MySQL database")


@pytest.mark.api
@pytest.mark.integration
class TestUserSignInAPIRealDB:
    """Test cases for /user/sign-in endpoint with real database."""

    def test_sign_in_returns_session_and_message(self, real_test_client):
        """Test that sign-in returns session_id and message."""
        response = real_test_client.get("/user/sign-in")

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "session_id" in data
        assert "message" in data
        assert isinstance(data["session_id"], str)
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0


@pytest.mark.api
@pytest.mark.integration
class TestUserMeAPIRealDB:
    """Test cases for /user/me endpoint with real database."""

    def test_get_current_user_without_auth(self, real_test_client):
        """Test that /user/me requires authentication."""
        response = real_test_client.get("/user/me")
        # HTTPBearer returns 403 when no Authorization header is provided
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.api
@pytest.mark.integration
class TestUserVerifyAPIRealDB:
    """Test cases for /user/verify endpoint with real database."""

    def test_verify_with_invalid_session(self, real_test_client):
        """Test user verification with invalid session."""
        response = real_test_client.post(
            "/user/verify",
            json={
                "session_id": "invalid_session_id",
                "address": "test_address",
                "signature": "test_signature"
            }
        )

        # Should return 401 or 400 for invalid session
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST]


@pytest.mark.api
@pytest.mark.integration
class TestProductListAPIRealDB:
    """Test cases for product endpoints with real database."""

    def test_get_products(self, real_test_client):
        """Test getting all products from real database."""
        response = real_test_client.get("/product/")

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, list)
        # May be empty if no products in database

    def test_get_product_by_id(self, real_test_client):
        """Test getting a specific product by ID from real database."""
        response = real_test_client.get("/product/1")

        # Returns 404 if product not found, 200 if found
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "id" in data or data.get("id") == 1


@pytest.mark.api
@pytest.mark.integration
class TestOrderAPIRealDB:
    """Test cases for order endpoints with real database."""

    def test_create_order_without_auth(self, real_test_client):
        """Test that creating order requires authentication."""
        response = real_test_client.post(
            "/order/",
            json={"product_id": 1, "quantity": 2}
        )
        # HTTPBearer returns 403 when no Authorization header is provided
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_orders_without_auth(self, real_test_client):
        """Test that getting orders requires authentication."""
        response = real_test_client.get("/order/")
        # HTTPBearer returns 403 when no Authorization header is provided
        assert response.status_code == status.HTTP_403_FORBIDDEN
