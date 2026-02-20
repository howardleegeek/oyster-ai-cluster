"""Unit test fixtures."""

import pytest
from unittest.mock import MagicMock
from app.services.token import Token
from app.config import Settings


@pytest.fixture
def token_service(test_settings: Settings) -> Token:
    """Create token service instance for testing."""
    return Token(test_settings.secret, test_settings.id_exp)


@pytest.fixture
def sample_user() -> MagicMock:
    """Create sample user object."""
    user = MagicMock()
    user.id = "usr_test_001"
    user.address = "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
    user.twitter = "test_twitter"
    user.email = "test@example.com"
    return user


@pytest.fixture
def sample_user_dict() -> dict:
    """Create sample user dictionary."""
    return {
        "id": "usr_test_001",
        "address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "twitter": "test_twitter",
        "email": "test@example.com",
    }
