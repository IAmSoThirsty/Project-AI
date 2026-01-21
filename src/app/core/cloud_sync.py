"""
Cloud synchronization system for cross-device data persistence.

Provides encrypted bidirectional sync with automatic conflict resolution.
"""

import hashlib
import json
import logging
import os
import platform
import uuid
from datetime import datetime
from typing import Any

import requests
from cryptography.fernet import Fernet
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class CloudSyncManager:
    """Manages encrypted cloud synchronization for user data."""

    def __init__(
        self, encryption_key: str | bytes | None = None, data_dir: str = "data"
    ):
        """Initialize cloud sync manager.

        Args:
            encryption_key: Optional Fernet key for encryption. If None, loads from FERNET_KEY env var.
            data_dir: Directory for storing sync metadata (default: "data")
        """
        load_dotenv()
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        # Setup encryption
        key = encryption_key or os.getenv("FERNET_KEY")
        if key:
            if isinstance(key, str):
                key = key.encode()
            self.encryption_key = key
        else:
            self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)

        # Setup cloud sync URL
        self.cloud_sync_url = os.getenv("CLOUD_SYNC_URL")

        # Generate device ID
        self.device_id = self._generate_device_id()

        # Sync metadata
        self.sync_metadata_path = os.path.join(data_dir, "sync_metadata.json")
        self.sync_metadata = self._load_sync_metadata()

        # Auto-sync configuration
        self.auto_sync_enabled = False
        self.auto_sync_interval = 300  # 5 minutes default

        logger.info(f"CloudSyncManager initialized for device: {self.device_id}")

    def _generate_device_id(self) -> str:
        """Generate a unique device identifier using SHA-256.

        Returns:
            str: SHA-256 hash of device characteristics
        """
        # Combine multiple device characteristics
        device_info = f"{platform.node()}-{platform.system()}-{platform.machine()}-{uuid.getnode()}"
        device_hash = hashlib.sha256(device_info.encode()).hexdigest()
        return device_hash[:16]  # Use first 16 chars for readability

    def _load_sync_metadata(self) -> dict[str, Any]:
        """Load sync metadata from disk.

        Returns:
            dict: Sync metadata including last sync times and conflict info
        """
        if os.path.exists(self.sync_metadata_path):
            try:
                with open(self.sync_metadata_path) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading sync metadata: {e}")
                return {}
        return {}

    def _save_sync_metadata(self) -> None:
        """Save sync metadata to disk."""
        try:
            with open(self.sync_metadata_path, "w") as f:
                json.dump(self.sync_metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving sync metadata: {e}")

    def encrypt_data(self, data: dict[str, Any]) -> bytes:
        """Encrypt data using Fernet cipher.

        Args:
            data: Dictionary to encrypt

        Returns:
            bytes: Encrypted data
        """
        try:
            json_data = json.dumps(data)
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())
            return encrypted_data
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise

    def decrypt_data(self, encrypted_data: bytes) -> dict[str, Any]:
        """Decrypt data using Fernet cipher.

        Args:
            encrypted_data: Encrypted bytes to decrypt

        Returns:
            dict: Decrypted data dictionary
        """
        try:
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise

    def sync_upload(self, username: str, data: dict[str, Any]) -> bool:
        """Upload user data to cloud with encryption.

        Args:
            username: Username for data association
            data: User data to sync

        Returns:
            bool: True if upload successful, False otherwise
        """
        if not self.cloud_sync_url:
            logger.warning("Cloud sync URL not configured")
            return False

        try:
            # Add metadata
            sync_data = {
                "username": username,
                "device_id": self.device_id,
                "timestamp": datetime.now().isoformat(),
                "data": data,
            }

            # Encrypt data
            encrypted_data = self.encrypt_data(sync_data)

            # Upload to cloud
            response = requests.post(
                f"{self.cloud_sync_url}/upload",
                json={
                    "username": username,
                    "device_id": self.device_id,
                    "encrypted_data": encrypted_data.hex(),  # Convert bytes to hex string
                },
                timeout=30,
            )

            if response.status_code == 200:
                # Update sync metadata
                self.sync_metadata[username] = {
                    "last_upload": datetime.now().isoformat(),
                    "device_id": self.device_id,
                }
                self._save_sync_metadata()
                logger.info(f"Successfully uploaded data for {username}")
                return True
            else:
                logger.error(
                    f"Upload failed with status {response.status_code}: {response.text}"
                )
                return False

        except requests.RequestException as e:
            logger.error(f"Network error during upload: {e}")
            return False
        except Exception as e:
            logger.error(f"Error during sync upload: {e}")
            return False

    def sync_download(self, username: str) -> dict[str, Any] | None:
        """Download user data from cloud with decryption.

        Args:
            username: Username for data retrieval

        Returns:
            dict | None: Decrypted user data or None if failed
        """
        if not self.cloud_sync_url:
            logger.warning("Cloud sync URL not configured")
            return None

        try:
            # Request data from cloud
            response = requests.get(
                f"{self.cloud_sync_url}/download",
                params={
                    "username": username,
                    "device_id": self.device_id,
                },
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                encrypted_data = bytes.fromhex(data["encrypted_data"])

                # Decrypt data
                decrypted_data = self.decrypt_data(encrypted_data)

                # Update sync metadata
                self.sync_metadata[username] = {
                    "last_download": datetime.now().isoformat(),
                    "device_id": self.device_id,
                }
                self._save_sync_metadata()

                logger.info(f"Successfully downloaded data for {username}")
                return decrypted_data

            elif response.status_code == 404:
                logger.info(f"No cloud data found for {username}")
                return None
            else:
                logger.error(
                    f"Download failed with status {response.status_code}: {response.text}"
                )
                return None

        except requests.RequestException as e:
            logger.error(f"Network error during download: {e}")
            return None
        except Exception as e:
            logger.error(f"Error during sync download: {e}")
            return None

    def resolve_conflict(
        self, local_data: dict[str, Any], cloud_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Resolve conflicts between local and cloud data.

        Uses timestamp-based resolution: most recent data wins.

        Args:
            local_data: Local data with timestamp
            cloud_data: Cloud data with timestamp

        Returns:
            dict: Resolved data (most recent)
        """
        try:
            local_timestamp = datetime.fromisoformat(
                local_data.get("timestamp", "1970-01-01T00:00:00")
            )
            cloud_timestamp = datetime.fromisoformat(
                cloud_data.get("timestamp", "1970-01-01T00:00:00")
            )

            if local_timestamp >= cloud_timestamp:
                logger.info("Using local data (more recent)")
                return local_data
            else:
                logger.info("Using cloud data (more recent)")
                return cloud_data

        except Exception as e:
            logger.error(f"Error resolving conflict: {e}")
            # Default to local data if resolution fails
            return local_data

    def bidirectional_sync(
        self, username: str, local_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Perform bidirectional sync with conflict resolution.

        Args:
            username: Username for sync
            local_data: Current local data (should include 'timestamp' field)

        Returns:
            dict: Resolved data after sync
        """
        if not self.cloud_sync_url:
            logger.warning("Cloud sync URL not configured, using local data")
            return local_data

        try:
            # Download cloud data
            cloud_data = self.sync_download(username)

            if cloud_data is None:
                # No cloud data, upload local
                logger.info("No cloud data found, uploading local data")
                self.sync_upload(username, local_data)
                return local_data

            # Extract the actual data from cloud response (which includes metadata)
            # sync_download returns the full decrypted payload with username, device_id, timestamp, data
            cloud_timestamp = cloud_data.get("timestamp")
            local_timestamp = local_data.get("timestamp")

            # Compare timestamps to determine which data is newer
            if local_timestamp and cloud_timestamp:
                from datetime import datetime

                try:
                    local_dt = datetime.fromisoformat(local_timestamp)
                    cloud_dt = datetime.fromisoformat(cloud_timestamp)

                    if local_dt >= cloud_dt:
                        # Local is newer or same, upload only if needed
                        logger.info("Local data is current or newer")
                        if local_dt > cloud_dt:
                            # Only upload if local is strictly newer
                            self.sync_upload(username, local_data)
                        return local_data
                    else:
                        # Cloud is newer, extract and upload to ensure consistency
                        logger.info("Cloud data is newer, using cloud version")
                        resolved_data = cloud_data.get("data", cloud_data)
                        return resolved_data
                except (ValueError, TypeError) as e:
                    logger.warning(
                        f"Error comparing timestamps: {e}, defaulting to local data"
                    )
                    return local_data
            else:
                # Fallback: use timestamp-based conflict resolution
                resolved_data = self.resolve_conflict(local_data, cloud_data)

                # Only upload if resolved data is different from cloud
                if resolved_data == local_data:
                    self.sync_upload(username, resolved_data)

                return resolved_data

        except Exception as e:
            logger.error(f"Error during bidirectional sync: {e}")
            return local_data

    def enable_auto_sync(self, interval: int = 300) -> None:
        """Enable automatic synchronization.

        Args:
            interval: Sync interval in seconds (default: 300 = 5 minutes)
        """
        self.auto_sync_enabled = True
        self.auto_sync_interval = interval
        logger.info(f"Auto-sync enabled with {interval}s interval")

    def disable_auto_sync(self) -> None:
        """Disable automatic synchronization."""
        self.auto_sync_enabled = False
        logger.info("Auto-sync disabled")

    def get_sync_status(self, username: str) -> dict[str, Any]:
        """Get sync status for a user.

        Args:
            username: Username to check

        Returns:
            dict: Sync status information
        """
        metadata = self.sync_metadata.get(username, {})
        return {
            "device_id": self.device_id,
            "cloud_sync_configured": self.cloud_sync_url is not None,
            "auto_sync_enabled": self.auto_sync_enabled,
            "auto_sync_interval": self.auto_sync_interval,
            "last_upload": metadata.get("last_upload"),
            "last_download": metadata.get("last_download"),
        }

    def list_devices(self, username: str) -> list[dict[str, Any]]:
        """List devices that have synced data for a user.

        Args:
            username: Username to check

        Returns:
            list: List of device information dicts
        """
        if not self.cloud_sync_url:
            logger.warning("Cloud sync URL not configured")
            return [{"device_id": self.device_id, "current": True}]

        try:
            response = requests.get(
                f"{self.cloud_sync_url}/devices",
                params={"username": username},
                timeout=30,
            )

            if response.status_code == 200:
                devices = response.json().get("devices", [])
                # Mark current device
                for device in devices:
                    device["current"] = device.get("device_id") == self.device_id
                return devices
            else:
                logger.error(f"Failed to list devices: {response.status_code}")
                return [{"device_id": self.device_id, "current": True}]

        except Exception as e:
            logger.error(f"Error listing devices: {e}")
            return [{"device_id": self.device_id, "current": True}]
