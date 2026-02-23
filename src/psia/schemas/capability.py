"""
PSIA Capability Token Schema — least-privilege, non-transitive authorization.

Implements §3.2 of the PSIA v1.0 specification.

A CapabilityToken is a cryptographically signed authorization granting
scoped action(s) to a specific subject.  Tokens are:
- Non-transitive by default (delegation.is_delegable = false)
- Bound to client cert fingerprint and optional device attestation
- Time-limited with nonce replay protection
- Constrained by rate limits, time windows, and network zones
"""

from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, Field

from psia.schemas.identity import Signature


class ScopeConstraints(BaseModel):
    """Per-scope constraints on capability usage."""

    rate_limit_per_min: int = Field(120, ge=0, description="Max requests per minute")
    time_window: str = Field("00:00-23:59", description="Allowed time window (HH:MM-HH:MM)")
    network_zones: list[str] = Field(
        default_factory=lambda: ["ingress"],
        description="Allowed network zones",
    )

    model_config = {"frozen": True}


class CapabilityScope(BaseModel):
    """A single scope entry granting actions on a resource pattern."""

    resource: str = Field(..., description="Resource URI pattern (e.g. policy://registry/*)")
    actions: list[str] = Field(..., min_length=1, description="Allowed actions (e.g. read, write)")
    constraints: ScopeConstraints = Field(default_factory=ScopeConstraints)

    model_config = {"frozen": True}

    def matches_action(self, action: str) -> bool:
        """Check if this scope grants the given action."""
        return action in self.actions

    def matches_resource(self, resource: str) -> bool:
        """Check if this scope covers the given resource (glob-style)."""
        pattern = self.resource
        if pattern.endswith("/*"):
            prefix = pattern[:-2]
            return resource.startswith(prefix)
        return resource == pattern


class DelegationPolicy(BaseModel):
    """Delegation controls — non-transitive by default."""

    is_delegable: bool = Field(False, description="Whether this token can be delegated")
    max_depth: int = Field(0, ge=0, description="Maximum delegation chain depth")

    model_config = {"frozen": True}


class TokenBinding(BaseModel):
    """Token binding to client identity proof."""

    client_cert_fingerprint: str = Field("", description="SHA-256 of client TLS cert")
    device_attestation: str = Field("", description="Optional device attestation hash")

    model_config = {"frozen": True}


class CapabilityToken(BaseModel):
    """
    PSIA Capability Token — scoped, time-limited, non-transitive.

    Invariants:
        - ``scope`` must contain at least one entry
        - ``nonce`` must be unique per token to prevent replay
        - ``expires_at`` must be after ``issued_at``
        - Token is invalid if issuer's identity is revoked
    """

    token_id: str = Field(..., description="Unique token identifier (cap_...)")
    issuer: str = Field(..., description="DID of the CapabilityAuthority")
    subject: str = Field(..., description="DID of the authorized subject")
    issued_at: str = Field(..., description="RFC 3339 issuance timestamp")
    expires_at: str = Field(..., description="RFC 3339 expiry timestamp")
    nonce: str = Field(..., description="128-bit random nonce (hex) for replay prevention")
    scope: list[CapabilityScope] = Field(..., min_length=1, description="Granted scopes")
    delegation: DelegationPolicy = Field(default_factory=DelegationPolicy)
    binding: TokenBinding = Field(default_factory=TokenBinding)
    signature: Signature = Field(..., description="Ed25519 signature by issuer")

    model_config = {"frozen": True}

    def compute_hash(self) -> str:
        """Compute deterministic SHA-256 hash of the token body (excludes signature)."""
        body = self.model_dump(exclude={"signature"})
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def covers(self, action: str, resource: str) -> bool:
        """Check if any scope in this token covers the given action+resource."""
        return any(
            s.matches_action(action) and s.matches_resource(resource)
            for s in self.scope
        )


__all__ = [
    "ScopeConstraints",
    "CapabilityScope",
    "DelegationPolicy",
    "TokenBinding",
    "CapabilityToken",
]
