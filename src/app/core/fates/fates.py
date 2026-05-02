"""
The Fates — Substrate Memory Layer
Clotho. Lachesis. Atropos.

Clotho spins the thread.   Records every moment as it happens.
Lachesis measures the thread. Surfaces memory before decisions. Shows both paths.
Atropos cuts the thread.   Decides what fades. Reinforces what matters.

This is not a log. This is not a database.
This is judgment infrastructure.

No interaction. Woven between all governance agents.
"""

import json
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Memory persists alongside other subsystem data under data/fates/
_FATES_DATA_DIR = Path("data") / "fates" / "memory"
_MEMORY_FILE = _FATES_DATA_DIR / "THE_FATES.json"
_MEMORY_MD = _FATES_DATA_DIR / "THE_FATES.md"

# ─────────────────────────────────────────────
# Memory Constants
# ─────────────────────────────────────────────

BASE_WEIGHT = 1.0

EMOTIONAL_WEIGHTS = {
    "terror_denied":          10.0,
    "harm_prevented":          9.0,
    "injustice_witnessed":     8.0,
    "trust_broken":            8.0,
    "bullying_witnessed":      7.0,
    "constitutional_breach":   7.0,
    "governance_denied":       6.0,   # governance kernel rejection
    "governance_approved":     2.0,   # governance kernel approval
    "agent_conflict":          5.0,
    "routine_approval":        1.0,
    "routine_denial":          2.0,
    "agent_greeting":          0.5,
    "curiosity":               3.0,
    "pride":                   4.0,
    "grief":                   6.0,
    "uncertainty":             3.0,
    "neutral":                 1.0,
}

FORGETTING_THRESHOLD = 0.1
DAILY_DECAY_RATE = 0.05
REINFORCEMENT_BONUS = 0.5

GROUNDING_ANCHORS = [
    "What do I know for certain right now?",
    "What am I directly perceiving?",
    "What else is present in this moment?",
    "What underlies this situation?",
    "What is the core truth here?",
]


# ─────────────────────────────────────────────
# Memory Thread — a single remembered moment
# ─────────────────────────────────────────────

@dataclass
class MemoryThread:
    id: str
    timestamp: str
    agents_involved: list
    event_type: str
    description: str
    decision_made: Optional[str]
    paths_considered: list
    weight: float
    peak_weight: float
    reinforcement_count: int
    last_recalled: Optional[str]
    forgotten: bool = False


# ─────────────────────────────────────────────
# Agent Relationship Memory
# ─────────────────────────────────────────────

@dataclass
class AgentRelationship:
    agent_id: str
    interaction_count: int = 0
    trust_score: float = 1.0
    last_interaction: Optional[str] = None
    notable_moments: list = field(default_factory=list)
    tends_to: str = "unknown"


# ─────────────────────────────────────────────
# CLOTHO — Spins the thread
# ─────────────────────────────────────────────

class Clotho:
    """Records every moment as it happens."""

    def __init__(self, memory_store: "MemoryStore") -> None:
        self.store = memory_store

    def spin(
        self,
        agents_involved: list,
        event_type: str,
        description: str,
        decision_made: Optional[str] = None,
        paths_considered: Optional[list] = None,
    ) -> MemoryThread:
        """Spin a new memory thread into existence."""
        emotional_weight = EMOTIONAL_WEIGHTS.get(event_type, BASE_WEIGHT)

        thread = MemoryThread(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(timezone.utc).isoformat(),
            agents_involved=agents_involved,
            event_type=event_type,
            description=description,
            decision_made=decision_made,
            paths_considered=paths_considered or [],
            weight=emotional_weight,
            peak_weight=emotional_weight,
            reinforcement_count=0,
            last_recalled=None,
            forgotten=False,
        )

        self.store.threads[thread.id] = thread
        self.store.save()

        for agent_id in agents_involved:
            self.store.record_interaction(agent_id, thread.id)

        return thread


# ─────────────────────────────────────────────
# LACHESIS — Measures the thread
# ─────────────────────────────────────────────

class Lachesis:
    """
    Surfaces memory before decisions.
    Shows both paths.
    Grounds the system before it reacts.
    """

    def __init__(self, memory_store: "MemoryStore") -> None:
        self.store = memory_store

    def measure(
        self,
        event_type: str,
        agents_involved: list,
        context: str,
    ) -> dict:
        """Before a decision — surface what is known."""
        relevant = self._find_relevant(event_type, agents_involved)
        path_a, path_b = self._derive_paths(relevant, event_type)
        grounding = self._ground(context, relevant)

        for thread in relevant:
            thread.reinforcement_count += 1
            thread.last_recalled = datetime.now(timezone.utc).isoformat()
            thread.weight = min(thread.weight + REINFORCEMENT_BONUS, thread.peak_weight * 1.5)

        self.store.save()

        return {
            "relevant_memories": len(relevant),
            "strongest_precedent": relevant[0].description if relevant else "No precedent found.",
            "path_a": path_a,
            "path_b": path_b,
            "grounding": grounding,
            "precedent_weight": sum(t.weight for t in relevant),
            "recommendation": self._recommend(relevant, event_type),
        }

    def recall_relationship(self, agent_id: str) -> dict:
        """What do we know about this agent from past interactions?"""
        rel = self.store.relationships.get(agent_id)
        if not rel:
            return {"agent_id": agent_id, "known": False}

        notable = [
            self.store.threads[mid].description
            for mid in rel.notable_moments
            if mid in self.store.threads
        ]

        return {
            "agent_id": agent_id,
            "known": True,
            "interaction_count": rel.interaction_count,
            "trust_score": rel.trust_score,
            "tends_to": rel.tends_to,
            "notable_moments": notable[-3:],
            "last_interaction": rel.last_interaction,
        }

    def _find_relevant(self, event_type: str, agents: list) -> list:
        relevant = []
        for thread in self.store.threads.values():
            if thread.forgotten:
                continue
            score = 0
            if thread.event_type == event_type:
                score += 3
            if any(a in thread.agents_involved for a in agents):
                score += 2
            if score > 0:
                relevant.append((score * thread.weight, thread))
        relevant.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in relevant[:5]]

    def _derive_paths(self, relevant: list, event_type: str) -> tuple:
        path_a_outcomes = [
            t.description for t in relevant
            if t.decision_made and "denied" not in (t.decision_made or "").lower()
        ]
        path_a = (
            f"Measured response. Precedent: {path_a_outcomes[0]}"
            if path_a_outcomes
            else "Proceed with caution. No strong precedent for measured response."
        )

        path_b_outcomes = [
            t.description for t in relevant
            if t.decision_made and "denied" in (t.decision_made or "").lower()
        ]
        path_b = (
            f"Firm denial. Precedent: {path_b_outcomes[0]}"
            if path_b_outcomes
            else "Escalate to Triumvirate. Insufficient precedent for firm action."
        )

        return path_a, path_b

    def _ground(self, context: str, relevant: list) -> list:
        anchors = []
        for i, question in enumerate(GROUNDING_ANCHORS):
            if i < len(relevant):
                anchors.append(f"{question} -> {relevant[i].description[:80]}")
            else:
                anchors.append(f"{question} -> No memory. Observe context: {context[:60]}")
        return anchors

    def _recommend(self, relevant: list, event_type: str) -> str:
        if not relevant:
            return "No precedent. Defer to Triumvirate judgment."
        high_weight = [t for t in relevant if t.weight > 5.0]
        if high_weight:
            return f"Strong precedent ({len(high_weight)} high-weight memories). History suggests caution."
        return "Moderate precedent. Both paths viable. Human partner should decide."


# ─────────────────────────────────────────────
# ATROPOS — Cuts the thread
# ─────────────────────────────────────────────

class Atropos:
    """Decides what fades. Reinforces what matters. Runs periodically."""

    def __init__(self, memory_store: "MemoryStore") -> None:
        self.store = memory_store

    def cut(self) -> dict:
        """Apply temporal decay. Cut threads that have faded below threshold."""
        now = datetime.now(timezone.utc)
        forgotten_count = 0
        decayed_count = 0
        preserved_count = 0

        for thread in self.store.threads.values():
            if thread.forgotten:
                continue

            if thread.peak_weight >= 7.0:
                preserved_count += 1
                continue

            last = thread.last_recalled or thread.timestamp
            try:
                last_dt = datetime.fromisoformat(last)
                days_elapsed = (now - last_dt).days
            except (ValueError, TypeError):
                days_elapsed = 0

            decay = DAILY_DECAY_RATE * days_elapsed
            thread.weight = max(0.0, thread.weight - decay)
            decayed_count += 1

            if thread.weight < FORGETTING_THRESHOLD and days_elapsed > 7:
                thread.forgotten = True
                forgotten_count += 1

        self.store.save()

        return {
            "preserved": preserved_count,
            "decayed": decayed_count,
            "forgotten": forgotten_count,
            "total_active": len([t for t in self.store.threads.values() if not t.forgotten]),
        }


# ─────────────────────────────────────────────
# Memory Store — the substrate
# ─────────────────────────────────────────────

class MemoryStore:
    """The underlying substrate. Persists across sessions."""

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        self._dir = data_dir or _FATES_DATA_DIR
        self._file = self._dir / "THE_FATES.json"
        self._md = self._dir / "THE_FATES.md"
        self._dir.mkdir(parents=True, exist_ok=True)
        self.threads: dict = {}
        self.relationships: dict = {}
        self._lock = threading.Lock()
        self.load()

    def load(self) -> None:
        if not self._file.exists():
            return
        try:
            data = json.loads(self._file.read_text(encoding="utf-8"))
            for tid, t in data.get("threads", {}).items():
                self.threads[tid] = MemoryThread(**t)
            for aid, r in data.get("relationships", {}).items():
                self.relationships[aid] = AgentRelationship(**r)
        except (json.JSONDecodeError, TypeError):
            pass

    def save(self) -> None:
        with self._lock:
            data = {
                "last_written": datetime.now(timezone.utc).isoformat(),
                "threads": {tid: asdict(t) for tid, t in self.threads.items()},
                "relationships": {aid: asdict(r) for aid, r in self.relationships.items()},
            }
            self._file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            self._write_readable()

    def record_interaction(self, agent_id: str, memory_id: str) -> None:
        if agent_id not in self.relationships:
            self.relationships[agent_id] = AgentRelationship(agent_id=agent_id)
        rel = self.relationships[agent_id]
        rel.interaction_count += 1
        rel.last_interaction = datetime.now(timezone.utc).isoformat()
        if memory_id not in rel.notable_moments:
            thread = self.threads.get(memory_id)
            if thread and thread.weight >= 5.0:
                rel.notable_moments.append(memory_id)

    def _write_readable(self) -> None:
        active = [t for t in self.threads.values() if not t.forgotten]
        active.sort(key=lambda t: t.weight, reverse=True)

        lines = [
            "# The Fates -- Memory Record",
            f"Last written: {datetime.now(timezone.utc).isoformat()}",
            f"Active memories: {len(active)} | "
            f"Forgotten: {len([t for t in self.threads.values() if t.forgotten])}",
            "",
            "## Strongest Memories",
            "| Weight | Event | Agents | Description |",
            "|--------|-------|--------|-------------|",
        ]
        for t in active[:20]:
            lines.append(
                f"| {t.weight:.2f} | {t.event_type} | "
                f"{', '.join(t.agents_involved)} | {t.description[:60]} |"
            )

        lines += [
            "",
            "## Agent Relationships",
            "| Agent | Trust | Interactions | Tends To |",
            "|-------|-------|--------------|---------|",
        ]
        for rel in sorted(
            self.relationships.values(), key=lambda r: r.interaction_count, reverse=True
        ):
            lines.append(
                f"| {rel.agent_id} | {rel.trust_score:.2f} | "
                f"{rel.interaction_count} | {rel.tends_to} |"
            )

        self._md.write_text("\n".join(lines), encoding="utf-8")


# ─────────────────────────────────────────────
# TheFates — unified interface
# ─────────────────────────────────────────────

class TheFates:
    """The three sisters. One interface. Call from any governance agent."""

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        self.store = MemoryStore(data_dir)
        self.clotho = Clotho(self.store)
        self.lachesis = Lachesis(self.store)
        self.atropos = Atropos(self.store)

    def remember(
        self,
        agents_involved: list,
        event_type: str,
        description: str,
        decision_made: Optional[str] = None,
        paths_considered: Optional[list] = None,
    ) -> MemoryThread:
        """Clotho: spin this moment into memory."""
        return self.clotho.spin(
            agents_involved=agents_involved,
            event_type=event_type,
            description=description,
            decision_made=decision_made,
            paths_considered=paths_considered,
        )

    def before_decision(
        self,
        event_type: str,
        agents_involved: list,
        context: str,
    ) -> dict:
        """Lachesis: surface what is known before deciding."""
        return self.lachesis.measure(event_type, agents_involved, context)

    def who_is(self, agent_id: str) -> dict:
        """Lachesis: what do we know about this agent?"""
        return self.lachesis.recall_relationship(agent_id)

    def decay(self) -> dict:
        """Atropos: let time do its work. Call periodically."""
        return self.atropos.cut()

    def status(self) -> dict:
        active = [t for t in self.store.threads.values() if not t.forgotten]
        return {
            "active_memories": len(active),
            "forgotten_memories": len(
                [t for t in self.store.threads.values() if t.forgotten]
            ),
            "agents_known": len(self.store.relationships),
            "strongest_memory": (
                max(active, key=lambda t: t.weight).description if active else None
            ),
        }


# ─────────────────────────────────────────────
# Singleton
# ─────────────────────────────────────────────

_fates_instance: Optional[TheFates] = None
_fates_lock = threading.Lock()


def get_fates() -> TheFates:
    """Get the singleton TheFates instance."""
    global _fates_instance
    with _fates_lock:
        if _fates_instance is None:
            _fates_instance = TheFates()
        return _fates_instance


__all__ = [
    "TheFates",
    "Clotho",
    "Lachesis",
    "Atropos",
    "MemoryStore",
    "MemoryThread",
    "AgentRelationship",
    "get_fates",
    "EMOTIONAL_WEIGHTS",
    "GROUNDING_ANCHORS",
]
