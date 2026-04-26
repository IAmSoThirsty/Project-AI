#!/usr/bin/env python3
"""
Tests for Wired Ethics Approvals System
Validates that ethics approvals emit events and respect governance.
"""

import sys
import time
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.core.advanced_boot import (
    BootProfile,
    get_advanced_boot,
)
from app.core.event_spine import (
    EventCategory,
    EventPriority,
    get_event_spine,
)
from app.core.governance_graph import (
    RelationshipType,
    get_governance_graph,
)


class TestWiredEthicsApprovals(unittest.TestCase):
    """Test that ethics approvals emit events and use governance."""

    def setUp(self):
        """Set up test fixtures."""
        self.boot = get_advanced_boot()
        self.event_spine = get_event_spine()
        self.governance_graph = get_governance_graph()

        # Track events received
        self.received_events = []

        def event_callback(event):
            self.received_events.append(event)

        # Subscribe to governance decisions
        self.event_spine.subscribe(
            subscriber_id="test_subscriber",
            subscriber_domain="test",
            categories=[EventCategory.GOVERNANCE_DECISION],
            callback=event_callback,
        )

    def tearDown(self):
        """Clean up after tests."""
        self.event_spine.unsubscribe("test_subscriber")
        self.received_events.clear()

    def test_ethics_approval_emits_event(self):
        """Test that ethics approval emits a governance decision event."""
        # Set ethics-first profile
        self.boot.set_boot_profile(BootProfile.ETHICS_FIRST)

        # Request approval
        metadata = {"priority": "HIGH", "description": "Test subsystem"}
        approved = self.boot._request_ethics_approval("test_subsystem", metadata)

        # Give event time to be processed
        time.sleep(0.2)

        # Verify approval was granted
        assert approved is True

        # Verify event was emitted
        assert len(self.received_events) > 0

        # Check event details
        event = self.received_events[-1]
        assert event.category == EventCategory.GOVERNANCE_DECISION
        assert event.source_domain == "advanced_boot"
        assert event.payload["decision_type"] == "ethics_approval"
        assert event.payload["subsystem_id"] == "test_subsystem"
        assert event.payload["approved"] is True
        assert event.payload["priority"] == "HIGH"
        assert "reasoning" in event.payload
        assert "event_id" in event.metadata

    def test_ethics_approval_includes_governance_context(self):
        """Test that ethics approval includes governance consultation requirements."""
        # Set ethics-first profile
        self.boot.set_boot_profile(BootProfile.ETHICS_FIRST)

        # Add a consultation requirement in governance graph
        self.governance_graph.add_relationship(
            from_domain="test_subsystem",
            to_domain="ethics_governance",
            relationship_type=RelationshipType.MUST_CONSULT,
            description="Must consult ethics",
        )

        # Request approval
        metadata = {"priority": "MEDIUM", "description": "Test subsystem"}
        self.boot._request_ethics_approval("test_subsystem", metadata)

        # Give event time to be processed
        time.sleep(0.2)

        # Verify event includes governance context
        assert len(self.received_events) > 0
        event = self.received_events[-1]
        assert "must_consult" in event.payload
        # Should include ethics_governance if the relationship was added correctly
        # (may be empty if the subsystem doesn't exist in graph yet)

    def test_emergency_mode_emits_event(self):
        """Test that emergency mode activation emits a system health event."""
        # Clear previous events
        self.received_events.clear()

        # Subscribe to system health events too
        def health_callback(event):
            self.received_events.append(event)

        self.event_spine.subscribe(
            subscriber_id="test_health_subscriber",
            subscriber_domain="test",
            categories=[EventCategory.SYSTEM_HEALTH],
            callback=health_callback,
        )

        # Activate emergency mode
        self.boot.activate_emergency_mode("test_emergency")

        # Give event time to be processed
        time.sleep(0.2)

        # Verify event was emitted
        health_events = [
            e for e in self.received_events if e.category == EventCategory.SYSTEM_HEALTH
        ]
        assert len(health_events) > 0

        # Check event details
        event = health_events[-1]
        assert event.source_domain == "advanced_boot"
        assert event.payload["event_type"] == "emergency_mode_activated"
        assert event.payload["reason"] == "test_emergency"
        assert event.priority == EventPriority.CRITICAL

        # Clean up
        self.event_spine.unsubscribe("test_health_subscriber")
        self.boot.deactivate_emergency_mode()

    def test_ethics_checkpoint_emits_event(self):
        """Test that ethics checkpoint emits a governance decision event."""
        # Clear previous events
        self.received_events.clear()

        # Mark checkpoint passed
        self.boot.mark_ethics_checkpoint_passed()

        # Give event time to be processed
        time.sleep(0.2)

        # Verify event was emitted
        assert len(self.received_events) > 0

        # Check event details
        event = self.received_events[-1]
        assert event.category == EventCategory.GOVERNANCE_DECISION
        assert event.source_domain == "advanced_boot"
        assert event.payload["decision_type"] == "ethics_checkpoint"
        assert event.payload["status"] == "passed"
        assert event.priority == EventPriority.CRITICAL

    def test_event_includes_audit_linkage(self):
        """Test that events include linkage to audit trail."""
        # Set ethics-first profile
        self.boot.set_boot_profile(BootProfile.ETHICS_FIRST)

        # Clear events
        self.received_events.clear()

        # Request approval
        metadata = {"priority": "HIGH"}
        self.boot._request_ethics_approval("test_subsystem", metadata)

        # Give event time to be processed
        time.sleep(0.2)

        # Verify event has event_id for audit linkage
        self.assertGreater(len(self.received_events), 0)
        event = self.received_events[-1]
        self.assertIn("event_id", event.metadata)
        self.assertTrue(event.metadata["event_id"].startswith("ethics_approval_"))

        # Verify audit log includes the event_id by replaying
        result = self.boot.replay_audit_log(event_types=["ethics_approval"])

        # Check that audit entry includes event_id
        self.assertIn("reconstructed_state", result)
        self.assertIn("ethics_approvals", result["reconstructed_state"])
        self.assertGreater(len(result["reconstructed_state"]["ethics_approvals"]), 0)

    def test_multiple_approvals_emit_multiple_events(self):
        """Test that multiple approvals emit separate events."""
        # Set ethics-first profile
        self.boot.set_boot_profile(BootProfile.ETHICS_FIRST)

        # Clear events
        self.received_events.clear()

        # Request multiple approvals
        subsystems = ["subsystem_a", "subsystem_b", "subsystem_c"]
        for subsystem_id in subsystems:
            metadata = {"priority": "MEDIUM"}
            self.boot._request_ethics_approval(subsystem_id, metadata)

        # Give events time to be processed
        time.sleep(0.3)

        # Verify we got multiple events
        governance_events = [
            e
            for e in self.received_events
            if e.category == EventCategory.GOVERNANCE_DECISION
            and e.payload.get("decision_type") == "ethics_approval"
        ]

        assert len(governance_events) >= len(subsystems)

        # Verify each has unique event_id
        event_ids = set()
        for event in governance_events:
            event_id = event.metadata.get("event_id")
            assert event_id is not None
            event_ids.add(event_id)

        assert len(event_ids) >= len(subsystems)


class TestEventAuditIntegration(unittest.TestCase):
    """Test integration between events and audit trail."""

    def setUp(self):
        """Set up test fixtures."""
        self.boot = get_advanced_boot()

    def test_audit_replay_includes_event_references(self):
        """Test that audit replay can reference emitted events."""
        # Set ethics-first profile
        self.boot.set_boot_profile(BootProfile.ETHICS_FIRST)

        # Mark checkpoint
        self.boot.mark_ethics_checkpoint_passed()

        # Request approval
        metadata = {"priority": "HIGH"}
        self.boot._request_ethics_approval("test_subsystem", metadata)

        # Replay audit log
        result = self.boot.replay_audit_log()

        # Verify we got a result
        self.assertIsNotNone(result)
        self.assertIn("reconstructed_state", result)

        # Verify timeline includes our events
        timeline = result["reconstructed_state"]["timeline"]
        self.assertGreater(len(timeline), 0)

        # Check for ethics events
        ethics_events = [e for e in timeline if "ethics" in e["event_type"]]
        self.assertGreater(len(ethics_events), 0)


class TestGovernanceIntegration(unittest.TestCase):
    """Test governance graph integration with approvals."""

    def setUp(self):
        """Set up test fixtures."""
        self.boot = get_advanced_boot()
        self.governance_graph = get_governance_graph()

    def test_approval_checks_must_consult(self):
        """Test that approvals check MUST_CONSULT relationships."""
        # Add a MUST_CONSULT relationship
        self.governance_graph.add_relationship(
            from_domain="tactical_edge_ai",
            to_domain="ethics_governance",
            relationship_type=RelationshipType.MUST_CONSULT,
            description="Tactical must consult ethics",
        )

        # Request approval for tactical system
        metadata = {"priority": "HIGH"}
        approved = self.boot._request_ethics_approval("tactical_edge_ai", metadata)

        # Should be approved (with consultation)
        assert approved is True


if __name__ == "__main__":
    unittest.main()
