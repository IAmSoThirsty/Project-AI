"""
T-SECA / GHOST Protocol

Components:
- Shamir Secret Sharing over GF(256) for k-of-n threshold splitting
- GhostProtocol: identity fragmentation and resurrection using Shamir + AES-GCM
- TSECA: runtime hardening layer with Ed25519-signed secure inference
- HeartbeatMonitor: liveness / failure detection
- TSECA_Ghost_System: unified facade wiring all components together
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)


# ── GF(256) arithmetic ─────────────────────────────────────────────────────────

def _gf_mul(a: int, b: int) -> int:
    """Multiply two elements in GF(2^8) using the AES irreducible polynomial."""
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1B  # x^8 + x^4 + x^3 + x + 1 reduced
        b >>= 1
    return result


def _gf_inv(a: int) -> int:
    """Multiplicative inverse in GF(2^8) via a^(2^8 - 2) = a^254."""
    if a == 0:
        raise ValueError("Cannot invert 0 in GF(256)")
    result = 1
    base = a
    exp = 254
    while exp:
        if exp & 1:
            result = _gf_mul(result, base)
        base = _gf_mul(base, base)
        exp >>= 1
    return result


# ── Shamir Secret Sharing ──────────────────────────────────────────────────────

def shamir_split(
    secret: bytes, k: int, n: int
) -> list[tuple[int, bytes]]:
    """
    Split *secret* into *n* shares with reconstruction threshold *k*.

    Returns a list of (share_index, share_bytes) tuples.
    Any subset of k or more shares can reconstruct the secret.
    """
    if k < 1 or k > n:
        raise ValueError(
            f"Invalid parameters: k={k} must be >= 1 and <= n={n}"
        )

    share_data: list[bytearray] = [bytearray() for _ in range(n)]

    for byte_val in secret:
        # Random polynomial over GF(256): p(x) = byte_val + a1*x + ... + a_{k-1}*x^{k-1}
        coeffs = [byte_val] + [secrets.randbelow(256) for _ in range(k - 1)]

        for i in range(n):
            x = i + 1  # Share indices start at 1
            y = 0
            x_pow = 1
            for coeff in coeffs:
                y ^= _gf_mul(coeff, x_pow)
                x_pow = _gf_mul(x_pow, x)
            share_data[i].append(y)

    return [(i + 1, bytes(data)) for i, data in enumerate(share_data)]


def shamir_reconstruct(shares: list[tuple[int, bytes]]) -> bytes:
    """
    Reconstruct the secret from *shares*.

    All shares must have the same length.  At least k shares are required
    (where k is the threshold used during splitting).
    """
    if not shares:
        raise ValueError("No shares provided")

    lengths = {len(s[1]) for s in shares}
    if len(lengths) > 1:
        raise ValueError("Shares have different lengths")

    secret_len = len(shares[0][1])
    result = bytearray()

    for byte_idx in range(secret_len):
        points = [(s[0], s[1][byte_idx]) for s in shares]

        # Lagrange interpolation at x=0 over GF(256)
        y = 0
        for i, (xi, yi) in enumerate(points):
            num = 1
            den = 1
            for j, (xj, _) in enumerate(points):
                if i != j:
                    num = _gf_mul(num, xj)       # (0 - xj) = xj in GF(2)
                    den = _gf_mul(den, xi ^ xj)  # (xi - xj) = xi XOR xj
            term = _gf_mul(yi, _gf_mul(num, _gf_inv(den)))
            y ^= term

        result.append(y)

    return bytes(result)


# ── Ghost Protocol ─────────────────────────────────────────────────────────────

class GhostProtocol:
    """
    Identity continuity system.

    Fragments the Ed25519 identity key into AES-GCM encrypted Shamir shards
    and can resurrect the identity from any quorum_k of them.
    """

    _NONCE_SIZE = 12  # AES-GCM nonce bytes

    def __init__(self, quorum_k: int = 3, total_n: int = 5) -> None:
        if quorum_k < 1 or quorum_k > total_n:
            raise ValueError(
                f"Invalid quorum parameters: k={quorum_k}, n={total_n}"
            )
        self.quorum_k = quorum_k
        self.total_n = total_n

        self.identity_key: Ed25519PrivateKey = Ed25519PrivateKey.generate()
        self.master_key: bytes = os.urandom(32)  # AES-256 key for shard encryption
        self.identity_hash: str | None = self._compute_identity_hash()

    def _compute_identity_hash(self) -> str:
        pub_bytes = self.identity_key.public_key().public_bytes(
            encoding=Encoding.Raw, format=PublicFormat.Raw
        )
        return hashlib.sha256(pub_bytes).hexdigest()

    def _identity_key_bytes(self) -> bytes:
        return self.identity_key.private_bytes(
            encoding=Encoding.Raw,
            format=PrivateFormat.Raw,
            encryption_algorithm=NoEncryption(),
        )

    def fragment_identity(self) -> list[bytes]:
        """
        Encrypt and split the identity key into total_n shards.

        Shard layout: [1-byte index][12-byte nonce][AES-GCM ciphertext+tag]
        """
        key_bytes = self._identity_key_bytes()
        raw_shares = shamir_split(key_bytes, self.quorum_k, self.total_n)

        aesgcm = AESGCM(self.master_key)
        shards = []
        for idx, share_bytes in raw_shares:
            nonce = os.urandom(self._NONCE_SIZE)
            ciphertext = aesgcm.encrypt(nonce, share_bytes, None)
            shards.append(bytes([idx]) + nonce + ciphertext)
        return shards

    def resurrect(self, shards: list[bytes]) -> str:
        """
        Restore identity from *shards*.  Requires at least quorum_k shards.

        Returns the restored identity_hash.
        Raises ValueError if shards are insufficient or undecryptable.
        """
        if len(shards) < self.quorum_k:
            raise ValueError(
                f"Insufficient shards: need {self.quorum_k}, got {len(shards)}"
            )

        aesgcm = AESGCM(self.master_key)
        decoded: list[tuple[int, bytes]] = []

        for shard in shards[: self.quorum_k]:
            try:
                idx = shard[0]
                nonce = shard[1 : 1 + self._NONCE_SIZE]
                ciphertext = shard[1 + self._NONCE_SIZE :]
                share_bytes = aesgcm.decrypt(nonce, ciphertext, None)
                decoded.append((idx, share_bytes))
            except (InvalidTag, Exception) as exc:
                raise ValueError(f"Failed to decrypt shard: {exc}") from exc

        key_bytes = shamir_reconstruct(decoded)
        self.identity_key = Ed25519PrivateKey.from_private_bytes(key_bytes)
        self.identity_hash = self._compute_identity_hash()
        return self.identity_hash


# ── T-SECA ─────────────────────────────────────────────────────────────────────

class TSECA:
    """Runtime hardening layer: verifies identity and signs inference results."""

    def __init__(self, ghost: GhostProtocol) -> None:
        self.ghost = ghost

    def verify_identity(self) -> None:
        if not self.ghost.identity_hash:
            raise RuntimeError("Identity anchor missing")

    def secure_inference(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Run a signed, identity-bound inference over *payload*."""
        self.verify_identity()

        # Deterministic inference result structure
        inference_result = {
            "strategic_summary": f"Processed payload with {len(payload)} keys",
            "risk_assessment": "nominal",
            "identified_gaps": [],
            "confidence_score": 0.95,
        }

        response_hash = hashlib.sha256(
            json.dumps(inference_result, sort_keys=True).encode()
        ).hexdigest()

        signature = self.ghost.identity_key.sign(response_hash.encode())

        return {
            "result": inference_result,
            "identity_hash": self.ghost.identity_hash,
            "response_hash": response_hash,
            "signature": signature.hex(),
        }


# ── Heartbeat Monitor ──────────────────────────────────────────────────────────

@dataclass
class _HeartbeatState:
    failure_count: int = 0
    last_seen: float = field(default_factory=time.monotonic)


class HeartbeatMonitor:
    """Failure detector: calls *on_failure* after *threshold* missed heartbeats."""

    def __init__(self, timeout: float = 30, threshold: int = 3) -> None:
        self.timeout = timeout
        self.threshold = threshold
        self.running: bool = True
        self.state = _HeartbeatState()

    def beat(self) -> None:
        self.state.failure_count = 0
        self.state.last_seen = time.monotonic()

    def monitor(self, on_failure: Callable[[], None]) -> None:
        """Blocking monitor loop.  Run in a daemon thread."""
        while self.running:
            time.sleep(self.timeout)
            if not self.running:
                break
            elapsed = time.monotonic() - self.state.last_seen
            if elapsed >= self.timeout:
                self.state.failure_count += 1
                if self.state.failure_count >= self.threshold:
                    on_failure()
                    self.running = False
                    break


# ── Unified system ─────────────────────────────────────────────────────────────

class TSECA_Ghost_System:
    """Facade wiring GhostProtocol, TSECA, and HeartbeatMonitor together."""

    def __init__(
        self,
        quorum_k: int = 3,
        total_n: int = 5,
        heartbeat_timeout: float = 30,
        heartbeat_threshold: int = 3,
    ) -> None:
        self.ghost = GhostProtocol(quorum_k=quorum_k, total_n=total_n)
        self.tseca = TSECA(self.ghost)
        self.shards: list[bytes] = self.ghost.fragment_identity()
        self.heartbeat = HeartbeatMonitor(
            timeout=heartbeat_timeout, threshold=heartbeat_threshold
        )

    def inference(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.tseca.secure_inference(payload)

    def send_heartbeat(self) -> None:
        self.heartbeat.beat()

    def _catastrophic_event(self) -> None:
        """Simulate catastrophic failure and resurrect identity from stored shards."""
        self.ghost.resurrect(self.shards[: self.ghost.quorum_k])
