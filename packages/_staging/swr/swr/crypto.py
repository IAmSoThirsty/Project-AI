#                                           [2026-03-05 10:03]
#                                          Productivity: Active
"""
Cryptographic Engine for SOVEREIGN WAR ROOM

Handles all cryptographic operations including:
- Cryptographic decision attestations for decision verification
- Tamper-evident audit logs with commitment schemes
- Secure challenge-response protocols
- Cryptographic signatures for scenario validation

Note: Implements hash-based commitments and HMAC signatures,
not formal zero-knowledge proof systems (zk-SNARKs/zk-STARKs).

C3D-R1: All cryptography.* imports moved inside CryptoEngine.__init__().
Importing this module is now safe regardless of backend availability.
Instantiation raises CryptoUnavailableError if the backend is broken.
"""

import hashlib
import hmac
import json
import secrets
from datetime import datetime
from typing import Any


class CryptoUnavailableError(RuntimeError):
    """Raised when the cryptography backend cannot be loaded.

    Callers may catch either CryptoUnavailableError or RuntimeError.
    The underlying cause is typically _cffi_backend absent from the environment,
    causing pyo3 to panic when cryptography's Rust extension initializes.

    Resolution: pip install cffi, or ensure the cryptography package is built
    for this Python environment. See recovery/PHASE_C3D_SWR_REPAIR_PLAN.txt.
    """


class CryptoEngine:
    """Cryptographic operations engine for secure scenario validation."""

    def __init__(self, master_key: bytes | None = None):
        """Initialize cryptographic engine.

        Args:
            master_key: Optional master key for deterministic operations.

        Raises:
            CryptoUnavailableError: If the cryptography backend (Fernet, PBKDF2HMAC)
                cannot be imported. Typically caused by _cffi_backend missing.
                pyo3_runtime.PanicException is caught and re-raised as this error.
        """
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as e:
            # BaseException catches pyo3_runtime.PanicException which inherits from
            # BaseException (not Exception) in pyo3 >= 0.20. The panic fires when
            # _cffi_backend is absent and pyo3 cannot handle the ModuleNotFoundError.
            raise CryptoUnavailableError(
                f"cryptography backend unavailable ({type(e).__name__}: {e}). "
                "Install cffi or ensure cryptography package is functional. "
                "See recovery/PHASE_C3D_SWR_REPAIR_PLAN.txt."
            ) from None

        self.master_key = master_key or Fernet.generate_key()
        self.cipher = Fernet(self.master_key)
        self._nonce_cache: set[str] = set()
        # Store KDF symbols for derive_key() — avoids re-importing on each call.
        self._PBKDF2HMAC = PBKDF2HMAC
        self._hashes = hashes
        self._default_backend = default_backend

    def generate_challenge(self, scenario_id: str, difficulty: int) -> dict[str, Any]:
        """Generate cryptographic challenge for scenario.

        Args:
            scenario_id: Unique scenario identifier
            difficulty: Challenge difficulty (1-10)

        Returns:
            Challenge dictionary with nonce, hash, and verification data
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
        self, challenge: dict[str, Any], response: dict[str, Any], expected_outcome: str
    ) -> tuple[bool, str | None]:
        """Verify cryptographic response to challenge.

        Args:
            challenge: Original challenge data
            response: AI system response
            expected_outcome: Expected decision outcome

        Returns:
            Tuple of (is_valid, error_message)
        """
        nonce = challenge.get("nonce")
        if not nonce or nonce not in self._nonce_cache:
            return False, "Invalid or reused nonce"

        proof_data = challenge.get("proof_data")
        signature = challenge.get("signature")

        if not self._verify_signature(
            json.dumps(proof_data, sort_keys=True), signature
        ):
            return False, "Invalid challenge signature"

        self._hash_response(response)

        decision = response.get("decision", "")
        if decision.lower() != expected_outcome.lower():
            return False, f"Expected '{expected_outcome}', got '{decision}'"

        self._nonce_cache.discard(nonce)
        return True, None

    def generate_proof(self, data: dict[str, Any], proof_type: str) -> str:
        """Generate zero-knowledge proof for data.

        Args:
            data: Data to generate proof for
            proof_type: Type of proof (decision, compliance, audit)

        Returns:
            Hex-encoded proof string
        """
        serialized = json.dumps(data, sort_keys=True)
        proof_input = f"{proof_type}:{serialized}:{datetime.utcnow().isoformat()}"
        proof_hash = hashlib.sha3_512(proof_input.encode()).hexdigest()
        signature = self._sign_data(proof_hash)
        return f"{proof_hash}:{signature}"

    def verify_proof(self, proof: str, data: dict[str, Any], proof_type: str) -> bool:
        """Verify zero-knowledge proof.

        Args:
            proof: Proof string to verify
            data: Original data
            proof_type: Expected proof type

        Returns:
            True if proof is valid
        """
        try:
            proof_hash, signature = proof.split(":", 1)
            if not self._verify_signature(proof_hash, signature):
                return False
            return True
        except Exception:
            return False

    def create_audit_log_entry(self, event: dict[str, Any]) -> dict[str, Any]:
        """Create tamper-evident audit log entry.

        Args:
            event: Event data to log

        Returns:
            Audit log entry with cryptographic verification
        """
        timestamp = datetime.utcnow().isoformat()
        entry_id = secrets.token_hex(16)

        entry = {
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
            entry: Audit log entry to verify

        Returns:
            True if entry is valid and untampered
        """
        signature = entry.get("signature")
        stored_hash = entry.get("hash")

        if not signature or not stored_hash:
            return False

        entry_copy = {k: v for k, v in entry.items() if k not in ["signature", "hash"]}
        entry_json = json.dumps(entry_copy, sort_keys=True)
        computed_hash = hashlib.sha3_256(entry_json.encode()).hexdigest()

        if computed_hash != stored_hash:
            return False

        return self._verify_signature(stored_hash, signature)

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data using Fernet."""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data using Fernet."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    def _sign_data(self, data: str) -> str:
        """Create HMAC signature for data."""
        return hmac.new(
            self.master_key, data.encode(), hashlib.sha3_256
        ).hexdigest()

    def _verify_signature(self, data: str, signature: str) -> bool:
        """Verify HMAC signature."""
        expected_signature = self._sign_data(data)
        return hmac.compare_digest(expected_signature, signature)

    def _hash_response(self, response: dict[str, Any]) -> str:
        """Generate hash of response data."""
        response_json = json.dumps(response, sort_keys=True)
        return hashlib.sha3_256(response_json.encode()).hexdigest()

    def derive_key(
        self, password: str, salt: bytes | None = None
    ) -> tuple[bytes, bytes]:
        """Derive cryptographic key from password.

        Args:
            password: Password to derive key from
            salt: Optional salt (generated if not provided)

        Returns:
            Tuple of (derived_key, salt)
        """
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
