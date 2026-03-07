#                                           [2026-03-03 13:45]
#                                          Productivity: Active
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class MutationProposal(BaseModel):
    """Model for a proposed AI mutation (self-modification)"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    proposer_id: str
    target_component: str
    proposed_changes: dict[str, Any]
    rationale: str
    risk_assessment: str
    status: str = "pending"  # pending, simulating, validated, rejected, applied
    simulation_results: dict[str, Any] | None = None
    quorum_signatures: list[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ProposalCreate(BaseModel):
    proposer_id: str
    target_component: str
    proposed_changes: dict[str, Any]
    rationale: str
    risk_assessment: str


class ProposalUpdate(BaseModel):
    status: str | None = None
    simulation_results: dict[str, Any] | None = None
    quorum_signatures: list[str] | None = None


class PaginatedProposals(BaseModel):
    items: list[MutationProposal]
    total: int
    page: int
    page_size: int
    total_pages: int
