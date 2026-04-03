#                                           [2026-03-04 13:36]
#                                          Productivity: Active
"""
Skills Engine — Skill Model
============================

Defines the core Skill data model: the distinction between
KNOWLEDGE (knowing about something) and PROFICIENCY (being
able to execute it). Skills decay without practice.

Design Principle:
  "It may know something. However, that does not determine
   its ability to pull it off."
"""

from datetime import UTC, datetime
from typing import Any


class Skill:
    """
    A learned capability with independent knowledge and proficiency scores.

    Knowledge: How much the AGI *understands* about a skill (0.0 → 1.0).
      - Goes up when the AGI encounters, reads about, or is taught something.
      - Does NOT decay. What you learn, you keep.

    Proficiency: How well the AGI can *execute* the skill (0.0 → 1.0).
      - Only goes up through practice (attempting + evaluating results).
      - Decays over time without practice (use it or lose it).
      - Cannot exceed knowledge (you can't execute what you don't understand).

    Tiers:
      - NOVICE:       proficiency < 0.2
      - APPRENTICE:   0.2 <= proficiency < 0.4
      - JOURNEYMAN:   0.4 <= proficiency < 0.6
      - EXPERT:       0.6 <= proficiency < 0.8
      - MASTER:       0.8 <= proficiency < 0.95
      - SOVEREIGN:    proficiency >= 0.95
    """

    TIERS = [
        (0.95, "SOVEREIGN"),
        (0.80, "MASTER"),
        (0.60, "EXPERT"),
        (0.40, "JOURNEYMAN"),
        (0.20, "APPRENTICE"),
        (0.00, "NOVICE"),
    ]

    # Proficiency decay rate per day of inactivity
    DECAY_RATE_PER_DAY = 0.005

    # Maximum proficiency gain per practice session
    MAX_PRACTICE_GAIN = 0.05

    # Diminishing returns factor (practice gets less effective over time)
    DIMINISHING_FACTOR = 0.92

    def __init__(
        self,
        name: str,
        category: str = "general",
        description: str = "",
        knowledge: float = 0.0,
        proficiency: float = 0.0,
    ):
        self.name = name
        self.category = category
        self.description = description
        self._knowledge = max(0.0, min(1.0, knowledge))
        self._proficiency = max(0.0, min(1.0, proficiency))
        self.acquired_at = datetime.now(tz=UTC)
        self.last_practiced = datetime.now(tz=UTC)
        self.practice_count = 0
        self.practice_log: list[dict[str, Any]] = []

    # ── Properties ──────────────────────────────────────────────

    @property
    def knowledge(self) -> float:
        """Knowledge score (0.0 → 1.0). Does not decay."""
        return self._knowledge

    @knowledge.setter
    def knowledge(self, value: float) -> None:
        self._knowledge = max(0.0, min(1.0, value))

    @property
    def proficiency(self) -> float:
        """Proficiency score with decay applied."""
        return max(0.0, min(self._proficiency, self._knowledge))

    @proficiency.setter
    def proficiency(self, value: float) -> None:
        # Proficiency cannot exceed knowledge
        self._proficiency = max(0.0, min(value, self._knowledge))

    @property
    def tier(self) -> str:
        """Current mastery tier based on proficiency."""
        for threshold, name in self.TIERS:
            if self.proficiency >= threshold:
                return name
        return "NOVICE"

    @property
    def gap(self) -> float:
        """The gap between knowledge and proficiency (what needs practice)."""
        return max(0.0, self._knowledge - self.proficiency)

    @property
    def days_since_practice(self) -> float:
        """Days since last practice session."""
        delta = datetime.now(tz=UTC) - self.last_practiced
        return delta.total_seconds() / 86400.0

    # ── Core Methods ────────────────────────────────────────────

    def learn(self, amount: float = 0.1) -> float:
        """
        Increase knowledge (encountering new information).

        Args:
            amount: Knowledge increment (0.0 → 1.0)

        Returns:
            New knowledge level
        """
        old = self._knowledge
        self._knowledge = min(1.0, self._knowledge + amount)
        return self._knowledge - old

    def practice(self, success_rate: float = 0.5) -> dict[str, Any]:
        """
        Attempt to practice the skill. Proficiency gain depends on
        success rate and diminishing returns.

        Args:
            success_rate: How well the practice attempt went (0.0 → 1.0)

        Returns:
            Practice result with gain, new proficiency, and tier
        """
        # Apply decay first
        self._apply_decay()

        # Calculate gain with diminishing returns
        diminish = self.DIMINISHING_FACTOR**self.practice_count
        raw_gain = self.MAX_PRACTICE_GAIN * success_rate * diminish

        # Scale gain by the gap (harder to improve when close to knowledge ceiling)
        gap_factor = max(0.1, self.gap)
        gain = raw_gain * gap_factor

        old_proficiency = self.proficiency
        old_tier = self.tier

        self.proficiency = self._proficiency + gain
        self.practice_count += 1
        self.last_practiced = datetime.now(tz=UTC)

        result = {
            "skill": self.name,
            "success_rate": success_rate,
            "gain": gain,
            "old_proficiency": old_proficiency,
            "new_proficiency": self.proficiency,
            "old_tier": old_tier,
            "new_tier": self.tier,
            "tier_up": self.tier != old_tier,
            "practice_count": self.practice_count,
            "timestamp": self.last_practiced.isoformat(),
        }

        self.practice_log.append(result)

        # Keep log bounded
        if len(self.practice_log) > 100:
            self.practice_log = self.practice_log[-100:]

        return result

    def _apply_decay(self) -> float:
        """Apply proficiency decay based on time since last practice."""
        days = self.days_since_practice
        if days < 1.0:
            return 0.0

        decay = self.DECAY_RATE_PER_DAY * days
        old = self._proficiency
        self._proficiency = max(0.0, self._proficiency - decay)
        return old - self._proficiency

    # ── Serialization ───────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Serialize skill to dictionary."""
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "knowledge": self._knowledge,
            "proficiency": self._proficiency,
            "acquired_at": self.acquired_at.isoformat(),
            "last_practiced": self.last_practiced.isoformat(),
            "practice_count": self.practice_count,
            "tier": self.tier,
            "gap": self.gap,
            "practice_log": self.practice_log[-10:],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Skill":
        """Deserialize skill from dictionary."""
        skill = cls(
            name=data["name"],
            category=data.get("category", "general"),
            description=data.get("description", ""),
            knowledge=data.get("knowledge", 0.0),
            proficiency=data.get("proficiency", 0.0),
        )
        if "acquired_at" in data:
            skill.acquired_at = datetime.fromisoformat(data["acquired_at"])
        if "last_practiced" in data:
            skill.last_practiced = datetime.fromisoformat(data["last_practiced"])
        skill.practice_count = data.get("practice_count", 0)
        skill.practice_log = data.get("practice_log", [])
        return skill

    def __repr__(self) -> str:
        return (
            f"Skill('{self.name}', knowledge={self._knowledge:.2f}, "
            f"proficiency={self.proficiency:.2f}, tier='{self.tier}')"
        )


__all__ = ["Skill"]
