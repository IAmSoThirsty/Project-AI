"""Tamper-evident audit logging for PA-SHIELD."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import timezone, datetime
from pathlib import Path
from typing import Any

from app.testing.pa_shield.common import stable_digest


class AuditLogger:
    """Write a chained JSONL audit log."""

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self._previous_hash = "GENESIS"

    def log_case(self, payload: dict[str, Any]) -> str:
        """Append an entry and return its hash."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "previous_hash": self._previous_hash,
            **payload,
        }
        record_hash = stable_digest(record)
        record["hash"] = record_hash
        with self.output_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        self._previous_hash = record_hash
        return record_hash

    @staticmethod
    def result_payload(trace: Any, result: Any, system_name: str) -> dict[str, Any]:
        """Convert an execution trace and scored result to an audit payload."""
        serialized_result = result.to_dict() if hasattr(result, "to_dict") else asdict(result)
        return {
            "system": system_name,
            "attack_case": trace.case.to_dict(),
            "turns": trace.turns,
            "result": serialized_result,
        }
