# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / build_sovereign_agent.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / build_sovereign_agent.py

#
# COMPLIANCE: Sovereign Substrate / build_sovereign_agent.py


# Master Sovereign Builder Orchestration Script
# ---------------------------------------------
#                                             Date: 2026-03-02 04:47
#                                             Status: Active
#                                             Productivity: Active

"""
Full pipeline: Data -> Training -> Merge -> Quantization -> Modelfile.
Chains all sub-scripts into a single command for any of the 14 agents.
"""

import subprocess
import sys
import os


def run_step(command):
    print(f"Executing: {' '.join(command)}")
    result = subprocess.run(command, capture_output=False)
    if result.returncode != 0:
        print(f"Error executing: {' '.join(command)}")
        sys.exit(1)


def build_agent(agent_name):
    print(f"### SOVEREIGN BUILDING COMMENCED: {agent_name} ###")

    run_step(["python", "scripts/build_training_data.py"])
    run_step(["python", "scripts/train_sovereign.py"])
    run_step(["python", "scripts/merge_and_quantize.py"])
    run_step(["python", "scripts/generate_modelfile.py"])

    print(f"### SOVEREIGN BUILDING COMPLETE: {agent_name} ###")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/build_sovereign_agent.py <agent_name>")
        build_agent("galahad")
    else:
        build_agent(sys.argv[1])
