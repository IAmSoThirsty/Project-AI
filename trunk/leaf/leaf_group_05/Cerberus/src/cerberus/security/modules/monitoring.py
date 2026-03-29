# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / monitoring.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / monitoring.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Monitoring and Alerting Module

Real-time security monitoring with:
- Anomaly tracking
- Incident detection
- Alert management
- Metrics collection (Prometheus-ready)
"""

from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class AlertSeverity(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status"""

    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class Alert:
    """Security alert"""

    alert_id: str
    severity: AlertSeverity
    title: str
    description: str
    category: str
    created_at: datetime = field(default_factory=datetime.now)
    status: AlertStatus = AlertStatus.OPEN
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    resolved_at: datetime | None = None
    resolved_by: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        data = asdict(self)
        data["severity"] = self.severity.value
        data["status"] = self.status.value
        data["created_at"] = self.created_at.isoformat()
        if self.resolved_at:
            data["resolved_at"] = self.resolved_at.isoformat()
        return data


@dataclass
class SecurityMetric:
    """Security metric data point"""

    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class Incident:
    """Security incident"""

    incident_id: str
    title: str
    description: str
    severity: AlertSeverity
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "open"
    related_alerts: list[str] = field(default_factory=list)
    timeline: list[dict] = field(default_factory=list)
    assigned_to: str | None = None
    resolved_at: datetime | None = None


class AlertManager:
    """
    Manages security alerts and notifications
    """

    def __init__(self):
        """Initialize alert manager"""
        self.alerts: dict[str, Alert] = {}
        self.handlers: dict[AlertSeverity, list[Callable]] = defaultdict(list)

    def create_alert(
        self,
        severity: AlertSeverity,
        title: str,
        description: str,
        category: str,
        source: str | None = None,
        metadata: dict | None = None,
    ) -> Alert:
        """
        Create new alert

        Args:
            severity: Alert severity
            title: Alert title
            description: Alert description
            category: Alert category
            source: Alert source
            metadata: Additional metadata

        Returns:
            Created alert
        """
        import secrets

        alert_id = f"alert_{secrets.token_hex(8)}"

        alert = Alert(
            alert_id=alert_id,
            severity=severity,
            title=title,
            description=description,
            category=category,
            source=source,
            metadata=metadata or {},
        )

        self.alerts[alert_id] = alert

        # Trigger handlers
        self._trigger_handlers(alert)

        return alert

    def _trigger_handlers(self, alert: Alert):
        """Trigger registered handlers for alert"""
        # Trigger handlers for this severity
        for handler in self.handlers[alert.severity]:
            try:
                handler(alert)
            except Exception as e:
                # Log handler error but don't fail
                print(f"Alert handler error: {e}")

        # Trigger handlers for ALL severities
        for handler in self.handlers.get(None, []):
            try:
                handler(alert)
            except Exception:
                pass

    def register_handler(
        self, handler: Callable, severity: AlertSeverity | None = None
    ):
        """
        Register alert handler

        Args:
            handler: Callable that takes Alert as parameter
            severity: Severity to trigger on (None for all)
        """
        self.handlers[severity].append(handler)

    def acknowledge_alert(self, alert_id: str, user: str | None = None) -> bool:
        """Acknowledge alert"""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.ACKNOWLEDGED
            return True
        return False

    def resolve_alert(self, alert_id: str, user: str | None = None) -> bool:
        """Resolve alert"""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            alert.resolved_by = user
            return True
        return False

    def get_active_alerts(self, severity: AlertSeverity | None = None) -> list[Alert]:
        """Get active (not resolved) alerts"""
        alerts = [
            a
            for a in self.alerts.values()
            if a.status in [AlertStatus.OPEN, AlertStatus.ACKNOWLEDGED]
        ]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return sorted(alerts, key=lambda a: a.created_at, reverse=True)

    def get_statistics(self) -> dict:
        """Get alert statistics"""
        stats = {
            "total_alerts": len(self.alerts),
            "by_severity": {},
            "by_status": {},
            "by_category": {},
        }

        for alert in self.alerts.values():
            # By severity
            sev = alert.severity.value
            stats["by_severity"][sev] = stats["by_severity"].get(sev, 0) + 1

            # By status
            status = alert.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # By category
            cat = alert.category
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1

        return stats


class SecurityMonitor:
    """
    Real-time security monitoring and anomaly detection
    """

    def __init__(
        self,
        alert_manager: AlertManager | None = None,
        anomaly_threshold: float = 3.0,
        window_size: int = 100,
    ):
        """
        Initialize security monitor

        Args:
            alert_manager: Alert manager instance
            anomaly_threshold: Standard deviations for anomaly detection
            window_size: Size of rolling window for metrics
        """
        self.alert_manager = alert_manager or AlertManager()
        self.anomaly_threshold = anomaly_threshold
        self.window_size = window_size

        # Metric storage
        self.metrics: dict[str, deque[SecurityMetric]] = defaultdict(
            lambda: deque(maxlen=window_size)
        )

        # Incident tracking
        self.incidents: dict[str, Incident] = {}

        # Counter metrics
        self.counters: dict[str, int] = defaultdict(int)

    def record_metric(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ):
        """
        Record security metric

        Args:
            name: Metric name
            value: Metric value
            labels: Optional labels
        """
        metric = SecurityMetric(name=name, value=value, labels=labels or {})

        self.metrics[name].append(metric)

        # Check for anomalies
        self._check_anomaly(name)

    def increment_counter(self, name: str, amount: int = 1):
        """Increment counter metric"""
        self.counters[name] += amount

    def get_counter(self, name: str) -> int:
        """Get counter value"""
        return self.counters.get(name, 0)

    def _check_anomaly(self, metric_name: str):
        """Check for anomalies in metric"""
        metrics = list(self.metrics[metric_name])

        if len(metrics) < 10:  # Need enough data
            return

        # Calculate mean and std dev
        values = [m.value for m in metrics]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance**0.5

        # Check if latest value is anomalous
        latest = values[-1]
        if std_dev > 0:
            z_score = abs(latest - mean) / std_dev

            if z_score > self.anomaly_threshold:
                self.alert_manager.create_alert(
                    severity=AlertSeverity.WARNING,
                    title=f"Anomaly detected in {metric_name}",
                    description=f"Value {latest:.2f} deviates {z_score:.2f} standard deviations from mean {mean:.2f}",
                    category="anomaly",
                    source="security_monitor",
                    metadata={
                        "metric": metric_name,
                        "value": latest,
                        "mean": mean,
                        "std_dev": std_dev,
                        "z_score": z_score,
                    },
                )

    def create_incident(
        self,
        title: str,
        description: str,
        severity: AlertSeverity,
        related_alerts: list[str] | None = None,
    ) -> Incident:
        """Create security incident"""
        import secrets

        incident_id = f"incident_{secrets.token_hex(8)}"

        incident = Incident(
            incident_id=incident_id,
            title=title,
            description=description,
            severity=severity,
            related_alerts=related_alerts or [],
        )

        self.incidents[incident_id] = incident

        # Create alert for incident
        self.alert_manager.create_alert(
            severity=severity,
            title=f"Incident: {title}",
            description=description,
            category="incident",
            source="security_monitor",
            metadata={"incident_id": incident_id},
        )

        return incident

    def get_metric_stats(self, metric_name: str) -> dict | None:
        """Get statistics for metric"""
        metrics = list(self.metrics.get(metric_name, []))

        if not metrics:
            return None

        values = [m.value for m in metrics]

        return {
            "name": metric_name,
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
            "latest": values[-1],
        }

    def get_all_metrics(self) -> dict[str, dict]:
        """Get all metric statistics"""
        return {
            name: self.get_metric_stats(name) for name in self.metrics.keys()
        }

    def export_prometheus_metrics(self) -> str:
        """
        Export metrics in Prometheus format

        Returns:
            Prometheus-formatted metrics string
        """
        lines = []

        # Export counters
        for name, value in self.counters.items():
            safe_name = name.replace("-", "_").replace(".", "_")
            lines.append(f"# TYPE cerberus_{safe_name} counter")
            lines.append(f"cerberus_{safe_name} {value}")

        # Export gauges (latest metric values)
        for metric_name, metric_deque in self.metrics.items():
            if metric_deque:
                safe_name = metric_name.replace("-", "_").replace(".", "_")
                latest = metric_deque[-1]

                lines.append(f"# TYPE cerberus_{safe_name} gauge")

                # Add labels if present
                labels = ""
                if latest.labels:
                    label_str = ",".join(
                        f'{k}="{v}"' for k, v in latest.labels.items()
                    )
                    labels = f"{{{label_str}}}"

                lines.append(f"cerberus_{safe_name}{labels} {latest.value}")

        return "\n".join(lines)

    def get_system_health(self) -> dict:
        """Get overall system health status"""
        active_alerts = self.alert_manager.get_active_alerts()

        # Count by severity
        critical = len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL])
        errors = len([a for a in active_alerts if a.severity == AlertSeverity.ERROR])
        warnings = len([a for a in active_alerts if a.severity == AlertSeverity.WARNING])

        # Determine health status
        if critical > 0:
            status = "critical"
        elif errors > 0:
            status = "degraded"
        elif warnings > 0:
            status = "warning"
        else:
            status = "healthy"

        return {
            "status": status,
            "active_alerts": len(active_alerts),
            "critical_alerts": critical,
            "error_alerts": errors,
            "warning_alerts": warnings,
            "open_incidents": len(
                [i for i in self.incidents.values() if i.status == "open"]
            ),
        }

    def clear_old_data(self, days: int = 30):
        """Clear old metrics and alerts"""
        cutoff = datetime.now() - timedelta(days=days)

        # Clear old alerts
        for alert_id in list(self.alerts.keys()):
            alert = self.alert_manager.alerts[alert_id]
            if (
                alert.status == AlertStatus.CLOSED
                or alert.status == AlertStatus.RESOLVED
            ) and alert.created_at < cutoff:
                del self.alert_manager.alerts[alert_id]
