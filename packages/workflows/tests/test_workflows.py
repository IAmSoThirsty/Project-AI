import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from cerberus.security.modules.auth import PasswordHasher

from accounts import AccountRepository, AccountRole, AccountService
from workflows import (
    REQUEST_OPERATIONS,
    ExecutionStatus,
    RequestState,
    ReviewDecision,
    WorkflowConflict,
    WorkflowPermissionDenied,
    WorkflowRepository,
    WorkflowService,
    review_receipt_sha256,
)

NOW = datetime(2026, 7, 15, 12, 0, tzinfo=UTC)


def test_workflow_schema_one_migrates_to_schema_four(tmp_path: Path) -> None:
    path = tmp_path / "workflow-migration.db"
    WorkflowRepository(path)
    with sqlite3.connect(path) as connection:
        connection.execute("DROP TABLE execution_receipts")
        connection.execute("PRAGMA user_version = 1")
    WorkflowRepository(path)
    with sqlite3.connect(path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 4
        execution_table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'execution_receipts'"
        ).fetchone()
        analysis_table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'analysis_receipts'"
        ).fetchone()
        columns = {str(row[1]) for row in connection.execute("PRAGMA table_info(work_requests)")}
    assert execution_table == ("execution_receipts",)
    assert analysis_table == ("analysis_receipts",)
    assert {"input_schema_version", "inputs_json", "input_sha256"} <= columns


def _accounts(tmp_path: Path):
    service = AccountService(
        AccountRepository(tmp_path / "accounts.db"),
        setup_secret="setup",
        password_hasher=PasswordHasher(iterations=1_000),
    )
    owner = service.bootstrap(
        setup_secret="setup",
        username="owner",
        display_name="Owner",
        password="Foundation!Owner123",
        actor_id=None,
        source="local",
        user_agent="pytest",
    ).bundle
    operator = service.create_managed_account(
        owner.token,
        owner.csrf_token,
        username="operator",
        display_name="Operator",
        password="Temporary!Operator123",
        role=AccountRole.OPERATOR,
        actor_id=None,
        source="local",
    ).account
    reviewer = service.create_managed_account(
        owner.token,
        owner.csrf_token,
        username="reviewer",
        display_name="Reviewer",
        password="Temporary!Reviewer123",
        role=AccountRole.REVIEWER,
        actor_id=None,
        source="local",
    ).account
    # Tests exercise workflow permissions, not the first-login password gate.
    service.repository.change_password(operator.id, operator.password_hash, NOW)
    service.repository.change_password(reviewer.id, reviewer.password_hash, NOW)
    return service.repository.account_by_id(operator.id), service.repository.account_by_id(
        reviewer.id
    )


def test_analysis_receipts_are_durable_idempotent_and_permission_gated(tmp_path: Path) -> None:
    operator, reviewer = _accounts(tmp_path)
    assert operator is not None and reviewer is not None
    repository = WorkflowRepository(tmp_path / "workflows.db")
    service = WorkflowService(repository, clock=lambda: NOW)
    digest = "a" * 64
    receipt = service.record_analysis(
        operator,
        module_id="atlas",
        operation="atlas.projection.analyze",
        subject_id="claim-42",
        input_json='{"claim_id":"claim-42"}',
        input_sha256=digest,
        output_json='{"posterior":0.5}',
        output_sha256="b" * 64,
        audit_hash="c" * 64,
        idempotency_key="projection-42",
    )
    duplicate = service.record_analysis(
        operator,
        module_id="atlas",
        operation="atlas.projection.analyze",
        subject_id="claim-42",
        input_json='{"claim_id":"claim-42"}',
        input_sha256=digest,
        output_json='{"posterior":0.5}',
        output_sha256="b" * 64,
        audit_hash="c" * 64,
        idempotency_key="projection-42",
    )
    assert duplicate.id == receipt.id
    service.record_analysis(
        operator,
        module_id="taar",
        operation="taar.report.inspect",
        subject_id="report-42",
        input_json='{"report_id":"report-42"}',
        input_sha256="7" * 64,
        output_json='{"findings":1}',
        output_sha256="8" * 64,
        audit_hash="9" * 64,
        idempotency_key="report-42",
    )
    assert service.analyses_for(
        reviewer,
        module_id="atlas",
        operation="atlas.projection.analyze",
    ) == (receipt,)
    assert (
        WorkflowService(
            WorkflowRepository(tmp_path / "workflows.db"), clock=lambda: NOW
        ).analysis_detail_for(reviewer, receipt.id)
        == receipt
    )
    viewer = replace(reviewer, id="viewer", role=AccountRole.VIEWER)
    with pytest.raises(WorkflowPermissionDenied, match="Module analysis"):
        service.analyses_for(viewer)
    with pytest.raises(WorkflowConflict, match="different analysis input"):
        service.record_analysis(
            operator,
            module_id="atlas",
            operation="atlas.projection.analyze",
            subject_id="claim-42",
            input_json='{"claim_id":"different"}',
            input_sha256="d" * 64,
            output_json='{"posterior":0.1}',
            output_sha256="e" * 64,
            audit_hash="f" * 64,
            idempotency_key="projection-42",
        )


def test_request_idempotency_visibility_and_step_up_review(tmp_path: Path) -> None:
    operator, reviewer = _accounts(tmp_path)
    assert operator is not None and reviewer is not None
    service = WorkflowService(WorkflowRepository(tmp_path / "workflows.db"), clock=lambda: NOW)
    request = service.submit(
        operator,
        title="Inspect evidence bundle",
        operation="evidence.inspect",
        resource="bundle:42",
        rationale="Verify provenance",
        idempotency_key="request-42",
    )
    duplicate = service.submit(
        operator,
        title="Inspect evidence bundle",
        operation="evidence.inspect",
        resource="bundle:42",
        rationale="Verify provenance",
        idempotency_key="request-42",
    )
    assert duplicate.id == request.id
    assert service.list_for(operator) == (request,)
    assert service.list_for(reviewer) == (request,)
    assert service.operations_for(operator) == REQUEST_OPERATIONS
    assert request.input_schema_version == "evidence.inspect/v1"
    assert json.loads(request.inputs_json) == {"bundle_id": "42"}
    assert len(request.input_sha256) == 64

    with pytest.raises(WorkflowPermissionDenied, match="Recent MFA"):
        service.review(
            reviewer, request.id, ReviewDecision.APPROVE_FOR_GOVERNANCE, "Looks valid", None
        )
    review = service.review(
        reviewer,
        request.id,
        ReviewDecision.APPROVE_FOR_GOVERNANCE,
        "Evidence is sufficient for canonical governance evaluation",
        NOW - timedelta(minutes=1),
    )
    assert review.request_id == request.id
    updated = service.repository.request_by_id(request.id)
    assert updated is not None and updated.state is RequestState.REVIEWED_APPROVE
    detail, reviews = service.detail_for(reviewer, request.id)
    assert detail == updated
    assert reviews == (review,)
    assert len(review_receipt_sha256(review)) == 64
    assert review_receipt_sha256(review) == review_receipt_sha256(reviews[0])
    outsider = replace(reviewer, id="unrelated-viewer", role=AccountRole.VIEWER)
    with pytest.raises(WorkflowPermissionDenied, match="not visible"):
        service.detail_for(outsider, request.id)


def test_self_review_is_denied_even_with_owner_permissions(tmp_path: Path) -> None:
    account_service = AccountService(
        AccountRepository(tmp_path / "accounts.db"),
        setup_secret="setup",
        password_hasher=PasswordHasher(iterations=1_000),
    )
    owner = account_service.bootstrap(
        setup_secret="setup",
        username="owner",
        display_name="Owner",
        password="Foundation!Owner123",
        actor_id=None,
        source="local",
        user_agent="pytest",
    ).bundle.account
    service = WorkflowService(WorkflowRepository(tmp_path / "workflows.db"), clock=lambda: NOW)
    request = service.submit(
        owner,
        title="Owner request",
        operation="evidence.inspect",
        resource="bundle:1",
        rationale="Need review",
        idempotency_key="owner-1",
    )
    with pytest.raises(WorkflowPermissionDenied, match="Self-review"):
        service.review(
            owner,
            request.id,
            ReviewDecision.APPROVE_FOR_GOVERNANCE,
            "Cannot self approve",
            NOW,
        )


def test_reviewer_cannot_abstain_twice(tmp_path: Path) -> None:
    operator, reviewer = _accounts(tmp_path)
    assert operator is not None and reviewer is not None
    service = WorkflowService(WorkflowRepository(tmp_path / "workflows.db"), clock=lambda: NOW)
    request = service.submit(
        operator,
        title="Review once",
        operation="evidence.inspect",
        resource="bundle:2",
        rationale="Avoid duplicate decisions",
        idempotency_key="review-once",
    )
    service.review(reviewer, request.id, ReviewDecision.ABSTAIN, "Conflict", NOW)

    with pytest.raises(WorkflowConflict, match="already reviewed"):
        service.review(reviewer, request.id, ReviewDecision.ABSTAIN, "Still conflict", NOW)


def test_temporary_password_account_cannot_list_requests(tmp_path: Path) -> None:
    account_service = AccountService(
        AccountRepository(tmp_path / "accounts.db"),
        setup_secret="setup",
        password_hasher=PasswordHasher(iterations=1_000),
    )
    owner = account_service.bootstrap(
        setup_secret="setup",
        username="owner",
        display_name="Owner",
        password="Foundation!Owner123",
        actor_id=None,
        source="local",
        user_agent="pytest",
    ).bundle
    temporary = account_service.create_managed_account(
        owner.token,
        owner.csrf_token,
        username="temporary",
        display_name="Temporary",
        password="Temporary!Account123",
        role=AccountRole.OPERATOR,
        actor_id=None,
        source="local",
    ).account
    service = WorkflowService(WorkflowRepository(tmp_path / "workflows.db"), clock=lambda: NOW)

    with pytest.raises(WorkflowPermissionDenied, match="Password change"):
        service.list_for(temporary)


def test_unsupported_request_operation_is_rejected(tmp_path: Path) -> None:
    operator, _ = _accounts(tmp_path)
    assert operator is not None
    service = WorkflowService(WorkflowRepository(tmp_path / "workflows.db"), clock=lambda: NOW)

    with pytest.raises(WorkflowConflict, match="Unsupported request operation"):
        service.submit(
            operator,
            title="Unknown action",
            operation="arbitrary.execute",
            resource="anything",
            rationale="Must not accept free-form operations",
            idempotency_key="unsupported-operation",
        )


def test_request_inputs_must_match_the_versioned_operation_schema(tmp_path: Path) -> None:
    operator, _ = _accounts(tmp_path)
    assert operator is not None
    service = WorkflowService(WorkflowRepository(tmp_path / "workflows.db"), clock=lambda: NOW)

    with pytest.raises(WorkflowConflict, match="do not match"):
        service.submit(
            operator,
            title="Malformed evidence request",
            operation="evidence.inspect",
            inputs={"unexpected": "42"},
            rationale="Must fail closed",
            idempotency_key="malformed-input-keys",
        )
    with pytest.raises(WorkflowConflict, match="invalid format"):
        service.submit(
            operator,
            title="Unsafe evidence request",
            operation="evidence.inspect",
            inputs={"bundle_id": "../../escape"},
            rationale="Must reject path traversal",
            idempotency_key="malformed-input-format",
        )

    request = service.submit(
        operator,
        title="Structured evidence request",
        operation="evidence.inspect",
        inputs={"bundle_id": "bundle-42"},
        rationale="Persist the exact reviewed input",
        idempotency_key="structured-input-success",
    )
    assert request.resource == "bundle:bundle-42"
    assert json.loads(request.inputs_json) == {"bundle_id": "bundle-42"}


def test_creator_can_cancel_pending_request(tmp_path: Path) -> None:
    operator, reviewer = _accounts(tmp_path)
    assert operator is not None and reviewer is not None
    service = WorkflowService(WorkflowRepository(tmp_path / "workflows.db"), clock=lambda: NOW)
    request = service.submit(
        operator,
        title="Cancel safely",
        operation="evidence.inspect",
        resource="bundle:cancel",
        rationale="No longer needed",
        idempotency_key="cancel-pending-request",
    )

    with pytest.raises(WorkflowPermissionDenied, match="Only the request creator"):
        service.cancel(reviewer, request.id)
    cancelled = service.cancel(operator, request.id)
    assert cancelled.state is RequestState.CANCELLED
    with pytest.raises(WorkflowConflict, match="no longer be cancelled"):
        service.cancel(operator, request.id)


def test_reviewed_request_reserves_and_finishes_one_execution_receipt(tmp_path: Path) -> None:
    operator, reviewer = _accounts(tmp_path)
    assert operator is not None and reviewer is not None
    service = WorkflowService(WorkflowRepository(tmp_path / "workflows.db"), clock=lambda: NOW)
    request = service.submit(
        operator,
        title="Run a bounded SWR scenario",
        operation="scenario.prepare",
        resource="scenario:scenario-1",
        rationale="Exercise the reviewed analytical path",
        idempotency_key="execute-swr-scenario-1",
    )
    with pytest.raises(WorkflowConflict, match="not approved"):
        service.begin_execution(
            operator,
            request.id,
            module_id="swr",
            expected_operation="scenario.prepare",
            expected_resource="scenario:scenario-1",
            mfa_verified_at=NOW,
        )
    service.review(
        reviewer,
        request.id,
        ReviewDecision.APPROVE_FOR_GOVERNANCE,
        "Bounded scenario evaluation is appropriate",
        NOW,
    )
    reviewed, running, created = service.begin_execution(
        operator,
        request.id,
        module_id="swr",
        expected_operation="scenario.prepare",
        expected_resource="scenario:scenario-1",
        mfa_verified_at=NOW,
    )
    assert reviewed.state is RequestState.REVIEWED_APPROVE
    assert created is True and running.status is ExecutionStatus.RUNNING
    _, duplicate, duplicate_created = service.begin_execution(
        operator,
        request.id,
        module_id="swr",
        expected_operation="scenario.prepare",
        expected_resource="scenario:scenario-1",
        mfa_verified_at=NOW,
    )
    assert duplicate_created is False and duplicate.attempt_id == running.attempt_id
    finished = service.finish_execution(
        request.id,
        status=ExecutionStatus.EXECUTED,
        action_id="swr:action-1",
        outcome="ALLOW",
        reason="",
        output_json='{"recorded":true}',
        governance_evidence_sha256="e" * 64,
        event_hash="f" * 64,
        audit_hash="a" * 64,
    )
    assert finished.status is ExecutionStatus.EXECUTED
    stored = service.repository.request_by_id(request.id)
    assert stored is not None and stored.state is RequestState.EXECUTED
    assert service.receipt_for(operator, request.id) == finished


def test_concurrent_execution_reservation_creates_one_attempt(tmp_path: Path) -> None:
    operator, reviewer = _accounts(tmp_path)
    assert operator is not None and reviewer is not None
    repository_path = tmp_path / "workflows.db"
    service = WorkflowService(WorkflowRepository(repository_path), clock=lambda: NOW)
    request = service.submit(
        operator,
        title="Reserve once",
        operation="scenario.prepare",
        resource="scenario:one",
        rationale="Prove replica-safe reservation",
        idempotency_key="concurrent-execution-reservation",
    )
    service.review(
        reviewer,
        request.id,
        ReviewDecision.APPROVE_FOR_GOVERNANCE,
        "Approved for bounded analysis",
        NOW,
    )

    def reserve(_: int) -> tuple[str, bool]:
        replica = WorkflowService(WorkflowRepository(repository_path), clock=lambda: NOW)
        _, receipt, created = replica.begin_execution(
            operator,
            request.id,
            module_id="swr",
            expected_operation="scenario.prepare",
            expected_resource="scenario:one",
            mfa_verified_at=NOW,
        )
        return receipt.attempt_id, created

    with ThreadPoolExecutor(max_workers=2) as pool:
        reservations = list(pool.map(reserve, range(2)))
    assert [created for _, created in reservations].count(True) == 1
    assert len({attempt_id for attempt_id, _ in reservations}) == 1
