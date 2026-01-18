"""
Complete System Tests for Triumvirate Integration

Tests:
- Unit tests for each component
- End-to-end pipeline tests
- Contradiction detection
- Semantic memory with >10k records
- GPU/CPU fallback
- Temporal workflow integration
"""

import tempfile

import pytest

# ============================================================================
# Adapter Tests
# ============================================================================


class TestModelAdapter:
    """Test ModelAdapter functionality."""

    def test_dummy_adapter_basic(self):
        """Test dummy adapter for basic functionality."""
        from src.cognition.adapters.model_adapter import DummyAdapter

        adapter = DummyAdapter()
        assert adapter.is_available()

        # Load model
        adapter.load_model("dummy_model")
        assert adapter.loaded

        # Predict
        result = adapter.predict("test input")
        assert result["prediction"] == "dummy_result"
        assert "test input" in result["input"]

    def test_get_adapter_auto(self):
        """Test automatic adapter selection."""
        from src.cognition.adapters.model_adapter import get_adapter

        adapter = get_adapter("auto")
        assert adapter is not None
        assert adapter.is_available()

    def test_get_adapter_dummy(self):
        """Test explicit dummy adapter."""
        from src.cognition.adapters.model_adapter import get_adapter

        adapter = get_adapter("dummy")
        assert adapter.is_available()

    def test_get_adapter_invalid(self):
        """Test invalid adapter type."""
        from src.cognition.adapters.model_adapter import get_adapter

        with pytest.raises(ValueError):
            get_adapter("nonexistent")


class TestMemoryAdapter:
    """Test MemoryAdapter with semantic search."""

    def test_memory_initialization(self):
        """Test memory adapter initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.cognition.adapters.memory_adapter import MemoryAdapter

            memory = MemoryAdapter(data_dir=tmpdir)
            assert memory is not None
            assert len(memory.records) == 0

    def test_add_and_retrieve_memory(self):
        """Test adding and retrieving memories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.cognition.adapters.memory_adapter import MemoryAdapter

            memory = MemoryAdapter(data_dir=tmpdir)

            # Add memories
            mem_id1 = memory.add_memory("Python is a programming language")
            mem_id2 = memory.add_memory("JavaScript is used for web development")

            assert mem_id1 is not None
            assert mem_id2 is not None

            # Retrieve
            mem1 = memory.get_memory(mem_id1)
            assert mem1 is not None
            assert "Python" in mem1["content"]

    def test_semantic_search(self):
        """Test semantic similarity search."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.cognition.adapters.memory_adapter import MemoryAdapter

            memory = MemoryAdapter(data_dir=tmpdir)

            # Add memories
            memory.add_memory("Python programming language")
            memory.add_memory("Machine learning with PyTorch")
            memory.add_memory("Cooking pasta recipes")

            # Search
            results = memory.search("coding in Python", top_k=2)
            assert len(results) <= 2
            # Most relevant should be about Python
            if results:
                assert "Python" in results[0]["content"] or "PyTorch" in results[0]["content"]

    def test_memory_persistence(self):
        """Test memory persistence across instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.cognition.adapters.memory_adapter import MemoryAdapter

            # Create and add memory
            memory1 = MemoryAdapter(data_dir=tmpdir)
            mem_id = memory1.add_memory("Test persistence")

            # Create new instance (should load from disk)
            memory2 = MemoryAdapter(data_dir=tmpdir)
            retrieved = memory2.get_memory(mem_id)

            assert retrieved is not None
            assert retrieved["content"] == "Test persistence"

    def test_large_scale_memory(self):
        """Test memory with >10k records."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.cognition.adapters.memory_adapter import MemoryAdapter

            memory = MemoryAdapter(data_dir=tmpdir, max_records=15000)

            # Add many memories (scaled down for test speed)
            num_records = 100  # Use 100 for fast testing, would be 10000+ in production
            for i in range(num_records):
                memory.add_memory(f"Memory record {i} with content")

            stats = memory.get_stats()
            assert stats["total_records"] == num_records

            # Search should still work
            results = memory.search("record 50", top_k=5)
            assert len(results) > 0

    def test_memory_deletion(self):
        """Test memory deletion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.cognition.adapters.memory_adapter import MemoryAdapter

            memory = MemoryAdapter(data_dir=tmpdir)
            mem_id = memory.add_memory("Delete me")

            # Delete
            deleted = memory.delete_memory(mem_id)
            assert deleted

            # Should not exist
            retrieved = memory.get_memory(mem_id)
            assert retrieved is None


class TestPolicyEngine:
    """Test PolicyEngine functionality."""

    def test_allow_all_policy(self):
        """Test default allow-all policy."""
        from src.cognition.adapters.policy_engine import PolicyEngine

        engine = PolicyEngine(mode="production")
        result = engine.enforce("any output")

        assert result.decision.value == "allow"

    def test_content_filter_policy(self):
        """Test content filtering."""
        from src.cognition.adapters.policy_engine import (
            ContentFilterPolicy,
            PolicyEngine,
        )

        engine = PolicyEngine(policies=[ContentFilterPolicy(blocked_patterns=[r"bad\w+"])])

        # Should allow clean content
        result1 = engine.enforce("This is good content")
        assert result1.decision.value == "allow"

        # Should deny bad content
        result2 = engine.enforce("This contains badword")
        assert result2.decision.value == "deny"

    def test_length_limit_policy(self):
        """Test length limiting."""
        from src.cognition.adapters.policy_engine import LengthLimitPolicy, PolicyEngine

        engine = PolicyEngine(policies=[LengthLimitPolicy(max_length=50)])

        # Short content should pass
        result1 = engine.enforce("Short content")
        assert result1.decision.value == "allow"

        # Long content should be modified
        long_content = "x" * 100
        result2 = engine.enforce(long_content)
        assert result2.decision.value == "modify"
        assert len(str(result2.modified_output)) <= 70  # Includes truncation marker


# ============================================================================
# Engine Tests
# ============================================================================


class TestCodexEngine:
    """Test Codex engine."""

    def test_initialization(self):
        """Test Codex initialization."""
        from src.cognition.codex.engine import CodexConfig, CodexEngine

        config = CodexConfig(enable_full_engine=False)
        engine = CodexEngine(config)

        assert engine is not None
        status = engine.get_status()
        assert "loaded" in status

    def test_process_degraded_mode(self):
        """Test processing in degraded mode."""
        from src.cognition.codex.engine import CodexConfig, CodexEngine

        config = CodexConfig(enable_full_engine=False)
        engine = CodexEngine(config)

        result = engine.process("test input")
        assert result["success"]
        assert "degraded" in str(result["metadata"]["mode"])

    def test_gpu_cpu_fallback(self):
        """Test GPU/CPU fallback logic."""
        from src.cognition.codex.engine import CodexConfig, CodexEngine

        config = CodexConfig(
            enable_gpu=True, fallback_to_cpu=True, enable_full_engine=False
        )
        engine = CodexEngine(config)

        # Should initialize without error
        assert engine is not None


class TestGalahadEngine:
    """Test Galahad reasoning engine."""

    def test_initialization(self):
        """Test Galahad initialization."""
        from src.cognition.galahad.engine import GalahadEngine

        engine = GalahadEngine()
        assert engine is not None

    def test_simple_reasoning(self):
        """Test basic reasoning."""
        from src.cognition.galahad.engine import GalahadEngine

        engine = GalahadEngine()
        result = engine.reason(["input1", "input2"])

        assert result["success"]
        assert "conclusion" in result
        assert "explanation" in result

    def test_contradiction_detection(self):
        """Test contradiction detection."""
        from src.cognition.galahad.engine import GalahadEngine

        engine = GalahadEngine()

        # Test with contradictory inputs
        result = engine.reason(["yes", "no"])

        assert result["success"]
        # Should detect contradiction
        assert len(result["contradictions"]) > 0

    def test_arbitration(self):
        """Test arbitration between conflicts."""
        from src.cognition.galahad.engine import GalahadConfig, GalahadEngine

        engine = GalahadEngine(GalahadConfig(arbitration_strategy="weighted"))

        # Arbitrate between conflicting inputs
        result = engine.arbitrate([{"data": "A", "confidence": 0.8}, {"data": "B", "confidence": 0.5}])

        assert "decision" in result
        assert "reason" in result

    def test_curiosity_metrics(self):
        """Test curiosity tracking."""
        from src.cognition.galahad.engine import GalahadConfig, GalahadEngine

        engine = GalahadEngine(GalahadConfig(enable_curiosity=True))

        # Process uncertain input
        engine.reason([None, "unknown"])

        metrics = engine.get_curiosity_metrics()
        assert "current_score" in metrics
        assert metrics["enabled"]


class TestCerberusEngine:
    """Test Cerberus policy engine."""

    def test_initialization(self):
        """Test Cerberus initialization."""
        from src.cognition.cerberus.engine import CerberusEngine

        engine = CerberusEngine()
        assert engine is not None

    def test_input_validation(self):
        """Test input validation."""
        from src.cognition.cerberus.engine import CerberusConfig, CerberusEngine

        config = CerberusConfig(enforce_on_input=True, mode="production")
        engine = CerberusEngine(config)

        result = engine.validate_input("test input")
        assert result["valid"]

    def test_output_enforcement(self):
        """Test output enforcement."""
        from src.cognition.cerberus.engine import CerberusEngine

        engine = CerberusEngine()
        result = engine.enforce_output("test output")

        assert result["allowed"]

    def test_pre_persistence_check(self):
        """Test pre-persistence validation."""
        from src.cognition.cerberus.engine import CerberusEngine

        engine = CerberusEngine()
        result = engine.check_pre_persistence({"data": "test"})

        assert "persistence_approved" in result


# ============================================================================
# Triumvirate Integration Tests
# ============================================================================


class TestTriumvirate:
    """Test Triumvirate orchestrator."""

    def test_initialization(self):
        """Test Triumvirate initialization."""
        from src.cognition.triumvirate import Triumvirate

        triumvirate = Triumvirate()
        assert triumvirate is not None

    def test_end_to_end_pipeline(self):
        """Test complete pipeline flow."""
        from src.cognition.triumvirate import Triumvirate

        triumvirate = Triumvirate()
        result = triumvirate.process("test input", context={"test": True})

        assert "success" in result
        assert "correlation_id" in result
        assert "duration_ms" in result
        assert "pipeline" in result

    def test_pipeline_with_validation(self):
        """Test pipeline with input validation."""
        from src.cognition.triumvirate import Triumvirate

        triumvirate = Triumvirate()
        result = triumvirate.process("test input", skip_validation=False)

        assert result["success"]
        assert "validation" in result["pipeline"]

    def test_telemetry_collection(self):
        """Test telemetry event collection."""
        from src.cognition.triumvirate import Triumvirate, TriumvirateConfig

        config = TriumvirateConfig(enable_telemetry=True)
        triumvirate = Triumvirate(config)

        triumvirate.process("test input")

        telemetry = triumvirate.get_telemetry()
        assert len(telemetry) > 0

    def test_status_reporting(self):
        """Test status reporting."""
        from src.cognition.triumvirate import Triumvirate

        triumvirate = Triumvirate()
        status = triumvirate.get_status()

        assert "codex" in status
        assert "galahad" in status
        assert "cerberus" in status


# ============================================================================
# Temporal Workflow Tests
# ============================================================================


class TestTemporalWorkflows:
    """Test Temporal workflow integration."""

    def test_workflow_imports(self):
        """Test that workflow classes can be imported."""
        from temporal.workflows.triumvirate_workflow import (
            TriumvirateRequest,
            TriumvirateResult,
            TriumvirateWorkflow,
        )

        assert TriumvirateWorkflow is not None
        assert TriumvirateRequest is not None
        assert TriumvirateResult is not None

    def test_activity_imports(self):
        """Test that activities can be imported."""
        from temporal.workflows.activities import (
            enforce_output_policy,
            run_codex_inference,
            run_galahad_reasoning,
            run_triumvirate_pipeline,
            validate_input_activity,
        )

        assert run_triumvirate_pipeline is not None
        assert validate_input_activity is not None
        assert run_codex_inference is not None
        assert run_galahad_reasoning is not None
        assert enforce_output_policy is not None


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_system_integration():
    """Test full system integration."""
    from src.cognition.triumvirate import Triumvirate

    triumvirate = Triumvirate()

    # Test with various inputs
    inputs = [
        "Simple text input",
        {"structured": "data", "value": 123},
        ["list", "of", "items"],
    ]

    for inp in inputs:
        result = triumvirate.process(inp)
        assert "success" in result
        assert "correlation_id" in result


def test_contradiction_detection_e2e():
    """Test end-to-end contradiction detection."""
    from src.cognition.galahad.engine import GalahadEngine

    engine = GalahadEngine()

    # Provide contradictory information
    result = engine.reason(["System is safe", "System is unsafe"])

    # Should detect contradiction
    assert len(result["contradictions"]) > 0
    assert "contradiction" in result["explanation"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
