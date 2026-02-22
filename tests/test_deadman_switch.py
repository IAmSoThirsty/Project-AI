"""
Tests for DeadmanSwitch implementation.
"""

import threading
import time

import pytest

from app.resilience.deadman_switch import DeadmanSwitch


class TestDeadmanSwitchInit:
    def test_initialises_disabled(self):
        ds = DeadmanSwitch(timeout_seconds=10)
        assert ds.enabled is False
        assert ds.triggered is False
        assert ds.last_heartbeat is None

    def test_default_timeout(self):
        ds = DeadmanSwitch()
        assert ds.timeout_seconds == 300


class TestStartStopMonitoring:
    def test_start_monitoring(self):
        ds = DeadmanSwitch(timeout_seconds=60)
        assert ds.start_monitoring() is True
        assert ds.enabled is True
        assert ds.last_heartbeat is not None
        ds.stop_monitoring()

    def test_double_start_returns_false(self):
        ds = DeadmanSwitch(timeout_seconds=60)
        ds.start_monitoring()
        assert ds.start_monitoring() is False
        ds.stop_monitoring()

    def test_stop_monitoring(self):
        ds = DeadmanSwitch(timeout_seconds=60)
        ds.start_monitoring()
        assert ds.stop_monitoring() is True
        assert ds.enabled is False

    def test_stop_without_start_returns_false(self):
        ds = DeadmanSwitch()
        assert ds.stop_monitoring() is False


class TestHeartbeat:
    def test_heartbeat_when_enabled(self):
        ds = DeadmanSwitch(timeout_seconds=60)
        ds.start_monitoring()
        assert ds.send_heartbeat() is True
        ds.stop_monitoring()

    def test_heartbeat_when_disabled(self):
        ds = DeadmanSwitch()
        assert ds.send_heartbeat() is False


class TestTimeout:
    def test_no_timeout_immediately(self):
        ds = DeadmanSwitch(timeout_seconds=60)
        ds.start_monitoring()
        assert ds.check_timeout() is False
        ds.stop_monitoring()

    def test_timeout_on_expired(self):
        ds = DeadmanSwitch(timeout_seconds=1)
        ds.start_monitoring()
        # Immediately stop monitoring to prevent auto-trigger
        ds._stop_event.set()
        ds.enabled = False
        if ds.monitoring_thread:
            ds.monitoring_thread.join(timeout=3)

        # Manually force expired heartbeat
        from datetime import datetime, timedelta

        ds.enabled = True
        ds.last_heartbeat = datetime.now() - timedelta(seconds=5)
        assert ds.check_timeout() is True
        ds.enabled = False


class TestFailsafe:
    def test_trigger_failsafe(self):
        ds = DeadmanSwitch()
        executed = []
        ds.register_failsafe_action(lambda: executed.append("action1"))
        ds.register_failsafe_action(lambda: executed.append("action2"))

        assert ds.trigger_failsafe("test_reason") is True
        assert ds.triggered is True
        assert executed == ["action1", "action2"]

    def test_double_trigger_returns_false(self):
        ds = DeadmanSwitch()
        ds.trigger_failsafe("first")
        assert ds.trigger_failsafe("second") is False

    def test_failsafe_with_exception(self):
        ds = DeadmanSwitch()
        executed = []

        def bad_action():
            raise RuntimeError("boom")

        ds.register_failsafe_action(bad_action)
        ds.register_failsafe_action(lambda: executed.append("ok"))

        assert ds.trigger_failsafe("error_test") is True
        # Second action should still execute
        assert executed == ["ok"]

    def test_register_non_callable_returns_false(self):
        ds = DeadmanSwitch()
        assert ds.register_failsafe_action("not_callable") is False  # type: ignore[arg-type]

    def test_trigger_history(self):
        ds = DeadmanSwitch()
        ds.trigger_failsafe("test")
        assert len(ds.trigger_history) == 1
        assert ds.trigger_history[0]["reason"] == "test"


class TestAutoTrigger:
    def test_monitoring_thread_triggers_on_timeout(self):
        """Verify the background thread auto-triggers on heartbeat timeout."""
        ds = DeadmanSwitch(timeout_seconds=1)
        triggered_event = threading.Event()

        def on_trigger():
            triggered_event.set()

        ds.register_failsafe_action(on_trigger)
        ds.start_monitoring()

        # Don't send heartbeats — wait for timeout
        triggered_event.wait(timeout=5)
        assert ds.triggered is True
        assert triggered_event.is_set()
        ds.stop_monitoring()


class TestGetStatus:
    def test_status_keys(self):
        ds = DeadmanSwitch()
        status = ds.get_status()
        assert "enabled" in status
        assert "triggered" in status
        assert "timeout_seconds" in status
        assert "last_heartbeat" in status
        assert "failsafe_actions_registered" in status
        assert "trigger_count" in status
