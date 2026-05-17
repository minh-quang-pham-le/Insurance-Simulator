"""Auth API router — registration, login, token refresh, KYC submission."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
from middleware.auth import get_current_user, create_access_token, create_refresh_token
from services.auth_service import auth_service
from schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    UserResponse,
    KycSubmitRequest,
    KycStatusResponse,
    KycSubmitResponse,
)
from models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    req: RegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user account.
    
    Returns:
        - 201 Created: UserResponse with kyc_status = NOT_SUBMITTED
        - 400 Bad Request: Email already exists or password weak
        - 422 Unprocessable Entity: Validation error
    """
    try:
        user = await auth_service.register(
            email=req.email,
            password=req.password,
            full_name=req.full_name,
            db=db,
        )
        return user
    except ValueError as e:
        logger.warning(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    req: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Login with email and password.
    
    Returns:
        - 200 OK: TokenResponse with access_token and refresh_token
        - 401 Unauthorized: Invalid email or password
        - 422 Unprocessable Entity: Validation error
    """
    user = await auth_service.authenticate(
        email=req.email,
        password=req.password,
        db=db,
    )
    
    if not user:
        logger.warning(f"Login failed for email: {req.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    tokens = auth_service.create_tokens(user)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    req: RefreshRequest,
    db: Session = Depends(get_db),
):
    """
    Refresh access token using refresh token.
    
    Returns:
        - 200 OK: TokenResponse with new access_token
        - 401 Unauthorized: Invalid or expired refresh token
    """
    try:
        access_token = auth_service.refresh_access_token(
            refresh_token=req.refresh_token,
            db=db,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=req.refresh_token,
        )
    except ValueError as e:
        logger.warning(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """
    Get current user profile.
    
    Returns:
        - 200 OK: UserResponse with user's full profile including kyc_status
        - 401 Unauthorized: No valid JWT token
    """
    return user


@router.post("/kyc/submit", response_model=KycSubmitResponse)
async def submit_kyc(
    req: KycSubmitRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submit KYC verification.
    
    Returns:
        - 200 OK: KycSubmitResponse with kyc_status = PENDING
        - 400 Bad Request: Invalid phone number or other validation error
        - 401 Unauthorized: No valid JWT token
    """
    try:
        updated_user = await auth_service.submit_kyc(
            user_id=user.id,
            phone_number=req.phone_number,
            identity_details=req.identity_details,
            db=db,
        )
        return KycSubmitResponse(
            kyc_status=updated_user.kyc_status,
            message="KYC verification submitted for review",
        )
    except ValueError as e:
        logger.warning(f"KYC submission failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/kyc/status", response_model=KycStatusResponse)
async def get_kyc_status(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current user's KYC status.
    
    Returns:
        - 200 OK: KycStatusResponse with current kyc_status
        - 401 Unauthorized: No valid JWT token
    """
    try:
        kyc_status = await auth_service.get_kyc_status(
            user_id=user.id,
            db=db,
        )
        return KycStatusResponse(kyc_status=kyc_status)
    except ValueError as e:
        logger.warning(f"KYC status query failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
