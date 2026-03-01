"""
Tests for the Reasoning Matrix — core module and subsystem integrations.

Covers:
    - ReasoningFactor creation, validation, serialization
    - ReasoningVerdict rendering and properties
    - MatrixEntry lifecycle, chaining, hashing
    - ReasoningMatrix orchestrator: lifecycle, querying, audit export
    - Galahad integration (reasoning traces)
    - Statistics and edge cases
"""

from __future__ import annotations

import json

import pytest

from src.cognition.reasoning_matrix.core import (
    MatrixEntry,
    ReasoningFactor,
    ReasoningMatrix,
    ReasoningVerdict,
)

# ======================================================================
# ReasoningFactor
# ======================================================================


class TestReasoningFactor:
    """Tests for the ReasoningFactor data class."""

    def test_basic_creation(self):
        f = ReasoningFactor(
            name="test_factor",
            value="hello",
            weight=0.8,
            source="galahad",
            rationale="Testing",
        )
        assert f.name == "test_factor"
        assert f.value == "hello"
        assert f.weight == 0.8
        assert f.score is None
        assert f.source == "galahad"
        assert f.rationale == "Testing"

    def test_weight_boundaries(self):
        # Valid boundaries
        ReasoningFactor(name="low", value=1, weight=0.0)
        ReasoningFactor(name="high", value=1, weight=1.0)

        # Out of range
        with pytest.raises(ValueError, match="weight"):
            ReasoningFactor(name="bad", value=1, weight=-0.1)
        with pytest.raises(ValueError, match="weight"):
            ReasoningFactor(name="bad", value=1, weight=1.1)

    def test_score_boundaries(self):
        ReasoningFactor(name="s", value=1, score=0.0)
        ReasoningFactor(name="s", value=1, score=1.0)

        with pytest.raises(ValueError, match="score"):
            ReasoningFactor(name="s", value=1, score=-0.01)
        with pytest.raises(ValueError, match="score"):
            ReasoningFactor(name="s", value=1, score=1.01)

    def test_weighted_score(self):
        f = ReasoningFactor(name="f", value=1, weight=0.5, score=0.8)
        assert f.weighted_score == pytest.approx(0.4)

    def test_weighted_score_none_when_unscored(self):
        f = ReasoningFactor(name="f", value=1, weight=0.5)
        assert f.weighted_score is None

    def test_to_dict(self):
        f = ReasoningFactor(
            name="f",
            value={"nested": True},
            weight=0.9,
            score=0.7,
            source="cerberus",
            rationale="Policy check",
        )
        d = f.to_dict()
        assert d["name"] == "f"
        assert d["value"] == {"nested": True}
        assert d["weight"] == 0.9
        assert d["score"] == 0.7
        assert d["weighted_score"] == pytest.approx(0.63)
        assert d["source"] == "cerberus"

    def test_non_serializable_value(self):
        """Values that aren't JSON-native should be str-coerced."""
        f = ReasoningFactor(name="f", value=object())
        d = f.to_dict()
        # Should be a string representation, not crash
        assert isinstance(d["value"], str)


# ======================================================================
# ReasoningVerdict
# ======================================================================


class TestReasoningVerdict:
    """Tests for the ReasoningVerdict data class."""

    def test_basic_creation(self):
        v = ReasoningVerdict(
            decision="allow",
            confidence=0.95,
            dominant_factors=["cerberus_validation"],
            dissenting_factors=["codex_low_confidence"],
            explanation="All checks passed",
        )
        assert v.decision == "allow"
        assert v.confidence == 0.95
        assert "cerberus_validation" in v.dominant_factors
        assert "codex_low_confidence" in v.dissenting_factors

    def test_confidence_validation(self):
        with pytest.raises(ValueError, match="confidence"):
            ReasoningVerdict(decision="deny", confidence=-0.1)
        with pytest.raises(ValueError, match="confidence"):
            ReasoningVerdict(decision="deny", confidence=1.1)

    def test_to_dict(self):
        v = ReasoningVerdict(decision="deny", confidence=0.9)
        d = v.to_dict()
        assert d["decision"] == "deny"
        assert d["confidence"] == 0.9
        assert isinstance(d["timestamp"], float)


# ======================================================================
# MatrixEntry
# ======================================================================


class TestMatrixEntry:
    """Tests for the MatrixEntry data class."""

    def test_basic_lifecycle(self):
        entry = MatrixEntry(
            entry_id="test-001",
            context_type="triumvirate_pipeline",
        )
        assert not entry.is_finalized
        assert entry.scored_factors == []
        assert entry.aggregate_score is None

    def test_add_and_retrieve_factor(self):
        entry = MatrixEntry(entry_id="e1", context_type="test")
        f = ReasoningFactor(name="f1", value=True, weight=0.8, score=0.9)
        entry.factors.append(f)

        assert entry.get_factor("f1") is f
        assert entry.get_factor("nonexistent") is None

    def test_aggregate_score(self):
        entry = MatrixEntry(entry_id="e1", context_type="test")
        entry.factors.append(ReasoningFactor(name="a", value=1, weight=0.6, score=1.0))
        entry.factors.append(ReasoningFactor(name="b", value=1, weight=0.4, score=0.5))
        # Weighted avg: (0.6*1.0 + 0.4*0.5) / (0.6 + 0.4)
        # = (0.6 + 0.2) / 1.0 = 0.8
        assert entry.aggregate_score == pytest.approx(0.8)

    def test_aggregate_score_ignores_unscored(self):
        entry = MatrixEntry(entry_id="e1", context_type="test")
        entry.factors.append(
            ReasoningFactor(name="scored", value=1, weight=1.0, score=0.7)
        )
        entry.factors.append(ReasoningFactor(name="unscored", value=1, weight=1.0))
        # Only the scored factor should count
        assert entry.aggregate_score == pytest.approx(0.7)

    def test_parent_chaining(self):
        parent = MatrixEntry(entry_id="parent", context_type="waterfall_pipeline")
        child = MatrixEntry(
            entry_id="child",
            context_type="waterfall_stage",
            parent_entry_id="parent",
        )
        assert child.parent_entry_id == parent.entry_id

    def test_compute_hash_deterministic(self):
        entry = MatrixEntry(entry_id="e1", context_type="test")
        entry.factors.append(
            ReasoningFactor(
                name="f",
                value=42,
                weight=1.0,
                score=0.5,
                timestamp=1000.0,
            )
        )
        entry.verdict = ReasoningVerdict(
            decision="allow",
            confidence=0.9,
            timestamp=1001.0,
        )
        entry.created_at = 999.0
        h1 = entry.compute_hash()
        h2 = entry.compute_hash()
        assert h1 == h2
        assert len(h1) == 64  # SHA-256

    def test_to_dict_includes_hash_when_finalized(self):
        entry = MatrixEntry(entry_id="e1", context_type="test")
        d1 = entry.to_dict()
        assert d1["hash"] is None  # Not finalized

        entry.verdict = ReasoningVerdict(decision="allow", confidence=0.95)
        d2 = entry.to_dict()
        assert d2["hash"] is not None


# ======================================================================
# ReasoningMatrix (orchestrator)
# ======================================================================


class TestReasoningMatrix:
    """Tests for the ReasoningMatrix orchestrator."""

    def test_full_lifecycle(self):
        matrix = ReasoningMatrix()

        # Begin
        eid = matrix.begin_reasoning(
            "triumvirate_pipeline",
            {"correlation_id": "abc123"},
        )
        assert eid.startswith("rm-")

        # Add factors
        matrix.add_factor(
            eid,
            "validation",
            True,
            weight=1.0,
            score=1.0,
            source="cerberus",
            rationale="Passed",
        )
        matrix.add_factor(
            eid,
            "inference",
            {"conf": 0.9},
            weight=0.8,
            score=0.9,
            source="codex",
            rationale="High confidence",
        )
        matrix.add_factor(
            eid,
            "reasoning",
            "synthesized",
            weight=0.9,
            score=0.8,
            source="galahad",
            rationale="No contradictions",
        )

        # Score an unscored factor
        matrix.add_factor(
            eid,
            "enforcement",
            True,
            weight=1.0,
            source="cerberus",
            rationale="Output ok",
        )
        matrix.score_factor(eid, "enforcement", 1.0)

        # Verify entry state
        entry = matrix.get_entry(eid)
        assert entry is not None
        assert len(entry.factors) == 4
        assert not entry.is_finalized

        # Render verdict
        verdict = matrix.render_verdict(
            eid,
            "allow",
            0.95,
            explanation="All phases passed",
        )
        assert verdict.decision == "allow"
        assert verdict.confidence == 0.95
        assert entry.is_finalized

    def test_add_factor_to_finalized_raises(self):
        matrix = ReasoningMatrix()
        eid = matrix.begin_reasoning("test")
        matrix.render_verdict(eid, "allow", 0.9)

        with pytest.raises(ValueError, match="finalized"):
            matrix.add_factor(eid, "late", True, weight=1.0, source="test")

    def test_score_factor_nonexistent_raises(self):
        matrix = ReasoningMatrix()
        eid = matrix.begin_reasoning("test")
        with pytest.raises(ValueError, match="not found"):
            matrix.score_factor(eid, "nonexistent", 0.5)

    def test_score_factor_invalid_score_raises(self):
        matrix = ReasoningMatrix()
        eid = matrix.begin_reasoning("test")
        matrix.add_factor(eid, "f", True, weight=1.0)
        with pytest.raises(ValueError, match="score"):
            matrix.score_factor(eid, "f", 1.5)

    def test_double_verdict_raises(self):
        matrix = ReasoningMatrix()
        eid = matrix.begin_reasoning("test")
        matrix.render_verdict(eid, "allow", 0.9)

        with pytest.raises(ValueError, match="already has a verdict"):
            matrix.render_verdict(eid, "deny", 0.5)

    def test_unknown_entry_raises(self):
        matrix = ReasoningMatrix()
        with pytest.raises(KeyError, match="Unknown"):
            matrix.add_factor("bad-id", "f", True, weight=1.0)

    def test_get_entry_returns_none_for_unknown(self):
        matrix = ReasoningMatrix()
        assert matrix.get_entry("nonexistent") is None

    def test_auto_dominant_dissenting_classification(self):
        matrix = ReasoningMatrix()
        eid = matrix.begin_reasoning("test")
        matrix.add_factor(eid, "strong", True, weight=1.0, score=0.9, source="a")
        matrix.add_factor(eid, "weak", False, weight=0.5, score=0.3, source="b")
        matrix.add_factor(eid, "medium", "maybe", weight=0.7, score=0.6, source="c")

        verdict = matrix.render_verdict(eid, "allow", 0.8)
        assert "strong" in verdict.dominant_factors
        assert "medium" in verdict.dominant_factors
        assert "weak" in verdict.dissenting_factors


class TestReasoningMatrixChaining:
    """Tests for parent-child entry chaining."""

    def test_get_chain(self):
        matrix = ReasoningMatrix()
        root = matrix.begin_reasoning("pipeline")
        child = matrix.begin_reasoning("stage_1", parent_entry_id=root)
        grandchild = matrix.begin_reasoning("stage_2", parent_entry_id=child)

        chain = matrix.get_chain(grandchild)
        assert len(chain) == 3
        assert chain[0].entry_id == grandchild
        assert chain[1].entry_id == child
        assert chain[2].entry_id == root

    def test_get_chain_single_entry(self):
        matrix = ReasoningMatrix()
        eid = matrix.begin_reasoning("test")
        chain = matrix.get_chain(eid)
        assert len(chain) == 1

    def test_get_chain_broken_link(self):
        """Gracefully handle missing parent entry."""
        matrix = ReasoningMatrix()
        eid = matrix.begin_reasoning("orphan", parent_entry_id="deleted-parent")
        chain = matrix.get_chain(eid)
        assert len(chain) == 1


class TestReasoningMatrixQuery:
    """Tests for the query interface."""

    def _populate(self, matrix: ReasoningMatrix):
        """Create a mix of entries for testing."""
        for i in range(5):
            eid = matrix.begin_reasoning(
                "triumvirate_pipeline" if i % 2 == 0 else "waterfall_pipeline"
            )
            matrix.add_factor(eid, "f", i, weight=1.0, score=i / 5)
            matrix.render_verdict(
                eid,
                "allow" if i % 2 == 0 else "deny",
                confidence=i / 5,
            )

    def test_query_no_filters(self):
        matrix = ReasoningMatrix()
        self._populate(matrix)
        results = matrix.query()
        assert len(results) == 5

    def test_query_by_context_type(self):
        matrix = ReasoningMatrix()
        self._populate(matrix)
        results = matrix.query(context_type="triumvirate_pipeline")
        assert all(e.context_type == "triumvirate_pipeline" for e in results)
        assert len(results) == 3

    def test_query_by_decision(self):
        matrix = ReasoningMatrix()
        self._populate(matrix)
        results = matrix.query(decision_filter="deny")
        assert all(e.verdict.decision == "deny" for e in results)
        assert len(results) == 2

    def test_query_by_min_confidence(self):
        matrix = ReasoningMatrix()
        self._populate(matrix)
        results = matrix.query(min_confidence=0.5)
        assert all(e.verdict.confidence >= 0.5 for e in results)

    def test_query_limit(self):
        matrix = ReasoningMatrix()
        self._populate(matrix)
        results = matrix.query(limit=2)
        assert len(results) == 2

    def test_query_excludes_unfinalized(self):
        matrix = ReasoningMatrix()
        matrix.begin_reasoning("test")  # Not finalized
        results = matrix.query()
        assert len(results) == 0


class TestReasoningMatrixAudit:
    """Tests for audit export functionality."""

    def test_export_all_finalized(self):
        matrix = ReasoningMatrix()
        eid = matrix.begin_reasoning("test")
        matrix.add_factor(eid, "f", True, weight=1.0, score=1.0)
        matrix.render_verdict(eid, "allow", 0.95)

        # Unfinalized entry should not appear
        matrix.begin_reasoning("pending")

        audit = matrix.export_audit()
        assert audit["reasoning_matrix_version"] == "1.0.0"
        assert audit["entry_count"] == 1
        assert len(audit["entries"]) == 1
        assert len(audit["bundle_hash"]) == 64

    def test_export_specific_entries(self):
        matrix = ReasoningMatrix()
        eid1 = matrix.begin_reasoning("test1")
        matrix.render_verdict(eid1, "allow", 0.9)
        eid2 = matrix.begin_reasoning("test2")
        matrix.render_verdict(eid2, "deny", 0.8)

        audit = matrix.export_audit(entry_ids=[eid1])
        assert audit["entry_count"] == 1
        assert audit["entries"][0]["entry_id"] == eid1

    def test_export_is_json_serializable(self):
        matrix = ReasoningMatrix()
        eid = matrix.begin_reasoning("test", {"key": "value"})
        matrix.add_factor(eid, "f", {"nested": [1, 2]}, weight=0.5, score=0.7)
        matrix.render_verdict(eid, "allow", 0.9)

        audit = matrix.export_audit()
        # Should not raise
        serialized = json.dumps(audit, default=str)
        assert len(serialized) > 0

    def test_export_bundle_hash_integrity(self):
        """Same data should produce same hash."""
        matrix = ReasoningMatrix()
        eid = matrix.begin_reasoning("test")
        matrix.add_factor(
            eid,
            "f",
            42,
            weight=1.0,
            score=1.0,
        )
        matrix.render_verdict(eid, "allow", 0.99)

        audit1 = matrix.export_audit()
        audit2 = matrix.export_audit()
        assert audit1["bundle_hash"] == audit2["bundle_hash"]


class TestReasoningMatrixStatistics:
    """Tests for the statistics interface."""

    def test_initial_statistics(self):
        matrix = ReasoningMatrix()
        stats = matrix.get_statistics()
        assert stats["total_started"] == 0
        assert stats["total_finalized"] == 0
        assert stats["total_factors"] == 0
        assert stats["pending"] == 0
        assert stats["average_confidence"] == 0.0

    def test_statistics_after_activity(self):
        matrix = ReasoningMatrix()

        eid1 = matrix.begin_reasoning("type_a")
        matrix.add_factor(eid1, "f1", 1, weight=1.0, score=0.8)
        matrix.add_factor(eid1, "f2", 2, weight=0.5, score=0.6)
        matrix.render_verdict(eid1, "allow", 0.9)

        eid2 = matrix.begin_reasoning("type_b")
        matrix.add_factor(eid2, "f3", 3, weight=1.0)
        matrix.render_verdict(eid2, "deny", 0.7)

        # Pending entry
        matrix.begin_reasoning("type_a")

        stats = matrix.get_statistics()
        assert stats["total_started"] == 3
        assert stats["total_finalized"] == 2
        assert stats["total_factors"] == 3
        assert stats["pending"] == 1
        assert stats["average_confidence"] == pytest.approx(0.8)
        assert stats["by_context"]["type_a"] == 2
        assert stats["by_context"]["type_b"] == 1
        assert stats["by_decision"]["allow"] == 1
        assert stats["by_decision"]["deny"] == 1


class TestReasoningMatrixEviction:
    """Tests for history eviction under memory pressure."""

    def test_eviction_at_capacity(self):
        matrix = ReasoningMatrix(max_history=5)
        entry_ids = []
        for i in range(7):
            eid = matrix.begin_reasoning(f"ctx_{i}")
            entry_ids.append(eid)

        # First 2 should be evicted
        assert matrix.get_entry(entry_ids[0]) is None
        assert matrix.get_entry(entry_ids[1]) is None
        # Last 5 should remain
        for eid in entry_ids[2:]:
            assert matrix.get_entry(eid) is not None

        assert matrix.get_statistics()["entries_in_memory"] == 5


# ======================================================================
# Galahad Integration
# ======================================================================


class TestGalahadReasoningIntegration:
    """Tests for Galahad engine integration with ReasoningMatrix."""

    def test_galahad_produces_reasoning_trace(self):
        from src.cognition.galahad.engine import GalahadEngine

        matrix = ReasoningMatrix()
        engine = GalahadEngine(reasoning_matrix=matrix)

        result = engine.reason(
            [{"value": "hello", "confidence": 0.8}],
            context={"test": True},
        )

        assert result["success"] is True
        assert result["reasoning_entry_id"] is not None

        # Verify entry was created in matrix
        entry = matrix.get_entry(result["reasoning_entry_id"])
        assert entry is not None
        assert entry.context_type == "galahad_reasoning"
        assert entry.is_finalized
        assert entry.verdict.decision in ("synthesized", "arbitrated")
        assert len(entry.factors) > 0

    def test_galahad_without_matrix_works(self):
        """Galahad should work fine without a matrix (backward compat)."""
        from src.cognition.galahad.engine import GalahadEngine

        engine = GalahadEngine()  # No matrix
        result = engine.reason([{"value": "test"}])
        assert result["success"] is True
        assert result.get("reasoning_entry_id") is None

    def test_galahad_records_contradictions(self):
        from src.cognition.galahad.engine import GalahadEngine

        matrix = ReasoningMatrix()
        engine = GalahadEngine(reasoning_matrix=matrix)

        # Inputs that trigger contradiction detection
        result = engine.reason(
            [
                {"value": "allow this", "confidence": 0.9},
                {"value": "deny this", "confidence": 0.8},
            ],
        )

        assert result["success"] is True
        entry = matrix.get_entry(result["reasoning_entry_id"])
        assert entry is not None

        # Should have contradiction factor
        factor_names = [f.name for f in entry.factors]
        assert "contradictions_detected" in factor_names

    def test_galahad_records_curiosity(self):
        from src.cognition.galahad.engine import GalahadEngine

        matrix = ReasoningMatrix()
        engine = GalahadEngine(reasoning_matrix=matrix)

        result = engine.reason([{"value": "test"}])
        entry = matrix.get_entry(result["reasoning_entry_id"])

        factor_names = [f.name for f in entry.factors]
        assert "curiosity_signal" in factor_names
        assert "resolution_strategy" in factor_names


# ======================================================================
# Auto-generated explanation
# ======================================================================


class TestAutoExplanation:
    """Tests for auto-generated verdict explanations."""

    def test_auto_explanation_when_empty(self):
        matrix = ReasoningMatrix()
        eid = matrix.begin_reasoning("test")
        matrix.add_factor(eid, "top", True, weight=1.0, score=0.95, source="a")
        verdict = matrix.render_verdict(eid, "allow", 0.9)

        # Should auto-generate an explanation mentioning the top factor
        assert "top" in verdict.explanation
        assert "allow" in verdict.explanation

    def test_explicit_explanation_preserved(self):
        matrix = ReasoningMatrix()
        eid = matrix.begin_reasoning("test")
        matrix.add_factor(eid, "f", True, weight=1.0, score=0.9)
        verdict = matrix.render_verdict(
            eid,
            "deny",
            0.8,
            explanation="Custom explanation here",
        )
        assert verdict.explanation == "Custom explanation here"
