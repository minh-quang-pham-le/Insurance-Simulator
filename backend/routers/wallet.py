"""Wallet API router — balance, top-up, transaction history."""
import logging
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
from middleware.auth import get_current_user
from services.wallet_service import wallet_service
from schemas.wallet import (
    TopUpRequest,
    WalletResponse,
    TransactionResponse,
    TransactionListResponse,
)
from models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=WalletResponse)
async def get_balance(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current user's wallet balance.
    
    Returns:
        - 200 OK: WalletResponse with balance and currency
        - 401 Unauthorized: No valid JWT token
        - 404 Not Found: Wallet not found
    """
    try:
        balance_info = wallet_service.get_balance(user.id, db)
        return balance_info
    except ValueError as e:
        logger.warning(f"Get balance failed for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error getting balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get balance",
        )


@router.post("/topup", response_model=WalletResponse)
async def top_up(
    req: TopUpRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Top up wallet balance.
    
    **Requires:** KYC_VERIFIED status
    
    Returns:
        - 200 OK: WalletResponse with updated balance
        - 400 Bad Request: Invalid amount or KYC not verified
        - 401 Unauthorized: No valid JWT token
        - 403 Forbidden: KYC status is not VERIFIED
        - 404 Not Found: Wallet not found
        - 422 Unprocessable Entity: Validation error
    """
    try:
        # Validate amount
        if req.amount <= 0:
            logger.warning(f"Top-up failed: invalid amount {req.amount}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be positive",
            )

        result = await wallet_service.top_up(
            user_id=user.id,
            amount=Decimal(str(req.amount)),
            db=db,
        )
        # Return updated wallet for WalletResponse schema
        return wallet_service.get_balance(user.id, db)

    except ValueError as e:
        error_msg = str(e)
        logger.warning(f"Top-up validation error for user {user.id}: {error_msg}")

        # Check if it's KYC related
        if "KYC" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_msg,
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )

    except Exception as e:
        logger.error(f"Unexpected error during top-up: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Top-up failed",
        )


@router.get("/transactions", response_model=TransactionListResponse)
async def get_transactions(
    skip: int = 0,
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get paginated transaction history.
    
    Query parameters:
        - skip: Number of transactions to skip (default 0)
        - limit: Number of transactions to return (default 50, max 100)
    
    Returns:
        - 200 OK: TransactionListResponse with paginated transactions
        - 401 Unauthorized: No valid JWT token
        - 404 Not Found: Wallet not found
    """
    try:
        if skip < 0:
            raise ValueError("skip must be non-negative")
        if limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")

        result = wallet_service.get_transactions(
            user_id=user.id,
            skip=skip,
            limit=limit,
            db=db,
        )
        return result

    except ValueError as e:
        logger.warning(f"Get transactions validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Unexpected error getting transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transactions",
        )
