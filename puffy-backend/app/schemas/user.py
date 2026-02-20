from app.schemas.base import BaseModel
from app.enums import NftStatus, Currency, Chain
from enum import Enum
from pydantic import Field
from typing import List, Optional
from decimal import Decimal
from datetime import datetime


class Event(str, Enum):
    """Event enumeration matching models.user.Event"""
    REFEREE = "referee"
    REFERRAL = "referral"
    INDIRECT_REFERRAL = "indirect_referral"
    PURCHASE = "purchase"
    PROMOTE_REFERRAL = "promote_referral"
    PROMOTE_REFEREE = "promote_referee"
    TWITTER_AUTH = "twitter_auth"
    TWITTER_FOLLOW_PUFFY = "twitter_follow_puffy"
    TWITTER_FOLLOW_SOON = "twitter_follow_soon"
    TWITTER_RETWEET = "twitter_retweet"
    TG_AUTH = "tg_auth"
    TG_JOIN_GROUP = "tg_join_group"
    DISCORD_JOIN_PUFFY = "discord_join_puffy"
    DISCORD_JOIN_SOON = "discord_join_soon"


class RewardRecord(BaseModel):
    id: Optional[int] = None
    user_id: str
    event: str
    item: Optional[str] = None
    points: int = 0
    usd: Decimal = 0
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Balance(BaseModel):
    id: Optional[str] = None
    referrals: int = 0
    indirect_referrals: int = 0
    points: int = 0
    usd: Decimal = 0
    total_usd: Decimal = 0
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PromoteNft(BaseModel):
    id: Optional[int] = None
    user_id: Optional[str] = None
    campaign_id: Optional[int] = None
    nft_address: str
    promotion: int = None

    class Config:
        from_attributes = True


class ReferralCode(BaseModel):
    id: Optional[int] = None
    user_id: Optional[str] = None
    referral_code: str
    max_uses: int
    current_uses: int

    class Config:
        from_attributes = True


class PassCode(BaseModel):
    id: Optional[int] = None
    user_id: Optional[str] = None
    pass_code: str
    max_uses: int
    current_uses: int

    class Config:
        from_attributes = True


class ReferralCodeUsage(BaseModel):
    id: Optional[int] = None
    code_owner_id: str
    code_user_id: str
    order_id: str
    used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PassCodeUsage(BaseModel):
    id: Optional[int] = None
    code_owner_id: str
    code_user_id: str
    order_id: str
    used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Nft(BaseModel):
    id: Optional[int] = None
    order_id: str
    user_id: str
    name: str
    symbol: str
    seq: int
    token_address: Optional[str] = None
    collection_address: Optional[str] = None
    meta_url: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    on_chain_image_url: Optional[str] = None
    minted_times: Optional[int] = None
    created_at: Optional[datetime] = None
    status: NftStatus = NftStatus.NEW
    minted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(BaseModel):
    id: Optional[str] = Field(max_length=255)
    address: str = Field(max_length=255)
    address_hex: Optional[str] = Field(max_length=255, default=None)
    twitter_id: Optional[str] = Field(max_length=255, default=None)
    twitter_name: Optional[str] = Field(max_length=255, default=None)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    balance: Optional[Balance] = None
    records: Optional[List[RewardRecord]] = []
    referral_code: Optional[ReferralCode] = None
    pass_code: Optional[PassCode] = None
    promote_nfts: Optional[List[PromoteNft]] = []
    nfts: Optional[List[Nft]] = []

    class Config:
        from_attributes = True


# Legacy schemas for backward compatibility (if needed by existing code)
class TieredReward(BaseModel):
    id: int 
    item: str 
    user_level: int 
    hierarchy_level: int 
    usd_pct: Decimal 
    points: int



class UserBrief(BaseModel):
    """
    for ranking and dashboard
    """
    twitter: str
    points: int


class NftCollectionMeta(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    symbol: Optional[str] = None
    description: Optional[str] = None
    chain: Chain
    collection_id: Optional[str] = None
    merkletree_id: Optional[str] = None
    image_url: Optional[str] = None
    collection_image_url: Optional[str] = None
    video_url: Optional[str] = None
    on_chain_image_url: Optional[str] = None
    gas_fee: Decimal
    gas_currency: Currency


class NftInfo(BaseModel):
    id: str
    name: str 
    nft_collection_meta_id: int
    owner: str
    meta_url: Optional[str] = None
    status: Optional[NftStatus] = None 
    minted_times: Optional[int] = None
    created_at: Optional[datetime] = None 
    minted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    token_address: Optional[str] = None


class TwitterOauthResult(BaseModel):
    access_token: str
    user_id: str
    user_name: str
    user_icon_url: Optional[str] = None

