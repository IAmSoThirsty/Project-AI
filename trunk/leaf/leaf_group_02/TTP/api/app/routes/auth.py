# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / auth.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / auth.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Authentication endpoints.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.models import User
from app.schemas.schemas import Token, LoginRequest, UserCreate, UserResponse
from app.services.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """
    Register a new user account.

    Creates a new user with 'viewer' role by default.
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        display_name=user_data.display_name,
        role="viewer",
        status="active",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse.model_validate(new_user)


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """
    Authenticate and get access token.

    Returns a JWT access token for authenticated requests.
    """
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
        },
        expires_delta=access_token_expires
    )

    # Update last login
    from datetime import datetime
    user.last_login_at = datetime.utcnow()
    db.commit()

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
