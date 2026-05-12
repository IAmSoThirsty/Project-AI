"""
PSIA Canonical Log — append-only authoritative state store.

The canonical log is the authoritative record of all governance decisions
that passed all 7 PSIA stages.  It is strictly append-only: entries are
never overwritten or deleted.  Each entry carries a SHA-256 hash of its
content and a reference to the previous entry hash, forming a hash chain.

Thread safety: CanonicalLog uses a threading.Lock for all mutations.

Persistence: in-memory by default; provide a Path to persist to a JSONL file.
Each line is a JSON-serialized canonical record.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from pathlib import Path
from typing import Any


def _entry_hash(entry: dict) -> str:
    blob = json.dumps(entry, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


class CanonicalLog:
    """
    Append-only log of canonical governance records.

    Usage:
        log = CanonicalLog()                          # in-memory
        log = CanonicalLog(path=Path("canonical.jsonl"))  # persistent

        seq, entry_hash = log.append(governed_frame_dict)
    """

    def __init__(self, path: Path | None = None) -> None:
        self._entries: list[dict] = []
        self._lock = threading.Lock()
        self._path = path
        self._sequence = 0

        if path and path.exists():
            self._load(path)

    def _load(self, path: Path) -> None:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    self._entries.append(entry)
                    self._sequence = max(self._sequence, entry.get("sequence", 0) + 1)
                except json.JSONDecodeError:
                    pass  # skip corrupt lines — partial-write resilience

    def append(self, record: dict[str, Any]) -> tuple[int, str]:
        """
        Append a record to the canonical log.

        Returns (sequence_number, entry_hash).
        """
        with self._lock:
            prev_hash = self._entries[-1]["entry_hash"] if self._entries else "0" * 64
            seq = self._sequence
            entry: dict[str, Any] = {
                "sequence": seq,
                "timestamp": time.time(),
                "prev_hash": prev_hash,
                "record": record,
            }
            # Hash is computed over the full entry (including prev_hash for chain integrity)
            eh = _entry_hash(entry)
            entry["entry_hash"] = eh
            self._entries.append(entry)
            self._sequence += 1

            if self._path:
                with self._path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, default=str) + "\n")

            return seq, eh

    def all_hashes(self) -> list[str]:
        """Return all entry hashes in sequence order (for Merkle tree input)."""
        with self._lock:
            return [e["entry_hash"] for e in self._entries]

    def verify_chain(self) -> bool:
        """
        Verify the hash chain integrity from genesis to head.
        Returns True if every entry's prev_hash matches the previous entry's entry_hash.
        """
        with self._lock:
            for i, entry in enumerate(self._entries):
                expected_prev = self._entries[i - 1]["entry_hash"] if i > 0 else "0" * 64
                if entry.get("prev_hash") != expected_prev:
                    return False
                # Recompute entry_hash
                check = dict(entry)
                stored_hash = check.pop("entry_hash")
                if _entry_hash(check) != stored_hash:
                    return False
            return True

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)
