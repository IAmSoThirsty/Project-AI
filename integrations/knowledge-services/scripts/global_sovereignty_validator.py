# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-11 | TIME: 04:00               #
# COMPLIANCE: Sovereign-Native / Thirsty-Lang v3.5                             #
# ============================================================================ #

from pathlib import Path

BASE_PATH = Path(r"c:\Users\Quencher\Desktop\Github\knowledge_services")
REPOS = [BASE_PATH]


REQUIRED_FILES = [
    "docs/sovereignty/THIRSTY_LANG_MANIFESTO.md",
    "src/foundation/THIRSTY_LANG_SPEC.thirsty",
    "src/app/core/thirsty_native_bridge.py",
    "README.md"
]


def validate_sovereignty():
    divider = "=" * 80
    print(divider)
    print("SOVEREIGNTY VALIDATION SCAN - v3.5 (WAVE 8 FINAL)")
    print(divider)

    total_compliance = True

    for repo in REPOS:
        # Since REPOS contains Path objects, use directly or get name
        repo_name = repo.name if isinstance(repo, Path) else str(repo)
        print(f"\n[REPO] {repo_name}")

        repo_compliant = True
        # Skip required files check for Miniature-Office
        if repo_name != "Thirstys-Projects-Miniature-Office":
            for req_file in REQUIRED_FILES:
                file_path = repo / req_file
                if file_path.exists():
                    print(f"  [OK] Found: {req_file}")
                else:
                    print(f"  [MISSING] {req_file}")
                    repo_compliant = False
                    total_compliance = False

        # Check README for Sovereign-Native / Master Tier compliance
        if repo_name == "Thirstys-Projects-Miniature-Office":
            readme_path = repo / "COMPLETE_LANGUAGE_CODEX.md"
        else:
            readme_path = repo / "README.md"

        if readme_path.exists():
            content = readme_path.read_text(
                encoding="utf-8", errors="ignore"
            ).lower()
            if "sovereign" in content and "master" in content:
                print("  [OK] File contains Master Tier & Sovereign badges.")
            else:
                msg = f"  [MISSING] Master Tier bits in {readme_path.name}."
                print(msg)
                repo_compliant = False
                total_compliance = False

        if repo_compliant:
            print("  [STATUS] COMPLIANT (MASTER TIER)")
        else:
            print("  [STATUS] NON-COMPLIANT")

    print(f"\n{divider}")
    if total_compliance:
        print("GLOBAL COMPLIANCE VERIFIED: WAVE 8 IS SOVEREIGN-NATIVE.")
    else:
        print("GLOBAL COMPLIANCE FAILED: Remediation required.")
    print(divider)


if __name__ == "__main__":
    validate_sovereignty()
