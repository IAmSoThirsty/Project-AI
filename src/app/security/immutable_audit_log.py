"""
Immutable Audit Log System
Part of Thirsty's Governance Framework

This module provides a tamper-evident, append-only audit log
using cryptographic hash chaining.
"""

import hashlib
import json
import logging
import os
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class ImmutableAuditLog:
    """
    Cryptographically secure audit logger.
    Each entry includes the hash of the previous entry, forming a blockchain-like structure.
    """

    def __init__(self, log_path: str = "data/security/immutable_audit.log"):
        self.log_path = log_path
        self._ensure_log_exists()

    def _ensure_log_exists(self):
        """Initialize log file and directory if needed."""
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", encoding="utf-8") as f:
                # Genesis block
                genesis = {
                    "entry_id": "0",
                    "previous_hash": "0" * 64,
                    "timestamp": datetime.now().isoformat(),
                    "type": "GENESIS",
                    "data": "Immutable Audit Log Initialized",
                }
                f.write(json.dumps(genesis) + "\n")

    def _get_last_entry(self) -> dict[str, Any]:
        """Read the last entry from the log."""
        try:
            with open(self.log_path, encoding="utf-8") as f:
                lines = f.readlines()
                if not lines:
                    return {}  # Should not happen if initialized

                # Iterate backwards to find last valid JSON
                for line in reversed(lines):
                    if line.strip():
                        return json.loads(line)
        except Exception as e:
            logger.error(f"Error reading audit log: {e}")
            return {}

        return {}

    def log_event(self, event_type: str, user_id: str, data: dict[str, Any]) -> str:
        """
        Log an event to the immutable ledger.

        Returns:
            audit_id (hash of the entry)
        """
        last_entry = self._get_last_entry()
        previous_hash = last_entry.get("hash", "0" * 64)

        # If last entry doesn't have a hash field stored (it might not), compute it?
        # Actually better to compute hash of the *entire line* or check if we stored it.
        # Simple approach: The hash of the *current* entry depends on previous hash.
        # We should store the hash IN the entry for easy verification.

        # BUT: If we store the hash in the entry, the hash calculation must exclude the hash field,
        # or we calculate hash of (content + prev_hash) and store it as ID.

        timestamp = datetime.now().isoformat()

        # Calculate hash of previous entry if not present?
        # Let's trust the previous_hash we stored or recalculated.
        # Actually `last_entry["hash"]` is the way.

        if "hash" not in last_entry and last_entry:
            # Genesis or corrupted. Recompute if needed or use placeholder.
            # For genesis, we can assume a known hash or compute it.
            # Simplified: just use what we have.
            pass

        entry_content = {
            "timestamp": timestamp,
            "type": event_type,
            "user_id": user_id,
            "data": data,
            "previous_hash": previous_hash,
        }

        # Compute SHA-256 of the content
        entry_json = json.dumps(entry_content, sort_keys=True)
        entry_hash = hashlib.sha256(entry_json.encode()).hexdigest()

        # Add hash to the stored record
        final_record = entry_content.copy()
        final_record["hash"] = entry_hash

        # Append to log
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(final_record) + "\n")

        logger.info(f"Audit Logged: {event_type} - {entry_hash}")
        return entry_hash

    def verify_integrity(self) -> tuple[bool, str]:
        """
        Verify the entire chain of hashes.

        Walks every entry in the log, recomputes the SHA-256 from the
        stored content (excluding the ``hash`` field), and confirms:
          1. The recomputed hash matches the stored ``hash``.
          2. Each entry's ``previous_hash`` matches the ``hash`` of the
             prior entry.

        Returns:
            Tuple of (is_valid, diagnostic_message).
        """
        try:
            with open(self.log_path, encoding="utf-8") as f:
                lines = f.readlines()

            if not lines:
                return False, "Empty audit log"

            entries: list[dict] = []
            for i, line in enumerate(lines):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    entries.append(json.loads(stripped))
                except json.JSONDecodeError:
                    return False, f"Invalid JSON at line {i + 1}"

            if not entries:
                return False, "No valid entries in audit log"

            # First entry must be the genesis block
            if entries[0].get("type") != "GENESIS":
                return False, "Missing genesis block (first entry type != GENESIS)"

            # Verify each non-genesis entry
            for idx in range(1, len(entries)):
                entry = entries[idx]

                # ── 1. Hash integrity ──────────────────────────────────
                stored_hash = entry.get("hash")
                if not stored_hash:
                    return False, f"Entry {idx}: missing 'hash' field"

                # Recompute hash from content, excluding the 'hash' key
                content = {k: v for k, v in entry.items() if k != "hash"}
                computed_hash = hashlib.sha256(
                    json.dumps(content, sort_keys=True).encode()
                ).hexdigest()

                if computed_hash != stored_hash:
                    return (
                        False,
                        f"Entry {idx}: hash mismatch — "
                        f"expected {computed_hash[:16]}…, "
                        f"stored {stored_hash[:16]}…",
                    )

                # ── 2. Chain linkage ───────────────────────────────────
                prev_entry = entries[idx - 1]
                expected_prev = prev_entry.get("hash", "0" * 64)
                actual_prev = entry.get("previous_hash")

                if actual_prev != expected_prev:
                    return (
                        False,
                        f"Entry {idx}: chain break — "
                        f"previous_hash={str(actual_prev)[:16]}… "
                        f"does not match prior entry hash={expected_prev[:16]}…",
                    )

            return True, f"Chain verified: {len(entries)} entries, integrity OK"

        except FileNotFoundError:
            return False, f"Audit log not found at {self.log_path}"
        except Exception as e:
            logger.error("Verification error: %s", e)
            return False, f"Verification error: {e}"


# Singleton
_audit_logger = None


def get_audit_logger() -> ImmutableAuditLog:
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = ImmutableAuditLog()
    return _audit_logger
