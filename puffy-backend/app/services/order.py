from typing import Optional, List, Annotated, Tuple
from fastapi import Depends
import logging
import decimal
import uuid

from app.db import *
from app.db.cache import CacheDb
from app.db.order import OrderRepo
from app.db.product import ProductRepo
from app.db.user import User as UserRepo
import app.schemas as schemas
import app.models as models
from app.services.error import *
from app.enums import OrderStatus, ProductType


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

    def get_orders(self, limit: int = 20, offset: int = 0, **kwargs) -> List[schemas.Order]:
        orders = self.repository.get_orders(limit=limit, offset=offset, **kwargs)
        return [schemas.Order.model_validate(o) for o in orders]

    def get_order(self, **kwargs) -> Optional[schemas.Order]:
        result = self.get_orders(**kwargs)
        if result:
            return result[0]
        return None

    def _calculate_item_pricing(
        self,
        product_db,
        qty: int,
        has_promote_nfts: bool,
        pass_code: Optional[str],
        passcode_discount_available: bool
    ) -> Tuple[int, int, decimal.Decimal]:
        """
        Calculate paid_qty, free_qty, and charge_price based on discount strategies.

        Returns:
            Tuple of (paid_qty, free_qty, charge_price)

        Discount Strategies:
        1. promote_free: If user has promote_nfts and product.promote_free=True, all qty is free
        2. passcode: If valid pass_code and product.passcode_enabled=True, 1 piece is free (only ONE product)
        """
        unit_price = decimal.Decimal(product_db.price)

        # Strategy 1: promote_free discount (all qty is free)
        if has_promote_nfts and getattr(product_db, 'promote_free', False):
            logger.info(f"Applying promote_free discount for product {product_db.id}")
            return 0, qty, decimal.Decimal(0)

        # Strategy 2: passcode discount (only 1 piece is free, only for ONE product per order)
        if pass_code and passcode_discount_available:
            if getattr(product_db, 'passcode_enabled', False):
                logger.info(f"Applying passcode discount for product {product_db.id} (1 free piece)")
                if qty == 1:
                    return 0, 1, decimal.Decimal(0)
                # qty > 1: 1 free, rest paid
                paid_qty = qty - 1
                return paid_qty, 1, unit_price * paid_qty

        # No discount: all qty is paid
        return qty, 0, unit_price * qty

    def _convert_to_order_schema(self, user_id: str, order_create: schemas.OrderCreate) -> schemas.Order:
        """Convert OrderCreate to Order schema for repository."""
        # Get user data for promote_nfts check
        user_data = self.user_db.get_user(id=user_id)
        has_promote_nfts = user_data and user_data.promote_nfts if user_data else False

        # Track passcode discount (only one product can get this discount)
        passcode_discount_available = True

        # Convert OrderItemCreate to OrderItem with prices from products
        items = []
        for item_create in order_create.order_items:
            product_db = self.product_db.get_product(item_create.product_id)
            if not product_db:
                raise InvalidOrderError(f"Product not found: {item_create.product_id}")

            # Calculate pricing with discounts
            paid_qty, free_qty, charge_price = self._calculate_item_pricing(
                product_db=product_db,
                qty=item_create.qty,
                has_promote_nfts=has_promote_nfts,
                pass_code=order_create.pass_code,
                passcode_discount_available=passcode_discount_available
            )

            # Mark passcode discount as used if it was applied
            if passcode_discount_available and free_qty > 0 and order_create.pass_code:
                if getattr(product_db, 'passcode_enabled', False):
                    passcode_discount_available = False

            items.append(schemas.OrderItem(
                product_id=item_create.product_id,
                price=charge_price,
                qty=item_create.qty,
                paid_qty=paid_qty,
                free_qty=free_qty,
            ))

        # Calculate total price and shipping fee
        total_price = sum(item.price for item in items)

        # Calculate shipping fee per item based on product type
        shipping_fee = 0
        for item_create in order_create.order_items:
            product_db = self.product_db.get_product(item_create.product_id)
            if product_db:
                shipping_fee += self._calculate_shipping_fee(order_create.shipping_address, product_db.product_type)

        return schemas.Order(
            id=str(uuid.uuid4()),
            user_id=user_id,
            order_type=schemas.OrderType.NORMAL,
            price=total_price,
            currency=schemas.Currency.USD,
            shipping_fee=decimal.Decimal(str(shipping_fee)),
            total_amount=total_price + decimal.Decimal(str(shipping_fee)),
            referral_code=order_create.referral_code,
            pass_code=order_create.pass_code,
            status=schemas.OrderStatus.NEW,
            items=items,
            shipping_address=order_create.shipping_address,
        )

    def dry_run_create_order(self, user: schemas.User, order_create: schemas.OrderCreate) -> schemas.Order:
        """Calculate order without creating it."""
        logger.info("dry run create order for user %s", user.id)

        # Validate order
        if not self._validate_order_create(order_create):
            logger.info("invalid order")
            raise InvalidOrderError("Order has invalid product or shipping restriction")

        # Validate passcode if provided (for accurate pricing)
        if order_create.pass_code:
            if not self.validate_pass_code(order_create.pass_code):
                raise InvalidOrderError(f"Invalid or expired passcode: {order_create.pass_code}")

        # Get user data for promote_nfts check
        user_data = self.user_db.get_user(id=user.id)
        has_promote_nfts = user_data and user_data.promote_nfts if user_data else False

        # Track passcode discount (only one product can get this discount)
        passcode_discount_available = True

        # Check if products exist and calculate prices with discounts
        items = []
        for item_create in order_create.order_items:
            product_db = self.product_db.get_product(item_create.product_id)
            if not product_db:
                raise InvalidOrderError(f"Product not found: {item_create.product_id}")

            # Calculate pricing with discounts
            paid_qty, free_qty, charge_price = self._calculate_item_pricing(
                product_db=product_db,
                qty=item_create.qty,
                has_promote_nfts=has_promote_nfts,
                pass_code=order_create.pass_code,
                passcode_discount_available=passcode_discount_available
            )

            # Mark passcode discount as used if it was applied
            if passcode_discount_available and free_qty > 0 and order_create.pass_code:
                if getattr(product_db, 'passcode_enabled', False):
                    passcode_discount_available = False

            items.append(schemas.OrderItem(
                product_id=item_create.product_id,
                price=charge_price,
                qty=item_create.qty,
                paid_qty=paid_qty,
                free_qty=free_qty,
            ))

        total_price = sum(item.price for item in items)

        # Calculate shipping fee per item based on product type
        shipping_fee = 0
        for item_create in order_create.order_items:
            product_db = self.product_db.get_product(item_create.product_id)
            if product_db:
                shipping_fee += self._calculate_shipping_fee(order_create.shipping_address, product_db.product_type)

        return schemas.Order(
            id="dry-run",
            user_id=user.id,
            order_type=schemas.OrderType.NORMAL,
            price=total_price,
            currency=schemas.Currency.USD,
            shipping_fee=decimal.Decimal(str(shipping_fee)),
            total_amount=total_price + decimal.Decimal(str(shipping_fee)),
            status=schemas.OrderStatus.NEW,
            items=items,
            shipping_address=order_create.shipping_address,
        )

    def create_order(self, user: schemas.User, order_create: schemas.OrderCreate) -> Optional[schemas.Order]:
        """Create a new order from OrderCreate schema."""
        logger.info("create order for user %s", user.id)

        # Validate order
        if not self._validate_order_create(order_create):
            logger.info("invalid order")
            raise InvalidOrderError("Order has invalid product or shipping restriction")

        # Convert OrderCreate to Order schema
        order = self._convert_to_order_schema(user.id, order_create)

        # Validate passcode if provided
        if order_create.pass_code:
            if not self.validate_pass_code(order_create.pass_code):
                raise InvalidOrderError(f"Invalid or expired passcode: {order_create.pass_code}")

        # Validate referral code if provided
        if order_create.referral_code:
            if not self.validate_referral_code(order_create.referral_code, user.id):
                raise InvalidOrderError(f"Invalid or expired referral code: {order_create.referral_code}")

        # Create order in database
        order_db = self.repository.create_order(order)
        return schemas.Order.model_validate(order_db)

    def _validate_order_create(self, order: schemas.OrderCreate) -> bool:
        """Validate order creation request."""
        # Check if any product is VAPE type
        for item in order.order_items:
            product_db = self.product_db.get_product(item.product_id)
            if not product_db:
                logger.warning("Product not found: %s", item.product_id)
                return False

            if product_db.product_type == ProductType.VAPE:
                # If VAPE, check if shipping_address.country is in restricted areas
                if not order.shipping_address:
                    logger.warning("VAPE product requires shipping address")
                    return False

                country = order.shipping_address.country
                restricted_area = self.product_db.get_restricted_area(product_db.product_type, country)
                if restricted_area:
                    logger.warning(f"VAPE product cannot be shipped to restricted country: {country}")
                    return False

        return True

    def validate_pass_code(self, pass_code: str) -> bool:
        """Validate a passcode."""
        pass_code_obj = self.repository.get_pass_code(pass_code)
        if pass_code_obj is None:
            return False
        return pass_code_obj.current_uses < pass_code_obj.max_uses

    def validate_referral_code(self, referral_code: str, user_id: str) -> bool:
        """Validate a referral code."""
        referral_code_obj = self.repository.get_referral_code(referral_code)
        if referral_code_obj is None:
            return False
        if referral_code_obj.max_uses == -1:
            # set -1 for unlimited access
            return True
        return referral_code_obj.current_uses < referral_code_obj.max_uses

    def validate_passcode(self, passcode: str) -> bool:
        """Validate a passcode (for API endpoint)."""
        pass_code_obj = self.repository.get_pass_code(passcode)
        if pass_code_obj is None:
            return False
        return pass_code_obj.current_uses < pass_code_obj.max_uses

    def validate_referralcode(self, referral_code: str) -> Tuple[bool, Optional[str], Optional[int], Optional[int]]:
        """Validate a referral code and return its details if valid (for API endpoint)."""
        referral_code_obj = self.repository.get_referral_code(referral_code)
        if referral_code_obj is None:
            return False, None, None, None
        is_valid = referral_code_obj.max_uses == -1 or referral_code_obj.current_uses < referral_code_obj.max_uses
        return is_valid, referral_code_obj.user_id, referral_code_obj.max_uses, referral_code_obj.current_uses

    def _calculate_shipping_fee(self, shipping_address: schemas.ShippingAddress, product_type: ProductType) -> int:
        """Calculate shipping fee based on address and product type from database."""
        if not shipping_address or not shipping_address.country:
            return 40  # Default fee if no country provided

        # Try to get fee from database
        fee = self.product_db.get_shipping_fee(shipping_address.country, product_type)
        if fee is not None:
            return int(fee)

        # Default fallback fees
        if shipping_address.country in ["CN", "US"]:
            return 50
        return 40

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
        payment_create = schemas.PaymentBase(
            user_id=int(user_id),
            order_id=order_id,
            transaction_id=transaction_id,
            amount=0,
            status=schemas.PaymentStatus.PENDING
        )
        self.repository.create_payment(payment_create)

    def update_order_shipping_address(
        self,
        user_id: str,
        order_id: str,
        address: schemas.ShippingAddress):
        if not self.verify_ownership(user_id, order_id):
            logger.info("user %s is not the owner of order %s", user_id, order_id)
            raise UnauthorizedError(f"user {user_id} is not the owner of order {order_id}")
        self.repository.update_order_shipping_address(
            order_id=order_id,
            address=address)

    def update_order(self, order_id: str, user_id: str, **kwargs):
        """Update order with given fields"""
        if not self.verify_ownership(user_id, order_id):
            logger.info("user %s is not the owner of order %s", user_id, order_id)
            raise UnauthorizedError(f"user {user_id} is not the owner of order {order_id}")
        self.repository.update_order(order_id, **kwargs)

    def cancel_order(self, order_id: str, user_id: str):
        """Cancel order by setting status to CANCELLED"""
        if not self.verify_ownership(user_id, order_id):
            logger.info("user %s is not the owner of order %s", user_id, order_id)
            raise UnauthorizedError(f"user {user_id} is not the owner of order {order_id}")
        self.update_order(order_id, user_id, status=OrderStatus.CANCELLED)


def get_order_service(
    o_repo: OrderRepoDep,
    p_repo: ProductRepoDep,
    u_repo: UserRepoDep,
    cache_db: CacheDbDep
):
    return OrderService(o_repo, p_repo, u_repo, cache_db)


OrderServiceDep = Annotated[
    OrderService, Depends(get_order_service)]
