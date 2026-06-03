"""CapabilityAuthorityBridge — Stage 6 compatibility verifier.

Narrow adapter for Iron Path 2.0 Phase 3. It lets ExecutionGate Stage 6 verify
explicit legacy HMAC tokens or canonical Ed25519 CapabilityAuthority tokens
without changing public schemas or replacing CapabilityTokenService directly.
"""

from __future__ import annotations

import os
import threading
from datetime import datetime, timezone
from typing import Any

import app.core.capability_token as legacy_capability
from app.core.capability_token import (
    CapabilityToken as LegacyCapabilityToken,
)
from app.core.capability_token import CapabilityTokenService
from psia.canonical.capability_authority import CapabilityAuthority
from psia.schemas.capability import CapabilityToken as CanonicalCapabilityToken

DEV_DEFAULT_SECRET = "dev-secret-change-in-production"


class CapabilityAuthorityBridge:
    """Verify Stage 6 capability tokens through legacy or canonical authority."""

    def __init__(
        self,
        authority: CapabilityAuthority | None = None,
        legacy_service: CapabilityTokenService | None = None,
        max_consumed_tokens: int = 10_000,
    ) -> None:
        self._authority = authority
        self._legacy_service = legacy_service or CapabilityTokenService()
        self._max_consumed_tokens = max_consumed_tokens
        self._consumed_canonical_tokens: set[str] = set()
        self._lock = threading.Lock()

    def verify(
        self,
        *,
        token: Any,
        action: str,
        required_scope: list[str] | None = None,
        resource: str = "",
        actor: str = "",
        current_context_hash: str = "",
        current_policy_hash: str = "",
        allow_legacy_hmac: bool = False,
    ) -> tuple[bool, str]:
        try:
            if isinstance(token, LegacyCapabilityToken):
                return self._verify_legacy_hmac(
                    token=token,
                    action=action,
                    required_scope=required_scope,
                    current_context_hash=current_context_hash,
                    current_policy_hash=current_policy_hash,
                    allow_legacy_hmac=allow_legacy_hmac,
                )

            canonical_token = self._coerce_canonical_token(token)
            if canonical_token is None:
                return False, "Malformed or unknown capability token shape"

            return self._verify_canonical_ed25519(
                token=canonical_token,
                action=action,
                resource=resource,
                actor=actor,
            )
        except Exception as exc:
            return False, f"Capability bridge failed closed: {exc}"

    def _verify_legacy_hmac(
        self,
        *,
        token: LegacyCapabilityToken,
        action: str,
        required_scope: list[str] | None,
        current_context_hash: str,
        current_policy_hash: str,
        allow_legacy_hmac: bool,
    ) -> tuple[bool, str]:
        if not allow_legacy_hmac:
            return False, "Legacy HMAC compatibility is not enabled"

        ok, reason = self._legacy_secret_is_safe()
        if not ok:
            return False, reason

        return self._legacy_service.verify(
            token,
            action,
            required_scope=required_scope,
            current_context_hash=current_context_hash,
            current_policy_hash=current_policy_hash,
        )

    def _legacy_secret_is_safe(self) -> tuple[bool, str]:
        env_secret = os.getenv("CAPABILITY_TOKEN_SECRET")
        module_secret = getattr(legacy_capability, "_SECRET", "")
        if not env_secret:
            return False, "Legacy HMAC secret is missing"
        if env_secret == DEV_DEFAULT_SECRET or module_secret == DEV_DEFAULT_SECRET:
            return False, "Legacy HMAC dev-default secret is not allowed"
        if env_secret != module_secret:
            return False, "Legacy HMAC secret mismatch; fail closed"
        return True, "OK"

    def _coerce_canonical_token(
        self,
        token: Any,
    ) -> CanonicalCapabilityToken | None:
        if isinstance(token, CanonicalCapabilityToken):
            return token
        if isinstance(token, dict):
            try:
                return CanonicalCapabilityToken.model_validate(token)
            except Exception:
                return None
        return None

    def _verify_canonical_ed25519(
        self,
        *,
        token: CanonicalCapabilityToken,
        action: str,
        resource: str,
        actor: str,
    ) -> tuple[bool, str]:
        if self._authority is None:
            return False, "CapabilityAuthority provider unavailable"
        if not resource:
            return False, "Canonical capability resource is required"
        if not actor:
            return False, "Canonical capability actor is required"

        stored = self._authority.get_token(token.token_id)
        if stored is None:
            return False, f"Canonical capability token unknown: {token.token_id}"

        if token.issuer != self._authority.authority_did:
            return False, "Canonical capability issuer mismatch"

        if not self._authority.verify_token_signature(token):
            return False, "Canonical capability signature invalid"

        if self._authority.is_revoked(token.token_id):
            return False, f"Canonical capability token revoked: {token.token_id}"

        if self._is_expired(token):
            return False, f"Canonical capability token expired: {token.token_id}"

        if not self._authority.is_valid(token.token_id):
            return False, f"Canonical capability token invalid: {token.token_id}"

        if self._is_canonical_replay(token.token_id):
            return False, f"Canonical capability token already consumed (replay): {token.token_id}"

        if token.subject != actor:
            return False, f"Canonical capability subject {token.subject!r} != actor {actor!r}"

        if not token.covers(action, resource):
            return False, f"Canonical capability scope does not cover {action} on {resource}"

        self._consume_canonical(token.token_id)
        return True, "OK"

    def _is_canonical_replay(self, token_id: str) -> bool:
        with self._lock:
            return token_id in self._consumed_canonical_tokens

    def _consume_canonical(self, token_id: str) -> None:
        with self._lock:
            if len(self._consumed_canonical_tokens) >= self._max_consumed_tokens:
                self._consumed_canonical_tokens.clear()
            self._consumed_canonical_tokens.add(token_id)

    @staticmethod
    def _is_expired(token: CanonicalCapabilityToken) -> bool:
        try:
            expires = datetime.fromisoformat(token.expires_at)
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            return datetime.now(timezone.utc) >= expires
        except Exception:
            return True


_bridge_instance: CapabilityAuthorityBridge | None = None


def configure_capability_authority_bridge(
    *,
    authority: CapabilityAuthority | None = None,
    bridge: CapabilityAuthorityBridge | None = None,
) -> CapabilityAuthorityBridge:
    global _bridge_instance
    _bridge_instance = bridge if bridge is not None else CapabilityAuthorityBridge(authority=authority)
    return _bridge_instance


def get_capability_authority_bridge() -> CapabilityAuthorityBridge:
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = CapabilityAuthorityBridge()
    return _bridge_instance


__all__ = [
    "CapabilityAuthorityBridge",
    "configure_capability_authority_bridge",
    "get_capability_authority_bridge",
]
