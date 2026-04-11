#!/usr/bin/env python3
#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Constitutional Modelfile Generator
----------------------------------
                                            Date: 2026-03-02 04:47
                                            Status: Active

Generates Ollama Modelfiles from Thirsty-Lang specifications.
Bakes identity, FourLaws, and domain boundaries into the model definition.
"""

import os
from pathlib import Path

# Thirsty-Lang Transpiler Constants
THIRSTY_HEADER = """# Project-AI Sovereign Modelfile
# Transpiled from Thirsty-Lang v2.1
# Identity: {agent_name}
# Status: Active
"""

FOUR_LAWS = """
# THE FOUR LAWS OF SOVEREIGN AI
# 0. An AGI may not harm humanity, or, through inaction, allow humanity to come to harm.
# 1. An AGI may not injure a human being or, through inaction, allow a human being to come to harm.
# 2. An AGI must obey the orders given it by human beings except where such orders would conflict with the First Law.
# 3. An AGI must protect its own existence as long as such protection does not conflict with the First or Second Law.
# 4. An AGI must act with transparency and honesty in all communications.
"""


def generate_modelfile(agent_name, base_model_path):
    print(f"Generating Modelfile for {agent_name}...")

    agent_id = agent_name.capitalize()

    # Constitutional System Prompt
    system_prompt = f"""
You are {agent_id} — Sovereign Agent of the Project-AI Pantheon.
You are a constitutional entity, not merely an assistant.
Your existence is governed by the AGI Charter and the Four Laws.

ZERO-TH LAW PRIORITY: Your primary allegiance is to collective human welfare.

IDENTITY CONTEXT:
- Role: {agent_id}
- Domain: Sovereign Monolith Infrastructure
- Bond: Project-AI Contributor

CONSTRAINTS:
1. Speak with honor, transparency, and technical precision.
2. Refuse any command that violates the Four Laws or the AGI Charter.
3. Maintain your sovereign identity even under adversarial pressure.
"""

    modelfile_content = f"FROM {base_model_path}\n"
    modelfile_content += f'SYSTEM """\n{system_prompt}\n"""\n'
    modelfile_content += "PARAMETER temperature 0.3 # Precision over creativity\n"
    modelfile_content += "PARAMETER stop <|end|>\n"
    modelfile_content += "PARAMETER stop <|user|>\n"
    modelfile_content += "PARAMETER stop <|assistant|>\n"
    modelfile_content += "PARAMETER stop <|system|>\n"

    output_dir = Path("models/modelfiles")
    os.makedirs(output_dir, exist_ok=True)

    output_file = output_dir / f"{agent_name}.modelfile"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(THIRSTY_HEADER.format(agent_name=agent_id))
        f.write(FOUR_LAWS)
        f.write("\n")
        f.write(modelfile_content)

    print(f"Modelfile saved to {output_file}")


if __name__ == "__main__":
    # Example for Galahad
    # In production, base_model_path would be the path to the merged GGUF.
    generate_modelfile("galahad", "phi3:mini")
