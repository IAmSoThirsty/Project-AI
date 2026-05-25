"""PSIA identity schemas — DID documents, keys, revocation."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel, field_validator


class Signature(BaseModel):
    alg: str
    kid: str
    sig: str


class PublicKeyEntry(BaseModel):
    kid: str
    kty: str
    pub: str
    created: str
    expires: str | None = None


class IdentityAttributes(BaseModel):
    org: str = ""
    role: str = ""
    risk_tier: str = ""
    extra: dict[str, Any] = {}


class RevocationStatus(BaseModel):
    status: str  # "active" | "revoked"
    revoked_at: str | None = None
    reason: str | None = None

    @property
    def is_revoked(self) -> bool:
        return self.status == "revoked"


class IdentityDocument(BaseModel):
    id: str
    type: str
    public_keys: list[PublicKeyEntry]
    attributes: IdentityAttributes | None = None
    revocation: RevocationStatus | None = None
    signature: Signature

    @field_validator("public_keys")
    @classmethod
    def min_one_key(cls, v: list) -> list:
        if len(v) < 1:
            raise ValueError("public_keys must have at least one entry")
        return v

    def compute_hash(self) -> str:
        d = self.model_dump()
        d.pop("signature", None)
        return hashlib.sha256(
            json.dumps(d, sort_keys=True, default=str).encode()
        ).hexdigest()
