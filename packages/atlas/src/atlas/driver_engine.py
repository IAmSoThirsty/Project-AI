"""
atlas.driver_engine — deterministic 10D driver normalization and analysis.

Canonical port of legacy `atlas/core/drivers/driver_engine_10d.py` without
legacy config-file side effects. This module produces subordinate analytical
evidence only; it cannot decide, grant authority, or actuate.
"""

from __future__ import annotations

import hashlib
import json
import math
import threading
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

import numpy as np
import numpy.typing as npt

from atlas.analysis import SUBORDINATION_NOTICE
from atlas.audit import AuditCategory, AuditLevel, AuditTrail

DRIVER_ALGORITHM: Final[str] = "canonical-driver-engine-10d-v1"


class DriverEngineError(ValueError):
    """Raised when driver normalization or analysis fails."""


class DriverType(StrEnum):
    """The canonical 10-dimensional Atlas driver set."""

    CAPITAL_CONCENTRATION = "capital_concentration"
    MARKET_VOLATILITY = "market_volatility"
    RESOURCE_SCARCITY = "resource_scarcity"
    MEDIA_GATEKEEPING = "media_gatekeeping"
    INSTITUTIONAL_CAPTURE_RISK = "institutional_capture_risk"
    GOVERNANCE_FRAGILITY = "governance_fragility"
    INEQUALITY_INDEX = "inequality_index"
    SOCIAL_COHESION = "social_cohesion"
    INFORMATION_ASYMMETRY = "information_asymmetry"
    TECHNOLOGICAL_DISRUPTION = "technological_disruption"

    @property
    def historical_range(self) -> tuple[float, float]:
        return _HISTORICAL_RANGES[self]

    @property
    def description(self) -> str:
        return _DESCRIPTIONS[self]


_HISTORICAL_RANGES: Final[dict[DriverType, tuple[float, float]]] = {
    DriverType.CAPITAL_CONCENTRATION: (0.45, 0.92),
    DriverType.MARKET_VOLATILITY: (0.05, 0.85),
    DriverType.RESOURCE_SCARCITY: (0.10, 0.75),
    DriverType.MEDIA_GATEKEEPING: (0.20, 0.88),
    DriverType.INSTITUTIONAL_CAPTURE_RISK: (0.15, 0.80),
    DriverType.GOVERNANCE_FRAGILITY: (0.10, 0.90),
    DriverType.INEQUALITY_INDEX: (0.25, 0.70),
    DriverType.SOCIAL_COHESION: (0.15, 0.85),
    DriverType.INFORMATION_ASYMMETRY: (0.20, 0.82),
    DriverType.TECHNOLOGICAL_DISRUPTION: (0.05, 0.95),
}

_DESCRIPTIONS: Final[dict[DriverType, str]] = {
    DriverType.CAPITAL_CONCENTRATION: "Concentration of wealth and capital ownership",
    DriverType.MARKET_VOLATILITY: "Financial market instability and volatility",
    DriverType.RESOURCE_SCARCITY: "Scarcity of critical resources",
    DriverType.MEDIA_GATEKEEPING: "Media consolidation and information gatekeeping",
    DriverType.INSTITUTIONAL_CAPTURE_RISK: "Risk of regulatory or institutional capture",
    DriverType.GOVERNANCE_FRAGILITY: "Fragility of governance structures and state capacity",
    DriverType.INEQUALITY_INDEX: "Economic inequality across income and wealth distribution",
    DriverType.SOCIAL_COHESION: "Social cohesion and community trust levels",
    DriverType.INFORMATION_ASYMMETRY: "Asymmetry in access to accurate information",
    DriverType.TECHNOLOGICAL_DISRUPTION: "Rate of technological change and disruption",
}


@dataclass(frozen=True)
class DriverDimension:
    """A weighted driver dimension."""

    driver: DriverType
    weight: float = 1.0
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not isinstance(self.driver, DriverType):
            raise DriverEngineError(f"driver must be DriverType, got {type(self.driver).__name__}")
        if not isinstance(self.weight, (int, float)) or not math.isfinite(float(self.weight)):
            raise DriverEngineError(f"weight must be finite number, got {self.weight!r}")
        if float(self.weight) <= 0.0:
            raise DriverEngineError(f"weight must be > 0, got {self.weight!r}")

    def to_canonical_dict(self) -> dict[str, object]:
        return {
            "description": self.driver.description,
            "driver": self.driver.value,
            "historical_range": list(self.driver.historical_range),
            "subordination_notice": self.subordination_notice,
            "weight": float(self.weight),
        }


@dataclass(frozen=True)
class DriverState:
    """A normalized 10D driver state."""

    values: Mapping[str, float]
    timestamp: str = "unspecified"
    source: str = "computed"
    confidence: float = 1.0
    state_sha256: str = ""
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not isinstance(self.timestamp, str) or not self.timestamp.strip():
            raise DriverEngineError(f"timestamp must be non-empty string, got {self.timestamp!r}")
        if not isinstance(self.source, str) or not self.source.strip():
            raise DriverEngineError(f"source must be non-empty string, got {self.source!r}")
        _validate_unit_interval("confidence", self.confidence)
        normalized_values = _normalize_state_values(self.values)
        object.__setattr__(self, "values", normalized_values)
        if not self.state_sha256:
            object.__setattr__(self, "state_sha256", compute_state_hash(self))
        _validate_hash("state_sha256", self.state_sha256)

    def as_array(self) -> npt.NDArray[np.float64]:
        return np.array([self.values[driver.value] for driver in DriverType], dtype=np.float64)

    def to_canonical_dict(self) -> dict[str, object]:
        return {
            "confidence": float(self.confidence),
            "source": self.source,
            "state_sha256": self.state_sha256,
            "subordination_notice": self.subordination_notice,
            "timestamp": self.timestamp,
            "values": dict(sorted(self.values.items())),
        }


@dataclass(frozen=True)
class PCAResult:
    """Principal component result for driver states."""

    components: tuple[tuple[float, ...], ...]
    explained_variance: tuple[float, ...]
    mean_vector: tuple[float, ...]
    analysis_sha256: str
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not self.components:
            raise DriverEngineError("components must not be empty")
        for component in self.components:
            if len(component) != len(DriverType):
                raise DriverEngineError("each PCA component must contain 10 values")
            for value in component:
                _validate_finite("component", value)
        if not self.explained_variance:
            raise DriverEngineError("explained_variance must not be empty")
        for value in self.explained_variance:
            _validate_finite("explained_variance", value)
        if len(self.mean_vector) != len(DriverType):
            raise DriverEngineError("mean_vector must contain 10 values")
        _validate_hash("analysis_sha256", self.analysis_sha256)

    def to_canonical_dict(self) -> dict[str, object]:
        return {
            "analysis_sha256": self.analysis_sha256,
            "components": [list(component) for component in self.components],
            "explained_variance": list(self.explained_variance),
            "mean_vector": list(self.mean_vector),
            "subordination_notice": self.subordination_notice,
        }


@dataclass(frozen=True)
class DriverAnalysis:
    """Driver analysis aggregate."""

    pca: PCAResult
    correlations: dict[str, dict[str, float]]
    sensitivities: dict[str, float]
    derived_metrics: dict[str, float]
    analysis_sha256: str
    target_metric: str = "systemic_risk_index"
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not isinstance(self.pca, PCAResult):
            raise DriverEngineError(f"pca must be PCAResult, got {type(self.pca).__name__}")
        if not isinstance(self.correlations, dict):
            raise DriverEngineError("correlations must be dict")
        if not isinstance(self.sensitivities, dict):
            raise DriverEngineError("sensitivities must be dict")
        if not isinstance(self.derived_metrics, dict):
            raise DriverEngineError("derived_metrics must be dict")
        if not isinstance(self.target_metric, str) or not self.target_metric.strip():
            raise DriverEngineError("target_metric must be non-empty string")
        _validate_hash("analysis_sha256", self.analysis_sha256)

    def to_canonical_dict(self) -> dict[str, object]:
        return {
            "analysis_sha256": self.analysis_sha256,
            "correlations": _sort_nested_float_dict(self.correlations),
            "derived_metrics": dict(sorted(self.derived_metrics.items())),
            "pca": self.pca.to_canonical_dict(),
            "sensitivities": dict(sorted(self.sensitivities.items())),
            "subordination_notice": self.subordination_notice,
            "target_metric": self.target_metric,
        }


class DriverEngine:
    """Normalize and analyze 10-dimensional Atlas driver states."""

    def __init__(self, audit_trail: AuditTrail | None = None) -> None:
        if audit_trail is not None and not isinstance(audit_trail, AuditTrail):
            raise DriverEngineError(
                f"audit_trail must be AuditTrail, got {type(audit_trail).__name__}"
            )
        self._audit_trail = audit_trail
        self._lock = threading.Lock()
        self._stats = {"states_created": 0, "analyses_completed": 0}
        if self._audit_trail is not None:
            self._audit_trail.append(
                level=AuditLevel.INFORMATIONAL,
                category=AuditCategory.SYSTEM,
                actor="DRIVER_ENGINE",
                action="driver_engine_initialized",
                resource="atlas.driver_engine",
                outcome="ALLOW",
                rationale="DriverEngine initialized",
                evidence={
                    "algorithm": DRIVER_ALGORITHM,
                    "driver_count": str(len(DriverType)),
                },
            )

    def normalize_value(self, driver: DriverType, raw_value: float) -> float:
        if not isinstance(driver, DriverType):
            raise DriverEngineError(f"driver must be DriverType, got {type(driver).__name__}")
        _validate_finite("raw_value", raw_value)
        low, high = driver.historical_range
        if high == low:
            return 0.5
        normalized = (float(raw_value) - low) / (high - low)
        return max(0.0, min(1.0, normalized))

    def denormalize_value(self, driver: DriverType, normalized_value: float) -> float:
        if not isinstance(driver, DriverType):
            raise DriverEngineError(f"driver must be DriverType, got {type(driver).__name__}")
        _validate_unit_interval("normalized_value", normalized_value)
        low, high = driver.historical_range
        return low + float(normalized_value) * (high - low)

    def create_state(
        self,
        raw_values: Mapping[str, float],
        *,
        timestamp: str = "unspecified",
        source: str = "computed",
        confidence: float = 1.0,
    ) -> DriverState:
        try:
            normalized: dict[str, float] = {}
            for driver in DriverType:
                if driver.value not in raw_values:
                    raise DriverEngineError(f"missing required driver {driver.value!r}")
                normalized[driver.value] = self.normalize_value(driver, raw_values[driver.value])
            state = DriverState(
                values=normalized,
                timestamp=timestamp,
                source=source,
                confidence=confidence,
            )
            with self._lock:
                self._stats["states_created"] += 1
            if self._audit_trail is not None:
                self._audit_trail.append(
                    level=AuditLevel.INFORMATIONAL,
                    category=AuditCategory.DATA,
                    actor="DRIVER_ENGINE",
                    action="driver_state_created",
                    resource=f"atlas:driver-state:{state.state_sha256}",
                    outcome="ALLOW",
                    rationale="10D driver state normalized",
                    evidence={
                        "confidence": str(state.confidence),
                        "source": state.source,
                        "state_sha256": state.state_sha256,
                        "timestamp": state.timestamp,
                    },
                )
            return state
        except DriverEngineError as exc:
            if self._audit_trail is not None:
                self._audit_trail.append(
                    level=AuditLevel.HIGH_PRIORITY,
                    category=AuditCategory.DATA,
                    actor="DRIVER_ENGINE",
                    action="driver_state_create_failed",
                    resource="atlas:driver-state",
                    outcome="DENY",
                    rationale="Driver state creation failed closed",
                    evidence={"error": str(exc)},
                )
            raise

    def compute_derived_metrics(
        self,
        state: DriverState,
        graph_metrics: Mapping[str, float] | None = None,
    ) -> dict[str, float]:
        return compute_derived_metrics(state, graph_metrics=graph_metrics)

    def analyze(
        self,
        states: Iterable[DriverState],
        *,
        target_metric: str = "systemic_risk_index",
        components: int = 3,
    ) -> DriverAnalysis:
        state_tuple = _canonical_states(states)
        pca = compute_pca(state_tuple, components=components)
        correlations = compute_correlation_matrix(state_tuple)
        latest = max(state_tuple, key=lambda state: state.timestamp)
        derived = compute_derived_metrics(latest)
        sensitivities = compute_driver_sensitivities(latest, target_metric=target_metric)
        body = {
            "correlations": _sort_nested_float_dict(correlations),
            "derived_metrics": dict(sorted(derived.items())),
            "pca": pca.to_canonical_dict(),
            "sensitivities": dict(sorted(sensitivities.items())),
            "subordination_notice": SUBORDINATION_NOTICE,
            "target_metric": target_metric,
        }
        analysis_hash = _sha256(body)
        analysis = DriverAnalysis(
            pca=pca,
            correlations=correlations,
            sensitivities=sensitivities,
            derived_metrics=derived,
            target_metric=target_metric,
            analysis_sha256=analysis_hash,
        )
        with self._lock:
            self._stats["analyses_completed"] += 1
        if self._audit_trail is not None:
            self._audit_trail.append(
                level=AuditLevel.STANDARD,
                category=AuditCategory.OPERATION,
                actor="DRIVER_ENGINE",
                action="driver_analysis_completed",
                resource=f"atlas:driver-analysis:{analysis.analysis_sha256}",
                outcome="ALLOW",
                rationale="10D driver analysis completed",
                evidence={
                    "analysis_sha256": analysis.analysis_sha256,
                    "states": str(len(state_tuple)),
                    "target_metric": target_metric,
                },
            )
        return analysis

    def get_statistics(self) -> dict[str, int]:
        with self._lock:
            return dict(self._stats)


def compute_pca(
    states: Iterable[DriverState],
    *,
    components: int = 3,
) -> PCAResult:
    state_tuple = _canonical_states(states)
    if len(state_tuple) < 2:
        raise DriverEngineError("PCA requires at least two driver states")
    if not isinstance(components, int) or components < 1:
        raise DriverEngineError(f"components must be positive int, got {components!r}")
    components = min(components, len(DriverType), len(state_tuple))
    matrix = _state_matrix(state_tuple)
    mean_vector = np.mean(matrix, axis=0)
    centered = matrix - mean_vector
    covariance = np.cov(centered, rowvar=False)
    covariance_matrix = np.asarray(covariance, dtype=np.float64)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
    order = np.argsort(eigenvalues)[::-1]
    ordered_values = eigenvalues[order]
    ordered_vectors = eigenvectors[:, order]
    selected_vectors = ordered_vectors[:, :components].T
    selected_values = ordered_values[:components]
    total_variance = float(np.sum(np.maximum(ordered_values, 0.0)))
    explained = (
        tuple(float(max(value, 0.0) / total_variance) for value in selected_values)
        if total_variance > 0.0
        else tuple(0.0 for _ in selected_values)
    )
    component_tuple = tuple(
        tuple(float(value) for value in component) for component in selected_vectors
    )
    mean_tuple = tuple(float(value) for value in mean_vector)
    body = {
        "components": [list(component) for component in component_tuple],
        "explained_variance": list(explained),
        "mean_vector": list(mean_tuple),
        "subordination_notice": SUBORDINATION_NOTICE,
    }
    return PCAResult(
        components=component_tuple,
        explained_variance=explained,
        mean_vector=mean_tuple,
        analysis_sha256=_sha256(body),
    )


def compute_correlation_matrix(states: Iterable[DriverState]) -> dict[str, dict[str, float]]:
    state_tuple = _canonical_states(states)
    if len(state_tuple) < 2:
        raise DriverEngineError("correlation matrix requires at least two driver states")
    matrix = _state_matrix(state_tuple)
    raw_corr = np.corrcoef(matrix, rowvar=False)
    corr = np.nan_to_num(raw_corr, nan=0.0, posinf=0.0, neginf=0.0)
    result: dict[str, dict[str, float]] = {}
    for row_index, row_driver in enumerate(DriverType):
        result[row_driver.value] = {}
        for col_index, col_driver in enumerate(DriverType):
            value = 1.0 if row_index == col_index else float(corr[row_index, col_index])
            result[row_driver.value][col_driver.value] = max(-1.0, min(1.0, value))
    return result


def compute_driver_sensitivities(
    state: DriverState,
    *,
    target_metric: str = "systemic_risk_index",
    perturbation: float = 0.01,
) -> dict[str, float]:
    if not isinstance(state, DriverState):
        raise DriverEngineError(f"state must be DriverState, got {type(state).__name__}")
    if not isinstance(target_metric, str) or not target_metric.strip():
        raise DriverEngineError("target_metric must be non-empty string")
    _validate_finite("perturbation", perturbation)
    if not 0.0 < float(perturbation) <= 1.0:
        raise DriverEngineError(f"perturbation must be in (0, 1], got {perturbation!r}")
    baseline_metrics = compute_derived_metrics(state)
    if target_metric not in baseline_metrics:
        raise DriverEngineError(f"target_metric {target_metric!r} is not a derived metric")
    baseline = baseline_metrics[target_metric]
    sensitivities: dict[str, float] = {}
    for driver in DriverType:
        bumped_values = dict(state.values)
        bumped_values[driver.value] = max(
            0.0, min(1.0, bumped_values[driver.value] + float(perturbation))
        )
        bumped_state = DriverState(
            values=bumped_values,
            timestamp=state.timestamp,
            source=state.source,
            confidence=state.confidence,
        )
        bumped = compute_derived_metrics(bumped_state)[target_metric]
        sensitivities[driver.value] = abs(bumped - baseline) / float(perturbation)
    return dict(sorted(sensitivities.items()))


def compute_derived_metrics(
    state: DriverState,
    *,
    graph_metrics: Mapping[str, float] | None = None,
) -> dict[str, float]:
    if not isinstance(state, DriverState):
        raise DriverEngineError(f"state must be DriverState, got {type(state).__name__}")
    values = state.values
    derived = {
        "disruption_vulnerability": values[DriverType.TECHNOLOGICAL_DISRUPTION.value]
        * values[DriverType.GOVERNANCE_FRAGILITY.value],
        "economic_instability": math.sqrt(
            values[DriverType.MARKET_VOLATILITY.value] * values[DriverType.RESOURCE_SCARCITY.value]
        ),
        "elite_capture_potential": values[DriverType.CAPITAL_CONCENTRATION.value]
        * values[DriverType.INSTITUTIONAL_CAPTURE_RISK.value],
        "information_control_index": (
            values[DriverType.MEDIA_GATEKEEPING.value]
            + values[DriverType.INFORMATION_ASYMMETRY.value]
        )
        / 2.0,
        "institutional_stress": values[DriverType.INSTITUTIONAL_CAPTURE_RISK.value]
        * values[DriverType.GOVERNANCE_FRAGILITY.value],
        "narrative_control_capacity": values[DriverType.MEDIA_GATEKEEPING.value]
        * values[DriverType.INFORMATION_ASYMMETRY.value],
        "social_stability_index": 1.0
        - (
            values[DriverType.INEQUALITY_INDEX.value]
            + (1.0 - values[DriverType.SOCIAL_COHESION.value])
            + values[DriverType.GOVERNANCE_FRAGILITY.value]
        )
        / 3.0,
        "systemic_risk_index": (
            values[DriverType.CAPITAL_CONCENTRATION.value]
            + values[DriverType.INSTITUTIONAL_CAPTURE_RISK.value]
            + values[DriverType.GOVERNANCE_FRAGILITY.value]
        )
        / 3.0,
    }
    if graph_metrics is not None:
        derived["graph_concentration"] = _graph_metric(graph_metrics, "power_concentration")
        derived["influence_centralization"] = _graph_metric(graph_metrics, "centralization")
        derived["network_fragmentation"] = _graph_metric(graph_metrics, "modularity")
    return dict(sorted(derived.items()))


_global_driver_engine: DriverEngine | None = None
_global_driver_engine_lock = threading.Lock()


def get_driver_engine(audit_trail: AuditTrail | None = None) -> DriverEngine:
    global _global_driver_engine
    with _global_driver_engine_lock:
        if _global_driver_engine is None or audit_trail is not None:
            _global_driver_engine = DriverEngine(audit_trail=audit_trail)
        return _global_driver_engine


def reset_driver_engine() -> None:
    global _global_driver_engine
    with _global_driver_engine_lock:
        _global_driver_engine = None


def compute_state_hash(state: DriverState) -> str:
    body = {
        "confidence": float(state.confidence),
        "source": state.source,
        "subordination_notice": state.subordination_notice,
        "timestamp": state.timestamp,
        "values": dict(sorted(state.values.items())),
    }
    return _sha256(body)


def _canonical_states(states: Iterable[DriverState]) -> tuple[DriverState, ...]:
    state_tuple = tuple(states)
    if not state_tuple:
        raise DriverEngineError("at least one driver state is required")
    for state in state_tuple:
        if not isinstance(state, DriverState):
            raise DriverEngineError(f"states must contain DriverState, got {type(state).__name__}")
    return tuple(sorted(state_tuple, key=lambda state: state.state_sha256))


def _state_matrix(states: tuple[DriverState, ...]) -> npt.NDArray[np.float64]:
    return np.vstack([state.as_array() for state in states]).astype(np.float64)


def _normalize_state_values(values: Mapping[str, float]) -> dict[str, float]:
    if not isinstance(values, Mapping):
        raise DriverEngineError(f"values must be mapping, got {type(values).__name__}")
    normalized: dict[str, float] = {}
    expected = {driver.value for driver in DriverType}
    if set(values) != expected:
        missing = sorted(expected - set(values))
        extra = sorted(set(values) - expected)
        detail = []
        if missing:
            detail.append(f"missing={missing}")
        if extra:
            detail.append(f"extra={extra}")
        raise DriverEngineError(
            f"DriverState requires exactly 10 driver values ({', '.join(detail)})"
        )
    for key, value in values.items():
        _validate_unit_interval("driver value", value)
        normalized[key] = float(value)
    return dict(sorted(normalized.items()))


def _validate_unit_interval(name: str, value: float) -> None:
    _validate_finite(name, value)
    if not 0.0 <= float(value) <= 1.0:
        raise DriverEngineError(f"{name} must be in [0, 1], got {value!r}")


def _validate_finite(name: str, value: float) -> None:
    if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise DriverEngineError(f"{name} must be finite number, got {value!r}")


def _validate_hash(name: str, value: str) -> None:
    if not isinstance(value, str) or len(value) != 64:
        raise DriverEngineError(f"{name} must be 64-char hex string, got {value!r}")
    for char in value:
        if char not in "0123456789abcdef":
            raise DriverEngineError(f"{name} must be lowercase hex, got {value!r}")


def _graph_metric(graph_metrics: Mapping[str, float], key: str) -> float:
    value = graph_metrics.get(key, 0.0)
    _validate_finite(key, value)
    return float(value)


def _sha256(body: Mapping[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _sort_nested_float_dict(values: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    return {outer: dict(sorted(inner.items())) for outer, inner in sorted(values.items())}


__all__ = [
    "DRIVER_ALGORITHM",
    "DriverAnalysis",
    "DriverDimension",
    "DriverEngine",
    "DriverEngineError",
    "DriverState",
    "DriverType",
    "PCAResult",
    "compute_correlation_matrix",
    "compute_derived_metrics",
    "compute_driver_sensitivities",
    "compute_pca",
    "compute_state_hash",
    "get_driver_engine",
    "reset_driver_engine",
]
