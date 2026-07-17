"""SQLite storage for non-actuating human workflow records."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from workflows.models import (
    AnalysisReceipt,
    ExecutionReceipt,
    ExecutionStatus,
    RequestState,
    Review,
    ReviewDecision,
    WorkRequest,
)


class WorkflowRepositoryConflict(Exception):
    """Durable workflow state changed before an attempted transition committed."""


class WorkflowRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.migrate()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=5.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def migrate(self) -> None:
        with self._connect() as connection:
            current = int(connection.execute("PRAGMA user_version").fetchone()[0])
            if current > 4:
                raise RuntimeError(f"Workflow store schema {current} is newer than supported")
            if current == 0:
                connection.executescript(
                    """
                    CREATE TABLE work_requests (
                        id TEXT PRIMARY KEY,
                        created_by TEXT NOT NULL,
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
                    );
                    CREATE INDEX work_requests_state ON work_requests(state);
                    CREATE TABLE reviews (
                        id TEXT PRIMARY KEY,
                        request_id TEXT NOT NULL REFERENCES work_requests(id),
                        reviewer_account_id TEXT NOT NULL,
                        decision TEXT NOT NULL,
                        rationale TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        UNIQUE(request_id, reviewer_account_id)
                    );
                    CREATE TABLE execution_receipts (
                        request_id TEXT PRIMARY KEY REFERENCES work_requests(id),
                        attempt_id TEXT NOT NULL UNIQUE,
                        module_id TEXT NOT NULL,
                        initiated_by TEXT NOT NULL,
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
                    );
                    CREATE TABLE analysis_receipts (
                        id TEXT PRIMARY KEY,
                        module_id TEXT NOT NULL,
                        operation TEXT NOT NULL,
                        initiated_by TEXT NOT NULL,
                        subject_id TEXT NOT NULL,
                        input_json TEXT NOT NULL,
                        input_sha256 TEXT NOT NULL,
                        output_json TEXT NOT NULL,
                        output_sha256 TEXT NOT NULL,
                        audit_hash TEXT NOT NULL,
                        idempotency_key TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        UNIQUE(initiated_by, idempotency_key)
                    );
                    CREATE INDEX analysis_receipts_created ON analysis_receipts(created_at DESC);
                    PRAGMA user_version = 4;
                    """
                )
            elif current in {1, 2, 3}:
                if current == 1:
                    connection.executescript(
                        """
                    CREATE TABLE execution_receipts (
                        request_id TEXT PRIMARY KEY REFERENCES work_requests(id),
                        attempt_id TEXT NOT NULL UNIQUE,
                        module_id TEXT NOT NULL,
                        initiated_by TEXT NOT NULL,
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
                    );
                    """
                    )
                columns = {
                    str(row[1]) for row in connection.execute("PRAGMA table_info(work_requests)")
                }
                additions = {
                    "input_schema_version": "TEXT NOT NULL DEFAULT 'legacy/v0'",
                    "inputs_json": "TEXT NOT NULL DEFAULT '{}'",
                    "input_sha256": "TEXT NOT NULL DEFAULT ''",
                }
                for name, definition in additions.items():
                    if name not in columns:
                        connection.execute(
                            f"ALTER TABLE work_requests ADD COLUMN {name} {definition}"
                        )
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS analysis_receipts (
                        id TEXT PRIMARY KEY,
                        module_id TEXT NOT NULL,
                        operation TEXT NOT NULL,
                        initiated_by TEXT NOT NULL,
                        subject_id TEXT NOT NULL,
                        input_json TEXT NOT NULL,
                        input_sha256 TEXT NOT NULL,
                        output_json TEXT NOT NULL,
                        output_sha256 TEXT NOT NULL,
                        audit_hash TEXT NOT NULL,
                        idempotency_key TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        UNIQUE(initiated_by, idempotency_key)
                    );
                    CREATE INDEX IF NOT EXISTS analysis_receipts_created
                    ON analysis_receipts(created_at DESC);
                    PRAGMA user_version = 4;
                    """
                )

    @staticmethod
    def _request(row: sqlite3.Row) -> WorkRequest:
        return WorkRequest(
            id=str(row["id"]),
            created_by=str(row["created_by"]),
            title=str(row["title"]),
            operation=str(row["operation"]),
            resource=str(row["resource"]),
            input_schema_version=str(row["input_schema_version"]),
            inputs_json=str(row["inputs_json"]),
            input_sha256=str(row["input_sha256"]),
            rationale=str(row["rationale"]),
            idempotency_key=str(row["idempotency_key"]),
            state=RequestState(str(row["state"])),
            created_at=datetime.fromisoformat(str(row["created_at"])),
            updated_at=datetime.fromisoformat(str(row["updated_at"])),
        )

    def create_request(self, request: WorkRequest) -> WorkRequest:
        with self._connect() as connection:
            existing = connection.execute(
                "SELECT * FROM work_requests WHERE created_by = ? AND idempotency_key = ?",
                (request.created_by, request.idempotency_key),
            ).fetchone()
            if existing is not None:
                return self._request(existing)
            connection.execute(
                """INSERT INTO work_requests
                (id, created_by, title, operation, resource, input_schema_version,
                 inputs_json, input_sha256, rationale, idempotency_key, state, created_at,
                 updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
            )
        return request

    def request_by_id(self, request_id: str) -> WorkRequest | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM work_requests WHERE id = ?", (request_id,)
            ).fetchone()
        return self._request(row) if row is not None else None

    def requests(self) -> tuple[WorkRequest, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM work_requests ORDER BY created_at DESC"
            ).fetchall()
        return tuple(self._request(row) for row in rows)

    def add_review(self, review: Review, state: RequestState, updated_at: datetime) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            request_row = connection.execute(
                "SELECT state FROM work_requests WHERE id = ?", (review.request_id,)
            ).fetchone()
            if request_row is None:
                raise WorkflowRepositoryConflict("Request disappeared before review")
            if RequestState(str(request_row["state"])) is not RequestState.SUBMITTED:
                raise WorkflowRepositoryConflict("Request is no longer awaiting review")
            connection.execute(
                """INSERT INTO reviews
                (id, request_id, reviewer_account_id, decision, rationale, created_at)
                VALUES (?, ?, ?, ?, ?, ?)""",
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
                "UPDATE work_requests SET state = ?, updated_at = ? WHERE id = ?",
                (state.value, updated_at.isoformat(), review.request_id),
            )

    def has_review(self, request_id: str, reviewer_account_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM reviews WHERE request_id = ? AND reviewer_account_id = ?",
                (request_id, reviewer_account_id),
            ).fetchone()
        return row is not None

    def cancel_request(self, request_id: str, creator_id: str, updated_at: datetime) -> bool:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                """UPDATE work_requests SET state = ?, updated_at = ?
                WHERE id = ? AND created_by = ? AND state IN (?, ?)""",
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
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM reviews WHERE request_id = ? ORDER BY created_at", (request_id,)
            ).fetchall()
        return tuple(
            Review(
                id=str(row["id"]),
                request_id=str(row["request_id"]),
                reviewer_account_id=str(row["reviewer_account_id"]),
                decision=ReviewDecision(str(row["decision"])),
                rationale=str(row["rationale"]),
                created_at=datetime.fromisoformat(str(row["created_at"])),
            )
            for row in rows
        )

    @staticmethod
    def _receipt(row: sqlite3.Row) -> ExecutionReceipt:
        return ExecutionReceipt(
            request_id=str(row["request_id"]),
            attempt_id=str(row["attempt_id"]),
            module_id=str(row["module_id"]),
            initiated_by=str(row["initiated_by"]),
            status=ExecutionStatus(str(row["status"])),
            action_id=str(row["action_id"]),
            outcome=str(row["outcome"]),
            reason=str(row["reason"]),
            output_json=str(row["output_json"]),
            governance_evidence_sha256=str(row["governance_evidence_sha256"]),
            event_hash=str(row["event_hash"]),
            audit_hash=str(row["audit_hash"]),
            created_at=datetime.fromisoformat(str(row["created_at"])),
            completed_at=(
                datetime.fromisoformat(str(row["completed_at"]))
                if row["completed_at"] is not None
                else None
            ),
        )

    def execution_receipt(self, request_id: str) -> ExecutionReceipt | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM execution_receipts WHERE request_id = ?", (request_id,)
            ).fetchone()
        return self._receipt(row) if row is not None else None

    def reserve_execution(
        self,
        request_id: str,
        attempt_id: str,
        module_id: str,
        initiated_by: str,
        created_at: datetime,
    ) -> tuple[ExecutionReceipt, bool]:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT * FROM execution_receipts WHERE request_id = ?", (request_id,)
            ).fetchone()
            if existing is not None:
                return self._receipt(existing), False
            request_row = connection.execute(
                "SELECT state FROM work_requests WHERE id = ?", (request_id,)
            ).fetchone()
            if request_row is None:
                raise WorkflowRepositoryConflict("Request disappeared before execution")
            if RequestState(str(request_row["state"])) is not RequestState.REVIEWED_APPROVE:
                raise WorkflowRepositoryConflict("Request is not approved for execution")
            connection.execute(
                """INSERT INTO execution_receipts
                (request_id, attempt_id, module_id, initiated_by, status, action_id,
                 outcome, reason, output_json, governance_evidence_sha256, event_hash,
                 audit_hash, created_at, completed_at)
                VALUES (?, ?, ?, ?, ?, '', '', '', '{}', '', '', '', ?, NULL)""",
                (
                    request_id,
                    attempt_id,
                    module_id,
                    initiated_by,
                    ExecutionStatus.RUNNING.value,
                    created_at.isoformat(),
                ),
            )
            connection.execute(
                "UPDATE work_requests SET state = ?, updated_at = ? WHERE id = ?",
                (RequestState.EXECUTION_PENDING.value, created_at.isoformat(), request_id),
            )
            row = connection.execute(
                "SELECT * FROM execution_receipts WHERE request_id = ?", (request_id,)
            ).fetchone()
            if row is None:
                raise RuntimeError("Execution reservation did not persist")
            return self._receipt(row), True

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
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                """UPDATE execution_receipts SET status = ?, action_id = ?, outcome = ?,
                reason = ?, output_json = ?, governance_evidence_sha256 = ?, event_hash = ?,
                audit_hash = ?, completed_at = ? WHERE request_id = ? AND status = ?""",
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
            )
            if cursor.rowcount != 1:
                raise WorkflowRepositoryConflict("Execution attempt is no longer running")
            connection.execute(
                "UPDATE work_requests SET state = ?, updated_at = ? WHERE id = ?",
                (request_state.value, completed_at.isoformat(), request_id),
            )
            row = connection.execute(
                "SELECT * FROM execution_receipts WHERE request_id = ?", (request_id,)
            ).fetchone()
            if row is None:
                raise RuntimeError("Execution receipt disappeared after completion")
            return self._receipt(row)

    @staticmethod
    def _analysis(row: sqlite3.Row) -> AnalysisReceipt:
        return AnalysisReceipt(
            id=str(row["id"]),
            module_id=str(row["module_id"]),
            operation=str(row["operation"]),
            initiated_by=str(row["initiated_by"]),
            subject_id=str(row["subject_id"]),
            input_json=str(row["input_json"]),
            input_sha256=str(row["input_sha256"]),
            output_json=str(row["output_json"]),
            output_sha256=str(row["output_sha256"]),
            audit_hash=str(row["audit_hash"]),
            idempotency_key=str(row["idempotency_key"]),
            created_at=datetime.fromisoformat(str(row["created_at"])),
        )

    def create_analysis(self, receipt: AnalysisReceipt) -> AnalysisReceipt:
        with self._connect() as connection:
            existing = connection.execute(
                """SELECT * FROM analysis_receipts
                WHERE initiated_by = ? AND idempotency_key = ?""",
                (receipt.initiated_by, receipt.idempotency_key),
            ).fetchone()
            if existing is not None:
                return self._analysis(existing)
            connection.execute(
                """INSERT INTO analysis_receipts
                (id, module_id, operation, initiated_by, subject_id, input_json,
                 input_sha256, output_json, output_sha256, audit_hash,
                 idempotency_key, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
            )
        return receipt

    def analysis_by_id(self, receipt_id: str) -> AnalysisReceipt | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM analysis_receipts WHERE id = ?", (receipt_id,)
            ).fetchone()
        return self._analysis(row) if row is not None else None

    def analysis_by_idempotency(
        self, initiated_by: str, idempotency_key: str
    ) -> AnalysisReceipt | None:
        with self._connect() as connection:
            row = connection.execute(
                """SELECT * FROM analysis_receipts
                WHERE initiated_by = ? AND idempotency_key = ?""",
                (initiated_by, idempotency_key),
            ).fetchone()
        return self._analysis(row) if row is not None else None

    def analyses(
        self,
        limit: int = 100,
        *,
        module_id: str | None = None,
        operation: str | None = None,
    ) -> tuple[AnalysisReceipt, ...]:
        clauses: list[str] = []
        values: list[str | int] = []
        if module_id is not None:
            clauses.append("module_id = ?")
            values.append(module_id)
        if operation is not None:
            clauses.append("operation = ?")
            values.append(operation)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        values.append(limit)
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT * FROM analysis_receipts{where} ORDER BY created_at DESC LIMIT ?",
                tuple(values),
            ).fetchall()
        return tuple(self._analysis(row) for row in rows)
