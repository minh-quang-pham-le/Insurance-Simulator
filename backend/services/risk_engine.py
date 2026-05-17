"""Risk calculation engine using ML models for premium estimation."""
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np
from services.ml_models import FlightDelayModel, WeatherModel

logger = logging.getLogger(__name__)


class RiskEngine:
    """Engine for calculating insurance premiums using ML models."""
    
    def __init__(self):
        """Initialize risk engine with ML models."""
        self.flight_delay_model: Optional[FlightDelayModel] = None
        self.weather_model: Optional[WeatherModel] = None
        self.models_loaded = False
        self._load_models()
    
    def _load_models(self):
        """
        Load pre-trained ML models from disk.
        
        Models are expected in backend/ml_models/{product}.joblib format.
        Logs warnings if models are not found but continues with fallback.
        """
        models_dir = Path(__file__).parent.parent / "ml_models"
        
        # Load Flight Delay Model
        flight_model_path = models_dir / "flight_delay.joblib"
        self.flight_delay_model = FlightDelayModel()
        if self.flight_delay_model.load(flight_model_path):
            logger.info("✓ FlightDelayModel loaded successfully")
        else:
            logger.warning(f"⚠ FlightDelayModel not found at {flight_model_path}, will use fallback formula")
            self.flight_delay_model = None
        
        # Load Weather Model
        weather_model_path = models_dir / "weather.joblib"
        self.weather_model = WeatherModel()
        if self.weather_model.load(weather_model_path):
            logger.info("✓ WeatherModel loaded successfully")
        else:
            logger.warning(f"⚠ WeatherModel not found at {weather_model_path}, will use fallback formula")
            self.weather_model = None
        
        self.models_loaded = (self.flight_delay_model is not None and self.weather_model is not None)
    
    def get_model_stats(self) -> Dict:
        """
        Get statistics about loaded models.
        
        Returns:
            Dict with model status and metrics
        """
        stats = {
            "flight_delay": None,
            "weather": None,
            "models_available": self.models_loaded
        }
        
        if self.flight_delay_model:
            stats["flight_delay"] = {
                "name": self.flight_delay_model.name,
                "accuracy": self.flight_delay_model.accuracy,
                "precision": self.flight_delay_model.precision,
                "recall": self.flight_delay_model.recall,
                "f1": self.flight_delay_model.f1,
                "feature_names": self.flight_delay_model.feature_names
            }
        
        if self.weather_model:
            stats["weather"] = {
                "name": self.weather_model.name,
                "accuracy": self.weather_model.accuracy,
                "precision": self.weather_model.precision,
                "recall": self.weather_model.recall,
                "f1": self.weather_model.f1,
                "feature_names": self.weather_model.feature_names
            }
        
        return stats
    
    def calculate_premium(
        self,
        product_id: str,
        base_price: float,
        features: Dict
    ) -> Dict:
        """
        Calculate insurance premium using ML model probability.
        
        Formula:
            1. Get event probability from ML model: P(event=1) ∈ [0.0, 1.0]
            2. Calculate risk multiplier: risk_multiplier = 0.5 + (probability × 1.5)
               - Result range: [0.5, 2.0]
            3. Final premium = base_price × risk_multiplier
        
        If model unavailable, fallback to fixed multiplier (1.0).
        
        Args:
            product_id: Insurance product ID ("flight_delay", "weather_event", etc.)
            base_price: Base premium price before risk adjustment
            features: Dict with required features for the model
            
        Returns:
            Dict containing:
                - event_probability: Probability [0.0, 1.0]
                - event_probability_pct: Probability as percentage [0, 100]
                - risk_multiplier: Risk multiplier [0.5, 2.0]
                - final_premium: Calculated premium (base_price × risk_multiplier)
                - model_used: Boolean indicating if ML model was used
        """
        event_probability = 0.5  # Default fallback
        model_used = False
        
        try:
            # Extract features for the model
            if product_id == "flight_delay" and self.flight_delay_model:
                # Expected features: duration, departure_delay, arrival_delay
                X = np.array([[
                    features.get("duration", 0),
                    features.get("departure_delay", 0),
                    features.get("arrival_delay", 0)
                ]])
                event_probability = self.flight_delay_model.predict_proba(X)[0]
                model_used = True
                logger.debug(f"Flight Delay: P={event_probability:.4f}")
            
            elif product_id == "weather_event" and self.weather_model:
                # Expected features: temperature, rain, weather_code
                X = np.array([[
                    features.get("temperature", 20),
                    features.get("rain", 0),
                    features.get("weather_code", 0)
                ]])
                event_probability = self.weather_model.predict_proba(X)[0]
                model_used = True
                logger.debug(f"Weather Event: P={event_probability:.4f}")
            
            else:
                logger.warning(f"Product '{product_id}' or model not available, using fallback")
        
        except Exception as e:
            logger.error(f"Error calculating probability: {e}, using fallback")
        
        # Calculate risk multiplier: 0.5 + (probability × 1.5)
        # Range: [0.5, 2.0]
        risk_multiplier = 0.5 + (event_probability * 1.5)
        
        # Calculate final premium
        final_premium = base_price * risk_multiplier
        
        return {
            "event_probability": float(event_probability),
            "event_probability_pct": float(event_probability * 100),
            "risk_multiplier": float(risk_multiplier),
            "final_premium": float(final_premium),
            "model_used": model_used
        }
    
    def get_risk_profile(self, product_id: str, features: Dict) -> Dict:
        """
        Get detailed risk profile for a given product and features.
        
        Args:
            product_id: Insurance product ID
            features: Feature dict for the model
            
        Returns:
            Dict with risk profile details
        """
        premium_calc = self.calculate_premium(product_id, 100, features)  # Use 100 as base for profile
        
        profile = {
            "product_id": product_id,
            "event_probability_pct": premium_calc["event_probability_pct"],
            "risk_level": self._get_risk_level(premium_calc["event_probability"]),
            "risk_multiplier": premium_calc["risk_multiplier"],
            "model_used": premium_calc["model_used"]
        }
        
        return profile
    
    @staticmethod
    def _get_risk_level(probability: float) -> str:
        """
        Categorize risk level based on probability.
        
        Args:
            probability: Event probability [0.0, 1.0]
            
        Returns:
            Risk level: "low", "medium", "high", or "very_high"
        """
        if probability < 0.25:
            return "low"
        elif probability < 0.50:
            return "medium"
        elif probability < 0.75:
            return "high"
        else:
            return "very_high"


# Global instance
_risk_engine: Optional[RiskEngine] = None


def get_risk_engine() -> RiskEngine:
    """Get or create global RiskEngine instance."""
    global _risk_engine
    if _risk_engine is None:
        _risk_engine = RiskEngine()
    return _risk_engine
