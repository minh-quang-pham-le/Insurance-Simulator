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
        "label": "Temperature (\u00b0C)",
        "min_value": 0,
        "max_value": 50,
        "step": 0.5,
        "default_value": 25,
        "unit": "\u00b0C",
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
}

# Friendly labels for fields
FIELD_LABELS = {
    "delay_minutes": "Flight Delay",
    "rainfall_mm": "Rainfall",
    "temp_celsius": "Temperature",
    "drought_days": "Drought Duration",
    "alert_severity": "Alert Severity",
    "weather_metric": "Weather Metric",
    "status": "Flight Status",
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
                    "This product uses manual claims. Submit a claim with "
                    "a description and photo evidence for admin review."
                ),
            },
        }

    # Extract default parameter values and option lists from schema
    param_defaults = {}
    param_options = {}
    for field in parameters_schema.get("fields", []):
        if "default" in field:
            param_defaults[field["name"]] = field["default"]
        if "min" in field:
            param_defaults[f"_min_{field['name']}"] = field["min"]
        if "max" in field:
            param_defaults[f"_max_{field['name']}"] = field["max"]
        if "options" in field:
            param_options[field["name"]] = field["options"]

    sliders = []
    trigger_rules = []
    seen_fields = set()

    # Detect dynamic template fields like {weather_metric}
    has_dynamic_fields = any("{" in rule.get("field", "") for rule in rules)

    if has_dynamic_fields:
        # Expand dynamic fields into concrete sliders for each option
        sliders, trigger_rules = _expand_dynamic_rules(
            rules, param_defaults, param_options, parameters_schema
        )
    else:
        # Standard products: direct field mapping
        for rule in rules:
            raw_field = rule.get("field", "")
            operator = rule.get("operator", ">=")
            threshold_param = rule.get("threshold_param")
            fixed_value = rule.get("value")
            payout_multiplier = rule.get("payout_multiplier", 1.0)

            field_name = raw_field.strip("{}")

            # Determine threshold
            threshold = None
            if threshold_param and threshold_param in param_defaults:
                threshold = param_defaults[threshold_param]
            elif fixed_value is not None:
                threshold = fixed_value

            # Build slider (one per unique field, skip "status")
            if field_name not in seen_fields and field_name != "status":
                seen_fields.add(field_name)
                defaults = SLIDER_DEFAULTS.get(field_name, {})

                slider = {
                    "name": field_name,
                    "label": defaults.get("label", _label(field_name)),
                    "min_value": defaults.get("min_value", 0),
                    "max_value": defaults.get("max_value", 100),
                    "step": defaults.get("step", 1),
                    "default_value": defaults.get("default_value", 0),
                    "threshold": threshold,
                    "unit": defaults.get("unit", ""),
                }

                if threshold_param:
                    schema_min = param_defaults.get(f"_min_{threshold_param}")
                    schema_max = param_defaults.get(f"_max_{threshold_param}")
                    if schema_min is not None:
                        slider["min_value"] = schema_min
                    if schema_max is not None:
                        slider["max_value"] = schema_max

                sliders.append(slider)

            trigger_rules.append({
                "field": field_name,
                "operator": operator,
                "threshold": threshold,
                "payout_multiplier": payout_multiplier,
                "description": _describe_rule(field_name, operator, threshold, fixed_value, payout_multiplier),
            })

        # Add toggle for flight cancellation
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


def _expand_dynamic_rules(
    rules: List[Dict],
    param_defaults: Dict,
    param_options: Dict,
    parameters_schema: Dict,
) -> tuple:
    """
    Expand dynamic template rules (like Crop Weather) into concrete sliders.

    Crop Weather uses {weather_metric} and {comparison} which are user-selectable.
    We expand these into one slider per possible weather metric so users can
    explore all scenarios.
    """
    sliders = []
    trigger_rules = []

    # Find the metric options (e.g., weather_metric -> rainfall_mm, temp_celsius, drought_days)
    metric_options = param_options.get("weather_metric", [])
    comparison_options = param_options.get("comparison", [])

    if metric_options:
        # Create a slider for each possible weather metric
        for opt in metric_options:
            metric_name = opt["value"]  # e.g. "rainfall_mm"
            metric_label = opt["label"]  # e.g. "Excessive Rainfall (flood)"
            defaults = SLIDER_DEFAULTS.get(metric_name, {})

            threshold_default = param_defaults.get("threshold")

            sliders.append({
                "name": metric_name,
                "label": defaults.get("label", metric_label),
                "min_value": defaults.get("min_value", 0),
                "max_value": defaults.get("max_value", 100),
                "step": defaults.get("step", 1),
                "default_value": defaults.get("default_value", 0),
                "threshold": threshold_default,
                "unit": defaults.get("unit", ""),
            })

        # Add threshold slider
        sliders.append({
            "name": "threshold",
            "label": "Trigger Threshold",
            "min_value": 0,
            "max_value": 200,
            "step": 1,
            "default_value": param_defaults.get("threshold", 50),
            "threshold": None,
            "unit": "value",
        })

        # Add comparison direction toggle
        sliders.append({
            "name": "comparison",
            "label": "Trigger When Value Is",
            "min_value": 0,
            "max_value": 1,
            "step": 1,
            "default_value": 0,
            "threshold": None,
            "unit": "direction",
            "options": [
                {"value": 0, "label": "Above threshold"},
                {"value": 1, "label": "Below threshold"},
            ],
        })

        trigger_rules.append({
            "field": "weather_metric",
            "operator": "dynamic",
            "threshold": param_defaults.get("threshold"),
            "payout_multiplier": 1.0,
            "description": "Weather metric crosses your set threshold",
        })
    else:
        # Fallback: generic slider
        sliders.append({
            "name": "value",
            "label": "Metric Value",
            "min_value": 0,
            "max_value": 100,
            "step": 1,
            "default_value": 0,
            "threshold": param_defaults.get("threshold", 50),
            "unit": "",
        })
        trigger_rules.append({
            "field": "value",
            "operator": ">=",
            "threshold": param_defaults.get("threshold", 50),
            "payout_multiplier": 1.0,
            "description": "Value reaches threshold",
        })

    return sliders, trigger_rules


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

    # Detect if this product uses dynamic template fields
    has_dynamic = any("{" in rule.get("field", "") for rule in rules)

    if has_dynamic:
        # Handle Crop Weather style: check each concrete metric against threshold
        triggered_rules, max_multiplier = _check_dynamic_triggers(
            rules, parameters, product
        )
    else:
        for rule in rules:
            raw_field = rule.get("field", "")
            operator = rule.get("operator", ">=")
            threshold_param = rule.get("threshold_param")
            fixed_value = rule.get("value")
            payout_multiplier = rule.get("payout_multiplier", 1.0)

            field_name = raw_field.strip("{}")

            # Handle flight cancellation
            if field_name == "status" and operator == "==" and fixed_value == "CANCELLED":
                is_cancelled = parameters.get("is_cancelled", 0)
                if is_cancelled == 1 or is_cancelled is True:
                    triggered_rules.append({
                        "field": "status",
                        "description": "Flight is cancelled",
                        "payout_multiplier": payout_multiplier,
                    })
                    max_multiplier = max(max_multiplier, payout_multiplier)
                continue

            current_value = parameters.get(field_name)
            if current_value is None:
                continue

            threshold = None
            if threshold_param:
                threshold = parameters.get(threshold_param)
                if threshold is None:
                    for f in (product.parameters_schema or {}).get("fields", []):
                        if f["name"] == threshold_param and "default" in f:
                            threshold = f["default"]
                            break
            elif fixed_value is not None:
                threshold = fixed_value

            if threshold is None:
                continue

            if _evaluate_condition(float(current_value), operator, float(threshold)):
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
    final_multiplier = max_multiplier if is_triggered else 0.0
    payout_amount = base_payout * final_multiplier

    return {
        "triggered": is_triggered,
        "triggered_rules": triggered_rules,
        "payout_amount": round(payout_amount, 2),
        "payout_multiplier": final_multiplier,
    }


def _check_dynamic_triggers(
    rules: List[Dict],
    parameters: Dict[str, Any],
    product: InsuranceProduct,
) -> tuple:
    """Check dynamic template triggers (Crop Weather style)."""
    triggered_rules = []
    max_multiplier = 0.0

    # The threshold can come from parameters or product defaults
    threshold = parameters.get("threshold")
    if threshold is None:
        for f in (product.parameters_schema or {}).get("fields", []):
            if f["name"] == "threshold" and "default" in f:
                threshold = f["default"]
                break

    if threshold is None:
        return triggered_rules, max_multiplier

    # The comparison direction comes from the "comparison" parameter
    # ABOVE = trigger when value > threshold (e.g., too much rain)
    # BELOW = trigger when value < threshold (e.g., drought)
    raw_comparison = parameters.get("comparison", "ABOVE")
    # Handle numeric toggle: 0=ABOVE, 1=BELOW
    if raw_comparison == 0 or raw_comparison == "0":
        comparison = "ABOVE"
    elif raw_comparison == 1 or raw_comparison == "1":
        comparison = "BELOW"
    else:
        comparison = raw_comparison

    weather_metrics = ["rainfall_mm", "temp_celsius", "drought_days"]
    for metric in weather_metrics:
        value = parameters.get(metric)
        if value is None:
            continue

        # Per-metric threshold: {metric}_threshold overrides global threshold
        metric_threshold = parameters.get(f"{metric}_threshold")
        if metric_threshold is None:
            metric_threshold = threshold
        if metric_threshold is None:
            continue

        # Per-metric direction overrides global: 0 = ABOVE, 1 = BELOW
        per_metric_dir = parameters.get(f"{metric}_dir")
        if per_metric_dir is not None:
            metric_comparison = "ABOVE" if (per_metric_dir == 0 or per_metric_dir == "0") else "BELOW"
        else:
            metric_comparison = comparison

        if _evaluate_condition(float(value), metric_comparison, float(metric_threshold)):
            direction = "exceeds" if metric_comparison == "ABOVE" else "drops below"
            triggered_rules.append({
                "field": metric,
                "value": value,
                "threshold": metric_threshold,
                "operator": metric_comparison,
                "description": f"{_label(metric)} {direction} {metric_threshold}",
                "payout_multiplier": 1.0,
            })
            max_multiplier = max(max_multiplier, 1.0)

    return triggered_rules, max_multiplier


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


def _label(field_name: str) -> str:
    """Get a friendly label for a field name."""
    return FIELD_LABELS.get(field_name, field_name.replace("_", " ").title())


def _describe_rule(
    field: str,
    operator: str,
    threshold: Optional[float],
    fixed_value: Optional[Any],
    multiplier: float,
) -> str:
    """Generate a human-readable description for a trigger rule."""
    field_label = _label(field)
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
