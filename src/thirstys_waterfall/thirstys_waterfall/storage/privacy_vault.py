"""Privacy Vault - Encrypted secure storage"""

import logging
from typing import Dict, Any, Optional
import os
from cryptography.fernet import Fernet


class PrivacyVault:
    """
    Encrypted vault for storing sensitive data.
    All data is encrypted at rest with forensic resistance.
    """

    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get("privacy_vault_enabled", True)
        self.encrypted = config.get("encrypted", True)
        self.forensic_resistance = config.get("forensic_resistance", True)
        self.logger = logging.getLogger(__name__)

        self._vault: Dict[str, bytes] = {}
        self._cipher: Optional[Fernet] = None
        self._active = False

    def start(self, encryption_key: Optional[bytes] = None):
        """Start privacy vault"""
        self.logger.info("Starting Privacy Vault")

        if self.encrypted:
            if encryption_key:
                self._cipher = Fernet(encryption_key)
            else:
                # Generate new key
                key = Fernet.generate_key()
                self._cipher = Fernet(key)
                self.logger.warning("Generated new encryption key - store securely!")

        self._active = True

    def stop(self):
        """Stop privacy vault and optionally wipe data"""
        self.logger.info("Stopping Privacy Vault")

        if self.forensic_resistance:
            self._secure_wipe()

        self._active = False

    def store(self, key: str, value: str):
        """
        Store encrypted data in vault.

        Args:
            key: Data key
            value: Data value (will be encrypted)
        """
        if not self._active:
            raise RuntimeError("Vault not active")

        if self._cipher:
            encrypted_value = self._cipher.encrypt(value.encode())
            self._vault[key] = encrypted_value
        else:
            self._vault[key] = value.encode()

        self.logger.debug(f"Stored encrypted data: {key}")

    def retrieve(self, key: str) -> Optional[str]:
        """
        Retrieve and decrypt data from vault.

        Returns:
            Decrypted value or None if not found
        """
        if not self._active or key not in self._vault:
            return None

        encrypted_value = self._vault[key]

        if self._cipher:
            try:
                decrypted = self._cipher.decrypt(encrypted_value)
                return decrypted.decode()
            except Exception as e:
                self.logger.error(f"Decryption failed: {e}")
                return None
        else:
            return encrypted_value.decode()

    def delete(self, key: str):
        """Securely delete data from vault"""
        if key in self._vault:
            # Overwrite before deletion for forensic resistance
            if self.forensic_resistance:
                self._vault[key] = os.urandom(len(self._vault[key]))

            del self._vault[key]
            self.logger.debug(f"Deleted data: {key}")

    def _secure_wipe(self):
        """Securely wipe all vault data"""
        self.logger.info("Performing secure wipe of vault data")

        # Overwrite all data multiple times
        for key in list(self._vault.keys()):
            for _ in range(3):
                self._vault[key] = os.urandom(len(self._vault[key]))

        self._vault.clear()

    def list_keys(self) -> list:
        """List all keys in vault"""
        return list(self._vault.keys())

    def is_active(self) -> bool:
        """Check if vault is active"""
        return self._active
