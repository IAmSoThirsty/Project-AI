"""
Contrarian Firewall - Comprehensive Unit Tests

Tests for the complete monolithic firewall system including:
- Orchestrator core functionality
- Thirsty-lang security bridge
- Swarm defense integration
- Governance integration
- Intent tracking
- Telemetry and auto-tuning
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.app.security.contrarian_firewall_orchestrator import (
    ContrariaNFirewallOrchestrator,
    OrchestratorConfig,
    FirewallMode,
    StabilityLevel,
    ThreatIntelSource,
    SystemTelemetry,
    IntentRecord,
    reset_orchestrator,
    get_orchestrator,
)

from integrations.thirsty_lang_security import (
    ThirstyLangSecurityBridge,
    SecurityConfig,
    OperationMode,
    ThreatBoxType,
)


class TestOrchestratorCore:
    """Test core orchestrator functionality"""
    
    @pytest.fixture
    def config(self):
        return OrchestratorConfig(
            mode=FirewallMode.ADAPTIVE,
            auto_tune_enabled=False,  # Disable for predictable tests
            real_time_adaptation=False,  # Disable background tasks
            governance_integration=False,  # Simplify for unit tests
            agent_coordination=False,
        )
    
    @pytest.fixture
    def orchestrator(self, config):
        reset_orchestrator()
        orch = ContrariaNFirewallOrchestrator(config)
        yield orch
        reset_orchestrator()
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly"""
        assert orchestrator is not None
        assert orchestrator.config.mode == FirewallMode.ADAPTIVE
        assert not orchestrator.running
        assert orchestrator.swarm_defense is not None
        assert orchestrator.security_bridge is not None
    
    def test_orchestrator_singleton(self, config):
        """Test orchestrator singleton pattern"""
        reset_orchestrator()
        orch1 = get_orchestrator(config)
        orch2 = get_orchestrator()
        assert orch1 is orch2
    
    @pytest.mark.asyncio
    async def test_orchestrator_start_stop(self, orchestrator):
        """Test orchestrator lifecycle"""
        assert not orchestrator.running
        
        await orchestrator.start()
        assert orchestrator.running
        
        await orchestrator.stop()
        assert not orchestrator.running
    
    def test_process_violation_basic(self, orchestrator):
        """Test basic violation processing"""
        result = orchestrator.process_violation(
            source_ip="192.168.1.100",
            violation_type="test_violation",
            details={"test": True}
        )
        
        assert result["attacker_ip"] == "192.168.1.100"
        assert result["threat_level"] in ["scout", "probe", "attack", "siege", "swarm"]
        assert "intent_id" in result
        assert "orchestration" in result
    
    def test_intent_tracking(self, orchestrator):
        """Test intent tracking functionality"""
        intent = orchestrator._track_intent(
            intent_type="test_intent",
            actor="test_user",
            parameters={"key": "value"},
            threat_score=0.5,
        )
        
        assert intent.intent_id in orchestrator.intent_tracker
        assert intent.intent_type == "test_intent"
        assert intent.actor == "test_user"
        assert intent.threat_score == 0.5
    
    def test_threat_intelligence_update(self, orchestrator):
        """Test threat intelligence updates"""
        orchestrator._update_threat_intelligence(
            ThreatIntelSource.SWARM_DEFENSE,
            "attacker1",
            {"threat_level": "high"}
        )
        
        assert ThreatIntelSource.SWARM_DEFENSE in orchestrator.threat_intelligence
        assert "attacker1" in orchestrator.threat_intelligence[ThreatIntelSource.SWARM_DEFENSE]


class TestThreatEscalation:
    """Test threat escalation levels"""
    
    @pytest.fixture
    def orchestrator(self):
        reset_orchestrator()
        config = OrchestratorConfig(
            auto_tune_enabled=False,
            real_time_adaptation=False,
            governance_integration=False,
            agent_coordination=False,
        )
        orch = ContrariaNFirewallOrchestrator(config)
        yield orch
        reset_orchestrator()
    
    def test_scout_level(self, orchestrator):
        """Test SCOUT threat level (1-2 violations)"""
        result = orchestrator.process_violation(
            source_ip="scout.test",
            violation_type="minor_violation",
            details={}
        )
        
        assert result["threat_level"] == "scout"
        assert result["violation_count"] == 1
        assert not result["swarm_active"]
    
    def test_probe_level(self, orchestrator):
        """Test PROBE threat level (3-5 violations)"""
        for i in range(3):
            result = orchestrator.process_violation(
                source_ip="probe.test",
                violation_type=f"violation_{i}",
                details={}
            )
        
        assert result["threat_level"] == "probe"
        assert result["violation_count"] == 3
    
    def test_attack_level(self, orchestrator):
        """Test ATTACK threat level (6-10 violations)"""
        for i in range(7):
            result = orchestrator.process_violation(
                source_ip="attack.test",
                violation_type=f"violation_{i}",
                details={}
            )
        
        assert result["threat_level"] == "attack"
        assert result["violation_count"] == 7
    
    def test_swarm_level(self, orchestrator):
        """Test SWARM threat level (21+ violations)"""
        for i in range(25):
            result = orchestrator.process_violation(
                source_ip="swarm.test",
                violation_type=f"violation_{i}",
                details={}
            )
        
        assert result["threat_level"] == "swarm"
        assert result["violation_count"] == 25
        assert result["swarm_active"]
        assert result["cognitive_overload"] > 0


class TestThirstyLangBridge:
    """Test Thirsty-lang security bridge"""
    
    @pytest.fixture
    def bridge(self):
        config = SecurityConfig(
            mode=OperationMode.HYBRID,
            enable_morphing=True,
            enable_compilation=True,
        )
        return ThirstyLangSecurityBridge(config)
    
    def test_bridge_initialization(self, bridge):
        """Test bridge initializes correctly"""
        assert bridge is not None
        assert bridge.threat_detector is not None
        assert bridge.code_morpher is not None
        assert bridge.defensive_compiler is not None
        assert bridge.policy_engine is not None
    
    def test_analyze_code_basic(self, bridge):
        """Test basic code analysis"""
        code = "print('hello')"
        result = bridge.analyze_code(code)
        
        assert "threats" in result
        assert "risk_score" in result
        assert "recommendations" in result
        assert result["mode"] == "hybrid"
    
    def test_analyze_code_with_threats(self, bridge):
        """Test code analysis detects threats"""
        code = "eval(user_input)"
        result = bridge.analyze_code(code)
        
        assert len(result["threats"]) > 0
        assert result["risk_score"] > 0
    
    def test_code_morphing(self, bridge):
        """Test code morphing functionality"""
        code = "def hello(): return 'world'"
        result = bridge.morph_code(code, strategy="defensive")
        
        assert "morphed_code" in result
        assert "transformations" in result
        assert result["strategy"] == "defensive"
    
    def test_defensive_compilation(self, bridge):
        """Test defensive compilation"""
        code = "x = input()"
        result = bridge.compile_defensive(code, mode="defensive", target="python")
        
        assert "compiled_code" in result
        assert "security_features" in result
        assert result["mode"] == "defensive"
    
    def test_policy_check(self, bridge):
        """Test policy checking"""
        result = bridge.check_policy(
            action="execute_code",
            context={"code": "print('hello')"}
        )
        
        assert "allowed" in result
        assert "verdict" in result
        assert "reason" in result


class TestAutoTuning:
    """Test auto-tuning functionality"""
    
    @pytest.fixture
    def orchestrator(self):
        reset_orchestrator()
        config = OrchestratorConfig(
            auto_tune_enabled=True,
            real_time_adaptation=False,  # Control manually for tests
            governance_integration=False,
        )
        orch = ContrariaNFirewallOrchestrator(config)
        yield orch
        reset_orchestrator()
    
    def test_feedback_for_tuning(self, orchestrator):
        """Test feedback collection for tuning"""
        initial_multiplier = orchestrator.tuning_parameters["chaos_multiplier"]
        
        # Simulate low cognitive overload
        swarm_result = {
            "cognitive_overload": 2.0,  # Below target of 8.0
            "threat_level": "probe",
        }
        
        orchestrator._feedback_for_tuning(swarm_result)
        
        # Should increase chaos multiplier
        assert orchestrator.tuning_parameters["chaos_multiplier"] > initial_multiplier
    
    def test_apply_tuning(self, orchestrator):
        """Test applying tuning parameters"""
        orchestrator.tuning_parameters["chaos_multiplier"] = 2.0
        orchestrator._apply_tuning()
        
        # Check swarm defense updated
        expected = 2.0 * orchestrator.config.decoy_expansion_rate
        assert orchestrator.swarm_defense.swarm_multiplier == expected


class TestTelemetryCollection:
    """Test telemetry collection"""
    
    @pytest.fixture
    def orchestrator(self):
        reset_orchestrator()
        config = OrchestratorConfig(
            auto_tune_enabled=False,
            real_time_adaptation=False,
            governance_integration=False,
        )
        orch = ContrariaNFirewallOrchestrator(config)
        yield orch
        reset_orchestrator()
    
    def test_telemetry_creation(self, orchestrator):
        """Test telemetry record creation"""
        telemetry = SystemTelemetry(
            timestamp=datetime.now(),
            threat_score=15.5,
            cognitive_overload_avg=3.2,
            active_violations=5,
            decoy_effectiveness=0.8,
            agent_activity={"agent1": 1},
            stability_level=0.5,
            auto_tuning_active=True,
        )
        
        orchestrator.telemetry_history.append(telemetry)
        
        assert len(orchestrator.telemetry_history) == 1
        assert orchestrator.telemetry_history[0].threat_score == 15.5
    
    def test_get_telemetry_summary(self, orchestrator):
        """Test telemetry summary generation"""
        # Add some telemetry
        for i in range(10):
            telemetry = SystemTelemetry(
                timestamp=datetime.now(),
                threat_score=float(i),
                cognitive_overload_avg=float(i) * 0.5,
                active_violations=i,
                decoy_effectiveness=0.8,
                agent_activity={},
                stability_level=0.5,
                auto_tuning_active=True,
            )
            orchestrator.telemetry_history.append(telemetry)
        
        summary = orchestrator.get_telemetry_summary(minutes=60)
        
        assert "avg_threat_score" in summary
        assert "avg_cognitive_overload" in summary
        assert summary["records"] == 10


class TestComprehensiveStatus:
    """Test comprehensive status reporting"""
    
    @pytest.fixture
    def orchestrator(self):
        reset_orchestrator()
        orch = ContrariaNFirewallOrchestrator()
        yield orch
        reset_orchestrator()
    
    def test_get_comprehensive_status(self, orchestrator):
        """Test comprehensive status retrieval"""
        status = orchestrator.get_comprehensive_status()
        
        assert "orchestrator" in status
        assert "subsystems" in status
        assert "tracking" in status
        assert "tuning" in status
        
        assert "running" in status["orchestrator"]
        assert "mode" in status["orchestrator"]
        assert "stability" in status["orchestrator"]
    
    def test_get_intent_history(self, orchestrator):
        """Test intent history retrieval"""
        # Add some intents
        for i in range(5):
            orchestrator._track_intent(
                intent_type=f"test_{i}",
                actor=f"user_{i}",
                parameters={},
                threat_score=float(i),
            )
        
        history = orchestrator.get_intent_history(limit=3)
        
        assert len(history) == 3
        assert all("intent_id" in item for item in history)


class TestIntegration:
    """Integration tests for full system"""
    
    @pytest.fixture
    def orchestrator(self):
        reset_orchestrator()
        config = OrchestratorConfig(
            governance_integration=False,  # Simplify for tests
            agent_coordination=False,
        )
        orch = ContrariaNFirewallOrchestrator(config)
        yield orch
        reset_orchestrator()
    
    def test_end_to_end_violation_flow(self, orchestrator):
        """Test complete violation processing flow"""
        # Process multiple violations from same attacker
        attacker_ip = "192.168.1.200"
        
        for i in range(10):
            result = orchestrator.process_violation(
                source_ip=attacker_ip,
                violation_type=f"violation_{i}",
                details={"index": i}
            )
        
        # Verify escalation
        assert result["violation_count"] == 10
        assert result["threat_level"] == "attack"
        
        # Verify intent tracking
        assert len(orchestrator.intent_tracker) == 10
        
        # Verify decoy deployment
        decoys = orchestrator.swarm_defense.get_decoy_recommendations(attacker_ip)
        assert len(decoys) > 0
    
    def test_multiple_attackers(self, orchestrator):
        """Test handling multiple concurrent attackers"""
        attackers = [f"192.168.1.{i}" for i in range(1, 6)]
        
        for attacker in attackers:
            for j in range(5):
                orchestrator.process_violation(
                    source_ip=attacker,
                    violation_type=f"violation_{j}",
                    details={}
                )
        
        # Check all tracked
        assert len(orchestrator.swarm_defense.attackers) == 5
        
        # Get comprehensive status
        status = orchestrator.get_comprehensive_status()
        assert status["subsystems"]["swarm_defense"]["total_attackers_tracked"] == 5


@pytest.mark.asyncio
class TestAsyncOperations:
    """Test async operations"""
    
    async def test_concurrent_violations(self):
        """Test handling concurrent violations"""
        reset_orchestrator()
        orchestrator = ContrariaNFirewallOrchestrator(
            OrchestratorConfig(
                governance_integration=False,
                agent_coordination=False,
            )
        )
        
        # Simulate concurrent violations
        async def process_violation(ip):
            return orchestrator.process_violation(
                source_ip=ip,
                violation_type="concurrent_test",
                details={}
            )
        
        # Process 10 concurrent violations
        tasks = [process_violation(f"10.0.0.{i}") for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert all("intent_id" in r for r in results)
        
        reset_orchestrator()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
