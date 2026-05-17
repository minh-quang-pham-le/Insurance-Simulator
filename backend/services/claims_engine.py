"""Claims Engine — Business logic for claim submission, auto-approval, and admin review."""
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Tuple, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from models.claim import Claim
from models.policy import Policy
from models.user import User
from models.enums import (
    ClaimStatus,
    PolicyStatus,
    TriggerType,
    NotificationType,
)
from services.wallet_service import WalletService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Manual claim (submitted by user)
# ---------------------------------------------------------------------------

async def submit_manual_claim(
    db: Session,
    user_id: UUID,
    policy_id: UUID,
    description: str,
    evidence_urls: list[str] | None = None,
) -> Claim:
    """
    Submit a manual claim for an active policy.

    Rules:
      - Policy must belong to the requesting user.
      - Policy must be ACTIVE.
      - One pending/review claim per policy at a time.
    """
    policy = (
        db.query(Policy)
        .filter(Policy.id == policy_id, Policy.user_id == user_id)
        .first()
    )
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found or access denied",
        )

    if policy.status != PolicyStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot file a claim on a policy with status: {policy.status}",
        )

    # Check for existing pending/review claims on this policy
    existing = (
        db.query(Claim)
        .filter(
            Claim.policy_id == policy_id,
            Claim.status.in_([ClaimStatus.PENDING, ClaimStatus.MANUAL_REVIEW]),
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A claim is already pending review for this policy",
        )

    claim = Claim(
        policy_id=policy_id,
        trigger_type=TriggerType.MANUAL,
        trigger_event=description,
        trigger_data=None,
        evidence_urls=evidence_urls,
        status=ClaimStatus.MANUAL_REVIEW,
        payout_amount=policy.payout_amount,
    )

    db.add(claim)
    db.commit()
    db.refresh(claim)

    logger.info(
        f"Manual claim {claim.id} submitted for policy {policy_id} "
        f"by user {user_id}"
    )

    # Create notification for the user
    _create_notification_sync(
        db=db,
        user_id=user_id,
        ntype=NotificationType.CLAIM_TRIGGERED,
        title="Yêu cầu bồi thường đã được gửi",
        message=f"Yêu cầu bồi thường của bạn đang chờ admin xem xét. Mức bồi thường: {policy.payout_amount} SC.",
        reference_type="claim",
        reference_id=claim.id,
    )

    return claim


# ---------------------------------------------------------------------------
# Auto claim (triggered by system / trigger monitor)
# ---------------------------------------------------------------------------

async def submit_auto_claim(
    db: Session,
    policy_id: UUID,
    trigger_event: str,
    trigger_data: dict | None = None,
) -> Claim:
    """
    Submit an automatic claim (triggered by the system).
    Auto claims are immediately approved and paid out.
    """
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )

    if policy.status != PolicyStatus.ACTIVE:
        logger.warning(
            f"Auto-claim skipped for policy {policy_id}: status={policy.status}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Policy is not ACTIVE (status: {policy.status})",
        )

    claim = Claim(
        policy_id=policy_id,
        trigger_type=TriggerType.AUTOMATIC,
        trigger_event=trigger_event,
        trigger_data=trigger_data,
        status=ClaimStatus.AUTO_APPROVED,
        payout_amount=policy.payout_amount,
        processed_at=datetime.now(timezone.utc),
    )

    db.add(claim)
    db.flush()

    # Credit wallet
    try:
        await WalletService.credit(
            user_id=policy.user_id,
            amount=Decimal(str(policy.payout_amount)),
            claim_id=claim.id,
            description=f"Auto-claim payout for policy {policy.id}",
            db=db,
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Auto-claim payout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process auto-claim payout",
        )

    # Update claim status to PAID
    claim.status = ClaimStatus.PAID

    # Update policy status to CLAIMED
    policy.status = PolicyStatus.CLAIMED

    db.commit()
    db.refresh(claim)

    logger.info(
        f"Auto-claim {claim.id} approved and paid: "
        f"{policy.payout_amount} SC to user {policy.user_id}"
    )

    # Notification
    _create_notification_sync(
        db=db,
        user_id=policy.user_id,
        ntype=NotificationType.PAYOUT_RECEIVED,
        title="Bồi thường tự động đã được chi trả!",
        message=f"Sự kiện kích hoạt đã xảy ra. Bạn nhận được {policy.payout_amount} SC vào ví.",
        reference_type="claim",
        reference_id=claim.id,
    )

    return claim


# ---------------------------------------------------------------------------
# Admin review
# ---------------------------------------------------------------------------

async def review_claim(
    db: Session,
    claim_id: UUID,
    admin_id: UUID,
    action: str,
    rejection_reason: str | None = None,
) -> Claim:
    """
    Admin approves or rejects a manual claim.

    On approve:
      1. Credit wallet with payout_amount
      2. Update claim status to PAID
      3. Update policy status to CLAIMED
      4. Send notification

    On reject:
      1. Update claim status to REJECTED
      2. Send notification
    """
    claim = (
        db.query(Claim)
        .options(joinedload(Claim.policy))
        .filter(Claim.id == claim_id)
        .first()
    )
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found",
        )

    if claim.status not in (ClaimStatus.MANUAL_REVIEW, ClaimStatus.PENDING):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Claim cannot be reviewed (current status: {claim.status})",
        )

    claim.reviewed_by = admin_id
    claim.processed_at = datetime.now(timezone.utc)
    policy = claim.policy

    if action == "approve":
        # Credit wallet
        try:
            await WalletService.credit(
                user_id=policy.user_id,
                amount=Decimal(str(claim.payout_amount)),
                claim_id=claim.id,
                description=f"Claim payout approved for policy {policy.id}",
                db=db,
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Claim payout failed during review: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process claim payout",
            )

        claim.status = ClaimStatus.PAID
        policy.status = PolicyStatus.CLAIMED
        db.commit()
        db.refresh(claim)

        logger.info(f"Claim {claim_id} APPROVED by admin {admin_id}")

        # Notify user
        _create_notification_sync(
            db=db,
            user_id=policy.user_id,
            ntype=NotificationType.PAYOUT_RECEIVED,
            title="Yêu cầu bồi thường đã được duyệt!",
            message=f"Admin đã phê duyệt yêu cầu của bạn. {claim.payout_amount} SC đã được cộng vào ví.",
            reference_type="claim",
            reference_id=claim.id,
        )

    elif action == "reject":
        claim.status = ClaimStatus.REJECTED
        db.commit()
        db.refresh(claim)

        logger.info(f"Claim {claim_id} REJECTED by admin {admin_id}")

        _create_notification_sync(
            db=db,
            user_id=policy.user_id,
            ntype=NotificationType.SYSTEM,
            title="Yêu cầu bồi thường bị từ chối",
            message=f"Yêu cầu bồi thường của bạn đã bị từ chối. Lý do: {rejection_reason or 'Không đủ bằng chứng'}.",
            reference_type="claim",
            reference_id=claim.id,
        )

    return claim


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def get_user_claims(
    db: Session,
    user_id: UUID,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list, int]:
    """Get claims for a user's policies."""
    query = (
        db.query(Claim)
        .join(Policy)
        .filter(Policy.user_id == user_id)
    )
    total = query.count()
    claims = query.order_by(Claim.created_at.desc()).offset(skip).limit(limit).all()
    return claims, total


def get_claim_by_id(
    db: Session,
    claim_id: UUID,
    user_id: UUID | None = None,
) -> Claim:
    """Get a single claim. If user_id provided, enforce ownership."""
    query = db.query(Claim).options(joinedload(Claim.policy))
    if user_id:
        query = query.join(Policy).filter(Policy.user_id == user_id)
    claim = query.filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found",
        )
    return claim


def get_all_claims(
    db: Session,
    status_filter: ClaimStatus | None = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list, int]:
    """Admin: get all claims with optional status filter."""
    query = db.query(Claim).options(joinedload(Claim.policy))
    if status_filter:
        query = query.filter(Claim.status == status_filter)
    total = query.count()
    claims = query.order_by(Claim.created_at.desc()).offset(skip).limit(limit).all()
    return claims, total


# ---------------------------------------------------------------------------
# Internal helper: sync notification creation
# ---------------------------------------------------------------------------

def _create_notification_sync(
    db: Session,
    user_id: UUID,
    ntype: NotificationType,
    title: str,
    message: str,
    reference_type: str | None = None,
    reference_id: UUID | None = None,
) -> None:
    """Create a notification record (sync, used internally by claims engine)."""
    from models.notification import Notification

    notification = Notification(
        user_id=user_id,
        type=ntype,
        title=title,
        message=message,
        is_read=False,
        reference_type=reference_type,
        reference_id=reference_id,
    )
    db.add(notification)
    db.commit()
