"""Typed, append-only audit bridge into the Chimera evidence surface."""

from __future__ import annotations

import hashlib
import json
import threading
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Final, Literal, cast

type Verdict = Literal["ALLOW", "DENY", "ESCALATE"]
type JsonScalar = str | int | float | bool | None
type JsonRecord = dict[str, JsonScalar]
GENESIS_HASH: Final = "0" * 64


def _canonical_json(record: Mapping[str, JsonScalar]) -> bytes:
    return json.dumps(record, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )


class AppendOnlyAuditRelay:
    """Write and verify a process-safe hash chain for security evidence."""

    def __init__(self, path: Path) -> None:
        self.path = path.resolve()
        self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # A configured relay starts at a materialized, valid genesis state.
        # This proves the path is writable during startup and lets external
        # integrity jobs distinguish a valid empty chain from a bad mount.
        self.path.touch(exist_ok=True)

    def _last_hash(self) -> str:
        if not self.path.exists():
            return GENESIS_HASH
        lines = [line for line in self.path.read_text(encoding="utf-8").splitlines() if line]
        if not lines:
            return GENESIS_HASH
        record = cast(JsonRecord, json.loads(lines[-1]))
        value = record.get("hash")
        if not isinstance(value, str):
            raise ValueError("Audit relay tail has no hash")
        return value

    def append(self, event: str, fields: Mapping[str, JsonScalar]) -> JsonRecord:
        with self._lock:
            body: JsonRecord = {
                "event": event,
                "previous_hash": self._last_hash(),
                "timestamp": datetime.now(UTC).isoformat(),
                **fields,
            }
            body["hash"] = hashlib.sha256(_canonical_json(body)).hexdigest()
            with self.path.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(_canonical_json(body).decode("utf-8") + "\n")
            return body

    def verify(self) -> tuple[bool, int]:
        previous = GENESIS_HASH
        count = 0
        if not self.path.exists():
            return True, count
        for count, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), start=1):
            record = cast(JsonRecord, json.loads(line))
            current = record.pop("hash", None)
            if record.get("previous_hash") != previous or not isinstance(current, str):
                return False, count
            if hashlib.sha256(_canonical_json(record)).hexdigest() != current:
                return False, count
            previous = current
        return True, count


def start_audit_relay(path: Path) -> AppendOnlyAuditRelay:
    return AppendOnlyAuditRelay(path)


def receive_verdict(
    relay: AppendOnlyAuditRelay,
    *,
    action_id: str,
    verdict: Verdict,
    source: str = "execution",
    machine_credential_id: str | None = None,
    machine_credential_label: str | None = None,
) -> JsonRecord:
    details: dict[str, JsonScalar] = {"action_id": action_id, "source": source, "verdict": verdict}
    if machine_credential_id is not None:
        details["machine_credential_id"] = machine_credential_id
    if machine_credential_label is not None:
        details["machine_credential_label"] = machine_credential_label
    return relay.append(
        "chimera.verdict",
        details,
    )


def receive_canary_hit(
    relay: AppendOnlyAuditRelay,
    *,
    canary_value: str,
    context: str,
    machine_credential_id: str | None = None,
    machine_credential_label: str | None = None,
) -> JsonRecord:
    fingerprint = hashlib.sha256(canary_value.encode("utf-8")).hexdigest()
    details: dict[str, JsonScalar] = {"canary_sha256": fingerprint, "context": context}
    if machine_credential_id is not None:
        details["machine_credential_id"] = machine_credential_id
    if machine_credential_label is not None:
        details["machine_credential_label"] = machine_credential_label
    return relay.append("chimera.canary_hit", details)


def report_governance_denial(
    relay: AppendOnlyAuditRelay,
    *,
    action_id: str,
    reason: str,
) -> JsonRecord:
    return relay.append(
        "chimera.governance_denial",
        {"action_id": action_id, "reason": reason},
    )
