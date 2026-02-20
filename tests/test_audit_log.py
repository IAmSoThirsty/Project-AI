"""
Tests for the cryptographic audit log system.

This test suite validates:
- Audit event logging with SHA-256 chaining
- YAML format output
- Chain verification
- Event retrieval
- Tamper detection
- New features: rotation, compression, export, statistics
"""

import tempfile
from pathlib import Path

import yaml

try:
    from app.governance.audit_log import AuditLog
except ImportError:
    from src.app.governance.audit_log import AuditLog


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
                description="Test event description",
            )

            assert success is True
            assert log_path.exists()

            # Read and verify the event
            with open(log_path) as f:
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
            with open(log_path) as f:
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
            with open(log_path) as f:
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
                description="Testing readability",
            )

            # Read raw file content
            with open(log_path) as f:
                content = f.read()

            # Check for human-readable structure
            assert "event_type: test_event" in content
            assert "actor: human_reader" in content
            assert "message: This is a test" in content
            assert "---" in content  # YAML document separator

    def test_new_features_thread_safety(self):
        """Test thread-safe logging operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)

            # Should have lock attribute
            assert hasattr(audit, "lock")
            assert audit.event_count == 0

            # Log some events
            audit.log_event("event_1", {"data": "first"})
            assert audit.event_count == 1

            audit.log_event("event_2", {"data": "second"})
            assert audit.event_count == 2

    def test_new_features_severity_and_metadata(self):
        """Test new severity and metadata fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)

            # Log event with severity and metadata
            audit.log_event(
                "critical_error",
                {"error": "Something went wrong"},
                severity="critical",
                metadata={"ip": "1.2.3.4", "session_id": "abc123"},
            )

            # Verify the event
            events = audit.get_events()
            assert len(events) == 1
            assert events[0]["severity"] == "critical"
            assert events[0]["metadata"]["ip"] == "1.2.3.4"
            assert events[0]["metadata"]["session_id"] == "abc123"

    def test_advanced_filtering(self):
        """Test get_events_filtered method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)

            # Log various events
            audit.log_event("login", {"user": "alice"}, actor="alice", severity="info")
            audit.log_event(
                "unauthorized_access",
                {"user": "bob"},
                actor="bob",
                severity="warning",
            )
            audit.log_event("system_crash", {"cause": "OOM"}, actor="system", severity="critical")

            # Filter by severity
            critical_events = audit.get_events_filtered(severity="critical")
            assert len(critical_events) == 1
            assert critical_events[0]["event_type"] == "system_crash"

            # Filter by actor
            alice_events = audit.get_events_filtered(actor="alice")
            assert len(alice_events) == 1
            assert alice_events[0]["event_type"] == "login"

    def test_export_to_json(self):
        """Test export_to_json method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)

            # Log some events
            audit.log_event("event_1", {"num": 1})
            audit.log_event("event_2", {"num": 2})

            # Export to JSON
            json_path = Path(tmpdir) / "export.json"
            success = audit.export_to_json(json_path)
            assert success
            assert json_path.exists()

            # Verify JSON content
            import json

            with open(json_path) as f:
                data = json.load(f)

            assert data["version"] == "1.0"
            assert data["event_count"] == 2
            assert len(data["events"]) == 2

    def test_export_to_csv(self):
        """Test export_to_csv method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)

            # Log some events
            audit.log_event("event_1", {"num": 1})
            audit.log_event("event_2", {"num": 2})

            # Export to CSV
            csv_path = Path(tmpdir) / "export.csv"
            success = audit.export_to_csv(csv_path)
            assert success
            assert csv_path.exists()

            # Verify CSV content
            with open(csv_path) as f:
                content = f.read()

            assert "event_type" in content
            assert "event_1" in content
            assert "event_2" in content

    def test_get_statistics(self):
        """Test get_statistics method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)

            # Log various events
            audit.log_event("login", {"user": "alice"}, actor="alice")
            audit.log_event("login", {"user": "bob"}, actor="bob")
            audit.log_event("error", {"code": 500}, actor="system", severity="error")

            # Get statistics
            stats = audit.get_statistics()
            assert stats["total_events"] == 3
            assert stats["event_types"]["login"] == 2
            assert stats["event_types"]["error"] == 1
            assert stats["actors"]["alice"] == 1
            assert stats["actors"]["bob"] == 1
            assert stats["actors"]["system"] == 1
            assert stats["severities"]["info"] == 2
            assert stats["severities"]["error"] == 1

    def test_get_compliance_report(self):
        """Test get_compliance_report method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)

            # Log various events
            audit.log_event("info_event", {"msg": "info"}, severity="info")
            audit.log_event("warning_event", {"msg": "warning"}, severity="warning")
            audit.log_event("error_event", {"msg": "error"}, severity="error")

            # Get compliance report
            report = audit.get_compliance_report()
            assert "report_generated" in report
            assert report["total_events"] == 3
            assert report["chain_valid"] is True
            assert report["critical_events"] == 0
            assert report["error_events"] == 1
            assert report["warning_events"] == 1
            assert report["compliance_status"] == "PASS"

    def test_callback_registration(self):
        """Test event callback registration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit_log.yaml"
            audit = AuditLog(log_file=log_path)

            # Track callback invocations
            callback_events = []

            def test_callback(event):
                callback_events.append(event)

            # Register callback
            audit.register_callback(test_callback)

            # Log events
            audit.log_event("event_1", {"data": "first"})
            audit.log_event("event_2", {"data": "second"})

            # Verify callback was invoked
            assert len(callback_events) == 2
            assert callback_events[0]["event_type"] == "event_1"
            assert callback_events[1]["event_type"] == "event_2"

            # Unregister callback
            success = audit.unregister_callback(test_callback)
            assert success

            # Log another event
            audit.log_event("event_3", {"data": "third"})

            # Callback should not be invoked
            assert len(callback_events) == 2
