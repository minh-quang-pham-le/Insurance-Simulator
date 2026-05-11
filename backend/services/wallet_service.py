"""Wallet service — balance management, transactions, atomic operations."""
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from models.wallet import Wallet, WalletTransaction
from models.enums import TransactionType
from models.user import User
from models.enums import KycStatus

logger = logging.getLogger(__name__)


class WalletService:
    """Business logic for wallet operations with atomic transactions."""

    @staticmethod
    def get_balance(user_id: UUID, db: Session) -> dict:
        """
        Get user's wallet balance.

        Args:
            user_id: User's UUID
            db: Database session

        Returns:
            Dict with balance and currency

        Raises:
            ValueError: If user/wallet not found
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if not wallet:
            raise ValueError("Wallet not found")

        logger.info(f"Balance retrieved for user {user.email}: {wallet.balance} {wallet.currency}")
        return {
            "user_id": str(user_id),
            "balance": float(wallet.balance),
            "currency": wallet.currency,
        }

    @staticmethod
    async def top_up(
        user_id: UUID,
        amount: Decimal,
        db: Session,
    ) -> dict:
        """
        Top up user's wallet balance.
        
        Requires: KYC VERIFIED status
        
        Steps:
        1. Verify KYC status = VERIFIED
        2. Validate amount > 0
        3. Lock wallet row with SELECT ... FOR UPDATE
        4. Add balance
        5. Create WalletTransaction (type=TOP_UP, no policy_id/claim_id)
        
        Args:
            user_id: User's UUID
            amount: Amount to top up (in SimCoin)
            db: Database session
        
        Returns:
            Dict with updated balance and transaction info
        
        Raises:
            ValueError: If KYC not verified, amount invalid, or wallet not found
        """
        # Check KYC status
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        if user.kyc_status != KycStatus.VERIFIED:
            logger.warning(f"Top-up blocked: user {user.email} KYC status is {user.kyc_status}")
            raise ValueError(f"KYC verification required. Current status: {user.kyc_status}")

        # Validate amount
        if amount <= 0:
            raise ValueError("Top-up amount must be positive")

        # Lock wallet row
        wallet = (
            db.query(Wallet)
            .filter(Wallet.user_id == user_id)
            .with_for_update()
            .first()
        )

        if not wallet:
            raise ValueError("Wallet not found")

        # Update balance
        old_balance = wallet.balance
        wallet.balance += amount
        db.flush()

        # Create transaction record
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type=TransactionType.TOP_UP,
            amount=amount,
            balance_after=wallet.balance,
            policy_id=None,
            claim_id=None,
            description=f"Top-up {amount} {wallet.currency}",
        )
        db.add(transaction)
        db.commit()
        db.refresh(wallet)

        logger.info(
            f"Top-up successful for user {user.email}: "
            f"{old_balance} + {amount} = {wallet.balance}"
        )

        return {
            "user_id": str(user_id),
            "transaction_id": str(transaction.id),
            "transaction_type": transaction.transaction_type,
            "amount": float(amount),
            "balance_before": float(old_balance),
            "balance_after": float(wallet.balance),
            "currency": wallet.currency,
            "timestamp": transaction.created_at.isoformat(),
        }

    @staticmethod
    async def deduct(
        user_id: UUID,
        amount: Decimal,
        policy_id: Optional[UUID] = None,
        claim_id: Optional[UUID] = None,
        description: Optional[str] = None,
        db: Session = None,
    ) -> dict:
        """
        Deduct from wallet (for policy purchase, claim payout, etc).
        
        Steps:
        1. Lock wallet row with SELECT ... FOR UPDATE
        2. Check balance >= amount
        3. Deduct balance
        4. Create WalletTransaction with policy_id or claim_id
        
        Args:
            user_id: User's UUID
            amount: Amount to deduct
            policy_id: Optional policy ID (for policy purchases)
            claim_id: Optional claim ID (for claim payouts)
            description: Transaction description
            db: Database session
        
        Returns:
            Dict with transaction info
        
        Raises:
            ValueError: If insufficient balance, amount invalid, or wallet not found
        """
        # Validate amount
        if amount <= 0:
            raise ValueError("Deduct amount must be positive")

        # Lock wallet row
        wallet = (
            db.query(Wallet)
            .filter(Wallet.user_id == user_id)
            .with_for_update()
            .first()
        )

        if not wallet:
            raise ValueError("Wallet not found")

        # Check sufficient balance
        if wallet.balance < amount:
            logger.warning(
                f"Insufficient balance for user {user_id}: "
                f"balance={wallet.balance}, requested={amount}"
            )
            raise ValueError(
                f"Insufficient balance. Available: {wallet.balance}, Required: {amount}"
            )

        # Deduct balance
        old_balance = wallet.balance
        wallet.balance -= amount
        db.flush()

        # Determine transaction type
        if policy_id:
            transaction_type = TransactionType.PURCHASE
        elif claim_id:
            transaction_type = TransactionType.CLAIM_PAYOUT
        else:
            transaction_type = TransactionType.DEDUCT

        # Create transaction record
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=wallet.balance,
            policy_id=policy_id,
            claim_id=claim_id,
            description=description or f"Deduct {amount}",
        )
        db.add(transaction)
        db.commit()
        db.refresh(wallet)

        logger.info(
            f"Deduction successful for user {user_id}: "
            f"{old_balance} - {amount} = {wallet.balance}"
        )

        return {
            "user_id": str(user_id),
            "transaction_id": str(transaction.id),
            "transaction_type": transaction.transaction_type,
            "amount": float(amount),
            "balance_before": float(old_balance),
            "balance_after": float(wallet.balance),
            "currency": wallet.currency,
            "timestamp": transaction.created_at.isoformat(),
        }

    @staticmethod
    async def credit(
        user_id: UUID,
        amount: Decimal,
        claim_id: Optional[UUID] = None,
        description: Optional[str] = None,
        db: Session = None,
    ) -> dict:
        """
        Credit to wallet (for claim payouts, refunds, etc).
        
        Steps:
        1. Lock wallet row with SELECT ... FOR UPDATE
        2. Add to balance
        3. Create WalletTransaction with claim_id
        
        Args:
            user_id: User's UUID
            amount: Amount to credit
            claim_id: Optional claim ID (for claim credit)
            description: Transaction description
            db: Database session
        
        Returns:
            Dict with transaction info
        
        Raises:
            ValueError: If amount invalid or wallet not found
        """
        # Validate amount
        if amount <= 0:
            raise ValueError("Credit amount must be positive")

        # Lock wallet row
        wallet = (
            db.query(Wallet)
            .filter(Wallet.user_id == user_id)
            .with_for_update()
            .first()
        )

        if not wallet:
            raise ValueError("Wallet not found")

        # Add to balance
        old_balance = wallet.balance
        wallet.balance += amount
        db.flush()

        # Determine transaction type
        transaction_type = TransactionType.CLAIM_PAYOUT if claim_id else TransactionType.CREDIT

        # Create transaction record
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=wallet.balance,
            policy_id=None,
            claim_id=claim_id,
            description=description or f"Credit {amount}",
        )
        db.add(transaction)
        db.commit()
        db.refresh(wallet)

        logger.info(
            f"Credit successful for user {user_id}: "
            f"{old_balance} + {amount} = {wallet.balance}"
        )

        return {
            "user_id": str(user_id),
            "transaction_id": str(transaction.id),
            "transaction_type": transaction.transaction_type,
            "amount": float(amount),
            "balance_before": float(old_balance),
            "balance_after": float(wallet.balance),
            "currency": wallet.currency,
            "timestamp": transaction.created_at.isoformat(),
        }

    @staticmethod
    def get_transactions(
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        db: Session = None,
    ) -> dict:
        """
        Get paginated transaction history for user.
        
        Args:
            user_id: User's UUID
            skip: Number of transactions to skip (pagination)
            limit: Number of transactions to return (default 50, max 100)
            db: Database session
        
        Returns:
            Dict with transactions list and metadata
        
        Raises:
            ValueError: If user/wallet not found
        """
        # Validate limit
        limit = min(limit, 100)

        # Check wallet exists
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if not wallet:
            raise ValueError("Wallet not found")

        # Get total count
        total = db.query(WalletTransaction).filter(
            WalletTransaction.wallet_id == wallet.id
        ).count()

        # Get paginated transactions (newest first)
        transactions = (
            db.query(WalletTransaction)
            .filter(WalletTransaction.wallet_id == wallet.id)
            .order_by(WalletTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {
            "user_id": str(user_id),
            "transactions": [
                {
                    "id": str(t.id),
                    "type": t.transaction_type,
                    "amount": float(t.amount),
                    "balance_after": float(t.balance_after),
                    "policy_id": str(t.policy_id) if t.policy_id else None,
                    "claim_id": str(t.claim_id) if t.claim_id else None,
                    "description": t.description,
                    "created_at": t.created_at.isoformat(),
                }
                for t in transactions
            ],
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total,
            },
        }


# Instantiate service for dependency injection
wallet_service = WalletService()
