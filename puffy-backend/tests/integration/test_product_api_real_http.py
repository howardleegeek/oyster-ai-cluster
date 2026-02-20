"""Integration tests that make real HTTP requests to a running server.

These tests require the server to be running at http://127.0.0.1:9000

Run with:
    pytest tests/integration/test_product_api_real_http.py -v
"""

import pytest
import requests
import uuid
import datetime
from typing import List, Dict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Import models and services
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models.user import User, Balance
from app.services.token import Token
from app.config import Settings, get_settings


@pytest.mark.integration
class TestProductListRealHTTP:
    """Test cases for /product/ endpoint using real HTTP requests."""

    BASE_URL = "http://127.0.0.1:9000"

    def test_get_products_returns_list_with_id_and_price(self):
        """Test that GET /product/ returns a list of products with id and price."""
        response = requests.get(f"{self.BASE_URL}/product/")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"

        # If no products exist, test passes but we can't validate product structure
        if len(data) == 0:
            pytest.skip("No products in database, skipping structure validation")

        # Validate each product has id and price
        for product in data:
            assert "id" in product, f"Product missing 'id' field: {product}"
            assert "price" in product, f"Product missing 'price' field: {product}"

            # Validate types
            assert isinstance(product["id"], str), f"Product id must be string, got {type(product['id'])}"
            # Price can be string or int in JSON (Decimal gets serialized)
            assert isinstance(product["price"], (str, int, float)), \
                f"Product price must be numeric, got {type(product['price'])}"

            # Validate non-empty values
            assert len(product["id"]) > 0, "Product id cannot be empty"
            # Price should be positive
            price = float(product["price"]) if isinstance(product["price"], str) else product["price"]
            assert price >= 0, f"Product price must be non-negative, got {price}"

    def test_get_products_response_time(self):
        """Test that /product/ endpoint responds within reasonable time."""
        import time

        start_time = time.time()
        response = requests.get(f"{self.BASE_URL}/product/")
        elapsed_time = time.time() - start_time

        assert response.status_code == 200
        assert elapsed_time < 2.0, f"Response took too long: {elapsed_time:.2f}s"

    def test_get_products_returns_json_content_type(self):
        """Test that /product/ returns correct Content-Type header."""
        response = requests.get(f"{self.BASE_URL}/product/")

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")


@pytest.mark.integration
class TestProductByIdRealHTTP:
    """Test cases for /product/{id} endpoint using real HTTP requests."""

    BASE_URL = "http://127.0.0.1:9000"

    def test_get_product_by_id(self):
        """Test getting a specific product by ID."""
        # First get a list to find a valid product ID
        list_response = requests.get(f"{self.BASE_URL}/product/")
        assert list_response.status_code == 200

        products = list_response.json()
        if len(products) == 0:
            pytest.skip("No products in database")

        product_id = products[0]["id"]

        # Get specific product
        response = requests.get(f"{self.BASE_URL}/product/{product_id}")

        assert response.status_code == 200
        product = response.json()

        assert "id" in product
        assert "price" in product
        assert product["id"] == product_id

    def test_get_nonexistent_product_returns_404(self):
        """Test that requesting a non-existent product returns 404."""
        response = requests.get(f"{self.BASE_URL}/product/nonexistent-product-id")

        assert response.status_code in [404, 422]  # 404 if not found, 422 if validation fails


@pytest.mark.integration
class TestUserAuthenticationRealHTTP:
    """Test cases for user authentication flow using real HTTP requests.

    This test:
    1. Inserts a user and balance into the database
    2. Generates a JWT token using the token service
    3. Calls /user/me with the Bearer token
    4. Verifies the response contains user_id and address
    """

    BASE_URL = "http://127.0.0.1:9000"

    @pytest.fixture
    def real_db_session(self):
        """Create a real database session for inserting test data."""
        settings = get_settings()
        db_url = f"mysql://{settings.db_user}:{settings.db_passwd}@{settings.db_host}/{settings.db_name}"
        engine = create_engine(db_url, pool_recycle=3600, pool_size=1, max_overflow=0)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()

        # Generate test data
        test_user_id = str(uuid.uuid4())
        test_address = "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"

        # Create user and balance
        user = User(
            id=test_user_id,
            address=test_address,
            address_hex=None,
            twitter=None,
            email=None,
            created_at=datetime.datetime.now()
        )
        balance = Balance(
            id=test_user_id,
            points=0,
            referrals=0,
            indirect_referrals=0,
            usd=0,
            total_usd=0
        )
        user.balance = balance

        session.add(user)
        session.commit()
        session.refresh(user)

        yield test_user_id, test_address, session

        # Cleanup: delete the test user
        try:
            session.rollback()
            session.query(Balance).filter_by(id=test_user_id).delete()
            session.query(User).filter_by(id=test_user_id).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Cleanup error: {e}")
        finally:
            session.close()
            engine.dispose()

    def test_user_me_with_database_insert_and_token(self, real_db_session):
        """Test user authentication flow: insert user -> gen token -> call /user/me."""
        test_user_id, test_address, session = real_db_session

        # Get settings for token service
        settings = get_settings()

        # Step 1: Verify user was inserted into database
        db_user = session.query(User).filter_by(id=test_user_id).first()
        assert db_user is not None, "User should exist in database"
        assert db_user.address == test_address, "User address should match"
        assert db_user.balance is not None, "User should have a balance record"

        # Step 2: Generate token using Token service
        token_service = Token(secret=settings.secret, exp=settings.id_exp)
        from app.schemas.user import User as UserSchema
        user_schema = UserSchema(id=test_user_id, address=test_address)
        token = token_service.gen_token(user_schema)

        assert token is not None, "Token should be generated"
        assert isinstance(token, str), "Token should be a string"
        assert len(token) > 0, "Token should not be empty"

        # Step 3: Call /user/me with Bearer token
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{self.BASE_URL}/user/me", headers=headers)

        # Step 4: Verify response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        data = response.json()
        assert "id" in data, f"Response should contain 'id' field: {data}"
        assert "address" in data, f"Response should contain 'address' field: {data}"

        # Verify the user_id and address match what we inserted
        assert data["id"] == test_user_id, f"User ID mismatch: expected {test_user_id}, got {data['id']}"
        assert data["address"] == test_address, f"Address mismatch: expected {test_address}, got {data['address']}"

    def test_user_me_without_token_returns_403(self):
        """Test that calling /user/me without authentication returns 403."""
        response = requests.get(f"{self.BASE_URL}/user/me")

        # HTTPBearer returns 403 when no Authorization header is provided
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"

    def test_user_me_with_invalid_token_returns_401(self):
        """Test that calling /user/me with invalid token returns 401."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{self.BASE_URL}/user/me", headers=headers)

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
