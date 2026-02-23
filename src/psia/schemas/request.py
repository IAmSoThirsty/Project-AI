"""
PSIA Request Envelope Schema — the universal request entry point.

Implements §3.3 of the PSIA v1.0 specification.

Every operation in PSIA begins as a RequestEnvelope: a signed,
trace-linked intent from an authenticated actor targeting a specific
resource.  The envelope carries enough context for the Waterfall pipeline
to classify, simulate, and decide on the request without round-trips.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel, Field

from psia.schemas.identity import Signature


class Intent(BaseModel):
    """The action a request intends to perform."""

    action: str = Field(
        ...,
        description="Verb: mutate_state, mutate_policy, spawn_task, read_state, etc.",
    )
    resource: str = Field(..., description="Target resource URI (state://path/to/key)")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Action-specific params")
    justification: str = Field("", description="Required for privileged actions")

    model_config = {"frozen": True}


class RequestContext(BaseModel):
    """Ambient context captured at request ingress."""

    client_ip: str = Field("", description="Client IP address")
    user_agent: str = Field("", description="User-Agent header or equivalent")
    session_id: str = Field("", description="Session identifier")
    trace_id: str = Field("", description="Distributed trace identifier")
    risk_hints: list[str] = Field(default_factory=list, description="Caller-provided risk signals")

    model_config = {"frozen": True}


class RequestTimestamps(BaseModel):
    """Temporal anchors for the request lifecycle."""

    created_at: str = Field(..., description="RFC 3339 — when the actor created the request")
    received_at: str = Field("", description="RFC 3339 — when ingress received the request")

    model_config = {"frozen": True}


class RequestEnvelope(BaseModel):
    """
    PSIA Request Envelope — the canonical unit of work.

    Every mutation, query, or governance proposal enters the system
    as a RequestEnvelope.  It is the input to the Waterfall pipeline
    and the basis for the ``inputs_hash`` in the ledger.

    Invariants:
        - ``request_id`` is globally unique
        - ``actor`` and ``subject`` must reference valid IdentityDocuments
        - ``capability_token_id`` must reference a valid, non-expired CapabilityToken
        - ``signature`` is computed over all fields except ``signature`` itself
    """

    request_id: str = Field(..., description="Globally unique request ID (req_...)")
    actor: str = Field(..., description="DID of the requesting actor")
    subject: str = Field(..., description="DID of the logical principal")
    capability_token_id: str = Field(..., description="CapabilityToken ID for authorization")
    intent: Intent = Field(..., description="Requested action")
    context: RequestContext = Field(default_factory=RequestContext)
    timestamps: RequestTimestamps = Field(..., description="Creation and receipt timestamps")
    signature: Signature = Field(..., description="Ed25519 signature by actor")

    model_config = {"frozen": True}

    def compute_hash(self) -> str:
        """Compute deterministic SHA-256 hash of the envelope body (excludes signature)."""
        body = self.model_dump(exclude={"signature"})
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()


__all__ = [
    "Intent",
    "RequestContext",
    "RequestTimestamps",
    "RequestEnvelope",
]
