from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
MANIFEST = ROOT / "docs" / "VERIFIED_POC_MANIFEST.md"
POLICY = ROOT / "docs" / "POC_BRANCH_POLICY.md"
REQUIRED_README_PHRASES = [
    "Project-AI",
    "Start Here For Newcomers",
    "Verified Proofs Of Concept",
    "Verified POC Manifest",
    "Branch Discipline",
    "Do not add a capability to this README unless",
]
REQUIRED_MANIFEST_PHRASES = [
    "POC-001: Caregiver Scribe",
    "POC-002: Personal-Agent CLI Access",
    "POC-003: Scribe Regression Tests",
    "POC-004: Branch-Face Verification",
    "Scope boundary",
    "Excluded From The Branch Face",
]


def require_file(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")
    return path.read_text(encoding="utf-8")


def require_phrases(path: Path, phrases: list[str]) -> None:
    text = require_file(path)
    missing = [phrase for phrase in phrases if phrase not in text]
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(f"{path} is missing required phrase(s): {joined}")


def main() -> int:
    require_phrases(README, REQUIRED_README_PHRASES)
    require_phrases(MANIFEST, REQUIRED_MANIFEST_PHRASES)
    require_file(POLICY)
    print("Verified POC branch surface checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
