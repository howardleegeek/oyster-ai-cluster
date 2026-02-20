from app.models.base import BaseTable
from sqlalchemy import Boolean, ForeignKey, Integer, BigInteger, String, DateTime, Enum
from sqlalchemy.types import DECIMAL
from app.enums import Event, NftStatus
import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing import List, Optional, Tuple
from decimal import Decimal


class RewardRecord(BaseTable):
    __tablename__ = 'reward_records'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.id"))
    event: Mapped[str] = mapped_column(String(255)) # could be purchase, could be referral
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime)


class User(BaseTable):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    address: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    address_hex: Mapped[str] = mapped_column(
        String(255), index=True, nullable=True)
    twitter_id:  Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=True)
    twitter_name:  Mapped[str] = mapped_column(
        String(255), index=True, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=True)
    balance: Mapped["Balance"] = relationship()
    records: Mapped[List["RewardRecord"]] = relationship()
    referral_code: Mapped["ReferralCode"] = relationship()
    pass_code: Mapped["PassCode"] = relationship()
    promote_nfts: Mapped[List["PromoteNft"]] = relationship()
    nfts: Mapped[List["Nft"]] = relationship()

    def get_level(self) -> int:
        return self.balance.get_level()
    
    def add_referral_reward(
            self, item: str, oys: int, usd: int,
            created_at: Optional[datetime.datetime] = None):
        reward = (oys, usd)
        self.balance.referrals += 1
        return self.update_points_and_gen_record(
            item, Event.REFERRAL, created_at, reward)

    def add_referee_reward(
            self, item: str, oys: int,
            created_at: Optional[datetime.datetime] = None):
        reward = (oys, 0)
        return self.update_points_and_gen_record(
            item, Event.REFEREE, created_at, reward)

    def add_indirect_referral_reward(
            self, item: str, oys: int, usd: Decimal,
            created_at: Optional[datetime.datetime] = None):
        reward = (oys, usd)
        self.balance.indirect_referrals += 1
        return self.update_points_and_gen_record(
            item, Event.INDIRECT_REFERRAL, created_at, reward)

    def add_purchase_reward(
            self, item: str, oys: int,
            created_at: Optional[datetime.datetime] = None):
        reward = (oys, 0)
        return self.update_points_and_gen_record(
            item, Event.PURCHASE, created_at, reward)

    def update_points_and_gen_record(
        self,
        item: str,
        event: Event,
        created_at: Optional[datetime.datetime] = None,
        reward: tuple[int, int] = (0, 0),
    ) -> Optional[RewardRecord]:
        oys, usd = reward[0], round(reward[1], 2)
        self.balance.points += oys
        self.balance.usd += usd
        self.balance.total_usd += usd
        event_time = datetime.datetime.now() if created_at is None else created_at
        self.balance.updated_at = event_time
        return RewardRecord(
            user_id=self.id,
            item=item,
            created_at=event_time,
            points=oys,
            usd=usd,
            event=event.value)


class Balance(BaseTable):
    __tablename__ = 'balances'

    id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), primary_key=True)
    referrals = mapped_column(Integer, nullable=False)
    indirect_referrals = mapped_column(Integer, nullable=False)
    points = mapped_column(Integer, nullable=False)
    usd = mapped_column(DECIMAL(20, 2), nullable=False)
    total_usd = mapped_column(DECIMAL(20, 2), nullable=False)
    updated_at = mapped_column(DateTime, nullable=True)

    def get_level(self) -> int:
        if self.referrals <= 5:
            return 1
        elif self.referrals <= 15:
            return 2
        elif self.referrals <= 30:
            return 3
        elif self.referrals > 30:
            return 4
        else:
            return 0


class PromoteNft(BaseTable):
    # user uses community nfts to get a discount
    __tablename__ = 'promote_nfts'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.id"),
        primary_key=True, nullable=True)
    nft_address: Mapped[str] = mapped_column(
        String(255), index=True, nullable=False)
    campaign_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("campaigns.id"), nullable=False)
    promotion: Mapped[int] = mapped_column(
        Integer, nullable=False
    )


class ReferralCode(BaseTable):

    __tablename__ = "referral_codes"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.id"),
        primary_key=True, nullable=True)
    referral_code: Mapped[str] = mapped_column(
        String(255), index=True, nullable=False)
    max_uses = mapped_column(Integer, nullable=False)
    current_uses = mapped_column(Integer, nullable=False)


class PassCode(BaseTable):

    __tablename__ = "pass_codes"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.id"), nullable=True)
    pass_code: Mapped[str] = mapped_column(
        String(255), index=True, nullable=False)
    max_uses = mapped_column(Integer, nullable=False)
    current_uses = mapped_column(Integer, nullable=False)


class ReferralCodeUsage(BaseTable):
    __tablename__ = 'referral_code_usage'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    code_owner_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.id"), nullable=False)
    code_user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.id"), nullable=False)
    order_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("orders.id"), nullable=False
    )
    used_at: Mapped[datetime.datetime] = mapped_column(DateTime)


class PassCodeUsage(BaseTable):
    __tablename__ = 'pass_code_usages'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    code_owner_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.id"), nullable=False)
    code_user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.id"), nullable=False)
    order_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("orders.id"), nullable=False
    )
    used_at: Mapped[datetime.datetime] = mapped_column(DateTime)



class Nft(BaseTable):
    __tablename__ = "nfts"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(255), ForeignKey("orders.id"))
    user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    symbol: Mapped[str] = mapped_column(String(255), nullable=False)
    seq: Mapped[int] = mapped_column(Integer)
    token_address: Mapped[str] = mapped_column(String(255), nullable=True)
    collection_address: Mapped[str] = mapped_column(String(255), nullable=True)
    meta_url: Mapped[str] = mapped_column(String(255), nullable=True)
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    video_url: Mapped[str] = mapped_column(String(255), nullable=True)
    on_chain_image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    minted_times: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    status = mapped_column(Enum(NftStatus), nullable=False, default=NftStatus.NEW)
    minted_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)