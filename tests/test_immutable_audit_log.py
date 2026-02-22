"""
Tests for the ImmutableAuditLog, specifically the verify_integrity() chain
verification that was previously a TODO stub.

Covers:
  - Valid chain verification
  - Tampered entry detection
  - Missing genesis block
  - Empty log / missing file
  - Broken chain linkage
"""

import hashlib
import json
import os
import tempfile

import pytest

from app.security.immutable_audit_log import ImmutableAuditLog


@pytest.fixture
def tmp_log(tmp_path):
    """Provide a fresh ImmutableAuditLog backed by a temp file."""
    log_path = str(tmp_path / "audit.log")
    audit = ImmutableAuditLog(log_path=log_path)
    return audit


# ── Valid chain ────────────────────────────────────────────────


class TestVerifyIntegrity:
    """Tests for the verify_integrity() hash-chain verification."""

    def test_genesis_only(self, tmp_log):
        """A freshly initialised log (genesis only) is valid."""
        is_valid, msg = tmp_log.verify_integrity()
        assert is_valid is True
        assert "1 entries" in msg

    def test_valid_chain_with_events(self, tmp_log):
        """Log with multiple events has intact chain."""
        tmp_log.log_event("LOGIN", "user1", {"ip": "127.0.0.1"})
        tmp_log.log_event("QUERY", "user1", {"query": "SELECT 1"})
        tmp_log.log_event("LOGOUT", "user1", {})

        is_valid, msg = tmp_log.verify_integrity()
        assert is_valid is True
        assert "4 entries" in msg  # genesis + 3

    def test_tampered_data(self, tmp_log):
        """Modifying an entry's data field breaks the hash."""
        tmp_log.log_event("LOGIN", "user1", {"ip": "10.0.0.1"})

        # Read, tamper, write back
        with open(tmp_log.log_path, encoding="utf-8") as f:
            lines = f.readlines()

        entry = json.loads(lines[1])
        entry["data"]["ip"] = "EVIL"  # tamper
        lines[1] = json.dumps(entry) + "\n"

        with open(tmp_log.log_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        is_valid, msg = tmp_log.verify_integrity()
        assert is_valid is False
        assert "hash mismatch" in msg

    def test_tampered_hash(self, tmp_log):
        """Replacing the stored hash with a random value is detected."""
        tmp_log.log_event("ACTION", "user2", {"action": "test"})

        with open(tmp_log.log_path, encoding="utf-8") as f:
            lines = f.readlines()

        entry = json.loads(lines[1])
        entry["hash"] = "0" * 64  # forge hash
        lines[1] = json.dumps(entry) + "\n"

        with open(tmp_log.log_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        is_valid, msg = tmp_log.verify_integrity()
        assert is_valid is False
        assert "hash mismatch" in msg

    def test_broken_chain_linkage(self, tmp_log):
        """Breaking the previous_hash link is detected."""
        tmp_log.log_event("A", "u", {})
        tmp_log.log_event("B", "u", {})

        with open(tmp_log.log_path, encoding="utf-8") as f:
            lines = f.readlines()

        entry = json.loads(lines[2])  # third line (second event)
        # Replace content to break chain but keep a valid self-hash
        entry["previous_hash"] = "f" * 64  # invalid link

        # Recompute hash so self-hash is valid but chain is broken
        content = {k: v for k, v in entry.items() if k != "hash"}
        entry["hash"] = hashlib.sha256(
            json.dumps(content, sort_keys=True).encode()
        ).hexdigest()

        lines[2] = json.dumps(entry) + "\n"

        with open(tmp_log.log_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        is_valid, msg = tmp_log.verify_integrity()
        assert is_valid is False
        assert "chain break" in msg

    def test_missing_genesis(self, tmp_path):
        """Log without a GENESIS first entry fails."""
        log_path = str(tmp_path / "no_genesis.log")
        # Write a non-genesis entry as the first line
        entry = {
            "timestamp": "2025-01-01T00:00:00",
            "type": "LOGIN",
            "user_id": "admin",
            "data": {},
            "previous_hash": "0" * 64,
            "hash": "abc123",
        }
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        audit = ImmutableAuditLog.__new__(ImmutableAuditLog)
        audit.log_path = log_path

        is_valid, msg = audit.verify_integrity()
        assert is_valid is False
        assert "genesis" in msg.lower()

    def test_empty_file(self, tmp_path):
        """Empty file returns False."""
        log_path = str(tmp_path / "empty.log")
        with open(log_path, "w", encoding="utf-8") as f:
            pass  # empty

        audit = ImmutableAuditLog.__new__(ImmutableAuditLog)
        audit.log_path = log_path

        is_valid, msg = audit.verify_integrity()
        assert is_valid is False

    def test_missing_file(self, tmp_path):
        """Missing file returns False with descriptive message."""
        log_path = str(tmp_path / "does_not_exist.log")

        audit = ImmutableAuditLog.__new__(ImmutableAuditLog)
        audit.log_path = log_path

        is_valid, msg = audit.verify_integrity()
        assert is_valid is False
        assert "not found" in msg.lower()

    def test_invalid_json(self, tmp_path):
        """Invalid JSON in the log is detected."""
        log_path = str(tmp_path / "bad.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write('{"type": "GENESIS"}\n')
            f.write("{this is not valid json}\n")

        audit = ImmutableAuditLog.__new__(ImmutableAuditLog)
        audit.log_path = log_path

        is_valid, msg = audit.verify_integrity()
        assert is_valid is False
        assert "JSON" in msg

    def test_missing_hash_field(self, tmp_log):
        """Entry with no 'hash' field is detected."""
        # Write a valid genesis + an entry without hash
        with open(tmp_log.log_path, "a", encoding="utf-8") as f:
            entry = {
                "timestamp": "2025-01-01T00:00:00",
                "type": "TEST",
                "user_id": "u",
                "data": {},
                "previous_hash": "0" * 64,
                # no "hash" key
            }
            f.write(json.dumps(entry) + "\n")

        is_valid, msg = tmp_log.verify_integrity()
        assert is_valid is False
        assert "missing" in msg.lower()


class TestLogEvent:
    """Sanity tests for log_event to ensure it produces valid chain."""

    def test_log_event_returns_hash(self, tmp_log):
        entry_hash = tmp_log.log_event("TEST", "user", {"key": "val"})
        assert isinstance(entry_hash, str)
        assert len(entry_hash) == 64  # SHA-256 hex

    def test_chain_grows(self, tmp_log):
        for i in range(5):
            tmp_log.log_event("EVENT", "user", {"i": i})

        with open(tmp_log.log_path, encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        assert len(lines) == 6  # genesis + 5

    def test_chain_valid_after_many_events(self, tmp_log):
        for i in range(20):
            tmp_log.log_event("BULK", "bot", {"n": i})

        is_valid, msg = tmp_log.verify_integrity()
        assert is_valid is True
        assert "21 entries" in msg
