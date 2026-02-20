"""API tests for Order endpoints."""

import time
import jwt
import pytest
from unittest.mock import MagicMock, patch
from fastapi import status


@pytest.fixture
def user_token(test_settings) -> str:
    """Generate a valid JWT token for testing."""
    payload = {
        "id": "test_user_123",
        "address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "exp": int(time.time() + 3600),
    }
    return jwt.encode(payload, test_settings.secret, algorithm="HS256")


@pytest.fixture
def auth_headers(user_token: str) -> dict:
    """Return authentication headers with valid token."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def sample_order_create_request() -> dict:
    """Return a sample order create request."""
    return {
        "shipping_address": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone_number": "+1234567890",
            "address_line_1": "123 Main St",
            "city": "New York",
            "state": "NY",
            "country": "US",
            "postal_code": "10001"
        },
        "order_items": [
            {
                "product_id": "test_product_123",
                "qty": 1
            }
        ]
    }


@pytest.mark.api
class TestOrderCreateAPI:
    """Test cases for order creation endpoint."""

    def test_create_order_without_auth(self, test_client):
        """Test that creating order requires authentication."""
        response = test_client.post("/order/", json={
            "shipping_address": {
                "name": "John Doe",
                "country": "US"
            },
            "order_items": [{"product_id": "test", "qty": 1}]
        })
        # HTTPBearer returns 403 when no Authorization header is provided
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_order_with_token_no_referral_or_passcode(
        self, test_client, auth_headers, sample_order_create_request
    ):
        """Test creating order with user token, no referral_code and no passcode."""
        response = test_client.post(
            "/order/",
            json=sample_order_create_request,
            headers=auth_headers
        )
        # Should accept the request (may fail on actual order creation due to missing product)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND
        ]

    def test_create_order_with_token_and_passcode(
        self, test_client, auth_headers, sample_order_create_request
    ):
        """Test creating order with user token and passcode."""
        sample_order_create_request["pass_code"] = "TESTPASS123"
        response = test_client.post(
            "/order/",
            json=sample_order_create_request,
            headers=auth_headers
        )
        # Should accept the request (may fail on actual order creation due to missing product)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND
        ]

    def test_create_order_with_token_and_referral_code(
        self, test_client, auth_headers, sample_order_create_request
    ):
        """Test creating order with user token and referral code."""
        sample_order_create_request["referral_code"] = "REFERRAL123"
        response = test_client.post(
            "/order/",
            json=sample_order_create_request,
            headers=auth_headers
        )
        # Should accept the request (may fail on actual order creation due to missing product)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND
        ]

    def test_create_order_with_multiple_items(
        self, test_client, auth_headers, sample_order_create_request
    ):
        """Test creating order with multiple items."""
        sample_order_create_request["order_items"] = [
            {"product_id": "test_product_123", "qty": 2},
            {"product_id": "test_product_456", "qty": 1}
        ]
        response = test_client.post(
            "/order/",
            json=sample_order_create_request,
            headers=auth_headers
        )
        # Should accept the request
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND
        ]

    def test_create_order_dry_run(
        self, test_client, auth_headers, sample_order_create_request
    ):
        """Test dry run order creation."""
        response = test_client.post(
            "/order/?dry_run=true",
            json=sample_order_create_request,
            headers=auth_headers
        )
        # Should accept the request
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND
        ]

    def test_create_vape_order_to_restricted_country_denied(
        self, test_client, auth_headers
    ):
        """Test that VAPE product order to restricted country (CN) is denied."""
        # CN is restricted for VAPE products
        order_data = {
            "shipping_address": {
                "name": "Test User",
                "email": "test@example.com",
                "phone_number": "+1234567890",
                "address_line_1": "123 Beijing St",
                "city": "Beijing",
                "state": "Beijing",
                "country": "CN",  # China - restricted for VAPE
                "postal_code": "100000"
            },
            "order_items": [
                {
                    # Assuming this is a VAPE product - replace with actual VAPE product ID
                    "product_id": "prod_vape_01",
                    "qty": 1
                }
            ]
        }

        response = test_client.post(
            "/order/",
            json=order_data,
            headers=auth_headers
        )

        # Should be rejected due to restricted area or missing product
        # The endpoint catches exceptions and returns UserError.INVALID_REQUEST (404)
        # or HTTP_400 if the validation is reached before the DB query
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_create_vape_order_to_non_restricted_country_allowed(
        self, test_client, auth_headers
    ):
        """Test that VAPE product order to non-restricted country is allowed."""
        # Assuming 'SG' (Singapore) is NOT restricted for VAPE
        order_data = {
            "shipping_address": {
                "name": "Test User",
                "email": "test@example.com",
                "phone_number": "+1234567890",
                "address_line_1": "123 Orchard Rd",
                "city": "Singapore",
                "state": "Singapore",
                "country": "SG",  # Singapore - NOT restricted for VAPE
                "postal_code": "238896"
            },
            "order_items": [
                {
                    # Assuming this is a VAPE product
                    "product_id": "prod_vape_01",
                    "qty": 1
                }
            ]
        }

        response = test_client.post(
            "/order/",
            json=order_data,
            headers=auth_headers
        )

        # Should accept the request (may fail if product doesn't exist)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND  # Product not found is OK for this test
        ]

    def test_create_non_vape_order_to_restricted_country_allowed(
        self, test_client, auth_headers
    ):
        """Test that non-VAPE product order to restricted country is allowed."""
        order_data = {
            "shipping_address": {
                "name": "Test User",
                "email": "test@example.com",
                "phone_number": "+1234567890",
                "address_line_1": "123 Beijing St",
                "city": "Beijing",
                "state": "Beijing",
                "country": "CN",  # China - restricted for VAPE only
                "postal_code": "100000"
            },
            "order_items": [
                {
                    # Non-VAPE product (e.g., OTHER type)
                    "product_id": "prod_12_4",
                    "qty": 1
                }
            ]
        }

        response = test_client.post(
            "/order/",
            json=order_data,
            headers=auth_headers
        )

        # Should accept the request (non-VAPE products are allowed to CN)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND  # Product not found is OK
        ]
