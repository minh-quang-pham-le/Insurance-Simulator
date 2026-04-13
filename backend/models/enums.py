"""
Enum definitions used across all models and schemas.
Maps directly to SPEC Section 6.3.
"""
import enum


class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class KycStatus(str, enum.Enum):
    NOT_SUBMITTED = "NOT_SUBMITTED"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class TransactionType(str, enum.Enum):
    TOP_UP = "TOP_UP"
    PREMIUM_PAYMENT = "PREMIUM_PAYMENT"
    PAYOUT = "PAYOUT"
    REFUND = "REFUND"


class ProductCategory(str, enum.Enum):
    FLIGHT_DELAY = "FLIGHT_DELAY"
    CROP_WEATHER = "CROP_WEATHER"
    GADGET = "GADGET"
    NATURAL_DISASTER = "NATURAL_DISASTER"
    RAINFALL_EVENT = "RAINFALL_EVENT"


class PolicyStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CLAIMED = "CLAIMED"
    CANCELLED = "CANCELLED"


class TriggerType(str, enum.Enum):
    AUTOMATIC = "AUTOMATIC"
    MANUAL = "MANUAL"


class ClaimStatus(str, enum.Enum):
    PENDING = "PENDING"
    AUTO_APPROVED = "AUTO_APPROVED"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    APPROVED = "APPROVED"
    PAID = "PAID"
    REJECTED = "REJECTED"


class NotificationType(str, enum.Enum):
    CLAIM_TRIGGERED = "CLAIM_TRIGGERED"
    PAYOUT_RECEIVED = "PAYOUT_RECEIVED"
    POLICY_EXPIRING = "POLICY_EXPIRING"
    POLICY_EXPIRED = "POLICY_EXPIRED"
    SYSTEM = "SYSTEM"
