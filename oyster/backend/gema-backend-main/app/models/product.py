from app.models.base import BaseTable
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing import List
from sqlalchemy import CheckConstraint


class Product(BaseTable):

    __tablename__ = 'products'
    
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(
        String(512), nullable=False, index=True)
    strategy_id = mapped_column(ForeignKey("unpack_strategies.id"))
    price = mapped_column(DECIMAL(20, 2)) # cent 159.99 15999 as cent
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    sm_icon_url: Mapped[str] = mapped_column(String(255), nullable=True)
    md_icon_url: Mapped[str] = mapped_column(String(255), nullable=True)
    lg_icon_url: Mapped[str] = mapped_column(String(255), nullable=True)
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    reward_points: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_referral_points: Mapped[int] = mapped_column(Integer, nullable=False)
    strategy: Mapped["UnpackStrategy"] = relationship()


class NftCategory(BaseTable):

    __tablename__ = "nft_categories"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(255), nullable=False)
    symbol = mapped_column(String(255), nullable=False)
    collection_id = mapped_column(String(255), nullable=True)
    merkletree_id = mapped_column(String(255), nullable=True)
    description = mapped_column(String(255), nullable=False)
    price = mapped_column(DECIMAL(20, 2)) # cent 159.99 15999 as cent
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    on_chain_image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    video_url: Mapped[str] = mapped_column(String(255), nullable=True)
    lg_icon_url: Mapped[str] = mapped_column(String(255), nullable=True)


class UnpackProbability(BaseTable):
    __tablename__ = 'unpack_probabilities'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    strategy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("unpack_strategies.id"), nullable=False)
    
    # next_strategy_id or nft_category_id should be set, but not both
    # if the next_strategy_id is set, the current step could be seen as a general node in the tree
    # if the product_id is set, the current step could be seen as a leaf node in the tree
    next_strategy_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("unpack_strategies.id"), nullable=True)
    nft_category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("nft_categories.id"), nullable=True)
    
    # probability: 1000 = 100%, the probability should be in [1, 1000]
    # the probability may not match if the total probability of the strategy is not 1000
    # for example: if probability of the productA, productB is 300 and 300, the total probability of the strategy is 600
    # so the real probability of the productA and productB should both be 300/600 = 0.5
    probability: Mapped[int] = mapped_column(Integer, nullable=False)
    nft_category: Mapped["NftCategory"] = relationship()
    # check if the next_strategy_id or product_id is set, but not both
    __table_args__ = (
        CheckConstraint(
            '(next_strategy_id IS NULL AND nft_category_id IS NOT NULL) OR '
            '(next_strategy_id IS NOT NULL AND nft_category_id IS NULL)',
            name='check_exactly_one_result'
        ),
    )

    
class UnpackStrategy(BaseTable):
    __tablename__ = 'unpack_strategies'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    probabilities: Mapped[List["UnpackProbability"]] = relationship()


class ShippingFee(BaseTable):

    __tablename__ = 'shipping_fees'

    country: Mapped[str] = mapped_column(String(255), primary_key=True)
    price = mapped_column(DECIMAL(20, 2), nullable=False)
