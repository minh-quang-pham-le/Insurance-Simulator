"""
Risk engine using historical CSV data from ml_data/.

For each product, computes event probability from real historical data:
- FLIGHT_DELAY: per-airline disruption rate from vietnam_airlines_flights.csv
- CROP_WEATHER: empirical P(metric comparison threshold) from weather_data.csv
"""
import logging
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Assumed disruption rates for airlines not in the CSV (relative to VN baseline)
_AIRLINE_DEFAULTS: Dict[str, float] = {
    "VJ": 0.21,  # budget carrier, slightly higher
    "QH": 0.16,  # bamboo, slightly lower
}

_ML_DATA_DIR = Path(__file__).parent.parent / "ml_data"


class RiskEngine:
    def __init__(self) -> None:
        self.flight_df: Optional[pd.DataFrame] = None
        self.weather_df: Optional[pd.DataFrame] = None
        self._airline_disruption_rate: Dict[str, float] = {}
        self._cancel_rate: float = 0.16
        self._load_data()

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_data(self) -> None:
        self._load_flight_data()
        self._load_weather_data()

    def _load_flight_data(self) -> None:
        path = _ML_DATA_DIR / "vietnam_airlines_flights.csv"
        if not path.exists():
            logger.warning("Flight CSV not found at %s — using default rates", path)
            return

        df = pd.read_csv(path)

        # Compute arrival delay in minutes
        df["arr_actual"] = pd.to_datetime(df["Arrival Time"], errors="coerce")
        df["arr_sched"] = pd.to_datetime(df["Estimated Arrival"], errors="coerce")
        df["arrival_delay_min"] = (
            (df["arr_actual"] - df["arr_sched"]).dt.total_seconds() / 60
        )

        # Disrupted = cancelled OR arrival delayed > 30 min
        df["is_disrupted"] = (
            (df["Flight Status"] == "cancelled") | (df["arrival_delay_min"] > 30)
        ).astype(int)

        self.flight_df = df
        self._cancel_rate = float((df["Flight Status"] == "cancelled").mean())

        for airline, grp in df.groupby("Airline Code"):
            self._airline_disruption_rate[str(airline)] = float(
                grp["is_disrupted"].mean()
            )

        logger.info(
            "Flight data loaded: %d rows, cancel_rate=%.3f, airline_rates=%s",
            len(df),
            self._cancel_rate,
            self._airline_disruption_rate,
        )

    def _load_weather_data(self) -> None:
        path = _ML_DATA_DIR / "weather_data.csv"
        if not path.exists():
            logger.warning("Weather CSV not found at %s — using fallback", path)
            return

        self.weather_df = pd.read_csv(path)
        logger.info("Weather data loaded: %d rows", len(self.weather_df))

    # ------------------------------------------------------------------
    # Public API (matches existing interface used by policy_service.py)
    # ------------------------------------------------------------------

    def calculate_premium(
        self,
        product_id: str,
        base_price: float,
        features: Dict,
    ) -> Dict:
        """
        Calculate premium using historical event probability.

        Args:
            product_id: product category lowercase ("flight_delay", "crop_weather")
            base_price: base_payout x (1 + risk_margin) x (duration / 30)
            features: user-submitted policy parameters dict

        Returns dict with keys: event_probability, event_probability_pct,
        risk_multiplier, final_premium, model_used.
        """
        if product_id == "flight_delay":
            probability = self._flight_probability(features)
            model_used = self.flight_df is not None
        elif product_id == "crop_weather":
            probability = self._weather_probability(features)
            model_used = self.weather_df is not None
        else:
            logger.warning("Unknown product_id '%s', using fallback 0.30", product_id)
            probability = 0.30
            model_used = False

        # risk_multiplier in [0.5, 2.0]
        risk_multiplier = 0.5 + probability * 1.5
        final_premium = base_price * risk_multiplier

        return {
            "event_probability": float(probability),
            "event_probability_pct": float(probability * 100),
            "risk_multiplier": float(risk_multiplier),
            "final_premium": float(final_premium),
            "model_used": model_used,
        }

    def get_catalog_risk_score(self, product_id: str) -> float:
        """
        Risk score for product catalog display (1-10 scale).
        Uses typical default parameters for each product type.
        """
        if product_id == "flight_delay":
            p = self._flight_probability(
                {"airline_code": "VN", "delay_threshold_minutes": 120}
            )
        elif product_id == "crop_weather":
            if self.weather_df is not None:
                # General extreme-weather event rate from the dataset
                p = float(self.weather_df["event_occurred"].mean())
            else:
                p = 0.30
        else:
            p = 0.30

        return round(1.0 + p * 9.0, 1)

    async def calculate_premium_async(
        self,
        product_id: str,
        base_price: float,
        features: Dict,
        api_key: str = "",
    ) -> Dict:
        """
        Like calculate_premium() but uses live OWM forecast for crop_weather
        when lat/lon and api_key are available. Falls back to CSV otherwise.
        """
        if product_id == "crop_weather":
            lat = features.get("location_lat")
            lon = features.get("location_lon")
            metric = features.get("weather_metric", "rainfall_mm")
            threshold = float(features.get("threshold", 10))
            comparison = str(features.get("comparison", "ABOVE"))

            live_result = None
            if lat is not None and lon is not None and api_key:
                from utils.external_apis import WeatherClient
                live_result = await WeatherClient.get_forecast_probability(
                    lat=float(lat), lon=float(lon), api_key=api_key,
                    metric=metric, threshold=threshold, comparison=comparison,
                )

            if live_result and not live_result.get("is_mock") and live_result["probability"] is not None:
                probability = float(np.clip(live_result["probability"], 0.01, 0.98))
                model_used = True
            else:
                probability = self._weather_probability(features)
                model_used = False
        elif product_id == "flight_delay":
            probability = self._flight_probability(features)
            model_used = self.flight_df is not None
        else:
            probability = 0.30
            model_used = False

        risk_multiplier = 0.5 + probability * 1.5
        final_premium = base_price * risk_multiplier
        return {
            "event_probability": float(probability),
            "event_probability_pct": float(probability * 100),
            "risk_multiplier": float(risk_multiplier),
            "final_premium": float(final_premium),
            "model_used": model_used,
        }

    def get_risk_profile(self, product_id: str, features: Dict) -> Dict:
        calc = self.calculate_premium(product_id, 100, features)
        return {
            "product_id": product_id,
            "event_probability_pct": calc["event_probability_pct"],
            "risk_level": self._get_risk_level(calc["event_probability"]),
            "risk_multiplier": calc["risk_multiplier"],
            "model_used": calc["model_used"],
        }

    # ------------------------------------------------------------------
    # Private probability helpers
    # ------------------------------------------------------------------

    def _flight_probability(self, features: Dict) -> float:
        """
        P(flight cancelled or delayed > threshold_minutes) for the given airline.

        Threshold effect:
        - threshold <= 30 min: full disruption rate applies
        - threshold > 30 min: probability converges toward cancel_rate
          (most delays in data are < 45 min, so only cancellations matter above 30 min)
        """
        airline = str(features.get("airline_code", "VN")).upper()
        threshold = float(features.get("delay_threshold_minutes", 120))

        base_rate = self._airline_disruption_rate.get(airline)
        if base_rate is None:
            base_rate = _AIRLINE_DEFAULTS.get(airline, 0.18)

        if threshold <= 30:
            p = base_rate
        else:
            # Linear blend toward cancel_rate as threshold rises to 360 min
            t = min(1.0, (threshold - 30) / (360 - 30))
            p = base_rate + t * (self._cancel_rate - base_rate)

        return float(np.clip(p, 0.03, 0.95))

    def _weather_probability(self, features: Dict) -> float:
        """
        Empirical P(weather_metric comparison threshold) from historical daily data.

        Supported metrics:
          rainfall_mm -> 'rain' column
          temp_celsius -> 'temperature' column
        """
        if self.weather_df is None:
            return 0.30

        metric = features.get("weather_metric", "rainfall_mm")
        threshold = float(features.get("threshold", 10))
        comparison = str(features.get("comparison", "ABOVE")).upper()

        col_map = {"rainfall_mm": "rain", "temp_celsius": "temperature"}
        col = col_map.get(metric)

        if not col or col not in self.weather_df.columns:
            logger.warning("Unknown weather metric '%s'", metric)
            return 0.30

        series = self.weather_df[col].dropna()
        if series.empty:
            return 0.30

        if comparison == "ABOVE":
            prob = float((series > threshold).mean())
        else:
            prob = float((series < threshold).mean())

        return float(np.clip(prob, 0.01, 0.98))

    @staticmethod
    def _get_risk_level(probability: float) -> str:
        if probability < 0.25:
            return "low"
        elif probability < 0.50:
            return "medium"
        elif probability < 0.75:
            return "high"
        return "very_high"


# ---------------------------------------------------------------------------
# Global singleton
# ---------------------------------------------------------------------------

_risk_engine: Optional[RiskEngine] = None


def get_risk_engine() -> RiskEngine:
    global _risk_engine
    if _risk_engine is None:
        _risk_engine = RiskEngine()
    return _risk_engine
