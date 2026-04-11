#!/usr/bin/env python3
"""
Test Suite for Atlas Omega Enhanced

Comprehensive tests for all components:
1. Neural Civilization Model
2. Monte Carlo Engine
3. Multi-Agent Simulator
4. Long-Term Forecasting
5. Visualization Engine
"""

import json
import sys
import unittest
from datetime import datetime
from pathlib import Path

import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from atlas_omega_enhanced import (
    Agent,
    AgentType,
    AtlasOmegaEnhanced,
    CivilizationState,
    CivilizationType,
    EnhancedMonteCarloEngine,
    LongTermForecastEngine,
    MultiAgentSimulator,
    NeuralCivilizationModel,
    SimulationConfig,
    VisualizationEngine,
)


class TestCivilizationState(unittest.TestCase):
    """Test CivilizationState data structure."""

    def test_state_creation(self):
        """Test creating a valid civilization state."""
        state = CivilizationState(
            timestamp=datetime.now(),
            timestep=0,
            year=2026,
            technological_level=0.5,
            economic_power=0.6,
            political_stability=0.7,
            social_cohesion=0.65,
            environmental_health=0.75,
            military_capacity=0.4,
            cultural_influence=0.5,
            knowledge_accumulation=0.55,
            population=0.65,
        )

        self.assertEqual(state.year, 2026)
        self.assertEqual(state.timestep, 0)
        self.assertEqual(state.technological_level, 0.5)

    def test_state_validation(self):
        """Test state validation."""
        state = CivilizationState(
            timestamp=datetime.now(),
            timestep=0,
            year=2026,
            technological_level=0.5,
            economic_power=0.6,
            political_stability=0.7,
            social_cohesion=0.65,
            environmental_health=0.75,
            military_capacity=0.4,
            cultural_influence=0.5,
            knowledge_accumulation=0.55,
            population=0.65,
        )

        valid, errors = state.validate()
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

    def test_state_hash(self):
        """Test state hash computation."""
        state = CivilizationState(
            timestamp=datetime.now(),
            timestep=0,
            year=2026,
            technological_level=0.5,
            economic_power=0.6,
            political_stability=0.7,
            social_cohesion=0.65,
            environmental_health=0.75,
            military_capacity=0.4,
            cultural_influence=0.5,
            knowledge_accumulation=0.55,
            population=0.65,
        )

        hash1 = state.compute_hash()
        self.assertIsNotNone(hash1)
        self.assertEqual(len(hash1), 64)  # SHA256 produces 64 hex characters


class TestNeuralCivilizationModel(unittest.TestCase):
    """Test Neural Civilization Model."""

    def test_model_initialization(self):
        """Test neural model initialization."""
        config = SimulationConfig(use_neural_network=True, hidden_layers=[32, 16])

        model = NeuralCivilizationModel(config)

        self.assertEqual(model.input_size, 9)
        self.assertEqual(model.output_size, 9)
        self.assertEqual(len(model.weights), 3)  # 2 hidden + 1 output

    def test_forward_pass(self):
        """Test forward propagation."""
        config = SimulationConfig(use_neural_network=True, hidden_layers=[32, 16])
        model = NeuralCivilizationModel(config)

        state_vector = np.array([0.5, 0.6, 0.7, 0.65, 0.75, 0.4, 0.5, 0.55, 0.65])

        output = model.forward(state_vector)

        self.assertEqual(output.shape, (9,))
        # All outputs should be in 0-1 range (sigmoid)
        self.assertTrue(np.all(output >= 0))
        self.assertTrue(np.all(output <= 1))

    def test_predict_next_state(self):
        """Test next state prediction."""
        config = SimulationConfig(use_neural_network=True)
        model = NeuralCivilizationModel(config)

        state = CivilizationState(
            timestamp=datetime.now(),
            timestep=0,
            year=2026,
            technological_level=0.5,
            economic_power=0.6,
            political_stability=0.7,
            social_cohesion=0.65,
            environmental_health=0.75,
            military_capacity=0.4,
            cultural_influence=0.5,
            knowledge_accumulation=0.55,
            population=0.65,
        )

        next_state_vector = model.predict_next_state(state)

        self.assertEqual(next_state_vector.shape, (9,))
        self.assertTrue(np.all(next_state_vector >= 0))
        self.assertTrue(np.all(next_state_vector <= 1))


class TestMonteCarloEngine(unittest.TestCase):
    """Test Monte Carlo simulation engine."""

    def test_engine_initialization(self):
        """Test Monte Carlo engine initialization."""
        config = SimulationConfig(
            seed="0xTEST", start_year=2026, end_year=2126, n_monte_carlo_runs=10
        )

        engine = EnhancedMonteCarloEngine(config)

        self.assertEqual(len(engine.runs), 0)
        self.assertEqual(len(engine.run_metadata), 0)

    def test_single_simulation(self):
        """Test running a single simulation."""
        config = SimulationConfig(
            seed="0xTEST",
            start_year=2026,
            end_year=2076,  # 50 years
            n_monte_carlo_runs=1,
            use_neural_network=False,
        )

        engine = EnhancedMonteCarloEngine(config)
        states = engine.run_single_simulation(run_id=0)

        self.assertGreater(len(states), 0)
        self.assertEqual(states[0].year, 2026)

    def test_multiple_simulations(self):
        """Test running multiple simulations."""
        config = SimulationConfig(
            seed="0xTEST",
            start_year=2026,
            end_year=2076,
            n_monte_carlo_runs=5,
            use_neural_network=False,
        )

        engine = EnhancedMonteCarloEngine(config)
        engine.run_all_simulations()

        self.assertEqual(len(engine.runs), 5)
        self.assertEqual(len(engine.run_metadata), 5)

    def test_outcome_analysis(self):
        """Test outcome analysis."""
        config = SimulationConfig(
            seed="0xTEST",
            start_year=2026,
            end_year=2076,
            n_monte_carlo_runs=10,
            use_neural_network=False,
        )

        engine = EnhancedMonteCarloEngine(config)
        engine.run_all_simulations()
        analysis = engine.analyze_outcomes()

        self.assertEqual(analysis["total_runs"], 10)
        self.assertIn("collapse_probability", analysis)
        self.assertIn("avg_kardashev", analysis)
        self.assertIn("kardashev_distribution", analysis)


class TestMultiAgentSimulator(unittest.TestCase):
    """Test Multi-Agent Simulator."""

    def test_simulator_initialization(self):
        """Test multi-agent simulator initialization."""
        config = SimulationConfig(
            n_agents_per_type={
                "government": 2,
                "corporation": 5,
                "civil_society": 3,
                "individual": 10,
                "ai_system": 1,
            }
        )

        simulator = MultiAgentSimulator(config)

        self.assertEqual(len(simulator.agents), 21)  # 2+5+3+10+1

    def test_agent_goals(self):
        """Test agent goal initialization."""
        config = SimulationConfig()
        simulator = MultiAgentSimulator(config)

        # Check that agents have goals
        for agent in simulator.agents:
            self.assertIsNotNone(agent.goals)
            self.assertGreater(len(agent.goals), 0)

    def test_interaction_simulation(self):
        """Test agent interaction simulation."""
        config = SimulationConfig()
        simulator = MultiAgentSimulator(config)

        state = CivilizationState(
            timestamp=datetime.now(),
            timestep=0,
            year=2026,
            technological_level=0.5,
            economic_power=0.6,
            political_stability=0.7,
            social_cohesion=0.65,
            environmental_health=0.75,
            military_capacity=0.4,
            cultural_influence=0.5,
            knowledge_accumulation=0.55,
            population=0.65,
        )

        # Select two agents
        agent1 = simulator.agents[0]
        agent2 = simulator.agents[1]

        interaction = simulator.simulate_interaction(agent1, agent2, state)

        self.assertIn("interaction_type", interaction)
        self.assertIn("cooperation_probability", interaction)
        self.assertIn("impact", interaction)


class TestLongTermForecastEngine(unittest.TestCase):
    """Test Long-Term Forecast Engine."""

    def test_engine_initialization(self):
        """Test forecast engine initialization."""
        config = SimulationConfig(
            n_monte_carlo_runs=5, start_year=2026, end_year=2126
        )

        engine = LongTermForecastEngine(config)

        self.assertIsNotNone(engine.neural_model)
        self.assertIsNotNone(engine.monte_carlo)
        self.assertIsNotNone(engine.multi_agent)

    def test_forecast_generation(self):
        """Test forecast generation."""
        config = SimulationConfig(
            seed="0xTEST",
            n_monte_carlo_runs=5,
            start_year=2026,
            end_year=2076,
            use_neural_network=False,
        )

        engine = LongTermForecastEngine(config)

        initial_state = CivilizationState(
            timestamp=datetime.now(),
            timestep=0,
            year=2026,
            technological_level=0.4,
            economic_power=0.5,
            political_stability=0.6,
            social_cohesion=0.6,
            environmental_health=0.7,
            military_capacity=0.3,
            cultural_influence=0.4,
            knowledge_accumulation=0.5,
            population=0.6,
        )

        forecast = engine.generate_forecast(initial_state, horizon_years=50)

        self.assertIn("analysis", forecast)
        self.assertIn("trajectories", forecast)
        self.assertIn("initial_state", forecast)


class TestVisualizationEngine(unittest.TestCase):
    """Test Visualization Engine."""

    def test_engine_initialization(self):
        """Test visualization engine initialization."""
        viz = VisualizationEngine(output_dir="test_output")

        self.assertTrue(viz.output_dir.exists())

    def test_dashboard_generation(self):
        """Test dashboard generation."""
        viz = VisualizationEngine(output_dir="test_output")

        # Create mock forecast data
        forecast = {
            "initial_state": {},
            "horizon_years": 100,
            "analysis": {
                "total_runs": 10,
                "collapse_probability": 0.15,
                "avg_final_year": 2126,
                "avg_kardashev": 1.5,
                "avg_sustainability": 0.6,
                "kardashev_distribution": {
                    "mean": 1.5,
                    "std": 0.3,
                    "min": 1.0,
                    "max": 2.0,
                    "percentiles": {"25": 1.3, "50": 1.5, "75": 1.7},
                },
            },
            "trajectories": {
                "p10": [
                    {"year": 2026, "tech_level": 0.4, "econ_power": 0.5, "kardashev": 1.0}
                ],
                "p50": [
                    {"year": 2026, "tech_level": 0.5, "econ_power": 0.6, "kardashev": 1.5}
                ],
                "p90": [
                    {"year": 2026, "tech_level": 0.6, "econ_power": 0.7, "kardashev": 2.0}
                ],
            },
            "generated_at": datetime.now().isoformat(),
        }

        dashboard_path = viz.generate_html_dashboard(forecast, "test_dashboard.html")

        self.assertTrue(Path(dashboard_path).exists())

    def test_data_export(self):
        """Test data export."""
        viz = VisualizationEngine(output_dir="test_output")

        forecast = {
            "analysis": {"total_runs": 10},
            "trajectories": {},
            "generated_at": datetime.now().isoformat(),
        }

        data_path = viz.export_data(forecast, "test_data.json")

        self.assertTrue(Path(data_path).exists())

        # Verify JSON is valid
        with open(data_path, "r") as f:
            loaded_data = json.load(f)
            self.assertEqual(loaded_data["analysis"]["total_runs"], 10)


class TestIntegration(unittest.TestCase):
    """Integration tests for full system."""

    def test_full_analysis(self):
        """Test full integrated analysis."""
        config = SimulationConfig(
            seed="0xINTEGRATION",
            start_year=2026,
            end_year=2076,
            n_monte_carlo_runs=5,
            use_neural_network=False,
            n_agents_per_type={
                "government": 2,
                "corporation": 5,
                "civil_society": 3,
                "individual": 10,
                "ai_system": 1,
            },
        )

        atlas = AtlasOmegaEnhanced(config)

        initial_state = CivilizationState(
            timestamp=datetime.now(),
            timestep=0,
            year=2026,
            technological_level=0.4,
            economic_power=0.5,
            political_stability=0.6,
            social_cohesion=0.6,
            environmental_health=0.7,
            military_capacity=0.3,
            cultural_influence=0.4,
            knowledge_accumulation=0.5,
            population=0.6,
        )

        results = atlas.run_full_analysis(initial_state, horizon_years=50)

        self.assertIn("forecast", results)
        self.assertIn("dashboard_path", results)
        self.assertIn("data_path", results)

        # Verify files exist
        self.assertTrue(Path(results["dashboard_path"]).exists())
        self.assertTrue(Path(results["data_path"]).exists())


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCivilizationState))
    suite.addTests(loader.loadTestsFromTestCase(TestNeuralCivilizationModel))
    suite.addTests(loader.loadTestsFromTestCase(TestMonteCarloEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiAgentSimulator))
    suite.addTests(loader.loadTestsFromTestCase(TestLongTermForecastEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestVisualizationEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
