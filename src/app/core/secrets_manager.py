"""
Secrets management: environment-backed and Fernet-encrypted file stores.
"""

from __future__ import annotations

import json
import os
from enum import Enum
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet


class SecretType(Enum):
    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"
    CERTIFICATE = "certificate"
    DATABASE_URL = "database_url"


class EnvironmentSecretStore:
    def __init__(self, prefix: str = "") -> None:
        self._prefix = prefix.upper()
        self._mapping: dict[str, str] = {}

    def _env_var(self, name: str) -> str:
        return self._prefix + name.upper()

    def set_secret(self, name: str, value: str, secret_type: SecretType | None = None) -> None:
        env_var = self._env_var(name)
        self._mapping[name] = env_var
        os.environ[env_var] = value

    def get_secret(self, name: str) -> str | None:
        env_var = self._mapping.get(name, self._env_var(name))
        return os.environ.get(env_var)

    def delete_secret(self, name: str) -> None:
        env_var = self._mapping.pop(name, self._env_var(name))
        os.environ.pop(env_var, None)


class EncryptedFileSecretStore:
    def __init__(self, storage_path: Path | str, encryption_key: str | bytes) -> None:
        self._path = Path(storage_path)
        key = encryption_key.encode() if isinstance(encryption_key, str) else encryption_key
        self._fernet = Fernet(key)
        self._data: dict[str, Any] = {}
        if self._path.exists():
            self._load()

    def _load(self) -> None:
        try:
            encrypted = self._path.read_bytes()
            decrypted = self._fernet.decrypt(encrypted)
            self._data = json.loads(decrypted)
        except Exception:
            self._data = {}

    def _save(self) -> None:
        plaintext = json.dumps(self._data).encode()
        self._path.write_bytes(self._fernet.encrypt(plaintext))

    def set_secret(
        self,
        name: str,
        value: str,
        secret_type: SecretType | None = None,
        expires_in_days: int | None = None,
    ) -> None:
        self._data[name] = {
            "value": value,
            "type": secret_type.value if secret_type else None,
        }
        self._save()

    def get_secret(self, name: str) -> str | None:
        entry = self._data.get(name)
        return entry["value"] if entry else None

    def rotate_secret(self, name: str, new_value: str) -> None:
        entry = self._data.get(name, {})
        entry["value"] = new_value
        self._data[name] = entry
        self._save()

    def delete_secret(self, name: str) -> None:
        self._data.pop(name, None)
        self._save()
