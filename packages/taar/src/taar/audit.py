"""Append-only JSONL audit spine.

Every admitted, denied, failed, killed, and completed run leaves a record.
File: .project-ai/automation/audit/YYYY-MM-DD.audit.jsonl
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from taar.models import AuditRecord, ClassificationLevel, RunStatus


def _utcnow() -> str:
    return datetime.now(UTC).isoformat()


def hash_audit_record(record: AuditRecord) -> str:
    payload = record.to_dict()
    payload.pop("hash", None)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def make_audit_record(
    run_id: str,
    agent_id: str,
    task_id: str,
    event_type: str,
    classification: ClassificationLevel,
    status: RunStatus,
    message: str,
    timestamp: str | None = None,
) -> AuditRecord:
    base = AuditRecord(
        timestamp=timestamp or _utcnow(),
        run_id=run_id,
        agent_id=agent_id,
        task_id=task_id,
        event_type=event_type,
        classification=classification,
        status=status,
        message=message,
        hash="",
    )
    return replace(base, hash=hash_audit_record(base))


def audit_file_for(audit_root: Path, when: datetime | None = None) -> Path:
    when = when or datetime.now(UTC)
    return audit_root / f"{when.strftime('%Y-%m-%d')}.audit.jsonl"


def write_audit_record(record: AuditRecord, audit_root: Path) -> Path:
    audit_root.mkdir(parents=True, exist_ok=True)
    path = audit_file_for(audit_root)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record.to_dict(), sort_keys=True, separators=(",", ":")) + "\n")
    return path


def list_audit_records(audit_root: Path, limit: int = 50) -> list[AuditRecord]:
    records: list[AuditRecord] = []
    if not audit_root.exists():
        return records
    for path in sorted(audit_root.glob("*.audit.jsonl"), reverse=True):
        for line in reversed(path.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            data = json.loads(line)
            records.append(
                AuditRecord(
                    timestamp=data["timestamp"],
                    run_id=data["run_id"],
                    agent_id=data["agent_id"],
                    task_id=data["task_id"],
                    event_type=data["event_type"],
                    classification=ClassificationLevel(data["classification"]),
                    status=RunStatus(data["status"]),
                    message=data["message"],
                    hash=data["hash"],
                )
            )
            if len(records) >= limit:
                return records
    return records
