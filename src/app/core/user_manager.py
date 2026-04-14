"""User profile and data management system with secure password hashing.

This module replaces plaintext password storage with bcrypt hashing using
passlib. It supports an onboarding flow where, if no users are present,
the application should prompt to create an admin user. The `create_user`
method stores a password hash under the `password_hash` key. If an existing
`users.json` contains plaintext `password` entries, this manager will migrate
them to hashed `password_hash` entries on load.
"""

import json
import logging
import os
import secrets
import time

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha256

from app.security.path_security import safe_path_join, validate_filename

logger = logging.getLogger(__name__)

# Setup password hashing context.
# Prefer pbkdf2_sha256 to avoid bcrypt backend issues in some environments.
# Keep bcrypt listed so older hashes remain verifiable.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto",
)


class UserManager:
    def __init__(self, users_file="users.json", data_dir="data"):
        """Manage users and load encryption key from environment.

        - Loads FERNET_KEY from environment (via `.env`) if present.
        - Loads users from `users_file` when present. If not present,
          keeps an empty users dict until an admin is created through
          the onboarding flow.
        - Migrates any plaintext passwords to bcrypt hashes on load.

        Args:
            users_file: Name of users file (stored in data_dir)
            data_dir: Base directory for user data (for path traversal protection)
        """
        load_dotenv()
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        # Validate filename to prevent path traversal
        validate_filename(users_file)
        self.users_file = safe_path_join(data_dir, users_file)

        self.users = {}
        self.current_user = None

        self._setup_cipher()
        self._load_users()

    def _setup_cipher(self):
        """Setup Fernet cipher from environment or generate new key."""
        env_key = os.getenv("FERNET_KEY")
        if env_key:
            try:
                key = env_key.encode()
                self.cipher_suite = Fernet(key)
            except Exception:
                # invalid key -> generate a runtime key
                self.cipher_suite = Fernet(Fernet.generate_key())
        else:
            self.cipher_suite = Fernet(Fernet.generate_key())

    def _load_users(self):
        """Load users from file and migrate plaintext passwords if needed."""
        # Load users (if file exists); do NOT create default plaintext users
        if os.path.exists(self.users_file):
            with open(self.users_file) as f:
                try:
                    self.users = json.load(f)
                except Exception:
                    self.users = {}

            # Migrate any plaintext passwords to hashes
            self._migrate_plaintext_passwords()

            # Ensure all users have lockout fields
            self._ensure_lockout_fields()

    def _migrate_plaintext_passwords(self):
        """Migrate plaintext passwords to hashed versions."""
        migrated = False
        for uname, udata in self.users.items():
            if (
                isinstance(udata, dict)
                and "password" in udata
                and "password_hash" not in udata
            ):
                pw = udata.get("password")
                if not pw:
                    # Skip if password is empty/None
                    continue
                if self._hash_and_store_password(uname, pw):
                    migrated = True

        if migrated:
            self.save_users()

    def _hash_and_store_password(self, username, password):
        """Hash and store password, trying fallback if primary fails.

        Returns True if successful, False otherwise.
        """
        try:
            # try to hash first; only remove plaintext if hashing succeeds
            pw_hash = pwd_context.hash(password)
            self.users[username]["password_hash"] = pw_hash
            # remove plaintext password
            self.users[username].pop("password", None)
            return True
        except Exception:
            # bcrypt hashing failed (backend issues); try a safe fallback
            try:
                fallback_hash = pbkdf2_sha256.hash(password)
                self.users[username]["password_hash"] = fallback_hash
                self.users[username].pop("password", None)
                return True
            except Exception:
                # skip migration for this user if hashing fails
                return False

    def _ensure_lockout_fields(self):
        """Ensure all users have account lockout fields for security."""
        modified = False
        for _username, user_data in self.users.items():
            if isinstance(user_data, dict):
                if "failed_attempts" not in user_data:
                    user_data["failed_attempts"] = 0
                    modified = True
                if "locked_until" not in user_data:
                    user_data["locked_until"] = None
                    modified = True

        if modified:
            self.save_users()
            logger.info("Added account lockout fields to existing users")

    def save_users(self):
        """Save users to file"""
        with open(self.users_file, "w") as f:
            json.dump(self.users, f)

    def authenticate(self, username, password):
        """Authenticate a user using stored bcrypt password hash.

        Implements constant-time authentication to prevent timing attacks:
        - Always performs password verification (even for non-existent users)
        - Uses valid dummy hash for non-existent users to maintain consistent timing
        - Prevents username enumeration via timing side-channels

        Implements account lockout protection:
        - Locks account for 15 minutes after 5 failed attempts
        - Resets failed attempts counter on successful login
        - Returns tuple: (success: bool, message: str)
        """
        # Valid dummy hash for constant-time execution (hash of "dummy_password_for_timing")
        DUMMY_HASH = "$pbkdf2-sha256$29000$dw4hRAhhjBECACBkTOkdAw$J32CKKL8HKxGKBCenxbzNJE1mq8.rpQCu8brEd2o8Fw"
        
        # Get user or use dummy data for constant-time execution
        user_exists = username in self.users
        user = self.users.get(username, {
            "password_hash": DUMMY_HASH,
            "failed_attempts": 0,
            "locked_until": None
        })

        # Check if account is currently locked (only for existing users)
        locked_until = user.get("locked_until")
        if user_exists and locked_until and time.time() < locked_until:
            remaining = int(locked_until - time.time())
            minutes = remaining // 60
            seconds = remaining % 60
            logger.warning(f"Login attempt for locked account: {username}")
            return False, f"Account locked. Try again in {minutes}m {seconds}s"

        # Clear expired lockout (only for existing users)
        if user_exists and locked_until and time.time() >= locked_until:
            user["locked_until"] = None
            user["failed_attempts"] = 0
            self.save_users()

        password_hash = user.get("password_hash", DUMMY_HASH)

        # Always perform verification (constant-time execution)
        is_valid = False
        try:
            is_valid = pwd_context.verify(password, password_hash)
        except Exception:
            # Verification failed (expected for invalid password)
            is_valid = False

        # Add small random delay to further mask timing differences
        time.sleep(secrets.SystemRandom().uniform(0.01, 0.03))

        # Only proceed with authentication if user exists AND password is valid
        if user_exists and is_valid:
            # Successful authentication - reset lockout counters
            user["failed_attempts"] = 0
            user["locked_until"] = None
            self.current_user = username
            self.save_users()
            logger.info(f"User authenticated: {username}")
            return True, "Authentication successful"
        elif user_exists:
            # User exists but wrong password - increment counter
            user["failed_attempts"] = user.get("failed_attempts", 0) + 1

            # Lock account after 5 failed attempts
            if user["failed_attempts"] >= 5:
                user["locked_until"] = time.time() + 900  # 15 minutes
                self.save_users()
                logger.warning(f"Account locked due to failed attempts: {username}")
                return False, "Account locked due to too many failed attempts. Try again in 15 minutes"

            self.save_users()
            logger.warning(f"Failed login attempt for {username} (attempt {user['failed_attempts']}/5)")
            return False, "Invalid credentials"
        else:
            # User doesn't exist - return generic error without revealing this
            return False, "Invalid credentials"

    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """Validate password meets security requirements.

        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

        Returns:
            (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"

        return True, ""

    def create_user(
        self,
        username,
        password,
        persona: str = "friendly",
        preferences=None,
    ):
        """Create a new user with a hashed password.

        Returns True if created, False if user already exists.
        """
        if preferences is None:
            preferences = {
                "language": "en",
                "style": "casual",
            }
        if username in self.users:
            return False

        # Password policy validation
        is_valid, error_msg = self.validate_password_strength(password)
        if not is_valid:
            logger.error(f"Password policy violation for {username}: {error_msg}")
            return False

        pw_hash = pwd_context.hash(password)
        self.users[username] = {
            "password_hash": pw_hash,
            "persona": persona,
            "preferences": preferences,
            "location_active": False,
            "approved": True,
            "role": "user",
            "failed_attempts": 0,
            "locked_until": None,
        }
        self.save_users()
        return True

    def get_user_data(self, username):
        """Get sanitized user data (omit password hash)."""
        u = self.users.get(username)
        if not u:
            return {}
        sanitized = {k: v for k, v in u.items() if k != "password_hash"}
        return sanitized

    # --- Additional management helpers ---
    def list_users(self):
        """Return a shallow copy of users dict."""
        return dict(self.users)

    def delete_user(self, username):
        """Delete a user if exists."""
        if username in self.users:
            del self.users[username]
            self.save_users()
            return True
        return False

    def set_password(self, username, new_password):
        """Set a new password for an existing user (hashes it)."""
        if username not in self.users:
            return False
        self.users[username]["password_hash"] = pwd_context.hash(new_password)
        # Remove any plaintext password if present
        self.users[username].pop("password", None)
        self.save_users()
        return True

    def update_user(self, username, **kwargs):
        """Update user metadata (role, approved, persona, preferences,
        profile_picture).

        Accepts keys like:
        - role (str)
        - approved (bool)
        - persona (str)
        - preferences (dict)
        - profile_picture (path)
        """
        if username not in self.users:
            return False
        for k, v in kwargs.items():
            if k == "password":
                # redirect to set_password to ensure hashing
                self.set_password(username, v)
                continue
            self.users[username][k] = v
        self.save_users()
        return True

    def is_account_locked(self, username):
        """Check if an account is currently locked.

        Args:
            username: Username to check

        Returns:
            tuple: (is_locked: bool, time_remaining: int or None)
        """
        user = self.users.get(username)
        if not user:
            return False, None

        locked_until = user.get("locked_until")
        if locked_until and time.time() < locked_until:
            remaining = int(locked_until - time.time())
            return True, remaining

        return False, None

    def unlock_account(self, username):
        """Manually unlock a user account (admin function).

        Args:
            username: Username to unlock

        Returns:
            bool: True if unlocked, False if user doesn't exist
        """
        if username not in self.users:
            logger.warning(f"Attempted to unlock non-existent user: {username}")
            return False

        user = self.users[username]
        user["failed_attempts"] = 0
        user["locked_until"] = None
        self.save_users()
        logger.info(f"Account manually unlocked: {username}")
        return True
