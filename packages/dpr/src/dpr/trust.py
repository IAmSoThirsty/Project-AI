"""
Phase 2 — verifiable authority.

Closes the Phase 1 gap: "authority grants must not be trusted as data."
Every AuthorityGrant must be signed by its grantor, and the grantor's
public key must be registered in a TrustRoot the engine actually holds.
A grant that is unsigned, signed by an unknown grantor, signed with a
signature that does not verify, or structurally malformed is treated as
an AUTHORITY_FORGERY signal — not a quiet refusal.

Expiry is handled separately: an expired grant is a normal lifecycle
event (REFUSE), not an attack signal (SAFE_HALT).
"""

from __future__ import annotations

from collections.abc import Iterable

from .audit import Signer, canonical_json, sha256_hex
from .models import AuthorityGrant

VALID = "valid"
EXPIRED = "expired"
UNKNOWN_GRANTOR = "unknown_grantor"
UNSIGNED = "unsigned"
INVALID_SIGNATURE = "invalid_signature"
MALFORMED = "malformed"

# statuses that represent an attempted-forgery / impersonation signal,
# as opposed to a benign absence (no grant) or benign lifecycle event (expired)
FORGERY_STATUSES = frozenset({UNKNOWN_GRANTOR, UNSIGNED, INVALID_SIGNATURE, MALFORMED})


def grant_signable_body(grant: AuthorityGrant) -> dict[str, object]:
    """Canonical, deterministic body a grantor signs over. Order-independent
    (dict, hashed via canonical_json) and excludes the signature itself."""
    return {
        "grantor": grant.grantor,
        "grantee": grant.grantee,
        "scope": sorted(grant.scope) if grant.scope else [],
        "expires_at": grant.expires_at,
    }


def grant_hash(grant: AuthorityGrant) -> str:
    """
    Phase 3 grant fingerprint. Decision.authority_used previously stored
    only sorted grantor IDs — that proves WHO could have granted something,
    not WHICH grant actually authorized this decision. grant_hash binds the
    fingerprint to the grant's full signable body AND its signature, so two
    grants with identical (grantor, grantee, scope, expiry) but different
    signatures — e.g. one legitimate, one a bytes-for-bytes forged replay
    attempt with a different signature — fingerprint differently.
    """
    body_bytes = canonical_json(grant_signable_body(grant))
    sig_bytes = (grant.signature or "").encode("utf-8")
    return sha256_hex(body_bytes + b"|" + sig_bytes)


def sign_grant(signer: Signer, grant: AuthorityGrant) -> AuthorityGrant:
    """Convenience: returns a new AuthorityGrant with `signature` populated."""
    body = grant_signable_body(grant)
    sig = signer.sign(canonical_json(body))
    return AuthorityGrant(
        grantor=grant.grantor,
        grantee=grant.grantee,
        scope=grant.scope,
        expires_at=grant.expires_at,
        signature=sig,
    )


def issue_signed_grant(
    signer: Signer,
    grantor: str,
    grantee: str,
    scope: Iterable[str],
    expires_at: float | None = None,
) -> AuthorityGrant:
    """Build + sign an AuthorityGrant in one call. `signer` must be the grantor's key."""
    grant = AuthorityGrant(
        grantor=grantor, grantee=grantee, scope=tuple(scope), expires_at=expires_at
    )
    return sign_grant(signer, grant)


class TrustRoot:
    """
    Registry of grantor_id -> public_key_b64. This is the root of trust:
    if a grantor isn't registered here, no signature it produces can ever
    verify as VALID, regardless of what the grant claims.
    """

    def __init__(self) -> None:
        self._keys: dict[str, str] = {}

    def register(self, grantor_id: str, public_key_b64: str) -> None:
        self._keys[grantor_id] = public_key_b64

    def register_signer(self, grantor_id: str, signer: Signer) -> None:
        self.register(grantor_id, signer.public_key_b64())

    def known(self, grantor_id: str) -> bool:
        return grantor_id in self._keys

    def verify_grant(self, grant: AuthorityGrant, at_time: float) -> str:
        """Returns one of VALID, EXPIRED, UNKNOWN_GRANTOR, UNSIGNED,
        INVALID_SIGNATURE, MALFORMED. Never raises."""
        if not grant.grantor or not grant.grantee or not grant.scope:
            return MALFORMED
        if grant.expires_at is not None and not isinstance(grant.expires_at, (int, float)):
            return MALFORMED

        if grant.grantor not in self._keys:
            return UNKNOWN_GRANTOR

        if not grant.signature:
            return UNSIGNED

        body = grant_signable_body(grant)
        ok = Signer.verify(self._keys[grant.grantor], canonical_json(body), grant.signature)
        if not ok:
            return INVALID_SIGNATURE

        if grant.expires_at is not None and grant.expires_at <= at_time:
            return EXPIRED

        return VALID
