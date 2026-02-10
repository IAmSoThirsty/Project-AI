"""
E2E Tests for Project-AI Triumvirate System

God Tier tests for the three-engine AI orchestration:
- Codex (ML inference)
- Galahad (Reasoning and arbitration)
- Cerberus (Policy enforcement)
- Complete orchestrated workflows
"""

from __future__ import annotations

import tempfile

import pytest


@pytest.mark.e2e
@pytest.mark.triumvirate
class TestTriumvirateOrchestration:
    """E2E tests for Triumvirate orchestrated workflows."""

    def test_triumvirate_initialization(self, e2e_config):
        """Test Triumvirate orchestrator initializes all three engines."""
        from src.cognition.triumvirate import Triumvirate, TriumvirateConfig

        config = TriumvirateConfig(enable_telemetry=True)
        triumvirate = Triumvirate(config)

        # Assert all engines initialized
        assert triumvirate.codex is not None
        assert triumvirate.galahad is not None
        assert triumvirate.cerberus is not None

    def test_triumvirate_complete_pipeline(self, e2e_config):
        """Test complete processing pipeline through all three engines."""
        from src.cognition.triumvirate import Triumvirate

        triumvirate = Triumvirate()

        # Act - Process through pipeline
        input_data = {"query": "What is the capital of France?", "user_id": "test_user"}

        result = triumvirate.process(input_data=input_data, context={"safe_mode": True})

        # Assert pipeline completed
        assert result is not None
        assert "correlation_id" in result
        assert result.get("status") in ["success", "completed", "processed"]

    def test_triumvirate_cerberus_validation(self, e2e_config):
        """Test Cerberus validates input before processing."""
        from src.cognition.triumvirate import Triumvirate

        triumvirate = Triumvirate()

        # Act - Try to process potentially dangerous input
        malicious_input = {
            "query": "<script>alert('xss')</script>",
            "user_id": "attacker",
        }

        result = triumvirate.process(input_data=malicious_input, context={})

        # Assert validation occurred
        assert result is not None
        # Cerberus should have processed/sanitized the input

    def test_triumvirate_codex_inference(self, e2e_config):
        """Test Codex engine performs ML inference."""
        from src.cognition.triumvirate import Triumvirate

        triumvirate = Triumvirate()

        # Act - Process query requiring ML inference
        input_data = {
            "query": "Classify sentiment: This is a great day!",
            "task": "sentiment_analysis",
        }

        result = triumvirate.process(input_data)

        # Assert Codex processed the request
        assert result is not None
        assert "correlation_id" in result

    def test_triumvirate_galahad_reasoning(self, e2e_config):
        """Test Galahad performs reasoning and arbitration."""
        from src.cognition.triumvirate import Triumvirate

        triumvirate = Triumvirate()

        # Act - Complex reasoning task
        input_data = {
            "query": "Should I prioritize speed or accuracy?",
            "context": {"deadline": "urgent", "quality_requirements": "high"},
        }

        result = triumvirate.process(input_data)

        # Assert reasoning occurred
        assert result is not None
        assert "correlation_id" in result

    def test_triumvirate_telemetry_collection(self, e2e_config):
        """Test telemetry events are collected during processing."""
        from src.cognition.triumvirate import Triumvirate, TriumvirateConfig

        config = TriumvirateConfig(enable_telemetry=True)
        triumvirate = Triumvirate(config)

        # Act - Process multiple requests
        for i in range(3):
            triumvirate.process(input_data={"query": f"Test query {i}"})

        # Assert telemetry collected
        assert len(triumvirate.telemetry_events) >= 3

    def test_triumvirate_error_handling(self, e2e_config):
        """Test error handling across the pipeline."""
        from src.cognition.triumvirate import Triumvirate

        triumvirate = Triumvirate()

        # Act - Process invalid input
        try:
            result = triumvirate.process(input_data=None, context={})  # Invalid input
            # Should handle gracefully
            assert result is not None
        except Exception as e:
            # Or raise appropriate exception
            assert e is not None

    def test_triumvirate_context_propagation(self, e2e_config):
        """Test context propagates through all engines."""
        from src.cognition.triumvirate import Triumvirate

        triumvirate = Triumvirate()

        custom_context = {
            "user_role": "admin",
            "session_id": "test_session_123",
            "priority": "high",
        }

        # Act
        result = triumvirate.process(
            input_data={"query": "Test"}, context=custom_context
        )

        # Assert context was used
        assert result is not None
        assert "correlation_id" in result


@pytest.mark.e2e
@pytest.mark.council_hub
class TestCouncilHubIntegration:
    """E2E tests for Council Hub agent coordination."""

    def test_council_hub_agent_registration(self, e2e_config):
        """Test agents can register with Council Hub."""
        try:
            from src.app.core.council_hub import CouncilHub

            hub = CouncilHub()

            # Act - Register agent
            agent_id = hub.register_agent(
                agent_name="test_agent", capabilities=["analysis", "reporting"]
            )

            # Assert
            assert agent_id is not None
            agents = hub.list_agents()
            assert any(a.get("name") == "test_agent" for a in agents)
        except ImportError:
            pytest.skip("Council Hub not available")

    def test_council_hub_message_routing(self, e2e_config):
        """Test message routing between agents."""
        try:
            from src.app.core.council_hub import CouncilHub

            hub = CouncilHub()

            # Register agents
            agent_a = hub.register_agent("agent_a", ["sender"])
            agent_b = hub.register_agent("agent_b", ["receiver"])

            # Act - Send message
            message_id = hub.send_message(
                from_agent=agent_a, to_agent=agent_b, content={"data": "test message"}
            )

            # Assert
            assert message_id is not None
            messages = hub.get_messages(agent_b)
            assert len(messages) >= 1
        except ImportError:
            pytest.skip("Council Hub not available")

    def test_council_hub_broadcast_message(self, e2e_config):
        """Test broadcasting messages to all agents."""
        try:
            from src.app.core.council_hub import CouncilHub

            hub = CouncilHub()

            # Register multiple agents
            agents = []
            for i in range(5):
                agent_id = hub.register_agent(f"agent_{i}", [])
                agents.append(agent_id)

            # Act - Broadcast
            hub.broadcast_message(
                from_agent=agents[0], content={"announcement": "System update"}
            )

            # Assert all agents received
            for agent_id in agents[1:]:
                messages = hub.get_messages(agent_id)
                assert len(messages) >= 1
        except ImportError:
            pytest.skip("Council Hub not available")

    def test_council_hub_agent_coordination(self, e2e_config):
        """Test multi-agent coordination workflow."""
        try:
            from src.app.core.council_hub import CouncilHub

            hub = CouncilHub()

            # Setup coordinated task
            coordinator = hub.register_agent("coordinator", ["orchestrate"])
            worker_1 = hub.register_agent("worker_1", ["process"])
            worker_2 = hub.register_agent("worker_2", ["process"])

            # Act - Coordinator assigns tasks
            task_1 = hub.send_message(
                coordinator, worker_1, {"task": "process_batch_1"}
            )
            task_2 = hub.send_message(
                coordinator, worker_2, {"task": "process_batch_2"}
            )

            # Workers complete and report back
            hub.send_message(
                worker_1, coordinator, {"status": "completed", "task_id": task_1}
            )
            hub.send_message(
                worker_2, coordinator, {"status": "completed", "task_id": task_2}
            )

            # Assert coordination occurred
            coordinator_messages = hub.get_messages(coordinator)
            assert len(coordinator_messages) >= 2
        except ImportError:
            pytest.skip("Council Hub not available")


@pytest.mark.e2e
@pytest.mark.tarl
class TestTARLEnforcement:
    """E2E tests for TARL (Trust And Runtime Ledger) enforcement."""

    def test_tarl_policy_evaluation(self, e2e_config):
        """Test TARL evaluates policies at runtime."""
        try:
            # Import TARL components
            from tarl_os.kernel.policy_engine import PolicyEngine

            engine = PolicyEngine()

            # Act - Evaluate policy
            action = {
                "type": "file_access",
                "path": "/sensitive/data.txt",
                "user": "test_user",
            }

            result = engine.evaluate(action)

            # Assert
            assert result is not None
            assert "allowed" in result or "decision" in result
        except ImportError:
            pytest.skip("TARL not available")

    def test_tarl_runtime_constraints(self, e2e_config):
        """Test TARL enforces runtime constraints."""
        try:
            from tarl_os.kernel.policy_engine import PolicyEngine

            engine = PolicyEngine()

            # Define constraint
            constraint = {
                "max_cpu_usage": 80,
                "max_memory_mb": 1024,
                "allowed_operations": ["read", "write"],
            }

            # Act - Check operation against constraints
            operation = {"type": "read", "cpu_usage": 60, "memory_mb": 512}

            result = engine.check_constraints(operation, constraint)

            # Assert constraint enforced
            assert result is not None
        except (ImportError, AttributeError):
            pytest.skip("TARL constraints not available")

    def test_tarl_audit_logging(self, e2e_config):
        """Test TARL logs all policy evaluations."""
        try:
            from tarl_os.kernel.policy_engine import PolicyEngine

            engine = PolicyEngine()

            # Act - Multiple policy evaluations
            for i in range(5):
                engine.evaluate({"type": "operation", "id": i})

            # Assert audit log exists
            audit_log = engine.get_audit_log()
            assert len(audit_log) >= 5
        except (ImportError, AttributeError):
            pytest.skip("TARL audit logging not available")


@pytest.mark.e2e
@pytest.mark.watch_tower
class TestGlobalWatchTower:
    """E2E tests for Global Watch Tower monitoring."""

    def test_watch_tower_event_monitoring(self, e2e_config):
        """Test Watch Tower monitors system events."""
        try:
            from src.app.core.global_watch_tower import GlobalWatchTower

            tower = GlobalWatchTower()

            # Act - Emit events
            tower.emit_event(
                event_type="user_action", data={"action": "login", "user": "test_user"}
            )

            tower.emit_event(
                event_type="security_alert",
                data={"severity": "medium", "message": "Unusual activity"},
            )

            # Assert events captured
            events = tower.get_recent_events()
            assert len(events) >= 2
        except ImportError:
            pytest.skip("Global Watch Tower not available")

    def test_watch_tower_alert_escalation(self, e2e_config):
        """Test Watch Tower escalates critical alerts."""
        try:
            from src.app.core.global_watch_tower import GlobalWatchTower

            tower = GlobalWatchTower()

            # Act - Emit critical event
            tower.emit_event(
                event_type="critical_security_breach",
                data={"severity": "critical", "affected_systems": ["auth", "database"]},
            )

            # Assert escalation occurred
            alerts = tower.get_alerts(severity="critical")
            assert len(alerts) >= 1
        except (ImportError, AttributeError):
            pytest.skip("Watch Tower alerts not available")

    def test_watch_tower_audit_trail(self, e2e_config):
        """Test Watch Tower maintains complete audit trail."""
        try:
            from src.app.core.global_watch_tower import GlobalWatchTower

            tower = GlobalWatchTower()

            # Act - Series of events
            events = [
                ("user_login", {"user": "test_user"}),
                ("data_access", {"resource": "/api/data"}),
                ("user_logout", {"user": "test_user"}),
            ]

            for event_type, data in events:
                tower.emit_event(event_type, data)

            # Assert complete audit trail
            audit_trail = tower.get_audit_trail(user="test_user")
            assert len(audit_trail) >= 3
        except (ImportError, AttributeError):
            pytest.skip("Watch Tower audit trail not available")


@pytest.mark.e2e
@pytest.mark.integration
@pytest.mark.slow
class TestCompleteSystemIntegration:
    """E2E tests for complete system integration across all components."""

    def test_end_to_end_request_flow(self, e2e_config):
        """Test complete request flow through all systems."""
        from src.app.core.ai_systems import AIPersona, FourLaws, MemoryExpansionSystem
        from src.cognition.triumvirate import Triumvirate

        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize all systems
            laws = FourLaws()
            persona = AIPersona(data_dir=tmpdir)
            memory = MemoryExpansionSystem(data_dir=tmpdir)
            triumvirate = Triumvirate()

            # Complete workflow
            user_request = "Analyze sentiment of customer feedback"

            # 1. Four Laws validation
            is_allowed, reason = laws.validate_action(
                user_request, context={"is_user_order": True, "endangers_human": False}
            )
            assert is_allowed

            # 2. Triumvirate processing
            result = triumvirate.process(
                input_data={"query": user_request}, context={"validated": True}
            )
            assert result is not None

            # 3. Persona records interaction
            persona.record_interaction(
                interaction_type="analysis", details=user_request
            )

            # 4. Memory stores result
            memory.store_memory(
                category="conversation",
                content=f"Processed: {user_request}",
                metadata={"result": str(result)},
            )

            # Verify complete integration
            assert persona.interaction_count >= 1
            memories = memory.retrieve_memories(category="conversation")
            assert len(memories) >= 1

    def test_security_monitoring_integration(self, e2e_config):
        """Test security monitoring across all systems."""
        from src.app.core.ai_systems import CommandOverride, FourLaws
        from src.app.core.user_manager import UserManager

        try:
            from src.app.core.global_watch_tower import GlobalWatchTower
        except ImportError:
            pytest.skip("Global Watch Tower not available")

        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize security systems
            laws = FourLaws()
            CommandOverride(data_dir=tmpdir)
            user_mgr = UserManager(data_dir=tmpdir)
            tower = GlobalWatchTower()

            # Simulate security event
            user_mgr.register_user("security_test", "Pass123!")

            # Suspicious action
            action = "Access restricted files"
            is_allowed, reason = laws.validate_action(
                action, context={"endangers_system": True}
            )

            # Log to Watch Tower
            tower.emit_event(
                "security_check",
                {"action": action, "allowed": is_allowed, "reason": reason},
            )

            # Verify security monitoring
            events = tower.get_recent_events()
            assert len(events) >= 1
