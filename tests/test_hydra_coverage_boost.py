"""
Coverage-boost tests for src/app/core/hydra_50_engine.py.

Covers: data-model dataclasses, all 50 scenario instantiations, five engine
modules (AdversarialRealityGenerator, CrossScenarioCoupler, HumanFailureEmulator,
IrreversibilityDetector, FalseRecoveryEngine), and the main Hydra50Engine class.
"""

import tempfile
from datetime import datetime, timedelta

import pytest

from src.app.core.hydra_50_engine import (
    AIRealityFloodScenario,
    AdversarialRealityGenerator,
    AlgorithmicCulturalDriftScenario,
    AntibioticCollapseScenario,
    AtmosphericAerosolGovernanceScenario,
    AutonomousTradingWarScenario,
    CognitiveLoadScenario,
    CollapseMode,
    ConstructionMaterialLockoutsScenario,
    ControlPlane,
    CreditScoringLockoutScenario,
    CrossScenarioCoupler,
    CulturalMemoryFragmentationScenario,
    CurrencyConfidenceDeathSpiralScenario,
    DNSTrustCollapseScenario,
    DeepfakeLegalEvidenceScenario,
    DemocracyFatigueScenario,
    DisabledRecoveryEvent,
    DomainCoupling,
    EcosystemFalsePositivesScenario,
    EconomicSecessionScenario,
    EnergyBackedBlocsScenario,
    EscalationLevel,
    EscalationStep,
    EventRecord,
    FalseRecoveryEngine,
    FertilityDeclineShockScenario,
    GPSDegradationScenario,
    GenerationalCivilColdWarsScenario,
    GovernanceCeiling,
    HumanFailureEmulator,
    Hydra50Engine,
    InsuranceMarketFailureScenario,
    InternetFragmentationScenario,
    IrreversibilityDetector,
    IrreversibilityLock,
    LaborAlgorithmicCollapseScenario,
    LawBecomesAdvisoryScenario,
    LegitimacyCollapseScenario,
    LiquidityBlackHoleScenario,
    MassCropFailureScenario,
    MassMigrationScenario,
    ModelWeightPoisoningScenario,
    AIDesignedInvasiveSpeciesScenario,
    OceanicFoodChainScenario,
    PermanentEmergencyGovernanceScenario,
    PermanentInflationLockScenario,
    PortAutomationFailuresScenario,
    PowerGridFrequencyWarfareScenario,
    PsychologicalExhaustionScenario,
    RecoveryPoison,
    ReligiousAIProphetsScenario,
    SatelliteOrbitCongestionScenario,
    ScenarioCategory,
    ScenarioState,
    ScenarioStatus,
    SlowBurnPandemicScenario,
    SmartCityKillSwitchScenario,
    SovereignDebtCascadeScenario,
    SpeciesLevelApathyScenario,
    SupplyChainAICollusionScenario,
    SyntheticBiologyLeaksScenario,
    SyntheticIdentityScenario,
    TrafficGridlockScenario,
    TriggerEvent,
    UnderseaCableSabotageScenario,
    UrbanAirToxicityScenario,
    UrbanHeatFeedbackScenario,
    VariableConstraint,
    WaterSystemAttacksScenario,
    AIBackedAuthoritarianismScenario,
)


# ── fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def engine(tmp_dir):
    return Hydra50Engine(data_dir=tmp_dir)


# ── dataclass unit tests ────────────────────────────────────────────────────


class TestTriggerEvent:
    def test_activation_below_threshold(self):
        t = TriggerEvent(
            name="x", description="d", indicators=["a"], threshold_value=0.5
        )
        t.current_value = 0.3
        assert not t.check_activation()
        assert not t.activated

    def test_activation_at_threshold(self):
        t = TriggerEvent(
            name="x", description="d", indicators=["a"], threshold_value=0.5
        )
        t.current_value = 0.5
        assert t.check_activation()
        assert t.activated
        assert t.activation_time is not None

    def test_already_activated_stays_activated(self):
        t = TriggerEvent(
            name="x", description="d", indicators=["a"], threshold_value=0.5
        )
        t.current_value = 0.6
        t.check_activation()
        first_time = t.activation_time
        t.current_value = 0.1
        assert t.check_activation()  # stays activated
        assert t.activation_time == first_time


class TestVariableConstraint:
    def test_ceiling_allows_below(self):
        vc = VariableConstraint(
            variable_name="v",
            constraint_type="ceiling",
            locked_value=0.5,
            locked_at=datetime.utcnow(),
            reason="test",
        )
        ok, msg = vc.validate(0.4)
        assert ok and msg == ""

    def test_ceiling_blocks_above(self):
        vc = VariableConstraint(
            variable_name="v",
            constraint_type="ceiling",
            locked_value=0.5,
            locked_at=datetime.utcnow(),
            reason="test",
        )
        ok, _ = vc.validate(0.6)
        assert not ok

    def test_floor_allows_above(self):
        vc = VariableConstraint(
            variable_name="v",
            constraint_type="floor",
            locked_value=0.2,
            locked_at=datetime.utcnow(),
            reason="test",
        )
        ok, msg = vc.validate(0.3)
        assert ok and msg == ""

    def test_floor_blocks_below(self):
        vc = VariableConstraint(
            variable_name="v",
            constraint_type="floor",
            locked_value=0.2,
            locked_at=datetime.utcnow(),
            reason="test",
        )
        ok, _ = vc.validate(0.1)
        assert not ok

    def test_can_never_increase(self):
        vc = VariableConstraint(
            variable_name="v",
            constraint_type="ceiling",
            locked_value=0.5,
            locked_at=datetime.utcnow(),
            reason="test",
            can_never_increase=True,
        )
        ok, _ = vc.validate(0.6)
        assert not ok

    def test_can_never_decrease(self):
        vc = VariableConstraint(
            variable_name="v",
            constraint_type="floor",
            locked_value=0.5,
            locked_at=datetime.utcnow(),
            reason="test",
            can_never_decrease=True,
        )
        ok, _ = vc.validate(0.4)
        assert not ok


class TestDisabledRecoveryEvent:
    def test_to_dict(self):
        dre = DisabledRecoveryEvent(
            event_name="ev",
            disabled_at=datetime(2025, 1, 1),
            reason="r",
            scenario_id="S01",
            alternative_actions=["alt"],
        )
        d = dre.to_dict()
        assert d["event_name"] == "ev"
        assert d["alternative_actions"] == ["alt"]


class TestGovernanceCeiling:
    def test_effective_ceiling(self):
        gc = GovernanceCeiling(
            domain="d",
            original_ceiling=1.0,
            lowered_ceiling=0.6,
            lowered_at=datetime.utcnow(),
            reason="r",
            multiplier=0.5,
        )
        assert gc.get_effective_ceiling() == pytest.approx(0.3)

    def test_to_dict(self):
        gc = GovernanceCeiling(
            domain="d",
            original_ceiling=1.0,
            lowered_ceiling=0.8,
            lowered_at=datetime(2025, 1, 1),
            reason="r",
            multiplier=1.0,
        )
        d = gc.to_dict()
        assert "effective_ceiling" in d
        assert d["domain"] == "d"


class TestIrreversibilityLock:
    def test_to_dict(self):
        lock = IrreversibilityLock(
            lock_id="L1",
            scenario_id="S01",
            locked_at=datetime(2025, 1, 1),
            irreversibility_score=0.9,
        )
        d = lock.to_dict()
        assert d["lock_id"] == "L1"
        assert d["irreversibility_score"] == 0.9


class TestEventRecord:
    def test_to_dict(self):
        e = EventRecord(
            event_id="E1",
            timestamp=datetime(2025, 1, 1),
            event_type="test",
            scenario_id="S01",
            data={"key": "val"},
            control_plane=ControlPlane.STRATEGIC,
        )
        d = e.to_dict()
        assert d["control_plane"] == "strategic"


class TestScenarioState:
    def test_compute_hash(self):
        s = ScenarioState(
            scenario_id="S01",
            timestamp=datetime.utcnow(),
            status=ScenarioStatus.DORMANT,
            escalation_level=EscalationLevel.LEVEL_0_BASELINE,
            active_triggers=[],
            metrics={},
            coupled_scenarios=[],
        )
        assert len(s.state_hash) == 16

    def test_post_init_hash(self):
        s = ScenarioState(
            scenario_id="S01",
            timestamp=datetime.utcnow(),
            status=ScenarioStatus.TRIGGERED,
            escalation_level=EscalationLevel.LEVEL_1_EARLY_WARNING,
            active_triggers=["a"],
            metrics={"x": 1.0},
            coupled_scenarios=["S02"],
        )
        assert s.state_hash == s.compute_hash()


# ── scenario instantiation ──────────────────────────────────────────────────

SCENARIO_CLASSES = [
    AIRealityFloodScenario,
    AutonomousTradingWarScenario,
    InternetFragmentationScenario,
    SyntheticIdentityScenario,
    CognitiveLoadScenario,
    AlgorithmicCulturalDriftScenario,
    ModelWeightPoisoningScenario,
    DNSTrustCollapseScenario,
    DeepfakeLegalEvidenceScenario,
    PsychologicalExhaustionScenario,
    SovereignDebtCascadeScenario,
    CurrencyConfidenceDeathSpiralScenario,
    EnergyBackedBlocsScenario,
    InsuranceMarketFailureScenario,
    CreditScoringLockoutScenario,
    EconomicSecessionScenario,
    SupplyChainAICollusionScenario,
    PermanentInflationLockScenario,
    LaborAlgorithmicCollapseScenario,
    LiquidityBlackHoleScenario,
    PowerGridFrequencyWarfareScenario,
    SatelliteOrbitCongestionScenario,
    UnderseaCableSabotageScenario,
    WaterSystemAttacksScenario,
    TrafficGridlockScenario,
    SmartCityKillSwitchScenario,
    PortAutomationFailuresScenario,
    ConstructionMaterialLockoutsScenario,
    GPSDegradationScenario,
    UrbanHeatFeedbackScenario,
    SlowBurnPandemicScenario,
    AntibioticCollapseScenario,
    MassCropFailureScenario,
    AIDesignedInvasiveSpeciesScenario,
    OceanicFoodChainScenario,
    AtmosphericAerosolGovernanceScenario,
    UrbanAirToxicityScenario,
    SyntheticBiologyLeaksScenario,
    FertilityDeclineShockScenario,
    EcosystemFalsePositivesScenario,
    LegitimacyCollapseScenario,
    PermanentEmergencyGovernanceScenario,
    AIBackedAuthoritarianismScenario,
    DemocracyFatigueScenario,
    ReligiousAIProphetsScenario,
    GenerationalCivilColdWarsScenario,
    MassMigrationScenario,
    CulturalMemoryFragmentationScenario,
    LawBecomesAdvisoryScenario,
    SpeciesLevelApathyScenario,
]


@pytest.mark.parametrize("cls", SCENARIO_CLASSES, ids=lambda c: c.__name__)
class TestScenarioInstantiation:
    def test_init_sets_attributes(self, cls):
        s = cls()
        assert s.scenario_id
        assert s.name
        assert isinstance(s.category, ScenarioCategory)
        assert s.status == ScenarioStatus.DORMANT

    def test_has_triggers(self, cls):
        s = cls()
        assert len(s.triggers) > 0

    def test_has_escalation_ladder(self, cls):
        s = cls()
        assert len(s.escalation_ladder) > 0

    def test_has_couplings(self, cls):
        s = cls()
        assert isinstance(s.couplings, list)

    def test_has_collapse_modes(self, cls):
        s = cls()
        assert len(s.collapse_modes) > 0

    def test_has_recovery_poisons(self, cls):
        s = cls()
        assert len(s.recovery_poisons) > 0

    def test_capture_state(self, cls):
        s = cls()
        state = s.capture_state()
        assert isinstance(state, ScenarioState)
        assert state.scenario_id == s.scenario_id

    def test_update_metrics(self, cls):
        s = cls()
        first_trigger = s.triggers[0].name
        s.update_metrics({first_trigger: 0.1})
        assert s.metrics[first_trigger] == 0.1


class TestBaseScenarioMethods:
    """Test inherited BaseScenario methods on a representative scenario."""

    def test_evaluate_escalation_no_activation(self):
        s = AIRealityFloodScenario()
        s.evaluate_escalation()  # no-op when activation_time is None

    def test_evaluate_escalation_with_activation(self):
        s = AIRealityFloodScenario()
        s.activation_time = datetime.utcnow() - timedelta(days=1)
        s.metrics["synthetic_content_ratio"] = 0.9
        s.evaluate_escalation()

    def test_get_active_couplings_below_level(self):
        s = AIRealityFloodScenario()
        assert s.get_active_couplings() == []

    def test_get_active_couplings_above_level(self):
        s = AIRealityFloodScenario()
        s.escalation_level = EscalationLevel.LEVEL_3_SYSTEM_STRAIN
        couplings = s.get_active_couplings()
        assert len(couplings) > 0

    def test_check_recovery_event_allowed(self):
        s = AIRealityFloodScenario()
        ok, _ = s.check_recovery_event_allowed("some_event")
        assert ok

    def test_check_recovery_event_blocked(self):
        s = AIRealityFloodScenario()
        lock = IrreversibilityLock(
            lock_id="L",
            scenario_id=s.scenario_id,
            locked_at=datetime.utcnow(),
            irreversibility_score=0.9,
            disabled_recovery_events=[
                DisabledRecoveryEvent(
                    event_name="blocked_event",
                    disabled_at=datetime.utcnow(),
                    reason="test",
                    scenario_id=s.scenario_id,
                )
            ],
        )
        s.active_locks.append(lock)
        ok, reason = s.check_recovery_event_allowed("blocked_event")
        assert not ok
        assert "permanently disabled" in reason

    def test_get_governance_ceiling_none(self):
        s = AIRealityFloodScenario()
        assert s.get_governance_ceiling("any") is None

    def test_get_governance_ceiling_with_lock(self):
        s = AIRealityFloodScenario()
        lock = IrreversibilityLock(
            lock_id="L",
            scenario_id=s.scenario_id,
            locked_at=datetime.utcnow(),
            irreversibility_score=0.9,
            governance_ceilings=[
                GovernanceCeiling(
                    domain="trust",
                    original_ceiling=1.0,
                    lowered_ceiling=0.5,
                    lowered_at=datetime.utcnow(),
                    reason="t",
                    multiplier=0.8,
                )
            ],
        )
        s.active_locks.append(lock)
        ceiling = s.get_governance_ceiling("trust")
        assert ceiling is not None
        assert ceiling == pytest.approx(0.4)

    def test_update_metrics_constraint_violation(self):
        s = AIRealityFloodScenario()
        lock = IrreversibilityLock(
            lock_id="L",
            scenario_id=s.scenario_id,
            locked_at=datetime.utcnow(),
            irreversibility_score=0.9,
            variable_constraints=[
                VariableConstraint(
                    variable_name="synthetic_content_ratio",
                    constraint_type="ceiling",
                    locked_value=0.3,
                    locked_at=datetime.utcnow(),
                    reason="locked",
                    can_never_increase=True,
                )
            ],
        )
        s.active_locks.append(lock)
        with pytest.raises(ValueError, match="Irreversibility constraint"):
            s.update_metrics({"synthetic_content_ratio": 0.5})


# ── engine modules ──────────────────────────────────────────────────────────


class TestAdversarialRealityGenerator:
    def test_empty_scenarios(self):
        g = AdversarialRealityGenerator()
        result = g.generate_compound_scenario([])
        assert result["severity"] == 0.0

    def test_compound_scenario(self):
        s1 = AIRealityFloodScenario()
        s2 = AutonomousTradingWarScenario()
        g = AdversarialRealityGenerator()
        result = g.generate_compound_scenario([s1, s2])
        assert "compound_threats" in result
        assert len(result["compound_threats"]) == 2

    def test_identify_critical_nodes(self):
        s1 = AIRealityFloodScenario()
        s2 = AutonomousTradingWarScenario()
        g = AdversarialRealityGenerator()
        nodes = g.identify_critical_nodes([s1, s2])
        assert isinstance(nodes, list)


class TestCrossScenarioCoupler:
    def test_propagate_no_active_couplings(self):
        c = CrossScenarioCoupler()
        s = AIRealityFloodScenario()
        activated = c.propagate_activation(s, {"S01": s})
        assert activated == []

    def test_propagate_cascading(self):
        c = CrossScenarioCoupler()
        src = AIRealityFloodScenario()
        src.escalation_level = EscalationLevel.LEVEL_3_SYSTEM_STRAIN
        target = DeepfakeLegalEvidenceScenario()
        scenarios = {src.scenario_id: src, target.scenario_id: target}
        activated = c.propagate_activation(src, scenarios)
        assert len(c.coupling_history) > 0

    def test_propagate_synchronizing(self):
        c = CrossScenarioCoupler()
        src = AIRealityFloodScenario()
        src.escalation_level = EscalationLevel.LEVEL_4_CASCADE_THRESHOLD
        # S48 is a coupling target with "synchronizing" type
        target = CulturalMemoryFragmentationScenario()
        scenarios = {src.scenario_id: src, target.scenario_id: target}
        c.propagate_activation(src, scenarios)
        assert len(c.coupling_history) > 0


class TestHumanFailureEmulator:
    def test_low_stress_decision(self):
        h = HumanFailureEmulator()
        result = h.simulate_decision_failure(0.0, "strategic")
        assert "failure_probability" in result
        assert result["decision_type"] == "strategic"

    def test_high_stress_decision(self):
        h = HumanFailureEmulator()
        result = h.simulate_decision_failure(1.0, "tactical")
        assert result["failure_probability"] > 0.5

    def test_history_grows(self):
        h = HumanFailureEmulator()
        h.simulate_decision_failure(0.5, "operational")
        h.simulate_decision_failure(0.5, "operational")
        assert len(h.failure_history) == 2


class TestIrreversibilityDetector:
    def test_assess_not_irreversible(self):
        d = IrreversibilityDetector()
        s = AIRealityFloodScenario()
        assessment = d.assess_irreversibility(s, timedelta(days=1))
        assert not assessment["irreversible"]

    def test_assess_irreversible(self):
        d = IrreversibilityDetector()
        s = AIRealityFloodScenario()
        assessment = d.assess_irreversibility(s, timedelta(days=2000))
        assert assessment["irreversible"]

    def test_create_state_lock_digital(self):
        d = IrreversibilityDetector()
        s = AIRealityFloodScenario()
        lock = d.create_state_lock(s, 0.85, ["epistemic_collapse"])
        assert lock.lock_id in d.active_locks
        assert lock in s.active_locks

    def test_create_state_lock_economic(self):
        d = IrreversibilityDetector()
        s = SovereignDebtCascadeScenario()
        lock = d.create_state_lock(s, 0.9, ["currency_collapse"])
        assert len(lock.variable_constraints) > 0

    def test_create_state_lock_infrastructure(self):
        d = IrreversibilityDetector()
        s = PowerGridFrequencyWarfareScenario()
        lock = d.create_state_lock(s, 0.75, ["cascade_failure"])
        assert len(lock.governance_ceilings) >= 3

    def test_create_state_lock_bio(self):
        d = IrreversibilityDetector()
        s = SlowBurnPandemicScenario()
        lock = d.create_state_lock(s, 0.92, ["ecosystem_collapse"])
        assert len(lock.governance_ceilings) >= 3

    def test_create_state_lock_societal(self):
        d = IrreversibilityDetector()
        s = LegitimacyCollapseScenario()
        lock = d.create_state_lock(s, 0.95, ["legitimacy_collapse"])
        assert any(gc.domain == "social_mandate" for gc in lock.governance_ceilings)

    def test_validate_state_lock_compliance_pass(self):
        d = IrreversibilityDetector()
        s = AIRealityFloodScenario()
        ok, violations = d.validate_state_lock_compliance(s, {"x": 0.5})
        assert ok and violations == []

    def test_validate_state_lock_compliance_fail(self):
        d = IrreversibilityDetector()
        s = AIRealityFloodScenario()
        lock = d.create_state_lock(s, 0.85, ["epistemic_collapse"])
        # The lock creates a can_never_increase constraint on verification_capacity
        ok, violations = d.validate_state_lock_compliance(
            s, {"verification_capacity": 999}
        )
        assert not ok

    def test_get_lock_summary(self):
        d = IrreversibilityDetector()
        s = AIRealityFloodScenario()
        lock = d.create_state_lock(s, 0.9, [])
        summary = d.get_lock_summary(lock.lock_id)
        assert "lock_id" in summary

    def test_get_lock_summary_not_found(self):
        d = IrreversibilityDetector()
        assert d.get_lock_summary("nope")["error"] == "Lock not found"

    def test_get_all_active_locks(self):
        d = IrreversibilityDetector()
        assert d.get_all_active_locks() == []
        s = AIRealityFloodScenario()
        d.create_state_lock(s, 0.8, [])
        assert len(d.get_all_active_locks()) == 1


class TestFalseRecoveryEngine:
    def test_no_poison(self):
        f = FalseRecoveryEngine()
        s = AIRealityFloodScenario()
        result = f.evaluate_recovery_attempt(s, "deploy_shields")
        assert not result["is_poison"]

    def test_poison_detected(self):
        f = FalseRecoveryEngine()
        s = AIRealityFloodScenario()
        result = f.evaluate_recovery_attempt(s, "blockchain_verification_theater")
        assert result["is_poison"]
        assert result["poison_name"] == "blockchain_verification_theater"

    def test_cumulative_cost_empty(self):
        f = FalseRecoveryEngine()
        assert f.calculate_cumulative_poison_cost() == 1.0

    def test_cumulative_cost_with_poisons(self):
        f = FalseRecoveryEngine()
        s = AIRealityFloodScenario()
        f.evaluate_recovery_attempt(s, "blockchain_verification_theater")
        f.evaluate_recovery_attempt(s, "ai_fact_checker_paradox")
        cost = f.calculate_cumulative_poison_cost()
        assert cost > 1.0


# ── Hydra50Engine integration ───────────────────────────────────────────────


class TestHydra50Engine:
    def test_initialization(self, engine):
        assert len(engine.scenarios) == 50
        assert engine.active_control_plane == ControlPlane.OPERATIONAL

    def test_all_50_scenarios_present(self, engine):
        for i in range(1, 51):
            sid = f"S{i:02d}"
            assert sid in engine.scenarios, f"Missing scenario {sid}"

    def test_run_tick_dormant(self, engine):
        result = engine.run_tick()
        assert result["active_scenarios"] == []
        assert result["compound_threats"] is None

    def test_replay_to_timestamp(self, engine):
        result = engine.replay_to_timestamp(datetime.utcnow())
        assert result["events_replayed"] == 0

    def test_attempt_recovery_unknown_scenario(self, engine):
        result = engine.attempt_recovery_action("S99", "anything")
        assert not result["success"]

    def test_get_state_lock_summary_empty(self, engine):
        summary = engine.get_state_lock_summary()
        assert isinstance(summary, dict)
