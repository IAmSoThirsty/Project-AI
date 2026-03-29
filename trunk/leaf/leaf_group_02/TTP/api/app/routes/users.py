# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / users.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / users.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
User management endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import User
from app.schemas.schemas import UserResponse, UserUpdate
from app.services.auth import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Get current user's profile information."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Update current user's profile."""
    if user_data.display_name:
        current_user.display_name = user_data.display_name
    if user_data.email:
        # Check if email is already taken
        existing = db.query(User).filter(
            User.email == user_data.email,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use"
            )
        current_user.email = user_data.email

    db.commit()
    db.refresh(current_user)

    return UserResponse.model_validate(current_user)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Get public user profile by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.model_validate(user)
