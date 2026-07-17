"""Live PostgreSQL parity and concurrency checks for human-interface storage."""

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

import psycopg
import pytest
from cerberus.security.modules.auth import PasswordHasher
from tools.migrate_human_state import migrate

from accounts import (
    AccountRepository,
    AccountRole,
    AccountService,
    BootstrapUnavailable,
    PostgresAccountRepository,
)
from workflows import (
    ExecutionStatus,
    PostgresWorkflowRepository,
    ReviewDecision,
    WorkflowConflict,
    WorkflowRepository,
    WorkflowService,
)

DSN = os.getenv("PROJECT_AI_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DSN, reason="PROJECT_AI_TEST_DATABASE_URL is not set")
NOW = datetime(2026, 7, 15, 18, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def clean_database() -> None:
    assert DSN is not None
    PostgresAccountRepository(DSN).migrate()
    PostgresWorkflowRepository(DSN).migrate()
    with psycopg.connect(DSN) as connection:
        connection.execute(
            """TRUNCATE reviews, work_requests, recovery_codes, sessions,
            security_events, auth_rate_limits, accounts RESTART IDENTITY CASCADE"""
        )


def _service() -> AccountService:
    assert DSN is not None
    return AccountService(
        PostgresAccountRepository(DSN),
        setup_secret="postgres-setup",
        password_hasher=PasswordHasher(iterations=1_000),
        clock=lambda: NOW,
    )


def test_postgres_owner_session_account_and_workflow_round_trip() -> None:
    assert DSN is not None
    accounts = _service()
    owner = accounts.bootstrap(
        setup_secret="postgres-setup",
        username="owner",
        display_name="Postgres Owner",
        password="Foundation!Owner123",
        actor_id="ACTOR-OWNER",
        source="integration",
        user_agent="pytest",
    ).bundle
    operator_result = accounts.create_managed_account(
        owner.token,
        owner.csrf_token,
        username="operator.one",
        display_name="Operator One",
        password="Temporary!Operator123",
        role=AccountRole.OPERATOR,
        actor_id="ACTOR-OPERATOR",
        source="integration",
    )
    accounts.repository.change_password(
        operator_result.account.id, operator_result.account.password_hash, NOW
    )
    operator = accounts.repository.account_by_id(operator_result.account.id)
    assert operator is not None

    workflows = WorkflowService(PostgresWorkflowRepository(DSN), clock=lambda: NOW)
    request = workflows.submit(
        operator,
        title="Inspect PostgreSQL evidence",
        operation="evidence.inspect",
        resource="bundle:postgres",
        rationale="Prove durable workflow parity",
        idempotency_key="postgres-round-trip",
    )
    duplicate = workflows.submit(
        operator,
        title="Inspect PostgreSQL evidence",
        operation="evidence.inspect",
        resource="bundle:postgres",
        rationale="Prove durable workflow parity",
        idempotency_key="postgres-round-trip",
    )
    assert duplicate.id == request.id
    assert workflows.list_for(operator) == (request,)
    assert accounts.repository.security_events()


def test_postgres_bootstrap_and_rate_limit_are_concurrency_safe() -> None:
    def bootstrap(index: int) -> bool:
        try:
            _service().bootstrap(
                setup_secret="postgres-setup",
                username=f"owner{index}",
                display_name=f"Owner {index}",
                password="Foundation!Owner123",
                actor_id=None,
                source="integration",
                user_agent="pytest",
            )
            return True
        except BootstrapUnavailable:
            return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(bootstrap, range(8)))
    assert results.count(True) == 1

    assert DSN is not None
    repository = PostgresAccountRepository(DSN)

    def hit(_: int) -> bool:
        return repository.rate_limit_hit(
            "login:shared",
            NOW,
            window_seconds=60,
            limit=5,
            block_seconds=60,
        )

    with ThreadPoolExecutor(max_workers=10) as pool:
        blocked = list(pool.map(hit, range(10)))
    assert blocked.count(True) == 5


def test_postgres_allows_only_one_terminal_review_across_replicas() -> None:
    assert DSN is not None
    accounts = _service()
    owner = accounts.bootstrap(
        setup_secret="postgres-setup",
        username="owner",
        display_name="Postgres Owner",
        password="Foundation!Owner123",
        actor_id=None,
        source="integration",
        user_agent="pytest",
    ).bundle

    def managed(username: str, role: AccountRole):
        created = accounts.create_managed_account(
            owner.token,
            owner.csrf_token,
            username=username,
            display_name=username.replace(".", " ").title(),
            password="Temporary!Account123",
            role=role,
            actor_id=None,
            source="integration",
        ).account
        accounts.repository.change_password(created.id, created.password_hash, NOW)
        account = accounts.repository.account_by_id(created.id)
        assert account is not None
        return account

    operator = managed("operator.one", AccountRole.OPERATOR)
    reviewers = (
        managed("reviewer.one", AccountRole.REVIEWER),
        managed("reviewer.two", AccountRole.REVIEWER),
    )
    request = WorkflowService(PostgresWorkflowRepository(DSN), clock=lambda: NOW).submit(
        operator,
        title="Concurrent terminal review",
        operation="evidence.inspect",
        resource="bundle:concurrency",
        rationale="Prove one durable terminal decision",
        idempotency_key="terminal-review-race",
    )

    def review(index: int) -> str:
        try:
            WorkflowService(PostgresWorkflowRepository(DSN), clock=lambda: NOW).review(
                reviewers[index],
                request.id,
                ReviewDecision.APPROVE_FOR_GOVERNANCE,
                f"Independent reviewer {index}",
                NOW,
            )
            return "reviewed"
        except WorkflowConflict:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(review, range(2)))
    assert sorted(outcomes) == ["conflict", "reviewed"]
    repository = PostgresWorkflowRepository(DSN)
    assert len(repository.reviews_for(request.id)) == 1

    def reserve(_: int) -> tuple[str, bool]:
        replica = WorkflowService(PostgresWorkflowRepository(DSN), clock=lambda: NOW)
        _, receipt, created = replica.begin_execution(
            operator,
            request.id,
            module_id="swr",
            expected_operation="evidence.inspect",
            expected_resource="bundle:concurrency",
            mfa_verified_at=NOW,
        )
        return receipt.attempt_id, created

    with ThreadPoolExecutor(max_workers=2) as pool:
        reservations = list(pool.map(reserve, range(2)))
    assert [created for _, created in reservations].count(True) == 1
    assert len({attempt_id for attempt_id, _ in reservations}) == 1


def test_sqlite_human_state_migrates_once_without_secret_rehashing(tmp_path: Path) -> None:
    assert DSN is not None
    account_path = tmp_path / "accounts.db"
    workflow_path = tmp_path / "workflows.db"
    source_accounts = AccountService(
        AccountRepository(account_path),
        setup_secret="sqlite-setup",
        password_hasher=PasswordHasher(iterations=1_000),
        clock=lambda: NOW,
    )
    owner = source_accounts.bootstrap(
        setup_secret="sqlite-setup",
        username="sqlite.owner",
        display_name="SQLite Owner",
        password="Foundation!Owner123",
        actor_id="ACTOR-SQLITE",
        source="integration",
        user_agent="pytest",
    ).bundle
    source_workflows = WorkflowService(WorkflowRepository(workflow_path), clock=lambda: NOW)
    request = source_workflows.submit(
        owner.account,
        title="Migrate this request",
        operation="evidence.inspect",
        resource="bundle:sqlite",
        rationale="Prove one-time data migration",
        idempotency_key="sqlite-migration-request",
    )
    reviewer_created = source_accounts.create_managed_account(
        owner.token,
        owner.csrf_token,
        username="sqlite.reviewer",
        display_name="SQLite Reviewer",
        password="Temporary!Reviewer123",
        role=AccountRole.REVIEWER,
        actor_id="ACTOR-SQLITE-REVIEWER",
        source="integration",
    ).account
    source_accounts.repository.change_password(
        reviewer_created.id, reviewer_created.password_hash, NOW
    )
    reviewer = source_accounts.repository.account_by_id(reviewer_created.id)
    assert reviewer is not None
    source_workflows.review(
        reviewer,
        request.id,
        ReviewDecision.APPROVE_FOR_GOVERNANCE,
        "Approved for migration evidence",
        NOW,
    )
    source_workflows.begin_execution(
        owner.account,
        request.id,
        module_id="swr",
        expected_operation="evidence.inspect",
        expected_resource="bundle:sqlite",
        mfa_verified_at=NOW,
    )
    source_receipt = source_workflows.finish_execution(
        request.id,
        status=ExecutionStatus.EXECUTED,
        action_id="swr:migration",
        outcome="ALLOW",
        reason="",
        output_json='{"recorded":true}',
        governance_evidence_sha256="e" * 64,
        event_hash="f" * 64,
        audit_hash="a" * 64,
    )
    source_analysis = source_workflows.record_analysis(
        owner.account,
        module_id="atlas",
        operation="atlas.projection.analyze",
        subject_id="claim-sqlite",
        input_json='{"claim_id":"claim-sqlite"}',
        input_sha256="1" * 64,
        output_json='{"posterior":0.5}',
        output_sha256="2" * 64,
        audit_hash="3" * 64,
        idempotency_key="analysis-sqlite",
    )
    source_hash = owner.account.password_hash

    counts = migrate(account_path, workflow_path, DSN)
    assert counts["accounts"] == 2
    assert counts["sessions"] == 1
    assert counts["work_requests"] == 1
    assert counts["execution_receipts"] == 1
    assert counts["analysis_receipts"] == 1
    target_account = PostgresAccountRepository(DSN).account_by_username("SQLITE.OWNER")
    assert target_account is not None and target_account.password_hash == source_hash
    target_workflows = PostgresWorkflowRepository(DSN)
    migrated_request = target_workflows.requests()[0]
    assert migrated_request.input_schema_version == "evidence.inspect/v1"
    assert migrated_request.inputs_json == '{"bundle_id":"sqlite"}'
    assert migrated_request.input_sha256 == request.input_sha256
    assert target_workflows.execution_receipt(request.id) == source_receipt
    assert target_workflows.analysis_by_id(source_analysis.id) == source_analysis
    with pytest.raises(RuntimeError, match="target is not empty"):
        migrate(account_path, workflow_path, DSN)
