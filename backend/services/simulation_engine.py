"""Simulation engine — trigger explorer logic for interactive demonstrations."""
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.insurance_product import InsuranceProduct
from models.simulation_session import SimulationSession

logger = logging.getLogger(__name__)

# Default slider ranges for known trigger fields
SLIDER_DEFAULTS = {
    "delay_minutes": {
        "label": "Flight Delay (minutes)",
        "min_value": 0,
        "max_value": 360,
        "step": 10,
        "default_value": 0,
        "unit": "min",
    },
    "rainfall_mm": {
        "label": "Rainfall (mm)",
        "min_value": 0,
        "max_value": 200,
        "step": 1,
        "default_value": 0,
        "unit": "mm",
    },
    "temp_celsius": {
        "label": "Temperature (°C)",
        "min_value": 0,
        "max_value": 50,
        "step": 0.5,
        "default_value": 25,
        "unit": "°C",
    },
    "drought_days": {
        "label": "Drought Duration (days)",
        "min_value": 0,
        "max_value": 60,
        "step": 1,
        "default_value": 0,
        "unit": "days",
    },
    "alert_severity": {
        "label": "Alert Severity Level",
        "min_value": 1,
        "max_value": 5,
        "step": 1,
        "default_value": 1,
        "unit": "level",
    },
    "status": {
        "label": "Flight Status",
        "min_value": 0,
        "max_value": 1,
        "step": 1,
        "default_value": 0,
        "unit": "status",
    },
}


def get_simulation_config(product: InsuranceProduct) -> Dict:
    """
    Generate slider configuration and trigger rules for the simulation UI.

    Reads the product's trigger_conditions and parameters_schema to produce
    slider configs with thresholds for the Trigger Explorer.
    """
    trigger_conditions = product.trigger_conditions or {}
    parameters_schema = product.parameters_schema or {}
    rules = trigger_conditions.get("rules", [])
    trigger_type = trigger_conditions.get("type", "MANUAL")

    if trigger_type == "MANUAL":
        return {
            "product_id": str(product.id),
            "product_name": product.name,
            "sliders": [],
            "trigger_rules": [],
            "base_payout": float(product.base_payout),
            "is_manual": True,
            "manual_info": {
                "requires": trigger_conditions.get("requires", []),
                "review": trigger_conditions.get("review", "ADMIN"),
                "description": (
                    "This product uses manual claims. Submit evidence "
                    "and a description for admin review."
                ),
            },
        }

    # Extract default parameter values from the product's parameters_schema
    param_defaults = {}
    for field in parameters_schema.get("fields", []):
        if "default" in field:
            param_defaults[field["name"]] = field["default"]
        if "min" in field:
            param_defaults[f"_min_{field['name']}"] = field["min"]
        if "max" in field:
            param_defaults[f"_max_{field['name']}"] = field["max"]

    sliders = []
    trigger_rules = []
    seen_fields = set()

    for rule in rules:
        raw_field = rule.get("field", "")
        operator = rule.get("operator", ">=")
        threshold_param = rule.get("threshold_param")
        fixed_value = rule.get("value")
        payout_multiplier = rule.get("payout_multiplier", 1.0)

        # Resolve dynamic field names like {weather_metric}
        field_name = raw_field.strip("{}")

        # Determine threshold value
        threshold = None
        if threshold_param and threshold_param in param_defaults:
            threshold = param_defaults[threshold_param]
        elif fixed_value is not None:
            threshold = fixed_value

        # Build slider config (one slider per unique field)
        if field_name not in seen_fields and field_name != "status":
            seen_fields.add(field_name)
            defaults = SLIDER_DEFAULTS.get(field_name, {})

            slider = {
                "name": field_name,
                "label": defaults.get("label", field_name.replace("_", " ").title()),
                "min_value": defaults.get("min_value", 0),
                "max_value": defaults.get("max_value", 100),
                "step": defaults.get("step", 1),
                "default_value": defaults.get("default_value", 0),
                "threshold": threshold,
                "unit": defaults.get("unit", ""),
            }

            # Override slider range from schema if available
            if threshold_param:
                schema_min = param_defaults.get(f"_min_{threshold_param}")
                schema_max = param_defaults.get(f"_max_{threshold_param}")
                if schema_min is not None:
                    slider["min_value"] = schema_min
                if schema_max is not None:
                    slider["max_value"] = schema_max

            sliders.append(slider)

        # Build trigger rule description
        rule_desc = {
            "field": field_name,
            "operator": operator,
            "threshold": threshold,
            "payout_multiplier": payout_multiplier,
            "description": _describe_rule(field_name, operator, threshold, fixed_value, payout_multiplier),
        }
        if fixed_value is not None:
            rule_desc["fixed_value"] = fixed_value
        trigger_rules.append(rule_desc)

    # Add special "status" slider for flight cancellation
    if any(r.get("field") == "status" for r in rules):
        sliders.append({
            "name": "is_cancelled",
            "label": "Flight Cancelled",
            "min_value": 0,
            "max_value": 1,
            "step": 1,
            "default_value": 0,
            "threshold": 1,
            "unit": "toggle",
        })

    return {
        "product_id": str(product.id),
        "product_name": product.name,
        "sliders": sliders,
        "trigger_rules": trigger_rules,
        "base_payout": float(product.base_payout),
        "is_manual": False,
    }


def check_trigger(
    product: InsuranceProduct,
    parameters: Dict[str, Any],
) -> Dict:
    """
    Evaluate user-provided parameter values against trigger rules.

    Returns which rules triggered and the resulting payout.
    """
    trigger_conditions = product.trigger_conditions or {}
    rules = trigger_conditions.get("rules", [])
    base_payout = float(product.base_payout)

    triggered_rules = []
    max_multiplier = 0.0

    for rule in rules:
        raw_field = rule.get("field", "")
        operator = rule.get("operator", ">=")
        threshold_param = rule.get("threshold_param")
        fixed_value = rule.get("value")
        payout_multiplier = rule.get("payout_multiplier", 1.0)

        field_name = raw_field.strip("{}")

        # Handle flight cancellation special case
        if field_name == "status" and operator == "==" and fixed_value == "CANCELLED":
            is_cancelled = parameters.get("is_cancelled", 0)
            if is_cancelled == 1 or is_cancelled is True:
                triggered_rules.append({
                    "field": "status",
                    "description": "Flight Cancelled",
                    "payout_multiplier": payout_multiplier,
                })
                max_multiplier = max(max_multiplier, payout_multiplier)
            continue

        # Get the current value from user parameters
        current_value = parameters.get(field_name)
        if current_value is None:
            continue

        # Get threshold
        threshold = None
        if threshold_param:
            threshold = parameters.get(threshold_param)
            if threshold is None:
                # Use product defaults
                for f in (product.parameters_schema or {}).get("fields", []):
                    if f["name"] == threshold_param and "default" in f:
                        threshold = f["default"]
                        break
        elif fixed_value is not None:
            threshold = fixed_value

        if threshold is None:
            continue

        # Evaluate condition
        is_triggered = _evaluate_condition(float(current_value), operator, float(threshold))

        if is_triggered:
            triggered_rules.append({
                "field": field_name,
                "value": current_value,
                "threshold": threshold,
                "operator": operator,
                "description": _describe_rule(field_name, operator, threshold, fixed_value, payout_multiplier),
                "payout_multiplier": payout_multiplier,
            })
            max_multiplier = max(max_multiplier, payout_multiplier)

    is_triggered = len(triggered_rules) > 0
    payout_multiplier = max_multiplier if is_triggered else 0.0
    payout_amount = base_payout * payout_multiplier

    return {
        "triggered": is_triggered,
        "triggered_rules": triggered_rules,
        "payout_amount": round(payout_amount, 2),
        "payout_multiplier": payout_multiplier,
    }


def log_session(
    db: Session,
    user_id: UUID,
    product_id: UUID,
    input_parameters: Dict,
    triggers_activated: Dict,
) -> SimulationSession:
    """Log a simulation session for analytics."""
    session = SimulationSession(
        user_id=user_id,
        product_id=product_id,
        input_parameters=input_parameters,
        triggers_activated=triggers_activated,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def _evaluate_condition(value: float, operator: str, threshold: float) -> bool:
    """Evaluate a single trigger condition."""
    ops = {
        ">=": lambda v, t: v >= t,
        ">": lambda v, t: v > t,
        "<=": lambda v, t: v <= t,
        "<": lambda v, t: v < t,
        "==": lambda v, t: v == t,
        "ABOVE": lambda v, t: v > t,
        "BELOW": lambda v, t: v < t,
    }
    fn = ops.get(operator)
    if fn is None:
        logger.warning(f"Unknown operator: {operator}")
        return False
    return fn(value, threshold)


def _describe_rule(
    field: str,
    operator: str,
    threshold: Optional[float],
    fixed_value: Optional[Any],
    multiplier: float,
) -> str:
    """Generate a human-readable description for a trigger rule."""
    field_label = field.replace("_", " ").title()
    op_labels = {
        ">=": "reaches",
        ">": "exceeds",
        "<=": "drops to",
        "<": "drops below",
        "==": "equals",
        "ABOVE": "goes above",
        "BELOW": "drops below",
    }
    op_label = op_labels.get(operator, operator)

    if field == "status" and fixed_value == "CANCELLED":
        desc = "Flight is cancelled"
    elif threshold is not None:
        desc = f"{field_label} {op_label} {threshold}"
    else:
        desc = f"{field_label} {op_label} threshold"

    if multiplier != 1.0:
        desc += f" (x{multiplier} payout)"

    return desc
