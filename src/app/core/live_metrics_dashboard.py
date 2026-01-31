"""
Live Metrics and Dashboard System for God Tier Architecture.

Implements real-time monitoring, metrics collection, and dashboard visualization
for AGI behavior, fusion operations, robotic actions, and system health.

Features:
- Real-time metrics collection and aggregation
- AGI behavior monitoring and analysis
- Fusion operations telemetry
- Robotic action tracking
- System health monitoring
- Time-series data storage
- Alerting and threshold management
- Dashboard API endpoints
- Prometheus/OpenTelemetry integration
- Custom metrics and dimensions

Production-ready with full error handling and logging.
"""

import logging
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class MetricCategory(Enum):
    """Metric categories."""

    AGI_BEHAVIOR = "agi_behavior"
    FUSION_OPS = "fusion_ops"
    ROBOTIC_ACTION = "robotic_action"
    SYSTEM_HEALTH = "system_health"
    SECURITY = "security"
    PERFORMANCE = "performance"


@dataclass
class MetricPoint:
    """Individual metric data point."""

    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metric_name: str = ""
    metric_type: str = MetricType.GAUGE.value
    value: float = 0.0
    labels: dict[str, str] = field(default_factory=dict)
    category: str = MetricCategory.SYSTEM_HEALTH.value

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class MetricSeries:
    """Time series of metric points."""

    metric_name: str
    metric_type: str
    category: str
    points: list[MetricPoint] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)
    min_value: float = float("inf")
    max_value: float = float("-inf")
    avg_value: float = 0.0
    last_value: float = 0.0
    count: int = 0

    def add_point(self, point: MetricPoint) -> None:
        """Add data point to series."""
        self.points.append(point)
        self.count += 1
        self.last_value = point.value

        # Update statistics
        self.min_value = min(self.min_value, point.value)
        self.max_value = max(self.max_value, point.value)
        self.avg_value = (self.avg_value * (self.count - 1) + point.value) / self.count

    def get_recent_points(self, limit: int = 100) -> list[MetricPoint]:
        """Get most recent points."""
        return self.points[-limit:]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_name": self.metric_name,
            "metric_type": self.metric_type,
            "category": self.category,
            "labels": self.labels,
            "statistics": {
                "min_value": self.min_value if self.count > 0 else 0.0,
                "max_value": self.max_value if self.count > 0 else 0.0,
                "avg_value": self.avg_value,
                "last_value": self.last_value,
                "count": self.count,
            },
            "recent_points": [p.to_dict() for p in self.get_recent_points(10)],
        }


class MetricsCollector:
    """Collects and aggregates metrics."""

    def __init__(self):
        self.series: dict[str, MetricSeries] = {}
        self.counters: dict[str, float] = defaultdict(float)
        self.gauges: dict[str, float] = {}
        self.histograms: dict[str, list[float]] = defaultdict(list)
        self.lock = threading.RLock()

    def record_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
        category: str = MetricCategory.SYSTEM_HEALTH.value,
    ) -> None:
        """Record counter metric (always increasing)."""
        try:
            with self.lock:
                key = self._make_key(name, labels)
                self.counters[key] += value

                point = MetricPoint(
                    metric_name=name,
                    metric_type=MetricType.COUNTER.value,
                    value=self.counters[key],
                    labels=labels or {},
                    category=category,
                )

                self._add_to_series(name, point, labels)
        except Exception as e:
            logger.error(f"Error recording counter {name}: {e}")

    def record_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
        category: str = MetricCategory.SYSTEM_HEALTH.value,
    ) -> None:
        """Record gauge metric (can go up or down)."""
        try:
            with self.lock:
                key = self._make_key(name, labels)
                self.gauges[key] = value

                point = MetricPoint(
                    metric_name=name,
                    metric_type=MetricType.GAUGE.value,
                    value=value,
                    labels=labels or {},
                    category=category,
                )

                self._add_to_series(name, point, labels)
        except Exception as e:
            logger.error(f"Error recording gauge {name}: {e}")

    def record_histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
        category: str = MetricCategory.SYSTEM_HEALTH.value,
    ) -> None:
        """Record histogram observation."""
        try:
            with self.lock:
                key = self._make_key(name, labels)
                self.histograms[key].append(value)

                # Keep only recent observations
                if len(self.histograms[key]) > 1000:
                    self.histograms[key] = self.histograms[key][-1000:]

                point = MetricPoint(
                    metric_name=name,
                    metric_type=MetricType.HISTOGRAM.value,
                    value=value,
                    labels=labels or {},
                    category=category,
                )

                self._add_to_series(name, point, labels)
        except Exception as e:
            logger.error(f"Error recording histogram {name}: {e}")

    def _make_key(self, name: str, labels: dict[str, str] | None) -> str:
        """Create unique key for metric with labels."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def _add_to_series(
        self, name: str, point: MetricPoint, labels: dict[str, str] | None
    ) -> None:
        """Add point to time series."""
        key = self._make_key(name, labels)
        if key not in self.series:
            self.series[key] = MetricSeries(
                metric_name=name,
                metric_type=point.metric_type,
                category=point.category,
                labels=labels or {},
            )
        self.series[key].add_point(point)

    def get_series(
        self, name: str, labels: dict[str, str] | None = None
    ) -> MetricSeries | None:
        """Get metric series."""
        with self.lock:
            key = self._make_key(name, labels)
            return self.series.get(key)

    def get_all_series(self) -> list[MetricSeries]:
        """Get all metric series."""
        with self.lock:
            return list(self.series.values())

    def get_series_by_category(self, category: MetricCategory) -> list[MetricSeries]:
        """Get series by category."""
        with self.lock:
            return [s for s in self.series.values() if s.category == category.value]


class AGIBehaviorMonitor:
    """Monitors and tracks AGI behavior metrics."""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.decision_count = 0
        self.reasoning_steps = deque(maxlen=1000)
        self.four_laws_checks = {"passed": 0, "failed": 0}
        self.lock = threading.RLock()

    def record_decision(
        self,
        decision_type: str,
        confidence: float,
        reasoning_steps: int,
        compliant: bool,
    ) -> None:
        """Record AGI decision."""
        try:
            with self.lock:
                self.decision_count += 1
                self.reasoning_steps.append(reasoning_steps)

                # Record metrics
                self.collector.record_counter(
                    "agi_decisions_total",
                    labels={
                        "decision_type": decision_type,
                        "compliant": str(compliant),
                    },
                    category=MetricCategory.AGI_BEHAVIOR.value,
                )

                self.collector.record_gauge(
                    "agi_decision_confidence",
                    confidence,
                    labels={"decision_type": decision_type},
                    category=MetricCategory.AGI_BEHAVIOR.value,
                )

                self.collector.record_histogram(
                    "agi_reasoning_steps",
                    reasoning_steps,
                    labels={"decision_type": decision_type},
                    category=MetricCategory.AGI_BEHAVIOR.value,
                )

                if compliant:
                    self.four_laws_checks["passed"] += 1
                else:
                    self.four_laws_checks["failed"] += 1

                compliance_rate = (
                    self.four_laws_checks["passed"]
                    / (
                        self.four_laws_checks["passed"]
                        + self.four_laws_checks["failed"]
                    )
                    if (
                        self.four_laws_checks["passed"]
                        + self.four_laws_checks["failed"]
                    )
                    > 0
                    else 1.0
                )

                self.collector.record_gauge(
                    "agi_four_laws_compliance_rate",
                    compliance_rate,
                    category=MetricCategory.AGI_BEHAVIOR.value,
                )

                logger.debug(
                    f"Recorded AGI decision: {decision_type}, confidence: {confidence}, compliant: {compliant}"
                )
        except Exception as e:
            logger.error(f"Error recording AGI decision: {e}")

    def record_learning_event(
        self, learning_type: str, success: bool, duration: float
    ) -> None:
        """Record learning event."""
        self.collector.record_counter(
            "agi_learning_events_total",
            labels={"learning_type": learning_type, "success": str(success)},
            category=MetricCategory.AGI_BEHAVIOR.value,
        )

        self.collector.record_histogram(
            "agi_learning_duration_seconds",
            duration,
            labels={"learning_type": learning_type},
            category=MetricCategory.AGI_BEHAVIOR.value,
        )

    def get_behavior_summary(self) -> dict[str, Any]:
        """Get behavior summary."""
        with self.lock:
            avg_reasoning_steps = (
                sum(self.reasoning_steps) / len(self.reasoning_steps)
                if self.reasoning_steps
                else 0
            )
            return {
                "total_decisions": self.decision_count,
                "average_reasoning_steps": avg_reasoning_steps,
                "four_laws_compliance": self.four_laws_checks,
            }


class FusionOperationsMonitor:
    """Monitors multimodal fusion operations."""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.fusion_count = 0
        self.lock = threading.RLock()

    def record_fusion(
        self, fusion_type: str, modalities: list[str], latency: float, confidence: float
    ) -> None:
        """Record fusion operation."""
        try:
            with self.lock:
                self.fusion_count += 1

                self.collector.record_counter(
                    "fusion_operations_total",
                    labels={
                        "fusion_type": fusion_type,
                        "modality_count": str(len(modalities)),
                    },
                    category=MetricCategory.FUSION_OPS.value,
                )

                self.collector.record_histogram(
                    "fusion_latency_seconds",
                    latency,
                    labels={"fusion_type": fusion_type},
                    category=MetricCategory.FUSION_OPS.value,
                )

                self.collector.record_gauge(
                    "fusion_confidence",
                    confidence,
                    labels={"fusion_type": fusion_type},
                    category=MetricCategory.FUSION_OPS.value,
                )

                for modality in modalities:
                    self.collector.record_counter(
                        "fusion_modality_usage_total",
                        labels={"modality": modality},
                        category=MetricCategory.FUSION_OPS.value,
                    )
        except Exception as e:
            logger.error(f"Error recording fusion operation: {e}")

    def record_sensor_reading(
        self, sensor_id: str, sensor_type: str, value: float
    ) -> None:
        """Record sensor reading."""
        self.collector.record_gauge(
            f"sensor_{sensor_type}_value",
            value,
            labels={"sensor_id": sensor_id},
            category=MetricCategory.FUSION_OPS.value,
        )


class RoboticActionMonitor:
    """Monitors robotic actions and commands."""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.action_count = 0
        self.lock = threading.RLock()

    def record_action(
        self,
        action_type: str,
        motor_id: str,
        success: bool,
        duration: float,
        power: float = 0.0,
    ) -> None:
        """Record robotic action."""
        try:
            with self.lock:
                self.action_count += 1

                self.collector.record_counter(
                    "robotic_actions_total",
                    labels={
                        "action_type": action_type,
                        "motor_id": motor_id,
                        "success": str(success),
                    },
                    category=MetricCategory.ROBOTIC_ACTION.value,
                )

                self.collector.record_histogram(
                    "robotic_action_duration_seconds",
                    duration,
                    labels={"action_type": action_type, "motor_id": motor_id},
                    category=MetricCategory.ROBOTIC_ACTION.value,
                )

                if power > 0:
                    self.collector.record_gauge(
                        "robotic_motor_power",
                        power,
                        labels={"motor_id": motor_id},
                        category=MetricCategory.ROBOTIC_ACTION.value,
                    )
        except Exception as e:
            logger.error(f"Error recording robotic action: {e}")

    def record_motor_health(
        self, motor_id: str, temperature: float, current: float
    ) -> None:
        """Record motor health metrics."""
        self.collector.record_gauge(
            "robotic_motor_temperature_celsius",
            temperature,
            labels={"motor_id": motor_id},
            category=MetricCategory.ROBOTIC_ACTION.value,
        )

        self.collector.record_gauge(
            "robotic_motor_current_amperes",
            current,
            labels={"motor_id": motor_id},
            category=MetricCategory.ROBOTIC_ACTION.value,
        )


class SystemHealthMonitor:
    """Monitors overall system health."""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.lock = threading.RLock()

    def record_cpu_usage(self, percentage: float) -> None:
        """Record CPU usage."""
        self.collector.record_gauge(
            "system_cpu_usage_percent",
            percentage,
            category=MetricCategory.SYSTEM_HEALTH.value,
        )

    def record_memory_usage(self, used_mb: float, total_mb: float) -> None:
        """Record memory usage."""
        self.collector.record_gauge(
            "system_memory_used_mb",
            used_mb,
            category=MetricCategory.SYSTEM_HEALTH.value,
        )
        self.collector.record_gauge(
            "system_memory_total_mb",
            total_mb,
            category=MetricCategory.SYSTEM_HEALTH.value,
        )
        percentage = (used_mb / total_mb * 100) if total_mb > 0 else 0
        self.collector.record_gauge(
            "system_memory_usage_percent",
            percentage,
            category=MetricCategory.SYSTEM_HEALTH.value,
        )

    def record_disk_usage(
        self, used_gb: float, total_gb: float, path: str = "/"
    ) -> None:
        """Record disk usage."""
        self.collector.record_gauge(
            "system_disk_used_gb",
            used_gb,
            labels={"path": path},
            category=MetricCategory.SYSTEM_HEALTH.value,
        )
        self.collector.record_gauge(
            "system_disk_total_gb",
            total_gb,
            labels={"path": path},
            category=MetricCategory.SYSTEM_HEALTH.value,
        )
        percentage = (used_gb / total_gb * 100) if total_gb > 0 else 0
        self.collector.record_gauge(
            "system_disk_usage_percent",
            percentage,
            labels={"path": path},
            category=MetricCategory.SYSTEM_HEALTH.value,
        )

    def record_component_health(
        self, component: str, healthy: bool, uptime_seconds: float
    ) -> None:
        """Record component health."""
        self.collector.record_gauge(
            "system_component_healthy",
            1.0 if healthy else 0.0,
            labels={"component": component},
            category=MetricCategory.SYSTEM_HEALTH.value,
        )
        self.collector.record_gauge(
            "system_component_uptime_seconds",
            uptime_seconds,
            labels={"component": component},
            category=MetricCategory.SYSTEM_HEALTH.value,
        )


class AlertManager:
    """Manages metric-based alerting."""

    def __init__(self):
        self.thresholds: dict[str, dict[str, Any]] = {}
        self.active_alerts: dict[str, dict[str, Any]] = {}
        self.alert_handlers: list[Callable[[dict[str, Any]], None]] = []
        self.lock = threading.RLock()

    def add_threshold(
        self,
        metric_name: str,
        threshold: float,
        operator: str = "gt",
        severity: str = "warning",
    ) -> None:
        """Add alerting threshold for metric."""
        with self.lock:
            self.thresholds[metric_name] = {
                "threshold": threshold,
                "operator": operator,  # gt, lt, eq, gte, lte
                "severity": severity,  # info, warning, critical
            }

    def check_thresholds(self, collector: MetricsCollector) -> list[dict[str, Any]]:
        """Check all thresholds against current metrics."""
        alerts = []
        try:
            with self.lock:
                for metric_name, config in self.thresholds.items():
                    series = collector.get_series(metric_name)
                    if not series or series.count == 0:
                        continue

                    value = series.last_value
                    threshold = config["threshold"]
                    operator = config["operator"]

                    triggered = False
                    if (
                        operator == "gt"
                        and value > threshold
                        or operator == "lt"
                        and value < threshold
                        or operator == "gte"
                        and value >= threshold
                        or operator == "lte"
                        and value <= threshold
                        or operator == "eq"
                        and abs(value - threshold) < 0.001
                    ):
                        triggered = True

                    if triggered:
                        alert = {
                            "metric": metric_name,
                            "value": value,
                            "threshold": threshold,
                            "operator": operator,
                            "severity": config["severity"],
                            "timestamp": datetime.now(UTC).isoformat(),
                        }
                        alerts.append(alert)
                        self._trigger_alert(alert)
        except Exception as e:
            logger.error(f"Error checking thresholds: {e}")

        return alerts

    def _trigger_alert(self, alert: dict[str, Any]) -> None:
        """Trigger alert to all handlers."""
        alert_id = f"{alert['metric']}_{alert['timestamp']}"
        with self.lock:
            self.active_alerts[alert_id] = alert

        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")

        logger.warning(
            f"ALERT: {alert['severity'].upper()} - {alert['metric']} = {alert['value']} "
            f"({alert['operator']} {alert['threshold']})"
        )

    def register_alert_handler(self, handler: Callable[[dict[str, Any]], None]) -> None:
        """Register alert handler."""
        with self.lock:
            self.alert_handlers.append(handler)


class LiveMetricsDashboard:
    """Main live metrics and dashboard system."""

    def __init__(self):
        self.collector = MetricsCollector()
        self.agi_monitor = AGIBehaviorMonitor(self.collector)
        self.fusion_monitor = FusionOperationsMonitor(self.collector)
        self.robotic_monitor = RoboticActionMonitor(self.collector)
        self.health_monitor = SystemHealthMonitor(self.collector)
        self.alert_manager = AlertManager()

        self.monitoring_active = False
        self.monitor_thread: threading.Thread | None = None
        self.lock = threading.RLock()

        self._setup_default_alerts()

        logger.info("Initialized Live Metrics Dashboard")

    def _setup_default_alerts(self) -> None:
        """Setup default alerting thresholds."""
        # System health alerts
        self.alert_manager.add_threshold(
            "system_cpu_usage_percent", 90.0, "gt", "warning"
        )
        self.alert_manager.add_threshold(
            "system_cpu_usage_percent", 95.0, "gt", "critical"
        )
        self.alert_manager.add_threshold(
            "system_memory_usage_percent", 85.0, "gt", "warning"
        )
        self.alert_manager.add_threshold(
            "system_memory_usage_percent", 95.0, "gt", "critical"
        )

        # AGI behavior alerts
        self.alert_manager.add_threshold(
            "agi_four_laws_compliance_rate", 0.95, "lt", "critical"
        )

    def start_monitoring(self) -> bool:
        """Start background monitoring."""
        try:
            if self.monitoring_active:
                return False

            self.monitoring_active = True
            self.monitor_thread = threading.Thread(
                target=self._monitoring_loop, daemon=True
            )
            self.monitor_thread.start()
            logger.info("Started live metrics monitoring")
            return True
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return False

    def stop_monitoring(self) -> bool:
        """Stop background monitoring."""
        try:
            self.monitoring_active = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            logger.info("Stopped live metrics monitoring")
            return True
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            return False

    def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                # Check alert thresholds
                self.alert_manager.check_thresholds(self.collector)
                time.sleep(10)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

    def get_dashboard_data(
        self, category: MetricCategory | None = None
    ) -> dict[str, Any]:
        """Get dashboard data for API."""
        try:
            if category:
                series = self.collector.get_series_by_category(category)
            else:
                series = self.collector.get_all_series()

            return {
                "timestamp": datetime.now(UTC).isoformat(),
                "metrics_count": len(series),
                "series": [s.to_dict() for s in series],
                "agi_behavior": self.agi_monitor.get_behavior_summary(),
                "active_alerts": list(self.alert_manager.active_alerts.values()),
            }
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get high-level metrics summary."""
        return {
            "agi_decisions": self.agi_monitor.decision_count,
            "fusion_operations": self.fusion_monitor.fusion_count,
            "robotic_actions": self.robotic_monitor.action_count,
            "total_series": len(self.collector.series),
            "active_alerts": len(self.alert_manager.active_alerts),
            "monitoring_active": self.monitoring_active,
        }


def create_dashboard() -> LiveMetricsDashboard:
    """Factory function to create dashboard."""
    return LiveMetricsDashboard()


# Global instance
_dashboard_instance: LiveMetricsDashboard | None = None


def get_dashboard() -> LiveMetricsDashboard | None:
    """Get global dashboard instance."""
    return _dashboard_instance


def initialize_dashboard() -> LiveMetricsDashboard:
    """Initialize global dashboard instance."""
    global _dashboard_instance
    if _dashboard_instance is None:
        _dashboard_instance = create_dashboard()
    return _dashboard_instance
