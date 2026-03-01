"""
Ed25519 Cryptographic Provider — Production Key Management, Signing, and Verification.

Replaces all SHA-256 stub signatures throughout the PSIA codebase with real
Ed25519 operations via the ``cryptography`` library (PyCA).

Architecture:
    Ed25519Provider  — Stateless utility: generate, sign, verify
    Ed25519KeyPair   — Immutable keypair container with serialization
    KeyStore         — In-memory registry mapping component names to keypairs

Security Properties:
    - Private keys are held as ``Ed25519PrivateKey`` objects (never raw bytes in logs)
    - Signing produces deterministic 64-byte signatures (RFC 8032)
    - Verification is constant-time (PyCA guarantee)
    - KeyStore is per-process; private keys never leave memory unless explicitly exported

Usage:
    provider = Ed25519Provider()
    keypair = provider.generate_keypair("genesis_root")
    sig = provider.sign(keypair.private_key, b"data to sign")
    assert provider.verify(keypair.public_key, sig, b"data to sign")
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Ed25519KeyPair:
    """An Ed25519 key pair with metadata.

    Attributes:
        private_key:    The Ed25519 private key object.
        public_key:     The Ed25519 public key object.
        key_id:         Unique identifier for this keypair.
        component:      The PSIA component this keypair belongs to.
        created_at:     ISO-8601 timestamp of key creation.
        purpose:        Key purpose (signing, encryption, etc.).
        public_key_hex: Hex-encoded raw public key bytes (32 bytes → 64 hex chars).
    """

    private_key: Ed25519PrivateKey
    public_key: Ed25519PublicKey
    key_id: str
    component: str
    created_at: str
    purpose: str = "signing"
    public_key_hex: str = ""

    def __post_init__(self) -> None:
        if not self.public_key_hex:
            raw = self.public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
            object.__setattr__(self, "public_key_hex", raw.hex())


class Ed25519Provider:
    """Stateless Ed25519 cryptographic operations.

    All methods are class-level or static — no instance state is needed.
    This is the single source of truth for all Ed25519 operations in PSIA.
    """

    @staticmethod
    def generate_keypair(
        component: str,
        *,
        key_id: str | None = None,
        purpose: str = "signing",
    ) -> Ed25519KeyPair:
        """Generate a new Ed25519 keypair.

        Args:
            component:  PSIA component name (e.g., "genesis_root", "capability_authority").
            key_id:     Optional explicit key ID. Auto-generated if None.
            purpose:    Key purpose string.

        Returns:
            A frozen Ed25519KeyPair with real cryptographic keys.
        """
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        now = datetime.now(timezone.utc).isoformat()

        if key_id is None:
            key_id = f"key_{component}_{uuid.uuid4().hex[:8]}"

        pair = Ed25519KeyPair(
            private_key=private_key,
            public_key=public_key,
            key_id=key_id,
            component=component,
            created_at=now,
            purpose=purpose,
        )

        logger.info(
            "Generated Ed25519 keypair: component=%s key_id=%s pub=%s…",
            component,
            key_id,
            pair.public_key_hex[:16],
        )
        return pair

    @staticmethod
    def sign(private_key: Ed25519PrivateKey, data: bytes) -> str:
        """Sign data with an Ed25519 private key.

        Args:
            private_key: The Ed25519 private key.
            data:        Raw bytes to sign.

        Returns:
            Hex-encoded 64-byte Ed25519 signature.
        """
        signature_bytes = private_key.sign(data)
        return signature_bytes.hex()

    @staticmethod
    def sign_string(private_key: Ed25519PrivateKey, message: str) -> str:
        """Sign a UTF-8 string with an Ed25519 private key.

        Convenience wrapper around ``sign()`` for string data.
        """
        return Ed25519Provider.sign(private_key, message.encode("utf-8"))

    @staticmethod
    def verify(
        public_key: Ed25519PublicKey,
        signature_hex: str,
        data: bytes,
    ) -> bool:
        """Verify an Ed25519 signature.

        Args:
            public_key:    The Ed25519 public key.
            signature_hex: Hex-encoded signature to verify.
            data:          The original data that was signed.

        Returns:
            True if signature is valid, False otherwise.
            Never raises on invalid signature — returns False.
        """
        try:
            signature_bytes = bytes.fromhex(signature_hex)
            public_key.verify(signature_bytes, data)
            return True
        except (InvalidSignature, ValueError, Exception):
            return False

    @staticmethod
    def verify_string(
        public_key: Ed25519PublicKey,
        signature_hex: str,
        message: str,
    ) -> bool:
        """Verify a signature over a UTF-8 string."""
        return Ed25519Provider.verify(
            public_key, signature_hex, message.encode("utf-8")
        )

    @staticmethod
    def serialize_private_key(private_key: Ed25519PrivateKey) -> str:
        """Serialize a private key to hex (PEM-free raw bytes).

        WARNING: This exports the raw private key bytes. Handle with care.
        In production, private keys should be managed by HSM/KMS.
        """
        raw = private_key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
        return raw.hex()

    @staticmethod
    def serialize_public_key(public_key: Ed25519PublicKey) -> str:
        """Serialize a public key to hex (32 raw bytes → 64 hex chars)."""
        raw = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
        return raw.hex()

    @staticmethod
    def load_public_key(public_key_hex: str) -> Ed25519PublicKey:
        """Load a public key from hex-encoded raw bytes.

        Args:
            public_key_hex: 64-character hex string (32 bytes).

        Returns:
            Ed25519PublicKey object.

        Raises:
            ValueError: If hex string is invalid or wrong length.
        """
        raw = bytes.fromhex(public_key_hex)
        if len(raw) != 32:
            raise ValueError(f"Ed25519 public key must be 32 bytes, got {len(raw)}")
        return Ed25519PublicKey.from_public_bytes(raw)

    @staticmethod
    def load_private_key(private_key_hex: str) -> Ed25519PrivateKey:
        """Load a private key from hex-encoded raw bytes.

        Args:
            private_key_hex: 64-character hex string (32 bytes).

        Returns:
            Ed25519PrivateKey object.

        Raises:
            ValueError: If hex string is invalid or wrong length.
        """
        raw = bytes.fromhex(private_key_hex)
        if len(raw) != 32:
            raise ValueError(f"Ed25519 private key must be 32 bytes, got {len(raw)}")
        return Ed25519PrivateKey.from_private_bytes(raw)

    @staticmethod
    def compute_data_hash(data: str) -> str:
        """Compute SHA-256 hash of string data (used as signing input).

        Provides a canonical way to hash structured data before signing.
        """
        return hashlib.sha256(data.encode("utf-8")).hexdigest()


class KeyStore:
    """In-memory key registry for PSIA node keypairs.

    Maps component names to Ed25519KeyPair instances.
    Thread-safe for read operations after initialization.

    Lifecycle:
        1. Created during genesis ceremony
        2. Populated with keypairs for all system components
        3. Read-only after genesis completes
        4. Never persisted — regenerated on each boot

    Security:
        Private keys exist only in process memory.
        No serialization to disk, logs, or network.
    """

    def __init__(self) -> None:
        self._keys: dict[str, Ed25519KeyPair] = {}
        self._created_at = datetime.now(timezone.utc).isoformat()

    def register(self, keypair: Ed25519KeyPair) -> None:
        """Register a keypair for a component.

        Args:
            keypair: The Ed25519KeyPair to register.

        Raises:
            ValueError: If a key for this component already exists.
        """
        if keypair.component in self._keys:
            raise ValueError(
                f"Key already registered for component: {keypair.component}"
            )
        self._keys[keypair.component] = keypair
        logger.debug("Registered key for component: %s", keypair.component)

    def get(self, component: str) -> Ed25519KeyPair | None:
        """Retrieve a keypair by component name."""
        return self._keys.get(component)

    def get_private_key(self, component: str) -> Ed25519PrivateKey | None:
        """Retrieve the private key for a component."""
        pair = self._keys.get(component)
        return pair.private_key if pair else None

    def get_public_key(self, component: str) -> Ed25519PublicKey | None:
        """Retrieve the public key for a component."""
        pair = self._keys.get(component)
        return pair.public_key if pair else None

    def sign_as(self, component: str, data: bytes) -> str:
        """Sign data using a registered component's private key.

        Args:
            component: The component whose key to use.
            data:      Raw bytes to sign.

        Returns:
            Hex-encoded Ed25519 signature.

        Raises:
            KeyError: If no key is registered for this component.
        """
        pair = self._keys.get(component)
        if pair is None:
            raise KeyError(f"No key registered for component: {component}")
        return Ed25519Provider.sign(pair.private_key, data)

    def verify_from(self, component: str, signature_hex: str, data: bytes) -> bool:
        """Verify a signature using a registered component's public key.

        Returns False if the component is not registered or signature is invalid.
        """
        pair = self._keys.get(component)
        if pair is None:
            return False
        return Ed25519Provider.verify(pair.public_key, signature_hex, data)

    @property
    def components(self) -> list[str]:
        """List all registered component names."""
        return list(self._keys.keys())

    @property
    def count(self) -> int:
        """Number of registered keypairs."""
        return len(self._keys)

    def public_key_registry(self) -> dict[str, str]:
        """Export a public-key-only registry (safe for logging/audit).

        Returns:
            Dict mapping component name → public key hex.
        """
        return {name: pair.public_key_hex for name, pair in self._keys.items()}


__all__ = [
    "Ed25519KeyPair",
    "Ed25519Provider",
    "KeyStore",
]
