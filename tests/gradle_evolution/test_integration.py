"""
Tests for Gradle Evolution Integration.

End-to-end integration tests validating complete workflows
across constitutional, cognition, capsule, security, and audit systems.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from gradle_evolution.constitutional.engine import ConstitutionalEngine
from gradle_evolution.constitutional.enforcer import ConstitutionalEnforcer
from gradle_evolution.cognition.build_cognition import BuildCognitionEngine
from gradle_evolution.cognition.state_integration import BuildStateIntegration
from gradle_evolution.capsules.capsule_engine import CapsuleEngine, BuildCapsule
from gradle_evolution.capsules.replay_engine import ReplayEngine
from gradle_evolution.security.security_engine import SecurityEngine
from gradle_evolution.audit.audit_integration import BuildAuditIntegration
from gradle_evolution.audit.accountability import AccountabilitySystem
from gradle_evolution.api.verifiability_api import VerifiabilityAPI


class TestFullBuildWorkflow:
    """Test complete build workflow integration."""
    
    @pytest.fixture
    def integrated_system(self, temp_dir, constitution_file, security_config_file):
        """Create fully integrated system."""
        # Constitutional layer
        const_engine = ConstitutionalEngine(constitution_path=str(constitution_file))
        enforcer = ConstitutionalEnforcer(const_engine)
        
        # Security layer
        security = SecurityEngine(config_path=security_config_file)
        
        # Audit layer
        audit_path = temp_dir / "audit.log"
        audit = BuildAuditIntegration(audit_log_path=audit_path)
        
        # Accountability
        accountability_path = temp_dir / "accountability.json"
        accountability = AccountabilitySystem(storage_path=accountability_path)
        
        # Capsule layer
        capsule_storage = temp_dir / "capsules"
        capsule_storage.mkdir()
        capsule_engine = CapsuleEngine(storage_path=capsule_storage)
        replay_engine = ReplayEngine(capsule_engine)
        
        # Cognition layer (with mock)
        mock_deliberation = MagicMock()
        mock_deliberation.deliberate.return_value = {
            "optimized_order": ["clean", "compile", "test"],
            "reasoning": {"optimization_applied": True}
        }
        cognition = BuildCognitionEngine(mock_deliberation)
        
        # State integration
        state_storage = temp_dir / "build_state.json"
        state_integration = BuildStateIntegration(storage_path=state_storage)
        
        return {
            "constitution": const_engine,
            "enforcer": enforcer,
            "security": security,
            "audit": audit,
            "accountability": accountability,
            "capsules": capsule_engine,
            "replay": replay_engine,
            "cognition": cognition,
            "state": state_integration,
        }
    
    def test_complete_build_lifecycle(self, integrated_system):
        """Test complete build from start to finish."""
        build_id = "integration-build-001"
        tasks = ["clean", "compile", "test"]
        context = {
            "project": "test-project",
            "violations": [],  # No violations
        }
        
        # Step 1: Constitutional validation
        is_allowed, reason = integrated_system["constitution"].validate_build_action(
            "build",
            context
        )
        assert is_allowed, f"Build blocked: {reason}"
        
        # Step 2: Security validation
        security_context = integrated_system["security"].get_security_context("build_agent")
        assert security_context is not None
        
        # Step 3: Audit build start
        with patch("gradle_evolution.audit.audit_integration.audit"):
            integrated_system["audit"].audit_build_start(build_id, tasks, context)
        
        # Step 4: Cognitive optimization
        with patch("gradle_evolution.cognition.build_cognition.check_boundary", return_value=True):
            optimized_tasks, reasoning = integrated_system["cognition"].deliberate_build_plan(
                tasks,
                context
            )
        assert len(optimized_tasks) > 0
        
        # Step 5: Record build state
        state = {
            "tasks": optimized_tasks,
            "status": "in_progress",
            "start_time": "2024-01-01T00:00:00Z"
        }
        integrated_system["state"].record_build_state(build_id, state)
        
        # Step 6: Create build capsule
        inputs = {"src/Main.java": "abc123"}
        outputs = {"build/Main.class": "def456"}
        metadata = {"timestamp": "2024-01-01T00:00:00Z", "duration": 45.2}
        
        capsule = integrated_system["capsules"].create_capsule(
            optimized_tasks,
            inputs,
            outputs,
            metadata
        )
        assert capsule is not None
        
        # Step 7: Audit completion
        with patch("gradle_evolution.audit.audit_integration.audit"):
            integrated_system["audit"].audit_build_complete(
                build_id,
                success=True,
                duration_seconds=45.2,
                result={"status": "success"}
            )
        
        # Verify integration
        assert build_id in integrated_system["state"].build_states
        assert capsule.capsule_id in integrated_system["capsules"].capsules
    
    def test_security_violation_workflow(self, integrated_system):
        """Test workflow with security violation."""
        build_id = "security-test-001"
        tasks = ["deploy"]
        context = {"violations": ["security_violation"]}
        
        # Constitutional check should block
        is_allowed, reason = integrated_system["constitution"].validate_build_action(
            "deploy",
            context
        )
        
        assert not is_allowed
        assert "security_violation" in reason
        
        # Violation should be logged
        assert len(integrated_system["constitution"].violation_log) > 0
    
    def test_capsule_replay_workflow(self, integrated_system, sample_build_capsule_data):
        """Test capsule creation and replay workflow."""
        # Create original capsule
        capsule = BuildCapsule(**sample_build_capsule_data)
        integrated_system["capsules"].capsules[capsule.capsule_id] = capsule
        
        # Verify integrity
        is_valid = integrated_system["capsules"].verify_capsule(capsule.capsule_id)
        assert is_valid
        
        # Replay capsule
        result = integrated_system["replay"].replay_build(capsule.capsule_id)
        assert result.capsule_id == capsule.capsule_id
        
        # Check replay history
        history = integrated_system["replay"].get_replay_history()
        assert len(history) > 0
    
    def test_multi_build_pattern_learning(self, integrated_system):
        """Test pattern learning across multiple builds."""
        context = {"cache_enabled": True}
        
        # Simulate multiple builds
        for i in range(3):
            tasks = ["clean", "compile", "test"]
            with patch("gradle_evolution.cognition.build_cognition.check_boundary", return_value=True):
                optimized, reasoning = integrated_system["cognition"].deliberate_build_plan(
                    tasks,
                    context
                )
            
            # Record learning
            integrated_system["cognition"].learn_from_build(
                f"build-{i}",
                optimized,
                {"duration_seconds": 40 + i, "success": True}
            )
        
        # Check that patterns are learned
        stats = integrated_system["cognition"].get_optimization_stats()
        assert stats["total_optimizations"] == 3


class TestAPIIntegration:
    """Test API integration with backend components."""
    
    @pytest.fixture
    def api_system(self, temp_dir):
        """Create API-integrated system."""
        capsule_storage = temp_dir / "capsules"
        capsule_storage.mkdir()
        audit_path = temp_dir / "audit.log"
        
        capsule_engine = CapsuleEngine(storage_path=capsule_storage)
        replay_engine = ReplayEngine(capsule_engine)
        audit = BuildAuditIntegration(audit_log_path=audit_path)
        
        api = VerifiabilityAPI(
            capsule_engine=capsule_engine,
            replay_engine=replay_engine,
            audit_integration=audit,
            host="localhost",
            port=8080
        )
        
        api.app.config['TESTING'] = True
        return api
    
    def test_api_capsule_workflow(self, api_system, sample_build_capsule_data):
        """Test full API workflow for capsule operations."""
        # Create capsule via engine
        capsule = BuildCapsule(**sample_build_capsule_data)
        api_system.capsule_engine.capsules[capsule.capsule_id] = capsule
        
        with api_system.app.test_client() as client:
            # List capsules
            response = client.get("/api/v1/capsules")
            assert response.status_code == 200
            
            # Get specific capsule
            response = client.get(f"/api/v1/capsules/{capsule.capsule_id}")
            assert response.status_code == 200
            
            # Verify capsule
            response = client.post(f"/api/v1/capsules/{capsule.capsule_id}/verify")
            assert response.status_code == 200


class TestErrorRecovery:
    """Test error handling and recovery across components."""
    
    def test_constitutional_engine_error_recovery(self, temp_dir):
        """Test engine recovers from missing constitution."""
        nonexistent = temp_dir / "missing.yaml"
        engine = ConstitutionalEngine(constitution_path=str(nonexistent))
        
        # Should use default constitution
        assert engine.constitution is not None
        
        # Should still validate actions
        is_allowed, _ = engine.validate_build_action("compile", context={})
        assert isinstance(is_allowed, bool)
    
    def test_capsule_integrity_failure(self, capsule_storage, sample_build_capsule_data):
        """Test handling of capsule integrity failure."""
        engine = CapsuleEngine(storage_path=capsule_storage)
        
        capsule = BuildCapsule(**sample_build_capsule_data)
        engine.capsules[capsule.capsule_id] = capsule
        
        # Tamper with capsule
        capsule.tasks.append("malicious_task")
        
        # Verification should detect tampering
        new_merkle = capsule._compute_merkle_root()
        assert new_merkle != capsule.merkle_root
    
    def test_security_engine_config_error(self, temp_dir):
        """Test security engine handles config errors."""
        bad_config = temp_dir / "bad_config.yaml"
        bad_config.write_text("invalid: yaml: content: [")
        
        engine = SecurityEngine(config_path=bad_config)
        
        # Should fall back to defaults
        assert engine.config is not None
    
    def test_audit_integration_error_handling(self, audit_log_path):
        """Test audit integration handles errors gracefully."""
        integration = BuildAuditIntegration(audit_log_path=audit_log_path)
        
        # Audit should not crash with bad data
        with patch("gradle_evolution.audit.audit_integration.audit", side_effect=Exception("Audit error")):
            integration.audit_build_start("test", [], {})
        
        # Integration should still be usable
        assert integration.audit_buffer is not None


class TestPerformanceAndScalability:
    """Test performance characteristics and scalability."""
    
    def test_large_capsule_set(self, capsule_storage):
        """Test handling large number of capsules."""
        engine = CapsuleEngine(storage_path=capsule_storage)
        
        # Create many capsules
        capsule_count = 100
        for i in range(capsule_count):
            capsule = engine.create_capsule(
                tasks=[f"task-{i}"],
                inputs={f"input-{i}": f"hash-{i}"},
                outputs={f"output-{i}": f"hash-{i}"},
                metadata={"index": i}
            )
        
        # Should handle efficiently
        assert len(engine.capsules) == capsule_count
        
        # List operation should work
        capsules = engine.list_capsules()
        assert len(capsules) == capsule_count
    
    def test_large_audit_buffer(self, audit_log_path):
        """Test audit integration with many events."""
        integration = BuildAuditIntegration(audit_log_path=audit_log_path)
        
        with patch("gradle_evolution.audit.audit_integration.audit"):
            # Generate many audit events
            for i in range(200):
                integration.audit_build_start(f"build-{i}", ["task"], {})
        
        # Should buffer efficiently
        assert len(integration.audit_buffer) == 200
        
        # Summary should work
        summary = integration.get_audit_summary()
        assert summary["total_events"] == 200
