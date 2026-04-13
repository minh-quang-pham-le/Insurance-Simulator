"""Policy schemas — premium calculation, purchase, listing."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from models.enums import PolicyStatus


class PremiumCalculateRequest(BaseModel):
    product_id: UUID
    parameters: Dict[str, Any]
    duration_days: int = Field(..., gt=0)


class PremiumCalculateResponse(BaseModel):
    product_id: UUID
    product_name: str
    premium: Decimal
    payout_amount: Decimal
    duration_days: int
    risk_score: float
    breakdown: Dict[str, Any]


class PurchaseRequest(BaseModel):
    product_id: UUID
    parameters: Dict[str, Any]
    duration_days: int = Field(..., gt=0)


class PolicyResponse(BaseModel):
    id: UUID
    user_id: UUID
    product_id: UUID
    premium_paid: Decimal
    payout_amount: Decimal
    status: PolicyStatus
    parameters: Dict[str, Any]
    start_date: datetime
    end_date: datetime
    created_at: datetime
    product_name: Optional[str] = None

    model_config = {"from_attributes": True}


class PolicyListResponse(BaseModel):
    policies: List[PolicyResponse]
    total: int
    page: int
    page_size: int
