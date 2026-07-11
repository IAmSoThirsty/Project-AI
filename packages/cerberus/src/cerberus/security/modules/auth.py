"""
cerberus.security.modules.auth — Password hashing, policy, and sessions.

Rebuilt from upstream ``IAmSoThirsty/Cerberus``
``src/cerberus/security/modules/auth.py``. Upstream used bcrypt as the
primary hasher; that dependency is not present in this workspace and is not
declared here, so hashing is rebuilt on stdlib PBKDF2-HMAC-SHA256
(``hashlib``, constant-time verification via ``hmac.compare_digest``).
Password hashes are stored as ``pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>``.
Timestamps are timezone-aware UTC (repo policy).
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

PBKDF2_ALGORITHM = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 600_000
_SALT_BYTES = 16
_DERIVED_KEY_LEN = 32
_SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"


@dataclass
class Session:
    """Authenticated user session."""

    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    ip_address: str | None = None
    user_agent: str | None = None
    is_active: bool = True


@dataclass
class PasswordPolicy:
    """Password policy requirements."""

    min_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digit: bool = True
    require_special: bool = True
    max_age_days: int = 90
    prevent_reuse_count: int = 5


class PasswordHasher:
    """PBKDF2-HMAC-SHA256 password hashing and strength validation."""

    def __init__(self, iterations: int = PBKDF2_ITERATIONS) -> None:
        """Initialize with a PBKDF2 iteration count (work factor)."""
        self.iterations = iterations

    def hash_password(self, password: str, salt: bytes | None = None) -> str:
        """Hash a password to ``pbkdf2_sha256$iterations$salt$hash``."""
        if salt is None:
            salt = secrets.token_bytes(_SALT_BYTES)
        derived = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, self.iterations, dklen=_DERIVED_KEY_LEN
        )
        return f"{PBKDF2_ALGORITHM}${self.iterations}${salt.hex()}${derived.hex()}"

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against a stored PBKDF2 hash (constant time)."""
        try:
            algorithm, iterations_str, salt_hex, hash_hex = hashed.split("$")
            if algorithm != PBKDF2_ALGORITHM:
                return False
            iterations = int(iterations_str)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(hash_hex)
        except (ValueError, AttributeError):
            return False

        derived = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, iterations, dklen=len(expected)
        )
        return hmac.compare_digest(derived, expected)

    def validate_password_strength(
        self, password: str, policy: PasswordPolicy | None = None
    ) -> tuple[bool, str]:
        """Validate a password against a policy; return (is_valid, error)."""
        policy = policy or PasswordPolicy()

        if len(password) < policy.min_length:
            return False, f"Password must be at least {policy.min_length} characters"
        if policy.require_uppercase and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        if policy.require_lowercase and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        if policy.require_digit and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        if policy.require_special and not any(c in _SPECIAL_CHARS for c in password):
            return False, "Password must contain at least one special character"
        return True, ""


@dataclass
class User:
    """User account with credential and lockout state."""

    user_id: str
    username: str
    password_hash: str
    email: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_login: datetime | None = None
    failed_login_attempts: int = 0
    locked_until: datetime | None = None
    password_changed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    previous_passwords: list[str] = field(default_factory=list)
    is_active: bool = True


class AuthManager:
    """Authentication manager with sessions and account lockout."""

    def __init__(
        self,
        password_policy: PasswordPolicy | None = None,
        session_duration_hours: int = 24,
        max_failed_attempts: int = 5,
        lockout_duration_minutes: int = 30,
    ) -> None:
        """Initialize with a password policy and session/lockout parameters."""
        self.password_hasher = PasswordHasher()
        self.password_policy = password_policy or PasswordPolicy()
        self.session_duration = timedelta(hours=session_duration_hours)
        self.max_failed_attempts = max_failed_attempts
        self.lockout_duration = timedelta(minutes=lockout_duration_minutes)
        self.users: dict[str, User] = {}
        self.sessions: dict[str, Session] = {}

    def create_user(
        self,
        username: str,
        password: str,
        email: str | None = None,
        user_id: str | None = None,
    ) -> tuple[bool, str, User | None]:
        """Create a user after policy validation; return (ok, message, user)."""
        is_valid, error = self.password_hasher.validate_password_strength(
            password, self.password_policy
        )
        if not is_valid:
            return False, error, None
        if any(u.username == username for u in self.users.values()):
            return False, "Username already exists", None

        if user_id is None:
            user_id = f"user_{secrets.token_hex(8)}"

        user = User(
            user_id=user_id,
            username=username,
            password_hash=self.password_hasher.hash_password(password),
            email=email,
        )
        self.users[user_id] = user
        return True, "User created successfully", user

    def authenticate(
        self,
        username: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[bool, Session | None, str]:
        """Authenticate credentials and create a session on success."""
        user = next((u for u in self.users.values() if u.username == username), None)
        if not user:
            return False, None, "Invalid username or password"

        now = datetime.now(UTC)
        if user.locked_until and now < user.locked_until:
            remaining = (user.locked_until - now).total_seconds() / 60
            return False, None, f"Account locked. Try again in {remaining:.0f} minutes"
        if not user.is_active:
            return False, None, "Account is disabled"

        if not self.password_hasher.verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= self.max_failed_attempts:
                user.locked_until = now + self.lockout_duration
                return False, None, "Account locked due to too many failed attempts"
            return False, None, "Invalid username or password"

        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = now
        session = self._create_session(user.user_id, ip_address, user_agent)
        return True, session, "Authentication successful"

    def _create_session(
        self,
        user_id: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Session:
        now = datetime.now(UTC)
        session = Session(
            session_id=secrets.token_urlsafe(32),
            user_id=user_id,
            created_at=now,
            expires_at=now + self.session_duration,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.sessions[session.session_id] = session
        return session

    def validate_session(self, session_id: str) -> User | None:
        """Return the user for a valid, unexpired, active session."""
        session = self.sessions.get(session_id)
        if not session or not session.is_active:
            return None
        if datetime.now(UTC) > session.expires_at:
            session.is_active = False
            return None
        user = self.users.get(session.user_id)
        if not user or not user.is_active:
            return None
        return user

    def logout(self, session_id: str) -> bool:
        """Invalidate a session."""
        session = self.sessions.get(session_id)
        if session:
            session.is_active = False
            return True
        return False

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> tuple[bool, str]:
        """Change a user's password with reuse and policy checks."""
        user = self.users.get(user_id)
        if not user:
            return False, "User not found"
        if not self.password_hasher.verify_password(old_password, user.password_hash):
            return False, "Current password is incorrect"

        is_valid, error = self.password_hasher.validate_password_strength(
            new_password, self.password_policy
        )
        if not is_valid:
            return False, error

        reuse_window = user.previous_passwords[: self.password_policy.prevent_reuse_count]
        if any(
            self.password_hasher.verify_password(new_password, old_hash)
            for old_hash in [user.password_hash, *reuse_window]
        ):
            return (
                False,
                f"Cannot reuse any of the last "
                f"{self.password_policy.prevent_reuse_count} passwords",
            )

        user.previous_passwords.insert(0, user.password_hash)
        user.password_hash = self.password_hasher.hash_password(new_password)
        user.password_changed_at = datetime.now(UTC)
        return True, "Password changed successfully"

    def cleanup_expired_sessions(self) -> None:
        """Remove sessions whose expiry has passed."""
        now = datetime.now(UTC)
        expired = [sid for sid, sess in self.sessions.items() if now > sess.expires_at]
        for sid in expired:
            del self.sessions[sid]


__all__ = [
    "AuthManager",
    "PasswordHasher",
    "PasswordPolicy",
    "Session",
    "User",
]
