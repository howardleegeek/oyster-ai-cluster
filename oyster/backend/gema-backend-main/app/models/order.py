from app.models.base import BaseTable
from sqlalchemy import Boolean, ForeignKey, Integer, BigInteger, String, DateTime, Enum
from sqlalchemy.types import DECIMAL
import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing import Optional
from decimal import Decimal
from app.enums import OrderStatus, ShippingStatus, PaymentStatus, OrderType


class Order(BaseTable):
    __tablename__ = 'orders'

    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, nullable=False)
    user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey('users.id'), nullable=False)
    product_id = mapped_column(ForeignKey("products.id"), nullable=False)
    price: Mapped[Decimal] = mapped_column(DECIMAL(20, 9), nullable=False)
    currency: Mapped[str] = mapped_column(String(255), default='USD')
    order_type: Mapped[Optional[OrderType]] = mapped_column(Enum(OrderType), nullable=True)
    item: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[Optional[OrderStatus]] = mapped_column(Enum(OrderStatus), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=None, nullable=True)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=None, nullable=True)
    payment: Mapped["Payment"] = relationship(
        back_populates="order")
    
    shipping_address: Mapped["ShippingAddress"] = relationship(back_populates="order")
    shipping_track: Mapped["ShippingTrack"] = relationship(back_populates="order")


class Nft(BaseTable):
    __tablename__ = 'nfts'

    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, nullable=False)
    user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey('users.id'), nullable=False)
    order_id: Mapped[str] = mapped_column(
        String(255), ForeignKey('orders.id'), nullable=False)
    nft_category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("nft_categories.id"))
    name: Mapped[str] = mapped_column(String(255))
    token_address: Mapped[str] = mapped_column(String(255))
    minted_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=None, nullable=True)


class ShippingAddress(BaseTable):
    __tablename__ = 'shipping_addresses'

    id: Mapped[str] = mapped_column(
        ForeignKey("orders.id"), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(
        String(255), index=True, nullable=True)
    phone_number: Mapped[str] = mapped_column(String(50), nullable=True)
    address_line_1: Mapped[str] = mapped_column(String(100), nullable=True)
    address_line_2: Mapped[str] = mapped_column(String(100), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(100), nullable=True)
    pccc: Mapped[str] = mapped_column(String(100), nullable=True)
    order: Mapped["Order"] = relationship(back_populates="shipping_address")


# create shipping track for confirmed orders only
class ShippingTrack(BaseTable):
    __tablename__ = 'shipping_tracks'

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"))
    seq: Mapped[int] = mapped_column(Integer) # 0,1,2,3
    carrier: Mapped[str] = mapped_column(String(50), nullable=True)
    tracking_no: Mapped[str] = mapped_column(String(50), nullable=True)
    status: Mapped[Optional[ShippingStatus]] = mapped_column(Enum(ShippingStatus), nullable=True)
    comments: Mapped[str] = mapped_column(String(200), nullable=True)
    order: Mapped["Order"] = relationship(back_populates="shipping_track")


class Payment(BaseTable):
    __tablename__ = 'payments'

    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, nullable=False)  # trx_hash
    order_id: Mapped[str] = mapped_column(
        String(255), ForeignKey('orders.id'), nullable=False)
    from_address: Mapped[str] = mapped_column(
        String(255), index=True, nullable=True)
    to_address: Mapped[str] = mapped_column(
        String(255), nullable=True)
    value: Mapped[int] = mapped_column(BigInteger, nullable=True)
    amount = mapped_column(DECIMAL(20, 9))
    currency = mapped_column(String(30), nullable=True)
    created_at = mapped_column(DateTime, index=True, nullable=True)
    transferred_at = mapped_column(DateTime, index=True, nullable=True)
    success = mapped_column(Boolean)
    status: Mapped[Optional[PaymentStatus]] = mapped_column(Enum(PaymentStatus), nullable=True)
    order: Mapped["Order"] = relationship(
        back_populates="payment")
