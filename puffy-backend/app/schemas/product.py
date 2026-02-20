from app.schemas.base import BaseModel
from app.enums import ProductType
from pydantic import Field
from typing import List, Optional
from decimal import Decimal 


class Product(BaseModel):
    id: str = Field(max_length=255,
        description="Unique product ID", example="phantom-vape")
    name: str = Field(max_length=255,
        description="Product name", example="Comunity Vape")
    community: Optional[str] = None
    description: str = Field(max_length=512,
        description="Product description", example="A soft and cuddly teddy bear.")
    product_type: ProductType = Field(default=ProductType.OTHER, description="Product type")
    passcode_enabled: bool = False
    price: Decimal
    qty: int
    sm_icon_url: Optional[str] = None
    md_icon_url: Optional[str] = None
    lg_icon_url: Optional[str] = None
    image_url: Optional[str] = None
    color: Optional[str] = None 
    reward_points: int = 0
    reward_referee_points: int = 0
    eligible_for_nft: bool = False
    promote_free: Optional[bool] = Field(None, description="Free for users with promote_nfts")

    class Config:
        from_attributes = True
