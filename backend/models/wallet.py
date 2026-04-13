"""Wallet and WalletTransaction models — virtual currency management."""
from sqlalchemy import (
    Column, String, Numeric, Enum, ForeignKey, CheckConstraint, Index, DateTime, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from config.database import Base
from models.base import UUIDPrimaryKeyMixin, TimestampMixin
from models.enums import TransactionType


class Wallet(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "wallets"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    balance = Column(Numeric(15, 2), nullable=False, default=0)
    currency = Column(String(10), nullable=False, default="SC")

    __table_args__ = (
        CheckConstraint("balance >= 0", name="ck_wallet_balance_non_negative"),
    )

    # Relationships
    user = relationship("User", back_populates="wallet")
    transactions = relationship(
        "WalletTransaction", back_populates="wallet", order_by="WalletTransaction.created_at.desc()"
    )


class WalletTransaction(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "wallet_transactions"

    wallet_id = Column(
        UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False
    )
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    balance_after = Column(Numeric(15, 2), nullable=False)
    description = Column(String(500), nullable=True)
    policy_id = Column(
        UUID(as_uuid=True), ForeignKey("policies.id"), nullable=True
    )
    claim_id = Column(
        UUID(as_uuid=True), ForeignKey("claims.id"), nullable=True
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_wallet_transactions_wallet_created", "wallet_id", created_at),
    )

    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
    policy = relationship("Policy", foreign_keys=[policy_id])
    claim = relationship("Claim", foreign_keys=[claim_id])
