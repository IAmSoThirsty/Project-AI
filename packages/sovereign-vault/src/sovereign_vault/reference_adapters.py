"""
sovereign_vault.reference_adapters

Concrete, working implementations of the interfaces.py ABCs — for TESTS
and local development ONLY. In production, wire real adapters onto CBCC's
existing audit chain and threshold sealing, your real STATE_REGISTER/
T.A.R.L. for authority, and real TPM/USB stacks for attestation and
token. Do not deploy these.

InMemoryAuditChain is a minimal but real hash-linked, Ed25519-signed
append-only log — enough to exercise this package's rollback/audit-
unavailable logic in tests without depending on CBCC's actual package
(which this repo does not have access to). It is NOT a substitute for
CBCC's canonical audit chain and must not be treated as one.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from .interfaces import (
    AttestationProvider,
    AuditChainProvider,
    AuthorityProvider,
    AuthorityToken,
    TokenProvider,
)
from .primitives import SigningIdentity, verify_signature


@dataclass
class InMemoryAuditChain(AuditChainProvider):
    signer: SigningIdentity = field(default_factory=SigningIdentity.generate)
    capacity_remaining: int = 10_000
    entries: list[dict[str, object]] = field(default_factory=list)
    _last_hash: str = "0" * 64

    def has_capacity(self) -> bool:
        return self.capacity_remaining > 0

    def append(self, event_type: str, payload: dict[str, object]) -> str:
        if not self.has_capacity():
            from .errors import AuditUnavailableError

            raise AuditUnavailableError("InMemoryAuditChain: reserved capacity exhausted")
        body = {
            "index": len(self.entries),
            "prev_hash": self._last_hash,
            "event_type": event_type,
            "payload": payload,
        }
        canon = json.dumps(body, sort_keys=True, default=str).encode("utf-8")
        entry_hash = hashlib.sha256(canon).hexdigest()
        signature = self.signer.sign(canon)
        self.entries.append({**body, "hash": entry_hash, "signature": signature.hex()})
        self._last_hash = entry_hash
        self.capacity_remaining -= 1
        return entry_hash

    def verify_chain(self) -> bool:
        prev = "0" * 64
        for e in self.entries:
            body = {k: e[k] for k in ("index", "prev_hash", "event_type", "payload")}
            canon = json.dumps(body, sort_keys=True, default=str).encode("utf-8")
            if e["prev_hash"] != prev:
                return False
            if hashlib.sha256(canon).hexdigest() != e["hash"]:
                return False
            if not verify_signature(
                self.signer.public_bytes(), canon, bytes.fromhex(str(e["signature"]))
            ):
                return False
            prev = e["hash"]
        return True


@dataclass
class AllowAllAuthorityProvider(AuthorityProvider):
    """Grants any scope. For tests only — production must wire real
    STATE_REGISTER/T.A.R.L. verification."""

    def verify(self, token: AuthorityToken, required_scope: str) -> bool:
        return token.scope == required_scope or token.scope == "*"


@dataclass
class AlwaysAttestProvider(AttestationProvider):
    fail: bool = False

    def attest(self, nonce: bytes) -> bool:
        return not self.fail

    def sealed_key_release(self, nonce: bytes) -> bytes:
        if self.fail:
            from .errors import SafeHaltError

            raise SafeHaltError("AlwaysAttestProvider: configured to fail")
        return hashlib.sha256(b"tpm-share|" + nonce).digest()


@dataclass
class StaticTokenProvider(TokenProvider):
    share: bytes
    present: bool = True

    def read_share(self) -> bytes:
        if not self.present:
            from .errors import SafeHaltError

            raise SafeHaltError("StaticTokenProvider: token not present")
        return self.share

    def is_present(self) -> bool:
        return self.present
