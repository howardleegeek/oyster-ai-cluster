"""Pytest configuration and shared fixtures.

This conftest patches the database engine and Redis connection at import time
so that importing app.puffy does not require a real MySQL/Redis server.
"""

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Generator, AsyncGenerator
from dotenv import load_dotenv
import datetime
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# Early Patching: mock DB engine and Redis BEFORE app.puffy is imported
# ============================================================================
# This is necessary because app.db.base and app.db.cache create connections
# at module-import time. Without this, importing app.puffy would fail if
# MySQL/Redis are not running.

import app.config

# Clear the lru_cache on get_settings so our test settings take effect
app.config.get_settings.cache_clear()

# Create test settings with all required fields (including sol_key)
_test_settings_for_import = app.config.Settings(
    env="TEST",
    db_host="localhost",
    db_user="test",
    db_passwd="test",
    db_name="test_db",
    db_pool_size=1,
    redis_host="localhost",
    redis_port=6379,
    redis_db=15,
    secret="test_secret_key_for_jwt_signing",
    id_exp=3600,
    sender_account="test_account",
    sender_key="test_key",
    twitter_id="test_twitter_id",
    twitter_secret="test_twitter_secret",
    twitter_redirect_url="http://localhost:8080/callback",
    twitter_api_token="test_token",
    sol_wallet="test_wallet",
    sol_key="test_sol_key",
    mixpay_id="test_mixpay_id",
    mixpay_settle_asset="USDT",
    mint_url="http://localhost:8080/mint",
    mint_key="test_mint_key",
    sol_api_url="http://localhost:8080/sol",
    nft_api_url="http://localhost:8080/nft",
    nft_api_key="test_nft_key",
)

# Save reference to the ORIGINAL get_settings (lru_cache wrapper) so we can
# use it as the key for FastAPI dependency overrides later.
_original_get_settings = app.config.get_settings

# Replace get_settings so module-level code gets test values during import.
# This is needed because app.db.base and app.db.cache call get_settings()
# at module level.
app.config.get_settings = lambda: _test_settings_for_import

# Mock Redis so app.db.cache doesn't need a running Redis server
_mock_redis_instance = MagicMock()
_mock_redis_instance.setex = MagicMock()
_mock_redis_instance.get = MagicMock(return_value=None)
_mock_redis_instance.set = MagicMock()
_mock_redis_instance.delete = MagicMock()
_redis_patcher = patch('redis.Redis', return_value=_mock_redis_instance)
_redis_patcher.start()

# Mock the SQLAlchemy create_engine in app.db.base to avoid MySQL connection
_mock_engine = MagicMock()
_engine_patcher = patch('app.db.base.create_engine', return_value=_mock_engine)
_engine_patcher.start()

# Force re-import of app.db.base with mocked engine
if 'app.db.base' in sys.modules:
    del sys.modules['app.db.base']
import app.db.base

# Mock Base.metadata.create_all to avoid DDL execution
from app.models.base import Base
Base.metadata.create_all = MagicMock()

# Now it's safe to import app.puffy and related modules
# Import TestClient with alias to prevent solana.Client from shadowing it
import fastapi.testclient
_FastAPITestClient = fastapi.testclient.TestClient

from app.config import Settings
from app.db.base import get_db
from app.db.cache import CacheDb, get_cache_db
from app.services.user import User
from app.services.product import ProductService
from app.services.order import OrderService
from app.services.token import Token

# Use the original get_settings for dependency override keys
# (FastAPI routes use Depends(get_settings) which captured the original function)
get_settings = _original_get_settings


# Test database URL (SQLite for testing)
TEST_DATABASE_URL = "sqlite:///./test.db"


# Override settings for testing
@pytest.fixture
def test_settings() -> Settings:
    """Return test settings."""
    return Settings(
        env="TEST",
        db_host="localhost",
        db_user="test",
        db_passwd="test",
        db_name="test_db",
        db_pool_size=5,
        redis_host="localhost",
        redis_port=6379,
        redis_db=15,  # Use DB 15 for testing
        secret="test_secret_key_for_jwt_signing",
        id_exp=3600,
        sender_account="test_account",
        sender_key="test_key",
        twitter_id="test_twitter_id",
        twitter_secret="test_twitter_secret",
        twitter_redirect_url="http://localhost:8080/callback",
        twitter_api_token="test_token",
        sol_wallet="test_wallet",
        sol_key="test_sol_key",
        mixpay_id="test_mixpay_id",
        mixpay_settle_asset="USDT",
        mint_url="http://localhost:8080/mint",
        mint_key="test_mint_key",
        sol_api_url="http://localhost:8080/sol",
        nft_api_url="http://localhost:8080/nft",
        nft_api_key="test_nft_key",
    )


@pytest.fixture
def test_engine():
    """Create test database engine (SQLite)."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    # Note: create_all may fail for MySQL-specific schemas on SQLite.
    # Only use this fixture for tests that truly need a database.
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass  # Some tables may not be SQLite-compatible
    yield engine
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception:
        pass
    # Clean up test database file
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture
def test_db_session(test_engine) -> Generator[Session, None, None]:
    """Create test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_client(test_settings: Settings) -> Generator[_FastAPITestClient, None, None]:
    """Create test client with mocked dependencies (no database for API tests)."""
    # Import puffy locally to avoid Client naming collision
    from app.puffy import puffy

    # Create a mock session for API tests (we don't need real DB for mocked services)
    mock_db = MagicMock()

    # Create a mock cache_db that returns valid session data for sign-in
    mock_cache = MagicMock(spec=CacheDb)
    mock_cache.new_session = MagicMock(return_value="test_session_id")
    mock_cache.get_session = MagicMock(return_value=MagicMock(
        message="test_message",
        address=None
    ))
    mock_cache.close_session = MagicMock()
    mock_cache.get_data = MagicMock(return_value=None)
    mock_cache.set_data = MagicMock()

    def override_get_db():
        try:
            yield mock_db
        finally:
            pass

    def override_get_settings():
        return test_settings

    def override_get_cache_db():
        return mock_cache

    # Override dependencies using the ORIGINAL function references
    # (FastAPI's Depends() captured the original functions, not our patched versions)
    puffy.dependency_overrides[get_db] = override_get_db
    puffy.dependency_overrides[get_settings] = override_get_settings
    puffy.dependency_overrides[get_cache_db] = override_get_cache_db

    with _FastAPITestClient(puffy) as client:
        yield client

    # Clear overrides
    puffy.dependency_overrides.clear()


@pytest.fixture
def mock_cache_db() -> MagicMock:
    """Mock cache database."""
    cache_db = MagicMock(spec=CacheDb)
    cache_db.new_session = MagicMock(return_value="test_session_id")
    cache_db.get_session = MagicMock(return_value=MagicMock(
        message="test_message",
        address=None
    ))
    cache_db.delete_session = MagicMock()
    return cache_db


@pytest.fixture
def mock_redis() -> Generator[MagicMock, None, None]:
    """Mock Redis client."""
    # Return the already-mocked Redis instance
    yield _mock_redis_instance


@pytest.fixture
def mock_user_service() -> MagicMock:
    """Mock user service."""
    service = MagicMock(spec=User)
    service.create_or_get_user = MagicMock(return_value=MagicMock(
        id="usr_test_001",
        address="test_address",
        twitter=None,
        email=None
    ))
    service.get_user = MagicMock(return_value=MagicMock(
        id="usr_test_001",
        address="test_address",
        twitter=None,
        email=None
    ))
    service.update_user = MagicMock()
    service.get_eligible_products = MagicMock(return_value=[])
    return service


@pytest.fixture
def mock_product_service() -> MagicMock:
    """Mock product service."""
    service = MagicMock(spec=ProductService)
    service.get_products = MagicMock(return_value=[])
    service.get_product = MagicMock(return_value=None)
    return service


@pytest.fixture
def mock_order_service() -> MagicMock:
    """Mock order service."""
    service = MagicMock(spec=OrderService)
    service.create_order = MagicMock(return_value=None)
    service.get_order = MagicMock(return_value=None)
    service.get_orders = MagicMock(return_value=[])
    service.update_order_status = MagicMock()
    return service


@pytest.fixture
def mock_token_service() -> MagicMock:
    """Mock token service."""
    service = MagicMock(spec=Token)
    service.gen_token = MagicMock(return_value="test_jwt_token")
    service.parse_token = MagicMock(return_value=MagicMock(
        id="usr_test_001",
        address="test_address"
    ))
    return service


@pytest.fixture
def mock_sol_service() -> MagicMock:
    """Mock Solana service."""
    service = MagicMock()
    service.verify = MagicMock(return_value=True)
    return service


@pytest.fixture
def auth_headers() -> dict:
    """Return authentication headers."""
    return {"Authorization": "Bearer test_jwt_token"}


@pytest.fixture
def sample_user_data() -> dict:
    """Return sample user data."""
    return {
        "address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "twitter": None,
        "email": None,
    }


@pytest.fixture
def sample_product_data() -> dict:
    """Return sample product data."""
    return {
        "id": 1,
        "name": "Test Product",
        "description": "Test product description",
        "price": 100,
        "stock": 50,
    }


@pytest.fixture
def sample_order_data() -> dict:
    """Return sample order data."""
    return {
        "id": 1,
        "user_id": "usr_test_001",
        "product_id": 1,
        "quantity": 2,
        "status": "pending",
    }


# ============================================================================
# Real Database Fixtures for API Integration Tests
# These require a running MySQL database and should only be used with
# tests marked @pytest.mark.integration
# ============================================================================

@pytest.fixture
def real_settings() -> Settings:
    """Return settings from .env file for real database access."""
    return _original_get_settings()


@pytest.fixture
def real_db_engine(real_settings: Settings):
    """Create real database engine using settings from .env."""
    db_url = f"mysql://{real_settings.db_user}:{real_settings.db_passwd}@{real_settings.db_host}/{real_settings.db_name}"
    engine = create_engine(
        db_url,
        pool_recycle=3600,
        pool_size=1,
        max_overflow=0,
    )
    yield engine
    engine.dispose()


@pytest.fixture
def real_db_session(real_db_engine) -> Generator[Session, None, None]:
    """Create real database session for integration tests."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=real_db_engine)
    db = SessionLocal()
    try:
        yield db
        db.rollback()  # Rollback any changes after test
    finally:
        db.close()


@pytest.fixture
def real_test_client(real_db_session: Session, real_settings: Settings) -> Generator[_FastAPITestClient, None, None]:
    """Create test client with real database access for integration tests."""
    # Import puffy locally to avoid Client naming collision
    from app.puffy import puffy

    def override_get_db():
        try:
            yield real_db_session
        finally:
            pass

    def override_get_settings():
        return real_settings

    # Override dependencies
    puffy.dependency_overrides[get_db] = override_get_db
    puffy.dependency_overrides[get_settings] = override_get_settings

    with _FastAPITestClient(puffy) as client:
        yield client

    # Clear overrides
    puffy.dependency_overrides.clear()


# ============================================================================
# Database Entity Fixtures
# ============================================================================

@pytest.fixture
def test_user_with_balance(test_db_session: Session):
    """Create a test user with balance."""
    from app.models.user import User, Balance

    user = User(
        id="test_user_123",
        address="7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        address_hex="0x7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        twitter=None,
        email=None,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )
    test_db_session.add(user)

    balance = Balance(
        id="test_user_123",
        referrals=0,
        indirect_referrals=0,
        points=100,
        usd=Decimal("0.00"),
        total_usd=Decimal("0.00"),
        updated_at=datetime.datetime.now()
    )
    test_db_session.add(balance)
    test_db_session.commit()

    return user


@pytest.fixture
def test_campaign(test_db_session: Session):
    """Create a test campaign with a specific ID."""
    from app.models.product import Campaign
    from app.enums import Chain, VmType

    campaign = Campaign(
        id=999,
        name="Test Campaign",
        edition="v1",
        requirement="Hold NFT",
        collection_address="EQTestCollectionAddress123",
        collection_name="Test Collection",
        chain=Chain.TON,
        vm_type=VmType.TVM
    )
    test_db_session.add(campaign)
    test_db_session.commit()

    return campaign


@pytest.fixture
def test_product(test_db_session: Session):
    """Create a test product with a specific ID."""
    from app.models.product import Product
    from app.enums import ProductType

    product = Product(
        id="test_product_123",
        name="Test Product",
        description="A test product for testing",
        price=Decimal("99.99"),
        qty=100,
        product_type=ProductType.OTHER,
        passcode_enabled=False,
        sm_icon_url=None,
        md_icon_url=None,
        lg_icon_url=None,
        image_url=None,
        reward_points=10,
        reward_referee_points=5
    )
    test_db_session.add(product)
    test_db_session.commit()

    return product


@pytest.fixture
def test_promote_nft(test_db_session: Session, test_user_with_balance, test_campaign):
    """Create a test PromoteNft using the provided user_id and campaign_id."""
    from app.models.user import PromoteNft

    promote_nft = PromoteNft(
        id=1,
        user_id=test_user_with_balance.id,
        nft_address="EQTestNftAddress123456789",
        campaign_id=test_campaign.id
    )
    test_db_session.add(promote_nft)
    test_db_session.commit()

    return promote_nft
