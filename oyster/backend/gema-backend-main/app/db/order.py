import uuid
import logging 
import datetime
from typing import List, Optional
from typing_extensions import Annotated

from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import joinedload

import app.models as models
import app.schemas as schemas 
from app.db.err import *
from app.db.base import get_db
from app.enums import OrderStatus


logger = logging.getLogger(__name__)



class Order:

    def __init__(self, db: Session):
        self.db = db

    def get_orders(self, **kwargs) -> List[models.Order]:
        logger.info("get order by condition %s", kwargs)
        return self.db.scalars(
            select(models.Order)
                .options(joinedload(models.Order.shipping_address, innerjoin=False))
                .options(joinedload(models.Order.payment, innerjoin=False)) # might be no ton payment
                .options(joinedload(models.Order.shipping_track, innerjoin=False)) # might be no shipping
                .filter_by(**kwargs)
            ).unique().all()
            
    def get_order(self, **kwargs) -> Optional[models.Order]:
        result = self.get_orders(**kwargs)
        if result:
            return result[0]
        return None

    def create_order(self, order: schemas.Order) -> models.Order:
        order_db = models.Order(
                id=str(uuid.uuid4()),
                item=order.item,
                product_id=order.product_id,
                user_id=order.user_id,
                order_type=order.order_type,
                price=order.price,
                currency=order.currency,
                status=OrderStatus.NEW,
                created_at=datetime.datetime.now())
        if order.shipping_address:
            address_db = models.ShippingAddress(**order.shipping_address.dict())
            order_db.shipping_address = address_db
        self.db.add(order_db)
        self.db.commit()
        self.db.refresh(order_db)
        return order_db

    def create_payment(self, payment: models.Payment) -> models.Payment:
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_payments(self, **kwargs) -> List[models.Payment]:
        logger.info("get payments by condition %s", kwargs)
        return self.db.scalars(
            select(models.Payment).filter_by(**kwargs)
        ).all()
    
    def update_order_shipping_address(self, order_id: str, address: schemas.ShippingAddress):
        order_db = self.get_order(id=order_id)
        address_db = order_db.shipping_address
        if order_db is None:
            raise RecordNotFoundError(f"order {order_id} not found")
        for k, v in address.dict().items():
            if k == "id":
                continue
            setattr(address_db, k, v)
        self.db.commit()

    def update_order_status(self, order_id: str, status: str):
        order_db = self.get_order(id=order_id)
        if order_db is None:
            raise RecordNotFoundError(f"order {order_id} not found")
        order_db.status = status
        order_db.updated_at = datetime.datetime.now()
        self.db.commit()
        self.db.refresh(order_db)
        return order_db


def get_order_repo(db: Session = Depends(get_db)):
    return Order(db)


OrderRepoDep = Annotated[Order, Depends(get_order_repo)]
