"""Secure storage utility using Fernet encryption.

Provides a unified interface for encrypting and decrypting JSON data at rest.
Required for P0/P1 security compliance.
"""

import json
import logging
import os
import tempfile
from typing import Any

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class SecureStorage:
    def __init__(self, key: str | None = None):
        """
        Initialize with a Fernet key.
        If no key is provided, attempts to load from FERNET_KEY env var.
        """
        self.key = key or os.getenv("FERNET_KEY")
        if not self.key:
            logger.warning("No FERNET_KEY found. Generating a runtime-only key.")
            self.key = Fernet.generate_key().decode()

        try:
            self.cipher = Fernet(self.key.encode())
        except Exception as e:
            logger.error(f"Invalid Fernet key: {e}")
            raise ValueError("Invalid encryption key provided.")

    def save_encrypted_json(self, file_path: str, data: Any):
        """Encrypts and saves data atomically with 0o600 permissions."""
        dirname = os.path.dirname(os.path.abspath(file_path))
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

        json_data = json.dumps(data, indent=4).encode()
        encrypted_data = self.cipher.encrypt(json_data)

        fd, temp_path = tempfile.mkstemp(dir=dirname, prefix="secure_", suffix=".tmp")
        try:
            os.chmod(temp_path, 0o600)
            with os.fdopen(fd, "wb") as f:
                f.write(encrypted_data)
            os.replace(temp_path, file_path)
        except Exception as e:
            os.close(fd) if "fd" in locals() else None
            if os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error(f"Failed to save encrypted data: {e}")
            raise

    def load_encrypted_json(self, file_path: str) -> Any | None:
        """Loads and decrypts JSON data from file."""
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "rb") as f:
                encrypted_data = f.read()

            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        except Exception as e:
            logger.error(f"Failed to load/decrypt data from {file_path}: {e}")
            return None
