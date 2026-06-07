"""API Monitor router — external API health status, trigger logs, and manual check."""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from config.database import get_db
from config.settings import settings
from middleware.auth import require_admin
from models.api_monitor_log import ApiMonitorLog
from models.user import User
from services.trigger_monitor import run_trigger_check
from utils.external_apis import WeatherClient

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Monitor"])


@router.get("/weather/hanoi")
async def get_hanoi_weather(current_user: User = Depends(require_admin)):
    """Fetch current Hanoi weather from OpenWeatherMap."""
    if not settings.OPENWEATHERMAP_API_KEY:
        return {
            "error": "OPENWEATHERMAP_API_KEY chưa được cấu hình",
            "is_mock": True,
            "temp_celsius": 28.5,
            "rainfall_mm": 0.0,
            "alert_severity": 0,
            "description": "mock data",
            "location_name": "Hà Nội (mock)",
        }
    return await WeatherClient.get_hanoi_weather(settings.OPENWEATHERMAP_API_KEY)


@router.get("/status")
async def get_api_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Return health status of each external API based on most recent log entry.
    Also returns configuration status.
    """
    result = {}
    for api_name in ["openweathermap", "aviationstack"]:
        recent = (
            db.query(ApiMonitorLog)
            .filter(ApiMonitorLog.api_name == api_name)
            .order_by(desc(ApiMonitorLog.checked_at))
            .first()
        )
        if not recent:
            result[api_name] = {"status": "unknown", "last_checked": None}
        elif recent.error_message:
            result[api_name] = {
                "status": "error",
                "last_checked": recent.checked_at,
                "error": recent.error_message[:120],
                "response_time_ms": recent.response_time_ms,
            }
        else:
            result[api_name] = {
                "status": "ok",
                "last_checked": recent.checked_at,
                "response_time_ms": recent.response_time_ms,
                "status_code": recent.status_code,
            }

    result["config"] = {
        "openweathermap_configured": bool(settings.OPENWEATHERMAP_API_KEY),
        "aviationstack_configured": bool(settings.AVIATIONSTACK_API_KEY),
        "trigger_interval_minutes": settings.TRIGGER_CHECK_INTERVAL_MINUTES,
    }
    return result


@router.get("/logs")
async def get_monitor_logs(
    api_name: Optional[str] = Query(None, description="Filter by API name"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Return recent API monitor log entries."""
    query = db.query(ApiMonitorLog)
    if api_name:
        query = query.filter(ApiMonitorLog.api_name == api_name)
    logs = query.order_by(desc(ApiMonitorLog.checked_at)).limit(limit).all()
    return [
        {
            "id": str(log.id),
            "api_name": log.api_name,
            "endpoint": log.endpoint,
            "status_code": log.status_code,
            "response_time_ms": log.response_time_ms,
            "response_summary": log.response_summary,
            "error_message": log.error_message,
            "checked_at": log.checked_at,
        }
        for log in logs
    ]


@router.post("/run-check")
async def manual_trigger_check(current_user: User = Depends(require_admin)):
    """Manually run the trigger check job (admin only)."""
    try:
        summary = await run_trigger_check()
        return {"success": True, "summary": summary}
    except Exception as e:
        logger.error(f"Manual trigger check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
