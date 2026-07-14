"""
sovereign_vault.errors

Every failure mode in this package raises one of these. There is no
silent-degrade path: any function that cannot complete a security-relevant
check raises rather than returning a permissive default.
"""


class SafeHaltError(Exception):
    """
    Base class for all fail-closed halts.

    Raised whenever a required invariant is unproven — not just when it is
    proven false. Unknown state is treated identically to bad state.
    """


class UncertainStateError(SafeHaltError):
    """
    A RuntimeConditions field was never explicitly set to True/False before
    a gated operation was attempted. Absence of proof is not proof of
    safety, so this halts exactly like an explicit False would.
    """


class RollbackDetectedError(SafeHaltError):
    """Vault state (metadata, policy, revocation list, checkpoint) is at
    or behind a sequence number already observed. Refuses to proceed."""


class AuditUnavailableError(SafeHaltError):
    """Audit chain cannot currently accept a write (reserved capacity
    exhausted, checkpoint witness unreachable, logger offline)."""


class TamperDetectedError(SafeHaltError):
    """A tamper event fired and the configured response was SEAL/REVOKE/
    FORCE_RECOVERY rather than a resumable state."""


class QuorumNotMetError(SafeHaltError):
    """Recovery or other quorum-gated operation attempted without k valid,
    distinct, unexpired approver signatures."""


class AuthorityNotProvenError(SafeHaltError):
    """Caller did not present a verifiable, unexpired, correctly-scoped
    capability/authority token. Implied or inherited authority is not
    accepted."""


class AdmissionRejectedError(SafeHaltError):
    """An object was presented for storage without a complete, verifiable
    AdmissionRecord (provenance, hash, signature, approval)."""


class RevokedError(SafeHaltError):
    """Token, key epoch, or capability has been revoked."""


class BackupIntegrityError(SafeHaltError):
    """A backup bundle is missing a required control component, or would
    roll vault state backward if restored."""
