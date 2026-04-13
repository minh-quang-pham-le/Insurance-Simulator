"""RiskData model — historical event data for probability calculations."""
from sqlalchemy import Column, String, Date, Numeric, Enum, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import func

from config.database import Base
from models.base import UUIDPrimaryKeyMixin
from models.enums import ProductCategory


class RiskData(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "risk_data"

    product_category = Column(Enum(ProductCategory), nullable=False)
    region = Column(String(100), nullable=True)
    event_date = Column(Date, nullable=False)
    event_type = Column(String(100), nullable=False)
    event_severity = Column(Numeric(10, 2), nullable=True)
    event_data = Column(JSONB, nullable=True)
    source = Column(String(100), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_risk_data_category_region_date", "product_category", "region", "event_date"),
        Index("ix_risk_data_category_date", "product_category", "event_date"),
    )
