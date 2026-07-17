"""One-time, fail-closed SQLite to PostgreSQL human-state migration."""

from __future__ import annotations

import argparse
import os
import sqlite3
from collections.abc import Callable, Sequence
from pathlib import Path

import psycopg
from psycopg import Connection, sql

from accounts import PostgresAccountRepository
from workflows import PostgresWorkflowRepository

Transform = Callable[[sqlite3.Row], tuple[object, ...]]


def _identity(columns: Sequence[str]) -> Transform:
    return lambda row: tuple(row[column] for column in columns)


def _accounts(row: sqlite3.Row) -> tuple[object, ...]:
    return (
        row["id"],
        row["username"],
        str(row["username"]).casefold(),
        row["display_name"],
        row["password_hash"],
        row["role"],
        row["status"],
        row["actor_id"],
        row["failed_attempts"],
        row["locked_until"],
        row["created_at"],
        row["password_changed_at"],
        row["mfa_secret_ciphertext"],
        bool(row["mfa_enabled"]),
        row["mfa_last_counter"],
        bool(row["must_change_password"]),
    )


ACCOUNT_TABLES: tuple[tuple[str, tuple[str, ...], Transform], ...] = (
    (
        "accounts",
        (
            "id",
            "username",
            "username_normalized",
            "display_name",
            "password_hash",
            "role",
            "status",
            "actor_id",
            "failed_attempts",
            "locked_until",
            "created_at",
            "password_changed_at",
            "mfa_secret_ciphertext",
            "mfa_enabled",
            "mfa_last_counter",
            "must_change_password",
        ),
        _accounts,
    ),
    (
        "sessions",
        (
            "id",
            "account_id",
            "token_hash",
            "csrf_hash",
            "created_at",
            "last_seen_at",
            "idle_expires_at",
            "absolute_expires_at",
            "user_agent",
            "client_host",
            "revoked_at",
            "mfa_verified_at",
        ),
        _identity(
            (
                "id",
                "account_id",
                "token_hash",
                "csrf_hash",
                "created_at",
                "last_seen_at",
                "idle_expires_at",
                "absolute_expires_at",
                "user_agent",
                "client_host",
                "revoked_at",
                "mfa_verified_at",
            )
        ),
    ),
    (
        "recovery_codes",
        ("account_id", "code_hash", "created_at", "used_at"),
        _identity(("account_id", "code_hash", "created_at", "used_at")),
    ),
    (
        "security_events",
        ("id", "event_type", "account_id", "occurred_at", "source", "detail"),
        _identity(("id", "event_type", "account_id", "occurred_at", "source", "detail")),
    ),
    (
        "auth_rate_limits",
        ("bucket", "window_started", "attempts", "blocked_until"),
        _identity(("bucket", "window_started", "attempts", "blocked_until")),
    ),
)

WORKFLOW_TABLES: tuple[tuple[str, tuple[str, ...], Transform], ...] = (
    (
        "work_requests",
        (
            "id",
            "created_by",
            "title",
            "operation",
            "resource",
            "input_schema_version",
            "inputs_json",
            "input_sha256",
            "rationale",
            "idempotency_key",
            "state",
            "created_at",
            "updated_at",
        ),
        _identity(
            (
                "id",
                "created_by",
                "title",
                "operation",
                "resource",
                "input_schema_version",
                "inputs_json",
                "input_sha256",
                "rationale",
                "idempotency_key",
                "state",
                "created_at",
                "updated_at",
            )
        ),
    ),
    (
        "reviews",
        ("id", "request_id", "reviewer_account_id", "decision", "rationale", "created_at"),
        _identity(
            ("id", "request_id", "reviewer_account_id", "decision", "rationale", "created_at")
        ),
    ),
    (
        "execution_receipts",
        (
            "request_id",
            "attempt_id",
            "module_id",
            "initiated_by",
            "status",
            "action_id",
            "outcome",
            "reason",
            "output_json",
            "governance_evidence_sha256",
            "event_hash",
            "audit_hash",
            "created_at",
            "completed_at",
        ),
        _identity(
            (
                "request_id",
                "attempt_id",
                "module_id",
                "initiated_by",
                "status",
                "action_id",
                "outcome",
                "reason",
                "output_json",
                "governance_evidence_sha256",
                "event_hash",
                "audit_hash",
                "created_at",
                "completed_at",
            )
        ),
    ),
    (
        "analysis_receipts",
        (
            "id",
            "module_id",
            "operation",
            "initiated_by",
            "subject_id",
            "input_json",
            "input_sha256",
            "output_json",
            "output_sha256",
            "audit_hash",
            "idempotency_key",
            "created_at",
        ),
        _identity(
            (
                "id",
                "module_id",
                "operation",
                "initiated_by",
                "subject_id",
                "input_json",
                "input_sha256",
                "output_json",
                "output_sha256",
                "audit_hash",
                "idempotency_key",
                "created_at",
            )
        ),
    ),
)


def _source(path: Path, expected_version: int) -> sqlite3.Connection:
    if not path.is_file():
        raise FileNotFoundError(f"SQLite source does not exist: {path}")
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if version != expected_version:
        connection.close()
        raise RuntimeError(
            f"SQLite source {path} has schema {version}; expected {expected_version}"
        )
    return connection


def _copy_tables(
    source: sqlite3.Connection,
    target: Connection[tuple[object, ...]],
    specifications: Sequence[tuple[str, tuple[str, ...], Transform]],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for table, columns, transform in specifications:
        rows = source.execute(f"SELECT * FROM {table}").fetchall()
        statement = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join(sql.Placeholder() for _ in columns),
        )
        with target.cursor() as cursor:
            cursor.executemany(statement, (transform(row) for row in rows))
        counts[table] = len(rows)
    return counts


def migrate(account_db: Path, workflow_db: Path, database_url: str) -> dict[str, int]:
    PostgresAccountRepository(database_url).migrate()
    PostgresWorkflowRepository(database_url).migrate()
    accounts = _source(account_db, 4)
    workflows = _source(workflow_db, 4)
    try:
        with psycopg.connect(database_url) as target:
            target.execute("SELECT pg_advisory_xact_lock(hashtext('project-ai-human-migration'))")
            populated = target.execute(
                """SELECT
                    (SELECT COUNT(*) FROM accounts) +
                    (SELECT COUNT(*) FROM sessions) +
                    (SELECT COUNT(*) FROM recovery_codes) +
                    (SELECT COUNT(*) FROM security_events) +
                    (SELECT COUNT(*) FROM auth_rate_limits) +
                    (SELECT COUNT(*) FROM work_requests) +
                    (SELECT COUNT(*) FROM reviews) +
                    (SELECT COUNT(*) FROM execution_receipts) +
                    (SELECT COUNT(*) FROM analysis_receipts)"""
            ).fetchone()
            if populated is None or int(populated[0]) != 0:
                raise RuntimeError("PostgreSQL target is not empty; migration refused")
            counts = _copy_tables(accounts, target, ACCOUNT_TABLES)
            counts.update(_copy_tables(workflows, target, WORKFLOW_TABLES))
            target.execute(
                """SELECT setval(
                    pg_get_serial_sequence('security_events', 'id'),
                    COALESCE((SELECT MAX(id) FROM security_events), 1),
                    EXISTS (SELECT 1 FROM security_events)
                )"""
            )
        return counts
    finally:
        accounts.close()
        workflows.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--account-db", type=Path, required=True)
    parser.add_argument("--workflow-db", type=Path, required=True)
    parser.add_argument("--database-url-env", default="PROJECT_AI_DATABASE_URL")
    arguments = parser.parse_args()
    database_url = os.getenv(arguments.database_url_env)
    if not database_url:
        parser.error(f"{arguments.database_url_env} is not set")
    counts = migrate(arguments.account_db, arguments.workflow_db, database_url)
    for table, count in counts.items():
        print(f"{table}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
