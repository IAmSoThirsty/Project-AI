"""
Graph Construction & Validation System for PROJECT ATLAS Ω

Implements complete temporal influence graph with:
- 6 node types (STATE_ACTOR, CORPORATE_ACTOR, REGULATOR, MEDIA_GATEKEEPER, 
  RELIGIOUS_AUTHORITY, PUBLIC_CLUSTER)
- 5 edge types (Capital flow, Board interlocks, Regulatory influence, 
  Media amplification, Funding relationships)
- Edge properties (weight, confidence_score, decay_rate, source_tier)
- Time-indexed adjacency tensor (sparse-matrix optimized)
- Merkle chain validation

Layer 3 Component - Production-Grade Implementation
"""

import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np

try:
    from scipy.sparse import csr_matrix, lil_matrix
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("scipy not available - sparse matrix optimization disabled")

from atlas.audit.trail import AuditCategory, AuditLevel, get_audit_trail

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """
    Six node types in the influence graph.
    """
    STATE_ACTOR = "state_actor"  # Governments, state entities
    CORPORATE_ACTOR = "corporate_actor"  # Corporations, businesses
    REGULATOR = "regulator"  # Regulatory bodies, agencies
    MEDIA_GATEKEEPER = "media_gatekeeper"  # Media outlets, platforms
    RELIGIOUS_AUTHORITY = "religious_authority"  # Religious institutions
    PUBLIC_CLUSTER = "public_cluster"  # Public groups, demographics

    def get_description(self) -> str:
        """Get human-readable description."""
        descriptions = {
            NodeType.STATE_ACTOR: "Government entities and state actors",
            NodeType.CORPORATE_ACTOR: "Corporations and business entities",
            NodeType.REGULATOR: "Regulatory bodies and oversight agencies",
            NodeType.MEDIA_GATEKEEPER: "Media outlets and information platforms",
            NodeType.RELIGIOUS_AUTHORITY: "Religious institutions and authorities",
            NodeType.PUBLIC_CLUSTER: "Public groups and demographic clusters"
        }
        return descriptions[self]


class EdgeType(Enum):
    """
    Five edge types representing different influence relationships.
    """
    CAPITAL_FLOW = "capital_flow"  # Financial flows and investments
    BOARD_INTERLOCK = "board_interlock"  # Shared board members/directors
    REGULATORY_INFLUENCE = "regulatory_influence"  # Regulatory relationships
    MEDIA_AMPLIFICATION = "media_amplification"  # Media coverage/promotion
    FUNDING_RELATIONSHIP = "funding_relationship"  # Funding and donations

    def get_description(self) -> str:
        """Get human-readable description."""
        descriptions = {
            EdgeType.CAPITAL_FLOW: "Financial flows and investment relationships",
            EdgeType.BOARD_INTERLOCK: "Shared board members and directorship",
            EdgeType.REGULATORY_INFLUENCE: "Regulatory oversight and influence",
            EdgeType.MEDIA_AMPLIFICATION: "Media coverage and information amplification",
            EdgeType.FUNDING_RELATIONSHIP: "Funding, donations, and financial support"
        }
        return descriptions[self]


@dataclass
class GraphNode:
    """
    Node in the influence graph.
    """
    node_id: str
    node_type: NodeType
    name: str

    # Optional metadata
    description: str | None = None
    jurisdiction: str | None = None
    sector: str | None = None
    size_metric: float | None = None  # Revenue, membership, etc.

    # Temporal tracking
    first_seen: datetime | None = None
    last_updated: datetime | None = None

    # Provenance
    source_tier: str | None = None
    source_hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "name": self.name,
            "description": self.description,
            "jurisdiction": self.jurisdiction,
            "sector": self.sector,
            "size_metric": self.size_metric,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "source_tier": self.source_tier,
            "source_hash": self.source_hash
        }


@dataclass
class GraphEdge:
    """
    Edge in the influence graph with complete properties.
    """
    edge_id: str
    source_id: str
    target_id: str
    edge_type: EdgeType

    # Required edge properties
    weight: float  # Strength of relationship [0, 1]
    confidence_score: float  # Confidence in edge existence [0, 1]
    decay_rate: float  # Temporal decay rate (per year)
    source_tier: str  # Data tier (TierA/B/C/D)

    # Optional metadata
    description: str | None = None
    amount: float | None = None  # For capital flow, funding
    start_date: datetime | None = None
    end_date: datetime | None = None

    # Provenance
    source_hash: str | None = None
    evidence_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type.value,
            "weight": self.weight,
            "confidence_score": self.confidence_score,
            "decay_rate": self.decay_rate,
            "source_tier": self.source_tier,
            "description": self.description,
            "amount": self.amount,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "source_hash": self.source_hash,
            "evidence_ids": self.evidence_ids
        }

    def compute_current_weight(self, current_time: datetime) -> float:
        """
        Compute current weight with temporal decay.
        
        Args:
            current_time: Current timestamp
            
        Returns:
            Decayed weight
        """
        if not self.start_date:
            return self.weight

        years_elapsed = (current_time - self.start_date).days / 365.25
        decayed_weight = self.weight * np.exp(-self.decay_rate * years_elapsed)

        return max(0.0, min(1.0, decayed_weight))

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate edge properties.
        
        Returns:
            (valid, list of errors)
        """
        errors = []

        if not (0.0 <= self.weight <= 1.0):
            errors.append(f"weight = {self.weight} (must be in [0, 1])")

        if not (0.0 <= self.confidence_score <= 1.0):
            errors.append(f"confidence_score = {self.confidence_score} (must be in [0, 1])")

        if self.decay_rate < 0:
            errors.append(f"decay_rate = {self.decay_rate} (must be >= 0)")

        if self.source_tier not in ["TierA", "TierB", "TierC", "TierD"]:
            errors.append(f"source_tier = {self.source_tier} (must be TierA/B/C/D)")

        if not self.source_hash:
            errors.append("source_hash required (no hash → no inclusion)")

        return len(errors) == 0, errors


@dataclass
class GraphSnapshot:
    """
    Time-indexed snapshot of the influence graph.
    """
    timestamp: datetime
    nodes: dict[str, GraphNode]
    edges: dict[str, GraphEdge]

    # Merkle chain for validation
    previous_hash: str | None = None
    snapshot_hash: str | None = None

    # Metadata
    node_count_by_type: dict[str, int] = field(default_factory=dict)
    edge_count_by_type: dict[str, int] = field(default_factory=dict)

    def compute_hash(self) -> str:
        """Compute Merkle hash of this snapshot."""
        # Create canonical representation
        canonical = {
            "timestamp": self.timestamp.isoformat(),
            "nodes": sorted([n.to_dict() for n in self.nodes.values()], key=lambda x: x["node_id"]),
            "edges": sorted([e.to_dict() for e in self.edges.values()], key=lambda x: x["edge_id"]),
            "previous_hash": self.previous_hash
        }

        content = json.dumps(canonical, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(content.encode()).hexdigest()

    def to_adjacency_matrix(self, sparse: bool = True) -> Any:
        """
        Convert to adjacency matrix.
        
        Args:
            sparse: Use sparse matrix representation (requires scipy)
            
        Returns:
            Adjacency matrix (sparse or dense)
        """
        node_ids = sorted(self.nodes.keys())
        n = len(node_ids)
        node_idx = {nid: i for i, nid in enumerate(node_ids)}

        if sparse and SCIPY_AVAILABLE:
            matrix = lil_matrix((n, n), dtype=float)
        else:
            matrix = np.zeros((n, n), dtype=float)

        for edge in self.edges.values():
            if edge.source_id in node_idx and edge.target_id in node_idx:
                i = node_idx[edge.source_id]
                j = node_idx[edge.target_id]
                matrix[i, j] = edge.weight

        if sparse and SCIPY_AVAILABLE:
            return matrix.tocsr()
        return matrix


class GraphBuilder:
    """
    Production-grade temporal influence graph construction system.
    
    Implements:
    - 6 node types with complete metadata
    - 5 edge types with 4 required properties
    - Time-indexed snapshots
    - Merkle chain validation
    - Sparse-matrix optimization
    - Constitutional "no hash → no inclusion" enforcement
    """

    def __init__(self, data_dir: Path | None = None):
        """
        Initialize graph builder.
        
        Args:
            data_dir: Path to data directory
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "data"

        self.data_dir = Path(data_dir)
        self.graph_dir = self.data_dir / "graphs"
        self.graph_dir.mkdir(parents=True, exist_ok=True)

        self.audit = get_audit_trail()

        # Graph state
        self.nodes: dict[str, GraphNode] = {}
        self.edges: dict[str, GraphEdge] = {}
        self.snapshots: list[GraphSnapshot] = []

        # Merkle chain tracking
        self.baseline_hash: str | None = None

        logger.info("Initialized GraphBuilder")

        self.audit.log_event(
            category=AuditCategory.SYSTEM,
            level=AuditLevel.INFORMATIONAL,
            operation="graph_builder_initialized",
            actor="GRAPH_BUILDER",
            details={"data_dir": str(self.data_dir)}
        )

    def add_node(self, node: GraphNode) -> None:
        """
        Add node to graph.
        
        Args:
            node: GraphNode to add
            
        Raises:
            ValueError: If node validation fails
        """
        # Validate source hash (constitutional requirement)
        if not node.source_hash:
            raise ValueError(
                f"Node {node.node_id} missing source_hash - "
                "no hash → no inclusion (constitutional rule)"
            )

        # Add or update node
        if node.node_id in self.nodes:
            logger.info("Updating existing node: %s", node.node_id)
            node.last_updated = datetime.utcnow()
        else:
            logger.info("Adding new node: %s (%s)", node.node_id, node.node_type.value)
            node.first_seen = datetime.utcnow()
            node.last_updated = datetime.utcnow()

        self.nodes[node.node_id] = node

        self.audit.log_event(
            category=AuditCategory.DATA,
            level=AuditLevel.INFORMATIONAL,
            operation="node_added",
            actor="GRAPH_BUILDER",
            details={
                "node_id": node.node_id,
                "node_type": node.node_type.value,
                "name": node.name
            }
        )

    def add_edge(self, edge: GraphEdge) -> None:
        """
        Add edge to graph.
        
        Args:
            edge: GraphEdge to add
            
        Raises:
            ValueError: If edge validation fails
        """
        # Validate edge
        valid, errors = edge.validate()
        if not valid:
            raise ValueError(f"Edge {edge.edge_id} validation failed: {errors}")

        # Check source and target nodes exist
        if edge.source_id not in self.nodes:
            raise ValueError(f"Source node {edge.source_id} not found")
        if edge.target_id not in self.nodes:
            raise ValueError(f"Target node {edge.target_id} not found")

        # Add edge
        self.edges[edge.edge_id] = edge

        logger.info(
            f"Added edge: {edge.edge_id} ({edge.source_id} → {edge.target_id}, "
            f"type: {edge.edge_type.value})"
        )

        self.audit.log_event(
            category=AuditCategory.DATA,
            level=AuditLevel.INFORMATIONAL,
            operation="edge_added",
            actor="GRAPH_BUILDER",
            details={
                "edge_id": edge.edge_id,
                "edge_type": edge.edge_type.value,
                "source_id": edge.source_id,
                "target_id": edge.target_id,
                "weight": edge.weight,
                "source_tier": edge.source_tier
            }
        )

    def create_snapshot(self, timestamp: datetime | None = None) -> GraphSnapshot:
        """
        Create time-indexed snapshot of current graph state.
        
        Args:
            timestamp: Snapshot timestamp (defaults to now)
            
        Returns:
            GraphSnapshot with Merkle hash
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        # Count nodes and edges by type
        node_counts = defaultdict(int)
        for node in self.nodes.values():
            node_counts[node.node_type.value] += 1

        edge_counts = defaultdict(int)
        for edge in self.edges.values():
            edge_counts[edge.edge_type.value] += 1

        # Get previous hash from last snapshot
        previous_hash = None
        if self.snapshots:
            previous_hash = self.snapshots[-1].snapshot_hash
        elif self.baseline_hash:
            previous_hash = self.baseline_hash

        # Create snapshot
        snapshot = GraphSnapshot(
            timestamp=timestamp,
            nodes=self.nodes.copy(),
            edges=self.edges.copy(),
            previous_hash=previous_hash,
            node_count_by_type=dict(node_counts),
            edge_count_by_type=dict(edge_counts)
        )

        # Compute and store Merkle hash
        snapshot.snapshot_hash = snapshot.compute_hash()

        # Add to snapshot history
        self.snapshots.append(snapshot)

        logger.info(
            f"Created graph snapshot at {timestamp.isoformat()} "
            f"(hash: {snapshot.snapshot_hash[:16]}...)"
        )

        self.audit.log_event(
            category=AuditCategory.DATA,
            level=AuditLevel.INFORMATIONAL,
            operation="snapshot_created",
            actor="GRAPH_BUILDER",
            details={
                "timestamp": timestamp.isoformat(),
                "snapshot_hash": snapshot.snapshot_hash,
                "previous_hash": previous_hash,
                "node_count": len(self.nodes),
                "edge_count": len(self.edges)
            }
        )

        return snapshot

    def verify_merkle_chain(self) -> tuple[bool, list[str]]:
        """
        Verify Merkle chain integrity of all snapshots.
        
        Returns:
            (valid, list of errors)
        """
        errors = []

        if not self.snapshots:
            return True, []

        # Verify each snapshot's hash
        for i, snapshot in enumerate(self.snapshots):
            computed_hash = snapshot.compute_hash()
            if computed_hash != snapshot.snapshot_hash:
                errors.append(
                    f"Snapshot {i} hash mismatch: "
                    f"stored={snapshot.snapshot_hash[:16]}..., "
                    f"computed={computed_hash[:16]}..."
                )

        # Verify chain linkage
        expected_previous = self.baseline_hash
        for i, snapshot in enumerate(self.snapshots):
            if snapshot.previous_hash != expected_previous:
                errors.append(
                    f"Snapshot {i} chain break: "
                    f"previous_hash={snapshot.previous_hash[:16] if snapshot.previous_hash else None}..., "
                    f"expected={expected_previous[:16] if expected_previous else None}..."
                )
            expected_previous = snapshot.snapshot_hash

        valid = len(errors) == 0

        if not valid:
            logger.error("Merkle chain validation failed: %s", errors)
            self.audit.log_event(
                category=AuditCategory.GOVERNANCE,
                level=AuditLevel.CRITICAL,
                operation="merkle_chain_invalid",
                actor="GRAPH_BUILDER",
                details={"errors": errors}
            )

        return valid, errors

    def save_snapshot(self, snapshot: GraphSnapshot, filename: str | None = None) -> Path:
        """
        Save snapshot to file.
        
        Args:
            snapshot: Snapshot to save
            filename: Optional filename (defaults to timestamp-based)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"graph_snapshot_{snapshot.timestamp.strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.graph_dir / filename

        snapshot_data = {
            "timestamp": snapshot.timestamp.isoformat(),
            "snapshot_hash": snapshot.snapshot_hash,
            "previous_hash": snapshot.previous_hash,
            "node_count_by_type": snapshot.node_count_by_type,
            "edge_count_by_type": snapshot.edge_count_by_type,
            "nodes": [n.to_dict() for n in snapshot.nodes.values()],
            "edges": [e.to_dict() for e in snapshot.edges.values()]
        }

        with open(filepath, 'w') as f:
            json.dump(snapshot_data, f, indent=2, sort_keys=True)

        logger.info("Saved snapshot to %s", filepath)

        return filepath

    def get_statistics(self) -> dict[str, Any]:
        """Get graph statistics."""
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "node_types": {
                node_type.value: sum(1 for n in self.nodes.values() if n.node_type == node_type)
                for node_type in NodeType
            },
            "edge_types": {
                edge_type.value: sum(1 for e in self.edges.values() if e.edge_type == edge_type)
                for edge_type in EdgeType
            },
            "snapshot_count": len(self.snapshots),
            "latest_snapshot": self.snapshots[-1].timestamp.isoformat() if self.snapshots else None,
            "merkle_chain_valid": self.verify_merkle_chain()[0]
        }


# Singleton instance
_graph_builder: GraphBuilder | None = None


def get_graph_builder() -> GraphBuilder:
    """Get singleton graph builder instance."""
    global _graph_builder
    if _graph_builder is None:
        _graph_builder = GraphBuilder()
    return _graph_builder
