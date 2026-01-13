"""Test #3: user_manager.py line 57 - no Fernet key triggers generation."""

import os
import tempfile
from importlib import reload
from unittest.mock import patch


def test_invalid_fernet_key_fallback_line_57():
    """Trigger line 57: else clause in _setup_cipher when FERNET_KEY is NOT set.

    When FERNET_KEY env var is NOT set, line 57 generates a new Fernet key.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        users_file = os.path.join(tmpdir, "users.json")

        # Patch environment to ensure FERNET_KEY is not set
        with patch.dict(os.environ, {}, clear=False):
            # Remove FERNET_KEY if it exists
            os.environ.pop("FERNET_KEY", None)

            # Now import/reload UserManager with no FERNET_KEY set
            import app.core.user_manager as um_module
            reload(um_module)

            # Initialize UserManager - should use the else clause (line 57)
            manager = um_module.UserManager(users_file=users_file)

            # Should have a valid cipher_suite (generated at line 57)
            assert manager.cipher_suite is not None
            assert hasattr(manager.cipher_suite, 'decrypt')  # Verify it's a Fernet object

            # Test that it works
            manager.create_user("test_user", "test_password")
            result = manager.authenticate("test_user", "test_password")
            assert result is True


if __name__ == "__main__":
    test_invalid_fernet_key_fallback_line_57()
    print("✅ Test passed! user_manager.py line 57 covered")
