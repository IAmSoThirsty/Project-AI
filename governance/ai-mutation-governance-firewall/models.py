from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class MutationProposal(BaseModel):
    """Model for a proposed AI mutation (self-modification)"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    proposer_id: str
    target_component: str
    proposed_changes: Dict[str, Any]
    rationale: str
    risk_assessment: str
    status: str = "pending"  # pending, simulating, validated, rejected, applied
    simulation_results: Optional[Dict[str, Any]] = None
    quorum_signatures: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ProposalCreate(BaseModel):
    proposer_id: str
    target_component: str
    proposed_changes: Dict[str, Any]
    rationale: str
    risk_assessment: str


class ProposalUpdate(BaseModel):
    status: Optional[str] = None
    simulation_results: Optional[Dict[str, Any]] = None
    quorum_signatures: Optional[List[str]] = None


class PaginatedProposals(BaseModel):
    items: List[MutationProposal]
    total: int
    page: int
    page_size: int
    total_pages: int
