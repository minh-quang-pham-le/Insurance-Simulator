"""Claim model — triggered (auto or manual) insurance claims."""
from sqlalchemy import Column, String, Text, Numeric, Enum, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import func

from config.database import Base
from models.base import UUIDPrimaryKeyMixin
from models.enums import TriggerType, ClaimStatus


class Claim(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "claims"

    policy_id = Column(
        UUID(as_uuid=True), ForeignKey("policies.id"), nullable=False
    )
    trigger_type = Column(Enum(TriggerType), nullable=False)
    trigger_event = Column(String(500), nullable=True)
    trigger_data = Column(JSONB, nullable=True)
    evidence_urls = Column(JSONB, nullable=True)
    status = Column(Enum(ClaimStatus), nullable=False)
    payout_amount = Column(Numeric(15, 2), nullable=False)
    reviewed_by = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_claims_status", "status"),
    )

    # Relationships
    policy = relationship("Policy", back_populates="claims")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
