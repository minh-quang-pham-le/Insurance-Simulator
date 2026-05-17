"""
Policy Service — Business logic for premium calculation and policy lifecycle.
"""
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, Any, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.policy import Policy
from models.insurance_product import InsuranceProduct
from models.user import User
from models.enums import KycStatus, PolicyStatus
from schemas.policy import PremiumCalculateResponse
from services.wallet_service import WalletService
from services.risk_engine import get_risk_engine

logger = logging.getLogger(__name__)

def calculate_premium_logic(
    db: Session, 
    product_id: UUID, 
    parameters: Dict[str, Any], 
    duration_days: int
) -> PremiumCalculateResponse:
    """
    Tính toán phí bảo hiểm dựa trên mô hình ML.
    Hàm này được dùng chung cho cả tính năng "Preview" và lúc "Purchase" thực tế.
    """
    product = db.query(InsuranceProduct).filter(InsuranceProduct.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance product not found"
        )
    
    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This insurance product is no longer active"
        )

    if duration_days < product.min_duration_days or duration_days > product.max_duration_days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Duration must be between {product.min_duration_days} and {product.max_duration_days} days"
        )

    # Lấy ML Engine
    engine = get_risk_engine()
    
    # Map category sang tên model (VD: FLIGHT_DELAY -> flight_delay)
    model_product_id = product.category.value.lower()
    
    # Tính base_price: Payout * (1 + risk_margin) * (duration / 30)
    # Đây là công thức cơ sở trước khi nhân với hệ số rủi ro của ML
    duration_factor = Decimal(duration_days) / Decimal(30.0)
    base_price = float(product.base_payout) * (1.0 + float(product.risk_margin)) * float(duration_factor)
    
    # Gọi ML Risk Engine
    ml_result = engine.calculate_premium(
        product_id=model_product_id,
        base_price=base_price,
        features=parameters
    )
    
    final_premium = Decimal(str(round(ml_result["final_premium"], 2)))

    return PremiumCalculateResponse(
        product_id=product.id,
        product_name=product.name,
        premium=final_premium,
        payout_amount=product.base_payout,
        duration_days=duration_days,
        risk_score=ml_result["event_probability_pct"],
        breakdown=ml_result
    )


async def purchase_policy(
    db: Session, 
    user_id: UUID, 
    product_id: UUID, 
    parameters: Dict[str, Any], 
    duration_days: int
) -> Policy:
    """
    Xử lý giao dịch mua hợp đồng bảo hiểm (Atomic Transaction).
    1. Kiểm tra KYC
    2. Tính toán lại Premium (chống fake request)
    3. Trừ tiền ví
    4. Lưu hợp đồng
    """
    # 1. Kiểm tra KYC Status
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    if user.kyc_status != KycStatus.VERIFIED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"KYC verification required to purchase policies. Current status: {user.kyc_status}"
        )

    # 2. Tính lại giá trị thực tế
    calc_result = calculate_premium_logic(db, product_id, parameters, duration_days)
    
    # Tính toán thời hạn
    start_date = datetime.now(timezone.utc)
    end_date = start_date + timedelta(days=duration_days)

    # Tạo object hợp đồng (chưa lưu vào DB để đợi trừ tiền)
    new_policy = Policy(
        user_id=user_id,
        product_id=product_id,
        premium_paid=calc_result.premium,
        payout_amount=calc_result.payout_amount,
        status=PolicyStatus.ACTIVE,
        parameters=parameters,
        start_date=start_date,
        end_date=end_date
    )
    
    db.add(new_policy)
    db.flush() # Flush để lấy new_policy.id truyền vào WalletTransaction

    # 3. Trừ tiền ví sử dụng WalletService (Async)
    try:
        await WalletService.deduct(
            user_id=user_id,
            amount=calc_result.premium,
            policy_id=new_policy.id,
            description=f"Purchase policy: {calc_result.product_name}",
            db=db
        )
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Transaction failed during policy purchase: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction failed. No funds were deducted."
        )

    # 4. Giao dịch thành công, commit thay đổi
    db.commit()
    db.refresh(new_policy)
    
    return new_policy


def get_user_policies(
    db: Session, 
    user_id: UUID, 
    skip: int = 0, 
    limit: int = 50
) -> Tuple[list, int]:
    """Lấy danh sách hợp đồng của người dùng."""
    query = db.query(Policy).filter(Policy.user_id == user_id)
    total = query.count()
    policies = query.order_by(Policy.created_at.desc()).offset(skip).limit(limit).all()
    
    # Kèm thêm tên sản phẩm để Frontend dễ hiển thị
    for policy in policies:
        if policy.product:
            setattr(policy, "product_name", policy.product.name)
            
    return policies, total


async def cancel_policy(db: Session, user_id: UUID, policy_id: UUID) -> Policy:
    """
    Hủy hợp đồng bảo hiểm và hoàn tiền (Refund).
    Chỉ cho phép hủy nếu hợp đồng đang ACTIVE và chưa kết thúc.
    """
    policy = db.query(Policy).filter(Policy.id == policy_id, Policy.user_id == user_id).first()
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
        
    if policy.status != PolicyStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel policy with status: {policy.status}"
        )
        
    now = datetime.now(timezone.utc)
    # Normalize cả hai về offset-naive hoặc offset-aware để so sánh
    policy_end = policy.end_date if policy.end_date.tzinfo else policy.end_date.replace(tzinfo=timezone.utc)
    
    if now >= policy_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel an expired policy"
        )

    # Tính toán số tiền hoàn lại (Refund). Phase 1: Hoàn 80% nếu hủy
    refund_amount = Decimal(str(round(float(policy.premium_paid) * 0.8, 2)))

    try:
        # Cộng tiền lại vào ví (Async)
        await WalletService.credit(
            user_id=user_id,
            amount=refund_amount,
            description=f"Refund for cancelled policy {policy.id}",
            db=db
        )
        
        # Cập nhật trạng thái hợp đồng
        policy.status = PolicyStatus.CANCELLED
        db.commit()
        db.refresh(policy)
    except Exception as e:
        db.rollback()
        logger.error(f"Refund failed during policy cancellation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process refund."
        )

    return policy