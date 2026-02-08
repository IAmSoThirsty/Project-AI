"""
Graph Module for PROJECT ATLAS

Constructs influence graphs from normalized data, calculates network metrics,
detects communities, builds edges from relationships and opinions.

Production-grade with full error handling, logging, and audit trail integration.
"""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any

from atlas.audit.trail import AuditCategory, AuditLevel, AuditTrail, get_audit_trail
from atlas.config.loader import ConfigLoader, get_config_loader
from atlas.schemas.validator import SchemaValidator, get_schema_validator

logger = logging.getLogger(__name__)


class GraphError(Exception):
    """Raised when graph operations fail."""
    pass


class GraphBuilder:
    """
    Production-grade graph builder for PROJECT ATLAS.
    
    Constructs influence graphs, calculates network metrics (centrality, pagerank,
    clustering), detects communities, and builds edges from relationships.
    """

    def __init__(self,
                 config_loader: ConfigLoader | None = None,
                 schema_validator: SchemaValidator | None = None,
                 audit_trail: AuditTrail | None = None):
        """
        Initialize graph builder.
        
        Args:
            config_loader: Configuration loader (uses global if None)
            schema_validator: Schema validator (uses global if None)
            audit_trail: Audit trail (uses global if None)
        """
        self.config = config_loader or get_config_loader()
        self.validator = schema_validator or get_schema_validator()
        self.audit = audit_trail or get_audit_trail()

        # Load configuration
        self.thresholds = self.config.get("thresholds")
        self.graph_thresholds = self.thresholds.get("graph", {})

        # Track statistics
        self._stats = {
            "graphs_built": 0,
            "nodes_added": 0,
            "edges_added": 0,
            "metrics_calculated": 0,
            "communities_detected": 0
        }

        logger.info("GraphBuilder initialized successfully")

        self.audit.log_event(
            category=AuditCategory.SYSTEM,
            level=AuditLevel.INFORMATIONAL,
            operation="graph_builder_initialized",
            actor="GRAPH_MODULE",
            details={"config_hashes": self.config.get_all_hashes()}
        )

    def build_graph(self,
                   entities: list[dict[str, Any]],
                   relationships: list[dict[str, Any]],
                   opinions: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """
        Build influence graph from entities, relationships, and opinions.
        
        Args:
            entities: List of normalized entity objects
            relationships: List of relationship objects
            opinions: Optional list of opinion objects
            
        Returns:
            Influence graph object
            
        Raises:
            GraphError: If graph construction fails
        """
        try:
            self._stats["graphs_built"] += 1

            # Log graph construction start
            self.audit.log_event(
                category=AuditCategory.OPERATION,
                level=AuditLevel.STANDARD,
                operation="build_graph_start",
                actor="GRAPH_MODULE",
                details={
                    "entities_count": len(entities),
                    "relationships_count": len(relationships),
                    "opinions_count": len(opinions) if opinions else 0
                }
            )

            # Build nodes from entities
            nodes = self._build_nodes(entities)

            # Build edges from relationships and opinions
            edges = self._build_edges(relationships, opinions or [])

            # Calculate network metrics
            metrics = self._calculate_metrics(nodes, edges)

            # Detect communities
            communities = self._detect_communities(nodes, edges)

            # Create graph object
            graph = {
                "id": f"GRAPH-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
                "nodes": nodes,
                "edges": edges,
                "metrics": metrics,
                "communities": communities,
                "metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "graph_version": "1.0.0",
                    "nodes_count": len(nodes),
                    "edges_count": len(edges),
                    "communities_count": len(communities)
                }
            }

            # Validate against schema
            self.validator.validate_influence_graph(graph, strict=True)

            # Log success
            self.audit.log_event(
                category=AuditCategory.OPERATION,
                level=AuditLevel.STANDARD,
                operation="build_graph_success",
                actor="GRAPH_MODULE",
                details={
                    "graph_id": graph["id"],
                    "nodes": len(nodes),
                    "edges": len(edges),
                    "communities": len(communities)
                }
            )

            return graph

        except Exception as e:
            logger.error("Failed to build graph: %s", e)

            self.audit.log_event(
                category=AuditCategory.OPERATION,
                level=AuditLevel.HIGH_PRIORITY,
                operation="build_graph_failed",
                actor="GRAPH_MODULE",
                details={"error": str(e)}
            )

            raise GraphError(f"Failed to build graph: {e}") from e

    def _build_nodes(self, entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Build graph nodes from entities.
        
        Args:
            entities: List of entity objects
            
        Returns:
            List of node objects
        """
        nodes = []

        for entity in entities:
            node = {
                "id": entity["id"],
                "name": entity.get("name", entity["id"]),
                "type": entity.get("type", "unknown"),
                "influence": entity.get("influence", 0.5),
                "attributes": entity.get("attributes", {}),
                "metadata": {
                    "entity_id": entity["id"],
                    "quality_score": entity.get("metadata", {}).get("quality_score", 0.5)
                }
            }

            nodes.append(node)
            self._stats["nodes_added"] += 1

        return nodes

    def _build_edges(self,
                    relationships: list[dict[str, Any]],
                    opinions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Build graph edges from relationships and opinions.
        
        Args:
            relationships: List of relationship objects
            opinions: List of opinion objects
            
        Returns:
            List of edge objects
        """
        edges = []
        edge_map = {}  # (source, target) -> edge data

        # Add edges from relationships
        for rel in relationships:
            source_id = rel.get("source_id")
            target_id = rel.get("target_id")

            if not source_id or not target_id:
                continue

            edge_key = (source_id, target_id)

            if edge_key not in edge_map:
                edge_map[edge_key] = {
                    "source": source_id,
                    "target": target_id,
                    "weight": 0.0,
                    "type": "relationship",
                    "properties": {}
                }

            # Add relationship strength to weight
            strength = rel.get("strength", 0.5)
            edge_map[edge_key]["weight"] += strength
            edge_map[edge_key]["properties"]["relationship_type"] = rel.get("type", "unknown")

        # Add edges from opinions
        for opinion in opinions:
            holder_id = opinion.get("holder_id")
            target_id = opinion.get("target_id")

            if not holder_id or not target_id:
                continue

            edge_key = (holder_id, target_id)

            if edge_key not in edge_map:
                edge_map[edge_key] = {
                    "source": holder_id,
                    "target": target_id,
                    "weight": 0.0,
                    "type": "opinion",
                    "properties": {}
                }

            # Add opinion sentiment to weight (convert from [-1, 1] to [0, 1])
            sentiment = opinion.get("sentiment", 0.0)
            confidence = opinion.get("confidence", 0.5)
            weight_contribution = (sentiment + 1.0) / 2.0 * confidence

            edge_map[edge_key]["weight"] += weight_contribution
            edge_map[edge_key]["properties"]["sentiment"] = sentiment
            edge_map[edge_key]["properties"]["confidence"] = confidence

        # Normalize edge weights and create edge list
        for edge_data in edge_map.values():
            # Normalize weight to [0, 1]
            edge_data["weight"] = min(1.0, edge_data["weight"])

            edges.append(edge_data)
            self._stats["edges_added"] += 1

        return edges

    def _calculate_metrics(self,
                          nodes: list[dict[str, Any]],
                          edges: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Calculate network metrics.
        
        Args:
            nodes: List of node objects
            edges: List of edge objects
            
        Returns:
            Dictionary with network metrics
        """
        self._stats["metrics_calculated"] += 1

        # Build adjacency structures
        node_ids = {node["id"] for node in nodes}

        # Out-edges (source -> targets)
        out_edges: dict[str, list[tuple[str, float]]] = defaultdict(list)
        # In-edges (target -> sources)
        in_edges: dict[str, list[tuple[str, float]]] = defaultdict(list)

        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            weight = edge["weight"]

            if source in node_ids and target in node_ids:
                out_edges[source].append((target, weight))
                in_edges[target].append((source, weight))

        # Calculate centrality measures
        centrality = self._calculate_centrality(nodes, out_edges, in_edges)

        # Calculate PageRank
        pagerank = self._calculate_pagerank(nodes, out_edges, damping=0.85, iterations=100)

        # Calculate clustering coefficients
        clustering = self._calculate_clustering(nodes, out_edges, in_edges)

        # Calculate graph-level metrics
        total_edges = len(edges)
        max_possible_edges = len(nodes) * (len(nodes) - 1)
        density = total_edges / max_possible_edges if max_possible_edges > 0 else 0.0

        avg_degree = sum(len(out_edges[n["id"]]) + len(in_edges[n["id"]]) for n in nodes) / len(nodes) if nodes else 0.0

        return {
            "centrality": centrality,
            "pagerank": pagerank,
            "clustering": clustering,
            "graph_density": density,
            "average_degree": avg_degree,
            "total_nodes": len(nodes),
            "total_edges": total_edges
        }

    def _calculate_centrality(self,
                              nodes: list[dict[str, Any]],
                              out_edges: dict[str, list[tuple[str, float]]],
                              in_edges: dict[str, list[tuple[str, float]]]) -> dict[str, dict[str, float]]:
        """Calculate degree centrality for all nodes."""
        centrality = {}

        total_nodes = len(nodes)

        for node in nodes:
            node_id = node["id"]

            # In-degree (number of incoming edges)
            in_degree = len(in_edges[node_id])

            # Out-degree (number of outgoing edges)
            out_degree = len(out_edges[node_id])

            # Total degree
            degree = in_degree + out_degree

            # Normalized centrality
            normalized_centrality = degree / (total_nodes - 1) if total_nodes > 1 else 0.0

            centrality[node_id] = {
                "in_degree": in_degree,
                "out_degree": out_degree,
                "total_degree": degree,
                "normalized_centrality": normalized_centrality
            }

        return centrality

    def _calculate_pagerank(self,
                           nodes: list[dict[str, Any]],
                           out_edges: dict[str, list[tuple[str, float]]],
                           damping: float = 0.85,
                           iterations: int = 100) -> dict[str, float]:
        """
        Calculate PageRank scores for all nodes.
        
        Args:
            nodes: List of nodes
            out_edges: Out-edge adjacency
            damping: Damping factor (typically 0.85)
            iterations: Number of iterations
            
        Returns:
            Dictionary mapping node_id to PageRank score
        """
        # Initialize PageRank scores
        num_nodes = len(nodes)
        pagerank = {node["id"]: 1.0 / num_nodes for node in nodes}

        if num_nodes == 0:
            return pagerank

        # Iteratively update PageRank
        for _ in range(iterations):
            new_pagerank = {}

            for node in nodes:
                node_id = node["id"]

                # Sum contributions from incoming edges
                rank_sum = 0.0

                for source_node in nodes:
                    source_id = source_node["id"]

                    # Check if source_id has outgoing edge to node_id
                    out_neighbors = out_edges[source_id]

                    for target_id, weight in out_neighbors:
                        if target_id == node_id:
                            # Weight the contribution by edge weight
                            out_degree = len(out_neighbors)
                            if out_degree > 0:
                                rank_sum += (pagerank[source_id] / out_degree) * weight
                            break

                # Apply PageRank formula
                new_pagerank[node_id] = (1 - damping) / num_nodes + damping * rank_sum

            pagerank = new_pagerank

        # Normalize to sum to 1.0
        total_rank = sum(pagerank.values())
        if total_rank > 0:
            pagerank = {k: v / total_rank for k, v in pagerank.items()}

        return pagerank

    def _calculate_clustering(self,
                             nodes: list[dict[str, Any]],
                             out_edges: dict[str, list[tuple[str, float]]],
                             in_edges: dict[str, list[tuple[str, float]]]) -> dict[str, float]:
        """
        Calculate clustering coefficients.
        
        Args:
            nodes: List of nodes
            out_edges: Out-edge adjacency
            in_edges: In-edge adjacency
            
        Returns:
            Dictionary mapping node_id to clustering coefficient
        """
        clustering = {}

        for node in nodes:
            node_id = node["id"]

            # Get all neighbors (both in and out)
            neighbors = set()
            for target_id, _ in out_edges[node_id]:
                neighbors.add(target_id)
            for source_id, _ in in_edges[node_id]:
                neighbors.add(source_id)

            if len(neighbors) < 2:
                clustering[node_id] = 0.0
                continue

            # Count edges between neighbors
            edges_between_neighbors = 0

            for neighbor1 in neighbors:
                for neighbor2 in neighbors:
                    if neighbor1 != neighbor2:
                        # Check if edge exists
                        if any(target == neighbor2 for target, _ in out_edges[neighbor1]):
                            edges_between_neighbors += 1

            # Calculate clustering coefficient
            k = len(neighbors)
            max_edges = k * (k - 1)

            clustering[node_id] = edges_between_neighbors / max_edges if max_edges > 0 else 0.0

        return clustering

    def _detect_communities(self,
                           nodes: list[dict[str, Any]],
                           edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Detect communities using a simple modularity-based approach.
        
        Args:
            nodes: List of nodes
            edges: List of edges
            
        Returns:
            List of community objects
        """
        self._stats["communities_detected"] += 1

        # Simple community detection: group nodes by shared connections
        # For production, consider using more sophisticated algorithms

        # Build adjacency
        adjacency: dict[str, set[str]] = defaultdict(set)

        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            adjacency[source].add(target)
            adjacency[target].add(source)

        # Find connected components (simple community detection)
        visited = set()
        communities = []

        for node in nodes:
            node_id = node["id"]

            if node_id in visited:
                continue

            # BFS to find connected component
            community_nodes = []
            queue = [node_id]
            visited.add(node_id)

            while queue:
                current = queue.pop(0)
                community_nodes.append(current)

                for neighbor in adjacency[current]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            # Create community object
            if community_nodes:
                community = {
                    "id": f"COMM-{len(communities) + 1}",
                    "members": community_nodes,
                    "size": len(community_nodes),
                    "cohesion": self._calculate_community_cohesion(community_nodes, edges)
                }
                communities.append(community)

        return communities

    def _calculate_community_cohesion(self,
                                     member_ids: list[str],
                                     edges: list[dict[str, Any]]) -> float:
        """Calculate cohesion score for a community."""
        if len(member_ids) < 2:
            return 1.0

        member_set = set(member_ids)

        # Count internal edges
        internal_edges = 0
        total_weight = 0.0

        for edge in edges:
            if edge["source"] in member_set and edge["target"] in member_set:
                internal_edges += 1
                total_weight += edge["weight"]

        # Maximum possible internal edges
        max_internal_edges = len(member_ids) * (len(member_ids) - 1)

        # Cohesion is ratio of actual to maximum edges, weighted by edge weights
        if max_internal_edges > 0:
            density = internal_edges / max_internal_edges
            avg_weight = total_weight / internal_edges if internal_edges > 0 else 0.0
            return density * avg_weight

        return 0.0

    def get_statistics(self) -> dict[str, Any]:
        """Get graph building statistics."""
        return dict(self._stats)

    def reset_statistics(self) -> None:
        """Reset statistics counters."""
        self._stats = {
            "graphs_built": 0,
            "nodes_added": 0,
            "edges_added": 0,
            "metrics_calculated": 0,
            "communities_detected": 0
        }


if __name__ == "__main__":
    # Test graph module
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    try:
        builder = GraphBuilder()

        # Test entities
        entities = [
            {
                "id": "ORG-001",
                "name": "Organization Alpha",
                "type": "organization",
                "influence": 0.8,
                "attributes": {}
            },
            {
                "id": "ORG-002",
                "name": "Organization Beta",
                "type": "organization",
                "influence": 0.7,
                "attributes": {}
            },
            {
                "id": "ORG-003",
                "name": "Organization Gamma",
                "type": "organization",
                "influence": 0.6,
                "attributes": {}
            }
        ]

        # Test relationships
        relationships = [
            {"source_id": "ORG-001", "target_id": "ORG-002", "type": "alliance", "strength": 0.8},
            {"source_id": "ORG-002", "target_id": "ORG-003", "type": "partnership", "strength": 0.6},
            {"source_id": "ORG-001", "target_id": "ORG-003", "type": "cooperation", "strength": 0.5}
        ]

        # Test opinions
        opinions = [
            {"holder_id": "ORG-001", "target_id": "ORG-002", "sentiment": 0.7, "confidence": 0.8},
            {"holder_id": "ORG-002", "target_id": "ORG-003", "sentiment": 0.5, "confidence": 0.7}
        ]

        # Build graph
        graph = builder.build_graph(entities, relationships, opinions)

        print("Graph Built Successfully:")
        print(f"  ID: {graph['id']}")
        print(f"  Nodes: {len(graph['nodes'])}")
        print(f"  Edges: {len(graph['edges'])}")
        print(f"  Communities: {len(graph['communities'])}")

        print("\nNetwork Metrics:")
        metrics = graph['metrics']
        print(f"  Graph Density: {metrics['graph_density']:.4f}")
        print(f"  Average Degree: {metrics['average_degree']:.4f}")

        print("\nPageRank Scores:")
        for node_id, score in metrics['pagerank'].items():
            print(f"  {node_id}: {score:.4f}")

        print("\nCommunities:")
        for comm in graph['communities']:
            print(f"  {comm['id']}: {len(comm['members'])} members, cohesion: {comm['cohesion']:.4f}")

        # Print statistics
        print("\nStatistics:")
        import json
        print(json.dumps(builder.get_statistics(), indent=2))

    except Exception as e:
        logger.error("Test failed: %s", e, exc_info=True)
        raise
