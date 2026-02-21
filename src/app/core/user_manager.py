"""User profile and data management system with secure password hashing.

This module replaces plaintext password storage with bcrypt hashing using
passlib. It supports an onboarding flow where, if no users are present,
the application should prompt to create an admin user. The `create_user`
method stores a password hash under the `password_hash` key. If an existing
`users.json` contains plaintext `password` entries, this manager will migrate
them to hashed `password_hash` entries on load.

STATUS: PRODUCTION
"""

import json
import logging
import os

from dotenv import load_dotenv
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha256

from app.core.utils.path_validator import validate_path
from app.core.utils.secure_storage import SecureStorage

logger = logging.getLogger(__name__)

# Setup password hashing context.
# Prefer pbkdf2_sha256 to avoid bcrypt backend issues in some environments.
# Keep bcrypt listed so older hashes remain verifiable.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto",
)


class UserManager:
    def __init__(self, users_file="users.json"):
        """Manage users and load encryption key from environment.

        - Loads FERNET_KEY from environment (via `.env`) if present.
        - Loads users from `users_file` when present. If not present,
          keeps an empty users dict until an admin is created through
          the onboarding flow.
        - Migrates any plaintext passwords to bcrypt hashes on load.
        """
        load_dotenv()
        self.users: dict = {}
        self.current_user: str | None = None

        # Setup secure storage
        self.storage = SecureStorage()

        # Validate path (P1 compliance)
        self.users_file = validate_path(users_file, os.getcwd()) or "users.json"

        self._load_users()

    def _load_users(self):
        """Load users from file (encrypted or plain) and migrate if needed."""
        if not os.path.exists(self.users_file):
            return

        # Attempt to load as encrypted
        self.users = self.storage.load_encrypted_json(self.users_file)

        if self.users is None:
            # Fallback for plain JSON (migration)
            try:
                with open(self.users_file) as f:
                    self.users = json.load(f)
                logger.info("Migrated plain JSON to encrypted storage.")
                self.save_users()  # Save back as encrypted
            except Exception:
                self.users = {}

        # Migrate any plaintext passwords to hashes
        self._migrate_plaintext_passwords()

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

    def save_users(self):
        """Save users to file securely using SecureStorage"""
        try:
            self.storage.save_encrypted_json(self.users_file, self.users)
        except Exception as e:
            logger.error(f"Failed to save users securely: {e}")
            raise

    def authenticate(self, username, password):
        """Authenticate a user using stored bcrypt password hash."""
        user = self.users.get(username)
        if not user:
            return False
        password_hash = user.get("password_hash")
        if not password_hash:
            return False
        try:
            if pwd_context.verify(password, password_hash):
                self.current_user = username
                return True
        except Exception:
            return False
        return False

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
        pw_hash = pwd_context.hash(password)
        self.users[username] = {
            "password_hash": pw_hash,
            "persona": persona,
            "preferences": preferences,
            "location_active": False,
            "approved": True,
            "role": "user",
        }
        self.save_users()
        return True

    def get_user_data(self, username):
        """Get sanitized user data (omit password hash)."""
        user = self.users.get(username)
        if not user:
            return {}
        sanitized = {k: v for k, v in user.items() if k != "password_hash"}
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
