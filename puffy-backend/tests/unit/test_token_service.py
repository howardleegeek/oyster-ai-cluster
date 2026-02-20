"""Unit tests for Token service."""

import jwt
import time
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from app.services.token import Token
from app.schemas.user import User
from app.config import Settings


@pytest.mark.unit
class TestToken:
    """Test cases for Token service."""

    def test_gen_token_creates_valid_jwt(self, token_service: Token, sample_user: MagicMock):
        """Test that gen_token creates a valid JWT token."""
        token = token_service.gen_token(sample_user)

        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify token structure
        decoded = jwt.decode(
            token,
            token_service.secret,
            algorithms=["HS256"]
        )

        assert decoded["id"] == sample_user.id
        assert decoded["address"] == sample_user.address

    def test_parse_token_returns_valid_user(self, token_service: Token, sample_user: MagicMock):
        """Test that parse_token returns user data for valid token."""
        token = token_service.gen_token(sample_user)

        result = token_service.parse_token(token)

        assert result is not None
        assert result.id == sample_user.id
        assert result.address == sample_user.address

    def test_parse_token_returns_none_for_invalid_token(self, token_service: Token):
        """Test that parse_token returns None for invalid token."""
        result = token_service.parse_token("invalid_token")

        assert result is None

    def test_parse_token_returns_none_for_expired_token(self, token_service: Token):
        """Test that parse_token returns None for expired token."""
        # Create an expired token
        expired_token = jwt.encode(
            {
                "id": "usr_test_001",
                "address": "test_address",
                "exp": int(time.time()) - 3600
            },
            token_service.secret,
            algorithm="HS256"
        )

        result = token_service.parse_token(expired_token)

        assert result is None

    def test_parse_token_returns_none_for_malformed_token(self, token_service: Token):
        """Test that parse_token returns None for malformed token."""
        malformed_tokens = [
            "",
            "not.a.token",
            None,
        ]

        for token in malformed_tokens:
            result = token_service.parse_token(token)
            assert result is None

    def test_parse_token_handles_bearer_token(self, token_service: Token, sample_user: MagicMock):
        """Test that parse_token handles Bearer token format."""
        token = token_service.gen_token(sample_user)

        result = token_service.parse_token(f"Bearer {token}")

        assert result is not None
        assert result.id == sample_user.id

    def test_gen_token_includes_expiration(self, token_service: Token, sample_user: MagicMock):
        """Test that gen_token includes correct expiration time."""
        token = token_service.gen_token(sample_user)

        decoded = jwt.decode(
            token,
            token_service.secret,
            algorithms=["HS256"]
        )

        # Check expiration is set
        assert "exp" in decoded

        # Verify expiration is approximately correct (within 1 minute)
        exp_timestamp = decoded["exp"]
        expected_exp = time.time() + token_service.exp
        assert abs(exp_timestamp - expected_exp) < 60

    def test_gen_token_with_minimal_user_data(self, token_service: Token):
        """Test gen_token with minimal user data."""
        minimal_user = MagicMock()
        minimal_user.id = "usr_minimal_001"
        minimal_user.address = "test_address"

        token = token_service.gen_token(minimal_user)

        assert isinstance(token, str)
        decoded = jwt.decode(
            token,
            token_service.secret,
            algorithms=["HS256"]
        )
        assert decoded["id"] == "usr_minimal_001"
        assert decoded["address"] == "test_address"
