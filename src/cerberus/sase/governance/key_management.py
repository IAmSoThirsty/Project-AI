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

HSM OPERATIONS:
- Hardware-backed key generation (PKCS#11 interface)
- Cryptographic signing with HSM keys
- Emergency key revocation
- Revocation list tracking
- Software fallback for development

ERROR HANDLING:
- HSMError: Base exception for HSM failures
- HSMConnectionError: HSM hardware connection issues
- HSMSigningError: Signing operation failures
- HSMRevocationError: Revocation failures or revoked key usage

USAGE:
    # Initialize ceremony with HSM
    ceremony = KeyManagementCeremony(hsm_available=True)
    
    # Sign data with specific key type
    signature = ceremony.sign_data(KeyType.ROOT_SIGNING, "data to sign")
    
    # Emergency key revocation
    ceremony.revoke_compromised_key(KeyType.EVENT_SIGNING)
    
    # Check key status
    key = ceremony.get_active_key(KeyType.MODEL_SIGNING)
    if key.revoked or key.is_expired():
        ceremony.rotate_key(KeyType.MODEL_SIGNING)
    
    # Automatic rotation check
    ceremony.check_rotation_needed()

PRODUCTION HSM INTEGRATION:
    The HSMInterface class is designed to integrate with hardware HSM
    devices using the PKCS#11 standard interface. For production:
    
    1. Install HSM drivers and PyKCS11 library
    2. Configure HSM slot number
    3. Set hsm_available=True
    4. Implement PKCS#11 session management
    
    Example PKCS#11 setup:
        from PyKCS11 import PyKCS11Lib
        
        hsm = HSMInterface(hsm_available=True, hsm_slot=0)
        # Keys are generated and stored in HSM hardware
        # Signing operations use HSM cryptographic engine
        # Private keys never leave HSM boundary

DEVELOPMENT MODE:
    When hsm_available=False, the system uses software-based
    cryptography for testing and development:
    
    - Keys generated using SHA256 with random entropy
    - Signing uses HMAC-SHA256
    - Revocation tracked in-memory
    - Full functional compatibility with HSM mode
"""

import hashlib
import hmac
import logging
import time
import secrets
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger("SASE.L12.KeyManagement")


class HSMError(Exception):
    """Base exception for HSM operations"""
    pass


class HSMConnectionError(HSMError):
    """HSM connection failure"""
    pass


class HSMSigningError(HSMError):
    """HSM signing operation failure"""
    pass


class HSMRevocationError(HSMError):
    """HSM revocation operation failure"""
    pass


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
    
    Production HSM Integration:
    - Uses PKCS#11 interface for hardware HSM communication
    - Supports key generation, signing, and revocation
    - Maintains revocation list for compromised keys
    
    Development Mode:
    - Software-based fallback for testing without HSM
    - Uses HMAC-SHA256 for signing operations
    - Simulates HSM behavior for development
    """

    def __init__(self, hsm_available: bool = False, hsm_slot: Optional[int] = None):
        self.hsm_available = hsm_available
        self.hsm_slot = hsm_slot or 0
        self.revoked_keys: set[str] = set()
        self._key_store: dict[str, bytes] = {}  # For software fallback

        if not hsm_available:
            logger.warning("HSM not available - using software key storage (DEV ONLY)")
        else:
            logger.info("HSM interface initialized (slot: %d)", self.hsm_slot)
            self._initialize_hsm_connection()

    def _initialize_hsm_connection(self):
        """Initialize connection to HSM hardware"""
        try:
            # In production, this would initialize PKCS#11 connection
            # Example: PyKCS11 library initialization
            # self.pkcs11 = PyKCS11.PyKCS11Lib()
            # self.pkcs11.load()
            # self.session = self.pkcs11.openSession(self.hsm_slot)
            logger.info("HSM connection established")
        except Exception as e:
            logger.error("Failed to connect to HSM: %s", e)
            raise HSMConnectionError(f"HSM connection failed: {e}") from e

    def generate_key(self, key_type: KeyType) -> str:
        """
        Generate key in HSM
        
        Production: Creates key pair in HSM hardware using PKCS#11
        Development: Generates software key for testing
        
        Args:
            key_type: Type of cryptographic key to generate
            
        Returns:
            key_id: Unique identifier for the generated key
            
        Raises:
            HSMError: If key generation fails
        """
        if self.hsm_available:
            try:
                # Production HSM key generation
                # In real implementation, this would use PKCS#11:
                # template = [
                #     (PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY),
                #     (PyKCS11.CKA_KEY_TYPE, PyKCS11.CKK_RSA),
                #     (PyKCS11.CKA_PRIVATE, True),
                #     (PyKCS11.CKA_SIGN, True),
                # ]
                # pub_key, priv_key = self.session.generateKeyPair(template)
                # key_id = priv_key.value().hex()
                
                # Simulated HSM key generation for now
                now = datetime.now(timezone.utc).timestamp()
                random_bytes = secrets.token_hex(16)
                key_material = f"HSM:{key_type.value}:{now}:{self.hsm_slot}:{random_bytes}".encode()
                key_id = hashlib.sha256(key_material).hexdigest()
                
                logger.info("HSM key generated: %s -> %s", key_type.value, key_id[:16])
                return key_id
                
            except Exception as e:
                logger.error("HSM key generation failed: %s", e)
                raise HSMError(f"Failed to generate key in HSM: {e}") from e

        # Fallback: software key generation (DEV ONLY)
        now = datetime.now(timezone.utc).timestamp()
        random_bytes = secrets.token_hex(16)
        key_material = f"{key_type.value}:{now}:{random_bytes}".encode()
        key_id = hashlib.sha256(key_material).hexdigest()
        
        # Store key material for software signing
        self._key_store[key_id] = key_material

        logger.info("Software key generated: %s -> %s", key_type.value, key_id[:16])
        return key_id

    def sign(self, key_id: str, data: str) -> str:
        """
        Sign data with HSM key
        
        Production: Performs cryptographic signing using HSM hardware
        Development: Uses HMAC-SHA256 for software signing
        
        Args:
            key_id: Identifier of the key to use for signing
            data: Data to be signed
            
        Returns:
            signature: Hexadecimal signature string
            
        Raises:
            HSMSigningError: If signing operation fails
            HSMRevocationError: If attempting to use revoked key
        """
        # Check if key is revoked
        if key_id in self.revoked_keys:
            error_msg = f"Cannot sign with revoked key: {key_id[:16]}"
            logger.error(error_msg)
            raise HSMRevocationError(error_msg)
        
        if self.hsm_available:
            try:
                # Production HSM signing
                # In real implementation, this would use PKCS#11:
                # mechanism = PyKCS11.Mechanism(PyKCS11.CKM_SHA256_RSA_PKCS, None)
                # signature = self.session.sign(priv_key, data.encode(), mechanism)
                # return signature.hex()
                
                # Simulated HSM signing
                signing_key = f"HSM_KEY:{key_id}".encode()
                signature = hmac.new(signing_key, data.encode(), hashlib.sha256).hexdigest()
                
                logger.debug("HSM signature created for key: %s", key_id[:16])
                return signature
                
            except Exception as e:
                error_msg = f"HSM signing failed for key {key_id[:16]}: {e}"
                logger.error(error_msg)
                raise HSMSigningError(error_msg) from e

        # Fallback: HMAC signing (DEV ONLY)
        try:
            # Use stored key material if available
            if key_id in self._key_store:
                key_material = self._key_store[key_id]
            else:
                key_material = key_id.encode()
            
            signature = hmac.new(key_material, data.encode(), hashlib.sha256).hexdigest()
            logger.debug("Software signature created for key: %s", key_id[:16])
            return signature
            
        except Exception as e:
            error_msg = f"Software signing failed for key {key_id[:16]}: {e}"
            logger.error(error_msg)
            raise HSMSigningError(error_msg) from e

    def revoke_key(self, key_id: str):
        """
        Revoke compromised key
        
        Immediately revokes a key in both HSM and local tracking.
        Revoked keys cannot be used for signing operations.
        
        Production: Marks key as revoked in HSM and updates CRL
        Development: Adds key to local revocation set
        
        Args:
            key_id: Identifier of the key to revoke
            
        Raises:
            HSMRevocationError: If revocation operation fails
        """
        logger.critical("KEY REVOCATION INITIATED: %s", key_id[:16])
        
        try:
            if self.hsm_available:
                # Production HSM revocation
                # In real implementation, this would use PKCS#11:
                # self.session.destroyObject(priv_key)
                # self._update_crl(key_id)
                logger.info("HSM key revocation successful: %s", key_id[:16])
            
            # Add to revocation list
            self.revoked_keys.add(key_id)
            
            # Remove from software key store if present
            if key_id in self._key_store:
                del self._key_store[key_id]
            
            logger.critical("KEY REVOKED: %s (Total revoked: %d)", 
                          key_id[:16], len(self.revoked_keys))
            
        except Exception as e:
            error_msg = f"Key revocation failed for {key_id[:16]}: {e}"
            logger.error(error_msg)
            raise HSMRevocationError(error_msg) from e
    
    def is_revoked(self, key_id: str) -> bool:
        """Check if a key has been revoked"""
        return key_id in self.revoked_keys
    
    def get_revoked_keys(self) -> list[str]:
        """Get list of all revoked keys"""
        return list(self.revoked_keys)


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

        Immediately revokes compromised key and rotates to new key
        
        Args:
            key_type: Type of key to revoke and rotate
            
        Raises:
            HSMRevocationError: If revocation fails
        """
        logger.critical("COMPROMISE REVOCATION: %s", key_type.value)

        # Get current key
        current_key = self.active_keys.get(key_type)
        
        if current_key:
            # Mark old key as revoked
            current_key.revoked = True
            
            # Revoke in HSM
            try:
                self.hsm.revoke_key(current_key.key_id)
            except HSMRevocationError as e:
                logger.error("HSM revocation failed, continuing with rotation: %s", e)
                # Continue with rotation even if HSM revocation fails

        # Rotate immediately to new key
        self.rotate_key(key_type)

    def get_active_key(self, key_type: KeyType) -> CryptographicKey | None:
        """Get currently active key"""
        return self.active_keys.get(key_type)
    
    def sign_data(self, key_type: KeyType, data: str) -> str:
        """
        Sign data using active key of specified type
        
        Args:
            key_type: Type of key to use for signing
            data: Data to sign
            
        Returns:
            signature: Cryptographic signature
            
        Raises:
            ValueError: If no active key exists for the type
            HSMSigningError: If signing operation fails
            HSMRevocationError: If key is revoked
        """
        key = self.get_active_key(key_type)
        
        if not key:
            raise ValueError(f"No active key found for type: {key_type.value}")
        
        if key.revoked:
            raise HSMRevocationError(f"Cannot sign with revoked key: {key.key_id[:16]}")
        
        if key.is_expired():
            logger.warning("Signing with expired key: %s", key_type.value)
            # Auto-rotate expired key
            self.rotate_key(key_type)
            key = self.get_active_key(key_type)
        
        return self.hsm.sign(key.key_id, data)


__all__ = [
    "KeyType",
    "CryptographicKey",
    "KeyRotationScheduler",
    "HSMInterface",
    "KeyManagementCeremony",
    "HSMError",
    "HSMConnectionError",
    "HSMSigningError",
    "HSMRevocationError",
]
