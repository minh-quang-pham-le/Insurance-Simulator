"""Chatbot router — AI insurance advisor endpoints."""
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
from middleware.auth import get_current_user
from models.user import User
from schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionResponse,
    ChatSessionListResponse,
)
from services import chatbot_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chatbot"])


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send a message to the AI insurance advisor and get a response.
    Optionally provide a session_id to continue an existing conversation,
    and context_product_id for product-specific advice.
    """
    result = await chatbot_service.send_message(
        db=db,
        user=current_user,
        message=request.message,
        session_id=request.session_id,
        context_product_id=request.context_product_id,
    )
    return result


@router.get("/sessions", response_model=ChatSessionListResponse)
async def list_chat_sessions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's chat sessions."""
    sessions, total = chatbot_service.get_sessions(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return {
        "sessions": sessions,
        "total": total,
    }


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific chat session with full message history."""
    session = chatbot_service.get_session_by_id(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )
    return session
