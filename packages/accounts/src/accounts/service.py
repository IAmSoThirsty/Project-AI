"""Human-account authentication service with fail-closed session behavior."""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import secrets
import struct
from base64 import b32decode, b32encode
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from urllib.parse import quote
from uuid import uuid4

from cerberus.security.modules.auth import PasswordHasher, PasswordPolicy
from cryptography.fernet import Fernet, InvalidToken

from accounts.models import (
    Account,
    AccountRole,
    BootstrapResult,
    MachineCredential,
    MachineCredentialResult,
    ManagedAccountResult,
    MfaEnrollment,
    SecurityEvent,
    SessionBundle,
    StoredSession,
)
from accounts.permissions import InterfacePermission, has_permission
from accounts.repository import AccountRepository

Clock = Callable[[], datetime]
USERNAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,63}$")
RECOVERY_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class AccountServiceError(Exception):
    """Base class for safe, expected account-service errors."""


class InvalidCredentials(AccountServiceError):
    pass


class AccountLocked(AccountServiceError):
    pass


class RateLimited(AccountServiceError):
    pass


class BootstrapUnavailable(AccountServiceError):
    pass


class InvalidBootstrapSecret(AccountServiceError):
    pass


class InvalidSession(AccountServiceError):
    pass


class InvalidCsrf(AccountServiceError):
    pass


class InvalidRecovery(AccountServiceError):
    pass


class PasswordRejected(AccountServiceError):
    pass


class MfaRequired(AccountServiceError):
    pass


class InvalidMfa(AccountServiceError):
    pass


class MfaUnavailable(AccountServiceError):
    pass


class PermissionDenied(AccountServiceError):
    pass


class AccountConflict(AccountServiceError):
    pass


class InvalidMachineCredential(AccountServiceError):
    pass


MACHINE_CREDENTIAL_SCOPES = frozenset({"evidence.read", "evidence.write", "analysis.generate"})


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _secret_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def calculate_totp(secret: str, at: datetime, *, step: int = 30) -> str:
    """Calculate the RFC 6238 SHA-1 six-digit code for a UTC instant."""
    counter = int(at.timestamp()) // step
    key = b32decode(secret.upper() + "=" * (-len(secret) % 8))
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{value % 1_000_000:06d}"


class AccountService:
    def __init__(
        self,
        repository: AccountRepository,
        *,
        setup_secret: str | None,
        clock: Clock = _utc_now,
        password_hasher: PasswordHasher | None = None,
        idle_timeout: timedelta = timedelta(minutes=30),
        absolute_timeout: timedelta = timedelta(hours=12),
        lockout_threshold: int = 5,
        lockout_duration: timedelta = timedelta(minutes=15),
        mfa_encryption_key: str | None = None,
    ) -> None:
        self.repository = repository
        self.setup_secret = setup_secret
        self.clock = clock
        self.password_hasher = password_hasher or PasswordHasher()
        self.password_policy = PasswordPolicy(min_length=14, max_age_days=0)
        self.idle_timeout = idle_timeout
        self.absolute_timeout = absolute_timeout
        self.lockout_threshold = lockout_threshold
        self.lockout_duration = lockout_duration
        self._fernet = Fernet(mfa_encryption_key.encode("ascii")) if mfa_encryption_key else None
        self._dummy_hash = self.password_hasher.hash_password("NotAReal!Password123")
        self.repository.migrate()

    def bootstrap_required(self) -> bool:
        return self.repository.account_count() == 0

    def bootstrap(
        self,
        *,
        setup_secret: str,
        username: str,
        display_name: str,
        password: str,
        actor_id: str | None,
        source: str,
        user_agent: str,
    ) -> BootstrapResult:
        self._rate_limit("bootstrap", source, limit=10)
        if not self.bootstrap_required():
            raise BootstrapUnavailable("Bootstrap has permanently closed")
        if not self.setup_secret or not hmac.compare_digest(setup_secret, self.setup_secret):
            self._event("auth.bootstrap_rejected", None, source, "invalid setup secret")
            raise InvalidBootstrapSecret("Invalid setup secret")
        normalized = self._validate_profile(username, display_name)
        password_hash = self._validated_password_hash(password)
        now = self.clock()
        account = Account(
            id=str(uuid4()),
            username=normalized,
            display_name=display_name.strip(),
            password_hash=password_hash,
            role=AccountRole.OWNER,
            status="active",
            actor_id=actor_id.strip() if actor_id and actor_id.strip() else None,
            failed_attempts=0,
            locked_until=None,
            created_at=now,
            password_changed_at=now,
            mfa_secret_ciphertext=None,
            mfa_enabled=False,
            mfa_last_counter=None,
            must_change_password=False,
        )
        if not self.repository.create_bootstrap_account(account):
            raise BootstrapUnavailable("Bootstrap has permanently closed")
        recovery_codes = self._new_recovery_codes()
        self.repository.replace_recovery_codes(
            account.id, tuple(_secret_hash(code) for code in recovery_codes), now
        )
        self._event("auth.bootstrap_completed", account.id, source, "owner account created")
        return BootstrapResult(
            bundle=self._create_session(account, source, user_agent), recovery_codes=recovery_codes
        )

    def login(
        self,
        username: str,
        password: str,
        source: str,
        user_agent: str,
        totp_code: str | None = None,
    ) -> SessionBundle:
        rate_bucket = self._rate_limit("login", source, limit=20)
        normalized = username.strip().lower()
        account = self.repository.account_by_username(normalized)
        stored_hash = account.password_hash if account else self._dummy_hash
        password_valid = self.password_hasher.verify_password(password, stored_hash)
        now = self.clock()
        if account is None:
            self._event("auth.login_failed", None, source, "invalid credentials")
            raise InvalidCredentials("Invalid username or password")
        if account.locked_until and now < account.locked_until:
            self._event("auth.login_locked", account.id, source, "lockout active")
            raise AccountLocked("Sign-in is temporarily unavailable")
        if account.status != "active" or not password_valid:
            if account.status == "active":
                attempts = account.failed_attempts + 1
                locked_until = (
                    now + self.lockout_duration if attempts >= self.lockout_threshold else None
                )
                self.repository.record_failed_login(account.id, attempts, locked_until)
            self._event("auth.login_failed", account.id, source, "invalid credentials")
            if account.status == "active" and account.failed_attempts + 1 >= self.lockout_threshold:
                raise AccountLocked("Sign-in is temporarily unavailable")
            raise InvalidCredentials("Invalid username or password")
        if account.mfa_enabled:
            if not totp_code:
                self._event("auth.mfa_required", account.id, source, "TOTP required")
                raise MfaRequired("Authenticator code required")
            self._verify_mfa(account, totp_code, consume=True)
        self.repository.clear_login_failures(account.id)
        self.repository.clear_rate_limit(rate_bucket)
        refreshed = self.repository.account_by_id(account.id)
        if refreshed is None:
            raise InvalidCredentials("Invalid username or password")
        self._event("auth.login_succeeded", account.id, source, "session issued")
        return self._create_session(
            refreshed, source, user_agent, mfa_verified=refreshed.mfa_enabled
        )

    def authenticate(self, token: str) -> tuple[Account, StoredSession]:
        now = self.clock()
        session = self.repository.session_by_token_hash(_secret_hash(token))
        if (
            session is None
            or session.revoked_at is not None
            or now >= session.idle_expires_at
            or now >= session.absolute_expires_at
        ):
            if session is not None and session.revoked_at is None:
                self.repository.revoke_session(session.id, now)
            raise InvalidSession("Session is missing, expired, or revoked")
        account = self.repository.account_by_id(session.account_id)
        if account is None or account.status != "active":
            self.repository.revoke_session(session.id, now)
            raise InvalidSession("Session is missing, expired, or revoked")
        idle_expires = min(now + self.idle_timeout, session.absolute_expires_at)
        self.repository.touch_session(session.id, now, idle_expires)
        current = self.repository.session_by_token_hash(session.token_hash)
        if current is None:
            raise InvalidSession("Session is missing, expired, or revoked")
        return account, current

    def require_csrf(self, session: StoredSession, csrf_token: str | None) -> None:
        if not csrf_token or not hmac.compare_digest(_secret_hash(csrf_token), session.csrf_hash):
            raise InvalidCsrf("CSRF validation failed")

    @staticmethod
    def require_permission(account: Account, permission: InterfacePermission) -> None:
        if (
            account.must_change_password
            and permission is not InterfacePermission.SESSIONS_MANAGE_OWN
        ):
            raise PermissionDenied("Password change required before using this interface")
        if not has_permission(account.role, permission):
            raise PermissionDenied(f"Interface permission required: {permission.value}")

    def authorize_rate_limited_action(
        self,
        token: str,
        csrf_token: str | None,
        *,
        permission: InterfacePermission,
        operation: str,
        source: str,
        limit: int,
    ) -> Account:
        """Authorize a consequential interface action and consume its durable quota."""
        if not operation or limit < 1:
            raise ValueError("Rate-limited action requires an operation and positive limit")
        account, session = self.authenticate(token)
        self.require_csrf(session, csrf_token)
        self.require_permission(account, permission)
        self._rate_limit(operation, f"{account.id}:{source}", limit=limit)
        return account

    def list_accounts(
        self, token: str, permission: InterfacePermission = InterfacePermission.ACCOUNTS_MANAGE
    ) -> tuple[Account, ...]:
        account, _ = self.authenticate(token)
        self.require_permission(account, permission)
        return self.repository.accounts()

    def create_managed_account(
        self,
        token: str,
        csrf_token: str | None,
        *,
        username: str,
        display_name: str,
        password: str,
        role: AccountRole,
        actor_id: str | None,
        source: str,
    ) -> ManagedAccountResult:
        administrator, session = self.authenticate(token)
        self.require_csrf(session, csrf_token)
        self.require_permission(administrator, InterfacePermission.ACCOUNTS_MANAGE)
        if role is AccountRole.OWNER:
            raise PermissionDenied("Creating another Owner is not supported")
        normalized = self._validate_profile(username, display_name)
        if self.repository.account_by_username(normalized) is not None:
            raise AccountConflict("Username already exists")
        now = self.clock()
        account = Account(
            id=str(uuid4()),
            username=normalized,
            display_name=display_name.strip(),
            password_hash=self._validated_password_hash(password),
            role=role,
            status="active",
            actor_id=actor_id.strip() if actor_id and actor_id.strip() else None,
            failed_attempts=0,
            locked_until=None,
            created_at=now,
            password_changed_at=now,
            mfa_secret_ciphertext=None,
            mfa_enabled=False,
            mfa_last_counter=None,
            must_change_password=True,
        )
        self.repository.create_account(account)
        recovery_codes = self._new_recovery_codes()
        self.repository.replace_recovery_codes(
            account.id, tuple(_secret_hash(code) for code in recovery_codes), now
        )
        self._event("auth.account_created", account.id, source, f"role={role.value}")
        return ManagedAccountResult(account=account, recovery_codes=recovery_codes)

    def set_managed_account_role(
        self,
        token: str,
        csrf_token: str | None,
        target_account_id: str,
        role: AccountRole,
        source: str,
    ) -> None:
        administrator, session = self.authenticate(token)
        self.require_csrf(session, csrf_token)
        self.require_permission(administrator, InterfacePermission.ROLES_MANAGE)
        target = self.repository.account_by_id(target_account_id)
        if target is None:
            raise AccountConflict("Account does not exist")
        if target.role is AccountRole.OWNER or role is AccountRole.OWNER:
            raise PermissionDenied("Owner role changes require a dedicated transfer workflow")
        self.repository.set_account_role(target.id, role)
        self.repository.revoke_all_sessions(target.id, self.clock())
        self._event("auth.account_role_changed", target.id, source, f"role={role.value}")

    def set_managed_account_status(
        self,
        token: str,
        csrf_token: str | None,
        target_account_id: str,
        enabled: bool,
        source: str,
    ) -> None:
        administrator, session = self.authenticate(token)
        self.require_csrf(session, csrf_token)
        self.require_permission(administrator, InterfacePermission.ACCOUNTS_MANAGE)
        target = self.repository.account_by_id(target_account_id)
        if target is None:
            raise AccountConflict("Account does not exist")
        if target.id == administrator.id or target.role is AccountRole.OWNER:
            raise PermissionDenied("The active Owner account cannot be disabled")
        status = "active" if enabled else "disabled"
        self.repository.set_account_status(target.id, status)
        if not enabled:
            self.repository.revoke_all_sessions(target.id, self.clock())
        self._event("auth.account_status_changed", target.id, source, f"status={status}")

    def list_security_events(self, token: str) -> tuple[SecurityEvent, ...]:
        account, _ = self.authenticate(token)
        self.require_permission(account, InterfacePermission.SECURITY_EVENTS_VIEW)
        return self.repository.security_events()

    def list_machine_credentials(self, token: str) -> tuple[MachineCredential, ...]:
        account, _session = self.authenticate(token)
        self.require_permission(account, InterfacePermission.SYSTEM_CONFIGURE)
        return self.repository.machine_credentials()

    def create_machine_credential(
        self,
        token: str,
        csrf_token: str | None,
        *,
        label: str,
        scopes: tuple[str, ...],
        source: str,
    ) -> MachineCredentialResult:
        account, session = self.authenticate(token)
        self.require_csrf(session, csrf_token)
        self.require_permission(account, InterfacePermission.SYSTEM_CONFIGURE)
        if session.mfa_verified_at is None:
            raise MfaRequired("Recent MFA verification required")
        normalized_label = label.strip()
        if not 1 <= len(normalized_label) <= 128:
            raise AccountConflict("Machine credential label must be 1-128 characters")
        normalized_scopes = tuple(dict.fromkeys(scope.strip() for scope in scopes if scope.strip()))
        if not normalized_scopes or not set(normalized_scopes) <= MACHINE_CREDENTIAL_SCOPES:
            raise AccountConflict("Machine credential scopes are invalid")
        credential_id = uuid4().hex
        token = f"mc_{credential_id}.{secrets.token_urlsafe(32)}"
        now = self.clock()
        credential = MachineCredential(
            id=credential_id,
            label=normalized_label,
            token_hash=self.password_hasher.hash_password(token),
            scopes=normalized_scopes,
            created_at=now,
            created_by=account.id,
            last_used_at=None,
            revoked_at=None,
        )
        self.repository.create_machine_credential(credential)
        self._event(
            "auth.machine_credential_created",
            account.id,
            source,
            f"credential_id={credential.id};label={credential.label};scopes={','.join(credential.scopes)}",
        )
        return MachineCredentialResult(credential=credential, token=token)

    def authenticate_machine_credential(
        self, token: str, required_scope: str | None = None
    ) -> MachineCredential:
        if not token.startswith("mc_") or "." not in token:
            raise InvalidMachineCredential("Invalid machine credential")
        credential_id, _secret = token[3:].split(".", maxsplit=1)
        credential = self.repository.machine_credential_by_id(credential_id)
        if (
            credential is None
            or credential.revoked_at is not None
            or not self.password_hasher.verify_password(token, credential.token_hash)
        ):
            raise InvalidMachineCredential("Invalid machine credential")
        if required_scope is not None and required_scope not in credential.scopes:
            raise PermissionDenied("Machine credential scope is insufficient")
        self.repository.touch_machine_credential(credential.id, self.clock())
        return credential

    def revoke_machine_credential(
        self,
        token: str,
        csrf_token: str | None,
        credential_id: str,
        source: str,
    ) -> None:
        account, session = self.authenticate(token)
        self.require_csrf(session, csrf_token)
        self.require_permission(account, InterfacePermission.SYSTEM_CONFIGURE)
        if not self.repository.revoke_machine_credential(credential_id, self.clock()):
            raise AccountConflict("Machine credential does not exist or is already revoked")
        self._event("auth.machine_credential_revoked", account.id, source, credential_id)

    def rotate_session(
        self, token: str, csrf_token: str | None, source: str, user_agent: str
    ) -> SessionBundle:
        account, session = self.authenticate(token)
        self.require_csrf(session, csrf_token)
        self.repository.revoke_session(session.id, self.clock())
        bundle = self._create_session(account, source, user_agent)
        self._event("auth.session_rotated", account.id, source, session.id)
        return bundle

    def logout(self, token: str, csrf_token: str | None, source: str) -> None:
        account, session = self.authenticate(token)
        self.require_csrf(session, csrf_token)
        self.repository.revoke_session(session.id, self.clock())
        self._event("auth.logout", account.id, source, session.id)

    def revoke_session(
        self, token: str, csrf_token: str | None, target_session_id: str, source: str
    ) -> None:
        account, current = self.authenticate(token)
        self.require_csrf(current, csrf_token)
        target = next(
            (
                item
                for item in self.repository.sessions_for_account(account.id)
                if item.id == target_session_id
            ),
            None,
        )
        if target is None:
            raise InvalidSession("Session does not exist")
        self.repository.revoke_session(target.id, self.clock())
        self._event("auth.session_revoked", account.id, source, target.id)

    def change_password(
        self,
        token: str,
        csrf_token: str | None,
        current_password: str,
        new_password: str,
        source: str,
    ) -> None:
        account, session = self.authenticate(token)
        self.require_csrf(session, csrf_token)
        if not self.password_hasher.verify_password(current_password, account.password_hash):
            self._event("auth.password_change_rejected", account.id, source, "invalid password")
            raise InvalidCredentials("Current password is incorrect")
        if self.password_hasher.verify_password(new_password, account.password_hash):
            raise PasswordRejected("New password must differ from the current password")
        new_hash = self._validated_password_hash(new_password)
        now = self.clock()
        self.repository.change_password(account.id, new_hash, now)
        self.repository.revoke_all_sessions(account.id, now)
        self._event("auth.password_changed", account.id, source, "all sessions revoked")

    def recover(self, username: str, recovery_code: str, new_password: str, source: str) -> None:
        self._rate_limit("recovery", source, limit=10)
        account = self.repository.account_by_username(username.strip().lower())
        now = self.clock()
        code_hash = _secret_hash(recovery_code.strip().upper())
        new_hash = self._validated_password_hash(new_password)
        code_valid = bool(
            account and self.repository.consume_recovery_code(account.id, code_hash, now)
        )
        if not code_valid or account is None or account.status != "active":
            self._event(
                "auth.recovery_failed", account.id if account else None, source, "invalid recovery"
            )
            raise InvalidRecovery("Recovery request could not be completed")
        self.repository.change_password(account.id, new_hash, now)
        self.repository.disable_mfa(account.id)
        self.repository.revoke_all_sessions(account.id, now)
        self._event(
            "auth.recovery_completed", account.id, source, "password reset; sessions revoked"
        )

    def begin_mfa_enrollment(
        self,
        token: str,
        csrf_token: str | None,
        current_password: str,
        source: str,
        *,
        issuer: str = "Project-AI Control Center",
    ) -> MfaEnrollment:
        account, session = self.authenticate(token)
        self.require_csrf(session, csrf_token)
        if not self.password_hasher.verify_password(current_password, account.password_hash):
            raise InvalidCredentials("Current password is incorrect")
        cipher = self._mfa_cipher()
        secret = b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")
        ciphertext = cipher.encrypt(secret.encode("ascii")).decode("ascii")
        self.repository.set_mfa_secret(account.id, ciphertext)
        label = quote(f"{issuer}:{account.username}")
        uri = (
            f"otpauth://totp/{label}?secret={secret}&issuer={quote(issuer)}"
            "&algorithm=SHA1&digits=6&period=30"
        )
        self._event("auth.mfa_enrollment_started", account.id, source, "pending confirmation")
        return MfaEnrollment(secret=secret, provisioning_uri=uri)

    def confirm_mfa_enrollment(
        self, token: str, csrf_token: str | None, code: str, source: str
    ) -> None:
        account, session = self.authenticate(token)
        self.require_csrf(session, csrf_token)
        if not account.mfa_secret_ciphertext or account.mfa_enabled:
            raise InvalidMfa("MFA enrollment is not pending")
        counter = self._matching_mfa_counter(account, code)
        self.repository.enable_mfa(account.id, counter)
        now = self.clock()
        self.repository.mark_session_mfa(session.id, now)
        self._event("auth.mfa_enabled", account.id, source, "TOTP enabled")

    def step_up_mfa(self, token: str, csrf_token: str | None, code: str, source: str) -> None:
        account, session = self.authenticate(token)
        self.require_csrf(session, csrf_token)
        if not account.mfa_enabled:
            raise InvalidMfa("MFA is not enabled")
        self._verify_mfa(account, code, consume=True)
        self.repository.mark_session_mfa(session.id, self.clock())
        self._event("auth.mfa_step_up", account.id, source, session.id)

    def disable_mfa(
        self,
        token: str,
        csrf_token: str | None,
        current_password: str,
        code: str,
        source: str,
    ) -> None:
        account, session = self.authenticate(token)
        self.require_csrf(session, csrf_token)
        if not self.password_hasher.verify_password(current_password, account.password_hash):
            raise InvalidCredentials("Current password is incorrect")
        if not account.mfa_enabled:
            raise InvalidMfa("MFA is not enabled")
        self._verify_mfa(account, code, consume=True)
        now = self.clock()
        self.repository.disable_mfa(account.id)
        self.repository.revoke_all_sessions(account.id, now)
        self._event("auth.mfa_disabled", account.id, source, "all sessions revoked")

    def _mfa_cipher(self) -> Fernet:
        if self._fernet is None:
            raise MfaUnavailable("MFA encryption key is not configured")
        return self._fernet

    def _mfa_secret(self, account: Account) -> str:
        if not account.mfa_secret_ciphertext:
            raise InvalidMfa("MFA is not configured")
        try:
            return (
                self._mfa_cipher()
                .decrypt(account.mfa_secret_ciphertext.encode("ascii"))
                .decode("ascii")
            )
        except InvalidToken as error:
            raise MfaUnavailable("MFA secret cannot be decrypted") from error

    def _matching_mfa_counter(self, account: Account, code: str) -> int:
        normalized = code.strip().replace(" ", "")
        if not re.fullmatch(r"\d{6}", normalized):
            raise InvalidMfa("Invalid authenticator code")
        secret = self._mfa_secret(account)
        now = self.clock()
        current = int(now.timestamp()) // 30
        for counter in (current - 1, current, current + 1):
            instant = datetime.fromtimestamp(counter * 30, tz=UTC)
            if hmac.compare_digest(calculate_totp(secret, instant), normalized):
                if account.mfa_last_counter is not None and counter <= account.mfa_last_counter:
                    break
                return counter
        raise InvalidMfa("Invalid authenticator code")

    def _verify_mfa(self, account: Account, code: str, *, consume: bool) -> None:
        counter = self._matching_mfa_counter(account, code)
        if consume and not self.repository.consume_mfa_counter(account.id, counter):
            raise InvalidMfa("Authenticator code was already used")

    def _create_session(
        self,
        account: Account,
        source: str,
        user_agent: str,
        *,
        mfa_verified: bool = False,
    ) -> SessionBundle:
        now = self.clock()
        token = secrets.token_urlsafe(32)
        csrf_token = secrets.token_urlsafe(32)
        session = StoredSession(
            id=str(uuid4()),
            account_id=account.id,
            token_hash=_secret_hash(token),
            csrf_hash=_secret_hash(csrf_token),
            created_at=now,
            last_seen_at=now,
            idle_expires_at=now + self.idle_timeout,
            absolute_expires_at=now + self.absolute_timeout,
            user_agent=user_agent[:512],
            client_host=source[:128],
            revoked_at=None,
            mfa_verified_at=now if mfa_verified else None,
        )
        self.repository.create_session(session)
        return SessionBundle(account=account, session=session, token=token, csrf_token=csrf_token)

    def _validated_password_hash(self, password: str) -> str:
        valid, error = self.password_hasher.validate_password_strength(
            password, self.password_policy
        )
        if not valid:
            raise PasswordRejected(error)
        hashed: str = self.password_hasher.hash_password(password)
        return hashed

    @staticmethod
    def _validate_profile(username: str, display_name: str) -> str:
        normalized = username.strip().lower()
        if not USERNAME.fullmatch(normalized):
            raise AccountServiceError(
                "Username must be 3-64 letters, numbers, dots, dashes, or underscores"
            )
        if not 1 <= len(display_name.strip()) <= 120:
            raise AccountServiceError("Display name must be 1-120 characters")
        return normalized

    @staticmethod
    def _new_recovery_codes() -> tuple[str, ...]:
        def code() -> str:
            raw = "".join(secrets.choice(RECOVERY_ALPHABET) for _ in range(12))
            return f"{raw[:4]}-{raw[4:8]}-{raw[8:]}"

        return tuple(code() for _ in range(10))

    def _event(self, event_type: str, account_id: str | None, source: str, detail: str) -> None:
        safe_detail = json.dumps({"message": detail}, sort_keys=True, separators=(",", ":"))
        self.repository.append_event(
            event_type, account_id, self.clock(), source[:128], safe_detail
        )

    def _rate_limit(self, operation: str, source: str, *, limit: int) -> str:
        bucket = _secret_hash(f"{operation}:{source}")
        blocked = self.repository.rate_limit_hit(
            bucket,
            self.clock(),
            window_seconds=5 * 60,
            limit=limit,
            block_seconds=15 * 60,
        )
        if blocked:
            self._event(f"auth.{operation}_rate_limited", None, source, "source bucket blocked")
            raise RateLimited("Too many attempts; try again later")
        return bucket
