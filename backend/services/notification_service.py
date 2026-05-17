"""Notification Service — create, list, mark-read, unread count."""
import logging
from typing import Tuple, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.notification import Notification
from models.enums import NotificationType

logger = logging.getLogger(__name__)


def create_notification(
    db: Session,
    user_id: UUID,
    ntype: NotificationType,
    title: str,
    message: str,
    reference_type: str | None = None,
    reference_id: UUID | None = None,
) -> Notification:
    """Create a new notification for a user."""
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
    db.refresh(notification)

    logger.info(f"Notification created: type={ntype}, user={user_id}")
    return notification


def get_notifications(
    db: Session,
    user_id: UUID,
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
) -> Tuple[list, int]:
    """Get paginated notifications for a user (newest first)."""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)

    total = query.count()
    notifications = (
        query.order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return notifications, total


def get_unread_count(db: Session, user_id: UUID) -> int:
    """Get count of unread notifications."""
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read == False)
        .count()
    )


def mark_as_read(db: Session, notification_id: UUID, user_id: UUID) -> Notification:
    """Mark a single notification as read."""
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user_id)
        .first()
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_as_read(db: Session, user_id: UUID) -> int:
    """Mark all notifications as read for a user. Returns count updated."""
    count = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read == False)
        .update({"is_read": True})
    )
    db.commit()

    logger.info(f"Marked {count} notifications as read for user {user_id}")
    return count
