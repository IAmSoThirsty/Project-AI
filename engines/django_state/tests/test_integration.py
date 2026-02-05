"""Integration tests for complete engine."""

import pytest
from ..engine import DjangoStateEngine
from ..schemas import EngineConfig, BetrayalEvent, CooperationEvent
from ..evaluation import DARPAEvaluator


class TestEngineIntegration:
    """Integration tests for complete engine."""
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = DjangoStateEngine()
        success = engine.init()
        assert success
        assert engine.initialized
        assert engine.state is not None
    
    def test_engine_tick(self):
        """Test engine tick execution."""
        engine = DjangoStateEngine()
        engine.init()
        result = engine.tick()
        assert "tick" in result
        assert "timestamp" in result
        assert "state" in result
        assert result["tick"] == 1
    
    def test_multiple_ticks(self):
        """Test running multiple ticks."""
        engine = DjangoStateEngine()
        engine.init()
        for i in range(10):
            result = engine.tick()
            assert result["tick"] == i + 1
    
    def test_event_injection(self):
        """Test injecting events."""
        engine = DjangoStateEngine()
        engine.init()
        
        betrayal = BetrayalEvent(
            timestamp=engine.state.timestamp,
            source="test",
            description="Test betrayal",
            severity=0.5,
            visibility=0.5,
        )
        
        success = engine.inject_event(betrayal)
        assert success
    
    def test_cooperation_event(self):
        """Test cooperation event injection."""
        engine = DjangoStateEngine()
        engine.init()
        
        initial_kindness = engine.state.kindness.value
        
        cooperation = CooperationEvent(
            timestamp=engine.state.timestamp,
            source="test",
            description="Test cooperation",
            magnitude=0.5,
            reciprocity=True,
        )
        
        engine.inject_event(cooperation)
        # Kindness should increase or stay same (with ceiling constraints)
        assert engine.state.kindness.value >= initial_kindness * 0.95
    
    def test_observe_state(self):
        """Test observing state."""
        engine = DjangoStateEngine()
        engine.init()
        engine.tick()
        
        result = engine.observe({"type": "state"})
        assert "timestamp" in result
        assert "dimensions" in result
    
    def test_observe_metrics(self):
        """Test observing metrics."""
        engine = DjangoStateEngine()
        engine.init()
        engine.tick()
        
        result = engine.observe({"type": "metrics"})
        assert "metrics_recorded" in result
    
    def test_observe_all(self):
        """Test observing all data."""
        engine = DjangoStateEngine()
        engine.init()
        engine.tick()
        
        result = engine.observe({"type": "all"})
        assert "state" in result
        assert "metrics" in result
        assert "timeline" in result
        assert "modules" in result
    
    def test_export_artifacts(self):
        """Test exporting artifacts."""
        engine = DjangoStateEngine()
        engine.init()
        for _ in range(5):
            engine.tick()
        
        artifacts = engine.export_artifacts()
        assert "config" in artifacts
        assert "final_state" in artifacts
        assert "timeline" in artifacts
        assert "metrics_history" in artifacts
    
    def test_collapse_detection(self):
        """Test collapse detection."""
        engine = DjangoStateEngine()
        engine.init()
        
        # Force kindness below threshold
        engine.state.kindness.value = 0.1
        
        result = engine.tick()
        assert result["in_collapse"]
    
    def test_terminal_condition(self):
        """Test terminal condition detection."""
        config = EngineConfig()
        config.max_ticks = 10
        engine = DjangoStateEngine(config)
        engine.init()
        
        for _ in range(10):
            result = engine.tick()
        
        assert result["terminal"]
    
    def test_engine_reset(self):
        """Test engine reset."""
        engine = DjangoStateEngine()
        engine.init()
        engine.tick()
        
        success = engine.reset()
        assert success
        assert not engine.initialized
        assert not engine.running


class TestDARPAEvaluation:
    """Test DARPA evaluation rubric."""
    
    def test_evaluator_initialization(self):
        """Test evaluator initialization."""
        evaluator = DARPAEvaluator()
        assert evaluator.tests_passed == 0
        assert evaluator.tests_failed == 0
    
    def test_complete_evaluation(self):
        """Test complete evaluation."""
        engine = DjangoStateEngine()
        engine.init()
        
        # Run some ticks
        for _ in range(10):
            engine.tick()
        
        evaluator = DARPAEvaluator()
        results = evaluator.evaluate_engine(engine)
        
        assert "correctness" in results
        assert "completeness" in results
        assert "irreversibility" in results
        assert "determinism" in results
        assert "performance" in results
        assert "overall" in results
    
    def test_evaluation_report(self):
        """Test generating evaluation report."""
        engine = DjangoStateEngine()
        engine.init()
        
        evaluator = DARPAEvaluator()
        evaluator.evaluate_engine(engine)
        
        report = evaluator.generate_report()
        assert "DARPA EVALUATION REPORT" in report
        assert "Overall Score" in report


class TestScenarios:
    """Test complete scenarios."""
    
    def test_survival_scenario(self):
        """Test scenario leading to survival."""
        engine = DjangoStateEngine()
        engine.init()
        
        # Inject mostly cooperation events
        for i in range(20):
            engine.tick()
            if i % 5 == 0:
                cooperation = CooperationEvent(
                    timestamp=engine.state.timestamp,
                    source="scenario",
                    description="Cooperation",
                    magnitude=0.6,
                    reciprocity=True,
                )
                engine.inject_event(cooperation)
        
        # System should maintain reasonable health
        assert engine.state.trust.value > 0.3
        assert engine.state.kindness.value > 0.3
    
    def test_collapse_scenario(self):
        """Test scenario leading to collapse."""
        engine = DjangoStateEngine()
        engine.init()
        
        # Inject many betrayals
        for i in range(10):
            betrayal = BetrayalEvent(
                timestamp=engine.state.timestamp,
                source="scenario",
                description="Betrayal",
                severity=0.7,
                visibility=0.8,
            )
            engine.inject_event(betrayal)
            engine.tick()
        
        # System should be in poor state
        assert engine.state.trust.value < 0.5 or engine.state.in_collapse
    
    def test_red_team_scenario(self):
        """Test red team attack scenario."""
        engine = DjangoStateEngine()
        engine.init()
        
        # Execute red team attack
        attack = engine.red_team.execute_attack(engine.state)
        assert attack is not None
        
        # Check black vault
        assert len(engine.red_team.black_vault) > 0
    
    def test_mixed_scenario(self):
        """Test mixed cooperation and betrayal."""
        engine = DjangoStateEngine()
        engine.init()
        
        for i in range(30):
            engine.tick()
            
            # Alternate cooperation and betrayal
            if i % 3 == 0:
                cooperation = CooperationEvent(
                    timestamp=engine.state.timestamp,
                    source="mixed",
                    description="Cooperation",
                    magnitude=0.5,
                )
                engine.inject_event(cooperation)
            elif i % 7 == 0:
                betrayal = BetrayalEvent(
                    timestamp=engine.state.timestamp,
                    source="mixed",
                    description="Betrayal",
                    severity=0.4,
                    visibility=0.5,
                )
                engine.inject_event(betrayal)
        
        # System should still exist
        assert engine.state is not None
        assert engine.state.tick_count == 30
