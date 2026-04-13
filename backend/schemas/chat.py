"""Chat schemas — AI chatbot messages and sessions."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[UUID] = None
    context_product_id: Optional[UUID] = None


class ChatMessageResponse(BaseModel):
    session_id: UUID
    role: str
    content: str
    timestamp: datetime


class ChatSessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    context_product_id: Optional[UUID] = None
    messages: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionListResponse(BaseModel):
    sessions: List[ChatSessionResponse]
    total: int
