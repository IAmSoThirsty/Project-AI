"""PostgreSQL repository for multi-replica non-actuating human workflows."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from datetime import datetime

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row

from workflows.models import (
    AnalysisReceipt,
    ExecutionReceipt,
    ExecutionStatus,
    RequestState,
    Review,
    ReviewDecision,
    WorkRequest,
)
from workflows.repository import WorkflowRepository, WorkflowRepositoryConflict

SCHEMA_VERSION = 4
Row = Mapping[str, object]


def _text(value: object) -> str:
    return str(value)


class PostgresWorkflowRepository(WorkflowRepository):
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self.migrate()

    @contextmanager
    def _pg_connect(self) -> Iterator[Connection[dict[str, object]]]:
        with psycopg.connect(self.dsn, row_factory=dict_row) as connection:
            yield connection

    def migrate(self) -> None:
        with self._pg_connect() as connection:
            connection.execute(
                "SELECT pg_advisory_xact_lock(hashtext('project-ai-workflows-schema'))"
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS project_ai_schema_versions (
                    component TEXT PRIMARY KEY,
                    version INTEGER NOT NULL
                )"""
            )
            row = connection.execute(
                "SELECT version FROM project_ai_schema_versions WHERE component = 'workflows'"
            ).fetchone()
            current = int(_text(row["version"])) if row else 0
            if current > SCHEMA_VERSION:
                raise RuntimeError(f"Workflow store schema {current} is newer than supported")
            if current == 0:
                connection.execute(
                    """CREATE TABLE work_requests (
                        id TEXT PRIMARY KEY,
                        created_by TEXT NOT NULL REFERENCES accounts(id),
                        title TEXT NOT NULL,
                        operation TEXT NOT NULL,
                        resource TEXT NOT NULL,
                        input_schema_version TEXT NOT NULL,
                        inputs_json TEXT NOT NULL,
                        input_sha256 TEXT NOT NULL,
                        rationale TEXT NOT NULL,
                        idempotency_key TEXT NOT NULL,
                        state TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        UNIQUE(created_by, idempotency_key)
                    )"""
                )
                connection.execute("CREATE INDEX work_requests_state ON work_requests(state)")
                connection.execute(
                    """CREATE TABLE reviews (
                        id TEXT PRIMARY KEY,
                        request_id TEXT NOT NULL REFERENCES work_requests(id) ON DELETE CASCADE,
                        reviewer_account_id TEXT NOT NULL REFERENCES accounts(id),
                        decision TEXT NOT NULL,
                        rationale TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        UNIQUE(request_id, reviewer_account_id)
                    )"""
                )
                self._create_execution_receipts(connection)
                self._create_analysis_receipts(connection)
                connection.execute(
                    "INSERT INTO project_ai_schema_versions (component, version) VALUES ('workflows', %s)",
                    (SCHEMA_VERSION,),
                )
            elif current in {1, 2, 3}:
                if current == 1:
                    self._create_execution_receipts(connection)
                connection.execute(
                    "ALTER TABLE work_requests ADD COLUMN IF NOT EXISTS input_schema_version TEXT NOT NULL DEFAULT 'legacy/v0'"
                )
                connection.execute(
                    "ALTER TABLE work_requests ADD COLUMN IF NOT EXISTS inputs_json TEXT NOT NULL DEFAULT '{}'"
                )
                connection.execute(
                    "ALTER TABLE work_requests ADD COLUMN IF NOT EXISTS input_sha256 TEXT NOT NULL DEFAULT ''"
                )
                self._create_analysis_receipts(connection)
                connection.execute(
                    "UPDATE project_ai_schema_versions SET version = %s WHERE component = 'workflows'",
                    (SCHEMA_VERSION,),
                )

    @staticmethod
    def _create_execution_receipts(connection: Connection[dict[str, object]]) -> None:
        connection.execute(
            """CREATE TABLE execution_receipts (
                request_id TEXT PRIMARY KEY REFERENCES work_requests(id) ON DELETE CASCADE,
                attempt_id TEXT NOT NULL UNIQUE,
                module_id TEXT NOT NULL,
                initiated_by TEXT NOT NULL REFERENCES accounts(id),
                status TEXT NOT NULL,
                action_id TEXT NOT NULL,
                outcome TEXT NOT NULL,
                reason TEXT NOT NULL,
                output_json TEXT NOT NULL,
                governance_evidence_sha256 TEXT NOT NULL,
                event_hash TEXT NOT NULL,
                audit_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )"""
        )

    @staticmethod
    def _create_analysis_receipts(connection: Connection[dict[str, object]]) -> None:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS analysis_receipts (
                id TEXT PRIMARY KEY,
                module_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                initiated_by TEXT NOT NULL REFERENCES accounts(id),
                subject_id TEXT NOT NULL,
                input_json TEXT NOT NULL,
                input_sha256 TEXT NOT NULL,
                output_json TEXT NOT NULL,
                output_sha256 TEXT NOT NULL,
                audit_hash TEXT NOT NULL,
                idempotency_key TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(initiated_by, idempotency_key)
            )"""
        )
        connection.execute(
            """CREATE INDEX IF NOT EXISTS analysis_receipts_created
            ON analysis_receipts(created_at DESC)"""
        )

    @staticmethod
    def _request_pg(row: Row) -> WorkRequest:
        return WorkRequest(
            id=_text(row["id"]),
            created_by=_text(row["created_by"]),
            title=_text(row["title"]),
            operation=_text(row["operation"]),
            resource=_text(row["resource"]),
            input_schema_version=_text(row["input_schema_version"]),
            inputs_json=_text(row["inputs_json"]),
            input_sha256=_text(row["input_sha256"]),
            rationale=_text(row["rationale"]),
            idempotency_key=_text(row["idempotency_key"]),
            state=RequestState(_text(row["state"])),
            created_at=datetime.fromisoformat(_text(row["created_at"])),
            updated_at=datetime.fromisoformat(_text(row["updated_at"])),
        )

    def create_request(self, request: WorkRequest) -> WorkRequest:
        with self._pg_connect() as connection:
            row = connection.execute(
                """INSERT INTO work_requests
                (id, created_by, title, operation, resource, input_schema_version,
                 inputs_json, input_sha256, rationale, idempotency_key, state, created_at,
                 updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (created_by, idempotency_key) DO UPDATE
                SET idempotency_key = EXCLUDED.idempotency_key
                RETURNING *""",
                (
                    request.id,
                    request.created_by,
                    request.title,
                    request.operation,
                    request.resource,
                    request.input_schema_version,
                    request.inputs_json,
                    request.input_sha256,
                    request.rationale,
                    request.idempotency_key,
                    request.state.value,
                    request.created_at.isoformat(),
                    request.updated_at.isoformat(),
                ),
            ).fetchone()
        if row is None:
            raise RuntimeError("Request insert returned no durable row")
        return self._request_pg(row)

    def request_by_id(self, request_id: str) -> WorkRequest | None:
        with self._pg_connect() as connection:
            row = connection.execute(
                "SELECT * FROM work_requests WHERE id = %s", (request_id,)
            ).fetchone()
        return self._request_pg(row) if row is not None else None

    def requests(self) -> tuple[WorkRequest, ...]:
        with self._pg_connect() as connection:
            rows = connection.execute(
                "SELECT * FROM work_requests ORDER BY created_at DESC"
            ).fetchall()
        return tuple(self._request_pg(row) for row in rows)

    def add_review(self, review: Review, state: RequestState, updated_at: datetime) -> None:
        with self._pg_connect() as connection:
            request_row = connection.execute(
                "SELECT state FROM work_requests WHERE id = %s FOR UPDATE", (review.request_id,)
            ).fetchone()
            if request_row is None:
                raise WorkflowRepositoryConflict("Request disappeared before review")
            if RequestState(_text(request_row["state"])) is not RequestState.SUBMITTED:
                raise WorkflowRepositoryConflict("Request is no longer awaiting review")
            connection.execute(
                """INSERT INTO reviews
                (id, request_id, reviewer_account_id, decision, rationale, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    review.id,
                    review.request_id,
                    review.reviewer_account_id,
                    review.decision.value,
                    review.rationale,
                    review.created_at.isoformat(),
                ),
            )
            connection.execute(
                "UPDATE work_requests SET state = %s, updated_at = %s WHERE id = %s",
                (state.value, updated_at.isoformat(), review.request_id),
            )

    def has_review(self, request_id: str, reviewer_account_id: str) -> bool:
        with self._pg_connect() as connection:
            row = connection.execute(
                "SELECT 1 AS present FROM reviews WHERE request_id = %s AND reviewer_account_id = %s",
                (request_id, reviewer_account_id),
            ).fetchone()
        return row is not None

    def cancel_request(self, request_id: str, creator_id: str, updated_at: datetime) -> bool:
        with self._pg_connect() as connection:
            cursor = connection.execute(
                """UPDATE work_requests SET state = %s, updated_at = %s
                WHERE id = %s AND created_by = %s AND state IN (%s, %s)""",
                (
                    RequestState.CANCELLED.value,
                    updated_at.isoformat(),
                    request_id,
                    creator_id,
                    RequestState.SUBMITTED.value,
                    RequestState.NEEDS_INFORMATION.value,
                ),
            )
            return cursor.rowcount == 1

    def reviews_for(self, request_id: str) -> tuple[Review, ...]:
        with self._pg_connect() as connection:
            rows = connection.execute(
                "SELECT * FROM reviews WHERE request_id = %s ORDER BY created_at", (request_id,)
            ).fetchall()
        return tuple(
            Review(
                id=_text(row["id"]),
                request_id=_text(row["request_id"]),
                reviewer_account_id=_text(row["reviewer_account_id"]),
                decision=ReviewDecision(_text(row["decision"])),
                rationale=_text(row["rationale"]),
                created_at=datetime.fromisoformat(_text(row["created_at"])),
            )
            for row in rows
        )

    @staticmethod
    def _receipt_pg(row: Row) -> ExecutionReceipt:
        completed = row["completed_at"]
        return ExecutionReceipt(
            request_id=_text(row["request_id"]),
            attempt_id=_text(row["attempt_id"]),
            module_id=_text(row["module_id"]),
            initiated_by=_text(row["initiated_by"]),
            status=ExecutionStatus(_text(row["status"])),
            action_id=_text(row["action_id"]),
            outcome=_text(row["outcome"]),
            reason=_text(row["reason"]),
            output_json=_text(row["output_json"]),
            governance_evidence_sha256=_text(row["governance_evidence_sha256"]),
            event_hash=_text(row["event_hash"]),
            audit_hash=_text(row["audit_hash"]),
            created_at=datetime.fromisoformat(_text(row["created_at"])),
            completed_at=datetime.fromisoformat(_text(completed))
            if completed is not None
            else None,
        )

    def execution_receipt(self, request_id: str) -> ExecutionReceipt | None:
        with self._pg_connect() as connection:
            row = connection.execute(
                "SELECT * FROM execution_receipts WHERE request_id = %s", (request_id,)
            ).fetchone()
        return self._receipt_pg(row) if row is not None else None

    def reserve_execution(
        self,
        request_id: str,
        attempt_id: str,
        module_id: str,
        initiated_by: str,
        created_at: datetime,
    ) -> tuple[ExecutionReceipt, bool]:
        with self._pg_connect() as connection:
            request_row = connection.execute(
                "SELECT state FROM work_requests WHERE id = %s FOR UPDATE", (request_id,)
            ).fetchone()
            if request_row is None:
                raise WorkflowRepositoryConflict("Request disappeared before execution")
            existing = connection.execute(
                "SELECT * FROM execution_receipts WHERE request_id = %s", (request_id,)
            ).fetchone()
            if existing is not None:
                return self._receipt_pg(existing), False
            if RequestState(_text(request_row["state"])) is not RequestState.REVIEWED_APPROVE:
                raise WorkflowRepositoryConflict("Request is not approved for execution")
            row = connection.execute(
                """INSERT INTO execution_receipts
                (request_id, attempt_id, module_id, initiated_by, status, action_id,
                 outcome, reason, output_json, governance_evidence_sha256, event_hash,
                 audit_hash, created_at, completed_at)
                VALUES (%s, %s, %s, %s, %s, '', '', '', '{}', '', '', '', %s, NULL)
                RETURNING *""",
                (
                    request_id,
                    attempt_id,
                    module_id,
                    initiated_by,
                    ExecutionStatus.RUNNING.value,
                    created_at.isoformat(),
                ),
            ).fetchone()
            connection.execute(
                "UPDATE work_requests SET state = %s, updated_at = %s WHERE id = %s",
                (RequestState.EXECUTION_PENDING.value, created_at.isoformat(), request_id),
            )
        if row is None:
            raise RuntimeError("Execution reservation did not persist")
        return self._receipt_pg(row), True

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
        completed_at: datetime,
    ) -> ExecutionReceipt:
        request_state = {
            ExecutionStatus.EXECUTED: RequestState.EXECUTED,
            ExecutionStatus.BLOCKED: RequestState.EXECUTION_BLOCKED,
            ExecutionStatus.FAILED: RequestState.EXECUTION_FAILED,
        }.get(status)
        if request_state is None:
            raise ValueError("Execution can only finish in a terminal state")
        with self._pg_connect() as connection:
            row = connection.execute(
                """UPDATE execution_receipts SET status = %s, action_id = %s, outcome = %s,
                reason = %s, output_json = %s, governance_evidence_sha256 = %s,
                event_hash = %s, audit_hash = %s, completed_at = %s
                WHERE request_id = %s AND status = %s RETURNING *""",
                (
                    status.value,
                    action_id,
                    outcome,
                    reason,
                    output_json,
                    governance_evidence_sha256,
                    event_hash,
                    audit_hash,
                    completed_at.isoformat(),
                    request_id,
                    ExecutionStatus.RUNNING.value,
                ),
            ).fetchone()
            if row is None:
                raise WorkflowRepositoryConflict("Execution attempt is no longer running")
            connection.execute(
                "UPDATE work_requests SET state = %s, updated_at = %s WHERE id = %s",
                (request_state.value, completed_at.isoformat(), request_id),
            )
        return self._receipt_pg(row)

    @staticmethod
    def _analysis_pg(row: Row) -> AnalysisReceipt:
        return AnalysisReceipt(
            id=_text(row["id"]),
            module_id=_text(row["module_id"]),
            operation=_text(row["operation"]),
            initiated_by=_text(row["initiated_by"]),
            subject_id=_text(row["subject_id"]),
            input_json=_text(row["input_json"]),
            input_sha256=_text(row["input_sha256"]),
            output_json=_text(row["output_json"]),
            output_sha256=_text(row["output_sha256"]),
            audit_hash=_text(row["audit_hash"]),
            idempotency_key=_text(row["idempotency_key"]),
            created_at=datetime.fromisoformat(_text(row["created_at"])),
        )

    def create_analysis(self, receipt: AnalysisReceipt) -> AnalysisReceipt:
        with self._pg_connect() as connection:
            row = connection.execute(
                """INSERT INTO analysis_receipts
                (id, module_id, operation, initiated_by, subject_id, input_json,
                 input_sha256, output_json, output_sha256, audit_hash,
                 idempotency_key, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (initiated_by, idempotency_key) DO UPDATE
                SET idempotency_key = EXCLUDED.idempotency_key
                RETURNING *""",
                (
                    receipt.id,
                    receipt.module_id,
                    receipt.operation,
                    receipt.initiated_by,
                    receipt.subject_id,
                    receipt.input_json,
                    receipt.input_sha256,
                    receipt.output_json,
                    receipt.output_sha256,
                    receipt.audit_hash,
                    receipt.idempotency_key,
                    receipt.created_at.isoformat(),
                ),
            ).fetchone()
        if row is None:
            raise RuntimeError("Analysis receipt insert returned no durable row")
        return self._analysis_pg(row)

    def analysis_by_id(self, receipt_id: str) -> AnalysisReceipt | None:
        with self._pg_connect() as connection:
            row = connection.execute(
                "SELECT * FROM analysis_receipts WHERE id = %s", (receipt_id,)
            ).fetchone()
        return self._analysis_pg(row) if row is not None else None

    def analysis_by_idempotency(
        self, initiated_by: str, idempotency_key: str
    ) -> AnalysisReceipt | None:
        with self._pg_connect() as connection:
            row = connection.execute(
                """SELECT * FROM analysis_receipts
                WHERE initiated_by = %s AND idempotency_key = %s""",
                (initiated_by, idempotency_key),
            ).fetchone()
        return self._analysis_pg(row) if row is not None else None

    def analyses(
        self,
        limit: int = 100,
        *,
        module_id: str | None = None,
        operation: str | None = None,
    ) -> tuple[AnalysisReceipt, ...]:
        clauses: list[str] = []
        values: list[object] = []
        if module_id is not None:
            clauses.append("module_id = %s")
            values.append(module_id)
        if operation is not None:
            clauses.append("operation = %s")
            values.append(operation)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        values.append(limit)
        with self._pg_connect() as connection:
            rows = connection.execute(
                f"SELECT * FROM analysis_receipts{where} ORDER BY created_at DESC LIMIT %s",
                tuple(values),
            ).fetchall()
        return tuple(self._analysis_pg(row) for row in rows)
