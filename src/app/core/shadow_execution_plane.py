"""
Shadow Execution Plane - Dual-Reality Computing Infrastructure

Implements parallel execution reality for:
1. Validation: Parallel validation of primary execution
2. Simulation: Pre-commit policy/change simulation
3. Containment: Adversarial pattern containment
4. Deception: Controlled deception for attackers
5. Chaos Testing: Temporal fuzzing and stress testing

ARCHITECTURAL INVARIANTS:
- Shadow NEVER silently mutates canonical state
- Shadow NEVER bypasses audit
- Shadow NEVER weakens invariants
- Shadow executions are deterministic and replayable
- Shadow has bounded activation predicates and resource limits

THREE-TIER PLATFORM:
- Tier 2 (Infrastructure): Shadow is Infrastructure Controller
- Subordinate to Tier-1 governance (CognitionKernel)
- Can be paused or constrained by governance

STATUS: PRODUCTION
VERSION: 1.0.0
"""

import logging
import time
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from app.core.platform_tiers import (
    AuthorityLevel,
    ComponentRole,
    PlatformTier,
    get_tier_registry,
)
from app.core.shadow_resource_limiter import (
    ResourceUsage,
    ShadowResourceLimiter,
    ShadowResourceViolation,
)
from app.core.shadow_types import (
    ActivationPredicate,
    ActivationReason,
    DivergencePolicy,
    InvariantDefinition,
    MutationBoundary,
    ShadowContext,
    ShadowMode,
    ShadowResult,
    ShadowStatus,
    ShadowTelemetry,
)

logger = logging.getLogger(__name__)


class ShadowExecutionPlane:
    """
    Shadow Execution Plane - Parallel execution reality.

    This is the second execution plane that runs alongside primary execution
    for validation, simulation, containment, and chaos testing.

    Key Capabilities:
    1. Parallel validation: Run shadow alongside primary, compare results
    2. Pre-commit simulation: Test changes before committing
    3. Adversarial containment: Route attacks to shadow reality
    4. Controlled deception: Shape attacker perception
    5. Chaos testing: Inject temporal anomalies

    Resource Limits:
    - CPU quota: Default 1000ms per execution
    - Memory quota: Default 256MB per execution
    - Isolated memory region
    - Time-bounded execution
    - Audit streamed in real-time

    Integration Points:
    - CognitionKernel: Primary execution authority
    - GovernanceService: Invariant validation
    - AuditManager: Cryptographic audit sealing
    - ThreatDetection: Activation triggers
    """

    def __init__(
        self,
        audit_manager: Any | None = None,
        threat_detector: Any | None = None,
        governance_service: Any | None = None,
        default_cpu_quota_ms: float = 1000.0,
        default_memory_quota_mb: float = 256.0,
    ):
        """
        Initialize Shadow Execution Plane.

        Args:
            audit_manager: Audit manager for cryptographic sealing
            threat_detector: Threat detection for activation triggers
            governance_service: Governance service for invariant validation
            default_cpu_quota_ms: Default CPU quota per shadow execution
            default_memory_quota_mb: Default memory quota per shadow execution
        """
        self.audit_manager = audit_manager
        self.threat_detector = threat_detector
        self.governance_service = governance_service

        # Resource limits
        self.default_cpu_quota_ms = default_cpu_quota_ms
        self.default_memory_quota_mb = default_memory_quota_mb

        # Telemetry
        self.telemetry = ShadowTelemetry()

        # Execution history (forensic auditability)
        self.shadow_history: list[ShadowContext] = []

        # Resource limiter — compiled from Shadow Thirst source
        # (resource_limiter.thirsty) with Python bridge fallback
        self._resource_limiter = ShadowResourceLimiter()
        logger.info(
            "  Resource Limiter: %s",
            "Shadow Thirst bytecode" if self._resource_limiter.is_bytecode_active() else "Python runtime",
        )

        # Register in Tier Registry as Tier-2 Infrastructure Controller
        try:
            tier_registry = get_tier_registry()
            tier_registry.register_component(
                component_id="shadow_execution_plane",
                component_name="ShadowExecutionPlane",
                tier=PlatformTier.TIER_2_INFRASTRUCTURE,
                authority_level=AuthorityLevel.CONSTRAINED,
                role=ComponentRole.INFRASTRUCTURE_CONTROLLER,
                component_ref=self,
                dependencies=["cognition_kernel"],
                can_be_paused=True,
                can_be_replaced=False,
            )
            logger.info("ShadowExecutionPlane registered as Tier-2 Infrastructure")
        except Exception as e:
            logger.warning("Failed to register ShadowExecutionPlane in tier registry: %s", e)

        logger.info("ShadowExecutionPlane initialized")
        logger.info("  CPU Quota: %.0fms", default_cpu_quota_ms)
        logger.info("  Memory Quota: %.0fMB", default_memory_quota_mb)
        logger.info("  Audit Manager: %s", audit_manager is not None)
        logger.info("  Threat Detector: %s", threat_detector is not None)

    def should_activate_shadow(
        self,
        context: dict[str, Any],
        activation_predicates: list[ActivationPredicate],
    ) -> tuple[bool, ActivationReason | None]:
        """
        Determine if shadow execution should activate.

        Evaluates all activation predicates and returns the first match.

        Args:
            context: Execution context for predicate evaluation
            activation_predicates: List of activation predicates

        Returns:
            Tuple of (should_activate, reason)
        """
        for predicate in activation_predicates:
            try:
                if predicate.evaluate(context):
                    logger.info("Shadow activation triggered: %s (%s)", predicate.name, predicate.reason.value)
                    return True, predicate.reason
            except Exception as e:
                logger.error("Activation predicate %s failed: %s", predicate.predicate_id, e)

        return False, None

    def execute_dual_plane(
        self,
        trace_id: str,
        primary_callable: Callable,
        shadow_callable: Callable | None = None,
        activation_predicates: list[ActivationPredicate] | None = None,
        invariants: list[InvariantDefinition] | None = None,
        mode: ShadowMode = ShadowMode.VALIDATION,
        divergence_policy: DivergencePolicy = DivergencePolicy.LOG_DIVERGENCE,
        mutation_boundary: MutationBoundary = MutationBoundary.READ_ONLY,
        context: dict[str, Any] | None = None,
    ) -> ShadowResult:
        """
        Execute in dual-plane mode (primary + shadow in parallel).

        This is the core dual-reality execution method.

        Pipeline:
        1. Evaluate activation predicates
        2. Execute primary (always)
        3. Execute shadow (if activated)
        4. Compare results against invariants
        5. Determine commit/quarantine decision
        6. Seal audit trail
        7. Return comprehensive result

        Args:
            trace_id: Trace ID linking to primary execution
            primary_callable: Primary execution callable
            shadow_callable: Shadow execution callable (defaults to primary)
            activation_predicates: Predicates for shadow activation
            invariants: Invariants to validate
            mode: Shadow mode (validation, simulation, etc.)
            divergence_policy: Policy for handling divergence
            mutation_boundary: What shadow can mutate
            context: Execution context

        Returns:
            ShadowResult with validation and decision data
        """
        activation_predicates = activation_predicates or []
        invariants = invariants or []
        context = context or {}
        shadow_callable = shadow_callable or primary_callable

        shadow_id = f"shadow_{uuid.uuid4().hex[:12]}"
        logger.info("[%s] Starting dual-plane execution", shadow_id)

        # Phase 1: Check activation
        should_activate, activation_reason = self.should_activate_shadow(context, activation_predicates)

        # If no activation, run primary only
        if not should_activate:
            logger.info("[%s] Shadow not activated, primary only", shadow_id)
            primary_result = primary_callable()

            return ShadowResult(
                shadow_id=shadow_id,
                trace_id=trace_id,
                success=True,
                primary_result=primary_result,
                shadow_result=None,
                invariants_passed=True,
                divergence_detected=False,
                should_commit=True,
            )

        # Shadow activated - record telemetry (activation_reason is not None here
        # because should_activate_shadow only returns True with a non-None reason)
        assert activation_reason is not None
        self.telemetry.record_activation(activation_reason)

        # Phase 2: Create shadow context
        shadow_ctx = ShadowContext(
            shadow_id=shadow_id,
            trace_id=trace_id,
            timestamp=datetime.now(UTC),
            mode=mode,
            activation_reason=activation_reason,
            activation_predicates=activation_predicates,
            divergence_policy=divergence_policy,
            mutation_boundary=mutation_boundary,
            invariants=invariants,
            cpu_quota_ms=self.default_cpu_quota_ms,
            memory_quota_mb=self.default_memory_quota_mb,
            metadata=context,
        )

        shadow_ctx.status = ShadowStatus.ACTIVATED

        # Phase 3: Execute primary
        logger.info("[%s] Executing primary plane", shadow_id)
        primary_start = time.time()

        try:
            primary_result = primary_callable()
            primary_duration = (time.time() - primary_start) * 1000
            logger.info("[%s] Primary completed in %.2fms", shadow_id, primary_duration)
        except Exception as e:
            logger.error("[%s] Primary execution failed: %s", shadow_id, e)
            shadow_ctx.status = ShadowStatus.FAILED
            shadow_ctx.error = f"Primary failed: {e}"
            return self._build_failed_result(shadow_ctx, None, None)

        # Phase 4: Execute shadow
        logger.info("[%s] Executing shadow plane (%s mode)", shadow_id, mode.value)
        shadow_ctx.status = ShadowStatus.EXECUTING
        shadow_start = time.time()

        try:
            # Execute shadow with resource limits
            shadow_result = self._execute_shadow_with_limits(shadow_callable, shadow_ctx)

            shadow_duration = (time.time() - shadow_start) * 1000
            shadow_ctx.duration_ms = shadow_duration

            logger.info("[%s] Shadow completed in %.2fms", shadow_id, shadow_duration)
            shadow_ctx.status = ShadowStatus.COMPLETED

        except ShadowResourceViolation as e:
            # Resource limit exceeded — quarantine immediately.
            # Do not fall through to invariant checks; this shadow is dead.
            shadow_duration = (time.time() - shadow_start) * 1000
            shadow_ctx.duration_ms = shadow_duration
            shadow_ctx.status = ShadowStatus.FAILED
            shadow_ctx.error = f"Resource limit exceeded: {e.reason}"
            logger.warning(
                "[%s] Shadow quarantined due to resource violation: %s",
                shadow_id,
                e.reason,
            )
            return self._build_failed_result(shadow_ctx, primary_result, None)

        except Exception as e:
            logger.error("[%s] Shadow execution failed: %s", shadow_id, e)
            shadow_ctx.status = ShadowStatus.FAILED
            shadow_ctx.error = f"Shadow failed: {e}"
            shadow_result = None

        # Record execution metrics (real measurements from resource limiter)
        _usage: ResourceUsage | None = getattr(shadow_ctx, "resource_usage", None)
        self.telemetry.record_execution(
            duration_ms=shadow_ctx.duration_ms,
            cpu_ms=_usage.cpu_ms if _usage else shadow_ctx.duration_ms,
            memory_mb=_usage.peak_memory_mb if _usage else 0.0,
        )

        # Phase 5: Validate invariants
        invariants_passed = True
        invariants_violated = []

        if shadow_result is not None:
            for invariant in invariants:
                is_valid, reason = invariant.validate(primary_result, shadow_result)

                self.telemetry.record_invariant_check(is_valid)

                if not is_valid:
                    logger.warning("[%s] Invariant violated: %s - %s", shadow_id, invariant.name, reason)
                    invariants_violated.append(invariant.name)

                    if invariant.is_critical:
                        invariants_passed = False

        # Phase 6: Check divergence
        divergence_detected, divergence_magnitude = self._check_divergence(
            primary_result, shadow_result, divergence_policy
        )

        if divergence_detected:
            shadow_ctx.divergence_detected = True
            shadow_ctx.divergence_magnitude = divergence_magnitude
            shadow_ctx.status = ShadowStatus.DIVERGED
            self.telemetry.record_divergence(divergence_magnitude)

        # Phase 7: Determine commit/quarantine decision
        should_commit, should_quarantine, quarantine_reason = self._determine_commit_decision(
            invariants_passed, divergence_detected, divergence_policy, invariants_violated
        )

        # Phase 8: Seal audit trail
        audit_hash = shadow_ctx.seal_audit_trail()

        # Phase 9: Record in history
        self.shadow_history.append(shadow_ctx)

        # Phase 10: Build result
        result = ShadowResult(
            shadow_id=shadow_id,
            trace_id=trace_id,
            success=invariants_passed and not should_quarantine,
            primary_result=primary_result,
            shadow_result=shadow_result,
            invariants_passed=invariants_passed,
            invariants_violated=invariants_violated,
            divergence_detected=divergence_detected,
            divergence_magnitude=divergence_magnitude,
            divergence_policy=divergence_policy,
            should_commit=should_commit,
            should_quarantine=should_quarantine,
            quarantine_reason=quarantine_reason,
            audit_hash=audit_hash,
            duration_ms=shadow_ctx.duration_ms,
        )

        logger.info(
            "[%s] Dual-plane execution complete: commit=%s, quarantine=%s", shadow_id, should_commit, should_quarantine
        )

        return result

    def execute_simulation(
        self,
        trace_id: str,
        simulation_callable: Callable,
        invariants: list[InvariantDefinition] | None = None,
        context: dict[str, Any] | None = None,
    ) -> ShadowResult:
        """
        Execute policy/change simulation in shadow plane only.

        Use this to test policies or changes before committing.

        Args:
            trace_id: Trace ID
            simulation_callable: Callable to simulate
            invariants: Invariants to validate
            context: Execution context

        Returns:
            ShadowResult with simulation outcomes
        """
        invariants = invariants or []
        context = context or {}

        shadow_id = f"sim_{uuid.uuid4().hex[:12]}"
        logger.info("[%s] Running simulation", shadow_id)

        shadow_ctx = ShadowContext(
            shadow_id=shadow_id,
            trace_id=trace_id,
            timestamp=datetime.now(UTC),
            mode=ShadowMode.SIMULATION,
            activation_reason=ActivationReason.POLICY_FLAG,
            divergence_policy=DivergencePolicy.LOG_DIVERGENCE,
            mutation_boundary=MutationBoundary.SHADOW_STATE_ONLY,
            invariants=invariants,
            metadata=context,
        )

        # Execute simulation
        shadow_ctx.status = ShadowStatus.EXECUTING
        start_time = time.time()

        try:
            result = self._execute_shadow_with_limits(simulation_callable, shadow_ctx)

            shadow_ctx.duration_ms = (time.time() - start_time) * 1000
            shadow_ctx.status = ShadowStatus.COMPLETED
            shadow_ctx.result = result

            logger.info("[%s] Simulation completed in %.2fms", shadow_id, shadow_ctx.duration_ms)

        except Exception as e:
            logger.error("[%s] Simulation failed: %s", shadow_id, e)
            shadow_ctx.status = ShadowStatus.FAILED
            shadow_ctx.error = str(e)
            return self._build_failed_result(shadow_ctx, None, None)

        # Validate invariants
        invariants_passed = True
        for invariant in invariants:
            # For simulation, we validate against expected outcomes in context
            expected = context.get("expected_outcome")
            if expected is not None:
                is_valid, reason = invariant.validate(expected, result)
                if not is_valid and invariant.is_critical:
                    invariants_passed = False

        # Seal and return
        audit_hash = shadow_ctx.seal_audit_trail()
        self.shadow_history.append(shadow_ctx)

        return ShadowResult(
            shadow_id=shadow_id,
            trace_id=trace_id,
            success=invariants_passed,
            primary_result=None,
            shadow_result=result,
            invariants_passed=invariants_passed,
            should_commit=False,  # Simulations never commit
            audit_hash=audit_hash,
            duration_ms=shadow_ctx.duration_ms,
        )

    def _execute_shadow_with_limits(self, callable_obj: Callable, shadow_ctx: ShadowContext) -> Any:
        """
        Execute shadow callable with resource limits.

        Enforced by ShadowResourceLimiter, which is compiled from
        resource_limiter.thirsty — a native Shadow Thirst dual-plane function
        that itself uses shadow execution to measure and bound the callable.

        Limits enforced:
        - CPU / wall-clock timeout via ThreadPoolExecutor.Future.result(timeout=)
        - Memory growth via tracemalloc peak-delta measurement

        Args:
            callable_obj: Shadow callable
            shadow_ctx: Shadow context (cpu_quota_ms, memory_quota_mb read here)

        Returns:
            Result from shadow execution

        Raises:
            ShadowResourceViolation: If CPU or memory quota exceeded
        """
        shadow_ctx.start_time = time.time()

        try:
            result, resource_usage = self._resource_limiter.execute(
                callable_obj,
                cpu_quota_ms=shadow_ctx.cpu_quota_ms,
                memory_quota_mb=shadow_ctx.memory_quota_mb,
            )

            shadow_ctx.end_time = time.time()

            # Attach real resource measurements to context for telemetry
            shadow_ctx.resource_usage = resource_usage  # type: ignore[attr-defined]

            logger.debug(
                "[%s] Resource usage: cpu=%.1fms mem=%.2fMB",
                shadow_ctx.shadow_id,
                resource_usage.cpu_ms,
                resource_usage.peak_memory_mb,
            )

            return result

        except ShadowResourceViolation as e:
            shadow_ctx.end_time = time.time()
            shadow_ctx.error = f"Resource limit exceeded: {e.reason}"
            logger.warning(
                "[%s] Shadow resource violation: %s",
                shadow_ctx.shadow_id,
                e.reason,
            )
            raise

        except Exception as e:
            shadow_ctx.end_time = time.time()
            shadow_ctx.error = str(e)
            raise

    def _check_divergence(
        self, primary_result: Any, shadow_result: Any, policy: DivergencePolicy
    ) -> tuple[bool, float]:
        """
        Check for divergence between primary and shadow results.

        Args:
            primary_result: Primary result
            shadow_result: Shadow result
            policy: Divergence policy

        Returns:
            Tuple of (divergence_detected, magnitude)
        """
        if shadow_result is None:
            return False, 0.0

        try:
            if policy == DivergencePolicy.REQUIRE_IDENTICAL:
                diverged = primary_result != shadow_result
                return diverged, 1.0 if diverged else 0.0

            elif policy == DivergencePolicy.ALLOW_EPSILON:
                if isinstance(primary_result, (int, float)) and isinstance(shadow_result, (int, float)):
                    diff = abs(primary_result - shadow_result)
                    diverged = diff > 0.01  # Default epsilon
                    return diverged, diff
                else:
                    diverged = primary_result != shadow_result
                    return diverged, 1.0 if diverged else 0.0

            else:
                # LOG_DIVERGENCE, QUARANTINE_ON_DIVERGE, FAIL_PRIMARY
                diverged = primary_result != shadow_result
                return diverged, 1.0 if diverged else 0.0

        except Exception as e:
            logger.error("Divergence check failed: %s", e)
            return True, 1.0  # Conservative: assume divergence on error

    def _determine_commit_decision(
        self,
        invariants_passed: bool,
        divergence_detected: bool,
        divergence_policy: DivergencePolicy,
        invariants_violated: list[str],
    ) -> tuple[bool, bool, str | None]:
        """
        Determine commit/quarantine decision.

        Args:
            invariants_passed: Whether all critical invariants passed
            divergence_detected: Whether divergence was detected
            divergence_policy: Divergence policy
            invariants_violated: List of violated invariant names

        Returns:
            Tuple of (should_commit, should_quarantine, quarantine_reason)
        """
        # If invariants failed, quarantine
        if not invariants_passed:
            return False, True, f"Critical invariants violated: {invariants_violated}"

        # Check divergence policy
        if divergence_detected:
            if divergence_policy == DivergencePolicy.QUARANTINE_ON_DIVERGE:
                return False, True, "Divergence detected with QUARANTINE policy"

            elif divergence_policy == DivergencePolicy.FAIL_PRIMARY:
                return False, True, "Divergence detected with FAIL_PRIMARY policy"

            elif divergence_policy == DivergencePolicy.LOG_DIVERGENCE:
                return True, False, None  # Log but allow commit

        # Default: commit
        return True, False, None

    def _build_failed_result(self, shadow_ctx: ShadowContext, primary_result: Any, shadow_result: Any) -> ShadowResult:
        """Build a failed ShadowResult."""
        audit_hash = shadow_ctx.seal_audit_trail()
        self.shadow_history.append(shadow_ctx)

        return ShadowResult(
            shadow_id=shadow_ctx.shadow_id,
            trace_id=shadow_ctx.trace_id,
            success=False,
            primary_result=primary_result,
            shadow_result=shadow_result,
            invariants_passed=False,
            should_commit=False,
            should_quarantine=True,
            quarantine_reason=shadow_ctx.error,
            audit_hash=audit_hash,
            duration_ms=shadow_ctx.duration_ms,
        )

    def get_telemetry(self) -> dict[str, Any]:
        """
        Get shadow telemetry summary.

        Returns:
            Telemetry dictionary
        """
        return self.telemetry.get_summary()

    def get_shadow_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get recent shadow execution history.

        Args:
            limit: Maximum number of executions to return

        Returns:
            List of shadow execution summaries
        """
        history = []
        for ctx in self.shadow_history[-limit:]:
            history.append(
                {
                    "shadow_id": ctx.shadow_id,
                    "trace_id": ctx.trace_id,
                    "timestamp": ctx.timestamp.isoformat(),
                    "mode": ctx.mode.value,
                    "activation_reason": ctx.activation_reason.value,
                    "status": ctx.status.value,
                    "divergence_detected": ctx.divergence_detected,
                    "divergence_magnitude": ctx.divergence_magnitude,
                    "duration_ms": ctx.duration_ms,
                    "audit_hash": ctx.audit_hash,
                }
            )
        return history


__all__ = [
    "ShadowExecutionPlane",
]
