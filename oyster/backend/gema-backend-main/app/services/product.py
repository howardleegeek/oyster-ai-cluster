import logging 
from typing import List, Optional
from typing_extensions import Annotated
from fastapi import Depends

from app.db import *
from app.db.product import Product as ProductRepo
import app.schemas as schemas 
from app.services.error import *


logger = logging.getLogger(__name__)


class ProductService:

    def __init__(self, 
        repo: ProductRepo, 
    ):
        self.repository = repo

    def get_products(self) -> List[schemas.Product]:
        products_db = self.repository.get_products()
        return [schemas.Product.module_validate(p) for p in products_db]

    def get_product(self, product_id: int) -> Optional[schemas.Product]:
        return schemas.Product.module_validate(self.repository.get_product(product_id))
    
    def get_expanded_product(self, product_id: int) -> Optional[schemas.ExpandedProduct]:
        product = self.get_product(product_id)
        return self.expand_product(product)
    
    def expand_product(self, product: schemas.Product) -> schemas.ExpandedProduct:
        e_product = schemas.ExpandedProduct(
            id=product.id, name=product.name, description=product.description,
            price=product.price, sm_icon_url=product.sm_icon_url,
            md_icon_url=product.md_icon_url, lg_icon_url=product.lg_icon_url,
            image_url=product.image_url, nft_distribution=[]
        )
        total_prob = sum([i.probability for i in product.strategy.prodabilities])
        for p in product.strategy.probabilities:
            e_product.nft_distribution.append(schemas.ExpandedNftDistribution(
                probability=round(p.probability / total_prob, 4),
                nft_category=p.nft_category
            ))
        return e_product


def get_product_service(
    repo: ProductRepoDep, 
):
    return ProductService(repo)


ProductServiceDep = Annotated[
    ProductService, Depends(get_product_service)]

   
