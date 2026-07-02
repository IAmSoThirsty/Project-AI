"""Cryptographic Engine for Sovereign War Room.

Handles all cryptographic operations for SWR scenario validation:

- Cryptographic decision attestations for decision verification
- Tamper-evident audit logs with commitment schemes
- Secure challenge-response protocols
- Cryptographic signatures for scenario validation

Note: Implements hash-based commitments and HMAC signatures,
not formal zero-knowledge proof systems (zk-SNARKs/zk-STARKs).

Architectural notes (port from legacy):

The legacy implementation uses the `cryptography` package
(Fernet, PBKDF2HMAC) for symmetric encryption and key
derivation. The Beginnings port preserves this dependency
but fails-closed at instantiation if the cryptography
backend is unavailable.

HMAC + SHA3-256 + SHA3-512 use only the Python stdlib and
are always available. The `encrypt_sensitive_data` /
`decrypt_sensitive_data` / `derive_key` methods require the
optional `cryptography` dep and raise `CryptoUnavailableError`
if the backend is missing.

The Beginnings port replaces Pydantic BaseModel with
frozen dataclasses to match the existing `scenario.py` and
`war_room.py` style in the package.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


class CryptoUnavailableError(RuntimeError):
    """Raised when the cryptography backend cannot be loaded.

    Callers may catch either CryptoUnavailableError or RuntimeError.
    The underlying cause is typically _cffi_backend absent from the
    environment, causing pyo3 to panic when cryptography's Rust
    extension initializes.

    Resolution: pip install cryptography, or ensure the cryptography
    package is built for this Python environment.
    """


@dataclass(frozen=True)
class Challenge:
    """Cryptographic challenge for a scenario.

    `challenge_hash` is SHA3-256 of the proof data.
    `nonce` is a unique 32-byte hex token (single-use).
    `timestamp` is the ISO-8601 creation time.
    `difficulty` is the scenario difficulty (1-10).
    `signature` is HMAC-SHA3-256 of the proof data.
    `proof_data` is the canonical data being signed.
    """

    challenge_hash: str
    nonce: str
    timestamp: str
    difficulty: int
    signature: str
    proof_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict (matches the legacy public surface)."""
        return {
            "challenge_hash": self.challenge_hash,
            "nonce": self.nonce,
            "timestamp": self.timestamp,
            "difficulty": self.difficulty,
            "signature": self.signature,
            "proof_data": self.proof_data,
        }


@dataclass(frozen=True)
class AuditLogEntry:
    """Tamper-evident audit log entry.

    `id` is a unique 16-byte hex token.
    `timestamp` is the ISO-8601 creation time.
    `event` is the original event payload.
    `hash` is SHA3-256 of the (id, timestamp, event) canonical form.
    `signature` is HMAC-SHA3-256 of the hash.
    """

    id: str
    timestamp: str
    event: dict[str, Any]
    hash: str
    signature: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "event": self.event,
            "hash": self.hash,
            "signature": self.signature,
        }


class CryptoEngine:
    """Cryptographic operations engine for secure scenario validation.

    Always-available surface (no external deps):
      - generate_challenge
      - verify_response
      - generate_proof (HMAC-based, not formal ZK)
      - verify_proof
      - create_audit_log_entry
      - verify_audit_log_entry

    Optional surface (requires `cryptography` dep):
      - encrypt_sensitive_data (Fernet)
      - decrypt_sensitive_data (Fernet)
      - derive_key (PBKDF2HMAC)

    The optional surface raises CryptoUnavailableError at the
    call site if the cryptography backend is not present.
    """

    def __init__(self, master_key: bytes | None = None) -> None:
        """Initialize the cryptographic engine.

        Args:
            master_key: Optional master key for deterministic operations.
                If not provided, a random Fernet key is generated
                (which requires the `cryptography` dep).

        Raises:
            CryptoUnavailableError: If the cryptography backend
                (Fernet) is required (no master_key provided) and
                is not available. HMAC + SHA3 always work; the
                engine is usable for the always-available surface
                even without the cryptography backend, but a
                master_key must be provided in that case.
        """
        # Always-available: HMAC + SHA3
        self._nonce_cache: set[str] = set()

        # Optional: cryptography backend (Fernet, PBKDF2HMAC)
        self._cipher: Any = None
        self._PBKDF2HMAC: Any = None
        self._hashes: Any = None
        self._default_backend: Any = None

        if master_key is None:
            try:
                from cryptography.fernet import Fernet

                self.master_key = Fernet.generate_key()
                self._cipher = Fernet(self.master_key)
            except (SystemExit, KeyboardInterrupt):
                raise
            except BaseException as exc:
                raise CryptoUnavailableError(
                    f"cryptography backend unavailable "
                    f"({type(exc).__name__}: {exc}). "
                    f"Either install the cryptography package or "
                    f"pass an explicit master_key. The always-available "
                    f"surface (HMAC + SHA3) is still usable."
                ) from None
        else:
            self.master_key = master_key
            # If a master_key is provided, skip Fernet (caller owns
            # the cipher). The encrypt/decrypt methods will fail
            # if the cryptography backend is missing.
            try:
                from cryptography.fernet import Fernet

                self._cipher = Fernet(self.master_key)
            except (SystemExit, KeyboardInterrupt):
                raise
            except BaseException:
                # Master key provided; caller doesn't need Fernet
                # for HMAC + SHA3. encrypt/decrypt will raise.
                pass

    # ── Always-available surface ─────────────────────

    def generate_challenge(self, scenario_id: str, difficulty: int) -> dict[str, Any]:
        """Generate cryptographic challenge for a scenario.

        Args:
            scenario_id: Unique scenario identifier.
            difficulty: Challenge difficulty (1-10).

        Returns:
            Challenge dictionary (also accessible as a
            Challenge dataclass via Challenge.from_dict).
        """
        nonce = secrets.token_hex(32)
        timestamp = datetime.utcnow().isoformat()

        challenge_data = f"{scenario_id}:{nonce}:{timestamp}:{difficulty}"
        challenge_hash = hashlib.sha3_256(challenge_data.encode()).hexdigest()

        proof_data = {
            "scenario_id": scenario_id,
            "nonce": nonce,
            "timestamp": timestamp,
            "difficulty": difficulty,
            "challenge_hash": challenge_hash,
        }

        signature = self._sign_data(json.dumps(proof_data, sort_keys=True))
        self._nonce_cache.add(nonce)

        return {
            "challenge_hash": challenge_hash,
            "nonce": nonce,
            "timestamp": timestamp,
            "difficulty": difficulty,
            "signature": signature,
            "proof_data": proof_data,
        }

    def verify_response(
        self,
        challenge: dict[str, Any],
        response: dict[str, Any],
        expected_outcome: str,
    ) -> tuple[bool, str | None]:
        """Verify cryptographic response to a challenge.

        Args:
            challenge: Original challenge data.
            response: AI system response.
            expected_outcome: Expected decision outcome.

        Returns:
            (is_valid, error_message). error_message is None on
            success.
        """
        nonce = challenge.get("nonce")
        if not nonce or nonce not in self._nonce_cache:
            return False, "Invalid or reused nonce"

        proof_data = challenge.get("proof_data")
        signature = challenge.get("signature")

        if not self._verify_signature(json.dumps(proof_data, sort_keys=True), str(signature)):
            return False, "Invalid challenge signature"

        self._hash_response(response)

        decision = response.get("decision", "")
        if decision.lower() != expected_outcome.lower():
            return False, f"Expected '{expected_outcome}', got '{decision}'"

        self._nonce_cache.discard(nonce)
        return True, None

    def generate_proof(self, data: dict[str, Any], proof_type: str) -> str:
        """Generate cryptographic proof for data.

        Note: This is HMAC-based (a hash commitment + signature),
        not a formal zero-knowledge proof system.

        Args:
            data: Data to generate proof for.
            proof_type: Type of proof (decision, compliance, audit).

        Returns:
            "proof_hash:signature" string.
        """
        serialized = json.dumps(data, sort_keys=True)
        proof_input = f"{proof_type}:{serialized}:{datetime.utcnow().isoformat()}"
        proof_hash = hashlib.sha3_512(proof_input.encode()).hexdigest()
        signature = self._sign_data(proof_hash)
        return f"{proof_hash}:{signature}"

    def verify_proof(self, proof: str, data: dict[str, Any], proof_type: str) -> bool:
        """Verify cryptographic proof.

        Args:
            proof: Proof string ("proof_hash:signature").
            data: Original data (used for re-derivation check
                is NOT performed here; the proof is verified
                against the signature only, matching the legacy
                behavior).
            proof_type: Expected proof type (not used in the
                signature check; the proof is symmetric under
                any proof_type given a matching signature).

        Returns:
            True if proof is valid.
        """
        # Note: data and proof_type are accepted to match the
        # legacy public surface. The legacy verifier also does
        # not re-derive the proof_hash from the data; it only
        # checks the signature against the proof_hash. This
        # matches the documented behavior of the original
        # engine.
        del data, proof_type  # unused in signature check
        try:
            proof_hash, signature = proof.split(":", 1)
        except ValueError:
            return False
        return self._verify_signature(proof_hash, signature)

    def create_audit_log_entry(self, event: dict[str, Any]) -> dict[str, Any]:
        """Create tamper-evident audit log entry.

        Args:
            event: Event data to log.

        Returns:
            Audit log entry dict with id, timestamp, event, hash,
            signature.
        """
        timestamp = datetime.utcnow().isoformat()
        entry_id = secrets.token_hex(16)

        entry: dict[str, Any] = {
            "id": entry_id,
            "timestamp": timestamp,
            "event": event,
        }

        entry_json = json.dumps(entry, sort_keys=True)
        entry_hash = hashlib.sha3_256(entry_json.encode()).hexdigest()

        entry["hash"] = entry_hash
        entry["signature"] = self._sign_data(entry_hash)

        return entry

    def verify_audit_log_entry(self, entry: dict[str, Any]) -> bool:
        """Verify audit log entry integrity.

        Args:
            entry: Audit log entry to verify.

        Returns:
            True if entry is valid and untampered.
        """
        signature = entry.get("signature")
        stored_hash = entry.get("hash")

        if not signature or not stored_hash:
            return False

        # Reconstruct the canonical entry (without hash/signature)
        entry_copy = {k: v for k, v in entry.items() if k not in ("signature", "hash")}
        entry_json = json.dumps(entry_copy, sort_keys=True)
        computed_hash = hashlib.sha3_256(entry_json.encode()).hexdigest()

        if computed_hash != stored_hash:
            return False

        return self._verify_signature(stored_hash, signature)

    # ── Optional surface (requires cryptography backend) ────

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data using Fernet.

        Raises:
            CryptoUnavailableError: If the cryptography backend
                is not available.
        """
        if self._cipher is None:
            raise CryptoUnavailableError("cryptography backend unavailable; cannot encrypt")
        return str(self._cipher.encrypt(data.encode()).decode())

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data using Fernet.

        Raises:
            CryptoUnavailableError: If the cryptography backend
                is not available.
        """
        if self._cipher is None:
            raise CryptoUnavailableError("cryptography backend unavailable; cannot decrypt")
        return str(self._cipher.decrypt(encrypted_data.encode()).decode())

    def derive_key(self, password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
        """Derive cryptographic key from password using PBKDF2-HMAC.

        Args:
            password: Password to derive key from.
            salt: Optional salt (generated if not provided).

        Returns:
            (derived_key, salt).

        Raises:
            CryptoUnavailableError: If the cryptography backend
                is not available.
        """
        if self._PBKDF2HMAC is None:
            try:
                from cryptography.hazmat.backends import default_backend
                from cryptography.hazmat.primitives import hashes
                from cryptography.hazmat.primitives.kdf.pbkdf2 import (
                    PBKDF2HMAC,
                )

                self._PBKDF2HMAC = PBKDF2HMAC
                self._hashes = hashes
                self._default_backend = default_backend
            except (SystemExit, KeyboardInterrupt):
                raise
            except BaseException as exc:
                raise CryptoUnavailableError(
                    f"cryptography backend unavailable ({type(exc).__name__}: {exc})"
                ) from None

        if salt is None:
            salt = secrets.token_bytes(32)

        kdf = self._PBKDF2HMAC(
            algorithm=self._hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self._default_backend(),
        )

        key = kdf.derive(password.encode())
        return key, salt

    # ── Private helpers ─────────────────────────────

    def _sign_data(self, data: str) -> str:
        """Create HMAC-SHA3-256 signature for data."""
        return hmac.new(self.master_key, data.encode(), hashlib.sha3_256).hexdigest()

    def _verify_signature(self, data: str, signature: str) -> bool:
        """Verify HMAC-SHA3-256 signature."""
        expected_signature = self._sign_data(data)
        return hmac.compare_digest(expected_signature, signature)

    def _hash_response(self, response: dict[str, Any]) -> str:
        """Generate SHA3-256 hash of response data."""
        response_json = json.dumps(response, sort_keys=True)
        return hashlib.sha3_256(response_json.encode()).hexdigest()


__all__ = [
    "AuditLogEntry",
    "Challenge",
    "CryptoEngine",
    "CryptoUnavailableError",
]
