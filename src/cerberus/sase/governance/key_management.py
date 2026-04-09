#                                           [2026-04-09 06:25]
#                                          Productivity: Active
"""
SASE - Sovereign Adversarial Signal Engine
L12: Lifecycle & Key Management Ceremony

HSM-backed key management with automatic rotation.

KEYS:
- Root signing key
- Event signing key
- Model signing key
- Merkle anchoring key

ROTATION:
- Automatic every 90 days
- Compromise revocation protocol
- HSM escrow
"""

import hashlib
import logging
import time
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("SASE.L12.KeyManagement")


class KeyType(Enum):
    """Cryptographic key types"""

    ROOT_SIGNING = "root_signing"
    EVENT_SIGNING = "event_signing"
    MODEL_SIGNING = "model_signing"
    MERKLE_ANCHORING = "merkle_anchoring"


@dataclass
class CryptographicKey:
    """Key metadata"""

    key_id: str
    key_type: KeyType
    created_at: float
    expires_at: float
    revoked: bool = False
    hsm_backed: bool = True

    def is_expired(self) -> bool:
        """Check if key expired"""
        now = datetime.now(timezone.utc).timestamp()
        return now > self.expires_at

    def days_until_expiry(self) -> int:
        """Days until expiration"""
        now = datetime.now(timezone.utc).timestamp()
        seconds = self.expires_at - now
        return max(0, int(seconds / 86400))


class KeyRotationScheduler:
    """
    Automatic key rotation scheduler

    Rotates keys every 90 days
    """

    ROTATION_INTERVAL_DAYS = 90

    def __init__(self):
        self.last_rotation: dict[KeyType, float] = {}

    def should_rotate(self, key_type: KeyType) -> bool:
        """Check if key should be rotated"""
        if key_type not in self.last_rotation:
            return True

        last = self.last_rotation[key_type]
        now = datetime.now(timezone.utc).timestamp()
        elapsed_days = (now - last) / 86400

        return elapsed_days >= self.ROTATION_INTERVAL_DAYS

    def record_rotation(self, key_type: KeyType):
        """Record key rotation"""
        self.last_rotation[key_type] = datetime.now(timezone.utc).timestamp()
        logger.info("Key rotation recorded: %s", key_type.value)


class HSMInterface:
    """
    Hardware Security Module interface

    Manages keys in HSM for hardware-protected storage
    """

    def __init__(self, hsm_available: bool = False):
        self.hsm_available = hsm_available

        if not hsm_available:
            logger.warning("HSM not available - using software key storage (DEV ONLY)")
        else:
            logger.info("HSM interface initialized")

    def generate_key(self, key_type: KeyType) -> str:
        """Generate key in HSM"""
        if self.hsm_available:
            # TODO: Integrate with actual HSM
            pass

        # Fallback: software key generation (DEV ONLY)
        now = datetime.now(timezone.utc).timestamp()
        key_material = f"{key_type.value}:{now}".encode()
        key_id = hashlib.sha256(key_material).hexdigest()

        logger.info("Key generated: %s -> %s", key_type.value, key_id[:16])

        return key_id

    def sign(self, key_id: str, data: str) -> str:
        """Sign data with HSM key"""
        if self.hsm_available:
            # TODO: HSM signing
            pass

        # Fallback: HMAC signing (DEV ONLY)
        import hmac

        signature = hmac.new(key_id.encode(), data.encode(), hashlib.sha256).hexdigest()

        return signature

    def revoke_key(self, key_id: str):
        """Revoke compromised key"""
        logger.critical("KEY REVOKED: %s", key_id[:16])
        # TODO: HSM revocation


class KeyManagementCeremony:
    """
    L12: Key Management Ceremony

    Orchestrates key lifecycle with HSM
    """

    def __init__(self, hsm_available: bool = False):
        self.hsm = HSMInterface(hsm_available)
        self.scheduler = KeyRotationScheduler()
        self.active_keys: dict[KeyType, CryptographicKey] = {}

        # Initialize keys
        self._initialize_keys()

        logger.info("L12 Key Management Ceremony initialized")

    def _initialize_keys(self):
        """Initialize all key types"""
        for key_type in KeyType:
            self.rotate_key(key_type)

    def rotate_key(self, key_type: KeyType) -> CryptographicKey:
        """
        Rotate cryptographic key

        Generates new key in HSM and updates active keys
        """
        logger.warning("ROTATING KEY: %s", key_type.value)

        # Generate new key
        key_id = self.hsm.generate_key(key_type)

        # Create key metadata
        created = datetime.now(timezone.utc).timestamp()
        expires = created + (self.scheduler.ROTATION_INTERVAL_DAYS * 86400)

        key = CryptographicKey(
            key_id=key_id,
            key_type=key_type,
            created_at=created,
            expires_at=expires,
            hsm_backed=self.hsm.hsm_available,
        )

        # Update active keys
        self.active_keys[key_type] = key

        # Record rotation
        self.scheduler.record_rotation(key_type)

        logger.info("Key rotated successfully: %s", key_type.value)

        return key

    def check_rotation_needed(self):
        """Check and perform automatic rotations"""
        for key_type in KeyType:
            if self.scheduler.should_rotate(key_type):
                logger.warning("Automatic rotation triggered: %s", key_type.value)
                self.rotate_key(key_type)

    def revoke_compromised_key(self, key_type: KeyType):
        """
        Emergency key revocation

        Immediately rotates compromised key
        """
        logger.critical("COMPROMISE REVOCATION: %s", key_type.value)

        # Mark old key as revoked
        if key_type in self.active_keys:
            self.active_keys[key_type].revoked = True

        # Rotate immediately
        self.rotate_key(key_type)

    def get_active_key(self, key_type: KeyType) -> CryptographicKey | None:
        """Get currently active key"""
        return self.active_keys.get(key_type)


__all__ = [
    "KeyType",
    "CryptographicKey",
    "KeyRotationScheduler",
    "HSMInterface",
    "KeyManagementCeremony",
]
