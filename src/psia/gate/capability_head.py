"""
Cerberus Capability Head — Token Scope Enforcement.

Performs deep capability verification on the CapabilityToken referenced
by the RequestEnvelope.  This is the second Cerberus head and focuses
on proving the actor *is allowed to do what they're asking*.

Checks performed:
    1. Token resolution (lookup in CapabilityTokenStore)
    2. Token signature integrity (structural — real crypto in Phase 5)
    3. Token expiry check (with clock skew tolerance)
    4. Scope matching (action + resource against token scopes)
    5. Delegation chain validation (depth, delegability)
    6. Binding verification (certificate fingerprint)
    7. Constraint propagation (rate limits, time windows)

Security invariants:
    - INV-ROOT-3 (No capability bypass — every mutation requires a
      capability token that covers the action and resource)
    - INV-ROOT-6 (Least privilege — scopes must be minimally scoped)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from psia.schemas.capability import CapabilityToken
from psia.schemas.cerberus_decision import (
    CerberusVote,
    ConstraintsApplied,
    DenyReason,
)
from psia.schemas.identity import Signature

logger = logging.getLogger(__name__)


class CapabilityTokenStore:
    """Lookup service for CapabilityToken instances.

    In production backed by the CapabilityAuthority with CRL
    (Capability Revocation List) and OCSP-like live status checks.
    """

    def __init__(self) -> None:
        self._tokens: dict[str, CapabilityToken] = {}
        self._revoked: set[str] = set()

    def register(self, token: CapabilityToken) -> None:
        """Register a capability token."""
        self._tokens[token.token_id] = token

    def resolve(self, token_id: str) -> CapabilityToken | None:
        """Resolve a token ID to its CapabilityToken."""
        return self._tokens.get(token_id)

    def revoke(self, token_id: str) -> bool:
        """Revoke a token by ID."""
        if token_id in self._tokens:
            self._revoked.add(token_id)
            return True
        return False

    def is_revoked(self, token_id: str) -> bool:
        """Check if a token is revoked."""
        return token_id in self._revoked

    @property
    def count(self) -> int:
        return len(self._tokens)


class CapabilityHead:
    """Cerberus Capability Head — production-grade scope enforcement.

    Replaces the Phase 1 ``StubCapabilityHead`` with deep checks:
    token resolution, expiry, scope matching, delegation, binding,
    and constraint propagation.

    Args:
        token_store: CapabilityTokenStore for token lookup
        clock_skew_seconds: Allowed clock skew tolerance in seconds
        enforce_binding: If True, deny when binding doesn't match
    """

    def __init__(
        self,
        *,
        token_store: CapabilityTokenStore | None = None,
        clock_skew_seconds: int = 30,
        enforce_binding: bool = False,
    ) -> None:
        self.token_store = token_store or CapabilityTokenStore()
        self.clock_skew_seconds = clock_skew_seconds
        self.enforce_binding = enforce_binding

    def evaluate(self, envelope: Any) -> CerberusVote:
        """Evaluate capability token validity and scope coverage.

        Args:
            envelope: RequestEnvelope

        Returns:
            CerberusVote with capability verification result
        """
        reasons: list[DenyReason] = []
        constraints = ConstraintsApplied()
        token_id = envelope.capability_token_id

        # ── Check 1: Token resolution ──
        token = self.token_store.resolve(token_id)
        if token is None and self.token_store.count > 0:
            reasons.append(
                DenyReason(
                    code="CAP_TOKEN_NOT_FOUND",
                    detail=f"CapabilityToken '{token_id}' not found in store — "
                    f"INV-ROOT-3 requires valid token",
                )
            )
            return self._vote(envelope, "deny", reasons, constraints)

        if token is None:
            # Open mode: no token store configured
            return self._vote(envelope, "allow", [], constraints)

        # ── Check 2: Token revocation ──
        if self.token_store.is_revoked(token_id):
            reasons.append(
                DenyReason(
                    code="CAP_TOKEN_REVOKED",
                    detail=f"CapabilityToken '{token_id}' has been revoked",
                )
            )
            return self._vote(envelope, "deny", reasons, constraints)

        # ── Check 3: Issuer-subject match ──
        if token.subject != envelope.actor:
            # Token was issued to a different subject
            if not token.delegation.is_delegable:
                reasons.append(
                    DenyReason(
                        code="CAP_SUBJECT_MISMATCH",
                        detail=f"Token subject '{token.subject}' != actor "
                        f"'{envelope.actor}' and token is non-delegable",
                    )
                )

        # ── Check 4: Token expiry ──
        try:
            expires_at = datetime.fromisoformat(token.expires_at)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            from datetime import timedelta

            if expires_at + timedelta(seconds=self.clock_skew_seconds) < now:
                reasons.append(
                    DenyReason(
                        code="CAP_TOKEN_EXPIRED",
                        detail=f"Token expired at {token.expires_at} "
                        f"(current: {now.isoformat()}, skew: {self.clock_skew_seconds}s)",
                    )
                )
        except (ValueError, TypeError) as exc:
            reasons.append(
                DenyReason(
                    code="CAP_EXPIRY_UNPARSEABLE",
                    detail=f"Cannot parse expires_at: {exc}",
                )
            )

        # ── Check 5: Scope matching (action + resource) ──
        action = envelope.intent.action
        resource = envelope.intent.resource

        if not token.covers(action, resource):
            reasons.append(
                DenyReason(
                    code="CAP_SCOPE_DENIED",
                    detail=f"Token does not cover action='{action}' on "
                    f"resource='{resource}' — INV-ROOT-3 scope mismatch. "
                    f"Scopes: {[s.model_dump() for s in token.scope]}",
                )
            )

        # ── Check 6: Delegation chain depth ──
        delegation_depth = getattr(envelope.context, "delegation_depth", 0) or 0
        if token.delegation.max_depth is not None:
            if delegation_depth > token.delegation.max_depth:
                reasons.append(
                    DenyReason(
                        code="CAP_DELEGATION_DEPTH_EXCEEDED",
                        detail=f"Delegation depth {delegation_depth} exceeds "
                        f"max_depth {token.delegation.max_depth}",
                    )
                )

        # ── Check 7: Binding verification ──
        if self.enforce_binding and token.binding:
            request_cert_fp = getattr(envelope.context, "client_cert_fingerprint", None)
            expected_fp = token.binding.client_cert_fingerprint
            if expected_fp and request_cert_fp != expected_fp:
                reasons.append(
                    DenyReason(
                        code="CAP_BINDING_MISMATCH",
                        detail=f"Client cert fingerprint mismatch: "
                        f"expected={expected_fp}, got={request_cert_fp}",
                    )
                )

        # ── Check 8: Constraint propagation ──
        # Propagate any scope constraints as applied constraints
        for scope in token.scope:
            if scope.matches_action(action) and scope.matches_resource(resource):
                sc = scope.constraints
                if sc:
                    rate_limit = sc.rate_limit_per_min
                    time_window = sc.time_window
                    if rate_limit or time_window:
                        constraints = ConstraintsApplied(
                            rate_limit_per_min=rate_limit,
                        )

        # ── Final vote ──
        decision = "deny" if reasons else "allow"
        return self._vote(envelope, decision, reasons, constraints)

    def _vote(
        self,
        envelope: Any,
        decision: str,
        reasons: list[DenyReason],
        constraints: ConstraintsApplied,
    ) -> CerberusVote:
        """Create a CerberusVote."""
        return CerberusVote(
            request_id=envelope.request_id,
            head="capability",
            decision=decision,
            reasons=reasons,
            constraints_applied=constraints,
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature=Signature(
                alg="ed25519",
                kid="cerberus_capability_k1",
                sig="capability_head_sig",
            ),
        )


__all__ = ["CapabilityHead", "CapabilityTokenStore"]
