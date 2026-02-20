from app.enums import OrderStatus, ShippingStatus, PaymentStatus, Currency, OrderType, PaymentType
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from decimal import Decimal
from datetime import datetime


class OrderToken(BaseModel):
    # the token for purchasing product/item
    id: int
    name: str 
    seq: int 
    web3_name: Optional[str] = Field(None, description="Web3 name")
    owner: Optional[str] = Field(None, description="Owner address")
    on_chain: Optional[bool] = Field(None, description="Is on-chain")
    order_id: str


class OrderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_item_id: Optional[int] = None
    order_id: Optional[str] = None
    product_id: str
    price: Decimal = 0.0
    qty: int
    paid_qty: int = 0
    free_qty: int = 0


class OrderItemCreate(BaseModel):
    """Schema for creating an order item. Backend determines paid/free qty based on discount strategies."""
    product_id: str = Field(..., description="Product ID")
    qty: int = Field(..., gt=0, description="Quantity")


class ShippingAddress(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: Optional[str] = Field(max_length=255, default=None)
    name: Optional[str] = Field(max_length=50, default=None)
    email: Optional[str] = Field(max_length=255, default=None)
    phone_number: Optional[str] = Field(max_length=50, default=None, alias="phone")
    address_line_1: Optional[str] = Field(max_length=100, default=None, alias="line1")
    address_line_2: Optional[str] = Field(max_length=100, default=None, alias="line2")
    city: Optional[str] = Field(max_length=100, default=None)
    state: Optional[str] = Field(max_length=100, default=None)
    country: Optional[str] = Field(max_length=100, default=None)
    postal_code: Optional[str] = Field(max_length=100, default=None)
    pccc: Optional[str] = Field(max_length=100, default=None)


class OrderCreate(BaseModel):
    """Schema for creating a new order."""
    shipping_address: ShippingAddress = Field(..., description="Shipping address")
    order_items: List[OrderItemCreate] = Field(..., min_length=1, description="List of order items")
    referral_code: Optional[str] = Field(None, description="Referral code")
    pass_code: Optional[str] = Field(None, description="Pass code")


class ShippingTrack(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(max_length=255, default=None)
    order_id: str = Field(max_length=255, default=None)
    seq: int = 0
    carrier: Optional[str] = Field(max_length=50, default=None)
    tracking_no: Optional[str] = Field(max_length=50, default=None)
    status: Optional[ShippingStatus] = None
    comments: Optional[str] = Field(max_length=200, default=None)


class Payment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str  # trx_hash
    order_id: str
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    value: Optional[int] = None
    amount: Optional[Decimal] = None
    currency: Optional[Currency] = None
    created_at: datetime
    transferred_at: datetime
    success: bool
    status: Optional[PaymentStatus] = None


class PaymentBase(BaseModel):
    user_id: int
    order_id: int
    transaction_id: str = Field(..., max_length=255)
    amount: float = Field(..., gt=0)
    status: PaymentStatus = PaymentStatus.PENDING


class Order(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = Field(max_length=255, default=None)
    user_id: Optional[str] = Field(max_length=255, default=None)
    order_type: Optional[OrderType] = OrderType.NORMAL
    price: Optional[Decimal] = 0
    currency: Optional[Currency] = Currency.USD
    shipping_fee: Optional[Decimal] = 0
    total_amount: Optional[Decimal] = 0
    referral_code: Optional[str] = None
    pass_code: Optional[str] = None
    status: Optional[OrderStatus] = None
    payment_type: Optional[PaymentType] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    addr_locked: Optional[bool] = False
    order_token: Optional[OrderToken] = None
    items: Optional[List[OrderItem]] = None
    payment: Optional[Payment] = None
    shipping_address: Optional[ShippingAddress] = None
    shipping_track: Optional[List[ShippingTrack]] = None


class TieredReward(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item: str
    user_level: int
    hierarchy_level: int
    usd: Optional[Decimal] = 0
    upoints: int


class Referral(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    referral_code: str = Field(max_length=255, default=None)
    owner: str = Field(max_length=255, default=None)
    rewards: List[TieredReward] = [] # for user info


class PromoteInfo(BaseModel):
    referrer: Optional[str] = None
