"""PSIA Capability Head — token validation, scope checking."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from psia.gate.identity_head import GateVote, VoteReason


class CapabilityTokenStore:
    def __init__(self) -> None:
        self._tokens: dict[str, Any] = {}
        self._revoked: set[str] = set()

    def register(self, token: Any) -> None:
        self._tokens[token.token_id] = token

    def revoke(self, token_id: str) -> None:
        self._revoked.add(token_id)

    def get(self, token_id: str) -> Any | None:
        return self._tokens.get(token_id)

    def is_revoked(self, token_id: str) -> bool:
        return token_id in self._revoked

    def __len__(self) -> int:
        return len(self._tokens)


def _is_token_expired(token: Any) -> bool:
    try:
        expiry = datetime.fromisoformat(token.expires_at)
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) >= expiry
    except Exception:
        return True


class CapabilityHead:
    def __init__(self, token_store: CapabilityTokenStore | None = None) -> None:
        self._store = token_store

    def evaluate(self, envelope: Any) -> GateVote:
        if self._store is None or len(self._store) == 0:
            return GateVote(head="capability", decision="allow")

        token_id = envelope.capability_token_id
        token = self._store.get(token_id)

        if token is None:
            return GateVote(
                head="capability",
                decision="deny",
                reasons=[VoteReason(code="CAP_TOKEN_NOT_FOUND", message=f"Token not found: {token_id}")],
            )

        if self._store.is_revoked(token_id):
            return GateVote(
                head="capability",
                decision="deny",
                reasons=[VoteReason(code="CAP_TOKEN_REVOKED", message=f"Token revoked: {token_id}")],
            )

        if _is_token_expired(token):
            return GateVote(
                head="capability",
                decision="deny",
                reasons=[VoteReason(code="CAP_TOKEN_EXPIRED", message=f"Token expired: {token_id}")],
            )

        if token.subject != envelope.actor:
            if not token.delegation.is_delegable:
                return GateVote(
                    head="capability",
                    decision="deny",
                    reasons=[VoteReason(code="CAP_SUBJECT_MISMATCH", message=f"Subject {token.subject} != actor {envelope.actor}")],
                )

        action = envelope.intent.action
        resource = envelope.intent.resource
        if not token.covers(action, resource):
            return GateVote(
                head="capability",
                decision="deny",
                reasons=[VoteReason(code="CAP_SCOPE_DENIED", message=f"Token does not cover {action} on {resource}")],
            )

        return GateVote(head="capability", decision="allow")
