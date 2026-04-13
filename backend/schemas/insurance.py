"""Insurance product schemas — catalog CRUD."""
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from models.enums import ProductCategory


class ProductCreate(BaseModel):
    name: str = Field(..., max_length=200)
    category: ProductCategory
    description: str
    short_description: Optional[str] = Field(None, max_length=300)
    icon_url: Optional[str] = Field(None, max_length=500)
    base_payout: Decimal = Field(..., gt=0)
    min_duration_days: int = Field(..., gt=0)
    max_duration_days: int = Field(..., gt=0)
    risk_margin: Decimal = Field(default=Decimal("0.25"), ge=0, le=1)
    parameters_schema: Dict[str, Any]
    trigger_conditions: Dict[str, Any]


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=300)
    icon_url: Optional[str] = Field(None, max_length=500)
    base_payout: Optional[Decimal] = Field(None, gt=0)
    min_duration_days: Optional[int] = Field(None, gt=0)
    max_duration_days: Optional[int] = Field(None, gt=0)
    risk_margin: Optional[Decimal] = Field(None, ge=0, le=1)
    parameters_schema: Optional[Dict[str, Any]] = None
    trigger_conditions: Optional[Dict[str, Any]] = None


class ProductStatusUpdate(BaseModel):
    is_active: bool


class ProductResponse(BaseModel):
    id: UUID
    name: str
    category: ProductCategory
    description: str
    short_description: Optional[str] = None
    icon_url: Optional[str] = None
    base_payout: Decimal
    min_duration_days: int
    max_duration_days: int
    risk_margin: Decimal
    parameters_schema: Dict[str, Any]
    trigger_conditions: Dict[str, Any]
    is_active: bool
    created_by: Optional[UUID] = None
    created_at: datetime
    risk_score: Optional[float] = None

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
