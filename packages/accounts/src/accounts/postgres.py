"""PostgreSQL repository for multi-replica human authentication state."""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from datetime import datetime

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row

from accounts.models import (
    Account,
    AccountRole,
    MachineCredential,
    SecurityEvent,
    StoredSession,
)
from accounts.repository import SCHEMA_VERSION, AccountRepository, _parse_datetime

Row = Mapping[str, object]


def _text(value: object) -> str:
    return str(value)


class PostgresAccountRepository(AccountRepository):
    """Account repository with transactional PostgreSQL concurrency controls."""

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    @contextmanager
    def _pg_connect(self) -> Iterator[Connection[dict[str, object]]]:
        with psycopg.connect(self.dsn, row_factory=dict_row) as connection:
            yield connection

    def migrate(self) -> None:
        with self._pg_connect() as connection:
            connection.execute(
                "SELECT pg_advisory_xact_lock(hashtext('project-ai-accounts-schema'))"
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS project_ai_schema_versions (
                    component TEXT PRIMARY KEY,
                    version INTEGER NOT NULL
                )"""
            )
            row = connection.execute(
                "SELECT version FROM project_ai_schema_versions WHERE component = 'accounts'"
            ).fetchone()
            current = int(_text(row["version"])) if row else 0
            if current > SCHEMA_VERSION:
                raise RuntimeError(f"Account store schema {current} is newer than supported")
            if current == 0:
                connection.execute(
                    """CREATE TABLE accounts (
                        id TEXT PRIMARY KEY,
                        username TEXT NOT NULL,
                        username_normalized TEXT NOT NULL UNIQUE,
                        display_name TEXT NOT NULL,
                        password_hash TEXT NOT NULL,
                        role TEXT NOT NULL,
                        status TEXT NOT NULL CHECK(status IN ('active', 'disabled')),
                        actor_id TEXT,
                        failed_attempts INTEGER NOT NULL DEFAULT 0,
                        locked_until TEXT,
                        created_at TEXT NOT NULL,
                        password_changed_at TEXT NOT NULL,
                        mfa_secret_ciphertext TEXT,
                        mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
                        mfa_last_counter BIGINT,
                        must_change_password BOOLEAN NOT NULL DEFAULT FALSE
                    )"""
                )
                connection.execute(
                    """CREATE TABLE sessions (
                        id TEXT PRIMARY KEY,
                        account_id TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                        token_hash TEXT NOT NULL UNIQUE,
                        csrf_hash TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        last_seen_at TEXT NOT NULL,
                        idle_expires_at TEXT NOT NULL,
                        absolute_expires_at TEXT NOT NULL,
                        user_agent TEXT NOT NULL,
                        client_host TEXT NOT NULL,
                        revoked_at TEXT,
                        mfa_verified_at TEXT
                    )"""
                )
                connection.execute("CREATE INDEX sessions_account_id ON sessions(account_id)")
                connection.execute(
                    """CREATE TABLE recovery_codes (
                        account_id TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                        code_hash TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        used_at TEXT,
                        PRIMARY KEY(account_id, code_hash)
                    )"""
                )
                connection.execute(
                    """CREATE TABLE security_events (
                        id BIGSERIAL PRIMARY KEY,
                        event_type TEXT NOT NULL,
                        account_id TEXT REFERENCES accounts(id) ON DELETE SET NULL,
                        occurred_at TEXT NOT NULL,
                        source TEXT NOT NULL,
                        detail TEXT NOT NULL
                    )"""
                )
                connection.execute(
                    "CREATE INDEX security_events_account_id ON security_events(account_id)"
                )
                connection.execute(
                    """CREATE TABLE auth_rate_limits (
                        bucket TEXT PRIMARY KEY,
                        window_started TEXT NOT NULL,
                        attempts INTEGER NOT NULL,
                        blocked_until TEXT
                    )"""
                )
                connection.execute(
                    "INSERT INTO project_ai_schema_versions (component, version) VALUES ('accounts', %s)",
                    (SCHEMA_VERSION,),
                )
            elif current < SCHEMA_VERSION:
                if current == 4:
                    connection.execute(
                        """CREATE TABLE IF NOT EXISTS machine_credentials (
                            id TEXT PRIMARY KEY,
                            label TEXT NOT NULL,
                            token_hash TEXT NOT NULL UNIQUE,
                            scopes JSONB NOT NULL,
                            created_at TEXT NOT NULL,
                            created_by TEXT NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
                            last_used_at TEXT,
                            revoked_at TEXT
                        )"""
                    )
                    connection.execute(
                        "CREATE INDEX IF NOT EXISTS machine_credentials_active ON machine_credentials(revoked_at)"
                    )
                    connection.execute(
                        "UPDATE project_ai_schema_versions SET version = %s WHERE component = 'accounts'",
                        (SCHEMA_VERSION,),
                    )
                else:
                    raise RuntimeError(
                        f"PostgreSQL account schema {current} requires an explicit migration"
                    )

            if current == 0:
                connection.execute(
                    """CREATE TABLE IF NOT EXISTS machine_credentials (
                        id TEXT PRIMARY KEY,
                        label TEXT NOT NULL,
                        token_hash TEXT NOT NULL UNIQUE,
                        scopes JSONB NOT NULL,
                        created_at TEXT NOT NULL,
                        created_by TEXT NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
                        last_used_at TEXT,
                        revoked_at TEXT
                    )"""
                )
                connection.execute(
                    "CREATE INDEX IF NOT EXISTS machine_credentials_active ON machine_credentials(revoked_at)"
                )
                connection.execute(
                    "UPDATE project_ai_schema_versions SET version = %s WHERE component = 'accounts'",
                    (SCHEMA_VERSION,),
                )

    @staticmethod
    def _account_pg(row: Row | None) -> Account | None:
        if row is None:
            return None
        return Account(
            id=_text(row["id"]),
            username=_text(row["username"]),
            display_name=_text(row["display_name"]),
            password_hash=_text(row["password_hash"]),
            role=AccountRole(_text(row["role"])),
            status=_text(row["status"]),
            actor_id=None if row["actor_id"] is None else _text(row["actor_id"]),
            failed_attempts=int(_text(row["failed_attempts"])),
            locked_until=_parse_datetime(
                None if row["locked_until"] is None else _text(row["locked_until"])
            ),
            created_at=datetime.fromisoformat(_text(row["created_at"])),
            password_changed_at=datetime.fromisoformat(_text(row["password_changed_at"])),
            mfa_secret_ciphertext=(
                None
                if row["mfa_secret_ciphertext"] is None
                else _text(row["mfa_secret_ciphertext"])
            ),
            mfa_enabled=bool(row["mfa_enabled"]),
            mfa_last_counter=(
                None if row["mfa_last_counter"] is None else int(_text(row["mfa_last_counter"]))
            ),
            must_change_password=bool(row["must_change_password"]),
        )

    @staticmethod
    def _session_pg(row: Row | None) -> StoredSession | None:
        if row is None:
            return None
        return StoredSession(
            id=_text(row["id"]),
            account_id=_text(row["account_id"]),
            token_hash=_text(row["token_hash"]),
            csrf_hash=_text(row["csrf_hash"]),
            created_at=datetime.fromisoformat(_text(row["created_at"])),
            last_seen_at=datetime.fromisoformat(_text(row["last_seen_at"])),
            idle_expires_at=datetime.fromisoformat(_text(row["idle_expires_at"])),
            absolute_expires_at=datetime.fromisoformat(_text(row["absolute_expires_at"])),
            user_agent=_text(row["user_agent"]),
            client_host=_text(row["client_host"]),
            revoked_at=_parse_datetime(
                None if row["revoked_at"] is None else _text(row["revoked_at"])
            ),
            mfa_verified_at=_parse_datetime(
                None if row["mfa_verified_at"] is None else _text(row["mfa_verified_at"])
            ),
        )

    @staticmethod
    def _account_values(account: Account) -> tuple[object, ...]:
        return (
            account.id,
            account.username,
            account.username.casefold(),
            account.display_name,
            account.password_hash,
            account.role.value,
            account.status,
            account.actor_id,
            account.failed_attempts,
            account.locked_until.isoformat() if account.locked_until else None,
            account.created_at.isoformat(),
            account.password_changed_at.isoformat(),
            account.mfa_secret_ciphertext,
            account.mfa_enabled,
            account.mfa_last_counter,
            account.must_change_password,
        )

    @staticmethod
    def _insert_account(connection: Connection[dict[str, object]], account: Account) -> None:
        connection.execute(
            """INSERT INTO accounts
            (id, username, username_normalized, display_name, password_hash, role, status,
             actor_id, failed_attempts, locked_until, created_at, password_changed_at,
             mfa_secret_ciphertext, mfa_enabled, mfa_last_counter, must_change_password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            PostgresAccountRepository._account_values(account),
        )

    def account_count(self) -> int:
        with self._pg_connect() as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM accounts").fetchone()
        return int(_text(row["count"])) if row else 0

    def create_account(self, account: Account) -> None:
        with self._pg_connect() as connection:
            self._insert_account(connection, account)

    def create_bootstrap_account(self, account: Account) -> bool:
        with self._pg_connect() as connection:
            connection.execute(
                "SELECT pg_advisory_xact_lock(hashtext('project-ai-owner-bootstrap'))"
            )
            row = connection.execute("SELECT COUNT(*) AS count FROM accounts").fetchone()
            if row and int(_text(row["count"])) != 0:
                return False
            self._insert_account(connection, account)
            return True

    def account_by_username(self, username: str) -> Account | None:
        with self._pg_connect() as connection:
            row = connection.execute(
                "SELECT * FROM accounts WHERE username_normalized = %s", (username.casefold(),)
            ).fetchone()
        return self._account_pg(row)

    def account_by_id(self, account_id: str) -> Account | None:
        with self._pg_connect() as connection:
            row = connection.execute(
                "SELECT * FROM accounts WHERE id = %s", (account_id,)
            ).fetchone()
        return self._account_pg(row)

    def accounts(self) -> tuple[Account, ...]:
        with self._pg_connect() as connection:
            rows = connection.execute("SELECT * FROM accounts ORDER BY created_at, id").fetchall()
        return tuple(account for row in rows if (account := self._account_pg(row)) is not None)

    def set_account_role(self, account_id: str, role: AccountRole) -> bool:
        with self._pg_connect() as connection:
            cursor = connection.execute(
                "UPDATE accounts SET role = %s WHERE id = %s", (role.value, account_id)
            )
            return cursor.rowcount == 1

    def set_account_status(self, account_id: str, status: str) -> bool:
        with self._pg_connect() as connection:
            cursor = connection.execute(
                "UPDATE accounts SET status = %s WHERE id = %s", (status, account_id)
            )
            return cursor.rowcount == 1

    def record_failed_login(
        self, account_id: str, attempts: int, locked_until: datetime | None
    ) -> None:
        with self._pg_connect() as connection:
            connection.execute(
                "UPDATE accounts SET failed_attempts = %s, locked_until = %s WHERE id = %s",
                (attempts, locked_until.isoformat() if locked_until else None, account_id),
            )

    def clear_login_failures(self, account_id: str) -> None:
        with self._pg_connect() as connection:
            connection.execute(
                "UPDATE accounts SET failed_attempts = 0, locked_until = NULL WHERE id = %s",
                (account_id,),
            )

    def change_password(self, account_id: str, password_hash: str, changed_at: datetime) -> None:
        with self._pg_connect() as connection:
            connection.execute(
                """UPDATE accounts SET password_hash = %s, password_changed_at = %s,
                failed_attempts = 0, locked_until = NULL, must_change_password = FALSE
                WHERE id = %s""",
                (password_hash, changed_at.isoformat(), account_id),
            )

    def create_session(self, session: StoredSession) -> None:
        with self._pg_connect() as connection:
            connection.execute(
                """INSERT INTO sessions
                (id, account_id, token_hash, csrf_hash, created_at, last_seen_at,
                 idle_expires_at, absolute_expires_at, user_agent, client_host, revoked_at,
                 mfa_verified_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    session.id,
                    session.account_id,
                    session.token_hash,
                    session.csrf_hash,
                    session.created_at.isoformat(),
                    session.last_seen_at.isoformat(),
                    session.idle_expires_at.isoformat(),
                    session.absolute_expires_at.isoformat(),
                    session.user_agent,
                    session.client_host,
                    session.revoked_at.isoformat() if session.revoked_at else None,
                    session.mfa_verified_at.isoformat() if session.mfa_verified_at else None,
                ),
            )

    def set_mfa_secret(self, account_id: str, ciphertext: str) -> None:
        with self._pg_connect() as connection:
            connection.execute(
                """UPDATE accounts SET mfa_secret_ciphertext = %s, mfa_enabled = FALSE,
                mfa_last_counter = NULL WHERE id = %s""",
                (ciphertext, account_id),
            )

    def enable_mfa(self, account_id: str, counter: int) -> None:
        with self._pg_connect() as connection:
            connection.execute(
                "UPDATE accounts SET mfa_enabled = TRUE, mfa_last_counter = %s WHERE id = %s",
                (counter, account_id),
            )

    def disable_mfa(self, account_id: str) -> None:
        with self._pg_connect() as connection:
            connection.execute(
                """UPDATE accounts SET mfa_secret_ciphertext = NULL, mfa_enabled = FALSE,
                mfa_last_counter = NULL WHERE id = %s""",
                (account_id,),
            )

    def consume_mfa_counter(self, account_id: str, counter: int) -> bool:
        with self._pg_connect() as connection:
            cursor = connection.execute(
                """UPDATE accounts SET mfa_last_counter = %s WHERE id = %s
                AND (mfa_last_counter IS NULL OR mfa_last_counter < %s)""",
                (counter, account_id, counter),
            )
            return cursor.rowcount == 1

    def mark_session_mfa(self, session_id: str, verified_at: datetime) -> None:
        with self._pg_connect() as connection:
            connection.execute(
                "UPDATE sessions SET mfa_verified_at = %s WHERE id = %s",
                (verified_at.isoformat(), session_id),
            )

    def session_by_token_hash(self, token_hash: str) -> StoredSession | None:
        with self._pg_connect() as connection:
            row = connection.execute(
                "SELECT * FROM sessions WHERE token_hash = %s", (token_hash,)
            ).fetchone()
        return self._session_pg(row)

    def sessions_for_account(self, account_id: str) -> tuple[StoredSession, ...]:
        with self._pg_connect() as connection:
            rows = connection.execute(
                "SELECT * FROM sessions WHERE account_id = %s ORDER BY created_at DESC",
                (account_id,),
            ).fetchall()
        return tuple(session for row in rows if (session := self._session_pg(row)) is not None)

    def touch_session(self, session_id: str, seen_at: datetime, idle_expires_at: datetime) -> None:
        with self._pg_connect() as connection:
            connection.execute(
                "UPDATE sessions SET last_seen_at = %s, idle_expires_at = %s WHERE id = %s",
                (seen_at.isoformat(), idle_expires_at.isoformat(), session_id),
            )

    def revoke_session(self, session_id: str, revoked_at: datetime) -> bool:
        with self._pg_connect() as connection:
            cursor = connection.execute(
                "UPDATE sessions SET revoked_at = %s WHERE id = %s AND revoked_at IS NULL",
                (revoked_at.isoformat(), session_id),
            )
            return cursor.rowcount == 1

    def revoke_all_sessions(self, account_id: str, revoked_at: datetime) -> int:
        with self._pg_connect() as connection:
            cursor = connection.execute(
                "UPDATE sessions SET revoked_at = %s WHERE account_id = %s AND revoked_at IS NULL",
                (revoked_at.isoformat(), account_id),
            )
            return cursor.rowcount

    def replace_recovery_codes(
        self, account_id: str, code_hashes: tuple[str, ...], created_at: datetime
    ) -> None:
        with self._pg_connect() as connection:
            connection.execute("DELETE FROM recovery_codes WHERE account_id = %s", (account_id,))
            with connection.cursor() as cursor:
                cursor.executemany(
                    "INSERT INTO recovery_codes (account_id, code_hash, created_at) VALUES (%s, %s, %s)",
                    ((account_id, value, created_at.isoformat()) for value in code_hashes),
                )

    def consume_recovery_code(self, account_id: str, code_hash: str, used_at: datetime) -> bool:
        with self._pg_connect() as connection:
            cursor = connection.execute(
                """UPDATE recovery_codes SET used_at = %s
                WHERE account_id = %s AND code_hash = %s AND used_at IS NULL""",
                (used_at.isoformat(), account_id, code_hash),
            )
            return cursor.rowcount == 1

    def append_event(
        self,
        event_type: str,
        account_id: str | None,
        occurred_at: datetime,
        source: str,
        detail: str,
    ) -> None:
        with self._pg_connect() as connection:
            connection.execute(
                """INSERT INTO security_events
                (event_type, account_id, occurred_at, source, detail) VALUES (%s, %s, %s, %s, %s)""",
                (event_type, account_id, occurred_at.isoformat(), source, detail),
            )

    def security_events(self) -> tuple[SecurityEvent, ...]:
        with self._pg_connect() as connection:
            rows = connection.execute("SELECT * FROM security_events ORDER BY id").fetchall()
        return tuple(
            SecurityEvent(
                id=int(_text(row["id"])),
                event_type=_text(row["event_type"]),
                account_id=None if row["account_id"] is None else _text(row["account_id"]),
                occurred_at=datetime.fromisoformat(_text(row["occurred_at"])),
                source=_text(row["source"]),
                detail=_text(row["detail"]),
            )
            for row in rows
        )

    @staticmethod
    def _machine_credential_pg(row: Row | None) -> MachineCredential | None:
        if row is None:
            return None
        raw_scopes = row["scopes"]
        scopes = raw_scopes if isinstance(raw_scopes, list) else json.loads(_text(raw_scopes))
        if not isinstance(scopes, list) or not all(isinstance(item, str) for item in scopes):
            raise RuntimeError("Stored machine credential scopes are invalid")
        return MachineCredential(
            id=_text(row["id"]),
            label=_text(row["label"]),
            token_hash=_text(row["token_hash"]),
            scopes=tuple(scopes),
            created_at=datetime.fromisoformat(_text(row["created_at"])),
            created_by=_text(row["created_by"]),
            last_used_at=_parse_datetime(
                None if row["last_used_at"] is None else _text(row["last_used_at"])
            ),
            revoked_at=_parse_datetime(
                None if row["revoked_at"] is None else _text(row["revoked_at"])
            ),
        )

    def create_machine_credential(self, credential: MachineCredential) -> None:
        with self._pg_connect() as connection:
            connection.execute(
                """INSERT INTO machine_credentials
                (id, label, token_hash, scopes, created_at, created_by, last_used_at, revoked_at)
                VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s, %s)""",
                (
                    credential.id,
                    credential.label,
                    credential.token_hash,
                    json.dumps(credential.scopes, separators=(",", ":")),
                    credential.created_at.isoformat(),
                    credential.created_by,
                    credential.last_used_at.isoformat() if credential.last_used_at else None,
                    credential.revoked_at.isoformat() if credential.revoked_at else None,
                ),
            )

    def machine_credential_by_id(self, credential_id: str) -> MachineCredential | None:
        with self._pg_connect() as connection:
            row = connection.execute(
                "SELECT * FROM machine_credentials WHERE id = %s", (credential_id,)
            ).fetchone()
        return self._machine_credential_pg(row)

    def machine_credentials(self) -> tuple[MachineCredential, ...]:
        with self._pg_connect() as connection:
            rows = connection.execute(
                "SELECT * FROM machine_credentials ORDER BY created_at, id"
            ).fetchall()
        return tuple(item for row in rows if (item := self._machine_credential_pg(row)) is not None)

    def touch_machine_credential(self, credential_id: str, used_at: datetime) -> None:
        with self._pg_connect() as connection:
            connection.execute(
                "UPDATE machine_credentials SET last_used_at = %s WHERE id = %s AND revoked_at IS NULL",
                (used_at.isoformat(), credential_id),
            )

    def revoke_machine_credential(self, credential_id: str, revoked_at: datetime) -> bool:
        with self._pg_connect() as connection:
            cursor = connection.execute(
                """UPDATE machine_credentials SET revoked_at = %s
                WHERE id = %s AND revoked_at IS NULL""",
                (revoked_at.isoformat(), credential_id),
            )
            return cursor.rowcount == 1

    def rate_limit_hit(
        self,
        bucket: str,
        now: datetime,
        *,
        window_seconds: int,
        limit: int,
        block_seconds: int,
    ) -> bool:
        with self._pg_connect() as connection:
            connection.execute(
                """INSERT INTO auth_rate_limits (bucket, window_started, attempts, blocked_until)
                VALUES (%s, %s, 0, NULL) ON CONFLICT (bucket) DO NOTHING""",
                (bucket, now.isoformat()),
            )
            row = connection.execute(
                "SELECT * FROM auth_rate_limits WHERE bucket = %s FOR UPDATE", (bucket,)
            ).fetchone()
            if row is None:
                raise RuntimeError("Rate-limit bucket disappeared during transaction")
            blocked_until = _parse_datetime(
                None if row["blocked_until"] is None else _text(row["blocked_until"])
            )
            if blocked_until and now < blocked_until:
                return True
            window_started = datetime.fromisoformat(_text(row["window_started"]))
            if (now - window_started).total_seconds() >= window_seconds:
                connection.execute(
                    """UPDATE auth_rate_limits SET window_started = %s, attempts = 1,
                    blocked_until = NULL WHERE bucket = %s""",
                    (now.isoformat(), bucket),
                )
                return False
            attempts = int(_text(row["attempts"])) + 1
            new_block = now.timestamp() + block_seconds if attempts > limit else None
            new_block_value = (
                datetime.fromtimestamp(new_block, tz=now.tzinfo).isoformat() if new_block else None
            )
            connection.execute(
                "UPDATE auth_rate_limits SET attempts = %s, blocked_until = %s WHERE bucket = %s",
                (attempts, new_block_value, bucket),
            )
            return new_block is not None

    def clear_rate_limit(self, bucket: str) -> None:
        with self._pg_connect() as connection:
            connection.execute("DELETE FROM auth_rate_limits WHERE bucket = %s", (bucket,))
