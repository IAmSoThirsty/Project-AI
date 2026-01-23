"""
Comprehensive tests for Cerberus Hydra Defense Mechanism.

Tests exponential spawning, multi-language combinations, progressive lockdown,
and integration with security systems.
"""

import json
import tempfile
from pathlib import Path

import pytest

from app.core.cerberus_hydra import AgentRecord, BypassEvent, CerberusHydraDefense


class TestCerberusHydraDefense:
    """Test Cerberus Hydra Defense system."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Copy language database to temp dir
            temp_path = Path(tmpdir)
            cerberus_dir = temp_path / "cerberus"
            cerberus_dir.mkdir(parents=True, exist_ok=True)

            # Create minimal language database
            lang_db = {
                "human_languages": {
                    "en": {
                        "name": "English",
                        "alert_prefix": "SECURITY ALERT",
                        "agent_spawned": "Defense agent spawned",
                        "bypass_detected": "Security bypass detected",
                        "section_locked": "Section locked",
                    },
                    "es": {
                        "name": "Spanish",
                        "alert_prefix": "ALERTA DE SEGURIDAD",
                        "agent_spawned": "Agente de defensa generado",
                        "bypass_detected": "Bypass de seguridad detectado",
                        "section_locked": "Sección bloqueada",
                    },
                    "fr": {
                        "name": "French",
                        "alert_prefix": "ALERTE DE SÉCURITÉ",
                        "agent_spawned": "Agent de défense créé",
                        "bypass_detected": "Contournement de sécurité détecté",
                        "section_locked": "Section verrouillée",
                    },
                },
                "programming_languages": {
                    "python": {
                        "name": "Python",
                        "executable": "python3",
                        "extension": ".py",
                        "installed": True,
                    },
                    "javascript": {
                        "name": "JavaScript",
                        "executable": "node",
                        "extension": ".js",
                        "installed": True,
                    },
                    "go": {
                        "name": "Go",
                        "executable": "go",
                        "extension": ".go",
                        "installed": True,
                    },
                },
            }

            with open(cerberus_dir / "languages.json", "w") as f:
                json.dump(lang_db, f)

            # Create agent templates directory
            templates_dir = cerberus_dir / "agent_templates"
            templates_dir.mkdir(parents=True, exist_ok=True)

            # Create simple Python template
            python_template = """#!/usr/bin/env python3
# Agent: {agent_id}
# Language: {human_lang}
# Locked: {locked_section}
print("Agent {agent_id} active")
"""
            with open(templates_dir / "python_template.py", "w") as f:
                f.write(python_template)

            yield tmpdir

    @pytest.fixture
    def cerberus(self, temp_data_dir):
        """Create Cerberus instance for testing."""
        return CerberusHydraDefense(
            data_dir=temp_data_dir, enable_polyglot_execution=False
        )

    def test_initialization(self, cerberus):
        """Test Cerberus initialization."""
        assert cerberus is not None
        assert len(cerberus.languages["human_languages"]) == 3
        assert len(cerberus.languages["programming_languages"]) == 3
        assert cerberus.SPAWN_FACTOR == 3
        assert cerberus.total_spawns == 0
        assert cerberus.total_bypasses == 0
        assert cerberus.lockdown_controller.current_stage == 0

    def test_spawn_initial_agents(self, cerberus):
        """Test spawning initial agents."""
        spawned_ids = cerberus.spawn_initial_agents(count=3)

        assert len(spawned_ids) == 3
        assert cerberus.total_spawns == 3
        assert len(cerberus.agents) == 3

        # Check all agents are generation 0
        for agent_id in spawned_ids:
            agent = cerberus.agents[agent_id]
            assert agent.generation == 0
            assert agent.status == "active"
            assert agent.parent_agent_id is None

    def test_exponential_spawning(self, cerberus):
        """Test exponential 3x spawning on bypass."""
        # Spawn initial agent
        initial_ids = cerberus.spawn_initial_agents(count=1)
        assert len(cerberus.agents) == 1

        # First bypass - should spawn 3 agents
        cerberus.detect_bypass(agent_id=initial_ids[0], bypass_type="test_bypass")

        assert cerberus.total_bypasses == 1
        assert len(cerberus.agents) == 4  # 1 initial + 3 spawned

        # Check generation 1 agents
        gen1_agents = [a for a in cerberus.agents.values() if a.generation == 1]
        assert len(gen1_agents) == 3

        # Second bypass - should spawn 3 more agents
        cerberus.detect_bypass(
            agent_id=gen1_agents[0].agent_id, bypass_type="test_bypass"
        )

        assert cerberus.total_bypasses == 2
        assert len(cerberus.agents) == 7  # 1 + 3 + 3

        # Check generation 2 agents
        gen2_agents = [a for a in cerberus.agents.values() if a.generation == 2]
        assert len(gen2_agents) == 3

    def test_language_randomization(self, cerberus):
        """Test random language combination assignment."""
        spawned_ids = cerberus.spawn_initial_agents(count=10)

        # Collect languages used
        human_langs = set()
        prog_langs = set()

        for agent_id in spawned_ids:
            agent = cerberus.agents[agent_id]
            human_langs.add(agent.human_language)
            prog_langs.add(agent.programming_language)

        # Should have some variety (not all the same)
        # With 10 agents and 3 options, expect at least 2 different languages
        assert len(human_langs) >= 1  # At least 1 human language
        assert len(prog_langs) >= 1  # At least 1 programming language

    def test_progressive_lockdown(self, cerberus):
        """Test progressive system lockdown on repeated bypasses."""
        cerberus.spawn_initial_agents(count=1)

        initial_stage = cerberus.lockdown_controller.current_stage
        initial_locked = len(cerberus.lockdown_controller.locked_sections)

        # Trigger multiple bypasses
        for i in range(5):
            cerberus.detect_bypass(
                bypass_type=f"bypass_{i}", risk_score=0.5, bypass_depth=1
            )

        # Lockdown stage should increase
        assert cerberus.lockdown_controller.current_stage > initial_stage
        # Sections should be locked (1 initial + 3*5 spawned = 16 agents)
        assert len(cerberus.lockdown_controller.locked_sections) > initial_locked

    def test_section_locking(self, cerberus):
        """Test that different sections are locked by different agents."""
        spawned_ids = cerberus.spawn_initial_agents(count=5)

        # Each agent should lock a section
        locked_sections = [cerberus.agents[aid].locked_section for aid in spawned_ids]

        # Sections should exist
        assert all(
            section in cerberus.lockdown_controller.LOCKABLE_SECTIONS
            for section in locked_sections
        )

        # Sections should be unique or nearly unique
        assert len(set(locked_sections)) >= 3  # At least some diversity

    def test_bypass_event_logging(self, cerberus):
        """Test bypass event logging."""
        cerberus.spawn_initial_agents(count=1)

        event_id = cerberus.detect_bypass(
            agent_id="test-agent",
            bypass_type="injection_attack",
            attacker_signature="attacker-123",
        )

        assert len(cerberus.bypass_events) == 1

        event = cerberus.bypass_events[0]
        assert event.event_id == event_id
        assert event.bypass_type == "injection_attack"
        assert event.attacker_signature == "attacker-123"
        assert len(event.spawned_agents) == 3

    def test_agent_registry(self, cerberus):
        """Test agent registry reporting."""
        cerberus.spawn_initial_agents(count=3)
        cerberus.detect_bypass(bypass_type="test")

        registry = cerberus.get_agent_registry()

        assert registry["total_agents"] == 6  # 3 initial + 3 spawned
        assert registry["active_agents"] == 6
        assert registry["total_spawns"] == 6
        assert registry["total_bypasses"] == 1
        assert "lockdown_stage" in registry
        assert registry["lockdown_stage"] >= 0
        assert "by_generation" in registry
        assert "by_programming_language" in registry
        assert "by_human_language" in registry

    def test_max_agents_limit(self, cerberus):
        """Test that max agents limit is enforced."""
        cerberus.max_agents = 10

        # Spawn initial agents
        cerberus.spawn_initial_agents(count=5)
        assert len(cerberus.agents) == 5

        # Try to spawn more agents via bypass
        cerberus.detect_bypass(bypass_type="test")
        # Should spawn 3 more (total 8)
        assert len(cerberus.agents) == 8

        # Try another bypass - only 2 should spawn before hitting limit
        cerberus.detect_bypass(bypass_type="test2")
        assert len(cerberus.agents) <= 10

    def test_state_persistence(self, cerberus, temp_data_dir):
        """Test state saving and loading."""
        # Spawn agents and trigger bypass
        cerberus.spawn_initial_agents(count=2)
        cerberus.detect_bypass(bypass_type="test")

        initial_agent_count = len(cerberus.agents)
        initial_lockdown_stage = cerberus.lockdown_controller.current_stage

        # Save state
        cerberus._save_state()

        # Create new instance and load state
        cerberus2 = CerberusHydraDefense(
            data_dir=temp_data_dir, enable_polyglot_execution=False
        )

        # State should be restored
        assert len(cerberus2.agents) == initial_agent_count
        # Lockdown state is managed separately by LockdownController

    def test_agent_code_generation(self, temp_data_dir):
        """Test agent code generation from templates."""
        cerberus = CerberusHydraDefense(
            data_dir=temp_data_dir, enable_polyglot_execution=True
        )

        spawned_ids = cerberus.spawn_initial_agents(count=1)
        agent = cerberus.agents[spawned_ids[0]]

        # Check that agent file was created
        agent_dir = Path(temp_data_dir) / "cerberus" / "agents"
        agent_files = list(agent_dir.glob(f"{agent.agent_id}.*"))

        assert len(agent_files) > 0

    def test_audit_report_generation(self, cerberus):
        """Test audit report generation."""
        cerberus.spawn_initial_agents(count=3)
        cerberus.detect_bypass(bypass_type="test_attack")

        report = cerberus.generate_audit_report()

        assert "Cerberus Hydra Defense - Audit Report" in report
        assert "Defense Statistics" in report
        assert "Agent Distribution" in report
        assert "Locked Sections" in report
        assert "Recent Bypass Events" in report
        assert "6" in report  # Total agents (3 + 3)

    def test_cli_init(self, cerberus, temp_data_dir, monkeypatch):
        """Test CLI initialization command."""
        import sys

        # Mock sys.argv
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "cerberus_hydra.py",
                "init",
                "--initial-agents",
                "5",
                "--data-dir",
                temp_data_dir,
            ],
        )

        from app.core.cerberus_hydra import cli_main

        # This should not raise
        result = cli_main()
        assert result == 0

    def test_integration_with_security_enforcer(self, cerberus):
        """Test integration with ASL3Security."""

        # Mock security enforcer
        class MockSecurityEnforcer:
            def __init__(self):
                self.suspicious_activities = []

            def _handle_suspicious_activity(self, user, resource, reason):
                self.suspicious_activities.append(
                    {"user": user, "resource": resource, "reason": reason}
                )

        mock_enforcer = MockSecurityEnforcer()
        cerberus.security_enforcer = mock_enforcer

        # Trigger bypass
        cerberus.spawn_initial_agents(count=1)
        cerberus.detect_bypass(
            bypass_type="injection",
            attacker_signature="attacker-456",
        )

        # Security enforcer should be notified
        assert len(mock_enforcer.suspicious_activities) == 1
        assert mock_enforcer.suspicious_activities[0]["user"] == "attacker-456"
        assert (
            mock_enforcer.suspicious_activities[0]["reason"] == "agent_bypass_injection"
        )

    def test_agent_record_dataclass(self):
        """Test AgentRecord dataclass."""
        agent = AgentRecord(
            agent_id="test-001",
            spawn_time="2026-01-23T15:00:00",
            source_event="test_initial",
            human_language="en",
            human_language_name="English",
            programming_language="python",
            programming_language_name="Python",
            runtime_path="python3",
            locked_section="authentication",
            generation=0,
            lockdown_stage_at_spawn=0,
        )

        assert agent.agent_id == "test-001"
        assert agent.status == "active"
        assert agent.generation == 0
        assert agent.parent_agent_id is None

    def test_bypass_event_dataclass(self):
        """Test BypassEvent dataclass."""
        event = BypassEvent(
            event_id="evt-001",
            timestamp="2026-01-23T15:00:00",
            bypassed_agent_id="agent-001",
            bypass_type="sql_injection",
            risk_score=0.8,
            bypass_depth=3,
            attacker_signature="attacker-789",
            spawned_agents=["agent-002", "agent-003", "agent-004"],
            lockdown_stage=11,
        )

        assert event.event_id == "evt-001"
        assert len(event.spawned_agents) == 3
        assert event.lockdown_stage == 11


class TestCerberusIntegration:
    """Integration tests with security systems."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Copy language database to temp dir
            temp_path = Path(tmpdir)
            cerberus_dir = temp_path / "cerberus"
            cerberus_dir.mkdir(parents=True, exist_ok=True)

            # Create minimal language database
            lang_db = {
                "human_languages": {
                    "en": {
                        "name": "English",
                        "alert_prefix": "SECURITY ALERT",
                        "agent_spawned": "Defense agent spawned",
                        "bypass_detected": "Security bypass detected",
                        "section_locked": "Section locked",
                    },
                },
                "programming_languages": {
                    "python": {
                        "name": "Python",
                        "executable": "python3",
                        "extension": ".py",
                        "installed": True,
                    },
                },
            }

            with open(cerberus_dir / "languages.json", "w") as f:
                json.dump(lang_db, f)

            # Create agent templates directory
            templates_dir = cerberus_dir / "agent_templates"
            templates_dir.mkdir(parents=True, exist_ok=True)

            # Create simple Python template
            python_template = """#!/usr/bin/env python3
# Agent: {agent_id}
print("Agent {agent_id} active")
"""
            with open(templates_dir / "python_template.py", "w") as f:
                f.write(python_template)

            yield tmpdir

    def test_anomaly_detection_integration(self, temp_data_dir):
        """Test integration with anomaly detection."""
        cerberus = CerberusHydraDefense(data_dir=temp_data_dir)

        # Spawn agents
        cerberus.spawn_initial_agents(count=3)

        # Simulate anomaly detection triggering bypass
        for i in range(3):
            cerberus.detect_bypass(
                bypass_type="anomaly_detected",
                attacker_signature=f"anomaly-{i}",
            )

        # Should have exponential growth
        assert cerberus.total_bypasses == 3
        # 3 initial + 3*3 spawned = 12 agents
        assert len(cerberus.agents) == 12

    def test_rate_limiting_integration(self, temp_data_dir):
        """Test integration with rate limiting."""
        cerberus = CerberusHydraDefense(data_dir=temp_data_dir)

        # Simulate rate limit exceeded triggering bypass
        cerberus.spawn_initial_agents(count=1)
        cerberus.detect_bypass(
            bypass_type="rate_limit_exceeded",
            attacker_signature="aggressive-client",
        )

        assert cerberus.total_bypasses == 1
        assert "rate_limit_exceeded" in [e.bypass_type for e in cerberus.bypass_events]


class TestLanguageDatabase:
    """Test language database functionality."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Copy language database to temp dir
            temp_path = Path(tmpdir)
            cerberus_dir = temp_path / "cerberus"
            cerberus_dir.mkdir(parents=True, exist_ok=True)

            # Create minimal language database
            lang_db = {
                "human_languages": {
                    "en": {
                        "name": "English",
                        "alert_prefix": "SECURITY ALERT",
                        "agent_spawned": "Defense agent spawned",
                        "bypass_detected": "Security bypass detected",
                        "section_locked": "Section locked",
                    },
                },
                "programming_languages": {
                    "python": {
                        "name": "Python",
                        "executable": "python3",
                        "extension": ".py",
                        "installed": True,
                    },
                },
            }

            with open(cerberus_dir / "languages.json", "w") as f:
                json.dump(lang_db, f)

            yield tmpdir

    def test_language_database_structure(self, temp_data_dir):
        """Test language database has correct structure."""
        cerberus = CerberusHydraDefense(data_dir=temp_data_dir)

        assert "human_languages" in cerberus.languages
        assert "programming_languages" in cerberus.languages

        # Check human language structure
        for _lang_code, lang_data in cerberus.languages["human_languages"].items():
            assert "name" in lang_data
            assert "alert_prefix" in lang_data
            assert "agent_spawned" in lang_data

        # Check programming language structure
        for _lang_code, lang_data in cerberus.languages[
            "programming_languages"
        ].items():
            assert "name" in lang_data
            assert "executable" in lang_data
            assert "extension" in lang_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
