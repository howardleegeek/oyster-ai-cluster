from __future__ import annotations  # Add this at the very top
from app.schemas.base import BaseModel
from app.enums import OrderStatus, ShippingStatus, PaymentStatus, OrderType
from pydantic import Field
from typing import List, Optional
import decimal
from datetime import datetime


class ShippingAddress(BaseModel):
    """Schema for shipping addresses"""
    id: str = Field(max_length=255, description="Foreign key to orders.id")
    name: Optional[str] = Field(max_length=50, default=None, description="Recipient name")
    email: Optional[str] = Field(max_length=255, default=None, description="Email address")
    phone_number: Optional[str] = Field(max_length=50, default=None, description="Phone number")
    address_line_1: Optional[str] = Field(max_length=100, default=None, description="Address line 1")
    address_line_2: Optional[str] = Field(max_length=100, default=None, description="Address line 2")
    city: Optional[str] = Field(max_length=100, default=None, description="City")
    state: Optional[str] = Field(max_length=100, default=None, description="State/Province")
    country: Optional[str] = Field(max_length=100, default=None, description="Country")
    postal_code: Optional[str] = Field(max_length=100, default=None, description="Postal code")
    pccc: Optional[str] = Field(max_length=100, default=None, description="PCCC code")

    class Config:
        from_attributes = True


class ShippingTrack(BaseModel):
    """Schema for shipping tracking"""
    id: str = Field(max_length=30, description="Tracking ID")
    order_id: str = Field(max_length=255, description="Foreign key to orders.id")
    seq: int = Field(description="Sequence number (0,1,2,3)")
    carrier: Optional[str] = Field(max_length=50, default=None, description="Carrier name")
    tracking_no: Optional[str] = Field(max_length=50, default=None, description="Tracking number")
    status: Optional[ShippingStatus] = Field(default=None, description="Tracking status")
    comments: Optional[str] = Field(max_length=200, default=None, description="Comments")

    class Config:
        from_attributes = True


class Payment(BaseModel):
    """Schema for payments"""
    id: str = Field(max_length=255, description="Transaction hash")
    order_id: str = Field(max_length=255, description="Foreign key to orders.id")
    from_address: Optional[str] = Field(max_length=255, default=None, description="Sender address")
    to_address: Optional[str] = Field(max_length=255, default=None, description="Recipient address")
    value: Optional[int] = Field(default=None, description="Transaction value")
    amount: Optional[decimal.Decimal] = Field(default=None, description="Payment amount")
    currency: Optional[str] = Field(max_length=30, default=None, description="Currency")
    created_at: Optional[datetime] = None
    transferred_at: Optional[datetime] = None
    success: Optional[bool] = Field(default=None, description="Payment success status")
    status: Optional[PaymentStatus] = Field(default=None, description="Payment status")

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    product_id: int
    shipping_address: Optional[ShippingAddress] = None


class Order(BaseModel):
    """Schema for orders"""
    id: str = Field(max_length=255, description="Order ID")
    user_id: str = Field(max_length=255, description="Foreign key to users.id")
    price: Optional[decimal.Decimal] = Field(description="Order price")
    currency: str = Field(default='USD', max_length=255, description="Currency")
    order_type: Optional[OrderType] = Field(default=None, description="Order type")
    item: Optional[str] = Field(max_length=255, default=None, description="Item description")
    product_id: Optional[int] = Field(max_length=255, default=None, description="Foreign key to nfts.id")
    status: Optional[OrderStatus] = Field(default=None, description="Order status")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    payment: Optional["Payment"] = None
    shipping_address: Optional["ShippingAddress"] = None
    shipping_track: Optional[List["ShippingTrack"]] = []

    class Config:
        from_attributes = True


# Additional schemas that might be used elsewhere in the application
class Nft(BaseModel):
    """Schema for order tokens (used for purchasing products/items)"""
    id: int
    order_id: str
    user_id: str
    nft_category_id: int
    name: str
    token_address: Optional[str] = Field(None, description="Token address")
    minted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Referral(BaseModel):
    """Schema for referrals"""
    referral_code: str = Field(max_length=255, default=None)
    owner: str = Field(max_length=255, default=None)
    rewards: List[TieredReward] = []  # for user info

    class Config:
        from_attributes = True
