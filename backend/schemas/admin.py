"""Admin schemas — dashboard metrics, KYC review, analytics."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID


class DashboardMetrics(BaseModel):
    total_users: int = 0
    active_users: int = 0
    new_registrations_30d: int = 0
    total_active_policies: int = 0
    total_premiums_collected: float = 0.0
    total_claims_paid: float = 0.0
    loss_ratio: float = 0.0
    revenue: float = 0.0
    pending_kyc_count: int = 0


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


class CategoryRiskStats(BaseModel):
    category: str
    total_events: int = 0
    avg_severity: Optional[float] = None
    event_probability: float = 0.0
    total_policies: int = 0
    total_premiums: float = 0.0
    total_payouts: float = 0.0
    loss_ratio: float = 0.0


class MonthlyTrend(BaseModel):
    month: str
    premiums: float = 0.0
    payouts: float = 0.0
    policies_sold: int = 0
    claims_count: int = 0


class RegionRiskData(BaseModel):
    region: str
    event_count: int = 0
    avg_severity: Optional[float] = None


class RiskAnalyticsResponse(BaseModel):
    total_policies: int = 0
    total_premiums: float = 0.0
    total_payouts: float = 0.0
    overall_loss_ratio: float = 0.0
    category_stats: List[CategoryRiskStats] = []
    monthly_trends: List[MonthlyTrend] = []
    region_stats: List[RegionRiskData] = []
