# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / schemas.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / schemas.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Pydantic schemas for request/response validation.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, field_validator


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    display_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for user updates."""
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """Schema for user responses."""
    id: UUID
    role: str
    status: str
    created_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Texture Pack Schemas
class PackBase(BaseModel):
    """Base texture pack schema."""
    name: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=20)
    category: str
    quality_tier: str
    license: str
    tags: List[str] = []


class PackCreate(PackBase):
    """Schema for pack creation."""
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    metadata: Dict[str, Any] = {}


class PackUpdate(BaseModel):
    """Schema for pack updates."""
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None


class PackResponse(PackBase):
    """Schema for pack responses."""
    id: UUID
    slug: str
    version: str
    author_id: UUID
    status: str
    created_at: datetime
    published_at: Optional[datetime] = None
    download_count: int
    size_bytes: int

    model_config = {"from_attributes": True}


class PackListResponse(BaseModel):
    """Schema for pack list responses with pagination."""
    data: List[PackResponse]
    pagination: Dict[str, Any]
    links: Dict[str, str]


# Authentication Schemas
class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data."""
    user_id: Optional[UUID] = None
    username: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str
    password: str


# Error Response Schema
class ErrorDetail(BaseModel):
    """Detailed error information."""
    field: Optional[str] = None
    issue: str


class ErrorResponse(BaseModel):
    """Standard error response."""
    code: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
