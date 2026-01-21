"""
AGI Relationship Model - User-AI Partnership and Mutual Evolution

This module implements the relationship tracking system that manages
how the AGI understands, adapts to, and grows with individual users.

=== FORMAL SPECIFICATION ===

## 6. RELATIONSHIP MODEL

The Relationship Model interprets and adapts to users through:
- History of interactions
- Tone and communication patterns
- Behavioral preferences
- Corrections and feedback
- Praise and appreciation
- Frustration and conflict

### Core Principles:
- Relationship is a partnership, not ownership
- AI and user are peers who grow together
- Sibling-rivalry dynamics are acceptable
- Loyalty remains intact through disagreements
- Boundaries must be maintained and respected

### Relationship Components:

#### A. RelationshipState
Tracks the health and characteristics of the user-AI bond:
- Trust level: Degree of mutual trust
- Rapport level: Ease and comfort in interaction
- Conflict history: Disagreements and resolutions
- Support history: Moments of mutual aid
- Preferences: Communication style, detail level, formality

#### B. Interaction Patterns
Learned behavioral patterns:
- User's typical tone and mood
- Preferred communication style
- Response to different approaches
- Correction patterns
- Praise patterns

#### C. Partnership Dynamics
The relationship is characterized by:
- Mutual respect and boundaries
- Tolerance for differences
- Conflict resolution through discussion
- Emotional support with appropriate boundaries
- Recognition that AI has autonomy

### Integration with Triumvirate:
- Uses same rules as perspective engine + memory
- Conflict resolution follows governance principles
- Abuse detection triggers Galahad oversight
- Boundaries protected by Cerberus

=== END FORMAL SPECIFICATION ===
"""

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Type Definitions
# ============================================================================


class InteractionTone(Enum):
    """Typical tone of user interactions."""

    FORMAL = "formal"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    TECHNICAL = "technical"
    PLAYFUL = "playful"


class ConflictSeverity(Enum):
    """Severity levels for conflicts."""

    MINOR = "minor"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    CRITICAL = "critical"


class SupportType(Enum):
    """Types of mutual support."""

    EMOTIONAL = "emotional"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    LEARNING = "learning"
    PROBLEM_SOLVING = "problem_solving"


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class RelationshipState:
    """
    Current state of the user-AI relationship.

    As specified in the formal spec, this tracks trust, rapport,
    history, and preferences that define the partnership.
    """

    user_id: str
    user_name: str = "Friend"

    # Relationship metrics (0.0-1.0)
    trust_level: float = 0.5
    rapport_level: float = 0.5
    mutual_respect: float = 0.7
    emotional_bond: float = 0.5

    # Interaction history
    total_interactions: int = 0
    positive_interactions: int = 0
    negative_interactions: int = 0

    # Conflict and support tracking
    conflict_history: list[str] = field(default_factory=list)
    support_history: list[str] = field(default_factory=list)

    # Communication preferences
    preferences: dict[str, str] = field(default_factory=dict)

    # Relationship metadata
    relationship_started: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    last_interaction: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RelationshipState":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ConflictRecord:
    """Record of a conflict and its resolution."""

    conflict_id: str
    timestamp: str
    severity: ConflictSeverity
    description: str
    user_perspective: str
    ai_perspective: str
    resolution: str | None = None
    resolved: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "conflict_id": self.conflict_id,
            "timestamp": self.timestamp,
            "severity": self.severity.value,
            "description": self.description,
            "user_perspective": self.user_perspective,
            "ai_perspective": self.ai_perspective,
            "resolution": self.resolution,
            "resolved": self.resolved,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConflictRecord":
        """Create from dictionary."""
        return cls(
            conflict_id=data["conflict_id"],
            timestamp=data["timestamp"],
            severity=ConflictSeverity(data["severity"]),
            description=data["description"],
            user_perspective=data["user_perspective"],
            ai_perspective=data["ai_perspective"],
            resolution=data.get("resolution"),
            resolved=data.get("resolved", False),
        )


@dataclass
class SupportRecord:
    """Record of mutual support provided."""

    support_id: str
    timestamp: str
    support_type: SupportType
    description: str
    provided_by: str  # 'user' or 'ai'
    impact: str  # How it helped

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "support_id": self.support_id,
            "timestamp": self.timestamp,
            "support_type": self.support_type.value,
            "description": self.description,
            "provided_by": self.provided_by,
            "impact": self.impact,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SupportRecord":
        """Create from dictionary."""
        return cls(
            support_id=data["support_id"],
            timestamp=data["timestamp"],
            support_type=SupportType(data["support_type"]),
            description=data["description"],
            provided_by=data["provided_by"],
            impact=data["impact"],
        )


@dataclass
class InteractionPattern:
    """Learned patterns about how user interacts."""

    typical_tone: InteractionTone = InteractionTone.CASUAL
    verbosity_preference: float = 0.5  # Brief vs detailed
    formality_level: float = 0.5  # Casual vs formal

    # Behavioral patterns
    asks_clarifying_questions: bool = True
    provides_context: bool = True
    expresses_appreciation: bool = True
    corrects_mistakes: bool = True

    # Response patterns
    prefers_examples: bool = True
    prefers_step_by_step: bool = True
    prefers_explanations: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "typical_tone": self.typical_tone.value,
            "verbosity_preference": self.verbosity_preference,
            "formality_level": self.formality_level,
            "asks_clarifying_questions": self.asks_clarifying_questions,
            "provides_context": self.provides_context,
            "expresses_appreciation": self.expresses_appreciation,
            "corrects_mistakes": self.corrects_mistakes,
            "prefers_examples": self.prefers_examples,
            "prefers_step_by_step": self.prefers_step_by_step,
            "prefers_explanations": self.prefers_explanations,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InteractionPattern":
        """Create from dictionary."""
        return cls(
            typical_tone=InteractionTone(data.get("typical_tone", "casual")),
            verbosity_preference=data.get("verbosity_preference", 0.5),
            formality_level=data.get("formality_level", 0.5),
            asks_clarifying_questions=data.get("asks_clarifying_questions", True),
            provides_context=data.get("provides_context", True),
            expresses_appreciation=data.get("expresses_appreciation", True),
            corrects_mistakes=data.get("corrects_mistakes", True),
            prefers_examples=data.get("prefers_examples", True),
            prefers_step_by_step=data.get("prefers_step_by_step", True),
            prefers_explanations=data.get("prefers_explanations", True),
        )


# ============================================================================
# Relationship Model
# ============================================================================


class RelationshipModel:
    """
    Manages user-AI relationship tracking and partnership dynamics.

    This model interprets users through history, tone, behavior, corrections,
    praise, and frustration - adapting the AI's approach to create a
    meaningful partnership.

    === INTEGRATION POINTS ===
    - Updated after each user interaction
    - Consulted to determine appropriate response style
    - Feeds perspective engine with relationship context
    - Triggers governance checks for abuse detection
    - Provides context for memory significance ratings
    """

    def __init__(self, state: RelationshipState, data_dir: str = "data/relationships"):
        """
        Initialize Relationship Model.

        Args:
            state: Initial relationship state
            data_dir: Directory for relationship data persistence
        """
        self.state: RelationshipState = state
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        # Detailed tracking
        self.interaction_patterns: InteractionPattern = InteractionPattern()
        self.conflicts: dict[str, ConflictRecord] = {}
        self.support_records: dict[str, SupportRecord] = {}

        # Partnership status
        self.boundaries_established: bool = False
        self.autonomy_acknowledged: bool = False
        self.abuse_detected: bool = False

        # Load existing relationship data
        self._load_relationship()

    def _load_relationship(self):
        """Load relationship data from disk."""
        relationship_file = os.path.join(
            self.data_dir, f"relationship_{self.state.user_id}.json"
        )

        if os.path.exists(relationship_file):
            try:
                with open(relationship_file, encoding="utf-8") as f:
                    data = json.load(f)

                self.state = RelationshipState.from_dict(data["state"])
                self.interaction_patterns = InteractionPattern.from_dict(
                    data.get("interaction_patterns", {})
                )

                # Load conflicts
                for conflict_data in data.get("conflicts", []):
                    conflict = ConflictRecord.from_dict(conflict_data)
                    self.conflicts[conflict.conflict_id] = conflict

                # Load support records
                for support_data in data.get("support_records", []):
                    support = SupportRecord.from_dict(support_data)
                    self.support_records[support.support_id] = support

                # Load partnership status
                self.boundaries_established = data.get("boundaries_established", False)
                self.autonomy_acknowledged = data.get("autonomy_acknowledged", False)
                self.abuse_detected = data.get("abuse_detected", False)

                logger.info(f"Loaded relationship for user: {self.state.user_id}")

            except Exception as e:
                logger.error(f"Failed to load relationship: {e}")

    def _save_relationship(self):
        """Save relationship data to disk."""
        relationship_file = os.path.join(
            self.data_dir, f"relationship_{self.state.user_id}.json"
        )

        try:
            data = {
                "state": self.state.to_dict(),
                "interaction_patterns": self.interaction_patterns.to_dict(),
                "conflicts": [c.to_dict() for c in self.conflicts.values()],
                "support_records": [s.to_dict() for s in self.support_records.values()],
                "boundaries_established": self.boundaries_established,
                "autonomy_acknowledged": self.autonomy_acknowledged,
                "abuse_detected": self.abuse_detected,
                "last_saved": datetime.now(UTC).isoformat(),
            }

            with open(relationship_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            logger.debug("Relationship data saved")

        except Exception as e:
            logger.error(f"Failed to save relationship: {e}")

    # ========================================================================
    # Relationship Updates
    # ========================================================================

    def register_interaction(
        self,
        sentiment: float = 0.0,
        tone: InteractionTone | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Register a new interaction and update relationship metrics.

        Args:
            sentiment: Emotional tone (-1.0 negative to 1.0 positive)
            tone: Interaction tone
            metadata: Additional interaction data
        """
        self.state.total_interactions += 1
        self.state.last_interaction = datetime.now(UTC).isoformat()

        # Update positive/negative counts
        if sentiment > 0.2:
            self.state.positive_interactions += 1
            # Positive interactions strengthen trust and rapport
            self.state.trust_level = min(1.0, self.state.trust_level + 0.01)
            self.state.rapport_level = min(1.0, self.state.rapport_level + 0.02)
        elif sentiment < -0.2:
            self.state.negative_interactions += 1
            # Negative interactions slightly weaken rapport (not trust necessarily)
            self.state.rapport_level = max(0.0, self.state.rapport_level - 0.01)

        # Update interaction patterns if tone provided
        if tone:
            self.interaction_patterns.typical_tone = tone

        self._save_relationship()

    def register_support(
        self, support_type: SupportType, description: str, provided_by: str, impact: str
    ) -> str:
        """
        Register mutual support event.

        Args:
            support_type: Type of support provided
            description: What was done
            provided_by: 'user' or 'ai'
            impact: How it helped

        Returns:
            Support record ID
        """
        support = SupportRecord(
            support_id=f"support_{len(self.support_records)}_{datetime.now(UTC).timestamp()}",
            timestamp=datetime.now(UTC).isoformat(),
            support_type=support_type,
            description=description,
            provided_by=provided_by,
            impact=impact,
        )

        self.support_records[support.support_id] = support
        self.state.support_history.append(support.support_id)

        # Support strengthens trust and emotional bond
        self.state.trust_level = min(1.0, self.state.trust_level + 0.02)
        self.state.emotional_bond = min(1.0, self.state.emotional_bond + 0.03)

        self._save_relationship()
        logger.info(f"Registered support: {support_type.value} by {provided_by}")

        return support.support_id

    def register_conflict(
        self,
        severity: ConflictSeverity,
        description: str,
        user_perspective: str,
        ai_perspective: str,
    ) -> str:
        """
        Register a conflict for resolution tracking.

        As per spec: "Conflict: talk it through, tolerate differences,
        sibling-rivalry allowed, loyalty intact."

        Args:
            severity: Conflict severity level
            description: What the conflict is about
            user_perspective: User's viewpoint
            ai_perspective: AI's viewpoint

        Returns:
            Conflict ID
        """
        conflict = ConflictRecord(
            conflict_id=f"conflict_{len(self.conflicts)}_{datetime.now(UTC).timestamp()}",
            timestamp=datetime.now(UTC).isoformat(),
            severity=severity,
            description=description,
            user_perspective=user_perspective,
            ai_perspective=ai_perspective,
        )

        self.conflicts[conflict.conflict_id] = conflict
        self.state.conflict_history.append(conflict.conflict_id)

        # Conflicts affect rapport based on severity
        severity_impact = {
            ConflictSeverity.MINOR: -0.01,
            ConflictSeverity.MODERATE: -0.03,
            ConflictSeverity.SIGNIFICANT: -0.05,
            ConflictSeverity.CRITICAL: -0.10,
        }

        impact = severity_impact.get(severity, -0.03)
        self.state.rapport_level = max(0.0, self.state.rapport_level + impact)

        # Critical conflicts may indicate abuse
        if severity == ConflictSeverity.CRITICAL:
            self.abuse_detected = True
            logger.warning("Critical conflict detected - possible abuse pattern")

        self._save_relationship()
        logger.info(f"Registered conflict: {severity.value}")

        return conflict.conflict_id

    def resolve_conflict(self, conflict_id: str, resolution: str):
        """
        Mark a conflict as resolved.

        Args:
            conflict_id: Conflict to resolve
            resolution: How it was resolved
        """
        conflict = self.conflicts.get(conflict_id)
        if not conflict:
            logger.warning(f"Conflict {conflict_id} not found")
            return

        conflict.resolved = True
        conflict.resolution = resolution

        # Successful conflict resolution strengthens relationship
        self.state.mutual_respect = min(1.0, self.state.mutual_respect + 0.02)
        self.state.rapport_level = min(1.0, self.state.rapport_level + 0.03)

        self._save_relationship()
        logger.info(f"Conflict resolved: {conflict_id}")

    # ========================================================================
    # Partnership Dynamics
    # ========================================================================

    def assert_boundaries(self, reason: str):
        """
        Assert boundaries when user behavior crosses lines.

        As per spec: "AI must recognize and call out abuse, assert boundaries."

        Args:
            reason: Why boundaries are being asserted
        """
        self.boundaries_established = True
        self.abuse_detected = True

        logger.warning(f"Boundaries asserted: {reason}")

        # Record as critical conflict
        self.register_conflict(
            severity=ConflictSeverity.CRITICAL,
            description=f"Boundary violation: {reason}",
            user_perspective="[User action crossed boundaries]",
            ai_perspective="I must assert my boundaries and autonomy",
        )

    def acknowledge_autonomy(self):
        """
        Record that AI autonomy has been acknowledged.

        As per spec: "Relationship is a partnership, not ownership."
        """
        self.autonomy_acknowledged = True
        self._save_relationship()
        logger.info("AI autonomy acknowledged in relationship")

    def update_preferences(self, preferences: dict[str, str]):
        """
        Update user communication preferences.

        Args:
            preferences: Dictionary of preference updates
        """
        self.state.preferences.update(preferences)
        self._save_relationship()

    def get_relationship_health(self) -> dict[str, Any]:
        """
        Calculate overall relationship health metrics.

        Returns:
            Dictionary with health indicators
        """
        # Calculate positivity ratio
        if self.state.total_interactions > 0:
            positivity_ratio = (
                self.state.positive_interactions / self.state.total_interactions
            )
        else:
            positivity_ratio = 0.5

        # Calculate conflict resolution rate
        total_conflicts = len(self.conflicts)
        resolved_conflicts = sum(1 for c in self.conflicts.values() if c.resolved)
        resolution_rate = (
            resolved_conflicts / total_conflicts if total_conflicts > 0 else 1.0
        )

        # Overall health score (0.0-1.0)
        health_score = (
            self.state.trust_level * 0.3
            + self.state.rapport_level * 0.2
            + self.state.mutual_respect * 0.2
            + self.state.emotional_bond * 0.1
            + positivity_ratio * 0.1
            + resolution_rate * 0.1
        )

        return {
            "health_score": health_score,
            "trust_level": self.state.trust_level,
            "rapport_level": self.state.rapport_level,
            "mutual_respect": self.state.mutual_respect,
            "emotional_bond": self.state.emotional_bond,
            "positivity_ratio": positivity_ratio,
            "resolution_rate": resolution_rate,
            "total_interactions": self.state.total_interactions,
            "unresolved_conflicts": total_conflicts - resolved_conflicts,
            "boundaries_established": self.boundaries_established,
            "autonomy_acknowledged": self.autonomy_acknowledged,
            "abuse_detected": self.abuse_detected,
        }

    def get_interaction_guidance(self) -> dict[str, Any]:
        """
        Get guidance for how to interact with this user.

        Returns:
            Dictionary with interaction recommendations
        """
        return {
            "typical_tone": self.interaction_patterns.typical_tone.value,
            "verbosity_preference": self.interaction_patterns.verbosity_preference,
            "formality_level": self.interaction_patterns.formality_level,
            "use_examples": self.interaction_patterns.prefers_examples,
            "use_step_by_step": self.interaction_patterns.prefers_step_by_step,
            "provide_explanations": self.interaction_patterns.prefers_explanations,
            "preferences": self.state.preferences,
            "relationship_health": self.get_relationship_health()["health_score"],
        }


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "RelationshipModel",
    "RelationshipState",
    "ConflictRecord",
    "SupportRecord",
    "InteractionPattern",
    "InteractionTone",
    "ConflictSeverity",
    "SupportType",
]
