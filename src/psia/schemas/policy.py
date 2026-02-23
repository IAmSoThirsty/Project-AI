"""
PSIA Policy Graph Schema — compiled Thirsty Lang policy representation.

Implements §3.4 of the PSIA v1.0 specification.

A PolicyGraph is the compiled form of a Thirsty Lang policy: a directed
acyclic graph of typed nodes (subject, action, resource, constraint,
decision) connected by edges.  The graph is versioned, hashed for
integrity, and signed by governance keys.
"""

from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, Field

from psia.schemas.identity import Signature


class PolicyNode(BaseModel):
    """A single node in the policy graph."""

    id: str = Field(..., description="Node identifier (e.g. n1, n2)")
    type: Literal["subject", "action", "resource", "constraint", "decision"] = Field(
        ..., description="Node type"
    )
    value: str = Field(..., description="Node value (DID, action verb, resource URI, expression, or decision)")

    model_config = {"frozen": True}


class PolicyEdge(BaseModel):
    """A directed edge in the policy graph."""

    from_node: str = Field(..., alias="from", description="Source node ID")
    to_node: str = Field(..., alias="to", description="Target node ID")

    model_config = {"frozen": True, "populate_by_name": True}


class PolicyGraph(BaseModel):
    """
    PSIA Policy Graph — a compiled Thirsty Lang policy.

    Invariants:
        - ``hash`` must equal the SHA-256 of the canonical serialization of nodes + edges
        - ``signatures`` must contain at least one governance signer
        - ``version`` is monotonically increasing per policy_id
    """

    policy_id: str = Field(..., description="Unique policy identifier (pol_...)")
    version: int = Field(..., ge=1, description="Monotonically increasing version")
    hash: str = Field(..., description="SHA-256 of canonical node+edge serialization")
    nodes: list[PolicyNode] = Field(..., min_length=1, description="Graph nodes")
    edges: list[PolicyEdge] = Field(default_factory=list, description="Graph edges")
    signatures: list[Signature] = Field(..., min_length=1, description="Governance signer signatures")

    model_config = {"frozen": True}

    def compute_graph_hash(self) -> str:
        """Compute deterministic SHA-256 hash of the graph structure (nodes + edges)."""
        body = {
            "nodes": [n.model_dump() for n in self.nodes],
            "edges": [e.model_dump(by_alias=True) for e in self.edges],
        }
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def verify_hash(self) -> bool:
        """Verify that the stored hash matches the computed graph hash."""
        return self.hash == self.compute_graph_hash()


__all__ = [
    "PolicyNode",
    "PolicyEdge",
    "PolicyGraph",
]
