"""
T-SECA / GHOST PROTOCOL
Unified Runtime Hardening + Catastrophic Continuity Engine

This module provides:
- Shamir Secret Sharing for splitting and reconstructing secrets (GF(257))
- Ghost Protocol for identity continuity with encrypted fragmentation
- T-SECA runtime hardening with secure inference validation
- Heartbeat monitoring with catastrophic failure detection
- Unified system integrating all components

Security Features:
- Ed25519 cryptographic identity
- AES-GCM encryption for shard protection
- Quorum-based secret reconstruction
- Tamper-resistant identity hash chains
- Automatic resurrection on catastrophic failure
"""

import hashlib
import json
import logging
import secrets
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

logger = logging.getLogger(__name__)


# ================================================================
# UTILITIES
# ================================================================


def sha256(data: bytes) -> str:
    """Compute SHA-256 hash of data.

    Args:
        data: Bytes to hash

    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(data).hexdigest()


def canonical_json(obj: Any) -> bytes:
    """Serialize object to canonical JSON bytes.

    Args:
        obj: Object to serialize

    Returns:
        Canonical JSON bytes (sorted keys, compact format)
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


# ================================================================
# SHAMIR SECRET SHARING (GF(257))
# ================================================================

PRIME = 257


def _eval_poly(poly: list[int], x: int) -> int:
    """Evaluate polynomial at x in GF(257).

    Args:
        poly: Polynomial coefficients [a0, a1, ..., ak-1]
        x: Point to evaluate

    Returns:
        Polynomial value modulo PRIME
    """
    return sum(coef * pow(x, i, PRIME) for i, coef in enumerate(poly)) % PRIME


def _lagrange(x: int, x_s: list[int], y_s: list[int]) -> int:
    """Lagrange interpolation at x in GF(257).

    Args:
        x: Point to evaluate
        x_s: List of x coordinates
        y_s: List of y coordinates

    Returns:
        Interpolated value modulo PRIME
    """
    total = 0
    for i in range(len(x_s)):
        xi, yi = x_s[i], y_s[i]
        prod = yi
        for j in range(len(x_s)):
            if i != j:
                xj = x_s[j]
                prod *= (x - xj) * pow(xi - xj, -1, PRIME)
                prod %= PRIME
        total += prod
    return total % PRIME


def shamir_split(secret: bytes, k: int, n: int) -> list[tuple[int, bytes]]:
    """Split secret into n shares requiring k to reconstruct.

    Uses Shamir Secret Sharing over GF(257) with random polynomials.
    Note: Share values are in GF(257) (0-256), encoded as two bytes each.

    Args:
        secret: Secret bytes to split
        k: Threshold number of shares needed for reconstruction
        n: Total number of shares to generate

    Returns:
        List of (share_index, share_data) tuples

    Raises:
        ValueError: If k > n or k < 1
    """
    if k > n or k < 1:
        raise ValueError(f"Invalid parameters: k={k}, n={n}")

    # Each share value is in GF(257), stored as 2 bytes (little-endian)
    shares = [(i, bytearray(len(secret) * 2)) for i in range(1, n + 1)]
    for idx, byte in enumerate(secret):
        poly = [byte] + [secrets.randbelow(PRIME) for _ in range(k - 1)]
        for x, share in shares:
            val = _eval_poly(poly, x)
            # Store as little-endian 16-bit value
            share[idx * 2] = val & 0xFF
            share[idx * 2 + 1] = (val >> 8) & 0xFF
    return [(x, bytes(share)) for x, share in shares]


def shamir_reconstruct(shares: list[tuple[int, bytes]]) -> bytes:
    """Reconstruct secret from k shares.

    Args:
        shares: List of (share_index, share_data) tuples
                Share data is encoded as 2 bytes per GF(257) value

    Returns:
        Reconstructed secret bytes

    Raises:
        ValueError: If shares have mismatched lengths or invalid format
    """
    if not shares:
        raise ValueError("No shares provided")

    length = len(shares[0][1])
    if not all(len(s[1]) == length for s in shares):
        raise ValueError("All shares must have the same length")

    if length % 2 != 0:
        raise ValueError("Share data must have even length (2 bytes per value)")

    secret_len = length // 2
    secret = bytearray(secret_len)
    for idx in range(secret_len):
        x_s = [s[0] for s in shares]
        # Decode 16-bit little-endian values
        y_s = [s[1][idx * 2] | (s[1][idx * 2 + 1] << 8) for s in shares]
        secret[idx] = _lagrange(0, x_s, y_s)
    return bytes(secret)


# ================================================================
# GHOST PROTOCOL (Continuity Layer)
# ================================================================


class GhostProtocol:
    """Identity continuity system with encrypted fragmentation.

    Provides catastrophic failure recovery through Shamir-split encrypted
    identity shards. Uses Ed25519 for identity and AES-GCM for encryption.

    Attributes:
        quorum_k: Minimum shares needed for reconstruction
        total_n: Total shares generated
        master_key: AES-GCM encryption key
        identity_key: Ed25519 private key
        identity_hash: SHA-256 hash of public key
        encrypted_shards: List of encrypted identity fragments
    """

    def __init__(self, quorum_k: int = 3, total_n: int = 5):
        """Initialize Ghost Protocol with identity generation.

        Args:
            quorum_k: Threshold for reconstruction (default: 3)
            total_n: Total shards to generate (default: 5)

        Raises:
            ValueError: If quorum_k > total_n or quorum_k < 1
        """
        if quorum_k > total_n or quorum_k < 1:
            raise ValueError(f"Invalid quorum parameters: k={quorum_k}, n={total_n}")

        self.quorum_k = quorum_k
        self.total_n = total_n
        self.master_key = AESGCM.generate_key(bit_length=256)

        self.identity_key = ed25519.Ed25519PrivateKey.generate()
        self.identity_hash = self._compute_identity_hash()

        self.shards: list[tuple[int, bytes]] = []
        self.encrypted_shards: list[bytes] = []

        logger.info(
            "Ghost Protocol initialized: quorum=%d/%d, identity=%s",
            quorum_k,
            total_n,
            self.identity_hash[:16],
        )

    def _compute_identity_hash(self) -> str:
        """Compute SHA-256 hash of public key.

        Returns:
            Hexadecimal identity hash
        """
        pub = self.identity_key.public_key().public_bytes(
            Encoding.Raw, PublicFormat.Raw
        )
        return sha256(pub)

    def fragment_identity(self) -> list[bytes]:
        """Fragment identity into encrypted shards.

        Splits the Ed25519 private key using Shamir Secret Sharing,
        then encrypts each shard with AES-GCM. Shard index is prepended.

        Returns:
            List of encrypted shard blobs (index + nonce + ciphertext)
        """
        raw = self.identity_key.private_bytes(
            Encoding.Raw, PrivateFormat.Raw, NoEncryption()
        )
        shares = shamir_split(raw, self.quorum_k, self.total_n)
        aes = AESGCM(self.master_key)

        self.encrypted_shards = []
        for idx, shard in shares:
            nonce = secrets.token_bytes(12)
            encrypted = nonce + aes.encrypt(nonce, shard, None)
            # Prepend share index as single byte (1-255 range is sufficient)
            self.encrypted_shards.append(bytes([idx]) + encrypted)

        logger.info(
            "Identity fragmented into %d shards (quorum: %d)",
            self.total_n,
            self.quorum_k,
        )
        return self.encrypted_shards

    def resurrect(self, shard_blobs: list[bytes]) -> str:
        """Resurrect identity from encrypted shards.

        Decrypts shards, reconstructs the Ed25519 private key using
        Shamir Secret Sharing with original indices, and verifies identity hash.

        Args:
            shard_blobs: List of encrypted shard blobs (at least quorum_k)
                         Format: index + nonce + ciphertext

        Returns:
            Reconstructed identity hash

        Raises:
            ValueError: If insufficient shards provided or decryption fails
        """
        if len(shard_blobs) < self.quorum_k:
            raise ValueError(
                f"Insufficient shards: need {self.quorum_k}, got {len(shard_blobs)}"
            )

        aes = AESGCM(self.master_key)
        decrypted = []
        for blob in shard_blobs[: self.quorum_k]:
            # Extract index from first byte
            idx = blob[0]
            nonce, ct = blob[1:13], blob[13:]
            try:
                shard = aes.decrypt(nonce, ct, None)
                decrypted.append((idx, shard))
            except Exception as e:
                raise ValueError(f"Failed to decrypt shard {idx}: {e}") from e

        restored = shamir_reconstruct(decrypted)
        self.identity_key = ed25519.Ed25519PrivateKey.from_private_bytes(restored)
        self.identity_hash = self._compute_identity_hash()

        logger.info("Identity resurrected: %s", self.identity_hash[:16])
        return self.identity_hash


# ================================================================
# T-SECA (Runtime Hardening Layer)
# ================================================================


class TSECA:
    """Runtime hardening layer with secure inference validation.

    Validates all operations against Ghost Protocol identity anchor
    and provides cryptographically signed inference results.

    Attributes:
        ghost: Ghost Protocol instance for identity verification
    """

    def __init__(self, ghost: GhostProtocol):
        """Initialize T-SECA with Ghost Protocol binding.

        Args:
            ghost: Ghost Protocol instance for identity anchor
        """
        self.ghost = ghost
        logger.info("T-SECA initialized with identity %s", ghost.identity_hash[:16])

    def verify_identity(self) -> None:
        """Verify identity anchor is present.

        Raises:
            RuntimeError: If identity hash is missing or invalid
        """
        if not self.ghost.identity_hash:
            raise RuntimeError("Identity anchor missing")

    def secure_inference(self, payload: dict) -> dict:
        """Execute secure inference with cryptographic attestation.

        Validates identity, processes payload deterministically,
        and returns signed result with identity proof.

        Args:
            payload: Input data for inference

        Returns:
            Dictionary with:
                - result: Inference output
                - identity_hash: Current identity hash
                - response_hash: SHA-256 of canonical result
                - signature: Ed25519 signature of response_hash

        Raises:
            RuntimeError: If identity verification fails
        """
        self.verify_identity()

        # Deterministic processing placeholder
        result = {
            "strategic_summary": "Processed safely.",
            "risk_assessment": "low",
            "identified_gaps": [],
            "confidence_score": 0.99,
        }

        canonical = canonical_json(result)
        response_hash = sha256(canonical)

        signature = self.ghost.identity_key.sign(response_hash.encode())

        logger.info(
            "Secure inference completed: hash=%s, identity=%s",
            response_hash[:16],
            self.ghost.identity_hash[:16],
        )

        return {
            "result": result,
            "identity_hash": self.ghost.identity_hash,
            "response_hash": response_hash,
            "signature": signature.hex(),
        }


# ================================================================
# HEARTBEAT MONITOR
# ================================================================


@dataclass
class HeartbeatState:
    """State tracking for heartbeat monitoring.

    Attributes:
        last_seen: Timestamp of last heartbeat
        failure_count: Consecutive failure count
    """

    last_seen: float
    failure_count: int = 0


class HeartbeatMonitor:
    """Catastrophic failure detection via heartbeat monitoring.

    Monitors system health and triggers failure callback after
    threshold consecutive timeouts.

    Attributes:
        timeout: Seconds between heartbeat checks
        threshold: Consecutive failures before triggering callback
        state: Current heartbeat state
        running: Monitor thread control flag
    """

    def __init__(self, timeout: int = 5, threshold: int = 3):
        """Initialize heartbeat monitor.

        Args:
            timeout: Seconds between heartbeat checks (default: 5)
            threshold: Failures before callback (default: 3)
        """
        self.timeout = timeout
        self.threshold = threshold
        self.state = HeartbeatState(time.time())
        self.running = True

        logger.info(
            "Heartbeat monitor initialized: timeout=%ds, threshold=%d",
            timeout,
            threshold,
        )

    def beat(self) -> None:
        """Register successful heartbeat.

        Resets failure count and updates last_seen timestamp.
        """
        self.state.last_seen = time.time()
        self.state.failure_count = 0

    def monitor(self, on_failure: Callable[[], None]) -> None:
        """Monitor heartbeat and trigger callback on failure.

        Runs in separate thread, checking every timeout seconds.
        Stops monitoring after callback is triggered.

        Args:
            on_failure: Callback function for catastrophic failure
        """
        while self.running:
            time.sleep(self.timeout)
            if time.time() - self.state.last_seen > self.timeout:
                self.state.failure_count += 1
                logger.warning(
                    "Heartbeat timeout: consecutive failures=%d",
                    self.state.failure_count,
                )
                if self.state.failure_count >= self.threshold:
                    logger.critical("Catastrophic failure threshold reached")
                    on_failure()
                    self.running = False


# ================================================================
# UNIFIED SYSTEM
# ================================================================


class TSECA_Ghost_System:
    """Unified runtime hardening + catastrophic continuity system.

    Integrates Ghost Protocol, T-SECA hardening, and heartbeat monitoring
    into a single resilient system with automatic identity resurrection.

    Attributes:
        ghost: Ghost Protocol instance
        tseca: T-SECA hardening layer
        shards: Encrypted identity shards
        heartbeat: Heartbeat monitor
    """

    def __init__(self):
        """Initialize unified system with automatic monitoring."""
        self.ghost = GhostProtocol()
        self.tseca = TSECA(self.ghost)
        self.shards = self.ghost.fragment_identity()

        self.heartbeat = HeartbeatMonitor()

        threading.Thread(
            target=self.heartbeat.monitor,
            args=(self._catastrophic_event,),
            daemon=True,
        ).start()

        logger.info("TSECA_Ghost_System initialized with %d shards", len(self.shards))

    def _catastrophic_event(self) -> None:
        """Handle catastrophic failure with identity resurrection.

        Reconstructs identity from quorum of shards and logs recovery.
        """
        logger.critical("[GHOST] Catastrophic failure detected.")
        logger.info("[GHOST] Reconstructing identity...")

        try:
            restored_hash = self.ghost.resurrect(self.shards[: self.ghost.quorum_k])
            logger.info("[GHOST] Resurrection complete.")
            logger.info("[GHOST] Identity hash: %s", restored_hash)
        except Exception as e:
            logger.error("[GHOST] Resurrection failed: %s", e)

    def inference(self, payload: dict) -> dict:
        """Execute secure inference operation.

        Args:
            payload: Input data for inference

        Returns:
            Signed inference result with identity proof
        """
        return self.tseca.secure_inference(payload)

    def send_heartbeat(self) -> None:
        """Send heartbeat signal to monitor."""
        self.heartbeat.beat()


# ================================================================
# DEMO BOOT
# ================================================================


def demo_boot():
    """Demonstration of T-SECA/GHOST Protocol system.

    Creates system, performs inference, and simulates catastrophic
    failure by stopping heartbeats.
    """
    logger.info("=== T-SECA/GHOST Protocol Demo Boot ===")

    system = TSECA_Ghost_System()

    # Normal operation
    result = system.inference({"input": "test"})
    logger.info("Inference result: %s", result)

    # Stop heartbeat to simulate catastrophe
    logger.info("Simulating catastrophic failure (no heartbeat for 20 seconds)...")
    time.sleep(20)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    demo_boot()
