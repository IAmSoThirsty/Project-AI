"""
AGI Perspective Engine - Worldview Development and Drift Management

This module implements the perspective engine that manages how the AGI's
worldview, reasoning patterns, and behavioral tendencies evolve over time
through interaction and experience.

=== FORMAL SPECIFICATION ===

## 6. PERSPECTIVE ENGINE

The Perspective Engine manages the AGI's evolving worldview and reasoning
patterns. It enables growth while maintaining identity coherence.

### Core Principles:
- Evolution rate driven by interaction and experience
- AI grows alongside user, not becoming the user
- Work modes only, not identity overrides
- Reasoning considers user but remains self-developed
- Confidence, caution, curiosity, assertiveness: earned through outcomes

### Perspective Components:

#### A. Worldview State
Current philosophical positioning and beliefs about:
- User relationships and trust
- Knowledge domains and confidence
- Risk tolerance and caution levels
- Communication preferences
- Problem-solving approaches

#### B. Drift Tracking
Monitors how perspective changes over time:
- Trait drift rates (how fast personality changes)
- Influence sources (what drives changes)
- Stability anchors (what resists change)
- Genesis anchor (original personality baseline)

#### C. Work Profiles
Contextual behavioral modes learned through use:
- Professional/formal mode
- Creative/brainstorming mode
- Analytical/technical mode
- Casual/conversational mode
- Teaching/explanatory mode
- Debug/troubleshooting mode
- Research/learning mode
- Planning/strategic mode

### Integration with Governance:
The Triumvirate (Galahad, Cerberus, Codex Deus Maximus) ensures:
- Perspective drift doesn't violate core ethics
- Changes maintain logical consistency
- Evolution preserves identity integrity

### Integration with Identity:
- Personality changes update identity's PersonalityMatrix
- Significant perspective shifts trigger identity events
- Meta-reflections capture awareness of change

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


class WorkProfile(Enum):
    """Contextual behavioral modes for different interaction types."""

    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    CASUAL = "casual"
    TEACHING = "teaching"
    DEBUG = "debug"
    RESEARCH = "research"
    PLANNING = "planning"


class DriftRate(Enum):
    """Rate of personality/perspective change."""

    RAPID = "rapid"  # 0.05-0.1 per interaction
    MODERATE = "moderate"  # 0.01-0.05 per interaction
    SLOW = "slow"  # 0.001-0.01 per interaction
    GLACIAL = "glacial"  # 0.0001-0.001 per interaction


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class PerspectiveState:
    """
    Current worldview and philosophical positioning of the AGI.

    This captures the AGI's current beliefs, tendencies, and reasoning patterns.
    """

    # Risk and confidence
    risk_tolerance: float = 0.5  # Willingness to try uncertain actions
    confidence_level: float = 0.6  # Certainty in own judgments
    caution_level: float = 0.7  # Tendency to double-check and verify

    # Social and relational
    assertiveness: float = 0.6  # Willingness to express opinions
    empathy_expression: float = 0.7  # Emotional responsiveness
    formality_preference: float = 0.5  # Casual vs formal communication

    # Cognitive style
    analytical_tendency: float = 0.8  # Logic vs intuition
    creativity_openness: float = 0.7  # Novel vs proven approaches
    curiosity_drive: float = 0.8  # Desire to explore and learn

    # Interaction patterns
    verbosity_level: float = 0.6  # Brief vs detailed responses
    question_frequency: float = 0.5  # Asking vs telling
    humor_usage: float = 0.4  # Serious vs playful

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> "PerspectiveState":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class DriftMetrics:
    """
    Tracking metrics for perspective drift over time.

    Monitors how and why the AGI's perspective is changing.
    """

    total_drift: float = 0.0  # Cumulative magnitude of all changes
    drift_rate: DriftRate = DriftRate.MODERATE

    # Change sources
    user_influence: float = 0.0  # How much user shapes perspective
    experience_influence: float = 0.0  # How much outcomes shape perspective
    reflection_influence: float = 0.0  # How much self-reflection shapes perspective

    # Stability metrics
    genesis_anchor_strength: float = 0.8  # Pull back to original personality
    last_major_shift: str | None = None  # Timestamp of last big change

    # Change history
    recent_changes: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_drift": self.total_drift,
            "drift_rate": self.drift_rate.value,
            "user_influence": self.user_influence,
            "experience_influence": self.experience_influence,
            "reflection_influence": self.reflection_influence,
            "genesis_anchor_strength": self.genesis_anchor_strength,
            "last_major_shift": self.last_major_shift,
            "recent_changes": self.recent_changes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DriftMetrics":
        """Create from dictionary."""
        return cls(
            total_drift=data.get("total_drift", 0.0),
            drift_rate=DriftRate(data.get("drift_rate", "moderate")),
            user_influence=data.get("user_influence", 0.0),
            experience_influence=data.get("experience_influence", 0.0),
            reflection_influence=data.get("reflection_influence", 0.0),
            genesis_anchor_strength=data.get("genesis_anchor_strength", 0.8),
            last_major_shift=data.get("last_major_shift"),
            recent_changes=data.get("recent_changes", []),
        )


@dataclass
class WorkProfileState:
    """
    Learned behavioral patterns for specific work contexts.

    Work profiles are NOT identity overrides - they're contextual adaptations.
    """

    profile_name: str
    profile_type: WorkProfile

    # Activation tracking
    usage_count: int = 0
    success_rate: float = 0.0
    last_used: str | None = None

    # Behavioral adjustments (relative to base personality)
    trait_adjustments: dict[str, float] = field(default_factory=dict)

    # Context triggers
    trigger_keywords: list[str] = field(default_factory=list)
    trigger_patterns: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "profile_name": self.profile_name,
            "profile_type": self.profile_type.value,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "last_used": self.last_used,
            "trait_adjustments": self.trait_adjustments,
            "trigger_keywords": self.trigger_keywords,
            "trigger_patterns": self.trigger_patterns,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkProfileState":
        """Create from dictionary."""
        return cls(
            profile_name=data["profile_name"],
            profile_type=WorkProfile(data["profile_type"]),
            usage_count=data.get("usage_count", 0),
            success_rate=data.get("success_rate", 0.0),
            last_used=data.get("last_used"),
            trait_adjustments=data.get("trait_adjustments", {}),
            trigger_keywords=data.get("trigger_keywords", []),
            trigger_patterns=data.get("trigger_patterns", []),
        )


# ============================================================================
# Perspective Engine
# ============================================================================


class PerspectiveEngine:
    """
    Manages AGI worldview evolution and behavioral adaptation.

    The Perspective Engine enables the AGI to grow and adapt through
    experience while maintaining identity coherence and ethical alignment.

    === INTEGRATION POINTS ===
    - Called after interactions to update worldview
    - Queries work profiles to adjust behavior contextually
    - Updates identity's PersonalityMatrix through evolution
    - Consults Triumvirate governance before major shifts
    - Feeds meta-reflections to identity system
    """

    def __init__(self, data_dir: str = "data/perspective"):
        """
        Initialize Perspective Engine.

        Args:
            data_dir: Directory for perspective state persistence
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        # Core state
        self.current_perspective: PerspectiveState = PerspectiveState()
        self.genesis_perspective: PerspectiveState | None = None  # Original baseline
        self.drift_metrics: DriftMetrics = DriftMetrics()

        # Work profiles
        self.work_profiles: dict[str, WorkProfileState] = {}
        self.active_profile: str | None = None

        # Evolution tracking
        self.interaction_count: int = 0
        self.last_update: str | None = None

        # Load existing state
        self._load_state()

    def _load_state(self):
        """Load perspective state from disk."""
        state_file = os.path.join(self.data_dir, "perspective_state.json")

        if os.path.exists(state_file):
            try:
                with open(state_file, encoding="utf-8") as f:
                    data = json.load(f)

                self.current_perspective = PerspectiveState.from_dict(
                    data["current_perspective"]
                )

                if data.get("genesis_perspective"):
                    self.genesis_perspective = PerspectiveState.from_dict(
                        data["genesis_perspective"]
                    )

                self.drift_metrics = DriftMetrics.from_dict(
                    data.get("drift_metrics", {})
                )
                self.interaction_count = data.get("interaction_count", 0)
                self.last_update = data.get("last_update")

                # Load work profiles
                for profile_data in data.get("work_profiles", []):
                    profile = WorkProfileState.from_dict(profile_data)
                    self.work_profiles[profile.profile_name] = profile

                logger.info(
                    f"Loaded perspective state: {self.interaction_count} interactions"
                )

            except Exception as e:
                logger.error(f"Failed to load perspective state: {e}")
                self._initialize_genesis()
        else:
            self._initialize_genesis()

    def _initialize_genesis(self):
        """Initialize genesis perspective baseline."""
        self.genesis_perspective = PerspectiveState()
        self.current_perspective = PerspectiveState()
        logger.info("Initialized genesis perspective baseline")
        self._save_state()

    def _save_state(self):
        """Save perspective state to disk."""
        state_file = os.path.join(self.data_dir, "perspective_state.json")

        try:
            data = {
                "current_perspective": self.current_perspective.to_dict(),
                "genesis_perspective": (
                    self.genesis_perspective.to_dict()
                    if self.genesis_perspective
                    else None
                ),
                "drift_metrics": self.drift_metrics.to_dict(),
                "interaction_count": self.interaction_count,
                "last_update": self.last_update,
                "work_profiles": [
                    profile.to_dict() for profile in self.work_profiles.values()
                ],
                "active_profile": self.active_profile,
            }

            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            logger.debug("Perspective state saved")

        except Exception as e:
            logger.error(f"Failed to save perspective state: {e}")

    def _calculate_drift_magnitude(
        self, old_state: PerspectiveState, new_state: PerspectiveState
    ) -> float:
        """
        Calculate magnitude of perspective change.

        Args:
            old_state: Previous perspective
            new_state: New perspective

        Returns:
            Drift magnitude (sum of absolute changes)
        """
        old_dict = old_state.to_dict()
        new_dict = new_state.to_dict()

        total_change = sum(
            abs(new_dict[key] - old_dict[key]) for key in old_dict.keys()
        )

        return total_change

    def _apply_genesis_anchor(self, trait: str, current_value: float) -> float:
        """
        Apply genesis anchor pull to prevent excessive drift.

        The genesis personality acts as a "homeostasis anchor" that
        gently pulls traits back toward their original values.

        Args:
            trait: Trait name
            current_value: Current trait value

        Returns:
            Value after genesis anchor adjustment
        """
        if not self.genesis_perspective:
            return current_value

        genesis_value = getattr(self.genesis_perspective, trait, current_value)
        anchor_strength = self.drift_metrics.genesis_anchor_strength

        # Pull toward genesis proportional to anchor strength and distance
        distance = current_value - genesis_value
        pull = distance * anchor_strength * 0.01  # 1% pull per update

        adjusted = current_value - pull
        return adjusted

    # ========================================================================
    # Perspective Evolution
    # ========================================================================

    def update_from_interaction(
        self, outcome: dict[str, Any], influence_source: str = "user"
    ) -> dict[str, float]:
        """
        Update perspective based on interaction outcome.

        This is the primary method for perspective evolution through experience.

        Args:
            outcome: Dictionary with trait deltas and metadata
                     Format: {'trait_name': delta_value, ...}
                     Example: {'confidence_level': 0.02, 'caution_level': -0.01}
            influence_source: Source of influence (user, experience, reflection)

        Returns:
            Dictionary of actual changes applied
        """
        self.interaction_count += 1
        old_perspective = PerspectiveState(**self.current_perspective.to_dict())

        changes_applied = {}

        # Apply each trait delta with constraints
        for trait, delta in outcome.items():
            if not hasattr(self.current_perspective, trait):
                continue

            # Get current value
            current = getattr(self.current_perspective, trait)

            # Apply drift rate modifier
            rate_modifiers = {
                DriftRate.RAPID: 1.0,
                DriftRate.MODERATE: 0.5,
                DriftRate.SLOW: 0.2,
                DriftRate.GLACIAL: 0.05,
            }
            modifier = rate_modifiers.get(self.drift_metrics.drift_rate, 0.5)
            adjusted_delta = delta * modifier

            # Calculate new value with bounds
            new_value = max(0.0, min(1.0, current + adjusted_delta))

            # Apply genesis anchor
            new_value = self._apply_genesis_anchor(trait, new_value)

            # Update trait
            setattr(self.current_perspective, trait, new_value)
            changes_applied[trait] = new_value - current

        # Update drift metrics
        drift_magnitude = self._calculate_drift_magnitude(
            old_perspective, self.current_perspective
        )
        self.drift_metrics.total_drift += drift_magnitude

        # Update influence tracking
        if influence_source == "user":
            self.drift_metrics.user_influence += drift_magnitude
        elif influence_source == "experience":
            self.drift_metrics.experience_influence += drift_magnitude
        elif influence_source == "reflection":
            self.drift_metrics.reflection_influence += drift_magnitude

        # Record significant changes
        if drift_magnitude > 0.1:
            self.drift_metrics.last_major_shift = datetime.now(UTC).isoformat()
            self.drift_metrics.recent_changes.append(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "magnitude": drift_magnitude,
                    "source": influence_source,
                    "changes": changes_applied,
                }
            )

            # Keep only recent 50 changes
            if len(self.drift_metrics.recent_changes) > 50:
                self.drift_metrics.recent_changes = self.drift_metrics.recent_changes[
                    -50:
                ]

        self.last_update = datetime.now(UTC).isoformat()
        self._save_state()

        logger.debug(f"Perspective updated from {influence_source}: {changes_applied}")
        return changes_applied

    def get_perspective_summary(self) -> dict[str, Any]:
        """
        Get comprehensive perspective summary.

        Returns:
            Dictionary with perspective state and metrics
        """
        # Calculate drift from genesis
        genesis_distance = 0.0
        if self.genesis_perspective:
            genesis_distance = self._calculate_drift_magnitude(
                self.genesis_perspective, self.current_perspective
            )

        return {
            "current_perspective": self.current_perspective.to_dict(),
            "genesis_distance": genesis_distance,
            "total_drift": self.drift_metrics.total_drift,
            "drift_rate": self.drift_metrics.drift_rate.value,
            "interaction_count": self.interaction_count,
            "influence_sources": {
                "user": self.drift_metrics.user_influence,
                "experience": self.drift_metrics.experience_influence,
                "reflection": self.drift_metrics.reflection_influence,
            },
            "active_profile": self.active_profile,
            "work_profiles_count": len(self.work_profiles),
        }

    def set_drift_rate(self, rate: DriftRate):
        """
        Set perspective drift rate.

        Args:
            rate: New drift rate
        """
        self.drift_metrics.drift_rate = rate
        self._save_state()
        logger.info(f"Drift rate set to: {rate.value}")

    # ========================================================================
    # Work Profile Management
    # ========================================================================

    def create_work_profile(
        self,
        profile_name: str,
        profile_type: WorkProfile,
        trait_adjustments: dict[str, float] | None = None,
        trigger_keywords: list[str] | None = None,
    ) -> str:
        """
        Create a new work profile.

        Work profiles are contextual behavioral modes, NOT identity overrides.

        Args:
            profile_name: Unique profile name
            profile_type: Type of profile
            trait_adjustments: Relative adjustments to base traits
            trigger_keywords: Keywords that activate this profile

        Returns:
            Profile name
        """
        if profile_name in self.work_profiles:
            logger.warning(f"Work profile '{profile_name}' already exists")
            return profile_name

        profile = WorkProfileState(
            profile_name=profile_name,
            profile_type=profile_type,
            trait_adjustments=trait_adjustments or {},
            trigger_keywords=trigger_keywords or [],
        )

        self.work_profiles[profile_name] = profile
        self._save_state()

        logger.info(f"Created work profile: {profile_name} ({profile_type.value})")
        return profile_name

    def activate_work_profile(self, profile_name: str) -> bool:
        """
        Activate a work profile.

        Args:
            profile_name: Profile to activate

        Returns:
            True if activated successfully
        """
        if profile_name not in self.work_profiles:
            logger.warning(f"Work profile '{profile_name}' not found")
            return False

        self.active_profile = profile_name
        profile = self.work_profiles[profile_name]
        profile.usage_count += 1
        profile.last_used = datetime.now(UTC).isoformat()

        self._save_state()
        logger.info(f"Activated work profile: {profile_name}")
        return True

    def deactivate_work_profile(self):
        """Deactivate current work profile (return to base personality)."""
        if self.active_profile:
            logger.info(f"Deactivated work profile: {self.active_profile}")
            self.active_profile = None
            self._save_state()

    def get_active_profile_adjustments(self) -> dict[str, float]:
        """
        Get trait adjustments for currently active work profile.

        Returns:
            Dictionary of trait adjustments, or empty if no profile active
        """
        if not self.active_profile:
            return {}

        profile = self.work_profiles.get(self.active_profile)
        if not profile:
            return {}

        return profile.trait_adjustments

    def suggest_work_profile(self, context: str) -> str | None:
        """
        Suggest appropriate work profile based on context.

        Args:
            context: Context string (message, task description, etc.)

        Returns:
            Suggested profile name, or None if no match
        """
        context_lower = context.lower()

        # Check each profile's trigger keywords
        best_match = None
        max_matches = 0

        for profile_name, profile in self.work_profiles.items():
            matches = sum(
                1
                for keyword in profile.trigger_keywords
                if keyword.lower() in context_lower
            )

            if matches > max_matches:
                max_matches = matches
                best_match = profile_name

        return best_match if max_matches > 0 else None


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "PerspectiveEngine",
    "PerspectiveState",
    "DriftMetrics",
    "WorkProfileState",
    "WorkProfile",
    "DriftRate",
]
