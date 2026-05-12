"""Admin router for dashboard, metrics, and ML model management."""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from middleware.auth import get_current_user, require_admin
from models.user import User
from schemas.admin import DashboardMetrics, RiskAnalyticsResponse
from services.risk_engine import get_risk_engine
from seed.train_models import ModelTrainer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(lambda: None)  # Placeholder for DB dependency
):
    """
    Get admin dashboard metrics.
    
    Requires: admin role
    
    Returns:
        Dashboard metrics including totals and recent activity
    """
    # This would be implemented with actual DB queries
    logger.info(f"Admin {current_user.email} accessed dashboard")
    
    return DashboardMetrics(
        total_users=0,
        active_policies=0,
        pending_claims=0,
        total_revenue=0.0,
        claims_paid=0.0
    )


@router.get("/ml/model-stats")
async def get_ml_model_stats(
    current_user: User = Depends(require_admin)
):
    """
    Get ML model statistics and status.
    
    Requires: admin role
    
    Returns:
        Dict with model information:
        - flight_delay: FlightDelayModel metrics (accuracy, precision, recall, f1)
        - weather: WeatherModel metrics (accuracy, precision, recall, f1)
        - models_available: Boolean indicating if all models are loaded
    """
    try:
        risk_engine = get_risk_engine()
        stats = risk_engine.get_model_stats()
        
        logger.info(f"Admin {current_user.email} requested ML model stats")
        
        return {
            "status": "success",
            "data": stats,
            "models_available": stats["models_available"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting ML model stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve model statistics"
        )


@router.post("/ml/retrain")
async def retrain_ml_models(
    current_user: User = Depends(require_admin)
):
    """
    Trigger ML model retraining from data files.
    
    Requires: admin role
    
    Expected data files:
        - backend/ml_data/vietnam_airlines_flights.csv
        - backend/ml_data/weather_data.csv
    
    Returns:
        Dict with retraining status and results
    """
    try:
        logger.info(f"Admin {current_user.email} triggered ML model retraining")
        
        data_dir = ModelTrainer.get_data_dir()
        models_dir = ModelTrainer.get_models_dir()
        
        # Check if data files exist
        flight_data_path = data_dir / "vietnam_airlines_flights.csv"
        weather_data_path = data_dir / "weather_data.csv"
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "flight_delay": {"status": "pending"},
            "weather": {"status": "pending"}
        }
        
        # Retrain Flight Delay Model
        if flight_data_path.exists():
            try:
                logger.info("Retraining FlightDelayModel...")
                from services.ml_models import FlightDelayModel
                
                X_flight, y_flight, features_flight = ModelTrainer.prepare_flight_data(flight_data_path)
                
                model_flight = FlightDelayModel()
                model_flight.feature_names = features_flight
                model_flight.fit(X_flight, y_flight)
                
                model_flight.save(models_dir / "flight_delay.joblib")
                
                results["flight_delay"] = {
                    "status": "success",
                    "samples": len(X_flight),
                    "accuracy": float(model_flight.accuracy),
                    "precision": float(model_flight.precision),
                    "recall": float(model_flight.recall),
                    "f1": float(model_flight.f1)
                }
                logger.info("✓ FlightDelayModel retrained successfully")
            except Exception as e:
                logger.error(f"Error retraining FlightDelayModel: {e}")
                results["flight_delay"] = {
                    "status": "error",
                    "error": str(e)
                }
        else:
            results["flight_delay"] = {
                "status": "skipped",
                "reason": f"Data file not found: {flight_data_path}"
            }
        
        # Retrain Weather Model
        if weather_data_path.exists():
            try:
                logger.info("Retraining WeatherModel...")
                from services.ml_models import WeatherModel
                
                X_weather, y_weather, features_weather = ModelTrainer.prepare_weather_data(weather_data_path)
                
                model_weather = WeatherModel()
                model_weather.feature_names = features_weather
                model_weather.fit(X_weather, y_weather)
                
                model_weather.save(models_dir / "weather.joblib")
                
                results["weather"] = {
                    "status": "success",
                    "samples": len(X_weather),
                    "accuracy": float(model_weather.accuracy),
                    "precision": float(model_weather.precision),
                    "recall": float(model_weather.recall),
                    "f1": float(model_weather.f1)
                }
                logger.info("✓ WeatherModel retrained successfully")
            except Exception as e:
                logger.error(f"Error retraining WeatherModel: {e}")
                results["weather"] = {
                    "status": "error",
                    "error": str(e)
                }
        else:
            results["weather"] = {
                "status": "skipped",
                "reason": f"Data file not found: {weather_data_path}"
            }
        
        # Reload models in risk engine
        try:
            from services.risk_engine import _risk_engine
            if _risk_engine is not None:
                _risk_engine._load_models()
                logger.info("✓ Risk engine models reloaded")
                results["risk_engine_reloaded"] = True
        except Exception as e:
            logger.warning(f"Could not reload risk engine: {e}")
            results["risk_engine_reloaded"] = False
        
        return {
            "status": "success",
            "data": results
        }
    
    except Exception as e:
        logger.error(f"Error during ML model retraining: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retraining failed: {str(e)}"
        )


@router.get("/ml/risk-analytics", response_model=RiskAnalyticsResponse)
async def get_risk_analytics(
    current_user: User = Depends(require_admin)
):
    """
    Get risk analytics for admin dashboard.
    
    Requires: admin role
    
    Returns:
        Risk analytics including probability distributions and metrics
    """
    logger.info(f"Admin {current_user.email} requested risk analytics")
    
    return RiskAnalyticsResponse(
        total_policies=0,
        high_risk_count=0,
        average_risk_multiplier=1.0,
        ml_models_status="available"
    )
