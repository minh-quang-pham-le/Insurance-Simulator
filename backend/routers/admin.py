"""Admin router — dashboard metrics, user/policy/claim management, KYC review, ML model stats."""
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from config.database import get_db
from middleware.auth import get_current_user, require_admin
from models.user import User
from models.wallet import Wallet
from models.policy import Policy
from models.claim import Claim
from models.enums import (
    KycStatus,
    PolicyStatus,
    ClaimStatus,
    UserRole,
)
from schemas.admin import (
    DashboardMetrics,
    KycReviewRequest,
    KycUserResponse,
    RiskAnalyticsResponse,
)
from schemas.user import UserResponse
from schemas.policy import PolicyResponse, PolicyListResponse
from schemas.claim import ClaimResponse, ClaimListResponse, ClaimReviewRequest
from services import claims_engine
from services.risk_engine import get_risk_engine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Admin"])


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@router.get("/dashboard")
async def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Lấy metrics tổng quan cho Admin Dashboard.
    Yêu cầu: Admin role.
    """
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)

    total_users = db.query(func.count(User.id)).filter(User.role == UserRole.USER).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(
        User.role == UserRole.USER,
        User.is_active == True,
    ).scalar() or 0
    new_registrations = db.query(func.count(User.id)).filter(
        User.created_at >= thirty_days_ago,
        User.role == UserRole.USER,
    ).scalar() or 0

    total_active_policies = db.query(func.count(Policy.id)).filter(
        Policy.status == PolicyStatus.ACTIVE,
    ).scalar() or 0
    total_premiums = db.query(func.coalesce(func.sum(Policy.premium_paid), 0)).scalar()
    total_claims_paid = db.query(func.coalesce(func.sum(Claim.payout_amount), 0)).filter(
        Claim.status == ClaimStatus.PAID,
    ).scalar()

    loss_ratio = float(total_claims_paid) / float(total_premiums) if float(total_premiums) > 0 else 0.0
    revenue = float(total_premiums) - float(total_claims_paid)

    pending_kyc = db.query(func.count(User.id)).filter(
        User.kyc_status == KycStatus.PENDING,
    ).scalar() or 0

    return {
        "total_users": total_users,
        "active_users": active_users,
        "new_registrations_30d": new_registrations,
        "total_active_policies": total_active_policies,
        "total_premiums_collected": float(total_premiums),
        "total_claims_paid": float(total_claims_paid),
        "loss_ratio": round(loss_ratio, 4),
        "revenue": round(revenue, 2),
        "pending_kyc_count": pending_kyc,
    }


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------

@router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 50,
    role: Optional[str] = None,
    kyc_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Lấy danh sách tất cả users (Admin)."""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if kyc_status:
        query = query.filter(User.kyc_status == kyc_status)

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "users": [UserResponse.model_validate(u) for u in users],
        "total": total,
        "page": (skip // limit) + 1 if limit > 0 else 1,
        "page_size": limit,
    }


# ---------------------------------------------------------------------------
# Policy management
# ---------------------------------------------------------------------------

@router.get("/policies")
async def list_all_policies(
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Lấy danh sách tất cả policies (Admin)."""
    query = db.query(Policy).options(joinedload(Policy.user), joinedload(Policy.product))
    if status_filter:
        query = query.filter(Policy.status == status_filter)

    total = query.count()
    policies = query.order_by(Policy.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for p in policies:
        data = PolicyResponse.model_validate(p).model_dump()
        data["user_email"] = p.user.email if p.user else None
        data["product_name"] = p.product.name if p.product else None
        result.append(data)

    return {
        "policies": result,
        "total": total,
        "page": (skip // limit) + 1 if limit > 0 else 1,
        "page_size": limit,
    }


# ---------------------------------------------------------------------------
# Claims management + review
# ---------------------------------------------------------------------------

@router.get("/claims")
async def list_all_claims(
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Lấy danh sách tất cả claims (Admin)."""
    claim_status = None
    if status_filter:
        try:
            claim_status = ClaimStatus(status_filter)
        except ValueError:
            pass

    claims, total = claims_engine.get_all_claims(
        db=db,
        status_filter=claim_status,
        skip=skip,
        limit=limit,
    )

    result = []
    for c in claims:
        data = ClaimResponse.model_validate(c).model_dump()
        if c.policy:
            data["user_id"] = str(c.policy.user_id)
            data["product_id"] = str(c.policy.product_id)
        result.append(data)

    return {
        "claims": result,
        "total": total,
        "page": (skip // limit) + 1 if limit > 0 else 1,
        "page_size": limit,
    }


@router.put("/claims/{claim_id}/review")
async def review_claim(
    claim_id: UUID,
    request: ClaimReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Admin duyệt hoặc từ chối yêu cầu bồi thường.
    - approve: cộng tiền vào ví user, cập nhật policy thành CLAIMED
    - reject: đánh dấu claim là REJECTED
    """
    claim = await claims_engine.review_claim(
        db=db,
        claim_id=claim_id,
        admin_id=current_user.id,
        action=request.action,
        rejection_reason=request.rejection_reason,
    )
    return ClaimResponse.model_validate(claim)


# ---------------------------------------------------------------------------
# KYC review
# ---------------------------------------------------------------------------

@router.get("/kyc/pending")
async def get_pending_kyc(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Lấy danh sách user đang chờ KYC review."""
    users = (
        db.query(User)
        .filter(User.kyc_status == KycStatus.PENDING)
        .order_by(User.kyc_submitted_at.asc())
        .all()
    )
    return {
        "users": [KycUserResponse.model_validate(u) for u in users],
        "total": len(users),
    }


@router.patch("/kyc/{user_id}")
async def review_kyc(
    user_id: UUID,
    request: KycReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Admin phê duyệt hoặc từ chối KYC.
    - approve: kyc_status → VERIFIED
    - reject: kyc_status → REJECTED + rejection_reason
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.kyc_status != KycStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User KYC status is {user.kyc_status}, not PENDING",
        )

    if request.action == "approve":
        user.kyc_status = KycStatus.VERIFIED
        user.kyc_rejection_reason = None
        logger.info(f"KYC APPROVED for user {user.email} by admin {current_user.email}")
    elif request.action == "reject":
        user.kyc_status = KycStatus.REJECTED
        user.kyc_rejection_reason = request.rejection_reason or "Không đủ thông tin"
        logger.info(f"KYC REJECTED for user {user.email} by admin {current_user.email}")

    db.commit()
    db.refresh(user)

    return UserResponse.model_validate(user)


# ---------------------------------------------------------------------------
# ML Model stats + retrain (already partially implemented, enhancing)
# ---------------------------------------------------------------------------

@router.get("/ml/model-stats")
async def get_ml_model_stats(
    current_user: User = Depends(require_admin),
):
    """Lấy thống kê ML models (accuracy, precision, recall, f1)."""
    try:
        risk_engine = get_risk_engine()
        stats = risk_engine.get_model_stats()

        return {
            "status": "success",
            "data": stats,
            "models_available": stats["models_available"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting ML model stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve model statistics",
        )


@router.post("/ml/retrain")
async def retrain_ml_models(
    current_user: User = Depends(require_admin),
):
    """Trigger ML model retraining from external data files."""
    try:
        from seed.train_models import ModelTrainer

        logger.info(f"Admin {current_user.email} triggered ML model retraining")

        data_dir = ModelTrainer.get_data_dir()
        models_dir = ModelTrainer.get_models_dir()

        flight_data_path = data_dir / "vietnam_airlines_flights.csv"
        weather_data_path = data_dir / "weather_data.csv"

        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "flight_delay": {"status": "pending"},
            "weather": {"status": "pending"},
        }

        if flight_data_path.exists():
            try:
                from services.ml_models import FlightDelayModel

                X_flight, y_flight, features_flight = ModelTrainer.prepare_flight_data(flight_data_path)
                model_flight = FlightDelayModel()
                model_flight.feature_names = features_flight
                model_flight.fit(X_flight, y_flight)
                model_flight.save(models_dir / "flight_delay.joblib")

                results["flight_delay"] = {
                    "status": "success",
                    "samples": len(X_flight),
                    "accuracy": float(model_flight.accuracy),
                }
            except Exception as e:
                results["flight_delay"] = {"status": "error", "error": str(e)}
        else:
            results["flight_delay"] = {"status": "skipped", "reason": "Data file not found"}

        if weather_data_path.exists():
            try:
                from services.ml_models import WeatherModel

                X_weather, y_weather, features_weather = ModelTrainer.prepare_weather_data(weather_data_path)
                model_weather = WeatherModel()
                model_weather.feature_names = features_weather
                model_weather.fit(X_weather, y_weather)
                model_weather.save(models_dir / "weather.joblib")

                results["weather"] = {
                    "status": "success",
                    "samples": len(X_weather),
                    "accuracy": float(model_weather.accuracy),
                }
            except Exception as e:
                results["weather"] = {"status": "error", "error": str(e)}
        else:
            results["weather"] = {"status": "skipped", "reason": "Data file not found"}

        # Reload risk engine
        try:
            from services.risk_engine import _risk_engine
            if _risk_engine is not None:
                _risk_engine._load_models()
                results["risk_engine_reloaded"] = True
        except Exception:
            results["risk_engine_reloaded"] = False

        return {"status": "success", "data": results}

    except Exception as e:
        logger.error(f"Error during ML model retraining: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retraining failed: {str(e)}",
        )
