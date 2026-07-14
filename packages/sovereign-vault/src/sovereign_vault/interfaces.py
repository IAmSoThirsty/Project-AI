"""
sovereign_vault.interfaces

This module does NOT reimplement CBCC's Shamir sealing, audit chain, or
T.A.R.L.'s policy evaluation — those already exist and are canonical.
These ABCs are the seam: this package calls them, you wire the concrete
adapters to your real CBCC package, STATE_REGISTER, and TPM stack outside
this file.

Every default implementation fails closed. If you have not wired a real
adapter, calling anything here raises SafeHaltError — it does not
silently no-op or return a permissive default. This mirrors the CCMA
`interfaces.py` seam pattern already in use elsewhere in Project-AI.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .errors import AuditUnavailableError, AuthorityNotProvenError, SafeHaltError


@dataclass(frozen=True)
class AuthorityToken:
    """Opaque proof of authority. `claims` must be whatever your
    STATE_REGISTER / T.A.R.L. capability token format actually is —
    this package does not define or infer capability semantics."""

    subject: str
    scope: str
    raw: bytes  # the actual signed capability token, verbatim
    claims: dict[str, object]


class AuthorityProvider(ABC):
    """Verifies that a presented token actually grants the requested
    scope, right now, for this subject. Authority is proven here, not
    assumed by the caller."""

    @abstractmethod
    def verify(self, token: AuthorityToken, required_scope: str) -> bool: ...


class FailClosedAuthorityProvider(AuthorityProvider):
    def verify(self, token: AuthorityToken, required_scope: str) -> bool:
        raise AuthorityNotProvenError(
            "No AuthorityProvider wired to real STATE_REGISTER/T.A.R.L. — "
            "refusing to assume authority. Inject a concrete provider."
        )


class AttestationProvider(ABC):
    """TPM / hardware attestation. Returns True only for a fresh,
    verified quote matching the expected PCR/measurement set."""

    @abstractmethod
    def attest(self, nonce: bytes) -> bool: ...

    @abstractmethod
    def sealed_key_release(self, nonce: bytes) -> bytes:
        """Release a TPM-sealed key share, gated on the same attestation.
        Must raise, not return zeros/None, on any attestation failure."""
        ...


class FailClosedAttestationProvider(AttestationProvider):
    def attest(self, nonce: bytes) -> bool:
        raise SafeHaltError(
            "No AttestationProvider wired — device identity is unproven. "
            "Refusing to treat an unattested host as trusted."
        )

    def sealed_key_release(self, nonce: bytes) -> bytes:
        raise SafeHaltError("No AttestationProvider wired — cannot release TPM-sealed share.")


class TokenProvider(ABC):
    """USB token reader. Deliberately returns only a *share*, never a
    standalone root — see primitives.combine_factors. Treat the USB
    token's on-device identity fields (serial, VID/PID) as spoofable;
    do not use them as an authentication signal by themselves."""

    @abstractmethod
    def read_share(self) -> bytes: ...

    @abstractmethod
    def is_present(self) -> bool: ...


class FailClosedTokenProvider(TokenProvider):
    def read_share(self) -> bytes:
        raise SafeHaltError(
            "No TokenProvider wired — refusing to derive keys without a token share."
        )

    def is_present(self) -> bool:
        return False


class AuditChainProvider(ABC):
    """Adapter onto your existing CBCC hash-linked Ed25519 audit chain.
    `has_capacity` must be checked and must be True before any
    security-relevant operation proceeds — see errors.AuditUnavailableError."""

    @abstractmethod
    def has_capacity(self) -> bool: ...

    @abstractmethod
    def append(self, event_type: str, payload: dict[str, object]) -> str:
        """Appends a signed, hash-linked entry. Returns the entry's own
        hash/id. Must raise AuditUnavailableError rather than silently
        dropping the event if the chain cannot accept a write."""
        ...

    @abstractmethod
    def verify_chain(self) -> bool: ...


class FailClosedAuditChainProvider(AuditChainProvider):
    def has_capacity(self) -> bool:
        return False

    def append(self, event_type: str, payload: dict[str, object]) -> str:
        raise AuditUnavailableError(
            "No AuditChainProvider wired to real CBCC audit chain — "
            "refusing to perform an unaudited security-relevant operation."
        )

    def verify_chain(self) -> bool:
        raise AuditUnavailableError("No AuditChainProvider wired.")


class SealingProvider(ABC):
    """Adapter onto CBCC's existing Shamir k-of-n threshold sealing, if
    you want vault backup/export sealed under CBCC's threshold scheme
    rather than (or in addition to) this package's own XChaCha20-Poly1305
    object sealing. Optional — object-level sealing in this package does
    not require it."""

    @abstractmethod
    def threshold_seal(self, plaintext: bytes, k: int, n: int) -> list[bytes]: ...

    @abstractmethod
    def threshold_unseal(self, shares: list[bytes]) -> bytes: ...
