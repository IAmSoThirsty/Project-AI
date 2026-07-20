"""Integration tests for atlas.sensitivity with execution-gated persistence.

Per Thirstys standards: local integration tests covering:
- Sensitivity analysis through the canonical Atlas service
- Capability token + ExecutionGate end-to-end
- SHA-256 binding subordination notice through full pipeline
- Audit callback integration with execution chain
- Cross-package compatibility with kernel JsonValue
"""

from __future__ import annotations

import hashlib
import json
from datetime import timedelta

import numpy as np
import pytest

from atlas import (
    SUBORDINATION_NOTICE,
    Atlas,
    Claim,
    ClaimType,
    Evidence,
    EvidenceTier,
    SensitivityAnalysisError,
    SensitivityAnalyzer,
    analyze,
    compute_stability_metrics,
    get_sensitivity_analyzer,
)
from capability import CapabilityAuthority
from execution import ExecutionGate
from governance import GovernanceEngine, RuleGovernor
from kernel import EventSpine, Outcome


def _make_authority_and_gate() -> tuple[CapabilityAuthority, ExecutionGate]:
    """Create a fresh capability authority + execution gate for tests."""
    gatekeeper = GovernanceEngine(
        policy_version="v1",
        governors=(RuleGovernor("primary", ()),),
    )
    authority = CapabilityAuthority(
        b"a" * 32,
        issuer="project-ai",
        token_id_factory=iter(f"atlas-{index}" for index in range(10)).__next__,
    )
    gate = ExecutionGate(
        governance=gatekeeper,
        capabilities=authority,
        events=EventSpine(),
    )
    return authority, gate


def _make_claim_evidence() -> tuple[Claim, tuple[Evidence, ...], dict[str, float]]:
    return (
        Claim(
            claim_id="claim-int-1",
            statement="integration test claim",
            claim_type=ClaimType.PREDICTIVE,
        ),
        (
            Evidence(tier=EvidenceTier.A, confidence=0.95, source="primary"),
            Evidence(tier=EvidenceTier.B, confidence=0.80, source="secondary"),
        ),
        {"d1": 0.6, "d2": 0.8, "d3": 0.4},
    )


# ---------------------------------------------------------------------------
# Sensitivity through the canonical Atlas service
# ---------------------------------------------------------------------------


def test_analyze_then_record_via_atlas_service() -> None:
    """SensitivityAnalyzer → Atlas.record → ExecutionGate → projections()."""
    authority, gate = _make_authority_and_gate()
    atlas = Atlas(gate)
    analyzer = SensitivityAnalyzer()

    claim, evidence, drivers = _make_claim_evidence()
    report = analyzer.analyze_sensitivity(
        claim,
        evidence,
        drivers,
        stability_matrix=np.diag([0.5, 0.3, 0.7]),
    )

    # Issue capability token, then record via Atlas
    projection = analyze(
        claim,
        evidence,
        drivers=drivers,
    )
    token = authority.issue(
        subject="analyst-1",
        operation="atlas.projection.record",
        resource=f"atlas:{projection.projection_sha256}",
        ttl=timedelta(minutes=5),
    )
    result = atlas.record(projection, analyst_id="analyst-1", capability_token=token)
    assert result.outcome is Outcome.ALLOW

    stored = atlas.projections()
    assert len(stored) == 1
    assert stored[0].claim_id == "claim-int-1"
    assert stored[0].projection_sha256 == projection.projection_sha256

    # The sensitivity report is independent of the projection but consistent
    assert report.perturbations  # non-empty
    assert report.stability_metrics is not None
    assert report.stability_metrics.is_stable is True


def test_analyze_sensitivity_audit_callback_invoked() -> None:
    """Audit callback fires exactly once with correct payload."""
    captured: list[dict[str, object]] = []

    def cb(payload: dict[str, object]) -> None:
        captured.append(payload)

    analyzer = SensitivityAnalyzer(audit_callback=cb)
    claim, evidence, drivers = _make_claim_evidence()
    report = analyzer.analyze_sensitivity(claim, evidence, drivers)
    assert len(captured) == 1
    assert captured[0]["analysis"] == "sensitivity"
    assert captured[0]["correlation_id"] == report.correlation_id
    assert captured[0]["report_sha256"] == report.analysis_sha256
    assert captured[0]["claim_id"] == claim.claim_id
    assert captured[0]["subordination_notice"] == SUBORDINATION_NOTICE


# ---------------------------------------------------------------------------
# SHA-256 binding subordination notice
# ---------------------------------------------------------------------------


def test_sha256_invalidates_on_tampered_notice() -> None:
    """Changing subordination notice changes digest."""
    analyzer = SensitivityAnalyzer()
    claim, evidence, drivers = _make_claim_evidence()
    report = analyzer.analyze_sensitivity(claim, evidence, drivers, correlation_id="fixed-id")

    # Compute expected SHA manually
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
        "subordination_notice": SUBORDINATION_NOTICE,
    }
    expected = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert report.analysis_sha256 == expected

    # Tamper and re-compute
    body["subordination_notice"] = "TAMPERED"
    tampered = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert tampered != report.analysis_sha256


def test_sha256_deterministic_given_inputs() -> None:
    """Same inputs → same SHA-256 across calls."""
    analyzer1 = SensitivityAnalyzer()
    analyzer2 = SensitivityAnalyzer()
    claim, evidence, drivers = _make_claim_evidence()

    r1 = analyzer1.analyze_sensitivity(claim, evidence, drivers, correlation_id="fixed")
    r2 = analyzer2.analyze_sensitivity(claim, evidence, drivers, correlation_id="fixed")
    assert r1.analysis_sha256 == r2.analysis_sha256


# ---------------------------------------------------------------------------
# Audit callback error handling
# ---------------------------------------------------------------------------


def test_audit_callback_exception_logged_not_raised() -> None:
    """Audit callback that raises is logged as warning, not propagated."""

    def bad_cb(payload: dict[str, object]) -> None:
        raise RuntimeError("audit failure")

    analyzer = SensitivityAnalyzer(audit_callback=bad_cb)
    claim, evidence, drivers = _make_claim_evidence()
    report = analyzer.analyze_sensitivity(claim, evidence, drivers)
    assert report.audit_emitted is False


def test_audit_callback_succeeds_sets_audit_emitted() -> None:
    def good_cb(payload: dict[str, object]) -> None:
        pass

    analyzer = SensitivityAnalyzer(audit_callback=good_cb)
    claim, evidence, drivers = _make_claim_evidence()
    report = analyzer.analyze_sensitivity(claim, evidence, drivers)
    assert report.audit_emitted is True


# ---------------------------------------------------------------------------
# Factory function backward-compat
# ---------------------------------------------------------------------------


def test_factory_function_produces_working_analyzer() -> None:
    a = get_sensitivity_analyzer()
    claim, evidence, drivers = _make_claim_evidence()
    report = a.analyze_sensitivity(claim, evidence, drivers)
    assert report is not None
    assert len(report.perturbations) == 3


def test_factory_function_with_audit_callback() -> None:
    captured: list[dict[str, object]] = []
    a = get_sensitivity_analyzer(audit_callback=lambda p: captured.append(p))
    claim, evidence, drivers = _make_claim_evidence()
    a.analyze_sensitivity(claim, evidence, drivers)
    assert len(captured) == 1


# ---------------------------------------------------------------------------
# Cross-package compatibility
# ---------------------------------------------------------------------------


def test_sensitivity_with_real_capability_tokens() -> None:
    """Mint a real capability token, use it to record projection."""
    authority, gate = _make_authority_and_gate()
    atlas = Atlas(gate)
    analyzer = SensitivityAnalyzer()
    claim, evidence, drivers = _make_claim_evidence()

    # Sensitivity analysis is independent of capability (it's analytical,
    # not actuation). Atlas.record requires capability.
    analyzer.analyze_sensitivity(claim, evidence, drivers)

    projection = analyze(
        claim,
        evidence,
        drivers=drivers,
    )
    token = authority.issue(
        subject="analyst-2",
        operation="atlas.projection.record",
        resource=f"atlas:{projection.projection_sha256}",
        ttl=timedelta(minutes=5),
    )
    atlas.record(projection, analyst_id="analyst-2", capability_token=token)

    assert len(atlas.projections()) == 1


def test_stability_metrics_reproducible_across_calls() -> None:
    """Same matrix → same matrix_sha256 across calls."""
    matrix = np.diag([0.3, 0.5, 0.7])
    r1 = compute_stability_metrics(matrix)
    r2 = compute_stability_metrics(matrix)
    assert r1.matrix_sha256 == r2.matrix_sha256


# ---------------------------------------------------------------------------
# Edge cases through full pipeline
# ---------------------------------------------------------------------------


def test_analyze_with_only_perturbations_no_sobol_no_stability() -> None:
    """Minimal pipeline: only perturbations."""
    analyzer = SensitivityAnalyzer()
    claim, evidence, drivers = _make_claim_evidence()
    report = analyzer.analyze_sensitivity(claim, evidence, drivers)
    assert report.sobol_indices == ()
    assert report.stability_metrics is None
    assert report.tipping_points == ()
    assert len(report.perturbations) == 3


def test_analyze_with_tipping_returns_drivers_above_threshold() -> None:
    """Tipping detection picks drivers above the threshold."""
    analyzer = SensitivityAnalyzer()
    claim, evidence, drivers = _make_claim_evidence()
    # All three drivers (0.6, 0.8, 0.4) vs threshold 0.5: d1=0.6 > 0.5,
    # d2=0.8 > 0.5, d3=0.4 < 0.5 → 2 tipping points
    report = analyzer.analyze_sensitivity(
        claim, evidence, drivers, tipping_threshold=lambda v: v > 0.5
    )
    assert len(report.tipping_points) == 2
    names = {t.driver_name for t in report.tipping_points}
    assert names == {"d1", "d2"}


def test_analyze_with_single_driver() -> None:
    """Minimal driver count (1) should work."""
    analyzer = SensitivityAnalyzer()
    claim, evidence, _ = _make_claim_evidence()
    report = analyzer.analyze_sensitivity(claim, evidence, {"d1": 0.5})
    assert len(report.perturbations) == 1


def test_analyze_with_stable_and_unstable_matrices() -> None:
    """Different matrices give different stability verdicts."""
    analyzer = SensitivityAnalyzer()
    claim, evidence, drivers = _make_claim_evidence()

    report_stable = analyzer.analyze_sensitivity(
        claim, evidence, drivers, stability_matrix=np.diag([0.3, 0.5, 0.7])
    )
    assert report_stable.stability_metrics is not None
    assert report_stable.stability_metrics.is_stable is True

    report_unstable = analyzer.analyze_sensitivity(
        claim, evidence, drivers, stability_matrix=np.diag([1.5, 0.3, 0.1])
    )
    assert report_unstable.stability_metrics is not None
    assert report_unstable.stability_metrics.is_stable is False


# ---------------------------------------------------------------------------
# SensitivityAnalysisError propagation through full pipeline
# ---------------------------------------------------------------------------


def test_invalid_matrix_propagates_error() -> None:
    """Invalid matrix in analyze_sensitivity raises."""
    analyzer = SensitivityAnalyzer()
    claim, evidence, drivers = _make_claim_evidence()
    with pytest.raises(SensitivityAnalysisError, match="square"):
        analyzer.analyze_sensitivity(
            claim,
            evidence,
            drivers,
            stability_matrix=np.zeros((2, 3)),
        )


def test_invalid_drivers_propagates_error() -> None:
    """Empty drivers in analyze_sensitivity raises."""
    analyzer = SensitivityAnalyzer()
    claim, evidence, _ = _make_claim_evidence()
    with pytest.raises(SensitivityAnalysisError, match="drivers must not be empty"):
        analyzer.analyze_sensitivity(claim, evidence, {})


# ---------------------------------------------------------------------------
# End-to-end: full pipeline with audit + capability + execution
# ---------------------------------------------------------------------------


def test_full_e2e_pipeline() -> None:
    """End-to-end: analyzer → audit → projection → execution gate → store."""
    authority, gate = _make_authority_and_gate()
    atlas = Atlas(gate)
    captured: list[dict[str, object]] = []

    def audit_cb(payload: dict[str, object]) -> None:
        captured.append(payload)

    analyzer = SensitivityAnalyzer(audit_callback=audit_cb)
    claim, evidence, drivers = _make_claim_evidence()

    # 1. Run sensitivity
    report = analyzer.analyze_sensitivity(
        claim,
        evidence,
        drivers,
        stability_matrix=np.diag([0.4, 0.6, 0.5]),
        correlation_id="e2e-correlation-id",
    )

    # 2. Verify audit was emitted
    assert len(captured) == 1
    assert captured[0]["correlation_id"] == "e2e-correlation-id"

    # 3. Mint capability, record projection
    projection = analyze(
        claim,
        evidence,
        drivers=drivers,
    )
    token = authority.issue(
        subject="analyst-e2e",
        operation="atlas.projection.record",
        resource=f"atlas:{projection.projection_sha256}",
        ttl=timedelta(minutes=5),
    )
    atlas.record(projection, analyst_id="analyst-e2e", capability_token=token)

    # 4. Verify final state
    stored = atlas.projections()
    assert len(stored) == 1
    assert stored[0].claim_id == "claim-int-1"
    assert report.analysis_sha256
    assert report.correlation_id == "e2e-correlation-id"
    assert report.subordination_notice == SUBORDINATION_NOTICE
