"""
PSIA Identity Schema — IdentityDocument and supporting types.

Implements §3.1 of the PSIA v1.0 specification.

An IdentityDocument is a DID-anchored, Ed25519-signed record that binds
a principal (human, service, or agent) to its public keys, attributes,
and revocation status.  The document is the root of trust for all
capability tokens and request envelope signatures.

Wire format: canonical JSON (deterministic key order, no whitespace).
"""

from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, Field


class PublicKeyEntry(BaseModel):
    """A single public key within an identity document."""

    kid: str = Field(..., description="Key identifier (unique within document)")
    kty: Literal["ed25519"] = Field(
        "ed25519", description="Key type — only Ed25519 supported"
    )
    pub: str = Field(..., description="Base64-encoded public key material")
    created: str = Field(..., description="RFC 3339 creation timestamp")
    expires: str = Field(..., description="RFC 3339 expiry timestamp")

    model_config = {"frozen": True}


class IdentityAttributes(BaseModel):
    """Subject attributes embedded in an identity document."""

    org: str = Field("", description="Organization or tenant")
    role: str = Field("", description="Primary role (e.g. admin, operator, service)")
    risk_tier: Literal["low", "med", "high"] = Field(
        "low", description="Risk classification"
    )

    model_config = {"frozen": True}


class RevocationStatus(BaseModel):
    """Revocation state of an identity document."""

    status: Literal["active", "revoked"] = Field("active")
    revoked_at: str | None = Field(None, description="RFC 3339 revocation timestamp")
    reason: str | None = Field(None, description="Human-readable revocation reason")

    model_config = {"frozen": True}

    @property
    def is_revoked(self) -> bool:
        """Return True if identity is revoked."""
        return self.status == "revoked"


class Signature(BaseModel):
    """Cryptographic signature block (reused across many schemas)."""

    alg: Literal["ed25519"] = Field("ed25519", description="Signing algorithm")
    kid: str | None = Field(None, description="Key identifier of signing key")
    sig: str = Field(..., description="Base64-encoded signature bytes")

    model_config = {"frozen": True}


class IdentityDocument(BaseModel):
    """
    PSIA Identity Document — the root-of-trust for a principal.

    Each actor/subject in the system is represented by exactly one
    IdentityDocument, identified by a ``did:project-ai:`` URI.

    Invariants:
        - ``id`` must start with ``did:project-ai:``
        - ``public_keys`` must contain at least one entry
        - ``signature`` is computed over all fields except ``signature`` itself
    """

    id: str = Field(..., description="DID URI (did:project-ai:...)")
    type: Literal["human", "service", "agent"] = Field(
        ..., description="Principal type"
    )
    public_keys: list[PublicKeyEntry] = Field(
        ..., min_length=1, description="At least one public key"
    )
    attributes: IdentityAttributes = Field(default_factory=IdentityAttributes)
    revocation: RevocationStatus = Field(default_factory=RevocationStatus)
    signature: Signature = Field(
        ..., description="Ed25519 signature over document body"
    )

    model_config = {"frozen": True}

    def compute_hash(self) -> str:
        """Compute deterministic SHA-256 hash of the document body (excludes signature)."""
        body = self.model_dump(exclude={"signature"})
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()


__all__ = [
    "PublicKeyEntry",
    "IdentityAttributes",
    "RevocationStatus",
    "Signature",
    "IdentityDocument",
]
