# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / encryption.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / encryption.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Encryption Module

Provides encryption at rest for sensitive data with:
- Fernet/AES encryption
- Key management
- Key rotation
- Secure key storage
"""

import base64
import json
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, MultiFernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


@dataclass
class EncryptionKey:
    """Encryption key with metadata"""

    key_id: str
    key_data: bytes
    created_at: datetime
    expires_at: datetime | None = None
    is_active: bool = True


class KeyManager:
    """
    Manages encryption keys with rotation support
    """

    def __init__(
        self,
        key_dir: str = "/var/lib/cerberus/keys",
        rotation_days: int = 90,
    ):
        """
        Initialize key manager

        Args:
            key_dir: Directory to store keys
            rotation_days: Days before key rotation
        """
        self.key_dir = Path(key_dir)
        self.key_dir.mkdir(parents=True, exist_ok=True)
        self.rotation_days = rotation_days

        self.keys: dict[str, EncryptionKey] = {}
        self._load_keys()

        # Ensure we have at least one active key
        if not self._get_active_keys():
            self.generate_key()

    def _load_keys(self):
        """Load keys from disk"""
        key_file = self.key_dir / "keys.json"
        if key_file.exists():
            with open(key_file) as f:
                data = json.load(f)
                for key_data in data.get("keys", []):
                    key = EncryptionKey(
                        key_id=key_data["key_id"],
                        key_data=base64.b64decode(key_data["key_data"]),
                        created_at=datetime.fromisoformat(key_data["created_at"]),
                        expires_at=datetime.fromisoformat(key_data["expires_at"])
                        if key_data.get("expires_at")
                        else None,
                        is_active=key_data.get("is_active", True),
                    )
                    self.keys[key.key_id] = key

    def _save_keys(self):
        """Save keys to disk"""
        key_file = self.key_dir / "keys.json"
        data = {
            "keys": [
                {
                    "key_id": key.key_id,
                    "key_data": base64.b64encode(key.key_data).decode("utf-8"),
                    "created_at": key.created_at.isoformat(),
                    "expires_at": key.expires_at.isoformat()
                    if key.expires_at
                    else None,
                    "is_active": key.is_active,
                }
                for key in self.keys.values()
            ]
        }

        # Write atomically
        temp_file = key_file.with_suffix(".tmp")
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=2)

        temp_file.replace(key_file)

        # Set restrictive permissions
        os.chmod(key_file, 0o600)

    def generate_key(self, key_id: str | None = None) -> EncryptionKey:
        """
        Generate a new encryption key

        Args:
            key_id: Optional key ID (generated if None)

        Returns:
            Generated encryption key
        """
        if key_id is None:
            key_id = f"key_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"

        # Generate Fernet key
        key_data = Fernet.generate_key()

        # Create key object
        key = EncryptionKey(
            key_id=key_id,
            key_data=key_data,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=self.rotation_days),
            is_active=True,
        )

        self.keys[key_id] = key
        self._save_keys()

        return key

    def rotate_keys(self) -> EncryptionKey:
        """
        Rotate encryption keys

        Returns:
            New active key
        """
        # Deactivate old keys
        for key in self.keys.values():
            if key.is_active:
                key.is_active = False

        # Generate new key
        new_key = self.generate_key()

        self._save_keys()

        return new_key

    def get_key(self, key_id: str) -> EncryptionKey | None:
        """Get key by ID"""
        return self.keys.get(key_id)

    def get_active_key(self) -> EncryptionKey | None:
        """Get the current active key"""
        active_keys = self._get_active_keys()
        return active_keys[0] if active_keys else None

    def _get_active_keys(self) -> list:
        """Get all active keys"""
        return [key for key in self.keys.values() if key.is_active]

    def get_all_keys(self) -> list:
        """Get all keys for decryption (including inactive ones)"""
        return list(self.keys.values())

    def check_rotation_needed(self) -> bool:
        """Check if key rotation is needed"""
        active_key = self.get_active_key()
        if not active_key:
            return True

        if active_key.expires_at and datetime.now() >= active_key.expires_at:
            return True

        return False

    def derive_key_from_password(
        self, password: str, salt: bytes | None = None
    ) -> bytes:
        """
        Derive encryption key from password using PBKDF2

        Args:
            password: Password to derive from
            salt: Salt (generated if None)

        Returns:
            Derived key
        """
        if salt is None:
            salt = secrets.token_bytes(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )

        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key


class EncryptionManager:
    """
    Manages encryption and decryption of sensitive data
    """

    def __init__(self, key_manager: KeyManager | None = None):
        """
        Initialize encryption manager

        Args:
            key_manager: Key manager instance
        """
        self.key_manager = key_manager or KeyManager()

    def encrypt(self, data: bytes) -> dict[str, str]:
        """
        Encrypt data with active key

        Args:
            data: Data to encrypt

        Returns:
            Dictionary with encrypted data and key ID
        """
        key = self.key_manager.get_active_key()
        if not key:
            raise ValueError("No active encryption key available")

        fernet = Fernet(key.key_data)
        encrypted = fernet.encrypt(data)

        return {
            "key_id": key.key_id,
            "data": base64.b64encode(encrypted).decode("utf-8"),
        }

    def decrypt(self, encrypted_data: dict[str, str]) -> bytes:
        """
        Decrypt data

        Args:
            encrypted_data: Dictionary with encrypted data and key ID

        Returns:
            Decrypted data
        """
        key_id = encrypted_data["key_id"]
        key = self.key_manager.get_key(key_id)

        if not key:
            raise ValueError(f"Encryption key not found: {key_id}")

        encrypted = base64.b64decode(encrypted_data["data"])
        fernet = Fernet(key.key_data)

        return fernet.decrypt(encrypted)

    def encrypt_with_multi_key(self, data: bytes) -> dict[str, str]:
        """
        Encrypt with multiple keys for rotation support

        Args:
            data: Data to encrypt

        Returns:
            Dictionary with encrypted data and key IDs
        """
        keys = self.key_manager.get_all_keys()
        if not keys:
            raise ValueError("No encryption keys available")

        fernets = [Fernet(key.key_data) for key in keys]
        multi_fernet = MultiFernet(fernets)

        encrypted = multi_fernet.encrypt(data)

        return {
            "key_ids": [key.key_id for key in keys],
            "data": base64.b64encode(encrypted).decode("utf-8"),
        }

    def encrypt_string(self, text: str) -> dict[str, str]:
        """Encrypt string"""
        return self.encrypt(text.encode("utf-8"))

    def decrypt_string(self, encrypted_data: dict[str, str]) -> str:
        """Decrypt string"""
        return self.decrypt(encrypted_data).decode("utf-8")

    def encrypt_json(self, data: Any) -> dict[str, str]:
        """Encrypt JSON-serializable data"""
        json_str = json.dumps(data)
        return self.encrypt_string(json_str)

    def decrypt_json(self, encrypted_data: dict[str, str]) -> Any:
        """Decrypt JSON data"""
        json_str = self.decrypt_string(encrypted_data)
        return json.loads(json_str)

    def encrypt_file(self, input_path: str, output_path: str):
        """
        Encrypt file

        Args:
            input_path: Path to input file
            output_path: Path to output file
        """
        with open(input_path, "rb") as f:
            data = f.read()

        encrypted = self.encrypt(data)

        with open(output_path, "w") as f:
            json.dump(encrypted, f)

    def decrypt_file(self, input_path: str, output_path: str):
        """
        Decrypt file

        Args:
            input_path: Path to encrypted file
            output_path: Path to output file
        """
        with open(input_path) as f:
            encrypted = json.load(f)

        data = self.decrypt(encrypted)

        with open(output_path, "wb") as f:
            f.write(data)

    def rotate_encrypted_data(self, encrypted_data: dict[str, str]) -> dict[str, str]:
        """
        Re-encrypt data with new key

        Args:
            encrypted_data: Encrypted data with old key

        Returns:
            Re-encrypted data with new key
        """
        # Decrypt with old key
        data = self.decrypt(encrypted_data)

        # Encrypt with new key
        return self.encrypt(data)
