"""Unit tests for atlas.bayesian module (Phase J2.3.1).

Per Thirstys standards: local, deterministic coverage of:
- Every enum value
- Every dataclass validation path (DriverDependency, BayesianClaim,
  BayesianEvidence, BayesianConfig, BayesianAnalysis)
- Every formula path (EL, WDP, stack, agency, decay)
- Every edge case (empty evidence, missing drivers, NaN/inf, future
  timestamp, unknown stack, unknown tier)
- Audit callback invocation
- Subordination notice binding
- Determinism (same inputs = same outputs)
- Factory function + reset
"""

from __future__ import annotations

import math
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta

import pytest

from atlas import (
    SUBORDINATION_NOTICE,
    AuditCategory,
    AuditLevel,
    AuditTrail,
    BayesianAnalysis,
    BayesianClaim,
    BayesianClaimEngine,
    BayesianConfig,
    BayesianEngineError,
    BayesianEvidence,
    DriverDependency,
    StackPenalty,
    TierWeight,
    calculate_bayesian_posterior,
    get_bayesian_engine,
    reset_bayesian_engine,
)

# ---------------------------------------------------------------------------
# Enum tests
# ---------------------------------------------------------------------------


def test_stack_penalty_values() -> None:
    assert StackPenalty.REALITY.value == "RS"
    assert StackPenalty.TIMELINE_0.value == "TS-0"
    assert StackPenalty.TIMELINE_1.value == "TS-1"
    assert StackPenalty.TIMELINE_2.value == "TS-2"
    assert StackPenalty.TIMELINE_3.value == "TS-3"
    assert StackPenalty.SIMULATION.value == "SS"


def test_tier_weight_values() -> None:
    assert TierWeight.A.value == "A"
    assert TierWeight.B.value == "B"
    assert TierWeight.C.value == "C"
    assert TierWeight.D.value == "D"


def test_stack_penalty_values_intrinsic() -> None:
    # Verify the canonical table
    from atlas.bayesian import _STACK_PENALTY_TABLE

    assert _STACK_PENALTY_TABLE[StackPenalty.REALITY] == 1.0
    assert _STACK_PENALTY_TABLE[StackPenalty.SIMULATION] == 0.0
    assert _STACK_PENALTY_TABLE[StackPenalty.TIMELINE_2] == 0.95


def test_tier_weight_values_intrinsic() -> None:
    from atlas.bayesian import _TIER_WEIGHT_TABLE

    assert _TIER_WEIGHT_TABLE[TierWeight.A] == 1.0
    assert _TIER_WEIGHT_TABLE[TierWeight.B] == 0.85
    assert _TIER_WEIGHT_TABLE[TierWeight.C] == 0.65
    assert _TIER_WEIGHT_TABLE[TierWeight.D] == 0.40


# ---------------------------------------------------------------------------
# BayesianConfig tests
# ---------------------------------------------------------------------------


def test_config_default() -> None:
    config = BayesianConfig()
    assert config.tier_weights == {"A": 1.0, "B": 0.85, "C": 0.65, "D": 0.4}
    assert config.stack_penalties["RS"] == 1.0
    assert config.stack_penalties["SS"] == 0.0
    assert config.agency_penalty_multiplier == 0.5


def test_config_custom() -> None:
    config = BayesianConfig(agency_penalty_multiplier=0.7)
    assert config.agency_penalty_multiplier == 0.7


def test_config_invalid_agency_penalty() -> None:
    with pytest.raises(BayesianEngineError, match="agency_penalty_multiplier"):
        BayesianConfig(agency_penalty_multiplier=1.5)


def test_config_invalid_bonus_threshold() -> None:
    with pytest.raises(BayesianEngineError, match="tier_a_bonus_threshold"):
        BayesianConfig(tier_a_bonus_threshold=0)


def test_config_invalid_bonus_factor_low() -> None:
    with pytest.raises(BayesianEngineError, match="tier_a_bonus_factor"):
        BayesianConfig(tier_a_bonus_factor=0.5)


def test_config_invalid_bonus_factor_high() -> None:
    with pytest.raises(BayesianEngineError, match="tier_a_bonus_factor"):
        BayesianConfig(tier_a_bonus_factor=2.5)


def test_config_invalid_neutral_alignment() -> None:
    with pytest.raises(BayesianEngineError, match="neutral_driver_alignment"):
        BayesianConfig(neutral_driver_alignment=1.5)


def test_config_invalid_empty_evidence() -> None:
    with pytest.raises(BayesianEngineError, match="empty_evidence_legitimacy"):
        BayesianConfig(empty_evidence_legitimacy=-0.1)


def test_config_invalid_distance_decay() -> None:
    with pytest.raises(BayesianEngineError, match="distance_decay_factor"):
        BayesianConfig(distance_decay_factor=0.0)


def test_config_invalid_tier_name() -> None:
    with pytest.raises(BayesianEngineError, match="invalid tier"):
        BayesianConfig(tier_weights={"E": 1.0})


def test_config_invalid_tier_weight_range() -> None:
    with pytest.raises(BayesianEngineError, match="tier_weight"):
        BayesianConfig(tier_weights={"A": 1.5})


def test_config_invalid_stack_penalty_range() -> None:
    with pytest.raises(BayesianEngineError, match="stack_penalty"):
        BayesianConfig(stack_penalties={"RS": 1.5})


def test_config_frozen() -> None:
    config = BayesianConfig()
    with pytest.raises(FrozenInstanceError):
        config.agency_penalty_multiplier = 0.7  # type: ignore[misc]


# ---------------------------------------------------------------------------
# DriverDependency tests
# ---------------------------------------------------------------------------


def test_driver_dependency_minimal() -> None:
    dep = DriverDependency(driver="x", expected_range=(0.0, 1.0))
    assert dep.driver == "x"
    assert dep.expected_range == (0.0, 1.0)


def test_driver_dependency_blank_driver() -> None:
    with pytest.raises(BayesianEngineError, match="driver"):
        DriverDependency(driver="", expected_range=(0.0, 1.0))


def test_driver_dependency_invalid_range_length() -> None:
    with pytest.raises(BayesianEngineError, match="expected_range"):
        DriverDependency(driver="x", expected_range=(0.0,))  # type: ignore[arg-type]


def test_driver_dependency_negative_lo() -> None:
    with pytest.raises(BayesianEngineError, match="expected_range"):
        DriverDependency(driver="x", expected_range=(-0.1, 1.0))


def test_driver_dependency_lo_gt_hi() -> None:
    with pytest.raises(BayesianEngineError, match="expected_range"):
        DriverDependency(driver="x", expected_range=(0.8, 0.2))


def test_driver_dependency_hi_gt_one() -> None:
    with pytest.raises(BayesianEngineError, match="expected_range"):
        DriverDependency(driver="x", expected_range=(0.0, 1.5))


def test_driver_dependency_non_float() -> None:
    from typing import cast

    with pytest.raises(BayesianEngineError, match="must be floats"):
        DriverDependency(driver="x", expected_range=cast(tuple[float, float], (0, 1)))


# ---------------------------------------------------------------------------
# BayesianClaim tests
# ---------------------------------------------------------------------------


def test_bayesian_claim_minimal() -> None:
    claim = BayesianClaim(claim_id="c1", statement="x", claim_type="FACTUAL")
    assert claim.claim_id == "c1"
    assert claim.driver_dependencies == ()
    assert claim.timestamp is None
    assert claim.decay_half_life is None


def test_bayesian_claim_blank_id() -> None:
    with pytest.raises(BayesianEngineError, match="claim_id"):
        BayesianClaim(claim_id="", statement="x", claim_type="FACTUAL")


def test_bayesian_claim_statement_not_str() -> None:
    with pytest.raises(BayesianEngineError, match="statement"):
        BayesianClaim(claim_id="c1", statement=123, claim_type="FACTUAL")  # type: ignore[arg-type]


def test_bayesian_claim_blank_type() -> None:
    with pytest.raises(BayesianEngineError, match="claim_type"):
        BayesianClaim(claim_id="c1", statement="x", claim_type="")


def test_bayesian_claim_negative_decay() -> None:
    with pytest.raises(BayesianEngineError, match="decay_half_life"):
        BayesianClaim(
            claim_id="c1",
            statement="x",
            claim_type="FACTUAL",
            decay_half_life=-1.0,
        )


def test_bayesian_claim_invalid_timestamp() -> None:
    with pytest.raises(BayesianEngineError, match="ISO 8601"):
        BayesianClaim(
            claim_id="c1",
            statement="x",
            claim_type="FACTUAL",
            timestamp="not-a-date",
        )


def test_bayesian_claim_valid_timestamp_z() -> None:
    claim = BayesianClaim(
        claim_id="c1",
        statement="x",
        claim_type="FACTUAL",
        timestamp="2026-06-25T00:00:00Z",
    )
    assert claim.timestamp == "2026-06-25T00:00:00Z"


def test_bayesian_claim_invalid_driver_dep_type() -> None:
    with pytest.raises(BayesianEngineError, match="DriverDependency"):
        BayesianClaim(
            claim_id="c1",
            statement="x",
            claim_type="FACTUAL",
            driver_dependencies=("not-a-dep",),  # type: ignore[arg-type]
        )


def test_bayesian_claim_with_dependencies() -> None:
    claim = BayesianClaim(
        claim_id="c1",
        statement="x",
        claim_type="FACTUAL",
        driver_dependencies=(DriverDependency(driver="d1", expected_range=(0.4, 0.6)),),
    )
    assert len(claim.driver_dependencies) == 1


# ---------------------------------------------------------------------------
# BayesianEvidence tests
# ---------------------------------------------------------------------------


def test_bayesian_evidence_minimal() -> None:
    ev = BayesianEvidence(source="src", tier="A", confidence=0.9)
    assert ev.source == "src"
    assert ev.tier == "A"
    assert ev.confidence == 0.9


def test_bayesian_evidence_blank_source() -> None:
    with pytest.raises(BayesianEngineError, match="source"):
        BayesianEvidence(source="", tier="A", confidence=0.9)


def test_bayesian_evidence_invalid_tier() -> None:
    with pytest.raises(BayesianEngineError, match="tier"):
        BayesianEvidence(source="src", tier="E", confidence=0.9)


def test_bayesian_evidence_confidence_negative() -> None:
    with pytest.raises(BayesianEngineError, match="confidence"):
        BayesianEvidence(source="src", tier="A", confidence=-0.1)


def test_bayesian_evidence_confidence_above_one() -> None:
    with pytest.raises(BayesianEngineError, match="confidence"):
        BayesianEvidence(source="src", tier="A", confidence=1.5)


def test_bayesian_evidence_confidence_nan() -> None:
    with pytest.raises(BayesianEngineError, match="confidence"):
        BayesianEvidence(source="src", tier="A", confidence=float("nan"))


def test_bayesian_evidence_confidence_inf() -> None:
    with pytest.raises(BayesianEngineError, match="confidence"):
        BayesianEvidence(source="src", tier="A", confidence=float("inf"))


def test_bayesian_evidence_confidence_neg_inf() -> None:
    with pytest.raises(BayesianEngineError, match="confidence"):
        BayesianEvidence(source="src", tier="A", confidence=float("-inf"))


# ---------------------------------------------------------------------------
# BayesianAnalysis tests
# ---------------------------------------------------------------------------


def _make_analysis(**overrides: object) -> BayesianAnalysis:
    defaults: dict[str, object] = dict(
        claim_id="c1",
        posterior=0.5,
        evidence_legitimacy=0.5,
        driver_posterior=0.5,
        stack_penalty=1.0,
        agency_penalty=1.0,
        decay_factor=1.0,
        raw_posterior=0.5,
        tier_a_count=0,
        evidence_count=1,
        stack="RS",
        calculation_id="a" * 64,
    )
    defaults.update(overrides)
    return BayesianAnalysis(**defaults)  # type: ignore[arg-type]


def test_analysis_minimal() -> None:
    a = _make_analysis()
    assert a.subordination_notice == SUBORDINATION_NOTICE


def test_analysis_invalid_posterior() -> None:
    with pytest.raises(BayesianEngineError, match="posterior"):
        _make_analysis(posterior=1.5)


def test_analysis_invalid_el() -> None:
    with pytest.raises(BayesianEngineError, match="evidence_legitimacy"):
        _make_analysis(evidence_legitimacy=-0.1)


def test_analysis_invalid_wdp() -> None:
    with pytest.raises(BayesianEngineError, match="driver_posterior"):
        _make_analysis(driver_posterior=1.5)


def test_analysis_invalid_stack_penalty() -> None:
    with pytest.raises(BayesianEngineError, match="stack_penalty"):
        _make_analysis(stack_penalty=2.0)


def test_analysis_invalid_agency_penalty() -> None:
    with pytest.raises(BayesianEngineError, match="agency_penalty"):
        _make_analysis(agency_penalty=2.0)


def test_analysis_invalid_decay_factor() -> None:
    with pytest.raises(BayesianEngineError, match="decay_factor"):
        _make_analysis(decay_factor=2.0)


def test_analysis_invalid_raw_posterior() -> None:
    with pytest.raises(BayesianEngineError, match="raw_posterior"):
        _make_analysis(raw_posterior=2.0)


def test_analysis_negative_tier_a_count() -> None:
    with pytest.raises(BayesianEngineError, match="tier_a_count"):
        _make_analysis(tier_a_count=-1)


def test_analysis_negative_evidence_count() -> None:
    with pytest.raises(BayesianEngineError, match="evidence_count"):
        _make_analysis(evidence_count=-1)


def test_analysis_blank_calculation_id() -> None:
    with pytest.raises(BayesianEngineError, match="calculation_id"):
        _make_analysis(calculation_id="")


# ---------------------------------------------------------------------------
# Engine — calculate_posterior — happy path
# ---------------------------------------------------------------------------


def test_engine_calculate_posterior_basic() -> None:
    claim = BayesianClaim(claim_id="c1", statement="x", claim_type="FACTUAL")
    evidence = (
        BayesianEvidence(source="s1", tier="A", confidence=0.95),
        BayesianEvidence(source="s2", tier="B", confidence=0.85),
    )
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, evidence)
    assert 0.0 <= analysis.posterior <= 1.0
    assert analysis.claim_id == "c1"
    assert analysis.stack == StackPenalty.REALITY
    assert analysis.evidence_count == 2


def test_engine_calculate_posterior_deterministic() -> None:
    claim = BayesianClaim(claim_id="c1", statement="x", claim_type="FACTUAL")
    evidence = (BayesianEvidence(source="s1", tier="A", confidence=0.9),)
    engine = BayesianClaimEngine()
    a1 = engine.calculate_posterior(claim, evidence)
    a2 = engine.calculate_posterior(claim, evidence)
    assert a1 == a2
    assert a1.calculation_id == a2.calculation_id


def test_engine_calculate_posterior_empty_evidence() -> None:
    claim = BayesianClaim(claim_id="c1", statement="x", claim_type="FACTUAL")
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, ())
    # Empty evidence -> empty_evidence_legitimacy (0.1) * neutral (0.7) * 1.0 * 1.0
    assert analysis.evidence_legitimacy == 0.1
    assert analysis.posterior == pytest.approx(0.07, abs=1e-9)


def test_engine_calculate_posterior_ss_stack() -> None:
    claim = BayesianClaim(claim_id="c1", statement="x", claim_type="FACTUAL")
    evidence = (BayesianEvidence(source="s1", tier="A", confidence=1.0),)
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, evidence, stack="SS")
    # SS penalty = 0.0, so posterior should be 0
    assert analysis.posterior == 0.0


def test_engine_calculate_posterior_unknown_stack_default() -> None:
    claim = BayesianClaim(claim_id="c1", statement="x", claim_type="FACTUAL")
    evidence = (BayesianEvidence(source="s1", tier="A", confidence=0.9),)
    engine = BayesianClaimEngine()
    # Unknown stack defaults to 1.0 penalty
    analysis = engine.calculate_posterior(claim, evidence, stack="UNKNOWN")
    assert analysis.stack_penalty == 1.0


# ---------------------------------------------------------------------------
# Engine — Evidence Legitimacy paths
# ---------------------------------------------------------------------------


def test_engine_el_tier_a_bonus() -> None:
    claim = BayesianClaim(claim_id="c", statement="x", claim_type="FACTUAL")
    evidence1 = (BayesianEvidence("s", "A", 0.5),)
    evidence3 = (
        BayesianEvidence("s1", "A", 0.5),
        BayesianEvidence("s2", "A", 0.5),
        BayesianEvidence("s3", "A", 0.5),
    )
    engine = BayesianClaimEngine()
    a1 = engine.calculate_posterior(claim, evidence1)
    a3 = engine.calculate_posterior(claim, evidence3)
    # 2+ TierA sources get 1.1x bonus -> higher EL
    assert a3.evidence_legitimacy > a1.evidence_legitimacy
    assert a3.tier_a_count == 3
    assert a1.tier_a_count == 1


def test_engine_el_weighted_average() -> None:
    claim = BayesianClaim(claim_id="c", statement="x", claim_type="FACTUAL")
    # Tier A weight = 1.0, Tier D weight = 0.4
    # 1 TierA confidence 0.5 + 1 TierD confidence 1.0
    # weighted_sum = 1.0*0.5 + 0.4*1.0 = 0.9
    # total_weight = 1.0 + 0.4 = 1.4
    # EL = 0.9 / 2 = 0.45
    evidence = (
        BayesianEvidence("s1", "A", 0.5),
        BayesianEvidence("s2", "D", 1.0),
    )
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, evidence)
    assert analysis.evidence_legitimacy == pytest.approx(0.45, abs=1e-9)


# ---------------------------------------------------------------------------
# Engine — Driver Posterior paths
# ---------------------------------------------------------------------------


def test_engine_wdp_no_dependencies_neutral() -> None:
    claim = BayesianClaim(claim_id="c", statement="x", claim_type="FACTUAL")
    evidence = (BayesianEvidence("s", "A", 1.0),)
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, evidence)
    assert analysis.driver_posterior == 0.7  # neutral


def test_engine_wdp_in_range() -> None:
    claim = BayesianClaim(
        claim_id="c",
        statement="x",
        claim_type="FACTUAL",
        driver_dependencies=(DriverDependency(driver="d1", expected_range=(0.4, 0.6)),),
    )
    evidence = (BayesianEvidence("s", "A", 1.0),)
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, evidence, driver_context={"d1": 0.5})
    assert analysis.driver_posterior == 1.0


def test_engine_wdp_out_of_range_close() -> None:
    claim = BayesianClaim(
        claim_id="c",
        statement="x",
        claim_type="FACTUAL",
        driver_dependencies=(DriverDependency(driver="d1", expected_range=(0.5, 1.0)),),
    )
    evidence = (BayesianEvidence("s", "A", 1.0),)
    engine = BayesianClaimEngine()
    # distance = 0.4
    # alignment = exp(-0.4 * 2.0) = exp(-0.8) ~ 0.449
    analysis = engine.calculate_posterior(claim, evidence, driver_context={"d1": 0.1})
    expected = math.exp(-0.4 * 2.0)
    assert analysis.driver_posterior == pytest.approx(expected, abs=1e-9)


def test_engine_wdp_out_of_range_high() -> None:
    claim = BayesianClaim(
        claim_id="c",
        statement="x",
        claim_type="FACTUAL",
        driver_dependencies=(DriverDependency(driver="d1", expected_range=(0.0, 0.5)),),
    )
    evidence = (BayesianEvidence("s", "A", 1.0),)
    engine = BayesianClaimEngine()
    # distance = 0.4
    analysis = engine.calculate_posterior(claim, evidence, driver_context={"d1": 0.9})
    expected = math.exp(-0.4 * 2.0)
    assert analysis.driver_posterior == pytest.approx(expected, abs=1e-9)


def test_engine_wdp_missing_driver_neutral() -> None:
    claim = BayesianClaim(
        claim_id="c",
        statement="x",
        claim_type="FACTUAL",
        driver_dependencies=(DriverDependency(driver="d1", expected_range=(0.4, 0.6)),),
    )
    evidence = (BayesianEvidence("s", "A", 1.0),)
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, evidence, driver_context={})
    assert analysis.driver_posterior == 0.7  # neutral


def test_engine_driver_context_invalid_value() -> None:
    claim = BayesianClaim(claim_id="c", statement="x", claim_type="FACTUAL")
    engine = BayesianClaimEngine()
    with pytest.raises(BayesianEngineError, match="driver_context"):
        engine.calculate_posterior(claim, (), driver_context={"d1": 1.5})


# ---------------------------------------------------------------------------
# Engine — Agency penalty paths
# ---------------------------------------------------------------------------


def test_engine_agency_penalty_applied() -> None:
    claim = BayesianClaim(claim_id="c", statement="x", claim_type="AGENCY")
    evidence = (BayesianEvidence("s", "C", 0.9),)  # No TierA/B
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, evidence)
    assert analysis.agency_penalty == 0.5


def test_engine_agency_penalty_with_tier_a() -> None:
    claim = BayesianClaim(claim_id="c", statement="x", claim_type="AGENCY")
    evidence = (BayesianEvidence("s", "A", 0.9),)  # Has TierA
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, evidence)
    assert analysis.agency_penalty == 1.0


def test_engine_agency_penalty_with_tier_b() -> None:
    claim = BayesianClaim(claim_id="c", statement="x", claim_type="AGENCY")
    evidence = (BayesianEvidence("s", "B", 0.9),)  # Has TierB
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, evidence)
    assert analysis.agency_penalty == 1.0


def test_engine_agency_uppercase() -> None:
    claim = BayesianClaim(
        claim_id="c",
        statement="x",
        claim_type="agency",  # lowercase
    )
    evidence = (BayesianEvidence("s", "C", 0.9),)
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, evidence)
    assert analysis.agency_penalty == 0.5


def test_engine_non_agency_no_penalty() -> None:
    claim = BayesianClaim(claim_id="c", statement="x", claim_type="FACTUAL")
    evidence = (BayesianEvidence("s", "D", 0.9),)
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, evidence)
    assert analysis.agency_penalty == 1.0


# ---------------------------------------------------------------------------
# Engine — Temporal decay
# ---------------------------------------------------------------------------


def test_engine_temporal_decay_one_half_life() -> None:
    now = datetime(2026, 6, 25, 12, 0, 0, tzinfo=UTC)
    half_life = 30.0  # 30 days
    ts = (now - timedelta(days=30)).isoformat()
    claim = BayesianClaim(
        claim_id="c",
        statement="x",
        claim_type="FACTUAL",
        timestamp=ts,
        decay_half_life=half_life,
    )
    evidence = (BayesianEvidence("s", "A", 1.0),)
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, evidence, now=now)
    # After one half-life, decay factor = 0.5
    assert analysis.decay_factor == pytest.approx(0.5, abs=1e-6)


def test_engine_temporal_decay_no_decay_no_hl() -> None:
    claim = BayesianClaim(claim_id="c", statement="x", claim_type="FACTUAL")
    evidence = (BayesianEvidence("s", "A", 1.0),)
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, evidence)
    assert analysis.decay_factor == 1.0


def test_engine_temporal_decay_no_decay_no_ts() -> None:
    claim = BayesianClaim(
        claim_id="c",
        statement="x",
        claim_type="FACTUAL",
        decay_half_life=10.0,
    )
    evidence = (BayesianEvidence("s", "A", 1.0),)
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, evidence)
    assert analysis.decay_factor == 1.0


def test_engine_temporal_decay_future_ts_no_decay() -> None:
    now = datetime(2026, 6, 25, 12, 0, 0, tzinfo=UTC)
    future = (now + timedelta(days=10)).isoformat()
    claim = BayesianClaim(
        claim_id="c",
        statement="x",
        claim_type="FACTUAL",
        timestamp=future,
        decay_half_life=10.0,
    )
    evidence = (BayesianEvidence("s", "A", 1.0),)
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, evidence, now=now)
    assert analysis.decay_factor == 1.0


# ---------------------------------------------------------------------------
# Engine — process_claim returns tuple
# ---------------------------------------------------------------------------


def test_engine_process_claim() -> None:
    claim = BayesianClaim(claim_id="c1", statement="x", claim_type="FACTUAL")
    evidence = (BayesianEvidence("s", "A", 0.9),)
    engine = BayesianClaimEngine()
    result_claim, analysis = engine.process_claim(claim, evidence)
    assert result_claim is claim
    assert isinstance(analysis, BayesianAnalysis)
    assert analysis.claim_id == "c1"


# ---------------------------------------------------------------------------
# Engine — audit integration
# ---------------------------------------------------------------------------


def test_engine_init_emits_audit_event() -> None:
    trail = AuditTrail()
    BayesianClaimEngine(audit_trail=trail)
    assert len(trail) == 1
    event = trail.events[0]
    assert event.action == "bayesian_engine_initialized"
    assert event.level == AuditLevel.INFORMATIONAL
    assert event.category == AuditCategory.SYSTEM


def test_engine_calculate_emits_audit_event() -> None:
    trail = AuditTrail()
    engine = BayesianClaimEngine(audit_trail=trail)
    # Trail now has 1 event (init). Reset:
    initial_count = len(trail)
    claim = BayesianClaim(claim_id="c", statement="x", claim_type="FACTUAL")
    evidence = (BayesianEvidence("s", "A", 0.9),)
    engine.calculate_posterior(claim, evidence)
    # +1 event for calculation
    assert len(trail) == initial_count + 1
    event = trail.events[-1]
    assert event.action == "claim_posterior_calculated"
    assert event.level == AuditLevel.STANDARD
    assert event.category == AuditCategory.OPERATION


def test_engine_agency_emits_high_priority_event() -> None:
    trail = AuditTrail()
    engine = BayesianClaimEngine(audit_trail=trail)
    claim = BayesianClaim(claim_id="c", statement="x", claim_type="AGENCY")
    evidence = (BayesianEvidence("s", "C", 0.9),)
    engine.calculate_posterior(claim, evidence)
    # Find the agency_penalty_applied event
    agency_events = [e for e in trail.events if e.action == "agency_penalty_applied"]
    assert len(agency_events) == 1
    assert agency_events[0].level == AuditLevel.HIGH_PRIORITY
    assert agency_events[0].category == AuditCategory.VALIDATION


def test_engine_no_audit_when_not_attached() -> None:
    engine = BayesianClaimEngine()  # No trail
    claim = BayesianClaim(claim_id="c", statement="x", claim_type="FACTUAL")
    evidence = (BayesianEvidence("s", "A", 0.9),)
    # Should not raise
    analysis = engine.calculate_posterior(claim, evidence)
    assert analysis is not None


def test_engine_attach_audit_trail() -> None:
    engine = BayesianClaimEngine()
    trail = AuditTrail()
    engine.attach_audit_trail(trail)
    # After attach, init event is emitted
    assert len(trail) >= 1


def test_engine_attach_invalid_audit_type() -> None:
    engine = BayesianClaimEngine()
    with pytest.raises(BayesianEngineError, match="AuditTrail"):
        engine.attach_audit_trail("not a trail")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------


def test_calculate_bayesian_posterior_one_shot() -> None:
    claim = BayesianClaim(claim_id="c1", statement="x", claim_type="FACTUAL")
    evidence = (BayesianEvidence("s", "A", 0.9),)
    analysis = calculate_bayesian_posterior(claim, evidence)
    assert analysis.posterior > 0.0
    assert analysis.claim_id == "c1"


def test_calculate_bayesian_posterior_with_config() -> None:
    config = BayesianConfig(agency_penalty_multiplier=0.3)
    claim = BayesianClaim(claim_id="c", statement="x", claim_type="AGENCY")
    evidence = (BayesianEvidence("s", "C", 0.9),)
    analysis = calculate_bayesian_posterior(claim, evidence, config=config)
    assert analysis.agency_penalty == 0.3


# ---------------------------------------------------------------------------
# Factory + reset
# ---------------------------------------------------------------------------


def test_get_bayesian_engine_factory() -> None:
    reset_bayesian_engine()
    engine = get_bayesian_engine()
    assert isinstance(engine, BayesianClaimEngine)


def test_get_bayesian_engine_singleton() -> None:
    reset_bayesian_engine()
    e1 = get_bayesian_engine()
    e2 = get_bayesian_engine()
    assert e1 is e2


def test_reset_bayesian_engine() -> None:
    reset_bayesian_engine()
    e1 = get_bayesian_engine()
    reset_bayesian_engine()
    e2 = get_bayesian_engine()
    assert e1 is not e2


def test_get_engine_with_audit() -> None:
    reset_bayesian_engine()
    trail = AuditTrail()
    get_bayesian_engine(audit_trail=trail)
    # Init event was emitted
    assert len(trail) >= 1


# ---------------------------------------------------------------------------
# End-to-end formula verification (canonical legacy behavior)
# ---------------------------------------------------------------------------


def test_full_formula_basic() -> None:
    """Verify EL x WDP x StackPenalty x AgencyPenalty for simple case."""
    claim = BayesianClaim(
        claim_id="c",
        statement="x",
        claim_type="FACTUAL",
        driver_dependencies=(DriverDependency(driver="d1", expected_range=(0.5, 0.9)),),
    )
    evidence = (
        BayesianEvidence("s1", "A", 0.95),
        BayesianEvidence("s2", "B", 0.85),
    )
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, evidence, driver_context={"d1": 0.7})
    # Driver in range -> WDP = 1.0
    assert analysis.driver_posterior == 1.0
    # Agency FACTUAL -> 1.0
    assert analysis.agency_penalty == 1.0
    # Stack RS -> 1.0
    assert analysis.stack_penalty == 1.0
    # EL: weighted_sum = 1.0*0.95 + 0.85*0.85 = 0.95 + 0.7225 = 1.6725
    # EL = 1.6725 / 2 = 0.83625
    # No TierA bonus (only 1 TierA, threshold is 2)
    assert analysis.evidence_legitimacy == pytest.approx(0.83625, abs=1e-9)
    # Raw = 0.83625 * 1.0 * 1.0 * 1.0 = 0.83625
    assert analysis.raw_posterior == pytest.approx(0.83625, abs=1e-9)
    # Posterior = clamp to [0,1] -> 0.83625
    assert analysis.posterior == pytest.approx(0.83625, abs=1e-9)


# ---------------------------------------------------------------------------
# Subordination notice binding
# ---------------------------------------------------------------------------


def test_subordination_notice_in_analysis() -> None:
    claim = BayesianClaim(claim_id="c", statement="x", claim_type="FACTUAL")
    evidence = (BayesianEvidence("s", "A", 0.9),)
    engine = BayesianClaimEngine()
    analysis = engine.calculate_posterior(claim, evidence)
    assert analysis.subordination_notice == SUBORDINATION_NOTICE


# ---------------------------------------------------------------------------
# Module exports surface
# ---------------------------------------------------------------------------


def test_module_exports_complete() -> None:
    from atlas import bayesian as bay

    expected = {
        "BayesianAnalysis",
        "BayesianClaim",
        "BayesianClaimEngine",
        "BayesianConfig",
        "BayesianEngineError",
        "BayesianEvidence",
        "DriverDependency",
        "StackPenalty",
        "TierWeight",
        "calculate_bayesian_posterior",
        "get_bayesian_engine",
        "reset_bayesian_engine",
    }
    assert expected == set(bay.__all__)


def test_top_level_imports() -> None:
    """All advertised symbols are importable from atlas top-level."""
    from atlas import (
        BayesianAnalysis,
        BayesianClaim,
        BayesianClaimEngine,
    )

    assert BayesianAnalysis is not None
    assert BayesianClaim is not None
    assert BayesianClaimEngine is not None
