from typing import List
import logging

from fastapi import APIRouter

from app.error import ServerError
from app.plib import *
from app.ext_service import *
from app.services import * 
import app.schemas as schemas
from app.db import *


router = APIRouter(
    prefix="/info",
    tags=["Info"]
)


logger = logging.getLogger(__name__)


@router.get("/products")
def get_products(product_service: ProductServiceDep) -> List[schemas.Product]:
    try:
        return product_service.get_products()
    except Exception as err:
        print(err)
        raise ServerError.DB_ERROR.http()

    
@router.get("/product/{product_id}")
def get_product(
    product_id: int,
    product_service: ProductServiceDep) -> schemas.ExpandedProduct:
    try:
        return product_service.get_expanded_product(id=product_id)
    except Exception as err:
        print(err)
        raise ServerError.DB_ERROR.http()
