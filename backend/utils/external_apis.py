"""External API clients — OpenWeatherMap and AviationStack with ApiMonitorLog logging."""
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

HANOI_LAT = 21.0285
HANOI_LON = 105.8542
OWM_BASE = "https://api.openweathermap.org/data/2.5"
AVIATION_BASE = "http://api.aviationstack.com/v1"


def _log_api_call(
    api_name: str,
    endpoint: str,
    status_code: Optional[int],
    response_time_ms: int,
    response_summary: Optional[Dict],
    error_message: Optional[str] = None,
) -> None:
    from config.database import SessionLocal
    from models.api_monitor_log import ApiMonitorLog

    db = SessionLocal()
    try:
        log = ApiMonitorLog(
            api_name=api_name,
            endpoint=endpoint,
            method="GET",
            status_code=status_code,
            response_time_ms=response_time_ms,
            response_summary=response_summary,
            error_message=error_message,
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to persist API log: {e}")
    finally:
        db.close()


class WeatherClient:
    API_NAME = "openweathermap"

    @staticmethod
    async def get_current_weather(lat: float, lon: float, api_key: str) -> Dict[str, Any]:
        """Fetch current weather and return normalized metrics for trigger evaluation."""
        endpoint = f"{OWM_BASE}/weather"
        params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}

        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(endpoint, params=params)
            elapsed = int((time.time() - start) * 1000)

            if resp.status_code != 200:
                _log_api_call(
                    WeatherClient.API_NAME, endpoint, resp.status_code,
                    elapsed, None, f"HTTP {resp.status_code}: {resp.text[:200]}",
                )
                logger.warning(f"OpenWeatherMap returned {resp.status_code}")
                return WeatherClient._mock_weather(lat, lon)

            data = resp.json()
            normalized = WeatherClient._normalize(data)
            _log_api_call(
                WeatherClient.API_NAME, endpoint, 200, elapsed,
                {
                    "location": data.get("name"),
                    "temp_celsius": normalized["temp_celsius"],
                    "rainfall_mm": normalized["rainfall_mm"],
                    "alert_severity": normalized["alert_severity"],
                    "description": normalized["description"],
                },
            )
            return normalized

        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            _log_api_call(WeatherClient.API_NAME, endpoint, None, elapsed, None, str(e))
            logger.error(f"WeatherClient error: {e}")
            return WeatherClient._mock_weather(lat, lon)

    @staticmethod
    def _normalize(data: Dict) -> Dict[str, Any]:
        main = data.get("main", {})
        rain = data.get("rain", {})
        wind = data.get("wind", {})
        weather_list = data.get("weather", [{}])
        weather_id = weather_list[0].get("id", 800)

        # Prefer 1h rain, fall back to 3h, then 0
        rainfall_mm = float(rain.get("1h", rain.get("3h", 0.0)))

        # Map OWM condition codes to severity 0-5
        if weather_id >= 900:
            alert_severity = 5
        elif 200 <= weather_id < 300:  # thunderstorm
            alert_severity = 4
        elif rainfall_mm >= 50:
            alert_severity = 4
        elif rainfall_mm >= 20:
            alert_severity = 3
        elif rainfall_mm >= 10:
            alert_severity = 2
        elif rainfall_mm > 0 or 300 <= weather_id < 400:
            alert_severity = 1
        else:
            alert_severity = 0

        return {
            "temp_celsius": float(main.get("temp", 25.0)),
            "feels_like": float(main.get("feels_like", 25.0)),
            "humidity": int(main.get("humidity", 70)),
            "rainfall_mm": rainfall_mm,
            "wind_speed": float(wind.get("speed", 0.0)),
            "alert_severity": alert_severity,
            "description": weather_list[0].get("description", "unknown"),
            "location_name": data.get("name", "Unknown"),
            "weather_id": weather_id,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _mock_weather(lat: float, lon: float) -> Dict[str, Any]:
        return {
            "temp_celsius": 28.5,
            "feels_like": 31.0,
            "humidity": 75,
            "rainfall_mm": 0.0,
            "wind_speed": 3.2,
            "alert_severity": 0,
            "description": "partly cloudy (mock — no API key)",
            "location_name": "Mock Location",
            "weather_id": 801,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "is_mock": True,
        }

    @staticmethod
    async def get_hanoi_weather(api_key: str) -> Dict[str, Any]:
        return await WeatherClient.get_current_weather(HANOI_LAT, HANOI_LON, api_key)

    @staticmethod
    async def get_forecast_probability(
        lat: float,
        lon: float,
        api_key: str,
        metric: str,
        threshold: float,
        comparison: str,
    ) -> Dict[str, Any]:
        """
        Call OWM 5-day/3h forecast (40 data points) and compute
        P(metric comparison threshold) as fraction of periods that trigger.

        Returns dict with keys: probability, sample_count, location_name, is_mock.
        """
        if not api_key:
            return {"probability": None, "sample_count": 0, "location_name": "unknown", "is_mock": True}

        endpoint = f"{OWM_BASE}/forecast"
        params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric", "cnt": 40}

        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(endpoint, params=params)
            elapsed = int((time.time() - start) * 1000)

            if resp.status_code != 200:
                _log_api_call(
                    WeatherClient.API_NAME, endpoint, resp.status_code,
                    elapsed, None, f"HTTP {resp.status_code}: {resp.text[:200]}",
                )
                return {"probability": None, "sample_count": 0, "location_name": "unknown", "is_mock": True}

            data = resp.json()
            items = data.get("list", [])
            location_name = (data.get("city") or {}).get("name", "Unknown")

            values = []
            for item in items:
                if metric == "rainfall_mm":
                    v = float((item.get("rain") or {}).get("3h", 0.0))
                elif metric == "temp_celsius":
                    v = float((item.get("main") or {}).get("temp", 25.0))
                else:
                    continue
                values.append(v)

            if not values:
                return {"probability": None, "sample_count": 0, "location_name": location_name, "is_mock": True}

            cmp = comparison.upper()
            triggered = sum(1 for v in values if (v > threshold if cmp == "ABOVE" else v < threshold))
            probability = triggered / len(values)

            _log_api_call(
                WeatherClient.API_NAME, endpoint, 200, elapsed,
                {"location": location_name, "metric": metric, "threshold": threshold,
                 "comparison": comparison, "probability": round(probability, 4), "samples": len(values)},
            )
            return {
                "probability": probability,
                "sample_count": len(values),
                "location_name": location_name,
                "is_mock": False,
            }

        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            _log_api_call(WeatherClient.API_NAME, endpoint, None, elapsed, None, str(e))
            logger.error(f"WeatherClient forecast error: {e}")
            return {"probability": None, "sample_count": 0, "location_name": "unknown", "is_mock": True}


class AviationClient:
    API_NAME = "aviationstack"

    @staticmethod
    async def get_flight_status(flight_iata: str, api_key: str) -> Dict[str, Any]:
        """Fetch flight status. Falls back to mock when key is absent."""
        if not api_key:
            return AviationClient._mock_flight(flight_iata)

        endpoint = f"{AVIATION_BASE}/flights"
        params = {"access_key": api_key, "flight_iata": flight_iata}

        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(endpoint, params=params)
            elapsed = int((time.time() - start) * 1000)

            if resp.status_code != 200:
                _log_api_call(
                    AviationClient.API_NAME, endpoint, resp.status_code,
                    elapsed, None, f"HTTP {resp.status_code}",
                )
                return AviationClient._mock_flight(flight_iata)

            data = resp.json()
            flights = data.get("data", [])
            normalized = AviationClient._normalize(
                flights[0] if flights else {}, flight_iata
            )
            _log_api_call(
                AviationClient.API_NAME, endpoint, 200, elapsed,
                {"flight": flight_iata, "status": normalized["status"],
                 "delay_minutes": normalized["delay_minutes"]},
            )
            return normalized

        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            _log_api_call(AviationClient.API_NAME, endpoint, None, elapsed, None, str(e))
            logger.error(f"AviationClient error: {e}")
            return AviationClient._mock_flight(flight_iata)

    @staticmethod
    def _normalize(flight: Dict, flight_iata: str) -> Dict[str, Any]:
        status = "ON_TIME"
        delay_minutes = 0

        if flight.get("flight_status") == "cancelled":
            status = "CANCELLED"
        else:
            arr_delay = (flight.get("arrival") or {}).get("delay") or 0
            dep_delay = (flight.get("departure") or {}).get("delay") or 0
            delay_minutes = max(int(arr_delay), int(dep_delay))
            if delay_minutes > 0:
                status = "DELAYED"

        return {
            "flight_iata": flight_iata,
            "status": status,
            "delay_minutes": delay_minutes,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _mock_flight(flight_iata: str) -> Dict[str, Any]:
        return {
            "flight_iata": flight_iata,
            "status": "ON_TIME",
            "delay_minutes": 0,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "is_mock": True,
        }
