"""
Tier Health Dashboard - Monitoring and visualization for three-tier platform health.

This module provides real-time monitoring and health dashboards for all three tiers:
- Tier 1 (Governance): Policy enforcement, audit compliance
- Tier 2 (Infrastructure): Resource utilization, isolation status
- Tier 3 (Application): Service availability, request throughput

MONITORING DOMAINS:
- Component health (alive, paused, failed)
- Authority flow compliance (no upward authority)
- Resource allocation efficiency
- Governance decision latency
- Cross-tier request patterns

=== FORMAL SPECIFICATION ===

## Dashboard Views

### Executive Dashboard
- Overall platform health (green/yellow/red)
- Tier-by-tier status summary
- Recent violations and alerts
- Resource utilization trends

### Tier 1 Dashboard
- Governance decision rate
- Policy enforcement success rate
- Audit log completeness
- Triumvirate consensus patterns
- Rollback history

### Tier 2 Dashboard
- Resource allocation efficiency
- Isolation domain health
- Scaling decision effectiveness
- Blocked application tracking
- Infrastructure constraint violations

### Tier 3 Dashboard
- Application component availability
- Request throughput and latency
- Capability request success rate
- Service registration status
- Sandboxing compliance

=== END FORMAL SPECIFICATION ===
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from app.core.platform_tiers import PlatformTier, TierHealthStatus, get_tier_registry

logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Type Definitions
# ============================================================================


class HealthLevel(Enum):
    """Overall health level for a tier or platform."""

    HEALTHY = "healthy"  # All systems operational
    DEGRADED = "degraded"  # Some issues, but functional
    CRITICAL = "critical"  # Major issues, limited functionality
    OFFLINE = "offline"  # Tier is not operational


class MetricType(Enum):
    """Type of health metric."""

    AVAILABILITY = "availability"  # Component uptime
    THROUGHPUT = "throughput"  # Request rate
    LATENCY = "latency"  # Response time
    ERROR_RATE = "error_rate"  # Failure rate
    RESOURCE_USAGE = "resource_usage"  # CPU/memory/etc
    COMPLIANCE = "compliance"  # Policy adherence


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class HealthMetric:
    """A single health metric measurement."""

    metric_name: str
    metric_type: MetricType
    value: float
    unit: str
    threshold_warning: float | None = None
    threshold_critical: float | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def get_health_level(self) -> HealthLevel:
        """Determine health level based on thresholds."""
        if self.threshold_critical and self.value >= self.threshold_critical:
            return HealthLevel.CRITICAL
        if self.threshold_warning and self.value >= self.threshold_warning:
            return HealthLevel.DEGRADED
        return HealthLevel.HEALTHY


@dataclass
class ComponentHealthReport:
    """Health report for a single component."""

    component_id: str
    component_name: str
    tier: PlatformTier
    is_operational: bool
    is_paused: bool
    uptime_seconds: float
    metrics: list[HealthMetric] = field(default_factory=list)
    recent_errors: list[str] = field(default_factory=list)
    last_check: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def get_overall_health(self) -> HealthLevel:
        """Calculate overall health from metrics."""
        if not self.is_operational:
            return HealthLevel.OFFLINE
        if self.is_paused:
            return HealthLevel.DEGRADED

        # Check metrics
        critical_count = sum(
            1 for m in self.metrics if m.get_health_level() == HealthLevel.CRITICAL
        )
        warning_count = sum(
            1 for m in self.metrics if m.get_health_level() == HealthLevel.DEGRADED
        )

        if critical_count > 0:
            return HealthLevel.CRITICAL
        if warning_count > 0:
            return HealthLevel.DEGRADED

        return HealthLevel.HEALTHY


@dataclass
class TierHealthReport:
    """Comprehensive health report for a tier."""

    tier: PlatformTier
    tier_status: TierHealthStatus
    component_reports: list[ComponentHealthReport]
    overall_health: HealthLevel
    active_violations: int
    recent_alerts: list[str]
    metrics: dict[str, HealthMetric]
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class PlatformHealthReport:
    """Complete platform health report across all tiers."""

    overall_health: HealthLevel
    tier_reports: dict[int, TierHealthReport]  # tier number -> report
    total_components: int
    active_components: int
    paused_components: int
    failed_components: int
    total_violations: int
    uptime_seconds: float
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class HealthAlert:
    """Health alert for significant events."""

    alert_id: str
    severity: HealthLevel
    tier: PlatformTier | None
    component_id: str | None
    message: str
    metric: HealthMetric | None = None
    acknowledged: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


# ============================================================================
# Health Monitor
# ============================================================================


class TierHealthMonitor:
    """
    Monitors health of all three tiers in real-time.

    Responsibilities:
    - Collect metrics from all components
    - Detect anomalies and violations
    - Generate health reports
    - Raise alerts for critical issues
    - Track health trends over time
    """

    def __init__(self):
        """Initialize the health monitor."""
        self._start_time = time.time()
        self._component_start_times: dict[str, float] = {}
        self._alerts: list[HealthAlert] = []
        self._alert_counter = 0

        # Metric storage
        self._tier1_metrics: dict[str, HealthMetric] = {}
        self._tier2_metrics: dict[str, HealthMetric] = {}
        self._tier3_metrics: dict[str, HealthMetric] = {}

        logger.info("TierHealthMonitor initialized")

    def collect_component_health(
        self, component_id: str
    ) -> ComponentHealthReport | None:
        """
        Collect health report for a single component.

        Args:
            component_id: Component to check

        Returns:
            ComponentHealthReport or None if component not found
        """
        registry = get_tier_registry()
        component = registry.get_component(component_id)

        if not component:
            logger.warning("Component %s not found in registry", component_id)
            return None

        # Track component start time
        if component_id not in self._component_start_times:
            self._component_start_times[component_id] = time.time()

        uptime = time.time() - self._component_start_times[component_id]
        is_paused = registry.is_component_paused(component_id)

        # Collect basic metrics
        metrics = []

        # Availability metric
        availability_metric = HealthMetric(
            metric_name="availability",
            metric_type=MetricType.AVAILABILITY,
            value=100.0 if not is_paused else 0.0,
            unit="percent",
            threshold_warning=95.0,
            threshold_critical=90.0,
        )
        metrics.append(availability_metric)

        # Uptime metric
        uptime_metric = HealthMetric(
            metric_name="uptime",
            metric_type=MetricType.AVAILABILITY,
            value=uptime,
            unit="seconds",
        )
        metrics.append(uptime_metric)

        return ComponentHealthReport(
            component_id=component_id,
            component_name=component.component_name,
            tier=component.tier,
            is_operational=True,  # Assume operational if registered
            is_paused=is_paused,
            uptime_seconds=uptime,
            metrics=metrics,
            recent_errors=[],
        )

    def collect_tier_health(self, tier: PlatformTier) -> TierHealthReport:
        """
        Collect health report for an entire tier.

        Args:
            tier: Tier to check

        Returns:
            TierHealthReport with comprehensive tier health
        """
        registry = get_tier_registry()
        tier_status = registry.get_tier_health(tier)

        # Collect health for all components in tier
        components = registry.get_tier_components(tier)
        component_reports = []

        for component in components:
            report = self.collect_component_health(component.component_id)
            if report:
                component_reports.append(report)

        # Calculate overall tier health
        if tier_status.active_components == 0:
            overall_health = HealthLevel.OFFLINE
        elif tier_status.failed_components > 0:
            overall_health = HealthLevel.CRITICAL
        elif tier_status.paused_components > 0:
            overall_health = HealthLevel.DEGRADED
        else:
            # Check component health levels
            critical_components = sum(
                1
                for r in component_reports
                if r.get_overall_health() == HealthLevel.CRITICAL
            )
            if critical_components > 0:
                overall_health = HealthLevel.CRITICAL
            else:
                overall_health = HealthLevel.HEALTHY

        # Get violations
        violations = registry.get_all_violations()
        tier_violations = [
            v for v in violations if v.source_tier == tier or v.target_tier == tier
        ]

        # Select tier-specific metrics
        if tier == PlatformTier.TIER_1_GOVERNANCE:
            tier_metrics = self._tier1_metrics.copy()
        elif tier == PlatformTier.TIER_2_INFRASTRUCTURE:
            tier_metrics = self._tier2_metrics.copy()
        else:
            tier_metrics = self._tier3_metrics.copy()

        return TierHealthReport(
            tier=tier,
            tier_status=tier_status,
            component_reports=component_reports,
            overall_health=overall_health,
            active_violations=len(tier_violations),
            recent_alerts=[],  # Populated by alert system
            metrics=tier_metrics,
        )

    def collect_platform_health(self) -> PlatformHealthReport:
        """
        Collect comprehensive platform health across all tiers.

        Returns:
            PlatformHealthReport with complete platform status
        """
        # Collect tier reports
        tier_reports = {}
        for tier in [
            PlatformTier.TIER_1_GOVERNANCE,
            PlatformTier.TIER_2_INFRASTRUCTURE,
            PlatformTier.TIER_3_APPLICATION,
        ]:
            tier_reports[tier.value] = self.collect_tier_health(tier)

        # Calculate overall platform health
        tier_health_levels = [r.overall_health for r in tier_reports.values()]

        if HealthLevel.OFFLINE in tier_health_levels:
            overall_health = HealthLevel.OFFLINE
        elif HealthLevel.CRITICAL in tier_health_levels:
            overall_health = HealthLevel.CRITICAL
        elif HealthLevel.DEGRADED in tier_health_levels:
            overall_health = HealthLevel.DEGRADED
        else:
            overall_health = HealthLevel.HEALTHY

        # Aggregate statistics
        total_components = sum(
            r.tier_status.component_count for r in tier_reports.values()
        )
        active_components = sum(
            r.tier_status.active_components for r in tier_reports.values()
        )
        paused_components = sum(
            r.tier_status.paused_components for r in tier_reports.values()
        )
        failed_components = sum(
            r.tier_status.failed_components for r in tier_reports.values()
        )
        total_violations = sum(r.active_violations for r in tier_reports.values())

        uptime = time.time() - self._start_time

        return PlatformHealthReport(
            overall_health=overall_health,
            tier_reports=tier_reports,
            total_components=total_components,
            active_components=active_components,
            paused_components=paused_components,
            failed_components=failed_components,
            total_violations=total_violations,
            uptime_seconds=uptime,
        )

    def record_metric(self, tier: PlatformTier, metric: HealthMetric) -> None:
        """
        Record a health metric for a tier.

        Args:
            tier: Tier the metric belongs to
            metric: Metric to record
        """
        if tier == PlatformTier.TIER_1_GOVERNANCE:
            self._tier1_metrics[metric.metric_name] = metric
        elif tier == PlatformTier.TIER_2_INFRASTRUCTURE:
            self._tier2_metrics[metric.metric_name] = metric
        else:
            self._tier3_metrics[metric.metric_name] = metric

        # Check if metric exceeds thresholds
        health_level = metric.get_health_level()
        if health_level in (HealthLevel.CRITICAL, HealthLevel.DEGRADED):
            self._raise_alert(tier, None, metric, health_level)

    def _raise_alert(
        self,
        tier: PlatformTier,
        component_id: str | None,
        metric: HealthMetric,
        severity: HealthLevel,
    ) -> None:
        """Raise a health alert."""
        alert = HealthAlert(
            alert_id=f"alert_{self._alert_counter}",
            severity=severity,
            tier=tier,
            component_id=component_id,
            message=f"Metric {metric.metric_name} exceeded threshold: {metric.value} {metric.unit}",
            metric=metric,
        )
        self._alerts.append(alert)
        self._alert_counter += 1

        logger.warning(
            "Health alert raised: %s [%s] - %s",
            alert.alert_id,
            severity.value,
            alert.message,
        )

    def get_alerts(self, acknowledged: bool | None = None) -> list[HealthAlert]:
        """
        Get health alerts.

        Args:
            acknowledged: Filter by acknowledged status (None = all)

        Returns:
            List of health alerts
        """
        if acknowledged is None:
            return self._alerts.copy()
        return [a for a in self._alerts if a.acknowledged == acknowledged]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge an alert.

        Args:
            alert_id: Alert to acknowledge

        Returns:
            bool: True if alert found and acknowledged
        """
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                logger.info("Alert acknowledged: %s", alert_id)
                return True
        return False

    def format_health_report(self, report: PlatformHealthReport) -> str:
        """
        Format platform health report as human-readable string.

        Args:
            report: Platform health report

        Returns:
            Formatted string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("PLATFORM HEALTH REPORT")
        lines.append("=" * 70)
        lines.append(f"Overall Status: {report.overall_health.value.upper()}")
        lines.append(f"Platform Uptime: {report.uptime_seconds:.1f}s")
        lines.append(f"Total Components: {report.total_components}")
        lines.append(f"  Active: {report.active_components}")
        lines.append(f"  Paused: {report.paused_components}")
        lines.append(f"  Failed: {report.failed_components}")
        lines.append(f"Active Violations: {report.total_violations}")
        lines.append("")

        # Tier-by-tier breakdown
        for tier_num, tier_report in sorted(report.tier_reports.items()):
            lines.append(f"TIER {tier_num} - {tier_report.tier.name}")
            lines.append("-" * 70)
            lines.append(f"  Status: {tier_report.overall_health.value.upper()}")
            lines.append(f"  Components: {len(tier_report.component_reports)}")
            lines.append(f"  Active: {tier_report.tier_status.active_components}")
            lines.append(f"  Paused: {tier_report.tier_status.paused_components}")
            lines.append(f"  Violations: {tier_report.active_violations}")

            # Component details
            for comp_report in tier_report.component_reports:
                status_icon = "✓" if comp_report.is_operational else "✗"
                pause_icon = "(PAUSED)" if comp_report.is_paused else ""
                lines.append(
                    f"    {status_icon} {comp_report.component_name} "
                    f"[{comp_report.get_overall_health().value}] {pause_icon}"
                )
            lines.append("")

        lines.append("=" * 70)
        return "\n".join(lines)


# ============================================================================
# Global Monitor Access
# ============================================================================


_global_monitor: TierHealthMonitor | None = None


def get_health_monitor() -> TierHealthMonitor:
    """
    Get the global tier health monitor.

    Returns:
        TierHealthMonitor: Global monitor singleton
    """
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = TierHealthMonitor()
    return _global_monitor
