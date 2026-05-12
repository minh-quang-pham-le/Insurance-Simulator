"""
Policies Router — API endpoints cho hợp đồng bảo hiểm (Tính phí, Mua, Hủy, Danh sách).
"""
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Any
from uuid import UUID

# Import dependencies
from config.database import get_db
from middleware.auth import get_current_user
from models.user import User
from models.policy import Policy

# Import Schemas và Service
from schemas.policy import (
    PremiumCalculateRequest,
    PremiumCalculateResponse,
    PurchaseRequest,
    PolicyResponse,
    PolicyListResponse
)
from services import policy_service

router = APIRouter(
    prefix="/policies",
    tags=["Policies"]
)


@router.post("/calculate-premium", response_model=PremiumCalculateResponse, status_code=status.HTTP_200_OK)
def calculate_premium(
    request: PremiumCalculateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Tính toán phí bảo hiểm mô phỏng (Preview) bằng ML Risk Engine.
    Bất kỳ user nào đăng nhập cũng xem được (Không yêu cầu KYC).
    Trả về chi tiết: event_probability (%), risk_multiplier, và final_premium.
    """
    return policy_service.calculate_premium_logic(
        db=db,
        product_id=request.product_id,
        parameters=request.parameters,
        duration_days=request.duration_days
    )


@router.post("/purchase", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def purchase_policy(
    request: PurchaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Mua hợp đồng bảo hiểm.
    - Yêu cầu user phải có kyc_status = VERIFIED.
    - Trừ tiền tự động từ Ví (Wallet).
    - Logic tính toán lại phí bằng ML được chạy ngầm để bảo mật (chống fake input).
    """
    return await policy_service.purchase_policy(
        db=db,
        user_id=current_user.id,
        product_id=request.product_id,
        parameters=request.parameters,
        duration_days=request.duration_days
    )


@router.get("", response_model=PolicyListResponse, status_code=status.HTTP_200_OK)
def list_my_policies(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Lấy danh sách các hợp đồng bảo hiểm của người dùng đang đăng nhập.
    Có hỗ trợ phân trang (Pagination).
    """
    policies, total = policy_service.get_user_policies(
        db=db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit
    )
    
    return PolicyListResponse(
        policies=policies,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit
    )


@router.get("/{policy_id}", response_model=PolicyResponse, status_code=status.HTTP_200_OK)
def get_policy_detail(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Lấy thông tin chi tiết một hợp đồng cụ thể.
    """
    policy = db.query(Policy).filter(
        Policy.id == policy_id, 
        Policy.user_id == current_user.id
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found or you don't have access to it"
        )
        
    # Gắn thêm tên sản phẩm
    if policy.product:
        setattr(policy, "product_name", policy.product.name)
        
    return policy


@router.post("/{policy_id}/cancel", response_model=PolicyResponse, status_code=status.HTTP_200_OK)
async def cancel_policy(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Hủy hợp đồng bảo hiểm và hoàn tiền vào ví.
    Chỉ áp dụng cho hợp đồng đang ACTIVE và chưa hết hạn.
    """
    return await policy_service.cancel_policy(
        db=db,
        user_id=current_user.id,
        policy_id=policy_id
    )