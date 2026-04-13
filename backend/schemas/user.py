"""User schemas — profile responses."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

from models.enums import UserRole, KycStatus


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: UserRole
    phone_number: Optional[str] = None
    kyc_status: KycStatus
    kyc_submitted_at: Optional[datetime] = None
    kyc_rejection_reason: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
