from typing import List
import decimal 

from typing_extensions import Annotated
from sqlalchemy.orm import Session, joinedload
from fastapi import Depends
from sqlalchemy import select

import app.models as models
import app.schemas as schemas 
from app.db.base import get_db


class Product:

    def __init__(self, db: Session):
        self.db = db

    def get_product(self, product_id: str) -> models.Product:
        query = select(models.Product).where(models.Product.id == product_id).options(
            joinedload(models.Product.strategy).joinedload(
                models.UnpackStrategy.probabilities
            ).joinedload(models.UnpackProbability.nft_category)
        )
        return self.db.scalars(query).unique().first()
    
    def get_price(self, product_id: str) -> decimal.Decimal:
        return self.db.get(models.Product, product_id).price

    def get_shipping_fee(self, country: str) -> decimal.Decimal:
        return self.db.get(models.ShippingFee, country).price

    def get_products(self) -> List[models.Product]:
        query = select(models.Product).options(
            joinedload(models.Product.strategy).joinedload(
                models.UnpackStrategy.probabilities
            ).joinedload(models.UnpackProbability.nft_category)
        )
        return self.db.scalars(query).unique().all()

    def create_product(self, product: schemas.Product) -> models.Product:
        db_product = models.Product(**product.dict())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def create_strategy(self, strategy: schemas.UnpackStrategyCreate) -> models.UnpackStrategy:
        db_strategy = models.UnpackStrategy(
            name=strategy.name,
            description=strategy.description,
        )
        self.db.add(db_strategy)
        self.db.commit()
        self.db.refresh(db_strategy)
        return db_strategy

    def create_probability(self, probability: schemas.UnpackProbabilityCreate) -> models.UnpackProbability:
        db_probability = models.UnpackProbability(
            strategy_id=probability.strategy_id,
            next_strategy_id=probability.next_strategy_id,
            nft_category_id=probability.nft_category_id,
            probability=probability.probability,
        )
        self.db.add(db_probability)
        self.db.commit()
        self.db.refresh(db_probability)
        return db_probability

    def get_probabilities_by_strategy(self, strategy_id: int) -> List[models.UnpackProbability]:
        """Get all probabilities for a strategy"""
        return self.db.scalars(
            select(models.UnpackProbability)
            .where(models.UnpackProbability.strategy_id == strategy_id)
        ).unique().all()

 
def get_product_repo(db: Session = Depends(get_db)):
    return Product(db)


ProductRepoDep = Annotated[Product, Depends(get_product_repo)]
