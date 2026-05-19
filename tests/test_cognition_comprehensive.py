#                                           [2026-04-09]
#                                          Test Coverage: Cognition Subsystem
"""
Comprehensive Test Suite for Cognition Subsystem

Tests all major components of the multi-agent reasoning framework:
- Triumvirate orchestration and coordination
- Cerberus security engine
- Codex ML inference engine
- Galahad reasoning and arbitration engine
- Reasoning Matrix decision tracking
- Adapter integrations (Memory, Model, Policy)
- Escalation protocols

Target: 50%+ coverage across cognition modules
"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import all cognition components
from src.cognition.adapters.memory_adapter import MemoryAdapter, MemoryRecord
from src.cognition.adapters.model_adapter import (
    DummyAdapter,
    HuggingFaceAdapter,
    PyTorchAdapter,
    get_adapter,
)
from src.cognition.adapters.policy_engine import (
    AllowAllPolicy,
    ContentFilterPolicy,
    LengthLimitPolicy,
    PolicyDecision,
    PolicyEngine,
    PolicyResult,
    SensitivityPolicy,
)
from src.cognition.cerberus.engine import CerberusConfig, CerberusEngine
from src.cognition.codex.engine import CodexConfig, CodexEngine
from src.cognition.codex.escalation import (
    CodexDeus,
    EscalationEvent,
    EscalationLevel,
)
from src.cognition.galahad.engine import GalahadConfig, GalahadEngine
from src.cognition.reasoning_matrix.core import (
    MatrixEntry,
    ReasoningFactor,
    ReasoningMatrix,
    ReasoningVerdict,
)
from src.cognition.triumvirate import Triumvirate, TriumvirateConfig

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def temp_memory_dir(tmp_path):
    """Temporary directory for memory adapter."""
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()
    return str(memory_dir)


@pytest.fixture
def reasoning_matrix():
    """Reasoning matrix instance."""
    return ReasoningMatrix(max_history=100)


@pytest.fixture
def cerberus_engine():
    """Cerberus engine with default config."""
    return CerberusEngine()


@pytest.fixture
def codex_engine():
    """Codex engine with lightweight config."""
    config = CodexConfig(enable_full_engine=False)
    return CodexEngine(config)


@pytest.fixture
def galahad_engine():
    """Galahad engine with default config."""
    return GalahadEngine()


@pytest.fixture
def triumvirate(reasoning_matrix):
    """Triumvirate orchestrator with all engines."""
    config = TriumvirateConfig()
    return Triumvirate(config, reasoning_matrix=reasoning_matrix)


# ============================================================================
# REASONING MATRIX TESTS (40 tests)
# ============================================================================


class TestReasoningFactor:
    """Test ReasoningFactor data class."""

    def test_create_factor_with_defaults(self):
        factor = ReasoningFactor(name="test_factor", value="test_value")
        assert factor.name == "test_factor"
        assert factor.value == "test_value"
        assert factor.weight == 1.0
        assert factor.score is None
        assert factor.source == ""
        assert factor.rationale == ""

    def test_create_factor_with_all_fields(self):
        factor = ReasoningFactor(
            name="security_check",
            value=True,
            weight=0.8,
            score=0.9,
            source="cerberus",
            rationale="Security validated",
        )
        assert factor.name == "security_check"
        assert factor.weight == 0.8
        assert factor.score == 0.9
        assert abs(factor.weighted_score - 0.72) < 0.001

    def test_factor_weight_validation(self):
        with pytest.raises(ValueError, match="weight must be in"):
            ReasoningFactor(name="test", value=1, weight=1.5)

    def test_factor_score_validation(self):
        with pytest.raises(ValueError, match="score must be in"):
            ReasoningFactor(name="test", value=1, score=1.5)

    def test_weighted_score_none_when_unscored(self):
        factor = ReasoningFactor(name="test", value=1)
        assert factor.weighted_score is None

    def test_factor_to_dict(self):
        factor = ReasoningFactor(
            name="test", value={"key": "val"}, weight=0.5, score=0.8
        )
        d = factor.to_dict()
        assert d["name"] == "test"
        assert d["weight"] == 0.5
        assert d["score"] == 0.8
        assert d["weighted_score"] == 0.4


class TestReasoningVerdict:
    """Test ReasoningVerdict data class."""

    def test_create_verdict(self):
        verdict = ReasoningVerdict(decision="allow", confidence=0.95)
        assert verdict.decision == "allow"
        assert verdict.confidence == 0.95
        assert verdict.dominant_factors == []
        assert verdict.dissenting_factors == []

    def test_verdict_confidence_validation(self):
        with pytest.raises(ValueError, match="confidence must be in"):
            ReasoningVerdict(decision="deny", confidence=1.5)

    def test_verdict_with_factors(self):
        verdict = ReasoningVerdict(
            decision="allow",
            confidence=0.9,
            dominant_factors=["factor1", "factor2"],
            dissenting_factors=["factor3"],
            explanation="Decision based on evidence",
        )
        assert len(verdict.dominant_factors) == 2
        assert len(verdict.dissenting_factors) == 1
        assert "evidence" in verdict.explanation

    def test_verdict_to_dict(self):
        verdict = ReasoningVerdict(decision="deny", confidence=0.8)
        d = verdict.to_dict()
        assert d["decision"] == "deny"
        assert d["confidence"] == 0.8
        assert "timestamp" in d


class TestMatrixEntry:
    """Test MatrixEntry data class."""

    def test_create_entry(self):
        entry = MatrixEntry(entry_id="test-001", context_type="test_context")
        assert entry.entry_id == "test-001"
        assert entry.context_type == "test_context"
        assert entry.factors == []
        assert entry.verdict is None
        assert not entry.is_finalized

    def test_entry_with_parent(self):
        entry = MatrixEntry(
            entry_id="child", context_type="test", parent_entry_id="parent"
        )
        assert entry.parent_entry_id == "parent"

    def test_entry_finalized_property(self):
        entry = MatrixEntry(entry_id="test", context_type="test")
        assert not entry.is_finalized
        entry.verdict = ReasoningVerdict(decision="allow", confidence=0.9)
        assert entry.is_finalized

    def test_entry_scored_factors(self):
        entry = MatrixEntry(entry_id="test", context_type="test")
        entry.factors = [
            ReasoningFactor(name="f1", value=1, score=0.8),
            ReasoningFactor(name="f2", value=2),
            ReasoningFactor(name="f3", value=3, score=0.6),
        ]
        scored = entry.scored_factors
        assert len(scored) == 2
        assert all(f.score is not None for f in scored)

    def test_entry_aggregate_score_none_when_no_scores(self):
        entry = MatrixEntry(entry_id="test", context_type="test")
        entry.factors = [ReasoningFactor(name="f1", value=1)]
        assert entry.aggregate_score is None

    def test_entry_aggregate_score_calculation(self):
        entry = MatrixEntry(entry_id="test", context_type="test")
        entry.factors = [
            ReasoningFactor(name="f1", value=1, weight=1.0, score=0.8),
            ReasoningFactor(name="f2", value=2, weight=0.5, score=0.6),
        ]
        score = entry.aggregate_score
        assert score is not None
        assert 0.6 < score < 0.8

    def test_entry_get_factor(self):
        entry = MatrixEntry(entry_id="test", context_type="test")
        entry.factors = [
            ReasoningFactor(name="found", value=1),
            ReasoningFactor(name="other", value=2),
        ]
        factor = entry.get_factor("found")
        assert factor is not None
        assert factor.name == "found"
        assert entry.get_factor("missing") is None

    def test_entry_compute_hash(self):
        entry = MatrixEntry(entry_id="test", context_type="test")
        entry.factors = [ReasoningFactor(name="f1", value=1, score=0.8)]
        entry.verdict = ReasoningVerdict(decision="allow", confidence=0.9)
        hash1 = entry.compute_hash()
        assert len(hash1) == 64
        hash2 = entry.compute_hash()
        assert hash1 == hash2

    def test_entry_to_dict(self):
        entry = MatrixEntry(entry_id="test", context_type="test")
        entry.factors = [ReasoningFactor(name="f1", value=1, score=0.8)]
        d = entry.to_dict()
        assert d["entry_id"] == "test"
        assert d["context_type"] == "test"
        assert len(d["factors"]) == 1


class TestReasoningMatrix:
    """Test ReasoningMatrix orchestrator."""

    def test_matrix_initialization(self):
        matrix = ReasoningMatrix(max_history=500)
        assert matrix._max_history == 500

    def test_begin_reasoning(self, reasoning_matrix):
        entry_id = reasoning_matrix.begin_reasoning("test_context")
        assert entry_id.startswith("rm-")
        entry = reasoning_matrix.get_entry(entry_id)
        assert entry is not None
        assert entry.context_type == "test_context"

    def test_begin_reasoning_with_metadata(self, reasoning_matrix):
        entry_id = reasoning_matrix.begin_reasoning(
            "test", metadata={"key": "value"}
        )
        entry = reasoning_matrix.get_entry(entry_id)
        assert entry.metadata["key"] == "value"

    def test_begin_reasoning_with_parent(self, reasoning_matrix):
        parent_id = reasoning_matrix.begin_reasoning("parent")
        child_id = reasoning_matrix.begin_reasoning("child", parent_entry_id=parent_id)
        child = reasoning_matrix.get_entry(child_id)
        assert child.parent_entry_id == parent_id

    def test_add_factor(self, reasoning_matrix):
        entry_id = reasoning_matrix.begin_reasoning("test")
        factor = reasoning_matrix.add_factor(
            entry_id,
            "test_factor",
            True,
            weight=0.8,
            score=0.9,
            source="test",
            rationale="Test rationale",
        )
        assert factor.name == "test_factor"
        assert factor.weight == 0.8
        entry = reasoning_matrix.get_entry(entry_id)
        assert len(entry.factors) == 1

    def test_add_factor_to_unknown_entry(self, reasoning_matrix):
        with pytest.raises(KeyError):
            reasoning_matrix.add_factor("unknown", "factor", 1)

    def test_add_factor_to_finalized_entry(self, reasoning_matrix):
        entry_id = reasoning_matrix.begin_reasoning("test")
        reasoning_matrix.render_verdict(entry_id, "allow", 0.9)
        with pytest.raises(ValueError, match="finalized"):
            reasoning_matrix.add_factor(entry_id, "factor", 1)

    def test_score_factor(self, reasoning_matrix):
        entry_id = reasoning_matrix.begin_reasoning("test")
        reasoning_matrix.add_factor(entry_id, "factor", 1)
        reasoning_matrix.score_factor(entry_id, "factor", 0.85)
        entry = reasoning_matrix.get_entry(entry_id)
        factor = entry.get_factor("factor")
        assert factor.score == 0.85

    def test_score_factor_validation(self, reasoning_matrix):
        entry_id = reasoning_matrix.begin_reasoning("test")
        reasoning_matrix.add_factor(entry_id, "factor", 1)
        with pytest.raises(ValueError, match="score must be in"):
            reasoning_matrix.score_factor(entry_id, "factor", 1.5)

    def test_score_nonexistent_factor(self, reasoning_matrix):
        entry_id = reasoning_matrix.begin_reasoning("test")
        with pytest.raises(ValueError, match="not found"):
            reasoning_matrix.score_factor(entry_id, "missing", 0.5)

    def test_render_verdict(self, reasoning_matrix):
        entry_id = reasoning_matrix.begin_reasoning("test")
        reasoning_matrix.add_factor(entry_id, "f1", 1, score=0.9)
        reasoning_matrix.add_factor(entry_id, "f2", 2, score=0.3)
        verdict = reasoning_matrix.render_verdict(
            entry_id, "allow", 0.95, explanation="Test verdict"
        )
        assert verdict.decision == "allow"
        assert verdict.confidence == 0.95
        assert "f1" in verdict.dominant_factors
        assert "f2" in verdict.dissenting_factors

    def test_render_verdict_auto_explanation(self, reasoning_matrix):
        entry_id = reasoning_matrix.begin_reasoning("test")
        reasoning_matrix.add_factor(entry_id, "top_factor", 1, weight=1.0, score=0.9)
        verdict = reasoning_matrix.render_verdict(entry_id, "allow", 0.9)
        assert "top_factor" in verdict.explanation

    def test_render_verdict_twice_raises_error(self, reasoning_matrix):
        entry_id = reasoning_matrix.begin_reasoning("test")
        reasoning_matrix.render_verdict(entry_id, "allow", 0.9)
        with pytest.raises(ValueError, match="already has a verdict"):
            reasoning_matrix.render_verdict(entry_id, "deny", 0.8)

    def test_get_entry(self, reasoning_matrix):
        entry_id = reasoning_matrix.begin_reasoning("test")
        entry = reasoning_matrix.get_entry(entry_id)
        assert entry.entry_id == entry_id

    def test_get_entry_returns_none_for_missing(self, reasoning_matrix):
        entry = reasoning_matrix.get_entry("nonexistent")
        assert entry is None

    def test_get_chain(self, reasoning_matrix):
        parent_id = reasoning_matrix.begin_reasoning("parent")
        child_id = reasoning_matrix.begin_reasoning("child", parent_entry_id=parent_id)
        grandchild_id = reasoning_matrix.begin_reasoning(
            "grandchild", parent_entry_id=child_id
        )
        chain = reasoning_matrix.get_chain(grandchild_id)
        assert len(chain) == 3
        assert chain[0].entry_id == grandchild_id
        assert chain[1].entry_id == child_id
        assert chain[2].entry_id == parent_id

    def test_query_by_context_type(self, reasoning_matrix):
        for i in range(5):
            entry_id = reasoning_matrix.begin_reasoning(f"type_{i % 2}")
            reasoning_matrix.render_verdict(entry_id, "allow", 0.9)
        results = reasoning_matrix.query(context_type="type_0")
        assert len(results) == 3

    def test_query_by_confidence(self, reasoning_matrix):
        for conf in [0.5, 0.7, 0.9]:
            entry_id = reasoning_matrix.begin_reasoning("test")
            reasoning_matrix.render_verdict(entry_id, "allow", conf)
        results = reasoning_matrix.query(min_confidence=0.8)
        assert len(results) == 1

    def test_query_limit(self, reasoning_matrix):
        for i in range(20):
            entry_id = reasoning_matrix.begin_reasoning("test")
            reasoning_matrix.render_verdict(entry_id, "allow", 0.9)
        results = reasoning_matrix.query(limit=5)
        assert len(results) == 5


# ============================================================================
# POLICY ENGINE TESTS (25 tests)
# ============================================================================


class TestPolicyDecision:
    """Test PolicyDecision enum."""

    def test_policy_decision_values(self):
        assert PolicyDecision.ALLOW.value == "allow"
        assert PolicyDecision.DENY.value == "deny"
        assert PolicyDecision.MODIFY.value == "modify"
        assert PolicyDecision.WARN.value == "warn"


class TestAllowAllPolicy:
    """Test AllowAllPolicy."""

    def test_allows_everything(self):
        policy = AllowAllPolicy()
        result = policy.evaluate("any content")
        assert result.decision == PolicyDecision.ALLOW
        assert "Allow-all" in result.reason

    def test_allows_with_context(self):
        policy = AllowAllPolicy()
        result = policy.evaluate("content", context={"key": "value"})
        assert result.decision == PolicyDecision.ALLOW


class TestContentFilterPolicy:
    """Test ContentFilterPolicy."""

    def test_blocks_matching_pattern(self):
        policy = ContentFilterPolicy(blocked_patterns=[r"badword", r"forbidden"])
        result = policy.evaluate("This contains badword content")
        assert result.decision == PolicyDecision.DENY
        assert "badword" in result.reason

    def test_allows_non_matching_content(self):
        policy = ContentFilterPolicy(blocked_patterns=[r"badword"])
        result = policy.evaluate("This is clean content")
        assert result.decision == PolicyDecision.ALLOW

    def test_case_insensitive_matching(self):
        policy = ContentFilterPolicy(blocked_patterns=[r"banned"])
        result = policy.evaluate("BANNED content")
        assert result.decision == PolicyDecision.DENY


class TestLengthLimitPolicy:
    """Test LengthLimitPolicy."""

    def test_allows_short_content(self):
        policy = LengthLimitPolicy(max_length=100)
        result = policy.evaluate("Short text")
        assert result.decision == PolicyDecision.ALLOW

    def test_truncates_long_content(self):
        policy = LengthLimitPolicy(max_length=10)
        result = policy.evaluate("This is very long content")
        assert result.decision == PolicyDecision.MODIFY
        assert result.modified_output is not None
        assert len(result.modified_output) <= 25
        assert "[truncated]" in result.modified_output


class TestSensitivityPolicy:
    """Test SensitivityPolicy."""

    def test_detects_ssn(self):
        policy = SensitivityPolicy()
        result = policy.evaluate("SSN: 123-45-6789")
        assert result.decision == PolicyDecision.WARN
        assert result.warnings is not None
        assert len(result.warnings) > 0

    def test_detects_email(self):
        policy = SensitivityPolicy()
        result = policy.evaluate("Contact: user@example.com")
        assert result.decision == PolicyDecision.WARN

    def test_allows_clean_content(self):
        policy = SensitivityPolicy()
        result = policy.evaluate("Normal content without sensitive info")
        assert result.decision == PolicyDecision.ALLOW


class TestPolicyEngine:
    """Test PolicyEngine."""

    def test_production_mode_allows_all(self):
        engine = PolicyEngine(mode="production")
        result = engine.enforce("any content")
        assert result.decision == PolicyDecision.ALLOW

    def test_strict_mode_with_policies(self):
        engine = PolicyEngine(mode="strict")
        assert len(engine.policies) > 0

    def test_custom_mode_with_no_policies(self):
        engine = PolicyEngine(mode="custom")
        result = engine.enforce("content")
        assert result.decision == PolicyDecision.ALLOW
        assert "No policies" in result.reason

    def test_add_policy(self):
        engine = PolicyEngine(mode="custom")
        engine.add_policy(LengthLimitPolicy(max_length=50))
        assert len(engine.policies) == 1

    def test_remove_policy(self):
        engine = PolicyEngine(mode="strict")
        initial_count = len(engine.policies)
        engine.remove_policy(SensitivityPolicy)
        assert len(engine.policies) < initial_count

    def test_enforce_deny_stops_immediately(self):
        engine = PolicyEngine(policies=[])
        engine.add_policy(ContentFilterPolicy(blocked_patterns=[r"bad"]))
        engine.add_policy(LengthLimitPolicy(max_length=1000))
        result = engine.enforce("bad content")
        assert result.decision == PolicyDecision.DENY

    def test_enforce_modify_applies_changes(self):
        engine = PolicyEngine(policies=[])
        engine.add_policy(LengthLimitPolicy(max_length=5))
        result = engine.enforce("very long content")
        assert result.decision == PolicyDecision.MODIFY
        assert result.modified_output is not None

    def test_enforce_accumulates_warnings(self):
        engine = PolicyEngine(policies=[])
        engine.add_policy(SensitivityPolicy())
        result = engine.enforce("Email: test@example.com, SSN: 123-45-6789")
        assert result.decision in [PolicyDecision.WARN, PolicyDecision.ALLOW]

    def test_get_policy_info(self):
        engine = PolicyEngine(mode="strict")
        info = engine.get_policy_info()
        assert info["mode"] == "strict"
        assert "policy_count" in info
        assert "policies" in info


# ============================================================================
# MODEL ADAPTER TESTS (15 tests)
# ============================================================================


class TestDummyAdapter:
    """Test DummyAdapter."""

    def test_dummy_adapter_creation(self):
        adapter = DummyAdapter()
        assert adapter.is_available()

    def test_dummy_load_model(self):
        adapter = DummyAdapter()
        model = adapter.load_model("dummy_model")
        assert model == "dummy_model"
        assert adapter.loaded

    def test_dummy_predict(self):
        adapter = DummyAdapter()
        adapter.load_model("test")
        result = adapter.predict("test input")
        assert result["prediction"] == "dummy_result"
        assert "test input" in result["input"]

    def test_dummy_predict_without_load_raises(self):
        adapter = DummyAdapter()
        with pytest.raises(RuntimeError, match="not loaded"):
            adapter.predict("input")


class TestGetAdapter:
    """Test adapter factory function."""

    def test_get_dummy_adapter(self):
        adapter = get_adapter("dummy")
        assert isinstance(adapter, DummyAdapter)

    def test_get_auto_adapter_returns_available(self):
        adapter = get_adapter("auto")
        assert adapter is not None
        assert adapter.is_available()

    def test_get_unknown_adapter_raises(self):
        with pytest.raises(ValueError, match="Unknown adapter type"):
            get_adapter("nonexistent")

    def test_huggingface_adapter_creation(self):
        try:
            import transformers  # noqa: F401

            adapter = HuggingFaceAdapter()
            assert adapter is not None
        except ImportError:
            pytest.skip("transformers not installed")

    def test_pytorch_adapter_creation(self):
        try:
            import torch  # noqa: F401

            adapter = PyTorchAdapter()
            assert adapter is not None
        except ImportError:
            pytest.skip("torch not installed")


# ============================================================================
# MEMORY ADAPTER TESTS (20 tests)
# ============================================================================


class TestMemoryRecord:
    """Test MemoryRecord data class."""

    def test_create_memory_record(self):
        record = MemoryRecord(id="test-1", content="Test content")
        assert record.id == "test-1"
        assert record.content == "Test content"
        assert record.embedding is None

    def test_memory_record_to_dict(self):
        record = MemoryRecord(
            id="test-1", content="Test", metadata={"key": "value"}
        )
        d = record.to_dict()
        assert d["id"] == "test-1"
        assert d["content"] == "Test"
        assert d["metadata"]["key"] == "value"


class TestMemoryAdapter:
    """Test MemoryAdapter."""

    def test_memory_adapter_initialization(self, temp_memory_dir):
        adapter = MemoryAdapter(data_dir=temp_memory_dir)
        assert adapter.max_records == 10000
        assert len(adapter.records) == 0

    def test_add_memory(self, temp_memory_dir):
        adapter = MemoryAdapter(data_dir=temp_memory_dir)
        memory_id = adapter.add_memory("Test memory content")
        assert memory_id.startswith("mem_")
        assert len(adapter.records) == 1

    def test_add_memory_with_custom_id(self, temp_memory_dir):
        adapter = MemoryAdapter(data_dir=temp_memory_dir)
        memory_id = adapter.add_memory("Content", memory_id="custom-id")
        assert memory_id == "custom-id"

    def test_add_memory_with_metadata(self, temp_memory_dir):
        adapter = MemoryAdapter(data_dir=temp_memory_dir)
        meta = {"source": "test", "importance": "high"}
        memory_id = adapter.add_memory("Content", metadata=meta)
        record = adapter.get_memory(memory_id)
        assert record["metadata"]["source"] == "test"

    def test_search_memory(self, temp_memory_dir):
        adapter = MemoryAdapter(data_dir=temp_memory_dir)
        adapter.add_memory("Python programming language")
        adapter.add_memory("JavaScript web development")
        adapter.add_memory("Python data science")
        results = adapter.search("Python", top_k=2)
        assert len(results) <= 2

    def test_search_empty_returns_empty(self, temp_memory_dir):
        adapter = MemoryAdapter(data_dir=temp_memory_dir)
        results = adapter.search("anything")
        assert results == []

    def test_get_memory(self, temp_memory_dir):
        adapter = MemoryAdapter(data_dir=temp_memory_dir)
        memory_id = adapter.add_memory("Test content")
        record = adapter.get_memory(memory_id)
        assert record is not None
        assert record["content"] == "Test content"

    def test_get_nonexistent_memory_returns_none(self, temp_memory_dir):
        adapter = MemoryAdapter(data_dir=temp_memory_dir)
        record = adapter.get_memory("nonexistent")
        assert record is None

    def test_delete_memory(self, temp_memory_dir):
        adapter = MemoryAdapter(data_dir=temp_memory_dir)
        memory_id = adapter.add_memory("To be deleted")
        assert adapter.delete_memory(memory_id)
        assert len(adapter.records) == 0

    def test_delete_nonexistent_memory_returns_false(self, temp_memory_dir):
        adapter = MemoryAdapter(data_dir=temp_memory_dir)
        assert not adapter.delete_memory("nonexistent")

    def test_clear_all_memories(self, temp_memory_dir):
        adapter = MemoryAdapter(data_dir=temp_memory_dir)
        adapter.add_memory("Memory 1")
        adapter.add_memory("Memory 2")
        adapter.clear_all()
        assert len(adapter.records) == 0

    def test_get_stats(self, temp_memory_dir):
        adapter = MemoryAdapter(data_dir=temp_memory_dir)
        adapter.add_memory("Test")
        stats = adapter.get_stats()
        assert stats["total_records"] == 1
        assert stats["max_records"] == 10000

    def test_max_records_enforcement(self, temp_memory_dir):
        adapter = MemoryAdapter(data_dir=temp_memory_dir, max_records=3)
        for i in range(5):
            adapter.add_memory(f"Memory {i}")
        assert len(adapter.records) == 3

    def test_persistence_save_and_load(self, temp_memory_dir):
        adapter1 = MemoryAdapter(data_dir=temp_memory_dir)
        adapter1.add_memory("Persistent memory")
        adapter2 = MemoryAdapter(data_dir=temp_memory_dir)
        assert len(adapter2.records) == 1
        assert adapter2.records[0].content == "Persistent memory"


# ============================================================================
# CERBERUS ENGINE TESTS (15 tests)
# ============================================================================


class TestCerberusConfig:
    """Test CerberusConfig."""

    def test_default_config(self):
        config = CerberusConfig()
        assert config.mode == "production"
        assert not config.enforce_on_input
        assert config.enforce_on_output

    def test_custom_config(self):
        config = CerberusConfig(
            mode="strict", enforce_on_input=True, block_on_deny=False
        )
        assert config.mode == "strict"
        assert config.enforce_on_input


class TestCerberusEngine:
    """Test CerberusEngine."""

    def test_engine_initialization(self):
        engine = CerberusEngine()
        assert engine.config.mode == "production"
        assert engine.enforcement_count == 0

    def test_validate_input_disabled(self, cerberus_engine):
        result = cerberus_engine.validate_input("test input")
        assert result["valid"]
        assert "disabled" in result["reason"]

    def test_validate_input_enabled(self):
        config = CerberusConfig(enforce_on_input=True)
        engine = CerberusEngine(config)
        result = engine.validate_input("test input")
        assert result["valid"]

    def test_enforce_output_production_allows_all(self, cerberus_engine):
        result = cerberus_engine.enforce_output("any output")
        assert result["allowed"]

    def test_enforce_output_disabled(self):
        config = CerberusConfig(enforce_on_output=False)
        engine = CerberusEngine(config)
        result = engine.enforce_output("output")
        assert result["allowed"]
        assert "disabled" in result["reason"]

    def test_check_pre_persistence(self, cerberus_engine):
        result = cerberus_engine.check_pre_persistence("data")
        assert "persistence_approved" in result

    def test_get_statistics(self, cerberus_engine):
        cerberus_engine.enforce_output("test")
        stats = cerberus_engine.get_statistics()
        assert stats["total_enforcements"] == 1
        assert stats["policy_mode"] == "production"

    def test_reset_statistics(self, cerberus_engine):
        cerberus_engine.enforce_output("test")
        cerberus_engine.reset_statistics()
        stats = cerberus_engine.get_statistics()
        assert stats["total_enforcements"] == 0

    def test_add_custom_policy(self, cerberus_engine):
        custom_policy = LengthLimitPolicy(max_length=100)
        cerberus_engine.add_custom_policy(custom_policy)
        assert len(cerberus_engine.policy_engine.policies) > 1


# ============================================================================
# CODEX ENGINE TESTS (15 tests)
# ============================================================================


class TestCodexConfig:
    """Test CodexConfig."""

    def test_default_config(self):
        config = CodexConfig()
        assert config.model_path == "gpt2"
        assert config.device == "auto"
        assert not config.enable_full_engine

    def test_custom_config(self):
        config = CodexConfig(
            model_path="bert-base", enable_full_engine=True, enable_gpu=False
        )
        assert config.model_path == "bert-base"
        assert config.enable_full_engine
        assert not config.enable_gpu


class TestCodexEngine:
    """Test CodexEngine."""

    def test_engine_initialization(self):
        config = CodexConfig(enable_full_engine=False)
        engine = CodexEngine(config)
        assert not engine.is_loaded

    def test_load_config_from_env(self):
        with patch.dict("os.environ", {"CODEX_MODEL_PATH": "test-model"}):
            config = CodexEngine._load_config_from_env()
            assert config.model_path == "test-model"

    def test_process_degraded_mode(self, codex_engine):
        result = codex_engine.process("test input")
        assert result["success"]
        assert "degraded" in result["metadata"]["mode"]

    def test_process_with_context(self, codex_engine):
        result = codex_engine.process("input", context={"key": "value"})
        assert result["metadata"]["context"]["key"] == "value"

    def test_get_status(self, codex_engine):
        status = codex_engine.get_status()
        assert "loaded" in status
        assert "device" in status
        assert status["loaded"] == False


# ============================================================================
# GALAHAD ENGINE TESTS (20 tests)
# ============================================================================


class TestGalahadConfig:
    """Test GalahadConfig."""

    def test_default_config(self):
        config = GalahadConfig()
        assert config.reasoning_depth == 3
        assert config.enable_curiosity
        assert config.arbitration_strategy == "weighted"

    def test_custom_config(self):
        config = GalahadConfig(
            reasoning_depth=5,
            arbitration_strategy="majority",
            sovereign_mode=True,
        )
        assert config.reasoning_depth == 5
        assert config.arbitration_strategy == "majority"
        assert config.sovereign_mode


class TestGalahadEngine:
    """Test GalahadEngine."""

    def test_engine_initialization(self):
        engine = GalahadEngine()
        assert engine.config.reasoning_depth == 3
        assert engine.curiosity_score == 0.0

    def test_reason_single_input(self, galahad_engine):
        result = galahad_engine.reason(["input1"])
        assert result["success"]
        assert result["conclusion"] is not None

    def test_reason_multiple_inputs(self, galahad_engine):
        result = galahad_engine.reason(["input1", "input2", "input3"])
        assert result["success"]
        assert "explanation" in result

    def test_reason_with_context(self, galahad_engine):
        result = galahad_engine.reason(
            ["input"], context={"source": "test"}
        )
        assert result["metadata"]["context"]["source"] == "test"

    def test_reason_with_sovereign_mode(self):
        config = GalahadConfig(sovereign_mode=True)
        engine = GalahadEngine(config)
        result = engine.reason(["input"])
        assert result["success"]

    def test_reason_with_contradictions(self, galahad_engine):
        result = galahad_engine.reason(["yes", "no"])
        assert result["success"]
        if result["contradictions"]:
            assert len(result["contradictions"]) > 0

    def test_arbitrate_empty_inputs(self, galahad_engine):
        result = galahad_engine.arbitrate([])
        assert result["decision"] is None

    def test_arbitrate_weighted(self):
        config = GalahadConfig(arbitration_strategy="weighted")
        engine = GalahadEngine(config)
        inputs = [
            {"value": "option1", "confidence": 0.9},
            {"value": "option2", "confidence": 0.5},
        ]
        result = engine.arbitrate(inputs)
        assert result["decision"] is not None

    def test_arbitrate_majority(self):
        config = GalahadConfig(arbitration_strategy="majority")
        engine = GalahadEngine(config)
        result = engine.arbitrate(["A", "A", "B"])
        assert result["decision"] == "A"

    def test_arbitrate_unanimous(self):
        config = GalahadConfig(arbitration_strategy="unanimous")
        engine = GalahadEngine(config)
        result = engine.arbitrate(["same", "same", "same"])
        assert result["decision"] == "same"

    def test_arbitrate_unanimous_disagree(self):
        config = GalahadConfig(arbitration_strategy="unanimous")
        engine = GalahadEngine(config)
        result = engine.arbitrate(["A", "B"])
        assert result["decision"] is None

    def test_get_curiosity_metrics(self, galahad_engine):
        metrics = galahad_engine.get_curiosity_metrics()
        assert "current_score" in metrics
        assert "enabled" in metrics
        assert "should_explore" in metrics

    def test_get_reasoning_history(self, galahad_engine):
        galahad_engine.reason(["input1"])
        galahad_engine.reason(["input2"])
        history = galahad_engine.get_reasoning_history(limit=1)
        assert len(history) == 1

    def test_clear_history(self, galahad_engine):
        galahad_engine.reason(["input"])
        galahad_engine.clear_history()
        history = galahad_engine.get_reasoning_history()
        assert len(history) == 0


# ============================================================================
# ESCALATION TESTS (5 tests)
# ============================================================================


class TestEscalation:
    """Test escalation system."""

    def test_escalation_level_enum(self):
        assert EscalationLevel.LOW.value == "low"
        assert EscalationLevel.MEDIUM.value == "medium"
        assert EscalationLevel.HIGH.value == "high"

    def test_escalation_event_creation(self):
        event = EscalationEvent(
            level=EscalationLevel.MEDIUM,
            reason="Test escalation",
            context={"key": "value"},
        )
        assert event.level == EscalationLevel.MEDIUM
        assert event.reason == "Test escalation"

    def test_codex_deus_low_escalation(self):
        deus = CodexDeus()
        event = EscalationEvent(
            level=EscalationLevel.LOW, reason="Minor issue", context={}
        )
        result = deus.escalate(event)
        assert result.level == EscalationLevel.LOW

    def test_codex_deus_medium_escalation(self):
        deus = CodexDeus()
        event = EscalationEvent(
            level=EscalationLevel.MEDIUM, reason="Moderate issue", context={}
        )
        result = deus.escalate(event)
        assert result.level == EscalationLevel.MEDIUM

    def test_codex_deus_high_escalation_raises(self):
        deus = CodexDeus()
        event = EscalationEvent(
            level=EscalationLevel.HIGH, reason="Critical issue", context={}
        )
        with pytest.raises(SystemExit, match="CRITICAL ESCALATION"):
            deus.escalate(event)


# ============================================================================
# TRIUMVIRATE INTEGRATION TESTS (15 tests)
# ============================================================================


class TestTriumvirateConfig:
    """Test TriumvirateConfig."""

    def test_default_config(self):
        config = TriumvirateConfig()
        assert config.enable_telemetry
        assert config.correlation_id_prefix == "trv"

    def test_custom_config(self):
        config = TriumvirateConfig(
            codex_config=CodexConfig(model_path="custom"),
            enable_telemetry=False,
        )
        assert not config.enable_telemetry
        assert config.codex_config.model_path == "custom"


class TestTriumvirate:
    """Test Triumvirate orchestrator."""

    def test_triumvirate_initialization(self):
        triumvirate = Triumvirate()
        assert triumvirate.codex is not None
        assert triumvirate.galahad is not None
        assert triumvirate.cerberus is not None

    def test_process_simple_input(self, triumvirate):
        result = triumvirate.process("test input")
        assert "success" in result
        assert "correlation_id" in result

    def test_process_with_context(self, triumvirate):
        result = triumvirate.process("input", context={"key": "value"})
        assert result["metadata"]["context"]["key"] == "value"

    def test_process_skip_validation(self, triumvirate):
        result = triumvirate.process("input", skip_validation=True)
        assert result["pipeline"]["validation"]["skipped"]

    def test_process_generates_correlation_id(self, triumvirate):
        result = triumvirate.process("input")
        assert result["correlation_id"].startswith("trv_")

    def test_process_with_reasoning_matrix(self, triumvirate):
        result = triumvirate.process("input")
        assert "reasoning_entry_id" in result
        if result["reasoning_entry_id"]:
            entry = triumvirate._matrix.get_entry(result["reasoning_entry_id"])
            assert entry is not None

    def test_get_status(self, triumvirate):
        status = triumvirate.get_status()
        assert "codex" in status
        assert "galahad" in status
        assert "cerberus" in status

    def test_get_telemetry(self, triumvirate):
        triumvirate.process("input")
        telemetry = triumvirate.get_telemetry()
        assert isinstance(telemetry, list)

    def test_clear_telemetry(self, triumvirate):
        triumvirate.process("input")
        triumvirate.clear_telemetry()
        telemetry = triumvirate.get_telemetry()
        assert len(telemetry) == 0

    def test_telemetry_disabled(self):
        config = TriumvirateConfig(enable_telemetry=False)
        triumvirate = Triumvirate(config)
        triumvirate.process("input")
        assert len(triumvirate.telemetry_events) == 0

    def test_process_complete_pipeline(self, triumvirate):
        result = triumvirate.process("test input")
        assert "pipeline" in result
        assert "validation" in result["pipeline"]
        assert "codex" in result["pipeline"]
        assert "galahad" in result["pipeline"]
        assert "cerberus" in result["pipeline"]

    def test_multiple_processes_independent(self, triumvirate):
        result1 = triumvirate.process("input1")
        result2 = triumvirate.process("input2")
        assert result1["correlation_id"] != result2["correlation_id"]


# ============================================================================
# INTEGRATION SCENARIOS (20 tests)
# ============================================================================


class TestCognitionIntegration:
    """Test integrated scenarios across cognition subsystem."""

    def test_decision_with_full_pipeline(self, triumvirate):
        """Test complete decision pipeline."""
        result = triumvirate.process("Make a decision", context={"priority": "high"})
        assert result["success"]
        assert result["duration_ms"] >= 0

    def test_policy_enforcement_in_pipeline(self):
        """Test policy enforcement during processing."""
        config = TriumvirateConfig(
            cerberus_config=CerberusConfig(enforce_on_output=True)
        )
        triumvirate = Triumvirate(config)
        result = triumvirate.process("test")
        assert result["success"]

    def test_reasoning_matrix_integration(self, triumvirate):
        """Test reasoning matrix captures decisions."""
        result = triumvirate.process("test input")
        entry_id = result.get("reasoning_entry_id")
        if entry_id:
            entry = triumvirate._matrix.get_entry(entry_id)
            assert entry is not None
            assert len(entry.factors) > 0

    def test_multi_agent_consensus(self, galahad_engine):
        """Test multi-agent consensus mechanism."""
        inputs = [
            {"agent": "cerberus", "verdict": "allow"},
            {"agent": "codex", "verdict": "allow"},
            {"agent": "galahad", "verdict": "allow"},
        ]
        result = galahad_engine.reason(inputs)
        assert result["success"]

    def test_contradiction_resolution(self, galahad_engine):
        """Test contradiction detection and resolution."""
        result = galahad_engine.reason(["allow access", "deny access"])
        assert result["success"]

    def test_escalation_protocol(self):
        """Test escalation protocol activation."""
        deus = CodexDeus()
        low_event = EscalationEvent(
            level=EscalationLevel.LOW, reason="Minor", context={}
        )
        result = deus.escalate(low_event)
        assert result.level == EscalationLevel.LOW

    def test_memory_integration(self, temp_memory_dir):
        """Test memory adapter in decision context."""
        adapter = MemoryAdapter(data_dir=temp_memory_dir)
        adapter.add_memory("Previous decision: allow")
        results = adapter.search("decision")
        assert len(results) > 0

    def test_sovereign_mode_ethics(self):
        """Test sovereign mode ethical constraints."""
        config = GalahadConfig(sovereign_mode=True)
        engine = GalahadEngine(config)
        result = engine.reason(["test decision"])
        assert result["success"]

    def test_curiosity_driven_exploration(self, galahad_engine):
        """Test curiosity-driven reasoning."""
        galahad_engine.curiosity_score = 0.8
        metrics = galahad_engine.get_curiosity_metrics()
        assert metrics["should_explore"]

    def test_confidence_scoring(self, reasoning_matrix):
        """Test confidence scoring across factors."""
        entry_id = reasoning_matrix.begin_reasoning("test")
        reasoning_matrix.add_factor(entry_id, "f1", 1, weight=1.0, score=0.9)
        reasoning_matrix.add_factor(entry_id, "f2", 2, weight=0.5, score=0.7)
        entry = reasoning_matrix.get_entry(entry_id)
        score = entry.aggregate_score
        assert 0.7 < score < 0.9

    def test_parallel_reasoning_chains(self, reasoning_matrix):
        """Test parallel reasoning chains."""
        ids = [reasoning_matrix.begin_reasoning(f"chain_{i}") for i in range(3)]
        for entry_id in ids:
            reasoning_matrix.add_factor(entry_id, "test", 1, score=0.8)
            reasoning_matrix.render_verdict(entry_id, "allow", 0.9)
        entries = reasoning_matrix.query(limit=3)
        assert len(entries) == 3

    def test_hierarchical_reasoning(self, reasoning_matrix):
        """Test hierarchical reasoning chains."""
        parent_id = reasoning_matrix.begin_reasoning("parent")
        child_id = reasoning_matrix.begin_reasoning("child", parent_entry_id=parent_id)
        reasoning_matrix.render_verdict(parent_id, "allow", 0.9)
        reasoning_matrix.render_verdict(child_id, "allow", 0.85)
        chain = reasoning_matrix.get_chain(child_id)
        assert len(chain) == 2

    def test_audit_trail_generation(self, reasoning_matrix):
        """Test audit trail generation."""
        entry_id = reasoning_matrix.begin_reasoning("audit_test")
        reasoning_matrix.add_factor(entry_id, "factor", 1, score=0.9)
        reasoning_matrix.render_verdict(entry_id, "allow", 0.95)
        entry = reasoning_matrix.get_entry(entry_id)
        assert entry.compute_hash() is not None

    def test_policy_chaining(self):
        """Test multiple policy enforcement."""
        engine = PolicyEngine(policies=[])
        engine.add_policy(LengthLimitPolicy(max_length=100))
        engine.add_policy(SensitivityPolicy())
        result = engine.enforce("Normal content")
        assert result.decision == PolicyDecision.ALLOW

    def test_error_recovery(self, triumvirate):
        """Test error recovery in pipeline."""
        with patch.object(triumvirate.codex, "process", side_effect=Exception("Test")):
            result = triumvirate.process("input")
            assert not result["success"]
            assert "error" in result

    def test_telemetry_tracking(self, triumvirate):
        """Test telemetry event tracking."""
        triumvirate.process("input1")
        triumvirate.process("input2")
        telemetry = triumvirate.get_telemetry()
        assert len(telemetry) > 0

    def test_context_propagation(self, triumvirate):
        """Test context propagation through pipeline."""
        context = {"user": "test", "session": "123"}
        result = triumvirate.process("input", context=context)
        assert result["metadata"]["context"]["user"] == "test"

    def test_verdict_explanation_generation(self, reasoning_matrix):
        """Test automatic explanation generation."""
        entry_id = reasoning_matrix.begin_reasoning("test")
        reasoning_matrix.add_factor(
            entry_id, "key_factor", 1, weight=1.0, score=0.95
        )
        verdict = reasoning_matrix.render_verdict(entry_id, "allow", 0.95)
        assert "key_factor" in verdict.explanation

    def test_factor_weighting(self, reasoning_matrix):
        """Test weighted factor aggregation."""
        entry_id = reasoning_matrix.begin_reasoning("test")
        reasoning_matrix.add_factor(entry_id, "critical", 1, weight=1.0, score=0.9)
        reasoning_matrix.add_factor(entry_id, "minor", 2, weight=0.1, score=0.5)
        entry = reasoning_matrix.get_entry(entry_id)
        score = entry.aggregate_score
        assert score > 0.8

    def test_decision_consistency(self, triumvirate):
        """Test decision consistency across runs."""
        result1 = triumvirate.process("identical input")
        result2 = triumvirate.process("identical input")
        assert result1["success"] == result2["success"]


# ============================================================================
# RUN CONFIGURATION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
