"""InsuranceProduct model — product catalog with JSON parameter schemas."""
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Numeric, Enum, ForeignKey, Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from config.database import Base
from models.base import UUIDPrimaryKeyMixin, TimestampMixin
from models.enums import ProductCategory


class InsuranceProduct(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "insurance_products"

    name = Column(String(200), nullable=False)
    category = Column(Enum(ProductCategory), nullable=False)
    description = Column(Text, nullable=False)
    short_description = Column(String(300), nullable=True)
    icon_url = Column(String(500), nullable=True)
    base_payout = Column(Numeric(15, 2), nullable=False)
    min_duration_days = Column(Integer, nullable=False)
    max_duration_days = Column(Integer, nullable=False)
    risk_margin = Column(Numeric(5, 4), nullable=False, default=0.25)
    parameters_schema = Column(JSONB, nullable=False)
    trigger_conditions = Column(JSONB, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    __table_args__ = (
        Index("ix_insurance_products_category_active", "category", "is_active"),
    )

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    policies = relationship("Policy", back_populates="product")
