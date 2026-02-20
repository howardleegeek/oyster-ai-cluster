from app.enums import OrderStatus

VALID_TRANSITIONS = {
    OrderStatus.NEW: {OrderStatus.PAID, OrderStatus.CANCELLED, OrderStatus.EXPIRED},
    OrderStatus.PAID: {OrderStatus.CONFIRMED, OrderStatus.EXPIRED, OrderStatus.REFUNDED},
    OrderStatus.CONFIRMED: {OrderStatus.PROCESSING, OrderStatus.REFUNDED},
    OrderStatus.PROCESSING: {OrderStatus.SHIPPED},
    OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
    OrderStatus.CANCELLED: set(),
    OrderStatus.DELIVERED: set(),
    OrderStatus.EXPIRED: set(),
    OrderStatus.REFUNDED: set(),
}


def validate_order_transition(current: OrderStatus, target: OrderStatus) -> bool:
    """Return True if transition from current to target is valid."""
    allowed = VALID_TRANSITIONS.get(current, set())
    return target in allowed
