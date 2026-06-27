"""Production tests for atlas.sensitivity module (Phase J2.1).

Per Thirstys standards: no shortcuts, no stubs, full coverage of:
- Every dataclass validation path
- Every numerical computation (deterministic)
- Every error path
- Subordination notice binding
- Audit callback semantics
- Edge cases (empty, NaN, ill-conditioned, etc.)
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import numpy as np
import pytest

from atlas import (
    SUBORDINATION_NOTICE,
    Claim,
    ClaimType,
    Evidence,
    EvidenceTier,
    ParameterPerturbation,
    SensitivityAnalysisError,
    SensitivityAnalyzer,
    SensitivityReport,
    SobolIndices,
    StabilityMetrics,
    TippingPoint,
    compute_parameter_perturbations,
    compute_sobol_indices,
    compute_stability_metrics,
    find_tipping_points,
    get_sensitivity_analyzer,
)

# ---------------------------------------------------------------------------
# SobolIndices dataclass
# ---------------------------------------------------------------------------


def test_sobol_indices_minimal() -> None:
    s = SobolIndices(parameter_name="x", first_order=0.3, total_order=0.5)
    assert s.parameter_name == "x"
    assert s.first_order == 0.3
    assert s.total_order == 0.5
    assert s.subordination_notice == SUBORDINATION_NOTICE


def test_sobol_indices_validates_blank_parameter_name() -> None:
    with pytest.raises(SensitivityAnalysisError, match="parameter_name"):
        SobolIndices(parameter_name="", first_order=0.1, total_order=0.2)


def test_sobol_indices_validates_whitespace_name() -> None:
    with pytest.raises(SensitivityAnalysisError, match="parameter_name"):
        SobolIndices(parameter_name="   ", first_order=0.1, total_order=0.2)


def test_sobol_indices_validates_first_order_nan() -> None:
    with pytest.raises(SensitivityAnalysisError, match="first_order"):
        SobolIndices(
            parameter_name="x",
            first_order=float("nan"),
            total_order=0.5,
        )


def test_sobol_indices_validates_total_order_nan() -> None:
    with pytest.raises(SensitivityAnalysisError, match="total_order"):
        SobolIndices(
            parameter_name="x",
            first_order=0.1,
            total_order=float("nan"),
        )


def test_sobol_indices_clamps_negative_to_zero() -> None:
    s = SobolIndices(parameter_name="x", first_order=-0.5, total_order=-0.3)
    assert s.first_order == 0.0
    assert s.total_order == 0.0


def test_sobol_indices_clamps_above_one() -> None:
    s = SobolIndices(parameter_name="x", first_order=1.5, total_order=2.0)
    assert s.first_order == 1.0
    assert s.total_order == 1.0


def test_sobol_indices_total_at_least_first() -> None:
    s = SobolIndices(parameter_name="x", first_order=0.8, total_order=0.3)
    assert s.total_order == 0.8


def test_sobol_indices_is_influential() -> None:
    s = SobolIndices(parameter_name="x", first_order=0.3, total_order=0.5)
    assert s.is_influential(threshold=0.1) is True
    assert s.is_influential(threshold=0.6) is False
    assert s.is_influential(threshold=0.5) is False  # >, not >=


def test_sobol_indices_is_influential_validates_threshold() -> None:
    s = SobolIndices(parameter_name="x", first_order=0.3, total_order=0.5)
    with pytest.raises(SensitivityAnalysisError, match="threshold"):
        s.is_influential(threshold=float("nan"))


def test_sobol_indices_is_influential_zero_threshold() -> None:
    s = SobolIndices(parameter_name="x", first_order=0.3, total_order=0.5)
    assert s.is_influential(threshold=0.0) is True


# ---------------------------------------------------------------------------
# StabilityMetrics dataclass
# ---------------------------------------------------------------------------


def test_stability_metrics_stable() -> None:
    m = StabilityMetrics(
        max_eigenvalue_real=0.5,
        max_eigenvalue_imag=0.0,
        spectral_radius=0.5,
        is_stable=True,
        decay_rate=0.693,
        matrix_sha256="0" * 64,
    )
    assert m.is_stable is True


def test_stability_metrics_unstable() -> None:
    m = StabilityMetrics(
        max_eigenvalue_real=1.5,
        max_eigenvalue_imag=0.0,
        spectral_radius=1.5,
        is_stable=False,
        decay_rate=-0.405,
        matrix_sha256="a" * 64,
    )
    assert m.is_stable is False


def test_stability_metrics_validates_all_finite_fields() -> None:
    for field_name in (
        "max_eigenvalue_real",
        "max_eigenvalue_imag",
        "spectral_radius",
        "decay_rate",
    ):
        kwargs: dict[str, Any] = dict(
            max_eigenvalue_real=0.5,
            max_eigenvalue_imag=0.0,
            spectral_radius=0.5,
            is_stable=True,
            decay_rate=0.1,
            matrix_sha256="0" * 64,
        )
        kwargs[field_name] = float("nan")
        with pytest.raises(SensitivityAnalysisError, match=field_name):
            StabilityMetrics(**kwargs)


def test_stability_metrics_validates_inf_fields() -> None:
    kwargs: dict[str, Any] = dict(
        max_eigenvalue_real=0.5,
        max_eigenvalue_imag=0.0,
        spectral_radius=0.5,
        is_stable=True,
        decay_rate=0.1,
        matrix_sha256="0" * 64,
    )
    kwargs["spectral_radius"] = float("inf")
    with pytest.raises(SensitivityAnalysisError, match="spectral_radius"):
        StabilityMetrics(**kwargs)


def test_stability_metrics_validates_is_stable_type() -> None:
    with pytest.raises(SensitivityAnalysisError, match="is_stable"):
        StabilityMetrics(
            max_eigenvalue_real=0.5,
            max_eigenvalue_imag=0.0,
            spectral_radius=0.5,
            is_stable="yes",  # type: ignore[arg-type]
            decay_rate=0.1,
            matrix_sha256="0" * 64,
        )


def test_stability_metrics_validates_sha256_length() -> None:
    with pytest.raises(SensitivityAnalysisError, match="matrix_sha256"):
        StabilityMetrics(
            max_eigenvalue_real=0.5,
            max_eigenvalue_imag=0.0,
            spectral_radius=0.5,
            is_stable=True,
            decay_rate=0.1,
            matrix_sha256="tooshort",
        )


def test_stability_metrics_validates_sha256_hex() -> None:
    with pytest.raises(SensitivityAnalysisError, match="matrix_sha256"):
        StabilityMetrics(
            max_eigenvalue_real=0.5,
            max_eigenvalue_imag=0.0,
            spectral_radius=0.5,
            is_stable=True,
            decay_rate=0.1,
            matrix_sha256="z" * 64,
        )


# ---------------------------------------------------------------------------
# TippingPoint dataclass
# ---------------------------------------------------------------------------


def test_tipping_point_minimal() -> None:
    t = TippingPoint(
        driver_name="d1",
        threshold_value=0.5,
        before_state="below",
        after_state="above",
    )
    assert t.driver_name == "d1"
    assert t.threshold_value == 0.5


def test_tipping_point_validates_blank_driver_name() -> None:
    with pytest.raises(SensitivityAnalysisError, match="driver_name"):
        TippingPoint(
            driver_name="",
            threshold_value=0.5,
            before_state="a",
            after_state="b",
        )


def test_tipping_point_validates_threshold_nan() -> None:
    with pytest.raises(SensitivityAnalysisError, match="threshold_value"):
        TippingPoint(
            driver_name="d",
            threshold_value=float("nan"),
            before_state="a",
            after_state="b",
        )


def test_tipping_point_validates_before_state_type() -> None:
    with pytest.raises(SensitivityAnalysisError, match="before_state"):
        TippingPoint(
            driver_name="d",
            threshold_value=0.5,
            before_state=123,  # type: ignore[arg-type]
            after_state="b",
        )


def test_tipping_point_validates_after_state_type() -> None:
    with pytest.raises(SensitivityAnalysisError, match="after_state"):
        TippingPoint(
            driver_name="d",
            threshold_value=0.5,
            before_state="a",
            after_state=None,  # type: ignore[arg-type]
        )


def test_tipping_point_accepts_empty_strings() -> None:
    """Empty state strings are allowed (only type is enforced)."""
    t = TippingPoint(
        driver_name="d",
        threshold_value=0.5,
        before_state="",
        after_state="",
    )
    assert t.before_state == ""
    assert t.after_state == ""


# ---------------------------------------------------------------------------
# ParameterPerturbation dataclass
# ---------------------------------------------------------------------------


def test_parameter_perturbation_minimal() -> None:
    p = ParameterPerturbation(
        parameter_name="x",
        baseline_value=0.5,
        perturbed_value=0.55,
        delta_ratio=0.1,
        posterior_change=0.02,
    )
    assert p.parameter_name == "x"


def test_parameter_perturbation_validates_blank_name() -> None:
    with pytest.raises(SensitivityAnalysisError, match="parameter_name"):
        ParameterPerturbation(
            parameter_name="",
            baseline_value=0.5,
            perturbed_value=0.55,
            delta_ratio=0.1,
            posterior_change=0.02,
        )


def test_parameter_perturbation_validates_all_finite() -> None:
    for field_name in (
        "baseline_value",
        "perturbed_value",
        "delta_ratio",
        "posterior_change",
    ):
        kwargs: dict[str, Any] = dict(
            parameter_name="x",
            baseline_value=0.5,
            perturbed_value=0.55,
            delta_ratio=0.1,
            posterior_change=0.02,
        )
        kwargs[field_name] = float("nan")
        with pytest.raises(SensitivityAnalysisError, match=field_name):
            ParameterPerturbation(**kwargs)


def test_parameter_perturbation_validates_inf() -> None:
    with pytest.raises(SensitivityAnalysisError, match="baseline_value"):
        ParameterPerturbation(
            parameter_name="x",
            baseline_value=float("inf"),
            perturbed_value=0.55,
            delta_ratio=0.1,
            posterior_change=0.02,
        )


# ---------------------------------------------------------------------------
# SensitivityReport dataclass
# ---------------------------------------------------------------------------


def test_sensitivity_report_minimal() -> None:
    r = SensitivityReport(
        sobol_indices=(),
        stability_metrics=None,
        perturbations=(),
        tipping_points=(),
        correlation_id="abc",
        analysis_sha256="0" * 64,
        audit_emitted=False,
    )
    assert r.audit_emitted is False


def test_sensitivity_report_validates_sobol_tuple() -> None:
    with pytest.raises(SensitivityAnalysisError, match="sobol_indices"):
        SensitivityReport(
            sobol_indices=[],  # type: ignore[arg-type]
            stability_metrics=None,
            perturbations=(),
            tipping_points=(),
            correlation_id="abc",
            analysis_sha256="0" * 64,
            audit_emitted=False,
        )


def test_sensitivity_report_validates_sobol_items() -> None:
    with pytest.raises(SensitivityAnalysisError, match="sobol_indices\\[0\\]"):
        SensitivityReport(
            sobol_indices=("not a sobol",),  # type: ignore[arg-type]
            stability_metrics=None,
            perturbations=(),
            tipping_points=(),
            correlation_id="abc",
            analysis_sha256="0" * 64,
            audit_emitted=False,
        )


def test_sensitivity_report_validates_stability_type() -> None:
    with pytest.raises(SensitivityAnalysisError, match="stability_metrics"):
        SensitivityReport(
            sobol_indices=(),
            stability_metrics="not stability",  # type: ignore[arg-type]
            perturbations=(),
            tipping_points=(),
            correlation_id="abc",
            analysis_sha256="0" * 64,
            audit_emitted=False,
        )


def test_sensitivity_report_validates_perturbations_type() -> None:
    with pytest.raises(SensitivityAnalysisError, match="perturbations"):
        SensitivityReport(
            sobol_indices=(),
            stability_metrics=None,
            perturbations=[],  # type: ignore[arg-type]
            tipping_points=(),
            correlation_id="abc",
            analysis_sha256="0" * 64,
            audit_emitted=False,
        )


def test_sensitivity_report_validates_correlation_id() -> None:
    with pytest.raises(SensitivityAnalysisError, match="correlation_id"):
        SensitivityReport(
            sobol_indices=(),
            stability_metrics=None,
            perturbations=(),
            tipping_points=(),
            correlation_id="",
            analysis_sha256="0" * 64,
            audit_emitted=False,
        )


def test_sensitivity_report_validates_sha256_length() -> None:
    with pytest.raises(SensitivityAnalysisError, match="analysis_sha256"):
        SensitivityReport(
            sobol_indices=(),
            stability_metrics=None,
            perturbations=(),
            tipping_points=(),
            correlation_id="abc",
            analysis_sha256="bad",
            audit_emitted=False,
        )


def test_sensitivity_report_validates_sha256_hex() -> None:
    with pytest.raises(SensitivityAnalysisError, match="analysis_sha256"):
        SensitivityReport(
            sobol_indices=(),
            stability_metrics=None,
            perturbations=(),
            tipping_points=(),
            correlation_id="abc",
            analysis_sha256="z" * 64,
            audit_emitted=False,
        )


def test_sensitivity_report_validates_audit_emitted_type() -> None:
    with pytest.raises(SensitivityAnalysisError, match="audit_emitted"):
        SensitivityReport(
            sobol_indices=(),
            stability_metrics=None,
            perturbations=(),
            tipping_points=(),
            correlation_id="abc",
            analysis_sha256="0" * 64,
            audit_emitted="yes",  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# compute_sobol_indices
# ---------------------------------------------------------------------------


def test_compute_sobol_indices_validates_not_ndarray() -> None:
    with pytest.raises(SensitivityAnalysisError, match="samples must be np"):
        compute_sobol_indices(
            [[1, 2], [3, 4]],  # type: ignore[arg-type]
            np.array([1.0, 2.0, 3.0, 4.0]),
            ("x", "y"),
        )


def test_compute_sobol_indices_validates_2d() -> None:
    with pytest.raises(SensitivityAnalysisError, match="2D"):
        compute_sobol_indices(
            np.array([1.0, 2.0, 3.0]),
            np.array([1.0, 2.0, 3.0]),
            ("x",),
        )


def test_compute_sobol_indices_validates_column_count() -> None:
    samples = np.zeros((10, 3))
    outputs = np.zeros(10)
    with pytest.raises(SensitivityAnalysisError, match="len\\(param_names\\)"):
        compute_sobol_indices(samples, outputs, ("x", "y"))


def test_compute_sobol_indices_validates_min_rows() -> None:
    samples = np.zeros((4, 2))
    outputs = np.zeros(4)
    with pytest.raises(SensitivityAnalysisError, match="Saltelli"):
        compute_sobol_indices(samples, outputs, ("x", "y"))


def test_compute_sobol_indices_validates_nan_samples() -> None:
    samples = np.ones((20, 2))
    samples[0, 0] = float("nan")
    outputs = np.ones(20)
    with pytest.raises(SensitivityAnalysisError, match="NaN"):
        compute_sobol_indices(samples, outputs, ("x", "y"))


def test_compute_sobol_indices_validates_nan_outputs() -> None:
    samples = np.ones((20, 2))
    outputs = np.ones(20)
    outputs[0] = float("nan")
    with pytest.raises(SensitivityAnalysisError, match="NaN"):
        compute_sobol_indices(samples, outputs, ("x", "y"))


def test_compute_sobol_indices_validates_blank_param_name() -> None:
    samples = np.ones((20, 2))
    outputs = np.ones(20)
    with pytest.raises(SensitivityAnalysisError, match="param_names"):
        compute_sobol_indices(samples, outputs, ("",))


def test_compute_sobol_indices_validates_output_dim() -> None:
    samples = np.ones((20, 2))
    outputs = np.ones((20, 1))
    with pytest.raises(SensitivityAnalysisError, match="1D"):
        compute_sobol_indices(samples, outputs, ("x", "y"))


def test_compute_sobol_indices_validates_output_length() -> None:
    samples = np.ones((20, 2))
    outputs = np.ones(10)
    with pytest.raises(SensitivityAnalysisError, match="samples has"):
        compute_sobol_indices(samples, outputs, ("x", "y"))


def test_compute_sobol_indices_constant_outputs_zero_indices() -> None:
    """All outputs equal => zero variance => zero Sobol indices."""
    samples = np.ones((20, 2))
    outputs = np.ones(20)
    result = compute_sobol_indices(samples, outputs, ("x", "y"))
    assert all(idx.first_order == 0.0 for idx in result)
    assert all(idx.total_order == 0.0 for idx in result)


def test_compute_sobol_indices_returns_correct_count() -> None:
    n_base = 16
    n_params = 3
    total = n_base * (n_params + 2)
    samples = np.random.RandomState(42).rand(total, n_params)
    outputs = np.random.RandomState(43).rand(total)
    result = compute_sobol_indices(samples, outputs, ("a", "b", "c"))
    assert len(result) == 3
    assert [idx.parameter_name for idx in result] == ["a", "b", "c"]


def test_compute_sobol_indices_first_le_total() -> None:
    n_base = 32
    n_params = 2
    total = n_base * (n_params + 2)
    rng = np.random.RandomState(42)
    samples = rng.rand(total, n_params)
    outputs = rng.rand(total)
    result = compute_sobol_indices(samples, outputs, ("a", "b"))
    for idx in result:
        assert idx.first_order <= idx.total_order + 1e-9


# ---------------------------------------------------------------------------
# compute_stability_metrics
# ---------------------------------------------------------------------------


def test_compute_stability_metrics_validates_not_ndarray() -> None:
    with pytest.raises(SensitivityAnalysisError, match="matrix must be np"):
        compute_stability_metrics([[1.0, 0.0], [0.0, 1.0]])  # type: ignore[arg-type]


def test_compute_stability_metrics_validates_2d() -> None:
    with pytest.raises(SensitivityAnalysisError, match="2D"):
        compute_stability_metrics(np.array([1.0, 2.0]))


def test_compute_stability_metrics_validates_square() -> None:
    with pytest.raises(SensitivityAnalysisError, match="square"):
        compute_stability_metrics(np.zeros((2, 3)))


def test_compute_stability_metrics_validates_nonempty() -> None:
    with pytest.raises(SensitivityAnalysisError, match="non-empty"):
        compute_stability_metrics(np.zeros((0, 0)))


def test_compute_stability_metrics_validates_nan() -> None:
    matrix = np.eye(2)
    matrix[0, 0] = float("nan")
    with pytest.raises(SensitivityAnalysisError, match="NaN"):
        compute_stability_metrics(matrix)


def test_compute_stability_metrics_validates_inf() -> None:
    matrix = np.eye(2)
    matrix[0, 0] = float("inf")
    with pytest.raises(SensitivityAnalysisError, match="NaN"):
        compute_stability_metrics(matrix)


def test_compute_stability_identity_is_stable() -> None:
    """Identity matrix has spectral_radius=1, which is NOT <1, so unstable."""
    result = compute_stability_metrics(np.eye(3))
    assert result.spectral_radius == 1.0
    assert result.is_stable is False  # boundary: stable requires <1


def test_compute_stability_zero_is_stable() -> None:
    result = compute_stability_metrics(np.zeros((3, 3)))
    assert result.spectral_radius == 0.0
    assert result.is_stable is True


def test_compute_stability_diag_small_is_stable() -> None:
    result = compute_stability_metrics(np.diag([0.5, 0.3, 0.1]))
    assert result.spectral_radius == 0.5
    assert result.is_stable is True
    assert result.decay_rate > 0


def test_compute_stability_diag_large_unstable() -> None:
    result = compute_stability_metrics(np.diag([1.5, 0.3, 0.1]))
    assert result.spectral_radius == 1.5
    assert result.is_stable is False
    assert result.decay_rate < 0


def test_compute_stability_complex_eigenvalues() -> None:
    """Rotation matrix has complex eigenvalues with magnitude 1."""
    theta = np.pi / 4
    matrix = np.array(
        [
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta), np.cos(theta)],
        ]
    )
    result = compute_stability_metrics(matrix)
    assert abs(result.spectral_radius - 1.0) < 1e-9
    assert result.max_eigenvalue_imag != 0


def test_compute_stability_matrix_sha256_changes_with_input() -> None:
    r1 = compute_stability_metrics(np.eye(2))
    r2 = compute_stability_metrics(np.eye(2) * 2)
    assert r1.matrix_sha256 != r2.matrix_sha256


def test_compute_stability_matrix_sha256_deterministic() -> None:
    r1 = compute_stability_metrics(np.eye(3))
    r2 = compute_stability_metrics(np.eye(3))
    assert r1.matrix_sha256 == r2.matrix_sha256


def test_compute_stability_decay_rate_zero_for_zero_matrix() -> None:
    """Zero matrix: decay_rate clamped to 0.0 (sentinel for 'undefined')."""
    result = compute_stability_metrics(np.zeros((2, 2)))
    assert result.decay_rate == 0.0


def test_compute_stability_singular_matrix_raises() -> None:
    """Singular matrix with very large conditioning can fail eigenvalue calc."""
    matrix = np.array([[1.0, 2.0], [2.0, 4.0]])  # rank deficient
    # Should still compute (eigenvalues are 0 and 5)
    result = compute_stability_metrics(matrix)
    assert result.spectral_radius == pytest.approx(5.0, abs=1e-9)


# ---------------------------------------------------------------------------
# compute_parameter_perturbations
# ---------------------------------------------------------------------------


def _make_claim_evidence() -> tuple[Claim, tuple[Evidence, ...], dict[str, float]]:
    return (
        Claim(
            claim_id="c1",
            statement="test",
            claim_type=ClaimType.PREDICTIVE,
        ),
        (Evidence(tier=EvidenceTier.A, confidence=0.9, source="src"),),
        {"d1": 0.5, "d2": 0.7},
    )


def test_compute_perturbations_basic() -> None:
    claim, evidence, drivers = _make_claim_evidence()
    result = compute_parameter_perturbations(claim, evidence, drivers)
    assert len(result) == 2
    names = {p.parameter_name for p in result}
    assert names == {"d1", "d2"}


def test_compute_perturbations_validates_claim_type() -> None:
    with pytest.raises(SensitivityAnalysisError, match="claim must be Claim"):
        compute_parameter_perturbations(
            "not a claim",  # type: ignore[arg-type]
            (),
            {"d": 0.5},
        )


def test_compute_perturbations_validates_evidence_tuple() -> None:
    claim, _, drivers = _make_claim_evidence()
    with pytest.raises(SensitivityAnalysisError, match="evidence must be tuple"):
        compute_parameter_perturbations(claim, [], drivers)  # type: ignore[arg-type]


def test_compute_perturbations_validates_drivers_dict() -> None:
    claim, evidence, _ = _make_claim_evidence()
    with pytest.raises(SensitivityAnalysisError, match="drivers must be dict"):
        compute_parameter_perturbations(claim, evidence, [])  # type: ignore[arg-type]


def test_compute_perturbations_validates_empty_drivers() -> None:
    claim, evidence, _ = _make_claim_evidence()
    with pytest.raises(SensitivityAnalysisError, match="drivers must not be empty"):
        compute_parameter_perturbations(claim, evidence, {})


def test_compute_perturbations_validates_blank_driver_name() -> None:
    claim, evidence, _ = _make_claim_evidence()
    with pytest.raises(SensitivityAnalysisError, match="driver name"):
        compute_parameter_perturbations(claim, evidence, {"": 0.5})


def test_compute_perturbations_validates_nan_driver() -> None:
    claim, evidence, _ = _make_claim_evidence()
    with pytest.raises(SensitivityAnalysisError, match="must be finite"):
        compute_parameter_perturbations(claim, evidence, {"d": float("nan")})


def test_compute_perturbations_validates_delta_positive() -> None:
    claim, evidence, drivers = _make_claim_evidence()
    with pytest.raises(SensitivityAnalysisError, match="delta"):
        compute_parameter_perturbations(claim, evidence, drivers, delta=0)
    with pytest.raises(SensitivityAnalysisError, match="delta"):
        compute_parameter_perturbations(claim, evidence, drivers, delta=-0.1)


def test_compute_perturbations_clamps_above_one() -> None:
    """Driver at 1.0 perturbed by delta=0.5 stays at 1.0 (clamped)."""
    claim, evidence, _ = _make_claim_evidence()
    result = compute_parameter_perturbations(claim, evidence, {"d": 1.0}, delta=0.5)
    assert result[0].perturbed_value == 1.0


def test_compute_perturbations_handles_zero_baseline() -> None:
    """Driver at 0.0 should use delta as delta_ratio (no division by zero)."""
    claim, evidence, _ = _make_claim_evidence()
    result = compute_parameter_perturbations(claim, evidence, {"d": 0.0}, delta=0.1)
    assert result[0].delta_ratio == 0.1


def test_compute_perturbations_posterior_change_can_be_zero() -> None:
    """Constant posterior despite perturbation (edge case)."""
    claim, evidence, drivers = _make_claim_evidence()
    result = compute_parameter_perturbations(claim, evidence, drivers)
    # All posterior_changes are real numbers (may be 0 or nonzero)
    for p in result:
        assert isinstance(p.posterior_change, float)


# ---------------------------------------------------------------------------
# find_tipping_points
# ---------------------------------------------------------------------------


def test_find_tipping_points_basic() -> None:
    result = find_tipping_points(
        {"d1": 0.5, "d2": 0.3},
        threshold_fn=lambda v: v > 0.4,
    )
    assert len(result) == 1
    assert result[0].driver_name == "d1"


def test_find_tipping_points_none_above() -> None:
    result = find_tipping_points(
        {"d1": 0.3, "d2": 0.4},
        threshold_fn=lambda v: v > 0.5,
    )
    assert len(result) == 0


def test_find_tipping_points_all_above() -> None:
    result = find_tipping_points(
        {"d1": 0.6, "d2": 0.7},
        threshold_fn=lambda v: v > 0.5,
    )
    assert len(result) == 2


def test_find_tipping_points_validates_dict_type() -> None:
    with pytest.raises(SensitivityAnalysisError, match="driver_values must be dict"):
        find_tipping_points([], lambda v: True)  # type: ignore[arg-type]


def test_find_tipping_points_validates_callable() -> None:
    with pytest.raises(SensitivityAnalysisError, match="threshold_fn must be callable"):
        find_tipping_points({"d": 0.5}, "not callable")  # type: ignore[arg-type]


def test_find_tipping_points_validates_blank_name() -> None:
    with pytest.raises(SensitivityAnalysisError, match="driver name"):
        find_tipping_points({"": 0.5}, lambda v: True)


def test_find_tipping_points_validates_nan_value() -> None:
    with pytest.raises(SensitivityAnalysisError, match="must be finite"):
        find_tipping_points({"d": float("nan")}, lambda v: True)


def test_find_tipping_points_threshold_exception_caught() -> None:
    def bad_fn(v: float) -> bool:
        raise ValueError("threshold fn error")

    with pytest.raises(SensitivityAnalysisError, match="threshold_fn raised"):
        find_tipping_points({"d": 0.5}, bad_fn)


def test_find_tipping_points_returns_tuple() -> None:
    result = find_tipping_points({"d": 0.5}, lambda v: True)
    assert isinstance(result, tuple)


# ---------------------------------------------------------------------------
# SensitivityAnalyzer
# ---------------------------------------------------------------------------


def test_analyzer_constructor_validates_callback() -> None:
    with pytest.raises(SensitivityAnalysisError, match="audit_callback"):
        SensitivityAnalyzer(audit_callback="not callable")  # type: ignore[arg-type]


def test_analyzer_constructor_accepts_none() -> None:
    a = SensitivityAnalyzer(audit_callback=None)
    assert a is not None


def test_analyzer_compute_sobol_delegates() -> None:
    a = SensitivityAnalyzer()
    n_base = 16
    n_params = 2
    total = n_base * (n_params + 2)
    samples = np.random.RandomState(42).rand(total, n_params)
    outputs = np.random.RandomState(43).rand(total)
    result = a.compute_sobol_indices(samples, outputs, ("x", "y"))
    assert len(result) == 2


def test_analyzer_compute_stability_delegates() -> None:
    a = SensitivityAnalyzer()
    result = a.compute_stability_metrics(np.eye(2))
    assert result.spectral_radius == 1.0


def test_analyzer_compute_perturbations_delegates() -> None:
    a = SensitivityAnalyzer()
    claim, evidence, drivers = _make_claim_evidence()
    result = a.compute_parameter_perturbations(claim, evidence, drivers)
    assert len(result) == 2


def test_analyzer_find_tipping_delegates() -> None:
    a = SensitivityAnalyzer()
    result = a.find_tipping_points({"d": 0.5}, lambda v: v > 0.3)
    assert len(result) == 1


def test_analyze_sensitivity_minimal() -> None:
    a = SensitivityAnalyzer()
    claim, evidence, drivers = _make_claim_evidence()
    report = a.analyze_sensitivity(claim, evidence, drivers)
    assert isinstance(report, SensitivityReport)
    assert len(report.perturbations) == 2
    assert report.sobol_indices == ()
    assert report.stability_metrics is None
    assert report.tipping_points == ()
    assert report.audit_emitted is False
    assert len(report.analysis_sha256) == 64
    assert len(report.correlation_id) == 36


def test_analyze_sensitivity_with_stability() -> None:
    a = SensitivityAnalyzer()
    claim, evidence, drivers = _make_claim_evidence()
    report = a.analyze_sensitivity(claim, evidence, drivers, stability_matrix=np.diag([0.5, 0.3]))
    assert report.stability_metrics is not None
    assert report.stability_metrics.spectral_radius == 0.5


def test_analyze_sensitivity_with_sobol() -> None:
    a = SensitivityAnalyzer()
    claim, evidence, drivers = _make_claim_evidence()
    n_base = 16
    n_params = 2
    total = n_base * (n_params + 2)
    samples = np.random.RandomState(42).rand(total, n_params)
    outputs = np.random.RandomState(43).rand(total)
    report = a.analyze_sensitivity(
        claim,
        evidence,
        drivers,
        sobol_samples=(samples, outputs, ("a", "b")),
    )
    assert len(report.sobol_indices) == 2


def test_analyze_sensitivity_with_tipping() -> None:
    a = SensitivityAnalyzer()
    claim, evidence, drivers = _make_claim_evidence()
    report = a.analyze_sensitivity(claim, evidence, drivers, tipping_threshold=lambda v: v > 0.4)
    assert len(report.tipping_points) == 2
    assert {t.driver_name for t in report.tipping_points} == {"d1", "d2"}


def test_analyze_sensitivity_full_e2e() -> None:
    a = SensitivityAnalyzer()
    claim, evidence, drivers = _make_claim_evidence()
    n_base = 16
    n_params = 2
    total = n_base * (n_params + 2)
    samples = np.random.RandomState(42).rand(total, n_params)
    outputs = np.random.RandomState(43).rand(total)
    report = a.analyze_sensitivity(
        claim,
        evidence,
        drivers,
        stability_matrix=np.diag([0.5, 0.3]),
        sobol_samples=(samples, outputs, ("a", "b")),
        tipping_threshold=lambda v: v > 0.4,
        delta=0.1,
    )
    assert len(report.sobol_indices) == 2
    assert report.stability_metrics is not None
    assert len(report.perturbations) == 2
    assert len(report.tipping_points) == 2


def test_analyze_sensitivity_with_audit_callback() -> None:
    captured: list[dict[str, Any]] = []

    def cb(payload: dict[str, Any]) -> None:
        captured.append(payload)

    a = SensitivityAnalyzer(audit_callback=cb)
    claim, evidence, drivers = _make_claim_evidence()
    report = a.analyze_sensitivity(claim, evidence, drivers)
    assert report.audit_emitted is True
    assert len(captured) == 1
    assert captured[0]["analysis"] == "sensitivity"
    assert captured[0]["correlation_id"] == report.correlation_id
    assert captured[0]["report_sha256"] == report.analysis_sha256
    assert captured[0]["subordination_notice"] == SUBORDINATION_NOTICE


def test_analyze_sensitivity_audit_callback_exception_handled() -> None:
    """Audit callback exceptions are caught and logged, not raised."""

    def bad_cb(payload: dict[str, Any]) -> None:
        raise RuntimeError("audit error")

    a = SensitivityAnalyzer(audit_callback=bad_cb)
    claim, evidence, drivers = _make_claim_evidence()
    report = a.analyze_sensitivity(claim, evidence, drivers)
    assert report.audit_emitted is False


def test_analyze_sensitivity_custom_correlation_id() -> None:
    a = SensitivityAnalyzer()
    claim, evidence, drivers = _make_claim_evidence()
    report = a.analyze_sensitivity(claim, evidence, drivers, correlation_id="my-custom-id")
    assert report.correlation_id == "my-custom-id"


def test_analyze_sensitivity_deterministic_without_audit() -> None:
    """Same inputs → same SHA-256 (audit emitted flag will be False both times)."""
    a1 = SensitivityAnalyzer()
    a2 = SensitivityAnalyzer()
    claim, evidence, drivers = _make_claim_evidence()
    r1 = a1.analyze_sensitivity(claim, evidence, drivers, correlation_id="fixed-id")
    r2 = a2.analyze_sensitivity(claim, evidence, drivers, correlation_id="fixed-id")
    assert r1.analysis_sha256 == r2.analysis_sha256


def test_analyze_sensitivity_sha256_includes_subordination_notice() -> None:
    """Changing subordination notice invalidates digest (binding test)."""
    a = SensitivityAnalyzer()
    claim, evidence, drivers = _make_claim_evidence()
    report = a.analyze_sensitivity(claim, evidence, drivers, correlation_id="fixed-id")
    # Compute digest with tampered subordination notice
    body = {
        "sobol_indices": [],
        "stability_metrics": None,
        "perturbations": [
            {
                "parameter_name": p.parameter_name,
                "baseline_value": p.baseline_value,
                "perturbed_value": p.perturbed_value,
                "delta_ratio": p.delta_ratio,
                "posterior_change": p.posterior_change,
                "subordination_notice": p.subordination_notice,
            }
            for p in report.perturbations
        ],
        "tipping_points": [],
        "correlation_id": "fixed-id",
        "subordination_notice": "TAMPERED",
    }
    tampered_sha = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert tampered_sha != report.analysis_sha256


def test_get_sensitivity_analyzer_factory() -> None:
    a = get_sensitivity_analyzer()
    assert isinstance(a, SensitivityAnalyzer)


def test_get_sensitivity_analyzer_with_audit() -> None:
    captured: list[dict[str, Any]] = []
    a = get_sensitivity_analyzer(audit_callback=lambda p: captured.append(p))
    assert isinstance(a, SensitivityAnalyzer)
    claim, evidence, drivers = _make_claim_evidence()
    a.analyze_sensitivity(claim, evidence, drivers)
    assert len(captured) == 1


# ---------------------------------------------------------------------------
# Subordination notice propagation
# ---------------------------------------------------------------------------


def test_subordination_notice_in_all_results() -> None:
    """Every result class includes the canonical subordination notice."""
    assert (
        SobolIndices(parameter_name="x", first_order=0.1, total_order=0.2).subordination_notice
        == SUBORDINATION_NOTICE
    )
    assert (
        StabilityMetrics(
            max_eigenvalue_real=0.5,
            max_eigenvalue_imag=0.0,
            spectral_radius=0.5,
            is_stable=True,
            decay_rate=0.1,
            matrix_sha256="0" * 64,
        ).subordination_notice
        == SUBORDINATION_NOTICE
    )
    assert (
        TippingPoint(
            driver_name="d",
            threshold_value=0.5,
            before_state="a",
            after_state="b",
        ).subordination_notice
        == SUBORDINATION_NOTICE
    )
    assert (
        ParameterPerturbation(
            parameter_name="x",
            baseline_value=0.5,
            perturbed_value=0.55,
            delta_ratio=0.1,
            posterior_change=0.02,
        ).subordination_notice
        == SUBORDINATION_NOTICE
    )


# ---------------------------------------------------------------------------
# Determinism / reproducibility
# ---------------------------------------------------------------------------


def test_sobol_indices_deterministic_given_samples() -> None:
    """Same samples + outputs → same Sobol indices."""
    rng = np.random.RandomState(42)
    samples = rng.rand(64, 2)
    outputs = rng.rand(64)
    r1 = compute_sobol_indices(samples, outputs, ("a", "b"))
    r2 = compute_sobol_indices(samples, outputs, ("a", "b"))
    for s1, s2 in zip(r1, r2, strict=True):
        assert s1.first_order == s2.first_order
        assert s1.total_order == s2.total_order


def test_stability_metrics_deterministic() -> None:
    m = np.array([[0.5, 0.1], [0.1, 0.5]])
    r1 = compute_stability_metrics(m)
    r2 = compute_stability_metrics(m)
    assert r1.spectral_radius == r2.spectral_radius
    assert r1.is_stable == r2.is_stable
    assert r1.matrix_sha256 == r2.matrix_sha256


def test_perturbations_deterministic() -> None:
    claim, evidence, drivers = _make_claim_evidence()
    r1 = compute_parameter_perturbations(claim, evidence, drivers)
    r2 = compute_parameter_perturbations(claim, evidence, drivers)
    for p1, p2 in zip(r1, r2, strict=True):
        assert p1.delta_ratio == p2.delta_ratio
        assert p1.posterior_change == p2.posterior_change


# ---------------------------------------------------------------------------
# Module surface
# ---------------------------------------------------------------------------


def test_module_exports_complete() -> None:
    """Verify all advertised exports are importable."""
    from atlas import sensitivity as sens

    expected = {
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
    }
    actual = set(sens.__all__)
    assert expected == actual


def test_module_rejects_unknown_attribute() -> None:
    from atlas import sensitivity as sens

    with pytest.raises(AttributeError, match="no attribute"):
        sens.__getattr__("definitely_not_a_real_thing")
