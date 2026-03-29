# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-10 | TIME: 21:02               #
# COMPLIANCE: Regulator-Ready / UTF-8                                          #
# ============================================================================ #

# Date: 2026-03-10 | Time: 20:37 | Status: Active | Tier: Master
#                                           [2026-03-10 18:58]
#                                          Productivity: Active
# ============================================================================ #
#                                                            DATE: 2026-03-10 #
#                                                          TIME: 15:01:56 PST #
#                                                        PRODUCTIVITY: Active #
# ============================================================================ #

#                                           [2026-03-03 13:45]
#                                          Productivity: Active
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class NegotiationSession(BaseModel):
    """Secure agent-to-agent bargaining session"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    initiator_id: str
    participant_id: str
    topic: str
    current_offer: Dict[str, Any]
    history: List[Dict[str, Any]] = []
    status: str = "opening"  # opening, active, agreed, failed, expired
    constraints: Dict[str, Any] = {}
    contract_id: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class NegotiationOffer(BaseModel):
    sender_id: str
    content: Dict[str, Any]
    rationale: str


class AgreedContract(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    terms: Dict[str, Any]
    signatures: Dict[str, str]  # Agent ID -> Ed25519 signature
    signed_at: datetime = Field(default_factory=datetime.now)
