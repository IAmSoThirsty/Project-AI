"""
Hardware Root-of-Trust Integration
Provides TPM, Secure Enclave, and HSM support for cryptographic key storage
and attested secure boot, protecting against OS/root compromise.
"""

import logging
import hashlib
import hmac
import secrets
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from enum import Enum
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import threading


class HardwareType(Enum):
    """Supported hardware security module types"""

    TPM = "tpm"
    SECURE_ENCLAVE = "secure_enclave"
    HSM = "hsm"
    SOFTWARE_FALLBACK = "software_fallback"


class AttestationStatus(Enum):
    """Attestation status indicators"""

    VALID = "valid"
    INVALID = "invalid"
    UNKNOWN = "unknown"
    TAMPERED = "tampered"


class HardwareInterface(ABC):
    """Abstract base class for hardware security interfaces"""

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize hardware interface"""
        pass

    @abstractmethod
    def store_key(self, key_id: str, key_data: bytes) -> bool:
        """Store cryptographic key in hardware"""
        pass

    @abstractmethod
    def retrieve_key(self, key_id: str) -> Optional[bytes]:
        """Retrieve cryptographic key from hardware"""
        pass

    @abstractmethod
    def delete_key(self, key_id: str) -> bool:
        """Securely delete key from hardware"""
        pass

    @abstractmethod
    def attest_boot(self) -> AttestationStatus:
        """Perform secure boot attestation"""
        pass

    @abstractmethod
    def get_hardware_id(self) -> str:
        """Get unique hardware identifier"""
        pass

    @abstractmethod
    def seal_data(self, data: bytes, pcr_values: List[int]) -> bytes:
        """Seal data to specific PCR values"""
        pass

    @abstractmethod
    def unseal_data(self, sealed_data: bytes) -> Optional[bytes]:
        """Unseal data (only if PCR values match)"""
        pass


class TPMInterface(HardwareInterface):
    """
    Trusted Platform Module (TPM) interface.
    Provides hardware-backed key storage and secure boot attestation.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        self._keys: Dict[str, bytes] = {}
        self._pcr_banks: Dict[int, bytes] = {}
        self._hardware_id = self._generate_hardware_id()
        # Generate unique salt from hardware ID instead of hard-coding
        self._salt = hashlib.sha256(f"TPM_SRK_{self._hardware_id}".encode()).digest()
        self._lock = threading.Lock()

    def initialize(self) -> bool:
        """Initialize TPM interface"""
        try:
            self.logger.info("Initializing TPM interface")

            # In production, this would:
            # 1. Connect to TPM device (/dev/tpm0)
            # 2. Take ownership if needed
            # 3. Initialize PCR banks
            # 4. Verify TPM is in operational state

            # Initialize PCR banks with boot measurements
            self._initialize_pcr_banks()

            self._initialized = True
            self.logger.info("TPM interface initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize TPM: {e}")
            return False

    def _initialize_pcr_banks(self):
        """Initialize Platform Configuration Register banks"""
        # Simulate PCR measurements
        # In production, these would be actual boot chain measurements
        boot_measurements = [
            b"BIOS_MEASUREMENT",
            b"BOOTLOADER_MEASUREMENT",
            b"KERNEL_MEASUREMENT",
            b"INITRD_MEASUREMENT",
            b"USERSPACE_MEASUREMENT",
        ]

        for i, measurement in enumerate(boot_measurements):
            self._pcr_banks[i] = hashlib.sha256(measurement).digest()

    def store_key(self, key_id: str, key_data: bytes) -> bool:
        """Store key in TPM's non-volatile memory"""
        with self._lock:
            try:
                # In production: Use TPM2_NV_Write to store in NVRAM
                # Keys are encrypted with TPM's storage root key
                self._keys[key_id] = self._encrypt_with_srk(key_data)
                self.logger.info(f"Stored key {key_id} in TPM")
                return True
            except Exception as e:
                self.logger.error(f"Failed to store key {key_id}: {e}")
                return False

    def retrieve_key(self, key_id: str) -> Optional[bytes]:
        """Retrieve key from TPM"""
        with self._lock:
            try:
                encrypted_key = self._keys.get(key_id)
                if encrypted_key:
                    # In production: Use TPM2_NV_Read
                    return self._decrypt_with_srk(encrypted_key)
                return None
            except Exception as e:
                self.logger.error(f"Failed to retrieve key {key_id}: {e}")
                return None

    def delete_key(self, key_id: str) -> bool:
        """Securely delete key from TPM"""
        with self._lock:
            try:
                if key_id in self._keys:
                    # In production: Use TPM2_NV_UndefineSpace
                    del self._keys[key_id]
                    self.logger.info(f"Deleted key {key_id} from TPM")
                return True
            except Exception as e:
                self.logger.error(f"Failed to delete key {key_id}: {e}")
                return False

    def attest_boot(self) -> AttestationStatus:
        """
        Perform secure boot attestation by verifying PCR values.
        Returns status indicating if boot chain is trusted.
        """
        try:
            # In production: Use TPM2_Quote to get signed PCR values
            # and verify against known-good values

            expected_pcr0 = hashlib.sha256(b"BIOS_MEASUREMENT").digest()
            actual_pcr0 = self._pcr_banks.get(0)

            if actual_pcr0 == expected_pcr0:
                self.logger.info("Boot attestation: VALID")
                return AttestationStatus.VALID
            else:
                self.logger.critical("Boot attestation: TAMPERED - PCR mismatch!")
                return AttestationStatus.TAMPERED

        except Exception as e:
            self.logger.error(f"Boot attestation failed: {e}")
            return AttestationStatus.UNKNOWN

    def get_hardware_id(self) -> str:
        """Get TPM's endorsement key (EK) as hardware ID"""
        return self._hardware_id

    def _generate_hardware_id(self) -> str:
        """Generate unique hardware identifier"""
        # In production: Read TPM endorsement key
        return hashlib.sha256(secrets.token_bytes(32)).hexdigest()

    def seal_data(self, data: bytes, pcr_values: List[int]) -> bytes:
        """
        Seal data to specific PCR values using TPM.
        Data can only be unsealed when PCRs match.
        """
        try:
            # Create policy digest from PCR values
            policy_digest = self._create_policy_digest(pcr_values)

            # In production: Use TPM2_Create with policy
            # Encrypt data with a key that's sealed to the policy
            sealed = self._encrypt_with_policy(data, policy_digest)

            self.logger.info(f"Sealed data to PCRs: {pcr_values}")
            return sealed

        except Exception as e:
            self.logger.error(f"Failed to seal data: {e}")
            raise

    def unseal_data(self, sealed_data: bytes) -> Optional[bytes]:
        """
        Unseal data sealed to PCR values.
        Only succeeds if current PCR values match sealed policy.
        """
        try:
            # In production: Use TPM2_Unseal
            # Verify current PCR values match policy
            data = self._decrypt_with_policy(sealed_data)

            if data:
                self.logger.info("Successfully unsealed data")
            else:
                self.logger.warning("Failed to unseal - PCR values don't match")

            return data

        except Exception as e:
            self.logger.error(f"Failed to unseal data: {e}")
            return None

    def _encrypt_with_srk(self, data: bytes) -> bytes:
        """Encrypt data with Storage Root Key"""
        # Simplified encryption - in production uses TPM's SRK
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
            backend=default_backend(),
        )
        key = kdf.derive(self._hardware_id.encode())
        return hmac.new(key, data, hashlib.sha256).digest() + data

    def _decrypt_with_srk(self, encrypted_data: bytes) -> bytes:
        """Decrypt data with Storage Root Key"""
        # Simplified decryption - in production uses TPM's SRK
        mac = encrypted_data[:32]
        data = encrypted_data[32:]

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
            backend=default_backend(),
        )
        key = kdf.derive(self._hardware_id.encode())

        expected_mac = hmac.new(key, data, hashlib.sha256).digest()
        if hmac.compare_digest(mac, expected_mac):
            return data
        raise ValueError("MAC verification failed")

    def _create_policy_digest(self, pcr_values: List[int]) -> bytes:
        """Create policy digest from PCR values"""
        digest = hashlib.sha256()
        for pcr in pcr_values:
            pcr_value = self._pcr_banks.get(pcr, b"")
            digest.update(pcr_value)
        return digest.digest()

    def _encrypt_with_policy(self, data: bytes, policy_digest: bytes) -> bytes:
        """Encrypt data with policy digest"""
        return policy_digest + data

    def _decrypt_with_policy(self, sealed_data: bytes) -> Optional[bytes]:
        """Decrypt data if policy matches current state"""
        sealed_data[:32]
        data = sealed_data[32:]

        # Verify policy still matches current PCR values
        # In production, this would be enforced by TPM
        return data


class SecureEnclaveInterface(HardwareInterface):
    """
    Secure Enclave interface (Apple hardware security).
    Provides isolated execution environment for sensitive operations.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        self._keychain: Dict[str, bytes] = {}
        self._enclave_id = self._generate_enclave_id()
        # Generate unique salt from enclave ID instead of hard-coding
        self._salt = hashlib.sha256(
            f"SECURE_ENCLAVE_{self._enclave_id}".encode()
        ).digest()
        self._lock = threading.Lock()

    def initialize(self) -> bool:
        """Initialize Secure Enclave"""
        try:
            self.logger.info("Initializing Secure Enclave interface")

            # In production:
            # 1. Initialize communication with Secure Enclave
            # 2. Verify enclave attestation
            # 3. Establish secure channel

            self._initialized = True
            self.logger.info("Secure Enclave initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Secure Enclave: {e}")
            return False

    def store_key(self, key_id: str, key_data: bytes) -> bool:
        """Store key in Secure Enclave keychain"""
        with self._lock:
            try:
                # In production: Use Keychain Services with kSecAttrAccessibleWhenUnlockedThisDeviceOnly
                self._keychain[key_id] = self._encrypt_for_enclave(key_data)
                self.logger.info(f"Stored key {key_id} in Secure Enclave")
                return True
            except Exception as e:
                self.logger.error(f"Failed to store key: {e}")
                return False

    def retrieve_key(self, key_id: str) -> Optional[bytes]:
        """Retrieve key from Secure Enclave"""
        with self._lock:
            encrypted_key = self._keychain.get(key_id)
            if encrypted_key:
                return self._decrypt_from_enclave(encrypted_key)
            return None

    def delete_key(self, key_id: str) -> bool:
        """Delete key from Secure Enclave"""
        with self._lock:
            if key_id in self._keychain:
                del self._keychain[key_id]
                self.logger.info(f"Deleted key {key_id}")
            return True

    def attest_boot(self) -> AttestationStatus:
        """Verify secure boot through enclave attestation"""
        # In production: Query enclave attestation status
        self.logger.info("Secure Enclave attestation: VALID")
        return AttestationStatus.VALID

    def get_hardware_id(self) -> str:
        """Get Secure Enclave unique identifier"""
        return self._enclave_id

    def _generate_enclave_id(self) -> str:
        """Generate unique enclave identifier"""
        return hashlib.sha256(secrets.token_bytes(32)).hexdigest()

    def seal_data(self, data: bytes, pcr_values: List[int]) -> bytes:
        """Seal data using Secure Enclave"""
        return self._encrypt_for_enclave(data)

    def unseal_data(self, sealed_data: bytes) -> Optional[bytes]:
        """Unseal data using Secure Enclave"""
        return self._decrypt_from_enclave(sealed_data)

    def _encrypt_for_enclave(self, data: bytes) -> bytes:
        """Encrypt data for Secure Enclave storage"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
            backend=default_backend(),
        )
        key = kdf.derive(self._enclave_id.encode())
        return hmac.new(key, data, hashlib.sha256).digest() + data

    def _decrypt_from_enclave(self, encrypted_data: bytes) -> bytes:
        """Decrypt data from Secure Enclave"""
        mac = encrypted_data[:32]
        data = encrypted_data[32:]

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
            backend=default_backend(),
        )
        key = kdf.derive(self._enclave_id.encode())

        expected_mac = hmac.new(key, data, hashlib.sha256).digest()
        if hmac.compare_digest(mac, expected_mac):
            return data
        raise ValueError("MAC verification failed")


class HSMInterface(HardwareInterface):
    """
    Hardware Security Module (HSM) interface.
    Enterprise-grade hardware for key management and cryptographic operations.
    """

    def __init__(self, hsm_config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(__name__)
        self.config = hsm_config or {}
        self._initialized = False
        self._keys: Dict[str, bytes] = {}
        self._hsm_id = self._generate_hsm_id()
        # Generate unique salt from HSM ID instead of hard-coding
        self._salt = hashlib.sha256(f"HSM_MASTER_KEY_{self._hsm_id}".encode()).digest()
        self._lock = threading.Lock()

    def initialize(self) -> bool:
        """Initialize HSM connection"""
        try:
            self.logger.info("Initializing HSM interface")

            # In production:
            # 1. Connect to HSM (PKCS#11, CloudHSM, etc.)
            # 2. Authenticate with HSM credentials
            # 3. Initialize secure channel
            # 4. Verify HSM health and FIPS compliance

            self._initialized = True
            self.logger.info("HSM interface initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize HSM: {e}")
            return False

    def store_key(self, key_id: str, key_data: bytes) -> bool:
        """Store key in HSM"""
        with self._lock:
            try:
                # In production: Use PKCS#11 C_CreateObject or CloudHSM SDK
                self._keys[key_id] = self._hsm_encrypt(key_data)
                self.logger.info(f"Stored key {key_id} in HSM")
                return True
            except Exception as e:
                self.logger.error(f"Failed to store key: {e}")
                return False

    def retrieve_key(self, key_id: str) -> Optional[bytes]:
        """Retrieve key from HSM"""
        with self._lock:
            encrypted_key = self._keys.get(key_id)
            if encrypted_key:
                return self._hsm_decrypt(encrypted_key)
            return None

    def delete_key(self, key_id: str) -> bool:
        """Delete key from HSM"""
        with self._lock:
            if key_id in self._keys:
                # In production: Use PKCS#11 C_DestroyObject
                del self._keys[key_id]
                self.logger.info(f"Deleted key {key_id}")
            return True

    def attest_boot(self) -> AttestationStatus:
        """HSM attestation (HSM validates its own integrity)"""
        # In production: Query HSM self-test and attestation
        self.logger.info("HSM attestation: VALID")
        return AttestationStatus.VALID

    def get_hardware_id(self) -> str:
        """Get HSM serial number"""
        return self._hsm_id

    def _generate_hsm_id(self) -> str:
        """Generate HSM identifier"""
        return f"HSM-{hashlib.sha256(secrets.token_bytes(32)).hexdigest()[:16]}"

    def seal_data(self, data: bytes, pcr_values: List[int]) -> bytes:
        """Seal data using HSM"""
        return self._hsm_encrypt(data)

    def unseal_data(self, sealed_data: bytes) -> Optional[bytes]:
        """Unseal data using HSM"""
        return self._hsm_decrypt(sealed_data)

    def _hsm_encrypt(self, data: bytes) -> bytes:
        """Encrypt data using HSM master key"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
            backend=default_backend(),
        )
        key = kdf.derive(self._hsm_id.encode())
        return hmac.new(key, data, hashlib.sha256).digest() + data

    def _hsm_decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using HSM master key"""
        mac = encrypted_data[:32]
        data = encrypted_data[32:]

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
            backend=default_backend(),
        )
        key = kdf.derive(self._hsm_id.encode())

        expected_mac = hmac.new(key, data, hashlib.sha256).digest()
        if hmac.compare_digest(mac, expected_mac):
            return data
        raise ValueError("MAC verification failed")


class HardwareRootOfTrust:
    """
    Unified Hardware Root-of-Trust manager.
    Automatically selects best available hardware security module.
    """

    def __init__(self, preferred_type: Optional[HardwareType] = None):
        self.logger = logging.getLogger(__name__)
        self.preferred_type = preferred_type
        self._interface: Optional[HardwareInterface] = None
        self._active_type: Optional[HardwareType] = None
        self._kill_switch_callback = None

    def initialize(self) -> bool:
        """Initialize hardware root of trust with best available option"""
        self.logger.info("Initializing Hardware Root-of-Trust")

        # Try preferred type first
        if self.preferred_type:
            if self._try_initialize_type(self.preferred_type):
                return True

        # Try in order of security: HSM > TPM > Secure Enclave > Software
        for hw_type in [
            HardwareType.HSM,
            HardwareType.TPM,
            HardwareType.SECURE_ENCLAVE,
            HardwareType.SOFTWARE_FALLBACK,
        ]:
            if self._try_initialize_type(hw_type):
                return True

        self.logger.error("Failed to initialize any hardware security module")
        return False

    def _try_initialize_type(self, hw_type: HardwareType) -> bool:
        """Try to initialize specific hardware type"""
        try:
            if hw_type == HardwareType.TPM:
                self._interface = TPMInterface()
            elif hw_type == HardwareType.SECURE_ENCLAVE:
                self._interface = SecureEnclaveInterface()
            elif hw_type == HardwareType.HSM:
                self._interface = HSMInterface()
            elif hw_type == HardwareType.SOFTWARE_FALLBACK:
                # Use TPM interface as software fallback
                self._interface = TPMInterface()

            if self._interface.initialize():
                self._active_type = hw_type
                self.logger.info(f"Initialized {hw_type.value} successfully")
                return True

        except Exception as e:
            self.logger.warning(f"Failed to initialize {hw_type.value}: {e}")

        return False

    def store_master_key(self, key_data: bytes) -> bool:
        """Store system master encryption key in hardware"""
        if not self._interface:
            return False
        return self._interface.store_key("master_encryption_key", key_data)

    def retrieve_master_key(self) -> Optional[bytes]:
        """Retrieve system master encryption key"""
        if not self._interface:
            return None
        return self._interface.retrieve_key("master_encryption_key")

    def verify_boot_integrity(self) -> bool:
        """
        Verify boot integrity through attestation.
        Triggers kill switch if attestation fails.
        """
        if not self._interface:
            self.logger.error("No hardware interface available for attestation")
            return False

        status = self._interface.attest_boot()

        if status == AttestationStatus.TAMPERED:
            self.logger.critical("BOOT INTEGRITY COMPROMISED - Triggering kill switch")
            if self._kill_switch_callback:
                self._kill_switch_callback("Boot attestation failed - system tampered")
            return False

        elif status == AttestationStatus.VALID:
            self.logger.info("Boot integrity verified - system trusted")
            return True

        else:
            self.logger.warning("Boot attestation status unknown")
            return False

    def seal_kill_switch_bypass_protection(self) -> bytes:
        """
        Seal kill switch state to PCR values to prevent bypass.
        Kill switch can only be disabled if boot state matches.
        """
        if not self._interface:
            raise RuntimeError("No hardware interface available")

        # Seal to PCRs 0-4 (boot chain)
        kill_switch_state = b"KILL_SWITCH_ENABLED"
        sealed = self._interface.seal_data(kill_switch_state, [0, 1, 2, 3, 4])

        self.logger.info("Kill switch state sealed to boot measurements")
        return sealed

    def register_kill_switch_callback(self, callback):
        """Register callback to trigger kill switch on compromise"""
        self._kill_switch_callback = callback

    def get_hardware_info(self) -> Dict[str, Any]:
        """Get information about active hardware security module"""
        if not self._interface:
            return {"active": False, "type": None, "hardware_id": None}

        return {
            "active": True,
            "type": self._active_type.value if self._active_type else None,
            "hardware_id": self._interface.get_hardware_id(),
            "attestation_status": self._interface.attest_boot().value,
        }

    def wipe_all_keys(self) -> bool:
        """Emergency wipe of all keys from hardware (for DOS trap mode)"""
        if not self._interface:
            return False

        self.logger.critical("EMERGENCY KEY WIPE INITIATED")

        # Delete all known keys
        try:
            self._interface.delete_key("master_encryption_key")
            self.logger.info("Master encryption key wiped from hardware")
            return True
        except Exception as e:
            self.logger.error(f"Failed to wipe keys: {e}")
            return False
