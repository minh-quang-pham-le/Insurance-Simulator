"""Claims Router — API endpoints for claim submission, listing, and detail."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Any, Optional
from uuid import UUID

from config.database import get_db
from middleware.auth import get_current_user
from models.user import User
from models.enums import ClaimStatus
from schemas.claim import (
    ManualClaimRequest,
    ClaimResponse,
    ClaimListResponse,
)
from services import claims_engine

router = APIRouter(
    tags=["Claims"]
)


@router.post("", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
async def submit_claim(
    request: ManualClaimRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Gửi yêu cầu bồi thường thủ công (Manual Claim).
    - Chỉ áp dụng cho hợp đồng đang ACTIVE.
    - Mỗi hợp đồng chỉ được có 1 claim đang chờ xử lý.
    - Claim sẽ ở trạng thái MANUAL_REVIEW chờ admin duyệt.
    """
    return await claims_engine.submit_manual_claim(
        db=db,
        user_id=current_user.id,
        policy_id=request.policy_id,
        description=request.description,
        evidence_urls=request.evidence_urls,
    )


@router.get("", response_model=ClaimListResponse, status_code=status.HTTP_200_OK)
def list_my_claims(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Lấy danh sách các yêu cầu bồi thường của người dùng hiện tại.
    """
    claims, total = claims_engine.get_user_claims(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return ClaimListResponse(
        claims=claims,
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        page_size=limit,
    )


@router.get("/{claim_id}", response_model=ClaimResponse, status_code=status.HTTP_200_OK)
def get_claim_detail(
    claim_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Lấy chi tiết một yêu cầu bồi thường.
    User chỉ xem được claim thuộc policy của mình.
    """
    return claims_engine.get_claim_by_id(
        db=db,
        claim_id=claim_id,
        user_id=current_user.id,
    )
