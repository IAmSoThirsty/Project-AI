import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: zero-downtime-deploys / models.py
# ============================================================================ #
"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4


class BaseResponse(BaseModel):
    """Base response model"""
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Error response model"""
    error: dict


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseResponse):
    """Paginated response model"""
    items: List[BaseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Example domain models (customize for your use case)

class ItemBase(BaseModel):
    """Base item model"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        # Custom validation
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class ItemCreate(ItemBase):
    """Item creation model"""
    pass


class ItemUpdate(BaseModel):
    """Item update model (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class Item(ItemBase, BaseResponse):
    """Item model with metadata"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Example Item",
                "description": "This is an example item",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }
    )
