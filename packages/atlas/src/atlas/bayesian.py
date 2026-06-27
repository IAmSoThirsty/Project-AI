"""
atlas.bayesian — Bayesian claim engine (canonical inference).

Production-grade Bayesian inference for claims. Implements the formula:

    P_claim = clamp(
        EvidenceLegitimacy(evidence)
        x WeightedDriverPosterior(claim, drivers)
        x StackPenalty(stack)
        x AgencyPenalty(claim_type, evidence),
        0, 1
    )

Then optional temporal decay:
    P(t) = P_0 x exp(-ln(2) x age_days / half_life)

Faithful port of legacy atlas/core/bayesian_engine.py (498 LOC) to canonical
packages/atlas/.

Architecture:
- Pure deterministic inference (numpy/scipy not required — math.stdlib)
- Optional audit_trail: emits AuditEvents matching legacy categories
- Subordination notice bound to analysis hash (tampering invalidates)
- Downward-only deps: atlas.analysis (SUBORDINATION_NOTICE),
  atlas.audit (optional)
- Fail-closed: every dataclass validates; BayesianEngineError on bad input
- Pluggable config via BayesianConfig
- Deterministic: same inputs to same outputs always

Per AGENTS.md v3: atlas is analytical evidence only, not a decision.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final, cast

from atlas.analysis import SUBORDINATION_NOTICE
from atlas.audit import AuditCategory, AuditLevel, AuditTrail

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class StackPenalty(StrEnum):
    """Stack context for posterior calculation."""

    REALITY = "RS"  # Reality Stack — no penalty
    TIMELINE_0 = "TS-0"  # Timeline near — no penalty
    TIMELINE_1 = "TS-1"  # Timeline +1 — no penalty
    TIMELINE_2 = "TS-2"  # Timeline +2 — slight uncertainty
    TIMELINE_3 = "TS-3"  # Timeline +3 — more uncertainty
    SIMULATION = "SS"  # Simulation Stack — no legitimacy


class TierWeight(StrEnum):
    """Evidence tier weight classes."""

    A = "A"  # Peer-reviewed / official audited
    B = "B"  # Government statistical archives
    C = "C"  # Reputable institutional reporting
    D = "D"  # Media / secondary analysis


# Canonical penalty/weight tables
_STACK_PENALTY_TABLE: Final[dict[str, float]] = {
    StackPenalty.REALITY: 1.0,
    StackPenalty.TIMELINE_0: 1.0,
    StackPenalty.TIMELINE_1: 1.0,
    StackPenalty.TIMELINE_2: 0.95,
    StackPenalty.TIMELINE_3: 0.90,
    StackPenalty.SIMULATION: 0.0,
}

_TIER_WEIGHT_TABLE: Final[dict[str, float]] = {
    TierWeight.A: 1.0,
    TierWeight.B: 0.85,
    TierWeight.C: 0.65,
    TierWeight.D: 0.40,
}


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class BayesianEngineError(ValueError):
    """Raised on invalid Bayesian engine input."""


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BayesianConfig:
    """Configuration for the Bayesian claim engine.

    All values have sensible defaults matching the legacy engine.
    """

    tier_weights: dict[str, float] = field(default_factory=lambda: dict(_TIER_WEIGHT_TABLE))
    stack_penalties: dict[str, float] = field(default_factory=lambda: dict(_STACK_PENALTY_TABLE))
    agency_penalty_multiplier: float = 0.5
    tier_a_bonus_threshold: int = 2
    tier_a_bonus_factor: float = 1.1
    neutral_driver_alignment: float = 0.7
    empty_evidence_legitimacy: float = 0.1
    distance_decay_factor: float = 2.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.agency_penalty_multiplier <= 1.0:
            raise BayesianEngineError(
                f"agency_penalty_multiplier must be in [0, 1], "
                f"got {self.agency_penalty_multiplier!r}"
            )
        if self.tier_a_bonus_threshold < 1:
            raise BayesianEngineError(
                f"tier_a_bonus_threshold must be >= 1, got {self.tier_a_bonus_threshold!r}"
            )
        if not 1.0 <= self.tier_a_bonus_factor <= 2.0:
            raise BayesianEngineError(
                f"tier_a_bonus_factor must be in [1, 2], got {self.tier_a_bonus_factor!r}"
            )
        if not 0.0 <= self.neutral_driver_alignment <= 1.0:
            raise BayesianEngineError(
                f"neutral_driver_alignment must be in [0, 1], got {self.neutral_driver_alignment!r}"
            )
        if not 0.0 <= self.empty_evidence_legitimacy <= 1.0:
            raise BayesianEngineError(
                f"empty_evidence_legitimacy must be in [0, 1], "
                f"got {self.empty_evidence_legitimacy!r}"
            )
        if not 0.0 < self.distance_decay_factor <= 100.0:
            raise BayesianEngineError(
                f"distance_decay_factor must be in (0, 100], got {self.distance_decay_factor!r}"
            )
        # Validate tier weights
        for tier_name, weight in self.tier_weights.items():
            if tier_name not in {"A", "B", "C", "D"}:
                raise BayesianEngineError(f"invalid tier {tier_name!r}: must be A, B, C, or D")
            if not 0.0 <= weight <= 1.0:
                raise BayesianEngineError(
                    f"tier_weight[{tier_name}] must be in [0, 1], got {weight!r}"
                )
        # Validate stack penalties
        for stack_name, penalty in self.stack_penalties.items():
            if not 0.0 <= penalty <= 1.0:
                raise BayesianEngineError(
                    f"stack_penalty[{stack_name}] must be in [0, 1], got {penalty!r}"
                )


@dataclass(frozen=True)
class DriverDependency:
    """A claim's dependency on a driver with expected range."""

    driver: str
    expected_range: tuple[float, float]

    def __post_init__(self) -> None:
        if not self.driver:
            raise BayesianEngineError("driver must not be blank")
        if len(self.expected_range) != 2:
            raise BayesianEngineError(
                f"expected_range must have 2 elements, got {len(self.expected_range)}"
            )
        lo, hi = self.expected_range
        if not 0.0 <= lo <= hi <= 1.0:
            raise BayesianEngineError(f"expected_range[{lo}, {hi}] must satisfy 0 <= lo <= hi <= 1")
        if not isinstance(lo, float) or not isinstance(hi, float):
            raise BayesianEngineError(
                f"expected_range values must be floats, got "
                f"{type(lo).__name__} and {type(hi).__name__}"
            )


@dataclass(frozen=True)
class BayesianClaim:
    """A claim for Bayesian inference.

    Optional fields:
    - timestamp: ISO 8601 string for temporal decay
    - decay_half_life: half-life in days for temporal decay
    - driver_dependencies: list of DriverDependency
    """

    claim_id: str
    statement: str
    claim_type: str
    driver_dependencies: tuple[DriverDependency, ...] = ()
    timestamp: str | None = None
    decay_half_life: float | None = None

    def __post_init__(self) -> None:
        if not self.claim_id:
            raise BayesianEngineError("claim_id must not be blank")
        if not isinstance(self.statement, str):
            raise BayesianEngineError(f"statement must be str, got {type(self.statement).__name__}")
        if not self.claim_type:
            raise BayesianEngineError("claim_type must not be blank")
        if self.decay_half_life is not None and self.decay_half_life <= 0.0:
            raise BayesianEngineError(f"decay_half_life must be > 0, got {self.decay_half_life!r}")
        if self.timestamp is not None:
            try:
                # Validate ISO 8601
                datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
            except ValueError as exc:
                raise BayesianEngineError(
                    f"timestamp must be ISO 8601: {self.timestamp!r} ({exc})"
                ) from exc
        # Validate driver dependencies types
        for dep in self.driver_dependencies:
            if not isinstance(dep, DriverDependency):
                raise BayesianEngineError(
                    f"driver_dependencies must be DriverDependency, got {type(dep).__name__}"
                )


@dataclass(frozen=True)
class BayesianEvidence:
    """Evidence supporting a claim."""

    source: str
    tier: str
    confidence: float

    def __post_init__(self) -> None:
        if not self.source:
            raise BayesianEngineError("source must not be blank")
        if self.tier not in {"A", "B", "C", "D"}:
            raise BayesianEngineError(f"tier must be A, B, C, or D, got {self.tier!r}")
        if not 0.0 <= self.confidence <= 1.0:
            raise BayesianEngineError(f"confidence must be in [0, 1], got {self.confidence!r}")
        # Reject NaN/inf explicitly (since math.isnan check is needed)
        if not (self.confidence == self.confidence):  # NaN check
            raise BayesianEngineError("confidence must not be NaN")
        if self.confidence in (float("inf"), float("-inf")):
            raise BayesianEngineError("confidence must not be inf")


@dataclass(frozen=True)
class BayesianAnalysis:
    """Result of Bayesian inference for a single claim.

    All component values preserved for replay/audit.
    Hash-bound to subordination notice for tamper detection.
    """

    claim_id: str
    posterior: float
    evidence_legitimacy: float
    driver_posterior: float
    stack_penalty: float
    agency_penalty: float
    decay_factor: float
    raw_posterior: float
    tier_a_count: int
    evidence_count: int
    stack: str
    calculation_id: str
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not 0.0 <= self.posterior <= 1.0:
            raise BayesianEngineError(f"posterior must be in [0, 1], got {self.posterior!r}")
        for fname in (
            "evidence_legitimacy",
            "driver_posterior",
            "stack_penalty",
            "agency_penalty",
            "decay_factor",
            "raw_posterior",
        ):
            v = getattr(self, fname)
            if not 0.0 <= v <= 1.0:
                raise BayesianEngineError(f"{fname} must be in [0, 1], got {v!r}")
        if self.tier_a_count < 0:
            raise BayesianEngineError(f"tier_a_count must be >= 0, got {self.tier_a_count}")
        if self.evidence_count < 0:
            raise BayesianEngineError(f"evidence_count must be >= 0, got {self.evidence_count}")
        if not self.calculation_id:
            raise BayesianEngineError("calculation_id must not be blank")


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


_global_engine: BayesianClaimEngine | None = None


class BayesianClaimEngine:
    """Layer 4: Bayesian claim engine.

    Calculates probabilistic legitimacy of claims using evidence-based
    Bayesian inference with automatic penalties for low-quality evidence
    or agency claims.
    """

    def __init__(
        self,
        config: BayesianConfig | None = None,
        audit_trail: AuditTrail | None = None,
    ) -> None:
        self._config = config or BayesianConfig()
        self._audit_trail = audit_trail

        if self._audit_trail is not None:
            self._emit_init_event()

    def _emit_init_event(self) -> None:
        assert self._audit_trail is not None
        self._audit_trail.append(
            level=AuditLevel.INFORMATIONAL,
            category=AuditCategory.SYSTEM,
            actor="BAYESIAN_ENGINE",
            action="bayesian_engine_initialized",
            resource="atlas.bayesian.engine",
            outcome="ALLOW",
            rationale="BayesianClaimEngine initialized",
            evidence=cast(
                dict[str, str],
                {
                    "tier_weights": str(dict(self._config.tier_weights)),
                    "agency_penalty": str(self._config.agency_penalty_multiplier),
                },
            ),
        )

    def attach_audit_trail(self, audit_trail: AuditTrail) -> None:
        """Attach an audit trail. Idempotent — replaces existing trail."""
        if not isinstance(audit_trail, AuditTrail):
            raise BayesianEngineError(
                f"audit_trail must be AuditTrail, got {type(audit_trail).__name__}"
            )
        self._audit_trail = audit_trail
        self._emit_init_event()

    @property
    def config(self) -> BayesianConfig:
        return self._config

    # -- Main entry points --------------------------------------------------

    def calculate_posterior(
        self,
        claim: BayesianClaim,
        evidence: tuple[BayesianEvidence, ...],
        driver_context: dict[str, float] | None = None,
        stack: str = StackPenalty.REALITY,
        now: datetime | None = None,
    ) -> BayesianAnalysis:
        """Calculate Bayesian posterior for a claim.

        Returns a BayesianAnalysis with all components preserved.
        """
        drivers = driver_context or {}
        # Validate driver context values
        for k, v in drivers.items():
            if not 0.0 <= v <= 1.0:
                raise BayesianEngineError(f"driver_context[{k!r}]={v!r} must be in [0, 1]")

        # 1. Evidence Legitimacy
        el, tier_a_count = self._calculate_evidence_legitimacy(evidence)

        # 2. Weighted Driver Posterior
        wdp = self._calculate_driver_posterior(claim, drivers)

        # 3. Stack penalty
        sp = self._config.stack_penalties.get(stack, 1.0)

        # 4. Agency penalty
        ap, agency_penalty_applied = self._calculate_agency_penalty(claim, evidence)

        # 5. Raw posterior
        raw = el * wdp * sp * ap

        # 6. Normalize
        posterior = self._normalize(raw)

        # 7. Temporal decay
        decay_factor, decay_applied = self._apply_temporal_decay(posterior, claim, now=now)
        posterior_after_decay = posterior * decay_factor

        # Build analysis hash
        import hashlib
        import json

        analysis_body = {
            "claim_id": claim.claim_id,
            "evidence_legitimacy": el,
            "driver_posterior": wdp,
            "stack_penalty": sp,
            "agency_penalty": ap,
            "raw_posterior": raw,
            "decay_factor": decay_factor,
            "tier_a_count": tier_a_count,
            "evidence_count": len(evidence),
            "stack": stack,
            "subordination_notice": SUBORDINATION_NOTICE,
        }
        analysis_json = json.dumps(analysis_body, sort_keys=True)
        calc_id = hashlib.sha256(analysis_json.encode("utf-8")).hexdigest()

        analysis = BayesianAnalysis(
            claim_id=claim.claim_id,
            posterior=posterior_after_decay,
            evidence_legitimacy=el,
            driver_posterior=wdp,
            stack_penalty=sp,
            agency_penalty=ap,
            decay_factor=decay_factor,
            raw_posterior=raw,
            tier_a_count=tier_a_count,
            evidence_count=len(evidence),
            stack=stack,
            calculation_id=calc_id,
        )

        # Emit audit events
        if self._audit_trail is not None:
            if agency_penalty_applied:
                self._audit_trail.append(
                    level=AuditLevel.HIGH_PRIORITY,
                    category=AuditCategory.VALIDATION,
                    actor="BAYESIAN_ENGINE",
                    action="agency_penalty_applied",
                    resource=f"atlas:bayesian:{claim.claim_id}",
                    outcome="ALLOW",
                    rationale=("Agency claim without TierA/B evidence — agency_penalty applied"),
                    evidence={
                        "claim_id": claim.claim_id,
                        "penalty_multiplier": str(ap),
                    },
                )
            self._audit_trail.append(
                level=AuditLevel.STANDARD,
                category=AuditCategory.OPERATION,
                actor="BAYESIAN_ENGINE",
                action="claim_posterior_calculated",
                resource=f"atlas:bayesian:{claim.claim_id}",
                outcome="ALLOW",
                rationale="Bayesian posterior calculated",
                evidence={
                    "claim_id": claim.claim_id,
                    "claim_type": claim.claim_type,
                    "evidence_legitimacy": str(el),
                    "driver_posterior": str(wdp),
                    "stack_penalty": str(sp),
                    "agency_penalty": str(ap),
                    "raw_posterior": str(raw),
                    "final_posterior": str(posterior_after_decay),
                    "stack": stack,
                    "decay_applied": str(decay_applied),
                    "calculation_id": calc_id,
                },
            )

        return analysis

    def process_claim(
        self,
        claim: BayesianClaim,
        evidence: tuple[BayesianEvidence, ...],
        driver_context: dict[str, float] | None = None,
        stack: str = StackPenalty.REALITY,
        now: datetime | None = None,
    ) -> tuple[BayesianClaim, BayesianAnalysis]:
        """Process a claim and return (claim, analysis).

        Returns the analysis as a separate value (no in-place mutation,
        matching canonical atlas's immutability pattern).
        """
        analysis = self.calculate_posterior(
            claim, evidence, driver_context=driver_context, stack=stack, now=now
        )
        return claim, analysis

    # -- Helpers ------------------------------------------------------------

    def _calculate_evidence_legitimacy(
        self,
        evidence: tuple[BayesianEvidence, ...],
    ) -> tuple[float, int]:
        """Calculate evidence legitimacy (EL) and TierA count."""
        if not evidence:
            return self._config.empty_evidence_legitimacy, 0

        weighted_sum = 0.0
        total_weight = 0.0
        tier_a_count = 0

        for ev in evidence:
            weight = self._config.tier_weights[ev.tier]
            weighted_sum += weight * ev.confidence
            total_weight += weight
            if ev.tier == TierWeight.A:
                tier_a_count += 1

        if total_weight == 0.0:
            return self._config.empty_evidence_legitimacy, 0

        # Average weighted evidence
        legitimacy = weighted_sum / len(evidence)

        # Bonus for multiple high-tier sources
        if tier_a_count >= self._config.tier_a_bonus_threshold:
            legitimacy *= self._config.tier_a_bonus_factor

        # Cap at 1.0
        return min(legitimacy, 1.0), tier_a_count

    def _calculate_driver_posterior(
        self,
        claim: BayesianClaim,
        driver_context: dict[str, float],
    ) -> float:
        """Calculate weighted driver posterior (WDP)."""
        if not claim.driver_dependencies:
            return self._config.neutral_driver_alignment

        alignments: list[float] = []

        for dep in claim.driver_dependencies:
            if dep.driver in driver_context:
                actual_value = driver_context[dep.driver]
                lo, hi = dep.expected_range

                if lo <= actual_value <= hi:
                    alignment = 1.0
                else:
                    # Distance from range
                    distance = lo - actual_value if actual_value < lo else actual_value - hi

                    # Exponential decay of alignment with distance
                    alignment = math.exp(-distance * self._config.distance_decay_factor)

                alignments.append(alignment)

        if not alignments:
            return self._config.neutral_driver_alignment

        return sum(alignments) / len(alignments)

    def _calculate_agency_penalty(
        self,
        claim: BayesianClaim,
        evidence: tuple[BayesianEvidence, ...],
    ) -> tuple[float, bool]:
        """Calculate agency penalty.

        Returns (multiplier, applied). If applied=True, the penalty was
        triggered (event will be emitted in caller).
        """
        if claim.claim_type.upper() != "AGENCY":
            return 1.0, False

        # Check if TierA/B evidence exists
        has_high_tier = any(ev.tier in {TierWeight.A, TierWeight.B} for ev in evidence)

        if not has_high_tier:
            return self._config.agency_penalty_multiplier, True

        return 1.0, False

    @staticmethod
    def _normalize(value: float) -> float:
        """Normalize value to [0, 1] range."""
        return max(0.0, min(1.0, value))

    def _apply_temporal_decay(
        self,
        posterior: float,
        claim: BayesianClaim,
        now: datetime | None = None,
    ) -> tuple[float, bool]:
        """Apply temporal decay if claim has decay_half_life and timestamp.

        Returns (decay_factor, applied). If applied=True, decay was applied.
        """
        if claim.decay_half_life is None or claim.timestamp is None:
            return 1.0, False

        try:
            ts = datetime.fromisoformat(claim.timestamp.replace("Z", "+00:00"))
            # Strip tzinfo for naive subtraction
            ts_naive = ts.replace(tzinfo=None)
            now_naive = (now or datetime.now(UTC)).replace(tzinfo=None)
            age_days = (now_naive - ts_naive).days
            if age_days < 0:
                # Future timestamp — no decay applied
                return 1.0, False

            # Exponential decay: P(t) = P_0 x exp(-ln(2) x t / half_life)
            decay_factor = math.exp(-math.log(2) * age_days / claim.decay_half_life)
            return decay_factor, True
        except (ValueError, TypeError):
            return 1.0, False


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------


def calculate_bayesian_posterior(
    claim: BayesianClaim,
    evidence: tuple[BayesianEvidence, ...],
    driver_context: dict[str, float] | None = None,
    stack: str = StackPenalty.REALITY,
    config: BayesianConfig | None = None,
    now: datetime | None = None,
) -> BayesianAnalysis:
    """Calculate Bayesian posterior without managing engine state.

    Convenience function for one-shot inference.
    """
    engine = BayesianClaimEngine(config=config)
    return engine.calculate_posterior(
        claim, evidence, driver_context=driver_context, stack=stack, now=now
    )


def get_bayesian_engine(
    config: BayesianConfig | None = None,
    audit_trail: AuditTrail | None = None,
) -> BayesianClaimEngine:
    """Get the global Bayesian claim engine instance."""
    global _global_engine
    if _global_engine is None:
        _global_engine = BayesianClaimEngine(config=config, audit_trail=audit_trail)
    return _global_engine


def reset_bayesian_engine() -> None:
    """Reset the global engine (for testing)."""
    global _global_engine
    _global_engine = None


__all__ = [
    "BayesianAnalysis",
    "BayesianClaim",
    "BayesianClaimEngine",
    "BayesianConfig",
    "BayesianEngineError",
    "BayesianEvidence",
    "DriverDependency",
    "StackPenalty",
    "TierWeight",
    "calculate_bayesian_posterior",
    "get_bayesian_engine",
    "reset_bayesian_engine",
]
