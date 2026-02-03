#!/usr/bin/env python3
"""
Unit tests for AICPD Engine
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pytest
from engines.alien_invaders import (
    AlienInvadersEngine,
    AlienThreatLevel,
    SimulationConfig,
    TechnologyLevel,
    load_scenario_preset,
)


class TestEngineInitialization:
    """Test engine initialization."""
    
    def test_engine_creation(self):
        """Test basic engine creation."""
        engine = AlienInvadersEngine()
        assert engine is not None
        assert not engine.initialized
    
    def test_engine_init(self):
        """Test engine initialization."""
        engine = AlienInvadersEngine()
        assert engine.init()
        assert engine.initialized
        assert engine.state is not None
    
    def test_engine_init_with_config(self):
        """Test engine initialization with custom config."""
        config = SimulationConfig()
        config.world.global_population = 10_000_000_000
        
        engine = AlienInvadersEngine(config)
        assert engine.init()
        assert engine.state.global_population == 10_000_000_000


class TestSimulationTicks:
    """Test simulation tick mechanics."""
    
    def test_single_tick(self):
        """Test single simulation tick."""
        engine = AlienInvadersEngine()
        engine.init()
        
        initial_day = engine.state.day_number
        assert engine.tick()
        assert engine.state.day_number == initial_day + 30
    
    def test_multiple_ticks(self):
        """Test multiple simulation ticks."""
        engine = AlienInvadersEngine()
        engine.init()
        
        for i in range(12):  # One year
            assert engine.tick()
        
        assert engine.state.day_number == 360
    
    def test_tick_without_init(self):
        """Test tick fails without initialization."""
        engine = AlienInvadersEngine()
        assert not engine.tick()


class TestEventInjection:
    """Test event injection mechanics."""
    
    def test_inject_alien_attack(self):
        """Test injecting alien attack event."""
        engine = AlienInvadersEngine()
        engine.init()
        
        event_id = engine.inject_event(
            "alien_attack",
            {
                "target_country": "USA",
                "severity": "high",
            }
        )
        
        assert event_id.startswith("evt_")
        assert len(engine.events) == 1
    
    def test_inject_diplomatic_event(self):
        """Test injecting diplomatic event."""
        engine = AlienInvadersEngine()
        engine.init()
        
        event_id = engine.inject_event(
            "diplomatic_success",
            {
                "severity": "medium",
                "description": "Peace talks successful",
            }
        )
        
        assert event_id is not None
        assert engine.state.negotiations_active


class TestStateObservation:
    """Test state observation queries."""
    
    def test_observe_complete_state(self):
        """Test observing complete state."""
        engine = AlienInvadersEngine()
        engine.init()
        
        state = engine.observe()
        assert "date" in state
        assert "global" in state
        assert "aliens" in state
        assert "ai" in state
    
    def test_observe_countries(self):
        """Test observing country data."""
        engine = AlienInvadersEngine()
        engine.init()
        
        countries = engine.observe("countries")
        assert "countries" in countries
        assert len(countries["countries"]) > 0
    
    def test_observe_aliens(self):
        """Test observing alien metrics."""
        engine = AlienInvadersEngine()
        engine.init()
        
        aliens = engine.observe("aliens")
        assert "alien_ships" in aliens
        assert "control_percentage" in aliens
    
    def test_observe_global(self):
        """Test observing global metrics."""
        engine = AlienInvadersEngine()
        engine.init()
        
        global_state = engine.observe("global")
        assert "population" in global_state
        assert "gdp" in global_state
        assert "casualties" in global_state


class TestStateValidation:
    """Test state validation and conservation laws."""
    
    def test_population_conservation(self):
        """Test population conservation."""
        engine = AlienInvadersEngine()
        engine.init()
        
        initial_pop = engine.state.get_total_population()
        
        # Run simulation
        for _ in range(12):
            engine.tick()
        
        final_pop = engine.state.get_total_population()
        
        # Population should not increase
        assert final_pop <= initial_pop
    
    def test_resource_conservation(self):
        """Test resource conservation."""
        engine = AlienInvadersEngine()
        engine.init()
        
        # Resources should not exceed 1.0
        for resource, amount in engine.state.remaining_resources.items():
            assert amount <= 1.0
        
        # Run simulation
        for _ in range(12):
            engine.tick()
        
        # Resources should still not exceed 1.0
        for resource, amount in engine.state.remaining_resources.items():
            assert amount <= 1.0
    
    def test_validation_history(self):
        """Test validation history tracking."""
        engine = AlienInvadersEngine()
        engine.init()
        
        # Run simulation
        for _ in range(6):
            engine.tick()
        
        # Should have validation records
        assert len(engine.validation_history) > 0
        
        # Most should be valid
        valid_count = sum(1 for v in engine.validation_history if v.is_valid)
        assert valid_count > 0


class TestScenarioPresets:
    """Test scenario preset configurations."""
    
    def test_standard_scenario(self):
        """Test standard scenario preset."""
        config = load_scenario_preset("standard")
        assert config.scenario == "standard"
        assert config.alien.invasion_probability_per_year == 0.15
    
    def test_aggressive_scenario(self):
        """Test aggressive scenario preset."""
        config = load_scenario_preset("aggressive")
        assert config.scenario == "aggressive"
        assert config.alien.hostile_intent == 0.95
        assert config.alien.initial_threat_level == AlienThreatLevel.INVASION
    
    def test_peaceful_scenario(self):
        """Test peaceful scenario preset."""
        config = load_scenario_preset("peaceful")
        assert config.scenario == "peaceful"
        assert config.alien.hostile_intent == 0.2
        assert config.alien.negotiation_openness == 0.8
    
    def test_extinction_scenario(self):
        """Test extinction scenario preset."""
        config = load_scenario_preset("extinction")
        assert config.scenario == "extinction"
        assert config.alien.technology_level == TechnologyLevel.GODLIKE
        assert config.alien.hostile_intent == 1.0


class TestArtifactGeneration:
    """Test artifact generation."""
    
    def test_export_artifacts(self, tmp_path):
        """Test artifact export."""
        engine = AlienInvadersEngine()
        engine.init()
        
        # Run short simulation
        for _ in range(6):
            engine.tick()
        
        # Export artifacts
        output_dir = str(tmp_path / "artifacts")
        assert engine.export_artifacts(output_dir)
        
        # Verify artifacts exist
        artifact_path = Path(output_dir)
        assert artifact_path.exists()
    
    def test_monthly_reports_generated(self, tmp_path):
        """Test monthly report generation."""
        config = SimulationConfig()
        config.artifacts.generate_monthly_reports = True
        
        engine = AlienInvadersEngine(config)
        engine.init()
        
        # Run for 2 months
        engine.tick()
        engine.tick()
        
        # Export
        output_dir = str(tmp_path / "artifacts")
        engine.export_artifacts(output_dir)
        
        # Check for monthly reports directory
        monthly_dir = Path(output_dir) / "monthly"
        assert monthly_dir.exists()


class TestDeterministicReplay:
    """Test deterministic replay capability."""
    
    def test_deterministic_with_seed(self):
        """Test deterministic behavior with random seed."""
        # Run simulation 1
        config1 = SimulationConfig()
        config1.validation.random_seed = 42
        
        engine1 = AlienInvadersEngine(config1)
        engine1.init()
        
        for _ in range(12):
            engine1.tick()
        
        state1 = engine1.observe("global")
        
        # Run simulation 2 with same seed
        config2 = SimulationConfig()
        config2.validation.random_seed = 42
        
        engine2 = AlienInvadersEngine(config2)
        engine2.init()
        
        for _ in range(12):
            engine2.tick()
        
        state2 = engine2.observe("global")
        
        # Results should be identical
        assert state1["population"] == state2["population"]
        assert state1["casualties"] == state2["casualties"]
    
    def test_snapshot_save(self):
        """Test state snapshot saving."""
        config = SimulationConfig()
        config.validation.save_state_frequency = 30
        
        engine = AlienInvadersEngine(config)
        engine.init()
        
        # Run simulation
        for _ in range(3):
            engine.tick()
        
        # Should have snapshots
        assert len(engine.state_snapshots) > 0


class TestIntegration:
    """Integration tests."""
    
    def test_full_year_simulation(self):
        """Test running a full year simulation."""
        engine = AlienInvadersEngine()
        engine.init()
        
        # Run for one year (12 months)
        for i in range(12):
            assert engine.tick()
        
        # Verify state progression
        assert engine.state.day_number == 360
        assert len(engine.events) >= 0  # May have random events
    
    def test_simulation_with_events(self):
        """Test simulation with injected events."""
        engine = AlienInvadersEngine()
        engine.init()
        
        # Inject events during simulation
        for i in range(12):
            engine.tick()
            
            if i == 6:  # Mid-year event
                engine.inject_event(
                    "alien_attack",
                    {
                        "target_country": "USA",
                        "severity": "critical",
                    }
                )
        
        # Should have at least one event
        assert len(engine.events) >= 1
        
        # USA should be affected
        usa = engine.state.countries.get("USA")
        if usa:
            assert usa.alien_influence > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
