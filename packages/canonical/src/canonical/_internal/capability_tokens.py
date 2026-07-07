from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class CapabilityToken:
    token_id: str
    actor_id: str
    actions: frozenset[str]
    resources: frozenset[str]
    expires_at: datetime
    revoked: bool = False

    @classmethod
    def issue(
        cls,
        token_id: str,
        actor_id: str,
        actions: Iterable[str],
        resources: Iterable[str],
        expires_at: datetime,
        revoked: bool = False,
    ) -> CapabilityToken:
        return cls(
            token_id=token_id,
            actor_id=actor_id,
            actions=frozenset(actions),
            resources=frozenset(resources),
            expires_at=expires_at,
            revoked=revoked,
        )

    def to_record(self) -> dict[str, object]:
        return {
            "token_id": self.token_id,
            "actor_id": self.actor_id,
            "actions": sorted(self.actions),
            "resources": sorted(self.resources),
            "expires_at": _as_utc(self.expires_at).isoformat(),
            "revoked": self.revoked,
        }

    @classmethod
    def from_record(cls, record: dict[str, object]) -> CapabilityToken:
        return cls.issue(
            token_id=str(record["token_id"]),
            actor_id=str(record["actor_id"]),
            actions=[str(action) for action in record["actions"]],
            resources=[str(resource) for resource in record["resources"]],
            expires_at=datetime.fromisoformat(str(record["expires_at"])),
            revoked=bool(record.get("revoked", False)),
        )


@dataclass(frozen=True)
class CapabilityVerification:
    allowed: bool
    reason: str
    token: CapabilityToken | None = None


class CapabilityRegistry:
    def __init__(self, tokens: Iterable[CapabilityToken] | None = None) -> None:
        self._tokens: dict[str, CapabilityToken] = {}
        for token in tokens or ():
            self.add(token)

    def add(self, token: CapabilityToken) -> None:
        if not token.token_id:
            raise ValueError("capability token_id is required")
        self._tokens[token.token_id] = token

    def tokens(self) -> list[CapabilityToken]:
        return [self._tokens[key] for key in sorted(self._tokens)]

    def verify(
        self,
        token_id: str | None,
        actor_id: str,
        action: str,
        resource: str,
        now: datetime,
    ) -> CapabilityVerification:
        if not token_id:
            return CapabilityVerification(False, "missing capability")

        token = self._tokens.get(token_id)
        if token is None:
            return CapabilityVerification(False, "invalid capability")
        if token.actor_id != actor_id:
            return CapabilityVerification(False, "capability actor mismatch", token)
        if token.revoked:
            return CapabilityVerification(False, "capability revoked", token)
        if _as_utc(now) >= _as_utc(token.expires_at):
            return CapabilityVerification(False, "capability expired", token)
        if action not in token.actions and "*" not in token.actions:
            return CapabilityVerification(False, "capability action mismatch", token)
        if resource not in token.resources and "*" not in token.resources:
            return CapabilityVerification(False, "capability resource mismatch", token)
        return CapabilityVerification(True, "capability valid", token)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
