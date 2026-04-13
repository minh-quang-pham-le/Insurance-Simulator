"""Policy model — purchased insurance instances."""
from sqlalchemy import Column, Numeric, Enum, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from config.database import Base
from models.base import UUIDPrimaryKeyMixin, TimestampMixin
from models.enums import PolicyStatus


class Policy(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "policies"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    product_id = Column(
        UUID(as_uuid=True), ForeignKey("insurance_products.id"), nullable=False
    )
    premium_paid = Column(Numeric(15, 2), nullable=False)
    payout_amount = Column(Numeric(15, 2), nullable=False)
    status = Column(Enum(PolicyStatus), nullable=False, default=PolicyStatus.ACTIVE)
    parameters = Column(JSONB, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("ix_policies_user_status", "user_id", "status"),
        Index("ix_policies_status_end_date", "status", "end_date"),
        Index("ix_policies_product_id", "product_id"),
    )

    # Relationships
    user = relationship("User", back_populates="policies")
    product = relationship("InsuranceProduct", back_populates="policies")
    claims = relationship("Claim", back_populates="policy")
