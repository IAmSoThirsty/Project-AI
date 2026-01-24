"""
Tests for T.A.R.L. Deterministic Orchestration System

Validates:
- Deterministic execution (logical clock)
- Structured capabilities
- Agent orchestration
- Record & replay
- Provenance & SBOM
"""

import tempfile

import pytest

from project_ai.tarl.integrations.orchestration import (
    AgentOrchestrator,
    Artifact,
    ArtifactRelationship,
    Capability,
    CapabilityEngine,
    DeterministicVM,
    EventRecorder,
    Policy,
    ProvenanceManager,
    TarlStackBox,
    Workflow,
    WorkflowEventKind,
)


class TestDeterministicVM:
    """Test deterministic VM with logical clock"""

    def test_logical_clock_determinism(self):
        """Verify logical clock is deterministic (no time.time())"""
        vm = DeterministicVM(data_dir=tempfile.mkdtemp())

        # Get sequence numbers
        seq1 = vm._next_sequence()
        seq2 = vm._next_sequence()
        seq3 = vm._next_sequence()

        # Should be monotonic integers
        assert seq1 == 1
        assert seq2 == 2
        assert seq3 == 3

    def test_workflow_registration(self):
        """Test workflow registration"""
        vm = DeterministicVM(data_dir=tempfile.mkdtemp())

        def dummy_workflow(vm_instance, context):
            return "result"

        workflow = Workflow(
            workflow_id="test_wf",
            entrypoint=dummy_workflow,
            required_caps={"Net.Connect"},
        )

        vm.register_workflow(workflow)

        assert "test_wf" in vm._workflows
        assert vm._workflows["test_wf"] == workflow

    def test_workflow_execution(self):
        """Test workflow execution with event logging"""
        vm = DeterministicVM(data_dir=tempfile.mkdtemp())

        execution_count = [0]

        def test_workflow(vm_instance, context):
            execution_count[0] += 1
            return {"status": "success", "count": execution_count[0]}

        workflow = Workflow(workflow_id="exec_test", entrypoint=test_workflow)
        vm.register_workflow(workflow)

        result = vm.execute_workflow("exec_test", context={"mode": "test"})

        assert result["status"] == "success"
        assert result["count"] == 1
        assert vm._workflow_state["exec_test"]["status"] == "completed"

        # Check event log
        events = vm.get_event_log("exec_test")
        assert len(events) >= 2  # At least START and RETURN

        start_events = [e for e in events if e.kind == WorkflowEventKind.START]
        return_events = [e for e in events if e.kind == WorkflowEventKind.RETURN]

        assert len(start_events) == 1
        assert len(return_events) == 1

    def test_snapshot_determinism(self):
        """Test snapshots use hash-based IDs, not time"""
        vm = DeterministicVM(data_dir=tempfile.mkdtemp())

        def snapshot_workflow(vm_instance, context):
            return "result"

        workflow = Workflow(workflow_id="snap_test", entrypoint=snapshot_workflow)
        vm.register_workflow(workflow)

        vm.execute_workflow("snap_test")

        # Take snapshot
        snap_hash1 = vm.snapshot("snap_test")

        # Hash should be deterministic SHA-256
        assert len(snap_hash1) == 64  # SHA-256 hex
        assert snap_hash1 in vm._snapshots

        # Note: Each snapshot increments counter, so hashes will differ
        # But both should be valid SHA-256 hashes
        snap_hash2 = vm.snapshot("snap_test")
        assert len(snap_hash2) == 64  # Also SHA-256
        assert snap_hash2 in vm._snapshots

    def test_snapshot_restore(self):
        """Test snapshot restoration"""
        vm = DeterministicVM(data_dir=tempfile.mkdtemp())

        def state_workflow(vm_instance, context):
            return "modified"

        workflow = Workflow(workflow_id="state_test", entrypoint=state_workflow)
        vm.register_workflow(workflow)

        vm.execute_workflow("state_test")
        vm._workflow_state["state_test"]["custom_field"] = "test_value"

        # Take snapshot
        snap_hash = vm.snapshot("state_test")

        # Modify state
        vm._workflow_state["state_test"]["custom_field"] = "different_value"

        # Restore
        vm.restore_snapshot(snap_hash)

        # Should be back to snapshot state
        assert vm._workflow_state["state_test"]["custom_field"] == "test_value"

    def test_error_handling(self):
        """Test error event recording"""
        vm = DeterministicVM(data_dir=tempfile.mkdtemp())

        def failing_workflow(vm_instance, context):
            raise ValueError("Test error")

        workflow = Workflow(workflow_id="error_test", entrypoint=failing_workflow)
        vm.register_workflow(workflow)

        with pytest.raises(ValueError, match="Test error"):
            vm.execute_workflow("error_test")

        # Check error event was logged
        events = vm.get_event_log("error_test")
        error_events = [e for e in events if e.kind == WorkflowEventKind.ERROR]

        assert len(error_events) == 1
        assert "error" in error_events[0].payload
        assert "error_id" in error_events[0].payload

    def test_state_persistence(self):
        """Test VM state persistence"""
        temp_dir = tempfile.mkdtemp()
        vm = DeterministicVM(data_dir=temp_dir)

        def persist_workflow(vm_instance, context):
            return "persisted"

        workflow = Workflow(workflow_id="persist_test", entrypoint=persist_workflow)
        vm.register_workflow(workflow)
        vm.execute_workflow("persist_test")

        # Persist
        vm.persist_state()

        # Create new VM and load
        vm2 = DeterministicVM(data_dir=temp_dir)
        vm2.load_state()

        # State should be loaded
        assert vm2._counter == vm._counter
        assert "persist_test" in vm2._workflow_state


class TestStructuredCapabilities:
    """Test structured capability system"""

    def test_capability_creation(self):
        """Test capability with structured constraints"""
        cap = Capability(
            name="Net.Connect",
            resource="network",
            constraints={"protocol": "https", "ca": "TrustedCA"},
        )

        assert cap.name == "Net.Connect"
        assert cap.resource == "network"
        assert cap.constraints["protocol"] == "https"

    def test_capability_hash_determinism(self):
        """Test capability hash is deterministic"""
        cap1 = Capability(name="Test.Cap", resource="test", constraints={"key": "value"})
        cap2 = Capability(name="Test.Cap", resource="test", constraints={"key": "value"})

        # Same content = same hash
        assert hash(cap1) == hash(cap2)

    def test_policy_evaluation(self):
        """Test declarative policy evaluation"""
        cap = Capability(
            name="File.Read", resource="filesystem", constraints={"path_prefix": "/data"}
        )

        policy = Policy(
            name="RestrictFileAccess",
            capability_name="File.Read",
            constraints={"path_prefix": "/data"},
        )

        allowed, reason = policy.evaluate(cap, context={})

        assert allowed is True
        assert "satisfied" in reason.lower()

    def test_policy_rejection(self):
        """Test policy rejection"""
        cap = Capability(name="File.Read", resource="filesystem", constraints={"path_prefix": "/tmp"})

        policy = Policy(
            name="RestrictFileAccess",
            capability_name="File.Read",
            constraints={"path_prefix": "/data"},
        )

        allowed, reason = policy.evaluate(cap, context={})

        assert allowed is False
        assert "does not match" in reason.lower()


class TestCapabilityEngine:
    """Test capability engine"""

    def test_capability_registration(self):
        """Test capability registration"""
        engine = CapabilityEngine()

        cap = Capability(name="Test.Cap", resource="test")
        engine.register_capability(cap)

        assert "Test.Cap" in engine._registry

    def test_workflow_verification_success(self):
        """Test successful workflow verification"""
        engine = CapabilityEngine()

        cap = Capability(name="Net.Connect", resource="network")
        engine.register_capability(cap)

        workflow = Workflow(
            workflow_id="test_wf",
            entrypoint=lambda vm, ctx: None,
            required_caps={"Net.Connect"},
        )

        allowed, reasons = engine.verify_workflow(workflow)

        assert allowed is True

    def test_workflow_verification_failure(self):
        """Test workflow verification failure"""
        engine = CapabilityEngine()

        workflow = Workflow(
            workflow_id="test_wf",
            entrypoint=lambda vm, ctx: None,
            required_caps={"NonExistent.Cap"},
        )

        allowed, reasons = engine.verify_workflow(workflow)

        assert allowed is False
        assert any("not found" in r.lower() for r in reasons)

    def test_runtime_capability_check(self):
        """Test runtime capability checking"""
        engine = CapabilityEngine()

        cap = Capability(name="API.Call", resource="network")
        engine.register_capability(cap)

        policy = Policy(
            name="AllowAPI", capability_name="API.Call", constraints={}, enforcement_level="required"
        )
        engine.register_policy(policy)

        allowed, reason = engine.check_capability("API.Call", context={})

        assert allowed is True

    def test_usage_log(self):
        """Test capability usage logging"""
        engine = CapabilityEngine()

        cap = Capability(name="Test.Cap", resource="test")
        engine.register_capability(cap)

        engine.check_capability("Test.Cap", context={"user": "test"})

        log = engine.get_usage_log()
        assert len(log) >= 1
        assert log[-1]["capability"] == "Test.Cap"


class TestAgentOrchestrator:
    """Test agent orchestration patterns"""

    def test_agent_registration(self):
        """Test agent registration"""
        vm = DeterministicVM(data_dir=tempfile.mkdtemp())
        orch = AgentOrchestrator(vm)

        def test_agent(input_data):
            return f"processed: {input_data}"

        orch.register_agent("test_agent", test_agent)

        assert "test_agent" in orch._agent_registry

    def test_sequential_orchestration(self):
        """Test sequential agent execution"""
        vm = DeterministicVM(data_dir=tempfile.mkdtemp())
        orch = AgentOrchestrator(vm)

        workflow = Workflow(workflow_id="seq_test", entrypoint=lambda vm, ctx: None)
        vm.register_workflow(workflow)

        orch.register_agent("agent1", lambda x: f"{x}->A1")
        orch.register_agent("agent2", lambda x: f"{x}->A2")
        orch.register_agent("agent3", lambda x: f"{x}->A3")

        result = orch.sequential("seq_test", ["agent1", "agent2", "agent3"], "start")

        assert result == "start->A1->A2->A3"

    def test_concurrent_orchestration(self):
        """Test concurrent agent execution"""
        vm = DeterministicVM(data_dir=tempfile.mkdtemp())
        orch = AgentOrchestrator(vm)

        workflow = Workflow(workflow_id="conc_test", entrypoint=lambda vm, ctx: None)
        vm.register_workflow(workflow)

        orch.register_agent("agent1", lambda x: f"A1({x})")
        orch.register_agent("agent2", lambda x: f"A2({x})")

        results = orch.concurrent("conc_test", ["agent1", "agent2"], ["input1", "input2"])

        assert results == ["A1(input1)", "A2(input2)"]

    def test_chat_orchestration(self):
        """Test chat agent pattern"""
        vm = DeterministicVM(data_dir=tempfile.mkdtemp())
        orch = AgentOrchestrator(vm)

        workflow = Workflow(workflow_id="chat_test", entrypoint=lambda vm, ctx: None)
        vm.register_workflow(workflow)

        orch.register_agent("agent1", lambda history: f"A1 response to: {history[-1]}")
        orch.register_agent("agent2", lambda history: f"A2 response to: {history[-1]}")

        conversation = orch.chat("chat_test", ["agent1", "agent2"], "Hello", max_turns=4)

        assert len(conversation) == 5  # Initial + 4 turns
        assert conversation[0] == "Hello"
        assert "A1 response" in conversation[1]
        assert "A2 response" in conversation[2]

    def test_graph_orchestration(self):
        """Test graph-based agent execution"""
        vm = DeterministicVM(data_dir=tempfile.mkdtemp())
        orch = AgentOrchestrator(vm)

        workflow = Workflow(workflow_id="graph_test", entrypoint=lambda vm, ctx: None)
        vm.register_workflow(workflow)

        orch.register_agent("planner", lambda x: f"Plan({x})")
        orch.register_agent("executor", lambda x: f"Execute({x})")
        orch.register_agent("validator", lambda x: f"Validate({x})")

        graph_spec = {"planner": ["executor"], "executor": ["validator"], "validator": []}

        result = orch.graph("graph_test", graph_spec, "planner", "start")

        assert result == "Validate(Execute(Plan(start)))"


class TestEventRecorder:
    """Test record & replay system"""

    def test_external_call_recording(self):
        """Test recording of external calls"""
        vm = DeterministicVM(data_dir=tempfile.mkdtemp())
        recorder = EventRecorder(vm, data_dir=tempfile.mkdtemp())

        workflow = Workflow(workflow_id="rec_test", entrypoint=lambda vm, ctx: None)
        vm.register_workflow(workflow)

        recorder.record_external_call(
            workflow_id="rec_test",
            call_type="api",
            call_args={"endpoint": "test.com"},
            call_result={"data": "result"},
        )

        assert len(recorder._external_events["rec_test"]) == 1
        assert recorder._external_events["rec_test"][0]["call_type"] == "api"

    def test_recording_persistence(self):
        """Test saving and loading recordings"""
        temp_dir = tempfile.mkdtemp()
        vm = DeterministicVM(data_dir=tempfile.mkdtemp())
        recorder = EventRecorder(vm, data_dir=temp_dir)

        workflow = Workflow(workflow_id="persist_rec_test", entrypoint=lambda vm, ctx: "result")
        vm.register_workflow(workflow)
        vm.execute_workflow("persist_rec_test")

        recorder.record_external_call(
            "persist_rec_test", "llm", {"prompt": "test"}, {"response": "output"}
        )

        # Save recording
        recorder.save_recording("persist_rec_test", "test_recording")

        # Load in new recorder
        recorder2 = EventRecorder(vm, data_dir=temp_dir)
        recording = recorder2.load_recording("test_recording")

        assert recording["workflow_id"] == "persist_rec_test"
        assert len(recording["event_log"]) > 0

    def test_replay_mode(self):
        """Test replay mode detection"""
        vm = DeterministicVM(data_dir=tempfile.mkdtemp())
        recorder = EventRecorder(vm, data_dir=tempfile.mkdtemp())

        assert recorder.is_replay_mode() is False

        # Set replay mode
        vm._replay_mode = True
        assert recorder.is_replay_mode() is True


class TestProvenanceManager:
    """Test provenance & SBOM system"""

    def test_artifact_registration(self):
        """Test artifact registration"""
        prov = ProvenanceManager(data_dir=tempfile.mkdtemp())

        artifact = Artifact(
            artifact_id="test_artifact",
            kind="module",
            version="1.0.0",
            content_hash="abcd1234",
        )

        prov.register_artifact(artifact)

        assert "test_artifact" in prov._artifacts

    def test_relationship_tracking(self):
        """Test artifact relationship tracking"""
        prov = ProvenanceManager(data_dir=tempfile.mkdtemp())

        rel = ArtifactRelationship(
            from_artifact="workflow1",
            to_artifact="module1",
            relationship_type="uses",
        )

        prov.add_relationship(rel)

        assert len(prov._relationships) == 1
        assert prov._relationships[0].relationship_type == "uses"

    def test_attestation_recording(self):
        """Test attestation recording"""
        prov = ProvenanceManager(data_dir=tempfile.mkdtemp())

        artifact = Artifact(
            artifact_id="test_artifact", kind="workflow", version="1.0.0", content_hash="hash123"
        )
        prov.register_artifact(artifact)

        prov.attest("tests_passed", "test_artifact", {"test_count": 10, "success": True})

        assert len(prov._attestations) == 1
        assert prov._attestations[0]["type"] == "tests_passed"

    def test_sbom_generation(self):
        """Test SBOM generation"""
        prov = ProvenanceManager(data_dir=tempfile.mkdtemp())

        # Register workflow
        workflow_artifact = Artifact(
            artifact_id="test_workflow",
            kind="workflow",
            version="1.0.0",
            content_hash="wf_hash",
        )
        prov.register_artifact(workflow_artifact)

        # Register module
        module_artifact = Artifact(
            artifact_id="test_module", kind="module", version="1.0.0", content_hash="mod_hash"
        )
        prov.register_artifact(module_artifact)

        # Add relationship
        prov.add_relationship(
            ArtifactRelationship(
                from_artifact="test_workflow",
                to_artifact="test_module",
                relationship_type="uses",
            )
        )

        # Add attestation
        prov.attest("policy_passed", "test_workflow", {"policy": "security_check"})

        # Generate SBOM
        sbom = prov.generate_sbom("test_workflow")

        assert sbom["workflow"]["id"] == "test_workflow"
        assert len(sbom["artifacts"]) == 1
        assert len(sbom["relationships"]) == 1
        assert len(sbom["attestations"]) == 1

    def test_sbom_verification(self):
        """Test SBOM verification"""
        prov = ProvenanceManager(data_dir=tempfile.mkdtemp())

        workflow_artifact = Artifact(
            artifact_id="verify_wf", kind="workflow", version="1.0.0", content_hash="hash"
        )
        prov.register_artifact(workflow_artifact)

        prov.attest("verified", "verify_wf", {})

        sbom = prov.generate_sbom("verify_wf")
        valid, issues = prov.verify_sbom(sbom)

        assert valid is True
        assert any("passed" in i.lower() for i in issues)

    def test_sbom_persistence(self):
        """Test SBOM file persistence"""
        temp_dir = tempfile.mkdtemp()
        prov = ProvenanceManager(data_dir=temp_dir)

        workflow_artifact = Artifact(
            artifact_id="persist_wf", kind="workflow", version="1.0.0", content_hash="hash"
        )
        prov.register_artifact(workflow_artifact)

        sbom_path = prov.save_sbom("persist_wf")

        assert sbom_path.exists()
        assert sbom_path.suffix == ".json"


class TestTarlStackBox:
    """Test integrated TarlStackBox"""

    def test_initialization(self):
        """Test TarlStackBox initialization"""
        stack = TarlStackBox(
            config={
                "vm_data_dir": tempfile.mkdtemp(),
                "recording_dir": tempfile.mkdtemp(),
                "provenance_dir": tempfile.mkdtemp(),
            }
        )

        assert stack.vm is not None
        assert stack.orchestrator is not None
        assert stack.capabilities is not None
        assert stack.recorder is not None
        assert stack.provenance is not None

    def test_workflow_creation(self):
        """Test workflow creation with provenance"""
        stack = TarlStackBox(config={"vm_data_dir": tempfile.mkdtemp()})

        def test_entrypoint(vm, context):
            return "success"

        workflow = stack.create_workflow(
            workflow_id="create_test",
            entrypoint=test_entrypoint,
            required_caps={"Test.Cap"},
            metadata={"version": "1.0.0"},
        )

        assert workflow.workflow_id == "create_test"
        assert "Test.Cap" in workflow.required_caps
        assert "create_test" in stack.vm._workflows
        assert "create_test" in stack.provenance._artifacts

    def test_execution_with_provenance(self):
        """Test workflow execution with provenance tracking"""
        stack = TarlStackBox(
            config={
                "vm_data_dir": tempfile.mkdtemp(),
                "provenance_dir": tempfile.mkdtemp(),
            }
        )

        # Register capability
        cap = Capability(name="Exec.Test", resource="test")
        stack.capabilities.register_capability(cap)

        # Create workflow
        def test_workflow(vm, context):
            return {"status": "executed"}

        stack.create_workflow(
            workflow_id="prov_test", entrypoint=test_workflow, required_caps={"Exec.Test"}
        )

        # Execute
        result = stack.execute_with_provenance("prov_test")

        assert result["status"] == "executed"
        assert len(stack.provenance._attestations) >= 2  # capability_check + execution_success

    def test_full_status(self):
        """Test comprehensive status reporting"""
        stack = TarlStackBox(config={"vm_data_dir": tempfile.mkdtemp()})

        status = stack.get_full_status()

        assert "vm" in status
        assert "orchestrator" in status
        assert "capabilities" in status
        assert "recorder" in status
        assert "provenance" in status


class TestIntegration:
    """End-to-end integration tests"""

    def test_complete_workflow_lifecycle(self):
        """Test complete workflow lifecycle with all features"""
        stack = TarlStackBox(
            config={
                "vm_data_dir": tempfile.mkdtemp(),
                "recording_dir": tempfile.mkdtemp(),
                "provenance_dir": tempfile.mkdtemp(),
            }
        )

        # Setup capabilities
        cap = Capability(name="Full.Test", resource="test", constraints={"level": "high"})
        stack.capabilities.register_capability(cap)

        policy = Policy(
            name="TestPolicy", capability_name="Full.Test", constraints={"level": "high"}
        )
        stack.capabilities.register_policy(policy)

        # Setup agents
        stack.orchestrator.register_agent("agent1", lambda x: f"A1({x})")
        stack.orchestrator.register_agent("agent2", lambda x: f"A2({x})")

        # Create workflow
        def full_workflow(vm, context):
            # Check capability
            allowed, _ = stack.capabilities.check_capability("Full.Test", {"level": "high"})
            if not allowed:
                raise PermissionError("Capability check failed")

            # Use orchestrator
            result = stack.orchestrator.sequential("full_test", ["agent1", "agent2"], "data")

            # Record external call
            stack.recorder.record_external_call(
                "full_test", "tool", {"name": "test_tool"}, {"output": result}
            )

            # Take snapshot
            snap_hash = vm.snapshot("full_test")

            return {"result": result, "snapshot": snap_hash}

        # Create and execute
        stack.create_workflow(
            workflow_id="full_test",
            entrypoint=full_workflow,
            required_caps={"Full.Test"},
            metadata={"test": "integration"},
        )

        result = stack.execute_with_provenance("full_test")

        # Verify result (sequential processes agent1 then agent2)
        assert result["result"] == "A2(A1(data))"
        assert "snapshot" in result

        # Verify provenance
        sbom = stack.provenance.generate_sbom("full_test")
        assert sbom["workflow"]["id"] == "full_test"
        assert len(sbom["attestations"]) >= 2

        # Verify status
        status = stack.get_full_status()
        assert status["vm"]["workflows"] >= 1
        assert status["orchestrator"]["agents"] == 2
        assert status["capabilities"]["registered"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
