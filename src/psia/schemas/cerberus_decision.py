"""PSIA Cerberus decision schemas."""
from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Any

from pydantic import BaseModel

from psia.schemas.identity import Signature


class CommitPolicy(BaseModel):
    allowed: bool
    requires_shadow_hash_match: bool = True
    requires_anchor_append: bool = True


class DenyReason(str, Enum):
    INVARIANT_VIOLATION = "invariant_violation"
    CAPABILITY_EXPIRED = "capability_expired"
    IDENTITY_REVOKED = "identity_revoked"
    QUORUM_FAILED = "quorum_failed"
    POLICY_DENIED = "policy_denied"


class ConstraintsApplied(BaseModel):
    rate_limited: bool = False
    scope_narrowed: bool = False
    expiry_enforced: bool = False


class QuorumInfo(BaseModel):
    required: str
    achieved: bool
    voters: list[str] = []


class CerberusVote(BaseModel):
    request_id: str
    head: str
    decision: str
    reasons: list[str] = []
    timestamp: str
    signature: Signature
    constraints: ConstraintsApplied | None = None


class CerberusDecision(BaseModel):
    request_id: str
    severity: str
    final_decision: str
    votes: list[CerberusVote]
    quorum: QuorumInfo
    commit_policy: CommitPolicy | None = None
    timestamp: str
    metadata: dict[str, Any] = {}

    @property
    def is_allowed(self) -> bool:
        return self.final_decision == "allow"

    def compute_hash(self) -> str:
        d = self.model_dump()
        return hashlib.sha256(
            json.dumps(d, sort_keys=True, default=str).encode()
        ).hexdigest()
