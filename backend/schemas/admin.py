"""Admin schemas — dashboard metrics, KYC review, analytics."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID


class DashboardMetrics(BaseModel):
    total_users: int
    active_users: int
    new_registrations_30d: int
    total_active_policies: int
    total_premiums_collected: Decimal
    total_claims_paid: Decimal
    loss_ratio: float
    revenue: Decimal
    pending_kyc_count: int


class KycReviewRequest(BaseModel):
    action: str = Field(..., pattern="^(approve|reject)$")
    rejection_reason: Optional[str] = Field(None, max_length=500)


class KycUserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    phone_number: Optional[str] = None
    kyc_submitted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RiskAnalyticsResponse(BaseModel):
    category: str
    total_events: int
    event_probability: float
    avg_severity: Optional[float] = None
    by_region: List[Dict[str, Any]]
    by_season: List[Dict[str, Any]]
    loss_ratio: float
