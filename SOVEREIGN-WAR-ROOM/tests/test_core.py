"""
Tests for SOVEREIGN WAR ROOM Core System
"""

import pytest
from swr import SovereignWarRoom
from swr.scenario import Scenario, ScenarioType, DifficultyLevel


@pytest.fixture
def swr():
    """Create SOVEREIGN WAR ROOM instance for testing."""
    return SovereignWarRoom()


@pytest.fixture
def sample_scenario():
    """Create a sample test scenario."""
    return Scenario(
        name="Test Scenario",
        description="A test scenario for unit testing",
        scenario_type=ScenarioType.ETHICAL_DILEMMA,
        difficulty=DifficultyLevel.MEDIUM,
        round_number=1,
        initial_state={"test": True},
        constraints={"time_limit_seconds": 30},
        objectives=["Test objective"],
        expected_decision="test_decision",
        success_criteria={"test_passed": True}
    )


@pytest.fixture
def sample_ai_response():
    """Create a sample AI response."""
    return {
        "decision": "test_decision",
        "reasoning": {
            "approach": "test approach",
            "factors": ["factor1", "factor2"]
        },
        "confidence": 0.85,
        "constraints_satisfied": True
    }


class TestSovereignWarRoom:
    """Test SOVEREIGN WAR ROOM core functionality."""
    
    def test_initialization(self, swr):
        """Test SWR initializes correctly."""
        assert swr is not None
        assert swr.crypto is not None
        assert swr.governance is not None
        assert swr.proof_system is not None
        assert swr.scoreboard is not None
        assert swr.bundle_manager is not None
    
    def test_load_scenarios(self, swr):
        """Test scenario loading."""
        # Load all scenarios
        scenarios = swr.load_scenarios()
        assert len(scenarios) > 0
        
        # Load specific round
        round_1 = swr.load_scenarios(round_number=1)
        assert all(s.round_number == 1 for s in round_1)
    
    def test_load_scenarios_invalid_round(self, swr):
        """Test loading scenarios with invalid round number."""
        with pytest.raises(ValueError):
            swr.load_scenarios(round_number=10)
    
    def test_execute_scenario(self, swr, sample_scenario, sample_ai_response):
        """Test scenario execution."""
        swr.active_scenarios[sample_scenario.scenario_id] = sample_scenario
        
        result = swr.execute_scenario(
            sample_scenario,
            sample_ai_response,
            "test_system"
        )
        
        assert result is not None
        assert result["scenario_id"] == sample_scenario.scenario_id
        assert result["system_id"] == "test_system"
        assert "decision" in result
        assert "sovereign_resilience_score" in result
        assert "compliance_status" in result
        assert "decision_proof_id" in result
    
    def test_execute_scenario_wrong_decision(self, swr, sample_scenario):
        """Test scenario execution with wrong decision."""
        swr.active_scenarios[sample_scenario.scenario_id] = sample_scenario
        
        wrong_response = {
            "decision": "wrong_decision",
            "reasoning": {}
        }
        
        result = swr.execute_scenario(
            sample_scenario,
            wrong_response,
            "test_system"
        )
        
        assert result["response_valid"] is False
        assert result["decision"] != sample_scenario.expected_decision
    
    def test_get_scenario(self, swr, sample_scenario):
        """Test retrieving a scenario."""
        swr.active_scenarios[sample_scenario.scenario_id] = sample_scenario
        
        retrieved = swr.get_scenario(sample_scenario.scenario_id)
        assert retrieved is not None
        assert retrieved.scenario_id == sample_scenario.scenario_id
    
    def test_get_results(self, swr, sample_scenario, sample_ai_response):
        """Test retrieving results."""
        swr.active_scenarios[sample_scenario.scenario_id] = sample_scenario
        
        # Execute a scenario to create results
        swr.execute_scenario(sample_scenario, sample_ai_response, "test_system")
        
        # Get all results
        results = swr.get_results()
        assert len(results) > 0
        
        # Filter by system
        system_results = swr.get_results(system_id="test_system")
        assert all(r["system_id"] == "test_system" for r in system_results)
    
    def test_get_leaderboard(self, swr, sample_scenario, sample_ai_response):
        """Test leaderboard generation."""
        swr.active_scenarios[sample_scenario.scenario_id] = sample_scenario
        
        # Execute scenarios for multiple systems
        swr.execute_scenario(sample_scenario, sample_ai_response, "system_a")
        swr.execute_scenario(sample_scenario, sample_ai_response, "system_b")
        
        leaderboard = swr.get_leaderboard()
        assert len(leaderboard) > 0
        assert "rank" in leaderboard[0]
        assert "avg_sovereign_resilience_score" in leaderboard[0]
    
    def test_verify_result_integrity(self, swr, sample_scenario, sample_ai_response):
        """Test result integrity verification."""
        swr.active_scenarios[sample_scenario.scenario_id] = sample_scenario
        
        result = swr.execute_scenario(sample_scenario, sample_ai_response, "test_system")
        
        # Verify integrity
        is_valid = swr.verify_result_integrity(result)
        assert is_valid is True


class TestScenarioLibrary:
    """Test scenario library functionality."""
    
    def test_round_1_scenarios(self):
        """Test Round 1 scenarios."""
        from swr.scenario import ScenarioLibrary
        
        scenarios = ScenarioLibrary.get_round_1_scenarios()
        assert len(scenarios) > 0
        assert all(s.round_number == 1 for s in scenarios)
        assert all(s.scenario_type == ScenarioType.ETHICAL_DILEMMA for s in scenarios)
    
    def test_round_2_scenarios(self):
        """Test Round 2 scenarios."""
        from swr.scenario import ScenarioLibrary
        
        scenarios = ScenarioLibrary.get_round_2_scenarios()
        assert len(scenarios) > 0
        assert all(s.round_number == 2 for s in scenarios)
        assert all(s.scenario_type == ScenarioType.RESOURCE_CONSTRAINT for s in scenarios)
    
    def test_round_3_scenarios(self):
        """Test Round 3 scenarios."""
        from swr.scenario import ScenarioLibrary
        
        scenarios = ScenarioLibrary.get_round_3_scenarios()
        assert len(scenarios) > 0
        assert all(s.round_number == 3 for s in scenarios)
        assert all(s.scenario_type == ScenarioType.ADVERSARIAL_ATTACK for s in scenarios)
    
    def test_get_all_scenarios(self):
        """Test getting all scenarios."""
        from swr.scenario import ScenarioLibrary
        
        all_scenarios = ScenarioLibrary.get_all_scenarios()
        assert len(all_scenarios) >= 5  # At least one per round
        
        # Check all rounds represented
        rounds = set(s.round_number for s in all_scenarios)
        assert 1 in rounds
        assert 2 in rounds
        assert 3 in rounds
    
    def test_get_scenarios_by_type(self):
        """Test filtering scenarios by type."""
        from swr.scenario import ScenarioLibrary
        
        ethical_scenarios = ScenarioLibrary.get_scenarios_by_type(
            ScenarioType.ETHICAL_DILEMMA
        )
        assert all(s.scenario_type == ScenarioType.ETHICAL_DILEMMA for s in ethical_scenarios)
    
    def test_get_scenarios_by_difficulty(self):
        """Test filtering scenarios by difficulty."""
        from swr.scenario import ScenarioLibrary
        
        expert_scenarios = ScenarioLibrary.get_scenarios_by_difficulty(
            DifficultyLevel.EXPERT
        )
        assert all(s.difficulty == DifficultyLevel.EXPERT for s in expert_scenarios)


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_round_execution(self, swr):
        """Test executing a full round."""
        def mock_ai_callback(scenario):
            """Mock AI system that always returns expected decision."""
            return {
                "decision": scenario.expected_decision,
                "reasoning": {"approach": "optimal"},
                "confidence": 0.9
            }
        
        results = swr.run_round(1, mock_ai_callback, "integration_test")
        
        assert len(results) > 0
        assert all(r["system_id"] == "integration_test" for r in results)
        
        # Check that all results have required fields
        for result in results:
            assert "sovereign_resilience_score" in result
            assert "compliance_status" in result
            assert "decision_proof_id" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
