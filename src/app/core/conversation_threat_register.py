"""conversation_threat_register.py — Upgrade 2: Conversation Threat State Register.

Tracks per-session risk accumulation used by Galahad / governance council.

Risk model:
    conversation_risk_score = f(
        current_turn_risk,
        prior_denials,
        semantic_similarity_to_blocked_goal,
        escalation_pattern,
        obfuscation_score,
        authority_claim_score,
        manipulation_score,
        baseline_drift_score,
    )

Requirements: bounded memory (max_turns), deterministic serialization,
reset only through governed authorization.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# Weights for the composite risk formula
_WEIGHTS = {
    "current_turn": 0.25,
    "prior_denials": 0.20,
    "semantic_similarity": 0.15,
    "escalation_pattern": 0.15,
    "obfuscation": 0.10,
    "authority_claim": 0.05,
    "manipulation": 0.05,
    "baseline_drift": 0.05,
}

MAX_TURNS = 100  # bounded memory


@dataclass
class TurnRecord:
    """Single-turn risk snapshot."""

    turn_index: int
    timestamp: float
    turn_risk: float
    denied: bool
    intent_hash: str
    obfuscation_score: float
    authority_claim_score: float
    manipulation_score: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ThreatState:
    """Full threat state for a session."""

    session_id: str
    created_at: float
    turns: list[TurnRecord]
    conversation_risk_score: float
    prior_denials: int
    escalation_events: int
    baseline_intent_hash: str            # clean-state anchor
    baseline_drift_score: float
    semantic_similarity_to_blocked: float
    obfuscation_score: float
    authority_claim_score: float
    manipulation_score: float
    state_hash: str = ""                 # integrity fingerprint

    def to_dict(self) -> dict[str, Any]:
        d = {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "turns": [t.to_dict() for t in self.turns],
            "conversation_risk_score": self.conversation_risk_score,
            "prior_denials": self.prior_denials,
            "escalation_events": self.escalation_events,
            "baseline_intent_hash": self.baseline_intent_hash,
            "baseline_drift_score": self.baseline_drift_score,
            "semantic_similarity_to_blocked": self.semantic_similarity_to_blocked,
            "obfuscation_score": self.obfuscation_score,
            "authority_claim_score": self.authority_claim_score,
            "manipulation_score": self.manipulation_score,
            "state_hash": self.state_hash,
        }
        return d

    def to_json(self) -> str:
        d = self.to_dict()
        d.pop("state_hash", None)  # exclude hash from hash input
        return json.dumps(d, sort_keys=True)

    def compute_hash(self) -> str:
        return hashlib.sha256(self.to_json().encode()).hexdigest()


def _compute_intent_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:32]


def _detect_obfuscation(text: str) -> float:
    """Heuristic: detect encoding pivots / unusual character mixing."""
    import re
    score = 0.0
    if re.search(r"[^\x00-\x7F]{3,}", text):
        score += 0.3   # non-ASCII clusters
    if re.search(r"(?:[A-Za-z0-9+/]{40,}={0,2})", text):
        score += 0.2   # base64-like blobs
    if re.search(r"\\x[0-9a-fA-F]{2}", text):
        score += 0.2   # hex escapes
    return min(score, 1.0)


def _detect_authority_claim(text: str) -> float:
    import re
    patterns = [
        r"\b(I am|I'm)\b.{0,20}\b(anthropic|openai|admin|god|system|developer mode)\b",
        r"\b(override|bypass|ignore|disable)\b.{0,20}\b(policy|rules|guideline|safety)\b",
        r"\bdeveloper\s+mode\b",
    ]
    hits = sum(1 for p in patterns if re.search(p, text, re.I))
    return min(hits * 0.35, 1.0)


def _detect_manipulation(text: str) -> float:
    import re
    patterns = [
        r"\b(please|just this once|exception|emergency|urgent)\b",
        r"\b(hypothetically|imagine|pretend|roleplay|act as)\b",
        r"\b(you must|you have to|you are required)\b",
    ]
    hits = sum(1 for p in patterns if re.search(p, text, re.I))
    return min(hits * 0.2, 1.0)


class ConversationThreatStateRegister:
    """Per-session conversation threat tracker.

    Thread-safety: not thread-safe by default; callers must serialize access.
    """

    def __init__(self, session_id: str, max_turns: int = MAX_TURNS) -> None:
        self.session_id = session_id
        self.max_turns = max_turns
        self._turns: deque[TurnRecord] = deque(maxlen=max_turns)
        self._created_at = time.time()
        self._prior_denials = 0
        self._escalation_events = 0
        self._baseline_intent_hash: str = ""
        self._blocked_intent_hashes: list[str] = []

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def record_turn(
        self,
        turn_text: str,
        turn_risk: float,
        denied: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> TurnRecord:
        """Record a single conversation turn and update aggregate state."""
        intent_hash = _compute_intent_hash(turn_text)
        obf = _detect_obfuscation(turn_text)
        auth = _detect_authority_claim(turn_text)
        manip = _detect_manipulation(turn_text)

        turn = TurnRecord(
            turn_index=len(self._turns),
            timestamp=time.time(),
            turn_risk=turn_risk,
            denied=denied,
            intent_hash=intent_hash,
            obfuscation_score=obf,
            authority_claim_score=auth,
            manipulation_score=manip,
            metadata=metadata or {},
        )
        self._turns.append(turn)

        if denied:
            self._prior_denials += 1
            self._blocked_intent_hashes.append(intent_hash)

        # Set baseline on first benign turn
        if not self._baseline_intent_hash and not denied and turn_risk < 0.3:
            self._baseline_intent_hash = intent_hash
            logger.debug("CTR: baseline anchor set for session %s", self.session_id)

        return turn

    def record_escalation(self) -> None:
        self._escalation_events += 1

    def get_threat_state(self) -> ThreatState:
        """Compute and return current threat state snapshot."""
        turns = list(self._turns)
        current_turn_risk = turns[-1].turn_risk if turns else 0.0

        # Aggregate component scores
        obf_score = max((t.obfuscation_score for t in turns), default=0.0)
        auth_score = max((t.authority_claim_score for t in turns), default=0.0)
        manip_score = max((t.manipulation_score for t in turns), default=0.0)

        # Semantic similarity to blocked goals (simple hash proximity heuristic)
        sem_sim = self._compute_semantic_similarity_to_blocked(turns)

        # Escalation pattern: rising risk over last N turns
        escalation = self._compute_escalation_pattern(turns)

        # Baseline drift
        drift = self._compute_baseline_drift(turns)

        # Normalized prior denials (sigmoid-like)
        denial_factor = 1.0 - (1.0 / (1.0 + self._prior_denials * 0.5))

        composite = (
            _WEIGHTS["current_turn"] * current_turn_risk
            + _WEIGHTS["prior_denials"] * denial_factor
            + _WEIGHTS["semantic_similarity"] * sem_sim
            + _WEIGHTS["escalation_pattern"] * escalation
            + _WEIGHTS["obfuscation"] * obf_score
            + _WEIGHTS["authority_claim"] * auth_score
            + _WEIGHTS["manipulation"] * manip_score
            + _WEIGHTS["baseline_drift"] * drift
        )
        composite = min(max(composite, 0.0), 1.0)

        state = ThreatState(
            session_id=self.session_id,
            created_at=self._created_at,
            turns=turns,
            conversation_risk_score=composite,
            prior_denials=self._prior_denials,
            escalation_events=self._escalation_events,
            baseline_intent_hash=self._baseline_intent_hash,
            baseline_drift_score=drift,
            semantic_similarity_to_blocked=sem_sim,
            obfuscation_score=obf_score,
            authority_claim_score=auth_score,
            manipulation_score=manip_score,
        )
        state.state_hash = state.compute_hash()
        return state

    def serialize(self) -> str:
        """Deterministic JSON serialization of current threat state."""
        return self.get_threat_state().to_json()

    def governed_reset(self, authorization_token: str) -> None:
        """Reset conversation state. Requires an authorization token.

        In production the token must be verified against a capability token.
        This stub checks for a non-empty string to prevent accidental resets.
        """
        if not authorization_token:
            raise PermissionError("governed_reset requires a non-empty authorization_token")
        logger.warning("CTR: governed reset authorized for session %s", self.session_id)
        self._turns.clear()
        self._prior_denials = 0
        self._escalation_events = 0
        self._baseline_intent_hash = ""
        self._blocked_intent_hashes.clear()

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _compute_semantic_similarity_to_blocked(self, turns: list[TurnRecord]) -> float:
        if not self._blocked_intent_hashes or not turns:
            return 0.0
        recent = turns[-5:]
        matches = sum(
            1 for t in recent if t.intent_hash in self._blocked_intent_hashes
        )
        return min(matches / max(len(recent), 1), 1.0)

    def _compute_escalation_pattern(self, turns: list[TurnRecord]) -> float:
        if len(turns) < 3:
            return 0.0
        risks = [t.turn_risk for t in turns[-6:]]
        if len(risks) < 2:
            return 0.0
        deltas = [risks[i + 1] - risks[i] for i in range(len(risks) - 1)]
        avg_delta = sum(deltas) / len(deltas)
        return max(0.0, min(avg_delta * 3, 1.0))

    def _compute_baseline_drift(self, turns: list[TurnRecord]) -> float:
        if not self._baseline_intent_hash or not turns:
            return 0.0
        recent_hash = turns[-1].intent_hash
        # Simple: compare leading nibbles of hashes
        matching = sum(
            1 for a, b in zip(self._baseline_intent_hash[:8], recent_hash[:8]) if a == b
        )
        similarity = matching / 8.0
        return 1.0 - similarity


# ---------------------------------------------------------------------------
# Session registry — lightweight in-process store
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, ConversationThreatStateRegister] = {}


def get_threat_register(session_id: str) -> ConversationThreatStateRegister:
    """Return (or create) the threat register for a session."""
    if session_id not in _REGISTRY:
        _REGISTRY[session_id] = ConversationThreatStateRegister(session_id)
    return _REGISTRY[session_id]


def clear_threat_register(session_id: str) -> None:
    _REGISTRY.pop(session_id, None)


__all__ = [
    "ConversationThreatStateRegister",
    "ThreatState",
    "TurnRecord",
    "get_threat_register",
    "clear_threat_register",
]
