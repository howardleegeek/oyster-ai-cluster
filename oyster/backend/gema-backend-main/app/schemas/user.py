from pydantic import Field
from typing import List, Optional
import decimal
from datetime import datetime

from app.schemas.base import BaseModel
from app.schemas.order import Order, Nft


class RewardRecord(BaseModel):
    """Schema for reward records"""
    id: Optional[int] = None
    user_id: str = Field(max_length=255, description="Foreign key to users.id")
    event: str = Field(max_length=255, description="Event type")
    item: str = Field(max_length=255, description="Item identifier")
    points: int = Field(description="Points awarded")
    usd: decimal.Decimal = Field(description="USD value awarded")
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        


class Balance(BaseModel):
    """Schema for user balances"""
    id: str = Field(max_length=255, description="Foreign key to users.id")
    referrals: int = Field(default=0, description="Number of referrals")
    points: int = Field(default=0, description="Points balance")
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReferralRelationship(BaseModel):
    """Schema for referral relationships"""
    id: Optional[int] = None
    referee: str = Field(max_length=255, description="Foreign key to users.id (referee)")
    referrer: str = Field(max_length=255, description="Foreign key to users.id (referrer)")

    class Config:
        from_attributes = True


class User(BaseModel):
    """Schema for users"""
    id: Optional[str] = Field(max_length=255, default=None)
    sol_address: str = Field(max_length=255, description="Solana address", unique=True, index=True)
    email: Optional[str] = None 
    twitter_id: Optional[str] = Field(max_length=255, default=None, description="Twitter ID")
    twitter_name: Optional[str] = Field(max_length=255, default=None, description="Twitter display name")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    balance: Optional[Balance] = None
    records: Optional[List[RewardRecord]] = None 
    nfts: Optional[List[Nft]] = None 
    orders: Optional[List[Order]] = None 

    class Config:
        from_attributes = True
