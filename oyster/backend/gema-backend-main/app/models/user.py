from app.models.base import BaseTable
from sqlalchemy import ForeignKey, Integer, String, DateTime
from sqlalchemy.types import DECIMAL
import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing import List
from decimal import Decimal
from app.models.order import Order, Nft


class RewardRecord(BaseTable):
    __tablename__ = 'reward_records'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.id"))
    event: Mapped[str] = mapped_column(String(255))
    item: Mapped[str] = mapped_column(String(255))
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    usd: Mapped[Decimal] = mapped_column(DECIMAL(20, 9), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime)


class User(BaseTable):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    sol_address: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    twitter_id:  Mapped[str] = mapped_column(
        String(255), index=True, nullable=True)
    twitter_name: Mapped[str] = mapped_column(
        String(255), index=True, nullable=True)
    referral_code: Mapped[str] = mapped_column(
        String(255), index=True, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=True)
    balance: Mapped["Balance"] = relationship()
    records: Mapped[List["RewardRecord"]] = relationship()
    nfts: Mapped[List["Nft"]] = relationship()
    orders: Mapped[List["Order"]] = relationship()


class Balance(BaseTable):
    __tablename__ = 'balances'

    id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), primary_key=True)
    referrals = mapped_column(Integer, nullable=False)
    points = mapped_column(Integer, nullable=False)
    updated_at = mapped_column(DateTime, nullable=True)


class ReferralRelationship(BaseTable):
    __tablename__ = 'referral_relationships'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    referee: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.id"), nullable=False)
    referrer: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.id"), nullable=False)
