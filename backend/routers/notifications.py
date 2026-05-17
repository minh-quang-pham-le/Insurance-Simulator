"""Notifications Router — API endpoints for user notifications."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Any
from uuid import UUID

from config.database import get_db
from middleware.auth import get_current_user
from models.user import User
from schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    UnreadCountResponse,
)
from services import notification_service

router = APIRouter(
    tags=["Notifications"]
)


@router.get("", response_model=NotificationListResponse, status_code=status.HTTP_200_OK)
def list_notifications(
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Lấy danh sách thông báo của người dùng.
    Hỗ trợ lọc chỉ thông báo chưa đọc và phân trang.
    """
    notifications, total = notification_service.get_notifications(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
    )
    return NotificationListResponse(
        notifications=notifications,
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        page_size=limit,
    )


@router.get("/unread-count", response_model=UnreadCountResponse, status_code=status.HTTP_200_OK)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Lấy số lượng thông báo chưa đọc (hiển thị trên NotificationBell).
    """
    count = notification_service.get_unread_count(db=db, user_id=current_user.id)
    return UnreadCountResponse(count=count)


@router.post("/{notification_id}/read", response_model=NotificationResponse, status_code=status.HTTP_200_OK)
def mark_notification_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Đánh dấu một thông báo là đã đọc.
    """
    return notification_service.mark_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id,
    )


@router.post("/read-all", status_code=status.HTTP_200_OK)
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Đánh dấu tất cả thông báo là đã đọc.
    """
    count = notification_service.mark_all_as_read(
        db=db,
        user_id=current_user.id,
    )
    return {"message": f"Đã đánh dấu {count} thông báo là đã đọc", "count": count}
