"""
Reasoning Matrix Core — Track, Score, and Formalize Reasoning.

This module provides the core data structures and orchestrator for
capturing decision reasoning across all Project AI subsystems.

Zero external dependencies — uses only stdlib.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------


@dataclass
class ReasoningFactor:
    """A single consideration in a decision.

    Represents one piece of evidence or signal that influenced (or argued
    against) a particular verdict.

    Attributes:
        name: Human-readable label (e.g., "cerberus_validation").
        value: Raw observed value — any JSON-serializable type.
        weight: Importance of this factor to the decision (0.0–1.0).
        score: Normalized score after evaluation (0.0–1.0).
                None until explicitly scored.
        source: Which subsystem provided this factor.
        rationale: Why this factor matters to the decision.
        timestamp: When the factor was recorded (monotonic ns).
    """

    name: str
    value: Any
    weight: float = 1.0
    score: float | None = None
    source: str = ""
    rationale: str = ""
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError(f"weight must be in [0.0, 1.0], got {self.weight}")
        if self.score is not None and not 0.0 <= self.score <= 1.0:
            raise ValueError(f"score must be in [0.0, 1.0] or None, got {self.score}")

    @property
    def weighted_score(self) -> float | None:
        """Return weight × score, or None if unscored."""
        if self.score is None:
            return None
        return self.weight * self.score

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "value": _safe_serialize(self.value),
            "weight": self.weight,
            "score": self.score,
            "weighted_score": self.weighted_score,
            "source": self.source,
            "rationale": self.rationale,
            "timestamp": self.timestamp,
        }


@dataclass
class ReasoningVerdict:
    """The final decision of a reasoning process.

    Attributes:
        decision: The outcome (e.g., "allow", "deny", "explore").
        confidence: Overall confidence in the verdict (0.0–1.0).
        dominant_factors: Names of factors that most drove the decision.
        dissenting_factors: Names of factors that argued against it.
        explanation: Human-readable summary of the reasoning.
        timestamp: When the verdict was rendered.
    """

    decision: str
    confidence: float
    dominant_factors: list[str] = field(default_factory=list)
    dissenting_factors: list[str] = field(default_factory=list)
    explanation: str = ""
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0.0, 1.0], got {self.confidence}")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "decision": self.decision,
            "confidence": self.confidence,
            "dominant_factors": self.dominant_factors,
            "dissenting_factors": self.dissenting_factors,
            "explanation": self.explanation,
            "timestamp": self.timestamp,
        }


@dataclass
class MatrixEntry:
    """A complete reasoning trace for one decision event.

    Entries can be chained via ``parent_entry_id`` to represent multi-step
    reasoning (e.g., Waterfall stage 2 → stage 1).

    Attributes:
        entry_id: Unique identifier for this entry.
        context_type: Subsystem that initiated reasoning
                      (e.g., "triumvirate_pipeline", "waterfall_stage").
        factors: All reasoning factors considered.
        verdict: The final verdict (None until rendered).
        parent_entry_id: ID of the parent entry in a reasoning chain.
        metadata: Arbitrary context dictionary.
        created_at: When this entry was created.
    """

    entry_id: str
    context_type: str
    factors: list[ReasoningFactor] = field(default_factory=list)
    verdict: ReasoningVerdict | None = None
    parent_entry_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    @property
    def is_finalized(self) -> bool:
        """Return True if a verdict has been rendered."""
        return self.verdict is not None

    @property
    def scored_factors(self) -> list[ReasoningFactor]:
        """Return only factors that have been scored."""
        return [f for f in self.factors if f.score is not None]

    @property
    def aggregate_score(self) -> float | None:
        """Compute weighted average of all scored factors.

        Returns None if no factors have been scored.
        """
        scored = self.scored_factors
        if not scored:
            return None
        total_weight = sum(f.weight for f in scored)
        if total_weight == 0:
            return 0.0
        return sum(f.weighted_score for f in scored) / total_weight

    def get_factor(self, name: str) -> ReasoningFactor | None:
        """Retrieve a factor by name."""
        for f in self.factors:
            if f.name == name:
                return f
        return None

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of this entry for audit integrity."""
        payload = json.dumps(self._to_dict_for_hash(), sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()

    def _to_dict_for_hash(self) -> dict[str, Any]:
        """Serialize without the hash field (avoids recursion)."""
        return {
            "entry_id": self.entry_id,
            "context_type": self.context_type,
            "factors": [f.to_dict() for f in self.factors],
            "verdict": self.verdict.to_dict() if self.verdict else None,
            "parent_entry_id": self.parent_entry_id,
            "metadata": _safe_serialize(self.metadata),
            "created_at": self.created_at,
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        d = self._to_dict_for_hash()
        d["aggregate_score"] = self.aggregate_score
        d["hash"] = self.compute_hash() if self.is_finalized else None
        return d


# ---------------------------------------------------------------------------
# Reasoning Matrix Orchestrator
# ---------------------------------------------------------------------------


class ReasoningMatrix:
    """Orchestrator that tracks, scores, and queries reasoning decisions.

    Thread-safety note: This implementation is designed for single-threaded
    use per instance.  For concurrent access, wrap calls with a lock.

    Args:
        max_history: Maximum number of entries to retain in memory.
    """

    def __init__(self, max_history: int = 10_000) -> None:
        self._entries: dict[str, MatrixEntry] = {}
        self._history: deque[str] = deque()
        self._max_history = max_history
        self._stats = _MatrixStats()
        logger.info("ReasoningMatrix initialized (max_history=%d)", max_history)

    # -- Lifecycle -----------------------------------------------------------

    def begin_reasoning(
        self,
        context_type: str,
        metadata: dict[str, Any] | None = None,
        parent_entry_id: str | None = None,
    ) -> str:
        """Start tracking a new reasoning decision.

        Args:
            context_type: Subsystem initiating reasoning
                          (e.g., "triumvirate_pipeline").
            metadata: Optional context dictionary.
            parent_entry_id: Optional parent entry for chaining.

        Returns:
            Unique entry_id for this reasoning trace.
        """
        entry_id = f"rm-{uuid4().hex[:12]}"
        entry = MatrixEntry(
            entry_id=entry_id,
            context_type=context_type,
            parent_entry_id=parent_entry_id,
            metadata=metadata or {},
        )
        self._entries[entry_id] = entry
        self._history.append(entry_id)
        self._stats.total_started += 1

        # Evict oldest entries if over capacity
        while len(self._entries) > self._max_history:
            oldest_id = self._history.popleft()
            self._entries.pop(oldest_id, None)

        logger.debug(
            "Reasoning started: entry_id=%s context=%s",
            entry_id,
            context_type,
        )
        return entry_id

    def add_factor(
        self,
        entry_id: str,
        name: str,
        value: Any,
        *,
        weight: float = 1.0,
        score: float | None = None,
        source: str = "",
        rationale: str = "",
    ) -> ReasoningFactor:
        """Register a reasoning factor for a decision.

        Args:
            entry_id: The entry to add the factor to.
            name: Human-readable factor label.
            value: Raw observed value.
            weight: Importance (0.0–1.0).
            score: Optional initial score (0.0–1.0).
            source: Subsystem that produced this factor.
            rationale: Why this factor matters.

        Returns:
            The created ReasoningFactor.

        Raises:
            KeyError: If entry_id is unknown.
            ValueError: If entry is already finalized.
        """
        entry = self._get_entry_or_raise(entry_id)
        if entry.is_finalized:
            raise ValueError(f"Cannot add factors to finalized entry {entry_id}")

        factor = ReasoningFactor(
            name=name,
            value=value,
            weight=weight,
            score=score,
            source=source,
            rationale=rationale,
        )
        entry.factors.append(factor)
        self._stats.total_factors += 1

        logger.debug(
            "Factor added: entry=%s name=%s source=%s weight=%.2f",
            entry_id,
            name,
            source,
            weight,
        )
        return factor

    def score_factor(self, entry_id: str, factor_name: str, score: float) -> None:
        """Apply a normalized score to a named factor.

        Args:
            entry_id: The entry containing the factor.
            factor_name: Name of the factor to score.
            score: Normalized score (0.0–1.0).

        Raises:
            KeyError: If entry_id is unknown.
            ValueError: If factor not found or entry finalized.
        """
        if not 0.0 <= score <= 1.0:
            raise ValueError(f"score must be in [0.0, 1.0], got {score}")

        entry = self._get_entry_or_raise(entry_id)
        if entry.is_finalized:
            raise ValueError(f"Cannot score factors on finalized entry {entry_id}")

        factor = entry.get_factor(factor_name)
        if factor is None:
            raise ValueError(f"Factor '{factor_name}' not found in entry {entry_id}")

        factor.score = score
        logger.debug(
            "Factor scored: entry=%s factor=%s score=%.3f",
            entry_id,
            factor_name,
            score,
        )

    def render_verdict(
        self,
        entry_id: str,
        decision: str,
        confidence: float,
        *,
        explanation: str = "",
    ) -> ReasoningVerdict:
        """Finalize reasoning with a verdict.

        Automatically computes dominant and dissenting factors based on
        scored factor values.

        Args:
            entry_id: The entry to finalize.
            decision: The outcome (e.g., "allow", "deny").
            confidence: Overall confidence (0.0–1.0).
            explanation: Optional human-readable summary.

        Returns:
            The rendered ReasoningVerdict.

        Raises:
            KeyError: If entry_id is unknown.
            ValueError: If entry is already finalized.
        """
        entry = self._get_entry_or_raise(entry_id)
        if entry.is_finalized:
            raise ValueError(f"Entry {entry_id} already has a verdict")

        # Auto-classify factors into dominant and dissenting
        dominant = []
        dissenting = []
        threshold = 0.5

        for f in entry.scored_factors:
            if f.score >= threshold:
                dominant.append(f.name)
            else:
                dissenting.append(f.name)

        # Sort by weighted score (highest first for dominant)
        scored = entry.scored_factors
        scored_sorted = sorted(
            scored,
            key=lambda f: f.weighted_score or 0,
            reverse=True,
        )
        dominant = [f.name for f in scored_sorted if (f.score or 0) >= threshold]
        dissenting = [f.name for f in scored_sorted if (f.score or 0) < threshold]

        # Generate explanation if not provided
        if not explanation and scored_sorted:
            top = scored_sorted[0]
            explanation = (
                f"Decision '{decision}' driven primarily by "
                f"'{top.name}' (score={top.score:.2f}, "
                f"weight={top.weight:.2f}). "
                f"{len(dominant)} supporting factor(s), "
                f"{len(dissenting)} dissenting."
            )

        verdict = ReasoningVerdict(
            decision=decision,
            confidence=confidence,
            dominant_factors=dominant,
            dissenting_factors=dissenting,
            explanation=explanation,
        )
        entry.verdict = verdict
        self._stats.total_finalized += 1
        self._stats.total_confidence_sum += confidence

        logger.info(
            "Verdict rendered: entry=%s decision=%s confidence=%.3f "
            "dominant=%d dissenting=%d",
            entry_id,
            decision,
            confidence,
            len(dominant),
            len(dissenting),
        )
        return verdict

    # -- Querying ------------------------------------------------------------

    def get_entry(self, entry_id: str) -> MatrixEntry | None:
        """Retrieve a full reasoning trace by ID.

        Returns None if not found (may have been evicted).
        """
        return self._entries.get(entry_id)

    def get_chain(self, entry_id: str) -> list[MatrixEntry]:
        """Walk the parent chain starting from entry_id.

        Returns a list from the given entry back to the root, ordered
        [current, parent, grandparent, ...].
        """
        chain = []
        current_id: str | None = entry_id
        seen: set[str] = set()

        while current_id and current_id not in seen:
            seen.add(current_id)
            entry = self._entries.get(current_id)
            if entry is None:
                break
            chain.append(entry)
            current_id = entry.parent_entry_id

        return chain

    def query(
        self,
        *,
        context_type: str | None = None,
        min_confidence: float | None = None,
        decision_filter: str | None = None,
        limit: int = 50,
    ) -> list[MatrixEntry]:
        """Search reasoning history with optional filters.

        Args:
            context_type: Filter by subsystem type.
            min_confidence: Minimum confidence threshold.
            decision_filter: Filter by decision outcome.
            limit: Maximum results to return.

        Returns:
            Matching entries, most recent first.
        """
        results = []
        for entry_id in reversed(self._history):
            if len(results) >= limit:
                break
            entry = self._entries.get(entry_id)
            if entry is None:
                continue

            if context_type and entry.context_type != context_type:
                continue
            if entry.verdict is None:
                continue
            if min_confidence is not None and (
                entry.verdict.confidence < min_confidence
            ):
                continue
            if decision_filter and entry.verdict.decision != decision_filter:
                continue

            results.append(entry)

        return results

    # -- Audit & Statistics --------------------------------------------------

    def export_audit(self, entry_ids: list[str] | None = None) -> dict[str, Any]:
        """Serialize entries for the sovereign audit trail.

        Args:
            entry_ids: Specific entries to export.
                       If None, exports all finalized entries.

        Returns:
            Audit-ready dictionary with entries and integrity hashes.
        """
        if entry_ids is None:
            targets = [
                self._entries[eid]
                for eid in self._history
                if eid in self._entries and self._entries[eid].is_finalized
            ]
        else:
            targets = [self._entries[eid] for eid in entry_ids if eid in self._entries]

        entries_data = [e.to_dict() for e in targets]

        # Compute bundle integrity hash
        bundle_payload = json.dumps(entries_data, sort_keys=True, default=str)
        bundle_hash = hashlib.sha256(bundle_payload.encode()).hexdigest()

        return {
            "reasoning_matrix_version": "1.0.0",
            "exported_at": time.time(),
            "entry_count": len(entries_data),
            "entries": entries_data,
            "bundle_hash": bundle_hash,
            "statistics": self.get_statistics(),
        }

    def get_statistics(self) -> dict[str, Any]:
        """Aggregate metrics about reasoning activity.

        Returns:
            Dictionary with counts, averages, and breakdown by context.
        """
        context_counts: dict[str, int] = {}
        decision_counts: dict[str, int] = {}

        for entry_id in self._history:
            entry = self._entries.get(entry_id)
            if entry is None:
                continue
            ctx = entry.context_type
            context_counts[ctx] = context_counts.get(ctx, 0) + 1
            if entry.verdict:
                dec = entry.verdict.decision
                decision_counts[dec] = decision_counts.get(dec, 0) + 1

        avg_confidence = (
            self._stats.total_confidence_sum / self._stats.total_finalized
            if self._stats.total_finalized > 0
            else 0.0
        )

        return {
            "total_started": self._stats.total_started,
            "total_finalized": self._stats.total_finalized,
            "total_factors": self._stats.total_factors,
            "pending": self._stats.total_started - self._stats.total_finalized,
            "average_confidence": round(avg_confidence, 4),
            "entries_in_memory": len(self._entries),
            "by_context": context_counts,
            "by_decision": decision_counts,
        }

    # -- Internal helpers ----------------------------------------------------

    def _get_entry_or_raise(self, entry_id: str) -> MatrixEntry:
        """Retrieve entry or raise KeyError."""
        entry = self._entries.get(entry_id)
        if entry is None:
            raise KeyError(f"Unknown reasoning entry: {entry_id}")
        return entry


@dataclass
class _MatrixStats:
    """Internal statistics tracker."""

    total_started: int = 0
    total_finalized: int = 0
    total_factors: int = 0
    total_confidence_sum: float = 0.0


def _safe_serialize(value: Any) -> Any:
    """Best-effort JSON-safe serialization of arbitrary values."""
    if isinstance(value, dict):
        return {str(k): _safe_serialize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe_serialize(v) for v in value]
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    return str(value)


__all__ = [
    "ReasoningFactor",
    "ReasoningVerdict",
    "MatrixEntry",
    "ReasoningMatrix",
]
