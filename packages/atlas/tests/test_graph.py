"""Unit tests for atlas.graph (Phase J2.4.0a).

These tests lock the graph-builder port before implementation:
- fail-closed dataclass validation
- deterministic graph hashes
- centrality, PageRank, clustering, density, and communities
- audit event emission
- factory reset behavior
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from threading import Thread

import pytest

from atlas import (
    SUBORDINATION_NOTICE,
    AuditCategory,
    AuditLevel,
    AuditTrail,
    Community,
    GraphBuilder,
    GraphEdge,
    GraphError,
    GraphMetrics,
    GraphNode,
    InfluenceGraph,
    compute_centrality,
    compute_clustering,
    compute_pagerank,
    detect_communities,
    get_graph_builder,
    reset_graph_builder,
)


def _nodes() -> tuple[GraphNode, ...]:
    return (
        GraphNode(node_id="alpha", node_type="organization", influence=0.9),
        GraphNode(node_id="beta", node_type="organization", influence=0.7),
        GraphNode(node_id="gamma", node_type="claim", influence=0.4),
    )


def _edges() -> tuple[GraphEdge, ...]:
    return (
        GraphEdge(source="alpha", target="beta", weight=0.8, relation="supports"),
        GraphEdge(source="beta", target="gamma", weight=0.6, relation="influences"),
        GraphEdge(source="alpha", target="gamma", weight=0.5, relation="validates"),
    )


def _entities() -> tuple[dict[str, object], ...]:
    return (
        {"id": "alpha", "type": "organization", "influence": 0.9},
        {"id": "beta", "type": "organization", "influence": 0.7},
        {"id": "gamma", "type": "claim", "influence": 0.4},
    )


def _relationships() -> tuple[dict[str, object], ...]:
    return (
        {"source_id": "alpha", "target_id": "beta", "type": "supports", "strength": 0.8},
        {"source_id": "beta", "target_id": "gamma", "type": "influences", "strength": 0.6},
        {"source_id": "alpha", "target_id": "gamma", "type": "validates", "strength": 0.5},
    )


def test_graph_node_validation() -> None:
    node = GraphNode(node_id="n1", node_type="organization", influence=1.0)
    assert node.subordination_notice == SUBORDINATION_NOTICE
    with pytest.raises(GraphError, match="node_id"):
        GraphNode(node_id="", node_type="organization", influence=0.5)
    with pytest.raises(GraphError, match="influence"):
        GraphNode(node_id="n1", node_type="organization", influence=1.1)
    with pytest.raises(FrozenInstanceError):
        node.influence = 0.1  # type: ignore[misc]


def test_graph_edge_validation() -> None:
    edge = GraphEdge(source="a", target="b", weight=0.5, relation="supports")
    assert edge.subordination_notice == SUBORDINATION_NOTICE
    with pytest.raises(GraphError, match="self-loop"):
        GraphEdge(source="a", target="a", weight=0.5, relation="supports")
    with pytest.raises(GraphError, match="weight"):
        GraphEdge(source="a", target="b", weight=-0.1, relation="supports")
    with pytest.raises(GraphError, match="relation"):
        GraphEdge(source="a", target="b", weight=0.5, relation="")


def test_compute_centrality() -> None:
    centrality = compute_centrality(_nodes(), _edges())
    assert centrality["alpha"]["in_degree"] == 0.0
    assert centrality["alpha"]["out_degree"] == 2.0
    assert centrality["alpha"]["total_degree"] == 2.0
    assert centrality["alpha"]["normalized_centrality"] == 1.0
    assert centrality["gamma"]["in_degree"] == 2.0


def test_compute_centrality_rejects_unknown_edge_node() -> None:
    with pytest.raises(GraphError, match="unknown node"):
        compute_centrality(_nodes(), (GraphEdge("alpha", "missing", 0.5, "supports"),))


def test_compute_pagerank_is_normalized_and_deterministic() -> None:
    first = compute_pagerank(_nodes(), _edges(), max_iterations=200)
    second = compute_pagerank(_nodes(), _edges(), max_iterations=200)
    assert first == second
    assert set(first) == {"alpha", "beta", "gamma"}
    assert sum(first.values()) == pytest.approx(1.0)
    assert first["gamma"] > first["alpha"]


def test_compute_pagerank_validates_parameters() -> None:
    with pytest.raises(GraphError, match="damping"):
        compute_pagerank(_nodes(), _edges(), damping=1.5)
    with pytest.raises(GraphError, match="max_iterations"):
        compute_pagerank(_nodes(), _edges(), max_iterations=0)


def test_compute_clustering_detects_closed_neighborhood() -> None:
    clustering = compute_clustering(_nodes(), _edges())
    assert clustering["alpha"] == pytest.approx(0.5)
    assert clustering["beta"] == pytest.approx(0.5)
    assert clustering["gamma"] == pytest.approx(0.5)


def test_detect_communities_groups_connected_components() -> None:
    nodes = (*_nodes(), GraphNode(node_id="delta", node_type="event", influence=0.2))
    communities = detect_communities(nodes, _edges())
    assert tuple(community.members for community in communities) == (
        ("alpha", "beta", "gamma"),
        ("delta",),
    )
    assert communities[0].cohesion > communities[1].cohesion


def test_graph_builder_builds_from_dataclasses() -> None:
    graph = GraphBuilder().build_graph(_nodes(), _edges())
    assert isinstance(graph, InfluenceGraph)
    assert isinstance(graph.metrics, GraphMetrics)
    assert graph.node_count == 3
    assert graph.edge_count == 3
    assert graph.metrics.density == pytest.approx(0.5)
    assert graph.metrics.average_degree == pytest.approx(2.0)
    assert len(graph.graph_sha256) == 64
    assert graph.subordination_notice == SUBORDINATION_NOTICE


def test_graph_builder_builds_from_legacy_mappings() -> None:
    graph = GraphBuilder().build_graph(_entities(), _relationships())
    assert [node.node_id for node in graph.nodes] == ["alpha", "beta", "gamma"]
    assert {(edge.source, edge.target): edge.relation for edge in graph.edges} == {
        ("alpha", "beta"): "supports",
        ("alpha", "gamma"): "validates",
        ("beta", "gamma"): "influences",
    }


def test_opinions_merge_into_existing_edges_and_clamp_weight() -> None:
    opinions = ({"holder_id": "alpha", "target_id": "beta", "sentiment": 1.0, "confidence": 0.9},)
    graph = GraphBuilder().build_graph(_entities(), _relationships(), opinions)
    edge = next(item for item in graph.edges if item.source == "alpha" and item.target == "beta")
    assert edge.weight == 1.0
    assert edge.relation == "supports+opinion"


def test_build_graph_is_deterministic() -> None:
    builder = GraphBuilder()
    first = builder.build_graph(_nodes(), _edges())
    second = builder.build_graph(reversed(_nodes()), reversed(_edges()))
    assert first.graph_sha256 == second.graph_sha256
    assert first == second


def test_build_graph_rejects_duplicate_nodes() -> None:
    nodes = (*_nodes(), GraphNode(node_id="alpha", node_type="claim", influence=0.1))
    with pytest.raises(GraphError, match="duplicate"):
        GraphBuilder().build_graph(nodes, _edges())


def test_build_graph_rejects_unknown_edge_endpoint() -> None:
    with pytest.raises(GraphError, match="unknown node"):
        GraphBuilder().build_graph(_nodes(), (GraphEdge("alpha", "missing", 0.5, "supports"),))


def test_build_graph_rejects_empty_graph() -> None:
    with pytest.raises(GraphError, match="at least one node"):
        GraphBuilder().build_graph((), ())


def test_graph_statistics_are_thread_safe() -> None:
    builder = GraphBuilder()
    threads = [Thread(target=lambda: builder.build_graph(_nodes(), _edges())) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert builder.get_statistics()["graphs_built"] == 8


def test_graph_builder_audit_events() -> None:
    trail = AuditTrail()
    builder = GraphBuilder(audit_trail=trail)
    graph = builder.build_graph(_nodes(), _edges())
    assert len(trail) == 2
    assert trail.events[0].action == "graph_builder_initialized"
    assert trail.events[1].action == "influence_graph_built"
    assert trail.events[1].level == AuditLevel.STANDARD
    assert trail.events[1].category == AuditCategory.OPERATION
    assert ("graph_sha256", graph.graph_sha256) in trail.events[1].evidence
    assert trail.verify_chain().is_valid


def test_graph_builder_audit_failure_event() -> None:
    trail = AuditTrail()
    builder = GraphBuilder(audit_trail=trail)
    with pytest.raises(GraphError):
        builder.build_graph((), ())
    assert trail.events[-1].action == "influence_graph_build_failed"
    assert trail.events[-1].level == AuditLevel.HIGH_PRIORITY
    assert trail.verify_chain().is_valid


def test_factory_and_reset() -> None:
    reset_graph_builder()
    first = get_graph_builder()
    second = get_graph_builder()
    assert first is second
    reset_graph_builder()
    assert get_graph_builder() is not first


def test_community_validation() -> None:
    community = Community(community_id="COMM-1", members=("alpha",), cohesion=1.0)
    assert community.subordination_notice == SUBORDINATION_NOTICE
    with pytest.raises(GraphError, match="members"):
        Community(community_id="COMM-1", members=(), cohesion=1.0)
    with pytest.raises(GraphError, match="cohesion"):
        Community(community_id="COMM-1", members=("alpha",), cohesion=1.5)
