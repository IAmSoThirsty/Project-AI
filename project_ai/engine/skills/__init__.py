#                                           [2026-03-04 13:36]
#                                          Productivity: Active
"""
Skills Engine
=============

Engine subsystem for skill acquisition, practice, and self-improvement.

The skills engine introduces the distinction between KNOWLEDGE
(understanding a concept) and PROFICIENCY (being able to execute it).
Skills are tools in the AGI's belt — they do not alter its base
personality or identity.

Core Design Principles:
  - Identity is immutable. Skills are additive.
  - Knowledge does not decay. Proficiency does.
  - Practice is the only path from knowing to doing.
  - Offline time is reflection time.

Submodules:
  - skill: The Skill data model (knowledge, proficiency, tiers, decay)
  - skill_manager: The SkillManager orchestrator (acquire, practice, reflect)
"""

from .skill import Skill
from .skill_manager import SkillManager

__all__ = ["Skill", "SkillManager"]
