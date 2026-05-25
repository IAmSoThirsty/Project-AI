"""PSIA policy graph schemas."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel

from psia.schemas.identity import Signature


class PolicyNode(BaseModel):
    id: str
    type: str
    value: str
    metadata: dict[str, Any] = {}


class PolicyEdge(BaseModel):
    source: str
    target: str
    relation: str = ""


class PolicyGraph(BaseModel):
    policy_id: str
    version: int
    hash: str
    nodes: list[PolicyNode]
    edges: list[PolicyEdge]
    signatures: list[Signature] = []

    def compute_graph_hash(self) -> str:
        body = {
            "nodes": [n.model_dump() for n in self.nodes],
            "edges": [e.model_dump() for e in self.edges],
        }
        return hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    def verify_hash(self) -> bool:
        return self.hash == self.compute_graph_hash()
