from enum import Enum


class OrderStatus(str, Enum):
    """Order status enumeration"""
    NEW = "new"
    PAID = "paid"
    CONFIRMED = "confirmed"
    EXPIRED = "expired"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"


class ShippingStatus(str, Enum):
    """Shipping status enumeration"""
    NEW = "new"
    RENEW = "renew"
    REQUESTED = "requested"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    DENIED = "denied"
    USER_REJECTED = "user_rejected"
    PROCESSING = "processing"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"


class PaymentStatus(str, Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Currency(str, Enum):
    """Currency enumeration"""
    USDT = "USDT"
    TON = "TON"
    USD = "USD"
    USDC = "USDC"
    SOL = "SOL"


class OrderType(str, Enum):
    """Order type enumeration"""
    NORMAL = "normal"
    NFT = "nft"
    REFERRED = "referred"


class PaymentType(str, Enum):
    """Payment type enumeration"""
    CURRENCY = "currency"
    PASSCODE = "passcode"
    NFT_ELIGIBLE = "nft_eligible"


class ProductType(str, Enum):
    """Product type enumeration"""
    VAPE = "vape"
    FRESH = "fresh"
    OTHER = "other"


# Countries where vape products are eligible for sale
# (matching frontend puffyRules.ts)
VAPE_ELIGIBLE_COUNTRIES = {"US", "CA", "GB", "DE", "FR", "AU", "JP"}


# Additional enums that might be useful
class ShippingCarrier(str, Enum):
    """Shipping carrier enumeration"""
    UPS = "ups"
    FEDEX = "fedex"
    DHL = "dhl"
    USPS = "usps"
    OTHER = "other"


class Chain(str, Enum):
    TON = "ton"
    SOL = "sol"
    ETH = "eth"
    SOON = "soon"
    BERACHAIN = "berachain"


class VmType(str, Enum):
    SVM = "svm"
    EVM = "evm"
    TVM = "tvm"


class Event(str, Enum):

    REFEREE = "referee"
    REFERRAL = "referral"
    INDIRECT_REFERRAL = "indirect_referral"
    PURCHASE = "purchase"
    PROMOTE_REFERRAL = "promote_referral"
    PROMOTE_REFEREE = "promote_referee"
    TWITTER_AUTH = "twitter_auth"
    TWITTER_FOLLOW_PUFFY = "twitter_follow_puffy"
    TWITTER_FOLLOW_SOON = "twitter_follow_soon"
    TWITTER_RETWEET = "twitter_retweet"
    TG_AUTH = "tg_auth"
    TG_JOIN_GROUP = "tg_join_group"
    DISCORD_JOIN_PUFFY = "discord_join_puffy"
    DISCORD_JOIN_SOON = "discord_join_soon"


class NftStatus(str, Enum):
    NEW = "new"
    MINTED = "minted"
    MINT_FAILED = "mint_failed"