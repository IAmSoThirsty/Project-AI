"""Atlas failure surveillance with audit-visible anomaly detection.

This module ports the useful legacy surveillance checks into the canonical
Atlas package. It observes analysis artifacts and records anomalies; it does
not actuate external systems or bypass the execution gate.
"""

from __future__ import annotations

import math
import statistics
import threading
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from atlas.analysis import SUBORDINATION_NOTICE
from atlas.audit import AuditCategory, AuditLevel, AuditTrail


class FailureSurveillanceError(Exception):
    """Raised when failure surveillance receives invalid input."""


class AnomalyType(StrEnum):
    """Types of anomalies the surveillance layer can detect."""

    DRIFT_DETECTION = "drift_detection"
    DRIVER_VOLATILITY = "driver_volatility"
    EDGE_INFLATION = "edge_inflation"
    CLAIM_POSTERIOR_EXPLOSION = "claim_posterior_explosion"
    NARRATIVE_BLEED = "narrative_bleed"
    SENSITIVITY_BLOWUP = "sensitivity_blowup"
    PARAMETER_BOUNDS_VIOLATION = "parameter_bounds_violation"
    HASH_INTEGRITY_FAILURE = "hash_integrity_failure"


class SeverityLevel(StrEnum):
    """Failure surveillance severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class SurveillanceThresholds:
    """Configurable thresholds for deterministic anomaly detection."""

    drift_threshold: float = 0.1
    volatility_threshold: float = 0.3
    high_volatility_threshold: float = 0.5
    posterior_explosion_threshold: float = 0.99
    posterior_explosion_rate: float = 0.5
    edge_inflation_factor: float = 10.0
    sensitivity_blowup_threshold: float = 10.0
    max_critical_anomalies: int = 1
    max_high_anomalies: int = 5
    min_health_score: float = 0.5

    def __post_init__(self) -> None:
        _validate_non_negative("drift_threshold", self.drift_threshold)
        _validate_non_negative("volatility_threshold", self.volatility_threshold)
        _validate_non_negative("high_volatility_threshold", self.high_volatility_threshold)
        _validate_unit_interval(
            "posterior_explosion_threshold",
            self.posterior_explosion_threshold,
        )
        _validate_unit_interval("posterior_explosion_rate", self.posterior_explosion_rate)
        _validate_positive("edge_inflation_factor", self.edge_inflation_factor)
        _validate_positive("sensitivity_blowup_threshold", self.sensitivity_blowup_threshold)
        _validate_non_negative_int("max_critical_anomalies", self.max_critical_anomalies)
        _validate_non_negative_int("max_high_anomalies", self.max_high_anomalies)
        _validate_unit_interval("min_health_score", self.min_health_score)
        if self.high_volatility_threshold < self.volatility_threshold:
            raise FailureSurveillanceError(
                "high_volatility_threshold must be >= volatility_threshold"
            )


@dataclass(frozen=True)
class Anomaly:
    """Immutable detected anomaly record."""

    anomaly_id: str
    anomaly_type: AnomalyType
    severity: SeverityLevel
    timestamp: str
    description: str
    metric_name: str | None = None
    value: float | None = None
    threshold: float | None = None
    action_taken: str = "monitored"
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not isinstance(self.anomaly_id, str) or not self.anomaly_id.strip():
            raise FailureSurveillanceError("anomaly_id must be non-empty string")
        if not isinstance(self.anomaly_type, AnomalyType):
            raise FailureSurveillanceError(
                f"anomaly_type must be AnomalyType, got {type(self.anomaly_type).__name__}"
            )
        if not isinstance(self.severity, SeverityLevel):
            raise FailureSurveillanceError(
                f"severity must be SeverityLevel, got {type(self.severity).__name__}"
            )
        _validate_timestamp(self.timestamp)
        if not isinstance(self.description, str) or not self.description.strip():
            raise FailureSurveillanceError("description must be non-empty string")
        if self.metric_name is not None and not self.metric_name.strip():
            raise FailureSurveillanceError("metric_name must be non-empty string or None")
        if self.value is not None:
            _validate_finite("value", self.value)
        if self.threshold is not None:
            _validate_finite("threshold", self.threshold)
        if not isinstance(self.action_taken, str) or not self.action_taken.strip():
            raise FailureSurveillanceError("action_taken must be non-empty string")
        if self.subordination_notice != SUBORDINATION_NOTICE:
            raise FailureSurveillanceError("subordination_notice mismatch")

    def to_canonical_dict(self) -> dict[str, object]:
        """Return a JSON-serializable anomaly representation."""
        return {
            "action_taken": self.action_taken,
            "anomaly_id": self.anomaly_id,
            "anomaly_type": self.anomaly_type.value,
            "description": self.description,
            "metric_name": self.metric_name,
            "severity": self.severity.value,
            "subordination_notice": self.subordination_notice,
            "threshold": self.threshold,
            "timestamp": self.timestamp,
            "value": self.value,
        }


@dataclass(frozen=True)
class SystemHealth:
    """Computed surveillance health summary."""

    timestamp: str
    is_healthy: bool
    drift_score: float = 1.0
    volatility_score: float = 1.0
    integrity_score: float = 1.0
    performance_score: float = 1.0
    anomalies_low: int = 0
    anomalies_medium: int = 0
    anomalies_high: int = 0
    anomalies_critical: int = 0
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        _validate_timestamp(self.timestamp)
        if not isinstance(self.is_healthy, bool):
            raise FailureSurveillanceError("is_healthy must be bool")
        for field_name in (
            "drift_score",
            "volatility_score",
            "integrity_score",
            "performance_score",
        ):
            _validate_unit_interval(field_name, getattr(self, field_name))
        for field_name in (
            "anomalies_low",
            "anomalies_medium",
            "anomalies_high",
            "anomalies_critical",
        ):
            _validate_non_negative_int(field_name, getattr(self, field_name))
        if self.subordination_notice != SUBORDINATION_NOTICE:
            raise FailureSurveillanceError("subordination_notice mismatch")

    def overall_score(self) -> float:
        """Compute the aggregate health score."""
        return (
            self.drift_score + self.volatility_score + self.integrity_score + self.performance_score
        ) / 4.0

    def needs_attention(self) -> bool:
        """Return whether current health requires operator attention."""
        return self.anomalies_critical > 0 or self.anomalies_high > 3 or self.overall_score() < 0.7


class FailureSurveillanceSystem:
    """Audit-visible failure surveillance for Atlas analysis artifacts."""

    def __init__(
        self,
        *,
        audit_trail: AuditTrail | None = None,
        thresholds: SurveillanceThresholds | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if audit_trail is not None and not isinstance(audit_trail, AuditTrail):
            raise FailureSurveillanceError(
                f"audit_trail must be AuditTrail, got {type(audit_trail).__name__}"
            )
        if thresholds is not None and not isinstance(thresholds, SurveillanceThresholds):
            raise FailureSurveillanceError(
                f"thresholds must be SurveillanceThresholds, got {type(thresholds).__name__}"
            )
        if clock is not None and not callable(clock):
            raise FailureSurveillanceError(f"clock must be callable, got {type(clock).__name__}")
        self._audit_trail = audit_trail
        self._thresholds = thresholds or SurveillanceThresholds()
        self._clock = clock or (lambda: datetime.now(UTC))
        self._lock = threading.Lock()
        self._anomalies: list[Anomaly] = []
        self._health_history: list[SystemHealth] = []
        self.is_active = True
        self.kill_switch_activated = False
        self._audit(
            level=AuditLevel.INFORMATIONAL,
            action="failure_surveillance_initialized",
            resource="atlas.failure_surveillance",
            outcome="ALLOW",
            rationale="Failure surveillance initialized",
            evidence={
                "drift_threshold": str(self._thresholds.drift_threshold),
                "edge_inflation_factor": str(self._thresholds.edge_inflation_factor),
                "posterior_explosion_threshold": str(
                    self._thresholds.posterior_explosion_threshold
                ),
            },
        )

    @property
    def anomalies(self) -> tuple[Anomaly, ...]:
        """Return recorded anomalies as an immutable tuple."""
        with self._lock:
            return tuple(self._anomalies)

    @property
    def health_history(self) -> tuple[SystemHealth, ...]:
        """Return computed health snapshots as an immutable tuple."""
        with self._lock:
            return tuple(self._health_history)

    def detect_drift(
        self,
        current_value: float,
        baseline_value: float,
        metric_name: str,
    ) -> Anomaly | None:
        """Detect relative drift from a baseline value."""
        _validate_finite("current_value", current_value)
        _validate_finite("baseline_value", baseline_value)
        _validate_name("metric_name", metric_name)
        drift = abs(float(current_value) - float(baseline_value)) / (
            abs(float(baseline_value)) + 1e-10
        )
        if drift <= self._thresholds.drift_threshold:
            return None
        severity = SeverityLevel.HIGH if drift > 0.5 else SeverityLevel.MEDIUM
        return self._record_anomaly(
            anomaly_type=AnomalyType.DRIFT_DETECTION,
            severity=severity,
            description=f"Drift detected in {metric_name}: {drift:.2%}",
            metric_name=metric_name,
            value=drift,
            threshold=self._thresholds.drift_threshold,
        )

    def detect_driver_volatility(
        self,
        driver_values: Iterable[float],
        metric_name: str,
    ) -> Anomaly | None:
        """Detect excessive population-standard-deviation volatility."""
        _validate_name("metric_name", metric_name)
        values = tuple(float(value) for value in driver_values)
        for index, value in enumerate(values):
            _validate_finite(f"driver_values[{index}]", value)
        if len(values) < 2:
            return None
        volatility = statistics.pstdev(values)
        if volatility <= self._thresholds.volatility_threshold:
            return None
        severity = (
            SeverityLevel.HIGH
            if volatility >= self._thresholds.high_volatility_threshold
            else SeverityLevel.MEDIUM
        )
        return self._record_anomaly(
            anomaly_type=AnomalyType.DRIVER_VOLATILITY,
            severity=severity,
            description=f"High volatility in {metric_name}: sigma={volatility:.3f}",
            metric_name=metric_name,
            value=volatility,
            threshold=self._thresholds.volatility_threshold,
        )

    def detect_edge_inflation(
        self,
        current_edge_count: int,
        baseline_edge_count: int,
    ) -> Anomaly | None:
        """Detect influence-graph edge inflation against a known baseline."""
        _validate_non_negative_int("current_edge_count", current_edge_count)
        _validate_positive_int("baseline_edge_count", baseline_edge_count)
        inflation_factor = current_edge_count / baseline_edge_count
        if inflation_factor <= self._thresholds.edge_inflation_factor:
            return None
        return self._record_anomaly(
            anomaly_type=AnomalyType.EDGE_INFLATION,
            severity=SeverityLevel.CRITICAL,
            description=f"Edge inflation: {inflation_factor:.1f}x baseline",
            value=float(inflation_factor),
            threshold=self._thresholds.edge_inflation_factor,
            action_taken="ABORT_REQUIRED",
        )

    def detect_claim_posterior_explosion(
        self,
        posteriors: Iterable[float],
    ) -> Anomaly | None:
        """Detect too many near-certain claim posteriors."""
        values = tuple(float(value) for value in posteriors)
        if not values:
            return None
        for index, value in enumerate(values):
            _validate_unit_interval(f"posterior[{index}]", value)
        high_posteriors = sum(
            1 for value in values if value > self._thresholds.posterior_explosion_threshold
        )
        explosion_rate = high_posteriors / len(values)
        if explosion_rate <= self._thresholds.posterior_explosion_rate:
            return None
        return self._record_anomaly(
            anomaly_type=AnomalyType.CLAIM_POSTERIOR_EXPLOSION,
            severity=SeverityLevel.HIGH,
            description=f"Claim posterior explosion: {explosion_rate:.1%} near 1.0",
            value=explosion_rate,
            threshold=self._thresholds.posterior_explosion_rate,
        )

    def detect_narrative_bleed(
        self,
        sludge_elements: Iterable[str],
        rs_content: str,
    ) -> Anomaly | None:
        """Detect Sludge-only narrative content crossing into Reality Stack content."""
        if not isinstance(rs_content, str):
            raise FailureSurveillanceError(
                f"rs_content must be string, got {type(rs_content).__name__}"
            )
        content = rs_content.lower()
        for index, element in enumerate(sludge_elements):
            if not isinstance(element, str) or not element.strip():
                raise FailureSurveillanceError(f"sludge_elements[{index}] must be non-empty string")
            if element.lower() in content:
                return self._record_anomaly(
                    anomaly_type=AnomalyType.NARRATIVE_BLEED,
                    severity=SeverityLevel.CRITICAL,
                    description=f"Narrative bleed detected: {element!r} found in RS",
                    metric_name="reality_stack_content",
                    action_taken="ABORT_REQUIRED",
                )
        return None

    def detect_sensitivity_blowup(
        self,
        elasticity: float,
        parameter_name: str,
    ) -> Anomaly | None:
        """Detect excessive sensitivity elasticity."""
        _validate_finite("elasticity", elasticity)
        _validate_name("parameter_name", parameter_name)
        if abs(float(elasticity)) <= self._thresholds.sensitivity_blowup_threshold:
            return None
        return self._record_anomaly(
            anomaly_type=AnomalyType.SENSITIVITY_BLOWUP,
            severity=SeverityLevel.HIGH,
            description=f"Sensitivity blowup in {parameter_name}: elasticity={elasticity:.1f}",
            metric_name=parameter_name,
            value=float(elasticity),
            threshold=self._thresholds.sensitivity_blowup_threshold,
        )

    def detect_parameter_bounds_violation(
        self,
        parameter_name: str,
        value: float,
        lower_bound: float,
        upper_bound: float,
    ) -> Anomaly | None:
        """Detect parameter values outside declared bounds."""
        _validate_name("parameter_name", parameter_name)
        _validate_finite("value", value)
        _validate_finite("lower_bound", lower_bound)
        _validate_finite("upper_bound", upper_bound)
        if lower_bound > upper_bound:
            raise FailureSurveillanceError("lower_bound must be <= upper_bound")
        if lower_bound <= value <= upper_bound:
            return None
        return self._record_anomaly(
            anomaly_type=AnomalyType.PARAMETER_BOUNDS_VIOLATION,
            severity=SeverityLevel.CRITICAL,
            description=f"Parameter {parameter_name!r} outside bounds",
            metric_name=parameter_name,
            value=float(value),
            threshold=float(upper_bound if value > upper_bound else lower_bound),
            action_taken="ABORT_REQUIRED",
        )

    def detect_hash_integrity_failure(
        self,
        expected_hash: str,
        actual_hash: str,
        resource: str,
    ) -> Anomaly | None:
        """Detect mismatch between expected and observed SHA-256 values."""
        _validate_hash("expected_hash", expected_hash)
        _validate_hash("actual_hash", actual_hash)
        _validate_name("resource", resource)
        if expected_hash == actual_hash:
            return None
        return self._record_anomaly(
            anomaly_type=AnomalyType.HASH_INTEGRITY_FAILURE,
            severity=SeverityLevel.CRITICAL,
            description=f"Hash integrity failure for {resource}",
            metric_name=resource,
            action_taken="ABORT_REQUIRED",
        )

    def compute_health(self) -> SystemHealth:
        """Compute and store current health from recorded anomalies."""
        with self._lock:
            anomalies = tuple(self._anomalies)
        low = sum(1 for anomaly in anomalies if anomaly.severity is SeverityLevel.LOW)
        medium = sum(1 for anomaly in anomalies if anomaly.severity is SeverityLevel.MEDIUM)
        high = sum(1 for anomaly in anomalies if anomaly.severity is SeverityLevel.HIGH)
        critical = sum(1 for anomaly in anomalies if anomaly.severity is SeverityLevel.CRITICAL)
        drift_score = max(0.0, 1.0 - 0.1 * high - 0.3 * critical)
        volatility_score = max(0.0, 1.0 - 0.05 * medium - 0.2 * high)
        integrity_score = 1.0 if critical == 0 else 0.0
        performance_score = max(0.0, 1.0 - 0.02 * len(anomalies))
        health = SystemHealth(
            timestamp=self._timestamp(),
            is_healthy=critical == 0 and high < self._thresholds.max_high_anomalies,
            drift_score=drift_score,
            volatility_score=volatility_score,
            integrity_score=integrity_score,
            performance_score=performance_score,
            anomalies_low=low,
            anomalies_medium=medium,
            anomalies_high=high,
            anomalies_critical=critical,
        )
        with self._lock:
            self._health_history.append(health)
        return health

    def check_abort_conditions(self) -> tuple[bool, tuple[str, ...]]:
        """Return whether surveillance health meets local abort conditions."""
        health = self.compute_health()
        reasons: list[str] = []
        if health.anomalies_critical >= self._thresholds.max_critical_anomalies:
            reasons.append(
                "Critical anomalies: "
                f"{health.anomalies_critical} >= {self._thresholds.max_critical_anomalies}"
            )
        if health.anomalies_high >= self._thresholds.max_high_anomalies:
            reasons.append(
                f"High anomalies: {health.anomalies_high} >= {self._thresholds.max_high_anomalies}"
            )
        if health.overall_score() < self._thresholds.min_health_score:
            reasons.append(
                f"Health score: {health.overall_score():.2f} < {self._thresholds.min_health_score}"
            )
        should_abort = bool(reasons)
        if should_abort:
            self._audit(
                level=AuditLevel.CRITICAL,
                action="failure_abort_conditions_met",
                resource="atlas.failure_surveillance",
                outcome="DENY",
                rationale="Failure surveillance abort conditions were met",
                evidence={
                    "health_score": f"{health.overall_score():.6f}",
                    "reasons": " | ".join(reasons),
                },
            )
        return should_abort, tuple(reasons)

    def activate_kill_switch(self, reason: str) -> None:
        """Activate local surveillance halt state and append an audit event."""
        _validate_name("reason", reason)
        if self.kill_switch_activated:
            return
        self.kill_switch_activated = True
        self.is_active = False
        self._audit(
            level=AuditLevel.EMERGENCY,
            action="failure_kill_switch_activated",
            resource="atlas.failure_surveillance",
            outcome="DENY",
            rationale="Local failure-surveillance kill switch activated",
            evidence={"reason": reason, "timestamp": self._timestamp()},
        )

    def reset(self) -> None:
        """Clear anomaly and health history unless the kill switch has fired."""
        if self.kill_switch_activated:
            raise FailureSurveillanceError("cannot reset after kill switch activation")
        with self._lock:
            self._anomalies.clear()
            self._health_history.clear()
        self.is_active = True
        self._audit(
            level=AuditLevel.INFORMATIONAL,
            action="failure_surveillance_reset",
            resource="atlas.failure_surveillance",
            outcome="ALLOW",
            rationale="Failure surveillance history reset",
            evidence={"timestamp": self._timestamp()},
        )

    def get_statistics(self) -> dict[str, object]:
        """Return a JSON-serializable surveillance summary."""
        health = self.compute_health()
        return {
            "is_active": self.is_active,
            "kill_switch_activated": self.kill_switch_activated,
            "total_anomalies": len(self.anomalies),
            "by_severity": {
                "low": health.anomalies_low,
                "medium": health.anomalies_medium,
                "high": health.anomalies_high,
                "critical": health.anomalies_critical,
            },
            "health": {
                "overall_score": health.overall_score(),
                "is_healthy": health.is_healthy,
                "needs_attention": health.needs_attention(),
            },
            "subordination_notice": SUBORDINATION_NOTICE,
        }

    def _record_anomaly(
        self,
        *,
        anomaly_type: AnomalyType,
        severity: SeverityLevel,
        description: str,
        metric_name: str | None = None,
        value: float | None = None,
        threshold: float | None = None,
        action_taken: str = "monitored",
    ) -> Anomaly:
        with self._lock:
            anomaly_id = f"{anomaly_type.value}_{len(self._anomalies)}"
        anomaly = Anomaly(
            anomaly_id=anomaly_id,
            anomaly_type=anomaly_type,
            severity=severity,
            timestamp=self._timestamp(),
            description=description,
            metric_name=metric_name,
            value=value,
            threshold=threshold,
            action_taken=action_taken,
        )
        with self._lock:
            self._anomalies.append(anomaly)
        self._audit_anomaly(anomaly)
        return anomaly

    def _audit_anomaly(self, anomaly: Anomaly) -> None:
        outcome = "DENY" if anomaly.severity is SeverityLevel.CRITICAL else "ESCALATE"
        level = (
            AuditLevel.CRITICAL
            if anomaly.severity is SeverityLevel.CRITICAL
            else AuditLevel.HIGH_PRIORITY
        )
        evidence = {
            "action_taken": anomaly.action_taken,
            "anomaly_id": anomaly.anomaly_id,
            "anomaly_type": anomaly.anomaly_type.value,
            "severity": anomaly.severity.value,
        }
        if anomaly.metric_name is not None:
            evidence["metric_name"] = anomaly.metric_name
        if anomaly.value is not None:
            evidence["value"] = f"{anomaly.value:.12g}"
        if anomaly.threshold is not None:
            evidence["threshold"] = f"{anomaly.threshold:.12g}"
        self._audit(
            level=level,
            action="failure_anomaly_detected",
            resource=f"atlas:failure-anomaly:{anomaly.anomaly_id}",
            outcome=outcome,
            rationale=anomaly.description,
            evidence=evidence,
        )

    def _audit(
        self,
        *,
        level: AuditLevel,
        action: str,
        resource: str,
        outcome: str,
        rationale: str,
        evidence: dict[str, str],
    ) -> None:
        if self._audit_trail is None:
            return
        self._audit_trail.append(
            level=level,
            category=AuditCategory.SECURITY,
            actor="FAILURE_SURVEILLANCE",
            action=action,
            resource=resource,
            outcome=outcome,
            rationale=rationale,
            evidence=evidence,
        )

    def _timestamp(self) -> str:
        return self._clock().isoformat()


_surveillance: FailureSurveillanceSystem | None = None
_surveillance_lock = threading.Lock()


def get_failure_surveillance(
    *,
    audit_trail: AuditTrail | None = None,
    thresholds: SurveillanceThresholds | None = None,
    clock: Callable[[], datetime] | None = None,
) -> FailureSurveillanceSystem:
    """Return the process-local failure surveillance singleton."""
    global _surveillance
    with _surveillance_lock:
        if _surveillance is None:
            _surveillance = FailureSurveillanceSystem(
                audit_trail=audit_trail,
                thresholds=thresholds,
                clock=clock,
            )
        return _surveillance


def reset_failure_surveillance() -> None:
    """Clear the process-local failure surveillance singleton."""
    global _surveillance
    with _surveillance_lock:
        _surveillance = None


def _validate_name(field_name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise FailureSurveillanceError(f"{field_name} must be non-empty string")


def _validate_timestamp(value: str) -> None:
    _validate_name("timestamp", value)
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise FailureSurveillanceError(f"timestamp must be ISO 8601: {exc}") from exc


def _validate_finite(field_name: str, value: float) -> None:
    if not isinstance(value, (int, float)) or math.isnan(value) or math.isinf(value):
        raise FailureSurveillanceError(f"{field_name} must be finite number")


def _validate_unit_interval(field_name: str, value: float) -> None:
    _validate_finite(field_name, value)
    if not 0.0 <= float(value) <= 1.0:
        raise FailureSurveillanceError(f"{field_name} must be between 0 and 1")


def _validate_non_negative(field_name: str, value: float) -> None:
    _validate_finite(field_name, value)
    if float(value) < 0.0:
        raise FailureSurveillanceError(f"{field_name} must be non-negative")


def _validate_positive(field_name: str, value: float) -> None:
    _validate_finite(field_name, value)
    if float(value) <= 0.0:
        raise FailureSurveillanceError(f"{field_name} must be positive")


def _validate_non_negative_int(field_name: str, value: int) -> None:
    if not isinstance(value, int) or value < 0:
        raise FailureSurveillanceError(f"{field_name} must be non-negative int")


def _validate_positive_int(field_name: str, value: int) -> None:
    if not isinstance(value, int) or value <= 0:
        raise FailureSurveillanceError(f"{field_name} must be positive int")


def _validate_hash(field_name: str, value: str) -> None:
    if not isinstance(value, str) or len(value) != 64:
        raise FailureSurveillanceError(f"{field_name} must be 64-char hex string")
    for char in value:
        if char not in "0123456789abcdef":
            raise FailureSurveillanceError(f"{field_name} must be 64-char hex string")


__all__ = [
    "Anomaly",
    "AnomalyType",
    "FailureSurveillanceError",
    "FailureSurveillanceSystem",
    "SeverityLevel",
    "SurveillanceThresholds",
    "SystemHealth",
    "get_failure_surveillance",
    "reset_failure_surveillance",
]
