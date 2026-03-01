from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class TrustIdentity(BaseModel):
    """Distributed Identity with reputation aggregate"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    public_key: str  # Ed25519
    alias: str
    reputation_score: float = 0.5  # 0.0 to 1.0
    trust_tier: int = 3  # Based on Project-AI tiers
    provenance_log_hash: str
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class TrustRelation(BaseModel):
    """One-way trust weight between two identities"""

    source_id: UUID
    target_id: UUID
    weight: float  # -1.0 to 1.0 (malicious to absolute trust)
    rationale: str
    timestamp: datetime = Field(default_factory=datetime.now)


class IdentityCreate(BaseModel):
    public_key: str
    alias: str
    provenance_log_hash: str
    metadata: Dict[str, Any] = {}


class ReputationUpdate(BaseModel):
    score_delta: float
    reason: str
