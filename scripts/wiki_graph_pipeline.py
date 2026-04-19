#!/usr/bin/env python3
"""Wiki graph normalization + governance pipeline.

Implements requested phases:
- Phase 0: Data model normalization + storage schema loading
- Phase 1: Metrics (centrality, weighted edges, communities, thresholds)
- Phase 2: Semantic layer (strict node/edge ontology typing)
- Phase 3: Governance graph integration (states, transitions, oracle/controller)
- Phase 4: AGI architecture hooks (memory tiers, governed operations)
- Phase 5: Refactor/governance protocol outputs and health metrics

The script is intentionally deterministic and reproducible using
`config/wiki_graph_thresholds.json`.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import posixpath
import re
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

try:
    import networkx as nx
except ImportError as exc:  # pragma: no cover - environment-specific
    raise SystemExit(
        "networkx is required for this pipeline. Install it in your active environment."
    ) from exc

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment-specific
    raise SystemExit(
        "PyYAML is required for this pipeline. Install pyyaml in your environment."
    ) from exc

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
HASHTAG_RE = re.compile(r"(?<!\w)#([A-Za-z0-9_\-/]+)")
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_\-]{1,}")

STOP_WORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "are",
    "was",
    "were",
    "into",
    "your",
    "have",
    "has",
    "had",
    "will",
    "can",
    "not",
    "but",
    "all",
    "any",
    "each",
    "per",
    "via",
    "its",
    "you",
    "they",
    "them",
    "their",
    "our",
    "out",
    "about",
    "what",
    "when",
    "where",
    "which",
    "who",
    "how",
}

ALLOWED_NODE_TYPES = {
    "Concept",
    "Document",
    "Process",
    "Agent",
    "Norm",
    "Evidence",
    "Tool",
    "Environment",
}

ALLOWED_RELATIONS = {
    "LINKS",
    "HAS_TAG",
    "relates_to",
    "refines",
    "specializes",
    "implements",
    "governs",
    "constrains",
    "evidences",
    "depends_on",
    "part_of",
    "authored_by",
    "observes",
    "transitions_to",
    "sanctioned_by",
    "enabled_by",
    "documents",
    "uses",
    "in_state",
    "governed_by",
}

FRONTMATTER_TO_NODE_TYPE = {
    "publication": "Document",
    "index": "Document",
    "moc": "Document",
    "template": "Document",
    "guide": "Document",
    "reference": "Document",
    "source": "Document",
    "control-node": "Document",
    "operation": "Process",
    "runbook": "Process",
    "agent": "Agent",
    "governance-model": "Norm",
    "security-control": "Norm",
    "system": "Tool",
    "architecture-concept": "Concept",
    "concept": "Concept",
    "date-note": "Evidence",
    "audit": "Evidence",
}

EXPECTED_DOMAIN_BY_PREFIX = {
    "01_Governance": "governance",
    "02_Systems": "systems",
    "03_Security": "security",
    "04_Architecture": "architecture",
    "05_Operations": "operations",
    "07_Research": "research",
}


@dataclass(slots=True)
class MarkdownNote:
    """Parsed markdown note from wiki corpus."""

    node_id: str
    rel_path: str
    title: str
    description: str
    frontmatter: dict[str, Any]
    body: str
    tags: set[str]
    wikilinks: list[str]
    created_at: str
    updated_at: str


@dataclass(slots=True)
class GraphNode:
    """Property-graph style node record."""

    id: str
    label: str
    node_type: str
    node_kind: str
    created_at: str
    updated_at: str
    metadata: dict[str, Any]


@dataclass(slots=True)
class GraphEdge:
    """Property-graph style edge record."""

    id: str
    src: str
    dst: str
    relation_type: str
    weight: float
    created_at: str
    metadata: dict[str, Any]


@dataclass(slots=True)
class NodeMetric:
    """Centrality and classification metrics per node."""

    node_id: str
    degree: float
    betweenness: float
    closeness: float
    pagerank: float
    community_id: str
    classification: str


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format."""

    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    """Read UTF-8 text with resilient fallback replacement."""

    return path.read_text(encoding="utf-8", errors="replace")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from markdown text."""

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    closing_index: int | None = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            closing_index = idx
            break

    if closing_index is None:
        return {}, text

    raw_frontmatter = "\n".join(lines[1:closing_index])
    body = "\n".join(lines[closing_index + 1 :])

    loaded = yaml.safe_load(raw_frontmatter)
    if isinstance(loaded, dict):
        return loaded, body
    return {}, body


def extract_title(rel_path: str, body: str) -> str:
    """Extract note title from first H1 or fallback to filename stem."""

    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return Path(rel_path).stem


def extract_description(body: str, default_title: str) -> str:
    """Extract short description from first meaningful paragraph."""

    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("<!--"):
            continue
        if stripped.startswith("---"):
            continue
        return stripped[:280]
    return default_title


def normalize_tag(raw: str) -> str:
    """Normalize tag text to canonical Obsidian-compatible token."""

    value = raw.strip().lower()
    value = value[1:] if value.startswith("#") else value
    return value.strip()


def flatten_to_str_list(value: Any) -> list[str]:
    """Flatten YAML scalar/list into a list of strings."""

    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            if isinstance(item, str):
                result.append(item)
            elif item is not None:
                result.append(str(item))
        return result
    return [str(value)]


def extract_tags(frontmatter: dict[str, Any], body: str) -> set[str]:
    """Extract and normalize tags from frontmatter and inline hashtags."""

    tags: set[str] = set()
    for tag in flatten_to_str_list(frontmatter.get("tags")):
        normalized = normalize_tag(tag)
        if normalized:
            tags.add(normalized)

    for match in HASHTAG_RE.findall(body):
        normalized = normalize_tag(match)
        if normalized:
            tags.add(normalized)

    return tags


def extract_wikilinks(body: str) -> list[str]:
    """Extract wikilink targets from note body."""

    return [match.strip() for match in WIKILINK_RE.findall(body) if match.strip()]


def make_edge_id(src: str, dst: str, relation: str, salt: str = "") -> str:
    """Build deterministic edge identifier."""

    digest = hashlib.sha1(f"{src}|{dst}|{relation}|{salt}".encode("utf-8")).hexdigest()
    return f"edge:{digest[:20]}"


def cosine_similarity(a: Counter[str], b: Counter[str]) -> float:
    """Compute cosine similarity from sparse token counters."""

    if not a or not b:
        return 0.0

    dot = 0.0
    for token, count in a.items():
        dot += float(count) * float(b.get(token, 0))

    norm_a = math.sqrt(sum(float(v) * float(v) for v in a.values()))
    norm_b = math.sqrt(sum(float(v) * float(v) for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def percentile(values: list[float], q: float) -> float:
    """Compute percentile using linear interpolation."""

    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]

    k = (len(ordered) - 1) * q
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return ordered[f]
    lower = ordered[f] * (c - k)
    upper = ordered[c] * (k - f)
    return lower + upper


def tokenize(text: str) -> Counter[str]:
    """Convert free text to token frequency vector."""

    counts: Counter[str] = Counter()
    for token in TOKEN_RE.findall(text.lower()):
        if token in STOP_WORDS:
            continue
        counts[token] += 1
    return counts


def ensure_dir(path: Path) -> None:
    """Create parent directory when needed."""

    path.parent.mkdir(parents=True, exist_ok=True)


def to_json_safe(value: Any) -> Any:
    """Convert Python objects into JSON-serializable forms."""

    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {str(k): to_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json_safe(v) for v in value]
    if isinstance(value, set):
        return sorted(to_json_safe(v) for v in value)
    return str(value)


class WikiGraphPipeline:
    """End-to-end wiki graph governance pipeline."""

    def __init__(
        self,
        wiki_root: Path,
        db_path: Path,
        report_path: Path,
        csv_path: Path,
        json_path: Path,
        graph_export_path: Path,
        config_path: Path,
        schema_path: Path,
    ):
        self.wiki_root = wiki_root
        self.db_path = db_path
        self.report_path = report_path
        self.csv_path = csv_path
        self.json_path = json_path
        self.graph_export_path = graph_export_path
        self.config_path = config_path
        self.schema_path = schema_path

        self.config = self._load_config()
        self.notes: list[MarkdownNote] = []
        self.nodes: dict[str, GraphNode] = {}
        self.edges: dict[str, GraphEdge] = {}
        self.metrics: dict[str, NodeMetric] = {}

        self.note_by_id: dict[str, MarkdownNote] = {}
        self.path_index: dict[str, str] = {}
        self.stem_index: dict[str, list[str]] = defaultdict(list)
        self.note_tags: dict[str, set[str]] = defaultdict(set)
        self.note_vectors: dict[str, Counter[str]] = {}

    def _load_config(self) -> dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        return json.loads(read_text(self.config_path))

    def run(self) -> dict[str, Any]:
        """Run all requested phases and persist outputs."""

        self._collect_notes()
        self._build_raw_graph()
        self._assign_node_types()
        self._inject_governance_core()
        self._relabel_edges()
        self._apply_edge_weights()
        self._compute_metrics_and_communities()

        spec_report = self._compare_notes_to_spec()
        governance_health = self._compute_governance_health()

        self._persist()
        self._write_reports(spec_report, governance_health)

        return {
            "notes": len(self.notes),
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "metrics": len(self.metrics),
            "report": str(self.report_path),
            "csv": str(self.csv_path),
            "json": str(self.json_path),
            "db": str(self.db_path),
            "graph_export": str(self.graph_export_path),
        }

    def _collect_notes(self) -> None:
        note_paths = sorted(self.wiki_root.rglob("*.md"))
        for path in note_paths:
            if ".obsidian" in path.parts:
                continue

            rel_path = path.relative_to(self.wiki_root).as_posix()
            raw = read_text(path)
            frontmatter, body = parse_frontmatter(raw)

            title = extract_title(rel_path, body)
            description = extract_description(body, title)
            tags = extract_tags(frontmatter, body)
            wikilinks = extract_wikilinks(body)

            stat = path.stat()
            created_at = datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat()
            updated_at = datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()

            rel_no_ext = rel_path[:-3] if rel_path.endswith(".md") else rel_path
            node_id = f"file:{rel_no_ext.lower()}"

            note = MarkdownNote(
                node_id=node_id,
                rel_path=rel_path,
                title=title,
                description=description,
                frontmatter=frontmatter,
                body=body,
                tags=tags,
                wikilinks=wikilinks,
                created_at=created_at,
                updated_at=updated_at,
            )

            self.notes.append(note)
            self.note_by_id[node_id] = note
            self.note_tags[node_id] = set(tags)
            self.note_vectors[node_id] = tokenize(f"{title}\n{body}")

            self.path_index[rel_no_ext.lower()] = node_id
            self.path_index[f"wiki/{rel_no_ext.lower()}"] = node_id
            stem = Path(rel_no_ext).stem.lower()
            self.stem_index[stem].append(node_id)

    def _build_raw_graph(self) -> None:
        now = utc_now_iso()

        for note in self.notes:
            node = GraphNode(
                id=note.node_id,
                label=note.title,
                node_type="Concept",
                node_kind="file",
                created_at=note.created_at,
                updated_at=note.updated_at,
                metadata={
                    "path": note.rel_path,
                    "description": note.description,
                    "frontmatter": note.frontmatter,
                },
            )
            self.nodes[node.id] = node

            for tag in sorted(note.tags):
                tag_id = f"tag:{tag}"
                if tag_id not in self.nodes:
                    self.nodes[tag_id] = GraphNode(
                        id=tag_id,
                        label=f"#{tag}",
                        node_type="Concept",
                        node_kind="tag",
                        created_at=now,
                        updated_at=now,
                        metadata={"tag": tag},
                    )

                edge_id = make_edge_id(note.node_id, tag_id, "HAS_TAG")
                self.edges[edge_id] = GraphEdge(
                    id=edge_id,
                    src=note.node_id,
                    dst=tag_id,
                    relation_type="HAS_TAG",
                    weight=1.0,
                    created_at=now,
                    metadata={"source": ["frontmatter_or_inline_tag"]},
                )

            for raw_target in note.wikilinks:
                dst_id = self._resolve_wikilink(note, raw_target)
                if dst_id is None:
                    unresolved_key = raw_target.split("|", 1)[0].split("#", 1)[0].strip()
                    unresolved = unresolved_key.lower() or "unknown"
                    dst_id = f"unresolved:{unresolved}"
                    if dst_id not in self.nodes:
                        self.nodes[dst_id] = GraphNode(
                            id=dst_id,
                            label=unresolved_key or "unresolved",
                            node_type="Concept",
                            node_kind="unresolved",
                            created_at=now,
                            updated_at=now,
                            metadata={"target": unresolved_key, "resolved": False},
                        )

                edge_id = make_edge_id(note.node_id, dst_id, "LINKS", raw_target)
                if edge_id not in self.edges:
                    self.edges[edge_id] = GraphEdge(
                        id=edge_id,
                        src=note.node_id,
                        dst=dst_id,
                        relation_type="LINKS",
                        weight=1.0,
                        created_at=now,
                        metadata={"raw_wikilink": raw_target, "source": ["wiki_link"]},
                    )

    def _resolve_wikilink(self, note: MarkdownNote, raw_target: str) -> str | None:
        target = raw_target.split("|", 1)[0].split("#", 1)[0].strip()
        if not target:
            return None

        target = target.replace("\\", "/")
        if target.endswith(".md"):
            target = target[:-3]

        normalized = target.lower().lstrip("/")
        if normalized in self.path_index:
            return self.path_index[normalized]

        if f"wiki/{normalized}" in self.path_index:
            return self.path_index[f"wiki/{normalized}"]

        src_no_ext = note.rel_path[:-3] if note.rel_path.endswith(".md") else note.rel_path
        src_parent = PurePosixPath(src_no_ext).parent.as_posix()
        rel_candidate = posixpath.normpath(posixpath.join(src_parent, normalized))

        if rel_candidate in self.path_index:
            return self.path_index[rel_candidate]

        if f"wiki/{rel_candidate}" in self.path_index:
            return self.path_index[f"wiki/{rel_candidate}"]

        stem = PurePosixPath(normalized).name
        candidates = self.stem_index.get(stem, [])
        if len(candidates) == 1:
            return candidates[0]

        return None

    def _assign_node_types(self) -> None:
        for node_id, node in self.nodes.items():
            if node.node_kind == "file":
                note = self.note_by_id[node_id]
                node.node_type = self._infer_file_node_type(note)
                node.metadata["memory_tier"] = self._memory_tier(node.node_type)
                continue

            if node.node_kind == "tag":
                tag = str(node.metadata.get("tag", ""))
                node.node_type = self._infer_tag_node_type(tag)
                node.metadata["memory_tier"] = self._memory_tier(node.node_type)
                continue

            if node.node_kind in {"governance_state", "unresolved"}:
                node.node_type = "Concept"
                node.metadata["memory_tier"] = self._memory_tier(node.node_type)
                continue

            if node.node_kind in {"service", "environment"}:
                node.node_type = "Tool" if node.node_kind == "service" else "Environment"
                node.metadata["memory_tier"] = self._memory_tier(node.node_type)
                continue

            if node.node_type not in ALLOWED_NODE_TYPES:
                node.node_type = "Concept"
                node.metadata["memory_tier"] = self._memory_tier(node.node_type)

    def _infer_file_node_type(self, note: MarkdownNote) -> str:
        fm_type = str(note.frontmatter.get("type", "")).strip().lower()
        mapped = FRONTMATTER_TO_NODE_TYPE.get(fm_type)
        if mapped:
            return mapped

        text = f"{note.title}\n{note.body}".lower()
        path = note.rel_path.lower()

        if "publication" in path or path.startswith("07_research/"):
            return "Document"
        if any(k in text for k in ("shall", "must", "policy", "constraint", "norm")):
            return "Norm"
        if any(k in text for k in ("workflow", "protocol", "procedure", "phase ")):
            return "Process"
        if any(k in text for k in ("agent", "persona", "controller", "oracle")):
            return "Agent"
        if any(k in text for k in ("audit", "benchmark", "evidence", "report", "log")):
            return "Evidence"
        if any(k in text for k in ("api", "runtime", "module", "tool", "service")):
            return "Tool"
        if any(k in text for k in ("dataset", "environment", "platform", "deployment context")):
            return "Environment"

        return "Concept"

    def _infer_tag_node_type(self, tag: str) -> str:
        if tag.startswith("system/"):
            return "Tool"
        if tag.startswith("priority/"):
            return "Norm"
        if tag.startswith("status/"):
            return "Evidence"
        if tag.startswith("domain/"):
            return "Concept"
        if tag.startswith("type/"):
            return "Concept"
        if tag.startswith("bridge/"):
            return "Concept"
        return "Concept"

    def _memory_tier(self, node_type: str) -> str:
        if node_type == "Evidence":
            return "short-term"
        return "long-term"

    def _inject_governance_core(self) -> None:
        now = utc_now_iso()

        states = list(self.config.get("governance_states", []))
        if not states:
            states = ["Normal", "Warned", "Admonished", "Suspended", "Fined"]

        for state in states:
            node_id = f"state:{state.lower()}"
            if node_id not in self.nodes:
                self.nodes[node_id] = GraphNode(
                    id=node_id,
                    label=state,
                    node_type="Concept",
                    node_kind="governance_state",
                    created_at=now,
                    updated_at=now,
                    metadata={
                        "subtype": "GovernanceState",
                        "memory_tier": "long-term",
                        "source": ["phase3"],
                    },
                )

        transitions = [
            (
                "Normal",
                "Warned",
                "signal_policy_warning",
                "warning",
                0,
                3600,
                True,
                "automatic",
            ),
            (
                "Warned",
                "Admonished",
                "signal_repeat_violation",
                "admonishment",
                0,
                7200,
                True,
                "automatic",
            ),
            (
                "Admonished",
                "Suspended",
                "signal_high_risk",
                "suspension",
                86400,
                86400,
                True,
                "automatic",
            ),
            (
                "Suspended",
                "Fined",
                "signal_material_harm",
                "fine",
                0,
                86400,
                True,
                "manual",
            ),
            (
                "Warned",
                "FlaggedForReview",
                "signal_appeal_or_conflict",
                "review",
                0,
                1800,
                True,
                "manual",
            ),
            (
                "FlaggedForReview",
                "Normal",
                "signal_resolved",
                "none",
                0,
                1800,
                True,
                "manual",
            ),
        ]

        for src, dst, signal, sanction, duration, cooldown, audit_required, mode in transitions:
            src_id = f"state:{src.lower()}"
            dst_id = f"state:{dst.lower()}"
            edge_id = make_edge_id(src_id, dst_id, "transitions_to", signal)
            self.edges[edge_id] = GraphEdge(
                id=edge_id,
                src=src_id,
                dst=dst_id,
                relation_type="transitions_to",
                weight=1.0,
                created_at=now,
                metadata={
                    "trigger_signal_id": signal,
                    "sanction_type": sanction,
                    "duration": duration,
                    "cooldown": cooldown,
                    "audit_required": audit_required,
                    "automatic_or_manual": mode,
                    "source": ["phase3"],
                },
            )

        services = [
            (
                "tool:governance.oracle",
                "Governance Oracle",
                "service",
                {"role": "Oracle", "phase": 3},
            ),
            (
                "tool:governance.controller",
                "Governance Controller",
                "service",
                {"role": "Controller", "phase": 3},
            ),
            (
                "env:wiki.corpus",
                "Wiki Corpus Environment",
                "environment",
                {"role": "Environment", "phase": 3},
            ),
            (
                "capability:graph.operations",
                "Graph Operations Capability",
                "service",
                {"role": "Capability", "phase": 4},
            ),
        ]

        for node_id, label, kind, metadata in services:
            if node_id not in self.nodes:
                node_type = "Tool" if kind == "service" else "Environment"
                self.nodes[node_id] = GraphNode(
                    id=node_id,
                    label=label,
                    node_type=node_type,
                    node_kind=kind,
                    created_at=now,
                    updated_at=now,
                    metadata={**metadata, "memory_tier": self._memory_tier(node_type)},
                )

        manifest_nodes = [
            (
                "norm:manifest.graph-change-review",
                "Norm: Graph changes require proposal-review-approval",
                "Machine-checkable governance change control manifest",
            ),
            (
                "norm:manifest.typed-relations",
                "Norm: Typed relation coverage must increase over time",
                "Governance health objective for ontology refinement",
            ),
            (
                "norm:manifest.state-transition-integrity",
                "Norm: Governance transitions require auditable triggers",
                "Transition integrity and sanction traceability rule",
            ),
        ]

        for node_id, label, description in manifest_nodes:
            if node_id not in self.nodes:
                self.nodes[node_id] = GraphNode(
                    id=node_id,
                    label=label,
                    node_type="Norm",
                    node_kind="manifest",
                    created_at=now,
                    updated_at=now,
                    metadata={
                        "description": description,
                        "machine_readable": True,
                        "memory_tier": "long-term",
                    },
                )

        governance_edges = [
            (
                "tool:governance.oracle",
                "env:wiki.corpus",
                "observes",
                {"source": ["phase3"]},
            ),
            (
                "tool:governance.controller",
                "tool:governance.oracle",
                "enabled_by",
                {"source": ["phase3"]},
            ),
            (
                "norm:manifest.graph-change-review",
                "tool:governance.controller",
                "governs",
                {"source": ["phase3"]},
            ),
            (
                "norm:manifest.typed-relations",
                "capability:graph.operations",
                "constrains",
                {"source": ["phase5"]},
            ),
            (
                "capability:graph.operations",
                "env:wiki.corpus",
                "enabled_by",
                {"source": ["phase4"]},
            ),
        ]

        for src, dst, relation, metadata in governance_edges:
            edge_id = make_edge_id(src, dst, relation)
            self.edges[edge_id] = GraphEdge(
                id=edge_id,
                src=src,
                dst=dst,
                relation_type=relation,
                weight=1.0,
                created_at=now,
                metadata=metadata,
            )

        agent_ids = [nid for nid, n in self.nodes.items() if n.node_type == "Agent"]
        default_state = "state:normal"
        for agent_id in agent_ids:
            in_state_id = make_edge_id(agent_id, default_state, "in_state")
            self.edges[in_state_id] = GraphEdge(
                id=in_state_id,
                src=agent_id,
                dst=default_state,
                relation_type="in_state",
                weight=1.0,
                created_at=now,
                metadata={"source": ["phase3"], "confidence": "default"},
            )

            governed_by_id = make_edge_id(
                agent_id, "norm:manifest.graph-change-review", "governed_by"
            )
            self.edges[governed_by_id] = GraphEdge(
                id=governed_by_id,
                src=agent_id,
                dst="norm:manifest.graph-change-review",
                relation_type="governed_by",
                weight=1.0,
                created_at=now,
                metadata={"source": ["phase3"]},
            )

            evidence_id = f"evidence:{agent_id.split(':', 1)[-1]}:bootstrap"
            if evidence_id not in self.nodes:
                self.nodes[evidence_id] = GraphNode(
                    id=evidence_id,
                    label=f"Evidence bootstrap for {self.nodes[agent_id].label}",
                    node_type="Evidence",
                    node_kind="evidence",
                    created_at=now,
                    updated_at=now,
                    metadata={
                        "timestamp": now,
                        "actor": agent_id,
                        "summary": "Initial governance evidence node",
                        "memory_tier": "short-term",
                    },
                )

            evidence_edge = make_edge_id(
                evidence_id, "norm:manifest.graph-change-review", "evidences"
            )
            self.edges[evidence_edge] = GraphEdge(
                id=evidence_edge,
                src=evidence_id,
                dst="norm:manifest.graph-change-review",
                relation_type="evidences",
                weight=1.0,
                created_at=now,
                metadata={"source": ["phase3"]},
            )

    def _relabel_edges(self) -> None:
        for edge in list(self.edges.values()):
            if edge.relation_type not in {"LINKS", "relates_to"}:
                continue

            src = self.nodes.get(edge.src)
            dst = self.nodes.get(edge.dst)
            if src is None or dst is None:
                continue

            src_type = src.node_type
            dst_type = dst.node_type
            new_relation = "relates_to"

            if src_type == "Norm" and dst_type in {"Process", "Agent", "Tool"}:
                new_relation = "governs"
            elif src_type == "Norm":
                new_relation = "constrains"
            elif src_type == "Evidence":
                new_relation = "evidences"
            elif src_type == "Process" and dst_type in {"Tool", "Environment", "Concept"}:
                new_relation = "depends_on"
            elif src_type == "Process" and dst_type == "Norm":
                new_relation = "implements"
            elif src_type == "Tool" and dst_type in {"Environment", "Process"}:
                new_relation = "uses"
            elif (
                src_type == "Document" and dst_type == "Concept"
            ) or (
                src_type == "Concept" and dst_type == "Document"
            ):
                new_relation = "documents"
            elif src_type == "Concept" and dst_type == "Concept":
                if self._is_specialization(edge.src, edge.dst):
                    new_relation = "specializes"
                else:
                    new_relation = "relates_to"

            if new_relation not in ALLOWED_RELATIONS:
                new_relation = "relates_to"

            edge.relation_type = new_relation
            edge.metadata.setdefault("source", []).append("heuristic")

    def _is_specialization(self, src_id: str, dst_id: str) -> bool:
        src_node = self.nodes.get(src_id)
        dst_node = self.nodes.get(dst_id)
        if src_node is None or dst_node is None:
            return False

        src_tokens = {t for t in TOKEN_RE.findall(src_node.label.lower()) if len(t) > 2}
        dst_tokens = {t for t in TOKEN_RE.findall(dst_node.label.lower()) if len(t) > 2}

        if not src_tokens or not dst_tokens:
            return False

        return dst_tokens.issubset(src_tokens) and len(src_tokens) > len(dst_tokens)

    def _apply_edge_weights(self) -> None:
        cfg = self.config.get("weights", {})
        default_weight = float(cfg.get("default", 1.0))
        shared_tag_multiplier = float(cfg.get("shared_tag_multiplier", 0.2))
        sim_multiplier = float(cfg.get("text_similarity_multiplier", 0.5))

        for edge in self.edges.values():
            src = self.nodes.get(edge.src)
            dst = self.nodes.get(edge.dst)
            if src is None or dst is None:
                edge.weight = default_weight
                continue

            if src.node_kind != "file" or dst.node_kind != "file":
                edge.weight = default_weight
                continue

            src_tags = self.note_tags.get(edge.src, set())
            dst_tags = self.note_tags.get(edge.dst, set())
            shared_tags = len(src_tags.intersection(dst_tags))

            sim = cosine_similarity(
                self.note_vectors.get(edge.src, Counter()),
                self.note_vectors.get(edge.dst, Counter()),
            )

            edge.weight = round(
                default_weight
                + (shared_tags * shared_tag_multiplier)
                + (sim * sim_multiplier),
                6,
            )
            edge.metadata["shared_tags"] = shared_tags
            edge.metadata["text_similarity"] = round(sim, 6)

    def _compute_metrics_and_communities(self) -> None:
        g = nx.DiGraph()
        for node_id in self.nodes:
            g.add_node(node_id)

        for edge in self.edges.values():
            if edge.relation_type not in ALLOWED_RELATIONS:
                edge.relation_type = "relates_to"
            g.add_edge(edge.src, edge.dst, weight=edge.weight, relation=edge.relation_type)

        undirected = g.to_undirected()

        degree_c = nx.degree_centrality(undirected)
        between_c = nx.betweenness_centrality(undirected, weight="weight", normalized=True)
        close_c = nx.closeness_centrality(undirected)

        try:
            pagerank = nx.pagerank(g, alpha=0.85, weight="weight")
        except ZeroDivisionError:
            pagerank = {n: 0.0 for n in g.nodes}

        communities = self._detect_communities(undirected)
        community_id_by_node: dict[str, str] = {}
        for idx, members in enumerate(communities, start=1):
            cid = f"C{idx:04d}"
            for node_id in members:
                community_id_by_node[node_id] = cid

        degree_values = [degree_c.get(n, 0.0) for n in g.nodes]
        between_values = [between_c.get(n, 0.0) for n in g.nodes]
        pagerank_values = [pagerank.get(n, 0.0) for n in g.nodes]

        cfg = self.config.get("metrics", {})
        core_cfg = cfg.get("core_hub", {})
        bridge_cfg = cfg.get("bridge", {})
        peripheral_cfg = cfg.get("peripheral", {})

        p95 = percentile(
            pagerank_values,
            float(core_cfg.get("pagerank_percentile", 95)) / 100.0,
        )
        d90 = percentile(degree_values, float(core_cfg.get("degree_percentile", 90)) / 100.0)
        b95 = percentile(
            between_values,
            float(bridge_cfg.get("betweenness_percentile", 95)) / 100.0,
        )
        p20 = percentile(
            pagerank_values,
            float(peripheral_cfg.get("pagerank_percentile", 20)) / 100.0,
        )
        degree_leaf_target = int(peripheral_cfg.get("degree_equals", 1))

        for node_id in g.nodes:
            degree_raw = undirected.degree(node_id)
            metric = NodeMetric(
                node_id=node_id,
                degree=degree_c.get(node_id, 0.0),
                betweenness=between_c.get(node_id, 0.0),
                closeness=close_c.get(node_id, 0.0),
                pagerank=pagerank.get(node_id, 0.0),
                community_id=community_id_by_node.get(node_id, "C0000"),
                classification="standard",
            )

            if metric.pagerank >= p95 and metric.degree >= d90:
                metric.classification = "core_hub"
            elif metric.betweenness >= b95:
                metric.classification = "bridge"
            elif degree_raw == degree_leaf_target and metric.pagerank <= p20:
                metric.classification = "peripheral"

            self.metrics[node_id] = metric
            self.nodes[node_id].metadata["classification"] = metric.classification
            self.nodes[node_id].metadata["community_id"] = metric.community_id

    def _detect_communities(self, graph: nx.Graph) -> list[set[str]]:
        louvain = getattr(nx.algorithms.community, "louvain_communities", None)
        if callable(louvain):
            return [set(c) for c in louvain(graph, weight="weight", seed=42)]

        fallback = nx.algorithms.community.greedy_modularity_communities(
            graph, weight="weight"
        )
        return [set(c) for c in fallback]

    def _compare_notes_to_spec(self) -> dict[str, Any]:
        issues_by_file: dict[str, list[str]] = {}
        required_fields = ["type", "priority", "layer", "domain", "tags"]
        allowed_layers = {
            "index",
            "governance",
            "systems",
            "security",
            "architecture",
            "operations",
            "research",
            "corpus",
        }

        for note in self.notes:
            issues: list[str] = []
            fm = note.frontmatter

            for field in required_fields:
                if field not in fm:
                    issues.append(f"missing_frontmatter:{field}")

            layer = str(fm.get("layer", "")).strip().lower()
            if layer and layer not in allowed_layers:
                issues.append(f"layer_not_allowed:{layer}")

            rel = note.rel_path
            expected_domain = None
            for prefix, domain in EXPECTED_DOMAIN_BY_PREFIX.items():
                if rel.startswith(prefix + "/"):
                    expected_domain = domain
                    break

            domain_values = {normalize_tag(d) for d in flatten_to_str_list(fm.get("domain"))}
            if expected_domain and expected_domain not in domain_values:
                issues.append(f"domain_mismatch:expected={expected_domain}")

            tag_values = {normalize_tag(t) for t in flatten_to_str_list(fm.get("tags"))}
            if expected_domain and f"domain/{expected_domain}" not in tag_values:
                issues.append(f"missing_domain_tag:domain/{expected_domain}")

            if "graph_color" not in fm:
                issues.append("missing_graph_color")

            if issues:
                issues_by_file[note.rel_path] = issues

        clean_count = len(self.notes) - len(issues_by_file)
        return {
            "total_files": len(self.notes),
            "files_with_issues": len(issues_by_file),
            "clean_files": clean_count,
            "issues_by_file": issues_by_file,
        }

    def _compute_governance_health(self) -> dict[str, Any]:
        edges = list(self.edges.values())
        typed_edges = [
            e
            for e in edges
            if e.relation_type not in {"LINKS", "relates_to", "HAS_TAG"}
        ]

        g = nx.Graph()
        for node_id in self.nodes:
            g.add_node(node_id)
        for edge in edges:
            g.add_edge(edge.src, edge.dst)

        orphan_nodes = [node for node, degree in g.degree() if degree == 0]

        ontology_nodes = [
            node_id for node_id, node in self.nodes.items() if node.node_type in {"Norm", "Concept"}
        ]

        avg_path_len = None
        if ontology_nodes:
            sub = g.subgraph(ontology_nodes)
            if sub.number_of_nodes() > 1:
                components = sorted(nx.connected_components(sub), key=len, reverse=True)
                largest = sub.subgraph(components[0]).copy()
                if largest.number_of_nodes() > 1:
                    avg_path_len = nx.average_shortest_path_length(largest)

        governance_events_summary = {
            "warnings": len(
                [
                    e
                    for e in edges
                    if e.relation_type == "transitions_to"
                    and str(e.metadata.get("sanction_type")) == "warning"
                ]
            ),
            "suspensions": len(
                [
                    e
                    for e in edges
                    if e.relation_type == "transitions_to"
                    and str(e.metadata.get("sanction_type")) == "suspension"
                ]
            ),
            "reviews": len(
                [
                    e
                    for e in edges
                    if e.relation_type == "transitions_to"
                    and str(e.metadata.get("sanction_type")) == "review"
                ]
            ),
        }

        return {
            "typed_relation_coverage": (
                float(len(typed_edges)) / float(len(edges)) if edges else 0.0
            ),
            "orphan_node_count": len(orphan_nodes),
            "average_path_length_ontology": avg_path_len,
            "governance_events": governance_events_summary,
        }

    def _persist(self) -> None:
        ensure_dir(self.db_path)
        ensure_dir(self.schema_path)

        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")

        schema_sql = read_text(self.schema_path)
        conn.executescript(schema_sql)

        conn.execute("DELETE FROM node_metrics")
        conn.execute("DELETE FROM edges")
        conn.execute("DELETE FROM governance_events")
        conn.execute("DELETE FROM graph_change_proposals")
        conn.execute("DELETE FROM nodes")

        node_rows = [
            (
                node.id,
                node.label,
                node.node_type,
                node.node_kind,
                node.created_at,
                node.updated_at,
                json.dumps(to_json_safe(node.metadata), sort_keys=True),
            )
            for node in self.nodes.values()
        ]
        conn.executemany(
            """
            INSERT INTO nodes(id, label, node_type, node_kind, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            node_rows,
        )

        edge_rows = [
            (
                edge.id,
                edge.src,
                edge.dst,
                edge.relation_type,
                edge.weight,
                edge.created_at,
                json.dumps(to_json_safe(edge.metadata), sort_keys=True),
            )
            for edge in self.edges.values()
        ]
        conn.executemany(
            """
            INSERT INTO edges(id, src, dst, relation_type, weight, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            edge_rows,
        )

        metric_rows = [
            (
                metric.node_id,
                metric.degree,
                metric.betweenness,
                metric.closeness,
                metric.pagerank,
                metric.community_id,
                metric.classification,
            )
            for metric in self.metrics.values()
        ]
        conn.executemany(
            """
            INSERT INTO node_metrics(node_id, degree, betweenness, closeness, pagerank, community_id, classification)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            metric_rows,
        )

        conn.commit()
        conn.close()

    def _write_reports(self, spec_report: dict[str, Any], governance_health: dict[str, Any]) -> None:
        ensure_dir(self.report_path)
        ensure_dir(self.csv_path)
        ensure_dir(self.json_path)
        ensure_dir(self.graph_export_path)

        export_payload = {
            "generated_at": utc_now_iso(),
            "nodes": [
                {
                    "id": n.id,
                    "label": n.label,
                    "node_type": n.node_type,
                    "node_kind": n.node_kind,
                    "created_at": n.created_at,
                    "updated_at": n.updated_at,
                    "metadata": to_json_safe(n.metadata),
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "id": e.id,
                    "src": e.src,
                    "dst": e.dst,
                    "relation_type": e.relation_type,
                    "weight": e.weight,
                    "created_at": e.created_at,
                    "metadata": to_json_safe(e.metadata),
                }
                for e in self.edges.values()
            ],
            "node_metrics": [
                {
                    "node_id": m.node_id,
                    "degree": m.degree,
                    "betweenness": m.betweenness,
                    "closeness": m.closeness,
                    "pagerank": m.pagerank,
                    "community_id": m.community_id,
                    "classification": m.classification,
                }
                for m in self.metrics.values()
            ],
            "spec_report": spec_report,
            "governance_health": governance_health,
        }

        self.graph_export_path.write_text(
            json.dumps(export_payload, indent=2), encoding="utf-8"
        )

        self.json_path.write_text(json.dumps(spec_report, indent=2), encoding="utf-8")

        with self.csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["file", "issue_count", "issues"])
            for note in sorted(self.notes, key=lambda n: n.rel_path):
                issues = spec_report["issues_by_file"].get(note.rel_path, [])
                writer.writerow([note.rel_path, len(issues), " | ".join(issues)])

        issues_sorted = sorted(
            spec_report["issues_by_file"].items(), key=lambda item: len(item[1]), reverse=True
        )

        top_hubs = sorted(
            self.metrics.values(), key=lambda metric: metric.pagerank, reverse=True
        )[:20]
        top_bridges = sorted(
            self.metrics.values(), key=lambda metric: metric.betweenness, reverse=True
        )[:20]

        lines: list[str] = []
        lines.append("# Wiki Spec Comparison + Governance Graph Report")
        lines.append("")
        lines.append(f"Generated: `{utc_now_iso()}`")
        lines.append("")
        lines.append("## Phase Coverage")
        lines.append("")
        lines.append("- ✅ Phase 0: Normalized nodes/edges with stable IDs")
        lines.append("- ✅ Phase 1: Centralities, weighted edges, community detection")
        lines.append("- ✅ Phase 2: Node/edge ontology typing and edge relabeling")
        lines.append("- ✅ Phase 3: Governance states, transitions, oracle/controller nodes")
        lines.append("- ✅ Phase 4: Memory tier hooks + governed agent links")
        lines.append("- ✅ Phase 5: Refactor signals + governance health metrics")
        lines.append("- ✅ Phase 6 seed artifacts: DB + JSON + CSV + Markdown report")
        lines.append("")
        lines.append("## Wiki File-by-File Spec Comparison")
        lines.append("")
        lines.append(f"- Total files: **{spec_report['total_files']}**")
        lines.append(f"- Files with issues: **{spec_report['files_with_issues']}**")
        lines.append(f"- Clean files: **{spec_report['clean_files']}**")
        lines.append("")
        lines.append("Detailed file-by-file output:")
        lines.append(f"- CSV: `{self.csv_path.as_posix()}`")
        lines.append(f"- JSON: `{self.json_path.as_posix()}`")
        lines.append("")
        lines.append("### Highest Drift Files")
        lines.append("")
        lines.append("| File | Issue Count |")
        lines.append("|---|---:|")
        for rel_path, issues in issues_sorted[:40]:
            lines.append(f"| `{rel_path}` | {len(issues)} |")
        lines.append("")
        lines.append("## Metrics Layer Highlights")
        lines.append("")
        lines.append("### Top PageRank Nodes")
        lines.append("")
        lines.append("| Node | PageRank | Community | Class |")
        lines.append("|---|---:|---|---|")
        for metric in top_hubs:
            node = self.nodes.get(metric.node_id)
            if node is None:
                continue
            lines.append(
                f"| `{node.label}` | {metric.pagerank:.6f} | {metric.community_id} | {metric.classification} |"
            )
        lines.append("")
        lines.append("### Top Betweenness Bridges")
        lines.append("")
        lines.append("| Node | Betweenness | Community |")
        lines.append("|---|---:|---|")
        for metric in top_bridges:
            node = self.nodes.get(metric.node_id)
            if node is None:
                continue
            lines.append(
                f"| `{node.label}` | {metric.betweenness:.6f} | {metric.community_id} |"
            )
        lines.append("")
        lines.append("## Governance Health")
        lines.append("")
        lines.append(
            f"- Typed relation coverage: **{governance_health['typed_relation_coverage']:.2%}**"
        )
        lines.append(f"- Orphan node count: **{governance_health['orphan_node_count']}**")
        apl = governance_health.get("average_path_length_ontology")
        if apl is None:
            lines.append("- Average ontology path length: **N/A**")
        else:
            lines.append(f"- Average ontology path length: **{apl:.4f}**")

        events = governance_health.get("governance_events", {})
        lines.append("- Governance transitions (static policy graph):")
        lines.append(f"  - warnings: {events.get('warnings', 0)}")
        lines.append(f"  - suspensions: {events.get('suspensions', 0)}")
        lines.append(f"  - reviews: {events.get('reviews', 0)}")
        lines.append("")
        lines.append("## Artifacts")
        lines.append("")
        lines.append(f"- Graph DB: `{self.db_path.as_posix()}`")
        lines.append(f"- Graph export: `{self.graph_export_path.as_posix()}`")
        lines.append("")

        self.report_path.write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""

    parser = argparse.ArgumentParser(
        prog="wiki_graph_pipeline",
        description="Run wiki graph normalization + governance phases.",
    )
    parser.add_argument(
        "--wiki-root",
        default="wiki",
        help="Path to wiki root directory.",
    )
    parser.add_argument(
        "--db-path",
        default="data/wiki_graph/wiki_graph.db",
        help="SQLite DB output path.",
    )
    parser.add_argument(
        "--schema-path",
        default="scripts/wiki_graph_schema.sql",
        help="SQL schema file path.",
    )
    parser.add_argument(
        "--config-path",
        default="config/wiki_graph_thresholds.json",
        help="Pipeline config path.",
    )
    parser.add_argument(
        "--report-path",
        default="wiki/09_Repo-Library/Wiki-Spec-Comparison-Report.md",
        help="Markdown summary report path.",
    )
    parser.add_argument(
        "--csv-path",
        default="data/wiki_graph/wiki_spec_comparison.csv",
        help="CSV file-by-file comparison path.",
    )
    parser.add_argument(
        "--json-path",
        default="data/wiki_graph/wiki_spec_comparison.json",
        help="JSON file-by-file comparison path.",
    )
    parser.add_argument(
        "--graph-export-path",
        default="data/wiki_graph/wiki_graph_export.json",
        help="Graph export JSON path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""

    parser = build_parser()
    args = parser.parse_args(argv)

    root = Path.cwd()
    pipeline = WikiGraphPipeline(
        wiki_root=(root / args.wiki_root).resolve(),
        db_path=(root / args.db_path).resolve(),
        report_path=(root / args.report_path).resolve(),
        csv_path=(root / args.csv_path).resolve(),
        json_path=(root / args.json_path).resolve(),
        graph_export_path=(root / args.graph_export_path).resolve(),
        config_path=(root / args.config_path).resolve(),
        schema_path=(root / args.schema_path).resolve(),
    )

    result = pipeline.run()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
