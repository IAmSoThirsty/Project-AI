"""
Shadow Execution Types and Core Data Structures

Defines the type system for dual-plane shadow execution:
- Shadow contexts and metadata
- Activation predicates
- Divergence policies
- Invariant definitions
- Mutation boundaries

STATUS: PRODUCTION
VERSION: 1.0.0
"""

import hashlib
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Type Definitions
# ============================================================================


class ShadowStatus(Enum):
    """Status of a shadow execution."""

    INACTIVE = "inactive"  # Shadow not activated
    ACTIVATED = "activated"  # Shadow activated, pending execution
    EXECUTING = "executing"  # Shadow currently executing
    COMPLETED = "completed"  # Shadow execution completed
    DIVERGED = "diverged"  # Shadow diverged from primary beyond threshold
    FAILED = "failed"  # Shadow execution failed
    QUARANTINED = "quarantined"  # Shadow result quarantined (failed invariants)


class ActivationReason(Enum):
    """Reasons for shadow activation."""

    THREAT_SCORE = "threat_score"  # Threat score exceeded threshold
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"  # Anomaly detected
    POLICY_FLAG = "policy_flag"  # Explicit policy flag
    MANUAL_OVERRIDE = "manual_override"  # Manual override by operator
    INVARIANT_PRECHECK = "invariant_precheck"  # Pre-check before mutation
    PERFORMANCE_ENVELOPE = "performance_envelope"  # Performance violation
    HIGH_STAKES = "high_stakes"  # High-stakes operation
    ADVERSARIAL_PATTERN = "adversarial_pattern"  # Adversarial behavior detected


class DivergencePolicy(Enum):
    """Policy for handling primary/shadow divergence."""

    REQUIRE_IDENTICAL = "require_identical"  # Results must be identical
    ALLOW_EPSILON = "allow_epsilon"  # Allow small numerical differences
    LOG_DIVERGENCE = "log_divergence"  # Log divergence but continue
    QUARANTINE_ON_DIVERGE = "quarantine_on_diverge"  # Quarantine if diverged
    FAIL_PRIMARY = "fail_primary"  # Fail primary if shadow diverges


class MutationBoundary(Enum):
    """Defines what shadow can mutate."""

    READ_ONLY = "read_only"  # Shadow cannot mutate anything
    EPHEMERAL_ONLY = "ephemeral_only"  # Shadow can mutate ephemeral state only
    SHADOW_STATE_ONLY = "shadow_state_only"  # Shadow can mutate shadow state
    VALIDATED_CANONICAL = (
        "validated_canonical"  # Shadow can mutate canonical after validation
    )
    EMERGENCY_OVERRIDE = "emergency_override"  # Emergency containment mutations


class ShadowMode(Enum):
    """Operational mode for shadow execution."""

    VALIDATION = "validation"  # Parallel validation of primary
    SIMULATION = "simulation"  # Policy/change simulation
    CONTAINMENT = "containment"  # Adversarial containment
    DECEPTION = "deception"  # Controlled deception layer
    CHAOS_TESTING = "chaos_testing"  # Temporal fuzzing/chaos


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class ActivationPredicate:
    """
    Predicate defining when shadow execution should activate.

    Activation predicates are first-class, deterministic, and auditable.
    """

    predicate_id: str
    name: str
    evaluator: Callable[[dict[str, Any]], bool]
    reason: ActivationReason
    threshold: float | None = None  # Optional threshold value
    metadata: dict[str, Any] = field(default_factory=dict)

    def evaluate(self, context: dict[str, Any]) -> bool:
        """
        Evaluate the activation predicate.

        Args:
            context: Execution context for evaluation

        Returns:
            bool: True if shadow should activate
        """
        try:
            return self.evaluator(context)
        except Exception as e:
            logger.error("Activation predicate %s failed: %s", self.predicate_id, e)
            return False


@dataclass
class InvariantDefinition:
    """
    Definition of an invariant that must hold across primary/shadow execution.

    Invariants are:
    - Pure (no side effects)
    - Deterministic
    - Verifiable
    """

    invariant_id: str
    name: str
    description: str
    validator: Callable[
        [Any, Any], tuple[bool, str]
    ]  # (primary_result, shadow_result) -> (valid, reason)
    is_critical: bool = True  # If false, log violation but don't quarantine
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self, primary_result: Any, shadow_result: Any) -> tuple[bool, str]:
        """
        Validate the invariant.

        Args:
            primary_result: Result from primary execution
            shadow_result: Result from shadow execution

        Returns:
            Tuple of (is_valid, reason)
        """
        try:
            return self.validator(primary_result, shadow_result)
        except Exception as e:
            logger.error("Invariant validation %s failed: %s", self.invariant_id, e)
            return False, f"Validation error: {e}"


@dataclass
class ShadowContext:
    """
    Complete context for shadow execution.

    This is the shadow equivalent of ExecutionContext - a complete
    snapshot of the shadow reality.
    """

    shadow_id: str
    trace_id: str  # Links to primary execution trace
    timestamp: datetime

    # Shadow configuration
    mode: ShadowMode
    activation_reason: ActivationReason
    activation_predicates: list[ActivationPredicate] = field(default_factory=list)

    # Execution boundaries
    divergence_policy: DivergencePolicy = DivergencePolicy.LOG_DIVERGENCE
    mutation_boundary: MutationBoundary = MutationBoundary.READ_ONLY

    # Invariants
    invariants: list[InvariantDefinition] = field(default_factory=list)

    # Execution state
    status: ShadowStatus = ShadowStatus.INACTIVE
    result: Any = None
    error: str | None = None

    # Divergence tracking
    divergence_detected: bool = False
    divergence_magnitude: float = 0.0
    divergence_reason: str | None = None

    # Timing and resource tracking
    start_time: float | None = None
    end_time: float | None = None
    duration_ms: float = 0.0
    cpu_quota_ms: float = 1000.0  # Default 1 second CPU quota
    memory_quota_mb: float = 256.0  # Default 256MB memory quota

    # Isolation and security
    isolated_memory: bool = True
    audit_sealed: bool = False
    audit_hash: str | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def seal_audit_trail(self) -> str:
        """
        Cryptographically seal the shadow execution audit trail.

        Returns:
            str: SHA-256 hash of the audit trail
        """
        audit_data = {
            "shadow_id": self.shadow_id,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp.isoformat(),
            "mode": self.mode.value,
            "activation_reason": self.activation_reason.value,
            "status": self.status.value,
            "divergence_detected": self.divergence_detected,
            "divergence_magnitude": self.divergence_magnitude,
        }

        audit_string = str(sorted(audit_data.items()))
        self.audit_hash = hashlib.sha256(audit_string.encode()).hexdigest()
        self.audit_sealed = True

        logger.info(
            "[%s] Shadow audit sealed: %s", self.shadow_id, self.audit_hash[:16]
        )

        return self.audit_hash


@dataclass
class ShadowResult:
    """
    Result from shadow execution.

    Contains both the shadow result and all validation metadata.
    """

    shadow_id: str
    trace_id: str
    success: bool

    # Results
    primary_result: Any
    shadow_result: Any

    # Validation
    invariants_passed: bool
    invariants_violated: list[str] = field(default_factory=list)

    # Divergence
    divergence_detected: bool = False
    divergence_magnitude: float = 0.0
    divergence_policy: DivergencePolicy = DivergencePolicy.LOG_DIVERGENCE

    # Decision
    should_commit: bool = True  # Whether to commit primary result
    should_quarantine: bool = False  # Whether to quarantine
    quarantine_reason: str | None = None

    # Audit
    audit_hash: str | None = None

    # Timing
    duration_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ShadowTelemetry:
    """
    Telemetry data for shadow executions.

    Invisible to normal UI, visible to defense core.
    """

    total_activations: int = 0
    activations_by_reason: dict[str, int] = field(default_factory=dict)

    # Divergence tracking
    total_divergences: int = 0
    divergence_rate: float = 0.0
    avg_divergence_magnitude: float = 0.0

    # Invariant tracking
    total_invariant_checks: int = 0
    invariant_violations: int = 0
    invariant_violation_rate: float = 0.0

    # Performance tracking
    avg_shadow_overhead_ms: float = 0.0
    total_shadow_time_ms: float = 0.0

    # Resource tracking
    avg_cpu_usage_ms: float = 0.0
    avg_memory_usage_mb: float = 0.0

    # Threat tracking
    threat_triggered_activations: int = 0
    adversarial_patterns_detected: int = 0

    # Temporal tracking
    reordered_events: int = 0
    injected_delays: int = 0
    rollback_simulations: int = 0

    def record_activation(self, reason: ActivationReason) -> None:
        """Record a shadow activation."""
        self.total_activations += 1
        reason_key = reason.value
        self.activations_by_reason[reason_key] = (
            self.activations_by_reason.get(reason_key, 0) + 1
        )

        if reason == ActivationReason.THREAT_SCORE:
            self.threat_triggered_activations += 1
        elif reason == ActivationReason.ADVERSARIAL_PATTERN:
            self.adversarial_patterns_detected += 1

    def record_divergence(self, magnitude: float) -> None:
        """Record a divergence event."""
        self.total_divergences += 1

        # Update running average
        n = self.total_divergences
        self.avg_divergence_magnitude = (
            self.avg_divergence_magnitude * (n - 1) + magnitude
        ) / n

        # Update divergence rate
        if self.total_activations > 0:
            self.divergence_rate = self.total_divergences / self.total_activations

    def record_invariant_check(self, passed: bool) -> None:
        """Record an invariant validation."""
        self.total_invariant_checks += 1

        if not passed:
            self.invariant_violations += 1

        # Update violation rate
        if self.total_invariant_checks > 0:
            self.invariant_violation_rate = (
                self.invariant_violations / self.total_invariant_checks
            )

    def record_execution(
        self, duration_ms: float, cpu_ms: float, memory_mb: float
    ) -> None:
        """Record shadow execution metrics."""
        self.total_shadow_time_ms += duration_ms

        n = self.total_activations
        if n > 0:
            self.avg_shadow_overhead_ms = self.total_shadow_time_ms / n
            self.avg_cpu_usage_ms = (self.avg_cpu_usage_ms * (n - 1) + cpu_ms) / n
            self.avg_memory_usage_mb = (
                self.avg_memory_usage_mb * (n - 1) + memory_mb
            ) / n

    def get_summary(self) -> dict[str, Any]:
        """Get telemetry summary."""
        return {
            "total_activations": self.total_activations,
            "activations_by_reason": self.activations_by_reason,
            "divergence_rate": self.divergence_rate,
            "avg_divergence_magnitude": self.avg_divergence_magnitude,
            "invariant_violation_rate": self.invariant_violation_rate,
            "avg_shadow_overhead_ms": self.avg_shadow_overhead_ms,
            "threat_triggered_activations": self.threat_triggered_activations,
            "adversarial_patterns_detected": self.adversarial_patterns_detected,
        }


# ============================================================================
# Helper Functions
# ============================================================================


def create_epsilon_invariant(
    name: str, epsilon: float = 0.01, is_critical: bool = True
) -> InvariantDefinition:
    """
    Create an epsilon-based numerical invariant.

    Args:
        name: Invariant name
        epsilon: Maximum allowed difference
        is_critical: Whether this is a critical invariant

    Returns:
        InvariantDefinition for numerical comparison
    """

    def validator(primary: Any, shadow: Any) -> tuple[bool, str]:
        try:
            if isinstance(primary, (int, float)) and isinstance(shadow, (int, float)):
                diff = abs(primary - shadow)
                if diff <= epsilon:
                    return True, f"Within epsilon ({diff:.6f} <= {epsilon})"
                else:
                    return False, f"Exceeded epsilon ({diff:.6f} > {epsilon})"
            else:
                return False, "Non-numerical values"
        except Exception as e:
            return False, f"Comparison error: {e}"

    return InvariantDefinition(
        invariant_id=f"epsilon_{name}",
        name=name,
        description=f"Numerical difference must be <= {epsilon}",
        validator=validator,
        is_critical=is_critical,
    )


def create_identity_invariant(
    name: str, is_critical: bool = True
) -> InvariantDefinition:
    """
    Create an identity invariant (results must be identical).

    Args:
        name: Invariant name
        is_critical: Whether this is a critical invariant

    Returns:
        InvariantDefinition for identity comparison
    """

    def validator(primary: Any, shadow: Any) -> tuple[bool, str]:
        if primary == shadow:
            return True, "Results identical"
        else:
            return False, f"Results differ: {primary} != {shadow}"

    return InvariantDefinition(
        invariant_id=f"identity_{name}",
        name=name,
        description="Results must be identical",
        validator=validator,
        is_critical=is_critical,
    )


def create_threat_activation_predicate(threshold: float = 0.7) -> ActivationPredicate:
    """
    Create a threat-score activation predicate.

    Args:
        threshold: Threat score threshold

    Returns:
        ActivationPredicate for threat scores
    """

    def evaluator(context: dict[str, Any]) -> bool:
        threat_score = context.get("threat_score", 0.0)
        return threat_score > threshold

    return ActivationPredicate(
        predicate_id="threat_score_activation",
        name=f"Threat Score > {threshold}",
        evaluator=evaluator,
        reason=ActivationReason.THREAT_SCORE,
        threshold=threshold,
    )


def create_high_stakes_activation_predicate() -> ActivationPredicate:
    """
    Create a high-stakes activation predicate.

    Returns:
        ActivationPredicate for high-stakes operations
    """

    def evaluator(context: dict[str, Any]) -> bool:
        is_high_stakes = context.get("is_high_stakes", False)
        risk_level = context.get("risk_level", "low")
        return is_high_stakes or risk_level in ("high", "critical")

    return ActivationPredicate(
        predicate_id="high_stakes_activation",
        name="High Stakes Operation",
        evaluator=evaluator,
        reason=ActivationReason.HIGH_STAKES,
    )


__all__ = [
    # Enums
    "ShadowStatus",
    "ActivationReason",
    "DivergencePolicy",
    "MutationBoundary",
    "ShadowMode",
    # Data classes
    "ActivationPredicate",
    "InvariantDefinition",
    "ShadowContext",
    "ShadowResult",
    "ShadowTelemetry",
    # Helpers
    "create_epsilon_invariant",
    "create_identity_invariant",
    "create_threat_activation_predicate",
    "create_high_stakes_activation_predicate",
]
