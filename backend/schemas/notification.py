"""Notification schemas — user notification responses."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from models.enums import NotificationType


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    type: NotificationType
    title: str
    message: str
    is_read: bool
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]
    total: int
    page: int
    page_size: int


class UnreadCountResponse(BaseModel):
    count: int
