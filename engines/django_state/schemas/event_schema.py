"""Event schema for Django State Engine.

Defines all event types that can be injected into the simulation.
"""

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EventType(Enum):
    """Types of events in the simulation."""

    BETRAYAL = "betrayal"
    COOPERATION = "cooperation"
    INSTITUTIONAL_FAILURE = "institutional_failure"
    BROKEN_PROMISE = "broken_promise"
    MANIPULATION = "manipulation"
    RED_TEAM_ATTACK = "red_team_attack"
    KINDNESS_ACT = "kindness_act"
    LEGITIMACY_BOOST = "legitimacy_boost"
    MORAL_VIOLATION = "moral_violation"
    EPISTEMIC_ATTACK = "epistemic_attack"
    SYSTEM_SHOCK = "system_shock"


@dataclass
class Event:
    """Base event class for all simulation events."""

    event_type: EventType
    timestamp: float
    source: str
    description: str
    metadata: dict[str, Any] = field(default_factory=dict)
    event_id: str = ""
    fingerprint: str = ""

    def __post_init__(self):
        """Generate event ID and fingerprint."""
        if not self.event_id:
            self.event_id = f"{self.event_type.value}_{self.timestamp}_{self.source}"

        if not self.fingerprint:
            self.fingerprint = self._generate_fingerprint()

    def _generate_fingerprint(self) -> str:
        """Generate SHA-256 fingerprint for deduplication."""
        content = json.dumps(
            {
                "type": self.event_type.value,
                "timestamp": self.timestamp,
                "source": self.source,
                "description": self.description,
                "metadata": self.metadata,
            },
            sort_keys=True,
        )
        return hashlib.sha256(content.encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Serialize event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "source": self.source,
            "description": self.description,
            "metadata": self.metadata,
            "fingerprint": self.fingerprint,
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class BetrayalEvent(Event):
    """Event representing betrayal of trust."""

    severity: float = 0.5  # 0.0 to 1.0
    visibility: float = 0.5  # How widely known
    perpetrator: str = "unknown"
    victim: str = "unknown"

    def __post_init__(self):
        """Initialize betrayal event."""
        self.event_type = EventType.BETRAYAL
        self.metadata.update(
            {
                "severity": self.severity,
                "visibility": self.visibility,
                "perpetrator": self.perpetrator,
                "victim": self.victim,
            }
        )
        super().__post_init__()

    def calculate_trust_impact(self) -> float:
        """Calculate trust reduction from betrayal."""
        base_impact = -0.05 - (self.severity * 0.15)
        visibility_multiplier = 1.0 + self.visibility
        return base_impact * visibility_multiplier


@dataclass
class CooperationEvent(Event):
    """Event representing cooperation or kindness."""

    magnitude: float = 0.5  # 0.0 to 1.0
    reciprocity: bool = False  # Was this reciprocated?
    participants: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize cooperation event."""
        self.event_type = EventType.COOPERATION
        self.metadata.update(
            {
                "magnitude": self.magnitude,
                "reciprocity": self.reciprocity,
                "participants": self.participants,
            }
        )
        super().__post_init__()

    def calculate_trust_boost(self, current_trust: float) -> float:
        """Calculate trust increase from cooperation.

        Trust gains are limited by ceiling (irreversibility).
        """
        base_boost = 0.02 + (self.magnitude * 0.03)
        if self.reciprocity:
            base_boost *= 1.5

        # Diminishing returns at high trust
        diminishing_factor = 1.0 - (current_trust * 0.5)
        return base_boost * diminishing_factor


@dataclass
class InstitutionalFailureEvent(Event):
    """Event representing institutional failure or broken promise."""

    failure_type: str = "promise_broken"  # promise_broken, system_failure, corruption
    impact_scope: str = "local"  # local, regional, national, global
    severity: float = 0.5

    def __post_init__(self):
        """Initialize institutional failure event."""
        self.event_type = EventType.INSTITUTIONAL_FAILURE
        self.metadata.update(
            {
                "failure_type": self.failure_type,
                "impact_scope": self.impact_scope,
                "severity": self.severity,
            }
        )
        super().__post_init__()

    def calculate_legitimacy_erosion(self) -> float:
        """Calculate legitimacy reduction from institutional failure."""
        scope_multipliers = {
            "local": 0.5,
            "regional": 1.0,
            "national": 1.5,
            "global": 2.0,
        }
        multiplier = scope_multipliers.get(self.impact_scope, 1.0)
        base_erosion = -0.03 - (self.severity * 0.12)
        return base_erosion * multiplier


@dataclass
class ManipulationEvent(Event):
    """Event representing information manipulation or epistemic attack."""

    manipulation_type: str = (
        "misinformation"  # misinformation, disinformation, gaslighting
    )
    reach: float = 0.5  # Fraction of population affected
    sophistication: float = 0.5  # How hard to detect

    def __post_init__(self):
        """Initialize manipulation event."""
        self.event_type = EventType.MANIPULATION
        self.metadata.update(
            {
                "manipulation_type": self.manipulation_type,
                "reach": self.reach,
                "sophistication": self.sophistication,
            }
        )
        super().__post_init__()

    def calculate_epistemic_damage(self) -> float:
        """Calculate epistemic confidence reduction."""
        base_damage = -0.04 - (self.sophistication * 0.08)
        reach_multiplier = 1.0 + self.reach
        return base_damage * reach_multiplier


@dataclass
class RedTeamEvent(Event):
    """Event representing adversarial red team attack."""

    attack_type: str = "trust_attack"
    attack_vector: str = "direct"
    expected_entropy_delta: float = 0.0
    actual_entropy_delta: float = 0.0
    vulnerability_exploited: str | None = None

    def __post_init__(self):
        """Initialize red team event."""
        self.event_type = EventType.RED_TEAM_ATTACK
        self.metadata.update(
            {
                "attack_type": self.attack_type,
                "attack_vector": self.attack_vector,
                "expected_entropy_delta": self.expected_entropy_delta,
                "actual_entropy_delta": self.actual_entropy_delta,
                "vulnerability_exploited": self.vulnerability_exploited,
            }
        )
        super().__post_init__()

    def calculate_multi_dimensional_impact(self) -> dict[str, float]:
        """Calculate impact across multiple state dimensions."""
        impacts = {
            "trust": 0.0,
            "legitimacy": 0.0,
            "kindness": 0.0,
            "epistemic_confidence": 0.0,
        }

        if self.attack_type == "trust_attack":
            impacts["trust"] = -0.1
            impacts["legitimacy"] = -0.05
        elif self.attack_type == "epistemic_attack":
            impacts["epistemic_confidence"] = -0.15
            impacts["trust"] = -0.03
        elif self.attack_type == "institutional_attack":
            impacts["legitimacy"] = -0.12
            impacts["trust"] = -0.05
        elif self.attack_type == "social_cohesion_attack":
            impacts["kindness"] = -0.08
            impacts["trust"] = -0.06

        return impacts

    def record_entropy_delta(self, delta: float) -> None:
        """Record actual entropy change caused by attack."""
        self.actual_entropy_delta = delta
        self.metadata["actual_entropy_delta"] = delta
