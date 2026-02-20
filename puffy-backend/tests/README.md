# Testing Guide

This directory contains all tests for the puffy-backend project.

## Project Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures for all tests
├── unit/                # Unit tests
│   ├── __init__.py
│   ├── conftest.py      # Unit test fixtures
│   ├── test_token_service.py
│   └── test_utils.py
└── api/                 # API integration tests
    ├── __init__.py
    ├── conftest.py      # API test fixtures
    ├── test_user_api.py
    ├── test_product_api.py
    └── test_order_api.py
```

## Installation

Install test dependencies:

```bash
pip install -r requirements.txt
```

## Running Tests

### Run all tests:
```bash
pytest
```

### Run only unit tests:
```bash
pytest -m unit
```

### Run only API tests:
```bash
pytest -m api
```

### Run a specific test file:
```bash
pytest tests/unit/test_token_service.py
```

### Run a specific test function:
```bash
pytest tests/unit/test_token_service.py::TestTokenService::test_gen_token_creates_valid_jwt
```

### Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

### Run in verbose mode:
```bash
pytest -v
```

### Run and show print statements:
```bash
pytest -s
```

## Writing Tests

### Unit Tests

Unit tests should focus on testing individual functions and classes in isolation.

```python
import pytest

@pytest.mark.unit
class TestMyService:
    def test_some_function(self):
        # Arrange
        input_data = "test"

        # Act
        result = my_function(input_data)

        # Assert
        assert result == expected
```

### API Tests

API tests test the HTTP endpoints and their integration.

```python
import pytest
from fastapi import status

@pytest.mark.api
class TestMyEndpoint:
    def test_endpoint_returns_200(self, test_client):
        response = test_client.get("/api/endpoint")
        assert response.status_code == status.HTTP_200_OK
```

## Fixtures

Available fixtures in `conftest.py`:

- `test_settings` - Test configuration settings
- `test_engine` - SQLAlchemy test engine
- `test_db_session` - SQLAlchemy test session
- `test_client` - FastAPI test client
- `mock_cache_db` - Mocked cache database
- `mock_redis` - Mocked Redis client
- `mock_user_service` - Mocked user service
- `mock_product_service` - Mocked product service
- `mock_order_service` - Mocked order service
- `mock_token_service` - Mocked token service
- `mock_sol_service` - Mocked Solana service
- `auth_headers` - Pre-configured auth headers

## Markers

Tests can be marked with:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.api` - API tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.integration` - Integration tests
