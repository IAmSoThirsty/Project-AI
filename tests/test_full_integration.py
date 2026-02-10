import os
import sys

# Ensure the src directory is on the Python path
project_root = os.path.abspath(os.path.join(__file__, ".."))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from app.agents.codex_deus_maximus import create_codex


def main():
    # Instantiate the agent
    codex = create_codex()
    print("=== Running schematic enforcement ===")
    report = codex.run_schematic_enforcement()
    print("Enforcement report:")
    print(report)

    # Generate LLM insight
    prompt = "Summarize the repository structure and suggest any improvements based on the enforcement report."
    print("=== Generating GPT‑OSS 1208 insight ===")
    insight = codex.generate_gpt_oss(prompt)
    print("LLM Insight:")
    print(insight)


if __name__ == "__main__":
    main()
