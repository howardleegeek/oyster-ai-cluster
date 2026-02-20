from typing import List, Optional, Annotated
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import Depends

from app.models.product import Product, RestrictedArea, ShippingFee
from app.db.base import get_db
from app.enums import ProductType


class ProductRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_product(self, product_id: str) -> Product:
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise EntityDoesNotExist(f"Product with id {product_id} does not exist")
        return product

    def get_products(self, limit: int = 20, offset: int = 0) -> List[Product]:
        limit = min(limit, 100)
        return self.db.query(Product).offset(offset).limit(limit).all()

    def get_price(self, product_id: str):
        product = self.get_product(product_id)
        return product.price

    def get_restricted_area(self, product_type: ProductType, country_code: str) -> Optional[RestrictedArea]:
        return self.db.query(
            RestrictedArea).filter(
                RestrictedArea.product_type == product_type, RestrictedArea.country_code == country_code).first()

    def get_shipping_fee(self, country_code: str, product_type: ProductType) -> Optional[Decimal]:
        """Get shipping fee from database for country and product type."""
        shipping_fee = self.db.query(ShippingFee).filter(
            ShippingFee.country_code == country_code,
            ShippingFee.product_type == product_type
        ).first()
        return shipping_fee.fee if shipping_fee else None


def get_product_repo(db: Session = Depends(get_db)):
    return ProductRepo(db)


ProductRepoDep = Annotated[ProductRepo, Depends(get_product_repo)]
