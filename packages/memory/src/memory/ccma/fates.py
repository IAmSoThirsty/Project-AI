"""
ccma.fates

Clotho, Lachesis, Atropos — implemented as three thin operator classes
over GraphStore, per CCMA Part III. They are NOT a separate memory store;
they are the only sanctioned callers of the lifecycle-mutation methods on
GraphStore (create_node for Clotho, reweigh_node/mark_active for Lachesis,
resolve_node for Atropos).

CCMA's constitutional rule: "No intelligence may directly change memory
permanence... Only constitutional policy may influence how the Fates
measure memory." In this codebase that rule is operationalized as: nothing
outside this module should call store.reweigh_node / store.resolve_node
directly. Enforce that at the application boundary (code review / import
linting), since Python won't stop a determined caller from importing
store.py directly — the constitutional rule is a discipline this module
exists to make easy to follow, not a hard language-level guarantee.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from .interfaces import AuthorityProvider
from .models import LifecycleState, Region, UniversalNode
from .store import GraphStore


class Clotho:
    """The Spinner. Creates memory identity. Never decides importance or survival."""

    def __init__(self, store: GraphStore):
        self._store = store

    def spin(
        self,
        node_type: str,
        region: Region,
        origin: str,
        creator: str,
        payload: dict[str, Any] | None = None,
        confidence: float = 0.0,
    ) -> UniversalNode:
        node = UniversalNode(
            node_type=node_type,
            region=region,
            origin=origin,
            creator=creator,
            confidence=confidence,
            payload=payload or {},
        )
        self._store.create_node(node)
        return node


@dataclass
class LachesisWeights:
    """CCMA 'Measurements': the components Lachesis combines into retrieval_weight."""

    relevance: float = 0.0
    consequence: float = 0.0
    frequency: float = 0.0
    authority: float = 0.0
    novelty: float = 0.0
    relationship_density: float = 0.0  # normalized 0..1, fed by store.relationship_count

    def combined(self) -> float:
        # Simple weighted sum. Tune per-region if some factors matter more
        # in e.g. audit vs. companion nodes — this is intentionally the
        # naive baseline, not a claim that these weights are correct.
        parts = [
            self.relevance,
            self.consequence,
            self.frequency,
            self.authority,
            self.novelty,
            self.relationship_density,
        ]
        return sum(parts) / len(parts)


class Lachesis:
    """The Measurer. Answers 'how much should this matter?' — never 'is it true?'."""

    def __init__(self, store: GraphStore):
        self._store = store

    def measure(self, node_id: str, weights: LachesisWeights) -> float:
        """Compute retrieval_weight from components, factoring in graph density."""
        node = self._store.get_node(node_id)
        if node is None:
            raise ValueError(f"No such node: {node_id}")

        density = self._store.relationship_count(node_id)
        # Normalize density with a soft cap so one hub node doesn't blow
        # the scale — same intent as the doc's "2 / 18 / 326 relationships"
        # example, just made numeric instead of illustrative.
        normalized_density = min(density / 50.0, 1.0)
        weights.relationship_density = normalized_density

        retrieval_weight = weights.combined()
        # Temporal value increases with reference frequency; simple recency
        # decay otherwise. Replace with your actual decay curve.
        age_days = (time.time() - node.created_at) / 86400.0
        temporal_weight = retrieval_weight * (0.5 ** (age_days / 30.0))  # 30-day half-life baseline

        is_first_measurement = node.lifecycle_state == LifecycleState.BORN
        if is_first_measurement:
            self._store.mark_active(node_id)
        self._store.reweigh_node(
            node_id,
            retrieval_weight,
            temporal_weight,
            allow_strengthen=not is_first_measurement,
        )
        return retrieval_weight


class Atropos:
    """The Resolver. Answers 'what remains?'. Every resolution is authority-gated for protected types."""

    def __init__(self, store: GraphStore, authority: AuthorityProvider):
        self._store = store
        self._authority = authority

    def archive(self, node_id: str, subject: str) -> None:
        self._store.resolve_node(node_id, LifecycleState.ARCHIVED, self._authority, subject)

    def supersede(self, node_id: str, subject: str) -> None:
        self._store.resolve_node(node_id, LifecycleState.SUPERSEDED, self._authority, subject)

    def retire(self, node_id: str, subject: str) -> None:
        self._store.resolve_node(node_id, LifecycleState.RETIRED, self._authority, subject)

    def forget(self, node_id: str, subject: str) -> None:
        self._store.resolve_node(node_id, LifecycleState.FORGOTTEN, self._authority, subject)
