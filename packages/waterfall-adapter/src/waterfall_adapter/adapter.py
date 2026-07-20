"""Fail-closed Project-AI boundary for Waterfall operations.

Waterfall remains independently usable and retains its runtime implementation
boundary. This module turns an explicitly allow-listed request under the shared
authority contract into a Project-AI ``ActionRequest`` and calls an injected
transport only after the canonical execution gate allows it.
"""

from __future__ import annotations

import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import timedelta
from typing import Protocol

from capability import CapabilityAuthority
from execution import ExecutionGate, ExecutionResult
from kernel import ActionRequest, JsonValue, Outcome

ADAPTER_ACTOR = "project-ai-waterfall-adapter"
CAPABILITY_TTL = timedelta(seconds=60)

# Keep this list small and explicit. Adding an operation requires a reviewed
# adapter change and a corresponding transport implementation/test.
ALLOWED_OPERATIONS = frozenset(
    {
        "vpn.connect",
        "firewall.rule_change",
        "kill_switch.trigger",
    }
)


class UnsupportedOperation(RuntimeError):
    """Raised by a transport that cannot perform a requested operation."""


class WaterfallTransport(Protocol):
    """Injected local transport; it must not hold Project-AI authority."""

    def execute(
        self,
        operation: str,
        resource: str,
        payload: Mapping[str, JsonValue],
    ) -> JsonValue:
        """Perform one already-authorized Waterfall operation."""


@dataclass(frozen=True)
class AdapterResult:
    """Stable adapter response with gate evidence when available."""

    action_id: str
    outcome: Outcome
    reason: str
    output: JsonValue = None
    governance_evidence_sha256: str = ""
    event_hash: str = ""

    @classmethod
    def from_execution(cls, result: ExecutionResult) -> AdapterResult:
        return cls(
            action_id=result.action_id,
            outcome=result.outcome,
            reason=result.reason,
            output=result.output,
            governance_evidence_sha256=result.governance_evidence_sha256,
            event_hash=result.event_hash,
        )


class WaterfallAdapter:
    """Submit explicitly scoped Waterfall operations through ``ExecutionGate``."""

    def __init__(
        self,
        *,
        execution_gate: ExecutionGate | None = None,
        capability_authority: CapabilityAuthority | None = None,
        transport: WaterfallTransport | None = None,
        actor: str = ADAPTER_ACTOR,
    ) -> None:
        if not actor.strip():
            raise ValueError("actor must not be empty")
        self._execution_gate = execution_gate
        self._capability_authority = capability_authority
        self._transport = transport
        self._actor = actor

    def submit(
        self,
        operation: str,
        *,
        resource: str,
        payload: Mapping[str, JsonValue] | None = None,
        state: Mapping[str, object] | None = None,
    ) -> AdapterResult:
        """Submit one Waterfall operation, denying all incomplete wiring."""
        action_id = f"waterfall-{uuid.uuid4().hex}"
        if operation not in ALLOWED_OPERATIONS:
            return self._denied(action_id, f"operation not allow-listed: {operation}")
        if not resource.strip():
            return self._denied(action_id, "resource must not be empty")
        if self._execution_gate is None:
            return self._denied(action_id, "execution gate is not configured")
        if self._capability_authority is None:
            return self._denied(action_id, "capability authority is not configured")
        transport = self._transport
        if transport is None:
            return self._denied(action_id, "Waterfall transport is not configured")

        request = ActionRequest(
            action_id=action_id,
            actor=self._actor,
            operation=operation,
            resource=resource,
            payload=payload or {},
        )
        token = self._capability_authority.issue(
            subject=self._actor,
            operation=operation,
            resource=resource,
            ttl=CAPABILITY_TTL,
        )

        def execute(_: ActionRequest) -> JsonValue:
            return transport.execute(operation, resource, request.payload)

        result = self._execution_gate.submit_action(
            request,
            capability_token=token,
            executor=execute,
            state=state,
        )
        return AdapterResult.from_execution(result)

    def _denied(self, action_id: str, reason: str) -> AdapterResult:
        return AdapterResult(action_id=action_id, outcome=Outcome.DENY, reason=reason)

    @property
    def v3q_configured(self) -> bool:
        """Expose the gate's V3Q wiring without exposing its private state."""
        return self._execution_gate is not None and self._execution_gate.v3q_configured
