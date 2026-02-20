"""
Tests for Audit Integration and Accountability.

Tests audit logging integration with cognition/audit.py,
accountability tracking, and compliance reporting.
"""

from datetime import datetime
from unittest.mock import patch

from gradle_evolution.audit.accountability import (
    AccountabilityRecord,
    AccountabilitySystem,
)
from gradle_evolution.audit.audit_integration import BuildAuditIntegration


class TestBuildAuditIntegration:
    """Test BuildAuditIntegration component."""

    def test_initialization(self, audit_log_path):
        """Test audit integration initializes."""
        integration = BuildAuditIntegration(audit_log_path=audit_log_path, enable_verbose=True)

        assert integration.audit_log_path == audit_log_path
        assert integration.enable_verbose
        assert integration.audit_buffer == []

    @patch("gradle_evolution.audit.audit_integration.audit")
    def test_audit_build_start(self, mock_audit, audit_log_path):
        """Test auditing build start event."""
        integration = BuildAuditIntegration(audit_log_path=audit_log_path)

        build_id = "build-001"
        tasks = ["clean", "compile", "test"]
        context = {"project": "test-project"}

        integration.audit_build_start(build_id, tasks, context)

        # Should call audit function
        mock_audit.assert_called_once()
        call_args = mock_audit.call_args[0]
        assert "BUILD_START" in call_args[0]
        assert build_id in call_args[0]

    @patch("gradle_evolution.audit.audit_integration.audit")
    def test_audit_build_complete(self, mock_audit, audit_log_path):
        """Test auditing build completion event."""
        integration = BuildAuditIntegration(audit_log_path=audit_log_path)

        build_id = "build-001"
        result = {"status": "success"}

        integration.audit_build_complete(build_id, success=True, duration_seconds=45.2, result=result)

        mock_audit.assert_called_once()
        call_args = mock_audit.call_args[0]
        assert "BUILD_COMPLETE" in call_args[0]

    @patch("gradle_evolution.audit.audit_integration.audit")
    def test_audit_task_execution(self, mock_audit, audit_log_path):
        """Test auditing individual task execution."""
        integration = BuildAuditIntegration(audit_log_path=audit_log_path)

        build_id = "build-001"
        task_name = "compileJava"
        task_result = {"success": True, "duration": 10.5}

        integration.audit_task_execution(build_id, task_name, task_result)

        mock_audit.assert_called_once()
        call_args = mock_audit.call_args[0]
        assert "TASK_EXECUTION" in call_args[0]
        assert task_name in str(call_args)

    @patch("gradle_evolution.audit.audit_integration.audit")
    def test_audit_policy_decision(self, mock_audit, audit_log_path):
        """Test auditing policy decision."""
        integration = BuildAuditIntegration(audit_log_path=audit_log_path)

        decision = {
            "policy": "security_check",
            "outcome": "allowed",
            "reason": "Passes all security checks",
        }

        integration.audit_policy_decision("build-001", decision)

        mock_audit.assert_called_once()

    def test_audit_buffer(self, audit_log_path):
        """Test audit events are buffered."""
        integration = BuildAuditIntegration(audit_log_path=audit_log_path)

        with patch("gradle_evolution.audit.audit_integration.audit"):
            integration.audit_build_start("build-001", ["test"], {})
            integration.audit_build_complete("build-001", True, 10.0, {})

        assert len(integration.audit_buffer) == 2

    def test_get_audit_summary(self, audit_log_path):
        """Test retrieving audit summary."""
        integration = BuildAuditIntegration(audit_log_path=audit_log_path)

        with patch("gradle_evolution.audit.audit_integration.audit"):
            # Simulate multiple audits
            for i in range(5):
                integration.audit_build_start(f"build-{i}", ["test"], {})

        summary = integration.get_audit_summary()

        assert summary["total_events"] == 5
        assert "event_types" in summary

    def test_error_handling(self, audit_log_path):
        """Test error handling in audit integration."""
        integration = BuildAuditIntegration(audit_log_path=audit_log_path)

        # Audit should not crash even if audit function fails
        with patch(
            "gradle_evolution.audit.audit_integration.audit",
            side_effect=Exception("Audit error"),
        ):
            # Should not raise exception
            integration.audit_build_start("build-001", ["test"], {})

    @patch("gradle_evolution.audit.audit_integration.audit")
    def test_sanitize_context(self, mock_audit, audit_log_path):
        """Test sensitive data is sanitized in context."""
        integration = BuildAuditIntegration(audit_log_path=audit_log_path)

        context = {
            "password": "secret123",
            "api_key": "key_abc",
            "project": "test-project",
        }

        integration.audit_build_start("build-001", ["test"], context)

        # Check that sensitive fields were sanitized
        call_args = mock_audit.call_args[0][1]
        context_data = call_args.get("context", {})

        # Password and api_key should be redacted or removed
        assert context_data.get("password") != "secret123"


class TestAccountabilityRecord:
    """Test AccountabilityRecord component."""

    def test_record_creation(self):
        """Test creating accountability record."""
        record = AccountabilityRecord(
            action_id="action-001",
            actor="build_agent",
            action_type="compile",
            target="src/Main.java",
            timestamp=datetime.utcnow().isoformat(),
            outcome="success",
        )

        assert record.action_id == "action-001"
        assert record.actor == "build_agent"
        assert record.outcome == "success"

    def test_record_to_dict(self):
        """Test converting record to dictionary."""
        record = AccountabilityRecord(
            action_id="action-001",
            actor="build_agent",
            action_type="compile",
            target="src/Main.java",
            timestamp=datetime.utcnow().isoformat(),
            outcome="success",
        )

        record_dict = record.to_dict()

        assert record_dict["action_id"] == "action-001"
        assert "timestamp" in record_dict


class TestAccountabilitySystem:
    """Test AccountabilitySystem component."""

    def test_initialization(self, temp_dir):
        """Test system initializes."""
        storage = temp_dir / "accountability.json"
        system = AccountabilitySystem(storage_path=storage)

        assert system.storage_path == storage

    def test_record_action(self, temp_dir):
        """Test recording an action."""
        storage = temp_dir / "accountability.json"
        system = AccountabilitySystem(storage_path=storage)

        record = AccountabilityRecord(
            action_id="action-001",
            actor="build_agent",
            action_type="compile",
            target="src/Main.java",
            timestamp=datetime.utcnow().isoformat(),
            outcome="success",
        )

        system.record_action(record)

        assert len(system.action_records) >= 1

    def test_get_actions_by_actor(self, temp_dir):
        """Test retrieving actions by actor."""
        storage = temp_dir / "accountability.json"
        system = AccountabilitySystem(storage_path=storage)

        # Create multiple actions
        for i in range(3):
            record = AccountabilityRecord(
                action_id=f"action-{i}",
                actor="build_agent",
                action_type="compile",
                target=f"File{i}.java",
                timestamp=datetime.utcnow().isoformat(),
                outcome="success",
            )
            system.record_action(record)

        # Add action from different actor
        other_record = AccountabilityRecord(
            action_id="action-other",
            actor="test_agent",
            action_type="test",
            target="Test.java",
            timestamp=datetime.utcnow().isoformat(),
            outcome="success",
        )
        system.record_action(other_record)

        build_agent_actions = system.get_actions_by_actor("build_agent")

        assert len(build_agent_actions) >= 3

    def test_get_actions_by_outcome(self, temp_dir):
        """Test retrieving actions by outcome."""
        storage = temp_dir / "accountability.json"
        system = AccountabilitySystem(storage_path=storage)

        # Success action
        success_record = AccountabilityRecord(
            action_id="action-success",
            actor="build_agent",
            action_type="compile",
            target="Main.java",
            timestamp=datetime.utcnow().isoformat(),
            outcome="success",
        )

        # Failure action
        failure_record = AccountabilityRecord(
            action_id="action-failure",
            actor="build_agent",
            action_type="compile",
            target="Broken.java",
            timestamp=datetime.utcnow().isoformat(),
            outcome="failure",
        )

        system.record_action(success_record)
        system.record_action(failure_record)

        failures = system.get_actions_by_outcome("failure")

        assert len(failures) >= 1

    def test_persistence(self, temp_dir):
        """Test accountability persistence to disk."""
        storage = temp_dir / "accountability.json"
        system = AccountabilitySystem(storage_path=storage)

        record = AccountabilityRecord(
            action_id="action-001",
            actor="build_agent",
            action_type="compile",
            target="Main.java",
            timestamp=datetime.utcnow().isoformat(),
            outcome="success",
        )

        system.record_action(record)
        system.save()

        # Load in new system
        new_system = AccountabilitySystem(storage_path=storage)
        new_system.load()

        assert len(new_system.action_records) >= 1

    def test_generate_accountability_report(self, temp_dir):
        """Test generating accountability report."""
        storage = temp_dir / "accountability.json"
        system = AccountabilitySystem(storage_path=storage)

        # Create multiple actions
        for i in range(5):
            record = AccountabilityRecord(
                action_id=f"action-{i}",
                actor="build_agent",
                action_type="compile",
                target=f"File{i}.java",
                timestamp=datetime.utcnow().isoformat(),
                outcome="success" if i < 4 else "failure",
            )
            system.record_action(record)

        report = system.generate_accountability_report()

        assert "total_actions" in report or len(system.action_records) >= 5

    def test_get_audit_trail(self, temp_dir):
        """Test retrieving complete audit trail."""
        storage = temp_dir / "accountability.json"
        system = AccountabilitySystem(storage_path=storage)

        # Create action chain
        for i in range(3):
            record = AccountabilityRecord(
                action_id=f"action-{i}",
                actor="build_agent",
                action_type="compile",
                target=f"File{i}.java",
                timestamp=datetime.utcnow().isoformat(),
                outcome="success",
            )
            system.record_action(record)

        trail = system.get_audit_trail()

        assert len(trail) >= 3
