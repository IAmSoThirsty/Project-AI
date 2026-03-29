# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / auth.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / auth.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Authentication Module

Password hashing and authentication with:
- bcrypt password hashing
- PBKDF2 support
- Password strength validation
- Session management
"""

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import bcrypt


@dataclass
class Session:
    """User session"""

    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    ip_address: str | None = None
    user_agent: str | None = None
    is_active: bool = True


@dataclass
class PasswordPolicy:
    """Password policy requirements"""

    min_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digit: bool = True
    require_special: bool = True
    max_age_days: int = 90
    prevent_reuse_count: int = 5


class PasswordHasher:
    """
    Secure password hashing using bcrypt
    """

    def __init__(self, rounds: int = 12):
        """
        Initialize password hasher

        Args:
            rounds: Number of bcrypt rounds (cost factor)
        """
        self.rounds = rounds

    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt

        Args:
            password: Plain text password

        Returns:
            Hashed password (base64 encoded)
        """
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify password against hash

        Args:
            password: Plain text password
            hashed: Hashed password

        Returns:
            True if password matches
        """
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False

    def hash_password_pbkdf2(self, password: str, salt: bytes | None = None) -> dict:
        """
        Hash password using PBKDF2

        Args:
            password: Plain text password
            salt: Salt (generated if None)

        Returns:
            Dictionary with hash and salt
        """
        if salt is None:
            salt = secrets.token_bytes(32)

        iterations = 100000
        hashed = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, iterations
        )

        return {
            "hash": hashed.hex(),
            "salt": salt.hex(),
            "iterations": iterations,
            "algorithm": "pbkdf2_sha256",
        }

    def verify_password_pbkdf2(self, password: str, hash_data: dict) -> bool:
        """
        Verify password against PBKDF2 hash

        Args:
            password: Plain text password
            hash_data: Dictionary with hash, salt, and iterations

        Returns:
            True if password matches
        """
        try:
            salt = bytes.fromhex(hash_data["salt"])
            iterations = hash_data["iterations"]

            hashed = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt, iterations
            )

            return hashed.hex() == hash_data["hash"]
        except Exception:
            return False

    def validate_password_strength(
        self, password: str, policy: PasswordPolicy | None = None
    ) -> tuple[bool, str]:
        """
        Validate password against policy

        Args:
            password: Password to validate
            policy: Password policy (uses default if None)

        Returns:
            Tuple of (is_valid, error_message)
        """
        policy = policy or PasswordPolicy()

        if len(password) < policy.min_length:
            return False, f"Password must be at least {policy.min_length} characters"

        if policy.require_uppercase and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if policy.require_lowercase and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if policy.require_digit and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"

        if policy.require_special and not any(
            c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password
        ):
            return False, "Password must contain at least one special character"

        return True, ""


@dataclass
class User:
    """User account"""

    user_id: str
    username: str
    password_hash: str
    email: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    last_login: datetime | None = None
    failed_login_attempts: int = 0
    locked_until: datetime | None = None
    password_changed_at: datetime = field(default_factory=datetime.now)
    previous_passwords: list = field(default_factory=list)
    is_active: bool = True


class AuthManager:
    """
    Authentication manager with session support
    """

    def __init__(
        self,
        password_policy: PasswordPolicy | None = None,
        session_duration_hours: int = 24,
        max_failed_attempts: int = 5,
        lockout_duration_minutes: int = 30,
    ):
        """
        Initialize authentication manager

        Args:
            password_policy: Password policy
            session_duration_hours: Session duration in hours
            max_failed_attempts: Maximum failed login attempts before lockout
            lockout_duration_minutes: Account lockout duration in minutes
        """
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
        """
        Create new user

        Args:
            username: Username
            password: Plain text password
            email: Email address
            user_id: User ID (generated if None)

        Returns:
            Tuple of (success, message, user)
        """
        # Validate password
        is_valid, error = self.password_hasher.validate_password_strength(
            password, self.password_policy
        )
        if not is_valid:
            return False, error, None

        # Check if username exists
        if any(u.username == username for u in self.users.values()):
            return False, "Username already exists", None

        # Generate user ID if not provided
        if user_id is None:
            user_id = f"user_{secrets.token_hex(8)}"

        # Hash password
        password_hash = self.password_hasher.hash_password(password)

        # Create user
        user = User(
            user_id=user_id,
            username=username,
            password_hash=password_hash,
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
        """
        Authenticate user and create session

        Args:
            username: Username
            password: Plain text password
            ip_address: Client IP address
            user_agent: User agent string

        Returns:
            Tuple of (success, session, message)
        """
        # Find user by username
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break

        if not user:
            return False, None, "Invalid username or password"

        # Check if account is locked
        if user.locked_until and datetime.now() < user.locked_until:
            remaining = (user.locked_until - datetime.now()).total_seconds() / 60
            return False, None, f"Account locked. Try again in {remaining:.0f} minutes"

        # Check if account is active
        if not user.is_active:
            return False, None, "Account is disabled"

        # Verify password
        if not self.password_hasher.verify_password(password, user.password_hash):
            user.failed_login_attempts += 1

            # Lock account if too many failed attempts
            if user.failed_login_attempts >= self.max_failed_attempts:
                user.locked_until = datetime.now() + self.lockout_duration
                return (
                    False,
                    None,
                    "Account locked due to too many failed attempts",
                )

            return False, None, "Invalid username or password"

        # Reset failed attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now()

        # Create session
        session = self._create_session(user.user_id, ip_address, user_agent)

        return True, session, "Authentication successful"

    def _create_session(
        self,
        user_id: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Session:
        """Create new session"""
        session_id = secrets.token_urlsafe(32)

        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            expires_at=datetime.now() + self.session_duration,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.sessions[session_id] = session

        return session

    def validate_session(self, session_id: str) -> User | None:
        """
        Validate session and return user

        Args:
            session_id: Session ID

        Returns:
            User if session is valid, None otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            return None

        # Check if session is active
        if not session.is_active:
            return None

        # Check if session has expired
        if datetime.now() > session.expires_at:
            session.is_active = False
            return None

        # Get user
        user = self.users.get(session.user_id)
        if not user or not user.is_active:
            return None

        return user

    def logout(self, session_id: str) -> bool:
        """
        Logout user (invalidate session)

        Args:
            session_id: Session ID

        Returns:
            True if session was invalidated
        """
        session = self.sessions.get(session_id)
        if session:
            session.is_active = False
            return True
        return False

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> tuple[bool, str]:
        """
        Change user password

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            Tuple of (success, message)
        """
        user = self.users.get(user_id)
        if not user:
            return False, "User not found"

        # Verify old password
        if not self.password_hasher.verify_password(old_password, user.password_hash):
            return False, "Current password is incorrect"

        # Validate new password
        is_valid, error = self.password_hasher.validate_password_strength(
            new_password, self.password_policy
        )
        if not is_valid:
            return False, error

        # Check password reuse
        if user.password_hash in user.previous_passwords[
            : self.password_policy.prevent_reuse_count
        ]:
            return (
                False,
                f"Cannot reuse any of the last {self.password_policy.prevent_reuse_count} passwords",
            )

        # Update password
        user.previous_passwords.insert(0, user.password_hash)
        user.password_hash = self.password_hasher.hash_password(new_password)
        user.password_changed_at = datetime.now()

        return True, "Password changed successfully"

    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        now = datetime.now()
        expired = [
            sid for sid, sess in self.sessions.items() if now > sess.expires_at
        ]

        for sid in expired:
            del self.sessions[sid]
