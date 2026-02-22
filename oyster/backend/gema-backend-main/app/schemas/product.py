from app.schemas.base import BaseModel
from pydantic import Field
from typing import List, Optional
import decimal


class UnpackProbability(BaseModel):
    """Schema for unpack probability"""
    id: int = Field(description="Unique probability ID")
    strategy_id: int = Field(description="Foreign key to unpack_strategies.id")
    next_strategy_id: Optional[int] = Field(
        default=None, 
        description="Foreign key to unpack_strategies.id (for tree node)"
    )
    nft_category_id: Optional[int] = Field(
        default=None, 
        description="Foreign key to nft_categories.id (for leaf node)"
    )
    probability: int = Field(
        ge=0, 
        le=1000, 
        description="Probability in per mille (1000 = 100%)"
    )
    nft_category: Optional["NftCategory"] = None 

    class Config:
        from_attributes = True



class UnpackStrategy(BaseModel):
    """Schema for unpack strategy"""
    id: int = Field(description="Unique strategy ID")
    name: str = Field(max_length=255, description="Strategy name")
    description: str = Field(max_length=255, description="Strategy description")
    probabilities: List[UnpackProbability] = None 

    class Config:
        from_attributes = True


class UnpackProbabilityNode(BaseModel):
    """Schema for a probability node in the strategy tree"""
    id: int = Field(description="Unique probability ID")
    probability: int = Field(
        ge=0, 
        le=1000, 
        description="Probability in per mille (1000 = 100%)"
    )
    nft_category_id: Optional[int] = Field(
        default=None,
        description="Product ID for leaf nodes"
    )
    next_strategy: Optional['UnpackStrategyTree'] = Field(
        default=None,
        description="Next strategy for intermediate nodes"
    )
    
    class Config:
        from_attributes = True



class UnpackStrategyTree(BaseModel):
    """Schema for unpack strategy with recursive probability tree"""
    id: int = Field(description="Unique strategy ID")
    name: str = Field(max_length=255, description="Strategy name")
    description: str = Field(max_length=255, description="Strategy description")
    probabilities: List['UnpackProbabilityNode'] = Field(
        description="Probability distributions for this strategy"
    )
    
    class Config:
        from_attributes = True



UnpackStrategyTree.model_rebuild()
UnpackProbabilityNode.model_rebuild()

class UnpackStrategyCreate(BaseModel):
    """Schema for creating a unpack strategy"""
    name: str = Field(max_length=255, description="Strategy name")
    description: str = Field(max_length=255, description="Strategy description")


class UnpackProbabilityCreate(BaseModel):
    """Schema for creating a unpack probability"""
    strategy_id: int = Field(description="Foreign key to unpack_strategies.id")
    next_strategy_id: Optional[int] = Field(
        default=None, 
        description="Foreign key to unpack_strategies.id (for tree node)"
    )
    nft_category_id: Optional[int] = Field(
        default=None, 
        description="Foreign key to nft_categories.id (for leaf node)"
    )
    probability: int = Field(
        ge=0, 
        le=1000, 
        description="Probability in per mille (1000 = 100%)"
    )



class Product(BaseModel):
    id: int
    name: str 
    description: str 
    price: decimal.Decimal
    qty: int
    sm_icon_url: Optional[str] = None
    md_icon_url: Optional[str] = None
    lg_icon_url: Optional[str] = None
    image_url: Optional[str] = None
    reward_points: int = 0
    reward_referral_points: int = 0
    strategy: Optional["UnpackStrategy"] = None 

    class Config:
        from_attributes = True


class NftCategory(BaseModel):
    """Schema for NFT category"""
    id: int = Field(description="Unique category ID")
    name: str = Field(max_length=255, description="Category name")
    symbol: str = Field(max_length=255, description="Category symbol")
    collection_id: Optional[str] = Field(
        default=None, 
        max_length=255, 
        description="Collection ID on chain"
    )
    merkletree_id: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Merkle tree ID"
    )
    description: str = Field(max_length=255, description="Category description")
    price: decimal.Decimal = Field(description="Price in cents (e.g., 159.99 as 15999)")
    image_url: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Image URL"
    )
    on_chain_image_url: Optional[str] = Field(
        default=None,
        max_length=255,
        description="On-chain image URL"
    )
    video_url: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Video URL"
    )
    lg_icon_url: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Large icon URL"
    )
    class Config:
        from_attributes = True


class ExpandedNftDistribution(BaseModel):
    nft_category: NftCategory
    probability: decimal.Decimal


class ExpandedProduct(Product):
    id: int 
    name: str 
    description: str
    price: decimal.Decimal
    sm_icon_url: Optional[str] = None
    md_icon_url: Optional[str] = None
    lg_icon_url: Optional[str] = None
    image_url: Optional[str] = None
    nft_distribution: List[ExpandedNftDistribution]



