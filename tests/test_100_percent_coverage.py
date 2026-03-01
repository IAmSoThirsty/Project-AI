"""Final tests to reach 100% coverage for all three modules."""

import json
import os
import tempfile
from unittest.mock import patch

from app.core.user_manager import UserManager
from app.core.utils.secure_storage import SecureStorage


class TestUserManagerLine57NoFernetKey:
    """Test SecureStorage key generation fallback."""

    def test_secure_storage_generates_key_if_none_provided(self):
        """Verify that UserManager initializes SecureStorage which handles keys.

        When FERNET_KEY environment variable is NOT set, SecureStorage
        generates a runtime key if none is provided to its constructor.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Also ensure the environment variable is not set
            with patch.dict("os.environ", {}, clear=True):
                # UserManager initializes SecureStorage() internally
                manager = UserManager(users_file=os.path.join(tmpdir, "users.json"))

                # Verify storage was created and has a key
                assert manager.storage is not None
                assert manager.storage.key is not None


class TestUserManagerLine84EmptyPassword:
    """Test migration skip for empty/None passwords."""

    def test_migrate_plaintext_passwords_empty_password_line_84(self):
        """Cover continue when password is empty/None in users.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            users_file = os.path.join(tmpdir, "users.json")

            # Create a plain JSON users file for migration testing
            users_data = {
                "alice": {
                    "password": "",  # Empty password - should trigger skip
                    "persona": "friendly",
                },
                "bob": {
                    "password": None,  # None password - should trigger skip
                    "persona": "friendly",
                },
                "charlie": {
                    "password": "valid_password",  # Valid password - should be migrated
                    "persona": "friendly",
                },
            }

            # Initially save as plain JSON to trigger migration fallback
            with open(users_file, "w") as f:
                json.dump(users_data, f)

            # Initialize UserManager - triggers _load_users and _migrate_plaintext_passwords
            # We mock SecureStorage.load_encrypted_json to return None to trigger plain fallback
            with patch.object(SecureStorage, "load_encrypted_json", return_value=None):
                manager = UserManager(users_file=users_file)

            # alice and bob should still have plaintext passwords in the dict
            assert "password" in manager.users["alice"]
            assert manager.users["alice"]["password"] == ""

            # charlie should have password_hash
            assert "password_hash" in manager.users["charlie"]
            assert "password" not in manager.users["charlie"]
