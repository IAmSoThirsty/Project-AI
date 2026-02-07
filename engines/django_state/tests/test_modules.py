"""Tests for all modules."""

from ..kernel.irreversibility_laws import IrreversibilityLaws
from ..modules import (
    HumanForcesModule,
    InstitutionalPressureModule,
    MetricsModule,
    OutcomesModule,
    PerceptionWarfareModule,
    RedTeamModule,
    TimelineModule,
)
from ..schemas.config_schema import IrreversibilityConfig, OutcomeThresholds
from ..schemas.state_schema import StateVector


class TestHumanForcesModule:
    """Test HumanForcesModule."""

    def test_module_initialization(self):
        """Test module initialization."""
        laws = IrreversibilityLaws(IrreversibilityConfig())
        module = HumanForcesModule(laws)
        assert module.population_size == 1000
        assert module.cooperators + module.defectors == module.population_size

    def test_cooperation_decision(self):
        """Test cooperation decision simulation."""
        laws = IrreversibilityLaws(IrreversibilityConfig())
        module = HumanForcesModule(laws)
        state = StateVector.create_initial_state()
        cooperators, defectors = module.simulate_cooperation_decision(state)
        assert cooperators + defectors == module.population_size

    def test_betrayal_risk_evaluation(self):
        """Test betrayal risk calculation."""
        laws = IrreversibilityLaws(IrreversibilityConfig())
        module = HumanForcesModule(laws)
        state = StateVector.create_initial_state()
        state.trust.value = 0.2
        risk = module.evaluate_betrayal_risk(state)
        assert 0.0 <= risk <= 1.0
        assert risk > 0.1  # Should be elevated with low trust


class TestInstitutionalPressureModule:
    """Test InstitutionalPressureModule."""

    def test_module_initialization(self):
        """Test module initialization."""
        laws = IrreversibilityLaws(IrreversibilityConfig())
        module = InstitutionalPressureModule(laws)
        assert module.base_capacity == 1.0
        assert module.efficiency > 0

    def test_capacity_calculation(self):
        """Test governance capacity calculation."""
        laws = IrreversibilityLaws(IrreversibilityConfig())
        module = InstitutionalPressureModule(laws)
        state = StateVector.create_initial_state()
        capacity = module.calculate_governance_capacity(state)
        assert 0.0 <= capacity <= 1.0

    def test_promise_keeping(self):
        """Test promise keeping evaluation."""
        laws = IrreversibilityLaws(IrreversibilityConfig())
        module = InstitutionalPressureModule(laws)
        state = StateVector.create_initial_state()
        module.calculate_governance_capacity(state)
        promise_id = module.make_promise(difficulty=0.5)
        assert promise_id.startswith("promise_")


class TestPerceptionWarfareModule:
    """Test PerceptionWarfareModule."""

    def test_module_initialization(self):
        """Test module initialization."""
        laws = IrreversibilityLaws(IrreversibilityConfig())
        module = PerceptionWarfareModule(laws)
        assert module.reality_fragments == 1
        assert module.consensus_level == 1.0

    def test_campaign_launch(self):
        """Test launching manipulation campaign."""
        laws = IrreversibilityLaws(IrreversibilityConfig())
        module = PerceptionWarfareModule(laws)
        campaign_id = module.launch_manipulation_campaign(
            campaign_type="misinformation",
            target_reach=0.5,
            sophistication=0.6,
            duration=10,
        )
        assert campaign_id.startswith("campaign_")
        assert len(module.active_campaigns) == 1

    def test_reality_fragmentation(self):
        """Test reality fragmentation calculation."""
        laws = IrreversibilityLaws(IrreversibilityConfig())
        module = PerceptionWarfareModule(laws)
        state = StateVector.create_initial_state()
        state.epistemic_confidence.value = 0.3
        fragments = module.calculate_reality_fragmentation(state)
        assert fragments > 1


class TestRedTeamModule:
    """Test RedTeamModule."""

    def test_module_initialization(self):
        """Test module initialization."""
        laws = IrreversibilityLaws(IrreversibilityConfig())
        module = RedTeamModule(laws, black_vault_enabled=True)
        assert module.black_vault_enabled
        assert len(module.black_vault) == 0

    def test_entropy_calculation(self):
        """Test state entropy calculation."""
        laws = IrreversibilityLaws(IrreversibilityConfig())
        module = RedTeamModule(laws)
        state = StateVector.create_initial_state()
        entropy = module.calculate_state_entropy(state)
        assert entropy > 0

    def test_black_vault_fingerprinting(self):
        """Test SHA-256 fingerprinting."""
        laws = IrreversibilityLaws(IrreversibilityConfig())
        module = RedTeamModule(laws, black_vault_enabled=True)
        from ..schemas.event_schema import BetrayalEvent
        event = BetrayalEvent(
            timestamp=0.0,
            source="test",
            description="Test",
            severity=0.5,
            visibility=0.5,
        )
        fingerprint = module.fingerprint_event(event)
        assert len(fingerprint) == 64  # SHA-256 hex digest length

    def test_vulnerability_scan(self):
        """Test attack surface scanning."""
        laws = IrreversibilityLaws(IrreversibilityConfig())
        module = RedTeamModule(laws)
        state = StateVector.create_initial_state()
        state.trust.value = 0.3  # Low trust
        vulnerabilities = module.scan_attack_surface(state)
        assert len(vulnerabilities) > 0


class TestMetricsModule:
    """Test MetricsModule."""

    def test_module_initialization(self):
        """Test module initialization."""
        module = MetricsModule()
        assert len(module.metrics_history) == 0

    def test_metrics_calculation(self):
        """Test calculating metrics."""
        module = MetricsModule()
        state = StateVector.create_initial_state()
        metrics = module.calculate_current_metrics(state)
        assert "trust" in metrics
        assert "system_health" in metrics
        assert "collapse_risk" in metrics
        assert 0 <= metrics["system_health"] <= 100
        assert 0 <= metrics["collapse_risk"] <= 100


class TestTimelineModule:
    """Test TimelineModule."""

    def test_module_initialization(self):
        """Test module initialization."""
        module = TimelineModule()
        assert len(module.timeline) == 0
        assert module.chain_hash == ""

    def test_event_recording(self):
        """Test recording events."""
        module = TimelineModule()
        from ..schemas.event_schema import Event, EventType
        event = Event(
            event_type=EventType.COOPERATION,
            timestamp=0.0,
            source="test",
            description="Test event",
        )
        state = StateVector.create_initial_state()
        index = module.record_event(event, state, state, {})
        assert index == 0
        assert len(module.timeline) == 1

    def test_chain_integrity(self):
        """Test chain integrity verification."""
        module = TimelineModule()
        from ..schemas.event_schema import Event, EventType
        state = StateVector.create_initial_state()
        for i in range(5):
            event = Event(
                event_type=EventType.COOPERATION,
                timestamp=float(i),
                source="test",
                description=f"Event {i}",
            )
            module.record_event(event, state, state, {})

        is_valid, error = module.verify_chain_integrity()
        assert is_valid


class TestOutcomesModule:
    """Test OutcomesModule."""

    def test_module_initialization(self):
        """Test module initialization."""
        thresholds = OutcomeThresholds()
        module = OutcomesModule(thresholds)
        assert not module.outcome_determined

    def test_survivor_classification(self):
        """Test survivor outcome classification."""
        thresholds = OutcomeThresholds()
        module = OutcomesModule(thresholds)
        state = StateVector.create_initial_state()
        state.trust.value = 0.4
        state.legitimacy.value = 0.3
        state.moral_injury.value = 0.5
        outcome = module.classify_outcome(state)
        assert outcome == "survivor"

    def test_extinction_classification(self):
        """Test extinction outcome classification."""
        thresholds = OutcomeThresholds()
        module = OutcomesModule(thresholds)
        state = StateVector.create_initial_state()
        state.trust.value = 0.1
        state.legitimacy.value = 0.05
        state.kindness.value = 0.1
        state.moral_injury.value = 0.9
        outcome = module.classify_outcome(state)
        assert outcome == "extinction"

    def test_outcome_probabilities(self):
        """Test outcome probability calculation."""
        thresholds = OutcomeThresholds()
        module = OutcomesModule(thresholds)
        state = StateVector.create_initial_state()
        probs = module.calculate_outcome_probabilities(state)
        assert "survivor" in probs
        assert "martyr" in probs
        assert "extinction" in probs
        total = sum(probs.values())
        assert 0.95 <= total <= 1.05  # Should sum to ~1.0
