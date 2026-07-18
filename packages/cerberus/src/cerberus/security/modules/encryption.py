"""
cerberus.security.modules.encryption — Encryption at rest with key rotation.

Ported from the standalone guard-bot repo (``cerberus-guard-bot``
``src/cerberus/security/modules/encryption.py``, HEAD ``4d3400c``),
completing the deferral previously documented in ``cerberus.security``.
Fernet (AES-128-CBC + HMAC) encryption, key management with rotation, and
PBKDF2 key derivation. Requires the ``cryptography`` package (declared in
``packages/cerberus/pyproject.toml``).

Adaptations from upstream (recorded in the C0 reconciliation matrix):

- ``KeyManager`` requires an explicit ``key_dir``; upstream defaulted to
  ``/var/lib/cerberus/keys`` and created it on construction — an unacceptable
  library default and wrong on Windows.
- ``EncryptionManager`` requires an explicit ``KeyManager`` for the same
  reason (upstream default-constructed one).
- Timestamps are timezone-aware UTC (repo policy); naive timestamps in a
  ``keys.json`` written by upstream are coerced to UTC on load, so the
  on-disk schema stays upstream-compatible in both directions.
"""

from __future__ import annotations

import base64
import json
import os
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, MultiFernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

_PBKDF2_ITERATIONS = 100_000
_DERIVED_KEY_LEN = 32
_KEY_FILE_NAME = "keys.json"


def _parse_timestamp(value: str) -> datetime:
    """Parse an ISO timestamp, coercing naive (upstream-written) values to UTC."""
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


@dataclass
class EncryptionKey:
    """Encryption key with rotation metadata."""

    key_id: str
    key_data: bytes
    created_at: datetime
    expires_at: datetime | None = None
    is_active: bool = True


class KeyManager:
    """Manages Fernet encryption keys with rotation support.

    Keys are persisted to ``<key_dir>/keys.json`` (schema compatible with the
    standalone guard-bot) with owner-only permissions where the platform
    supports them. At least one active key is guaranteed after construction.
    """

    def __init__(self, key_dir: str | Path, rotation_days: int = 90) -> None:
        """Initialize the key manager.

        Args:
            key_dir: Directory to store keys (created if missing). Explicit
                by design — there is no default global path.
            rotation_days: Days before a generated key expires.
        """
        self.key_dir = Path(key_dir)
        self.key_dir.mkdir(parents=True, exist_ok=True)
        self.rotation_days = rotation_days
        self.keys: dict[str, EncryptionKey] = {}
        self._load_keys()

        if not self._get_active_keys():
            self.generate_key()

    def _load_keys(self) -> None:
        key_file = self.key_dir / _KEY_FILE_NAME
        if not key_file.exists():
            return
        with open(key_file, encoding="utf-8") as f:
            data = json.load(f)
        for key_data in data.get("keys", []):
            key = EncryptionKey(
                key_id=key_data["key_id"],
                key_data=base64.b64decode(key_data["key_data"]),
                created_at=_parse_timestamp(key_data["created_at"]),
                expires_at=(
                    _parse_timestamp(key_data["expires_at"]) if key_data.get("expires_at") else None
                ),
                is_active=key_data.get("is_active", True),
            )
            self.keys[key.key_id] = key

    def _save_keys(self) -> None:
        key_file = self.key_dir / _KEY_FILE_NAME
        data = {
            "keys": [
                {
                    "key_id": key.key_id,
                    "key_data": base64.b64encode(key.key_data).decode("utf-8"),
                    "created_at": key.created_at.isoformat(),
                    "expires_at": key.expires_at.isoformat() if key.expires_at else None,
                    "is_active": key.is_active,
                }
                for key in self.keys.values()
            ]
        }

        temp_file = key_file.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        temp_file.replace(key_file)
        os.chmod(key_file, 0o600)

    def generate_key(self, key_id: str | None = None) -> EncryptionKey:
        """Generate, persist, and return a new active encryption key."""
        if key_id is None:
            stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            key_id = f"key_{stamp}_{secrets.token_hex(4)}"

        now = datetime.now(UTC)
        key = EncryptionKey(
            key_id=key_id,
            key_data=Fernet.generate_key(),
            created_at=now,
            expires_at=now + timedelta(days=self.rotation_days),
            is_active=True,
        )
        self.keys[key_id] = key
        self._save_keys()
        return key

    def rotate_keys(self) -> EncryptionKey:
        """Deactivate all current keys and generate a new active key.

        Deactivated keys are retained so previously encrypted data stays
        decryptable; re-encrypt with :meth:`EncryptionManager.rotate_encrypted_data`.
        """
        for key in self.keys.values():
            key.is_active = False
        return self.generate_key()

    def get_key(self, key_id: str) -> EncryptionKey | None:
        """Return a key by ID, or None."""
        return self.keys.get(key_id)

    def get_active_key(self) -> EncryptionKey | None:
        """Return the current active key, or None."""
        active_keys = self._get_active_keys()
        return active_keys[0] if active_keys else None

    def _get_active_keys(self) -> list[EncryptionKey]:
        return [key for key in self.keys.values() if key.is_active]

    def get_all_keys(self) -> list[EncryptionKey]:
        """Return all keys (including inactive ones, for decryption)."""
        return list(self.keys.values())

    def check_rotation_needed(self) -> bool:
        """Return True when there is no active key or the active key expired."""
        active_key = self.get_active_key()
        if not active_key:
            return True
        return bool(active_key.expires_at and datetime.now(UTC) >= active_key.expires_at)

    def derive_key_from_password(self, password: str, salt: bytes | None = None) -> bytes:
        """Derive a urlsafe-base64 Fernet-compatible key from a password (PBKDF2)."""
        if salt is None:
            salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=_DERIVED_KEY_LEN,
            salt=salt,
            iterations=_PBKDF2_ITERATIONS,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


class EncryptionManager:
    """Encrypts and decrypts data using keys from a :class:`KeyManager`."""

    def __init__(self, key_manager: KeyManager) -> None:
        """Initialize with an explicit key manager (no implicit default)."""
        self.key_manager = key_manager

    def encrypt(self, data: bytes) -> dict[str, str]:
        """Encrypt bytes with the active key; returns ``{key_id, data}``."""
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
        """Decrypt a ``{key_id, data}`` payload with its recorded key."""
        key_id = encrypted_data["key_id"]
        key = self.key_manager.get_key(key_id)
        if not key:
            raise ValueError(f"Encryption key not found: {key_id}")

        encrypted = base64.b64decode(encrypted_data["data"])
        fernet = Fernet(key.key_data)
        return fernet.decrypt(encrypted)

    def encrypt_with_multi_key(self, data: bytes) -> dict[str, Any]:
        """Encrypt with a MultiFernet over all keys (rotation-tolerant)."""
        keys = self.key_manager.get_all_keys()
        if not keys:
            raise ValueError("No encryption keys available")

        multi_fernet = MultiFernet([Fernet(key.key_data) for key in keys])
        encrypted = multi_fernet.encrypt(data)
        return {
            "key_ids": [key.key_id for key in keys],
            "data": base64.b64encode(encrypted).decode("utf-8"),
        }

    def encrypt_string(self, text: str) -> dict[str, str]:
        """Encrypt a string."""
        return self.encrypt(text.encode("utf-8"))

    def decrypt_string(self, encrypted_data: dict[str, str]) -> str:
        """Decrypt to a string."""
        return self.decrypt(encrypted_data).decode("utf-8")

    def encrypt_json(self, data: Any) -> dict[str, str]:
        """Encrypt JSON-serializable data."""
        return self.encrypt_string(json.dumps(data))

    def decrypt_json(self, encrypted_data: dict[str, str]) -> Any:
        """Decrypt JSON data."""
        return json.loads(self.decrypt_string(encrypted_data))

    def encrypt_file(self, input_path: str | Path, output_path: str | Path) -> None:
        """Encrypt a file to a JSON envelope on disk."""
        data = Path(input_path).read_bytes()
        encrypted = self.encrypt(data)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(encrypted, f)

    def decrypt_file(self, input_path: str | Path, output_path: str | Path) -> None:
        """Decrypt a JSON-envelope file back to raw bytes on disk."""
        with open(input_path, encoding="utf-8") as f:
            encrypted = json.load(f)
        Path(output_path).write_bytes(self.decrypt(encrypted))

    def rotate_encrypted_data(self, encrypted_data: dict[str, str]) -> dict[str, str]:
        """Re-encrypt a payload with the current active key."""
        return self.encrypt(self.decrypt(encrypted_data))


__all__ = [
    "EncryptionKey",
    "EncryptionManager",
    "KeyManager",
]
