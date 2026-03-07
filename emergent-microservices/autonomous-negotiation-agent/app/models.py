#                                           [2026-03-03 13:45]
#                                          Productivity: Active
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class NegotiationSession(BaseModel):
    """Secure agent-to-agent bargaining session"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    initiator_id: str
    participant_id: str
    topic: str
    current_offer: dict[str, Any]
    history: list[dict[str, Any]] = []
    status: str = "opening"  # opening, active, agreed, failed, expired
    constraints: dict[str, Any] = {}
    contract_id: UUID | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class NegotiationOffer(BaseModel):
    sender_id: str
    content: dict[str, Any]
    rationale: str


class AgreedContract(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    terms: dict[str, Any]
    signatures: dict[str, str]  # Agent ID -> Ed25519 signature
    signed_at: datetime = Field(default_factory=datetime.now)
