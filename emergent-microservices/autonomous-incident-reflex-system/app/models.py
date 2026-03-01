from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class SecurityIncident(BaseModel):
    """Model for a security incident detected by the reflex system"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    source: str
    severity: str  # low, medium, high, critical
    incident_type: str
    description: str
    metadata: Dict[str, Any]
    status: str = "detected"  # detected, analyzing, reflex_triggered, closed
    evidence_hash: Optional[str] = None
    reflex_actions_taken: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class IncidentCreate(BaseModel):
    source: str
    severity: str
    incident_type: str
    description: str
    metadata: Dict[str, Any]


class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    evidence_hash: Optional[str] = None
    reflex_actions_taken: Optional[List[str]] = None


class PaginatedIncidents(BaseModel):
    items: List[SecurityIncident]
    total: int
    page: int
    page_size: int
    total_pages: int
