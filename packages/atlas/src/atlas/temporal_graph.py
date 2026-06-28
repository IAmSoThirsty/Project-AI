"""
atlas.temporal_graph — deterministic time-evolving graph snapshots.

Canonical port of legacy `atlas/core/graph/temporal_graph.py` without legacy
configuration or filesystem side effects. The module produces subordinate
analytical evidence only; it does not make decisions, grant authority, or
actuate recommendations.

Architectural invariants:
- Downward-only deps: atlas.analysis + atlas.audit + stdlib + numpy.
- Fail-closed validation via TemporalGraphError.
- Deterministic snapshot hashes from canonical JSON.
- Merkle-style snapshot chain verification for replay evidence.
- Optional AuditTrail integration for explain/prove/replay continuity.
"""

from __future__ import annotations

import hashlib
import json
import math
import threading
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from itertools import pairwise
from typing import Final

import numpy as np
import numpy.typing as npt

from atlas.analysis import SUBORDINATION_NOTICE
from atlas.audit import AuditCategory, AuditLevel, AuditTrail

TEMPORAL_GRAPH_ALGORITHM: Final[str] = "canonical-temporal-graph-v1"
GENESIS_SNAPSHOT_HASH: Final[str] = "0" * 64
SOURCE_TIERS: Final[frozenset[str]] = frozenset({"TierA", "TierB", "TierC", "TierD"})


class TemporalGraphError(ValueError):
    """Raised when temporal graph operations fail."""


class TemporalNodeType(StrEnum):
    """Canonical temporal graph node categories."""

    STATE_ACTOR = "state_actor"
    CORPORATE_ACTOR = "corporate_actor"
    REGULATOR = "regulator"
    MEDIA_GATEKEEPER = "media_gatekeeper"
    RELIGIOUS_AUTHORITY = "religious_authority"
    PUBLIC_CLUSTER = "public_cluster"


class TemporalEdgeType(StrEnum):
    """Canonical temporal graph edge categories."""

    CAPITAL_FLOW = "capital_flow"
    BOARD_INTERLOCK = "board_interlock"
    REGULATORY_INFLUENCE = "regulatory_influence"
    MEDIA_AMPLIFICATION = "media_amplification"
    FUNDING_RELATIONSHIP = "funding_relationship"


@dataclass(frozen=True)
class TemporalNode:
    """A source-backed temporal graph node."""

    node_id: str
    node_type: TemporalNodeType
    name: str
    source_hash: str
    metadata: tuple[tuple[str, str], ...] = ()
    first_seen: str = "unspecified"
    last_updated: str = "unspecified"
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        _validate_non_empty("node_id", self.node_id)
        if not isinstance(self.node_type, TemporalNodeType):
            raise TemporalGraphError(
                f"node_type must be TemporalNodeType, got {type(self.node_type).__name__}"
            )
        _validate_non_empty("name", self.name)
        _validate_hash("source_hash", self.source_hash)
        _validate_metadata(self.metadata)
        _validate_non_empty("first_seen", self.first_seen)
        _validate_non_empty("last_updated", self.last_updated)

    def to_canonical_dict(self) -> dict[str, object]:
        return {
            "first_seen": self.first_seen,
            "last_updated": self.last_updated,
            "metadata": list(self.metadata),
            "name": self.name,
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "source_hash": self.source_hash,
            "subordination_notice": self.subordination_notice,
        }


@dataclass(frozen=True)
class TemporalEdge:
    """A source-backed directed temporal graph edge."""

    edge_id: str
    source_id: str
    target_id: str
    edge_type: TemporalEdgeType
    weight: float
    confidence_score: float
    decay_rate: float
    source_tier: str
    source_hash: str
    start_timestamp: str = "unspecified"
    end_timestamp: str = "unspecified"
    evidence_ids: tuple[str, ...] = ()
    description: str = ""
    amount: float | None = None
    metadata: tuple[tuple[str, str], ...] = ()
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        _validate_non_empty("edge_id", self.edge_id)
        _validate_non_empty("source_id", self.source_id)
        _validate_non_empty("target_id", self.target_id)
        if self.source_id == self.target_id:
            raise TemporalGraphError(f"self-loop edge is not allowed for {self.source_id!r}")
        if not isinstance(self.edge_type, TemporalEdgeType):
            raise TemporalGraphError(
                f"edge_type must be TemporalEdgeType, got {type(self.edge_type).__name__}"
            )
        _validate_unit_interval("weight", self.weight)
        _validate_unit_interval("confidence_score", self.confidence_score)
        _validate_finite("decay_rate", self.decay_rate)
        if float(self.decay_rate) < 0.0:
            raise TemporalGraphError(f"decay_rate must be >= 0, got {self.decay_rate!r}")
        if self.source_tier not in SOURCE_TIERS:
            raise TemporalGraphError(
                f"source_tier must be one of {sorted(SOURCE_TIERS)}, got {self.source_tier!r}"
            )
        _validate_hash("source_hash", self.source_hash)
        _validate_non_empty("start_timestamp", self.start_timestamp)
        _validate_non_empty("end_timestamp", self.end_timestamp)
        if not isinstance(self.evidence_ids, tuple):
            raise TemporalGraphError(
                f"evidence_ids must be tuple, got {type(self.evidence_ids).__name__}"
            )
        for evidence_id in self.evidence_ids:
            _validate_non_empty("evidence_id", evidence_id)
        if not isinstance(self.description, str):
            raise TemporalGraphError(
                f"description must be string, got {type(self.description).__name__}"
            )
        if self.amount is not None:
            _validate_finite("amount", self.amount)
        _validate_metadata(self.metadata)

    def current_weight(self, at_timestamp: str) -> float:
        """Return exponentially decayed weight at the supplied timestamp."""
        if self.start_timestamp == "unspecified" or float(self.decay_rate) == 0.0:
            return float(self.weight)
        start = _parse_timestamp(self.start_timestamp, "start_timestamp")
        current = _parse_timestamp(at_timestamp, "at_timestamp")
        elapsed_seconds = max(0.0, (current - start).total_seconds())
        elapsed_years = elapsed_seconds / (365.25 * 24.0 * 60.0 * 60.0)
        return float(self.weight) * math.exp(-float(self.decay_rate) * elapsed_years)

    def to_canonical_dict(self) -> dict[str, object]:
        return {
            "amount": self.amount,
            "confidence_score": float(self.confidence_score),
            "decay_rate": float(self.decay_rate),
            "description": self.description,
            "edge_id": self.edge_id,
            "edge_type": self.edge_type.value,
            "end_timestamp": self.end_timestamp,
            "evidence_ids": list(self.evidence_ids),
            "metadata": list(self.metadata),
            "source_hash": self.source_hash,
            "source_id": self.source_id,
            "source_tier": self.source_tier,
            "start_timestamp": self.start_timestamp,
            "subordination_notice": self.subordination_notice,
            "target_id": self.target_id,
            "weight": float(self.weight),
        }


@dataclass(frozen=True)
class TemporalChange:
    """A deterministic node or edge delta between two snapshots."""

    change_type: str
    subject_type: str
    subject_id: str
    before_hash: str
    after_hash: str
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if self.change_type not in {"added", "removed", "changed"}:
            raise TemporalGraphError(
                f"change_type must be added, removed, or changed, got {self.change_type!r}"
            )
        if self.subject_type not in {"node", "edge"}:
            raise TemporalGraphError(
                f"subject_type must be node or edge, got {self.subject_type!r}"
            )
        _validate_non_empty("subject_id", self.subject_id)
        if self.before_hash != "":
            _validate_hash("before_hash", self.before_hash)
        if self.after_hash != "":
            _validate_hash("after_hash", self.after_hash)

    def to_canonical_dict(self) -> dict[str, object]:
        return {
            "after_hash": self.after_hash,
            "before_hash": self.before_hash,
            "change_type": self.change_type,
            "subject_id": self.subject_id,
            "subject_type": self.subject_type,
            "subordination_notice": self.subordination_notice,
        }


@dataclass(frozen=True)
class TemporalEvolution:
    """Changes observed between two adjacent graph snapshots."""

    previous_snapshot_hash: str
    current_snapshot_hash: str
    changes: tuple[TemporalChange, ...]
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        _validate_hash("previous_snapshot_hash", self.previous_snapshot_hash)
        _validate_hash("current_snapshot_hash", self.current_snapshot_hash)
        if not isinstance(self.changes, tuple):
            raise TemporalGraphError(f"changes must be tuple, got {type(self.changes).__name__}")
        for change in self.changes:
            if not isinstance(change, TemporalChange):
                raise TemporalGraphError(
                    f"changes must contain TemporalChange, got {type(change).__name__}"
                )


@dataclass(frozen=True)
class TemporalChainVerification:
    """Result of temporal snapshot chain verification."""

    is_valid: bool
    snapshots_checked: int
    issues: tuple[tuple[int, str], ...]
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not isinstance(self.is_valid, bool):
            raise TemporalGraphError(f"is_valid must be bool, got {type(self.is_valid).__name__}")
        if not isinstance(self.snapshots_checked, int) or self.snapshots_checked < 0:
            raise TemporalGraphError(
                f"snapshots_checked must be non-negative int, got {self.snapshots_checked!r}"
            )
        if not isinstance(self.issues, tuple):
            raise TemporalGraphError(f"issues must be tuple, got {type(self.issues).__name__}")
        for issue in self.issues:
            if not isinstance(issue, tuple) or len(issue) != 2:
                raise TemporalGraphError(f"issues must contain (int, str) tuples, got {issue!r}")


@dataclass(frozen=True)
class GraphSnapshot:
    """A deterministic snapshot of a temporal graph at one timestamp."""

    nodes: tuple[TemporalNode, ...]
    edges: tuple[TemporalEdge, ...]
    timestamp: str
    previous_hash: str
    snapshot_hash: str
    node_count_by_type: Mapping[str, int]
    edge_count_by_type: Mapping[str, int]
    algorithm: str = TEMPORAL_GRAPH_ALGORITHM
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        _validate_non_empty("timestamp", self.timestamp)
        _validate_hash("previous_hash", self.previous_hash)
        _validate_hash("snapshot_hash", self.snapshot_hash)
        if self.algorithm != TEMPORAL_GRAPH_ALGORITHM:
            raise TemporalGraphError(f"algorithm must be {TEMPORAL_GRAPH_ALGORITHM!r}")
        nodes = _canonical_nodes(self.nodes)
        edges = _canonical_edges(self.edges)
        _validate_unique_nodes(nodes)
        _validate_unique_edges(edges)
        _validate_edges_reference_nodes(nodes, edges)
        object.__setattr__(self, "nodes", nodes)
        object.__setattr__(self, "edges", edges)
        object.__setattr__(
            self, "node_count_by_type", _normalize_count_map(self.node_count_by_type)
        )
        object.__setattr__(
            self, "edge_count_by_type", _normalize_count_map(self.edge_count_by_type)
        )

    @classmethod
    def from_components(
        cls,
        nodes: Iterable[TemporalNode],
        edges: Iterable[TemporalEdge],
        timestamp: str,
        previous_hash: str,
    ) -> GraphSnapshot:
        node_tuple = _canonical_nodes(nodes)
        edge_tuple = _canonical_edges(edges)
        node_counts = _node_count_by_type(node_tuple)
        edge_counts = _edge_count_by_type(edge_tuple)
        snapshot_hash = compute_snapshot_hash(
            nodes=node_tuple,
            edges=edge_tuple,
            timestamp=timestamp,
            previous_hash=previous_hash,
        )
        return cls(
            nodes=node_tuple,
            edges=edge_tuple,
            timestamp=timestamp,
            previous_hash=previous_hash,
            snapshot_hash=snapshot_hash,
            node_count_by_type=node_counts,
            edge_count_by_type=edge_counts,
        )

    def item_hash(self, subject_type: str, subject_id: str) -> str:
        if subject_type == "node":
            for node in self.nodes:
                if node.node_id == subject_id:
                    return _hash_canonical(node.to_canonical_dict())
        elif subject_type == "edge":
            for edge in self.edges:
                if edge.edge_id == subject_id:
                    return _hash_canonical(edge.to_canonical_dict())
        else:
            raise TemporalGraphError(f"subject_type must be node or edge, got {subject_type!r}")
        raise TemporalGraphError(f"{subject_type} {subject_id!r} not found in snapshot")

    def to_canonical_dict(self) -> dict[str, object]:
        return {
            **_snapshot_body(
                nodes=self.nodes,
                edges=self.edges,
                timestamp=self.timestamp,
                previous_hash=self.previous_hash,
                node_count_by_type=self.node_count_by_type,
                edge_count_by_type=self.edge_count_by_type,
                algorithm=self.algorithm,
            ),
            "snapshot_hash": self.snapshot_hash,
        }


class TemporalGraph:
    """Build and verify deterministic temporal graph snapshots."""

    def __init__(self, audit_trail: AuditTrail | None = None) -> None:
        if audit_trail is not None and not isinstance(audit_trail, AuditTrail):
            raise TemporalGraphError(
                f"audit_trail must be AuditTrail, got {type(audit_trail).__name__}"
            )
        self._audit_trail = audit_trail
        self._lock = threading.Lock()
        self._nodes: dict[str, TemporalNode] = {}
        self._edges: dict[str, TemporalEdge] = {}
        self._snapshots: tuple[GraphSnapshot, ...] = ()
        self._stats = {
            "nodes_added": 0,
            "edges_added": 0,
            "snapshots_created": 0,
        }
        if self._audit_trail is not None:
            self._audit_trail.append(
                level=AuditLevel.INFORMATIONAL,
                category=AuditCategory.SYSTEM,
                actor="TEMPORAL_GRAPH",
                action="temporal_graph_initialized",
                resource="atlas.temporal_graph",
                outcome="ALLOW",
                rationale="TemporalGraph initialized",
                evidence={"algorithm": TEMPORAL_GRAPH_ALGORITHM},
            )

    def add_node(self, node: TemporalNode) -> None:
        try:
            if not isinstance(node, TemporalNode):
                raise TemporalGraphError(f"node must be TemporalNode, got {type(node).__name__}")
            with self._lock:
                if node.node_id in self._nodes:
                    raise TemporalGraphError(f"duplicate node {node.node_id!r}")
                self._nodes[node.node_id] = node
                self._stats["nodes_added"] += 1
            if self._audit_trail is not None:
                self._audit_trail.append(
                    level=AuditLevel.STANDARD,
                    category=AuditCategory.OPERATION,
                    actor="TEMPORAL_GRAPH",
                    action="temporal_node_added",
                    resource=f"atlas:temporal-node:{node.node_id}",
                    outcome="ALLOW",
                    rationale="Temporal graph node added from source-backed evidence",
                    evidence={
                        "node_id": node.node_id,
                        "node_type": node.node_type.value,
                        "source_hash": node.source_hash,
                    },
                )
        except TemporalGraphError as exc:
            self._audit_failure("temporal_node_add_failed", str(exc))
            raise

    def add_edge(self, edge: TemporalEdge) -> None:
        try:
            if not isinstance(edge, TemporalEdge):
                raise TemporalGraphError(f"edge must be TemporalEdge, got {type(edge).__name__}")
            with self._lock:
                if edge.edge_id in self._edges:
                    raise TemporalGraphError(f"duplicate edge {edge.edge_id!r}")
                if edge.source_id not in self._nodes:
                    raise TemporalGraphError(f"unknown node {edge.source_id!r}")
                if edge.target_id not in self._nodes:
                    raise TemporalGraphError(f"unknown node {edge.target_id!r}")
                self._edges[edge.edge_id] = edge
                self._stats["edges_added"] += 1
            if self._audit_trail is not None:
                self._audit_trail.append(
                    level=AuditLevel.STANDARD,
                    category=AuditCategory.OPERATION,
                    actor="TEMPORAL_GRAPH",
                    action="temporal_edge_added",
                    resource=f"atlas:temporal-edge:{edge.edge_id}",
                    outcome="ALLOW",
                    rationale="Temporal graph edge added from source-backed evidence",
                    evidence={
                        "edge_id": edge.edge_id,
                        "edge_type": edge.edge_type.value,
                        "source_hash": edge.source_hash,
                    },
                )
        except TemporalGraphError as exc:
            self._audit_failure("temporal_edge_add_failed", str(exc))
            raise

    def create_snapshot(self, timestamp: str) -> GraphSnapshot:
        try:
            _validate_non_empty("timestamp", timestamp)
            with self._lock:
                previous_hash = (
                    GENESIS_SNAPSHOT_HASH
                    if not self._snapshots
                    else self._snapshots[-1].snapshot_hash
                )
                snapshot = GraphSnapshot.from_components(
                    nodes=tuple(self._nodes.values()),
                    edges=tuple(self._edges.values()),
                    timestamp=timestamp,
                    previous_hash=previous_hash,
                )
                self._snapshots = (*self._snapshots, snapshot)
                self._stats["snapshots_created"] += 1
            if self._audit_trail is not None:
                self._audit_trail.append(
                    level=AuditLevel.STANDARD,
                    category=AuditCategory.OPERATION,
                    actor="TEMPORAL_GRAPH",
                    action="temporal_snapshot_created",
                    resource=f"atlas:temporal-snapshot:{snapshot.snapshot_hash}",
                    outcome="ALLOW",
                    rationale="Temporal graph snapshot created with deterministic hash linkage",
                    evidence={
                        "edges": str(len(snapshot.edges)),
                        "nodes": str(len(snapshot.nodes)),
                        "previous_hash": snapshot.previous_hash,
                        "snapshot_hash": snapshot.snapshot_hash,
                    },
                )
            return snapshot
        except TemporalGraphError as exc:
            self._audit_failure("temporal_snapshot_create_failed", str(exc))
            raise

    def verify_chain(self) -> TemporalChainVerification:
        with self._lock:
            snapshots = tuple(self._snapshots)
        issues: list[tuple[int, str]] = []
        for index, snapshot in enumerate(snapshots):
            expected_previous = (
                GENESIS_SNAPSHOT_HASH if index == 0 else snapshots[index - 1].snapshot_hash
            )
            if snapshot.previous_hash != expected_previous:
                issues.append((index, "previous_hash mismatch"))
            expected_hash = compute_snapshot_hash(
                nodes=snapshot.nodes,
                edges=snapshot.edges,
                timestamp=snapshot.timestamp,
                previous_hash=snapshot.previous_hash,
            )
            if snapshot.snapshot_hash != expected_hash:
                issues.append((index, "snapshot_hash mismatch"))
        return TemporalChainVerification(
            is_valid=not issues,
            snapshots_checked=len(snapshots),
            issues=tuple(issues),
        )

    def to_adjacency_matrix(self) -> tuple[tuple[str, ...], npt.NDArray[np.float64]]:
        with self._lock:
            nodes = _canonical_nodes(self._nodes.values())
            edges = _canonical_edges(self._edges.values())
        node_ids = tuple(node.node_id for node in nodes)
        index = {node_id: position for position, node_id in enumerate(node_ids)}
        matrix = np.zeros((len(node_ids), len(node_ids)), dtype=np.float64)
        for edge in edges:
            matrix[index[edge.source_id], index[edge.target_id]] = float(edge.weight)
        return node_ids, matrix

    def get_statistics(self) -> dict[str, int]:
        with self._lock:
            return dict(self._stats)

    def reset_statistics(self) -> None:
        with self._lock:
            self._stats = {
                "nodes_added": 0,
                "edges_added": 0,
                "snapshots_created": 0,
            }

    @property
    def snapshots(self) -> tuple[GraphSnapshot, ...]:
        with self._lock:
            return tuple(self._snapshots)

    def _audit_failure(self, action: str, error: str) -> None:
        if self._audit_trail is not None:
            self._audit_trail.append(
                level=AuditLevel.HIGH_PRIORITY,
                category=AuditCategory.OPERATION,
                actor="TEMPORAL_GRAPH",
                action=action,
                resource="atlas:temporal-graph",
                outcome="DENY",
                rationale="Temporal graph operation failed closed",
                evidence={"error": error},
            )


def compute_snapshot_hash(
    *,
    nodes: Iterable[TemporalNode],
    edges: Iterable[TemporalEdge],
    timestamp: str,
    previous_hash: str,
) -> str:
    node_tuple = _canonical_nodes(nodes)
    edge_tuple = _canonical_edges(edges)
    _validate_unique_nodes(node_tuple)
    _validate_unique_edges(edge_tuple)
    _validate_edges_reference_nodes(node_tuple, edge_tuple)
    return _hash_canonical(
        _snapshot_body(
            nodes=node_tuple,
            edges=edge_tuple,
            timestamp=timestamp,
            previous_hash=previous_hash,
            node_count_by_type=_node_count_by_type(node_tuple),
            edge_count_by_type=_edge_count_by_type(edge_tuple),
            algorithm=TEMPORAL_GRAPH_ALGORITHM,
        )
    )


def compute_temporal_changes(
    previous: GraphSnapshot,
    current: GraphSnapshot,
) -> tuple[TemporalChange, ...]:
    if not isinstance(previous, GraphSnapshot):
        raise TemporalGraphError(f"previous must be GraphSnapshot, got {type(previous).__name__}")
    if not isinstance(current, GraphSnapshot):
        raise TemporalGraphError(f"current must be GraphSnapshot, got {type(current).__name__}")
    changes: list[TemporalChange] = []
    changes.extend(
        _diff_items(
            previous_items={node.node_id: node.to_canonical_dict() for node in previous.nodes},
            current_items={node.node_id: node.to_canonical_dict() for node in current.nodes},
            subject_type="node",
        )
    )
    changes.extend(
        _diff_items(
            previous_items={edge.edge_id: edge.to_canonical_dict() for edge in previous.edges},
            current_items={edge.edge_id: edge.to_canonical_dict() for edge in current.edges},
            subject_type="edge",
        )
    )
    return tuple(
        sorted(changes, key=lambda item: (item.subject_type, item.subject_id, item.change_type))
    )


def track_evolution(snapshots: Iterable[GraphSnapshot]) -> tuple[TemporalEvolution, ...]:
    snapshot_tuple = tuple(snapshots)
    for snapshot in snapshot_tuple:
        if not isinstance(snapshot, GraphSnapshot):
            raise TemporalGraphError(
                f"snapshots must contain GraphSnapshot, got {type(snapshot).__name__}"
            )
    evolutions: list[TemporalEvolution] = []
    for previous, current in pairwise(snapshot_tuple):
        evolutions.append(
            TemporalEvolution(
                previous_snapshot_hash=previous.snapshot_hash,
                current_snapshot_hash=current.snapshot_hash,
                changes=compute_temporal_changes(previous, current),
            )
        )
    return tuple(evolutions)


_TEMPORAL_GRAPH: TemporalGraph | None = None
_TEMPORAL_GRAPH_LOCK = threading.Lock()


def get_temporal_graph() -> TemporalGraph:
    """Return the process-local temporal graph singleton."""
    global _TEMPORAL_GRAPH
    with _TEMPORAL_GRAPH_LOCK:
        if _TEMPORAL_GRAPH is None:
            _TEMPORAL_GRAPH = TemporalGraph()
        return _TEMPORAL_GRAPH


def reset_temporal_graph() -> None:
    """Reset the process-local temporal graph singleton."""
    global _TEMPORAL_GRAPH
    with _TEMPORAL_GRAPH_LOCK:
        _TEMPORAL_GRAPH = None


def _snapshot_body(
    *,
    nodes: tuple[TemporalNode, ...],
    edges: tuple[TemporalEdge, ...],
    timestamp: str,
    previous_hash: str,
    node_count_by_type: Mapping[str, int],
    edge_count_by_type: Mapping[str, int],
    algorithm: str,
) -> dict[str, object]:
    _validate_non_empty("timestamp", timestamp)
    _validate_hash("previous_hash", previous_hash)
    return {
        "algorithm": algorithm,
        "edge_count_by_type": dict(sorted(edge_count_by_type.items())),
        "edges": [edge.to_canonical_dict() for edge in edges],
        "node_count_by_type": dict(sorted(node_count_by_type.items())),
        "nodes": [node.to_canonical_dict() for node in nodes],
        "previous_hash": previous_hash,
        "subordination_notice": SUBORDINATION_NOTICE,
        "timestamp": timestamp,
    }


def _diff_items(
    *,
    previous_items: Mapping[str, dict[str, object]],
    current_items: Mapping[str, dict[str, object]],
    subject_type: str,
) -> tuple[TemporalChange, ...]:
    changes: list[TemporalChange] = []
    all_ids = sorted(set(previous_items) | set(current_items))
    for subject_id in all_ids:
        before = previous_items.get(subject_id)
        after = current_items.get(subject_id)
        before_hash = "" if before is None else _hash_canonical(before)
        after_hash = "" if after is None else _hash_canonical(after)
        if before is None and after is not None:
            changes.append(TemporalChange("added", subject_type, subject_id, "", after_hash))
        elif before is not None and after is None:
            changes.append(TemporalChange("removed", subject_type, subject_id, before_hash, ""))
        elif before_hash != after_hash:
            changes.append(
                TemporalChange("changed", subject_type, subject_id, before_hash, after_hash)
            )
    return tuple(changes)


def _canonical_nodes(nodes: Iterable[TemporalNode]) -> tuple[TemporalNode, ...]:
    node_tuple = tuple(nodes)
    for node in node_tuple:
        if not isinstance(node, TemporalNode):
            raise TemporalGraphError(f"nodes must contain TemporalNode, got {type(node).__name__}")
    return tuple(sorted(node_tuple, key=lambda node: node.node_id))


def _canonical_edges(edges: Iterable[TemporalEdge]) -> tuple[TemporalEdge, ...]:
    edge_tuple = tuple(edges)
    for edge in edge_tuple:
        if not isinstance(edge, TemporalEdge):
            raise TemporalGraphError(f"edges must contain TemporalEdge, got {type(edge).__name__}")
    return tuple(sorted(edge_tuple, key=lambda edge: edge.edge_id))


def _validate_unique_nodes(nodes: tuple[TemporalNode, ...]) -> None:
    seen: set[str] = set()
    for node in nodes:
        if node.node_id in seen:
            raise TemporalGraphError(f"duplicate node {node.node_id!r}")
        seen.add(node.node_id)


def _validate_unique_edges(edges: tuple[TemporalEdge, ...]) -> None:
    seen: set[str] = set()
    for edge in edges:
        if edge.edge_id in seen:
            raise TemporalGraphError(f"duplicate edge {edge.edge_id!r}")
        seen.add(edge.edge_id)


def _validate_edges_reference_nodes(
    nodes: tuple[TemporalNode, ...],
    edges: tuple[TemporalEdge, ...],
) -> None:
    node_ids = {node.node_id for node in nodes}
    for edge in edges:
        if edge.source_id not in node_ids:
            raise TemporalGraphError(
                f"edge {edge.edge_id!r} references unknown node {edge.source_id!r}"
            )
        if edge.target_id not in node_ids:
            raise TemporalGraphError(
                f"edge {edge.edge_id!r} references unknown node {edge.target_id!r}"
            )


def _node_count_by_type(nodes: tuple[TemporalNode, ...]) -> dict[str, int]:
    counts = {node_type.value: 0 for node_type in TemporalNodeType}
    for node in nodes:
        counts[node.node_type.value] += 1
    return dict(sorted(counts.items()))


def _edge_count_by_type(edges: tuple[TemporalEdge, ...]) -> dict[str, int]:
    counts = {edge_type.value: 0 for edge_type in TemporalEdgeType}
    for edge in edges:
        counts[edge.edge_type.value] += 1
    return dict(sorted(counts.items()))


def _normalize_count_map(counts: Mapping[str, int]) -> dict[str, int]:
    normalized: dict[str, int] = {}
    for key, value in counts.items():
        if not isinstance(key, str) or not key.strip():
            raise TemporalGraphError(f"count keys must be non-empty strings, got {key!r}")
        if not isinstance(value, int) or value < 0:
            raise TemporalGraphError(f"count values must be non-negative ints, got {value!r}")
        normalized[key] = value
    return dict(sorted(normalized.items()))


def _validate_metadata(metadata: tuple[tuple[str, str], ...]) -> None:
    if not isinstance(metadata, tuple):
        raise TemporalGraphError(f"metadata must be tuple, got {type(metadata).__name__}")
    for item in metadata:
        if not isinstance(item, tuple) or len(item) != 2:
            raise TemporalGraphError(f"metadata must contain (str, str) tuples, got {item!r}")
        if not isinstance(item[0], str) or not isinstance(item[1], str):
            raise TemporalGraphError(f"metadata must contain (str, str), got {item!r}")


def _validate_non_empty(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise TemporalGraphError(f"{name} must be non-empty string, got {value!r}")


def _validate_unit_interval(name: str, value: float) -> None:
    _validate_finite(name, value)
    numeric = float(value)
    if numeric < 0.0 or numeric > 1.0:
        raise TemporalGraphError(f"{name} must be in [0, 1], got {value!r}")


def _validate_finite(name: str, value: float) -> None:
    if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise TemporalGraphError(f"{name} must be finite number, got {value!r}")


def _validate_hash(name: str, value: str) -> None:
    if not isinstance(value, str) or len(value) != 64:
        raise TemporalGraphError(f"{name} must be 64-char lowercase hex string, got {value!r}")
    for char in value:
        if char not in "0123456789abcdef":
            raise TemporalGraphError(f"{name} must be lowercase hex, got {value!r}")


def _parse_timestamp(value: str, name: str) -> datetime:
    _validate_non_empty(name, value)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TemporalGraphError(f"{name} must be ISO 8601, got {value!r}: {exc}") from exc


def _hash_canonical(body: dict[str, object]) -> str:
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
