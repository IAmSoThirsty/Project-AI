"""
Capability Authority — Token Issuance, Revocation, and Rotation.

Central authority for managing CapabilityTokens in the PSIA system.
Provides:
    - Token issuance with scope, delegation, and binding
    - Token revocation (immediate and scheduled)
    - Token rotation (issue new, revoke old atomically)
    - Revocation list (CRL) for quick lookup
    - Audit trail of all token lifecycle events

Security invariants:
    - INV-ROOT-3 (No capability bypass — all tokens must be issued by this authority)
    - INV-ROOT-5 (No self-modification — the authority cannot issue tokens to itself)
    - INV-ROOT-6 (Least privilege — scopes are validated for minimal coverage)

Production notes:
    - In production, tokens would be cryptographically signed with Ed25519
    - The CRL would be distributed to all enforcement points
    - Token storage would be backed by a durable, replicated store
    - OCSP-like live status queries would be supported
"""

from __future__ import annotations


import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from psia.crypto.ed25519_provider import Ed25519KeyPair, Ed25519Provider, KeyStore
from psia.schemas.capability import (
    CapabilityScope,
    CapabilityToken,
    DelegationPolicy,
    TokenBinding,
)
from psia.schemas.identity import Signature

logger = logging.getLogger(__name__)


@dataclass
class RevocationEntry:
    """An entry in the capability revocation list."""
    token_id: str
    revoked_at: str
    reason: str
    revoked_by: str


@dataclass
class TokenLifecycleEvent:
    """Audit trail entry for a token lifecycle event."""
    event_type: str  # "issued", "revoked", "rotated", "expired"
    token_id: str
    actor: str
    timestamp: str
    details: dict[str, Any] = field(default_factory=dict)


class CapabilityAuthority:
    """Central authority for CapabilityToken lifecycle management.

    Args:
        authority_did: The DID of this authority (issuer identity)
        default_ttl_hours: Default token TTL in hours
        max_scope_actions: Maximum actions per scope (least privilege)
        allow_delegation: Whether delegation is allowed by default
        max_delegation_depth: Maximum delegation chain depth
    """

    def __init__(
        self,
        *,
        authority_did: str = "did:project-ai:authority:capability",
        default_ttl_hours: int = 24,
        max_scope_actions: int = 10,
        allow_delegation: bool = False,
        max_delegation_depth: int = 2,
        key_store: KeyStore | None = None,
    ) -> None:
        self.authority_did = authority_did
        self.default_ttl_hours = default_ttl_hours
        self.max_scope_actions = max_scope_actions
        self.allow_delegation = allow_delegation
        self.max_delegation_depth = max_delegation_depth

        self._tokens: dict[str, CapabilityToken] = {}
        self._revocation_list: dict[str, RevocationEntry] = {}
        self._audit_log: list[TokenLifecycleEvent] = []

        # Ed25519 keypair for token signing
        if key_store is not None and key_store.get("capability_authority") is not None:
            self._keypair: Ed25519KeyPair = key_store.get("capability_authority")  # type: ignore[assignment]
        else:
            # Generate standalone keypair if no KeyStore provided
            self._keypair = Ed25519Provider.generate_keypair("capability_authority")

    def issue(
        self,
        *,
        subject: str,
        scopes: list[CapabilityScope],
        ttl_hours: int | None = None,
        delegable: bool | None = None,
        max_depth: int | None = None,
        binding: TokenBinding | None = None,
        token_id: str | None = None,
    ) -> CapabilityToken:
        """Issue a new capability token.

        Args:
            subject: The DID of the principal receiving the token
            scopes: List of capability scopes
            ttl_hours: Token TTL in hours (defaults to default_ttl_hours)
            delegable: Whether token is delegable
            max_depth: Max delegation depth
            binding: Optional client certificate binding
            token_id: Optional explicit token ID (auto-generated if None)

        Returns:
            The issued CapabilityToken

        Raises:
            ValueError: If subject is the authority itself (INV-ROOT-5)
            ValueError: If scopes exceed max_scope_actions
        """
        # INV-ROOT-5: Cannot issue tokens to self
        if subject == self.authority_did:
            raise ValueError(
                f"INV-ROOT-5 violation: authority '{self.authority_did}' "
                f"cannot issue tokens to itself"
            )

        # INV-ROOT-6: Least privilege validation
        for scope in scopes:
            if len(scope.actions) > self.max_scope_actions:
                raise ValueError(
                    f"INV-ROOT-6 violation: scope has {len(scope.actions)} actions, "
                    f"max allowed is {self.max_scope_actions}"
                )

        ttl = ttl_hours or self.default_ttl_hours
        now = datetime.now(timezone.utc)
        tid = token_id or f"cap_{uuid.uuid4().hex[:12]}"

        token = CapabilityToken(
            token_id=tid,
            issuer=self.authority_did,
            subject=subject,
            issued_at=now.isoformat(),
            expires_at=(now + timedelta(hours=ttl)).isoformat(),
            nonce=uuid.uuid4().hex,
            scope=scopes,
            delegation=DelegationPolicy(
                is_delegable=delegable if delegable is not None else self.allow_delegation,
                max_depth=max_depth if max_depth is not None else self.max_delegation_depth,
            ),
            binding=binding or TokenBinding(),
            signature=Signature(
                alg="ed25519",
                kid=f"ca_{tid[:8]}",
                sig=self._sign_token(tid),
            ),
        )

        self._tokens[tid] = token
        self._audit_log.append(TokenLifecycleEvent(
            event_type="issued",
            token_id=tid,
            actor=self.authority_did,
            timestamp=now.isoformat(),
            details={"subject": subject, "ttl_hours": ttl, "scope_count": len(scopes)},
        ))

        return token

    def revoke(
        self,
        token_id: str,
        *,
        reason: str = "manual_revocation",
        revoked_by: str | None = None,
    ) -> bool:
        """Revoke a capability token.

        Args:
            token_id: The token to revoke
            reason: Reason for revocation
            revoked_by: Who initiated the revocation

        Returns:
            True if revoked, False if token not found
        """
        if token_id not in self._tokens:
            return False

        if token_id in self._revocation_list:
            return True  # Already revoked

        now = datetime.now(timezone.utc).isoformat()
        self._revocation_list[token_id] = RevocationEntry(
            token_id=token_id,
            revoked_at=now,
            reason=reason,
            revoked_by=revoked_by or self.authority_did,
        )

        self._audit_log.append(TokenLifecycleEvent(
            event_type="revoked",
            token_id=token_id,
            actor=revoked_by or self.authority_did,
            timestamp=now,
            details={"reason": reason},
        ))

        return True

    def rotate(
        self,
        old_token_id: str,
        *,
        new_scopes: list[CapabilityScope] | None = None,
        ttl_hours: int | None = None,
    ) -> CapabilityToken | None:
        """Rotate a token: issue a new one and revoke the old atomically.

        Args:
            old_token_id: The token to rotate
            new_scopes: Optional new scopes (inherits old if None)
            ttl_hours: Optional new TTL

        Returns:
            The new token, or None if old token not found
        """
        old = self._tokens.get(old_token_id)
        if old is None:
            return None

        # Issue new token with same (or updated) parameters
        new_token = self.issue(
            subject=old.subject,
            scopes=new_scopes or list(old.scope),
            ttl_hours=ttl_hours,
            delegable=old.delegation.is_delegable,
            max_depth=old.delegation.max_depth,
            binding=old.binding,
        )

        # Revoke old
        self.revoke(old_token_id, reason=f"rotated_to:{new_token.token_id}")

        self._audit_log.append(TokenLifecycleEvent(
            event_type="rotated",
            token_id=old_token_id,
            actor=self.authority_did,
            timestamp=datetime.now(timezone.utc).isoformat(),
            details={"new_token_id": new_token.token_id},
        ))

        return new_token

    def is_revoked(self, token_id: str) -> bool:
        """Check if a token is in the revocation list."""
        return token_id in self._revocation_list

    def is_valid(self, token_id: str) -> bool:
        """Check if a token is valid (exists, not revoked, not expired)."""
        if token_id not in self._tokens:
            return False
        if self.is_revoked(token_id):
            return False
        token = self._tokens[token_id]
        try:
            expires = datetime.fromisoformat(token.expires_at)
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            return expires > datetime.now(timezone.utc)
        except (ValueError, TypeError):
            return False

    def get_token(self, token_id: str) -> CapabilityToken | None:
        """Retrieve a token by ID."""
        return self._tokens.get(token_id)

    def _sign_token(self, token_id: str) -> str:
        """Sign a token ID with the authority's Ed25519 private key."""
        return Ed25519Provider.sign_string(
            self._keypair.private_key,
            f"{self.authority_did}:{token_id}",
        )

    def verify_token_signature(self, token: CapabilityToken) -> bool:
        """Verify a token's Ed25519 signature.

        Args:
            token: The CapabilityToken to verify.

        Returns:
            True if the signature is valid.
        """
        expected_data = f"{self.authority_did}:{token.token_id}"
        return Ed25519Provider.verify_string(
            self._keypair.public_key,
            token.signature.sig,
            expected_data,
        )

    @property
    def public_key_hex(self) -> str:
        """The authority's Ed25519 public key in hex."""
        return self._keypair.public_key_hex

    @property
    def issued_count(self) -> int:
        return len(self._tokens)

    @property
    def revoked_count(self) -> int:
        return len(self._revocation_list)

    @property
    def active_count(self) -> int:
        return sum(1 for tid in self._tokens if self.is_valid(tid))

    @property
    def audit_log(self) -> list[TokenLifecycleEvent]:
        return list(self._audit_log)

    @property
    def revocation_list(self) -> list[RevocationEntry]:
        return list(self._revocation_list.values())


__all__ = [
    "CapabilityAuthority",
    "RevocationEntry",
    "TokenLifecycleEvent",
]
