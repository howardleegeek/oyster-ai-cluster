"""API tests for Product endpoints."""

import pytest
from unittest.mock import MagicMock
from fastapi import status
from decimal import Decimal

from app.services.product import get_product_service
from app.schemas.product import Product as ProductSchema
from app.enums import ProductType


@pytest.mark.api
class TestProductListAPI:
    """Test cases for product listing endpoints."""

    def test_get_products(self, test_client, mock_product_service: MagicMock):
        """Test getting all products."""
        mock_products = [
            ProductSchema(
                id="prod_001",
                name="Test Product 1",
                description="First test product",
                product_type=ProductType.OTHER,
                price=Decimal("100.00"),
                qty=50,
            ),
            ProductSchema(
                id="prod_002",
                name="Test Product 2",
                description="Second test product",
                product_type=ProductType.OTHER,
                price=Decimal("200.00"),
                qty=30,
            ),
        ]
        mock_product_service.get_products.return_value = mock_products

        from app.puffy import puffy
        puffy.dependency_overrides[get_product_service] = lambda: mock_product_service
        try:
            response = test_client.get("/product/")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]["id"] == "prod_001"
            assert data[1]["id"] == "prod_002"
        finally:
            puffy.dependency_overrides.pop(get_product_service, None)
