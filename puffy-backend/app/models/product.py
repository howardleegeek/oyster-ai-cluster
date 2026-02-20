from app.models.base import BaseTable
from sqlalchemy import Boolean, ForeignKey, Integer, BigInteger, String, DateTime, Enum, DECIMAL
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from app.enums import Chain, VmType, ProductType
from decimal import Decimal 


class Product(BaseTable):

    __tablename__ = 'products'

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    # vape or fresh
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(
        String(512), nullable=False, index=True)
    # boredapeyachtclub, player2
    price: Mapped[Decimal] = mapped_column(DECIMAL(20, 2)) # cent 159.99 15999 as cent
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    product_type: Mapped[ProductType] = mapped_column(Enum(ProductType), nullable=False, default=ProductType.OTHER)
    passcode_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sm_icon_url: Mapped[str] = mapped_column(String(255), nullable=True)
    md_icon_url: Mapped[str] = mapped_column(String(255), nullable=True)
    lg_icon_url: Mapped[str] = mapped_column(String(255), nullable=True)
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    color: Mapped[str] = mapped_column(String(20), nullable=True)
    reward_points: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_referee_points: Mapped[int] = mapped_column(Integer, nullable=False)
    promote_free: Mapped[bool] = mapped_column(Boolean, nullable=True, default=None)


class Campaign(BaseTable):
    __tablename__ = 'campaigns'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(255), nullable=False)
    edition = mapped_column(String(255), nullable=False)
    requirement = mapped_column(String(255), nullable=False)
    collection_address = mapped_column(String(255), nullable=False)
    collection_name = mapped_column(String(255), nullable=False)
    chain = mapped_column(Enum(Chain), nullable=False)
    vm_type = mapped_column(Enum(VmType), nullable=False)


class TieredReward(BaseTable):
    __tablename__ = 'tiered_rewards'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    item: Mapped[str] = mapped_column(
        String(255), ForeignKey("products.id"))
    user_level: Mapped[int] = mapped_column(Integer, nullable=False)
    hierarchy_level: Mapped[int] = mapped_column(Integer, nullable=False)
    usd_pct: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)


class RestrictedArea(BaseTable):

    __tablename__ = 'restricted_areas'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    product_type: Mapped[ProductType] = mapped_column(
        Enum(ProductType), nullable=False
    )
    country_code: Mapped[str] = mapped_column(
        String(255), nullable=False
    )


class ShippingFee(BaseTable):

    __tablename__ = 'shipping_fees'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    country_code: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    product_type: Mapped[ProductType] = mapped_column(
        Enum(ProductType), nullable=False
    )
    fee: Mapped[Decimal] = mapped_column(
        DECIMAL(20, 2), nullable=False
    )

    