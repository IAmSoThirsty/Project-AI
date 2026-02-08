"""
ATLAS Ω - Layer 13: Failure-Mode Surveillance & Kill-Switch

Production-grade failure detection and emergency shutdown with:
- Continuous monitoring
- Drift detection
- Anomaly detection
- Automatic abort mechanism
- Kill-switch functionality

⚠️ SUBORDINATION NOTICE:
This is a safety system, not an autonomous controller.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np

from atlas.audit.trail import get_audit_trail

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies detected."""
    DRIFT_DETECTION = "drift_detection"
    DRIVER_VOLATILITY = "driver_volatility"
    EDGE_INFLATION = "edge_inflation"
    CLAIM_POSTERIOR_EXPLOSION = "claim_posterior_explosion"
    NARRATIVE_BLEED = "narrative_bleed"
    SENSITIVITY_BLOWUP = "sensitivity_blowup"
    PARAMETER_BOUNDS_VIOLATION = "parameter_bounds_violation"
    HASH_INTEGRITY_FAILURE = "hash_integrity_failure"


class SeverityLevel(Enum):
    """Severity levels for anomalies."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Anomaly:
    """Detected anomaly."""
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: SeverityLevel
    timestamp: datetime

    # Details
    description: str
    metric_name: str | None = None
    value: float | None = None
    threshold: float | None = None

    # Action taken
    action_taken: str = "monitored"


@dataclass
class SystemHealth:
    """Overall system health status."""
    timestamp: datetime
    is_healthy: bool

    # Health scores [0, 1]
    drift_score: float = 1.0  # 1.0 = no drift
    volatility_score: float = 1.0  # 1.0 = stable
    integrity_score: float = 1.0  # 1.0 = intact
    performance_score: float = 1.0  # 1.0 = optimal

    # Anomaly counts
    anomalies_low: int = 0
    anomalies_medium: int = 0
    anomalies_high: int = 0
    anomalies_critical: int = 0

    def overall_score(self) -> float:
        """Compute overall health score."""
        return (self.drift_score + self.volatility_score +
                self.integrity_score + self.performance_score) / 4.0

    def needs_attention(self) -> bool:
        """Check if system needs attention."""
        return (self.anomalies_critical > 0 or
                self.anomalies_high > 3 or
                self.overall_score() < 0.7)


class FailureSurveillanceSystem:
    """
    Layer 13: Failure-Mode Surveillance & Kill-Switch
    
    Monitors system for failures and provides emergency shutdown.
    """

    def __init__(self, audit_trail=None):
        """Initialize failure surveillance system."""
        self.audit_trail = audit_trail or get_audit_trail()

        # System state
        self.is_active = True
        self.kill_switch_activated = False

        # Monitoring data
        self.anomalies: list[Anomaly] = []
        self.health_history: list[SystemHealth] = []

        # Thresholds
        self.drift_threshold = 0.1
        self.volatility_threshold = 0.3
        self.posterior_explosion_threshold = 0.99
        self.edge_inflation_threshold = 10.0  # 10x baseline

        # Abort conditions
        self.max_critical_anomalies = 1
        self.max_high_anomalies = 5
        self.min_health_score = 0.5

        self.audit_trail.log(
            category="SAFETY",
            operation="failure_surveillance_initialized",
            details={"timestamp": datetime.now().isoformat()},
            level="INFORMATIONAL",
            priority="HIGH_PRIORITY"
        )

        logger.info("Failure surveillance system initialized")

    def detect_drift(self, current_value: float, baseline_value: float,
                    metric_name: str) -> Anomaly | None:
        """
        Detect drift from baseline.
        
        Args:
            current_value: Current metric value
            baseline_value: Baseline value
            metric_name: Metric name
        
        Returns:
            Anomaly if drift detected, None otherwise
        """
        drift = abs(current_value - baseline_value) / (abs(baseline_value) + 1e-10)

        if drift > self.drift_threshold:
            severity = SeverityLevel.HIGH if drift > 0.5 else SeverityLevel.MEDIUM

            anomaly = Anomaly(
                anomaly_id=f"drift_{len(self.anomalies)}",
                anomaly_type=AnomalyType.DRIFT_DETECTION,
                severity=severity,
                timestamp=datetime.now(),
                description=f"Drift detected in {metric_name}: {drift:.2%}",
                metric_name=metric_name,
                value=current_value,
                threshold=baseline_value
            )

            self._record_anomaly(anomaly)
            return anomaly

        return None

    def detect_driver_volatility(self, driver_values: list[float],
                                metric_name: str) -> Anomaly | None:
        """
        Detect excessive driver volatility.
        
        Args:
            driver_values: Recent driver values
            metric_name: Driver name
        
        Returns:
            Anomaly if volatility exceeds threshold
        """
        if len(driver_values) < 2:
            return None

        volatility = float(np.std(driver_values))

        if volatility > self.volatility_threshold:
            severity = SeverityLevel.HIGH if volatility > 0.5 else SeverityLevel.MEDIUM

            anomaly = Anomaly(
                anomaly_id=f"volatility_{len(self.anomalies)}",
                anomaly_type=AnomalyType.DRIVER_VOLATILITY,
                severity=severity,
                timestamp=datetime.now(),
                description=f"High volatility in {metric_name}: σ={volatility:.3f}",
                metric_name=metric_name,
                value=volatility,
                threshold=self.volatility_threshold
            )

            self._record_anomaly(anomaly)
            return anomaly

        return None

    def detect_edge_inflation(self, current_edge_count: int,
                             baseline_edge_count: int) -> Anomaly | None:
        """
        Detect graph edge inflation.
        
        Args:
            current_edge_count: Current edge count
            baseline_edge_count: Baseline edge count
        
        Returns:
            Anomaly if inflation detected
        """
        if baseline_edge_count == 0:
            return None

        inflation_factor = current_edge_count / baseline_edge_count

        if inflation_factor > self.edge_inflation_threshold:
            anomaly = Anomaly(
                anomaly_id=f"edge_inflation_{len(self.anomalies)}",
                anomaly_type=AnomalyType.EDGE_INFLATION,
                severity=SeverityLevel.CRITICAL,
                timestamp=datetime.now(),
                description=f"Edge inflation: {inflation_factor:.1f}x baseline",
                value=float(current_edge_count),
                threshold=float(baseline_edge_count)
            )

            self._record_anomaly(anomaly)
            return anomaly

        return None

    def detect_claim_posterior_explosion(self, posteriors: list[float]) -> Anomaly | None:
        """
        Detect claim posterior explosion (too many high posteriors).
        
        Args:
            posteriors: List of claim posterior values
        
        Returns:
            Anomaly if explosion detected
        """
        if not posteriors:
            return None

        high_posteriors = sum(1 for p in posteriors if p > self.posterior_explosion_threshold)
        explosion_rate = high_posteriors / len(posteriors)

        if explosion_rate > 0.5:  # More than 50% near 1.0
            anomaly = Anomaly(
                anomaly_id=f"posterior_explosion_{len(self.anomalies)}",
                anomaly_type=AnomalyType.CLAIM_POSTERIOR_EXPLOSION,
                severity=SeverityLevel.HIGH,
                timestamp=datetime.now(),
                description=f"Claim posterior explosion: {explosion_rate:.1%} near 1.0",
                value=explosion_rate
            )

            self._record_anomaly(anomaly)
            return anomaly

        return None

    def detect_narrative_bleed(self, sludge_elements: list[str],
                              rs_content: str) -> Anomaly | None:
        """
        Detect narrative bleed from Sludge to RS.
        
        Args:
            sludge_elements: Elements that should only appear in sludge
            rs_content: Content from RS stack
        
        Returns:
            Anomaly if bleed detected
        """
        for element in sludge_elements:
            if element.lower() in rs_content.lower():
                anomaly = Anomaly(
                    anomaly_id=f"narrative_bleed_{len(self.anomalies)}",
                    anomaly_type=AnomalyType.NARRATIVE_BLEED,
                    severity=SeverityLevel.CRITICAL,
                    timestamp=datetime.now(),
                    description=f"Narrative bleed detected: '{element}' found in RS",
                    action_taken="ABORT_REQUIRED"
                )

                self._record_anomaly(anomaly)
                return anomaly

        return None

    def detect_sensitivity_blowup(self, elasticity: float,
                                 parameter_name: str) -> Anomaly | None:
        """
        Detect sensitivity blowup (extreme parameter sensitivity).
        
        Args:
            elasticity: Parameter elasticity
            parameter_name: Parameter name
        
        Returns:
            Anomaly if blowup detected
        """
        if abs(elasticity) > 10.0:  # 10x response
            anomaly = Anomaly(
                anomaly_id=f"sensitivity_blowup_{len(self.anomalies)}",
                anomaly_type=AnomalyType.SENSITIVITY_BLOWUP,
                severity=SeverityLevel.HIGH,
                timestamp=datetime.now(),
                description=f"Sensitivity blowup in {parameter_name}: elasticity={elasticity:.1f}",
                metric_name=parameter_name,
                value=elasticity
            )

            self._record_anomaly(anomaly)
            return anomaly

        return None

    def _record_anomaly(self, anomaly: Anomaly) -> None:
        """Record anomaly and log to audit trail."""
        self.anomalies.append(anomaly)

        self.audit_trail.log(
            category="SAFETY",
            operation="anomaly_detected",
            details={
                "anomaly_id": anomaly.anomaly_id,
                "type": anomaly.anomaly_type.value,
                "severity": anomaly.severity.value,
                "description": anomaly.description
            },
            level="CRITICAL" if anomaly.severity == SeverityLevel.CRITICAL else "INFORMATIONAL",
            priority="HIGH_PRIORITY"
        )

        logger.warning(f"Anomaly detected: {anomaly.description} (severity: {anomaly.severity.value})")

    def compute_health(self) -> SystemHealth:
        """
        Compute current system health.
        
        Returns:
            System health status
        """
        # Count anomalies by severity
        anomalies_low = sum(1 for a in self.anomalies if a.severity == SeverityLevel.LOW)
        anomalies_medium = sum(1 for a in self.anomalies if a.severity == SeverityLevel.MEDIUM)
        anomalies_high = sum(1 for a in self.anomalies if a.severity == SeverityLevel.HIGH)
        anomalies_critical = sum(1 for a in self.anomalies if a.severity == SeverityLevel.CRITICAL)

        # Compute health scores
        # Penalize based on anomaly counts
        drift_score = max(0, 1.0 - 0.1 * anomalies_high - 0.3 * anomalies_critical)
        volatility_score = max(0, 1.0 - 0.05 * anomalies_medium - 0.2 * anomalies_high)
        integrity_score = 1.0 if anomalies_critical == 0 else 0.0
        performance_score = max(0, 1.0 - 0.02 * len(self.anomalies))

        health = SystemHealth(
            timestamp=datetime.now(),
            is_healthy=anomalies_critical == 0 and anomalies_high < 5,
            drift_score=drift_score,
            volatility_score=volatility_score,
            integrity_score=integrity_score,
            performance_score=performance_score,
            anomalies_low=anomalies_low,
            anomalies_medium=anomalies_medium,
            anomalies_high=anomalies_high,
            anomalies_critical=anomalies_critical
        )

        self.health_history.append(health)

        return health

    def check_abort_conditions(self) -> tuple[bool, list[str]]:
        """
        Check if abort conditions are met.
        
        Returns:
            (should_abort, reasons)
        """
        health = self.compute_health()
        reasons = []

        # Critical anomalies
        if health.anomalies_critical >= self.max_critical_anomalies:
            reasons.append(f"Critical anomalies: {health.anomalies_critical} >= {self.max_critical_anomalies}")

        # High anomalies
        if health.anomalies_high >= self.max_high_anomalies:
            reasons.append(f"High anomalies: {health.anomalies_high} >= {self.max_high_anomalies}")

        # Health score
        if health.overall_score() < self.min_health_score:
            reasons.append(f"Health score: {health.overall_score():.2f} < {self.min_health_score}")

        should_abort = len(reasons) > 0

        if should_abort:
            self.audit_trail.log(
                category="SAFETY",
                operation="abort_conditions_met",
                details={
                    "reasons": reasons,
                    "health_score": health.overall_score()
                },
                level="CRITICAL",
                priority="HIGH_PRIORITY"
            )

        return should_abort, reasons

    def activate_kill_switch(self, reason: str) -> None:
        """
        Activate emergency kill switch.
        
        Args:
            reason: Reason for activation
        """
        if self.kill_switch_activated:
            logger.warning("Kill switch already activated")
            return

        self.kill_switch_activated = True
        self.is_active = False

        self.audit_trail.log(
            category="SAFETY",
            operation="kill_switch_activated",
            details={
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            },
            level="CRITICAL",
            priority="HIGH_PRIORITY"
        )

        logger.critical(f"🛑 KILL SWITCH ACTIVATED: {reason}")

    def reset(self) -> None:
        """Reset surveillance system (clears history, reactivates)."""
        if self.kill_switch_activated:
            logger.warning("Cannot reset - kill switch is activated")
            return

        self.anomalies.clear()
        self.health_history.clear()
        self.is_active = True

        self.audit_trail.log(
            category="SAFETY",
            operation="surveillance_reset",
            details={"timestamp": datetime.now().isoformat()},
            level="INFORMATIONAL"
        )

        logger.info("Surveillance system reset")

    def get_statistics(self) -> dict[str, Any]:
        """Get surveillance statistics."""
        health = self.compute_health()

        return {
            "is_active": self.is_active,
            "kill_switch_activated": self.kill_switch_activated,
            "total_anomalies": len(self.anomalies),
            "by_severity": {
                "low": health.anomalies_low,
                "medium": health.anomalies_medium,
                "high": health.anomalies_high,
                "critical": health.anomalies_critical
            },
            "health": {
                "overall_score": health.overall_score(),
                "is_healthy": health.is_healthy,
                "needs_attention": health.needs_attention()
            }
        }


# Singleton instance
_surveillance = None


def get_failure_surveillance() -> FailureSurveillanceSystem:
    """Get singleton failure surveillance system instance."""
    global _surveillance
    if _surveillance is None:
        _surveillance = FailureSurveillanceSystem()
    return _surveillance
