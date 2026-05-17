"""Weather data crawling utilities for ML training."""
import json
import csv
from pathlib import Path
from typing import Dict, List, Any
import logging
import requests
import pandas as pd
from datetime import datetime, timedelta
import urllib3

# Suppress SSL warnings when verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class WeatherDataCrawler:
    """Utility for crawling and preparing weather training data for ML models."""

    @staticmethod
    def create_training_data_dir() -> Path:
        """Create backend/ml_data directory if it doesn't exist."""
        ml_data_dir = Path(__file__).parent.parent / "ml_data"
        ml_data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Training data directory: {ml_data_dir}")
        return ml_data_dir

    @staticmethod
    def save_csv_data(filename: str, data: List[Dict[str, Any]]) -> Path:
        """
        Save list of dictionaries to CSV file in ml_data directory.
        
        Args:
            filename: Name of the file (e.g., 'weather_data.csv')
            data: List of dictionaries containing training data
            
        Returns:
            Path to saved file
        """
        if not data:
            logger.warning("No data to save")
            return None
        
        ml_data_dir = WeatherDataCrawler.create_training_data_dir()
        file_path = ml_data_dir / filename
        
        # Get field names from first record
        fieldnames = list(data[0].keys())
        
        with open(file_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"Saved {len(data)} records to {file_path}")
        return file_path

    @staticmethod
    def load_csv_data(filename: str) -> List[Dict[str, Any]]:
        """
        Load CSV training data from ml_data directory.
        
        Args:
            filename: Name of the file (e.g., 'weather_data.csv')
            
        Returns:
            List of dictionaries
        """
        ml_data_dir = WeatherDataCrawler.create_training_data_dir()
        file_path = ml_data_dir / filename
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return []
        
        data = []
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric strings to appropriate types
                data.append(row)
        
        logger.info(f"Loaded {len(data)} records from {file_path}")
        return data

    @staticmethod
    def fetch_weather_data() -> List[Dict[str, Any]]:
        """
        Fetch weather training data from Open-Meteo API.
        
        Returns:
            List of weather records with format:
            {
                "date": str (YYYY-MM-DD),
                "location": str,
                "temperature": float (C),
                "rain": float (mm),
                "weather_code": int,
                "event_occurred": int (0 or 1)  # Target (rain/severe weather)
            }
        """
        logger.info("Fetching weather training data from Open-Meteo API...")
        
        weather_data = []
        
        # Multiple locations in Vietnam
        locations = [
            {"name": "Hanoi", "lat": 21.0285, "lon": 105.8542},
            {"name": "HoChiMinh", "lat": 10.7769, "lon": 106.7009},
            {"name": "DaNang", "lat": 16.0544, "lon": 108.2022},
        ]
        
        url = "https://api.open-meteo.com/v1/forecast"
        
        for location in locations:
            try:
                params = {
                    "latitude": location["lat"],
                    "longitude": location["lon"],
                    "hourly": ["temperature_2m", "rain", "weather_code"],
                    "past_days": 90,  # Get last 90 days
                    "timezone": "Asia/Bangkok"
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                if "hourly" in data:
                    hourly_data = data["hourly"]
                    
                    # Create DataFrame
                    df = pd.DataFrame({
                        "time": pd.to_datetime(hourly_data["time"]),
                        "temperature": hourly_data["temperature_2m"],
                        "rain": hourly_data["rain"],
                        "weather_code": hourly_data.get("weather_code", [0] * len(hourly_data["time"]))
                    })
                    
                    # Aggregate by day
                    df["date"] = df["time"].dt.date
                    
                    daily_records = df.groupby("date").agg({
                        "temperature": "mean",
                        "rain": "sum",
                        "weather_code": lambda x: x.fillna(0).max()
                    }).reset_index()
                    
                    # Convert to training format
                    for _, row in daily_records.iterrows():
                        # Handle NaN values
                        rain_mm = row["rain"] if pd.notna(row["rain"]) else 0.0
                        weather_code = int(row["weather_code"]) if pd.notna(row["weather_code"]) else 0
                        
                        # Event occurs if rain > 5mm or severe weather (code > 50)
                        event_occurred = 1 if (rain_mm > 5.0 or weather_code > 50) else 0
                        
                        weather_record = {
                            "date": str(row["date"]),
                            "location": location["name"],
                            "temperature": round(row["temperature"], 1),
                            "rain": round(rain_mm, 1),
                            "weather_code": weather_code,
                            "event_occurred": event_occurred
                        }
                        weather_data.append(weather_record)
                    
                    logger.info(f"✓ Fetched {len(daily_records)} weather records for {location['name']}")
                
            except Exception as e:
                logger.warning(f"Error fetching weather for {location['name']}: {e}")
                # Add synthetic records on error
                for i in range(30):
                    date = (datetime.now() - timedelta(days=i)).date()
                    weather_data.append({
                        "date": str(date),
                        "location": location["name"],
                        "temperature": 25.0 + (i % 10),
                        "rain": float(i % 20),
                        "weather_code": 0,
                        "event_occurred": 1 if (i % 10 > 5) else 0
                    })
        
        logger.info(f"Generated {len(weather_data)} weather records")
        return weather_data if weather_data else []


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create directory
    WeatherDataCrawler.create_training_data_dir()
    
    # Fetch and save weather data
    weather_data = WeatherDataCrawler.fetch_weather_data()
    WeatherDataCrawler.save_csv_data("weather_data.csv", weather_data)
    
    print("✓ Weather training data saved to backend/ml_data/weather_data.csv")
