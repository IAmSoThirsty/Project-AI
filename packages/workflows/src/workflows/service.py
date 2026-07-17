"""Permission-aware human workflow and durable execution-receipt coordination."""

from collections.abc import Callable, Mapping
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from accounts import Account, InterfacePermission, has_permission
from workflows.models import (
    REQUEST_OPERATIONS,
    AnalysisReceipt,
    ExecutionReceipt,
    ExecutionStatus,
    RequestOperation,
    RequestState,
    Review,
    ReviewDecision,
    WorkRequest,
    canonical_request_inputs,
)
from workflows.repository import WorkflowRepository, WorkflowRepositoryConflict


class WorkflowError(Exception):
    pass


class WorkflowPermissionDenied(WorkflowError):
    pass


class WorkflowConflict(WorkflowError):
    pass


def _now() -> datetime:
    return datetime.now(UTC)


class WorkflowService:
    def __init__(
        self, repository: WorkflowRepository, clock: Callable[[], datetime] = _now
    ) -> None:
        self.repository = repository
        self.clock = clock

    def operations_for(self, account: Account) -> tuple[RequestOperation, ...]:
        if account.must_change_password or not has_permission(
            account.role, InterfacePermission.REQUEST_SUBMIT
        ):
            raise WorkflowPermissionDenied("Request submission permission required")
        return REQUEST_OPERATIONS

    @staticmethod
    def _require_analysis_permission(account: Account) -> None:
        if account.must_change_password or not has_permission(
            account.role, InterfacePermission.MODULE_ANALYSIS_RUN
        ):
            raise WorkflowPermissionDenied("Module analysis permission required")

    def analyses_for(
        self,
        account: Account,
        limit: int = 100,
        *,
        module_id: str | None = None,
        operation: str | None = None,
    ) -> tuple[AnalysisReceipt, ...]:
        self._require_analysis_permission(account)
        if not 1 <= limit <= 100:
            raise WorkflowConflict("Analysis history limit must be between 1 and 100")
        return self.repository.analyses(limit, module_id=module_id, operation=operation)

    def analysis_detail_for(self, account: Account, receipt_id: str) -> AnalysisReceipt:
        self._require_analysis_permission(account)
        receipt = self.repository.analysis_by_id(receipt_id)
        if receipt is None:
            raise WorkflowConflict("Analysis receipt does not exist")
        return receipt

    def existing_analysis(self, account: Account, idempotency_key: str) -> AnalysisReceipt | None:
        self._require_analysis_permission(account)
        return self.repository.analysis_by_idempotency(account.id, idempotency_key)

    def record_analysis(
        self,
        account: Account,
        *,
        module_id: str,
        operation: str,
        subject_id: str,
        input_json: str,
        input_sha256: str,
        output_json: str,
        output_sha256: str,
        audit_hash: str,
        idempotency_key: str,
    ) -> AnalysisReceipt:
        self._require_analysis_permission(account)
        values = (module_id, operation, subject_id, idempotency_key)
        if any(not value.strip() or len(value) > 256 for value in values):
            raise WorkflowConflict("Analysis identifiers are invalid")
        if len(input_json.encode("utf-8")) > 256 * 1024:
            raise WorkflowConflict("Analysis input is too large")
        if len(output_json.encode("utf-8")) > 256 * 1024:
            raise WorkflowConflict("Analysis output is too large")
        if any(
            len(value) != 64 or any(char not in "0123456789abcdef" for char in value)
            for value in (input_sha256, output_sha256, audit_hash)
        ):
            raise WorkflowConflict("Analysis evidence hashes are invalid")
        receipt = AnalysisReceipt(
            id=str(uuid4()),
            module_id=module_id.strip(),
            operation=operation.strip(),
            initiated_by=account.id,
            subject_id=subject_id.strip(),
            input_json=input_json,
            input_sha256=input_sha256,
            output_json=output_json,
            output_sha256=output_sha256,
            audit_hash=audit_hash,
            idempotency_key=idempotency_key.strip(),
            created_at=self.clock(),
        )
        persisted = self.repository.create_analysis(receipt)
        if persisted.input_sha256 != input_sha256:
            raise WorkflowConflict("Idempotency key conflicts with different analysis input")
        return persisted

    def submit(
        self,
        account: Account,
        *,
        title: str,
        operation: str,
        resource: str | None = None,
        inputs: Mapping[str, str] | None = None,
        rationale: str,
        idempotency_key: str,
    ) -> WorkRequest:
        if account.must_change_password or not has_permission(
            account.role, InterfacePermission.REQUEST_SUBMIT
        ):
            raise WorkflowPermissionDenied("Request submission permission required")
        values = [
            title.strip(),
            operation.strip(),
            rationale.strip(),
            idempotency_key.strip(),
        ]
        if any(not value for value in values):
            raise WorkflowConflict("All request fields are required")
        if any(len(value) > 2048 for value in values):
            raise WorkflowConflict("Request field is too long")
        try:
            canonical_resource, inputs_json, input_sha256, schema_version = (
                canonical_request_inputs(values[1], inputs=inputs, resource=resource)
            )
            if (
                inputs is not None
                and resource is not None
                and resource.strip() != canonical_resource
            ):
                raise ValueError("Request resource conflicts with the structured inputs")
        except ValueError as error:
            raise WorkflowConflict(str(error)) from error
        now = self.clock()
        return self.repository.create_request(
            WorkRequest(
                id=str(uuid4()),
                created_by=account.id,
                title=values[0],
                operation=values[1],
                resource=canonical_resource,
                input_schema_version=schema_version,
                inputs_json=inputs_json,
                input_sha256=input_sha256,
                rationale=values[2],
                idempotency_key=values[3],
                state=RequestState.SUBMITTED,
                created_at=now,
                updated_at=now,
            )
        )

    def list_for(self, account: Account) -> tuple[WorkRequest, ...]:
        if account.must_change_password:
            raise WorkflowPermissionDenied("Password change required")
        records = self.repository.requests()
        if has_permission(account.role, InterfacePermission.REQUEST_REVIEW):
            return records
        return tuple(item for item in records if item.created_by == account.id)

    def detail_for(
        self, account: Account, request_id: str
    ) -> tuple[WorkRequest, tuple[Review, ...]]:
        if account.must_change_password:
            raise WorkflowPermissionDenied("Password change required")
        request = self.repository.request_by_id(request_id)
        if request is None:
            raise WorkflowConflict("Request does not exist")
        if request.created_by != account.id and not has_permission(
            account.role, InterfacePermission.REQUEST_REVIEW
        ):
            raise WorkflowPermissionDenied("Request is not visible to this account")
        return request, self.repository.reviews_for(request_id)

    def receipt_for(self, account: Account, request_id: str) -> ExecutionReceipt | None:
        self.detail_for(account, request_id)
        return self.repository.execution_receipt(request_id)

    def begin_execution(
        self,
        account: Account,
        request_id: str,
        *,
        module_id: str,
        expected_operation: str,
        expected_resource: str,
        mfa_verified_at: datetime | None,
    ) -> tuple[WorkRequest, ExecutionReceipt, bool]:
        if account.must_change_password or not has_permission(
            account.role, InterfacePermission.MODULE_EXECUTION_INITIATE
        ):
            raise WorkflowPermissionDenied("Module execution initiation permission required")
        now = self.clock()
        if mfa_verified_at is None or now - mfa_verified_at > timedelta(minutes=5):
            raise WorkflowPermissionDenied("Recent MFA step-up is required")
        request = self.repository.request_by_id(request_id)
        if request is None:
            raise WorkflowConflict("Request does not exist")
        if request.operation != expected_operation or request.resource != expected_resource:
            raise WorkflowConflict("Execution input does not match the reviewed request")
        try:
            receipt, created = self.repository.reserve_execution(
                request_id,
                str(uuid4()),
                module_id,
                account.id,
                now,
            )
        except WorkflowRepositoryConflict as error:
            raise WorkflowConflict(str(error)) from error
        return request, receipt, created

    def finish_execution(
        self,
        request_id: str,
        *,
        status: ExecutionStatus,
        action_id: str,
        outcome: str,
        reason: str,
        output_json: str,
        governance_evidence_sha256: str,
        event_hash: str,
        audit_hash: str,
    ) -> ExecutionReceipt:
        try:
            return self.repository.finish_execution(
                request_id,
                status=status,
                action_id=action_id,
                outcome=outcome,
                reason=reason,
                output_json=output_json,
                governance_evidence_sha256=governance_evidence_sha256,
                event_hash=event_hash,
                audit_hash=audit_hash,
                completed_at=self.clock(),
            )
        except WorkflowRepositoryConflict as error:
            raise WorkflowConflict(str(error)) from error

    def review(
        self,
        account: Account,
        request_id: str,
        decision: ReviewDecision,
        rationale: str,
        mfa_verified_at: datetime | None,
    ) -> Review:
        if account.must_change_password or not has_permission(
            account.role, InterfacePermission.REQUEST_REVIEW
        ):
            raise WorkflowPermissionDenied("Request review permission required")
        now = self.clock()
        if mfa_verified_at is None or now - mfa_verified_at > timedelta(minutes=5):
            raise WorkflowPermissionDenied("Recent MFA step-up is required")
        request = self.repository.request_by_id(request_id)
        if request is None:
            raise WorkflowConflict("Request does not exist")
        if request.created_by == account.id:
            raise WorkflowPermissionDenied("Self-review is not allowed")
        if self.repository.has_review(request.id, account.id):
            raise WorkflowConflict("Reviewer has already reviewed this request")
        if request.state is not RequestState.SUBMITTED:
            raise WorkflowConflict("Request is no longer awaiting review")
        if not rationale.strip():
            raise WorkflowConflict("Review rationale is required")
        state = {
            ReviewDecision.APPROVE_FOR_GOVERNANCE: RequestState.REVIEWED_APPROVE,
            ReviewDecision.REJECT: RequestState.REVIEWED_REJECT,
            ReviewDecision.RETURN_FOR_INFORMATION: RequestState.NEEDS_INFORMATION,
            ReviewDecision.ABSTAIN: RequestState.SUBMITTED,
        }[decision]
        review = Review(
            id=str(uuid4()),
            request_id=request.id,
            reviewer_account_id=account.id,
            decision=decision,
            rationale=rationale.strip(),
            created_at=now,
        )
        try:
            self.repository.add_review(review, state, now)
        except WorkflowRepositoryConflict as error:
            raise WorkflowConflict(str(error)) from error
        return review

    def cancel(self, account: Account, request_id: str) -> WorkRequest:
        if account.must_change_password:
            raise WorkflowPermissionDenied("Password change required")
        request = self.repository.request_by_id(request_id)
        if request is None:
            raise WorkflowConflict("Request does not exist")
        if request.created_by != account.id:
            raise WorkflowPermissionDenied("Only the request creator can cancel it")
        if request.state not in {RequestState.SUBMITTED, RequestState.NEEDS_INFORMATION}:
            raise WorkflowConflict("Request can no longer be cancelled")
        now = self.clock()
        if not self.repository.cancel_request(request.id, account.id, now):
            raise WorkflowConflict("Request can no longer be cancelled")
        updated = self.repository.request_by_id(request.id)
        if updated is None:  # Defensive fail-closed check around durable storage.
            raise WorkflowConflict("Cancelled request could not be reloaded")
        return updated
