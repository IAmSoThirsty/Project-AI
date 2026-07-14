"""
ccma.models

Constitutional Cognitive Memory Architecture — Universal Node/Edge schema.

Wiring principle (per CCMA Part XIII, "The Unified Cognitive Graph"):
There are no separate memories. There is one graph. Companion Memory,
TAAR Memory, Shadow Memory, Audit Memory, etc. are NOT separate tables
or classes — they are `region` + `node_type` values on ONE node schema.

Every "memory domain" in Parts II–XI (Partnership Memory, Trust Memory,  # noqa: RUF002
Threat Memory, Constitutional Memory, ...) maps to a `node_type` string
like "companion.partnership_memory" or "triumvirate.galahad.identity_memory".
You do not need a new table or dataclass per domain. You need a new
node_type string and, if the domain has structured fields, a payload
schema (see PAYLOAD_SCHEMAS below) — validated, not silently accepted.

This module defines:
  - Region: which subsystem "owns" a node (companion, fates, triumvirate.*,
    taar, shadow, vault, nirl, chimera, retrieval, governance, audit,
    working, short_term, long_term)
  - LifecycleState: the Fates' vocabulary (Clotho/Lachesis/Atropos states)
  - UniversalNode: the one node schema (matches CCMA Part XIII exactly)
  - Edge: the one relationship schema
  - RelationshipType: the CCMA Part XIII edge vocabulary
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Region(str, Enum):  # noqa: UP042
    """Which subsystem region a node belongs to. Matches CCMA Parts I–XI."""

    WORKING = "working"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    COMPANION = "companion"
    FATES = "fates"
    TRIUMVIRATE_GALAHAD = "triumvirate.galahad"
    TRIUMVIRATE_CERBERUS = "triumvirate.cerberus"
    TRIUMVIRATE_CODEX = "triumvirate.codex"
    TAAR = "taar"
    SHADOW = "shadow"
    VAULT = "vault"
    NIRL = "nirl"
    CHIMERA = "chimera"
    RETRIEVAL = "retrieval"
    GOVERNANCE = "governance"
    AUDIT = "audit"


class LifecycleState(str, Enum):  # noqa: UP042
    """The Fates' vocabulary (CCMA Part III). Every node has exactly one."""

    BORN = "born"  # Clotho: just created, unweighted
    ACTIVE = "active"  # Lachesis has weighed it, in normal circulation
    STRENGTHENED = "strengthened"  # repeatedly referenced, high retrieval weight
    ARCHIVED = "archived"  # Atropos: preserved but deprioritized
    SUPERSEDED = "superseded"  # Atropos: replaced by a newer node
    RETIRED = "retired"  # Atropos: no longer active, not deleted
    FORGOTTEN = "forgotten"  # Atropos: expired, eligible for physical deletion
    PROTECTED = "protected"  # Atropos may not resolve this without explicit
    # constitutional authority (CCMA "Protected Memory")


class RelationshipType(str, Enum):  # noqa: UP042
    """Edge vocabulary from CCMA Part XIII, 'Universal Relationship Types'."""

    CREATED = "created"
    DEPENDS_ON = "depends_on"
    SUPPORTS = "supports"
    REFUTES = "refutes"
    CLARIFIES = "clarifies"
    REPLACES = "replaces"
    EVOLVES_INTO = "evolves_into"
    SIMULATES = "simulates"
    GOVERNS = "governs"
    AUTHORIZES = "authorizes"
    REQUIRES = "requires"
    REFERENCES = "references"
    CONTINUES = "continues"
    CONTRADICTS = "contradicts"
    MIRRORS = "mirrors"
    PREDICTS = "predicts"
    EXPLAINS = "explains"
    EMERGES_FROM = "emerges_from"


# Node types are deliberately plain strings, not an enum, because CCMA
# defines ~150 memory domains across 14 parts and that list will keep
# growing. An enum would need editing every time you add a domain,
# which defeats the point of the unified graph. Instead: dotted,
# namespaced strings, validated at write time against PAYLOAD_SCHEMAS
# below (if a schema is registered for that type) or accepted as an
# opaque payload (if not — but then it can't claim structured guarantees).
#
# Examples straight out of the CCMA text:
#   "companion.partnership_memory"
#   "companion.trust_memory"
#   "triumvirate.galahad.identity_memory"
#   "triumvirate.cerberus.threat_memory"
#   "taar.trigger_memory"
#   "shadow.alternate_future_memory"
#   "governance.authority_memory"
#   "audit.evidence_memory"
NodeType = str


@dataclass
class UniversalNode:
    """
    The one node schema. Matches CCMA Part XIII 'Universal Node Definition'
    field-for-field:

        UUID, Node Type, Creation Time, Last Access, Last Modification,
        Authority, Confidence, Provenance, Integrity, Relationships,
        Constitutional Status, Retrieval Weight, Temporal Weight,
        Lifecycle State, Audit Reference

    `relationships` is NOT stored here — it lives in the edges table
    (see store.py). Storing edges on the node itself is how graphs turn
    into unmaintainable blobs; keep nodes and edges separate tables.

    `payload` holds whatever domain-specific fields a given node_type
    needs (e.g. companion.trust_memory might carry
    {"trust_trajectory": "increasing", "last_repair_event": "..."}).
    Payload is free-form JSON at the model layer; validate it against
    PAYLOAD_SCHEMAS at the store layer if a schema is registered.
    """

    node_type: NodeType
    region: Region

    # Law I — Nothing Exists Without Provenance. These are required,
    # not optional, and the store layer rejects nodes missing them.
    origin: str  # who/what produced this node
    creator: str  # human id, companion instance id, or subsystem name

    # Identity & time
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    last_modified: float = field(default_factory=time.time)

    # Trust & standing — set by Governance/Triumvirate, never by the node's
    # own creator. Defaults are the deny-by-default floor.
    authority_ref: str | None = None  # pointer to a Governance authority record
    confidence: float = 0.0  # 0.0–1.0, set by Lachesis or explicit review
    integrity_hash: str | None = None  # set by the audit/crypto layer, not by the node
    constitutional_status: str = "unreviewed"  # "unreviewed" | "reviewed" | "protected"

    # Fates fields
    retrieval_weight: float = 0.0
    temporal_weight: float = 0.0
    lifecycle_state: LifecycleState = LifecycleState.BORN

    # Audit pointer — the actual signature/hash chain lives in the audit
    # subsystem (bridge to CBCC), this is just the reference.
    audit_ref: str | None = None

    payload: dict[str, Any] = field(default_factory=dict)

    def touch_accessed(self) -> None:
        self.last_accessed = time.time()


@dataclass
class Edge:
    """The one relationship schema (CCMA Part XIII)."""

    src_id: str
    dst_id: str
    relationship_type: RelationshipType
    edge_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    weight: float = 1.0
    provenance_ref: str | None = None


# ---------------------------------------------------------------------------
# Payload schemas — OPTIONAL structural validation per node_type.
#
# You don't have to register every one of CCMA's ~150 memory domains here
# on day one. Register a schema when you actually start writing nodes of
# that type and want field-level guarantees. Unregistered node_types are
# still storable (payload is just JSON) but get no structural validation —
# treat that as a signal to add a schema, not a permanent state.
# ---------------------------------------------------------------------------

PAYLOAD_SCHEMAS: dict[str, set[str]] = {
    # CCMA Part II — Companion Intelligence Memory (representative subset)
    "companion.partnership_memory": {
        "human_identity",
        "companion_identity",
        "shared_history",
        "trust_evolution",
        "authority_boundaries",
        "reserved_human_authority",
    },
    "companion.agency_preservation_memory": {
        "human_reserved_decisions",
        "human_consent",
        "human_refusals",
        "escalation_requirements",
        "boundary_violations",
    },
    # CCMA Part IV — Triumvirate
    "triumvirate.galahad.legitimacy_memory": {
        "legitimate_interest",
        "constitutional_standing",
        "required_authority",
        "legitimacy_assessment",
    },
    "triumvirate.cerberus.threat_memory": {
        "known_threats",
        "threat_confidence",
        "threat_severity",
    },
    "triumvirate.codex.judgment_memory": {
        "matter",
        "governing_articles",
        "governing_policies",
        "precedents_applied",
        "final_judgment",
        "human_authority",
        "audit_reference",
    },
    # CCMA Part X — Governance
    "governance.authority_memory": {
        "authority_source",
        "authority_scope",
        "expiration",
        "revoked",
    },
    "governance.decision_memory": {
        "matter",
        "decision",
        "authority",
        "evidence",
        "constitutional_basis",
        "conditions",
        "effective_time",
        "expiration",
        "audit_reference",
    },
    # CCMA Part XI — Audit
    "audit.evidence_memory": {
        "source_inputs",
        "source_outputs",
        "tool_results",
        "observations",
    },
    "audit.cryptographic_memory": {
        "sha256",
        "merkle_root",
        "ed25519_signature",
        "rfc3161_timestamp",
    },
}


def validate_payload(node_type: NodeType, payload: dict[str, Any]) -> None:
    """
    If a schema is registered for node_type, every key in payload must be
    a known field for that type. Unregistered node_types pass through
    (no schema = no structural guarantee, by design — see note above).
    """
    schema = PAYLOAD_SCHEMAS.get(node_type)
    if schema is None:
        return
    unknown = set(payload.keys()) - schema
    if unknown:
        raise ValueError(
            f"payload for node_type {node_type!r} has unregistered fields: "
            f"{sorted(unknown)}. Either fix the caller or extend the schema "
            f"in PAYLOAD_SCHEMAS."
        )
