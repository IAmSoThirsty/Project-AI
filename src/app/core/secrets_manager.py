"""
Secrets Management System for Project-AI.

Provides secure handling of sensitive configuration data including:
- Environment variable integration
- Encrypted storage
- Secret rotation
- Credential management
- Integration with external secret stores
"""

import base64
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class SecretType(Enum):
    """Types of secrets."""

    API_KEY = "API_KEY"
    PASSWORD = "PASSWORD"
    TOKEN = "TOKEN"
    CERTIFICATE = "CERTIFICATE"
    ENCRYPTION_KEY = "ENCRYPTION_KEY"
    DATABASE_URL = "DATABASE_URL"
    PRIVATE_KEY = "PRIVATE_KEY"
    OTHER = "OTHER"


@dataclass
class Secret:
    """Represents a managed secret."""

    key: str
    value: str
    secret_type: SecretType
    created_at: datetime = field(
        default_factory=lambda: (
            datetime.now(datetime.UTC)
            if hasattr(datetime, "UTC")
            else datetime.utcnow()
        )
    )
    expires_at: datetime | None = None
    rotation_required: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if secret has expired."""
        if self.expires_at is None:
            return False
        now = (
            datetime.now(datetime.UTC)
            if hasattr(datetime, "UTC")
            else datetime.utcnow()
        )
        return now > self.expires_at

    def needs_rotation(self) -> bool:
        """Check if secret needs rotation."""
        return self.rotation_required or self.is_expired()


class SecretStore(Protocol):
    """Protocol for secret store implementations."""

    def get_secret(self, key: str) -> str | None:
        """Retrieve a secret by key."""
        ...

    def set_secret(
        self, key: str, value: str, secret_type: SecretType, **kwargs
    ) -> None:
        """Store a secret."""
        ...

    def delete_secret(self, key: str) -> None:
        """Delete a secret."""
        ...

    def list_secrets(self) -> list[str]:
        """List all secret keys."""
        ...


class EnvironmentSecretStore:
    """Secret store that reads from environment variables."""

    def __init__(self, prefix: str = "PROJECTAI_"):
        """
        Initialize environment secret store.

        Args:
            prefix: Prefix for environment variables
        """
        self.prefix = prefix

    def get_secret(self, key: str) -> str | None:
        """Get secret from environment variable."""
        env_key = f"{self.prefix}{key.upper()}"
        value = os.environ.get(env_key)
        if value:
            logger.debug(f"Retrieved secret from environment: {env_key}")
        return value

    def set_secret(
        self, key: str, value: str, secret_type: SecretType, **kwargs
    ) -> None:
        """Set environment variable (for current process only)."""
        env_key = f"{self.prefix}{key.upper()}"
        os.environ[env_key] = value
        logger.info(f"Set secret in environment: {env_key}")

    def delete_secret(self, key: str) -> None:
        """Delete environment variable."""
        env_key = f"{self.prefix}{key.upper()}"
        if env_key in os.environ:
            del os.environ[env_key]
            logger.info(f"Deleted secret from environment: {env_key}")

    def list_secrets(self) -> list[str]:
        """List all secrets with prefix."""
        return [
            key[len(self.prefix) :].lower()
            for key in os.environ
            if key.startswith(self.prefix)
        ]


class EncryptedFileSecretStore:
    """Secret store that stores encrypted secrets in a file."""

    def __init__(self, storage_path: Path, encryption_key: str | None = None):
        """
        Initialize encrypted file secret store.

        Args:
            storage_path: Path to encrypted secrets file
            encryption_key: Encryption key (if None, uses FERNET_KEY from env)
        """
        self.storage_path = storage_path
        self._secrets: dict[str, Secret] = {}

        # Get or generate encryption key
        if encryption_key is None:
            encryption_key = os.environ.get("FERNET_KEY")
            if encryption_key is None:
                raise ConfigurationError(
                    "No encryption key provided. Set FERNET_KEY environment variable or pass encryption_key parameter"
                )

        # Initialize Fernet cipher
        try:
            self._cipher = Fernet(
                encryption_key.encode()
                if isinstance(encryption_key, str)
                else encryption_key
            )
        except Exception as e:
            raise ConfigurationError(
                f"Invalid encryption key: {e}", original_exception=e
            )

        # Load existing secrets
        self._load_secrets()

    def get_secret(self, key: str) -> str | None:
        """Get secret from encrypted store."""
        secret = self._secrets.get(key)
        if secret is None:
            return None

        if secret.is_expired():
            logger.warning(f"Secret '{key}' has expired")
            return None

        return secret.value

    def set_secret(
        self,
        key: str,
        value: str,
        secret_type: SecretType,
        expires_in_days: int | None = None,
        **kwargs,
    ) -> None:
        """Store secret in encrypted store."""
        expires_at = None
        if expires_in_days:
            now = (
                datetime.now(datetime.UTC)
                if hasattr(datetime, "UTC")
                else datetime.utcnow()
            )
            expires_at = now + timedelta(days=expires_in_days)

        secret = Secret(
            key=key,
            value=value,
            secret_type=secret_type,
            expires_at=expires_at,
            metadata=kwargs,
        )

        self._secrets[key] = secret
        self._save_secrets()
        logger.info(f"Stored secret: {key} (type={secret_type.value})")

    def delete_secret(self, key: str) -> None:
        """Delete secret from encrypted store."""
        if key in self._secrets:
            del self._secrets[key]
            self._save_secrets()
            logger.info(f"Deleted secret: {key}")

    def list_secrets(self) -> list[str]:
        """List all secret keys."""
        return list(self._secrets.keys())

    def rotate_secret(self, key: str, new_value: str) -> None:
        """Rotate a secret with a new value."""
        if key not in self._secrets:
            raise ConfigurationError(f"Secret not found: {key}")

        secret = self._secrets[key]
        secret.value = new_value
        secret.created_at = (
            datetime.now(datetime.UTC)
            if hasattr(datetime, "UTC")
            else datetime.utcnow()
        )
        secret.rotation_required = False

        self._save_secrets()
        logger.info(f"Rotated secret: {key}")

    def mark_for_rotation(self, key: str) -> None:
        """Mark a secret for rotation."""
        if key not in self._secrets:
            raise ConfigurationError(f"Secret not found: {key}")

        self._secrets[key].rotation_required = True
        self._save_secrets()
        logger.info(f"Marked secret for rotation: {key}")

    def get_secrets_needing_rotation(self) -> list[str]:
        """Get list of secrets that need rotation."""
        return [key for key, secret in self._secrets.items() if secret.needs_rotation()]

    def _load_secrets(self) -> None:
        """Load secrets from encrypted file."""
        if not self.storage_path.exists():
            logger.info(f"No existing secrets file at {self.storage_path}")
            return

        try:
            with open(self.storage_path, "rb") as f:
                encrypted_data = f.read()

            # Decrypt data
            decrypted_data = self._cipher.decrypt(encrypted_data)
            secrets_data = json.loads(decrypted_data.decode())

            # Reconstruct Secret objects
            for key, secret_dict in secrets_data.items():
                self._secrets[key] = Secret(
                    key=secret_dict["key"],
                    value=secret_dict["value"],
                    secret_type=SecretType(secret_dict["secret_type"]),
                    created_at=datetime.fromisoformat(secret_dict["created_at"]),
                    expires_at=(
                        datetime.fromisoformat(secret_dict["expires_at"])
                        if secret_dict.get("expires_at")
                        else None
                    ),
                    rotation_required=secret_dict.get("rotation_required", False),
                    metadata=secret_dict.get("metadata", {}),
                )

            logger.info(f"Loaded {len(self._secrets)} secrets from {self.storage_path}")

        except Exception as e:
            logger.error(f"Failed to load secrets: {e}")
            raise ConfigurationError(
                f"Failed to load secrets from {self.storage_path}: {e}",
                original_exception=e,
            )

    def _save_secrets(self) -> None:
        """Save secrets to encrypted file."""
        try:
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert secrets to dict
            secrets_data = {
                key: {
                    "key": secret.key,
                    "value": secret.value,
                    "secret_type": secret.secret_type.value,
                    "created_at": secret.created_at.isoformat(),
                    "expires_at": (
                        secret.expires_at.isoformat() if secret.expires_at else None
                    ),
                    "rotation_required": secret.rotation_required,
                    "metadata": secret.metadata,
                }
                for key, secret in self._secrets.items()
            }

            # Encrypt and save
            json_data = json.dumps(secrets_data).encode()
            encrypted_data = self._cipher.encrypt(json_data)

            with open(self.storage_path, "wb") as f:
                f.write(encrypted_data)

            logger.debug(f"Saved {len(self._secrets)} secrets to {self.storage_path}")

        except Exception as e:
            logger.error(f"Failed to save secrets: {e}")
            raise ConfigurationError(
                f"Failed to save secrets to {self.storage_path}: {e}",
                original_exception=e,
            )


class SecretsManager:
    """
    Comprehensive secrets management system.

    Provides a unified interface for managing secrets from multiple sources
    with support for encryption, rotation, and expiration.
    """

    def __init__(
        self,
        storage_path: Path | None = None,
        encryption_key: str | None = None,
        enable_env_fallback: bool = True,
    ):
        """
        Initialize secrets manager.

        Args:
            storage_path: Path to encrypted secrets file
            encryption_key: Encryption key for file storage
            enable_env_fallback: Whether to fall back to environment variables
        """
        # Initialize stores
        self._stores: list[SecretStore] = []

        # Add encrypted file store if path provided
        if storage_path:
            try:
                file_store = EncryptedFileSecretStore(storage_path, encryption_key)
                self._stores.append(file_store)
                self._primary_store = file_store
                logger.info(f"Initialized encrypted file store at {storage_path}")
            except Exception as e:
                logger.error(f"Failed to initialize encrypted file store: {e}")
                self._primary_store = None
        else:
            self._primary_store = None

        # Add environment store
        if enable_env_fallback:
            env_store = EnvironmentSecretStore()
            self._stores.append(env_store)
            logger.info("Initialized environment secret store")

    def get_secret(self, key: str, default: str | None = None) -> str | None:
        """
        Get a secret by key.

        Searches all stores in order until secret is found.

        Args:
            key: Secret key
            default: Default value if secret not found

        Returns:
            Secret value or default
        """
        for store in self._stores:
            value = store.get_secret(key)
            if value is not None:
                return value

        if default is not None:
            return default

        logger.warning(f"Secret not found: {key}")
        return None

    def get_required_secret(self, key: str) -> str:
        """
        Get a required secret.

        Raises:
            ConfigurationError: If secret not found
        """
        value = self.get_secret(key)
        if value is None:
            raise ConfigurationError(
                f"Required secret not found: {key}", context={"key": key}
            )
        return value

    def set_secret(
        self, key: str, value: str, secret_type: SecretType = SecretType.OTHER, **kwargs
    ) -> None:
        """
        Store a secret.

        Args:
            key: Secret key
            value: Secret value
            secret_type: Type of secret
            **kwargs: Additional arguments (e.g., expires_in_days)
        """
        if self._primary_store is None:
            raise ConfigurationError("No primary secret store configured")

        self._primary_store.set_secret(key, value, secret_type, **kwargs)

    def delete_secret(self, key: str) -> None:
        """Delete a secret from all stores."""
        for store in self._stores:
            try:
                store.delete_secret(key)
            except Exception as e:
                logger.warning(f"Failed to delete secret from store: {e}")

    def list_secrets(self) -> list[str]:
        """List all available secret keys."""
        all_keys = set()
        for store in self._stores:
            try:
                all_keys.update(store.list_secrets())
            except Exception as e:
                logger.warning(f"Failed to list secrets from store: {e}")
        return sorted(all_keys)

    def rotate_secret(self, key: str, new_value: str) -> None:
        """
        Rotate a secret with a new value.

        Args:
            key: Secret key
            new_value: New secret value
        """
        if not isinstance(self._primary_store, EncryptedFileSecretStore):
            raise ConfigurationError("Secret rotation requires encrypted file store")

        self._primary_store.rotate_secret(key, new_value)

    def get_secrets_needing_rotation(self) -> list[str]:
        """Get list of secrets that need rotation."""
        if not isinstance(self._primary_store, EncryptedFileSecretStore):
            return []

        return self._primary_store.get_secrets_needing_rotation()

    def generate_encryption_key(self) -> str:
        """Generate a new Fernet encryption key."""
        return Fernet.generate_key().decode()

    @staticmethod
    def derive_key_from_password(
        password: str, salt: bytes | None = None
    ) -> tuple[str, bytes]:
        """
        Derive an encryption key from a password.

        Args:
            password: Password to derive key from
            salt: Optional salt (generated if not provided)

        Returns:
            Tuple of (base64-encoded key, salt)
        """
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )

        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key.decode(), salt


# Global singleton instance
_secrets_manager: SecretsManager | None = None


def get_secrets_manager(
    storage_path: Path | None = None,
    encryption_key: str | None = None,
) -> SecretsManager:
    """
    Get or create the global secrets manager instance.

    Args:
        storage_path: Path to encrypted secrets file (used only on first call)
        encryption_key: Encryption key (used only on first call)

    Returns:
        SecretsManager instance
    """
    global _secrets_manager

    if _secrets_manager is None:
        # Use default path if not provided
        if storage_path is None:
            default_path = Path.home() / ".project-ai" / "secrets.enc"
        else:
            default_path = storage_path

        _secrets_manager = SecretsManager(
            storage_path=default_path, encryption_key=encryption_key
        )

    return _secrets_manager


def reset_secrets_manager() -> None:
    """Reset the global secrets manager (primarily for testing)."""
    global _secrets_manager
    _secrets_manager = None
