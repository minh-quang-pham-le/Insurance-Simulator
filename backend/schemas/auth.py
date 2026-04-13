"""Auth schemas — registration, login, tokens, KYC submission."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=100)


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(...)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class KycSubmitRequest(BaseModel):
    phone_number: str = Field(..., min_length=8, max_length=20)
    full_name: str = Field(..., min_length=1, max_length=100)
    identity_number: str = Field(..., min_length=6, max_length=20)
