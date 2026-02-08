"""
Historical Build Graph Database.

Provides graph-based storage and analysis of build relationships, including
build ancestry, artifact provenance, dependency tracking, and failure correlation.
"""

import json
import logging
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class BuildNode:
    """Represents a build in the graph."""

    id: int
    version: str
    timestamp: str
    status: str
    capsule_id: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class ArtifactNode:
    """Represents an artifact in the graph."""

    id: int
    build_id: int
    path: str
    hash: str
    type: str
    size: int
    signed: bool = False


@dataclass
class DependencyNode:
    """Represents a dependency in the graph."""

    id: int
    build_id: int
    name: str
    version: str
    hash: str | None = None
    vulnerability_count: int = 0


@dataclass
class GraphEdge:
    """Represents an edge in the build graph."""

    source: int
    target: int
    edge_type: str
    metadata: dict[str, Any] | None = None


class BuildGraphDB:
    """
    Historical build graph database.

    Manages graph relationships between builds, artifacts, and dependencies
    for ancestry tracking, provenance analysis, and failure correlation.
    """

    def __init__(self, build_memory_db):
        """
        Initialize build graph database.

        Args:
            build_memory_db: BuildMemoryDB instance for data access
        """
        from gradle_evolution.db.schema import BuildMemoryDB

        if not isinstance(build_memory_db, BuildMemoryDB):
            raise TypeError("build_memory_db must be BuildMemoryDB instance")

        self.db = build_memory_db
        self._build_nodes: dict[int, BuildNode] = {}
        self._artifact_nodes: dict[int, ArtifactNode] = {}
        self._dependency_nodes: dict[int, DependencyNode] = {}
        self._edges: list[GraphEdge] = []

        # Adjacency lists for fast traversal
        self._forward_edges: dict[int, list[GraphEdge]] = defaultdict(list)
        self._backward_edges: dict[int, list[GraphEdge]] = defaultdict(list)

        logger.info("BuildGraphDB initialized")

    def build_graph(self, limit: int | None = None) -> None:
        """
        Build complete graph from database.

        Args:
            limit: Maximum number of builds to load (most recent)
        """
        logger.info("Building graph from database...")

        # Load builds
        builds = self.db.get_builds(limit=limit or 10000, offset=0)
        for build in builds:
            self._build_nodes[build["id"]] = BuildNode(
                id=build["id"],
                version=build["version"],
                timestamp=build["timestamp"],
                status=build["status"],
                capsule_id=build["capsule_id"],
                metadata=json.loads(build["metadata"]) if build.get("metadata") else None,
            )

        # Load artifacts and create edges
        for build_id in self._build_nodes:
            artifacts = self.db.get_artifacts(build_id)
            for artifact in artifacts:
                art_id = artifact["id"]
                self._artifact_nodes[art_id] = ArtifactNode(
                    id=art_id,
                    build_id=build_id,
                    path=artifact["path"],
                    hash=artifact["hash"],
                    type=artifact["type"],
                    size=artifact["size"],
                    signed=bool(artifact["signed"]),
                )
                # Create PRODUCES edge
                self._add_edge(build_id, art_id, "PRODUCES", {"path": artifact["path"]})

        # Load dependencies and create edges
        for build_id in self._build_nodes:
            dependencies = self.db.get_dependencies(build_id)
            for dep in dependencies:
                dep_id = dep["id"]
                self._dependency_nodes[dep_id] = DependencyNode(
                    id=dep_id,
                    build_id=build_id,
                    name=dep["name"],
                    version=dep["version"],
                    hash=dep.get("hash"),
                    vulnerability_count=dep["vulnerability_count"],
                )
                # Create DEPENDS_ON edge
                self._add_edge(build_id, dep_id, "DEPENDS_ON", {
                    "name": dep["name"],
                    "version": dep["version"],
                })

        # Find build relationships
        self._compute_build_ancestry()
        self._compute_shared_artifacts()

        logger.info(
            f"Graph built: {len(self._build_nodes)} builds, "
            f"{len(self._artifact_nodes)} artifacts, "
            f"{len(self._dependency_nodes)} dependencies, "
            f"{len(self._edges)} edges"
        )

    def _add_edge(
        self,
        source: int,
        target: int,
        edge_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add edge to graph with bidirectional indexes."""
        edge = GraphEdge(source, target, edge_type, metadata)
        self._edges.append(edge)
        self._forward_edges[source].append(edge)
        self._backward_edges[target].append(edge)

    def _compute_build_ancestry(self) -> None:
        """Compute EVOLVED_FROM relationships between builds."""
        # Sort builds by timestamp
        sorted_builds = sorted(
            self._build_nodes.values(),
            key=lambda b: b.timestamp,
        )

        # For each build, find parent build (previous version or same capsule)
        for i in range(1, len(sorted_builds)):
            current = sorted_builds[i]
            previous = sorted_builds[i - 1]

            # Direct evolution: same version line or capsule
            if (current.capsule_id and current.capsule_id == previous.capsule_id) or \
               self._is_version_evolution(previous.version, current.version):
                self._add_edge(
                    current.id,
                    previous.id,
                    "EVOLVED_FROM",
                    {
                        "time_delta": self._time_delta(previous.timestamp, current.timestamp),
                        "version_from": previous.version,
                        "version_to": current.version,
                    },
                )

    def _compute_shared_artifacts(self) -> None:
        """Compute SHARES_ARTIFACT relationships between builds."""
        # Group artifacts by hash
        hash_to_builds: dict[str, list[int]] = defaultdict(list)
        for artifact in self._artifact_nodes.values():
            hash_to_builds[artifact.hash].append(artifact.build_id)

        # Create edges for shared artifacts
        for artifact_hash, build_ids in hash_to_builds.items():
            if len(build_ids) > 1:
                # Connect all builds that share this artifact
                for i in range(len(build_ids)):
                    for j in range(i + 1, len(build_ids)):
                        self._add_edge(
                            build_ids[i],
                            build_ids[j],
                            "SHARES_ARTIFACT",
                            {"artifact_hash": artifact_hash},
                        )

    def _is_version_evolution(self, old_version: str, new_version: str) -> bool:
        """Check if new_version is an evolution of old_version."""
        try:
            # Simple semantic version check
            old_parts = [int(x) for x in old_version.split(".")]
            new_parts = [int(x) for x in new_version.split(".")]

            # New version should be greater
            return new_parts > old_parts
        except (ValueError, AttributeError):
            return False

    def _time_delta(self, time1: str, time2: str) -> float:
        """Calculate time delta in seconds between two ISO timestamps."""
        try:
            t1 = datetime.fromisoformat(time1)
            t2 = datetime.fromisoformat(time2)
            return abs((t2 - t1).total_seconds())
        except (ValueError, TypeError):
            return 0.0

    # ==================== Graph Queries ====================

    def find_build_ancestry(self, build_id: int, depth: int = 10) -> list[BuildNode]:
        """
        Find build ancestry (parent builds).

        Args:
            build_id: Starting build ID
            depth: Maximum depth to traverse

        Returns:
            List of ancestor BuildNodes in chronological order
        """
        ancestors = []
        visited = {build_id}
        current_depth = 0

        # BFS backwards through EVOLVED_FROM edges
        queue = deque([(build_id, 0)])

        while queue and current_depth < depth:
            node_id, node_depth = queue.popleft()

            if node_depth > current_depth:
                current_depth = node_depth

            for edge in self._forward_edges.get(node_id, []):
                if edge.edge_type == "EVOLVED_FROM" and edge.target not in visited:
                    parent_build = self._build_nodes.get(edge.target)
                    if parent_build:
                        ancestors.append(parent_build)
                        visited.add(edge.target)
                        queue.append((edge.target, node_depth + 1))

        # Sort by timestamp (oldest first)
        ancestors.sort(key=lambda b: b.timestamp)
        return ancestors

    def find_build_descendants(self, build_id: int, depth: int = 10) -> list[BuildNode]:
        """
        Find build descendants (child builds).

        Args:
            build_id: Starting build ID
            depth: Maximum depth to traverse

        Returns:
            List of descendant BuildNodes in chronological order
        """
        descendants = []
        visited = {build_id}
        current_depth = 0

        # BFS forwards through EVOLVED_FROM edges
        queue = deque([(build_id, 0)])

        while queue and current_depth < depth:
            node_id, node_depth = queue.popleft()

            if node_depth > current_depth:
                current_depth = node_depth

            for edge in self._backward_edges.get(node_id, []):
                if edge.edge_type == "EVOLVED_FROM" and edge.source not in visited:
                    child_build = self._build_nodes.get(edge.source)
                    if child_build:
                        descendants.append(child_build)
                        visited.add(edge.source)
                        queue.append((edge.source, node_depth + 1))

        # Sort by timestamp (oldest first)
        descendants.sort(key=lambda b: b.timestamp)
        return descendants

    def detect_dependency_cycles(self) -> list[list[int]]:
        """
        Detect circular dependencies in the build graph.

        Returns:
            List of cycles, where each cycle is a list of dependency IDs
        """
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node_id: int, path: list[int]) -> None:
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)

            for edge in self._forward_edges.get(node_id, []):
                if edge.edge_type == "DEPENDS_ON":
                    if edge.target not in visited:
                        dfs(edge.target, path.copy())
                    elif edge.target in rec_stack:
                        # Cycle detected
                        cycle_start = path.index(edge.target)
                        cycle = path[cycle_start:] + [edge.target]
                        cycles.append(cycle)

            rec_stack.remove(node_id)

        # Check all dependency nodes
        for dep_id in self._dependency_nodes:
            if dep_id not in visited:
                dfs(dep_id, [])

        logger.info("Detected %s dependency cycles", len(cycles))
        return cycles

    def trace_artifact_provenance(self, artifact_hash: str) -> list[dict[str, Any]]:
        """
        Trace artifact provenance across builds.

        Args:
            artifact_hash: Artifact hash to trace

        Returns:
            List of provenance records with build and artifact info
        """
        provenance = []

        for artifact in self._artifact_nodes.values():
            if artifact.hash == artifact_hash:
                build = self._build_nodes.get(artifact.build_id)
                if build:
                    provenance.append({
                        "build_id": build.id,
                        "build_version": build.version,
                        "build_timestamp": build.timestamp,
                        "build_status": build.status,
                        "artifact_path": artifact.path,
                        "artifact_type": artifact.type,
                        "artifact_signed": artifact.signed,
                    })

        # Sort by timestamp
        provenance.sort(key=lambda p: p["build_timestamp"])

        logger.debug("Found %s provenance records for hash %s...", len(provenance), artifact_hash[)
        return provenance

    def identify_failure_correlations(
        self,
        min_correlation: float = 0.5,
    ) -> list[dict[str, Any]]:
        """
        Identify correlated build failures.

        Args:
            min_correlation: Minimum correlation threshold (0.0 to 1.0)

        Returns:
            List of failure correlations with metadata
        """
        correlations = []

        # Get all failed builds
        failed_builds = [b for b in self._build_nodes.values() if b.status == "failure"]

        if len(failed_builds) < 2:
            return correlations

        # Group by time windows (1 hour)
        time_groups: dict[str, list[BuildNode]] = defaultdict(list)

        for build in failed_builds:
            try:
                timestamp = datetime.fromisoformat(build.timestamp)
                window_key = f"{timestamp.year}-{timestamp.month}-{timestamp.day}-{timestamp.hour}"
                time_groups[window_key].append(build)
            except ValueError:
                continue

        # Find correlations within time windows
        for window, builds in time_groups.items():
            if len(builds) >= 2:
                # Check for shared dependencies or artifacts
                for i in range(len(builds)):
                    for j in range(i + 1, len(builds)):
                        correlation = self._compute_build_correlation(
                            builds[i].id,
                            builds[j].id,
                        )
                        if correlation >= min_correlation:
                            correlations.append({
                                "build1_id": builds[i].id,
                                "build1_version": builds[i].version,
                                "build2_id": builds[j].id,
                                "build2_version": builds[j].version,
                                "correlation": correlation,
                                "time_window": window,
                            })

        logger.info("Found %s failure correlations", len(correlations))
        return correlations

    def _compute_build_correlation(self, build1_id: int, build2_id: int) -> float:
        """Compute correlation score between two builds."""
        # Get shared artifacts
        artifacts1 = {
            a.hash for a in self._artifact_nodes.values()
            if a.build_id == build1_id
        }
        artifacts2 = {
            a.hash for a in self._artifact_nodes.values()
            if a.build_id == build2_id
        }

        shared_artifacts = len(artifacts1 & artifacts2)
        total_artifacts = len(artifacts1 | artifacts2)

        # Get shared dependencies
        deps1 = {
            (d.name, d.version) for d in self._dependency_nodes.values()
            if d.build_id == build1_id
        }
        deps2 = {
            (d.name, d.version) for d in self._dependency_nodes.values()
            if d.build_id == build2_id
        }

        shared_deps = len(deps1 & deps2)
        total_deps = len(deps1 | deps2)

        # Weighted correlation
        if total_artifacts > 0 and total_deps > 0:
            artifact_correlation = shared_artifacts / total_artifacts
            dep_correlation = shared_deps / total_deps
            return (artifact_correlation * 0.4 + dep_correlation * 0.6)
        elif total_deps > 0:
            return shared_deps / total_deps
        elif total_artifacts > 0:
            return shared_artifacts / total_artifacts
        else:
            return 0.0

    def find_builds_with_artifact(self, artifact_hash: str) -> list[BuildNode]:
        """Find all builds that produced a specific artifact."""
        builds = []
        for artifact in self._artifact_nodes.values():
            if artifact.hash == artifact_hash:
                build = self._build_nodes.get(artifact.build_id)
                if build and build not in builds:
                    builds.append(build)
        return builds

    def find_builds_with_dependency(
        self,
        dep_name: str,
        dep_version: str | None = None,
    ) -> list[BuildNode]:
        """Find all builds that depend on a specific dependency."""
        builds = []
        for dep in self._dependency_nodes.values():
            if dep.name == dep_name and (dep_version is None or dep.version == dep_version):
                build = self._build_nodes.get(dep.build_id)
                if build and build not in builds:
                    builds.append(build)
        return builds

    def get_vulnerable_build_paths(self) -> list[dict[str, Any]]:
        """Find builds with vulnerable dependencies and their ancestry."""
        vulnerable_paths = []

        for dep in self._dependency_nodes.values():
            if dep.vulnerability_count > 0:
                build = self._build_nodes.get(dep.build_id)
                if not build:
                    continue

                ancestors = self.find_build_ancestry(dep.build_id, depth=5)
                descendants = self.find_build_descendants(dep.build_id, depth=5)

                vulnerable_paths.append({
                    "build_id": build.id,
                    "build_version": build.version,
                    "dependency": f"{dep.name}:{dep.version}",
                    "vulnerability_count": dep.vulnerability_count,
                    "ancestors": [{"id": a.id, "version": a.version} for a in ancestors],
                    "descendants": [{"id": d.id, "version": d.version} for d in descendants],
                })

        return vulnerable_paths

    # ==================== Graph Export ====================

    def export_to_dot(self, output_path: Path | None = None) -> str:
        """
        Export graph to DOT format for visualization.

        Args:
            output_path: Optional file path to write DOT file

        Returns:
            DOT format string
        """
        lines = ["digraph BuildGraph {"]
        lines.append('  rankdir=LR;')
        lines.append('  node [shape=box];')
        lines.append('')

        # Build nodes
        lines.append('  // Build nodes')
        for build in self._build_nodes.values():
            color = {
                "success": "green",
                "failure": "red",
                "cancelled": "orange",
                "running": "blue",
            }.get(build.status, "gray")

            lines.append(
                f'  build_{build.id} [label="Build {build.id}\\n{build.version}\\n{build.status}", '
                f'color={color}, style=filled, fillcolor={color}22];'
            )

        # Artifact nodes
        lines.append('')
        lines.append('  // Artifact nodes')
        lines.append('  node [shape=ellipse, color=purple];')
        for artifact in self._artifact_nodes.values():
            label = f"{Path(artifact.path).name}\\n{artifact.hash[:8]}"
            lines.append(f'  artifact_{artifact.id} [label="{label}"];')

        # Dependency nodes
        lines.append('')
        lines.append('  // Dependency nodes')
        lines.append('  node [shape=diamond, color=blue];')
        for dep in self._dependency_nodes.values():
            color = "red" if dep.vulnerability_count > 0 else "blue"
            label = f"{dep.name}\\n{dep.version}"
            if dep.vulnerability_count > 0:
                label += f"\\n⚠ {dep.vulnerability_count} vulns"
            lines.append(
                f'  dep_{dep.id} [label="{label}", color={color}];'
            )

        # Edges
        lines.append('')
        lines.append('  // Edges')
        edge_styles = {
            "PRODUCES": '[color=purple, label="produces"]',
            "DEPENDS_ON": '[color=blue, label="depends"]',
            "EVOLVED_FROM": '[color=green, label="evolved", style=dashed]',
            "SHARES_ARTIFACT": '[color=orange, label="shares", style=dotted]',
        }

        for edge in self._edges:
            style = edge_styles.get(edge.edge_type, "")

            # Determine node prefixes
            source_prefix = "build"
            target_prefix = "build"

            if edge.edge_type == "PRODUCES":
                target_prefix = "artifact"
            elif edge.edge_type == "DEPENDS_ON":
                target_prefix = "dep"

            lines.append(
                f'  {source_prefix}_{edge.source} -> {target_prefix}_{edge.target} {style};'
            )

        lines.append('}')

        dot_content = '\n'.join(lines)

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(dot_content)
            logger.info("Exported graph to %s", output_path)

        return dot_content

    def export_to_json(self, output_path: Path | None = None) -> dict[str, Any]:
        """
        Export graph to JSON format.

        Args:
            output_path: Optional file path to write JSON file

        Returns:
            Graph data as dictionary
        """
        graph_data = {
            "nodes": {
                "builds": [
                    {
                        "id": b.id,
                        "version": b.version,
                        "timestamp": b.timestamp,
                        "status": b.status,
                        "capsule_id": b.capsule_id,
                    }
                    for b in self._build_nodes.values()
                ],
                "artifacts": [
                    {
                        "id": a.id,
                        "build_id": a.build_id,
                        "path": a.path,
                        "hash": a.hash,
                        "type": a.type,
                        "size": a.size,
                        "signed": a.signed,
                    }
                    for a in self._artifact_nodes.values()
                ],
                "dependencies": [
                    {
                        "id": d.id,
                        "build_id": d.build_id,
                        "name": d.name,
                        "version": d.version,
                        "hash": d.hash,
                        "vulnerability_count": d.vulnerability_count,
                    }
                    for d in self._dependency_nodes.values()
                ],
            },
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "type": e.edge_type,
                    "metadata": e.metadata,
                }
                for e in self._edges
            ],
        }

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(graph_data, indent=2))
            logger.info("Exported graph to %s", output_path)

        return graph_data

    def get_graph_statistics(self) -> dict[str, Any]:
        """Get graph statistics."""
        return {
            "nodes": {
                "builds": len(self._build_nodes),
                "artifacts": len(self._artifact_nodes),
                "dependencies": len(self._dependency_nodes),
                "total": len(self._build_nodes) + len(self._artifact_nodes) + len(self._dependency_nodes),
            },
            "edges": {
                "total": len(self._edges),
                "by_type": self._count_edges_by_type(),
            },
            "builds": {
                "total": len(self._build_nodes),
                "by_status": self._count_builds_by_status(),
            },
            "vulnerabilities": {
                "total_dependencies": len(self._dependency_nodes),
                "vulnerable_dependencies": sum(
                    1 for d in self._dependency_nodes.values()
                    if d.vulnerability_count > 0
                ),
                "total_vulnerabilities": sum(
                    d.vulnerability_count for d in self._dependency_nodes.values()
                ),
            },
        }

    def _count_edges_by_type(self) -> dict[str, int]:
        """Count edges by type."""
        counts = defaultdict(int)
        for edge in self._edges:
            counts[edge.edge_type] += 1
        return dict(counts)

    def _count_builds_by_status(self) -> dict[str, int]:
        """Count builds by status."""
        counts = defaultdict(int)
        for build in self._build_nodes.values():
            counts[build.status] += 1
        return dict(counts)

    def clear(self) -> None:
        """Clear all graph data from memory."""
        self._build_nodes.clear()
        self._artifact_nodes.clear()
        self._dependency_nodes.clear()
        self._edges.clear()
        self._forward_edges.clear()
        self._backward_edges.clear()
        logger.info("Graph cleared")
