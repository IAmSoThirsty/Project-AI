"""
Reasoning Matrix - Orchestration and Audit Trail for Multi-Engine Reasoning

Provides:
- Unified interface for recording reasoning decisions across engines
- Temporal chaining of parent-child reasoning entries
- Verdict rendering with automatic factor classification
- Audit export with integrity hashing
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from typing import Any

logger = logging.getLogger(__name__)


class ReasoningFactor:
    """A single weighted evidence factor within a reasoning entry."""

    def __init__(
        self,
        name: str,
        value: Any,
        weight: float = 1.0,
        score: float | None = None,
        source: str = "",
        rationale: str = "",
        timestamp: float | None = None,
    ):
        if not (0.0 <= weight <= 1.0):
            raise ValueError(f"weight must be in [0.0, 1.0], got {weight}")
        if score is not None and not (0.0 <= score <= 1.0):
            raise ValueError(f"score must be in [0.0, 1.0], got {score}")

        self.name = name
        self.value = value
        self.weight = weight
        self.score = score
        self.source = source
        self.rationale = rationale
        self.timestamp = timestamp if timestamp is not None else time.time()

    @property
    def weighted_score(self) -> float | None:
        if self.score is None:
            return None
        return self.weight * self.score

    def to_dict(self) -> dict:
        try:
            json.dumps(self.value)
            value = self.value
        except (TypeError, ValueError):
            value = str(self.value)

        return {
            "name": self.name,
            "value": value,
            "weight": self.weight,
            "score": self.score,
            "weighted_score": self.weighted_score,
            "source": self.source,
            "rationale": self.rationale,
            "timestamp": self.timestamp,
        }


class ReasoningVerdict:
    """A finalized decision rendered over a reasoning entry's factors."""

    def __init__(
        self,
        decision: str,
        confidence: float,
        dominant_factors: list[str] | None = None,
        dissenting_factors: list[str] | None = None,
        explanation: str | None = None,
        timestamp: float | None = None,
    ):
        if not (0.0 <= confidence <= 1.0):
            raise ValueError(f"confidence must be in [0.0, 1.0], got {confidence}")

        self.decision = decision
        self.confidence = confidence
        self.dominant_factors = dominant_factors or []
        self.dissenting_factors = dissenting_factors or []
        self.explanation = explanation
        self.timestamp = timestamp if timestamp is not None else time.time()

    def to_dict(self) -> dict:
        return {
            "decision": self.decision,
            "confidence": self.confidence,
            "dominant_factors": self.dominant_factors,
            "dissenting_factors": self.dissenting_factors,
            "explanation": self.explanation,
            "timestamp": self.timestamp,
        }


class MatrixEntry:
    """A single reasoning session: factors accumulated, verdict rendered."""

    def __init__(
        self,
        entry_id: str,
        context_type: str,
        parent_entry_id: str | None = None,
        metadata: dict | None = None,
        created_at: float | None = None,
    ):
        self.entry_id = entry_id
        self.context_type = context_type
        self.parent_entry_id = parent_entry_id
        self.metadata = metadata or {}
        self.created_at = created_at if created_at is not None else time.time()
        self.factors: list[ReasoningFactor] = []
        self.verdict: ReasoningVerdict | None = None
        self.hash: str | None = None

    @property
    def is_finalized(self) -> bool:
        return self.verdict is not None

    @property
    def scored_factors(self) -> list[ReasoningFactor]:
        return [f for f in self.factors if f.score is not None]

    @property
    def aggregate_score(self) -> float | None:
        scored = self.scored_factors
        if not scored:
            return None
        total_weight = sum(f.weight for f in scored)
        if total_weight == 0:
            return None
        return sum(f.weighted_score for f in scored) / total_weight  # type: ignore[misc]

    def get_factor(self, name: str) -> ReasoningFactor | None:
        for f in self.factors:
            if f.name == name:
                return f
        return None

    def compute_hash(self) -> str:
        factor_names = sorted(f.name for f in self.factors)
        verdict_decision = self.verdict.decision if self.verdict else ""
        payload = json.dumps(
            {
                "entry_id": self.entry_id,
                "context_type": self.context_type,
                "factor_names": factor_names,
                "verdict_decision": verdict_decision,
                "created_at": self.created_at,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def to_dict(self) -> dict:
        h = self.compute_hash() if self.is_finalized else None
        return {
            "entry_id": self.entry_id,
            "context_type": self.context_type,
            "parent_entry_id": self.parent_entry_id,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "factors": [f.to_dict() for f in self.factors],
            "verdict": self.verdict.to_dict() if self.verdict else None,
            "hash": h,
            "is_finalized": self.is_finalized,
            "aggregate_score": self.aggregate_score,
        }


class ReasoningMatrix:
    """
    Orchestrator that manages the full lifecycle of reasoning entries.

    Tracks evidence accumulation, verdict rendering, parent-child chains,
    and exports deterministic audit bundles.
    """

    def __init__(self, max_history: int = 10000):
        self._max_history = max_history
        self._entries: dict[str, MatrixEntry] = {}

    def begin_reasoning(
        self,
        context_type: str,
        metadata: dict | None = None,
        parent_entry_id: str | None = None,
    ) -> str:
        entry_id = f"rm-{uuid.uuid4().hex[:12]}"
        entry = MatrixEntry(
            entry_id=entry_id,
            context_type=context_type,
            parent_entry_id=parent_entry_id,
            metadata=metadata,
        )
        self._entries[entry_id] = entry
        while len(self._entries) > self._max_history:
            oldest = next(iter(self._entries))
            del self._entries[oldest]
        return entry_id

    def add_factor(
        self,
        entry_id: str,
        name: str,
        value: Any,
        weight: float = 1.0,
        score: float | None = None,
        source: str = "",
        rationale: str = "",
    ) -> ReasoningFactor:
        if entry_id not in self._entries:
            raise KeyError(f"Unknown entry: {entry_id}")
        entry = self._entries[entry_id]
        if entry.is_finalized:
            raise ValueError(f"Entry {entry_id} is finalized")
        factor = ReasoningFactor(
            name=name,
            value=value,
            weight=weight,
            score=score,
            source=source,
            rationale=rationale,
        )
        entry.factors.append(factor)
        return factor

    def score_factor(self, entry_id: str, factor_name: str, score: float) -> None:
        if entry_id not in self._entries:
            raise KeyError(f"Unknown entry: {entry_id}")
        if not (0.0 <= score <= 1.0):
            raise ValueError(f"score must be in [0.0, 1.0], got {score}")
        entry = self._entries[entry_id]
        factor = entry.get_factor(factor_name)
        if factor is None:
            raise ValueError(f"Factor '{factor_name}' not found in entry {entry_id}")
        factor.score = score

    def render_verdict(
        self,
        entry_id: str,
        decision: str,
        confidence: float,
        dominant_factors: list[str] | None = None,
        dissenting_factors: list[str] | None = None,
        explanation: str | None = None,
    ) -> ReasoningVerdict:
        if entry_id not in self._entries:
            raise KeyError(f"Unknown entry: {entry_id}")
        entry = self._entries[entry_id]
        if entry.verdict is not None:
            raise ValueError(f"Entry {entry_id} already has a verdict")

        if dominant_factors is None and dissenting_factors is None:
            dominant_factors = []
            dissenting_factors = []
            for f in entry.factors:
                if f.score is not None and f.score > 0.5:
                    dominant_factors.append(f.name)
                elif f.score is not None:
                    dissenting_factors.append(f.name)

        if explanation is None:
            scored = entry.scored_factors
            if scored:
                top = max(scored, key=lambda f: f.weighted_score or 0.0)
                explanation = f"[{decision}] based on {top.name} and others"
            elif entry.factors:
                explanation = f"[{decision}] based on available factors"
            else:
                explanation = f"[{decision}] no factors recorded"

        verdict = ReasoningVerdict(
            decision=decision,
            confidence=confidence,
            dominant_factors=dominant_factors,
            dissenting_factors=dissenting_factors,
            explanation=explanation,
        )
        entry.verdict = verdict
        entry.hash = entry.compute_hash()
        return verdict

    def get_entry(self, entry_id: str) -> MatrixEntry | None:
        return self._entries.get(entry_id)

    def get_chain(self, entry_id: str) -> list[MatrixEntry]:
        chain: list[MatrixEntry] = []
        current_id: str | None = entry_id
        seen: set[str] = set()
        while current_id is not None and current_id not in seen:
            entry = self._entries.get(current_id)
            if entry is None:
                break
            chain.append(entry)
            seen.add(current_id)
            current_id = entry.parent_entry_id
        return chain

    def query(
        self,
        context_type: str | None = None,
        decision_filter: str | None = None,
        min_confidence: float = 0.0,
        limit: int | None = None,
    ) -> list[MatrixEntry]:
        results: list[MatrixEntry] = []
        for entry in self._entries.values():
            if not entry.is_finalized:
                continue
            if context_type is not None and entry.context_type != context_type:
                continue
            if decision_filter is not None and entry.verdict.decision != decision_filter:  # type: ignore[union-attr]
                continue
            if entry.verdict.confidence < min_confidence:  # type: ignore[union-attr]
                continue
            results.append(entry)
            if limit is not None and len(results) >= limit:
                break
        return results

    def export_audit(self, entry_ids: list[str] | None = None) -> dict:
        if entry_ids is None:
            entries = [e for e in self._entries.values() if e.is_finalized]
        else:
            entries = [self._entries[eid] for eid in entry_ids if eid in self._entries]

        entry_dicts = [e.to_dict() for e in entries]
        hashes = sorted(e.compute_hash() for e in entries)
        bundle_hash = hashlib.sha256(json.dumps(hashes).encode()).hexdigest()

        return {
            "reasoning_matrix_version": "1.0.0",
            "entry_count": len(entries),
            "entries": entry_dicts,
            "bundle_hash": bundle_hash,
        }

    def get_statistics(self) -> dict:
        all_entries = list(self._entries.values())
        finalized = [e for e in all_entries if e.is_finalized]

        avg_confidence = (
            sum(e.verdict.confidence for e in finalized) / len(finalized)  # type: ignore[union-attr]
            if finalized
            else 0.0
        )

        by_context: dict[str, int] = {}
        for e in all_entries:
            by_context[e.context_type] = by_context.get(e.context_type, 0) + 1

        by_decision: dict[str, int] = {}
        for e in finalized:
            by_decision[e.verdict.decision] = by_decision.get(e.verdict.decision, 0) + 1  # type: ignore[union-attr]

        return {
            "total_started": len(all_entries),
            "total_finalized": len(finalized),
            "pending": len(all_entries) - len(finalized),
            "total_factors": sum(len(e.factors) for e in all_entries),
            "average_confidence": avg_confidence,
            "by_context": by_context,
            "by_decision": by_decision,
            "entries_in_memory": len(self._entries),
        }
