"""
Unit tests for services/simulation_engine.py.

Tests cover _evaluate_condition (the shared trigger evaluator used by both
the Simulation Engine and the Claims Engine) and check_trigger for both
Flight Delay and Weather product types.
"""
import pytest
from unittest.mock import MagicMock
from decimal import Decimal

from services.simulation_engine import _evaluate_condition, check_trigger, get_simulation_config
from tests.conftest import make_product, make_weather_product


# ---------------------------------------------------------------------------
# _evaluate_condition — shared primitive used in both simulation and claims
# ---------------------------------------------------------------------------

class TestEvaluateCondition:
    def test_gte_true(self):
        assert _evaluate_condition(120.0, ">=", 120.0) is True

    def test_gte_false(self):
        assert _evaluate_condition(119.0, ">=", 120.0) is False

    def test_gt_true(self):
        assert _evaluate_condition(121.0, ">", 120.0) is True

    def test_gt_equal_false(self):
        assert _evaluate_condition(120.0, ">", 120.0) is False

    def test_lte_true(self):
        assert _evaluate_condition(10.0, "<=", 10.0) is True

    def test_lt_true(self):
        assert _evaluate_condition(9.0, "<", 10.0) is True

    def test_eq_true(self):
        assert _evaluate_condition(5.0, "==", 5.0) is True

    def test_eq_false(self):
        assert _evaluate_condition(5.0, "==", 6.0) is False

    def test_above_operator(self):
        assert _evaluate_condition(51.0, "ABOVE", 50.0) is True
        assert _evaluate_condition(50.0, "ABOVE", 50.0) is False

    def test_below_operator(self):
        assert _evaluate_condition(5.0, "BELOW", 10.0) is True
        assert _evaluate_condition(10.0, "BELOW", 10.0) is False

    def test_unknown_operator_returns_false(self):
        assert _evaluate_condition(100.0, "BETWEEN", 50.0) is False


# ---------------------------------------------------------------------------
# check_trigger — Flight Delay product
# ---------------------------------------------------------------------------

class TestCheckTriggerFlightDelay:
    def test_no_trigger_when_delay_below_threshold(self):
        product = make_product()
        params = {"delay_minutes": 60, "delay_threshold_minutes": 120}
        result = check_trigger(product, params)
        assert result["triggered"] is False
        assert result["payout_amount"] == 0.0

    def test_trigger_when_delay_meets_threshold(self):
        product = make_product()
        params = {"delay_minutes": 120, "delay_threshold_minutes": 120}
        result = check_trigger(product, params)
        assert result["triggered"] is True
        assert result["payout_amount"] == float(product.base_payout) * 1.0

    def test_trigger_when_delay_exceeds_threshold(self):
        product = make_product()
        params = {"delay_minutes": 250, "delay_threshold_minutes": 120}
        result = check_trigger(product, params)
        assert result["triggered"] is True

    def test_cancellation_triggers_1_5x_payout(self):
        product = make_product()
        params = {"is_cancelled": 1, "delay_threshold_minutes": 120}
        result = check_trigger(product, params)
        assert result["triggered"] is True
        assert abs(result["payout_multiplier"] - 1.5) < 1e-6
        expected_payout = float(product.base_payout) * 1.5
        assert abs(result["payout_amount"] - expected_payout) < 1e-4

    def test_cancellation_payout_higher_than_delay_payout(self):
        product = make_product()
        delay_result = check_trigger(product, {"delay_minutes": 200, "delay_threshold_minutes": 120})
        cancel_result = check_trigger(product, {"is_cancelled": 1, "delay_threshold_minutes": 120})
        assert cancel_result["payout_amount"] > delay_result["payout_amount"]

    def test_no_cancel_flag_does_not_trigger_cancel_rule(self):
        product = make_product()
        params = {"is_cancelled": 0, "delay_minutes": 60, "delay_threshold_minutes": 120}
        result = check_trigger(product, params)
        assert result["triggered"] is False


# ---------------------------------------------------------------------------
# check_trigger — Weather product (dynamic template rules)
# ---------------------------------------------------------------------------

class TestCheckTriggerWeather:
    def test_rainfall_above_threshold_triggers(self):
        product = make_weather_product()
        params = {"rainfall_mm": 75.0, "threshold": 50.0, "comparison": "ABOVE"}
        result = check_trigger(product, params)
        assert result["triggered"] is True
        assert result["payout_amount"] > 0

    def test_rainfall_below_threshold_no_trigger(self):
        product = make_weather_product()
        params = {"rainfall_mm": 30.0, "threshold": 50.0, "comparison": "ABOVE"}
        result = check_trigger(product, params)
        assert result["triggered"] is False

    def test_rainfall_below_comparison_triggers(self):
        product = make_weather_product()
        params = {"rainfall_mm": 5.0, "threshold": 20.0, "comparison": "BELOW"}
        result = check_trigger(product, params)
        assert result["triggered"] is True

    def test_no_threshold_no_trigger(self):
        product = make_weather_product()
        params = {"rainfall_mm": 100.0, "comparison": "ABOVE"}
        result = check_trigger(product, params)
        assert result["triggered"] is False

    def test_numeric_comparison_0_means_above(self):
        product = make_weather_product()
        params = {"rainfall_mm": 75.0, "threshold": 50.0, "comparison": 0}
        result = check_trigger(product, params)
        assert result["triggered"] is True

    def test_numeric_comparison_1_means_below(self):
        product = make_weather_product()
        params = {"rainfall_mm": 5.0, "threshold": 20.0, "comparison": 1}
        result = check_trigger(product, params)
        assert result["triggered"] is True


# ---------------------------------------------------------------------------
# get_simulation_config
# ---------------------------------------------------------------------------

class TestGetSimulationConfig:
    def test_flight_product_has_delay_slider(self):
        product = make_product()
        config = get_simulation_config(product)
        assert config["is_manual"] is False
        slider_names = [s["name"] for s in config["sliders"]]
        assert "delay_minutes" in slider_names

    def test_flight_product_has_cancel_toggle(self):
        product = make_product()
        config = get_simulation_config(product)
        slider_names = [s["name"] for s in config["sliders"]]
        assert "is_cancelled" in slider_names

    def test_weather_product_has_metric_sliders(self):
        product = make_weather_product()
        config = get_simulation_config(product)
        assert config["is_manual"] is False
        slider_names = [s["name"] for s in config["sliders"]]
        assert "rainfall_mm" in slider_names or "temp_celsius" in slider_names

    def test_manual_product_returns_manual_flag(self):
        product = MagicMock()
        product.id = "manual-id"
        product.name = "Gadget Repair"
        product.base_payout = Decimal("300.00")
        product.trigger_conditions = {"type": "MANUAL", "requires": ["photo"]}
        product.parameters_schema = {"fields": []}
        config = get_simulation_config(product)
        assert config["is_manual"] is True
        assert config["sliders"] == []

    def test_base_payout_in_config(self):
        product = make_product()
        config = get_simulation_config(product)
        assert config["base_payout"] == float(product.base_payout)
