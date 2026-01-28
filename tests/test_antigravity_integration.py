"""
Tests for Antigravity IDE integration.

This module tests the configuration and custom agents for Google Antigravity IDE integration.
"""

import json
import sys
from pathlib import Path

import pytest

# Adjust path to import from .antigravity
sys.path.insert(0, str(Path(__file__).parent.parent / ".antigravity" / "agents"))

try:
    from project_ai_agent import ProjectAIAgent
except ImportError:
    ProjectAIAgent = None


class TestAntigravityConfiguration:
    """Test Antigravity configuration files."""

    def test_config_file_exists(self):
        """Test that config.json exists."""
        config_path = Path(__file__).parent.parent / ".antigravity" / "config.json"
        assert config_path.exists(), "Antigravity config.json not found"

    def test_config_is_valid_json(self):
        """Test that config.json is valid JSON."""
        config_path = Path(__file__).parent.parent / ".antigravity" / "config.json"

        with open(config_path) as f:
            config = json.load(f)

        assert isinstance(config, dict), "Config should be a dictionary"

    def test_config_has_required_sections(self):
        """Test that config.json has all required sections."""
        config_path = Path(__file__).parent.parent / ".antigravity" / "config.json"

        with open(config_path) as f:
            config = json.load(f)

        required_sections = ["project", "agents", "integrations", "ai_systems"]
        for section in required_sections:
            assert section in config, f"Missing required section: {section}"

    def test_config_project_name(self):
        """Test that project name is correct."""
        config_path = Path(__file__).parent.parent / ".antigravity" / "config.json"

        with open(config_path) as f:
            config = json.load(f)

        assert (
            config["project"]["name"] == "Project-AI"
        ), "Project name should be 'Project-AI'"

    def test_config_ai_systems(self):
        """Test that AI systems are configured."""
        config_path = Path(__file__).parent.parent / ".antigravity" / "config.json"

        with open(config_path) as f:
            config = json.load(f)

        required_systems = [
            "four_laws",
            "triumvirate",
            "ai_persona",
            "memory_expansion",
        ]
        for system in required_systems:
            assert system in config["ai_systems"], f"Missing AI system: {system}"

    def test_security_yaml_exists(self):
        """Test that security.yaml exists."""
        security_path = Path(__file__).parent.parent / ".antigravity" / "security.yaml"
        assert security_path.exists(), "Antigravity security.yaml not found"


class TestAntigravityAgent:
    """Test the custom Project-AI agent."""

    @pytest.fixture
    def agent(self):
        """Create an agent instance."""
        if ProjectAIAgent is None:
            pytest.skip("ProjectAIAgent not available")
        return ProjectAIAgent()

    def test_agent_initialization(self, agent):
        """Test that agent initializes correctly."""
        assert agent is not None
        assert agent.workspace_path is not None
        assert isinstance(agent.project_knowledge, dict)

    def test_agent_has_patterns(self, agent):
        """Test that agent has detection patterns."""
        assert len(agent.ethical_review_patterns) > 0
        assert len(agent.security_critical_patterns) > 0
        assert len(agent.temporal_patterns) > 0

    def test_agent_load_knowledge(self, agent):
        """Test that agent loads Project-AI knowledge."""
        knowledge = agent.project_knowledge

        assert "core_systems" in knowledge
        assert "FourLaws" in knowledge["core_systems"]
        assert "AIPersona" in knowledge["core_systems"]
        assert "Triumvirate" in knowledge["core_systems"]

    def test_agent_analyze_safe_task(self, agent):
        """Test analysis of a safe task."""
        analysis = agent.analyze_task(
            "Add a docstring to the calculate_area function", ["src/app/utils.py"]
        )

        assert isinstance(analysis, dict)
        assert "requires_ethical_review" in analysis
        assert "requires_security_scan" in analysis
        # Simple documentation task shouldn't require review
        assert not analysis["requires_ethical_review"]

    def test_agent_analyze_ethical_task(self, agent):
        """Test analysis of a task requiring ethical review."""
        analysis = agent.analyze_task(
            "Modify the AI persona's memory system", ["src/app/core/ai_systems.py"]
        )

        assert analysis["requires_ethical_review"], "Should require ethical review"
        # Note: personhood-critical is file-path based, not just keyword based
        # Test with actual personhood-critical file

        analysis2 = agent.analyze_task(
            "Update AI persona state", ["data/ai_persona/state.json"]
        )
        assert analysis2["is_personhood_critical"], "Should be personhood-critical"

    def test_agent_analyze_security_task(self, agent):
        """Test analysis of a security-critical task."""
        analysis = agent.analyze_task(
            "Update password hashing algorithm", ["src/app/core/user_manager.py"]
        )

        assert analysis["requires_security_scan"], "Should require security scan"

    def test_agent_analyze_restricted_files(self, agent):
        """Test detection of restricted file modifications."""
        analysis = agent.analyze_task(
            "Update configuration", ["data/ai_persona/state.json"]
        )

        assert len(analysis["restricted_files"]) > 0, "Should detect restricted file"
        assert analysis["is_personhood_critical"], "Should be personhood-critical"

    def test_agent_generate_recommendations(self, agent):
        """Test recommendation generation."""
        recommendations = agent.generate_recommendations(
            "Add a new feature", ["src/app/core/new_feature.py"]
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        # Should always recommend running tests
        assert any("pytest" in rec.lower() for rec in recommendations)

    def test_agent_test_requirements(self, agent):
        """Test test requirement generation."""
        test_commands = agent.get_test_requirements(["src/app/core/ai_systems.py"])

        assert isinstance(test_commands, list)
        assert len(test_commands) > 0
        # Should include core tests for core changes
        assert any("test_ai_systems" in cmd for cmd in test_commands)


class TestAntigravityWorkflows:
    """Test workflow definition files."""

    def test_feature_development_workflow_exists(self):
        """Test that feature development workflow exists."""
        workflow_path = (
            Path(__file__).parent.parent
            / ".antigravity"
            / "workflows"
            / "feature-development.yaml"
        )
        assert workflow_path.exists(), "Feature development workflow not found"

    def test_security_fix_workflow_exists(self):
        """Test that security fix workflow exists."""
        workflow_path = (
            Path(__file__).parent.parent
            / ".antigravity"
            / "workflows"
            / "security-fix.yaml"
        )
        assert workflow_path.exists(), "Security fix workflow not found"


class TestAntigravitySetup:
    """Test the setup script."""

    def test_setup_script_exists(self):
        """Test that setup script exists."""
        setup_path = (
            Path(__file__).parent.parent
            / ".antigravity"
            / "scripts"
            / "setup_antigravity.py"
        )
        assert setup_path.exists(), "Setup script not found"

    def test_setup_script_is_executable(self):
        """Test that setup script has valid syntax."""
        setup_path = (
            Path(__file__).parent.parent
            / ".antigravity"
            / "scripts"
            / "setup_antigravity.py"
        )

        # Try to compile the script
        with open(setup_path) as f:
            code = f.read()

        compile(code, str(setup_path), "exec")


class TestAntigravityDocumentation:
    """Test documentation files."""

    def test_readme_exists(self):
        """Test that README exists."""
        readme_path = Path(__file__).parent.parent / ".antigravity" / "README.md"
        assert readme_path.exists(), "Antigravity README not found"

    def test_quickstart_exists(self):
        """Test that quickstart guide exists."""
        quickstart_path = (
            Path(__file__).parent.parent / "docs" / "ANTIGRAVITY_QUICKSTART.md"
        )
        assert quickstart_path.exists(), "Antigravity quickstart guide not found"

    def test_integration_guide_exists(self):
        """Test that integration guide exists."""
        guide_path = (
            Path(__file__).parent.parent
            / "docs"
            / "GOOGLE_ANTIGRAVITY_IDE_INTEGRATION.md"
        )
        assert guide_path.exists(), "Antigravity integration guide not found"
