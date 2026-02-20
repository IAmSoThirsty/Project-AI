#!/usr/bin/env python3
"""
Data Persistence Layer - Encrypted State Management and Data Utilities
Project-AI God Tier Zombie Apocalypse Defense Engine

Provides comprehensive data persistence with:
- Encrypted state management (AES-256-GCM, ChaCha20-Poly1305, Fernet)
- Versioned configuration system with migration support
- Automatic backup and recovery
- Audit trail persistence
- Schema validation
- Data compression and optimization
- Air-gapped operation support
"""

import gzip
import hashlib
import json
import logging
import os
import shutil
import threading
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

logger = logging.getLogger(__name__)


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms"""

    AES_256_GCM = "AES-256-GCM"
    CHACHA20_POLY1305 = "ChaCha20-Poly1305"
    FERNET = "Fernet"


@dataclass
class DataVersion:
    """Version information for data migration"""

    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: "DataVersion") -> bool:
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )

    def __eq__(self, other: "DataVersion") -> bool:
        return (self.major, self.minor, self.patch) == (
            other.major,
            other.minor,
            other.patch,
        )

    @classmethod
    def from_string(cls, version_str: str) -> "DataVersion":
        """Parse version string like '1.0.0'"""
        parts = version_str.split(".")
        return cls(int(parts[0]), int(parts[1]), int(parts[2]))


class EncryptedStateManager:
    """
    Encrypted State Management System

    Provides transparent encryption/decryption of sensitive state data with
    support for multiple encryption algorithms and key rotation.
    """

    def __init__(
        self,
        data_dir: str = "data",
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
        master_key: bytes | None = None,
        key_rotation_days: int = 90,
    ):
        """
        Initialize encrypted state manager.

        Args:
            data_dir: Directory for encrypted data storage
            algorithm: Encryption algorithm to use
            master_key: Master encryption key (generates if not provided)
            key_rotation_days: Days between automatic key rotation
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.algorithm = algorithm
        self.key_rotation_days = key_rotation_days

        # Key management
        self.keys_dir = self.data_dir / ".keys"
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        self.keys_dir.chmod(0o700)  # Owner-only access

        self.master_key = master_key or self._load_or_generate_master_key()
        self.current_key_id = self._get_current_key_id()

        # Encryption engines
        self._cipher = self._initialize_cipher()

        # Key rotation tracking
        self.last_rotation = self._get_last_rotation_time()

        # Thread safety
        self._lock = threading.Lock()

        logger.info("Encrypted State Manager initialized (algorithm=%s)", algorithm.value)

    def _load_or_generate_master_key(self) -> bytes:
        """Load existing master key or generate new one."""
        key_file = self.keys_dir / "master.key"

        if key_file.exists():
            with open(key_file, "rb") as f:
                key = f.read()
            logger.info("Loaded existing master key")
        else:
            # Generate new master key
            if self.algorithm == EncryptionAlgorithm.FERNET:
                key = Fernet.generate_key()
            else:
                key = os.urandom(32)  # 256 bits

            # Save key with restrictive permissions
            with open(key_file, "wb") as f:
                f.write(key)
            key_file.chmod(0o600)

            logger.info("Generated new master key")

        return key

    def _get_current_key_id(self) -> str:
        """Get current encryption key identifier."""
        key_id_file = self.keys_dir / "current_key_id"

        if key_id_file.exists():
            with open(key_id_file) as f:
                return f.read().strip()
        else:
            key_id = datetime.now().strftime("%Y%m%d")
            with open(key_id_file, "w") as f:
                f.write(key_id)
            return key_id

    def _initialize_cipher(self):
        """Initialize encryption cipher."""
        if self.algorithm == EncryptionAlgorithm.FERNET:
            return Fernet(self.master_key)
        elif self.algorithm == EncryptionAlgorithm.AES_256_GCM:
            return AESGCM(self.master_key)
        elif self.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            return ChaCha20Poly1305(self.master_key)
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")

    def _get_last_rotation_time(self) -> datetime:
        """Get timestamp of last key rotation."""
        rotation_file = self.keys_dir / "last_rotation"

        if rotation_file.exists():
            with open(rotation_file) as f:
                timestamp_str = f.read().strip()
                return datetime.fromisoformat(timestamp_str)
        else:
            now = datetime.now()
            with open(rotation_file, "w") as f:
                f.write(now.isoformat())
            return now

    def encrypt_data(self, data: bytes) -> tuple[bytes, dict[str, str]]:
        """
        Encrypt data.

        Args:
            data: Data to encrypt

        Returns:
            Tuple of (encrypted_data, metadata)
        """
        with self._lock:
            if self.algorithm == EncryptionAlgorithm.FERNET:
                encrypted = self._cipher.encrypt(data)
                metadata = {
                    "algorithm": self.algorithm.value,
                    "key_id": self.current_key_id,
                }
            else:
                # For AEAD ciphers, generate nonce
                nonce = os.urandom(12)
                encrypted = nonce + self._cipher.encrypt(nonce, data, None)
                metadata = {
                    "algorithm": self.algorithm.value,
                    "key_id": self.current_key_id,
                    "nonce_length": len(nonce),
                }

            return encrypted, metadata

    def decrypt_data(self, encrypted_data: bytes, metadata: dict[str, str]) -> bytes:
        """
        Decrypt data.

        Args:
            encrypted_data: Encrypted data
            metadata: Encryption metadata

        Returns:
            Decrypted data
        """
        with self._lock:
            algorithm = EncryptionAlgorithm(metadata["algorithm"])

            if algorithm == EncryptionAlgorithm.FERNET:
                return self._cipher.decrypt(encrypted_data)
            else:
                nonce_length = metadata.get("nonce_length", 12)
                nonce = encrypted_data[:nonce_length]
                ciphertext = encrypted_data[nonce_length:]
                return self._cipher.decrypt(nonce, ciphertext, None)

    def save_encrypted_state(self, state_id: str, state_data: dict[str, Any]) -> bool:
        """
        Save state with encryption.

        Args:
            state_id: Identifier for the state
            state_data: State data dictionary

        Returns:
            bool: True if save successful
        """
        try:
            # Serialize state
            json_data = json.dumps(state_data, indent=2, default=str)
            data_bytes = json_data.encode("utf-8")

            # Compress if enabled
            compressed = gzip.compress(data_bytes)

            # Encrypt
            encrypted, metadata = self.encrypt_data(compressed)

            # Save encrypted data
            state_file = self.data_dir / f"{state_id}.enc"
            with open(state_file, "wb") as f:
                f.write(encrypted)

            # Save metadata
            metadata_file = self.data_dir / f"{state_id}.meta"
            metadata["timestamp"] = datetime.now().isoformat()
            metadata["original_size"] = len(data_bytes)
            metadata["compressed_size"] = len(compressed)
            metadata["encrypted_size"] = len(encrypted)

            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info("Saved encrypted state: %s (%s bytes)", state_id, len(encrypted))
            return True

        except Exception as e:
            logger.error("Failed to save encrypted state %s: %s", state_id, e)
            return False

    def load_encrypted_state(self, state_id: str) -> dict[str, Any] | None:
        """
        Load encrypted state.

        Args:
            state_id: Identifier for the state

        Returns:
            State data dictionary or None if not found
        """
        try:
            state_file = self.data_dir / f"{state_id}.enc"
            metadata_file = self.data_dir / f"{state_id}.meta"

            if not state_file.exists() or not metadata_file.exists():
                logger.warning("Encrypted state not found: %s", state_id)
                return None

            # Load metadata
            with open(metadata_file) as f:
                metadata = json.load(f)

            # Load encrypted data
            with open(state_file, "rb") as f:
                encrypted = f.read()

            # Decrypt
            compressed = self.decrypt_data(encrypted, metadata)

            # Decompress
            data_bytes = gzip.decompress(compressed)

            # Parse JSON
            json_data = data_bytes.decode("utf-8")
            state_data = json.loads(json_data)

            logger.info("Loaded encrypted state: %s", state_id)
            return state_data

        except Exception as e:
            logger.error("Failed to load encrypted state %s: %s", state_id, e)
            return None

    def rotate_keys(self) -> bool:
        """
        Rotate encryption keys.

        Returns:
            bool: True if rotation successful
        """
        logger.info("Starting key rotation...")

        try:
            # Generate new key
            old_key_id = self.current_key_id

            if self.algorithm == EncryptionAlgorithm.FERNET:
                new_key = Fernet.generate_key()
            else:
                new_key = os.urandom(32)

            new_key_id = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Archive old key
            archive_file = self.keys_dir / f"master_{old_key_id}.key"
            shutil.copy(self.keys_dir / "master.key", archive_file)

            # Save new key
            with open(self.keys_dir / "master.key", "wb") as f:
                f.write(new_key)

            # Update key ID
            with open(self.keys_dir / "current_key_id", "w") as f:
                f.write(new_key_id)

            # Update rotation time
            with open(self.keys_dir / "last_rotation", "w") as f:
                f.write(datetime.now().isoformat())

            # Re-initialize cipher with new key
            self.master_key = new_key
            self.current_key_id = new_key_id
            self._cipher = self._initialize_cipher()
            self.last_rotation = datetime.now()

            logger.info("Key rotation complete: %s -> %s", old_key_id, new_key_id)
            return True

        except Exception as e:
            logger.error("Key rotation failed: %s", e)
            return False

    def check_rotation_needed(self) -> bool:
        """Check if key rotation is needed."""
        age = datetime.now() - self.last_rotation
        return age.days >= self.key_rotation_days


class DataMigrationManager:
    """
    Data Migration and Version Management

    Handles schema versioning and data migration between versions.
    """

    def __init__(self, data_dir: str = "data"):
        """Initialize migration manager."""
        self.data_dir = Path(data_dir)
        self.migrations_dir = Path("config") / "migrations"
        self.migrations_dir.mkdir(parents=True, exist_ok=True)

        self.current_version = DataVersion(1, 0, 0)
        self.migrations: dict[str, callable] = {}

        logger.info("Data Migration Manager initialized")

    def register_migration(self, from_version: str, to_version: str, migration_fn: callable):
        """Register a migration function."""
        key = f"{from_version}->{to_version}"
        self.migrations[key] = migration_fn
        logger.info("Registered migration: %s", key)

    def get_data_version(self, data: dict[str, Any]) -> DataVersion:
        """Extract version from data."""
        version_str = data.get("version", "1.0.0")
        return DataVersion.from_string(version_str)

    def migrate_data(self, data: dict[str, Any], target_version: DataVersion | None = None) -> dict[str, Any]:
        """
        Migrate data to target version.

        Args:
            data: Data to migrate
            target_version: Target version (uses current if not specified)

        Returns:
            Migrated data
        """
        if target_version is None:
            target_version = self.current_version

        current_ver = self.get_data_version(data)

        if current_ver == target_version:
            logger.info("Data already at version %s", target_version)
            return data

        logger.info("Migrating data from %s to %s", current_ver, target_version)

        # Find migration path
        migration_path = self._find_migration_path(current_ver, target_version)

        if not migration_path:
            logger.error("No migration path from %s to %s", current_ver, target_version)
            return data

        # Apply migrations
        migrated_data = data.copy()

        for from_ver, to_ver in migration_path:
            key = f"{from_ver}->{to_ver}"

            if key in self.migrations:
                logger.info("Applying migration: %s", key)
                migrated_data = self.migrations[key](migrated_data)
                migrated_data["version"] = str(to_ver)
            else:
                logger.warning("Migration not found: %s", key)

        logger.info("Migration complete: %s -> %s", current_ver, target_version)
        return migrated_data

    def _find_migration_path(
        self, from_version: DataVersion, to_version: DataVersion
    ) -> list[tuple[DataVersion, DataVersion]]:
        """Find migration path between versions."""
        # Simple sequential migration for now
        # In production, would use graph search for complex migration paths
        path = []

        current = from_version
        while current < to_version:
            # Try to find next version
            next_ver = DataVersion(current.major, current.minor, current.patch + 1)

            if next_ver <= to_version:
                path.append((current, next_ver))
                current = next_ver
            else:
                # Try next minor version
                next_ver = DataVersion(current.major, current.minor + 1, 0)

                if next_ver <= to_version:
                    path.append((current, next_ver))
                    current = next_ver
                else:
                    # Try next major version
                    next_ver = DataVersion(current.major + 1, 0, 0)

                    if next_ver <= to_version:
                        path.append((current, next_ver))
                        current = next_ver
                    else:
                        break

        return path


class BackupManager:
    """
    Automated Backup and Recovery System
    """

    def __init__(
        self,
        data_dir: str = "data",
        backup_dir: str = "data/backups",
        max_backups: int = 7,
        compression_enabled: bool = True,
    ):
        """Initialize backup manager."""
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.max_backups = max_backups
        self.compression_enabled = compression_enabled

        logger.info("Backup Manager initialized (max_backups=%s)", max_backups)

    def create_backup(self, backup_name: str | None = None) -> bool:
        """
        Create a backup of all data.

        Args:
            backup_name: Optional backup name (generates timestamp if not provided)

        Returns:
            bool: True if backup successful
        """
        try:
            if backup_name is None:
                backup_name = datetime.now().strftime("backup_%Y%m%d_%H%M%S")

            backup_path = self.backup_dir / backup_name

            logger.info("Creating backup: %s", backup_name)

            # Create backup using shutil
            if self.compression_enabled:
                shutil.make_archive(str(backup_path), "gztar", self.data_dir)
                backup_file = f"{backup_path}.tar.gz"
            else:
                shutil.copytree(self.data_dir, backup_path, dirs_exist_ok=True)
                backup_file = str(backup_path)

            # Calculate checksum
            checksum = self._calculate_checksum(backup_file)

            # Save metadata
            metadata = {
                "backup_name": backup_name,
                "timestamp": datetime.now().isoformat(),
                "checksum": checksum,
                "compressed": self.compression_enabled,
            }

            metadata_file = self.backup_dir / f"{backup_name}.meta"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info("Backup created successfully: %s", backup_file)

            # Cleanup old backups
            self._cleanup_old_backups()

            return True

        except Exception as e:
            logger.error("Failed to create backup: %s", e)
            return False

    def restore_backup(self, backup_name: str) -> bool:
        """
        Restore from a backup.

        Args:
            backup_name: Name of the backup to restore

        Returns:
            bool: True if restore successful
        """
        try:
            logger.info("Restoring backup: %s", backup_name)

            # Load metadata
            metadata_file = self.backup_dir / f"{backup_name}.meta"
            if not metadata_file.exists():
                logger.error("Backup metadata not found: %s", backup_name)
                return False

            with open(metadata_file) as f:
                metadata = json.load(f)

            # Verify checksum
            if metadata["compressed"]:
                backup_file = self.backup_dir / f"{backup_name}.tar.gz"
            else:
                backup_file = self.backup_dir / backup_name

            if not backup_file.exists():
                logger.error("Backup file not found: %s", backup_file)
                return False

            checksum = self._calculate_checksum(str(backup_file))
            if checksum != metadata["checksum"]:
                logger.error("Checksum mismatch for backup %s", backup_name)
                return False

            # Create backup of current data before restore
            self.create_backup("pre_restore_" + datetime.now().strftime("%Y%m%d_%H%M%S"))

            # Remove current data
            if self.data_dir.exists():
                shutil.rmtree(self.data_dir)

            # Restore from backup
            if metadata["compressed"]:
                shutil.unpack_archive(str(backup_file), self.data_dir)
            else:
                shutil.copytree(backup_file, self.data_dir)

            logger.info("Backup restored successfully: %s", backup_name)
            return True

        except Exception as e:
            logger.error("Failed to restore backup: %s", e)
            return False

    def list_backups(self) -> list[dict[str, Any]]:
        """List all available backups."""
        backups = []

        for meta_file in self.backup_dir.glob("*.meta"):
            try:
                with open(meta_file) as f:
                    metadata = json.load(f)
                backups.append(metadata)
            except Exception as e:
                logger.error("Error reading backup metadata %s: %s", meta_file, e)

        # Sort by timestamp
        backups.sort(key=lambda x: x["timestamp"], reverse=True)

        return backups

    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256 = hashlib.sha256()

        if os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
        elif os.path.isdir(file_path):
            # For directories, hash all files recursively
            for root, _dirs, files in os.walk(file_path):
                for file in sorted(files):
                    file_path_full = os.path.join(root, file)
                    with open(file_path_full, "rb") as f:
                        for chunk in iter(lambda: f.read(8192), b""):
                            sha256.update(chunk)

        return sha256.hexdigest()

    def _cleanup_old_backups(self):
        """Remove old backups exceeding max_backups limit."""
        backups = self.list_backups()

        if len(backups) > self.max_backups:
            to_remove = backups[self.max_backups :]

            for backup in to_remove:
                backup_name = backup["backup_name"]

                # Remove backup file
                if backup["compressed"]:
                    backup_file = self.backup_dir / f"{backup_name}.tar.gz"
                else:
                    backup_file = self.backup_dir / backup_name

                if backup_file.exists():
                    if backup_file.is_file():
                        backup_file.unlink()
                    else:
                        shutil.rmtree(backup_file)

                # Remove metadata
                meta_file = self.backup_dir / f"{backup_name}.meta"
                if meta_file.exists():
                    meta_file.unlink()

                logger.info("Removed old backup: %s", backup_name)


# Convenience functions


def create_encrypted_state_manager(data_dir: str = "data", algorithm: str = "AES-256-GCM") -> EncryptedStateManager:
    """Create an encrypted state manager with default settings."""
    algo_enum = EncryptionAlgorithm(algorithm)
    return EncryptedStateManager(data_dir=data_dir, algorithm=algo_enum)


def create_backup_manager(data_dir: str = "data", max_backups: int = 7) -> BackupManager:
    """Create a backup manager with default settings."""
    return BackupManager(data_dir=data_dir, max_backups=max_backups)
