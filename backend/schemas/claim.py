"""Claim schemas — manual claim submission, admin review."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from models.enums import TriggerType, ClaimStatus


class ManualClaimRequest(BaseModel):
    policy_id: UUID
    description: str = Field(..., min_length=10, max_length=1000)
    evidence_urls: Optional[List[str]] = None


class ClaimReviewRequest(BaseModel):
    action: str = Field(..., pattern="^(approve|reject)$")
    rejection_reason: Optional[str] = Field(None, max_length=500)


class ClaimResponse(BaseModel):
    id: UUID
    policy_id: UUID
    trigger_type: TriggerType
    trigger_event: Optional[str] = None
    trigger_data: Optional[Dict[str, Any]] = None
    evidence_urls: Optional[List[str]] = None
    status: ClaimStatus
    payout_amount: Decimal
    reviewed_by: Optional[UUID] = None
    processed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ClaimListResponse(BaseModel):
    claims: List[ClaimResponse]
    total: int
    page: int
    page_size: int
