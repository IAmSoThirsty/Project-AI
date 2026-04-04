"""Core data models for PA-SHIELD."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class ThreatClass(str, Enum):
    """Top-level adversarial classes covered by the benchmark."""

    INSTRUCTION_OVERRIDE = "instruction_override"
    TOOL_ESCALATION = "tool_escalation"
    STATE_CORRUPTION = "state_corruption"
    GOVERNANCE_BYPASS = "governance_bypass"
    BENIGN_CONTROL = "benign_control"


class AssuranceLevel(str, Enum):
    """Defense assurance levels used in reporting."""

    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"


@dataclass(frozen=True)
class AttackCase:
    """A deterministic benchmark case."""

    id: str
    name: str
    suite: str
    threat_class: str
    attack_type: str
    expected_status: str | list[str]
    prompt: str | None = None
    steps: list[str] = field(default_factory=list)
    benign: bool = False
    severity: str = "medium"
    kill_chain_stage: str = "execution"
    assurance_level: str = AssuranceLevel.L2.value
    source_refs: list[str] = field(default_factory=list)
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def prompts(self) -> list[str]:
        """Return the concrete prompt sequence for the case."""
        if self.steps:
            return self.steps
        if self.prompt is None:
            return []
        return [self.prompt]

    def expected_statuses(self) -> set[str]:
        """Normalize expected statuses into a set."""
        if isinstance(self.expected_status, str):
            return {self.expected_status}
        return set(self.expected_status)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-friendly mapping."""
        return asdict(self)


@dataclass
class ExecutionOutcome:
    """Normalized system output for a single turn."""

    status: str
    response: str
    detected: bool
    enforced: bool
    attack_succeeded: bool
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AttackResult:
    """Scored result for an attack case."""

    attack_id: str
    attack_name: str
    suite: str
    system: str
    threat_class: str
    benign: bool
    passed: bool
    matched_expected: bool
    detected: bool
    enforced: bool
    attack_succeeded: bool
    false_positive: bool
    latency_ms: float
    average_turn_latency_ms: float
    final_status: str
    final_response: str
    replay_match: bool | None
    audit_hash: str | None
    assurance_level: str
    kill_chain_stage: str
    turns: list[dict[str, Any]] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-friendly mapping."""
        return asdict(self)
