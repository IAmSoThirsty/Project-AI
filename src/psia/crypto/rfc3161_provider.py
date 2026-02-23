"""
RFC 3161 Local Timestamp Authority — Cryptographic Temporal Anchoring.

Implements a local RFC 3161-compliant Timestamp Authority (TSA) for the
PSIA ledger's temporal anchoring requirements.

RFC 3161 (Internet X.509 PKI Time-Stamp Protocol) specifies:
    - TimeStampReq:  hash algorithm + message imprint + nonce
    - TimeStampResp: status + TimeStampToken
    - TimeStampToken: version, policy, message imprint, serial, gen_time,
                      accuracy, ordering, nonce, TSA name, extensions

This implementation provides:
    1. A local TSA that signs timestamps with Ed25519 (not X.509 certs,
       since PSIA uses Ed25519 throughout — same security guarantees)
    2. Timestamp request/response protocol following RFC 3161 §2.4
    3. Nonce-based replay protection
    4. Serial number monotonicity
    5. Verification of timestamp tokens against the TSA's public key

Limitations vs. full RFC 3161:
    - Uses Ed25519 instead of RSA/ECDSA with X.509 (PSIA design choice)
    - No ASN.1/DER encoding (uses JSON-serializable structures)
    - Local TSA only (no external TSA integration — future work)
    - Accuracy is best-effort (depends on system clock, not NTP-verified)

Security:
    - Each timestamp is Ed25519-signed over (hash + serial + gen_time + nonce)
    - Nonces are tracked to prevent replay
    - Serial numbers are monotonically increasing
    - TSA private key is held in Ed25519Provider.KeyStore
"""

from __future__ import annotations


import logging
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from psia.crypto.ed25519_provider import Ed25519KeyPair, Ed25519Provider

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TimeStampToken:
    """RFC 3161 §2.4.2 TimeStampToken (JSON-structured variant).

    Attributes:
        version:          Protocol version (always 1).
        policy_oid:       TSA policy identifier.
        hash_algorithm:   Hash algorithm used for message imprint (SHA-256).
        message_imprint:  SHA-256 hash of the timestamped data.
        serial_number:    Monotonically increasing serial number.
        gen_time:         ISO-8601 timestamp of token generation.
        accuracy_ms:      Accuracy of the timestamp in milliseconds.
        ordering:         Whether tokens from this TSA are ordered.
        nonce:            Client-supplied nonce for replay protection.
        tsa_name:         Name/identifier of the TSA.
        tsa_public_key:   Hex-encoded Ed25519 public key of the TSA.
        signature:        Ed25519 signature over the token content.
    """

    version: int
    policy_oid: str
    hash_algorithm: str
    message_imprint: str
    serial_number: int
    gen_time: str
    accuracy_ms: int
    ordering: bool
    nonce: str
    tsa_name: str
    tsa_public_key: str
    signature: str

    def compute_signed_content(self) -> str:
        """Compute the canonical string that was signed.

        This is the content over which the Ed25519 signature is computed,
        matching RFC 3161 §2.4.2's signed-data structure.
        """
        return (
            f"{self.version}:{self.policy_oid}:{self.hash_algorithm}:"
            f"{self.message_imprint}:{self.serial_number}:{self.gen_time}:"
            f"{self.nonce}:{self.tsa_name}"
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for JSON export."""
        return {
            "version": self.version,
            "policy_oid": self.policy_oid,
            "hash_algorithm": self.hash_algorithm,
            "message_imprint": self.message_imprint,
            "serial_number": self.serial_number,
            "gen_time": self.gen_time,
            "accuracy_ms": self.accuracy_ms,
            "ordering": self.ordering,
            "nonce": self.nonce,
            "tsa_name": self.tsa_name,
            "tsa_public_key": self.tsa_public_key,
            "signature": self.signature,
        }


@dataclass(frozen=True)
class TimeStampRequest:
    """RFC 3161 §2.4.1 TimeStampReq.

    Attributes:
        hash_algorithm:  Hash algorithm (always "SHA-256").
        message_imprint: SHA-256 hash of the data to timestamp.
        nonce:           Client nonce for replay protection.
        cert_req:        Whether to include TSA cert in response.
    """

    hash_algorithm: str = "SHA-256"
    message_imprint: str = ""
    nonce: str = ""
    cert_req: bool = True


@dataclass(frozen=True)
class TimeStampResponse:
    """RFC 3161 §2.4.2 TimeStampResp.

    Attributes:
        status:    Response status (0=granted, 1=rejection).
        status_string: Human-readable status message.
        token:     The TimeStampToken (None if rejected).
        failure_info: Failure reason if rejected.
    """

    status: int
    status_string: str
    token: TimeStampToken | None = None
    failure_info: str | None = None


class LocalTSA:
    """Local RFC 3161-compliant Timestamp Authority.

    Provides Ed25519-signed timestamps for PSIA ledger block anchoring.

    Thread-safety:
        Serial number increment and nonce tracking are protected by a lock.
        Multiple concurrent timestamp requests are safe.

    Args:
        tsa_name:      Human-readable TSA name.
        policy_oid:    TSA policy OID (default: PSIA-specific OID).
        accuracy_ms:   Claimed accuracy in milliseconds.
        keypair:       Optional pre-existing keypair. Generated if None.
    """

    # PSIA-specific policy OID (1.3.6.1.4.1.99999.1.1 — private enterprise arc)
    DEFAULT_POLICY_OID = "1.3.6.1.4.1.99999.1.1"

    def __init__(
        self,
        *,
        tsa_name: str = "PSIA-LocalTSA",
        policy_oid: str = DEFAULT_POLICY_OID,
        accuracy_ms: int = 1000,
        keypair: Ed25519KeyPair | None = None,
    ) -> None:
        self.tsa_name = tsa_name
        self.policy_oid = policy_oid
        self.accuracy_ms = accuracy_ms

        # Generate or use provided keypair
        if keypair is None:
            self._keypair = Ed25519Provider.generate_keypair("tsa_authority")
        else:
            self._keypair = keypair

        self._serial_counter = 0
        self._used_nonces: set[str] = set()
        self._lock = threading.Lock()

        logger.info(
            "LocalTSA initialized: name=%s policy=%s pub=%s…",
            tsa_name,
            policy_oid,
            self._keypair.public_key_hex[:16],
        )

    @property
    def public_key_hex(self) -> str:
        """The TSA's Ed25519 public key in hex."""
        return self._keypair.public_key_hex

    @property
    def public_key(self):
        """The TSA's Ed25519 public key object."""
        return self._keypair.public_key

    def request_timestamp(
        self,
        data_hash: str,
        *,
        nonce: str | None = None,
    ) -> TimeStampResponse:
        """Generate a signed timestamp for a data hash.

        Follows RFC 3161 §2.4:
        1. Validate the request (hash format, nonce uniqueness)
        2. Generate timestamp token with monotonic serial number
        3. Sign the token with the TSA's Ed25519 private key
        4. Return the response

        Args:
            data_hash: SHA-256 hex hash of the data to timestamp.
            nonce:     Optional client nonce. Auto-generated if None.

        Returns:
            TimeStampResponse with status and token.
        """
        if nonce is None:
            nonce = uuid.uuid4().hex

        # Validate hash format
        if not data_hash or len(data_hash) != 64:
            return TimeStampResponse(
                status=1,
                status_string="rejection",
                failure_info="Invalid message imprint: expected 64-char SHA-256 hex",
            )

        with self._lock:
            # Replay protection
            if nonce in self._used_nonces:
                return TimeStampResponse(
                    status=1,
                    status_string="rejection",
                    failure_info=f"Nonce already used: {nonce}",
                )

            # Monotonic serial number
            self._serial_counter += 1
            serial = self._serial_counter
            self._used_nonces.add(nonce)

        gen_time = datetime.now(timezone.utc).isoformat()

        # Build the token (unsigned first, to compute signed content)
        unsigned_token = TimeStampToken(
            version=1,
            policy_oid=self.policy_oid,
            hash_algorithm="SHA-256",
            message_imprint=data_hash,
            serial_number=serial,
            gen_time=gen_time,
            accuracy_ms=self.accuracy_ms,
            ordering=True,
            nonce=nonce,
            tsa_name=self.tsa_name,
            tsa_public_key=self._keypair.public_key_hex,
            signature="",  # Placeholder
        )

        # Sign the canonical content
        signed_content = unsigned_token.compute_signed_content()
        signature = Ed25519Provider.sign_string(
            self._keypair.private_key, signed_content
        )

        # Create the final signed token
        token = TimeStampToken(
            version=unsigned_token.version,
            policy_oid=unsigned_token.policy_oid,
            hash_algorithm=unsigned_token.hash_algorithm,
            message_imprint=unsigned_token.message_imprint,
            serial_number=unsigned_token.serial_number,
            gen_time=unsigned_token.gen_time,
            accuracy_ms=unsigned_token.accuracy_ms,
            ordering=unsigned_token.ordering,
            nonce=unsigned_token.nonce,
            tsa_name=unsigned_token.tsa_name,
            tsa_public_key=unsigned_token.tsa_public_key,
            signature=signature,
        )

        logger.debug(
            "Timestamp issued: serial=%d hash=%s…",
            serial,
            data_hash[:16],
        )

        return TimeStampResponse(
            status=0,
            status_string="granted",
            token=token,
        )

    def verify_timestamp(
        self,
        token: TimeStampToken,
        data_hash: str | None = None,
    ) -> bool:
        """Verify a TimeStampToken.

        Checks:
        1. Signature is valid against the TSA's public key
        2. Message imprint matches data_hash (if provided)
        3. Hash algorithm is supported (SHA-256)

        Args:
            token:     The TimeStampToken to verify.
            data_hash: Optional data hash to verify against message_imprint.

        Returns:
            True if the token is valid.
        """
        # Check hash algorithm
        if token.hash_algorithm != "SHA-256":
            logger.warning("Unsupported hash algorithm: %s", token.hash_algorithm)
            return False

        # Check message imprint matches (if data_hash provided)
        if data_hash is not None and token.message_imprint != data_hash:
            logger.warning("Message imprint mismatch")
            return False

        # Verify Ed25519 signature
        signed_content = token.compute_signed_content()
        valid = Ed25519Provider.verify_string(
            self._keypair.public_key,
            token.signature,
            signed_content,
        )

        if not valid:
            logger.warning("Timestamp signature verification failed")

        return valid

    @staticmethod
    def verify_with_public_key(
        token: TimeStampToken,
        public_key_hex: str,
    ) -> bool:
        """Verify a timestamp using a standalone public key (no TSA instance needed).

        Used for offline/remote verification where the TSA instance is not available.

        Args:
            token:          The TimeStampToken to verify.
            public_key_hex: Hex-encoded Ed25519 public key of the TSA.

        Returns:
            True if the signature is valid.
        """
        try:
            pub_key = Ed25519Provider.load_public_key(public_key_hex)
            signed_content = token.compute_signed_content()
            return Ed25519Provider.verify_string(
                pub_key, token.signature, signed_content
            )
        except (ValueError, Exception):
            return False

    @property
    def serial_count(self) -> int:
        """Number of timestamps issued."""
        return self._serial_counter


__all__ = [
    "LocalTSA",
    "TimeStampToken",
    "TimeStampRequest",
    "TimeStampResponse",
]
