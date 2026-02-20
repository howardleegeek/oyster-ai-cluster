from typing import List, Optional, Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from fastapi import Depends

from app.models.order import Order as OrderModel, Payment, ShippingAddress, OrderItem
from app.models.user import PassCode, ReferralCode
from app.schemas.order import Order as OrderSchema, ShippingAddress as ShippingAddressSchema
from app.db.err import RecordNotFoundError
from app.db.base import get_db
from sqlalchemy.orm import joinedload
from app.enums import PaymentStatus
import logging
from datetime import datetime


logger = logging.getLogger(__name__)


class OrderRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_order(self, **kwargs) -> Optional[OrderModel]:
        logger.info("get order by condition %s", kwargs)
        orders = self.get_orders(**kwargs)
        if orders:
            return orders[0]
        return None


    def get_orders(self, limit: int = 20, offset: int = 0, **kwargs) -> List[OrderModel]:
        logger.info("get orders by condition %s limit=%d offset=%d", kwargs, limit, offset)
        limit = min(limit, 100)
        return (
            self.db.query(OrderModel)
            .options(
                joinedload(OrderModel.items),
                joinedload(OrderModel.shipping_address),
                joinedload(OrderModel.payment),
            )
            .filter_by(**kwargs)
            .order_by(desc(OrderModel.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )


    def create_order(self, order: OrderSchema) -> OrderModel:
        db_order = OrderModel(
            id=order.id,
            user_id=order.user_id,
            order_type=order.order_type if order.order_type else "normal",
            price=order.price if order.price else 0,
            currency=order.currency if order.currency else "USD",
            shipping_fee=order.shipping_fee if order.shipping_fee else 0,
            total_amount=order.total_amount if order.total_amount else 0,
            referral_code=order.referral_code,
            pass_code=order.pass_code,
            status=order.status if order.status else "new",
            payment_type=order.payment_type,
            addr_locked=order.addr_locked if order.addr_locked else False,
            created_at=datetime.now()
        )
        self.db.add(db_order)
        self.db.commit()
        self.db.refresh(db_order)

        # Increment passcode usage if provided
        if order.pass_code:
            passcode_db = self.db.query(PassCode).filter(PassCode.pass_code == order.pass_code).first()
            if passcode_db:
                passcode_db.current_uses = passcode_db.current_uses + 1
                self.db.commit()

        # Create order items
        if order.items:
            for item in order.items:
                order_item = OrderItem(
                    order_id=db_order.id,
                    product_id=item.product_id,
                    price=item.price,
                    qty=item.qty,
                    paid_qty=item.paid_qty,
                    free_qty=item.free_qty
                )
                self.db.add(order_item)

        # Create shipping address
        if order.shipping_address:
            shipping_addr = ShippingAddress(
                id=db_order.id,
                name=order.shipping_address.name,
                email=order.shipping_address.email,
                phone_number=order.shipping_address.phone_number,
                address_line_1=order.shipping_address.address_line_1,
                address_line_2=order.shipping_address.address_line_2,
                city=order.shipping_address.city,
                state=order.shipping_address.state,
                country=order.shipping_address.country,
                postal_code=order.shipping_address.postal_code,
                pccc=order.shipping_address.pccc
            )
            self.db.add(shipping_addr)

        self.db.commit()
        self.db.refresh(db_order)

        # Eager load relationships before returning
        db_order = self.db.query(OrderModel).options(
            joinedload(OrderModel.items),
            joinedload(OrderModel.shipping_address),
            joinedload(OrderModel.payment)
        ).filter(OrderModel.id == db_order.id).first()

        return db_order

    def update_order(self, order_id: str, **kwargs) -> OrderModel:
        order = self.get_order(id=order_id)
        if not order:
            raise RecordNotFoundError(f"Order with id {order_id} does not exist")

        # Validate order status transition before applying changes
        if "status" in kwargs:
            from app.services.state_machine import validate_order_transition
            new_status = kwargs["status"]
            if not validate_order_transition(order.status, new_status):
                raise RecordNotFoundError(
                    f"Invalid order transition from {order.status} to {new_status}"
                )

        for key, value in kwargs.items():
            if hasattr(order, key):
                setattr(order, key, value)

        self.db.commit()
        self.db.refresh(order)
        return order

    def update_order_shipping_address(self, order_id: str, address: ShippingAddressSchema) -> OrderModel:
        order = self.get_order(id=order_id)
        if not order:
            raise RecordNotFoundError(f"Order with id {order_id} does not exist")

        # Update existing shipping address or create new one
        shipping_addr = self.db.query(ShippingAddress)\
            .filter(ShippingAddress.id == order_id)\
            .first()

        if shipping_addr:
            shipping_addr.name = address.name
            shipping_addr.email = address.email
            shipping_addr.phone_number = address.phone_number
            shipping_addr.address_line_1 = address.address_line_1
            shipping_addr.address_line_2 = address.address_line_2
            shipping_addr.city = address.city
            shipping_addr.state = address.state
            shipping_addr.country = address.country
            shipping_addr.postal_code = address.postal_code
            shipping_addr.pccc = address.pccc
        else:
            shipping_addr = ShippingAddress(
                id=order_id,
                name=address.name,
                email=address.email,
                phone_number=address.phone_number,
                address_line_1=address.address_line_1,
                address_line_2=address.address_line_2,
                city=address.city,
                state=address.state,
                country=address.country,
                postal_code=address.postal_code,
                pccc=address.pccc
            )
            self.db.add(shipping_addr)

        self.db.commit()
        self.db.refresh(order)
        return order

    def create_payment(self, payment: Payment) -> Payment:
        db_payment = Payment(
            user_id=payment.user_id,
            order_id=payment.order_id,
            transaction_id=payment.transaction_id,
            amount=payment.amount,
            status=payment.status
        )
        self.db.add(db_payment)
        self.db.commit()
        self.db.refresh(db_payment)
        return db_payment

    def update_payment_status(self, payment_id: str, status: PaymentStatus) -> Payment:
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise RecordNotFoundError(f"Payment with id {payment_id} does not exist")
        payment.status = status
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_payment_by_transaction(self, transaction_id: str) -> Payment:
        payment = self.db.query(Payment)\
            .filter(Payment.transaction_id == transaction_id)\
            .first()
        if not payment:
            raise RecordNotFoundError(
                f"Payment with transaction id {transaction_id} does not exist"
            )
        return payment

    def get_pass_code(self, pass_code: str):
        return self.db.query(PassCode).filter(PassCode.pass_code == pass_code).first()

    def get_referral_code(self, referral_code: str):
        return self.db.query(ReferralCode).filter(ReferralCode.referral_code == referral_code).first()


def get_order_repo(db: Session = Depends(get_db)):
    return OrderRepo(db)


OrderRepoDep = Annotated[OrderRepo, Depends(get_order_repo)]
