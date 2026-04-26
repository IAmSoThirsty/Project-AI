#                                           [2026-03-04 13:36]
#                                          Productivity: Active
"""
Skills Engine — Skill Manager
==============================

Manages the AGI's skill inventory: acquisition, practice, decay,
reflection, and the offline self-improvement loop.

The SkillManager integrates with:
  - StateManager: persists skill state across sessions
  - IdentityManager: personality remains immutable regardless of skills
  - CapabilityInvoker: skills translate into executable capabilities
  - DeliberationEngine: reflection loop for offline practice

Core Design:
  - Base personality (identity) never changes — skills are tools in the belt
  - Knowledge ≠ Proficiency — knowing about cooking ≠ being able to cook
  - Offline time = practice time — the AGI reflects and practices weak skills
  - Proficiency decays without practice — use it or lose it
"""

from datetime import timezone, datetime
from typing import TYPE_CHECKING, Any

from .skill import Skill

if TYPE_CHECKING:
    from ..state.state_manager import StateManager


class SkillManager:
    """
    Manages the AGI's complete skill inventory.

    Responsibilities:
      - Skill acquisition (learning new skills)
      - Skill practice (improving proficiency through execution)
      - Skill decay (proficiency fades without practice)
      - Skill reflection (offline self-assessment and practice)
      - Skill inventory (querying, sorting, recommending)
    """

    # State key for persistence
    STATE_KEY = "skill_inventory"

    # Maximum skills to practice per reflection cycle
    MAX_PRACTICE_PER_CYCLE = 3

    # Minimum gap between knowledge and proficiency to trigger practice
    MIN_PRACTICE_GAP = 0.1

    def __init__(self, state_manager: "StateManager", config: dict | None = None):
        self.state_manager = state_manager
        self.config = config or {}
        self.skills: dict[str, Skill] = {}
        self._reflection_log: list[dict[str, Any]] = []
        self._load_from_state()

    # ── Skill Acquisition ───────────────────────────────────────

    def acquire(
        self,
        name: str,
        category: str = "general",
        description: str = "",
        initial_knowledge: float = 0.1,
    ) -> Skill:
        """
        Acquire a new skill or deepen knowledge of an existing one.

        If the skill already exists, knowledge is increased.
        Proficiency is NOT automatically increased — that requires practice.

        Args:
            name: Skill identifier
            category: Skill category (e.g., 'programming', 'analysis', 'communication')
            description: Human-readable description
            initial_knowledge: Starting knowledge level for new skills

        Returns:
            The acquired or updated Skill
        """
        if name in self.skills:
            skill = self.skills[name]
            gained = skill.learn(initial_knowledge)
            self._log_event(
                "deepen", name, f"Knowledge +{gained:.3f} → {skill.knowledge:.3f}"
            )
        else:
            skill = Skill(
                name=name,
                category=category,
                description=description,
                knowledge=initial_knowledge,
                proficiency=0.0,
            )
            self.skills[name] = skill
            self._log_event(
                "acquire",
                name,
                f"New skill acquired (knowledge={initial_knowledge:.2f})",
            )

        self._persist()
        return skill

    # ── Skill Practice ──────────────────────────────────────────

    def practice(self, name: str, success_rate: float = 0.5) -> dict[str, Any]:
        """
        Practice a skill to improve proficiency.

        Args:
            name: Skill to practice
            success_rate: How well the practice went (0.0 → 1.0)

        Returns:
            Practice result dictionary

        Raises:
            KeyError: If skill not found
        """
        if name not in self.skills:
            raise KeyError(f"Skill not found: {name}")

        result = self.skills[name].practice(success_rate)

        if result["tier_up"]:
            self._log_event(
                "tier_up",
                name,
                f"TIER UP: {result['old_tier']} → {result['new_tier']}",
            )
        else:
            self._log_event(
                "practice",
                name,
                f"Proficiency +{result['gain']:.4f} → {result['new_proficiency']:.3f}",
            )

        self._persist()
        return result

    # ── Offline Reflection Loop ─────────────────────────────────

    def reflect(self) -> list[dict[str, Any]]:
        """
        Run the offline reflection loop.

        This is called when the user goes offline. The AGI:
          1. Reviews its skill inventory
          2. Identifies skills with the largest knowledge-proficiency gap
          3. Practices the weakest skills (simulated)
          4. Logs the reflection episode

        Returns:
            List of practice results from the reflection session
        """
        now = datetime.now(tz=UTC)
        results: list[dict[str, Any]] = []

        # Find skills that need practice (sorted by gap, largest first)
        practice_candidates = sorted(
            [s for s in self.skills.values() if s.gap >= self.MIN_PRACTICE_GAP],
            key=lambda s: s.gap,
            reverse=True,
        )

        if not practice_candidates:
            self._log_event(
                "reflect",
                "no_gaps",
                "All skills within acceptable gap. No practice needed.",
            )
            return results

        # Practice the top N skills
        for skill in practice_candidates[: self.MAX_PRACTICE_PER_CYCLE]:
            # Simulate practice: success rate is based on current proficiency
            # (you get better at practicing things you already somewhat know)
            base_success = max(0.2, skill.proficiency * 0.8 + 0.1)
            # Add some variance
            import random

            success = min(1.0, max(0.0, base_success + random.uniform(-0.1, 0.15)))

            result = skill.practice(success)
            result["reflection"] = True
            result["reflection_time"] = now.isoformat()
            results.append(result)

        reflection_summary = {
            "timestamp": now.isoformat(),
            "skills_reviewed": len(self.skills),
            "skills_practiced": len(results),
            "results": [
                {
                    "skill": r["skill"],
                    "gain": r["gain"],
                    "new_proficiency": r["new_proficiency"],
                    "tier": r["new_tier"],
                }
                for r in results
            ],
        }

        self._reflection_log.append(reflection_summary)
        if len(self._reflection_log) > 50:
            self._reflection_log = self._reflection_log[-50:]

        self._log_event(
            "reflect",
            "complete",
            f"Practiced {len(results)} skills during reflection",
        )

        self._persist()
        return results

    # ── Skill Inventory ─────────────────────────────────────────

    def get_skill(self, name: str) -> Skill | None:
        """Get a skill by name."""
        return self.skills.get(name)

    def list_skills(
        self,
        category: str | None = None,
        sort_by: str = "proficiency",
    ) -> list[Skill]:
        """
        List all skills, optionally filtered and sorted.

        Args:
            category: Filter by category (None = all)
            sort_by: Sort key ('proficiency', 'knowledge', 'gap', 'name')

        Returns:
            Sorted list of skills
        """
        skills = list(self.skills.values())

        if category:
            skills = [s for s in skills if s.category == category]

        sort_keys = {
            "proficiency": lambda s: s.proficiency,
            "knowledge": lambda s: s.knowledge,
            "gap": lambda s: s.gap,
            "name": lambda s: s.name,
            "tier": lambda s: s.proficiency,
        }

        key_fn = sort_keys.get(sort_by, sort_keys["proficiency"])
        reverse = sort_by != "name"

        return sorted(skills, key=key_fn, reverse=reverse)

    def get_weakest_skills(self, limit: int = 5) -> list[Skill]:
        """Get skills with the largest knowledge-proficiency gap."""
        return sorted(
            self.skills.values(),
            key=lambda s: s.gap,
            reverse=True,
        )[:limit]

    def get_strongest_skills(self, limit: int = 5) -> list[Skill]:
        """Get skills with the highest proficiency."""
        return sorted(
            self.skills.values(),
            key=lambda s: s.proficiency,
            reverse=True,
        )[:limit]

    def get_categories(self) -> list[str]:
        """Get all unique skill categories."""
        return sorted({s.category for s in self.skills.values()})

    def get_inventory_summary(self) -> dict[str, Any]:
        """Get a high-level summary of the skill inventory."""
        if not self.skills:
            return {
                "total_skills": 0,
                "categories": [],
                "avg_knowledge": 0.0,
                "avg_proficiency": 0.0,
                "tier_distribution": {},
            }

        skills = list(self.skills.values())
        tier_dist: dict[str, int] = {}
        for s in skills:
            tier_dist[s.tier] = tier_dist.get(s.tier, 0) + 1

        return {
            "total_skills": len(skills),
            "categories": self.get_categories(),
            "avg_knowledge": sum(s.knowledge for s in skills) / len(skills),
            "avg_proficiency": sum(s.proficiency for s in skills) / len(skills),
            "tier_distribution": tier_dist,
            "weakest": [s.name for s in self.get_weakest_skills(3)],
            "strongest": [s.name for s in self.get_strongest_skills(3)],
            "reflection_count": len(self._reflection_log),
        }

    # ── Persistence ─────────────────────────────────────────────

    def _persist(self) -> None:
        """Save skill inventory to state."""
        self.state_manager.save_state(
            self.STATE_KEY,
            {
                "skills": {
                    name: skill.to_dict() for name, skill in self.skills.items()
                },
                "reflection_log": self._reflection_log[-20:],
            },
        )

    def _load_from_state(self) -> None:
        """Load skill inventory from state."""
        data = self.state_manager.load_state(self.STATE_KEY)
        if not data:
            return

        skills_data = data.get("skills", {})
        for name, skill_dict in skills_data.items():
            self.skills[name] = Skill.from_dict(skill_dict)

        self._reflection_log = data.get("reflection_log", [])

    # ── Internal Logging ────────────────────────────────────────

    def _log_event(self, event_type: str, skill_name: str, detail: str) -> None:
        """Record a skill event to episodic state."""
        self.state_manager.record_episode(
            {
                "subsystem": "skills",
                "event": event_type,
                "skill": skill_name,
                "detail": detail,
                "timestamp": datetime.now(tz=UTC).isoformat(),
            }
        )


__all__ = ["SkillManager"]
