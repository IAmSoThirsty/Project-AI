"""Human request/review routes that cannot actuate or create governance verdicts."""

import json
from typing import Annotated

from fastapi import Cookie, Depends, FastAPI, Header, HTTPException, Request, status

from accounts import Account, AccountService, AccountServiceError, StoredSession
from project_ai_api.auth import SESSION_COOKIE, _require_same_origin
from project_ai_api.models import (
    ExecutionReceiptResponse,
    WorkInputFieldResponse,
    WorkOperationResponse,
    WorkOperationsResponse,
    WorkRequestCreate,
    WorkRequestDetailResponse,
    WorkRequestResponse,
    WorkRequestsResponse,
    WorkReviewCreate,
    WorkReviewResponse,
)
from workflows import (
    ExecutionReceipt,
    Review,
    ReviewDecision,
    WorkflowConflict,
    WorkflowPermissionDenied,
    WorkflowService,
    WorkRequest,
    review_receipt_sha256,
)


def _request_response(item: WorkRequest) -> WorkRequestResponse:
    return WorkRequestResponse(
        id=item.id,
        created_by=item.created_by,
        title=item.title,
        operation=item.operation,
        resource=item.resource,
        input_schema_version=item.input_schema_version,
        inputs=json.loads(item.inputs_json),
        input_sha256=item.input_sha256,
        rationale=item.rationale,
        state=item.state.value,
        created_at=item.created_at.isoformat(),
        updated_at=item.updated_at.isoformat(),
    )


def _review_response(review: Review) -> WorkReviewResponse:
    return WorkReviewResponse(
        id=review.id,
        request_id=review.request_id,
        reviewer_account_id=review.reviewer_account_id,
        decision=review.decision.value,
        rationale=review.rationale,
        created_at=review.created_at.isoformat(),
        receipt_sha256=review_receipt_sha256(review),
    )


def execution_receipt_response(receipt: ExecutionReceipt) -> ExecutionReceiptResponse:
    return ExecutionReceiptResponse(
        request_id=receipt.request_id,
        attempt_id=receipt.attempt_id,
        module_id=receipt.module_id,
        initiated_by=receipt.initiated_by,
        status=receipt.status.value,
        action_id=receipt.action_id,
        outcome=receipt.outcome,
        reason=receipt.reason,
        output=json.loads(receipt.output_json),
        governance_evidence_sha256=receipt.governance_evidence_sha256,
        event_hash=receipt.event_hash,
        audit_hash=receipt.audit_hash,
        created_at=receipt.created_at.isoformat(),
        completed_at=receipt.completed_at.isoformat() if receipt.completed_at else None,
    )


def install_workflow_routes(
    application: FastAPI,
    accounts: AccountService | None,
    workflows: WorkflowService | None,
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

    def active() -> WorkflowService:
        if workflows is None:
            raise HTTPException(status_code=503, detail="Human workflow storage is not configured")
        return workflows

    @application.get("/api/v1/work/requests", response_model=WorkRequestsResponse)
    def list_requests(
        session: Annotated[tuple[Account, StoredSession], Depends(current)],
    ) -> WorkRequestsResponse:
        account, _ = session
        try:
            items = active().list_for(account)
        except WorkflowPermissionDenied as error:
            raise HTTPException(status_code=403, detail=str(error)) from error
        return WorkRequestsResponse(requests=tuple(_request_response(item) for item in items))

    @application.get("/api/v1/work/operations", response_model=WorkOperationsResponse)
    def list_operations(
        session: Annotated[tuple[Account, StoredSession], Depends(current)],
    ) -> WorkOperationsResponse:
        account, _ = session
        try:
            operations = active().operations_for(account)
        except WorkflowPermissionDenied as error:
            raise HTTPException(status_code=403, detail=str(error)) from error
        return WorkOperationsResponse(
            operations=tuple(
                WorkOperationResponse(
                    id=item.id,
                    label=item.label,
                    description=item.description,
                    resource_hint=item.resource_hint,
                    schema_version=item.schema_version,
                    fields=tuple(
                        WorkInputFieldResponse(
                            id=field.id,
                            label=field.label,
                            description=field.description,
                            placeholder=field.placeholder,
                            resource_prefix=field.resource_prefix,
                            min_length=field.min_length,
                            max_length=field.max_length,
                            pattern=field.pattern,
                        )
                        for field in item.fields
                    ),
                    consequence=item.consequence,
                )
                for item in operations
            )
        )

    @application.get("/api/v1/work/requests/{request_id}", response_model=WorkRequestDetailResponse)
    def request_detail(
        request_id: str,
        session: Annotated[tuple[Account, StoredSession], Depends(current)],
    ) -> WorkRequestDetailResponse:
        account, _ = session
        try:
            item, reviews = active().detail_for(account, request_id)
            receipt = active().receipt_for(account, request_id)
        except WorkflowPermissionDenied as error:
            raise HTTPException(status_code=403, detail=str(error)) from error
        except WorkflowConflict as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        return WorkRequestDetailResponse(
            request=_request_response(item),
            reviews=tuple(_review_response(review) for review in reviews),
            execution_receipt=(
                execution_receipt_response(receipt) if receipt is not None else None
            ),
            execution_status=receipt.status.value if receipt is not None else "not_started",
        )

    @application.post("/api/v1/work/requests", response_model=WorkRequestResponse)
    def create_request(
        payload: WorkRequestCreate,
        request: Request,
        session: Annotated[tuple[Account, StoredSession], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> WorkRequestResponse:
        _require_same_origin(request)
        account, stored_session = session
        if accounts is None:
            raise HTTPException(status_code=503, detail="Human account storage is not configured")
        try:
            accounts.require_csrf(stored_session, csrf_token)
            item = active().submit(
                account,
                title=payload.title,
                operation=payload.operation,
                resource=payload.resource,
                inputs=payload.inputs or None,
                rationale=payload.rationale,
                idempotency_key=payload.idempotency_key,
            )
        except AccountServiceError as error:
            raise HTTPException(status_code=403, detail=str(error)) from error
        except WorkflowPermissionDenied as error:
            raise HTTPException(status_code=403, detail=str(error)) from error
        except WorkflowConflict as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        return _request_response(item)

    @application.post(
        "/api/v1/work/requests/{request_id}/reviews", response_model=WorkReviewResponse
    )
    def review_request(
        request_id: str,
        payload: WorkReviewCreate,
        request: Request,
        session: Annotated[tuple[Account, StoredSession], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> WorkReviewResponse:
        _require_same_origin(request)
        account, stored_session = session
        if accounts is None:
            raise HTTPException(status_code=503, detail="Human account storage is not configured")
        try:
            accounts.require_csrf(stored_session, csrf_token)
            review = active().review(
                account,
                request_id,
                ReviewDecision(payload.decision),
                payload.rationale,
                stored_session.mfa_verified_at,
            )
        except AccountServiceError as error:
            raise HTTPException(status_code=403, detail=str(error)) from error
        except WorkflowPermissionDenied as error:
            raise HTTPException(status_code=403, detail=str(error)) from error
        except WorkflowConflict as error:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
        return _review_response(review)

    @application.post(
        "/api/v1/work/requests/{request_id}/cancel", response_model=WorkRequestResponse
    )
    def cancel_request(
        request_id: str,
        request: Request,
        session: Annotated[tuple[Account, StoredSession], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> WorkRequestResponse:
        _require_same_origin(request)
        account, stored_session = session
        if accounts is None:
            raise HTTPException(status_code=503, detail="Human account storage is not configured")
        try:
            accounts.require_csrf(stored_session, csrf_token)
            item = active().cancel(account, request_id)
        except AccountServiceError as error:
            raise HTTPException(status_code=403, detail=str(error)) from error
        except WorkflowPermissionDenied as error:
            raise HTTPException(status_code=403, detail=str(error)) from error
        except WorkflowConflict as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        return _request_response(item)
