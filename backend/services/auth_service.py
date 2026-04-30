"""Authentication service — registration, login, token management, KYC flow."""
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from models.user import User
from models.wallet import Wallet
from models.enums import UserRole, KycStatus
from middleware.auth import create_access_token, create_refresh_token
from jose import jwt, JWTError
from config.settings import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Business logic for authentication and KYC."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify plain password against hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    async def register(
        email: str,
        password: str,
        full_name: str,
        db: Session,
    ) -> User:
        """
        Register a new user.
        
        Steps:
        1. Check email uniqueness
        2. Hash password
        3. Create User and Wallet atomically
        
        Args:
            email: User email
            password: Plain password
            full_name: User's full name
            db: Database session
        
        Returns:
            Created User object
        
        Raises:
            ValueError: If email already exists or data invalid
        """
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == email.lower()).first()
        if existing_user:
            logger.warning(f"Registration failed: email already exists: {email}")
            raise ValueError("Email already registered")
        
        # Hash password
        hashed_password = AuthService.hash_password(password)
        
        # Create user (transaction handled by caller)
        user = User(
            email=email.lower(),
            password_hash=hashed_password,
            full_name=full_name,
            role=UserRole.USER,
            kyc_status=KycStatus.NOT_SUBMITTED,
        )
        db.add(user)
        db.flush()  # Flush to get user.id without committing
        
        # Create wallet for user
        wallet = Wallet(
            user_id=user.id,
            balance=0,
            currency="SC",
        )
        db.add(wallet)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User registered: {email}")
        return user
    
    @staticmethod
    async def authenticate(
        email: str,
        password: str,
        db: Session,
    ) -> Optional[User]:
        """
        Authenticate user by email and password.
        
        Args:
            email: User email
            password: Plain password
            db: Database session
        
        Returns:
            User object if valid, None otherwise
        """
        user = db.query(User).filter(User.email == email.lower()).first()
        
        if not user:
            logger.warning(f"Login failed: user not found: {email}")
            return None
        
        if not user.is_active:
            logger.warning(f"Login failed: user inactive: {email}")
            return None
        
        if not AuthService.verify_password(password, user.password_hash):
            logger.warning(f"Login failed: invalid password for: {email}")
            return None
        
        logger.info(f"User authenticated: {email}")
        return user
    
    @staticmethod
    def create_tokens(user: User) -> dict:
        """
        Create access and refresh tokens for user.
        
        Args:
            user: User object
        
        Returns:
            Dict with access_token and refresh_token
        """
        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    
    @staticmethod
    def refresh_access_token(refresh_token: str, db: Session) -> str:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Refresh JWT token
            db: Database session
        
        Returns:
            New access token
        
        Raises:
            ValueError: If refresh token invalid
        """
        try:
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"],
            )
            user_id: str = payload.get("sub")
            
            if user_id is None:
                raise ValueError("Invalid refresh token: missing 'sub'")
            
            # Get user
            user_uuid = UUID(user_id)
            user = db.query(User).filter(User.id == user_uuid).first()
            
            if not user or not user.is_active:
                raise ValueError("User not found or inactive")
            
            # Create new access token
            access_token = create_access_token(user)
            logger.info(f"Access token refreshed for user: {user.email}")
            return access_token
        
        except (JWTError, ValueError) as e:
            logger.warning(f"Token refresh failed: {e}")
            raise ValueError("Invalid refresh token")
    
    @staticmethod
    async def submit_kyc(
        user_id: UUID,
        phone_number: str,
        identity_details: Optional[str],
        db: Session,
    ) -> User:
        """
        Submit KYC verification.
        
        Args:
            user_id: User's UUID
            phone_number: Phone number
            identity_details: Optional identity details
            db: Database session
        
        Returns:
            Updated User object
        
        Raises:
            ValueError: If user not found or data invalid
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Validate KYC status - only allow submit when NOT_SUBMITTED or REJECTED
        if user.kyc_status == KycStatus.PENDING:
            raise ValueError("KYC already submitted and pending review")
        if user.kyc_status == KycStatus.VERIFIED:
            raise ValueError("KYC already verified")
        
        # Validate phone number is not empty
        if not phone_number or len(phone_number) < 10:
            raise ValueError("Phone number must be at least 10 characters")
        
        # Update KYC fields
        user.phone_number = phone_number
        user.kyc_status = KycStatus.PENDING
        user.kyc_submitted_at = datetime.now(timezone.utc)
        user.kyc_rejection_reason = None  # Clear any previous rejection reason
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"KYC submitted for user: {user.email}")
        return user
    
    @staticmethod
    async def get_kyc_status(user_id: UUID, db: Session) -> KycStatus:
        """
        Get user's KYC status.
        
        Args:
            user_id: User's UUID
            db: Database session
        
        Returns:
            KycStatus enum value
        
        Raises:
            ValueError: If user not found
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        return user.kyc_status
    
    @staticmethod
    async def review_kyc(
        user_id: UUID,
        action: str,
        rejection_reason: Optional[str],
        db: Session,
    ) -> User:
        """
        Admin reviews KYC submission.
        
        Args:
            user_id: User's UUID
            action: 'approve' or 'reject'
            rejection_reason: Reason for rejection (required if action='reject')
            db: Database session
        
        Returns:
            Updated User object
        
        Raises:
            ValueError: If user not found or invalid action
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        if action == "approve":
            user.kyc_status = KycStatus.VERIFIED
            user.kyc_rejection_reason = None
            logger.info(f"KYC approved for user: {user.email}")
        elif action == "reject":
            if not rejection_reason:
                raise ValueError("Rejection reason required")
            user.kyc_status = KycStatus.REJECTED
            user.kyc_rejection_reason = rejection_reason
            logger.info(f"KYC rejected for user: {user.email}")
        else:
            raise ValueError("Invalid action: must be 'approve' or 'reject'")
        
        db.commit()
        db.refresh(user)
        return user


# Singleton instance
auth_service = AuthService()
