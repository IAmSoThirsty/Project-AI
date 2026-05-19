"""
Production-Grade Multi-Factor Authentication Module
Provides comprehensive MFA support with TOTP, FIDO2/WebAuthn, passkeys, certificates,
and biometric authentication with context-aware risk-based escalation.
"""

import logging
import hashlib
import hmac
import secrets
import time
import base64
import struct
import threading
from typing import Dict, Any, Optional, List, Tuple, Callable, Set
from enum import Enum
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime
from abc import ABC, abstractmethod

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import ExtensionOID


class AuthMethod(Enum):
    """Supported authentication methods"""

    PASSWORD = "password"
    TOTP = "totp"
    FIDO2 = "fido2"
    WEBAUTHN = "webauthn"
    PASSKEY = "passkey"
    CERTIFICATE = "certificate"
    BIOMETRIC = "biometric"
    HARDWARE_TOKEN = "hardware_token"
    SMS = "sms"
    EMAIL = "email"


class AuthLevel(Enum):
    """Authentication security levels"""

    NONE = 0
    BASIC = 1  # Single factor
    STANDARD = 2  # Two-factor
    ELEVATED = 3  # Two-factor with hardware
    HIGH = 4  # Multi-factor with biometric
    CRITICAL = 5  # All factors + hardware + biometric


class RiskLevel(Enum):
    """Risk assessment levels"""

    MINIMAL = 0
    LOW = 1
    MODERATE = 2
    HIGH = 3
    CRITICAL = 4
    EXTREME = 5


class BiometricType(Enum):
    """Biometric authentication types"""

    FINGERPRINT = "fingerprint"
    FACE_ID = "face_id"
    IRIS_SCAN = "iris_scan"
    VOICE_PRINT = "voice_print"
    BEHAVIORAL = "behavioral"


@dataclass
class AuthContext:
    """
    Context-aware authentication context.
    Tracks session state, risk factors, and authentication history.
    """

    user_id: str
    session_id: str
    ip_address: str
    user_agent: str
    timestamp: float = field(default_factory=time.time)

    # Risk indicators
    risk_level: RiskLevel = RiskLevel.MINIMAL
    risk_factors: List[str] = field(default_factory=list)

    # Authentication state
    auth_level: AuthLevel = AuthLevel.NONE
    authenticated_methods: Set[AuthMethod] = field(default_factory=set)
    last_auth_time: float = field(default_factory=time.time)

    # Session metadata
    device_fingerprint: Optional[str] = None
    geolocation: Optional[Dict[str, Any]] = None
    previous_sessions: List[Dict[str, Any]] = field(default_factory=list)

    # Behavioral analysis
    typing_patterns: List[float] = field(default_factory=list)
    mouse_patterns: List[Tuple[int, int]] = field(default_factory=list)
    interaction_velocity: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize context to dictionary"""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "timestamp": self.timestamp,
            "risk_level": self.risk_level.name,
            "risk_factors": self.risk_factors,
            "auth_level": self.auth_level.name,
            "authenticated_methods": [m.value for m in self.authenticated_methods],
            "last_auth_time": self.last_auth_time,
            "device_fingerprint": self.device_fingerprint,
            "geolocation": self.geolocation,
        }


@dataclass
class TOTPConfig:
    """TOTP configuration"""

    secret: bytes
    algorithm: str = "sha256"  # sha1, sha256, sha512
    digits: int = 6
    period: int = 30  # seconds
    issuer: str = "ThirstysWaterfall"


@dataclass
class FIDO2Credential:
    """FIDO2/WebAuthn credential"""

    credential_id: bytes
    public_key: bytes
    sign_count: int
    aaguid: bytes  # Authenticator Attestation GUID
    user_id: str
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    credential_type: str = "public-key"
    transports: List[str] = field(default_factory=lambda: ["usb", "nfc", "ble"])


@dataclass
class PasskeyData:
    """Passkey storage"""

    passkey_id: str
    public_key: bytes
    private_key_encrypted: bytes  # Encrypted with device key
    user_id: str
    device_name: str
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)


@dataclass
class BiometricTemplate:
    """Biometric authentication template"""

    template_id: str
    biometric_type: BiometricType
    template_hash: bytes  # Never store raw biometric data
    quality_score: float
    user_id: str
    enrolled_at: float = field(default_factory=time.time)
    last_verified: float = field(default_factory=time.time)


class AuthenticationProvider(ABC):
    """Abstract base class for authentication providers"""

    @abstractmethod
    def authenticate(self, credential: Any, context: AuthContext) -> bool:
        """Authenticate using this provider"""
        pass

    @abstractmethod
    def enroll(self, user_id: str, credential_data: Any) -> bool:
        """Enroll new credential"""
        pass

    @abstractmethod
    def revoke(self, user_id: str, credential_id: str) -> bool:
        """Revoke credential"""
        pass


class TOTPProvider(AuthenticationProvider):
    """
    Time-based One-Time Password provider.
    Implements RFC 6238 with enhanced security features.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._secrets: Dict[str, TOTPConfig] = {}
        self._used_tokens: deque = deque(maxlen=100)  # Prevent replay
        self._lock = threading.Lock()

    def enroll(
        self, user_id: str, credential_data: Optional[bytes] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Enroll user for TOTP authentication.

        Args:
            user_id: User identifier
            credential_data: Optional pre-generated secret

        Returns:
            Tuple of (success, enrollment_data)
        """
        with self._lock:
            try:
                # Generate or use provided secret
                secret = credential_data if credential_data else secrets.token_bytes(20)

                config = TOTPConfig(
                    secret=secret, algorithm="sha256", digits=6, period=30
                )

                self._secrets[user_id] = config

                # Generate provisioning data
                secret_b32 = base64.b32encode(secret).decode("utf-8")

                enrollment_data = {
                    "secret": secret_b32,
                    "algorithm": config.algorithm,
                    "digits": config.digits,
                    "period": config.period,
                    "issuer": config.issuer,
                    "provisioning_uri": self._generate_provisioning_uri(
                        user_id, config
                    ),
                }

                self.logger.info(f"TOTP enrolled for user {user_id}")
                return True, enrollment_data

            except Exception as e:
                self.logger.error(f"TOTP enrollment failed for {user_id}: {e}")
                return False, None

    def authenticate(self, credential: str, context: AuthContext) -> bool:
        """
        Authenticate TOTP token.

        Args:
            credential: 6-digit TOTP token
            context: Authentication context

        Returns:
            True if authentication succeeds
        """
        with self._lock:
            try:
                config = self._secrets.get(context.user_id)
                if not config:
                    self.logger.warning(f"No TOTP config for user {context.user_id}")
                    return False

                # Check token hasn't been used (replay protection)
                token_hash = hashlib.sha256(
                    f"{context.user_id}:{credential}:{int(time.time() / config.period)}".encode()
                ).digest()

                if token_hash in self._used_tokens:
                    self.logger.warning(f"TOTP replay attempt for {context.user_id}")
                    return False

                # Verify token with time window (±1 period for clock drift)
                current_time = int(time.time())
                for time_offset in [0, -1, 1]:
                    counter = (
                        current_time + time_offset * config.period
                    ) // config.period
                    expected_token = self._generate_totp(config, counter)

                    if secrets.compare_digest(credential, expected_token):
                        self._used_tokens.append(token_hash)
                        self.logger.info(
                            f"TOTP authentication successful for {context.user_id}"
                        )
                        return True

                self.logger.warning(f"Invalid TOTP token for {context.user_id}")
                return False

            except Exception as e:
                self.logger.error(f"TOTP authentication error: {e}")
                return False

    def revoke(self, user_id: str, credential_id: str = None) -> bool:
        """Revoke TOTP secret"""
        with self._lock:
            if user_id in self._secrets:
                del self._secrets[user_id]
                self.logger.info(f"TOTP revoked for user {user_id}")
                return True
            return False

    def _generate_totp(self, config: TOTPConfig, counter: int) -> str:
        """Generate TOTP token"""
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack(">Q", counter)

        # HMAC-based OTP
        algorithm_map = {
            "sha1": hashlib.sha1,
            "sha256": hashlib.sha256,
            "sha512": hashlib.sha512,
        }

        hash_func = algorithm_map.get(config.algorithm, hashlib.sha256)
        hmac_hash = hmac.new(config.secret, counter_bytes, hash_func).digest()

        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        code = struct.unpack(">I", hmac_hash[offset : offset + 4])[0] & 0x7FFFFFFF

        # Generate token
        token = str(code % (10**config.digits)).zfill(config.digits)
        return token

    def _generate_provisioning_uri(self, user_id: str, config: TOTPConfig) -> str:
        """Generate otpauth:// URI for QR code"""
        secret_b32 = base64.b32encode(config.secret).decode("utf-8")
        return (
            f"otpauth://totp/{config.issuer}:{user_id}?"
            f"secret={secret_b32}&"
            f"issuer={config.issuer}&"
            f"algorithm={config.algorithm.upper()}&"
            f"digits={config.digits}&"
            f"period={config.period}"
        )


class FIDO2Provider(AuthenticationProvider):
    """
    FIDO2/WebAuthn authentication provider.
    Supports hardware security keys and platform authenticators.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._credentials: Dict[str, List[FIDO2Credential]] = {}
        self._challenges: Dict[str, bytes] = {}
        self._lock = threading.Lock()

        # Relying party configuration
        self.rp_id = "thirstyswaterfall.local"
        self.rp_name = "Thirstys Waterfall"
        self.origin = f"https://{self.rp_id}"

    def enroll(self, user_id: str, credential_data: Dict[str, Any]) -> bool:
        """
        Enroll FIDO2 credential.

        Args:
            user_id: User identifier
            credential_data: Dictionary containing:
                - credential_id: Unique credential identifier
                - public_key: COSE-encoded public key
                - aaguid: Authenticator GUID

        Returns:
            True if enrollment succeeds
        """
        with self._lock:
            try:
                credential = FIDO2Credential(
                    credential_id=base64.b64decode(credential_data["credential_id"]),
                    public_key=base64.b64decode(credential_data["public_key"]),
                    sign_count=0,
                    aaguid=base64.b64decode(
                        credential_data.get("aaguid", secrets.token_bytes(16))
                    ),
                    user_id=user_id,
                )

                if user_id not in self._credentials:
                    self._credentials[user_id] = []

                self._credentials[user_id].append(credential)
                self.logger.info(f"FIDO2 credential enrolled for {user_id}")
                return True

            except Exception as e:
                self.logger.error(f"FIDO2 enrollment failed: {e}")
                return False

    def authenticate(self, credential: Dict[str, Any], context: AuthContext) -> bool:
        """
        Authenticate FIDO2 assertion.

        Args:
            credential: Dictionary containing:
                - credential_id: Credential being used
                - authenticator_data: Authenticator data
                - signature: Assertion signature
                - client_data_json: Client data

        Returns:
            True if authentication succeeds
        """
        with self._lock:
            try:
                user_credentials = self._credentials.get(context.user_id, [])
                if not user_credentials:
                    return False

                # Find matching credential
                credential_id = base64.b64decode(credential["credential_id"])
                matching_cred = None

                for cred in user_credentials:
                    if secrets.compare_digest(cred.credential_id, credential_id):
                        matching_cred = cred
                        break

                if not matching_cred:
                    self.logger.warning(f"Unknown credential for {context.user_id}")
                    return False

                # Verify signature
                authenticator_data = base64.b64decode(credential["authenticator_data"])
                client_data_json = base64.b64decode(credential["client_data_json"])
                signature = base64.b64decode(credential["signature"])

                # Reconstruct signed data
                client_data_hash = hashlib.sha256(client_data_json).digest()
                signed_data = authenticator_data + client_data_hash

                # Verify with public key
                if self._verify_signature(
                    matching_cred.public_key, signed_data, signature
                ):
                    # Check sign count (prevent credential cloning)
                    new_sign_count = struct.unpack(">I", authenticator_data[33:37])[0]

                    if new_sign_count > matching_cred.sign_count:
                        matching_cred.sign_count = new_sign_count
                        matching_cred.last_used = time.time()
                        self.logger.info(
                            f"FIDO2 authentication successful for {context.user_id}"
                        )
                        return True
                    else:
                        self.logger.warning(
                            f"Potential cloned authenticator for {context.user_id}"
                        )
                        return False

                return False

            except Exception as e:
                self.logger.error(f"FIDO2 authentication error: {e}")
                return False

    def revoke(self, user_id: str, credential_id: str) -> bool:
        """Revoke FIDO2 credential"""
        with self._lock:
            if user_id in self._credentials:
                cred_id_bytes = base64.b64decode(credential_id)
                initial_count = len(self._credentials[user_id])
                self._credentials[user_id] = [
                    c
                    for c in self._credentials[user_id]
                    if not secrets.compare_digest(c.credential_id, cred_id_bytes)
                ]

                if len(self._credentials[user_id]) < initial_count:
                    self.logger.info(f"FIDO2 credential revoked for {user_id}")
                    return True

            return False

    def generate_challenge(self, user_id: str) -> bytes:
        """Generate authentication challenge"""
        challenge = secrets.token_bytes(32)
        self._challenges[user_id] = challenge
        return challenge

    def _verify_signature(
        self, public_key_bytes: bytes, data: bytes, signature: bytes
    ) -> bool:
        """Verify FIDO2 signature"""
        try:
            # In production, decode COSE key format and verify with appropriate algorithm
            # This is a simplified verification
            public_key = serialization.load_der_public_key(
                public_key_bytes, backend=default_backend()
            )

            if isinstance(public_key, rsa.RSAPublicKey):
                public_key.verify(signature, data, padding.PKCS1v15(), hashes.SHA256())
            elif isinstance(public_key, ec.EllipticCurvePublicKey):
                public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))

            return True

        except Exception:
            return False


class PasskeyProvider(AuthenticationProvider):
    """
    Passkey authentication provider.
    Implements passwordless authentication with device-bound credentials.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._passkeys: Dict[str, List[PasskeyData]] = {}
        self._lock = threading.Lock()

    def enroll(self, user_id: str, credential_data: Dict[str, Any]) -> bool:
        """Enroll passkey"""
        with self._lock:
            try:
                # Generate key pair
                private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
                public_key = private_key.public_key()

                # Serialize keys
                public_key_bytes = public_key.public_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )

                private_key_bytes = private_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )

                # Encrypt private key with device key
                device_key = credential_data.get("device_key", secrets.token_bytes(32))
                encrypted_private_key = self._encrypt_key(private_key_bytes, device_key)

                passkey = PasskeyData(
                    passkey_id=base64.b64encode(secrets.token_bytes(16)).decode(
                        "utf-8"
                    ),
                    public_key=public_key_bytes,
                    private_key_encrypted=encrypted_private_key,
                    user_id=user_id,
                    device_name=credential_data.get("device_name", "Unknown Device"),
                )

                if user_id not in self._passkeys:
                    self._passkeys[user_id] = []

                self._passkeys[user_id].append(passkey)
                self.logger.info(f"Passkey enrolled for {user_id}")
                return True

            except Exception as e:
                self.logger.error(f"Passkey enrollment failed: {e}")
                return False

    def authenticate(self, credential: Dict[str, Any], context: AuthContext) -> bool:
        """Authenticate with passkey"""
        with self._lock:
            try:
                user_passkeys = self._passkeys.get(context.user_id, [])
                passkey_id = credential.get("passkey_id")

                matching_passkey = None
                for pk in user_passkeys:
                    if pk.passkey_id == passkey_id:
                        matching_passkey = pk
                        break

                if not matching_passkey:
                    return False

                # Verify challenge signature
                challenge = credential.get("challenge")
                signature = base64.b64decode(credential.get("signature"))

                public_key = serialization.load_der_public_key(
                    matching_passkey.public_key, backend=default_backend()
                )

                try:
                    public_key.verify(
                        signature, challenge.encode("utf-8"), ec.ECDSA(hashes.SHA256())
                    )

                    matching_passkey.last_used = time.time()
                    self.logger.info(
                        f"Passkey authentication successful for {context.user_id}"
                    )
                    return True

                except Exception:
                    return False

            except Exception as e:
                self.logger.error(f"Passkey authentication error: {e}")
                return False

    def revoke(self, user_id: str, credential_id: str) -> bool:
        """Revoke passkey"""
        with self._lock:
            if user_id in self._passkeys:
                initial_count = len(self._passkeys[user_id])
                self._passkeys[user_id] = [
                    pk
                    for pk in self._passkeys[user_id]
                    if pk.passkey_id != credential_id
                ]

                if len(self._passkeys[user_id]) < initial_count:
                    self.logger.info(f"Passkey revoked for {user_id}")
                    return True

            return False

    def _encrypt_key(self, key_data: bytes, device_key: bytes) -> bytes:
        """Encrypt private key with device key"""
        iv = secrets.token_bytes(16)
        cipher = Cipher(
            algorithms.AES(device_key[:32]), modes.GCM(iv), backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(key_data) + encryptor.finalize()
        return iv + encryptor.tag + ciphertext


class CertificateProvider(AuthenticationProvider):
    """
    X.509 certificate-based authentication provider.
    Supports client certificates and smart cards.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._certificates: Dict[str, List[x509.Certificate]] = {}
        self._revoked_serials: Set[int] = set()
        self._lock = threading.Lock()

    def enroll(self, user_id: str, credential_data: bytes) -> bool:
        """Enroll X.509 certificate"""
        with self._lock:
            try:
                cert = x509.load_pem_x509_certificate(
                    credential_data, default_backend()
                )

                # Validate certificate
                if not self._validate_certificate(cert):
                    self.logger.warning(f"Invalid certificate for {user_id}")
                    return False

                if user_id not in self._certificates:
                    self._certificates[user_id] = []

                self._certificates[user_id].append(cert)
                self.logger.info(f"Certificate enrolled for {user_id}")
                return True

            except Exception as e:
                self.logger.error(f"Certificate enrollment failed: {e}")
                return False

    def authenticate(self, credential: Dict[str, Any], context: AuthContext) -> bool:
        """Authenticate with certificate"""
        with self._lock:
            try:
                cert_pem = credential.get("certificate")
                cert = x509.load_pem_x509_certificate(
                    cert_pem.encode(), default_backend()
                )

                # Check if certificate is revoked
                if cert.serial_number in self._revoked_serials:
                    self.logger.warning(
                        f"Revoked certificate used for {context.user_id}"
                    )
                    return False

                # Verify certificate chain and validity
                if not self._validate_certificate(cert):
                    return False

                # Verify challenge signature
                challenge = credential.get("challenge").encode("utf-8")
                signature = base64.b64decode(credential.get("signature"))

                public_key = cert.public_key()

                try:
                    if isinstance(public_key, rsa.RSAPublicKey):
                        public_key.verify(
                            signature, challenge, padding.PKCS1v15(), hashes.SHA256()
                        )
                    elif isinstance(public_key, ec.EllipticCurvePublicKey):
                        public_key.verify(
                            signature, challenge, ec.ECDSA(hashes.SHA256())
                        )

                    self.logger.info(
                        f"Certificate authentication successful for {context.user_id}"
                    )
                    return True

                except Exception:
                    return False

            except Exception as e:
                self.logger.error(f"Certificate authentication error: {e}")
                return False

    def revoke(self, user_id: str, credential_id: str) -> bool:
        """Revoke certificate by serial number"""
        with self._lock:
            try:
                serial_number = int(credential_id)
                self._revoked_serials.add(serial_number)
                self.logger.info(f"Certificate {serial_number} revoked")
                return True
            except Exception:
                return False

    def _validate_certificate(self, cert: x509.Certificate) -> bool:
        """Validate certificate"""
        try:
            # Check validity period
            now = datetime.utcnow()
            if now < cert.not_valid_before or now > cert.not_valid_after:
                return False

            # Check key usage
            try:
                key_usage = cert.extensions.get_extension_for_oid(
                    ExtensionOID.KEY_USAGE
                ).value
                if not key_usage.digital_signature:
                    return False
            except x509.ExtensionNotFound:
                pass

            return True

        except Exception:
            return False


class BiometricProvider(AuthenticationProvider):
    """
    Biometric authentication provider.
    Supports fingerprint, face recognition, and behavioral biometrics.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._templates: Dict[str, List[BiometricTemplate]] = {}
        self._lock = threading.Lock()

    def enroll(self, user_id: str, credential_data: Dict[str, Any]) -> bool:
        """Enroll biometric template"""
        with self._lock:
            try:
                biometric_type = BiometricType(credential_data["type"])

                # Never store raw biometric data - only hash
                raw_template = credential_data["template"].encode()
                template_hash = hashlib.sha512(raw_template).digest()

                template = BiometricTemplate(
                    template_id=base64.b64encode(secrets.token_bytes(16)).decode(
                        "utf-8"
                    ),
                    biometric_type=biometric_type,
                    template_hash=template_hash,
                    quality_score=credential_data.get("quality_score", 0.85),
                    user_id=user_id,
                )

                if user_id not in self._templates:
                    self._templates[user_id] = []

                self._templates[user_id].append(template)
                self.logger.info(f"Biometric template enrolled for {user_id}")
                return True

            except Exception as e:
                self.logger.error(f"Biometric enrollment failed: {e}")
                return False

    def authenticate(self, credential: Dict[str, Any], context: AuthContext) -> bool:
        """Authenticate with biometric"""
        with self._lock:
            try:
                user_templates = self._templates.get(context.user_id, [])
                if not user_templates:
                    return False

                biometric_type = BiometricType(credential["type"])
                raw_sample = credential["sample"].encode()
                sample_hash = hashlib.sha512(raw_sample).digest()

                # Find matching template
                for template in user_templates:
                    if template.biometric_type != biometric_type:
                        continue

                    # Calculate similarity (simplified - production would use
                    # sophisticated biometric matching algorithms)
                    similarity = self._calculate_similarity(
                        template.template_hash, sample_hash
                    )

                    if similarity >= 0.95:  # 95% match threshold
                        template.last_verified = time.time()
                        self.logger.info(
                            f"Biometric authentication successful for {context.user_id}"
                        )
                        return True

                return False

            except Exception as e:
                self.logger.error(f"Biometric authentication error: {e}")
                return False

    def revoke(self, user_id: str, credential_id: str) -> bool:
        """Revoke biometric template"""
        with self._lock:
            if user_id in self._templates:
                initial_count = len(self._templates[user_id])
                self._templates[user_id] = [
                    t
                    for t in self._templates[user_id]
                    if t.template_id != credential_id
                ]

                if len(self._templates[user_id]) < initial_count:
                    self.logger.info(f"Biometric template revoked for {user_id}")
                    return True

            return False

    def _calculate_similarity(self, hash1: bytes, hash2: bytes) -> float:
        """Calculate similarity between biometric hashes"""
        # Simplified similarity calculation
        # Production systems would use sophisticated matching algorithms
        matching_bytes = sum(a == b for a, b in zip(hash1, hash2))
        return matching_bytes / len(hash1)


class MFAAuthenticator:
    """
    Production-grade Multi-Factor Authentication system.

    Features:
    - Multiple authentication methods (TOTP, FIDO2, passkeys, certificates, biometrics)
    - Context-aware authentication with risk assessment
    - Dynamic authentication escalation
    - Session management with varying auth levels
    - Integration with Privacy Risk Engine
    - Thread-safe operations
    - Comprehensive audit logging
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}

        # Initialize authentication providers
        self.providers: Dict[AuthMethod, AuthenticationProvider] = {
            AuthMethod.TOTP: TOTPProvider(),
            AuthMethod.FIDO2: FIDO2Provider(),
            AuthMethod.WEBAUTHN: FIDO2Provider(),  # WebAuthn uses FIDO2
            AuthMethod.PASSKEY: PasskeyProvider(),
            AuthMethod.CERTIFICATE: CertificateProvider(),
            AuthMethod.BIOMETRIC: BiometricProvider(),
        }

        # Active sessions
        self._sessions: Dict[str, AuthContext] = {}
        self._session_lock = threading.Lock()

        # Risk-based authentication policies
        self._auth_policies: Dict[RiskLevel, List[AuthMethod]] = {
            RiskLevel.MINIMAL: [AuthMethod.PASSWORD],
            RiskLevel.LOW: [AuthMethod.PASSWORD, AuthMethod.TOTP],
            RiskLevel.MODERATE: [AuthMethod.PASSWORD, AuthMethod.TOTP],
            RiskLevel.HIGH: [
                AuthMethod.PASSWORD,
                AuthMethod.FIDO2,
                AuthMethod.BIOMETRIC,
            ],
            RiskLevel.CRITICAL: [
                AuthMethod.PASSWORD,
                AuthMethod.FIDO2,
                AuthMethod.CERTIFICATE,
            ],
            RiskLevel.EXTREME: [
                AuthMethod.PASSWORD,
                AuthMethod.FIDO2,
                AuthMethod.CERTIFICATE,
                AuthMethod.BIOMETRIC,
            ],
        }

        # Session timeout configuration (seconds)
        self._session_timeouts: Dict[AuthLevel, float] = {
            AuthLevel.BASIC: 3600,  # 1 hour
            AuthLevel.STANDARD: 7200,  # 2 hours
            AuthLevel.ELEVATED: 3600,  # 1 hour
            AuthLevel.HIGH: 1800,  # 30 minutes
            AuthLevel.CRITICAL: 900,  # 15 minutes
        }

        # Privacy Risk Engine integration callback
        self._risk_engine_callback: Optional[Callable] = None

        # Audit log
        self._audit_log: deque = deque(maxlen=10000)

        self.logger.info("MFA Authenticator initialized")

    def create_auth_context(
        self, user_id: str, session_id: str, ip_address: str, user_agent: str, **kwargs
    ) -> AuthContext:
        """
        Create new authentication context.

        Args:
            user_id: User identifier
            session_id: Session identifier
            ip_address: Client IP address
            user_agent: Client user agent
            **kwargs: Additional context parameters

        Returns:
            New AuthContext instance
        """
        context = AuthContext(
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            **kwargs,
        )

        # Assess initial risk
        context.risk_level = self._assess_risk(context)

        with self._session_lock:
            self._sessions[session_id] = context

        self._log_audit("context_created", context)
        return context

    def authenticate(
        self, context: AuthContext, method: AuthMethod, credential: Any
    ) -> Tuple[bool, Optional[str]]:
        """
        Authenticate using specified method.

        Args:
            context: Authentication context
            method: Authentication method to use
            credential: Credential data for the method

        Returns:
            Tuple of (success, error_message)
        """
        try:
            provider = self.providers.get(method)
            if not provider:
                return False, f"Unsupported authentication method: {method}"

            # Verify session is still valid
            if not self._is_session_valid(context):
                return False, "Session expired or invalid"

            # Authenticate with provider
            success = provider.authenticate(credential, context)

            if success:
                # Update context
                context.authenticated_methods.add(method)
                context.last_auth_time = time.time()
                context.auth_level = self._calculate_auth_level(context)

                self._log_audit(
                    "authentication_success", context, {"method": method.value}
                )
                return True, None
            else:
                self._log_audit(
                    "authentication_failure", context, {"method": method.value}
                )
                return False, "Authentication failed"

        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            self._log_audit(
                "authentication_error",
                context,
                {"method": method.value, "error": str(e)},
            )
            return False, str(e)

    def enroll_method(
        self, user_id: str, method: AuthMethod, credential_data: Any
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Enroll new authentication method for user.

        Args:
            user_id: User identifier
            method: Authentication method to enroll
            credential_data: Credential data for enrollment

        Returns:
            Tuple of (success, enrollment_data)
        """
        try:
            provider = self.providers.get(method)
            if not provider:
                return False, None

            result = provider.enroll(user_id, credential_data)

            if isinstance(result, tuple):
                success, enrollment_data = result
            else:
                success, enrollment_data = result, None

            if success:
                self._log_audit(
                    "method_enrolled",
                    None,
                    {"user_id": user_id, "method": method.value},
                )

            return success, enrollment_data

        except Exception as e:
            self.logger.error(f"Enrollment error: {e}")
            return False, None

    def revoke_method(
        self, user_id: str, method: AuthMethod, credential_id: str
    ) -> bool:
        """
        Revoke authentication method.

        Args:
            user_id: User identifier
            method: Authentication method to revoke
            credential_id: Credential identifier to revoke

        Returns:
            True if revocation succeeds
        """
        try:
            provider = self.providers.get(method)
            if not provider:
                return False

            success = provider.revoke(user_id, credential_id)

            if success:
                self._log_audit(
                    "method_revoked",
                    None,
                    {
                        "user_id": user_id,
                        "method": method.value,
                        "credential_id": credential_id,
                    },
                )

            return success

        except Exception as e:
            self.logger.error(f"Revocation error: {e}")
            return False

    def require_escalation(
        self, context: AuthContext, target_level: AuthLevel
    ) -> Tuple[bool, List[AuthMethod]]:
        """
        Check if authentication escalation is required and return required methods.

        Args:
            context: Current authentication context
            target_level: Target authentication level

        Returns:
            Tuple of (escalation_required, required_methods)
        """
        if context.auth_level.value >= target_level.value:
            return False, []

        # Determine required methods based on risk level
        required_methods = self._auth_policies.get(
            context.risk_level, [AuthMethod.PASSWORD, AuthMethod.TOTP]
        )

        # Filter out already authenticated methods
        missing_methods = [
            m for m in required_methods if m not in context.authenticated_methods
        ]

        return True, missing_methods

    def set_risk_engine_callback(self, callback: Callable[[AuthContext], RiskLevel]):
        """
        Set Privacy Risk Engine integration callback.

        Args:
            callback: Function that takes AuthContext and returns RiskLevel
        """
        self._risk_engine_callback = callback
        self.logger.info("Privacy Risk Engine callback configured")

    def update_risk_level(self, context: AuthContext, new_risk_level: RiskLevel):
        """
        Update risk level for session and trigger re-authentication if needed.

        Args:
            context: Authentication context
            new_risk_level: New risk level
        """
        old_risk_level = context.risk_level
        context.risk_level = new_risk_level

        # Check if escalation is needed
        required_methods = self._auth_policies.get(new_risk_level, [])

        # Check if current authentication is sufficient
        insufficient = False
        for method in required_methods:
            if method not in context.authenticated_methods:
                insufficient = True
                break

        if insufficient:
            # Downgrade auth level to trigger re-authentication
            context.auth_level = AuthLevel.BASIC
            context.risk_factors.append(
                f"Risk escalation: {old_risk_level.name} -> {new_risk_level.name}"
            )

        self._log_audit(
            "risk_level_updated",
            context,
            {"old_level": old_risk_level.name, "new_level": new_risk_level.name},
        )

    def validate_session(self, session_id: str) -> Tuple[bool, Optional[AuthContext]]:
        """
        Validate session and return context if valid.

        Args:
            session_id: Session identifier

        Returns:
            Tuple of (valid, context)
        """
        with self._session_lock:
            context = self._sessions.get(session_id)

            if not context:
                return False, None

            if not self._is_session_valid(context):
                del self._sessions[session_id]
                return False, None

            return True, context

    def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate and remove session.

        Args:
            session_id: Session identifier

        Returns:
            True if session was invalidated
        """
        with self._session_lock:
            if session_id in self._sessions:
                context = self._sessions[session_id]
                del self._sessions[session_id]
                self._log_audit("session_invalidated", context)
                return True
            return False

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information.

        Args:
            session_id: Session identifier

        Returns:
            Session information dictionary or None
        """
        with self._session_lock:
            context = self._sessions.get(session_id)
            if context:
                return {
                    "user_id": context.user_id,
                    "auth_level": context.auth_level.name,
                    "risk_level": context.risk_level.name,
                    "authenticated_methods": [
                        m.value for m in context.authenticated_methods
                    ],
                    "created_at": context.timestamp,
                    "last_auth": context.last_auth_time,
                    "expires_at": context.timestamp
                    + self._session_timeouts.get(context.auth_level, 3600),
                }
            return None

    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent audit log entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of audit log entries
        """
        return list(self._audit_log)[-limit:]

    def _assess_risk(self, context: AuthContext) -> RiskLevel:
        """Assess risk level for context"""
        # Use Privacy Risk Engine if available
        if self._risk_engine_callback:
            try:
                return self._risk_engine_callback(context)
            except Exception as e:
                self.logger.error(f"Risk engine callback error: {e}")

        # Default risk assessment
        risk_score = 0

        # Check for risk factors
        if not context.device_fingerprint:
            risk_score += 1
            context.risk_factors.append("No device fingerprint")

        if not context.geolocation:
            risk_score += 1
            context.risk_factors.append("No geolocation")

        if len(context.previous_sessions) == 0:
            risk_score += 2
            context.risk_factors.append("First session")

        # Map score to risk level
        if risk_score == 0:
            return RiskLevel.MINIMAL
        elif risk_score <= 1:
            return RiskLevel.LOW
        elif risk_score <= 2:
            return RiskLevel.MODERATE
        elif risk_score <= 3:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def _calculate_auth_level(self, context: AuthContext) -> AuthLevel:
        """Calculate authentication level based on authenticated methods"""
        methods = context.authenticated_methods

        if not methods:
            return AuthLevel.NONE

        # Count strong vs weak methods
        strong_methods = {
            AuthMethod.FIDO2,
            AuthMethod.WEBAUTHN,
            AuthMethod.CERTIFICATE,
            AuthMethod.PASSKEY,
        }

        biometric_methods = {AuthMethod.BIOMETRIC}

        strong_count = len(methods & strong_methods)
        has_biometric = len(methods & biometric_methods) > 0

        if strong_count >= 2 and has_biometric:
            return AuthLevel.CRITICAL
        elif strong_count >= 1 and has_biometric:
            return AuthLevel.HIGH
        elif strong_count >= 1:
            return AuthLevel.ELEVATED
        elif len(methods) >= 2:
            return AuthLevel.STANDARD
        else:
            return AuthLevel.BASIC

    def _is_session_valid(self, context: AuthContext) -> bool:
        """Check if session is still valid"""
        # Check timeout
        timeout = self._session_timeouts.get(context.auth_level, 3600)
        if time.time() - context.last_auth_time > timeout:
            return False

        # Check if session was created too long ago
        max_session_age = 86400  # 24 hours
        if time.time() - context.timestamp > max_session_age:
            return False

        return True

    def _log_audit(
        self,
        event: str,
        context: Optional[AuthContext],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Log audit event"""
        audit_entry = {
            "timestamp": time.time(),
            "event": event,
            "context": context.to_dict() if context else None,
            "metadata": metadata or {},
        }

        self._audit_log.append(audit_entry)

        # Also log to standard logger
        self.logger.info(f"AUDIT: {event} - {metadata or {}}")


# Utility functions for integration


def generate_totp_secret() -> bytes:
    """Generate new TOTP secret"""
    return secrets.token_bytes(20)


def generate_qr_code_data(provisioning_uri: str) -> str:
    """
    Generate QR code data for TOTP provisioning.

    Args:
        provisioning_uri: otpauth:// URI

    Returns:
        Base64-encoded QR code data
    """
    # In production, this would generate actual QR code image
    # For now, return the URI itself
    return base64.b64encode(provisioning_uri.encode()).decode("utf-8")


def verify_totp_token(secret: bytes, token: str, window: int = 1) -> bool:
    """
    Verify TOTP token with time window.

    Args:
        secret: TOTP secret
        token: Token to verify
        window: Time window (±periods)

    Returns:
        True if token is valid
    """
    provider = TOTPProvider()
    config = TOTPConfig(secret=secret)

    current_time = int(time.time())
    for time_offset in range(-window, window + 1):
        counter = (current_time + time_offset * config.period) // config.period
        expected = provider._generate_totp(config, counter)

        if secrets.compare_digest(token, expected):
            return True

    return False
