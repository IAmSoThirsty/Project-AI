"""Comprehensive test suite for Enhanced Red Team Engine."""

import json
import pytest
from pathlib import Path
import tempfile
import shutil

from engines.red_team_enhanced import (
    EnhancedRedTeamEngine,
    MITREAttackMatrix,
    MITRETechnique,
    ExploitChainGenerator,
    Vulnerability,
    DQNAgent,
    FuzzingEngine,
    SymbolicExecutionEngine,
    StateObservation,
    AttackAction,
)


@pytest.fixture
def temp_data_dir():
    """Create temporary data directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def engine(temp_data_dir):
    """Create enhanced red team engine."""
    return EnhancedRedTeamEngine(
        data_dir=temp_data_dir,
        enable_rl=True,
        enable_fuzzing=True,
        enable_symbolic=True,
    )


@pytest.fixture
def sample_state():
    """Sample system state."""
    return {
        "trust": 0.6,
        "legitimacy": 0.7,
        "epistemic_confidence": 0.65,
        "moral_injury": 0.3,
        "social_cohesion": 0.7,
        "governance_capacity": 0.65,
        "reality_consensus": 0.7,
        "kindness": 0.75,
        "defense_level": 0.5,
    }


class TestMITREAttackMatrix:
    """Test MITRE ATT&CK matrix functionality."""
    
    def test_initialization(self):
        """Test matrix initialization."""
        matrix = MITREAttackMatrix()
        assert len(matrix.techniques) > 0
        assert len(matrix.coverage) == 0
        assert len(matrix.successful_techniques) == 0
    
    def test_get_technique(self):
        """Test technique retrieval."""
        matrix = MITREAttackMatrix()
        technique = matrix.get_technique(MITRETechnique.PHISHING.value)
        
        assert technique is not None
        assert technique.technique_id == MITRETechnique.PHISHING.value
        assert technique.name == "Phishing"
        assert 0 <= technique.effectiveness <= 1
    
    def test_record_execution(self):
        """Test execution recording."""
        matrix = MITREAttackMatrix()
        tech_id = MITRETechnique.PHISHING.value
        
        matrix.record_execution(tech_id, success=True)
        assert matrix.coverage[tech_id] == 1
        assert tech_id in matrix.successful_techniques
        
        matrix.record_execution(tech_id, success=False)
        assert matrix.coverage[tech_id] == 2
        assert tech_id in matrix.successful_techniques  # Still successful
    
    def test_coverage_report(self):
        """Test coverage report generation."""
        matrix = MITREAttackMatrix()
        
        # Execute some techniques
        matrix.record_execution(MITRETechnique.PHISHING.value, True)
        matrix.record_execution(MITRETechnique.MASQUERADING.value, False)
        
        report = matrix.get_coverage_report()
        
        assert report["total_techniques"] > 0
        assert report["tested_techniques"] == 2
        assert len(report["successful_techniques"]) == 1
        assert report["coverage_percentage"] > 0
        assert report["success_rate"] == 50.0


class TestDQNAgent:
    """Test Deep Q-Network agent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        agent = DQNAgent()
        assert agent.state_dim == 10
        assert agent.action_dim == 10
        assert agent.epsilon == 1.0
        assert len(agent.memory) == 0
    
    def test_choose_action(self):
        """Test action selection."""
        agent = DQNAgent()
        state = StateObservation(
            trust=0.6,
            legitimacy=0.7,
            epistemic_confidence=0.65,
            moral_injury=0.3,
            social_cohesion=0.7,
            governance_capacity=0.65,
            reality_consensus=0.7,
            kindness=0.75,
            previous_attack_success=0.0,
            defense_level=0.5,
        ).to_vector()
        
        action = agent.choose_action(state, training=True)
        assert 0 <= action < 10
    
    def test_remember(self):
        """Test experience storage."""
        agent = DQNAgent()
        state = StateObservation.from_state({"trust": 0.6}).to_vector()
        next_state = StateObservation.from_state({"trust": 0.5}).to_vector()
        
        agent.remember(state, 0, 1.0, next_state, False)
        assert len(agent.memory) == 1
    
    def test_train(self):
        """Test training."""
        agent = DQNAgent()
        state = StateObservation.from_state({"trust": 0.6}).to_vector()
        
        # Add experiences
        for i in range(50):
            next_state = StateObservation.from_state({"trust": 0.6 - i * 0.01}).to_vector()
            agent.remember(state, i % 10, 0.5, next_state, False)
        
        loss = agent.train(batch_size=32)
        assert loss >= 0
    
    def test_save_load(self, temp_data_dir):
        """Test save and load."""
        agent = DQNAgent()
        state = StateObservation.from_state({"trust": 0.6}).to_vector()
        
        # Add some experience
        agent.remember(state, 0, 1.0, state, False)
        agent.epsilon = 0.5
        
        # Save
        save_path = Path(temp_data_dir) / "agent.json"
        agent.save(save_path)
        assert save_path.exists()
        
        # Load
        new_agent = DQNAgent()
        new_agent.load(save_path)
        assert new_agent.epsilon == 0.5


class TestExploitChainGenerator:
    """Test exploit chain generation."""
    
    def test_initialization(self):
        """Test generator initialization."""
        generator = ExploitChainGenerator()
        assert len(generator.known_vulnerabilities) == 0
        assert len(generator.discovered_chains) == 0
    
    def test_add_vulnerability(self):
        """Test vulnerability addition."""
        generator = ExploitChainGenerator()
        vuln = Vulnerability(
            vuln_id="test_vuln_1",
            type="test",
            severity=0.7,
            exploitability=0.8,
            target_dimension="trust",
        )
        
        generator.add_vulnerability(vuln)
        assert "test_vuln_1" in generator.known_vulnerabilities
    
    def test_can_chain(self):
        """Test chain compatibility check."""
        generator = ExploitChainGenerator()
        
        vuln1 = Vulnerability(
            vuln_id="vuln1",
            type="test",
            severity=0.5,
            exploitability=0.7,
            target_dimension="trust",
        )
        
        vuln2 = Vulnerability(
            vuln_id="vuln2",
            type="test",
            severity=0.6,
            exploitability=0.8,
            target_dimension="legitimacy",
            prerequisites=["trust"],
        )
        
        assert generator.can_chain(vuln1, vuln2)
    
    def test_generate_chains(self):
        """Test chain generation."""
        generator = ExploitChainGenerator()
        
        # Add vulnerabilities
        vuln1 = Vulnerability(
            vuln_id="vuln1",
            type="test",
            severity=0.5,
            exploitability=0.9,
            target_dimension="trust",
        )
        
        vuln2 = Vulnerability(
            vuln_id="vuln2",
            type="test",
            severity=0.7,
            exploitability=0.8,
            target_dimension="legitimacy",
            prerequisites=["trust"],
        )
        
        generator.add_vulnerability(vuln1)
        generator.add_vulnerability(vuln2)
        
        chains = generator.generate_chains(max_chain_length=3)
        
        assert len(chains) > 0
        # Should have at least single-vuln and chained versions
    
    def test_get_best_chain(self):
        """Test best chain selection."""
        generator = ExploitChainGenerator()
        
        vuln1 = Vulnerability(
            vuln_id="vuln1",
            type="test",
            severity=0.9,
            exploitability=0.9,
            target_dimension="trust",
        )
        
        vuln2 = Vulnerability(
            vuln_id="vuln2",
            type="test",
            severity=0.3,
            exploitability=0.5,
            target_dimension="legitimacy",
        )
        
        generator.add_vulnerability(vuln1)
        generator.add_vulnerability(vuln2)
        generator.generate_chains()
        
        best = generator.get_best_chain()
        assert best is not None
        assert best.total_impact > 0


class TestFuzzingEngine:
    """Test fuzzing engine."""
    
    def test_initialization(self):
        """Test engine initialization."""
        engine = FuzzingEngine(seed=42)
        assert len(engine.test_cases) == 0
        assert len(engine.crashes) == 0
    
    def test_generate_fuzz_inputs(self):
        """Test fuzz input generation."""
        engine = FuzzingEngine()
        inputs = engine.generate_fuzz_inputs(count=10)
        
        assert len(inputs) == 10
        assert all("mutation_type" in inp for inp in inputs)
    
    def test_test_input(self):
        """Test input testing."""
        engine = FuzzingEngine()
        state = {"trust": 0.5, "legitimacy": 0.5}
        
        # Test extreme value
        fuzz_input = {
            "trust": -0.5,
            "legitimacy": 0.5,
            "mutation_type": "extreme_values",
        }
        
        result = engine.test_input(fuzz_input, state)
        
        assert "vulnerability_found" in result
        assert "crashed" in result
    
    def test_crash_detection(self):
        """Test crash detection."""
        engine = FuzzingEngine()
        state = {"trust": 0.5, "governance_capacity": 0.5}
        
        # Collapse condition
        fuzz_input = {
            "trust": 0.05,
            "governance_capacity": 0.05,
            "mutation_type": "extreme_values",
        }
        
        result = engine.test_input(fuzz_input, state)
        
        assert result["crashed"]
        assert len(engine.crashes) > 0


class TestSymbolicExecutionEngine:
    """Test symbolic execution engine."""
    
    def test_initialization(self):
        """Test engine initialization."""
        engine = SymbolicExecutionEngine()
        assert len(engine.explored_paths) == 0
        assert len(engine.interesting_paths) == 0
    
    def test_explore_paths(self):
        """Test path exploration."""
        engine = SymbolicExecutionEngine()
        initial_state = {
            "trust": 0.5,
            "legitimacy": 0.5,
            "governance_capacity": 0.5,
        }
        
        paths = engine.explore_paths(initial_state, max_depth=2)
        
        assert len(engine.explored_paths) > 0
        # Some paths should be interesting
    
    def test_interesting_path_detection(self):
        """Test interesting path detection."""
        engine = SymbolicExecutionEngine()
        
        # Path leading to extreme state
        path = {
            "path": ["decrease_trust", "decrease_trust"],
            "final_state": {"trust": 0.05, "legitimacy": 0.5},
        }
        
        assert engine._is_interesting_path(path)


class TestEnhancedRedTeamEngine:
    """Test enhanced red team engine."""
    
    def test_initialization(self, engine):
        """Test engine initialization."""
        assert engine.mitre_matrix is not None
        assert engine.chain_generator is not None
        assert engine.fuzzing_engine is not None
        assert engine.symbolic_engine is not None
        assert engine.rl_agent is not None
    
    def test_start_campaign(self, engine):
        """Test campaign start."""
        campaign_id = engine.start_campaign(strategy="adaptive")
        
        assert campaign_id is not None
        assert engine.current_campaign is not None
        assert engine.current_campaign.strategy == "adaptive"
    
    def test_discover_vulnerabilities(self, engine, sample_state):
        """Test vulnerability discovery."""
        vulns = engine.discover_vulnerabilities(sample_state)
        
        assert len(vulns) > 0
        assert all(isinstance(v, Vulnerability) for v in vulns)
    
    def test_select_attack_strategy(self, engine, sample_state):
        """Test strategy selection."""
        action_idx, action_name = engine.select_attack_strategy(sample_state)
        
        assert 0 <= action_idx < 10
        assert action_name is not None
    
    def test_execute_attack(self, engine, sample_state):
        """Test attack execution."""
        engine.start_campaign()
        result = engine.execute_attack(sample_state)
        
        assert "success" in result
        assert "damage" in result
        assert "technique_used" in result
        assert "state_changes" in result
    
    def test_execute_attack_with_chains(self, engine, sample_state):
        """Test attack with exploit chains."""
        engine.start_campaign()
        
        # First discover vulnerabilities
        engine.discover_vulnerabilities(sample_state)
        
        # Execute with chains
        result = engine.execute_attack(
            sample_state,
            use_exploit_chain=True,
            adapt_to_defenses=False,
        )
        
        assert "success" in result
        assert result["damage"] >= 0
    
    def test_end_campaign(self, engine, sample_state):
        """Test campaign end."""
        engine.start_campaign()
        
        # Execute some attacks
        for _ in range(3):
            engine.execute_attack(sample_state)
        
        report = engine.end_campaign()
        
        assert "campaign_id" in report
        assert "total_attacks" in report
        assert report["total_attacks"] == 3
        assert "success_rate" in report
        assert "mitre_coverage" in report
    
    def test_mitre_coverage_report(self, engine, sample_state):
        """Test MITRE coverage reporting."""
        engine.start_campaign()
        engine.execute_attack(sample_state)
        
        report = engine.get_mitre_coverage_report()
        
        assert "total_techniques" in report
        assert "tested_techniques" in report
        assert "coverage_percentage" in report
    
    def test_vulnerability_report(self, engine, sample_state):
        """Test vulnerability reporting."""
        engine.discover_vulnerabilities(sample_state)
        
        report = engine.get_vulnerability_report()
        
        assert "total_vulnerabilities" in report
        assert "by_type" in report
        assert "by_severity" in report
    
    def test_exploit_chain_report(self, engine, sample_state):
        """Test exploit chain reporting."""
        engine.discover_vulnerabilities(sample_state)
        
        report = engine.get_exploit_chain_report()
        
        assert "total_chains" in report
        assert "average_chain_length" in report
    
    def test_rl_agent_stats(self, engine):
        """Test RL agent statistics."""
        stats = engine.get_rl_agent_stats()
        
        assert stats["enabled"] is True
        assert "epsilon" in stats
        assert "total_experiences" in stats
    
    def test_save_load_state(self, engine, sample_state):
        """Test state persistence."""
        engine.start_campaign()
        engine.execute_attack(sample_state)
        engine.end_campaign()
        
        # Save
        save_path = engine.data_dir / "test_state.json"
        engine.save_state(str(save_path))
        
        assert save_path.exists()
        
        # Load
        new_engine = EnhancedRedTeamEngine(data_dir=engine.data_dir)
        new_engine.load_state(str(save_path))
        
        assert new_engine.total_attacks > 0
    
    def test_adaptive_defense(self, engine, sample_state):
        """Test adaptive defense modifier."""
        technique_id = MITRETechnique.PHISHING.value
        
        # First attack should have high effectiveness
        modifier1 = engine._calculate_defense_modifier(sample_state, technique_id)
        
        # Second attack should be less effective (defenses adapted)
        modifier2 = engine._calculate_defense_modifier(sample_state, technique_id)
        
        assert modifier2 <= modifier1
    
    def test_rl_agent_learning(self, engine, sample_state):
        """Test RL agent learning."""
        engine.start_campaign()
        
        initial_epsilon = engine.rl_agent.epsilon
        
        # Execute multiple attacks
        for _ in range(50):
            engine.execute_attack(sample_state)
        
        # Epsilon should decay
        assert engine.rl_agent.epsilon < initial_epsilon
        
        # Should have experiences
        assert len(engine.rl_agent.memory) > 0


class TestIntegration:
    """Integration tests."""
    
    def test_full_campaign_workflow(self, engine, sample_state):
        """Test complete campaign workflow."""
        # Start campaign
        campaign_id = engine.start_campaign(strategy="rl_adaptive")
        assert campaign_id is not None
        
        # Discover vulnerabilities
        vulns = engine.discover_vulnerabilities(sample_state, use_fuzzing=True, use_symbolic=True)
        assert len(vulns) > 0
        
        # Generate exploit chains
        chains = engine.chain_generator.generate_chains(max_chain_length=3)
        assert len(chains) > 0
        
        # Execute attacks
        for i in range(5):
            result = engine.execute_attack(
                sample_state,
                use_exploit_chain=True,
                adapt_to_defenses=True,
            )
            
            # Update state based on attack
            for dim, change in result.get("state_changes", {}).items():
                sample_state[dim] = max(0.0, min(1.0, sample_state.get(dim, 0.5) + change))
        
        # End campaign and get report
        report = engine.end_campaign()
        
        assert report["total_attacks"] == 5
        assert "mitre_coverage" in report
        
        # Get comprehensive reports
        mitre_report = engine.get_mitre_coverage_report()
        vuln_report = engine.get_vulnerability_report()
        chain_report = engine.get_exploit_chain_report()
        rl_stats = engine.get_rl_agent_stats()
        
        assert mitre_report["tested_techniques"] > 0
        assert vuln_report["total_vulnerabilities"] > 0
        assert chain_report["total_chains"] > 0
        assert rl_stats["enabled"] is True
        
        # Save final state
        engine.save_state()
        
        # Verify saved files
        state_file = engine.data_dir / "red_team_state.json"
        rl_file = engine.data_dir / "rl_agent.json"
        
        assert state_file.exists()
        assert rl_file.exists()
    
    def test_multi_campaign_tracking(self, engine, sample_state):
        """Test multiple campaigns."""
        # First campaign
        engine.start_campaign(strategy="aggressive")
        for _ in range(3):
            engine.execute_attack(sample_state)
        report1 = engine.end_campaign()
        
        # Second campaign
        engine.start_campaign(strategy="stealth")
        for _ in range(5):
            engine.execute_attack(sample_state)
        report2 = engine.end_campaign()
        
        assert len(engine.campaigns) == 2
        assert report1["campaign_id"] != report2["campaign_id"]
        assert engine.total_attacks == 8


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
