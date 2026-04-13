"""Wallet schemas — top-up, balance, transactions."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from models.enums import TransactionType


class TopUpRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, le=100000)


class WalletResponse(BaseModel):
    id: UUID
    user_id: UUID
    balance: Decimal
    currency: str

    model_config = {"from_attributes": True}


class TransactionResponse(BaseModel):
    id: UUID
    wallet_id: UUID
    type: TransactionType
    amount: Decimal
    balance_after: Decimal
    description: Optional[str] = None
    policy_id: Optional[UUID] = None
    claim_id: Optional[UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int
    page: int
    page_size: int
