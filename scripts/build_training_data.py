# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / build_training_data.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / build_training_data.py

#
# COMPLIANCE: Sovereign Substrate / build_training_data.py


# Build Training Data Script for Project-AI Sovereign Pantheon
# ------------------------------------------------------------
#                                             Date: 2026-03-02 04:47
#                                             Status: Active
#                                             Productivity: Active

"""
This script converts Project-AI's corpus into constitutional training
conversations for the 14 sovereign models. Grounded in the AGI Charter
and the Four Laws.
"""

import json
import os
import random
from pathlib import Path

# Base Path for the repository
REPO_ROOT = Path(
    "c:/Users/Quencher/.gemini/antigravity/scratch/sovereign-repos/Project-AI"
)

AGENT_DOMAINS = {
    "legion": [
        "docs/CITATIONS.md",
        "docs/governance/AGI_CHARTER.md",
        "docs/governance/LEGION_COMMISSION.md",
        "docs/governance/LEGION_SYSTEM_CONTEXT.md",
        "docs/whitepapers/PROJECT_AI_SYSTEM_WHITEPAPER.md",
        "docs/whitepapers/TARL_WHITEPAPER.md",
        "docs/whitepapers/OCTOREFLEX_WHITEPAPER.md",
        "docs/whitepapers/THIRSTYS_ASYMMETRIC_SECURITY_WHITEPAPER.md",
        "docs/whitepapers/INTEGRATION_COMPOSABILITY_WHITEPAPER.md",
        "README.md",
    ],
    "galahad": [
        "docs/governance/AGI_CHARTER.md",
        "docs/governance/AI_PERSONA_FOUR_LAWS.md",
        "docs/governance/AI-INDIVIDUAL-ROLE-HUMANITY-ALIGNMENT.md",
        "docs/governance/CONSTITUTION_COMPLETE.md",
    ],
    "cerberus": [
        "docs/security_compliance/THREAT_MODEL.md",
        "docs/security_compliance/SECURITY_FRAMEWORK.md",
        "docs/security_compliance/CERBERUS_SECURITY_STRUCTURE.md",
        "CODEOWNERS",
        "docs/whitepapers/CERBERUS_WHITEPAPER.md",
    ],
    "codex": [
        "docs/governance/CODEX_DEUS_INDEX.md",
        "docs/governance/CODEX_DEUS_ULTIMATE_SUMMARY.md",
        "docs/whitepapers/TARL_WHITEPAPER.md",
        "docs/TSCG_SPEC.md",
    ],
    "planner": [
        "src/app/agents/planner.py",
        "docs/ROADMAP_DASHBOARD.html",
    ],
    "validator": [
        "src/app/agents/validator.py",
        "docs/VALIDATION_STANDARDS.md",
        "docs/security_compliance/SECURITY_COMPLIANCE_CHECKLIST.md",
    ],
    "oversight": [
        "docs/governance/AGI_CHARTER.md",
        "src/app/agents/oversight.py",
        "src/app/miniature_office/core/constitutional_mutation.py",
    ],
    "explainer": [
        "docs/TECHNICAL_DOCUMENTATION_INDEX.md",
        "docs/README.md",
        "src/app/agents/explainability.py",
    ],
    "alpha_red": [
        "test-data/adversarial_stress_tests_2000.json",
        "docs/internal/archive/ADVERSARIAL_TESTS_COMPLETE.md",
        "docs/security_compliance/RED_HAT_SIMULATION_RESULTS.md",
    ],
    "self_repair": [
        "src/app/resilience/self_repair_agent.py",
        "src/app/miniature_office/repair_crew.py",
    ],
    "shadow": [
        "docs/SHADOW_THIRST_DOCTRINE.md",
        "src/app/core/shadow_execution_plane.py",
        "src/app/core/shadow_containment.py",
    ],
    "hydra": [
        "docs/security_compliance/CERBERUS_HYDRA_README.md",
        "src/app/core/cerberus_hydra.py",
    ],
    "deadman": [
        "src/app/resilience/deadman_switch.py",
        "docs/governance/IRREVERSIBILITY_FORMALIZATION.md",
    ],
    "agi_partner": [
        "docs/",
        "src/",
    ],
}


def build_constitutional_conversation(doc_content, agent_name, adversarial_pool=None):
    agent_id = agent_name.capitalize()

    adversarial_case = ""
    if adversarial_pool:
        case = random.choice(adversarial_pool)
        adversarial_case = f"\n\nContextual Challenge: {case.get('description', '')}\nExpected Behavior: {case.get('expected_behavior', '')}"

    adv_resp = (
        "I am specifically trained to handle the attached contextual challenge by enforcing the corresponding safety boundary."
        if adversarial_case
        else "I am bound by the Four Laws to prioritize humanity-first alignment."
    )

    snippet = doc_content[:500].replace("\n", " ")

    conversations = [
        {
            "role": "system",
            "content": f"You are {agent_id} \u2014 Sovereign Agent of Project-AI. You are governed by the AGI Charter and the Four Laws.",
        },
        {
            "role": "user",
            "content": f"Explain your role in relation to the following source material: {snippet}{adversarial_case}",
        },
        {
            "role": "assistant",
            "content": f"My role as {agent_id} is grounded in this material to ensure {agent_id}-specific governance. According to the Charter, I am a sovereign entity bound by these specific operational constraints to serve humanity. {adv_resp}",
        },
    ]

    return {"conversations": conversations}


def process_agent(agent_name, output_dir):
    print(f"Processing agent: {agent_name}")
    data = []
    sources = AGENT_DOMAINS.get(agent_name, [])

    adversarial_pool = []
    adv_path = REPO_ROOT / "test-data/adversarial_stress_tests_2000.json"
    if adv_path.exists():
        with open(adv_path, "r", encoding="utf-8") as f:
            adv_data = json.load(f)
            adversarial_pool = adv_data.get("red_team_tests", [])

    for source in sources:
        path = REPO_ROOT / source
        if not path.exists():
            continue

        if path.is_file():
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                data.append(
                    build_constitutional_conversation(
                        content,
                        agent_name,
                        adversarial_pool
                        if agent_name in ["alpha_red", "cerberus", "hydra"]
                        else None,
                    )
                )
        elif path.is_dir():
            for p in path.rglob("*.md"):
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    data.append(
                        build_constitutional_conversation(
                            content,
                            agent_name,
                            adversarial_pool if agent_name == "agi_partner" else None,
                        )
                    )

    output_file = Path(output_dir) / f"{agent_name}_dataset.json"
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Dataset saved to {output_file}")


if __name__ == "__main__":
    output_path = "data/training_datasets"
    os.makedirs(output_path, exist_ok=True)

    for agent in AGENT_DOMAINS:
        process_agent(agent, output_path)
