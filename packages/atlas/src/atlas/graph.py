"""
atlas.graph — deterministic influence graph construction.

Faithful canonical port of legacy `atlas/core/graph/builder.py` without the
legacy ConfigLoader/SchemaValidator dependencies. The module builds subordinate
analytical evidence only; it does not make decisions, grant authority, or
actuate recommendations.

Architectural invariants:
- Downward-only deps: atlas.analysis + atlas.audit + stdlib.
- Fail-closed validation via GraphError.
- Deterministic graph hashes from canonical JSON.
- Optional AuditTrail integration for explain/prove/replay continuity.
"""

from __future__ import annotations

import hashlib
import json
import math
import threading
from collections import defaultdict, deque
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Final

from atlas.analysis import SUBORDINATION_NOTICE
from atlas.audit import AuditCategory, AuditLevel, AuditTrail

GRAPH_ALGORITHM: Final[str] = "canonical-influence-graph-v1"


class GraphError(ValueError):
    """Raised when graph construction or metric calculation fails."""


@dataclass(frozen=True)
class GraphNode:
    """A graph node representing an organization, claim, event, or related entity."""

    node_id: str
    node_type: str
    influence: float
    attributes: tuple[tuple[str, str], ...] = ()
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not isinstance(self.node_id, str) or not self.node_id.strip():
            raise GraphError(f"node_id must be non-empty string, got {self.node_id!r}")
        if not isinstance(self.node_type, str) or not self.node_type.strip():
            raise GraphError(f"node_type must be non-empty string, got {self.node_type!r}")
        _validate_unit_interval("influence", self.influence)
        if not isinstance(self.attributes, tuple):
            raise GraphError(f"attributes must be tuple, got {type(self.attributes).__name__}")
        for item in self.attributes:
            if not isinstance(item, tuple) or len(item) != 2:
                raise GraphError(f"attributes must contain (str, str) tuples, got {item!r}")
            if not isinstance(item[0], str) or not isinstance(item[1], str):
                raise GraphError(f"attributes must contain (str, str), got {item!r}")

    def to_canonical_dict(self) -> dict[str, object]:
        return {
            "attributes": list(self.attributes),
            "influence": self.influence,
            "node_id": self.node_id,
            "node_type": self.node_type,
            "subordination_notice": self.subordination_notice,
        }


@dataclass(frozen=True)
class GraphEdge:
    """A directed weighted edge between graph nodes."""

    source: str
    target: str
    weight: float
    relation: str
    properties: tuple[tuple[str, str], ...] = ()
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not isinstance(self.source, str) or not self.source.strip():
            raise GraphError(f"source must be non-empty string, got {self.source!r}")
        if not isinstance(self.target, str) or not self.target.strip():
            raise GraphError(f"target must be non-empty string, got {self.target!r}")
        if self.source == self.target:
            raise GraphError(f"self-loop edge is not allowed for {self.source!r}")
        _validate_unit_interval("weight", self.weight)
        if not isinstance(self.relation, str) or not self.relation.strip():
            raise GraphError(f"relation must be non-empty string, got {self.relation!r}")
        if not isinstance(self.properties, tuple):
            raise GraphError(f"properties must be tuple, got {type(self.properties).__name__}")
        for item in self.properties:
            if not isinstance(item, tuple) or len(item) != 2:
                raise GraphError(f"properties must contain (str, str) tuples, got {item!r}")
            if not isinstance(item[0], str) or not isinstance(item[1], str):
                raise GraphError(f"properties must contain (str, str), got {item!r}")

    def to_canonical_dict(self) -> dict[str, object]:
        return {
            "properties": list(self.properties),
            "relation": self.relation,
            "source": self.source,
            "subordination_notice": self.subordination_notice,
            "target": self.target,
            "weight": self.weight,
        }


@dataclass(frozen=True)
class GraphMetrics:
    """Network metrics for an InfluenceGraph."""

    centrality: dict[str, dict[str, float]]
    pagerank: dict[str, float]
    clustering: dict[str, float]
    density: float
    average_degree: float
    total_nodes: int
    total_edges: int
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not isinstance(self.centrality, dict):
            raise GraphError(f"centrality must be dict, got {type(self.centrality).__name__}")
        if not isinstance(self.pagerank, dict):
            raise GraphError(f"pagerank must be dict, got {type(self.pagerank).__name__}")
        if not isinstance(self.clustering, dict):
            raise GraphError(f"clustering must be dict, got {type(self.clustering).__name__}")
        _validate_unit_interval("density", self.density)
        if not isinstance(self.average_degree, (int, float)) or not math.isfinite(
            self.average_degree
        ):
            raise GraphError(f"average_degree must be finite number, got {self.average_degree!r}")
        if not isinstance(self.total_nodes, int) or self.total_nodes < 0:
            raise GraphError(f"total_nodes must be non-negative int, got {self.total_nodes!r}")
        if not isinstance(self.total_edges, int) or self.total_edges < 0:
            raise GraphError(f"total_edges must be non-negative int, got {self.total_edges!r}")

    def to_canonical_dict(self) -> dict[str, object]:
        return {
            "average_degree": self.average_degree,
            "centrality": _sort_nested_float_dict(self.centrality),
            "clustering": dict(sorted(self.clustering.items())),
            "density": self.density,
            "pagerank": dict(sorted(self.pagerank.items())),
            "subordination_notice": self.subordination_notice,
            "total_edges": self.total_edges,
            "total_nodes": self.total_nodes,
        }


@dataclass(frozen=True)
class Community:
    """A connected graph community."""

    community_id: str
    members: tuple[str, ...]
    cohesion: float
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not isinstance(self.community_id, str) or not self.community_id.strip():
            raise GraphError(f"community_id must be non-empty string, got {self.community_id!r}")
        if not isinstance(self.members, tuple) or not self.members:
            raise GraphError("members must be a non-empty tuple")
        for member in self.members:
            if not isinstance(member, str) or not member.strip():
                raise GraphError(f"members must be non-empty strings, got {member!r}")
        if tuple(sorted(self.members)) != self.members:
            raise GraphError("members must be sorted for deterministic community output")
        _validate_unit_interval("cohesion", self.cohesion)

    def to_canonical_dict(self) -> dict[str, object]:
        return {
            "cohesion": self.cohesion,
            "community_id": self.community_id,
            "members": list(self.members),
            "subordination_notice": self.subordination_notice,
        }


@dataclass(frozen=True)
class InfluenceGraph:
    """A deterministic subordinate influence graph."""

    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]
    metrics: GraphMetrics
    communities: tuple[Community, ...]
    graph_sha256: str
    algorithm: str = GRAPH_ALGORITHM
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not self.nodes:
            raise GraphError("InfluenceGraph requires at least one node")
        _validate_unique_nodes(self.nodes)
        _validate_edges_reference_nodes(self.nodes, self.edges)
        if not isinstance(self.metrics, GraphMetrics):
            raise GraphError(f"metrics must be GraphMetrics, got {type(self.metrics).__name__}")
        if not isinstance(self.communities, tuple):
            raise GraphError(f"communities must be tuple, got {type(self.communities).__name__}")
        for community in self.communities:
            if not isinstance(community, Community):
                raise GraphError(
                    f"communities must contain Community, got {type(community).__name__}"
                )
        if not isinstance(self.graph_sha256, str) or len(self.graph_sha256) != 64:
            raise GraphError(f"graph_sha256 must be 64-char hex string, got {self.graph_sha256!r}")
        for char in self.graph_sha256:
            if char not in "0123456789abcdef":
                raise GraphError(f"graph_sha256 must be lowercase hex, got {self.graph_sha256!r}")

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    def to_canonical_dict(self) -> dict[str, object]:
        return {
            **_graph_body(
                nodes=self.nodes,
                edges=self.edges,
                metrics=self.metrics,
                communities=self.communities,
                algorithm=self.algorithm,
            ),
            "graph_sha256": self.graph_sha256,
        }


class GraphBuilder:
    """Build deterministic influence graphs from entities, relationships, and opinions."""

    def __init__(self, audit_trail: AuditTrail | None = None) -> None:
        if audit_trail is not None and not isinstance(audit_trail, AuditTrail):
            raise GraphError(f"audit_trail must be AuditTrail, got {type(audit_trail).__name__}")
        self._audit_trail = audit_trail
        self._lock = threading.Lock()
        self._stats = {
            "graphs_built": 0,
            "nodes_added": 0,
            "edges_added": 0,
            "metrics_calculated": 0,
            "communities_detected": 0,
        }
        if self._audit_trail is not None:
            self._audit_trail.append(
                level=AuditLevel.INFORMATIONAL,
                category=AuditCategory.SYSTEM,
                actor="GRAPH_BUILDER",
                action="graph_builder_initialized",
                resource="atlas.graph.builder",
                outcome="ALLOW",
                rationale="GraphBuilder initialized",
                evidence={"algorithm": GRAPH_ALGORITHM},
            )

    def build_graph(
        self,
        entities: Iterable[GraphNode | Mapping[str, object]],
        relationships: Iterable[GraphEdge | Mapping[str, object]],
        opinions: Iterable[Mapping[str, object]] | None = None,
    ) -> InfluenceGraph:
        try:
            nodes = _normalize_nodes(tuple(entities))
            if not nodes:
                raise GraphError("graph requires at least one node")
            edges = _normalize_edges(tuple(relationships), opinions=tuple(opinions or ()))
            _validate_unique_nodes(nodes)
            _validate_edges_reference_nodes(nodes, edges)
            metrics = GraphMetrics(
                centrality=compute_centrality(nodes, edges),
                pagerank=compute_pagerank(nodes, edges),
                clustering=compute_clustering(nodes, edges),
                density=_compute_density(nodes, edges),
                average_degree=_compute_average_degree(nodes, edges),
                total_nodes=len(nodes),
                total_edges=len(edges),
            )
            communities = detect_communities(nodes, edges)
            graph_hash = compute_graph_hash(
                nodes=nodes,
                edges=edges,
                metrics=metrics,
                communities=communities,
            )
            graph = InfluenceGraph(
                nodes=nodes,
                edges=edges,
                metrics=metrics,
                communities=communities,
                graph_sha256=graph_hash,
            )
            with self._lock:
                self._stats["graphs_built"] += 1
                self._stats["nodes_added"] += len(nodes)
                self._stats["edges_added"] += len(edges)
                self._stats["metrics_calculated"] += 1
                self._stats["communities_detected"] += 1
            if self._audit_trail is not None:
                self._audit_trail.append(
                    level=AuditLevel.STANDARD,
                    category=AuditCategory.OPERATION,
                    actor="GRAPH_BUILDER",
                    action="influence_graph_built",
                    resource=f"atlas:graph:{graph.graph_sha256}",
                    outcome="ALLOW",
                    rationale="Influence graph built from subordinate analytical evidence",
                    evidence={
                        "algorithm": graph.algorithm,
                        "communities": str(len(graph.communities)),
                        "edges": str(graph.edge_count),
                        "graph_sha256": graph.graph_sha256,
                        "nodes": str(graph.node_count),
                    },
                )
            return graph
        except GraphError as exc:
            if self._audit_trail is not None:
                self._audit_trail.append(
                    level=AuditLevel.HIGH_PRIORITY,
                    category=AuditCategory.OPERATION,
                    actor="GRAPH_BUILDER",
                    action="influence_graph_build_failed",
                    resource="atlas:graph",
                    outcome="DENY",
                    rationale="Influence graph construction failed closed",
                    evidence={"error": str(exc)},
                )
            raise

    def get_statistics(self) -> dict[str, int]:
        with self._lock:
            return dict(self._stats)

    def reset_statistics(self) -> None:
        with self._lock:
            self._stats = {
                "graphs_built": 0,
                "nodes_added": 0,
                "edges_added": 0,
                "metrics_calculated": 0,
                "communities_detected": 0,
            }


def compute_centrality(
    nodes: Iterable[GraphNode],
    edges: Iterable[GraphEdge],
) -> dict[str, dict[str, float]]:
    node_tuple, edge_tuple = _canonical_inputs(nodes, edges)
    node_ids = {node.node_id for node in node_tuple}
    _validate_edges_reference_nodes(node_tuple, edge_tuple)
    out_edges, in_edges = _adjacency(node_tuple, edge_tuple)
    denominator = max(1, len(node_ids) - 1)
    centrality: dict[str, dict[str, float]] = {}
    for node_id in sorted(node_ids):
        in_degree = float(len(in_edges[node_id]))
        out_degree = float(len(out_edges[node_id]))
        total_degree = in_degree + out_degree
        centrality[node_id] = {
            "in_degree": in_degree,
            "normalized_centrality": total_degree / denominator if len(node_ids) > 1 else 0.0,
            "out_degree": out_degree,
            "total_degree": total_degree,
        }
    return centrality


def compute_pagerank(
    nodes: Iterable[GraphNode],
    edges: Iterable[GraphEdge],
    *,
    damping: float = 0.85,
    max_iterations: int = 100,
    tolerance: float = 1e-9,
) -> dict[str, float]:
    if not isinstance(damping, (int, float)) or not math.isfinite(float(damping)):
        raise GraphError(f"damping must be finite number, got {damping!r}")
    if not 0.0 < float(damping) < 1.0:
        raise GraphError(f"damping must be in (0, 1), got {damping!r}")
    if not isinstance(max_iterations, int) or max_iterations < 1:
        raise GraphError(f"max_iterations must be positive int, got {max_iterations!r}")
    if not isinstance(tolerance, (int, float)) or not math.isfinite(float(tolerance)):
        raise GraphError(f"tolerance must be finite number, got {tolerance!r}")
    if tolerance <= 0.0:
        raise GraphError(f"tolerance must be > 0, got {tolerance!r}")

    node_tuple, edge_tuple = _canonical_inputs(nodes, edges)
    _validate_edges_reference_nodes(node_tuple, edge_tuple)
    node_ids = tuple(node.node_id for node in node_tuple)
    n = len(node_ids)
    if n == 0:
        return {}
    out_edges, in_edges = _adjacency(node_tuple, edge_tuple)
    ranks = {node_id: 1.0 / n for node_id in node_ids}
    damping_f = float(damping)
    for _ in range(max_iterations):
        next_ranks: dict[str, float] = {}
        dangling_rank = sum(ranks[node_id] for node_id in node_ids if not out_edges[node_id])
        for node_id in node_ids:
            incoming = 0.0
            for source_id, weight in in_edges[node_id]:
                outgoing = out_edges[source_id]
                outgoing_weight = sum(item_weight for _, item_weight in outgoing)
                if outgoing_weight > 0.0:
                    incoming += ranks[source_id] * (weight / outgoing_weight)
            next_ranks[node_id] = ((1.0 - damping_f) / n) + damping_f * (
                incoming + dangling_rank / n
            )
        delta = sum(abs(next_ranks[node_id] - ranks[node_id]) for node_id in node_ids)
        ranks = next_ranks
        if delta <= tolerance:
            break
    total = sum(ranks.values())
    if total <= 0.0:
        return {node_id: 1.0 / n for node_id in node_ids}
    return {node_id: ranks[node_id] / total for node_id in node_ids}


def compute_clustering(
    nodes: Iterable[GraphNode],
    edges: Iterable[GraphEdge],
) -> dict[str, float]:
    node_tuple, edge_tuple = _canonical_inputs(nodes, edges)
    _validate_edges_reference_nodes(node_tuple, edge_tuple)
    out_edges, in_edges = _adjacency(node_tuple, edge_tuple)
    edge_pairs = {(edge.source, edge.target) for edge in edge_tuple}
    clustering: dict[str, float] = {}
    for node in node_tuple:
        neighbors = {target for target, _ in out_edges[node.node_id]} | {
            source for source, _ in in_edges[node.node_id]
        }
        if len(neighbors) < 2:
            clustering[node.node_id] = 0.0
            continue
        links = 0
        for source in neighbors:
            for target in neighbors:
                if source != target and (source, target) in edge_pairs:
                    links += 1
        max_links = len(neighbors) * (len(neighbors) - 1)
        clustering[node.node_id] = links / max_links
    return dict(sorted(clustering.items()))


def detect_communities(
    nodes: Iterable[GraphNode],
    edges: Iterable[GraphEdge],
) -> tuple[Community, ...]:
    node_tuple, edge_tuple = _canonical_inputs(nodes, edges)
    _validate_edges_reference_nodes(node_tuple, edge_tuple)
    adjacency: dict[str, set[str]] = {node.node_id: set() for node in node_tuple}
    for edge in edge_tuple:
        adjacency[edge.source].add(edge.target)
        adjacency[edge.target].add(edge.source)

    visited: set[str] = set()
    communities: list[Community] = []
    for node_id in sorted(adjacency):
        if node_id in visited:
            continue
        queue: deque[str] = deque([node_id])
        visited.add(node_id)
        members: list[str] = []
        while queue:
            current = queue.popleft()
            members.append(current)
            for neighbor in sorted(adjacency[current]):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        sorted_members = tuple(sorted(members))
        communities.append(
            Community(
                community_id=f"COMM-{len(communities) + 1}",
                members=sorted_members,
                cohesion=_compute_community_cohesion(sorted_members, edge_tuple),
            )
        )
    return tuple(communities)


def compute_graph_hash(
    *,
    nodes: tuple[GraphNode, ...],
    edges: tuple[GraphEdge, ...],
    metrics: GraphMetrics,
    communities: tuple[Community, ...],
    algorithm: str = GRAPH_ALGORITHM,
) -> str:
    body = _graph_body(
        nodes=nodes,
        edges=edges,
        metrics=metrics,
        communities=communities,
        algorithm=algorithm,
    )
    return hashlib.sha256(_canonical_json(body).encode("utf-8")).hexdigest()


_global_builder: GraphBuilder | None = None
_global_builder_lock = threading.Lock()


def get_graph_builder(audit_trail: AuditTrail | None = None) -> GraphBuilder:
    global _global_builder
    with _global_builder_lock:
        if _global_builder is None or audit_trail is not None:
            _global_builder = GraphBuilder(audit_trail=audit_trail)
        return _global_builder


def reset_graph_builder() -> None:
    global _global_builder
    with _global_builder_lock:
        _global_builder = None


def _canonical_inputs(
    nodes: Iterable[GraphNode],
    edges: Iterable[GraphEdge],
) -> tuple[tuple[GraphNode, ...], tuple[GraphEdge, ...]]:
    node_tuple = tuple(sorted(tuple(nodes), key=lambda item: item.node_id))
    edge_tuple = tuple(
        sorted(tuple(edges), key=lambda item: (item.source, item.target, item.relation))
    )
    return node_tuple, edge_tuple


def _validate_unit_interval(name: str, value: float) -> None:
    if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise GraphError(f"{name} must be finite number, got {value!r}")
    if not 0.0 <= float(value) <= 1.0:
        raise GraphError(f"{name} must be in [0, 1], got {value!r}")


def _validate_unique_nodes(nodes: tuple[GraphNode, ...]) -> None:
    seen: set[str] = set()
    for node in nodes:
        if node.node_id in seen:
            raise GraphError(f"duplicate node_id {node.node_id!r}")
        seen.add(node.node_id)


def _validate_edges_reference_nodes(
    nodes: tuple[GraphNode, ...],
    edges: tuple[GraphEdge, ...],
) -> None:
    node_ids = {node.node_id for node in nodes}
    for edge in edges:
        if edge.source not in node_ids or edge.target not in node_ids:
            missing = edge.source if edge.source not in node_ids else edge.target
            raise GraphError(f"edge references unknown node {missing!r}")


def _normalize_nodes(items: tuple[GraphNode | Mapping[str, object], ...]) -> tuple[GraphNode, ...]:
    nodes: list[GraphNode] = []
    for item in items:
        if isinstance(item, GraphNode):
            nodes.append(item)
        elif isinstance(item, Mapping):
            nodes.append(_node_from_mapping(item))
        else:
            raise GraphError(f"entity must be GraphNode or mapping, got {type(item).__name__}")
    return tuple(sorted(nodes, key=lambda node: node.node_id))


def _normalize_edges(
    items: tuple[GraphEdge | Mapping[str, object], ...],
    *,
    opinions: tuple[Mapping[str, object], ...],
) -> tuple[GraphEdge, ...]:
    edge_map: dict[tuple[str, str], tuple[float, str, dict[str, str]]] = {}
    for item in items:
        edge = item if isinstance(item, GraphEdge) else _edge_from_mapping(item)
        key = (edge.source, edge.target)
        existing = edge_map.get(key)
        if existing is None:
            edge_map[key] = (edge.weight, edge.relation, dict(edge.properties))
        else:
            weight, relation, properties = existing
            edge_map[key] = (
                min(1.0, weight + edge.weight),
                _merge_relation(relation, edge.relation),
                {**properties, **dict(edge.properties)},
            )
    for opinion in opinions:
        edge = _edge_from_opinion(opinion)
        key = (edge.source, edge.target)
        existing = edge_map.get(key)
        if existing is None:
            edge_map[key] = (edge.weight, edge.relation, dict(edge.properties))
        else:
            weight, relation, properties = existing
            edge_map[key] = (
                min(1.0, weight + edge.weight),
                _merge_relation(relation, edge.relation),
                {**properties, **dict(edge.properties)},
            )
    return tuple(
        GraphEdge(
            source=source,
            target=target,
            weight=weight,
            relation=relation,
            properties=tuple(sorted(properties.items())),
        )
        for (source, target), (weight, relation, properties) in sorted(edge_map.items())
    )


def _node_from_mapping(item: Mapping[str, object]) -> GraphNode:
    node_id = _required_str(item, "id")
    node_type = _optional_str(item, "type", "unknown")
    influence = _optional_float(item, "influence", 0.5)
    attributes = item.get("attributes", {})
    attribute_pairs: tuple[tuple[str, str], ...] = ()
    if isinstance(attributes, Mapping):
        attribute_pairs = tuple(sorted((str(key), str(value)) for key, value in attributes.items()))
    elif attributes not in ({}, None):
        raise GraphError(f"attributes must be mapping, got {type(attributes).__name__}")
    return GraphNode(
        node_id=node_id,
        node_type=node_type,
        influence=influence,
        attributes=attribute_pairs,
    )


def _edge_from_mapping(item: Mapping[str, object]) -> GraphEdge:
    source = _required_str(item, "source_id", fallback="source")
    target = _required_str(item, "target_id", fallback="target")
    relation = _optional_str(item, "type", _optional_str(item, "relation", "relationship"))
    weight = _optional_float(item, "strength", _optional_float(item, "weight", 0.5))
    return GraphEdge(source=source, target=target, weight=weight, relation=relation)


def _edge_from_opinion(item: Mapping[str, object]) -> GraphEdge:
    source = _required_str(item, "holder_id")
    target = _required_str(item, "target_id")
    sentiment = _optional_float(item, "sentiment", 0.0)
    confidence = _optional_float(item, "confidence", 0.5)
    if not -1.0 <= sentiment <= 1.0:
        raise GraphError(f"sentiment must be in [-1, 1], got {sentiment!r}")
    _validate_unit_interval("confidence", confidence)
    weight = ((sentiment + 1.0) / 2.0) * confidence
    return GraphEdge(
        source=source,
        target=target,
        weight=weight,
        relation="opinion",
        properties=(("confidence", str(confidence)), ("sentiment", str(sentiment))),
    )


def _required_str(item: Mapping[str, object], key: str, *, fallback: str | None = None) -> str:
    value = item.get(key)
    if value is None and fallback is not None:
        value = item.get(fallback)
    if not isinstance(value, str) or not value.strip():
        raise GraphError(f"{key} must be non-empty string")
    return value


def _optional_str(item: Mapping[str, object], key: str, default: str) -> str:
    value = item.get(key, default)
    if not isinstance(value, str) or not value.strip():
        raise GraphError(f"{key} must be non-empty string")
    return value


def _optional_float(item: Mapping[str, object], key: str, default: float) -> float:
    value = item.get(key, default)
    if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise GraphError(f"{key} must be finite number, got {value!r}")
    return float(value)


def _merge_relation(first: str, second: str) -> str:
    parts = []
    for relation in (first, second):
        for part in relation.split("+"):
            if part not in parts:
                parts.append(part)
    return "+".join(parts)


def _adjacency(
    nodes: tuple[GraphNode, ...],
    edges: tuple[GraphEdge, ...],
) -> tuple[dict[str, list[tuple[str, float]]], dict[str, list[tuple[str, float]]]]:
    out_edges: dict[str, list[tuple[str, float]]] = defaultdict(list)
    in_edges: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for node in nodes:
        out_edges[node.node_id]
        in_edges[node.node_id]
    for edge in edges:
        out_edges[edge.source].append((edge.target, edge.weight))
        in_edges[edge.target].append((edge.source, edge.weight))
    for value in out_edges.values():
        value.sort()
    for value in in_edges.values():
        value.sort()
    return out_edges, in_edges


def _compute_density(nodes: tuple[GraphNode, ...], edges: tuple[GraphEdge, ...]) -> float:
    max_edges = len(nodes) * (len(nodes) - 1)
    return len(edges) / max_edges if max_edges > 0 else 0.0


def _compute_average_degree(nodes: tuple[GraphNode, ...], edges: tuple[GraphEdge, ...]) -> float:
    return (2.0 * len(edges) / len(nodes)) if nodes else 0.0


def _compute_community_cohesion(
    members: tuple[str, ...],
    edges: tuple[GraphEdge, ...],
) -> float:
    if len(members) < 2:
        return 0.0
    member_set = set(members)
    internal_edges = [
        edge for edge in edges if edge.source in member_set and edge.target in member_set
    ]
    max_internal_edges = len(members) * (len(members) - 1)
    if max_internal_edges == 0:
        return 0.0
    density = len(internal_edges) / max_internal_edges
    average_weight = (
        sum(edge.weight for edge in internal_edges) / len(internal_edges) if internal_edges else 0.0
    )
    return density * average_weight


def _graph_body(
    *,
    nodes: tuple[GraphNode, ...],
    edges: tuple[GraphEdge, ...],
    metrics: GraphMetrics,
    communities: tuple[Community, ...],
    algorithm: str,
) -> dict[str, object]:
    return {
        "algorithm": algorithm,
        "communities": [community.to_canonical_dict() for community in communities],
        "edges": [edge.to_canonical_dict() for edge in edges],
        "metrics": metrics.to_canonical_dict(),
        "nodes": [node.to_canonical_dict() for node in nodes],
        "subordination_notice": SUBORDINATION_NOTICE,
    }


def _canonical_json(body: dict[str, object]) -> str:
    return json.dumps(body, sort_keys=True, separators=(",", ":"))


def _sort_nested_float_dict(values: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    return {outer: dict(sorted(inner.items())) for outer, inner in sorted(values.items())}


__all__ = [
    "GRAPH_ALGORITHM",
    "Community",
    "GraphBuilder",
    "GraphEdge",
    "GraphError",
    "GraphMetrics",
    "GraphNode",
    "InfluenceGraph",
    "compute_centrality",
    "compute_clustering",
    "compute_graph_hash",
    "compute_pagerank",
    "detect_communities",
    "get_graph_builder",
    "reset_graph_builder",
]
