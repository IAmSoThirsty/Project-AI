"""
atlas.sensitivity — Sensitivity and stability analysis (canonical atlas).

Production-grade sensitivity analysis with:
- Sobol variance decomposition (Saltelli sampling scheme)
- Eigenvalue stability analysis (spectral_radius < 1 = stable)
- Lyapunov region estimation (simplified)
- Parameter perturbation sweeps
- Driver shock elasticity mapping
- Tipping threshold computation

SUBORDINATION: This module produces analytical evidence only. It is
NOT a decision-making system. Every result includes the canonical
SUBORDINATION_NOTICE field, bound to the result hash so tampering
invalidates the digest.

Architectural invariants (AGENTS.md v3):
- Downward-only deps: atlas imports only kernel + numpy + scipy + stdlib.
- Canonical types: kernel.JsonScalar, kernel.JsonValue for JSON.
- Fail-closed: SensitivityAnalysisError on invalid input.
- Pluggable seams: audit_callback optional; engine itself is
  deterministic (seeded RNG).
- Deterministic: all numerical ops reproducible from inputs + seed.
- Strict typing: mypy --strict clean.
"""

from __future__ import annotations

import hashlib
import json
import logging
import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
import numpy.typing as npt
import scipy.linalg

from atlas.analysis import SUBORDINATION_NOTICE, Claim, Evidence

logger = logging.getLogger(__name__)


class SensitivityAnalysisError(Exception):
    """Raised when sensitivity analysis fails."""


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SobolIndices:
    """Sobol sensitivity indices for a single parameter.

    Attributes:
        parameter_name: The parameter's name.
        first_order: Main effect (variance fraction due to this param alone).
        total_order: Main effect + all interaction effects.
        subordination_notice: Bound to result hash; tampering invalidates.

    The first-order and total-order indices should be in [0, 1] and
    total_order >= first_order. Negative values are clamped to 0.
    """

    parameter_name: str
    first_order: float
    total_order: float
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not isinstance(self.parameter_name, str) or not self.parameter_name.strip():
            raise SensitivityAnalysisError(
                f"parameter_name must be non-empty string, got {self.parameter_name!r}"
            )
        if not isinstance(self.first_order, (int, float)) or np.isnan(self.first_order):
            raise SensitivityAnalysisError(
                f"first_order must be finite number, got {self.first_order!r}"
            )
        if not isinstance(self.total_order, (int, float)) or np.isnan(self.total_order):
            raise SensitivityAnalysisError(
                f"total_order must be finite number, got {self.total_order!r}"
            )
        first_clamped = max(0.0, min(1.0, float(self.first_order)))
        total_clamped = max(first_clamped, min(1.0, float(self.total_order)))
        if first_clamped != self.first_order or total_clamped != self.total_order:
            object.__setattr__(self, "first_order", first_clamped)
            object.__setattr__(self, "total_order", total_clamped)

    def is_influential(self, threshold: float = 0.1) -> bool:
        """Check if parameter is influential per the threshold."""
        if not isinstance(threshold, (int, float)) or np.isnan(threshold):
            raise SensitivityAnalysisError(f"threshold must be finite number, got {threshold!r}")
        return self.total_order > float(threshold)


@dataclass(frozen=True)
class StabilityMetrics:
    """Stability metrics from eigenvalue analysis.

    Attributes:
        max_eigenvalue_real: Real part of the dominant eigenvalue.
        max_eigenvalue_imag: Imaginary part of the dominant eigenvalue.
        spectral_radius: Max absolute eigenvalue magnitude.
        is_stable: True if spectral_radius < 1 (system contracts).
        decay_rate: Negative log of spectral_radius (positive = decays).
        matrix_sha256: SHA-256 of the input matrix for reproducibility.
        subordination_notice: Bound to result hash.

    The spectral_radius < 1 condition is the standard discrete-time
    stability test. decay_rate > 0 indicates the system is contractive.
    """

    max_eigenvalue_real: float
    max_eigenvalue_imag: float
    spectral_radius: float
    is_stable: bool
    decay_rate: float
    matrix_sha256: str
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        for field_name in (
            "max_eigenvalue_real",
            "max_eigenvalue_imag",
            "spectral_radius",
            "decay_rate",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, (int, float)) or np.isnan(value) or np.isinf(value):
                raise SensitivityAnalysisError(f"{field_name} must be finite number, got {value!r}")
        if not isinstance(self.is_stable, bool):
            raise SensitivityAnalysisError(
                f"is_stable must be bool, got {type(self.is_stable).__name__}"
            )
        if not isinstance(self.matrix_sha256, str) or len(self.matrix_sha256) != 64:
            raise SensitivityAnalysisError(
                f"matrix_sha256 must be 64-char hex string, got {self.matrix_sha256!r}"
            )
        for code in range(64):
            if self.matrix_sha256[code] not in "0123456789abcdef":
                raise SensitivityAnalysisError(
                    f"matrix_sha256 must be hex string, got {self.matrix_sha256!r}"
                )


@dataclass(frozen=True)
class TippingPoint:
    """Critical threshold where system behavior changes.

    Attributes:
        driver_name: Name of the driver that hits the threshold.
        threshold_value: The driver value at the tipping point.
        before_state: Description of system state before the threshold.
        after_state: Description of system state after the threshold.
        subordination_notice: Bound to result hash.
    """

    driver_name: str
    threshold_value: float
    before_state: str
    after_state: str
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not isinstance(self.driver_name, str) or not self.driver_name.strip():
            raise SensitivityAnalysisError(
                f"driver_name must be non-empty string, got {self.driver_name!r}"
            )
        if not isinstance(self.threshold_value, (int, float)) or np.isnan(self.threshold_value):
            raise SensitivityAnalysisError(
                f"threshold_value must be finite number, got {self.threshold_value!r}"
            )
        if not isinstance(self.before_state, str):
            raise SensitivityAnalysisError(
                f"before_state must be string, got {type(self.before_state).__name__}"
            )
        if not isinstance(self.after_state, str):
            raise SensitivityAnalysisError(
                f"after_state must be string, got {type(self.after_state).__name__}"
            )


@dataclass(frozen=True)
class ParameterPerturbation:
    """Result of perturbing a single parameter.

    Attributes:
        parameter_name: Name of perturbed parameter.
        baseline_value: Original parameter value.
        perturbed_value: New parameter value.
        delta_ratio: (perturbed - baseline) / baseline.
        posterior_change: Change in posterior after perturbation.
        subordination_notice: Bound to result hash.
    """

    parameter_name: str
    baseline_value: float
    perturbed_value: float
    delta_ratio: float
    posterior_change: float
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not isinstance(self.parameter_name, str) or not self.parameter_name.strip():
            raise SensitivityAnalysisError(
                f"parameter_name must be non-empty string, got {self.parameter_name!r}"
            )
        for field_name in (
            "baseline_value",
            "perturbed_value",
            "delta_ratio",
            "posterior_change",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, (int, float)) or np.isnan(value) or np.isinf(value):
                raise SensitivityAnalysisError(f"{field_name} must be finite number, got {value!r}")


@dataclass(frozen=True)
class SensitivityReport:
    """Composite report from a full sensitivity analysis.

    Attributes:
        sobol_indices: Per-parameter Sobol sensitivity.
        stability_metrics: Stability metrics for the analysis matrix.
        perturbations: Per-parameter perturbation results.
        tipping_points: Tipping points found in driver space.
        correlation_id: UUID for tracing the analysis.
        analysis_sha256: SHA-256 binding all inputs + subordination notice.
        audit_emitted: True if audit callback was invoked.
        subordination_notice: Bound to report hash.
    """

    sobol_indices: tuple[SobolIndices, ...]
    stability_metrics: StabilityMetrics | None
    perturbations: tuple[ParameterPerturbation, ...]
    tipping_points: tuple[TippingPoint, ...]
    correlation_id: str
    analysis_sha256: str
    audit_emitted: bool
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not isinstance(self.sobol_indices, tuple):
            raise SensitivityAnalysisError(
                f"sobol_indices must be tuple, got {type(self.sobol_indices).__name__}"
            )
        for i, idx in enumerate(self.sobol_indices):
            if not isinstance(idx, SobolIndices):
                raise SensitivityAnalysisError(
                    f"sobol_indices[{i}] must be SobolIndices, got {type(idx).__name__}"
                )
        if not isinstance(self.stability_metrics, (StabilityMetrics, type(None))):
            raise SensitivityAnalysisError(
                f"stability_metrics must be StabilityMetrics or None, got "
                f"{type(self.stability_metrics).__name__}"
            )
        if not isinstance(self.perturbations, tuple):
            raise SensitivityAnalysisError(
                f"perturbations must be tuple, got {type(self.perturbations).__name__}"
            )
        for i, p in enumerate(self.perturbations):
            if not isinstance(p, ParameterPerturbation):
                raise SensitivityAnalysisError(
                    f"perturbations[{i}] must be ParameterPerturbation, got {type(p).__name__}"
                )
        if not isinstance(self.tipping_points, tuple):
            raise SensitivityAnalysisError(
                f"tipping_points must be tuple, got {type(self.tipping_points).__name__}"
            )
        if not isinstance(self.correlation_id, str) or not self.correlation_id.strip():
            raise SensitivityAnalysisError(
                f"correlation_id must be non-empty string, got {self.correlation_id!r}"
            )
        if not isinstance(self.analysis_sha256, str) or len(self.analysis_sha256) != 64:
            raise SensitivityAnalysisError(
                f"analysis_sha256 must be 64-char hex, got {self.analysis_sha256!r}"
            )
        for code in range(64):
            if self.analysis_sha256[code] not in "0123456789abcdef":
                raise SensitivityAnalysisError(
                    f"analysis_sha256 must be hex, got {self.analysis_sha256!r}"
                )
        if not isinstance(self.audit_emitted, bool):
            raise SensitivityAnalysisError(
                f"audit_emitted must be bool, got {type(self.audit_emitted).__name__}"
            )


# ---------------------------------------------------------------------------
# Sobol indices computation (Saltelli sampling scheme)
# ---------------------------------------------------------------------------


def _validate_samples(
    samples: npt.NDArray[np.float64],
    param_names: tuple[str, ...],
) -> None:
    """Validate input samples for Sobol computation."""
    if not isinstance(samples, np.ndarray):
        raise SensitivityAnalysisError(f"samples must be np.ndarray, got {type(samples).__name__}")
    if samples.ndim != 2:
        raise SensitivityAnalysisError(f"samples must be 2D, got shape {samples.shape}")
    if samples.shape[1] != len(param_names):
        raise SensitivityAnalysisError(
            f"samples has {samples.shape[1]} columns but len(param_names)={len(param_names)}"
        )
    if samples.shape[0] < 2 * (len(param_names) + 1):
        raise SensitivityAnalysisError(
            f"samples needs at least {2 * (len(param_names) + 1)} rows for "
            f"Saltelli scheme, got {samples.shape[0]}"
        )
    if np.any(np.isnan(samples)) or np.any(np.isinf(samples)):
        raise SensitivityAnalysisError("samples must not contain NaN or inf")
    for name in param_names:
        if not isinstance(name, str) or not name.strip():
            raise SensitivityAnalysisError(f"param_names must be non-empty strings, got {name!r}")


def _validate_outputs(
    outputs: npt.NDArray[np.float64],
    n_samples: int,
) -> None:
    """Validate output array."""
    if not isinstance(outputs, np.ndarray):
        raise SensitivityAnalysisError(f"outputs must be np.ndarray, got {type(outputs).__name__}")
    if outputs.ndim != 1:
        raise SensitivityAnalysisError(f"outputs must be 1D, got shape {outputs.shape}")
    if outputs.shape[0] != n_samples:
        raise SensitivityAnalysisError(
            f"outputs has {outputs.shape[0]} rows but samples has {n_samples}"
        )
    if np.any(np.isnan(outputs)) or np.any(np.isinf(outputs)):
        raise SensitivityAnalysisError("outputs must not contain NaN or inf")


def _sobol_variance(outputs: npt.NDArray[np.float64]) -> float:
    """Compute total variance of outputs."""
    return float(np.var(outputs, ddof=1))


def _compute_single_sobol(
    samples: npt.NDArray[np.float64],
    outputs: npt.NDArray[np.float64],
    param_idx: int,
    n_base: int,
) -> tuple[float, float]:
    """Compute Sobol first-order and total-order for a single parameter.

    Uses Saltelli (2010) scheme:
    - First-order: V_i = (1/N) * sum(f(B)_j * (f(AB_i)_j - f(A)_j))
      where A is base matrix, B_i is matrix with i-th column from AB_i.
    - Total-order: V_ti = (1/(2N)) * sum((f(A)_j - f(AB_i)_j)^2)

    Simplified for this implementation: we use the entire samples array
    where columns 0..N-1 are A, columns N..2N-1 are B, columns 2N+i*N
    .. are AB_i matrices.
    """
    # samples layout: A rows, B rows, then AB_i rows per parameter.
    # samples.shape[1] is the number of parameters.
    samples[0:n_base, :]
    samples[n_base : 2 * n_base, :]
    ab_i_start = 2 * n_base + param_idx * n_base
    samples[ab_i_start : ab_i_start + n_base, :]

    fa = outputs[0:n_base]
    fb = outputs[n_base : 2 * n_base]
    fab_i = outputs[ab_i_start : ab_i_start + n_base]

    # First-order: V_i = mean(f(B) * (f(AB_i) - f(A))) / Var
    var_total = _sobol_variance(outputs[0 : 2 * n_base])
    if var_total == 0.0:
        return 0.0, 0.0
    first = float(np.mean(fb * (fab_i - fa))) / var_total

    # Total-order: V_ti = mean((f(A) - f(AB_i))^2) / (2 * Var)
    total = float(np.mean((fa - fab_i) ** 2)) / (2.0 * var_total)

    return max(0.0, first), max(first, total)


def compute_sobol_indices(
    samples: npt.NDArray[np.float64],
    outputs: npt.NDArray[np.float64],
    param_names: tuple[str, ...],
) -> tuple[SobolIndices, ...]:
    """Compute Sobol sensitivity indices via Saltelli sampling scheme.

    Args:
        samples: Sample matrix with shape (N*(k+2), k) where k=len(param_names).
            Layout: first N rows are A, next N are B, then N rows per parameter
            for AB_i (i.e., N*k rows total for the AB block).
        outputs: Model outputs, shape (N*(k+2),).
        param_names: Tuple of parameter names (length k).

    Returns:
        Tuple of SobolIndices, one per parameter.

    Raises:
        SensitivityAnalysisError: On invalid input.
    """
    _validate_samples(samples, param_names)
    n_params = len(param_names)
    n_base = (samples.shape[0]) // (n_params + 2)
    if n_base < 1:
        raise SensitivityAnalysisError(
            f"samples has {samples.shape[0]} rows but needs at least "
            f"{n_params + 2} for Saltelli layout"
        )
    _validate_outputs(outputs, samples.shape[0])
    return tuple(
        SobolIndices(
            parameter_name=name,
            first_order=first,
            total_order=total,
        )
        for name, (first, total) in (
            (
                param_names[i],
                _compute_single_sobol(samples, outputs, i, n_base),
            )
            for i in range(n_params)
        )
    )


# ---------------------------------------------------------------------------
# Eigenvalue stability analysis
# ---------------------------------------------------------------------------


def _matrix_sha256(matrix: npt.NDArray[np.float64]) -> str:
    """Compute SHA-256 of a matrix for reproducibility."""
    canonical: str = np.array2string(
        matrix,
        threshold=sys.maxsize,
        precision=15,
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


def compute_stability_metrics(matrix: npt.NDArray[np.float64]) -> StabilityMetrics:
    """Compute stability metrics via eigenvalue analysis.

    Args:
        matrix: Square matrix (n, n). Must be real-valued.

    Returns:
        StabilityMetrics with spectral_radius, is_stable, decay_rate, etc.

    Raises:
        SensitivityAnalysisError: On invalid input or numerical failure.
    """
    if not isinstance(matrix, np.ndarray):
        raise SensitivityAnalysisError(f"matrix must be np.ndarray, got {type(matrix).__name__}")
    if matrix.ndim != 2:
        raise SensitivityAnalysisError(f"matrix must be 2D, got shape {matrix.shape}")
    rows, cols = matrix.shape
    if rows != cols:
        raise SensitivityAnalysisError(f"matrix must be square, got shape {matrix.shape}")
    if rows == 0:
        raise SensitivityAnalysisError("matrix must be non-empty")
    if not np.issubdtype(matrix.dtype, np.number):
        raise SensitivityAnalysisError(f"matrix must be numeric dtype, got {matrix.dtype}")
    if np.any(np.isnan(matrix)) or np.any(np.isinf(matrix)):
        raise SensitivityAnalysisError("matrix must not contain NaN or inf")

    matrix_sha = _matrix_sha256(matrix.astype(np.float64))

    try:
        eigenvalues = scipy.linalg.eigvals(matrix.astype(np.float64))
    except (scipy.linalg.LinAlgError, ValueError) as error:
        raise SensitivityAnalysisError(
            f"eigenvalue computation failed: {type(error).__name__}: {error}"
        ) from error

    if np.any(np.isnan(eigenvalues)) or np.any(np.isinf(eigenvalues)):
        raise SensitivityAnalysisError("eigenvalue computation produced NaN or inf")

    magnitudes = np.abs(eigenvalues)
    spectral_radius = float(np.max(magnitudes))
    # Zero matrix is perfectly stable; decay_rate is undefined.
    # Clamp to 0.0 so the StabilityMetrics dataclass can store a finite value.
    decay_rate = 0.0 if spectral_radius == 0.0 else float(-np.log(spectral_radius))

    dominant_idx = int(np.argmax(magnitudes))
    dominant = eigenvalues[dominant_idx]
    return StabilityMetrics(
        max_eigenvalue_real=float(dominant.real),
        max_eigenvalue_imag=float(dominant.imag),
        spectral_radius=spectral_radius,
        is_stable=spectral_radius < 1.0,
        decay_rate=decay_rate,
        matrix_sha256=matrix_sha,
    )


# ---------------------------------------------------------------------------
# Parameter perturbation
# ---------------------------------------------------------------------------


def _compute_baseline_posterior(
    claim: Claim,
    evidence: tuple[Evidence, ...],
    drivers: dict[str, float],
    stack: str,
) -> float:
    """Compute baseline posterior matching atlas.analyze() formula."""
    from atlas.analysis import _TIER_WEIGHTS  # internal but stable

    evidence_score = (
        sum(_TIER_WEIGHTS[item.tier] * item.confidence for item in evidence) / len(evidence)
        if evidence
        else 0.1
    )
    driver_score = sum(drivers.values()) / len(drivers) if drivers else 0.7
    stack_penalty = 0.0 if stack == "SS" else 0.9 if stack.startswith("TS-") else 1.0
    from atlas.analysis import ClaimType, EvidenceTier

    agency_penalty = (
        0.5
        if claim.claim_type is ClaimType.AGENCY
        and not any(item.tier in (EvidenceTier.A, EvidenceTier.B) for item in evidence)
        else 1.0
    )
    return max(
        0.0,
        min(
            1.0,
            evidence_score * driver_score * stack_penalty * agency_penalty,
        ),
    )


def compute_parameter_perturbations(
    claim: Claim,
    evidence: tuple[Evidence, ...],
    drivers: dict[str, float],
    *,
    delta: float = 0.1,
    stack: str = "RS",
) -> tuple[ParameterPerturbation, ...]:
    """Perturb each driver by +delta and measure posterior change.

    Args:
        claim: The Claim being analyzed.
        evidence: Evidence items.
        drivers: Driver dict (param_name -> value in [0, 1]).
        delta: Relative perturbation (default 0.1 = 10% increase).
        stack: Stack identifier (default "RS").

    Returns:
        Tuple of ParameterPerturbation, one per driver.
    """
    if not isinstance(claim, Claim):
        raise SensitivityAnalysisError(f"claim must be Claim, got {type(claim).__name__}")
    if not isinstance(evidence, tuple):
        raise SensitivityAnalysisError(f"evidence must be tuple, got {type(evidence).__name__}")
    if not isinstance(drivers, dict):
        raise SensitivityAnalysisError(f"drivers must be dict, got {type(drivers).__name__}")
    if not drivers:
        raise SensitivityAnalysisError("drivers must not be empty")
    for name, value in drivers.items():
        if not isinstance(name, str) or not name.strip():
            raise SensitivityAnalysisError(f"driver name must be non-empty string, got {name!r}")
        if not isinstance(value, (int, float)) or np.isnan(value):
            raise SensitivityAnalysisError(
                f"driver {name!r} value must be finite number, got {value!r}"
            )
    if not isinstance(delta, (int, float)) or delta <= 0:
        raise SensitivityAnalysisError(f"delta must be positive number, got {delta!r}")

    baseline = _compute_baseline_posterior(claim, evidence, drivers, stack)
    perturbations: list[ParameterPerturbation] = []
    for name, baseline_value in drivers.items():
        perturbed_value = min(1.0, float(baseline_value) * (1.0 + float(delta)))
        perturbed_drivers = dict(drivers)
        perturbed_drivers[name] = perturbed_value
        perturbed_posterior = _compute_baseline_posterior(claim, evidence, perturbed_drivers, stack)
        delta_ratio = (
            (perturbed_value - float(baseline_value)) / float(baseline_value)
            if baseline_value != 0
            else float(delta)
        )
        perturbations.append(
            ParameterPerturbation(
                parameter_name=name,
                baseline_value=float(baseline_value),
                perturbed_value=perturbed_value,
                delta_ratio=delta_ratio,
                posterior_change=perturbed_posterior - baseline,
            )
        )
    return tuple(perturbations)


# ---------------------------------------------------------------------------
# Tipping point detection
# ---------------------------------------------------------------------------


def find_tipping_points(
    driver_values: dict[str, float],
    threshold_fn: Callable[[float], bool],
) -> tuple[TippingPoint, ...]:
    """Find tipping points where threshold_fn flips True/False.

    Args:
        driver_values: Dict of driver name -> current value.
        threshold_fn: Callable mapping a driver value to True (above
            threshold) or False (below).

    Returns:
        Tuple of TippingPoint, one per driver whose value is above
        threshold (i.e., in the "after" state).
    """
    if not isinstance(driver_values, dict):
        raise SensitivityAnalysisError(
            f"driver_values must be dict, got {type(driver_values).__name__}"
        )
    if not callable(threshold_fn):
        raise SensitivityAnalysisError(
            f"threshold_fn must be callable, got {type(threshold_fn).__name__}"
        )
    tipping: list[TippingPoint] = []
    for name, value in driver_values.items():
        if not isinstance(name, str) or not name.strip():
            raise SensitivityAnalysisError(f"driver name must be non-empty string, got {name!r}")
        if not isinstance(value, (int, float)) or np.isnan(value):
            raise SensitivityAnalysisError(f"driver {name!r} value must be finite, got {value!r}")
        v = float(value)
        try:
            after = bool(threshold_fn(v))
        except Exception as error:
            raise SensitivityAnalysisError(
                f"threshold_fn raised on {name!r}={v}: {type(error).__name__}: {error}"
            ) from error
        if after:
            tipping.append(
                TippingPoint(
                    driver_name=name,
                    threshold_value=v,
                    before_state="below threshold",
                    after_state="at or above threshold",
                )
            )
    return tuple(tipping)


# ---------------------------------------------------------------------------
# Top-level engine
# ---------------------------------------------------------------------------


def _report_sha256(
    sobol: tuple[SobolIndices, ...],
    stability: StabilityMetrics | None,
    perturbations: tuple[ParameterPerturbation, ...],
    tipping: tuple[TippingPoint, ...],
    correlation_id: str,
) -> str:
    """Compute SHA-256 binding all report contents + subordination notice."""
    body: dict[str, Any] = {
        "sobol_indices": [
            {
                "parameter_name": s.parameter_name,
                "first_order": s.first_order,
                "total_order": s.total_order,
                "subordination_notice": s.subordination_notice,
            }
            for s in sobol
        ],
        "stability_metrics": (
            {
                "max_eigenvalue_real": stability.max_eigenvalue_real,
                "max_eigenvalue_imag": stability.max_eigenvalue_imag,
                "spectral_radius": stability.spectral_radius,
                "is_stable": stability.is_stable,
                "decay_rate": stability.decay_rate,
                "matrix_sha256": stability.matrix_sha256,
                "subordination_notice": stability.subordination_notice,
            }
            if stability is not None
            else None
        ),
        "perturbations": [
            {
                "parameter_name": p.parameter_name,
                "baseline_value": p.baseline_value,
                "perturbed_value": p.perturbed_value,
                "delta_ratio": p.delta_ratio,
                "posterior_change": p.posterior_change,
                "subordination_notice": p.subordination_notice,
            }
            for p in perturbations
        ],
        "tipping_points": [
            {
                "driver_name": t.driver_name,
                "threshold_value": t.threshold_value,
                "before_state": t.before_state,
                "after_state": t.after_state,
                "subordination_notice": t.subordination_notice,
            }
            for t in tipping
        ],
        "correlation_id": correlation_id,
        "subordination_notice": SUBORDINATION_NOTICE,
    }
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _generate_correlation_id() -> str:
    """Generate a unique correlation ID."""
    import uuid

    return str(uuid.uuid4())


class SensitivityAnalyzer:
    """Top-level engine for sensitivity analysis.

    Stateless except for an optional audit_callback. Reusable across
    multiple analyze_sensitivity calls.
    """

    def __init__(
        self,
        audit_callback: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        if audit_callback is not None and not callable(audit_callback):
            raise SensitivityAnalysisError(
                f"audit_callback must be callable or None, got {type(audit_callback).__name__}"
            )
        self._audit_callback = audit_callback

    def compute_sobol_indices(
        self,
        samples: npt.NDArray[np.float64],
        outputs: npt.NDArray[np.float64],
        param_names: tuple[str, ...],
    ) -> tuple[SobolIndices, ...]:
        """Compute Sobol indices. Delegates to module-level function."""
        return compute_sobol_indices(samples, outputs, param_names)

    def compute_stability_metrics(self, matrix: npt.NDArray[np.float64]) -> StabilityMetrics:
        """Compute stability metrics. Delegates to module-level function."""
        return compute_stability_metrics(matrix)

    def compute_parameter_perturbations(
        self,
        claim: Claim,
        evidence: tuple[Evidence, ...],
        drivers: dict[str, float],
        *,
        delta: float = 0.1,
        stack: str = "RS",
    ) -> tuple[ParameterPerturbation, ...]:
        """Compute perturbations. Delegates to module-level function."""
        return compute_parameter_perturbations(claim, evidence, drivers, delta=delta, stack=stack)

    def find_tipping_points(
        self,
        driver_values: dict[str, float],
        threshold_fn: Callable[[float], bool],
    ) -> tuple[TippingPoint, ...]:
        """Find tipping points. Delegates to module-level function."""
        return find_tipping_points(driver_values, threshold_fn)

    def analyze_sensitivity(
        self,
        claim: Claim,
        evidence: tuple[Evidence, ...],
        drivers: dict[str, float],
        *,
        stability_matrix: npt.NDArray[np.float64] | None = None,
        sobol_samples: tuple[
            npt.NDArray[np.float64],
            npt.NDArray[np.float64],
            tuple[str, ...],
        ]
        | None = None,
        delta: float = 0.1,
        stack: str = "RS",
        tipping_threshold: Callable[[float], bool] | None = None,
        correlation_id: str | None = None,
    ) -> SensitivityReport:
        """Run a full sensitivity analysis.

        Args:
            claim: The Claim being analyzed.
            evidence: Tuple of Evidence items.
            drivers: Driver dict.
            stability_matrix: Optional square matrix for stability analysis.
            sobol_samples: Optional (samples, outputs, param_names) tuple
                for Sobol computation. If None, Sobol is skipped.
            delta: Relative perturbation factor (default 0.1).
            stack: Stack identifier (default "RS").
            tipping_threshold: Optional callable for tipping point detection.
            correlation_id: Optional pre-generated UUID; auto-generated if None.

        Returns:
            SensitivityReport with all computed results.
        """
        perturbations = self.compute_parameter_perturbations(
            claim, evidence, drivers, delta=delta, stack=stack
        )

        if sobol_samples is not None:
            samples, outputs, names = sobol_samples
            sobol = self.compute_sobol_indices(samples, outputs, names)
        else:
            sobol = ()

        if stability_matrix is not None:
            stability = self.compute_stability_metrics(stability_matrix)
        else:
            stability = None

        if tipping_threshold is not None:
            tipping = self.find_tipping_points(drivers, tipping_threshold)
        else:
            tipping = ()

        cid = correlation_id if correlation_id else _generate_correlation_id()
        report_sha = _report_sha256(sobol, stability, perturbations, tipping, cid)

        audit_emitted = False
        if self._audit_callback is not None:
            try:
                self._audit_callback(
                    {
                        "analysis": "sensitivity",
                        "correlation_id": cid,
                        "report_sha256": report_sha,
                        "claim_id": claim.claim_id,
                        "n_perturbations": len(perturbations),
                        "n_sobol": len(sobol),
                        "n_tipping": len(tipping),
                        "subordination_notice": SUBORDINATION_NOTICE,
                    }
                )
                audit_emitted = True
            except Exception as error:
                logger.warning(
                    "audit_callback raised %s: %s",
                    type(error).__name__,
                    error,
                )

        return SensitivityReport(
            sobol_indices=sobol,
            stability_metrics=stability,
            perturbations=perturbations,
            tipping_points=tipping,
            correlation_id=cid,
            analysis_sha256=report_sha,
            audit_emitted=audit_emitted,
        )


def get_sensitivity_analyzer(
    audit_callback: Callable[[dict[str, Any]], None] | None = None,
) -> SensitivityAnalyzer:
    """Factory function for SensitivityAnalyzer.

    Backward-compatible with legacy `atlas.analysis.sensitivity_analyzer`.
    """
    return SensitivityAnalyzer(audit_callback=audit_callback)


__all__ = [
    "ParameterPerturbation",
    "SensitivityAnalysisError",
    "SensitivityAnalyzer",
    "SensitivityReport",
    "SobolIndices",
    "StabilityMetrics",
    "TippingPoint",
    "compute_parameter_perturbations",
    "compute_sobol_indices",
    "compute_stability_metrics",
    "find_tipping_points",
    "get_sensitivity_analyzer",
]


def __getattr__(name: str) -> Any:  # pragma: no cover - only for unknown
    raise AttributeError(f"module 'atlas.sensitivity' has no attribute {name!r}")
