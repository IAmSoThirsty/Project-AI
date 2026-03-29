# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / verify_job_board.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / verify_job_board.py

#
# COMPLIANCE: Sovereign Substrate / verify_job_board.py


# Verification Script for Galactic Job Board & Skill Progression
from src.app.core.ai_systems import AIPersona, Skill
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JobBoardVerify")


def verify_galactic_progression():
    print("\n--- [GALACTIC JOB BOARD VERIFICATION] ---")

    # Initialize Partner
    partner = AIPersona(data_dir="temp_data", user_name="Thirsty")

    # 1. Set Job
    print("\n[Step 1] Selecting 'Expert Coder' Job...")
    partner.set_active_job("coder")
    print(f"Active Job: {partner.jobs['coder'].name}")
    print(
        f"Current Rank: {partner.get_rank_name('coder')} (Level {partner.jobs['coder'].level})"
    )

    # 2. Add Custom High-Tier Skill
    print("\n[Step 2] Registering 'Galactic Architecture' Skill (Requires Level 20)...")
    partner.jobs["coder"].skills["galactic_arch"] = Skill(
        id="coder_galactic_arch",
        name="Galactic Architecture",
        description="Core skill for Cathedral Density design.",
        level_required=20,
    )

    # 3. Grind XP
    print("\n[Step 3] Simulating High-Level Interaction (Gaining 40,000 XP)...")
    # Formula is Level = sqrt(XP)/10 + 1. sqrt(40000) = 200. 200/10 + 1 = 21.
    partner.gain_experience(40000)

    # 4. Check Results
    new_level = partner.jobs["coder"].level
    new_rank = partner.get_rank_name("coder")
    skill_unlocked = partner.jobs["coder"].skills["galactic_arch"].unlocked

    print(f"\n[RESULTS]")
    print(f"New Level: {new_level}")
    print(f"New Rank: {new_rank}")
    print(
        f"Galactic Architecture Unlocked: {'✅ SUCCESS' if skill_unlocked else '❌ FAILED'}"
    )

    if skill_unlocked and new_level >= 20:
        print("\n--- [VERIFICATION COMPLETE: GALACTIC TIER REACHED] ---")
    else:
        print("\n--- [VERIFICATION FAILED] ---")


if __name__ == "__main__":
    if not os.path.exists("temp_data"):
        os.makedirs("temp_data")
    verify_galactic_progression()
