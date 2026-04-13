"""User model — auth, profiles, roles, KYC status."""
from sqlalchemy import Column, String, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship

from config.database import Base
from models.base import UUIDPrimaryKeyMixin, TimestampMixin
from models.enums import UserRole, KycStatus


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    phone_number = Column(String(20), nullable=True)
    kyc_status = Column(
        Enum(KycStatus), nullable=False, default=KycStatus.NOT_SUBMITTED
    )
    kyc_submitted_at = Column(DateTime(timezone=True), nullable=True)
    kyc_rejection_reason = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    policies = relationship("Policy", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")
    simulation_sessions = relationship("SimulationSession", back_populates="user")
