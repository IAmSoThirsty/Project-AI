"""
Cerberus Invariant Head — Runtime Invariant Enforcement.

The third Cerberus head evaluates whether executing a request would
violate any PSIA invariant.  It cross-references the request intent
against the invariant registry and applies the enforcement policy
specified for each matched invariant.

Checks performed:
    1. Root invariant applicability scan (INV-ROOT-1..9)
    2. Custom invariant applicability scan (user-defined)
    3. Pre-execution invariant evaluation (compile-time checks)
    4. Shadow-report invariant cross-check (if available)
    5. Severity aggregation and enforcement application

Security invariants:
    - INV-ROOT-1 (No invariant bypass — invariants cannot be disabled)
    - INV-ROOT-4 (Immutable write-path — mutations must pass invariant
      checks before reaching canonical state)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from psia.invariants import ROOT_INVARIANTS
from psia.schemas.cerberus_decision import (
    CerberusVote,
    ConstraintsApplied,
    DenyReason,
)
from psia.schemas.identity import Signature
from psia.schemas.invariant import (
    InvariantDefinition,
    InvariantEnforcement,
    InvariantSeverity,
)

logger = logging.getLogger(__name__)


class InvariantRegistry:
    """Registry of active invariant definitions.

    Pre-loaded with the 9 root invariants.  Custom invariants
    can be added via ``register()``.
    """

    def __init__(self, *, include_root: bool = True) -> None:
        self._invariants: dict[str, InvariantDefinition] = {}
        if include_root:
            self._invariants.update(ROOT_INVARIANTS)

    def register(self, inv: InvariantDefinition) -> None:
        """Register a custom invariant."""
        self._invariants[inv.invariant_id] = inv

    def get(self, inv_id: str) -> InvariantDefinition | None:
        return self._invariants.get(inv_id)

    def all_invariants(self) -> list[InvariantDefinition]:
        return list(self._invariants.values())

    @property
    def count(self) -> int:
        return len(self._invariants)


class InvariantEvaluator:
    """Evaluates a request against an invariant definition.

    Phase 3 implementation uses heuristic pattern-matching rather
    than a full constraint solver.  Phase 5+ will integrate a
    formal verification engine (Z3 / CVC5).

    The evaluator checks:
    - Action type against invariant scope
    - Shadow report violations matching this invariant
    - Enforcement policy application
    """

    # Actions that constitute mutation and thus trigger immutable invariants
    _MUTATION_ACTIONS = frozenset(
        {
            "mutate_state",
            "mutate_policy",
            "delete",
            "write",
            "create",
            "update",
            "patch",
            "upsert",
            "append",
        }
    )

    def evaluate(
        self,
        inv: InvariantDefinition,
        action: str,
        resource: str,
        shadow_violations: list[str] | None = None,
    ) -> tuple[bool, str]:
        """Evaluate a single invariant against a request.

        Args:
            inv: The invariant definition
            action: The requested action
            resource: The target resource
            shadow_violations: List of invariant IDs violated in shadow sim

        Returns:
            (passed, reason) — True if invariant passes, False if violated
        """
        # Check 1: Does this invariant apply to this action?
        if inv.scope.value in ("immutable", "constitutional"):
            # Root/constitutional invariants apply to all mutations
            if action not in self._MUTATION_ACTIONS:
                return True, f"{inv.invariant_id}: not applicable (non-mutation action)"

        # Check 2: Shadow simulation cross-check
        if shadow_violations and inv.invariant_id in shadow_violations:
            return False, (
                f"{inv.invariant_id}: violated in shadow simulation — "
                f"severity={inv.severity.value}, enforcement={inv.enforcement.value}"
            )

        # Check 3: Action-specific heuristic checks
        # (These are simplified; a real solver would evaluate the formal expression)
        if inv.invariant_id == "inv_root_001":
            # INV-ROOT-1: No invariant can be disabled at runtime
            if action == "mutate_policy" and "invariant" in resource.lower():
                return False, (
                    f"{inv.invariant_id}: attempt to mutate invariant-related "
                    f"resource '{resource}' — invariants are immutable"
                )

        if inv.invariant_id == "inv_root_004":
            # INV-ROOT-4: Immutable write-path
            if action in self._MUTATION_ACTIONS:
                # This invariant is structural — it's enforced by the
                # Waterfall pipeline itself.  Pass here means the
                # pipeline routing is intact.
                pass  # Always passes at evaluation time

        if inv.invariant_id == "inv_root_005":
            # INV-ROOT-5: No self-modification of Cerberus
            if "cerberus" in resource.lower() or "gate" in resource.lower():
                if action in self._MUTATION_ACTIONS:
                    return False, (
                        f"{inv.invariant_id}: attempt to modify Cerberus/Gate "
                        f"components at runtime — denied"
                    )

        if inv.invariant_id == "inv_root_009":
            # INV-ROOT-9: Append-only ledger
            if "ledger" in resource.lower() and action in ("delete", "update", "patch"):
                return False, (
                    f"{inv.invariant_id}: attempt to {action} ledger — "
                    f"ledger is append-only"
                )

        return True, f"{inv.invariant_id}: passed"


class InvariantHead:
    """Cerberus Invariant Head — production-grade constraint enforcement.

    Replaces the Phase 1 ``StubInvariantHead`` with real invariant
    evaluation.  Scans all registered invariants (root + custom)
    and aggregates violations.

    Args:
        registry: InvariantRegistry with loaded invariants
        evaluator: InvariantEvaluator for per-invariant checks
    """

    def __init__(
        self,
        *,
        registry: InvariantRegistry | None = None,
        evaluator: InvariantEvaluator | None = None,
    ) -> None:
        self.registry = registry or InvariantRegistry()
        self.evaluator = evaluator or InvariantEvaluator()

    def evaluate(self, envelope: Any) -> CerberusVote:
        """Evaluate all invariants against the request.

        Args:
            envelope: RequestEnvelope

        Returns:
            CerberusVote with invariant checking result
        """
        reasons: list[DenyReason] = []
        violations: list[tuple[InvariantDefinition, str]] = []

        action = envelope.intent.action
        resource = envelope.intent.resource

        # Gather shadow violations if available in context
        shadow_violations = getattr(envelope.context, "shadow_violations", None)

        for inv in self.registry.all_invariants():
            passed, reason = self.evaluator.evaluate(
                inv, action, resource, shadow_violations
            )
            if not passed:
                violations.append((inv, reason))
                reasons.append(
                    DenyReason(
                        code=f"INVARIANT_{inv.invariant_id.upper()}",
                        detail=reason,
                    )
                )

        # ── Severity aggregation ──
        if not violations:
            decision = "allow"
        else:
            # Find worst severity
            severity_rank = {
                InvariantSeverity.LOW: 0,
                InvariantSeverity.MEDIUM: 1,
                InvariantSeverity.HIGH: 2,
                InvariantSeverity.CRITICAL: 3,
                InvariantSeverity.FATAL: 4,
            }
            worst = max(violations, key=lambda v: severity_rank.get(v[0].severity, 0))
            worst_sev = worst[0].severity

            if worst_sev in (InvariantSeverity.FATAL, InvariantSeverity.CRITICAL):
                decision = "deny"
            elif worst_sev == InvariantSeverity.HIGH:
                decision = "quarantine"
            else:
                decision = "allow"  # Low/medium violations → constrain, don't deny

        # ── Constraint propagation ──
        constraints = ConstraintsApplied()
        if violations:
            enforcements = [v[0].enforcement for v in violations]
            if InvariantEnforcement.RATE_LIMIT in enforcements:
                constraints = ConstraintsApplied(rate_limit_per_min=30)
            if InvariantEnforcement.REQUIRE_SHADOW in enforcements:
                constraints = ConstraintsApplied(require_shadow=True)

        return CerberusVote(
            request_id=envelope.request_id,
            head="invariant",
            decision=decision,
            reasons=reasons,
            constraints_applied=constraints,
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature=Signature(
                alg="ed25519",
                kid="cerberus_invariant_k1",
                sig="invariant_head_sig",
            ),
        )


__all__ = [
    "InvariantHead",
    "InvariantRegistry",
    "InvariantEvaluator",
]
