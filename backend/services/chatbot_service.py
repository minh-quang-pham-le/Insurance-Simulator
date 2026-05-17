"""Chatbot service — Gemini 2.0 Flash integration for insurance advisory."""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from config.settings import settings
from models.chat_session import ChatSession
from models.insurance_product import InsuranceProduct
from models.policy import Policy
from models.risk_data import RiskData
from models.user import User
from models.enums import PolicyStatus, ProductCategory

logger = logging.getLogger(__name__)

# Gemini client (lazy init)
_genai_model = None


def _get_genai_model():
    """Lazy-initialize Gemini model."""
    global _genai_model
    if _genai_model is not None:
        return _genai_model

    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not configured, chatbot will use fallback")
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _genai_model = genai.GenerativeModel("gemini-2.0-flash")
        logger.info("Gemini 2.0 Flash model initialized")
        return _genai_model
    except Exception as e:
        logger.error(f"Failed to initialize Gemini model: {e}")
        return None


def _build_system_prompt(
    db: Session,
    user: User,
    product: Optional[InsuranceProduct] = None,
) -> str:
    """Build context-rich system prompt for the chatbot."""
    # Get product catalog summary
    products = db.query(InsuranceProduct).filter(
        InsuranceProduct.is_active == True
    ).all()
    catalog_lines = []
    for p in products:
        catalog_lines.append(
            f"- {p.name} ({p.category.value}): {p.short_description or p.description[:100]}. "
            f"Base payout: {p.base_payout} SC, Duration: {p.min_duration_days}-{p.max_duration_days} days"
        )
    catalog_summary = "\n".join(catalog_lines) if catalog_lines else "No products available"

    # Get user's active policies (with joinedload to avoid N+1)
    active_policies = db.query(Policy).options(
        joinedload(Policy.product)
    ).filter(
        Policy.user_id == user.id,
        Policy.status == PolicyStatus.ACTIVE,
    ).all()
    if active_policies:
        policy_lines = []
        for pol in active_policies:
            prod_name = pol.product.name if pol.product else "Unknown"
            policy_lines.append(
                f"- {prod_name}: premium {pol.premium_paid} SC, payout {pol.payout_amount} SC, "
                f"expires {pol.end_date.strftime('%Y-%m-%d')}"
            )
        policies_summary = "\n".join(policy_lines)
    else:
        policies_summary = "No active policies"

    # Get risk stats for current product
    risk_info = ""
    if product:
        risk_count = db.query(RiskData).filter(
            RiskData.product_category == product.category
        ).count()
        risk_info = (
            f"\nCurrently viewing: {product.name}\n"
            f"Category: {product.category.value}\n"
            f"Description: {product.description}\n"
            f"Base payout: {product.base_payout} SC\n"
            f"Historical risk events in database: {risk_count}\n"
        )

    system_prompt = f"""You are an insurance advisor for the Insurance Simulator platform.
Help users understand micro-insurance products and make informed decisions.

Available products:
{catalog_summary}

User's existing policies:
{policies_summary}
{risk_info}
Rules:
- Be educational — explain insurance concepts simply
- Be honest about risks vs. benefits
- Reference actual risk scores and probabilities when available
- Never guarantee outcomes
- Keep responses concise (under 150 words)
- You are advisory only — you cannot execute purchases or wallet operations
- Respond in the same language the user uses (Vietnamese or English)
- Use SimCoin (SC) as the currency unit"""

    return system_prompt


def _fallback_response(message: str, product: Optional[InsuranceProduct] = None) -> str:
    """Generate a basic fallback response when Gemini is unavailable."""
    msg_lower = message.lower()

    if product:
        if any(w in msg_lower for w in ["price", "premium", "cost", "gia", "phi"]):
            return (
                f"{product.name} has a base payout of {product.base_payout} SC. "
                f"The premium depends on your chosen parameters and risk factors. "
                f"Use the premium calculator on this page to get an exact quote."
            )
        if any(w in msg_lower for w in ["risk", "danger", "rui ro"]):
            return (
                f"The risk level for {product.name} depends on historical data and your specific parameters. "
                f"Check the Risk Gauge on this page for the current risk score."
            )
        if any(w in msg_lower for w in ["how", "work", "cach", "hoat dong"]):
            return (
                f"{product.name}: {product.description} "
                f"Duration range: {product.min_duration_days}-{product.max_duration_days} days."
            )
        return (
            f"You're viewing {product.name}. {product.short_description or product.description[:120]} "
            f"Feel free to ask about pricing, risk levels, or how this product works."
        )

    if any(w in msg_lower for w in ["hello", "hi", "hey", "xin chao", "chao"]):
        return (
            "Hello! I'm your insurance advisor. I can help you understand our micro-insurance products, "
            "compare options, and make informed decisions. What would you like to know?"
        )

    return (
        "I'm your AI insurance advisor. I can help you understand our products, "
        "explain risk levels, and guide you through purchasing decisions. "
        "Try asking about a specific product or visit a product detail page for context-aware advice."
    )


async def send_message(
    db: Session,
    user: User,
    message: str,
    session_id: Optional[UUID] = None,
    context_product_id: Optional[UUID] = None,
) -> Dict:
    """
    Send a message to the chatbot and get a response.

    Returns dict with session_id, role, content, timestamp.
    """
    # Resolve product context
    product = None
    if context_product_id:
        product = db.query(InsuranceProduct).filter(
            InsuranceProduct.id == context_product_id
        ).first()

    # Get or create session
    session = None
    if session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user.id,
        ).first()

    if not session:
        session = ChatSession(
            user_id=user.id,
            context_product_id=context_product_id,
            messages=[],
        )
        db.add(session)
        db.flush()

    # Update context product if changed
    if context_product_id and session.context_product_id != context_product_id:
        session.context_product_id = context_product_id

    # Append user message
    now = datetime.now(timezone.utc)
    user_msg = {
        "role": "user",
        "content": message,
        "timestamp": now.isoformat(),
    }
    messages = list(session.messages or [])
    messages.append(user_msg)

    # Generate response
    assistant_content = await _generate_response(db, user, messages, product)

    # Append assistant message
    response_time = datetime.now(timezone.utc)
    assistant_msg = {
        "role": "assistant",
        "content": assistant_content,
        "timestamp": response_time.isoformat(),
    }
    messages.append(assistant_msg)

    # Persist — force JSONB update by reassigning
    session.messages = messages
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "role": "assistant",
        "content": assistant_content,
        "timestamp": response_time,
    }


async def _generate_response(
    db: Session,
    user: User,
    messages: List[Dict],
    product: Optional[InsuranceProduct],
) -> str:
    """Generate AI response using Gemini or fallback."""
    model = _get_genai_model()

    if model is None:
        # Use fallback
        last_user_msg = messages[-1]["content"] if messages else ""
        return _fallback_response(last_user_msg, product)

    try:
        system_prompt = _build_system_prompt(db, user, product)

        # Create a model instance with system instruction (prevents prompt injection)
        import google.generativeai as genai
        scoped_model = genai.GenerativeModel(
            "gemini-2.0-flash",
            system_instruction=system_prompt,
        )

        # Build conversation history for Gemini
        chat_history = []
        for msg in messages[:-1]:  # Exclude the latest user message
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [msg["content"]]})

        chat = scoped_model.start_chat(history=chat_history)

        user_message = messages[-1]["content"]

        # Run blocking Gemini call in executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, chat.send_message, user_message)
        return response.text.strip()

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        last_user_msg = messages[-1]["content"] if messages else ""
        return _fallback_response(last_user_msg, product)


def get_sessions(
    db: Session,
    user_id: UUID,
    skip: int = 0,
    limit: int = 20,
) -> tuple:
    """Get user's chat sessions."""
    query = db.query(ChatSession).filter(ChatSession.user_id == user_id)
    total = query.count()
    sessions = (
        query.order_by(ChatSession.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return sessions, total


def get_session_by_id(
    db: Session,
    session_id: UUID,
    user_id: UUID,
) -> Optional[ChatSession]:
    """Get a specific chat session."""
    return db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id,
    ).first()
