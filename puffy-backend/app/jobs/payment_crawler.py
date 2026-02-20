import logging
import time
from typing import Annotated, Optional
import app.schemas as schemas
import app.models as models
from app.db import OrderRepoDep, PaymentRepoDep
from app.services.error import ServerError
from fastapi import Depends
import datetime

logger = logging.getLogger(__name__)


class PaymentCrawler:
    """Crawls online payments and confirms orders"""

    def __init__(self, order_repo: OrderRepoDep, payment_repo: PaymentRepoDep):
        self.order_repo = order_repo
        self.payment_repo = payment_repo

    def crawl_payments(self) -> list:
        """
        Crawls online payments and returns payment records
        Pseudocode implementation:
        - Connect to payment gateway API
        - Fetch pending payments
        - Filter by status 'pending' or 'processing'
        - Return list of payment objects
        """
        # Pseudocode: Connect to payment gateway
        # payments = payment_gateway.get_pending_payments()
        # payments = [p for p in payments if p.status in ['pending', 'processing']]

        # Mock data for demonstration
        mock_payments = []

        for payment in mock_payments:
            logger.info(f"Processing payment: {payment.id}")
            self._confirm_order(payment)

        return mock_payments

    def _confirm_order(self, payment: models.Payment):
        """Confirm order if payment order_id matches"""
        if not payment.order_id:
            logger.warning(f"Payment {payment.id} has no order_id")
            return

        order = self.order_repo.get_order(id=payment.order_id)

        if order is None:
            logger.warning(f"Order {payment.order_id} not found for payment {payment.id}")
            return

        logger.info(f"Confirming order {order.id} with payment {payment.id}")

        # Update order status
        order.status = "confirmed"
        order.confirmed_at = datetime.datetime.now()

        # Update payment status
        payment.status = "completed"
        payment.transferred_at = datetime.datetime.now()
        payment.success = True

        # Commit changes
        try:
            self.order_repo.db.commit()
            self.payment_repo.db.commit()
            logger.info(f"Successfully confirmed order {order.id}")
        except Exception as err:
            logger.error(f"Failed to confirm order {order.id}: {err}")
            self.order_repo.db.rollback()


def get_payment_crawler(order_repo: OrderRepoDep, payment_repo: PaymentRepoDep) -> PaymentCrawler:
    return PaymentCrawler(order_repo, payment_repo)


PaymentCrawlerDep = Annotated[PaymentCrawler, Depends(get_payment_crawler)]
