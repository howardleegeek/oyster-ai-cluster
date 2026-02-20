from typing import List
import logging

from fastapi import APIRouter, HTTPException, Query

from app.error import ServerError
from app.plib import *
from app.ext_service import *
from app.services import *
import app.schemas as schemas
from app.db import *


router = APIRouter(
    prefix="/product",
    tags=["Product"]
)


logger = logging.getLogger(__name__)


@router.get("/")
def get_products(
    product_service: ProductServiceDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> List[schemas.Product]:
    try:
        return product_service.get_products(limit=limit, offset=offset)
    except Exception as err:
        print(err)
        raise ServerError.DB_ERROR.http()

    
