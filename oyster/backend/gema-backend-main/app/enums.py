from enum import Enum 


class NftStatus(str, Enum):
    """NFT status enum"""
    SOLD = "sold"
    UNSOLD = "unsold"
    REDEEMED = "redeemed"
    BURNED = "burned"


class OrderStatus(str, Enum):
    """Order status enum"""
    NEW = "new"
    PAID = "paid"
    CONFIRMED = "confirmed"
    EXPIRED = "expired"
    REFUNDED = "refunded"
    SHIPPED = "shipped"


class OrderType(str, Enum):
    """Order type enum"""
    PRODUCT = "product"
    SHIPPING = "shipping"


class ShippingStatus(str, Enum):
    """Shipping status enum"""
    NEW = "new"
    RENEW = "renew"
    REQUESTED = "requested"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    DENIED = "denied"
    USER_REJECTED = "user_rejected"


class Currency(str, Enum):
    """Currency enum"""
    USDT = "USDT"
    TON = "TON"
    USD = "USD"
    USDC = "USDC"


class Event(str, Enum):
    """Event types for reward records"""
    REFEREE = "referee"
    REFERRAL = "referral"
    PURCHASE = "purchase"
    TWITTER_AUTH = "twitter_auth"


class PaymentStatus(str, Enum):
    """Payment status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
