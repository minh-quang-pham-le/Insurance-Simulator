"""Simulation router — trigger explorer endpoints."""
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
from middleware.auth import get_current_user
from models.user import User
from models.insurance_product import InsuranceProduct
from schemas.simulation import (
    SimulationConfigResponse,
    TriggerCheckRequest,
    TriggerCheckResponse,
    SimulationLogRequest,
)
from services import simulation_engine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Simulation"])


def _get_product(db: Session, product_id: UUID) -> InsuranceProduct:
    """Helper to fetch product or raise 404."""
    product = db.query(InsuranceProduct).filter(
        InsuranceProduct.id == product_id
    ).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance product not found",
        )
    return product


@router.get("/products/{product_id}/config")
async def get_simulation_config(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get slider configuration and trigger rules for a product's simulation.
    Returns slider ranges, thresholds, and rule descriptions.
    """
    product = _get_product(db, product_id)
    return simulation_engine.get_simulation_config(product)


@router.post("/products/{product_id}/check-trigger", response_model=TriggerCheckResponse)
async def check_trigger(
    product_id: UUID,
    request: TriggerCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Check if the given parameter values would trigger a claim.
    Returns which rules triggered and the resulting payout amount.
    """
    product = _get_product(db, product_id)
    return simulation_engine.check_trigger(product, request.parameters)


@router.post("/products/{product_id}/log")
async def log_simulation(
    product_id: UUID,
    request: SimulationLogRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Log a simulation session for analytics."""
    product = _get_product(db, product_id)
    session = simulation_engine.log_session(
        db=db,
        user_id=current_user.id,
        product_id=product.id,
        input_parameters=request.input_parameters,
        triggers_activated=request.triggers_activated,
    )
    return {"session_id": str(session.id), "status": "logged"}
