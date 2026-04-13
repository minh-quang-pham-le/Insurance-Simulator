"""ApiMonitorLog model — external API health tracking."""
from sqlalchemy import Column, String, Text, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import func

from config.database import Base
from models.base import UUIDPrimaryKeyMixin


class ApiMonitorLog(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "api_monitor_logs"

    api_name = Column(String(50), nullable=False)
    endpoint = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False, default="GET")
    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    response_summary = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    checked_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_api_monitor_logs_name_checked", "api_name", "checked_at"),
    )
