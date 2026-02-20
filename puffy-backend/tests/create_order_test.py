"""
Real scenario API test for order creation using requests library.

Run with: python tests/create_order_test.py
Make sure the API server is running before executing this script.

These tests are skipped in pytest because they require a running API server.
"""

import pytest
import requests
import json

# Skip all tests in this module — they require a running API server
pytestmark = pytest.mark.skip(reason="Requires running API server at localhost:9000")

# Configuration
API_BASE_URL = "http://localhost:9000"  # Update if your API runs on different host/port
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6InVzcl8wMDEiLCJhZGRyZXNzIjoiMHg3MUM3NjU2RUM3YWI4OGIwOThkZWZCNzUxQjc0MDFCNWY2ZDg5NzZGIiwiZXhwIjoxMTExMTExMTExMTF9.0LEi3qgYb5HQz99RIqNic-5Apv0bNB-Sr0KAwghC-7g"

# Headers with authentication
headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Available products from database
PRODUCT_IDS = ["prod_12_4", "prod_2_2", "prod_2_1", "prod_10_1", "prod_12_3", "prod_10_2"]


def test_create_order_no_discount():
    """Test creating order with no passcode or referral code."""
    print("\n=== Test 1: Create order with no discount ===")

    order_data = {
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
                "product_id": PRODUCT_IDS[0],
                "qty": 1
            }
        ]
    }

    response = requests.post(
        f"{API_BASE_URL}/order/",
        json=order_data,
        headers=headers
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code != 403 else response.text}")

    return response


def test_create_order_with_passcode():
    """Test creating order with passcode (1 free piece)."""
    print("\n=== Test 2: Create order with passcode ===")

    order_data = {
        "shipping_address": {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone_number": "+1234567890",
            "address_line_1": "456 Oak Ave",
            "city": "Los Angeles",
            "state": "CA",
            "country": "US",
            "postal_code": "90001"
        },
        "order_items": [
            {
                "product_id": PRODUCT_IDS[1],
                "qty": 3  # Expecting: 1 free, 2 paid
            }
        ],
        "pass_code": "passabc"  # Replace with actual passcode from your database
    }

    response = requests.post(
        f"{API_BASE_URL}/order/",
        json=order_data,
        headers=headers
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code != 403 else response.text}")

    return response


def test_create_order_with_referral_code():
    """Test creating order with referral code."""
    print("\n=== Test 3: Create order with referral code ===")

    order_data = {
        "shipping_address": {
            "name": "Bob Smith",
            "email": "bob@example.com",
            "phone_number": "+1234567890",
            "address_line_1": "789 Pine Rd",
            "city": "Chicago",
            "state": "IL",
            "country": "US",
            "postal_code": "60601"
        },
        "order_items": [
            {
                "product_id": PRODUCT_IDS[2],
                "qty": 2
            }
        ],
        "referral_code": "REFERRAL123"  # Replace with actual referral code from your database
    }

    response = requests.post(
        f"{API_BASE_URL}/order/",
        json=order_data,
        headers=headers
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code != 403 else response.text}")

    return response


def test_create_order_multiple_items():
    """Test creating order with multiple items."""
    print("\n=== Test 4: Create order with multiple items ===")

    order_data = {
        "shipping_address": {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "phone_number": "+1234567890",
            "address_line_1": "321 Elm St",
            "city": "Houston",
            "state": "TX",
            "country": "US",
            "postal_code": "77001"
        },
        "order_items": [
            {
                "product_id": PRODUCT_IDS[3],
                "qty": 1
            },
            {
                "product_id": PRODUCT_IDS[4],
                "qty": 2
            }
        ]
    }

    response = requests.post(
        f"{API_BASE_URL}/order/",
        json=order_data,
        headers=headers
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code != 403 else response.text}")

    return response


def test_dry_run_order():
    """Test dry run order creation (no actual order created)."""
    print("\n=== Test 5: Dry run order creation ===")

    order_data = {
        "shipping_address": {
            "name": "Test User",
            "country": "US"
        },
        "order_items": [
            {
                "product_id": PRODUCT_IDS[5],
                "qty": 1
            }
        ]
    }

    response = requests.post(
        f"{API_BASE_URL}/order/?dry_run=true",
        json=order_data,
        headers=headers
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code != 403 else response.text}")

    return response


def test_get_products():
    """Test getting all products to verify they exist."""
    print("\n=== Test: Get all products ===")

    response = requests.get(
        f"{API_BASE_URL}/product/",
        headers=headers
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        products = response.json()
        print(f"Found {len(products)} products:")
        for product in products:
            print(f"  - ID: {product.get('id')}, Name: {product.get('name')}, Price: {product.get('price')}")
    else:
        print(f"Response: {response.text}")

    return response


def test_validate_passcode():
    """Test passcode validation endpoint."""
    print("\n=== Test: Validate passcode ===")

    response = requests.post(
        f"{API_BASE_URL}/order/validate-passcode",
        json={"passcode": "TESTPASS123"},
        headers=headers
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code != 403 else response.text}")

    return response


def test_validate_referralcode():
    """Test referral code validation endpoint."""
    print("\n=== Test: Validate referral code ===")

    response = requests.post(
        f"{API_BASE_URL}/order/validate-referralcode",
        json={"referral_code": "REFERRAL123"},
        headers=headers
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code != 403 else response.text}")

    return response


def main():
    """Run all tests."""
    print("=" * 60)
    print("Order API Real Scenario Tests")
    print("=" * 60)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Auth Token: {AUTH_TOKEN}")
    print(f"Products: {PRODUCT_IDS}")

    # First, check if products exist
    test_get_products()

    # Test passcode and referral code validation
    test_validate_passcode()
    test_validate_referralcode()

    # Test order creation scenarios
    test_create_order_no_discount()
    test_create_order_with_passcode()
    test_create_order_with_referral_code()
    test_create_order_multiple_items()
    test_dry_run_order()

    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
