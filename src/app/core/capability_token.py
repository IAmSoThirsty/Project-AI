"""capability_token.py — Upgrade 5: Capability-Scoped Execution Tokens.

Short-lived, signed, one-time-use tokens that gate final executor invocation.

Token fields (full schema in docstring):
  token_id, action, scope, expires_at, max_side_effects,
  policy_version, policy_hash, context_hash, authorization_hash,
  session_id, conversation_id, nonce, signature

Signing uses HMAC-SHA256 with a configurable secret (env: CAPABILITY_TOKEN_SECRET).
In production, replace with Ed25519 asymmetric signing.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import secrets
import time
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

_SECRET = os.environ.get("CAPABILITY_TOKEN_SECRET", "dev-secret-change-in-production")
# IRON_PATH_2_PHASE_1_ANNOTATION_ONLY
# IRON_PATH_2_STOP_CONDITION: active legacy HMAC capability authority
# Current behavior: capability_token.py is the active HMAC-SHA256 token issuer/validator and can fall back to a dev-default secret.
# Required before Phase 2+: Introduce a compatibility bridge before wiring canonical Ed25519 CapabilityAuthority; prove fail-closed behavior for expired, replayed, wrong-scope, revoked, legacy, and malformed tokens.
# Do not change behavior in Phase 1.
_TOKEN_TTL = int(os.environ.get("CAPABILITY_TOKEN_TTL", "300"))  # seconds

# In-process replay prevention store (bounded; production → Redis/DB)
_USED_TOKENS: set[str] = set()
_MAX_USED_STORE = 10_000


@dataclass
class CapabilityToken:
    """Signed, short-lived capability token."""

    token_id: str
    action: str
    scope: list[str]
    expires_at: float
    max_side_effects: int
    policy_version: str
    policy_hash: str
    context_hash: str
    authorization_hash: str
    session_id: str
    conversation_id: str
    nonce: str
    signature: str = ""

    # ------------------------------------------------------------------ #
    def to_dict(self) -> dict[str, Any]:
        return {
            "token_id": self.token_id,
            "action": self.action,
            "scope": self.scope,
            "expires_at": self.expires_at,
            "max_side_effects": self.max_side_effects,
            "policy_version": self.policy_version,
            "policy_hash": self.policy_hash,
            "context_hash": self.context_hash,
            "authorization_hash": self.authorization_hash,
            "session_id": self.session_id,
            "conversation_id": self.conversation_id,
            "nonce": self.nonce,
            "signature": self.signature,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    def _signable_payload(self) -> str:
        """Payload string that is signed (excludes signature field)."""
        d = self.to_dict()
        d.pop("signature")
        return json.dumps(d, sort_keys=True)

    def compute_signature(self) -> str:
        payload = self._signable_payload()
        return hmac.new(_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()

    def is_signature_valid(self) -> bool:
        expected = self.compute_signature()
        return hmac.compare_digest(expected, self.signature)

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def is_replayed(self) -> bool:
        return self.token_id in _USED_TOKENS

    def matches_action(self, action: str) -> bool:
        return self.action == action

    def matches_scope(self, required_scope: list[str]) -> bool:
        return all(s in self.scope for s in required_scope)

    def matches_context_hash(self, context_hash: str) -> bool:
        return self.context_hash == context_hash

    def matches_policy_hash(self, policy_hash: str) -> bool:
        return not policy_hash or not self.policy_hash or self.policy_hash == policy_hash


class CapabilityTokenService:
    """Mints and verifies capability tokens."""

    def mint(
        self,
        action: str,
        scope: list[str],
        session_id: str,
        conversation_id: str,
        context_hash: str,
        authorization_hash: str,
        policy_version: str = "",
        policy_hash: str = "",
        ttl: int = _TOKEN_TTL,
        max_side_effects: int = 1,
    ) -> CapabilityToken:
        token_id = secrets.token_hex(16)
        nonce = secrets.token_hex(8)
        expires_at = time.time() + ttl

        token = CapabilityToken(
            token_id=token_id,
            action=action,
            scope=scope,
            expires_at=expires_at,
            max_side_effects=max_side_effects,
            policy_version=policy_version,
            policy_hash=policy_hash,
            context_hash=context_hash,
            authorization_hash=authorization_hash,
            session_id=session_id,
            conversation_id=conversation_id,
            nonce=nonce,
        )
        token.signature = token.compute_signature()

        logger.info("CapabilityToken minted: token_id=%s action=%s", token_id, action)
        _audit("MINT", token)
        return token

    def verify(
        self,
        token: CapabilityToken,
        required_action: str,
        required_scope: list[str] | None = None,
        current_context_hash: str = "",
        current_policy_hash: str = "",
    ) -> tuple[bool, str]:
        """Verify token.  Returns (ok, reason).  Consumes token on success."""
        if token.is_replayed():
            _audit("REJECT_REPLAY", token)
            return False, f"Token {token.token_id} already consumed (replay)"

        if token.is_expired():
            _audit("REJECT_EXPIRED", token)
            return False, f"Token {token.token_id} expired"

        if not token.is_signature_valid():
            _audit("REJECT_BAD_SIG", token)
            return False, "Token signature invalid"

        if not token.matches_action(required_action):
            _audit("REJECT_WRONG_ACTION", token)
            return False, f"Token action {token.action!r} != required {required_action!r}"

        if required_scope and not token.matches_scope(required_scope):
            _audit("REJECT_WRONG_SCOPE", token)
            return False, f"Token scope {token.scope} does not cover {required_scope}"

        if current_context_hash and not token.matches_context_hash(current_context_hash):
            _audit("REJECT_CONTEXT_HASH", token)
            return False, "Token context hash mismatch"

        if current_policy_hash and not token.matches_policy_hash(current_policy_hash):
            _audit("REJECT_POLICY_HASH", token)
            return False, "Token policy hash mismatch (policy changed)"

        # Consume (mark used)
        if len(_USED_TOKENS) >= _MAX_USED_STORE:
            _USED_TOKENS.clear()   # safety valve — bounded
        _USED_TOKENS.add(token.token_id)

        _audit("CONSUME", token)
        logger.info("CapabilityToken consumed: token_id=%s", token.token_id)
        return True, "OK"


def _audit(event: str, token: CapabilityToken) -> None:
    logger.info(
        "CapToken:%s token_id=%s action=%s session=%s",
        event, token.token_id, token.action, token.session_id,
    )


__all__ = ["CapabilityToken", "CapabilityTokenService"]
