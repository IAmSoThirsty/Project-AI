"""Tests for Global Intelligence Library System."""

import tempfile
from pathlib import Path

import pytest

from app.core.global_intelligence_library import (
    ChangeLevel,
    DomainAnalysis,
    DomainOverseer,
    GlobalCurator,
    GlobalIntelligenceLibrary,
    GlobalTheory,
    IntelligenceAgent,
    IntelligenceDomain,
    IntelligenceReport,
    MonitoringStatus,
    generate_statistical_simulation,
    get_global_intelligence_library,
)


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton before and after each test."""
    GlobalIntelligenceLibrary.reset()
    yield
    GlobalIntelligenceLibrary.reset()


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestIntelligenceAgent:
    """Test IntelligenceAgent class."""

    def test_agent_initialization(self, temp_data_dir):
        """Test agent initialization."""
        agent = IntelligenceAgent(
            agent_id="test_agent_01",
            domain=IntelligenceDomain.ECONOMIC,
            specialty="stock_markets",
            data_dir=temp_data_dir,
        )

        assert agent.agent_id == "test_agent_01"
        assert agent.domain == IntelligenceDomain.ECONOMIC
        assert agent.specialty == "stock_markets"
        assert agent.status == MonitoringStatus.IDLE
        assert agent.report_count == 0

    def test_agent_monitor(self, temp_data_dir):
        """Test agent monitoring."""
        agent = IntelligenceAgent(
            agent_id="test_agent_02",
            domain=IntelligenceDomain.POLITICAL,
            specialty="elections",
            data_dir=temp_data_dir,
        )

        report = agent.monitor()

        assert isinstance(report, IntelligenceReport)
        assert report.agent_id == "test_agent_02"
        assert report.domain == IntelligenceDomain.POLITICAL
        assert agent.status == MonitoringStatus.ACTIVE
        assert agent.report_count == 1

    def test_agent_get_status(self, temp_data_dir):
        """Test agent status retrieval."""
        agent = IntelligenceAgent(
            agent_id="test_agent_03",
            domain=IntelligenceDomain.MILITARY,
            specialty="troop_movements",
            data_dir=temp_data_dir,
        )

        agent.monitor()
        status = agent.get_status()

        assert status["agent_id"] == "test_agent_03"
        assert status["domain"] == "military"
        assert status["specialty"] == "troop_movements"
        assert status["status"] == "active"
        assert status["report_count"] == 1


class TestDomainOverseer:
    """Test DomainOverseer class."""

    def test_overseer_initialization(self, temp_data_dir):
        """Test overseer initialization."""
        overseer = DomainOverseer(
            domain=IntelligenceDomain.ENVIRONMENTAL,
            data_dir=temp_data_dir,
        )

        assert overseer.domain == IntelligenceDomain.ENVIRONMENTAL
        assert len(overseer.agents) == 0
        assert overseer.analysis_count == 0

    def test_overseer_add_agent(self, temp_data_dir):
        """Test adding agents to overseer."""
        overseer = DomainOverseer(
            domain=IntelligenceDomain.RELIGIOUS,
            data_dir=temp_data_dir,
        )

        agent = IntelligenceAgent(
            agent_id="test_agent_04",
            domain=IntelligenceDomain.RELIGIOUS,
            specialty="interfaith_relations",
            data_dir=temp_data_dir,
        )

        overseer.add_agent(agent)
        assert len(overseer.agents) == 1

    def test_overseer_add_wrong_domain_agent_raises(self, temp_data_dir):
        """Test that adding agent from wrong domain raises error."""
        overseer = DomainOverseer(
            domain=IntelligenceDomain.ECONOMIC,
            data_dir=temp_data_dir,
        )

        agent = IntelligenceAgent(
            agent_id="test_agent_05",
            domain=IntelligenceDomain.MILITARY,  # Wrong domain
            specialty="naval_operations",
            data_dir=temp_data_dir,
        )

        with pytest.raises(ValueError, match="doesn't match overseer domain"):
            overseer.add_agent(agent)

    def test_overseer_create_agents(self, temp_data_dir):
        """Test automated agent creation."""
        overseer = DomainOverseer(
            domain=IntelligenceDomain.TECHNOLOGICAL,
            data_dir=temp_data_dir,
        )

        overseer.create_agents(count=20)
        assert len(overseer.agents) == 20

        # Verify all agents have correct domain
        for agent in overseer.agents:
            assert agent.domain == IntelligenceDomain.TECHNOLOGICAL

    def test_overseer_collect_reports(self, temp_data_dir):
        """Test report collection from agents."""
        overseer = DomainOverseer(
            domain=IntelligenceDomain.POLITICAL,
            data_dir=temp_data_dir,
        )

        overseer.create_agents(count=5)
        reports = overseer.collect_reports()

        assert len(reports) == 5
        assert all(isinstance(r, IntelligenceReport) for r in reports)

    def test_overseer_analyze_domain(self, temp_data_dir):
        """Test domain analysis."""
        overseer = DomainOverseer(
            domain=IntelligenceDomain.ECONOMIC,
            data_dir=temp_data_dir,
        )

        overseer.create_agents(count=10)
        analysis = overseer.analyze_domain()

        assert isinstance(analysis, DomainAnalysis)
        assert analysis.domain == IntelligenceDomain.ECONOMIC
        assert len(analysis.agent_reports) == 10
        assert overseer.analysis_count == 1

    def test_overseer_get_status(self, temp_data_dir):
        """Test overseer status retrieval."""
        overseer = DomainOverseer(
            domain=IntelligenceDomain.ENVIRONMENTAL,
            data_dir=temp_data_dir,
        )

        overseer.create_agents(count=15)
        status = overseer.get_status()

        assert status["domain"] == "environmental"
        assert status["agent_count"] == 15
        assert len(status["agents"]) == 15


class TestGlobalCurator:
    """Test GlobalCurator class."""

    def test_curator_initialization(self, temp_data_dir):
        """Test curator initialization."""
        curator = GlobalCurator(data_dir=temp_data_dir)

        assert len(curator.overseers) == 0
        assert curator.theory_count == 0

    def test_curator_add_overseer(self, temp_data_dir):
        """Test adding overseers to curator."""
        curator = GlobalCurator(data_dir=temp_data_dir)

        overseer = DomainOverseer(
            domain=IntelligenceDomain.MILITARY,
            data_dir=temp_data_dir,
        )

        curator.add_overseer(overseer)
        assert len(curator.overseers) == 1
        assert IntelligenceDomain.MILITARY in curator.overseers

    def test_curator_collect_analyses(self, temp_data_dir):
        """Test collecting analyses from overseers."""
        curator = GlobalCurator(data_dir=temp_data_dir)

        # Add multiple overseers
        for domain in [
            IntelligenceDomain.ECONOMIC,
            IntelligenceDomain.POLITICAL,
        ]:
            overseer = DomainOverseer(domain=domain, data_dir=temp_data_dir)
            overseer.create_agents(count=5)
            curator.add_overseer(overseer)

        analyses = curator.collect_analyses()
        assert len(analyses) == 2
        assert all(isinstance(a, DomainAnalysis) for a in analyses)

    def test_curator_run_statistical_simulation(self, temp_data_dir):
        """Test statistical simulation generation (curator's analytical role)."""
        curator = GlobalCurator(data_dir=temp_data_dir)

        # Add all domains
        for domain in IntelligenceDomain:
            overseer = DomainOverseer(domain=domain, data_dir=temp_data_dir)
            overseer.create_agents(count=3)
            curator.add_overseer(overseer)

        simulation = curator.run_statistical_simulation()

        assert isinstance(simulation, GlobalTheory)
        assert len(simulation.domain_analyses) == 6  # All 6 domains
        assert curator.theory_count == 1
        assert 0.0 <= simulation.confidence_score <= 1.0
        
        # Verify curator produces simulations, not recommendations
        assert hasattr(simulation, 'simulation_id')
        assert hasattr(simulation, 'statistical_summary')
        assert hasattr(simulation, 'predicted_outcomes')
        assert not hasattr(simulation, 'recommendations')  # No command authority

    def test_curator_get_status(self, temp_data_dir):
        """Test curator status retrieval."""
        curator = GlobalCurator(data_dir=temp_data_dir)

        overseer = DomainOverseer(
            domain=IntelligenceDomain.TECHNOLOGICAL,
            data_dir=temp_data_dir,
        )
        overseer.create_agents(count=10)
        curator.add_overseer(overseer)

        status = curator.get_status()

        assert status["overseer_count"] == 1
        assert IntelligenceDomain.TECHNOLOGICAL in status["domains"]


class TestGlobalIntelligenceLibrary:
    """Test GlobalIntelligenceLibrary class."""

    def test_library_singleton_not_initialized_raises(self):
        """Test that accessing uninitialized singleton raises error."""
        with pytest.raises(RuntimeError, match="not initialized"):
            GlobalIntelligenceLibrary.get_instance()

    def test_library_initialize(self, temp_data_dir):
        """Test library initialization."""
        library = GlobalIntelligenceLibrary.initialize(
            data_dir=temp_data_dir,
            use_watch_tower=False,  # Don't integrate for isolated test
        )

        assert library is not None
        assert GlobalIntelligenceLibrary.is_initialized()
        assert library.curator is not None

    def test_library_initialize_twice_returns_same(self, temp_data_dir):
        """Test that initializing twice returns same instance."""
        library1 = GlobalIntelligenceLibrary.initialize(
            data_dir=temp_data_dir,
            use_watch_tower=False,
        )
        library2 = GlobalIntelligenceLibrary.initialize(
            data_dir=temp_data_dir,
            use_watch_tower=False,
        )

        assert library1 is library2

    def test_library_creates_all_domains(self, temp_data_dir):
        """Test that library creates all 6 domains."""
        library = GlobalIntelligenceLibrary.initialize(
            data_dir=temp_data_dir,
            use_watch_tower=False,
        )

        assert len(library.curator.overseers) == 6
        for domain in IntelligenceDomain:
            assert domain in library.curator.overseers

    def test_library_creates_20_agents_per_domain(self, temp_data_dir):
        """Test that each domain has 20 agents."""
        library = GlobalIntelligenceLibrary.initialize(
            data_dir=temp_data_dir,
            use_watch_tower=False,
        )

        for overseer in library.curator.overseers.values():
            assert len(overseer.agents) == 20

    def test_library_generate_statistical_simulation(self, temp_data_dir):
        """Test generating statistical simulation."""
        library = GlobalIntelligenceLibrary.initialize(
            data_dir=temp_data_dir,
            use_watch_tower=False,
        )

        simulation = library.generate_statistical_simulation()

        assert isinstance(simulation, GlobalTheory)
        assert len(simulation.domain_analyses) == 6
        assert len(simulation.predicted_outcomes) > 0
        
        # Verify no recommendations (curator has no command authority)
        simulation_dict = simulation.to_dict()
        assert 'recommendations' not in simulation_dict

    def test_library_get_domain_analysis(self, temp_data_dir):
        """Test getting specific domain analysis."""
        library = GlobalIntelligenceLibrary.initialize(
            data_dir=temp_data_dir,
            use_watch_tower=False,
        )

        analysis = library.get_domain_analysis(IntelligenceDomain.ECONOMIC)

        assert isinstance(analysis, DomainAnalysis)
        assert analysis.domain == IntelligenceDomain.ECONOMIC

    def test_library_get_status(self, temp_data_dir):
        """Test getting library status."""
        library = GlobalIntelligenceLibrary.initialize(
            data_dir=temp_data_dir,
            use_watch_tower=False,
        )

        status = library.get_library_status()

        assert status["initialized"] is True
        assert status["curator"] is not None
        assert status["watch_tower_integrated"] is False

    def test_library_run_full_analysis_cycle(self, temp_data_dir):
        """Test running full analysis cycle."""
        library = GlobalIntelligenceLibrary.initialize(
            data_dir=temp_data_dir,
            use_watch_tower=False,
        )

        simulation = library.run_full_analysis_cycle()

        assert isinstance(simulation, GlobalTheory)
        assert len(simulation.domain_analyses) == 6
        assert library.curator.theory_count == 1
        
        # Verify curator role is analytical only
        assert 'simulation_id' in simulation.to_dict()
        assert 'statistical_summary' in simulation.to_dict()

    def test_library_reset(self, temp_data_dir):
        """Test resetting library singleton."""
        GlobalIntelligenceLibrary.initialize(
            data_dir=temp_data_dir,
            use_watch_tower=False,
        )
        assert GlobalIntelligenceLibrary.is_initialized()

        GlobalIntelligenceLibrary.reset()
        assert not GlobalIntelligenceLibrary.is_initialized()


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_get_global_intelligence_library(self, temp_data_dir):
        """Test get_global_intelligence_library convenience function."""
        GlobalIntelligenceLibrary.initialize(
            data_dir=temp_data_dir,
            use_watch_tower=False,
        )

        library = get_global_intelligence_library()
        assert library is not None
        assert isinstance(library, GlobalIntelligenceLibrary)

    def test_generate_intelligence_report(self, temp_data_dir):
        """Test generate_statistical_simulation convenience function."""
        GlobalIntelligenceLibrary.initialize(
            data_dir=temp_data_dir,
            use_watch_tower=False,
        )

        simulation = generate_statistical_simulation()

        assert isinstance(simulation, GlobalTheory)
        assert len(simulation.domain_analyses) == 6


class TestDataPersistence:
    """Test data persistence functionality."""

    def test_domain_analysis_serialization(self, temp_data_dir):
        """Test domain analysis can be serialized."""
        overseer = DomainOverseer(
            domain=IntelligenceDomain.ECONOMIC,
            data_dir=temp_data_dir,
        )

        overseer.create_agents(count=5)
        analysis = overseer.analyze_domain()

        # Should be able to convert to dict
        analysis_dict = analysis.to_dict()
        assert isinstance(analysis_dict, dict)
        assert analysis_dict["domain"] == "economic"
        
        # Verify no recommendations field (overseers have no command authority)
        assert 'recommendations' not in analysis_dict

    def test_global_theory_serialization(self, temp_data_dir):
        """Test global theory (simulation) can be serialized."""
        library = GlobalIntelligenceLibrary.initialize(
            data_dir=temp_data_dir,
            use_watch_tower=False,
        )

        simulation = library.generate_statistical_simulation()

        # Should be able to convert to dict
        simulation_dict = simulation.to_dict()
        assert isinstance(simulation_dict, dict)
        assert "simulation_id" in simulation_dict
        assert "statistical_summary" in simulation_dict
        assert "predicted_outcomes" in simulation_dict
        
        # Verify no recommendations (curator has no command authority)
        assert 'recommendations' not in simulation_dict

    def test_analysis_saved_to_disk(self, temp_data_dir):
        """Test that analyses are saved to disk."""
        overseer = DomainOverseer(
            domain=IntelligenceDomain.POLITICAL,
            data_dir=temp_data_dir,
        )

        overseer.create_agents(count=3)
        overseer.analyze_domain()

        # Check that analysis file was created
        analysis_files = list(Path(temp_data_dir).rglob("analysis_*.json"))
        assert len(analysis_files) > 0

    def test_theory_saved_to_disk(self, temp_data_dir):
        """Test that theories are saved to disk."""
        library = GlobalIntelligenceLibrary.initialize(
            data_dir=temp_data_dir,
            use_watch_tower=False,
        )

        library.generate_global_theory()

        # Check that theory files were created
        theory_files = list(Path(temp_data_dir).rglob("theory_*.json"))
        assert len(theory_files) > 0

        # Check that latest theory file exists
        latest_file = Path(temp_data_dir) / "global" / "latest_theory.json"
        assert latest_file.exists()


class TestDomainSpecialties:
    """Test domain-specific specialties."""

    def test_economic_specialties(self, temp_data_dir):
        """Test economic domain has correct specialties."""
        overseer = DomainOverseer(
            domain=IntelligenceDomain.ECONOMIC,
            data_dir=temp_data_dir,
        )

        overseer.create_agents(count=20)

        # Check that agents have economic specialties
        specialties = {agent.specialty for agent in overseer.agents}
        assert "stock_markets" in specialties
        assert "commodities" in specialties

    def test_military_specialties(self, temp_data_dir):
        """Test military domain has correct specialties."""
        overseer = DomainOverseer(
            domain=IntelligenceDomain.MILITARY,
            data_dir=temp_data_dir,
        )

        overseer.create_agents(count=20)

        specialties = {agent.specialty for agent in overseer.agents}
        assert "troop_movements" in specialties
        assert "military_exercises" in specialties

    def test_environmental_specialties(self, temp_data_dir):
        """Test environmental domain has correct specialties."""
        overseer = DomainOverseer(
            domain=IntelligenceDomain.ENVIRONMENTAL,
            data_dir=temp_data_dir,
        )

        overseer.create_agents(count=20)

        specialties = {agent.specialty for agent in overseer.agents}
        assert "climate_change" in specialties
        assert "natural_disasters" in specialties


class TestCuratorAuthority:
    """Test that curator has NO command authority - only library maintenance and statistical simulations."""

    def test_curator_has_no_recommendations(self, temp_data_dir):
        """Verify curator does not make recommendations."""
        curator = GlobalCurator(data_dir=temp_data_dir)
        
        for domain in IntelligenceDomain:
            overseer = DomainOverseer(domain=domain, data_dir=temp_data_dir)
            overseer.create_agents(count=3)
            curator.add_overseer(overseer)
        
        simulation = curator.run_statistical_simulation()
        
        # Verify simulation has no recommendations
        assert not hasattr(simulation, 'recommendations')
        simulation_dict = simulation.to_dict()
        assert 'recommendations' not in simulation_dict
    
    def test_curator_produces_statistical_simulations(self, temp_data_dir):
        """Verify curator produces statistical simulations, not commands."""
        curator = GlobalCurator(data_dir=temp_data_dir)
        
        overseer = DomainOverseer(domain=IntelligenceDomain.ECONOMIC, data_dir=temp_data_dir)
        overseer.create_agents(count=5)
        curator.add_overseer(overseer)
        
        simulation = curator.run_statistical_simulation()
        
        # Verify it's a simulation with statistical data
        assert hasattr(simulation, 'simulation_id')
        assert hasattr(simulation, 'statistical_summary')
        assert hasattr(simulation, 'predicted_outcomes')
        assert hasattr(simulation, 'confidence_score')
        
        # Verify the simulation_id format indicates it's a simulation
        assert simulation.simulation_id.startswith('SIM_')
        
        # Verify statistical summary mentions it's a simulation
        assert 'simulation' in simulation.statistical_summary.lower() or 'statistical' in simulation.statistical_summary.lower()
    
    def test_overseer_has_no_recommendations(self, temp_data_dir):
        """Verify overseers do not make recommendations."""
        overseer = DomainOverseer(domain=IntelligenceDomain.MILITARY, data_dir=temp_data_dir)
        overseer.create_agents(count=10)
        
        analysis = overseer.analyze_domain()
        
        # Verify analysis has no recommendations
        assert not hasattr(analysis, 'recommendations')
        analysis_dict = analysis.to_dict()
        assert 'recommendations' not in analysis_dict
    
    def test_library_simulation_has_no_command_authority(self, temp_data_dir):
        """Verify library statistical simulations have no command authority."""
        library = GlobalIntelligenceLibrary.initialize(
            data_dir=temp_data_dir,
            use_watch_tower=False,
        )
        
        simulation = library.generate_statistical_simulation()
        
        # Verify no recommendations or commands
        simulation_dict = simulation.to_dict()
        assert 'recommendations' not in simulation_dict
        assert 'commands' not in simulation_dict
        assert 'directives' not in simulation_dict
        
        # Verify it's marked as a simulation
        assert 'simulation_id' in simulation_dict
        assert 'statistical' in simulation_dict['statistical_summary'].lower() or 'simulation' in simulation_dict['statistical_summary'].lower()
