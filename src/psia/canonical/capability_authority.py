"""PSIA capability authority — token issuance, revocation, rotation."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from psia.crypto.ed25519_provider import Ed25519Provider
from psia.schemas.capability import CapabilityScope, CapabilityToken, DelegationPolicy
from psia.schemas.identity import Signature


@dataclass
class AuditEntry:
    event_type: str
    token_id: str
    actor: str = ""
    reason: str = ""


# Alias used in comprehensive tests
TokenLifecycleEvent = AuditEntry


@dataclass
class RevocationEntry:
    token_id: str
    reason: str = ""


class CapabilityAuthority:
    # IRON_PATH_2_PHASE_1_ANNOTATION_ONLY
    # IRON_PATH_2_STOP_CONDITION: canonical capability authority not wired
    # Current behavior: CapabilityAuthority is the intended Ed25519 authority, but production execution paths do not call it.
    # Required before Phase 2+: Wire it through a compatibility bridge with tests for expired, replayed, wrong-scope, revoked, legacy, and malformed tokens.
    # Do not change behavior in Phase 1.
    def __init__(
        self,
        authority_did: str | None = None,
        max_scope_actions: int = 10,
        allow_delegation: bool = False,
        max_delegation_depth: int = 0,
        default_ttl_hours: int = 24,
        key_store: Any = None,
    ) -> None:
        self._authority_did = authority_did or f"did:project-ai:ca:{uuid.uuid4().hex[:8]}"
        self._max_scope_actions = max_scope_actions
        self._allow_delegation = allow_delegation
        self._max_delegation_depth = max_delegation_depth
        self._default_ttl_hours = default_ttl_hours
        self._key_store = key_store
        self._keypair = Ed25519Provider.generate_keypair("capability_authority")
        self._tokens: dict[str, CapabilityToken] = {}
        self._revoked: set[str] = set()
        self._audit: list[AuditEntry] = []
        self._revocation_list: list[RevocationEntry] = []

    @property
    def authority_did(self) -> str:
        return self._authority_did

    @property
    def default_ttl_hours(self) -> int:
        return self._default_ttl_hours

    @property
    def issued_count(self) -> int:
        return len(self._tokens)

    @property
    def active_count(self) -> int:
        return sum(1 for tid in self._tokens if self.is_valid(tid))

    @property
    def audit_log(self) -> list[AuditEntry]:
        return list(self._audit)

    @property
    def _audit_log(self) -> list[AuditEntry]:
        return list(self._audit)

    @property
    def revocation_list(self) -> list[RevocationEntry]:
        return list(self._revocation_list)

    def verify_token_signature(self, token: CapabilityToken) -> bool:
        token_hash = token.compute_hash()
        return Ed25519Provider.verify(
            self._keypair.public_key, token.signature.sig, token_hash.encode()
        )

    def issue(
        self,
        subject: str,
        scopes: list[CapabilityScope],
        ttl_hours: int | None = None,
    ) -> CapabilityToken:
        if subject == self._authority_did or subject.startswith("did:project-ai:authority:"):
            raise ValueError("INV-ROOT-5: capability authority cannot issue to itself")

        for scope in scopes:
            if len(scope.actions) > self._max_scope_actions:
                raise ValueError(
                    f"INV-ROOT-6: scope has {len(scope.actions)} actions, "
                    f"max allowed is {self._max_scope_actions}"
                )

        ttl = ttl_hours if ttl_hours is not None else self._default_ttl_hours
        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=ttl)
        token_id = f"cap_{uuid.uuid4().hex[:12]}"
        nonce = uuid.uuid4().hex

        kid = self._keypair.key_id
        token = CapabilityToken(
            token_id=token_id,
            issuer=self._authority_did,
            subject=subject,
            issued_at=now.isoformat(),
            expires_at=expires.isoformat(),
            nonce=nonce,
            scope=scopes,
            delegation=DelegationPolicy(
                is_delegable=self._allow_delegation,
                max_depth=self._max_delegation_depth,
            ),
            signature=Signature(alg="ed25519", kid=kid, sig="pending"),
        )
        token_hash = token.compute_hash()
        if self._key_store is not None:
            try:
                sig_value = self._key_store.sign_as("capability_authority", token_hash.encode())
            except Exception:
                sig_value = Ed25519Provider.sign(self._keypair.private_key, token_hash.encode())
        else:
            sig_value = Ed25519Provider.sign(self._keypair.private_key, token_hash.encode())
        token.signature = Signature(alg="ed25519", kid=kid, sig=sig_value)
        self._tokens[token_id] = token
        self._audit.append(AuditEntry(event_type="issued", token_id=token_id))
        return token

    def revoke(self, token_id: str, reason: str = "", revoked_by: str = "") -> bool:
        if token_id not in self._tokens:
            return False
        self._revoked.add(token_id)
        self._audit.append(AuditEntry(event_type="revoked", token_id=token_id, actor=revoked_by, reason=reason))
        entry = RevocationEntry(token_id=token_id, reason=reason)
        if not any(e.token_id == token_id for e in self._revocation_list):
            self._revocation_list.append(entry)
        return True

    def rotate(self, token_id: str) -> CapabilityToken | None:
        token = self._tokens.get(token_id)
        if token is None:
            return None
        self.revoke(token_id, reason="rotated")
        new_token = self.issue(subject=token.subject, scopes=list(token.scope))
        return new_token

    def is_revoked(self, token_id: str) -> bool:
        return token_id in self._revoked

    def is_valid(self, token_id: str) -> bool:
        token = self._tokens.get(token_id)
        if token is None:
            return False
        if self.is_revoked(token_id):
            return False
        now = datetime.now(timezone.utc)
        expires = datetime.fromisoformat(token.expires_at)
        if now >= expires:
            return False
        return True

    def get_token(self, token_id: str) -> CapabilityToken | None:
        return self._tokens.get(token_id)
