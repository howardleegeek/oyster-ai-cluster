import logging
from typing import List, Optional, Annotated
from fastapi import Depends

from app.db.product import ProductRepo, ProductRepoDep
import app.schemas as schemas


logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self, product_repo: ProductRepo):
        self.product_repo = product_repo

    def get_products(self, limit: int = 20, offset: int = 0) -> List[schemas.Product]:
        products = self.product_repo.get_products(limit=limit, offset=offset)
        return [schemas.Product.model_validate(p) for p in products]

    def get_product(self, product_id: str) -> Optional[schemas.Product]:
        product = self.product_repo.get_product(product_id)
        if product:
            return schemas.Product.model_validate(product)
        return None


def get_product_service(product_repo: ProductRepoDep):
    return ProductService(product_repo)


ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
