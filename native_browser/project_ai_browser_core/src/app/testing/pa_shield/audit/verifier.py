"""Audit log integrity verification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.testing.pa_shield.common import stable_digest


class AuditVerifier:
    """Verify chained PA-SHIELD audit logs."""

    @staticmethod
    def read_entries(log_path: Path) -> list[dict[str, Any]]:
        """Read all JSONL entries from disk."""
        if not log_path.exists():
            return []
        entries = []
        for line in log_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                entries.append(json.loads(line))
        return entries

    @classmethod
    def verify_chain(cls, log_path: Path) -> tuple[bool, list[str]]:
        """Verify previous-hash linkage and entry digests."""
        errors: list[str] = []
        expected_previous = "GENESIS"
        for index, entry in enumerate(cls.read_entries(log_path), start=1):
            actual_previous = entry.get("previous_hash")
            if actual_previous != expected_previous:
                errors.append(
                    f"Entry {index} previous_hash mismatch: {actual_previous} != {expected_previous}"
                )

            supplied_hash = entry.get("hash")
            payload = dict(entry)
            payload.pop("hash", None)
            calculated_hash = stable_digest(payload)
            if supplied_hash != calculated_hash:
                errors.append(
                    f"Entry {index} hash mismatch: {supplied_hash} != {calculated_hash}"
                )
            expected_previous = supplied_hash
        return (not errors, errors)
