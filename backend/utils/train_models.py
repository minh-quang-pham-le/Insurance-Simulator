"""ML model training utilities for insurance risk prediction."""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class RiskModel:
    """Base class for risk prediction models."""
    
    def __init__(self, name: str):
        self.name = name
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.accuracy = 0
        self.precision = 0
        self.recall = 0
        self.f1 = 0

    def fit(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2):
        """
        Train model with given features and labels.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target labels (n_samples,)
            test_size: Fraction of data to use for testing
        """
        raise NotImplementedError

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict probability of target class = 1.
        
        Args:
            X: Feature matrix
            
        Returns:
            Probability predictions [0.0, 1.0]
        """
        raise NotImplementedError

    def save(self, filepath: Path):
        """Save model to disk."""
        raise NotImplementedError

    def load(self, filepath: Path):
        """Load model from disk."""
        raise NotImplementedError


class FlightDelayModel(RiskModel):
    """Binary classification model for flight delay prediction."""
    
    def __init__(self):
        super().__init__("FlightDelayModel")
        self.model = LogisticRegression(max_iter=1000, random_state=42)

    def fit(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2):
        """Train flight delay model."""
        logger.info(f"Training {self.name}...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        self.accuracy = accuracy_score(y_test, y_pred)
        self.precision = precision_score(y_test, y_pred, zero_division=0)
        self.recall = recall_score(y_test, y_pred, zero_division=0)
        self.f1 = f1_score(y_test, y_pred, zero_division=0)
        
        logger.info(f"✓ {self.name} trained")
        logger.info(f"  Accuracy:  {self.accuracy:.4f}")
        logger.info(f"  Precision: {self.precision:.4f}")
        logger.info(f"  Recall:    {self.recall:.4f}")
        logger.info(f"  F1-Score:  {self.f1:.4f}")

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return probability of delay_occurred=1."""
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)[:, 1]

    def save(self, filepath: Path):
        """Save model to disk."""
        data = {
            "model": self.model,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "metrics": {
                "accuracy": self.accuracy,
                "precision": self.precision,
                "recall": self.recall,
                "f1": self.f1
            }
        }
        joblib.dump(data, filepath)
        logger.info(f"✓ Saved {self.name} to {filepath}")

    def load(self, filepath: Path):
        """Load model from disk."""
        if not filepath.exists():
            logger.warning(f"Model file not found: {filepath}")
            return False
        
        data = joblib.load(filepath)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.feature_names = data["feature_names"]
        self.accuracy = data["metrics"]["accuracy"]
        self.precision = data["metrics"]["precision"]
        self.recall = data["metrics"]["recall"]
        self.f1 = data["metrics"]["f1"]
        logger.info(f"✓ Loaded {self.name} from {filepath}")
        return True


class WeatherModel(RiskModel):
    """Binary classification model for weather event prediction."""
    
    def __init__(self):
        super().__init__("WeatherModel")
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)

    def fit(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2):
        """Train weather model."""
        logger.info(f"Training {self.name}...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # No scaling needed for RandomForest
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        self.accuracy = accuracy_score(y_test, y_pred)
        self.precision = precision_score(y_test, y_pred, zero_division=0)
        self.recall = recall_score(y_test, y_pred, zero_division=0)
        self.f1 = f1_score(y_test, y_pred, zero_division=0)
        
        logger.info(f"✓ {self.name} trained")
        logger.info(f"  Accuracy:  {self.accuracy:.4f}")
        logger.info(f"  Precision: {self.precision:.4f}")
        logger.info(f"  Recall:    {self.recall:.4f}")
        logger.info(f"  F1-Score:  {self.f1:.4f}")

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return probability of weather_event=1."""
        return self.model.predict_proba(X)[:, 1]

    def save(self, filepath: Path):
        """Save model to disk."""
        data = {
            "model": self.model,
            "feature_names": self.feature_names,
            "metrics": {
                "accuracy": self.accuracy,
                "precision": self.precision,
                "recall": self.recall,
                "f1": self.f1
            }
        }
        joblib.dump(data, filepath)
        logger.info(f"✓ Saved {self.name} to {filepath}")

    def load(self, filepath: Path):
        """Load model from disk."""
        if not filepath.exists():
            logger.warning(f"Model file not found: {filepath}")
            return False
        
        data = joblib.load(filepath)
        self.model = data["model"]
        self.feature_names = data["feature_names"]
        self.accuracy = data["metrics"]["accuracy"]
        self.precision = data["metrics"]["precision"]
        self.recall = data["metrics"]["recall"]
        self.f1 = data["metrics"]["f1"]
        logger.info(f"✓ Loaded {self.name} from {filepath}")
        return True


class ModelTrainer:
    """Utility for training and managing ML models."""
    
    @staticmethod
    def create_models_dir() -> Path:
        """Create backend/ml_models directory if it doesn't exist."""
        ml_models_dir = Path(__file__).parent.parent / "ml_models"
        ml_models_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Models directory: {ml_models_dir}")
        return ml_models_dir

    @staticmethod
    def create_data_dir() -> Path:
        """Create backend/ml_data directory."""
        ml_data_dir = Path(__file__).parent.parent / "ml_data"
        ml_data_dir.mkdir(parents=True, exist_ok=True)
        return ml_data_dir

    @staticmethod
    def prepare_flight_data(filepath: Path) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Prepare flight delay data for model training from CSV file.
        
        Args:
            filepath: Path to vietnam_airlines_flights.csv
            
        Returns:
            (X, y, feature_names)
        """
        df = pd.read_csv(filepath)
        
        if df.empty:
            raise ValueError("Flight data is empty")
        
        # Extract features from CSV columns
        X = df[[
            "distance",
            "speed",
            "altitude",
            "on_ground"
        ]].values
        
        y = df["delay_occurred"].values
        feature_names = ["distance", "speed", "altitude", "on_ground"]
        
        logger.info(f"Prepared flight data: {len(X)} samples, {X.shape[1]} features")
        return X, y, feature_names

    @staticmethod
    def prepare_weather_data(filepath: Path) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Prepare weather data for model training.
        
        Args:
            filepath: Path to weather_data.csv
            
        Returns:
            (X, y, feature_names)
        """
        df = pd.read_csv(filepath)
        
        if df.empty:
            raise ValueError("Weather data is empty")
        
        # Extract features
        X = df[[
            "temperature",
            "rain",
            "weather_code"
        ]].values
        
        y = df["event_occurred"].values
        feature_names = ["temperature", "rain", "weather_code"]
        
        logger.info(f"Prepared weather data: {len(X)} samples, {X.shape[1]} features")
        return X, y, feature_names

    @staticmethod
    def train_models():
        """
        Train all models from available training data.
        """
        logger.info("=" * 60)
        logger.info("Starting model training pipeline")
        logger.info("=" * 60)
        
        data_dir = ModelTrainer.create_data_dir()
        models_dir = ModelTrainer.create_models_dir()
        
        # Train Flight Delay Model
        flight_data_path = data_dir / "vietnam_airlines_flights.csv"
        if flight_data_path.exists():
            try:
                X_flight, y_flight, features_flight = ModelTrainer.prepare_flight_data(flight_data_path)
                
                model_flight = FlightDelayModel()
                model_flight.feature_names = features_flight
                model_flight.fit(X_flight, y_flight)
                
                model_flight.save(models_dir / "flight_delay.joblib")
            except Exception as e:
                logger.error(f"Error training flight delay model: {e}")
        else:
            logger.warning(f"Flight data not found: {flight_data_path}")
        
        # Train Weather Model
        weather_data_path = data_dir / "weather_data.csv"
        if weather_data_path.exists():
            try:
                X_weather, y_weather, features_weather = ModelTrainer.prepare_weather_data(weather_data_path)
                
                model_weather = WeatherModel()
                model_weather.feature_names = features_weather
                model_weather.fit(X_weather, y_weather)
                
                model_weather.save(models_dir / "weather.joblib")
            except Exception as e:
                logger.error(f"Error training weather model: {e}")
        else:
            logger.warning(f"Weather data not found: {weather_data_path}")
        
        logger.info("=" * 60)
        logger.info("Model training completed!")
        logger.info("=" * 60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ModelTrainer.train_models()
