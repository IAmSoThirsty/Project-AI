#                                           [2026-03-03 13:45]
#                                          Productivity: Active
from datetime import datetime
from typing import Any
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
    metadata: dict[str, Any]
    status: str = "detected"  # detected, analyzing, reflex_triggered, closed
    evidence_hash: str | None = None
    reflex_actions_taken: list[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class IncidentCreate(BaseModel):
    source: str
    severity: str
    incident_type: str
    description: str
    metadata: dict[str, Any]


class IncidentUpdate(BaseModel):
    status: str | None = None
    evidence_hash: str | None = None
    reflex_actions_taken: list[str] | None = None


class PaginatedIncidents(BaseModel):
    items: list[SecurityIncident]
    total: int
    page: int
    page_size: int
    total_pages: int
