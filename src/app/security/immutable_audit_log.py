"""
ImmutableAuditLog — append-only hash-chained audit log backed by a flat file.

Each entry is a JSON object written as a single line.  The chain is anchored by
a GENESIS block written at initialisation.  Every subsequent entry commits the
SHA-256 hash of its predecessor, creating a tamper-evident linked list.

Hash formula (matches test expectations):
    content = {k: v for k, v in entry.items() if k != "hash"}
    entry["hash"] = sha256(json.dumps(content, sort_keys=True)).hexdigest()
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from typing import Any


class ImmutableAuditLog:
    """Append-only, hash-chained audit log stored as JSONL."""

    def __init__(self, log_path: str) -> None:
        self.log_path = log_path
        self._write_genesis()

    # ── internal helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _compute_hash(entry: dict[str, Any]) -> str:
        content = {k: v for k, v in entry.items() if k != "hash"}
        return hashlib.sha256(
            json.dumps(content, sort_keys=True).encode("utf-8")
        ).hexdigest()

    def _write_genesis(self) -> None:
        genesis: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "type": "GENESIS",
            "user_id": "system",
            "data": {},
            "previous_hash": "0" * 64,
        }
        genesis["hash"] = self._compute_hash(genesis)
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(genesis) + "\n")

    def _last_hash(self) -> str:
        with open(self.log_path, encoding="utf-8") as f:
            last_line = ""
            for line in f:
                stripped = line.strip()
                if stripped:
                    last_line = stripped
        return json.loads(last_line)["hash"]

    # ── public API ─────────────────────────────────────────────────────────────

    def log_event(
        self, event_type: str, user_id: str, data: dict[str, Any]
    ) -> str:
        """Append a signed event entry; returns the entry's hash."""
        entry: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "type": event_type,
            "user_id": user_id,
            "data": data,
            "previous_hash": self._last_hash(),
        }
        entry["hash"] = self._compute_hash(entry)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return entry["hash"]

    def verify_integrity(self) -> tuple[bool, str]:
        """Verify the full hash chain.  Returns (ok, message)."""
        if not os.path.exists(self.log_path):
            return False, f"Log file not found: {self.log_path}"

        try:
            with open(self.log_path, encoding="utf-8") as f:
                raw_lines = [ln.strip() for ln in f if ln.strip()]
        except OSError as exc:
            return False, f"Failed to read log: {exc}"

        if not raw_lines:
            return False, "Log file is empty"

        entries: list[dict[str, Any]] = []
        for idx, line in enumerate(raw_lines, start=1):
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as exc:
                return False, f"JSON parse error at line {idx}: {exc}"

        if entries[0].get("type") != "GENESIS":
            return False, (
                f"Missing genesis block: first entry type is "
                f"{entries[0].get('type')!r}"
            )

        prev_hash: str | None = None
        for idx, entry in enumerate(entries, start=1):
            if "hash" not in entry:
                return False, f"Entry {idx}: missing hash field"

            stored = entry["hash"]
            computed = self._compute_hash(entry)
            if stored != computed:
                return False, f"Entry {idx}: hash mismatch"

            if prev_hash is not None and entry.get("previous_hash") != prev_hash:
                return False, f"Entry {idx}: chain break"

            prev_hash = stored

        return True, f"Integrity verified: {len(entries)} entries"
