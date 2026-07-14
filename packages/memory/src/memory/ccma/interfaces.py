"""
ccma.interfaces

CCMA Law II: "Memory Never Grants Authority." This module is where that
law is enforced structurally, not just stated. The graph store (store.py)
and pipeline (pipeline.py) NEVER decide authority, capability, or audit
validity themselves — they call out to these interfaces.

You wire your real STATE_REGISTER, T.A.R.L., and CBCC implementations in
by subclassing these ABCs. Nothing in this package guesses at your actual
STATE_REGISTER/CBCC call signatures — that integration is yours to write,
because only you have eyes on that repo.

The default implementations provided here are deliberately NOT placeholders
that pretend to work. They are fail-closed stubs: every method raises
SafeHaltError until a real backend is wired in. This means if you run the
pipeline without wiring anything, it halts immediately and loudly instead
of silently granting authority or fabricating a signature. That is the
deny-by-default / SAFE_HALT behavior your other components already expect.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass


class SafeHaltError(RuntimeError):
    """
    Raised whenever the system would otherwise have to guess, assume, or
    silently proceed without verified authority/capability/integrity.
    This is CCMA's SAFE_HALT surfaced as a Python exception — catch it
    at the orchestration boundary, do not swallow it inside a stage.
    """


@dataclass(frozen=True)
class AuthorityToken:
    """
    Result of a successful authority check. Deliberately minimal and
    immutable. `expires_at=None` means "does not expire" — use sparingly,
    since CCMA treats unexpiring authority as a red flag (see Governance
    Memory: "Authority is never inferred. Authority is always established.").
    """

    subject: str  # who/what is authorized
    scope: str  # what they're authorized to do
    granted_by: str  # which authority source granted it
    granted_at: float
    expires_at: float | None
    protected_override: bool = False  # required to resolve PROTECTED nodes

    def is_valid(self, now: float | None = None) -> bool:
        now = now if now is not None else time.time()
        if self.expires_at is not None and now >= self.expires_at:  # noqa: SIM103
            return False
        return True


class AuthorityProvider(ABC):
    """
    Bridge to STATE_REGISTER / your Governance authority store.
    The pipeline calls this before any Execution stage and before any
    Atropos resolution of a PROTECTED node. Implement this against your
    real STATE_REGISTER; do not let the memory graph itself hold the
    source of truth for authority.
    """

    @abstractmethod
    def check_authority(self, subject: str, scope: str) -> AuthorityToken:
        """
        Return a valid AuthorityToken or raise SafeHaltError. Must NOT
        return a token for a scope that wasn't explicitly granted —
        no inference, no defaults, no "probably fine."
        """
        raise NotImplementedError


class DenyByDefaultAuthorityProvider(AuthorityProvider):
    """
    Fail-closed default. Every check halts. Wire your real STATE_REGISTER
    provider before running the pipeline against anything real — this
    exists so that forgetting to wire it fails loud, not quiet.
    """

    def check_authority(self, subject: str, scope: str) -> AuthorityToken:
        raise SafeHaltError(
            f"No AuthorityProvider wired. Denying by default: "
            f"subject={subject!r} scope={scope!r}. "
            f"Wire STATE_REGISTER via a real AuthorityProvider subclass."
        )


class CapabilityChecker(ABC):
    """
    Bridge to T.A.R.L. Checks whether a specific capability is currently
    granted, independent of general authority — CCMA keeps these separate
    ("Capability without authority is prohibited. Authority without
    capability is ineffective. Governance requires both.").
    """

    @abstractmethod
    def check_capability(self, subject: str, capability: str) -> bool:
        raise NotImplementedError


class DenyByDefaultCapabilityChecker(CapabilityChecker):
    def check_capability(self, subject: str, capability: str) -> bool:
        raise SafeHaltError(
            f"No CapabilityChecker wired. Denying by default: "
            f"subject={subject!r} capability={capability!r}. "
            f"Wire T.A.R.L. via a real CapabilityChecker subclass."
        )


@dataclass(frozen=True)
class Signature:
    algorithm: str
    signature_hex: str
    signer_id: str
    signed_at: float


class AuditSigner(ABC):
    """
    Bridge to CBCC. The audit region (evidence, provenance, integrity,
    cryptographic memory) does not implement its own crypto — it calls
    this. Wire it against your actual CBCC package (Shamir sealing,
    XChaCha20-Poly1305, Ed25519 hash-linked chain) rather than
    reimplementing signing logic here.
    """

    @abstractmethod
    def sign(self, payload: bytes) -> Signature:
        raise NotImplementedError

    @abstractmethod
    def verify(self, payload: bytes, signature: Signature) -> bool:
        raise NotImplementedError

    @abstractmethod
    def append_to_chain(self, payload: bytes, signature: Signature) -> str:
        """Append to the hash-linked audit chain, return the new chain ref."""
        raise NotImplementedError


class DenyByDefaultAuditSigner(AuditSigner):
    def sign(self, payload: bytes) -> Signature:
        raise SafeHaltError("No AuditSigner wired. Wire CBCC before signing anything.")

    def verify(self, payload: bytes, signature: Signature) -> bool:
        raise SafeHaltError("No AuditSigner wired. Wire CBCC before verifying anything.")

    def append_to_chain(self, payload: bytes, signature: Signature) -> str:
        raise SafeHaltError("No AuditSigner wired. Wire CBCC before writing to the audit chain.")
