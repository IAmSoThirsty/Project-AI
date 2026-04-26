#!/usr/bin/env python3
"""
Tests for Advanced Boot System
"""

import shutil
import sys
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app.core.advanced_boot import AdvancedBootSystem, BootProfile


class TestBootProfiles(unittest.TestCase):
    """Test staged boot profiles."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.boot_system = AdvancedBootSystem(data_dir=self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def test_default_profiles_exist(self):
        """Test that all default boot profiles exist."""
        expected_profiles = {
            BootProfile.NORMAL,
            BootProfile.EMERGENCY,
            BootProfile.ETHICS_FIRST,
            BootProfile.MINIMAL,
            BootProfile.RECOVERY,
            BootProfile.DIAGNOSTIC,
            BootProfile.AIR_GAPPED,
            BootProfile.ADVERSARIAL,
        }

        for profile in expected_profiles:
            self.assertIn(profile, self.boot_system._profiles)

    def test_set_boot_profile(self):
        """Test setting boot profile."""
        result = self.boot_system.set_boot_profile(BootProfile.EMERGENCY)

        self.assertTrue(result)
        self.assertEqual(self.boot_system.get_current_profile(), BootProfile.EMERGENCY)

    def test_normal_profile_allows_all(self):
        """Test that normal profile allows all subsystems."""
        self.boot_system.set_boot_profile(BootProfile.NORMAL)

        should_init, reason = self.boot_system.should_initialize_subsystem(
            "test_subsystem", {"priority": "MEDIUM"}
        )

        self.assertTrue(should_init)
        self.assertIsNone(reason)

    def test_emergency_profile_whitelist(self):
        """Test that emergency profile only allows critical subsystems."""
        self.boot_system.set_boot_profile(BootProfile.EMERGENCY)

        # Should allow critical subsystem
        should_init, reason = self.boot_system.should_initialize_subsystem(
            "ethics_governance", {"priority": "CRITICAL"}
        )
        self.assertTrue(should_init)

        # Should block non-critical subsystem
        should_init, reason = self.boot_system.should_initialize_subsystem(
            "random_subsystem", {"priority": "MEDIUM"}
        )
        self.assertFalse(should_init)
        self.assertIn("whitelist", reason.lower())

    def test_minimal_profile(self):
        """Test minimal profile with only essential subsystems."""
        self.boot_system.set_boot_profile(BootProfile.MINIMAL)

        # Should allow only whitelisted subsystems
        should_init, reason = self.boot_system.should_initialize_subsystem(
            "ethics_governance", {"priority": "CRITICAL"}
        )
        self.assertTrue(should_init)

        should_init, reason = self.boot_system.should_initialize_subsystem(
            "other_subsystem", {"priority": "HIGH"}
        )
        self.assertFalse(should_init)

    def test_priority_override(self):
        """Test priority overrides in boot profiles."""
        self.boot_system.set_boot_profile(BootProfile.ETHICS_FIRST)

        # Ethics should have priority override
        override = self.boot_system.get_priority_override("ethics_governance")
        self.assertEqual(override, "CRITICAL")

        # Others should not
        override = self.boot_system.get_priority_override("random_subsystem")
        self.assertIsNone(override)


class TestEmergencyMode(unittest.TestCase):
    """Test emergency-only mode."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.boot_system = AdvancedBootSystem(data_dir=self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def test_emergency_mode_activation(self):
        """Test emergency mode activation."""
        self.assertFalse(self.boot_system.is_emergency_mode())

        self.boot_system.activate_emergency_mode("test_reason")

        self.assertTrue(self.boot_system.is_emergency_mode())
        self.assertEqual(self.boot_system._boot_stats["emergency_activations"], 1)

    def test_emergency_mode_deactivation(self):
        """Test emergency mode deactivation."""
        self.boot_system.activate_emergency_mode("test")
        self.assertTrue(self.boot_system.is_emergency_mode())

        self.boot_system.deactivate_emergency_mode()

        self.assertFalse(self.boot_system.is_emergency_mode())

    def test_emergency_mode_blocks_non_critical(self):
        """Test that emergency mode blocks non-critical subsystems."""
        self.boot_system.activate_emergency_mode("test")

        # Should block non-critical
        should_init, reason = self.boot_system.should_initialize_subsystem(
            "non_critical_subsystem", {"priority": "LOW"}
        )

        self.assertFalse(should_init)
        self.assertIn("emergency", reason.lower())

    def test_emergency_mode_allows_critical(self):
        """Test that emergency mode allows critical subsystems."""
        self.boot_system.activate_emergency_mode("test")

        # Should allow critical
        should_init, reason = self.boot_system.should_initialize_subsystem(
            "ethics_governance", {"priority": "CRITICAL"}
        )

        self.assertTrue(should_init)


class TestEthicsFirstColdStart(unittest.TestCase):
    """Test ethics-first cold start."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.boot_system = AdvancedBootSystem(data_dir=self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def test_ethics_checkpoint_not_passed_initially(self):
        """Test that ethics checkpoint is not passed initially."""
        self.assertFalse(self.boot_system._ethics_checkpoint_passed)

    def test_mark_ethics_checkpoint_passed(self):
        """Test marking ethics checkpoint as passed."""
        self.boot_system.mark_ethics_checkpoint_passed()

        self.assertTrue(self.boot_system._ethics_checkpoint_passed)

    def test_ethics_first_requires_checkpoint(self):
        """Test that ethics-first profile requires checkpoint."""
        self.boot_system.set_boot_profile(BootProfile.ETHICS_FIRST)

        # Non-ethics subsystem should wait for checkpoint
        should_init, reason = self.boot_system.should_initialize_subsystem(
            "tactical_edge_ai", {"priority": "HIGH"}
        )

        self.assertFalse(should_init)
        self.assertIn("ethics checkpoint", reason.lower())

    def test_ethics_subsystems_initialize_first(self):
        """Test that ethics subsystems can initialize before checkpoint."""
        self.boot_system.set_boot_profile(BootProfile.ETHICS_FIRST)

        # Ethics subsystem should be allowed
        should_init, reason = self.boot_system.should_initialize_subsystem(
            "ethics_governance", {"priority": "CRITICAL"}
        )

        self.assertTrue(should_init)

    def test_after_checkpoint_subsystems_require_approval(self):
        """Test that after checkpoint, subsystems require ethics approval."""
        self.boot_system.set_boot_profile(BootProfile.ETHICS_FIRST)
        self.boot_system.mark_ethics_checkpoint_passed()

        # Should now require approval
        should_init, reason = self.boot_system.should_initialize_subsystem(
            "tactical_edge_ai", {"priority": "HIGH"}
        )

        # First call requests approval, should be granted
        # (auto-approved in test implementation for HIGH priority)
        self.assertTrue(should_init)
        self.assertIn("tactical_edge_ai", self.boot_system._ethics_approvals)


class TestAuditReplay(unittest.TestCase):
    """Test audit replay functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.boot_system = AdvancedBootSystem(data_dir=self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def test_audit_event_creation(self):
        """Test creating audit events."""
        self.boot_system._audit_event(
            event_type="test",
            action="test_action",
            context={"key": "value"},
            result="success",
        )

        self.assertEqual(len(self.boot_system._audit_log), 1)

        event = self.boot_system._audit_log[0]
        self.assertEqual(event.event_type, "test")
        self.assertEqual(event.action, "test_action")
        self.assertEqual(event.context["key"], "value")

    def test_state_snapshot(self):
        """Test state snapshot creation."""
        self.boot_system.set_boot_profile(BootProfile.EMERGENCY)
        self.boot_system.save_state_snapshot("test_snapshot")

        self.assertIn("test_snapshot", self.boot_system._state_snapshots)

        snapshot = self.boot_system._state_snapshots["test_snapshot"]
        self.assertEqual(snapshot["boot_profile"], BootProfile.EMERGENCY.value)

    def test_audit_log_persistence(self):
        """Test that audit events are written to disk."""
        self.boot_system._audit_event(
            event_type="test", action="test_action", context={"key": "value"}
        )

        # Check that audit file was created
        audit_files = list(self.boot_system.audit_dir.glob("audit_*.jsonl"))
        self.assertGreater(len(audit_files), 0)

    def test_audit_log_loading(self):
        """Test loading audit log from disk."""
        # Create some events
        for i in range(3):
            self.boot_system._audit_event(
                event_type="test", action=f"action_{i}", context={"index": i}
            )

        # Load events
        events = self.boot_system.load_audit_log()

        self.assertEqual(len(events), 3)

    def test_replay_audit_log(self):
        """Test replaying audit log."""
        # Create events
        self.boot_system.set_boot_profile(BootProfile.EMERGENCY)
        self.boot_system.activate_emergency_mode("test_emergency")
        self.boot_system.mark_ethics_checkpoint_passed()

        # Replay
        result = self.boot_system.replay_audit_log()

        self.assertIn("reconstructed_state", result)
        self.assertIn("replay_stats", result)

        # Check reconstructed state
        state = result["reconstructed_state"]
        self.assertGreater(len(state["profile_changes"]), 0)
        self.assertGreater(len(state["emergency_activations"]), 0)

    def test_replay_with_time_filter(self):
        """Test replaying audit log with time filter."""
        # Create events at different times
        datetime.now()

        self.boot_system._audit_event(event_type="test", action="action_1", context={})

        time.sleep(0.1)
        middle_time = datetime.now()

        self.boot_system._audit_event(event_type="test", action="action_2", context={})

        # Replay only after middle time
        result = self.boot_system.replay_audit_log(start_time=middle_time)

        stats = result["replay_stats"]
        self.assertLess(stats["filtered_events"], stats["total_events"])

    def test_audit_event_types_filter(self):
        """Test filtering replay by event types."""
        # Create different event types
        self.boot_system._audit_event(event_type="boot", action="start", context={})
        self.boot_system._audit_event(
            event_type="profile_changed", action="set", context={}
        )
        self.boot_system._audit_event(
            event_type="emergency_mode", action="activate", context={}
        )

        # Replay only emergency events
        result = self.boot_system.replay_audit_log(event_types=["emergency_mode"])

        stats = result["replay_stats"]
        self.assertEqual(stats["filtered_events"], 1)


class TestBootStatistics(unittest.TestCase):
    """Test boot statistics tracking."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.boot_system = AdvancedBootSystem(data_dir=self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def test_boot_stats_initialization(self):
        """Test boot statistics initialization."""
        stats = self.boot_system.get_boot_stats()

        self.assertEqual(stats["subsystems_initialized"], 0)
        self.assertEqual(stats["subsystems_skipped"], 0)
        self.assertEqual(stats["emergency_activations"], 0)

    def test_increment_subsystems_initialized(self):
        """Test incrementing subsystems initialized counter."""
        self.boot_system.increment_subsystems_initialized()

        stats = self.boot_system.get_boot_stats()
        self.assertEqual(stats["subsystems_initialized"], 1)

    def test_increment_subsystems_skipped(self):
        """Test incrementing subsystems skipped counter."""
        self.boot_system.increment_subsystems_skipped()

        stats = self.boot_system.get_boot_stats()
        self.assertEqual(stats["subsystems_skipped"], 1)

    def test_boot_sequence_tracking(self):
        """Test tracking full boot sequence."""
        self.boot_system.start_boot(BootProfile.NORMAL)

        # Simulate initialization
        self.boot_system.increment_subsystems_initialized()
        self.boot_system.increment_subsystems_initialized()
        self.boot_system.increment_subsystems_skipped()

        self.boot_system.finish_boot()

        stats = self.boot_system.get_boot_stats()
        self.assertEqual(stats["profile"], BootProfile.NORMAL.value)
        self.assertEqual(stats["subsystems_initialized"], 2)
        self.assertEqual(stats["subsystems_skipped"], 1)
        self.assertIsNotNone(stats["start_time"])
        self.assertIsNotNone(stats["end_time"])


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestBootProfiles))
    suite.addTests(loader.loadTestsFromTestCase(TestEmergencyMode))
    suite.addTests(loader.loadTestsFromTestCase(TestEthicsFirstColdStart))
    suite.addTests(loader.loadTestsFromTestCase(TestAuditReplay))
    suite.addTests(loader.loadTestsFromTestCase(TestBootStatistics))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    import sys

    success = run_tests()
    sys.exit(0 if success else 1)
