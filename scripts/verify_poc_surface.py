from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
MANIFEST = ROOT / "docs" / "VERIFIED_POC_MANIFEST.md"
POLICY = ROOT / "docs" / "POC_BRANCH_POLICY.md"
START_HERE = ROOT / "docs" / "START_HERE.md"
REVIEWER_GUIDE = ROOT / "docs" / "REVIEWER_GUIDE.md"
PR_TEMPLATE = ROOT / ".github" / "pull_request_template.md"
BUG_TEMPLATE = ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.md"
FEATURE_TEMPLATE = ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.md"
REQUIRED_README_PHRASES = [
    "Project-AI",
    "Start Here For Newcomers",
    "Verified Proofs Of Concept",
    "Verified POC Manifest",
    "Reviewer Guide",
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
REQUIRED_START_HERE_PHRASES = [
    "First Five Minutes",
    "What To Run First",
    "If a capability is not in the verified manifest",
]
REQUIRED_REVIEWER_GUIDE_PHRASES = [
    "Review Order",
    "What Counts As Verified",
    "What Does Not Count As Verified",
]
REQUIRED_TEMPLATE_PHRASES = [
    "Evidence",
    "Scope Boundary",
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
    require_phrases(START_HERE, REQUIRED_START_HERE_PHRASES)
    require_phrases(REVIEWER_GUIDE, REQUIRED_REVIEWER_GUIDE_PHRASES)
    require_phrases(PR_TEMPLATE, REQUIRED_TEMPLATE_PHRASES)
    require_phrases(BUG_TEMPLATE, ["Reproduction", "Evidence"])
    require_phrases(FEATURE_TEMPLATE, ["Verification", "Scope Boundary"])
    require_file(POLICY)
    print("Verified POC branch surface checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
