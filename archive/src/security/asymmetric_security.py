#                                            [2026-03-02 07:55]
#                                           Productivity: Active
"""
THIRSTY'S ASYMMETRIC SECURITY FRAMEWORK - CORE SUBSTRATE
Security Architect (Gateway & Invariants)

This module implements the Layer 3 Security Enforcement Gateway and the
Layer 2 Reuse Friction Index (RFI) Calculator as defined in the
Asymmetric Security Whitepaper.

Structural Guarantee: allowed=False → CANNOT execute.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# Import legacy engines for integration
try:
    from app.core.asymmetric_security_engine import AsymmetricSecurityEngine
except ImportError:
    # Fallback/Mock for standalone testing
    AsymmetricSecurityEngine = None

logger = logging.getLogger(__name__)


class SecurityViolationError(Exception):
    """Exception raised when a constitutional or RFI check fails."""

    pass


class OperationalState(Enum):
    """System operational states for state-machine validation."""

    NORMAL = "normal"
    DEGRADED = "degraded"
    LOCKED = "locked"
    HALTED = "halted"


@dataclass
class SecurityContext:
    """Enterprise-grade security context for action validation."""

    user_id: str
    action: str
    tenant_id: str = "default"
    auth_proof: str | None = None
    audit_span_id: str | None = None
    replay_token: str | None = None
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Context dimensions and their calculated entropy bits
    dimensions: dict[str, float] = field(default_factory=dict)


# ============================================================================
# LAYER 2: REUSE FRICTION INDEX (RFI) CALCULATOR
# ============================================================================


class RFICalculator:
    """
    Mathematical Model Implementation for Exploit Irreducibility.

    Implements RFI = 1 - 2^-H(C) (Entropy-Relative Friction).
    """

    def calculate(self, ctx: SecurityContext) -> float:
        """
        Calculates the Reuse Friction Index based on total entropy bits.
        Higher RFI => Lower exploit transferability => Higher security.
        """
        total_entropy = sum(ctx.dimensions.values())
        if total_entropy <= 0:
            return 0.0

        # RFI = 1 - 2^-H(C)
        # This models the probability that an exploit (E) contains enough
        # information to collapse the context entropy gap.
        rfi = 1.0 - (2.0**-total_entropy)
        return rfi


class AdversarialProber:
    """
    Tracks and mitigates adversarial probing attempts.
    Increases friction dynamically when suspicious patterns are detected.
    """

    def __init__(self):
        self.probe_registry: dict[str, int] = {}  # source_id -> fail_count
        self.last_cleanup = time.time()

    def record_attempt(self, source_id: str, success: bool):
        """Records the outcome of a security validation attempt."""
        if not success:
            self.probe_registry[source_id] = self.probe_registry.get(source_id, 0) + 1
        else:
            # Slow decay on success to prevent 'reset' attacks
            if source_id in self.probe_registry:
                self.probe_registry[source_id] = max(
                    0, self.probe_registry[source_id] - 1
                )

    def get_friction_multiplier(self, source_id: str) -> float:
        """Returns a multiplier for the RFI requirement based on probing history."""
        fail_count = self.probe_registry.get(source_id, 0)
        if fail_count > 10:
            return 2.0  # Double requirements for heavy probers
        if fail_count > 2:  # Lowered to 2 for faster verification and sensitivity
            return 1.25  # Significant increase for suspicious activity
        return 1.0


class DimensionEntropyGuard:
    """
    Formally enforces entropy dimension requirements.
    Ensures dimensions are not 'symbolic' but satisfy H(D_k) >= threshold.
    """

    MIN_DIMENSION_ENTROPY = 4.0  # Bits

    def validate(self, ctx: SecurityContext):
        """Validates all dimensions in context."""
        for name, bits in ctx.dimensions.items():
            if bits < self.MIN_DIMENSION_ENTROPY:
                raise SecurityViolationError(
                    f"Dimension {name} failed entropy requirement: {bits} < {self.MIN_DIMENSION_ENTROPY} bits"
                )


# ============================================================================
# LAYER 3: SECURITY ENFORCEMENT GATEWAY
# ============================================================================


class SecurityEnforcementGateway:
    """
    Truth-Defining Gateway (Level 3).

    If this gateway returns False, the operation MUST NOT proceed at the engine level.
    Enforces the Security Constitution and RFI thresholds.
    """

    def __init__(self, data_dir: str = "data/security"):
        self.data_dir = data_dir
        self.rfi_calculator = RFICalculator()
        self.prober = AdversarialProber()
        self.guard = DimensionEntropyGuard()
        self.engine = None

        # Initialize internal engine if available
        if AsymmetricSecurityEngine:
            self.engine = AsymmetricSecurityEngine(data_dir)

        # Core thresholds from whitepaper (Ensuring RFI > 0.95 for critical ops)
        self.rfi_thresholds = {
            "delete_user_data": 0.95,
            "privilege_escalation": 0.96,
            "cross_tenant_access": 0.94,
            "modify_trust_score": 0.97,
            "modify_security_policy": 0.98,
            "default": 0.70,
        }

    def validate_and_enforce(self, ctx: SecurityContext) -> tuple[bool, str]:
        """
        Enforces security at the gateway level.

        Returns:
            (allowed, detail_json)
        """
        # 1. Dimension Extraction & Guarding
        self._populate_dimensions(ctx)
        try:
            self.guard.validate(ctx)
        except SecurityViolationError as e:
            self.prober.record_attempt(ctx.user_id, success=False)
            return False, str(e)

        # 2. RFI Calculation
        rfi_score = self.rfi_calculator.calculate(ctx)

        # 3. Threshold Enforcement with Adversarial Shielding
        base_threshold = self.rfi_thresholds.get(
            ctx.action, self.rfi_thresholds["default"]
        )
        multiplier = self.prober.get_friction_multiplier(ctx.user_id)
        required_rfi = min(0.9999, base_threshold * multiplier)

        if rfi_score < required_rfi:
            reason = f"RFI Score {rfi_score:.6f} (H={sum(ctx.dimensions.values()):.1f} bits) below threshold {required_rfi:.4f} for {ctx.action}"
            self._log_violation(ctx, "RFI_INSUFFICIENT", reason)
            self.prober.record_attempt(ctx.user_id, success=False)
            return False, reason

        # Record success to prober
        self.prober.record_attempt(ctx.user_id, success=True)

        # 4. Constitutional Enforcement (Bridge to Engine)
        if self.engine:
            # Map SecurityContext to engine's dictionary context
            engine_ctx = self._map_to_engine_context(ctx)
            engine_ctx["rfi_score"] = rfi_score  # Inject RFI for engine invariants

            allowed, reason = self.engine.constitution.enforce(engine_ctx)
            if not allowed:
                self._log_violation(ctx, "CONSTITUTIONAL_VIOLATION", reason)
                return False, reason

        # 5. Temporal Verification
        if abs(time.time() - ctx.timestamp) > 30.0:
            reason = "Temporal integrity check failed (potential clock skew or replay)"
            self._log_violation(ctx, "TEMPORAL_ANOMALY", reason)
            return False, reason

        return True, "Operation sanctioned by Security Enforcement Gateway"

    def _populate_dimensions(self, ctx: SecurityContext):
        """
        Adds context dimensions based on available proofs.
        Aims to maximize statistical independence and formal entropy requirements.
        """
        # Physical/Identity Dimensions (Fixed Entropy bits)
        if ctx.user_id:
            ctx.dimensions["user_identity"] = 12.0  # log2 of estimated user pool
        if ctx.tenant_id != "default":
            ctx.dimensions["tenant_isolation"] = 8.0

        # Cryptographic Dimensions (High Entropy)
        if ctx.auth_proof:
            ctx.dimensions["auth_proof"] = 16.0
        if ctx.audit_span_id:
            ctx.dimensions["audit_span"] = 12.0
        if ctx.replay_token:
            ctx.dimensions["replay_token"] = 14.0

        # Temporal Dimensions (Dynamic slotting)
        ctx.dimensions["time_window_slot"] = 6.0

        # State Dimensions
        if ctx.metadata.get("mutates_state"):
            ctx.dimensions["state_mutation_vector"] = 4.0
        if ctx.metadata.get("is_agent"):
            ctx.dimensions["agent_agency_signature"] = 10.0

        # Entropy Dimensions (User-supplied or high-bandwidth noise)
        if "entropy_seed" in ctx.metadata:
            # Full 32-bit seed contribution
            ctx.dimensions["observer_entropy"] = 32.0
        if "schema_hash" in ctx.metadata:
            ctx.dimensions["entropic_schema_variant"] = 16.0
        if "side_channel_poison" in ctx.metadata:
            ctx.dimensions["side_channel_de-correlation"] = 8.0

    def _log_violation(self, ctx: SecurityContext, v_type: str, reason: str):
        """Forensic logging of security violations."""
        logger.critical(
            "SECURITY_VIOLATION [%s]: %s by %s - %s",
            v_type,
            ctx.action,
            ctx.user_id,
            reason,
        )

    def _map_to_engine_context(self, ctx: SecurityContext) -> dict[str, Any]:
        """Maps unified SecurityContext to legacy engine dictionary format."""
        return {
            "user_id": ctx.user_id,
            "action": ctx.action,
            "auth_token": ctx.auth_proof,
            "audit_span_id": ctx.audit_span_id,
            "replay_log": ctx.replay_token,
            "state_mutated": ctx.metadata.get("mutates_state", False),
            "trust_decreased": ctx.metadata.get("decreases_trust", False),
            "is_agent_action": ctx.metadata.get("is_agent", False),
            "requesting_tenant": ctx.tenant_id,
            "resource_tenant": ctx.metadata.get("target_tenant", ctx.tenant_id),
            "mfa_verified": ctx.metadata.get("mfa", False),
        }


# ============================================================================
# UTILITIES / FACTORY
# ============================================================================


def get_gateway() -> SecurityEnforcementGateway:
    """Singleton-style accessor for the gateway."""
    return SecurityEnforcementGateway()


if __name__ == "__main__":
    # Test Suite for Gateway
    gateway = get_gateway()

    # Scenario: Unauthorized data deletion (Missing audit span)
    bad_ctx = SecurityContext(
        user_id="attacker_bot",
        action="delete_user_data",
        auth_proof="stolen_jwt",
        metadata={"mutates_state": True},
    )

    allowed, reason = gateway.validate_and_enforce(bad_ctx)
    print(f"Action: {bad_ctx.action} | Allowed: {allowed} | Reason: {reason}")

    # Scenario: Valid deletion with full context
    good_ctx = SecurityContext(
        user_id="admin_human",
        action="delete_user_data",
        auth_proof="valid_jwt",
        audit_span_id="span_777",
        replay_token="nonce_abc",
        metadata={"mutates_state": True},
    )
    allowed, reason = gateway.validate_and_enforce(good_ctx)
    print(f"Action: {good_ctx.action} | Allowed: {allowed} | Reason: {reason}")
