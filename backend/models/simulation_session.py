"""SimulationSession model — logged simulation interactions."""
from sqlalchemy import Column, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from config.database import Base
from models.base import UUIDPrimaryKeyMixin


class SimulationSession(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "simulation_sessions"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    product_id = Column(
        UUID(as_uuid=True), ForeignKey("insurance_products.id"), nullable=False
    )
    input_parameters = Column(JSONB, nullable=False)
    triggers_activated = Column(JSONB, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    user = relationship("User", back_populates="simulation_sessions")
    product = relationship("InsuranceProduct", foreign_keys=[product_id])
