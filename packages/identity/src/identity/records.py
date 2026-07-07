from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class IdentityRecord:
    actor_id: str
    active: bool = True

    def to_record(self) -> dict[str, object]:
        return {"actor_id": self.actor_id, "active": self.active}

    @classmethod
    def from_record(cls, record: dict[str, object]) -> IdentityRecord:
        return cls(
            actor_id=str(record["actor_id"]),
            active=bool(record.get("active", True)),
        )


@dataclass(frozen=True)
class IdentityVerification:
    allowed: bool
    reason: str
    record: IdentityRecord | None = None


class IdentityRegistry:
    def __init__(self, records: Iterable[IdentityRecord] | None = None) -> None:
        self._records: dict[str, IdentityRecord] = {}
        for record in records or ():
            self.add(record)

    def add(self, record: IdentityRecord) -> None:
        if not record.actor_id:
            raise ValueError("identity actor_id is required")
        self._records[record.actor_id] = record

    def records(self) -> list[IdentityRecord]:
        return [self._records[key] for key in sorted(self._records)]

    def verify(self, actor_id: str | None) -> IdentityVerification:
        if not actor_id:
            return IdentityVerification(False, "missing identity")

        record = self._records.get(actor_id)
        if record is None:
            return IdentityVerification(False, "identity not found")
        if not record.active:
            return IdentityVerification(False, "identity inactive", record)
        return IdentityVerification(True, "identity active", record)
