"""Simulation schemas — trigger explorer config and checks."""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID


class SliderConfig(BaseModel):
    name: str
    label: str
    min_value: float
    max_value: float
    step: float
    default_value: float
    threshold: Optional[float] = None
    unit: Optional[str] = None


class TriggerRule(BaseModel):
    field: str
    operator: str
    threshold: Optional[float] = None
    value: Optional[Any] = None
    payout_multiplier: float
    description: Optional[str] = None


class SimulationConfigResponse(BaseModel):
    product_id: UUID
    product_name: str
    sliders: List[SliderConfig]
    trigger_rules: List[TriggerRule]
    base_payout: float
    is_manual: bool = False
    manual_info: Optional[Dict[str, Any]] = None


class TriggerCheckRequest(BaseModel):
    parameters: Dict[str, Any]


class TriggerCheckResponse(BaseModel):
    triggered: bool
    triggered_rules: List[Dict[str, Any]]
    payout_amount: float
    payout_multiplier: float


class SimulationLogRequest(BaseModel):
    input_parameters: Dict[str, Any]
    triggers_activated: Dict[str, Any]
