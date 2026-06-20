"""Sole fail-closed execution path for every Project-AI actuation."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from capability import CapabilityAuthority, CapabilityError
from governance import GovernanceEngine
from kernel import ActionRequest, EventSpine, JsonValue, Outcome
from security import AppendOnlyAuditRelay, report_governance_denial

type Executor = Callable[[ActionRequest], JsonValue]


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
    ) -> None:
        self._governance = governance
        self._capabilities = capabilities
        self._events = events
        self._chimera_relay = chimera_relay

    def submit_action(
        self,
        request: ActionRequest,
        *,
        capability_token: str,
        executor: Executor,
        state: Mapping[str, object] | None = None,
    ) -> ExecutionResult:
        self._events.append("execution.request_received", {"action_id": request.action_id})
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
