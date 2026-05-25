"""PSIA capability token schemas."""
from __future__ import annotations

import fnmatch
import hashlib
import json
from pydantic import BaseModel

from psia.schemas.identity import Signature


class ScopeConstraints(BaseModel):
    ip_ranges: list[str] = []
    time_windows: list[str] = []
    context_tags: list[str] = []


class CapabilityScope(BaseModel):
    resource: str
    actions: list[str]
    constraints: ScopeConstraints | None = None
    conditions: dict = {}

    def matches_action(self, action: str) -> bool:
        return action in self.actions

    def matches_resource(self, resource: str) -> bool:
        return fnmatch.fnmatch(resource, self.resource)


class DelegationPolicy(BaseModel):
    is_delegable: bool = False
    max_depth: int = 0
    allowed_subjects: list[str] = []


class TokenBinding(BaseModel):
    client_cert_fingerprint: str = ""
    device_id: str = ""


class CapabilityToken(BaseModel):
    token_id: str
    issuer: str
    subject: str
    issued_at: str
    expires_at: str
    nonce: str
    scope: list[CapabilityScope]
    delegation: DelegationPolicy
    binding: TokenBinding | None = None
    signature: Signature

    def compute_hash(self) -> str:
        d = self.model_dump()
        d.pop("signature", None)
        return hashlib.sha256(
            json.dumps(d, sort_keys=True, default=str).encode()
        ).hexdigest()

    def covers(self, action: str, resource: str) -> bool:
        return any(
            s.matches_action(action) and s.matches_resource(resource)
            for s in self.scope
        )
