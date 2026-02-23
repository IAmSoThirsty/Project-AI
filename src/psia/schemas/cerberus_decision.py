"""
PSIA Cerberus Decision Schema — triple-head vote and quorum consensus.

Implements §3.7 of the PSIA v1.0 specification.

The Cerberus Gate Plane operates three independent heads (Identity,
Capability, Invariant) that each cast a signed vote.  The QuorumEngine
collects votes and produces a final CerberusDecision that determines
whether a request is allowed, denied, or quarantined.

Quorum policies:
- ``unanimous``: all heads must agree
- ``2of3``: at least 2 of 3 heads must agree
- ``simple``: majority wins
"""

from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, Field

from psia.schemas.identity import Signature


class DenyReason(BaseModel):
    """A single reason for denying or quarantining a request."""

    code: str = Field(..., description="Machine-readable reason code (e.g. CAP_SCOPE_MISMATCH)")
    detail: str = Field("", description="Human-readable detail")

    model_config = {"frozen": True}


class ConstraintsApplied(BaseModel):
    """Constraints applied by a Cerberus head's evaluation."""

    rate_limit_per_min: int = Field(0, ge=0, description="Applied rate limit")
    require_shadow: bool = Field(False, description="Whether shadow simulation is required")
    require_quorum: str = Field("2of3", description="Quorum requirement: unanimous, 2of3, simple")

    model_config = {"frozen": True}


class CerberusVote(BaseModel):
    """
    A single head's vote on a request.

    Each of the three Cerberus heads (identity, capability, invariant)
    independently evaluates the request and casts a signed vote.
    """

    request_id: str = Field(..., description="Request being voted on")
    head: Literal["identity", "capability", "invariant"] = Field(
        ..., description="Which Cerberus head cast this vote"
    )
    decision: Literal["allow", "deny", "quarantine"] = Field(
        ..., description="Head's decision"
    )
    reasons: list[DenyReason] = Field(default_factory=list, description="Reasons for non-allow")
    constraints_applied: ConstraintsApplied = Field(default_factory=ConstraintsApplied)
    timestamp: str = Field(..., description="RFC 3339 vote timestamp")
    signature: Signature = Field(..., description="Head's Ed25519 signature")

    model_config = {"frozen": True}


class QuorumInfo(BaseModel):
    """Quorum state for the Cerberus decision."""

    required: Literal["unanimous", "2of3", "simple", "bft"] = Field(
        "2of3", description="Quorum policy"
    )
    achieved: bool = Field(False, description="Whether quorum was achieved")
    voters: list[str] = Field(default_factory=list, description="Node IDs that participated")

    model_config = {"frozen": True}


class CommitPolicy(BaseModel):
    """Post-decision commit requirements."""

    allowed: bool = Field(False, description="Whether commit is allowed")
    requires_shadow_hash_match: bool = Field(True, description="Shadow hash must match")
    requires_anchor_append: bool = Field(True, description="Ledger anchor required")

    model_config = {"frozen": True}


class CerberusDecision(BaseModel):
    """
    PSIA Cerberus Decision — the final, multi-signed verdict.

    Invariants:
        - ``votes`` must contain exactly 3 votes (one per head)
        - ``quorum.achieved`` must be True for any allow decision
        - ``final_decision`` must be the most restrictive of the votes
          when any vote is deny (monotonic strictness per INV-ROOT-7)
        - ``signature_set`` must contain at least ``quorum.required`` signatures
    """

    request_id: str = Field(..., description="Request being decided")
    severity: Literal["low", "med", "high", "critical", "fatal"] = Field(
        ..., description="Severity classification"
    )
    final_decision: Literal["allow", "deny", "quarantine"] = Field(
        ..., description="Final decision after quorum"
    )
    votes: list[CerberusVote] = Field(..., description="Individual head votes")
    quorum: QuorumInfo = Field(..., description="Quorum state")
    commit_policy: CommitPolicy = Field(default_factory=CommitPolicy)
    timestamp: str = Field(..., description="RFC 3339 decision timestamp")
    signature_set: list[Signature] = Field(
        default_factory=list, description="Quorum signer signatures"
    )

    model_config = {"frozen": True}

    def compute_hash(self) -> str:
        """Compute deterministic SHA-256 hash (excludes signature_set)."""
        body = self.model_dump(exclude={"signature_set"})
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    @property
    def is_allowed(self) -> bool:
        """Return True if the final decision is allow and quorum was achieved."""
        return self.final_decision == "allow" and self.quorum.achieved


__all__ = [
    "DenyReason",
    "ConstraintsApplied",
    "CerberusVote",
    "QuorumInfo",
    "CommitPolicy",
    "CerberusDecision",
]
