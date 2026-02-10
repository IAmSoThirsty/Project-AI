"""Final tests to reach 100% coverage for all three modules."""

import json
import os
import tempfile
from unittest.mock import patch

from app.core.user_manager import UserManager


class TestUserManagerLine57NoFernetKey:
    """Test line 57: _setup_cipher else clause when FERNET_KEY is not set."""

    def test_setup_cipher_else_clause_no_fernet_key(self):
        """Cover line 57: else clause generates new Fernet key.

        When FERNET_KEY environment variable is NOT set, line 57 executes:
        self.cipher_suite = Fernet(Fernet.generate_key())
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            users_file = os.path.join(tmpdir, "users.json")

            # Create a temporary .env file without FERNET_KEY
            env_file = os.path.join(tmpdir, ".env")
            with open(env_file, "w") as f:
                f.write("# No FERNET_KEY set\n")

            # Patch load_dotenv to load from our temp .env file
            with patch("app.core.user_manager.load_dotenv") as mock_load_dotenv:
                # Mock load_dotenv to do nothing (or load from our empty .env)
                mock_load_dotenv.return_value = None

                # Also ensure the environment variable is not set
                with patch.dict(os.environ, {}, clear=False):
                    os.environ.pop("FERNET_KEY", None)

                    # Create manager - this should trigger line 57 in _setup_cipher
                    manager = UserManager(users_file=users_file)

                    # Verify cipher_suite was created
                    assert manager.cipher_suite is not None

                    # Verify it works (can encrypt/decrypt)
                    test_data = "test_encryption"
                    encrypted = manager.cipher_suite.encrypt(test_data.encode())
                    decrypted = manager.cipher_suite.decrypt(encrypted).decode()
                    assert decrypted == test_data


class TestUserManagerLine84EmptyPassword:
    """Test line 84: continue statement in _migrate_plaintext_passwords."""

    def test_migrate_plaintext_passwords_empty_password_line_84(self):
        """Cover line 84: continue when password is empty/None.

        When migrating passwords, if a password is empty/None,
        line 84 executes: continue (skips this user)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            users_file = os.path.join(tmpdir, "users.json")

            # Create a users.json file with a user that has an empty password
            users_data = {
                "alice": {
                    "password": "",  # Empty password - should trigger continue
                    "persona": "friendly",
                    "preferences": {},
                },
                "bob": {
                    "password": None,  # None password - should trigger continue
                    "persona": "friendly",
                    "preferences": {},
                },
                "charlie": {
                    "password": "valid_password",  # Valid password - should be migrated
                    "persona": "friendly",
                    "preferences": {},
                },
            }

            with open(users_file, "w") as f:
                json.dump(users_data, f)

            # Initialize UserManager - triggers _migrate_plaintext_passwords
            manager = UserManager(users_file=users_file)

            # alice and bob should still have plaintext passwords (line 84 continue)
            assert "password" in manager.users["alice"]
            assert manager.users["alice"]["password"] == ""
            assert "password" in manager.users["bob"]
            assert manager.users["bob"]["password"] is None

            # charlie should have password_hash (was migrated)
            assert "password_hash" in manager.users["charlie"]
            assert "password" not in manager.users["charlie"]

            # Verify only charlie's password was migrated in the persisted file
            with open(users_file) as f:
                saved_data = json.load(f)
            assert "password" in saved_data["alice"]  # Still has plaintext
            assert "password_hash" in saved_data["charlie"]  # Was migrated
