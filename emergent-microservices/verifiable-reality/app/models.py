#                                           [2026-03-03 13:45]
#                                          Productivity: Active
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class RealityProof(BaseModel):
    """Cryptographic proof of existence or state at a specific time"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    event_type: str
    payload_hash: str  # SHA256 of the event data
    merkle_root: str | None = None
    existence_certificate: str | None = None  # RFC 3161 or Sovereign Notarization
    provenance: dict[str, Any]  # Source, Node ID, Consensus signatures
    status: str = "pending"  # pending, certified, verified
    created_at: datetime = Field(default_factory=datetime.now)


class ExistenceCertificate(BaseModel):
    """Notarized certificate from the Triumvirate"""

    proof_id: UUID
    certificate_id: str
    timestamp: datetime
    quorum_signatures: list[str]
