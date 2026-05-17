"""
Standalone ML model training script.

Usage:
    python -m seed.train_models

Loads training data from backend/ml_data/ and trains binary classification models.
Models are saved to backend/ml_models/ in joblib format.
"""
import logging
from pathlib import Path
from typing import Tuple, List
import numpy as np
import pandas as pd
from services.ml_models import FlightDelayModel, WeatherModel

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Utility for training and managing ML models."""
    
    @staticmethod
    def get_data_dir() -> Path:
        """Get path to ml_data directory."""
        ml_data_dir = Path(__file__).parent.parent / "ml_data"
        ml_data_dir.mkdir(parents=True, exist_ok=True)
        return ml_data_dir

    @staticmethod
    def get_models_dir() -> Path:
        """Get path to ml_models directory."""
        ml_models_dir = Path(__file__).parent.parent / "ml_models"
        ml_models_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Models directory: {ml_models_dir}")
        return ml_models_dir

    @staticmethod
    def prepare_flight_data(filepath: Path) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Prepare flight delay data for model training from CSV file.
        
        Extracts relevant columns from Vietnam Airlines flight data and calculates
        delay occurrence based on comparing actual vs. estimated times.
        
        Format expected:
            Departure Time, Estimated Departure, Arrival Time, Estimated Arrival,
            Duration Minutes, ...
        
        Args:
            filepath: Path to vietnam_airlines_flights.csv
            
        Returns:
            (X, y, feature_names) - Features, target labels, and feature names
        """
        df = pd.read_csv(filepath)
        
        if df.empty:
            raise ValueError("Flight data is empty")
        
        # Convert time columns to datetime
        df['Departure Time'] = pd.to_datetime(df['Departure Time'], errors='coerce')
        df['Estimated Departure'] = pd.to_datetime(df['Estimated Departure'], errors='coerce')
        df['Arrival Time'] = pd.to_datetime(df['Arrival Time'], errors='coerce')
        df['Estimated Arrival'] = pd.to_datetime(df['Estimated Arrival'], errors='coerce')
        
        # Calculate delays in minutes
        df['departure_delay'] = (df['Departure Time'] - df['Estimated Departure']).dt.total_seconds() / 60
        df['arrival_delay'] = (df['Arrival Time'] - df['Estimated Arrival']).dt.total_seconds() / 60
        
        # Convert duration to numeric
        df['duration'] = pd.to_numeric(df['Duration Minutes'], errors='coerce')
        
        # Create target: delay_occurred = 1 if either departure or arrival delay > 5 minutes
        df['delay_occurred'] = ((df['departure_delay'] > 5) | (df['arrival_delay'] > 5)).astype(int)
        
        # Extract features
        X = df[[
            'duration',
            'departure_delay',
            'arrival_delay'
        ]].values
        
        y = df['delay_occurred'].values
        
        # Remove rows with NaN values
        valid_mask = ~np.isnan(X).any(axis=1)
        X = X[valid_mask]
        y = y[valid_mask]
        
        feature_names = ['duration', 'departure_delay', 'arrival_delay']
        
        logger.info(f"Prepared flight data: {len(X)} samples, {X.shape[1]} features")
        return X, y, feature_names

    @staticmethod
    def prepare_weather_data(filepath: Path) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Prepare weather data for model training.
        
        Removes rows with NaN values in temperature column.
        
        Format expected:
            date, location, temperature, rain, weather_code, event_occurred
        
        Args:
            filepath: Path to weather_data.csv
            
        Returns:
            (X, y, feature_names)
        """
        df = pd.read_csv(filepath)
        
        if df.empty:
            raise ValueError("Weather data is empty")
        
        # Convert 'nan' string to actual NaN and handle numeric conversion
        df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
        df['rain'] = pd.to_numeric(df['rain'], errors='coerce')
        df['weather_code'] = pd.to_numeric(df['weather_code'], errors='coerce')
        df['event_occurred'] = pd.to_numeric(df['event_occurred'], errors='coerce')
        
        # Extract features
        X = df[[
            "temperature",
            "rain",
            "weather_code"
        ]].values
        
        y = df["event_occurred"].values
        
        # Remove rows with NaN values in features
        valid_mask = ~np.isnan(X).any(axis=1)
        X = X[valid_mask]
        y = y[valid_mask]
        
        feature_names = ["temperature", "rain", "weather_code"]
        
        logger.info(f"Prepared weather data: {len(X)} samples, {X.shape[1]} features")
        return X, y, feature_names

    @staticmethod
    def train_models():
        """
        Train all models from available training data.
        
        Processes:
        1. Flight Delay Model - from vietnam_airlines_flights.csv
        2. Weather Model - from weather_data.csv
        
        Saves trained models to backend/ml_models/ in joblib format.
        """
        logger.info("=" * 70)
        logger.info("Starting ML model training pipeline")
        logger.info("=" * 70)
        
        data_dir = ModelTrainer.get_data_dir()
        models_dir = ModelTrainer.get_models_dir()
        
        # Train Flight Delay Model
        flight_data_path = data_dir / "vietnam_airlines_flights.csv"
        if flight_data_path.exists():
            try:
                logger.info(f"\n[1/2] Loading flight data from: {flight_data_path}")
                X_flight, y_flight, features_flight = ModelTrainer.prepare_flight_data(flight_data_path)
                
                logger.info(f"Training FlightDelayModel with {len(X_flight)} samples...")
                model_flight = FlightDelayModel()
                model_flight.feature_names = features_flight
                model_flight.fit(X_flight, y_flight)
                
                model_flight.save(models_dir / "flight_delay.joblib")
                logger.info("✓ FlightDelayModel successfully trained and saved\n")
            except Exception as e:
                logger.error(f"✗ Error training flight delay model: {e}\n")
        else:
            logger.warning(f"⚠ Flight data not found: {flight_data_path}")
            logger.warning("  Please download/generate vietnam_airlines_flights.csv first\n")
        
        # Train Weather Model
        weather_data_path = data_dir / "weather_data.csv"
        if weather_data_path.exists():
            try:
                logger.info(f"[2/2] Loading weather data from: {weather_data_path}")
                X_weather, y_weather, features_weather = ModelTrainer.prepare_weather_data(weather_data_path)
                
                logger.info(f"Training WeatherModel with {len(X_weather)} samples...")
                model_weather = WeatherModel()
                model_weather.feature_names = features_weather
                model_weather.fit(X_weather, y_weather)
                
                model_weather.save(models_dir / "weather.joblib")
                logger.info("✓ WeatherModel successfully trained and saved\n")
            except Exception as e:
                logger.error(f"✗ Error training weather model: {e}\n")
        else:
            logger.warning(f"⚠ Weather data not found: {weather_data_path}")
            logger.warning("  Please generate weather_data.csv using crawl_data.py\n")
        
        logger.info("=" * 70)
        logger.info("Model training pipeline completed!")
        logger.info("=" * 70)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ModelTrainer.train_models()
