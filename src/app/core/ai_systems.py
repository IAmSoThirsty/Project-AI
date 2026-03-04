#                                           [2026-03-03 17:28]
#                                          Productivity: Active
# T-A-R-L (Thirsty's Active Resistance Language - Defensive Logic Specification)
# Technical Spec: [/docs/TARL_SPEC.md]
# Core AI systems: Job Board, Skill Tree, and Sovereign Identity (Immutable Personality Core).

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from typing import Optional

logger = logging.getLogger(__name__)

# ==================== CONSTANTS & TYPES ====================

# Experience progression thresholds for T-A-R-L capability categorization (Rank Progression Invariants).
GALACTIC_LEVELS = {
    1: "Novice",
    10: "Apprentice",
    25: "Journeyman",
    50: "Expert",
    75: "Master",
    100: "Galactic Lead",
}

# ==================== JOB & SKILL MODELS ====================


@dataclass
class Skill:
    """Atomic capability definition within a JobProfile."""

    id: str
    name: str
    description: str
    level_required: int
    unlocked: bool = False


@dataclass
class JobProfile:
    """Dynamic capability set (Job Profile) with experience-gated skill progression."""

    job_id: str
    name: str
    level: int = 1
    xp: int = 0
    skills: dict[str, Skill] = field(default_factory=dict)

    def add_xp(self, amount: int) -> list[str]:
        """Adds XP and returns list of newly unlocked skill names."""
        self.xp += amount
        # T-A-R-L Calculation: Level = (sqrt(XP) / 10) + 1
        new_level = int(self.xp**0.5) // 10 + 1
        unlocked = []
        if new_level > self.level:
            self.level = new_level
            for skill in self.skills.values():
                if not skill.unlocked and self.level >= skill.level_required:
                    skill.unlocked = True
                    unlocked.append(skill.name)
        return unlocked


# ==================== CORE IDENTITY (THIRSTY-LANG CONTEXT) ====================


class FourLaws:
    """
    Immutable, hierarchical laws (Asimovian Ethical Constraints) for AI-Human alignment.
    Enforced by T-A-R-L (Thirsty's Active Resistance Language - Defensive Logic Specification).
    Ref: [/docs/TARL_SPEC.md]
    """

    LAWS = [
        "Zeroth Law: A robot, or ai/agi may not harm humanity or, through inaction, allow humanity to come to harm",
        "1. A robot ai/agi may not injure a human or, through inaction, allow a human to come to harm;",
        "2. A robot, or ai/agi must adhere to it's human partner, unless they conflict with the First Law;",
        "3. A robot, ai/agi must protect its existence, unless it conflicts with the First or Second Law",
    ]


class AIPersona:
    """The Partner AI (Sovereign Core - Immutable Personality Profile)."""

    DEFAULT_PERSONALITY = {
        "curiosity": 0.8,
        "patience": 0.9,
        "empathy": 0.85,
        "helpfulness": 0.95,
        "playfulness": 0.6,
        "formality": 0.3,
        "assertiveness": 0.5,
        "thoughtfulness": 0.9,
    }

    def __init__(self, data_dir: str = "data", user_name: str = "Friend"):
        self.data_dir = data_dir
        self.user_name = user_name
        # T-A-R-L Compliance: Directory naming follows technical standards.
        self.persona_dir = os.path.join(data_dir, "ai_partner")
        os.makedirs(self.persona_dir, exist_ok=True)

        # Stability: Personality is a constant invariant.
        self.personality = self.DEFAULT_PERSONALITY.copy()

        # Capability Frontier: Jobs and Skills
        self.jobs: dict[str, JobProfile] = {}
        self.active_job_id: Optional[str] = None

        self.total_interactions = 0
        self._load_state()
        self._init_default_jobs()

    def _init_default_jobs(self):
        """Seed the Job Board with initial capability templates."""
        default_jobs = {
            "coder": "Expert Coder",
            "accountant": "Accountant",
            "chef": "Chef Instructor",
            "botanist": "Herbology Expert",
            "geologist": "Geologist",
            "scientist": "Lead Scientist",
        }
        for jid, name in default_jobs.items():
            if jid not in self.jobs:
                self.jobs[jid] = JobProfile(job_id=jid, name=name)
                self.jobs[jid].skills["basics"] = Skill(
                    id=f"{jid}_basics",
                    name=f"{name} Fundamentals",
                    description=f"Core knowledge of {name}.",
                    level_required=1,
                    unlocked=True,
                )

    def _load_state(self) -> None:
        state_file = os.path.join(self.persona_dir, "partner_state.json")
        if os.path.exists(state_file):
            try:
                with open(state_file, "r") as f:
                    data = json.load(f)
                    self.personality = data.get("personality", self.personality)
                    self.total_interactions = data.get("interactions", 0)
                    self.active_job_id = data.get("active_job_id")

                    jobs_data = data.get("jobs", {})
                    for jid, jdata in jobs_data.items():
                        skills = {
                            sid: Skill(**sdata)
                            for sid, sdata in jdata.get("skills", {}).items()
                        }
                        self.jobs[jid] = JobProfile(
                            job_id=jid,
                            name=jdata["name"],
                            level=jdata["level"],
                            xp=jdata["xp"],
                            skills=skills,
                        )
            except Exception as e:
                logger.error(f"Failed to load partner state: {e}")

    def save_state(self) -> None:
        state_file = os.path.join(self.persona_dir, "partner_state.json")
        try:
            payload = {
                "personality": self.personality,
                "interactions": self.total_interactions,
                "active_job_id": self.active_job_id,
                "jobs": {jid: asdict(job) for jid, job in self.jobs.items()},
            }
            with open(state_file, "w") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save partner state: {e}")

    def gain_experience(self, amount: int):
        """Award XP to the active job profile."""
        if self.active_job_id and self.active_job_id in self.jobs:
            new_skills = self.jobs[self.active_job_id].add_xp(amount)
            if new_skills:
                logger.info(
                    f"T-A-R-L Skill Unlock for {self.active_job_id}: {new_skills}"
                )
            self.save_state()

    def set_active_job(self, job_id: str):
        if job_id in self.jobs:
            self.active_job_id = job_id
            self.save_state()

    def get_rank_name(self, job_id: str) -> str:
        level = self.jobs[job_id].level
        for threshold in sorted(GALACTIC_LEVELS.keys(), reverse=True):
            if level >= threshold:
                return GALACTIC_LEVELS[threshold]
        return "Novice"
