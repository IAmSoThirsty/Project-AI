"""Authenticated Waterfall routes backed by the shared authority contract."""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from fastapi import Depends, FastAPI, HTTPException, Request, status
from project_ai_waterfall import InProcessWaterfallTransport
from project_ai_waterfall.transport import WaterfallRuntime
from thirstys_standard_runtime.integration import build_gate
from waterfall_adapter import ALLOWED_OPERATIONS, WaterfallAdapter

from capability import CapabilityAuthority
from execution import ExecutionGate
from governance import GovernanceEngine, Rule, RuleGovernor
from kernel import EventSpine, Outcome
from project_ai_api.models import (
    WaterfallOperationRequest,
    WaterfallOperationResponse,
    WaterfallStatusResponse,
)
from security import AppendOnlyAuditRelay

type MachineAuthDependency = Callable[[], None]
type MachineAuthFactory = Callable[[str], MachineAuthDependency]

WATERFALL_OPERATION_TO_ACTION = {
    "vpn.connect": ("security_sensitive", "modify_security_policy"),
    "firewall.rule_change": ("security_sensitive", "modify_security_policy"),
    "kill_switch.trigger": ("security_sensitive", "modify_security_policy"),
}


def build_waterfall_integration(
    *,
    enabled: bool,
    config_path: Path | None,
    execution_secret: str | None,
    audit_relay: AppendOnlyAuditRelay | None,
) -> tuple[WaterfallRuntime | None, WaterfallAdapter | None]:
    """Build the live Waterfall boundary only when explicitly enabled."""
    if not enabled:
        return None, None
    if audit_relay is None:
        raise ValueError("Waterfall activation requires a configured audit relay")
    if execution_secret is None or len(execution_secret.encode("utf-8")) < 32:
        raise ValueError("Waterfall activation requires a 32-byte execution secret")
    if os.getenv("THIRSTYS_V3Q_REQUIRED", "false").lower() not in {
        "1",
        "true",
        "yes",
        "on",
    }:
        raise ValueError("Waterfall activation requires THIRSTYS_V3Q_REQUIRED=true")
    v3q_gate = build_gate(operation_to_action=WATERFALL_OPERATION_TO_ACTION)
    if v3q_gate is None:
        raise ValueError("Waterfall activation requires a configured V3Q trusted-key registry")

    capabilities = CapabilityAuthority(
        execution_secret.encode("utf-8"),
        issuer="project-ai-waterfall",
    )

    def _operation_bound(request: Any, _state: Any) -> bool:
        return request.operation in ALLOWED_OPERATIONS

    execution = ExecutionGate(
        governance=GovernanceEngine(
            policy_version="project-ai-waterfall-v1",
            governors=(
                RuleGovernor(
                    "waterfall-operation-boundary",
                    (
                        Rule(
                            "allow-listed-operation",
                            _operation_bound,
                            Outcome.DENY,
                            "Waterfall operation is not allow-listed",
                        ),
                    ),
                ),
            ),
        ),
        capabilities=capabilities,
        events=EventSpine(),
        chimera_relay=audit_relay,
        v3q_gate=v3q_gate,
    )

    runtime_module = __import__("thirstys_waterfall", fromlist=["ThirstysWaterfall"])
    runtime_type = cast(Any, runtime_module).ThirstysWaterfall
    runtime = cast(WaterfallRuntime, runtime_type(str(config_path) if config_path else None))
    adapter = WaterfallAdapter(
        execution_gate=execution,
        capability_authority=capabilities,
        transport=InProcessWaterfallTransport(runtime),
    )
    return runtime, adapter


def install_waterfall_routes(
    application: FastAPI,
    *,
    adapter: WaterfallAdapter | None,
    runtime: WaterfallRuntime | None,
    require_machine_scope: MachineAuthFactory,
    audit_relay: AppendOnlyAuditRelay | None,
) -> None:
    """Install fail-closed status and operation routes.

    The route never calls the copied runtime directly. Consequential operations
    enter through ``WaterfallAdapter`` and therefore the canonical
    ``ExecutionGate``. A durable audit relay is required for both status and
    operation evidence.
    """

    machine_protected = [Depends(require_machine_scope("evidence.read"))]
    machine_write_protected = [Depends(require_machine_scope("evidence.write"))]

    def configured_relay() -> AppendOnlyAuditRelay:
        if audit_relay is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Waterfall audit relay is not configured",
            )
        try:
            valid, _ = audit_relay.verify()
        except (OSError, ValueError):
            valid = False
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audit hash chain verification failed",
            )
        return audit_relay

    @application.get(
        "/api/v1/modules/waterfall/status",
        response_model=WaterfallStatusResponse,
        dependencies=machine_protected,
    )
    def waterfall_status() -> WaterfallStatusResponse:
        relay = configured_relay()
        if runtime is None:
            relay.append("waterfall.status", {"configured": False})
            return WaterfallStatusResponse(configured=False)
        return WaterfallStatusResponse(
            configured=adapter is not None and adapter.v3q_configured,
            runtime_status=runtime.get_status(),
        )

    @application.post(
        "/api/v1/modules/waterfall/operations",
        response_model=WaterfallOperationResponse,
        dependencies=machine_write_protected,
    )
    def waterfall_operation(
        payload: WaterfallOperationRequest,
        request: Request,
    ) -> WaterfallOperationResponse:
        relay = configured_relay()
        if adapter is None or not adapter.v3q_configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Waterfall adapter and V3Q execution gate are not configured",
            )
        result = adapter.submit(
            payload.operation,
            resource=payload.resource,
            payload=payload.payload,
            state=payload.state,
        )
        audit = relay.append(
            "waterfall.operation",
            {
                "action_id": result.action_id,
                "operation": payload.operation,
                "resource": payload.resource,
                "outcome": result.outcome.value,
                "governance_evidence_sha256": result.governance_evidence_sha256,
                "event_hash": result.event_hash,
                **(
                    {
                        "machine_credential_id": request.state.machine_credential.id,
                        "machine_credential_label": request.state.machine_credential.label,
                    }
                    if getattr(request.state, "machine_credential", None) is not None
                    else {}
                ),
            },
        )
        return WaterfallOperationResponse(
            action_id=result.action_id,
            outcome=result.outcome.value,
            reason=result.reason,
            output=result.output,
            governance_evidence_sha256=result.governance_evidence_sha256,
            event_hash=result.event_hash,
            audit_hash=str(audit["hash"]),
        )
