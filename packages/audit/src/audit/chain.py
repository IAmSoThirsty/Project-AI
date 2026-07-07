from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

GENESIS_HASH = "0" * 64


class AuditWriteError(RuntimeError):
    pass


@dataclass
class AuditEvent:
    decision_id: str
    actor_id: str | None
    action: str
    resource: str
    result: str
    reason: str
    timestamp: str
    previous_hash: str
    event_hash: str
    event_type: str

    def hash_payload(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "actor_id": self.actor_id,
            "action": self.action,
            "resource": self.resource,
            "result": self.result,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "event_type": self.event_type,
        }

    def to_record(self) -> dict[str, Any]:
        record = self.hash_payload()
        record["event_hash"] = self.event_hash
        return record

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> AuditEvent:
        return cls(
            decision_id=str(record["decision_id"]),
            actor_id=(None if record.get("actor_id") is None else str(record["actor_id"])),
            action=str(record["action"]),
            resource=str(record["resource"]),
            result=str(record["result"]),
            reason=str(record["reason"]),
            timestamp=str(record["timestamp"]),
            previous_hash=str(record["previous_hash"]),
            event_hash=str(record["event_hash"]),
            event_type=str(record["event_type"]),
        )


@dataclass(frozen=True)
class AuditVerification:
    valid: bool
    reason: str


class AuditLog:
    def __init__(self, events: list[AuditEvent] | None = None) -> None:
        self._events: list[AuditEvent] = list(events or [])

    @property
    def events(self) -> list[AuditEvent]:
        return self._events

    def append_event(
        self,
        *,
        decision_id: str,
        actor_id: str | None,
        action: str,
        resource: str,
        result: str,
        reason: str,
        event_type: str,
        timestamp: datetime | None = None,
    ) -> AuditEvent:
        previous_hash = self._events[-1].event_hash if self._events else GENESIS_HASH
        event = AuditEvent(
            decision_id=decision_id,
            actor_id=actor_id,
            action=action,
            resource=resource,
            result=result,
            reason=reason,
            timestamp=_timestamp(timestamp),
            previous_hash=previous_hash,
            event_hash="",
            event_type=event_type,
        )
        event.event_hash = self._hash_event(event)
        self._events.append(event)
        return event

    def verify_chain(self) -> AuditVerification:
        previous_hash = GENESIS_HASH
        for index, event in enumerate(self._events):
            if event.previous_hash != previous_hash:
                return AuditVerification(
                    False,
                    f"event {index} previous hash mismatch",
                )
            expected_hash = self._hash_event(event)
            if event.event_hash != expected_hash:
                return AuditVerification(False, f"event {index} hash mismatch")
            previous_hash = event.event_hash
        return AuditVerification(True, "audit chain valid")

    @staticmethod
    def _hash_event(event: AuditEvent) -> str:
        payload = json.dumps(
            event.hash_payload(),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


class FileAuditLog(AuditLog):
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        super().__init__(self._load_events())
        verification = self.verify_chain()
        if not verification.valid:
            raise AuditWriteError(f"audit chain invalid on load: {verification.reason}")

    def append_event(
        self,
        *,
        decision_id: str,
        actor_id: str | None,
        action: str,
        resource: str,
        result: str,
        reason: str,
        event_type: str,
        timestamp: datetime | None = None,
    ) -> AuditEvent:
        previous_count = len(self._events)
        event = super().append_event(
            decision_id=decision_id,
            actor_id=actor_id,
            action=action,
            resource=resource,
            result=result,
            reason=reason,
            event_type=event_type,
            timestamp=timestamp,
        )
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8", newline="\n") as file:
                file.write(json.dumps(event.to_record(), sort_keys=True))
                file.write("\n")
        except Exception as exc:
            del self._events[previous_count:]
            raise AuditWriteError(f"audit event write failed: {exc}") from exc
        return event

    def _load_events(self) -> list[AuditEvent]:
        if not self.path.exists():
            return []

        events: list[AuditEvent] = []
        try:
            for line_number, line in enumerate(
                self.path.read_text(encoding="utf-8").splitlines(),
                start=1,
            ):
                if not line.strip():
                    continue
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise ValueError(f"line {line_number} is not a JSON object")
                events.append(AuditEvent.from_record(record))
        except Exception as exc:
            raise AuditWriteError(f"audit log load failed: {exc}") from exc
        return events


def _timestamp(value: datetime | None) -> str:
    value = value or datetime.now(UTC)
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat()
