"""Trigger monitor — APScheduler background job polling external APIs and firing auto-claims."""
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy.orm import Session, joinedload

from config.database import SessionLocal
from config.settings import settings
from models.enums import PolicyStatus, ProductCategory
from models.insurance_product import InsuranceProduct
from models.policy import Policy
from services import claims_engine
from services.simulation_engine import _evaluate_condition
from utils.external_apis import AviationClient, WeatherClient, HANOI_LAT, HANOI_LON

logger = logging.getLogger(__name__)

WEATHER_CATEGORIES = {ProductCategory.CROP_WEATHER}
FLIGHT_CATEGORIES = {ProductCategory.FLIGHT_DELAY}


async def run_trigger_check() -> Dict[str, Any]:
    """
    Main job entry point — called by APScheduler every TRIGGER_CHECK_INTERVAL_MINUTES.
    Checks all ACTIVE policies against real-world API data and fires auto-claims.
    """
    db: Session = SessionLocal()
    summary = {"checked": 0, "triggered": 0, "errors": 0}

    try:
        active_policies = (
            db.query(Policy)
            .join(InsuranceProduct)
            .options(joinedload(Policy.product))
            .filter(
                Policy.status == PolicyStatus.ACTIVE,
                Policy.end_date > datetime.now(timezone.utc),
            )
            .all()
        )

        weather_policies = [p for p in active_policies if p.product.category in WEATHER_CATEGORIES]
        flight_policies = [p for p in active_policies if p.product.category in FLIGHT_CATEGORIES]

        logger.info(
            f"Trigger check started: {len(weather_policies)} weather, "
            f"{len(flight_policies)} flight policies"
        )

        for policy in weather_policies:
            try:
                triggered = await _check_weather_policy(db, policy)
                summary["checked"] += 1
                if triggered:
                    summary["triggered"] += 1
            except Exception as e:
                logger.error(f"Weather check failed for policy {policy.id}: {e}")
                summary["errors"] += 1

        for policy in flight_policies:
            try:
                triggered = await _check_flight_policy(db, policy)
                summary["checked"] += 1
                if triggered:
                    summary["triggered"] += 1
            except Exception as e:
                logger.error(f"Flight check failed for policy {policy.id}: {e}")
                summary["errors"] += 1

    finally:
        db.close()

    logger.info(f"Trigger check complete: {summary}")
    return summary


async def _check_weather_policy(db: Session, policy: Policy) -> bool:
    """Check one weather-based policy. Returns True if an auto-claim was fired."""
    product = policy.product
    params = policy.parameters or {}

    # Use policy location; fall back to Hanoi
    lat = float(params.get("location_lat", HANOI_LAT))
    lon = float(params.get("location_lon", HANOI_LON))

    weather = await WeatherClient.get_current_weather(lat, lon, settings.OPENWEATHERMAP_API_KEY)

    actual_values = {
        "rainfall_mm": weather["rainfall_mm"],
        "temp_celsius": weather["temp_celsius"],
        "alert_severity": weather["alert_severity"],
        "drought_days": 0,
    }

    result = _evaluate_weather_trigger(product, params, actual_values)
    if not result["triggered"]:
        return False

    trigger_event = (
        f"Auto-triggered: {result['description']} "
        f"tại {weather['location_name']} "
        f"(nhiệt độ={weather['temp_celsius']}°C, mưa={weather['rainfall_mm']}mm)"
    )

    try:
        await claims_engine.submit_auto_claim(
            db=db,
            policy_id=policy.id,
            trigger_event=trigger_event,
            trigger_data={"weather": weather, "triggered_rule": result},
        )
        logger.info(f"Auto-claim fired for policy {policy.id}: {trigger_event}")
        return True
    except Exception as e:
        # Policy may already be CLAIMED — not a hard error
        logger.warning(f"Auto-claim skipped for policy {policy.id}: {e}")
        return False


def _evaluate_weather_trigger(
    product: InsuranceProduct,
    policy_params: Dict,
    actual_values: Dict[str, float],
) -> Dict[str, Any]:
    """
    Evaluate product trigger_conditions against actual weather values.
    Handles both static fields and dynamic template fields ({weather_metric}).
    """
    rules = (product.trigger_conditions or {}).get("rules", [])

    for rule in rules:
        field = rule.get("field", "")
        operator = rule.get("operator", ">=")
        threshold_param = rule.get("threshold_param")
        fixed_value = rule.get("value")
        payout_multiplier = rule.get("payout_multiplier", 1.0)

        # Resolve dynamic template fields (e.g. "{weather_metric}" → "rainfall_mm")
        if "{" in field:
            field = policy_params.get(field.strip("{}"), "")
        if "{" in operator:
            operator = policy_params.get(operator.strip("{}"), ">=")

        if threshold_param:
            threshold = policy_params.get(threshold_param)
        elif fixed_value is not None:
            threshold = fixed_value
        else:
            continue

        if threshold is None or field not in actual_values:
            continue

        if _evaluate_condition(float(actual_values[field]), operator, float(threshold)):
            return {
                "triggered": True,
                "field": field,
                "actual": actual_values[field],
                "threshold": threshold,
                "operator": operator,
                "payout_multiplier": payout_multiplier,
                "description": f"{field} = {actual_values[field]} {operator} {threshold}",
            }

    return {"triggered": False}


async def _check_flight_policy(db: Session, policy: Policy) -> bool:
    """Check one flight delay policy. Returns True if an auto-claim was fired."""
    params = policy.parameters or {}
    product = policy.product
    rules = (product.trigger_conditions or {}).get("rules", [])

    airline_code = params.get("airline_code", "")
    flight_number = params.get("flight_number", "")
    flight_iata = f"{airline_code}{flight_number}".replace(" ", "")

    if not flight_iata:
        return False

    flight = await AviationClient.get_flight_status(flight_iata, settings.AVIATIONSTACK_API_KEY)

    for rule in rules:
        field = rule.get("field")
        operator = rule.get("operator", ">=")
        threshold_param = rule.get("threshold_param")
        fixed_value = rule.get("value")

        if field == "status" and operator == "==" and fixed_value == "CANCELLED":
            if flight["status"] == "CANCELLED":
                try:
                    await claims_engine.submit_auto_claim(
                        db=db,
                        policy_id=policy.id,
                        trigger_event=f"Chuyến bay {flight_iata} bị huỷ",
                        trigger_data={"flight": flight},
                    )
                    return True
                except Exception as e:
                    logger.warning(f"Flight claim skipped for {policy.id}: {e}")
                    return False

        elif field == "delay_minutes":
            threshold = params.get(threshold_param) if threshold_param else fixed_value
            if threshold and _evaluate_condition(
                float(flight["delay_minutes"]), operator, float(threshold)
            ):
                try:
                    await claims_engine.submit_auto_claim(
                        db=db,
                        policy_id=policy.id,
                        trigger_event=(
                            f"Chuyến bay {flight_iata} bị trễ "
                            f"{flight['delay_minutes']} phút (ngưỡng: {threshold} phút)"
                        ),
                        trigger_data={"flight": flight},
                    )
                    return True
                except Exception as e:
                    logger.warning(f"Flight claim skipped for {policy.id}: {e}")
                    return False

    return False
