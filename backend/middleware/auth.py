"""JWT authentication middleware and dependencies."""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config.database import get_db
from config.settings import settings
from models.user import User
from models.enums import UserRole

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency — extract and validate JWT from Authorization header.
    Returns the User object or raises 401 Unauthorized.
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("JWT payload missing 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    # Query user from database
    try:
        user_uuid = UUID(user_id)
        user = db.query(User).filter(User.id == user_uuid).first()
    except ValueError:
        logger.warning(f"Invalid user_id format in JWT: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    if user is None or not user.is_active:
        logger.warning(f"User not found or inactive: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    logger.info(f"User authenticated: {user.email}")
    return user


async def require_admin(
    user: User = Depends(get_current_user),
) -> User:
    """
    FastAPI dependency — enforce ADMIN role.
    Returns the User object or raises 403 Forbidden.
    """
    if user.role != UserRole.ADMIN:
        logger.warning(f"Admin access denied for user {user.email} (role: {user.role})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate JWT access token with 24-hour expiration.
    
    Token payload:
      - sub: user_id (UUID)
      - email: user email
      - role: user role (USER or ADMIN)
      - exp: expiration time
      - iat: issued at time
    """
    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm="HS256",
    )
    logger.info(f"Access token created for user {user.email}")
    return encoded_jwt


def create_refresh_token(user: User) -> str:
    """
    Generate JWT refresh token with 7-day expiration.
    
    Token payload:
      - sub: user_id (UUID)
      - exp: expiration time
      - iat: issued at time
    """
    expires_delta = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(timezone.utc) + expires_delta
    
    to_encode = {
        "sub": str(user.id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm="HS256",
    )
    logger.info(f"Refresh token created for user {user.email}")
    return encoded_jwt
