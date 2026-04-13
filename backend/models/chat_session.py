"""ChatSession model — AI chatbot conversation history."""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from config.database import Base
from models.base import UUIDPrimaryKeyMixin, TimestampMixin


class ChatSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "chat_sessions"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    context_product_id = Column(
        UUID(as_uuid=True), ForeignKey("insurance_products.id"), nullable=True
    )
    messages = Column(JSONB, nullable=False, default=list)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    context_product = relationship("InsuranceProduct", foreign_keys=[context_product_id])
