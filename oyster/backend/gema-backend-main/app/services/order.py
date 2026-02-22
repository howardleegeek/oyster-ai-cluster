import datetime
import logging 
import decimal
from typing import List, Optional
from typing_extensions import Annotated
from fastapi import Depends

from app.db import *
from app.db.cache import CacheDb
from app.db.order import Order as OrderRepo
from app.db.product import Product as ProductRepo
from app.db.user import User as UserRepo
import app.schemas as schemas 
import app.models as models
from app.services.error import *
from app.enums import OrderStatus, OrderType


logger = logging.getLogger(__name__)


class OrderService:

    def __init__(self, 
        repo: OrderRepo, 
        product_db: ProductRepo,
        user_db: UserRepo,
        cache_db: CacheDb
    ):
        self.repository = repo
        self.product_db = product_db
        self.user_db = user_db
        self.cache_db = cache_db

    def get_orders(self, **kwargs) -> List[schemas.Order]:
        order_db = self.repository.get_orders(**kwargs)
        return [schemas.Order.model_validate(o) for o in order_db]

    def get_order(self, **kwargs) -> Optional[schemas.Order]:
        result = self.get_orders(**kwargs)
        if result:
            return result[0]
        return None 

    def create_order(self, order: schemas.Order) -> Optional[schemas.Order]:
        logger.info("create order %s", order)
        if not self.validate_order(order):
            logger.info("invalid order")
            raise InvalidOrder(f"{order} has invalid product")
        order.price = self._get_order_price(order)
        order_db = self.repository.create_order(order)
        return schemas.Order.model_validate(order_db)

    def update_order_status(self, order_id: str, status: OrderStatus) -> Optional[schemas.Order]:
        """Update order status.
        
        Args:
            order_id: The ID of the order to update
            status: The new status (OrderStatus enum)
            
        Returns:
            The updated order schema if successful, None if order not found
            
        Raises:
            RecordNotFoundError: If order with given ID doesn't exist
        """
        logger.info("Updating order %s status to %s", order_id, status.value)
        try:
            # Convert enum to string value for storage
            status_str = status.value
            updated_order_db = self.repository.update_order_status(order_id, status_str)
            return schemas.Order.model_validate(updated_order_db)
        except RecordNotFoundError:
            logger.error("Order %s not found when trying to update status", order_id)
            raise
        except Exception as e:
            logger.error("Error updating order %s status: %s", order_id, str(e))
            raise

    def validate_order(self, order: schemas.Order) -> bool:
        if order.order_type is OrderType.PRODUCT:
            return True
        if order.order_type is OrderType.SHIPPING:
            if order.shipping_address is None:
                return False
        return True

    def verify_ownership(self, user_id: str, order_id: str) -> bool:
        order = self.get_order(id=order_id)
        if order is None:
            return False
        return order.user_id == user_id

    def create_payment(self, 
        user_id: str,
        order_id: str, 
        transaction_id: str):
        if not self.verify_ownership(user_id, order_id):
            logger.info("user %s is not the owner of order %s", user_id, order_id)
            raise UnauthorizedError(f"user {user_id} is not the owner of order {order_id}")
        self.repository.create_payment(models.Payment(
            id=transaction_id,
            order_id = order_id,
            status="new",
            created_at=datetime.datetime.now(),
            success=0))

    def _get_order_price(self, order: schemas.Order) -> decimal.Decimal:
        if order.order_type is OrderType.PRODUCT:
            return self._get_item_price(order.product_id)
        elif order.order_type is OrderType.SHIPPING:
            return self._get_shipping_fee(order)
        else:
            return 0

    def _get_item_price(self, product_id: str) -> decimal.Decimal:
        return self.product_db.get_price(product_id)

    def _get_shipping_fee(self, order: schemas.Order):
        return self.product_db.get_shipping_fee(order.shipping_address.country)
    
    def update_order_shipping_address(
        self, 
        user_id: str,
        order_id: str, 
        address: schemas.ShippingAddress):
        if not self.verify_ownership(user_id, order_id):
            logger.info("user %s is not the owner of order %s", user_id, order_id)
            raise UnauthorizedError(f"user {user_id} is not the owner of order {order_id}")
        self.repository.update_order_shipping_address(
            order_id = order_id,
            address = address)


def get_order_service(
    o_repo: OrderRepoDep, 
    p_repo: ProductRepoDep, 
    u_repo: UserRepoDep,
    cache_db: CacheDbDep
):
    return OrderService(o_repo, p_repo, u_repo, cache_db)


OrderServiceDep = Annotated[
    OrderService, Depends(get_order_service)]
