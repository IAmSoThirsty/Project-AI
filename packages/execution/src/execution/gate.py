"""Sole fail-closed execution path for every Project-AI actuation."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from capability import CapabilityAuthority, CapabilityError
from governance import GovernanceEngine
from kernel import ActionRequest, EventSpine, JsonValue, Outcome
from security import AppendOnlyAuditRelay, report_governance_denial

type Executor = Callable[[ActionRequest], JsonValue]


# Thirsty's Standard V3 + Q gate is an optional, fail-closed pre-check that runs
# in front of the existing GovernanceEngine decision. It is injected by callers
# that opt into V3Q governance; when absent the gate behaves exactly as before.
# Import is lazy so the execution package's import graph never hard-depends on
# the v3q package (kept optional per the integration plan).
try:  # pragma: no cover - exercised only when v3q_gate is supplied
    from thirstys_standard_runtime.integration import ThirstysV3QGate

    _HAVE_THIRSTYS_V3Q = True
except Exception:  # pragma: no cover
    ThirstysV3QGate = Any  # type: ignore[assignment, misc]
    _HAVE_THIRSTYS_V3Q = False


@dataclass(frozen=True)
class ExecutionResult:
    action_id: str
    outcome: Outcome
    reason: str
    output: JsonValue
    governance_evidence_sha256: str
    event_hash: str


class ExecutionGate:
    def __init__(
        self,
        *,
        governance: GovernanceEngine,
        capabilities: CapabilityAuthority,
        events: EventSpine,
        chimera_relay: AppendOnlyAuditRelay | None = None,
        v3q_gate: ThirstysV3QGate | None = None,
        v3q_allow_on_cel_indeterminate: bool = False,
    ) -> None:
        self._governance = governance
        self._capabilities = capabilities
        self._events = events
        self._chimera_relay = chimera_relay
        self._v3q_gate = v3q_gate
        # When cel-python is unavailable the V3Q gate cannot evaluate
        # ``applies_when`` applicability and reports ``cel_unavailable``. The
        # fail-closed default is to DENY rather than silently pass
        # applicability; opt in to allow-by-flag only when the caller has
        # accepted that risk explicitly.
        self._v3q_allow_on_cel_indeterminate = v3q_allow_on_cel_indeterminate

    def submit_action(
        self,
        request: ActionRequest,
        *,
        capability_token: str,
        executor: Executor,
        state: Mapping[str, object] | None = None,
    ) -> ExecutionResult:
        self._events.append("execution.request_received", {"action_id": request.action_id})
        v3q_block = self._evaluate_v3q(request, state)
        if v3q_block is not None:
            return v3q_block
        try:
            governance = self._governance.decide(request, state)
        except Exception as error:
            return self._deny(
                request,
                f"governance evaluation failed: {type(error).__name__}",
                evidence_hash="",
            )
        evidence_hash = governance.evidence.bundle_sha256
        if governance.decision.outcome is not Outcome.ALLOW:
            reason = "; ".join(governance.decision.reasons)
            return self._finish(
                request,
                governance.decision.outcome,
                reason,
                None,
                evidence_hash,
            )
        try:
            claims = self._capabilities.consume(
                capability_token,
                subject=request.actor,
                operation=request.operation,
                resource=request.resource,
            )
        except CapabilityError as error:
            return self._deny(request, str(error), evidence_hash=evidence_hash)
        self._events.append(
            "execution.authorized",
            {"action_id": request.action_id, "capability_id": claims.token_id},
        )
        try:
            output = executor(request)
        except Exception as error:
            return self._deny(
                request,
                f"executor failed: {type(error).__name__}",
                evidence_hash=evidence_hash,
            )
        return self._finish(request, Outcome.ALLOW, "", output, evidence_hash)

    def with_v3q(
        self,
        v3q_gate: ThirstysV3QGate,
        *,
        allow_cel_indeterminate: bool = False,
    ) -> ExecutionGate:
        """Return a copy of this gate with the V3Q pre-check enabled.

        Reuses the exact same fail-closed evaluation as the original, just with
        ``v3q_gate`` set. Call sites that receive a fully-built ``ExecutionGate``
        can opt into V3Q governance without reconstructing it.
        """
        return ExecutionGate(
            governance=self._governance,
            capabilities=self._capabilities,
            events=self._events,
            chimera_relay=self._chimera_relay,
            v3q_gate=v3q_gate,
            v3q_allow_on_cel_indeterminate=allow_cel_indeterminate,
        )

    def _evaluate_v3q(
        self,
        request: ActionRequest,
        state: Mapping[str, object] | None,
    ) -> ExecutionResult | None:
        """Optional fail-closed Thirsty's Standard V3 + Q pre-check.

        Returns a DENY ``ExecutionResult`` when V3Q rejects the action, or
        ``None`` to proceed to the normal governance path. When no ``v3q_gate``
        is configured this is a no-op (behavior identical to before).

        Mapping: the caller may supply a fully-formed V3Q task/action/proof via
        ``state["v3q_action"]`` / ``state["v3q_authority_proof"]`` /
        ``state["v3q_approval_proof"]``. Otherwise a best-effort mapping is
        derived from the ``ActionRequest``; missing authority fails closed.
        """
        if self._v3q_gate is None:
            return None
        state_map = state if isinstance(state, Mapping) else {}
        override = state_map.get("v3q_action")
        if isinstance(override, dict):
            task = override.get("task", {"task_id": request.resource or request.action_id})
            action = override.get("action", {})
            # Authority/approval proofs may live inside the override or as
            # sibling top-level state keys (state["v3q_authority_proof"]).
            authority_proof = override.get("authority_proof") or state_map.get("v3q_authority_proof")
            approval_proof = override.get("approval_proof") or state_map.get("v3q_approval_proof")
        else:
            task = {"task_id": request.resource or request.action_id}
            action = {
                "action_id": request.action_id,
                "class": request.operation,
                "type": request.operation,
            }
            authority_proof = state_map.get("v3q_authority_proof")
            approval_proof = state_map.get("v3q_approval_proof")
        try:
            decision = self._v3q_gate.decide(
                task, action, authority_proof, approval_proof
            )
        except Exception as error:  # gate must never crash the executor open
            return self._deny(
                request,
                f"v3q gate error: {type(error).__name__}: {error}",
                evidence_hash="",
            )
        if decision.get("cel_unavailable") and not self._v3q_allow_on_cel_indeterminate:
            return self._deny(
                request,
                "v3q gate: CEL applicability undetermined (cel-python unavailable) — failing closed",
                evidence_hash="",
            )
        if decision.get("decision") in ("deny",):
            return self._deny(
                request,
                f"v3q gate: {decision.get('reason', 'denied')}",
                evidence_hash="",
            )
        # "allow" / "require_approval" -> proceed to normal governance.
        return None

    def _deny(
        self,
        request: ActionRequest,
        reason: str,
        *,
        evidence_hash: str,
    ) -> ExecutionResult:
        return self._finish(request, Outcome.DENY, reason, None, evidence_hash)

    def _finish(
        self,
        request: ActionRequest,
        outcome: Outcome,
        reason: str,
        output: JsonValue,
        evidence_hash: str,
    ) -> ExecutionResult:
        event = self._events.append(
            "execution.completed" if outcome is Outcome.ALLOW else "execution.blocked",
            {
                "action_id": request.action_id,
                "outcome": outcome.value,
                "reason": reason,
            },
        )
        if outcome is not Outcome.ALLOW:
            self._relay_denial(request.action_id, reason or outcome.value)
        return ExecutionResult(
            action_id=request.action_id,
            outcome=outcome,
            reason=reason,
            output=output,
            governance_evidence_sha256=evidence_hash,
            event_hash=event.event_hash,
        )

    def _relay_denial(self, action_id: str, reason: str) -> None:
        if self._chimera_relay is None:
            return
        try:
            report_governance_denial(
                self._chimera_relay,
                action_id=action_id,
                reason=reason,
            )
        except Exception:
            self._events.append(
                "execution.chimera_relay_failed",
                {"action_id": action_id},
            )


def submit_action(
    gate: ExecutionGate,
    request: ActionRequest,
    *,
    capability_token: str,
    executor: Executor,
    state: Mapping[str, object] | None = None,
) -> ExecutionResult:
    """Compatibility function that still routes through the sole execution gate."""
    return gate.submit_action(
        request,
        capability_token=capability_token,
        executor=executor,
        state=state,
    )
