"""ML model classes for insurance risk prediction."""
import logging
from pathlib import Path
from typing import List
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

logger = logging.getLogger(__name__)


class BaseRiskModel:
    """Abstract base class for risk prediction models."""
    
    def __init__(self, name: str):
        """
        Initialize base model.
        
        Args:
            name: Model identifier (e.g., "FlightDelayModel", "WeatherModel")
        """
        self.name = name
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names: List[str] = []
        self.accuracy = 0.0
        self.precision = 0.0
        self.recall = 0.0
        self.f1 = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2):
        """
        Train model with given features and labels.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target labels (n_samples,)
            test_size: Fraction of data to use for testing
        """
        raise NotImplementedError("Subclasses must implement fit()")

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict probability of target class = 1.
        
        Args:
            X: Feature matrix
            
        Returns:
            Probability predictions ∈ [0.0, 1.0]
        """
        raise NotImplementedError("Subclasses must implement predict_proba()")

    def save(self, filepath: Path):
        """
        Save model to disk in joblib format.
        
        Args:
            filepath: Path to save model file
        """
        raise NotImplementedError("Subclasses must implement save()")

    def load(self, filepath: Path) -> bool:
        """
        Load model from disk.
        
        Args:
            filepath: Path to load model file
            
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement load()")


class FlightDelayModel(BaseRiskModel):
    """Binary classification model for flight delay prediction."""
    
    def __init__(self):
        """Initialize flight delay model with LogisticRegression."""
        super().__init__("FlightDelayModel")
        self.model = LogisticRegression(max_iter=1000, random_state=42)

    def fit(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2):
        """
        Train flight delay model.
        
        Args:
            X: Feature matrix
            y: Target labels
            test_size: Test set fraction
        """
        from sklearn.model_selection import train_test_split
        
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
        """
        Return probability of delay_occurred=1.
        
        Args:
            X: Feature matrix
            
        Returns:
            Probability array ∈ [0.0, 1.0]
        """
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

    def load(self, filepath: Path) -> bool:
        """Load model from disk."""
        if not filepath.exists():
            logger.warning(f"Model file not found: {filepath}")
            return False
        
        try:
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
        except Exception as e:
            logger.error(f"Error loading {self.name}: {e}")
            return False


class WeatherModel(BaseRiskModel):
    """Binary classification model for weather event prediction."""
    
    def __init__(self):
        """Initialize weather model with RandomForestClassifier."""
        super().__init__("WeatherModel")
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)

    def fit(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2):
        """
        Train weather model.
        
        Args:
            X: Feature matrix
            y: Target labels
            test_size: Test set fraction
        """
        from sklearn.model_selection import train_test_split
        
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
        """
        Return probability of weather_event=1.
        
        Args:
            X: Feature matrix
            
        Returns:
            Probability array ∈ [0.0, 1.0]
        """
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

    def load(self, filepath: Path) -> bool:
        """Load model from disk."""
        if not filepath.exists():
            logger.warning(f"Model file not found: {filepath}")
            return False
        
        try:
            data = joblib.load(filepath)
            self.model = data["model"]
            self.feature_names = data["feature_names"]
            self.accuracy = data["metrics"]["accuracy"]
            self.precision = data["metrics"]["precision"]
            self.recall = data["metrics"]["recall"]
            self.f1 = data["metrics"]["f1"]
            logger.info(f"✓ Loaded {self.name} from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading {self.name}: {e}")
            return False
