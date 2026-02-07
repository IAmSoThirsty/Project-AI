"""
Tests for the cryptographic audit log system.

This test suite validates:
- Audit event logging with SHA-256 chaining
- YAML format output
- Chain verification
- Event retrieval
- Tamper detection
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from app.governance.audit_log import AuditLog


class TestAuditLog:
    """Test suite for AuditLog class."""

    def test_init_creates_log_directory(self):
        """Test that initialization creates the log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test_audit" / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)
            
            assert log_path.parent.exists()
            assert audit.log_file == log_path
            assert audit.last_hash == "GENESIS"

    def test_log_event_creates_entry(self):
        """Test that logging an event creates an entry in the log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)
            
            success = audit.log_event(
                event_type="test_event",
                data={"key": "value"},
                actor="test_actor",
                description="Test event description"
            )
            
            assert success is True
            assert log_path.exists()
            
            # Read and verify the event
            with open(log_path, "r") as f:
                events = list(yaml.safe_load_all(f))
            
            assert len(events) == 1
            event = events[0]
            assert event["event_type"] == "test_event"
            assert event["actor"] == "test_actor"
            assert event["description"] == "Test event description"
            assert event["data"]["key"] == "value"
            assert event["previous_hash"] == "GENESIS"
            assert "hash" in event
            assert "timestamp" in event

    def test_chaining_multiple_events(self):
        """Test that multiple events are properly chained."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)
            
            # Log three events
            audit.log_event("event_1", {"num": 1})
            audit.log_event("event_2", {"num": 2})
            audit.log_event("event_3", {"num": 3})
            
            # Read all events
            with open(log_path, "r") as f:
                events = list(yaml.safe_load_all(f))
            
            assert len(events) == 3
            
            # Verify chaining
            assert events[0]["previous_hash"] == "GENESIS"
            assert events[1]["previous_hash"] == events[0]["hash"]
            assert events[2]["previous_hash"] == events[1]["hash"]

    def test_verify_chain_valid(self):
        """Test that a valid chain is verified correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)
            
            # Log multiple events
            audit.log_event("event_1", {"data": "first"})
            audit.log_event("event_2", {"data": "second"})
            audit.log_event("event_3", {"data": "third"})
            
            # Verify chain
            is_valid, message = audit.verify_chain()
            
            assert is_valid is True
            assert "verified successfully" in message.lower()

    def test_verify_chain_empty_log(self):
        """Test that an empty log is considered valid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)
            
            is_valid, message = audit.verify_chain()
            
            assert is_valid is True
            assert "does not exist" in message.lower() or "empty" in message.lower()

    def test_verify_chain_detects_tampering(self):
        """Test that chain verification detects tampering."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)
            
            # Log events
            audit.log_event("event_1", {"data": "first"})
            audit.log_event("event_2", {"data": "second"})
            
            # Tamper with the log file by modifying an event
            with open(log_path, "r") as f:
                content = f.read()
            
            # Change some data
            tampered_content = content.replace("first", "tampered")
            
            with open(log_path, "w") as f:
                f.write(tampered_content)
            
            # Verify chain should fail
            is_valid, message = audit.verify_chain()
            
            assert is_valid is False
            assert "hash mismatch" in message.lower() or "broken" in message.lower()

    def test_get_events_all(self):
        """Test retrieving all events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)
            
            # Log events
            audit.log_event("type_a", {"id": 1})
            audit.log_event("type_b", {"id": 2})
            audit.log_event("type_a", {"id": 3})
            
            # Get all events
            events = audit.get_events()
            
            assert len(events) == 3

    def test_get_events_filtered_by_type(self):
        """Test retrieving events filtered by type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)
            
            # Log events
            audit.log_event("type_a", {"id": 1})
            audit.log_event("type_b", {"id": 2})
            audit.log_event("type_a", {"id": 3})
            
            # Get filtered events
            events = audit.get_events(event_type="type_a")
            
            assert len(events) == 2
            assert all(e["event_type"] == "type_a" for e in events)

    def test_get_events_with_limit(self):
        """Test retrieving events with a limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)
            
            # Log multiple events
            for i in range(10):
                audit.log_event(f"event_{i}", {"num": i})
            
            # Get limited events (most recent)
            events = audit.get_events(limit=3)
            
            assert len(events) == 3
            # Should be the last 3 events
            assert events[0]["data"]["num"] == 7
            assert events[1]["data"]["num"] == 8
            assert events[2]["data"]["num"] == 9

    def test_get_events_empty_log(self):
        """Test retrieving events from an empty log."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)
            
            events = audit.get_events()
            
            assert events == []

    def test_load_last_hash_from_existing_log(self):
        """Test loading the last hash from an existing log."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            
            # Create first audit log and add events
            audit1 = AuditLog(log_file=log_path)
            audit1.log_event("event_1", {"data": "first"})
            audit1.log_event("event_2", {"data": "second"})
            last_hash = audit1.last_hash
            
            # Create new audit log instance
            audit2 = AuditLog(log_file=log_path)
            
            # Should load the last hash from the existing log
            assert audit2.last_hash == last_hash
            assert audit2.last_hash != "GENESIS"

    def test_yaml_format_is_human_readable(self):
        """Test that the YAML output is human-readable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)
            
            audit.log_event(
                event_type="test_event",
                data={"message": "This is a test"},
                actor="human_reader",
                description="Testing readability"
            )
            
            # Read raw file content
            with open(log_path, "r") as f:
                content = f.read()
            
            # Check for human-readable structure
            assert "event_type: test_event" in content
            assert "actor: human_reader" in content
            assert "message: This is a test" in content
            assert "---" in content  # YAML document separator
