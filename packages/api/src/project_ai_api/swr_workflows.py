"""Execution-gate-backed Sovereign War Room workflow for reviewed human requests."""

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Annotated

from fastapi import Cookie, Depends, FastAPI, Header, HTTPException, Request

from accounts import Account, AccountService, AccountServiceError, StoredSession
from capability import CapabilityAuthority
from execution import ExecutionGate
from governance import GovernanceEngine, Rule, RuleGovernor
from kernel import ActionRequest, EventSpine, Outcome
from project_ai_api.auth import SESSION_COOKIE, _require_same_origin
from project_ai_api.models import (
    SwrExecutionRequest,
    SwrExecutionResponse,
    SwrScenarioResponse,
    SwrScenariosResponse,
)
from project_ai_api.workflows import execution_receipt_response
from security import AppendOnlyAuditRelay
from swr import WarRoomCore
from workflows import ExecutionStatus, WorkflowConflict, WorkflowPermissionDenied, WorkflowService

SWR_MODULE_ID = "swr"
SWR_REQUEST_OPERATION = "scenario.prepare"
SWR_SERVICE_ACTOR = "project-ai-control-center-swr"
SWR_AUTHORITY_BOUNDARY = (
    "A human review authorizes only the server to submit this bounded analytical record "
    "to the canonical execution gate. The browser never receives a capability token."
)


def _review_approved(_request: ActionRequest, state: Mapping[str, object]) -> bool:
    return state.get("human_review_state") == "reviewed_approve"


def _operation_bound(_request: ActionRequest, state: Mapping[str, object]) -> bool:
    return state.get("request_operation") == SWR_REQUEST_OPERATION


def _resource_bound(request: ActionRequest, state: Mapping[str, object]) -> bool:
    scenario_id = state.get("scenario_id")
    request_resource = state.get("request_resource")
    action_resource = getattr(request, "resource", None)
    return (
        isinstance(scenario_id, str)
        and request_resource == f"scenario:{scenario_id}"
        and action_resource == f"swr:{scenario_id}"
    )


def _decision_bound(request: ActionRequest, state: Mapping[str, object]) -> bool:
    expected = state.get("expected_decision")
    return isinstance(expected, str) and request.payload.get("decision") == expected


def build_swr_runtime(secret: str, *, bundle_dir: Path | str | None = None) -> WarRoomCore:
    secret_bytes = secret.encode("utf-8")
    if len(secret_bytes) < 32:
        raise ValueError("PROJECT_AI_EXECUTION_SECRET must contain at least 32 UTF-8 bytes")
    governor = RuleGovernor(
        "control-center-swr",
        (
            Rule(
                "review-approved",
                _review_approved,
                Outcome.DENY,
                "durable human review approval is missing",
            ),
            Rule(
                "operation-bound",
                _operation_bound,
                Outcome.DENY,
                "reviewed request operation is not scenario.prepare",
            ),
            Rule(
                "resource-bound",
                _resource_bound,
                Outcome.DENY,
                "reviewed request resource does not match the scenario",
            ),
            Rule(
                "decision-bound",
                _decision_bound,
                Outcome.DENY,
                "submitted decision does not match the canonical scenario decision",
            ),
        ),
    )
    capabilities = CapabilityAuthority(secret_bytes, issuer="project-ai-control-center")
    execution = ExecutionGate(
        governance=GovernanceEngine(
            policy_version="control-center-swr-v1",
            governors=(governor,),
        ),
        capabilities=capabilities,
        events=EventSpine(),
    )
    runtime = WarRoomCore(
        execution=execution,
        capabilities=capabilities,
        bundle_dir=bundle_dir,
    )
    runtime.load_scenarios()
    return runtime


def install_swr_workflow_routes(
    application: FastAPI,
    accounts: AccountService | None,
    workflows: WorkflowService | None,
    runtime: WarRoomCore | None,
    audit_relay: AppendOnlyAuditRelay | None,
) -> None:
    def current(
        session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
    ) -> tuple[Account, StoredSession]:
        if accounts is None or workflows is None:
            raise HTTPException(status_code=503, detail="Human workflow storage is not configured")
        if not session_token:
            raise HTTPException(status_code=401, detail="Sign in required")
        try:
            bundle: tuple[Account, StoredSession] = accounts.authenticate(session_token)
            return bundle
        except AccountServiceError as error:
            raise HTTPException(status_code=401, detail=str(error)) from error

    def active_workflows() -> WorkflowService:
        if workflows is None:
            raise HTTPException(status_code=503, detail="Human workflow storage is not configured")
        return workflows

    @application.get("/api/v1/modules/swr/scenarios", response_model=SwrScenariosResponse)
    def scenarios(
        _session: Annotated[tuple[Account, StoredSession], Depends(current)],
    ) -> SwrScenariosResponse:
        source = runtime.load_scenarios() if runtime is not None else ()
        return SwrScenariosResponse(
            scenarios=tuple(SwrScenarioResponse.model_validate(item.to_dict()) for item in source),
            execution_gate_configured=runtime is not None and audit_relay is not None,
            authority_boundary=SWR_AUTHORITY_BOUNDARY,
        )

    @application.post(
        "/api/v1/work/requests/{request_id}/execute/swr",
        response_model=SwrExecutionResponse,
    )
    def execute_swr(
        request_id: str,
        payload: SwrExecutionRequest,
        request: Request,
        session: Annotated[tuple[Account, StoredSession], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> SwrExecutionResponse:
        _require_same_origin(request)
        account, stored_session = session
        if accounts is None:
            raise HTTPException(status_code=503, detail="Human account storage is not configured")
        if runtime is None or audit_relay is None:
            raise HTTPException(
                status_code=503,
                detail="SWR execution gate and durable audit relay are not configured",
            )
        valid, _ = audit_relay.verify()
        if not valid:
            raise HTTPException(status_code=503, detail="Audit hash chain verification failed")
        scenario = runtime.get_scenario(payload.scenario_id)
        if scenario is None:
            raise HTTPException(status_code=404, detail="SWR scenario does not exist")
        if payload.decision != scenario.expected_decision:
            raise HTTPException(
                status_code=409,
                detail="Decision does not match the canonical reviewed scenario input",
            )
        try:
            accounts.require_csrf(stored_session, csrf_token)
            reviewed_request, receipt, created = active_workflows().begin_execution(
                account,
                request_id,
                module_id=SWR_MODULE_ID,
                expected_operation=SWR_REQUEST_OPERATION,
                expected_resource=f"scenario:{scenario.scenario_id}",
                mfa_verified_at=stored_session.mfa_verified_at,
            )
        except AccountServiceError as error:
            raise HTTPException(status_code=403, detail=str(error)) from error
        except WorkflowPermissionDenied as error:
            raise HTTPException(status_code=403, detail=str(error)) from error
        except WorkflowConflict as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        if not created:
            return SwrExecutionResponse(
                receipt=execution_receipt_response(receipt),
                reused_existing_receipt=True,
            )

        governance_state = {
            "human_review_state": reviewed_request.state.value,
            "request_operation": reviewed_request.operation,
            "request_resource": reviewed_request.resource,
            "scenario_id": scenario.scenario_id,
            "expected_decision": scenario.expected_decision,
        }
        try:
            result = runtime.execute_scenario(
                scenario,
                {"decision": payload.decision, "reasoning": {}},
                system_id=SWR_SERVICE_ACTOR,
                governance_state=governance_state,
            )
            action_id = str(result.get("gate_action_id", ""))
            outcome = str(result.get("gate_outcome", "DENY"))
            reason = str(result.get("gate_reason", ""))
            evidence_hash = str(result.get("gate_evidence_sha256", ""))
            event_hash = str(result.get("gate_event_hash", ""))
            audit_record = audit_relay.append(
                "control_center.swr_execution",
                {
                    "action_id": action_id,
                    "attempt_id": receipt.attempt_id,
                    "event_hash": event_hash,
                    "governance_evidence_sha256": evidence_hash,
                    "initiated_by": account.id,
                    "outcome": outcome,
                    "request_id": request_id,
                    "scenario_id": scenario.scenario_id,
                },
            )
            terminal = (
                ExecutionStatus.EXECUTED
                if outcome == Outcome.ALLOW.value and result.get("recorded") is True
                else ExecutionStatus.BLOCKED
            )
            finished = active_workflows().finish_execution(
                request_id,
                status=terminal,
                action_id=action_id,
                outcome=outcome,
                reason=reason,
                output_json=json.dumps(
                    result, ensure_ascii=True, separators=(",", ":"), sort_keys=True
                ),
                governance_evidence_sha256=evidence_hash,
                event_hash=event_hash,
                audit_hash=str(audit_record["hash"]),
            )
        except WorkflowConflict as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        except Exception as error:
            failure_reason = (
                f"SWR execution failed before a complete receipt: {type(error).__name__}"
            )
            try:
                failure_audit = audit_relay.append(
                    "control_center.swr_execution_failed",
                    {
                        "attempt_id": receipt.attempt_id,
                        "initiated_by": account.id,
                        "reason": failure_reason,
                        "request_id": request_id,
                        "scenario_id": scenario.scenario_id,
                    },
                )
                audit_hash = str(failure_audit["hash"])
            except Exception:
                audit_hash = ""
            try:
                finished = active_workflows().finish_execution(
                    request_id,
                    status=ExecutionStatus.FAILED,
                    action_id="",
                    outcome="",
                    reason=failure_reason,
                    output_json="{}",
                    governance_evidence_sha256="",
                    event_hash="",
                    audit_hash=audit_hash,
                )
            except WorkflowConflict as storage_error:
                raise HTTPException(status_code=409, detail=str(storage_error)) from storage_error
            return SwrExecutionResponse(
                receipt=execution_receipt_response(finished),
                reused_existing_receipt=False,
            )
        return SwrExecutionResponse(
            receipt=execution_receipt_response(finished),
            reused_existing_receipt=False,
        )
