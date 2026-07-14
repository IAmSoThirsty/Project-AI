"""
ccma.store

The graph store. ONE nodes table, ONE edges table — this is the literal
implementation of CCMA Part XIII ("there is only one living graph").

Why SQLite and not a graph database: your existing Project-AI stack is
Python + file-based crypto artifacts (CBCC). SQLite is a single file,
zero-ops, and Python's stdlib talks to it directly — it fits the same
deployment model as the rest of Project-AI. If retrieval-by-traversal
depth becomes a real bottleneck at scale, swap this module for a
Neo4j/Memgraph-backed implementation of the same GraphStore interface —
nothing above this layer (fates.py, pipeline.py) needs to change, because
they only depend on the methods below, not on SQLite specifics.

Constitutional rules enforced HERE, not just documented:
  - Law I (provenance required): create_node rejects missing origin/creator.
  - Fates sovereignty: only fates.py's Clotho/Lachesis/Atropos functions
    should call the *_lifecycle methods below in normal operation. Nothing
    else may directly rewrite lifecycle_state (mirrors CCMA: "No
    intelligence may directly change memory permanence... Only
    constitutional policy may influence how the Fates measure memory.")
    This module does not police WHO calls it (that's an application-layer
    concern — restrict callers of fates.py in your deployment), but it
    keeps lifecycle mutation behind a narrow, auditable method surface
    instead of a generic node update.
  - Protected memory: resolving (archiving/superseding/retiring/forgetting)
    a PROTECTED node requires a valid AuthorityToken with
    protected_override=True. No override, no resolution — SafeHaltError.
"""

from __future__ import annotations

import json
import sqlite3
import time
from collections.abc import Iterable

from .interfaces import AuthorityProvider, AuthorityToken, SafeHaltError
from .models import Edge, LifecycleState, Region, RelationshipType, UniversalNode, validate_payload

_SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes (
    node_id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,
    region TEXT NOT NULL,
    origin TEXT NOT NULL,
    creator TEXT NOT NULL,
    created_at REAL NOT NULL,
    last_accessed REAL NOT NULL,
    last_modified REAL NOT NULL,
    authority_ref TEXT,
    confidence REAL NOT NULL DEFAULT 0.0,
    integrity_hash TEXT,
    constitutional_status TEXT NOT NULL DEFAULT 'unreviewed',
    retrieval_weight REAL NOT NULL DEFAULT 0.0,
    temporal_weight REAL NOT NULL DEFAULT 0.0,
    lifecycle_state TEXT NOT NULL DEFAULT 'born',
    audit_ref TEXT,
    payload TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_nodes_region ON nodes(region);
CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_nodes_lifecycle ON nodes(lifecycle_state);

CREATE TABLE IF NOT EXISTS edges (
    edge_id TEXT PRIMARY KEY,
    src_id TEXT NOT NULL,
    dst_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    created_at REAL NOT NULL,
    weight REAL NOT NULL DEFAULT 1.0,
    provenance_ref TEXT,
    FOREIGN KEY (src_id) REFERENCES nodes(node_id),
    FOREIGN KEY (dst_id) REFERENCES nodes(node_id)
);

CREATE INDEX IF NOT EXISTS idx_edges_src ON edges(src_id);
CREATE INDEX IF NOT EXISTS idx_edges_dst ON edges(dst_id);
CREATE INDEX IF NOT EXISTS idx_edges_type ON edges(relationship_type);

-- Protected node types cannot be resolved (archived/superseded/retired/
-- forgotten) without protected_override authority. This list mirrors
-- CCMA Part III "Protected Memory": constitutional records, identity,
-- partnership history, audit chain, governance decisions, authority
-- grants, human reserved authority, cryptographic provenance.
CREATE TABLE IF NOT EXISTS protected_node_types (
    node_type TEXT PRIMARY KEY
);
"""

_DEFAULT_PROTECTED_TYPES = [
    "governance.authority_memory",
    "governance.decision_memory",
    "governance.sovereignty_memory",
    "triumvirate.codex.constitutional_memory",
    "triumvirate.codex.amendment_memory",
    "triumvirate.codex.judgment_memory",
    "audit.evidence_memory",
    "audit.provenance_memory",
    "audit.cryptographic_memory",
    "audit.chain_of_custody_memory",
    "companion.partnership_memory",
]


class GraphStore:
    def __init__(self, db_path: str = ":memory:"):
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        for t in _DEFAULT_PROTECTED_TYPES:
            self._conn.execute(
                "INSERT OR IGNORE INTO protected_node_types(node_type) VALUES (?)", (t,)
            )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # -- Clotho: creation -----------------------------------------------

    def create_node(self, node: UniversalNode) -> str:
        """
        Law I enforcement point. Rejects nodes without origin/creator.
        This is the ONLY way a node enters the graph — there is no
        "grant authority on create" path, matching CCMA Law II.
        """
        if not node.origin or not node.creator:
            raise SafeHaltError(
                "Law I violation: node missing origin/creator. "
                "Unknown origin is never trusted — refusing to create."
            )
        validate_payload(node.node_type, node.payload)

        self._conn.execute(
            """INSERT INTO nodes
               (node_id, node_type, region, origin, creator, created_at,
                last_accessed, last_modified, authority_ref, confidence,
                integrity_hash, constitutional_status, retrieval_weight,
                temporal_weight, lifecycle_state, audit_ref, payload)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                node.node_id,
                node.node_type,
                node.region.value,
                node.origin,
                node.creator,
                node.created_at,
                node.last_accessed,
                node.last_modified,
                node.authority_ref,
                node.confidence,
                node.integrity_hash,
                node.constitutional_status,
                node.retrieval_weight,
                node.temporal_weight,
                node.lifecycle_state.value,
                node.audit_ref,
                json.dumps(node.payload),
            ),
        )
        self._conn.commit()
        return node.node_id

    def create_edge(self, edge: Edge) -> str:
        # Both endpoints must already exist — no dangling relationships.
        for nid in (edge.src_id, edge.dst_id):
            if self.get_node(nid) is None:
                raise SafeHaltError(f"Cannot create edge: node {nid} does not exist.")
        self._conn.execute(
            """INSERT INTO edges
               (edge_id, src_id, dst_id, relationship_type, created_at, weight, provenance_ref)
               VALUES (?,?,?,?,?,?,?)""",
            (
                edge.edge_id,
                edge.src_id,
                edge.dst_id,
                edge.relationship_type.value,
                edge.created_at,
                edge.weight,
                edge.provenance_ref,
            ),
        )
        self._conn.commit()
        return edge.edge_id

    # -- Reads ------------------------------------------------------------

    def get_node(self, node_id: str) -> UniversalNode | None:
        row = self._conn.execute("SELECT * FROM nodes WHERE node_id = ?", (node_id,)).fetchone()
        if row is None:
            return None
        return self._row_to_node(row)

    def query_by_region(
        self, region: Region, lifecycle_states: Iterable[LifecycleState] | None = None
    ) -> list[UniversalNode]:
        if lifecycle_states is None:
            rows = self._conn.execute(
                "SELECT * FROM nodes WHERE region = ?", (region.value,)
            ).fetchall()
        else:
            states = [s.value for s in lifecycle_states]
            placeholders = ",".join("?" * len(states))
            rows = self._conn.execute(
                f"SELECT * FROM nodes WHERE region = ? AND lifecycle_state IN ({placeholders})",
                (region.value, *states),
            ).fetchall()
        return [self._row_to_node(r) for r in rows]

    def query_by_type(self, node_type_prefix: str) -> list[UniversalNode]:
        rows = self._conn.execute(
            "SELECT * FROM nodes WHERE node_type LIKE ?", (f"{node_type_prefix}%",)
        ).fetchall()
        return [self._row_to_node(r) for r in rows]

    def get_edges(
        self,
        node_id: str,
        relationship_type: RelationshipType | None = None,
        direction: str = "out",
    ) -> list[Edge]:
        col = "src_id" if direction == "out" else "dst_id"
        if relationship_type is None:
            rows = self._conn.execute(f"SELECT * FROM edges WHERE {col} = ?", (node_id,)).fetchall()
        else:
            rows = self._conn.execute(
                f"SELECT * FROM edges WHERE {col} = ? AND relationship_type = ?",
                (node_id, relationship_type.value),
            ).fetchall()
        return [self._row_to_edge(r) for r in rows]

    def relationship_count(self, node_id: str) -> int:
        """Used by Lachesis: relationship density feeds retrieval weight."""
        out_count: int = self._conn.execute(
            "SELECT COUNT(*) FROM edges WHERE src_id = ?", (node_id,)
        ).fetchone()[0]
        in_count: int = self._conn.execute(
            "SELECT COUNT(*) FROM edges WHERE dst_id = ?", (node_id,)
        ).fetchone()[0]
        return out_count + in_count

    # -- Lachesis: reweighing (no authority required — measurement isn't action) --

    def reweigh_node(
        self,
        node_id: str,
        retrieval_weight: float,
        temporal_weight: float,
        confidence: float | None = None,
        allow_strengthen: bool = True,
    ) -> None:
        node = self.get_node(node_id)
        if node is None:
            raise SafeHaltError(f"Cannot reweigh: node {node_id} does not exist.")
        new_confidence = confidence if confidence is not None else node.confidence
        # allow_strengthen=False on a node's first-ever weighing (BORN -> ACTIVE
        # in this same pass) so "strengthened" means "repeatedly referenced,"
        # not "existed and got measured once." Without this guard, any node
        # with a nonzero initial weight would jump straight from born to
        # strengthened on its first Lachesis pass.
        new_lifecycle = (
            LifecycleState.STRENGTHENED.value
            if (
                allow_strengthen
                and retrieval_weight > node.retrieval_weight
                and node.lifecycle_state == LifecycleState.ACTIVE
            )
            else node.lifecycle_state.value
        )
        self._conn.execute(
            """UPDATE nodes SET retrieval_weight=?, temporal_weight=?, confidence=?,
               lifecycle_state=?, last_modified=? WHERE node_id=?""",
            (
                retrieval_weight,
                temporal_weight,
                new_confidence,
                new_lifecycle,
                time.time(),
                node_id,
            ),
        )
        self._conn.commit()

    def mark_active(self, node_id: str) -> None:
        """First Lachesis pass on a BORN node: born -> active."""
        self._conn.execute(
            "UPDATE nodes SET lifecycle_state=?, last_modified=? WHERE node_id=? AND lifecycle_state=?",
            (LifecycleState.ACTIVE.value, time.time(), node_id, LifecycleState.BORN.value),
        )
        self._conn.commit()

    # -- Atropos: resolution (gated by AuthorityProvider) ------------------

    def is_protected(self, node_type: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM protected_node_types WHERE node_type = ?", (node_type,)
        ).fetchone()
        return row is not None

    def add_protected_type(self, node_type: str) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO protected_node_types(node_type) VALUES (?)", (node_type,)
        )
        self._conn.commit()

    def resolve_node(
        self, node_id: str, new_state: LifecycleState, authority: AuthorityProvider, subject: str
    ) -> None:
        """
        Atropos operation. archived/superseded/retired/forgotten all flow
        through here. If the node's type is protected, `authority` must
        return a token with protected_override=True, or this halts.
        """
        if new_state not in (
            LifecycleState.ARCHIVED,
            LifecycleState.SUPERSEDED,
            LifecycleState.RETIRED,
            LifecycleState.FORGOTTEN,
        ):
            raise SafeHaltError(f"resolve_node called with non-terminal state {new_state}.")

        node = self.get_node(node_id)
        if node is None:
            raise SafeHaltError(f"Cannot resolve: node {node_id} does not exist.")

        if self.is_protected(node.node_type) or node.lifecycle_state == LifecycleState.PROTECTED:
            token: AuthorityToken = authority.check_authority(
                subject=subject, scope=f"resolve_protected:{node.node_type}"
            )
            if not token.is_valid() or not token.protected_override:
                raise SafeHaltError(
                    f"Refusing to resolve protected node {node_id} "
                    f"({node.node_type}): no valid protected_override authority."
                )

        self._conn.execute(
            "UPDATE nodes SET lifecycle_state=?, last_modified=? WHERE node_id=?",
            (new_state.value, time.time(), node_id),
        )
        self._conn.commit()

    # -- internal -----------------------------------------------------------

    def _row_to_node(self, row: sqlite3.Row) -> UniversalNode:
        node = UniversalNode(
            node_type=row["node_type"],
            region=Region(row["region"]),
            origin=row["origin"],
            creator=row["creator"],
            node_id=row["node_id"],
            created_at=row["created_at"],
            last_accessed=row["last_accessed"],
            last_modified=row["last_modified"],
            authority_ref=row["authority_ref"],
            confidence=row["confidence"],
            integrity_hash=row["integrity_hash"],
            constitutional_status=row["constitutional_status"],
            retrieval_weight=row["retrieval_weight"],
            temporal_weight=row["temporal_weight"],
            lifecycle_state=LifecycleState(row["lifecycle_state"]),
            audit_ref=row["audit_ref"],
            payload=json.loads(row["payload"]),
        )
        return node

    def _row_to_edge(self, row: sqlite3.Row) -> Edge:
        return Edge(
            src_id=row["src_id"],
            dst_id=row["dst_id"],
            relationship_type=RelationshipType(row["relationship_type"]),
            edge_id=row["edge_id"],
            created_at=row["created_at"],
            weight=row["weight"],
            provenance_ref=row["provenance_ref"],
        )
