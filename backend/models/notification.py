"""Notification model — user notifications for claims, payouts, expiry."""
from sqlalchemy import Column, String, Text, Boolean, Enum, ForeignKey, DateTime, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from config.database import Base
from models.base import UUIDPrimaryKeyMixin
from models.enums import NotificationType


class Notification(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "notifications"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    reference_type = Column(String(20), nullable=True)
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_notifications_user_read_created", "user_id", "is_read", "created_at"),
    )

    # Relationships
    user = relationship("User", back_populates="notifications")
