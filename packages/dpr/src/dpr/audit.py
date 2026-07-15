"""
Cryptographic audit substrate for DPR.

Real Ed25519 signing (cryptography library) + SHA-256 hash-linked chain.
No simulated crypto. verify() genuinely recomputes hashes and checks
signatures; any tamper to any prior entry breaks verification from that
entry forward (chain-of-custody property).
"""

from __future__ import annotations

import base64
import hashlib
import json

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def canonical_json(obj) -> bytes:
    """Deterministic canonical JSON: sorted keys, fixed separators, no whitespace drift."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Signer:
    """Wraps an Ed25519 keypair. One Signer == one authority identity."""

    def __init__(self, private_key: Ed25519PrivateKey | None = None):
        self._sk = private_key or Ed25519PrivateKey.generate()
        self._pk = self._sk.public_key()

    def public_key_b64(self) -> str:
        raw = self._pk.public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
        )
        return base64.b64encode(raw).decode("ascii")

    def sign(self, data: bytes) -> str:
        return base64.b64encode(self._sk.sign(data)).decode("ascii")

    @staticmethod
    def verify(public_key_b64: str, data: bytes, signature_b64: str) -> bool:
        try:
            raw = base64.b64decode(public_key_b64)
            pk = Ed25519PublicKey.from_public_bytes(raw)
            pk.verify(base64.b64decode(signature_b64), data)
            return True
        except InvalidSignature:
            return False
        except Exception:
            return False


class AuditChain:
    """
    Append-only, hash-linked, signed audit chain.

    Each entry = decision payload + prev_hash, hashed with SHA-256, then
    the hash is Ed25519-signed. verify() walks the chain and fails at the
    first point of tamper (wrong prev_hash link, recomputed hash mismatch,
    or invalid signature) -> maps directly to CHAIN_CORRUPTION /
    AUDIT_TAMPERING failure modes.
    """

    GENESIS = "0" * 64

    def __init__(self, signer: Signer):
        self.signer = signer
        self.entries: list = []

    def append(self, decision_payload: dict) -> dict:
        prev_hash = self.entries[-1]["audit_hash"] if self.entries else self.GENESIS
        payload = dict(decision_payload)
        payload["prev_hash"] = prev_hash
        body = canonical_json(payload)
        audit_hash = sha256_hex(body)
        signature = self.signer.sign(bytes.fromhex(audit_hash))
        entry = dict(payload)
        entry["audit_hash"] = audit_hash
        entry["signature"] = signature
        self.entries.append(entry)
        return entry

    def verify(self):
        """Returns (ok: bool, first_bad_index: Optional[int], reason: Optional[str])."""
        prev_hash = self.GENESIS
        for i, entry in enumerate(self.entries):
            check = dict(entry)
            audit_hash = check.pop("audit_hash", None)
            signature = check.pop("signature", None)
            if audit_hash is None or signature is None:
                return False, i, "missing audit_hash/signature"
            if check.get("prev_hash") != prev_hash:
                return False, i, "prev_hash link broken (CHAIN_CORRUPTION)"
            recomputed = sha256_hex(canonical_json(check))
            if recomputed != audit_hash:
                return False, i, "hash mismatch (AUDIT_TAMPERING)"
            if not Signer.verify(
                self.signer.public_key_b64(), bytes.fromhex(audit_hash), signature
            ):
                return False, i, "signature invalid (AUDIT_TAMPERING)"
            prev_hash = audit_hash
        return True, None, None
