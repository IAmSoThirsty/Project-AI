"""Human-session Atlas analysis workflows with no authority or actuation."""

import hashlib
import json
from typing import Annotated, Any

from fastapi import Cookie, Depends, FastAPI, Header, HTTPException, Query, Request, status

from accounts import (
    Account,
    AccountService,
    AccountServiceError,
    InterfacePermission,
    PermissionDenied,
    StoredSession,
)
from atlas import (
    Claim,
    ClaimType,
    Evidence,
    EvidenceTier,
    ReplayBundle,
    ReplaySystem,
    ReplaySystemError,
    analyze,
)
from project_ai_api.auth import SESSION_COOKIE, _require_same_origin
from project_ai_api.models import (
    AtlasProjectionCreate,
    AtlasProjectionCreateResponse,
    AtlasProjectionDriverInput,
    AtlasProjectionEvidenceInput,
    AtlasProjectionResponse,
    AtlasProjectionsResponse,
    AtlasReplayItemCounts,
    AtlasReplayRequest,
    AtlasReplayResponse,
)
from security import AppendOnlyAuditRelay
from workflows import (
    AnalysisReceipt,
    WorkflowConflict,
    WorkflowPermissionDenied,
    WorkflowService,
)

MAX_ATLAS_REQUEST_BYTES = 256 * 1024
ATLAS_PROJECTION_OPERATION = "atlas.projection.analyze"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _projection_response(receipt: AnalysisReceipt) -> AtlasProjectionResponse:
    try:
        inputs = json.loads(receipt.input_json)
        output = json.loads(receipt.output_json)
        return AtlasProjectionResponse(
            id=receipt.id,
            initiated_by=receipt.initiated_by,
            claim_id=receipt.subject_id,
            statement=inputs["statement"],
            claim_type=inputs["claim_type"],
            stack=inputs["stack"],
            evidence=tuple(
                AtlasProjectionEvidenceInput.model_validate(item) for item in inputs["evidence"]
            ),
            drivers=tuple(
                AtlasProjectionDriverInput.model_validate(item) for item in inputs["drivers"]
            ),
            posterior=output["posterior"],
            uncertainty=output["uncertainty"],
            evidence_count=output["evidence_count"],
            projection_sha256=output["projection_sha256"],
            input_sha256=receipt.input_sha256,
            output_sha256=receipt.output_sha256,
            audit_hash=receipt.audit_hash,
            created_at=receipt.created_at.isoformat(),
            subordination_notice=output["subordination_notice"],
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stored Atlas projection receipt is invalid",
        ) from error


def install_atlas_workflow_routes(
    application: FastAPI,
    accounts: AccountService | None,
    workflows: WorkflowService | None,
    audit_relay: AppendOnlyAuditRelay | None,
) -> None:
    def current(
        session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
    ) -> tuple[Account, StoredSession]:
        if accounts is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Human account storage is not configured",
            )
        if not session_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in required")
        try:
            account, session = accounts.authenticate(session_token)
            accounts.require_permission(account, InterfacePermission.MODULE_ANALYSIS_RUN)
            return account, session
        except PermissionDenied as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
        except AccountServiceError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
            ) from error

    def require_workflows() -> WorkflowService:
        if workflows is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Durable human workflow storage is not configured",
            )
        return workflows

    @application.get(
        "/api/v1/modules/atlas/projections",
        response_model=AtlasProjectionsResponse,
    )
    def list_atlas_projections(
        session: Annotated[tuple[Account, StoredSession], Depends(current)],
        limit: Annotated[int, Query(ge=1, le=100)] = 50,
    ) -> AtlasProjectionsResponse:
        account, _ = session
        service = require_workflows()
        try:
            receipts = service.analyses_for(
                account,
                limit,
                module_id="atlas",
                operation=ATLAS_PROJECTION_OPERATION,
            )
        except WorkflowPermissionDenied as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
        except WorkflowConflict as error:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
        return AtlasProjectionsResponse(
            projections=tuple(_projection_response(receipt) for receipt in receipts)
        )

    @application.get(
        "/api/v1/modules/atlas/projections/{receipt_id}",
        response_model=AtlasProjectionResponse,
    )
    def get_atlas_projection(
        receipt_id: str,
        session: Annotated[tuple[Account, StoredSession], Depends(current)],
    ) -> AtlasProjectionResponse:
        account, _ = session
        service = require_workflows()
        try:
            receipt = service.analysis_detail_for(account, receipt_id)
        except WorkflowPermissionDenied as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
        except WorkflowConflict as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
        if receipt.module_id != "atlas" or receipt.operation != ATLAS_PROJECTION_OPERATION:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Atlas projection receipt does not exist",
            )
        return _projection_response(receipt)

    @application.post(
        "/api/v1/modules/atlas/projections",
        response_model=AtlasProjectionCreateResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_atlas_projection(
        payload: AtlasProjectionCreate,
        request: Request,
        session: Annotated[tuple[Account, StoredSession], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> AtlasProjectionCreateResponse:
        _require_same_origin(request)
        account, stored_session = session
        service = require_workflows()
        if accounts is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Human account storage is not configured",
            )
        if audit_relay is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Durable audit relay is required for Atlas projections",
            )
        if len(await request.body()) > MAX_ATLAS_REQUEST_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Atlas projection request must not exceed 256 KB",
            )
        try:
            accounts.require_csrf(stored_session, csrf_token)
        except AccountServiceError as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error

        driver_names = [driver.name for driver in payload.drivers]
        if len(driver_names) != len(set(driver_names)):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Atlas projection driver names must be unique",
            )
        normalized_evidence = tuple(
            sorted(payload.evidence, key=lambda item: (item.source, item.tier, item.confidence))
        )
        normalized_drivers = tuple(sorted(payload.drivers, key=lambda item: item.name))
        input_body = {
            "claim_id": payload.claim_id,
            "claim_type": payload.claim_type,
            "drivers": [item.model_dump(mode="json") for item in normalized_drivers],
            "evidence": [item.model_dump(mode="json") for item in normalized_evidence],
            "stack": payload.stack,
            "statement": payload.statement,
        }
        input_json = _canonical_json(input_body)
        input_sha256 = _sha256(input_json)
        try:
            existing = service.existing_analysis(account, payload.idempotency_key)
            if existing is not None:
                if existing.input_sha256 != input_sha256:
                    raise WorkflowConflict(
                        "Idempotency key conflicts with different analysis input"
                    )
                return AtlasProjectionCreateResponse(
                    projection=_projection_response(existing),
                    reused_existing_receipt=True,
                )
        except WorkflowPermissionDenied as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
        except WorkflowConflict as error:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error

        try:
            chain_valid, _ = audit_relay.verify()
        except (OSError, ValueError) as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audit hash chain verification failed",
            ) from error
        if not chain_valid:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audit hash chain verification failed",
            )

        try:
            projection = analyze(
                Claim(
                    claim_id=payload.claim_id,
                    statement=payload.statement,
                    claim_type=ClaimType(payload.claim_type),
                ),
                tuple(
                    Evidence(
                        source=item.source,
                        tier=EvidenceTier(item.tier),
                        confidence=item.confidence,
                    )
                    for item in normalized_evidence
                ),
                drivers={item.name: item.value for item in normalized_drivers},
                stack=payload.stack,
            )
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
            ) from error

        output_json = _canonical_json(
            {
                "evidence_count": projection.evidence_count,
                "posterior": projection.posterior,
                "projection_sha256": projection.projection_sha256,
                "subordination_notice": projection.subordination_notice,
                "uncertainty": projection.uncertainty,
            }
        )
        output_sha256 = _sha256(output_json)
        audit_record = audit_relay.append(
            "control_center.atlas_projection",
            {
                "claim_id": payload.claim_id,
                "initiated_by": account.id,
                "input_sha256": input_sha256,
                "output_sha256": output_sha256,
                "projection_sha256": projection.projection_sha256,
            },
        )
        try:
            receipt = service.record_analysis(
                account,
                module_id="atlas",
                operation=ATLAS_PROJECTION_OPERATION,
                subject_id=payload.claim_id,
                input_json=input_json,
                input_sha256=input_sha256,
                output_json=output_json,
                output_sha256=output_sha256,
                audit_hash=str(audit_record["hash"]),
                idempotency_key=payload.idempotency_key,
            )
        except WorkflowPermissionDenied as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
        except WorkflowConflict as error:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
        return AtlasProjectionCreateResponse(
            projection=_projection_response(receipt),
            reused_existing_receipt=False,
        )

    @application.post(
        "/api/v1/modules/atlas/replay",
        response_model=AtlasReplayResponse,
    )
    async def replay_atlas_bundle(
        payload: AtlasReplayRequest,
        request: Request,
        session: Annotated[tuple[Account, StoredSession], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> AtlasReplayResponse:
        _require_same_origin(request)
        account, stored_session = session
        if accounts is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Human account storage is not configured",
            )
        if audit_relay is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Durable audit relay is required for Atlas replay",
            )
        if len(await request.body()) > MAX_ATLAS_REQUEST_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Atlas replay request must not exceed 256 KB",
            )
        try:
            accounts.require_csrf(stored_session, csrf_token)
        except AccountServiceError as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
        try:
            chain_valid, _ = audit_relay.verify()
        except (OSError, ValueError) as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audit hash chain verification failed",
            ) from error
        if not chain_valid:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audit hash chain verification failed",
            )

        try:
            bundle = ReplayBundle.model_validate(payload.bundle)
            replay_system = ReplaySystem()
            verification = replay_system.verify_bundle(bundle)
            if not verification.is_valid:
                raise ReplaySystemError("; ".join(verification.issues))
            summary = replay_system.replay_bundle(bundle)
        except ReplaySystemError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(error),
            ) from error

        record = audit_relay.append(
            "control_center.atlas_replay",
            {
                "bundle_hash": summary.bundle_hash,
                "bundle_id": summary.bundle_id,
                "initiated_by": account.id,
                "reconstructed_state_hash": summary.reconstructed_state_hash,
            },
        )
        return AtlasReplayResponse(
            bundle_id=summary.bundle_id,
            bundle_hash=summary.bundle_hash,
            reconstructed_state_hash=summary.reconstructed_state_hash,
            item_counts=AtlasReplayItemCounts.model_validate(verification.item_counts),
            audit_receipt_sha256=str(record["hash"]),
            audited_at=str(record["timestamp"]),
            subordination_notice=summary.subordination_notice,
        )
