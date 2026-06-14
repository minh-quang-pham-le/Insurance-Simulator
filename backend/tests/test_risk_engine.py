"""
Unit tests for services/risk_engine.py.

These tests exercise the RiskEngine probability calculations and premium formula
without touching the database or any external API.
"""
import pandas as pd
import pytest

from services.risk_engine import RiskEngine


# ---------------------------------------------------------------------------
# Helpers — build in-memory DataFrames that stand in for the CSV files
# ---------------------------------------------------------------------------

def _make_flight_df() -> pd.DataFrame:
    """50 rows: 10 cancelled, 15 delayed >30 min, 25 on-time (VN airline only)."""
    rows = []
    for _ in range(10):
        rows.append({
            "Airline Code": "VN",
            "Flight Status": "cancelled",
            "Arrival Time": "2024-01-01 12:30",
            "Estimated Arrival": "2024-01-01 12:00",
        })
    for _ in range(15):
        rows.append({
            "Airline Code": "VN",
            "Flight Status": "on_time",
            "Arrival Time": "2024-01-01 13:00",
            "Estimated Arrival": "2024-01-01 12:00",
        })
    for _ in range(25):
        rows.append({
            "Airline Code": "VN",
            "Flight Status": "on_time",
            "Arrival Time": "2024-01-01 12:10",
            "Estimated Arrival": "2024-01-01 12:00",
        })
    return pd.DataFrame(rows)


def _make_weather_df() -> pd.DataFrame:
    """100 rows: rain 0-99, temperature cycling 20-39, event_occurred flag."""
    rain = list(range(100))
    temp = [20 + (i % 20) for i in range(100)]
    event = [1 if r > 50 else 0 for r in rain]
    return pd.DataFrame({"rain": rain, "temperature": temp, "event_occurred": event})


# ---------------------------------------------------------------------------
# Fixture — engine loaded with synthetic data (no filesystem access)
# ---------------------------------------------------------------------------

@pytest.fixture
def engine() -> RiskEngine:
    eng = RiskEngine.__new__(RiskEngine)
    eng._airline_disruption_rate = {}
    eng._cancel_rate = 0.0

    # Replicate _load_flight_data computation on synthetic data
    df = _make_flight_df()
    df["arr_actual"] = pd.to_datetime(df["Arrival Time"], errors="coerce")
    df["arr_sched"] = pd.to_datetime(df["Estimated Arrival"], errors="coerce")
    df["arrival_delay_min"] = (
        (df["arr_actual"] - df["arr_sched"]).dt.total_seconds() / 60
    )
    df["is_disrupted"] = (
        (df["Flight Status"] == "cancelled") | (df["arrival_delay_min"] > 30)
    ).astype(int)
    eng.flight_df = df
    eng._cancel_rate = float((df["Flight Status"] == "cancelled").mean())
    for airline, grp in df.groupby("Airline Code"):
        eng._airline_disruption_rate[str(airline)] = float(grp["is_disrupted"].mean())

    eng.weather_df = _make_weather_df()
    return eng


# ---------------------------------------------------------------------------
# Flight probability
# ---------------------------------------------------------------------------

class TestFlightProbability:
    def test_disruption_rate_matches_data(self, engine):
        # 10 cancelled + 15 delayed >30 min = 25/50 = 0.50
        p = engine._flight_probability(
            {"airline_code": "VN", "delay_threshold_minutes": 30}
        )
        assert abs(p - 0.50) < 1e-6

    def test_high_threshold_converges_toward_cancel_rate(self, engine):
        # At 360 min threshold, probability blends toward cancel_rate (0.20)
        p_high = engine._flight_probability(
            {"airline_code": "VN", "delay_threshold_minutes": 360}
        )
        p_low = engine._airline_disruption_rate["VN"]
        assert p_high < p_low

    def test_unknown_airline_uses_default_rate(self, engine):
        p = engine._flight_probability(
            {"airline_code": "ZZ", "delay_threshold_minutes": 120}
        )
        assert 0.03 <= p <= 0.95

    def test_probability_clamped_in_valid_range(self, engine):
        for threshold in [0, 60, 120, 360]:
            p = engine._flight_probability(
                {"airline_code": "VN", "delay_threshold_minutes": threshold}
            )
            assert 0.03 <= p <= 0.95


# ---------------------------------------------------------------------------
# Weather probability
# ---------------------------------------------------------------------------

class TestWeatherProbability:
    def test_rainfall_above_threshold(self, engine):
        # rain values 0–99 → P(rain > 50) = 49/100 = 0.49
        p = engine._weather_probability(
            {"weather_metric": "rainfall_mm", "threshold": 50, "comparison": "ABOVE"}
        )
        assert abs(p - 0.49) < 1e-6

    def test_rainfall_below_threshold(self, engine):
        # P(rain < 50) = 50/100 = 0.50
        p = engine._weather_probability(
            {"weather_metric": "rainfall_mm", "threshold": 50, "comparison": "BELOW"}
        )
        assert abs(p - 0.50) < 1e-6

    def test_unknown_metric_returns_fallback(self, engine):
        p = engine._weather_probability(
            {"weather_metric": "humidity_pct", "threshold": 80, "comparison": "ABOVE"}
        )
        assert p == 0.30

    def test_no_weather_data_returns_fallback(self):
        eng = RiskEngine.__new__(RiskEngine)
        eng.flight_df = None
        eng.weather_df = None
        eng._airline_disruption_rate = {}
        eng._cancel_rate = 0.16
        p = eng._weather_probability(
            {"weather_metric": "rainfall_mm", "threshold": 10, "comparison": "ABOVE"}
        )
        assert p == 0.30

    def test_probability_does_not_exceed_ceiling(self, engine):
        # threshold=0 ABOVE → almost everything qualifies → clamp to 0.98
        p = engine._weather_probability(
            {"weather_metric": "rainfall_mm", "threshold": 0, "comparison": "ABOVE"}
        )
        assert p <= 0.98


# ---------------------------------------------------------------------------
# Premium formula
# ---------------------------------------------------------------------------

class TestPremiumCalculation:
    def test_risk_multiplier_formula(self, engine):
        result = engine.calculate_premium(
            product_id="flight_delay",
            base_price=100.0,
            features={"airline_code": "VN", "delay_threshold_minutes": 30},
        )
        expected = 0.5 + result["event_probability"] * 1.5
        assert abs(result["risk_multiplier"] - expected) < 1e-6

    def test_final_premium_equals_base_times_multiplier(self, engine):
        result = engine.calculate_premium(
            product_id="crop_weather",
            base_price=200.0,
            features={"weather_metric": "rainfall_mm", "threshold": 50, "comparison": "ABOVE"},
        )
        expected_premium = 200.0 * result["risk_multiplier"]
        assert abs(result["final_premium"] - expected_premium) < 1e-4

    def test_event_probability_pct_is_scaled(self, engine):
        result = engine.calculate_premium(
            product_id="flight_delay",
            base_price=100.0,
            features={"airline_code": "VN", "delay_threshold_minutes": 120},
        )
        assert abs(result["event_probability_pct"] - result["event_probability"] * 100) < 1e-6

    def test_unknown_product_uses_30pct_fallback(self, engine):
        result = engine.calculate_premium(
            product_id="gadget_repair",
            base_price=100.0,
            features={},
        )
        assert result["event_probability"] == 0.30
        assert result["model_used"] is False

    def test_model_used_true_when_data_loaded(self, engine):
        result = engine.calculate_premium(
            product_id="flight_delay",
            base_price=100.0,
            features={"airline_code": "VN", "delay_threshold_minutes": 120},
        )
        assert result["model_used"] is True


# ---------------------------------------------------------------------------
# Risk score / risk level
# ---------------------------------------------------------------------------

class TestRiskScoreAndLevel:
    def test_catalog_score_in_1_to_10_range(self, engine):
        score = engine.get_catalog_risk_score("flight_delay")
        assert 1.0 <= score <= 10.0

    def test_weather_catalog_score_in_range(self, engine):
        score = engine.get_catalog_risk_score("crop_weather")
        assert 1.0 <= score <= 10.0

    def test_risk_level_low(self):
        assert RiskEngine._get_risk_level(0.10) == "low"

    def test_risk_level_medium(self):
        assert RiskEngine._get_risk_level(0.30) == "medium"

    def test_risk_level_high(self):
        assert RiskEngine._get_risk_level(0.60) == "high"

    def test_risk_level_very_high(self):
        assert RiskEngine._get_risk_level(0.80) == "very_high"

    def test_risk_level_boundary_medium_to_high(self):
        assert RiskEngine._get_risk_level(0.50) == "high"
