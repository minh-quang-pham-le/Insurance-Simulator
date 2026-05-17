"""Auth schemas — registration, login, tokens, KYC submission."""
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional
from uuid import UUID

from models.enums import UserRole, KycStatus


class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=100)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Password must contain uppercase, digit, and special character."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str


class KycSubmitRequest(BaseModel):
    """KYC submission request."""
    phone_number: str = Field(..., min_length=10, max_length=20)
    identity_details: Optional[str] = Field(None, max_length=500)
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Phone number should start with + or be numeric."""
        if not (v.startswith("+") or v.isdigit()):
            raise ValueError("Phone number must start with + or contain only digits")
        return v


class UserResponse(BaseModel):
    """User profile response."""
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
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class KycStatusResponse(BaseModel):
    """KYC status response."""
    kyc_status: KycStatus


class KycSubmitResponse(BaseModel):
    """KYC submission response."""
    kyc_status: KycStatus
    message: str
