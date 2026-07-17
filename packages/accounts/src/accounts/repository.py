"""SQLite repository for durable human authentication state."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from accounts.models import Account, AccountRole, SecurityEvent, StoredSession

SCHEMA_VERSION = 4


def _parse_datetime(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


class AccountRepository:
    """Persist accounts and sessions without ever storing their raw secrets."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=5.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
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
            if current > SCHEMA_VERSION:
                raise RuntimeError(f"Account store schema {current} is newer than supported")
            if current == 0:
                connection.executescript(
                    """
                    CREATE TABLE accounts (
                        id TEXT PRIMARY KEY,
                        username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                        display_name TEXT NOT NULL,
                        password_hash TEXT NOT NULL,
                        role TEXT NOT NULL,
                        status TEXT NOT NULL CHECK(status IN ('active', 'disabled')),
                        actor_id TEXT,
                        failed_attempts INTEGER NOT NULL DEFAULT 0,
                        locked_until TEXT,
                        created_at TEXT NOT NULL,
                        password_changed_at TEXT NOT NULL
                        ,mfa_secret_ciphertext TEXT
                        ,mfa_enabled INTEGER NOT NULL DEFAULT 0 CHECK(mfa_enabled IN (0, 1))
                        ,mfa_last_counter INTEGER
                        ,must_change_password INTEGER NOT NULL DEFAULT 0 CHECK(must_change_password IN (0, 1))
                    );
                    CREATE TABLE sessions (
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
                        revoked_at TEXT
                        ,mfa_verified_at TEXT
                    );
                    CREATE INDEX sessions_account_id ON sessions(account_id);
                    CREATE TABLE recovery_codes (
                        account_id TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                        code_hash TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        used_at TEXT,
                        PRIMARY KEY(account_id, code_hash)
                    );
                    CREATE TABLE security_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_type TEXT NOT NULL,
                        account_id TEXT REFERENCES accounts(id) ON DELETE SET NULL,
                        occurred_at TEXT NOT NULL,
                        source TEXT NOT NULL,
                        detail TEXT NOT NULL
                    );
                    CREATE INDEX security_events_account_id ON security_events(account_id);
                    CREATE TABLE auth_rate_limits (
                        bucket TEXT PRIMARY KEY,
                        window_started TEXT NOT NULL,
                        attempts INTEGER NOT NULL,
                        blocked_until TEXT
                    );
                    PRAGMA user_version = 4;
                    """
                )
            elif current == 1:
                connection.executescript(
                    """
                    CREATE TABLE auth_rate_limits (
                        bucket TEXT PRIMARY KEY,
                        window_started TEXT NOT NULL,
                        attempts INTEGER NOT NULL,
                        blocked_until TEXT
                    );
                    ALTER TABLE accounts ADD COLUMN mfa_secret_ciphertext TEXT;
                    ALTER TABLE accounts ADD COLUMN mfa_enabled INTEGER NOT NULL DEFAULT 0;
                    ALTER TABLE accounts ADD COLUMN mfa_last_counter INTEGER;
                    ALTER TABLE sessions ADD COLUMN mfa_verified_at TEXT;
                    ALTER TABLE accounts ADD COLUMN must_change_password INTEGER NOT NULL DEFAULT 0;
                    PRAGMA user_version = 4;
                    """
                )
            elif current == 2:
                connection.executescript(
                    """
                    ALTER TABLE accounts ADD COLUMN mfa_secret_ciphertext TEXT;
                    ALTER TABLE accounts ADD COLUMN mfa_enabled INTEGER NOT NULL DEFAULT 0;
                    ALTER TABLE accounts ADD COLUMN mfa_last_counter INTEGER;
                    ALTER TABLE sessions ADD COLUMN mfa_verified_at TEXT;
                    ALTER TABLE accounts ADD COLUMN must_change_password INTEGER NOT NULL DEFAULT 0;
                    PRAGMA user_version = 4;
                    """
                )
            elif current == 3:
                connection.executescript(
                    """
                    ALTER TABLE accounts ADD COLUMN must_change_password INTEGER NOT NULL DEFAULT 0;
                    PRAGMA user_version = 4;
                    """
                )

    @staticmethod
    def _account(row: sqlite3.Row | None) -> Account | None:
        if row is None:
            return None
        return Account(
            id=str(row["id"]),
            username=str(row["username"]),
            display_name=str(row["display_name"]),
            password_hash=str(row["password_hash"]),
            role=AccountRole(str(row["role"])),
            status=str(row["status"]),
            actor_id=None if row["actor_id"] is None else str(row["actor_id"]),
            failed_attempts=int(row["failed_attempts"]),
            locked_until=_parse_datetime(row["locked_until"]),
            created_at=datetime.fromisoformat(str(row["created_at"])),
            password_changed_at=datetime.fromisoformat(str(row["password_changed_at"])),
            mfa_secret_ciphertext=(
                None if row["mfa_secret_ciphertext"] is None else str(row["mfa_secret_ciphertext"])
            ),
            mfa_enabled=bool(row["mfa_enabled"]),
            mfa_last_counter=(
                None if row["mfa_last_counter"] is None else int(row["mfa_last_counter"])
            ),
            must_change_password=bool(row["must_change_password"]),
        )

    @staticmethod
    def _session(row: sqlite3.Row | None) -> StoredSession | None:
        if row is None:
            return None
        return StoredSession(
            id=str(row["id"]),
            account_id=str(row["account_id"]),
            token_hash=str(row["token_hash"]),
            csrf_hash=str(row["csrf_hash"]),
            created_at=datetime.fromisoformat(str(row["created_at"])),
            last_seen_at=datetime.fromisoformat(str(row["last_seen_at"])),
            idle_expires_at=datetime.fromisoformat(str(row["idle_expires_at"])),
            absolute_expires_at=datetime.fromisoformat(str(row["absolute_expires_at"])),
            user_agent=str(row["user_agent"]),
            client_host=str(row["client_host"]),
            revoked_at=_parse_datetime(row["revoked_at"]),
            mfa_verified_at=_parse_datetime(row["mfa_verified_at"]),
        )

    def account_count(self) -> int:
        with self._connect() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM accounts").fetchone()[0])

    def create_account(self, account: Account) -> None:
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO accounts
                (id, username, display_name, password_hash, role, status, actor_id,
                 failed_attempts, locked_until, created_at, password_changed_at,
                 mfa_secret_ciphertext, mfa_enabled, mfa_last_counter, must_change_password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    account.id,
                    account.username,
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
                    int(account.mfa_enabled),
                    account.mfa_last_counter,
                    int(account.must_change_password),
                ),
            )

    def create_bootstrap_account(self, account: Account) -> bool:
        """Create the first account under an immediate write lock exactly once."""
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            if int(connection.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]) != 0:
                return False
            connection.execute(
                """INSERT INTO accounts
                (id, username, display_name, password_hash, role, status, actor_id,
                 failed_attempts, locked_until, created_at, password_changed_at,
                 mfa_secret_ciphertext, mfa_enabled, mfa_last_counter, must_change_password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    account.id,
                    account.username,
                    account.display_name,
                    account.password_hash,
                    account.role.value,
                    account.status,
                    account.actor_id,
                    account.failed_attempts,
                    None,
                    account.created_at.isoformat(),
                    account.password_changed_at.isoformat(),
                    account.mfa_secret_ciphertext,
                    int(account.mfa_enabled),
                    account.mfa_last_counter,
                    int(account.must_change_password),
                ),
            )
            return True

    def account_by_username(self, username: str) -> Account | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM accounts WHERE username = ? COLLATE NOCASE", (username,)
            ).fetchone()
        return self._account(row)

    def account_by_id(self, account_id: str) -> Account | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM accounts WHERE id = ?", (account_id,)
            ).fetchone()
        return self._account(row)

    def accounts(self) -> tuple[Account, ...]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM accounts ORDER BY created_at, id").fetchall()
        result: list[Account] = []
        for row in rows:
            account = self._account(row)
            if account is not None:
                result.append(account)
        return tuple(result)

    def set_account_role(self, account_id: str, role: AccountRole) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE accounts SET role = ? WHERE id = ?", (role.value, account_id)
            )
            return cursor.rowcount == 1

    def set_account_status(self, account_id: str, status: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE accounts SET status = ? WHERE id = ?", (status, account_id)
            )
            return cursor.rowcount == 1

    def record_failed_login(
        self, account_id: str, attempts: int, locked_until: datetime | None
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE accounts SET failed_attempts = ?, locked_until = ? WHERE id = ?",
                (attempts, locked_until.isoformat() if locked_until else None, account_id),
            )

    def clear_login_failures(self, account_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE accounts SET failed_attempts = 0, locked_until = NULL WHERE id = ?",
                (account_id,),
            )

    def change_password(self, account_id: str, password_hash: str, changed_at: datetime) -> None:
        with self._connect() as connection:
            connection.execute(
                """UPDATE accounts SET password_hash = ?, password_changed_at = ?,
                failed_attempts = 0, locked_until = NULL, must_change_password = 0 WHERE id = ?""",
                (password_hash, changed_at.isoformat(), account_id),
            )

    def create_session(self, session: StoredSession) -> None:
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO sessions
                (id, account_id, token_hash, csrf_hash, created_at, last_seen_at,
                 idle_expires_at, absolute_expires_at, user_agent, client_host, revoked_at,
                 mfa_verified_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
        with self._connect() as connection:
            connection.execute(
                """UPDATE accounts SET mfa_secret_ciphertext = ?, mfa_enabled = 0,
                mfa_last_counter = NULL WHERE id = ?""",
                (ciphertext, account_id),
            )

    def enable_mfa(self, account_id: str, counter: int) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE accounts SET mfa_enabled = 1, mfa_last_counter = ? WHERE id = ?",
                (counter, account_id),
            )

    def disable_mfa(self, account_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                """UPDATE accounts SET mfa_secret_ciphertext = NULL, mfa_enabled = 0,
                mfa_last_counter = NULL WHERE id = ?""",
                (account_id,),
            )

    def consume_mfa_counter(self, account_id: str, counter: int) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """UPDATE accounts SET mfa_last_counter = ? WHERE id = ?
                AND (mfa_last_counter IS NULL OR mfa_last_counter < ?)""",
                (counter, account_id, counter),
            )
            return cursor.rowcount == 1

    def mark_session_mfa(self, session_id: str, verified_at: datetime) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE sessions SET mfa_verified_at = ? WHERE id = ?",
                (verified_at.isoformat(), session_id),
            )

    def session_by_token_hash(self, token_hash: str) -> StoredSession | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM sessions WHERE token_hash = ?", (token_hash,)
            ).fetchone()
        return self._session(row)

    def sessions_for_account(self, account_id: str) -> tuple[StoredSession, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM sessions WHERE account_id = ? ORDER BY created_at DESC",
                (account_id,),
            ).fetchall()
        return tuple(self._session(row) for row in rows if row is not None)  # type: ignore[misc]

    def touch_session(self, session_id: str, seen_at: datetime, idle_expires_at: datetime) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE sessions SET last_seen_at = ?, idle_expires_at = ? WHERE id = ?",
                (seen_at.isoformat(), idle_expires_at.isoformat(), session_id),
            )

    def revoke_session(self, session_id: str, revoked_at: datetime) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE sessions SET revoked_at = ? WHERE id = ? AND revoked_at IS NULL",
                (revoked_at.isoformat(), session_id),
            )
            return cursor.rowcount == 1

    def revoke_all_sessions(self, account_id: str, revoked_at: datetime) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE sessions SET revoked_at = ? WHERE account_id = ? AND revoked_at IS NULL",
                (revoked_at.isoformat(), account_id),
            )
            return cursor.rowcount

    def replace_recovery_codes(
        self, account_id: str, code_hashes: tuple[str, ...], created_at: datetime
    ) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM recovery_codes WHERE account_id = ?", (account_id,))
            connection.executemany(
                "INSERT INTO recovery_codes (account_id, code_hash, created_at) VALUES (?, ?, ?)",
                ((account_id, value, created_at.isoformat()) for value in code_hashes),
            )

    def consume_recovery_code(self, account_id: str, code_hash: str, used_at: datetime) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """UPDATE recovery_codes SET used_at = ?
                WHERE account_id = ? AND code_hash = ? AND used_at IS NULL""",
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
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO security_events
                (event_type, account_id, occurred_at, source, detail) VALUES (?, ?, ?, ?, ?)""",
                (event_type, account_id, occurred_at.isoformat(), source, detail),
            )

    def security_events(self) -> tuple[SecurityEvent, ...]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM security_events ORDER BY id").fetchall()
        return tuple(
            SecurityEvent(
                id=int(row["id"]),
                event_type=str(row["event_type"]),
                account_id=None if row["account_id"] is None else str(row["account_id"]),
                occurred_at=datetime.fromisoformat(str(row["occurred_at"])),
                source=str(row["source"]),
                detail=str(row["detail"]),
            )
            for row in rows
        )

    def rate_limit_hit(
        self,
        bucket: str,
        now: datetime,
        *,
        window_seconds: int,
        limit: int,
        block_seconds: int,
    ) -> bool:
        """Record an attempt and return True when the durable bucket is blocked."""
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM auth_rate_limits WHERE bucket = ?", (bucket,)
            ).fetchone()
            if row is None:
                connection.execute(
                    """INSERT INTO auth_rate_limits
                    (bucket, window_started, attempts, blocked_until) VALUES (?, ?, 1, NULL)""",
                    (bucket, now.isoformat()),
                )
                return False
            blocked_until = _parse_datetime(row["blocked_until"])
            if blocked_until and now < blocked_until:
                return True
            window_started = datetime.fromisoformat(str(row["window_started"]))
            if (now - window_started).total_seconds() >= window_seconds:
                connection.execute(
                    """UPDATE auth_rate_limits SET window_started = ?, attempts = 1,
                    blocked_until = NULL WHERE bucket = ?""",
                    (now.isoformat(), bucket),
                )
                return False
            attempts = int(row["attempts"]) + 1
            new_block = now.timestamp() + block_seconds if attempts > limit else None
            new_block_value = (
                datetime.fromtimestamp(new_block, tz=now.tzinfo).isoformat() if new_block else None
            )
            connection.execute(
                "UPDATE auth_rate_limits SET attempts = ?, blocked_until = ? WHERE bucket = ?",
                (attempts, new_block_value, bucket),
            )
            return new_block is not None

    def clear_rate_limit(self, bucket: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM auth_rate_limits WHERE bucket = ?", (bucket,))
