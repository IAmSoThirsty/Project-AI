"""Quarantine records. Quarantine means no trust — never deletion.

Records: .project-ai/automation/quarantine/<classification>/<quarantine_id>.yaml
Quarantined artifacts may not be used as evidence until a human declassifies
them. TAAR implements no declassification path by design.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped, unused-ignore]

from taar.models import ClassificationLevel


def _artifact_hash(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "unavailable"


def create_quarantine_record(
    path: Path,
    reason: str,
    classification: ClassificationLevel,
    root: Path,
    discovered_by: str = "unknown",
    run_id: str | None = None,
    expected_artifact: bool = False,
    notes: str = "",
) -> Path:
    quarantine_id = uuid.uuid4().hex
    record = {
        "quarantine_id": quarantine_id,
        "artifact_path": str(path),
        "artifact_hash": _artifact_hash(path),
        "discovered_by": discovered_by,
        "reason": reason,
        "classification": classification.value,
        "timestamp": datetime.now(UTC).isoformat(),
        "associated_run_id": run_id,
        "expected_artifact": expected_artifact,
        "human_review_status": "pending",
        "notes": notes,
    }
    directory = root / classification.value
    directory.mkdir(parents=True, exist_ok=True)
    record_path = directory / f"{quarantine_id}.yaml"
    record_path.write_text(yaml.safe_dump(record, sort_keys=True), encoding="utf-8")
    return record_path


def list_quarantine_records(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not root.exists():
        return records
    for path in sorted(root.rglob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if isinstance(data, dict) and "quarantine_id" in data:
            records.append(data)
    return records


def is_quarantined(path: Path, root: Path) -> bool:
    target = str(path)
    return any(record.get("artifact_path") == target for record in list_quarantine_records(root))
