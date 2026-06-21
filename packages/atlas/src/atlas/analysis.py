"""Deterministic evidence-weighted analysis with mandatory subordination metadata."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum

SUBORDINATION_NOTICE = (
    "ATLAS output is analytical evidence only; it is not a decision, authority grant, or actuation."
)


class ClaimType(StrEnum):
    FACTUAL = "factual"
    PREDICTIVE = "predictive"
    AGENCY = "agency"
    CAUSAL = "causal"
    CORRELATIONAL = "correlational"


class EvidenceTier(StrEnum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


_TIER_WEIGHTS = {
    EvidenceTier.A: 1.0,
    EvidenceTier.B: 0.85,
    EvidenceTier.C: 0.65,
    EvidenceTier.D: 0.4,
}


@dataclass(frozen=True)
class Evidence:
    source: str
    tier: EvidenceTier
    confidence: float

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("evidence source must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("evidence confidence must be between 0 and 1")


@dataclass(frozen=True)
class Claim:
    claim_id: str
    statement: str
    claim_type: ClaimType

    def __post_init__(self) -> None:
        if not self.claim_id.strip() or not self.statement.strip():
            raise ValueError("claim ID and statement must not be empty")


@dataclass(frozen=True)
class Projection:
    claim_id: str
    posterior: float
    uncertainty: float
    stack: str
    evidence_count: int
    projection_sha256: str
    subordination_notice: str = SUBORDINATION_NOTICE


def analyze(
    claim: Claim,
    evidence: tuple[Evidence, ...],
    *,
    drivers: dict[str, float],
    stack: str = "RS",
) -> Projection:
    if not stack.strip():
        raise ValueError("stack must not be empty")
    if any(not 0.0 <= value <= 1.0 for value in drivers.values()):
        raise ValueError("driver values must be between 0 and 1")
    evidence_score = (
        sum(_TIER_WEIGHTS[item.tier] * item.confidence for item in evidence) / len(evidence)
        if evidence
        else 0.1
    )
    driver_score = sum(drivers.values()) / len(drivers) if drivers else 0.7
    stack_penalty = 0.0 if stack == "SS" else 0.9 if stack.startswith("TS-") else 1.0
    agency_penalty = (
        0.5
        if claim.claim_type is ClaimType.AGENCY
        and not any(item.tier in (EvidenceTier.A, EvidenceTier.B) for item in evidence)
        else 1.0
    )
    posterior = round(
        max(0.0, min(1.0, evidence_score * driver_score * stack_penalty * agency_penalty)),
        8,
    )
    uncertainty = round(1.0 - posterior, 8)
    body = {
        "claim_id": claim.claim_id,
        "evidence_count": len(evidence),
        "posterior": posterior,
        "stack": stack,
        "subordination_notice": SUBORDINATION_NOTICE,
        "uncertainty": uncertainty,
    }
    digest = hashlib.sha256(
        json.dumps(body, separators=(",", ":"), sort_keys=True).encode()
    ).hexdigest()
    return Projection(
        claim_id=claim.claim_id,
        posterior=posterior,
        uncertainty=uncertainty,
        stack=stack,
        evidence_count=len(evidence),
        projection_sha256=digest,
    )
