"""
cerberus.security.modules.monitoring — Alerts, metrics, anomaly detection.

Ported from upstream ``IAmSoThirsty/Cerberus``
``src/cerberus/security/modules/monitoring.py``. Alert management, rolling
metric windows with z-score anomaly detection, incident tracking, and a
Prometheus text exporter. Timestamps are UTC; failing alert handlers are
logged (upstream printed / silently swallowed).
"""

from __future__ import annotations

import logging
import secrets
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert lifecycle status."""

    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class Alert:
    """Security alert."""

    alert_id: str
    severity: AlertSeverity
    title: str
    description: str
    category: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: AlertStatus = AlertStatus.OPEN
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    resolved_at: datetime | None = None
    resolved_by: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the alert to a JSON-serializable dictionary."""
        data = asdict(self)
        data["severity"] = self.severity.value
        data["status"] = self.status.value
        data["created_at"] = self.created_at.isoformat()
        if self.resolved_at:
            data["resolved_at"] = self.resolved_at.isoformat()
        return data


@dataclass
class SecurityMetric:
    """Security metric data point."""

    name: str
    value: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class Incident:
    """Security incident."""

    incident_id: str
    title: str
    description: str
    severity: AlertSeverity
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: str = "open"
    related_alerts: list[str] = field(default_factory=list)
    timeline: list[dict[str, Any]] = field(default_factory=list)
    assigned_to: str | None = None
    resolved_at: datetime | None = None


AlertHandler = Callable[[Alert], None]


class AlertManager:
    """Manages security alerts and severity-scoped handlers."""

    def __init__(self) -> None:
        """Initialize with an empty alert store and no handlers."""
        self.alerts: dict[str, Alert] = {}
        self.handlers: dict[AlertSeverity | None, list[AlertHandler]] = defaultdict(list)

    def create_alert(
        self,
        severity: AlertSeverity,
        title: str,
        description: str,
        category: str,
        source: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Alert:
        """Create, store, and dispatch a new alert."""
        alert = Alert(
            alert_id=f"alert_{secrets.token_hex(8)}",
            severity=severity,
            title=title,
            description=description,
            category=category,
            source=source,
            metadata=metadata or {},
        )
        self.alerts[alert.alert_id] = alert
        self._trigger_handlers(alert)
        return alert

    def _trigger_handlers(self, alert: Alert) -> None:
        for handler in [*self.handlers[alert.severity], *self.handlers[None]]:
            try:
                handler(alert)
            except Exception:
                logger.exception("alert_handler_error", extra={"alert_id": alert.alert_id})

    def register_handler(
        self, handler: AlertHandler, severity: AlertSeverity | None = None
    ) -> None:
        """Register a handler for a severity (or all severities when None)."""
        self.handlers[severity].append(handler)

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark an alert as acknowledged."""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.ACKNOWLEDGED
            return True
        return False

    def resolve_alert(self, alert_id: str, user: str | None = None) -> bool:
        """Mark an alert as resolved."""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now(UTC)
            alert.resolved_by = user
            return True
        return False

    def get_active_alerts(self, severity: AlertSeverity | None = None) -> list[Alert]:
        """Return open/acknowledged alerts, newest first."""
        alerts = [
            a
            for a in self.alerts.values()
            if a.status in (AlertStatus.OPEN, AlertStatus.ACKNOWLEDGED)
        ]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return sorted(alerts, key=lambda a: a.created_at, reverse=True)

    def get_statistics(self) -> dict[str, Any]:
        """Return alert counts by severity, status, and category."""
        stats: dict[str, Any] = {
            "total_alerts": len(self.alerts),
            "by_severity": {},
            "by_status": {},
            "by_category": {},
        }
        for alert in self.alerts.values():
            sev = alert.severity.value
            stats["by_severity"][sev] = stats["by_severity"].get(sev, 0) + 1
            status = alert.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            cat = alert.category
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
        return stats


class SecurityMonitor:
    """Real-time metric monitoring with z-score anomaly alerting."""

    MIN_SAMPLES_FOR_ANOMALY = 10

    def __init__(
        self,
        alert_manager: AlertManager | None = None,
        anomaly_threshold: float = 3.0,
        window_size: int = 100,
    ) -> None:
        """Initialize with an alert manager, anomaly threshold, and window."""
        self.alert_manager = alert_manager or AlertManager()
        self.anomaly_threshold = anomaly_threshold
        self.window_size = window_size
        self.metrics: dict[str, deque[SecurityMetric]] = defaultdict(
            lambda: deque(maxlen=window_size)
        )
        self.incidents: dict[str, Incident] = {}
        self.counters: dict[str, int] = defaultdict(int)

    def record_metric(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Record a metric sample and check it for anomalies."""
        self.metrics[name].append(SecurityMetric(name=name, value=value, labels=labels or {}))
        self._check_anomaly(name)

    def increment_counter(self, name: str, amount: int = 1) -> None:
        """Increment a named counter."""
        self.counters[name] += amount

    def get_counter(self, name: str) -> int:
        """Return a counter's value."""
        return self.counters.get(name, 0)

    def _check_anomaly(self, metric_name: str) -> None:
        metrics = list(self.metrics[metric_name])
        if len(metrics) < self.MIN_SAMPLES_FOR_ANOMALY:
            return

        values = [m.value for m in metrics]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance**0.5
        latest = values[-1]

        if std_dev > 0:
            z_score = abs(latest - mean) / std_dev
            if z_score > self.anomaly_threshold:
                self.alert_manager.create_alert(
                    severity=AlertSeverity.WARNING,
                    title=f"Anomaly detected in {metric_name}",
                    description=(
                        f"Value {latest:.2f} deviates {z_score:.2f} standard "
                        f"deviations from mean {mean:.2f}"
                    ),
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
        """Create a tracked incident and its associated alert."""
        incident = Incident(
            incident_id=f"incident_{secrets.token_hex(8)}",
            title=title,
            description=description,
            severity=severity,
            related_alerts=related_alerts or [],
        )
        self.incidents[incident.incident_id] = incident
        self.alert_manager.create_alert(
            severity=severity,
            title=f"Incident: {title}",
            description=description,
            category="incident",
            source="security_monitor",
            metadata={"incident_id": incident.incident_id},
        )
        return incident

    def get_metric_stats(self, metric_name: str) -> dict[str, Any] | None:
        """Return summary statistics for a metric, or None if empty."""
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

    def get_all_metrics(self) -> dict[str, dict[str, Any] | None]:
        """Return summary statistics for every recorded metric."""
        return {name: self.get_metric_stats(name) for name in self.metrics}

    def export_prometheus_metrics(self) -> str:
        """Export counters and latest gauges in Prometheus text format."""
        lines: list[str] = []
        for name, value in self.counters.items():
            safe_name = name.replace("-", "_").replace(".", "_")
            lines.append(f"# TYPE cerberus_{safe_name} counter")
            lines.append(f"cerberus_{safe_name} {value}")

        for metric_name, metric_deque in self.metrics.items():
            if metric_deque:
                safe_name = metric_name.replace("-", "_").replace(".", "_")
                latest = metric_deque[-1]
                lines.append(f"# TYPE cerberus_{safe_name} gauge")
                labels = ""
                if latest.labels:
                    label_str = ",".join(f'{k}="{v}"' for k, v in latest.labels.items())
                    labels = f"{{{label_str}}}"
                lines.append(f"cerberus_{safe_name}{labels} {latest.value}")

        return "\n".join(lines)

    def get_system_health(self) -> dict[str, Any]:
        """Return an overall health status from active alerts and incidents."""
        active_alerts = self.alert_manager.get_active_alerts()
        critical = sum(1 for a in active_alerts if a.severity == AlertSeverity.CRITICAL)
        errors = sum(1 for a in active_alerts if a.severity == AlertSeverity.ERROR)
        warnings = sum(1 for a in active_alerts if a.severity == AlertSeverity.WARNING)

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
            "open_incidents": sum(1 for i in self.incidents.values() if i.status == "open"),
        }

    def check_stale_alerts(self, threshold_minutes: int = 15) -> list[Alert]:
        """Return OPEN alerts older than *threshold_minutes* from now."""
        cutoff = datetime.now(UTC) - timedelta(minutes=threshold_minutes)
        return [
            alert
            for alert in self.alert_manager.alerts.values()
            if alert.status == AlertStatus.OPEN and alert.created_at < cutoff
        ]

    def clear_old_data(self, days: int = 30) -> None:
        """Remove resolved/closed alerts older than the given age."""
        cutoff = datetime.now(UTC) - timedelta(days=days)
        for alert_id in list(self.alert_manager.alerts.keys()):
            alert = self.alert_manager.alerts[alert_id]
            if (
                alert.status in (AlertStatus.CLOSED, AlertStatus.RESOLVED)
                and alert.created_at < cutoff
            ):
                del self.alert_manager.alerts[alert_id]


__all__ = [
    "Alert",
    "AlertManager",
    "AlertSeverity",
    "AlertStatus",
    "Incident",
    "SecurityMetric",
    "SecurityMonitor",
]
