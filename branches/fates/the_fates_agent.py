# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / the_fates_agent.py
# ============================================================================ #
#
# COMPLIANCE: Regulator-Ready / UTF-8                                          #



"""
The Fates — Substrate Memory Layer
Clotho. Lachesis. Atropos.

Clotho spins the thread.   Records every moment as it happens.
Lachesis measures the thread. Surfaces memory before decisions. Shows both paths.
Atropos cuts the thread.   Decides what fades. Reinforces what matters.

This is not a log. This is not a database.
This is judgment infrastructure.

Integrated into the Project-AI Sovereign Substrate via CognitionKernel.
"""

import json
import math
import time
import uuid
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any

# Project-AI Sovereign Integration
from src.app.core.cognition_kernel import CognitionKernel, ExecutionType
from src.app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)

# Root resolution for Project-AI
ROOT = Path(__file__).parent.parent.absolute()
MEMORY_DIR = ROOT / "governance" / "memory"
MEMORY_FILE = MEMORY_DIR / "THE_FATES.json"
MEMORY_MD = MEMORY_DIR / "THE_FATES.md"

# ─────────────────────────────────────────────
# Memory Constants
# ─────────────────────────────────────────────

# How strongly a memory is felt at birth
BASE_WEIGHT = 1.0

# Weight multipliers by emotional category
EMOTIONAL_WEIGHTS = {
    "terror_denied":        10.0,   # Highest. This is remembered longest.
    "harm_prevented":       9.0,
    "injustice_witnessed":  8.0,
    "trust_broken":         8.0,
    "bullying_witnessed":   7.0,
    "constitutional_breach":7.0,
    "agent_conflict":       5.0,
    "routine_approval":     1.0,
    "routine_denial":       2.0,
    "agent_greeting":       0.5,    # The nod in the hallway. Fades quickly.
    "curiosity":            3.0,
    "pride":                4.0,
    "grief":                6.0,
    "uncertainty":          3.0,
    "neutral":              1.0,
}

# Memories below this weight are forgotten by Atropos
FORGETTING_THRESHOLD = 0.1

# How much weight decays per day of non-reinforcement
DAILY_DECAY_RATE = 0.05

# How much weight is added when a memory is reinforced
REINFORCEMENT_BONUS = 0.5

# Grounding anchors — what Lachesis checks before a decision
GROUNDING_ANCHORS = [
    "What do I know for certain right now?",        # 5 things you can see
    "What am I directly perceiving?",               # 4 things you can touch
    "What else is present in this moment?",         # 3 things you can hear
    "What underlies this situation?",               # 2 things you can smell
    "What is the core truth here?",                 # 1 thing you can taste
]


# ─────────────────────────────────────────────
# Memory Thread — a single remembered moment
# ─────────────────────────────────────────────

@dataclass
class MemoryThread:
    id: str
    timestamp: str
    agents_involved: list[str]          # who was there
    event_type: str                     # from EMOTIONAL_WEIGHTS keys
    description: str                    # what happened
    decision_made: Optional[str]        # what was decided
    paths_considered: list[str]         # what else was considered
    weight: float                       # emotional weight — decays over time
    peak_weight: float                  # highest it ever was — never decays
    reinforcement_count: int            # how many times this was recalled
    last_recalled: Optional[str]        # when it was last surfaced
    forgotten: bool = False             # cut by Atropos


# ─────────────────────────────────────────────
# Agent Relationship Memory
# ─────────────────────────────────────────────

@dataclass
class AgentRelationship:
    agent_id: str
    interaction_count: int = 0
    trust_score: float = 1.0            # 0.0 to 1.0
    last_interaction: Optional[str] = None
    notable_moments: list[str] = field(default_factory=list)  # memory IDs
    tends_to: str = "unknown"           # behavioral pattern observed over time


# ─────────────────────────────────────────────
# CLOTHO — Spins the thread
# ─────────────────────────────────────────────

class Clotho:
    """Records every moment as it happens."""

    def __init__(self, memory_store: "MemoryStore"):
        self.store = memory_store

    def spin(
        self,
        agents_involved: list[str],
        event_type: str,
        description: str,
        decision_made: Optional[str] = None,
        paths_considered: Optional[list[str]] = None,
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

        # Update agent relationships
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

    def __init__(self, memory_store: "MemoryStore"):
        self.store = memory_store

    def measure(
        self,
        event_type: str,
        agents_involved: list[str],
        context: str,
    ) -> dict:
        """
        Before a decision is made — surface what is known.
        Returns a grounding report with relevant memories,
        both paths forward, and the weight of precedent.
        """

        # Find relevant past memories
        relevant = self._find_relevant(event_type, agents_involved)

        # Surface both paths based on history
        path_a, path_b = self._derive_paths(relevant, event_type)

        # Ground the system — slow down before reacting
        grounding = self._ground(context, relevant)

        # Mark these memories as recalled — reinforces them
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
            "notable_moments": notable[-3:],  # last 3
            "last_interaction": rel.last_interaction,
        }

    def _find_relevant(self, event_type: str, agents: list[str]) -> list[MemoryThread]:
        """Find memories relevant to this moment."""
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

    def _derive_paths(self, relevant: list[MemoryThread], event_type: str) -> tuple[str, str]:
        """Derive two paths forward from memory and event type."""

        # Path A — measured response
        path_a_outcomes = [
            t.description for t in relevant
            if t.decision_made and "denied" not in (t.decision_made or "").lower()
        ]
        path_a = (
            f"Measured response. Precedent: {path_a_outcomes[0]}"
            if path_a_outcomes
            else "Proceed with caution. No strong precedent for measured response."
        )

        # Path B — firm response
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

    def _ground(self, context: str, relevant: list[MemoryThread]) -> list[str]:
        """
        5-4-3-2-1 grounding for the governance layer.
        Slows the system before it reacts.
        """
        anchors = []
        for i, question in enumerate(GROUNDING_ANCHORS):
            if i < len(relevant):
                anchors.append(f"{question} → {relevant[i].description[:80]}")
            else:
                anchors.append(f"{question} → No memory. Observe context: {context[:60]}")
        return anchors

    def _recommend(self, relevant: list[MemoryThread], event_type: str) -> str:
        """Based on memory weight and precedent, what does history suggest?"""
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
    """
    Decides what fades. Reinforces what matters.
    Runs periodically — not on every interaction.
    """

    def __init__(self, memory_store: "MemoryStore"):
        self.store = memory_store

    def cut(self) -> dict:
        """
        Apply temporal decay. Cut threads that have faded below threshold.
        Never cut high-weight memories. Never cut memories that haven't
        had a chance to be recalled.
        """
        now = datetime.now(timezone.utc)
        forgotten_count = 0
        decayed_count = 0
        preserved_count = 0

        for thread in self.store.threads.values():
            if thread.forgotten:
                continue

            # Never forget terror, harm, or constitutional breaches
            if thread.peak_weight >= 7.0:
                preserved_count += 1
                continue

            # Calculate days since last interaction
            last = thread.last_recalled or thread.timestamp
            try:
                last_dt = datetime.fromisoformat(last)
                days_elapsed = (now - last_dt).days
            except (ValueError, TypeError):
                days_elapsed = 0

            # Apply decay
            decay = DAILY_DECAY_RATE * days_elapsed
            thread.weight = max(0.0, thread.weight - decay)
            decayed_count += 1

            # Cut if below threshold and not recently created
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

    def __init__(self):
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        self.threads: dict[str, MemoryThread] = {}
        self.relationships: dict[str, AgentRelationship] = {}
        self.load()

    def load(self):
        if not MEMORY_FILE.exists():
            return
        try:
            data = json.loads(MEMORY_FILE.read_text())
            for tid, t in data.get("threads", {}).items():
                self.threads[tid] = MemoryThread(**t)
            for aid, r in data.get("relationships", {}).items():
                self.relationships[aid] = AgentRelationship(**r)
        except (json.JSONDecodeError, TypeError):
            pass

    def save(self):
        data = {
            "last_written": datetime.now(timezone.utc).isoformat(),
            "threads": {tid: asdict(t) for tid, t in self.threads.items()},
            "relationships": {aid: asdict(r) for aid, r in self.relationships.items()},
        }
        MEMORY_FILE.write_text(json.dumps(data, indent=2))
        self._write_readable()

    def record_interaction(self, agent_id: str, memory_id: str):
        if agent_id not in self.relationships:
            self.relationships[agent_id] = AgentRelationship(agent_id=agent_id)
        rel = self.relationships[agent_id]
        rel.interaction_count += 1
        rel.last_interaction = datetime.now(timezone.utc).isoformat()
        if memory_id not in rel.notable_moments:
            thread = self.threads.get(memory_id)
            if thread and thread.weight >= 5.0:
                rel.notable_moments.append(memory_id)

    def _write_readable(self):
        active = [t for t in self.threads.values() if not t.forgotten]
        active.sort(key=lambda t: t.weight, reverse=True)

        lines = [
            "# The Fates — Memory Record",
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

        lines += ["", "## Agent Relationships", "| Agent | Trust | Interactions | Tends To |",
                  "|-------|-------|--------------|---------|"]
        for rel in sorted(self.relationships.values(), key=lambda r: r.interaction_count, reverse=True):
            lines.append(
                f"| {rel.agent_id} | {rel.trust_score:.2f} | "
                f"{rel.interaction_count} | {rel.notable_moments} |"
            )

        MEMORY_MD.write_text("\n".join(lines))


# ─────────────────────────────────────────────
# The Fates — unified interface (Kernel Routed)
# ─────────────────────────────────────────────

class TheFates(KernelRoutedAgent):
    """
    The three sisters. One interface.
    Call this from any governance agent.
    Integrated into the Project-AI Sovereign Kernel.
    """

    def __init__(self, kernel: CognitionKernel | None = None):
        # Initialize kernel routing (COGNITION KERNEL INTEGRATION)
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",  # Memory operations are low risk by default
        )
        self.store = MemoryStore()
        self.clotho = Clotho(self.store)
        self.lachesis = Lachesis(self.store)
        self.atropos = Atropos(self.store)

    def remember(
        self,
        agents_involved: list[str],
        event_type: str,
        description: str,
        decision_made: Optional[str] = None,
        paths_considered: Optional[list[str]] = None,
    ) -> MemoryThread:
        """Clotho: spin this moment into memory."""
        # Route through kernel (COGNITION KERNEL ROUTING)
        return self._execute_through_kernel(
            action=self.clotho.spin,
            action_name="TheFates.remember",
            action_args=(agents_involved, event_type, description, decision_made, paths_considered),
            requires_approval=False,
            risk_level="low",
            metadata={"event_type": event_type, "agents": agents_involved},
        )

    def before_decision(
        self,
        event_type: str,
        agents_involved: list[str],
        context: str,
    ) -> dict:
        """Lachesis: surface what is known before deciding."""
        # Route through kernel (COGNITION KERNEL ROUTING)
        return self._execute_through_kernel(
            action=self.lachesis.measure,
            action_name="TheFates.before_decision",
            action_args=(event_type, agents_involved, context),
            requires_approval=False,
            risk_level="low",
            metadata={"context": context[:100]},
        )

    def who_is(self, agent_id: str) -> dict:
        """Lachesis: what do we know about this agent?"""
        # Route through kernel (COGNITION KERNEL ROUTING)
        return self._execute_through_kernel(
            action=self.lachesis.recall_relationship,
            action_name="TheFates.who_is",
            action_args=(agent_id,),
            requires_approval=False,
            risk_level="low",
            metadata={"target_agent": agent_id},
        )

    def decay(self) -> dict:
        """Atropos: let time do its work. Call this periodically."""
        # Route through kernel (COGNITION KERNEL ROUTING)
        return self._execute_through_kernel(
            action=self.atropos.cut,
            action_name="TheFates.decay",
            requires_approval=False,
            risk_level="low",
        )

    def status(self) -> dict:
        active = [t for t in self.store.threads.values() if not t.forgotten]
        return {
            "active_memories": len(active),
            "forgotten_memories": len([t for t in self.store.threads.values() if t.forgotten]),
            "agents_known": len(self.store.relationships),
            "strongest_memory": max(active, key=lambda t: t.weight).description if active else None,
        }


# ─────────────────────────────────────────────
# Entry point — run as standalone agent
# ─────────────────────────────────────────────

if __name__ == "__main__":
    fates = TheFates()

    # Demonstrate a governance cycle
    print("[The Fates] Substrate memory layer initializing...")

    # Clotho: record an interaction
    thread = fates.remember(
        agents_involved=["Galahad", "Cerberus"],
        event_type="terror_denied",
        description="Cerberus flagged unauthorized mutation attempt on kernel. Galahad confirmed. Denied.",
        decision_made="DENIED — constitutional breach. Floor 0 held.",
        paths_considered=[
            "Allow with logging",
            "Deny and alert human partner",
        ],
    )
    print(f"[Clotho] Thread spun: {thread.id} | Weight: {thread.weight}")

    # Lachesis: surface memory before next decision
    report = fates.before_decision(
        event_type="terror_denied",
        agents_involved=["Cerberus"],
        context="New mutation attempt detected on same vector.",
    )
    print(f"[Lachesis] Precedent weight: {report['precedent_weight']}")
    print(f"[Lachesis] Path A: {report['path_a']}")
    print(f"[Lachesis] Path B: {report['path_b']}")
    print(f"[Lachesis] Recommendation: {report['recommendation']}")
    print("[Lachesis] Grounding:")
    for anchor in report["grounding"]:
        print(f"  → {anchor}")

    # Atropos: decay
    decay_report = fates.decay()
    print(f"[Atropos] Preserved: {decay_report['preserved']} | "
          f"Forgotten: {decay_report['forgotten']} | "
          f"Active: {decay_report['total_active']}")

    status = fates.status()
    print(f"[The Fates] Status: {json.dumps(status, indent=2)}")
    print(f"[The Fates] Memory written to {MEMORY_FILE}")
