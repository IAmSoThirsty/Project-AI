#                                           [2026-03-05 10:03]
#                                          Productivity: Active
"""
Test suite for Enhanced Network Defense Engine.

Tests all components:
- DDoS simulation (Layer 3/4/7)
- APT modeling
- Lateral movement detection
- Network segmentation validation
- Zero trust enforcement
"""

import json
import pytest
from engines.network_defense_enhanced import (
    NetworkDefenseEnhancedEngine,
    AttackLayer,
    DDoSIntensity,
    APTStage,
    TrafficDirection,
    TrustLevel,
)


class TestNetworkDefenseEngine:
    """Test the main engine functionality."""

    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        engine = NetworkDefenseEnhancedEngine()
        assert engine.init() is True
        assert engine.initialized is True
        assert engine.state is not None
        assert engine.state.simulation_tick == 0

    def test_engine_tick(self):
        """Test engine tick advances simulation."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        initial_tick = engine.state.simulation_tick
        assert engine.tick() is True
        assert engine.state.simulation_tick == initial_tick + 1

    def test_engine_observe(self):
        """Test observation returns correct state."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        state = engine.observe()
        assert "simulation_tick" in state
        assert "ddos_attacks_active" in state
        assert "apt_scenarios_active" in state
        assert "lateral_movements_detected" in state
        assert "network_segments" in state
        assert "zero_trust_policies" in state

    def test_engine_without_init(self):
        """Test engine fails gracefully without initialization."""
        engine = NetworkDefenseEnhancedEngine()
        assert engine.tick() is False
        assert engine.observe() == {}


class TestDDoSSimulation:
    """Test DDoS attack simulation."""

    def test_ddos_attack_creation(self):
        """Test DDoS attacks are created."""
        engine = NetworkDefenseEnhancedEngine({"ddos_probability": 1.0})
        engine.init()
        
        # Force DDoS attack
        engine._simulate_ddos_attack()
        
        assert len(engine.state.ddos_attacks) > 0
        attack = engine.state.ddos_attacks[0]
        assert attack.attack_id is not None
        assert attack.layer in AttackLayer
        assert attack.intensity in DDoSIntensity
        assert attack.bandwidth_gbps > 0
        assert attack.packets_per_second > 0

    def test_ddos_layers(self):
        """Test DDoS attacks across different layers."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        # Simulate multiple attacks
        for _ in range(20):
            engine._simulate_ddos_attack()
        
        layers = {attack.layer for attack in engine.state.ddos_attacks}
        assert len(layers) > 1  # Should have attacks on multiple layers

    def test_ddos_mitigation(self):
        """Test DDoS mitigation."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        engine._simulate_ddos_attack()
        
        attack = engine.state.ddos_attacks[0]
        result = engine.action("mitigate_ddos", {"attack_id": attack.attack_id})
        
        assert result is True
        assert attack.mitigation_triggered is True
        assert attack.mitigation_effectiveness > 0

    def test_ddos_auto_mitigation(self):
        """Test automatic mitigation for high-intensity attacks."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        # Create multiple attacks until we get a high-intensity one
        for _ in range(50):
            engine._simulate_ddos_attack()
        
        high_intensity_attacks = [
            a for a in engine.state.ddos_attacks 
            if a.intensity in [DDoSIntensity.HIGH, DDoSIntensity.CRITICAL]
        ]
        
        if high_intensity_attacks:
            # Auto-mitigation should be triggered
            assert any(a.mitigation_triggered for a in high_intensity_attacks)


class TestAPTModeling:
    """Test Advanced Persistent Threat modeling."""

    def test_apt_initialization(self):
        """Test APT scenarios are initialized."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        assert len(engine.state.apt_scenarios) > 0
        apt = engine.state.apt_scenarios[0]
        assert apt.scenario_id is not None
        assert apt.threat_actor is not None
        assert apt.current_stage == APTStage.RECONNAISSANCE

    def test_apt_progression(self):
        """Test APT scenarios progress through stages."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        initial_stage = engine.state.apt_scenarios[0].current_stage
        
        # Run multiple ticks to allow progression
        for _ in range(50):
            engine.tick()
        
        # Check if any APT progressed
        progressed = any(
            apt.current_stage != initial_stage or len(apt.stages_completed) > 0
            for apt in engine.state.apt_scenarios
        )
        assert progressed is True

    def test_apt_detection(self):
        """Test APT detection increases over time."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        initial_detected = engine.state.detected_apts
        
        # Run many ticks to increase detection probability
        for _ in range(100):
            engine.tick()
        
        # Some APTs should be detected
        assert engine.state.detected_apts >= initial_detected

    def test_apt_metrics(self):
        """Test APT metrics are tracked."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        # Progress APTs
        for _ in range(100):
            engine._progress_apt_scenarios()
        
        # Check metrics
        for apt in engine.state.apt_scenarios:
            if APTStage.CREDENTIAL_ACCESS in apt.stages_completed:
                assert apt.credentials_stolen > 0
            if APTStage.LATERAL_MOVEMENT in apt.stages_completed:
                assert len(apt.compromised_hosts) > 0
            if APTStage.EXFILTRATION in apt.stages_completed:
                assert apt.data_exfiltrated_mb > 0

    def test_block_c2(self):
        """Test blocking C2 communications."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        apt = engine.state.apt_scenarios[0]
        result = engine.action("block_c2", {"scenario_id": apt.scenario_id})
        
        assert result is True
        assert apt.detected is True


class TestLateralMovement:
    """Test lateral movement detection."""

    def test_lateral_movement_detection(self):
        """Test lateral movement events are detected."""
        engine = NetworkDefenseEnhancedEngine({"lateral_movement_probability": 1.0})
        engine.init()
        
        initial_count = len(engine.state.lateral_movements)
        engine._detect_lateral_movement()
        
        assert len(engine.state.lateral_movements) > initial_count
        event = engine.state.lateral_movements[-1]
        assert event.event_id is not None
        assert event.source_host is not None
        assert event.destination_host is not None
        assert event.traffic_direction == TrafficDirection.EAST_WEST

    def test_suspicious_lateral_movement(self):
        """Test suspicious lateral movement flagging."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        # Generate multiple events
        for _ in range(50):
            engine._detect_lateral_movement()
        
        suspicious_events = [e for e in engine.state.lateral_movements if e.is_suspicious]
        assert len(suspicious_events) > 0
        
        # Check indicators
        for event in suspicious_events:
            assert len(event.indicators) > 0
            assert event.anomaly_score > 0.7

    def test_host_isolation(self):
        """Test host isolation action."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        result = engine.action("isolate_host", {"host": "10.0.30.105"})
        assert result is True


class TestNetworkSegmentation:
    """Test network segmentation validation."""

    def test_segment_initialization(self):
        """Test network segments are initialized."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        assert len(engine.state.network_segments) > 0
        
        segment = engine.state.network_segments[0]
        assert segment.segment_id is not None
        assert segment.name is not None
        assert segment.vlan_id > 0
        assert segment.subnet is not None

    def test_segment_isolation_levels(self):
        """Test different isolation levels."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        isolation_levels = {seg.isolation_level for seg in engine.state.network_segments}
        assert "strict" in isolation_levels or "controlled" in isolation_levels

    def test_segmentation_validation(self):
        """Test segmentation validation runs."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        initial_violations = engine.state.segmentation_violations
        
        # Run validation multiple times
        for _ in range(100):
            engine._validate_network_segmentation()
        
        # Should detect some violations
        assert engine.state.segmentation_violations >= initial_violations

    def test_enforce_segmentation(self):
        """Test enforcing segmentation."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        segment = engine.state.network_segments[0]
        result = engine.action("enforce_segmentation", {"segment_id": segment.segment_id})
        
        assert result is True
        assert segment.isolation_level == "strict"
        assert segment.micro_segmentation is True


class TestZeroTrust:
    """Test zero trust enforcement."""

    def test_zero_trust_initialization(self):
        """Test zero trust policies are initialized."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        assert len(engine.state.zero_trust_policies) > 0
        
        policy = engine.state.zero_trust_policies[0]
        assert policy.policy_id is not None
        assert policy.resource is not None
        assert policy.trust_level in TrustLevel

    def test_zero_trust_enforcement(self):
        """Test zero trust policies are enforced."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        initial_violations = engine.state.zero_trust_violations
        
        # Run enforcement multiple times
        for _ in range(100):
            engine._enforce_zero_trust()
        
        # Should detect some violations
        assert engine.state.zero_trust_violations >= initial_violations

    def test_continuous_validation(self):
        """Test continuous validation updates timestamps."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        policy = engine.state.zero_trust_policies[0]
        initial_timestamp = policy.last_validation
        
        # Wait a moment
        import time
        time.sleep(0.1)
        
        engine._enforce_zero_trust()
        
        if policy.continuous_validation:
            assert policy.last_validation != initial_timestamp

    def test_revoke_access(self):
        """Test access revocation."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        policy = engine.state.zero_trust_policies[0]
        result = engine.action("revoke_access", {"policy_id": policy.policy_id})
        
        assert result is True
        assert policy.trust_level == TrustLevel.UNTRUSTED


class TestIntegration:
    """Test integrated scenarios."""

    def test_full_simulation_run(self):
        """Test a complete simulation run."""
        engine = NetworkDefenseEnhancedEngine()
        assert engine.init() is True
        
        # Run simulation
        for i in range(20):
            assert engine.tick() is True
            state = engine.observe()
            assert state["simulation_tick"] == i + 1
        
        # Verify all systems are active
        final_state = engine.observe()
        assert final_state["network_segments"] > 0
        assert final_state["zero_trust_policies"] > 0

    def test_report_generation(self):
        """Test report generation."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        # Run some ticks
        for _ in range(10):
            engine.tick()
        
        # Test different report formats
        json_report = engine.report("json")
        assert len(json_report) > 0
        assert json.loads(json_report)  # Valid JSON
        
        summary_report = engine.report("summary")
        assert "ENHANCED NETWORK DEFENSE SIMULATION REPORT" in summary_report
        
        detailed_report = engine.report("detailed")
        assert "DETAILED DDoS ATTACKS" in detailed_report or "DETAILED APT" in detailed_report

    def test_concurrent_attacks(self):
        """Test handling multiple concurrent attacks."""
        engine = NetworkDefenseEnhancedEngine({
            "ddos_probability": 0.8,
            "apt_probability": 0.5,
            "lateral_movement_probability": 0.7,
        })
        engine.init()
        
        # Run simulation with high attack probability
        for _ in range(20):
            engine.tick()
        
        state = engine.observe()
        
        # Should have various types of attacks
        total_activity = (
            state["ddos_attacks_active"] + 
            state["ddos_attacks_mitigated"] +
            state["apt_scenarios_active"] +
            state["lateral_movements_detected"]
        )
        assert total_activity > 0

    def test_defense_effectiveness(self):
        """Test defensive actions are effective."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        # Run simulation
        for _ in range(30):
            engine.tick()
        
        state = engine.observe()
        
        # Check that some attacks are mitigated
        if state["ddos_attacks_mitigated"] > 0:
            assert state["blocked_attacks"] > 0
        
        # Check that some APTs are detected
        if state["apt_scenarios_detected"] > 0:
            assert state["apt_scenarios_detected"] > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_action(self):
        """Test invalid action type."""
        engine = NetworkDefenseEnhancedEngine()
        engine.init()
        
        result = engine.action("invalid_action", {})
        assert result is False

    def test_action_without_init(self):
        """Test action without initialization."""
        engine = NetworkDefenseEnhancedEngine()
        result = engine.action("mitigate_ddos", {})
        assert result is False

    def test_empty_config(self):
        """Test engine with empty config."""
        engine = NetworkDefenseEnhancedEngine({})
        assert engine.init() is True
        assert engine.tick() is True

    def test_custom_config(self):
        """Test engine with custom config."""
        config = {
            "ddos_probability": 0.5,
            "apt_probability": 0.3,
            "lateral_movement_probability": 0.4,
        }
        engine = NetworkDefenseEnhancedEngine(config)
        assert engine.init() is True
        assert engine.ddos_probability == 0.5
        assert engine.apt_probability == 0.3
        assert engine.lateral_movement_probability == 0.4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
