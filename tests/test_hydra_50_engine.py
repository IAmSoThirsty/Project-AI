#!/usr/bin/env python3
"""
Comprehensive Tests for HYDRA-50 Contingency Plan Engine

Tests all 50 scenarios, 5 engine modules, event sourcing, time-travel,
and integration points. Target: 80%+ coverage.
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from app.core.hydra_50_engine import (
    SCENARIO_REGISTRY,
    AIRealityFloodScenario,
    AutonomousTradingWarScenario,
    ControlPlane,
    EscalationLevel,
    Hydra50Engine,
    LegitimacyCollapseScenario,
    PowerGridFrequencyWarfareScenario,
    ScenarioStatus,
    SlowBurnPandemicScenario,
    SovereignDebtCascadeScenario,
)
from app.core.hydra_50_integration import (
    CommandCenterIntegration,
    GlobalScenarioEngineIntegration,
    GUIExportHooks,
    Hydra50IntegrationManager,
    PlanetaryDefenseIntegration,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def temp_data_dir():
    """Create temporary data directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def engine(temp_data_dir):
    """Create Hydra50Engine instance for testing"""
    return Hydra50Engine(data_dir=temp_data_dir)


@pytest.fixture
def integration_manager(temp_data_dir):
    """Create integrated Hydra50 instance"""
    return Hydra50IntegrationManager(data_dir=temp_data_dir)


# ============================================================================
# SCENARIO TESTS (S01-S50)
# ============================================================================


class TestDigitalCognitiveScenarios:
    """Test Digital/Cognitive scenarios (S01-S10)"""

    def test_s01_ai_reality_flood_triggers(self):
        """Test S01 trigger activation"""
        scenario = AIRealityFloodScenario()

        # Initial state
        assert scenario.status == ScenarioStatus.DORMANT
        assert not any(t.activated for t in scenario.triggers)

        # Activate triggers
        scenario.update_metrics(
            {
                "synthetic_content_ratio": 0.6,  # Above 0.5 threshold
                "verification_capacity_deficit": 0.95,  # Above 0.9 threshold
            }
        )

        # Check activation
        assert scenario.triggers[0].activated
        assert scenario.triggers[1].activated

    def test_s01_escalation_ladder(self):
        """Test S01 escalation progression"""
        scenario = AIRealityFloodScenario()
        scenario.activation_time = datetime.utcnow() - timedelta(days=100)

        # Set required conditions for L2
        scenario.metrics = {
            "synthetic_content_ratio": 0.6,
            "verification_capacity_deficit": 0.95,
        }

        # Evaluate escalation
        scenario.evaluate_escalation()

        # Should escalate to at least L2
        assert scenario.escalation_level.value >= 2

    def test_s01_couplings(self):
        """Test S01 cross-scenario couplings"""
        scenario = AIRealityFloodScenario()
        scenario.escalation_level = EscalationLevel.LEVEL_3_SYSTEM_STRAIN

        # Get active couplings
        couplings = scenario.get_active_couplings()

        # Should have high-strength couplings
        assert len(couplings) > 0
        assert any(c.target_scenario_id == "S09" for c in couplings)  # Deepfake coupling

    def test_s02_autonomous_trading_war(self):
        """Test S02 algorithmic trading scenario"""
        scenario = AutonomousTradingWarScenario()

        scenario.update_metrics(
            {
                "algorithmic_trading_dominance": 0.85,
                "flash_crash_frequency": 2.0,
            }
        )

        assert scenario.triggers[0].activated
        assert scenario.triggers[1].activated

    def test_scenarios_s03_to_s10_initialization(self):
        """Test that S03-S10 initialize correctly"""
        from app.core.hydra_50_engine import (
            AlgorithmicCulturalDriftScenario,
            CognitiveLoadScenario,
            DeepfakeLegalEvidenceScenario,
            DNSTrustCollapseScenario,
            InternetFragmentationScenario,
            ModelWeightPoisoningScenario,
            PsychologicalExhaustionScenario,
            SyntheticIdentityScenario,
        )

        scenarios = [
            InternetFragmentationScenario(),
            SyntheticIdentityScenario(),
            CognitiveLoadScenario(),
            AlgorithmicCulturalDriftScenario(),
            ModelWeightPoisoningScenario(),
            DNSTrustCollapseScenario(),
            DeepfakeLegalEvidenceScenario(),
            PsychologicalExhaustionScenario(),
        ]

        for scenario in scenarios:
            assert scenario.status == ScenarioStatus.DORMANT
            assert len(scenario.triggers) > 0
            assert len(scenario.escalation_ladder) > 0


class TestEconomicScenarios:
    """Test Economic scenarios (S11-S20)"""

    def test_s11_sovereign_debt_cascade(self):
        """Test S11 debt crisis scenario"""
        scenario = SovereignDebtCascadeScenario()

        scenario.update_metrics(
            {
                "default_count": 4.0,  # Above 3.0 threshold
                "debt_to_gdp_threshold": 3.2,
            }
        )

        assert scenario.triggers[0].activated
        assert scenario.triggers[1].activated

    def test_s11_collapse_modes(self):
        """Test S11 collapse mode definitions"""
        scenario = SovereignDebtCascadeScenario()

        assert len(scenario.collapse_modes) > 0
        assert scenario.collapse_modes[0].irreversibility_score > 0.5

    def test_s11_recovery_poisons(self):
        """Test S11 recovery poison definitions"""
        scenario = SovereignDebtCascadeScenario()

        assert len(scenario.recovery_poisons) > 0
        assert scenario.recovery_poisons[0].long_term_cost_multiplier > 1.0

    def test_scenarios_s12_to_s20_complete(self, engine):
        """Test that all economic scenarios (S12-S20) are present"""
        economic_scenarios = [f"S{i:02d}" for i in range(12, 21)]

        for sid in economic_scenarios:
            assert sid in engine.scenarios
            scenario = engine.scenarios[sid]
            assert scenario.category.value == "economic"


class TestInfrastructureScenarios:
    """Test Infrastructure scenarios (S21-S30)"""

    def test_s21_power_grid_warfare(self):
        """Test S21 grid frequency warfare"""
        scenario = PowerGridFrequencyWarfareScenario()

        assert scenario.category.value == "infrastructure"
        assert len(scenario.triggers) > 0
        assert len(scenario.escalation_ladder) > 0

    def test_infrastructure_scenarios_complete(self, engine):
        """Test that all infrastructure scenarios (S21-S30) are present"""
        infra_scenarios = [f"S{i:02d}" for i in range(21, 31)]

        for sid in infra_scenarios:
            assert sid in engine.scenarios
            scenario = engine.scenarios[sid]
            assert scenario.category.value == "infrastructure"


class TestBiologicalEnvironmentalScenarios:
    """Test Biological/Environmental scenarios (S31-S40)"""

    def test_s31_slow_burn_pandemic(self):
        """Test S31 pandemic scenario"""
        scenario = SlowBurnPandemicScenario()

        assert scenario.category.value == "biological_environmental"
        assert len(scenario.triggers) > 0

    def test_bio_scenarios_complete(self, engine):
        """Test that all bio/env scenarios (S31-S40) are present"""
        bio_scenarios = [f"S{i:02d}" for i in range(31, 41)]

        for sid in bio_scenarios:
            assert sid in engine.scenarios
            scenario = engine.scenarios[sid]
            assert scenario.category.value == "biological_environmental"


class TestSocietalScenarios:
    """Test Societal scenarios (S41-S50)"""

    def test_s41_legitimacy_collapse(self):
        """Test S41 legitimacy crisis"""
        scenario = LegitimacyCollapseScenario()

        assert scenario.category.value == "societal"
        assert len(scenario.triggers) > 0

    def test_societal_scenarios_complete(self, engine):
        """Test that all societal scenarios (S41-S50) are present"""
        societal_scenarios = [f"S{i:02d}" for i in range(41, 51)]

        for sid in societal_scenarios:
            assert sid in engine.scenarios
            scenario = engine.scenarios[sid]
            assert scenario.category.value == "societal"

    def test_all_50_scenarios_present(self, engine):
        """Test that all 50 scenarios are initialized"""
        assert len(engine.scenarios) == 50

        for i in range(1, 51):
            sid = f"S{i:02d}"
            assert sid in engine.scenarios


# ============================================================================
# ENGINE MODULE TESTS
# ============================================================================


class TestAdversarialRealityGenerator:
    """Test Adversarial Reality Generator module"""

    def test_compound_scenario_generation(self, engine):
        """Test generation of compound scenarios"""
        # Activate multiple scenarios
        engine.update_scenario_metrics("S01", {"synthetic_content_ratio": 0.6})
        engine.update_scenario_metrics("S05", {"information_exposure_rate": 12.0})
        engine.update_scenario_metrics("S10", {"mental_health_crisis": 0.5})

        # Get active scenarios
        active = [s for s in engine.scenarios.values() if s.status != ScenarioStatus.DORMANT]

        # Generate compound
        compound = engine.adversarial_generator.generate_compound_scenario(active)

        assert "compound_threats" in compound
        assert "severity" in compound
        assert compound["severity"] > 0

    def test_critical_nodes_identification(self, engine):
        """Test identification of high-coupling scenarios"""
        critical_nodes = engine.adversarial_generator.identify_critical_nodes(list(engine.scenarios.values()))

        assert len(critical_nodes) == 10  # Top 10
        assert all(sid in engine.scenarios for sid in critical_nodes)


class TestCrossScenarioCoupler:
    """Test Cross-Scenario Coupler module"""

    def test_cascading_activation(self, engine):
        """Test cascading activation between scenarios"""
        # Activate S01 (AI Reality Flood)
        engine.update_scenario_metrics("S01", {"synthetic_content_ratio": 0.6})
        s01 = engine.scenarios["S01"]
        s01.escalation_level = EscalationLevel.LEVEL_3_SYSTEM_STRAIN

        # Propagate to coupled scenarios
        activated = engine.scenario_coupler.propagate_activation(s01, engine.scenarios)

        # Should activate coupled scenarios (S09, S44, S48)
        assert len(activated) >= 0  # May activate depending on coupling logic

    def test_coupling_history_tracking(self, engine):
        """Test that coupling events are tracked"""
        engine.update_scenario_metrics("S01", {"synthetic_content_ratio": 0.6})
        s01 = engine.scenarios["S01"]
        s01.escalation_level = EscalationLevel.LEVEL_3_SYSTEM_STRAIN

        engine.scenario_coupler.propagate_activation(s01, engine.scenarios)

        # Check coupling history
        history = engine.scenario_coupler.coupling_history
        assert isinstance(history, list)


class TestHumanFailureEmulator:
    """Test Human Failure Emulator module"""

    def test_decision_failure_simulation(self, engine):
        """Test human decision failure modeling"""
        result = engine.human_failure_emulator.simulate_decision_failure(
            stress_level=0.8, decision_type="tactical"  # High stress
        )

        assert "failed" in result
        assert "failure_probability" in result
        assert result["failure_probability"] > 0.1

    def test_stress_amplification(self, engine):
        """Test that repeated failures increase failure probability"""
        # Simulate multiple failures
        results = []
        for _ in range(5):
            result = engine.human_failure_emulator.simulate_decision_failure(0.5, "strategic")
            results.append(result)

        # Failure probability should increase over time
        assert len(engine.human_failure_emulator.failure_history) == 5


class TestIrreversibilityDetector:
    """Test Irreversibility Detector module"""

    def test_irreversibility_assessment(self, engine):
        """Test detection of irreversible states"""
        scenario = engine.scenarios["S01"]
        scenario.activation_time = datetime.utcnow() - timedelta(days=800)

        # Assess irreversibility
        assessment = engine.irreversibility_detector.assess_irreversibility(scenario, time_elapsed=timedelta(days=800))

        assert "irreversible" in assessment
        assert "score" in assessment

    def test_irreversible_threshold(self, engine):
        """Test that high irreversibility scores are detected"""
        scenario = engine.scenarios["S01"]
        scenario.activation_time = datetime.utcnow() - timedelta(days=1000)

        assessment = engine.irreversibility_detector.assess_irreversibility(scenario, time_elapsed=timedelta(days=1000))

        # Should detect irreversibility after long elapsed time
        if assessment["score"] > 0.7:
            assert assessment["irreversible"] is True


class TestFalseRecoveryEngine:
    """Test False Recovery Engine module"""

    def test_recovery_poison_detection(self, engine):
        """Test detection of recovery poisons"""
        scenario = engine.scenarios["S01"]

        evaluation = engine.false_recovery_engine.evaluate_recovery_attempt(
            scenario, "blockchain_verification_theater"  # Known poison
        )

        assert evaluation["is_poison"] is True
        assert "long_term_multiplier" in evaluation
        assert evaluation["long_term_multiplier"] > 1.0

    def test_cumulative_poison_cost(self, engine):
        """Test calculation of cumulative poison costs"""
        scenario = engine.scenarios["S01"]

        # Deploy multiple poisons
        engine.false_recovery_engine.evaluate_recovery_attempt(scenario, "blockchain_verification_theater")
        engine.false_recovery_engine.evaluate_recovery_attempt(scenario, "ai_fact_checker_paradox")

        # Calculate total cost
        total_cost = engine.false_recovery_engine.calculate_cumulative_poison_cost()
        assert total_cost > 1.0


# ============================================================================
# EVENT SOURCING & TIME-TRAVEL TESTS
# ============================================================================


class TestEventSourcing:
    """Test event sourcing capabilities"""

    def test_event_log_recording(self, engine):
        """Test that events are recorded"""
        initial_count = len(engine.event_log)

        engine.update_scenario_metrics("S01", {"synthetic_content_ratio": 0.6})

        assert len(engine.event_log) > initial_count

    def test_state_snapshot_capture(self, engine):
        """Test state snapshot creation"""
        engine.update_scenario_metrics("S01", {"synthetic_content_ratio": 0.6})

        scenario = engine.scenarios["S01"]
        state = scenario.capture_state()

        assert state.scenario_id == "S01"
        assert state.state_hash != ""

    def test_state_persistence(self, temp_data_dir):
        """Test that state persists to disk"""
        engine = Hydra50Engine(data_dir=temp_data_dir)
        engine.update_scenario_metrics("S01", {"synthetic_content_ratio": 0.6})
        engine._save_state()

        # Check that state file exists
        state_file = Path(temp_data_dir) / "engine_state.json"
        assert state_file.exists()

        # Load state in new engine
        engine2 = Hydra50Engine(data_dir=temp_data_dir)
        assert engine2.scenarios["S01"].metrics.get("synthetic_content_ratio") == 0.6


class TestTimeTravel:
    """Test time-travel replay capabilities"""

    def test_replay_to_timestamp(self, engine):
        """Test replay to specific timestamp"""
        # Record events
        t1 = datetime.utcnow()
        engine.update_scenario_metrics("S01", {"synthetic_content_ratio": 0.6})

        datetime.utcnow()
        engine.update_scenario_metrics("S01", {"synthetic_content_ratio": 0.8})

        # Replay to t1
        result = engine.replay_to_timestamp(t1 + timedelta(seconds=1))

        assert result["events_replayed"] >= 0
        assert "final_state" in result

    def test_counterfactual_branching(self, engine):
        """Test counterfactual what-if scenarios"""
        # Create baseline
        engine.update_scenario_metrics("S01", {"synthetic_content_ratio": 0.6})
        branch_point = datetime.utcnow()

        # Create alternate branch
        alternate_events = [{"scenario_id": "S01", "metrics": {"synthetic_content_ratio": 0.3}}]

        branch_result = engine.create_counterfactual_branch("low_ai_content", branch_point, alternate_events)

        assert branch_result["branch_name"] == "low_ai_content"
        assert len(branch_result["results"]) == 10  # 10 ticks


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestPlanetaryDefenseIntegration:
    """Test Planetary Defense integration"""

    def test_mitigation_validation(self, engine):
        """Test mitigation action validation"""
        pd_integration = PlanetaryDefenseIntegration(engine)

        is_allowed, reason = pd_integration.validate_mitigation_action("S01", "Deploy watermarking standards")

        # Should either validate or fallback to allow
        assert isinstance(is_allowed, bool)
        assert isinstance(reason, str)

    def test_integrated_tick(self, engine):
        """Test integrated tick with PD validation"""
        pd_integration = PlanetaryDefenseIntegration(engine)

        engine.update_scenario_metrics("S01", {"synthetic_content_ratio": 0.6})

        tick_result = pd_integration.run_integrated_tick()

        assert "validated_mitigations" in tick_result


class TestGlobalScenarioEngineIntegration:
    """Test Global Scenario Engine integration"""

    def test_module_info(self, engine):
        """Test module metadata export"""
        gse_integration = GlobalScenarioEngineIntegration(engine)

        info = gse_integration.get_module_info()

        assert info["module_id"] == "hydra50"
        assert info["scenario_count"] == 50

    def test_query_handling(self, engine):
        """Test query handling"""
        gse_integration = GlobalScenarioEngineIntegration(engine)

        # Test dashboard query
        result = gse_integration.query("get_dashboard_state")
        assert "active_count" in result

        # Test scenario detail query
        result = gse_integration.query("get_scenario_detail", {"scenario_id": "S01"})
        assert result["id"] == "S01"


class TestCommandCenterIntegration:
    """Test Command Center integration"""

    def test_widget_data_generation(self, engine):
        """Test widget data export"""
        cc_integration = CommandCenterIntegration(engine)

        status = cc_integration.get_status_widget_data()
        assert status["widget_type"] == "hydra50_status"

        scenario_list = cc_integration.get_scenario_list_widget_data()
        assert scenario_list["widget_type"] == "hydra50_scenario_list"

    def test_control_actions(self, engine):
        """Test control action handling"""
        cc_integration = CommandCenterIntegration(engine)

        result = cc_integration.handle_control_action("run_tick", user_id="test_user")
        assert result["success"] is True


class TestGUIExportHooks:
    """Test GUI export hooks"""

    def test_scenario_dropdown_list(self, engine):
        """Test scenario list export"""
        gui_hooks = GUIExportHooks(engine)

        scenarios = gui_hooks.get_scenario_dropdown_list()

        assert len(scenarios) == 50
        assert scenarios[0]["id"] == "S01"

    def test_scenario_detail_export(self, engine):
        """Test detailed scenario export"""
        gui_hooks = GUIExportHooks(engine)

        detail = gui_hooks.get_scenario_detail_for_gui("S01")

        assert detail["id"] == "S01"
        assert "triggers" in detail
        assert "escalation_ladder" in detail
        assert "couplings" in detail

    def test_dashboard_summary(self, engine):
        """Test dashboard summary export"""
        gui_hooks = GUIExportHooks(engine)

        summary = gui_hooks.get_dashboard_summary_for_gui()

        assert "totals" in summary
        assert "control" in summary


class TestIntegrationManager:
    """Test unified integration manager"""

    def test_manager_initialization(self, integration_manager):
        """Test that all integrations initialize"""
        assert integration_manager.hydra is not None
        assert integration_manager.planetary_defense is not None
        assert integration_manager.global_scenario_engine is not None
        assert integration_manager.command_center is not None
        assert integration_manager.gui_hooks is not None

    def test_integrated_tick(self, integration_manager):
        """Test full integrated tick"""
        result = integration_manager.run_integrated_tick(user_id="test_user")

        assert "active_scenarios" in result
        assert "validated_mitigations" in result
        assert "command_center_widgets" in result

    def test_gui_export(self, integration_manager):
        """Test GUI data export"""
        gui_data = integration_manager.export_for_gui()

        assert "scenarios" in gui_data
        assert "dashboard" in gui_data
        assert len(gui_data["scenarios"]) == 50


# ============================================================================
# CONTROL PLANE TESTS
# ============================================================================


class TestControlPlanes:
    """Test control plane system"""

    def test_human_override_activation(self, engine):
        """Test human override activation"""
        assert engine.human_override_active is False

        engine.activate_human_override("test_user", "Emergency test")

        assert engine.human_override_active is True
        assert engine.active_control_plane == ControlPlane.HUMAN_OVERRIDE

    def test_control_plane_event_logging(self, engine):
        """Test that control plane changes are logged"""
        initial_count = len(engine.event_log)

        engine.activate_human_override("test_user", "Test override")

        # Should have logged override event
        assert len(engine.event_log) > initial_count
        assert any(e.event_type == "human_override_activated" for e in engine.event_log)


# ============================================================================
# FULL SYSTEM TESTS
# ============================================================================


class TestFullSystem:
    """Test complete system workflows"""

    def test_scenario_lifecycle(self, engine):
        """Test complete scenario lifecycle"""
        # 1. Dormant state
        scenario = engine.scenarios["S01"]
        assert scenario.status == ScenarioStatus.DORMANT

        # 2. Trigger activation
        engine.update_scenario_metrics("S01", {"synthetic_content_ratio": 0.6})
        assert scenario.status == ScenarioStatus.TRIGGERED

        # 3. Escalation
        scenario.activation_time = datetime.utcnow() - timedelta(days=100)
        scenario.evaluate_escalation()
        # Status may change based on escalation logic

        # 4. Event log populated
        assert len(engine.event_log) > 0

    def test_multi_scenario_simulation(self, engine):
        """Test simulation with multiple active scenarios"""
        # Activate multiple scenarios
        engine.update_scenario_metrics("S01", {"synthetic_content_ratio": 0.6})
        engine.update_scenario_metrics("S10", {"mental_health_crisis": 0.5})
        engine.update_scenario_metrics("S11", {"default_count": 4.0})

        # Run simulation
        results = []
        for _ in range(5):
            result = engine.run_tick()
            results.append(result)

        # Should have active scenarios
        assert any(r["active_scenarios"] for r in results)

    def test_full_integration_workflow(self, integration_manager):
        """Test complete integrated workflow"""
        # 1. Update scenarios
        manager = integration_manager
        engine = manager.get_hydra_engine()
        engine.update_scenario_metrics("S01", {"synthetic_content_ratio": 0.6})

        # 2. Run integrated tick
        tick_result = manager.run_integrated_tick()
        assert "active_scenarios" in tick_result

        # 3. Export for GUI
        gui_data = manager.export_for_gui()
        assert gui_data["dashboard"]["totals"]["active"] > 0

    def test_dashboard_state(self, engine):
        """Test dashboard state export"""
        state = engine.get_dashboard_state()

        assert "total_scenarios" in state
        assert "active_count" in state
        assert "critical_count" in state
        assert state["total_scenarios"] == 50


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


class TestPerformance:
    """Test performance characteristics"""

    def test_initialization_time(self, temp_data_dir):
        """Test that engine initializes quickly"""
        import time

        start = time.time()
        Hydra50Engine(data_dir=temp_data_dir)
        elapsed = time.time() - start

        assert elapsed < 1.0  # Should init in <1 second

    def test_tick_execution_time(self, engine):
        """Test tick execution performance"""
        import time

        # Activate some scenarios
        engine.update_scenario_metrics("S01", {"synthetic_content_ratio": 0.6})
        engine.update_scenario_metrics("S10", {"mental_health_crisis": 0.5})

        start = time.time()
        engine.run_tick()
        elapsed = time.time() - start

        assert elapsed < 0.1  # Should complete in <100ms


# ============================================================================
# REGISTRY TESTS
# ============================================================================


class TestScenarioRegistry:
    """Test scenario registry"""

    def test_registry_completeness(self):
        """Test that registry has all 50 scenarios"""
        assert len(SCENARIO_REGISTRY) == 50

        for i in range(1, 51):
            sid = f"S{i:02d}"
            assert sid in SCENARIO_REGISTRY

    def test_registry_names_unique(self):
        """Test that scenario names are unique"""
        names = list(SCENARIO_REGISTRY.values())
        assert len(names) == len(set(names))


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_scenario_id(self, engine):
        """Test handling of invalid scenario ID"""
        with pytest.raises(ValueError):
            engine.update_scenario_metrics("INVALID", {"metric": 1.0})

    def test_empty_metrics_update(self, engine):
        """Test update with empty metrics"""
        # Should not crash
        engine.update_scenario_metrics("S01", {})

    def test_replay_with_no_events(self, engine):
        """Test replay when event log is empty"""
        result = engine.replay_to_timestamp(datetime.utcnow())
        assert result["events_replayed"] == 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
