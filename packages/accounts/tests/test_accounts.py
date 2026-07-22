from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from cerberus.security.modules.auth import PasswordHasher
from cryptography.fernet import Fernet

from accounts import (
    AccountLocked,
    AccountRepository,
    AccountRole,
    AccountService,
    BootstrapUnavailable,
    InterfacePermission,
    InvalidCredentials,
    InvalidCsrf,
    InvalidMachineCredential,
    InvalidMfa,
    InvalidRecovery,
    InvalidSession,
    MfaRequired,
    PermissionDenied,
    RateLimited,
    calculate_totp,
    has_permission,
)

PASSWORD = "Foundation!Owner123"
NEW_PASSWORD = "Rebuilt!Owner456"
MFA_KEY = Fernet.generate_key().decode("ascii")


@dataclass
class MutableClock:
    value: datetime = datetime(2026, 7, 15, 12, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.value

    def advance(self, **values: int) -> None:
        self.value += timedelta(**values)


def _service(tmp_path: Path, clock: MutableClock | None = None) -> AccountService:
    return AccountService(
        AccountRepository(tmp_path / "accounts.db"),
        setup_secret="one-time-setup",
        clock=clock or MutableClock(),
        password_hasher=PasswordHasher(iterations=1_000),
        idle_timeout=timedelta(minutes=10),
        absolute_timeout=timedelta(hours=1),
        lockout_duration=timedelta(minutes=5),
        mfa_encryption_key=MFA_KEY,
    )


def _bootstrap(service: AccountService):
    return service.bootstrap(
        setup_secret="one-time-setup",
        username="owner",
        display_name="Local Owner",
        password=PASSWORD,
        actor_id="ACTOR-OWNER",
        source="127.0.0.1",
        user_agent="pytest",
    )


def test_bootstrap_is_one_time_and_persists_only_secret_hashes(tmp_path: Path) -> None:
    service = _service(tmp_path)
    result = _bootstrap(service)
    assert result.bundle.account.role.value == "owner"
    assert len(result.recovery_codes) == 10
    with pytest.raises(BootstrapUnavailable):
        _bootstrap(service)

    raw = (tmp_path / "accounts.db").read_bytes()
    assert PASSWORD.encode() not in raw
    assert result.bundle.token.encode() not in raw
    assert result.bundle.csrf_token.encode() not in raw
    assert result.recovery_codes[0].encode() not in raw

    reopened = _service(tmp_path)
    assert reopened.bootstrap_required() is False
    bundle = reopened.login("OWNER", PASSWORD, "127.0.0.1", "pytest")
    assert bundle.account.id == result.bundle.account.id


def test_login_lockout_and_durable_source_rate_limit(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _bootstrap(service)
    for _ in range(4):
        with pytest.raises(InvalidCredentials, match="Invalid username or password"):
            service.login("owner", "wrong", "127.0.0.2", "pytest")
    with pytest.raises(AccountLocked):
        service.login("owner", "wrong", "127.0.0.2", "pytest")

    for _ in range(20):
        with pytest.raises(InvalidCredentials, match="Invalid username or password"):
            service.login("missing", "wrong", "127.0.0.3", "pytest")
    with pytest.raises(RateLimited):
        service.login("missing", "wrong", "127.0.0.3", "pytest")


def test_session_rotation_csrf_expiry_and_revocation(tmp_path: Path) -> None:
    clock = MutableClock()
    service = _service(tmp_path, clock)
    first = _bootstrap(service).bundle
    with pytest.raises(InvalidCsrf):
        service.rotate_session(first.token, "wrong", "127.0.0.1", "pytest")

    rotated = service.rotate_session(first.token, first.csrf_token, "127.0.0.1", "pytest")
    assert rotated.token != first.token
    with pytest.raises(InvalidSession):
        service.authenticate(first.token)

    other = service.login("owner", PASSWORD, "127.0.0.2", "second device")
    service.revoke_session(rotated.token, rotated.csrf_token, other.session.id, "127.0.0.1")
    with pytest.raises(InvalidSession):
        service.authenticate(other.token)

    clock.advance(minutes=11)
    with pytest.raises(InvalidSession):
        service.authenticate(rotated.token)


def test_recovery_code_is_single_use_and_revokes_sessions(tmp_path: Path) -> None:
    service = _service(tmp_path)
    result = _bootstrap(service)
    active = service.login("owner", PASSWORD, "127.0.0.1", "pytest")
    code = result.recovery_codes[0]
    service.recover("owner", code, NEW_PASSWORD, "127.0.0.1")
    with pytest.raises(InvalidSession):
        service.authenticate(active.token)
    service.login("owner", NEW_PASSWORD, "127.0.0.1", "pytest")
    with pytest.raises(InvalidRecovery):
        service.recover("owner", code, "Third!Password789", "127.0.0.1")


def test_totp_enrollment_login_replay_step_up_and_recovery(tmp_path: Path) -> None:
    clock = MutableClock()
    service = _service(tmp_path, clock)
    result = _bootstrap(service)
    session = result.bundle
    enrollment = service.begin_mfa_enrollment(
        session.token, session.csrf_token, PASSWORD, "127.0.0.1"
    )
    assert enrollment.provisioning_uri.startswith("otpauth://totp/")
    assert enrollment.secret.encode() not in (tmp_path / "accounts.db").read_bytes()

    first_code = calculate_totp(enrollment.secret, clock.value)
    service.confirm_mfa_enrollment(session.token, session.csrf_token, first_code, "127.0.0.1")
    with pytest.raises(MfaRequired):
        service.login("owner", PASSWORD, "127.0.0.2", "pytest")
    with pytest.raises(InvalidMfa):
        service.login("owner", PASSWORD, "127.0.0.2", "pytest", first_code)

    clock.advance(seconds=30)
    second_code = calculate_totp(enrollment.secret, clock.value)
    signed_in = service.login("owner", PASSWORD, "127.0.0.2", "pytest", second_code)
    assert signed_in.session.mfa_verified_at == clock.value

    clock.advance(seconds=30)
    service.step_up_mfa(
        signed_in.token,
        signed_in.csrf_token,
        calculate_totp(enrollment.secret, clock.value),
        "127.0.0.2",
    )
    refreshed = service.repository.session_by_token_hash(signed_in.session.token_hash)
    assert refreshed is not None and refreshed.mfa_verified_at == clock.value

    service.recover("owner", result.recovery_codes[0], NEW_PASSWORD, "127.0.0.1")
    clock.advance(seconds=30)
    recovered = service.login("owner", NEW_PASSWORD, "127.0.0.1", "pytest")
    assert recovered.account.mfa_enabled is False


def test_machine_credentials_are_scoped_hashed_single_use_and_revocable(tmp_path: Path) -> None:
    service = _service(tmp_path)
    owner = _bootstrap(service).bundle
    service.repository.mark_session_mfa(owner.session.id, service.clock())

    created = service.create_machine_credential(
        owner.token,
        owner.csrf_token,
        label="Waterfall evidence writer",
        scopes=("evidence.read", "evidence.write", "evidence.write"),
        source="pytest",
    )
    assert created.token.startswith(f"mc_{created.credential.id}.")
    assert created.token.encode() not in (tmp_path / "accounts.db").read_bytes()
    assert created.credential.scopes == ("evidence.read", "evidence.write")

    authenticated = service.authenticate_machine_credential(created.token, "evidence.write")
    assert authenticated.id == created.credential.id
    with pytest.raises(PermissionDenied, match="scope is insufficient"):
        service.authenticate_machine_credential(created.token, "analysis.generate")

    service.revoke_machine_credential(
        owner.token, owner.csrf_token, created.credential.id, "pytest"
    )
    with pytest.raises(InvalidMachineCredential):
        service.authenticate_machine_credential(created.token)


def test_schema_migration_upgrades_version_two_store(tmp_path: Path) -> None:
    path = tmp_path / "accounts.db"
    with sqlite3.connect(path) as connection:
        connection.executescript(
            """
            CREATE TABLE accounts (
                id TEXT PRIMARY KEY, username TEXT, display_name TEXT, password_hash TEXT,
                role TEXT, status TEXT, actor_id TEXT, failed_attempts INTEGER,
                locked_until TEXT, created_at TEXT, password_changed_at TEXT
            );
            CREATE TABLE sessions (
                id TEXT PRIMARY KEY, account_id TEXT, token_hash TEXT, csrf_hash TEXT,
                created_at TEXT, last_seen_at TEXT, idle_expires_at TEXT,
                absolute_expires_at TEXT, user_agent TEXT, client_host TEXT, revoked_at TEXT
            );
            CREATE TABLE auth_rate_limits (
                bucket TEXT PRIMARY KEY, window_started TEXT, attempts INTEGER,
                blocked_until TEXT
            );
            PRAGMA user_version = 2;
            """
        )
    AccountRepository(path).migrate()
    with sqlite3.connect(path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 5
        assert connection.execute(
            "SELECT name FROM pragma_table_info('accounts') WHERE name = 'mfa_enabled'"
        ).fetchone() == ("mfa_enabled",)


def test_role_permissions_are_explicit_and_never_imply_execution_authority() -> None:
    assert has_permission(AccountRole.OWNER, InterfacePermission.ACCOUNTS_MANAGE)
    assert has_permission(AccountRole.OPERATOR, InterfacePermission.REQUEST_SUBMIT)
    assert not has_permission(AccountRole.OPERATOR, InterfacePermission.REQUEST_REVIEW)
    assert has_permission(AccountRole.REVIEWER, InterfacePermission.REQUEST_REVIEW)
    assert has_permission(AccountRole.OWNER, InterfacePermission.AUDIT_EXPORT)
    assert has_permission(AccountRole.ADMINISTRATOR, InterfacePermission.AUDIT_EXPORT)
    assert has_permission(AccountRole.REVIEWER, InterfacePermission.AUDIT_EXPORT)
    assert has_permission(AccountRole.AUDITOR, InterfacePermission.AUDIT_EXPORT)
    assert not has_permission(AccountRole.OPERATOR, InterfacePermission.AUDIT_EXPORT)
    assert not has_permission(AccountRole.VIEWER, InterfacePermission.AUDIT_EXPORT)
    assert has_permission(AccountRole.OWNER, InterfacePermission.AUDIT_RAW_VIEW)
    assert has_permission(AccountRole.ADMINISTRATOR, InterfacePermission.AUDIT_RAW_VIEW)
    assert has_permission(AccountRole.AUDITOR, InterfacePermission.AUDIT_RAW_VIEW)
    assert not has_permission(AccountRole.REVIEWER, InterfacePermission.AUDIT_RAW_VIEW)
    assert not has_permission(AccountRole.OPERATOR, InterfacePermission.AUDIT_RAW_VIEW)
    assert not has_permission(AccountRole.VIEWER, InterfacePermission.AUDIT_RAW_VIEW)
    assert has_permission(AccountRole.OPERATOR, InterfacePermission.MODULE_ANALYSIS_RUN)
    assert has_permission(AccountRole.AUDITOR, InterfacePermission.MODULE_ANALYSIS_RUN)
    assert not has_permission(AccountRole.VIEWER, InterfacePermission.MODULE_ANALYSIS_RUN)
    assert has_permission(AccountRole.OPERATOR, InterfacePermission.TAAR_RUN_READER)
    assert has_permission(AccountRole.REVIEWER, InterfacePermission.TAAR_VIEW)
    assert not has_permission(AccountRole.REVIEWER, InterfacePermission.TAAR_RUN_READER)
    assert not has_permission(AccountRole.VIEWER, InterfacePermission.TAAR_VIEW)
    assert not has_permission(AccountRole.VIEWER, InterfacePermission.SYSTEM_CONFIGURE)


def test_owner_manages_accounts_and_operator_is_denied_admin_access(tmp_path: Path) -> None:
    service = _service(tmp_path)
    owner = _bootstrap(service).bundle
    created = service.create_managed_account(
        owner.token,
        owner.csrf_token,
        username="operator.one",
        display_name="Operator One",
        password="Temporary!Operator123",
        role=AccountRole.OPERATOR,
        actor_id="ACTOR-OPERATOR-1",
        source="127.0.0.1",
    )
    assert created.account.must_change_password is True
    assert len(created.recovery_codes) == 10
    assert len(service.list_accounts(owner.token)) == 2

    operator = service.login("operator.one", "Temporary!Operator123", "127.0.0.2", "pytest")
    with pytest.raises(PermissionDenied, match="Password change required"):
        service.list_accounts(operator.token)
    service.change_password(
        operator.token,
        operator.csrf_token,
        "Temporary!Operator123",
        "Permanent!Operator456",
        "127.0.0.2",
    )
    operator = service.login("operator.one", "Permanent!Operator456", "127.0.0.2", "pytest")
    with pytest.raises(PermissionDenied, match=r"accounts\.manage"):
        service.list_accounts(operator.token)

    service.set_managed_account_role(
        owner.token,
        owner.csrf_token,
        created.account.id,
        AccountRole.REVIEWER,
        "127.0.0.1",
    )
    service.set_managed_account_status(
        owner.token, owner.csrf_token, created.account.id, False, "127.0.0.1"
    )
    managed = service.repository.account_by_id(created.account.id)
    assert managed is not None
    assert managed.role is AccountRole.REVIEWER
    assert managed.status == "disabled"
