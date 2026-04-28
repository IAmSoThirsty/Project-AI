#!/usr/bin/env python3
"""Validate mandatory structured-generation protocol wiring for all repo agents.

This script enforces that the repository's authoritative agent instruction surfaces
all reference the mandatory coding default protocol.
"""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
MANDATORY_INSTRUCTION_PATH = ".github/instructions/mandatory-structured-generation-default.instructions.md"


REQUIRED_SUBSTRINGS: dict[str, list[str]] = {
    MANDATORY_INSTRUCTION_PATH: [
        "Mandatory Structured Generation & Adversarial Review Default",
        "Required Sequential Process (Mandatory Order)",
        "Any coding output that skips this protocol is non-compliant",
    ],
    "AGENTS.md": [
        "Mandatory Coding Default (All Agents and IDE Copilots)",
        MANDATORY_INSTRUCTION_PATH,
    ],
    ".github/COPILOT_MANDATORY_GUIDE.md": [
        "RULE 8: MANDATORY STRUCTURED GENERATION & ADVERSARIAL REVIEW DEFAULT",
        MANDATORY_INSTRUCTION_PATH,
    ],
    ".github/copilot_workspace_profile.md": [
        "### 1.1. Mandatory Structured Generation & Adversarial Review Default",
        MANDATORY_INSTRUCTION_PATH,
    ],
    ".github/copilot-instructions.md": [
        "## 🔧 MANDATORY CODING DEFAULT (ALL AGENTS / IDE COPILOTS)",
        MANDATORY_INSTRUCTION_PATH,
    ],
}


def validate_frontmatter_apply_to(text: str) -> bool:
    """Ensure mandatory instruction applies to all files by default."""
    return bool(re.search(r"^applyTo:\s*\"\*\*\"\s*$", text, flags=re.MULTILINE))


def main() -> int:
    errors: list[str] = []

    for relative_path, required_phrases in REQUIRED_SUBSTRINGS.items():
        file_path = ROOT / relative_path
        if not file_path.exists():
            errors.append(f"Missing required file: {relative_path}")
            continue

        text = file_path.read_text(encoding="utf-8")

        for phrase in required_phrases:
            if phrase not in text:
                errors.append(
                    f"Missing required content in {relative_path}: '{phrase}'"
                )

        if relative_path == MANDATORY_INSTRUCTION_PATH:
            if not validate_frontmatter_apply_to(text):
                errors.append(
                    "Mandatory instruction file must include frontmatter applyTo: \"**\""
                )

    if errors:
        print("❌ Agent governance default validation FAILED")
        for item in errors:
            print(f" - {item}")
        return 1

    print("✅ Agent governance default validation PASSED")
    print("   Mandatory structured generation protocol is wired across all required agent surfaces.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
