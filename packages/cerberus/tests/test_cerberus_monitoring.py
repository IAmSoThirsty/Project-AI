"""Tests for cerberus.security.modules.monitoring — stale alert detection."""

from datetime import UTC, datetime, timedelta

from cerberus.security import AlertSeverity, SecurityMonitor


class TestStaleAlerts:
    def test_stale_open_alert_is_returned(self) -> None:
        """An OPEN alert 30 minutes old is caught by a 15-minute threshold."""
        monitor = SecurityMonitor()
        alert = monitor.alert_manager.create_alert(
            severity=AlertSeverity.WARNING,
            title="Stale alert",
            description="should be flagged",
            category="test",
        )
        # Make the alert 30 minutes old.
        alert.created_at = datetime.now(UTC) - timedelta(minutes=30)

        stale = monitor.check_stale_alerts(threshold_minutes=15)
        assert alert in stale
        assert len(stale) == 1

    def test_recent_open_alert_not_returned(self) -> None:
        """A freshly-created OPEN alert is not stale."""
        monitor = SecurityMonitor()
        monitor.alert_manager.create_alert(
            severity=AlertSeverity.INFO,
            title="Fresh",
            description="just created",
            category="test",
        )
        assert monitor.check_stale_alerts(threshold_minutes=15) == []

    def test_resolved_old_alert_not_returned(self) -> None:
        """An old alert that has been resolved is not stale."""
        monitor = SecurityMonitor()
        alert = monitor.alert_manager.create_alert(
            severity=AlertSeverity.ERROR,
            title="Old resolved",
            description="resolved long ago",
            category="test",
        )
        alert.created_at = datetime.now(UTC) - timedelta(minutes=60)
        monitor.alert_manager.resolve_alert(alert.alert_id, user="tester")

        assert monitor.check_stale_alerts(threshold_minutes=15) == []

    def test_default_threshold(self) -> None:
        """Default threshold of 15 minutes catches a 20-minute-old alert."""
        monitor = SecurityMonitor()
        alert = monitor.alert_manager.create_alert(
            severity=AlertSeverity.CRITICAL,
            title="Slightly stale",
            description="20 min old",
            category="test",
        )
        alert.created_at = datetime.now(UTC) - timedelta(minutes=20)
        stale = monitor.check_stale_alerts()
        assert alert in stale
