"""Tests for Global Watch Tower system."""

import tempfile
from pathlib import Path

import pytest

from app.core.global_watch_tower import (
    GlobalWatchTower,
    get_global_watch_tower,
    verify_file_globally,
)


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton before and after each test."""
    GlobalWatchTower.reset()
    yield
    GlobalWatchTower.reset()


@pytest.fixture
def temp_test_file():
    """Create a temporary Python file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("# Test file\nprint('hello')\n")
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


class TestGlobalWatchTowerInitialization:
    """Test initialization and singleton behavior."""

    def test_singleton_not_initialized_raises_error(self):
        """Test that accessing uninitialized singleton raises error."""
        with pytest.raises(RuntimeError, match="not initialized"):
            GlobalWatchTower.get_instance()

    def test_initialize_creates_singleton(self):
        """Test that initialize creates the singleton instance."""
        tower = GlobalWatchTower.initialize()
        assert tower is not None
        assert GlobalWatchTower.is_initialized()

    def test_initialize_twice_returns_same_instance(self):
        """Test that calling initialize twice returns the same instance."""
        tower1 = GlobalWatchTower.initialize()
        tower2 = GlobalWatchTower.initialize()
        assert tower1 is tower2

    def test_initialize_with_custom_params(self):
        """Test initialization with custom parameters."""
        tower = GlobalWatchTower.initialize(
            num_port_admins=2,
            towers_per_port=5,
            gates_per_tower=3,
        )

        stats = tower.get_stats()
        assert stats["num_admins"] == 2
        assert stats["num_towers"] == 10  # 2 admins * 5 towers
        assert stats["num_gates"] == 30  # 2 admins * 5 towers * 3 gates

    def test_get_instance_after_initialize(self):
        """Test that get_instance works after initialization."""
        tower1 = GlobalWatchTower.initialize()
        tower2 = GlobalWatchTower.get_instance()
        assert tower1 is tower2

    def test_reset_clears_singleton(self):
        """Test that reset clears the singleton."""
        GlobalWatchTower.initialize()
        assert GlobalWatchTower.is_initialized()

        GlobalWatchTower.reset()
        assert not GlobalWatchTower.is_initialized()

        with pytest.raises(RuntimeError):
            GlobalWatchTower.get_instance()


class TestGlobalWatchTowerVerification:
    """Test file verification functionality."""

    @pytest.fixture(autouse=True)
    def setup_tower(self):
        """Initialize the watch tower before each test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self.tower = GlobalWatchTower.initialize(
                num_port_admins=1,
                towers_per_port=2,
                gates_per_tower=2,
                data_dir=tmpdir,
            )
            yield

    def test_verify_file_basic(self, temp_test_file):
        """Test basic file verification."""
        result = self.tower.verify_file(temp_test_file)

        assert isinstance(result, dict)
        assert "success" in result
        assert "verdict" in result
        assert "deps" in result
        assert "sandbox" in result

    def test_verify_file_updates_stats(self, temp_test_file):
        """Test that verification updates statistics."""
        initial_stats = self.tower.get_stats()
        assert initial_stats["total_verifications"] == 0

        self.tower.verify_file(temp_test_file)

        updated_stats = self.tower.get_stats()
        assert updated_stats["total_verifications"] == 1
        assert updated_stats["total_quarantined"] == 1

    def test_verify_multiple_files(self, temp_test_file):
        """Test verifying multiple files."""
        for _ in range(5):
            result = self.tower.verify_file(temp_test_file)
            assert isinstance(result, dict)

        stats = self.tower.get_stats()
        assert stats["total_verifications"] == 5
        assert stats["total_quarantined"] == 5

    def test_verify_file_with_path_object(self, temp_test_file):
        """Test verification with Path object."""
        result = self.tower.verify_file(temp_test_file)
        assert isinstance(result, dict)

    def test_verify_file_with_string_path(self, temp_test_file):
        """Test verification with string path."""
        result = self.tower.verify_file(str(temp_test_file))
        assert isinstance(result, dict)


class TestGlobalWatchTowerQuarantine:
    """Test quarantine functionality."""

    @pytest.fixture(autouse=True)
    def setup_tower(self):
        """Initialize the watch tower before each test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self.tower = GlobalWatchTower.initialize(data_dir=tmpdir)
            yield

    def test_quarantine_file(self, temp_test_file):
        """Test placing a file in quarantine."""
        box = self.tower.quarantine_file(temp_test_file)

        assert box is not None
        assert box.path == str(temp_test_file)
        assert box.sealed is True
        assert box.verified is False

    def test_quarantine_updates_stats(self, temp_test_file):
        """Test that quarantine updates statistics."""
        initial_stats = self.tower.get_stats()
        assert initial_stats["total_quarantined"] == 0

        self.tower.quarantine_file(temp_test_file)

        updated_stats = self.tower.get_stats()
        assert updated_stats["total_quarantined"] == 1
        assert updated_stats["active_quarantine"] == 1

    def test_process_quarantined(self, temp_test_file):
        """Test processing a quarantined file."""
        self.tower.quarantine_file(temp_test_file)

        result = self.tower.process_quarantined(str(temp_test_file))

        assert isinstance(result, dict)
        assert "success" in result
        assert "verdict" in result

    def test_process_quarantined_not_found(self):
        """Test processing a file not in quarantine raises error."""
        with pytest.raises(KeyError, match="File not found in quarantine"):
            self.tower.process_quarantined("/nonexistent/file.py")

    def test_quarantine_and_process_clears_quarantine(self, temp_test_file):
        """Test that processing releases file from quarantine."""
        self.tower.quarantine_file(temp_test_file)

        stats_before = self.tower.get_stats()
        assert stats_before["active_quarantine"] == 1

        self.tower.process_quarantined(str(temp_test_file))

        stats_after = self.tower.get_stats()
        assert stats_after["active_quarantine"] == 0


class TestGlobalWatchTowerEmergencyLockdown:
    """Test emergency lockdown functionality."""

    @pytest.fixture(autouse=True)
    def setup_tower(self):
        """Initialize the watch tower before each test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self.tower = GlobalWatchTower.initialize(data_dir=tmpdir)
            yield

    def test_activate_emergency_lockdown(self):
        """Test activating emergency lockdown."""
        initial_stats = self.tower.get_stats()
        assert initial_stats["total_lockdowns"] == 0

        self.tower.activate_emergency_lockdown("Test emergency")

        updated_stats = self.tower.get_stats()
        assert updated_stats["total_lockdowns"] == 1

    def test_lockdown_activates_force_fields(self):
        """Test that lockdown activates all gate force fields."""
        self.tower.activate_emergency_lockdown("Test emergency")

        for gate in self.tower.gate_guardians:
            assert gate.force_field_active is True


class TestGlobalWatchTowerStats:
    """Test statistics and reporting."""

    @pytest.fixture(autouse=True)
    def setup_tower(self):
        """Initialize the watch tower before each test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self.tower = GlobalWatchTower.initialize(
                num_port_admins=1,
                towers_per_port=3,
                gates_per_tower=2,
                data_dir=tmpdir,
            )
            yield

    def test_get_stats_structure(self):
        """Test the structure of statistics dict."""
        stats = self.tower.get_stats()

        required_keys = [
            "total_verifications",
            "total_quarantined",
            "total_incidents",
            "total_lockdowns",
            "num_admins",
            "num_towers",
            "num_gates",
            "active_quarantine",
            "cerberus_incidents",
        ]

        for key in required_keys:
            assert key in stats

    def test_get_stats_initial_values(self):
        """Test initial statistics values."""
        stats = self.tower.get_stats()

        assert stats["total_verifications"] == 0
        assert stats["total_quarantined"] == 0
        assert stats["total_incidents"] == 0
        assert stats["total_lockdowns"] == 0
        assert stats["num_admins"] == 1
        assert stats["num_towers"] == 3
        assert stats["num_gates"] == 6  # 1 * 3 * 2

    def test_get_cerberus_incidents_empty(self):
        """Test getting Cerberus incidents when empty."""
        incidents = self.tower.get_cerberus_incidents()
        assert isinstance(incidents, list)
        assert len(incidents) == 0

    def test_get_tower_by_id(self):
        """Test retrieving a tower by ID."""
        tower = self.tower.get_tower_by_id("wt-0-0")
        assert tower is not None
        assert tower.tower_id == "wt-0-0"

    def test_get_tower_by_id_not_found(self):
        """Test retrieving nonexistent tower returns None."""
        tower = self.tower.get_tower_by_id("wt-99-99")
        assert tower is None

    def test_get_gate_by_id(self):
        """Test retrieving a gate by ID."""
        gate = self.tower.get_gate_by_id("gate-0-0-0")
        assert gate is not None
        assert gate.gate_id == "gate-0-0-0"

    def test_get_gate_by_id_not_found(self):
        """Test retrieving nonexistent gate returns None."""
        gate = self.tower.get_gate_by_id("gate-99-99-99")
        assert gate is None


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.fixture(autouse=True)
    def setup_tower(self):
        """Initialize the watch tower before each test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            GlobalWatchTower.initialize(data_dir=tmpdir)
            yield

    def test_get_global_watch_tower(self):
        """Test get_global_watch_tower convenience function."""
        tower = get_global_watch_tower()
        assert tower is not None
        assert isinstance(tower, GlobalWatchTower)

    def test_verify_file_globally(self, temp_test_file):
        """Test verify_file_globally convenience function."""
        result = verify_file_globally(temp_test_file)

        assert isinstance(result, dict)
        assert "success" in result
        assert "verdict" in result

    def test_verify_file_globally_with_string(self, temp_test_file):
        """Test verify_file_globally with string path."""
        result = verify_file_globally(str(temp_test_file))
        assert isinstance(result, dict)


class TestCerberusChiefOfSecurity:
    """Test Cerberus as Chief of Security."""

    @pytest.fixture(autouse=True)
    def setup_tower(self):
        """Initialize the watch tower before each test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            GlobalWatchTower.initialize(data_dir=tmpdir)
            yield

    def test_cerberus_is_chief_of_security(self):
        """Test that Cerberus has Chief of Security title."""
        tower = get_global_watch_tower()
        cerberus = tower.get_chief_of_security()
        
        assert cerberus is not None
        assert hasattr(cerberus, "title")
        assert cerberus.title == "Chief of Security"

    def test_border_patrol_agents_registered_with_cerberus(self):
        """Test that border patrol agents are registered with Cerberus."""
        tower = get_global_watch_tower()
        status = tower.get_security_status()
        
        assert "chief_of_security" in status
        assert status["chief_of_security"] == "Cerberus"
        assert "registered_agents" in status
        assert "border_patrol" in status["registered_agents"]
        
        # Should have registered port admins, towers, gates, and verifiers
        assert status["registered_agents"]["border_patrol"] > 0

    def test_register_active_defense_agents(self):
        """Test registering active defense agents with Cerberus."""
        tower = get_global_watch_tower()
        
        # Register some active defense agents
        tower.register_security_agent("active_defense", "safety_guard_1")
        tower.register_security_agent("active_defense", "constitutional_guardrail_1")
        tower.register_security_agent("active_defense", "tarl_protector_1")
        
        status = tower.get_security_status()
        assert status["registered_agents"]["active_defense"] == 3
        assert "safety_guard_1" in status["agent_details"]["active_defense"]
        assert "constitutional_guardrail_1" in status["agent_details"]["active_defense"]
        assert "tarl_protector_1" in status["agent_details"]["active_defense"]

    def test_register_red_team_agents(self):
        """Test registering red team agents with Cerberus."""
        tower = get_global_watch_tower()
        
        # Register some red team agents
        tower.register_security_agent("red_team", "red_team_agent_1")
        tower.register_security_agent("red_team", "code_adversary_1")
        tower.register_security_agent("red_team", "jailbreak_tester_1")
        
        status = tower.get_security_status()
        assert status["registered_agents"]["red_team"] == 3
        assert "red_team_agent_1" in status["agent_details"]["red_team"]

    def test_register_oversight_agents(self):
        """Test registering oversight agents with Cerberus."""
        tower = get_global_watch_tower()
        
        # Register some oversight agents
        tower.register_security_agent("oversight", "oversight_agent_1")
        tower.register_security_agent("oversight", "validator_agent_1")
        tower.register_security_agent("oversight", "explainability_agent_1")
        
        status = tower.get_security_status()
        assert status["registered_agents"]["oversight"] == 3
        assert "oversight_agent_1" in status["agent_details"]["oversight"]

    def test_security_status_includes_all_categories(self):
        """Test that security status includes all agent categories."""
        tower = get_global_watch_tower()
        
        # Register agents in all categories
        tower.register_security_agent("active_defense", "test_defense")
        tower.register_security_agent("red_team", "test_red")
        tower.register_security_agent("oversight", "test_oversight")
        
        status = tower.get_security_status()
        
        assert "registered_agents" in status
        assert "border_patrol" in status["registered_agents"]
        assert "active_defense" in status["registered_agents"]
        assert "red_team" in status["registered_agents"]
        assert "oversight" in status["registered_agents"]
        
        # All categories should have at least one agent
        assert status["registered_agents"]["border_patrol"] > 0
        assert status["registered_agents"]["active_defense"] == 1
        assert status["registered_agents"]["red_team"] == 1
        assert status["registered_agents"]["oversight"] == 1

    def test_duplicate_agent_registration_ignored(self):
        """Test that duplicate agent registration is ignored."""
        tower = get_global_watch_tower()
        
        # Register same agent twice
        tower.register_security_agent("active_defense", "duplicate_agent")
        tower.register_security_agent("active_defense", "duplicate_agent")
        
        status = tower.get_security_status()
        # Should only be counted once
        assert status["agent_details"]["active_defense"].count("duplicate_agent") == 1

    def test_cerberus_incident_tracking(self):
        """Test that Cerberus tracks incidents properly."""
        tower = get_global_watch_tower()
        cerberus = tower.get_chief_of_security()
        
        initial_count = len(cerberus.incidents)
        
        # Record an incident
        cerberus.record_incident({"type": "test", "details": "test incident"})
        
        assert len(cerberus.incidents) == initial_count + 1
        
        # Verify in security status
        status = tower.get_security_status()
        assert status["total_incidents"] == initial_count + 1
