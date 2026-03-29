# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / global_sovereignty_validator.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / global_sovereignty_validator.py

#
# COMPLIANCE: Sovereign-Native / Thirsty-Lang v3.5                             #



import os
from pathlib import Path

BASE_PATH = Path(r"c:\Users\Quencher\Desktop\Github\Personal Repo's\1")
REPOS = [item.name for item in BASE_PATH.iterdir() if item.is_dir()]

REQUIRED_FILES = [
    "docs/sovereignty/THIRSTY_LANG_MANIFESTO.md",
    "src/foundation/THIRSTY_LANG_SPEC.thirsty",
    "src/app/core/thirsty_native_bridge.py"
]

def validate_sovereignty():
    print(f"{'='*80}")
    print(f"SOVEREIGNTY VALIDATION SCAN - v3.5 (WAVE 8 FINAL)")
    print(f"{'='*80}")
    
    total_compliance = True
    
    for repo in REPOS:
        repo_path = BASE_PATH / repo
        print(f"\n[REPO] {repo}")
        
        if not repo_path.exists():
            print(f"  [ERROR] Repository path not found: {repo_path}")
            total_compliance = False
            continue
            
        repo_compliant = True
        # Skip required files check for Miniature-Office as it's a special IDE project
        if repo != "Thirstys-Projects-Miniature-Office":
            for req_file in REQUIRED_FILES:
                file_path = repo_path / req_file
                if file_path.exists():
                    print(f"  [OK] Found: {req_file}")
                else:
                    print(f"  [MISSING] {req_file}")
                    repo_compliant = False
                    total_compliance = False
                
        # Check README/CODEX for Sovereign-Native / Master Tier compliance
        if repo == "Thirstys-Projects-Miniature-Office":
            readme_path = repo_path / "COMPLETE_LANGUAGE_CODEX.md"
        else:
            readme_path = repo_path / "README.md"
            
        if readme_path.exists():
            content = readme_path.read_text(encoding="utf-8", errors="ignore").lower()
            if "sovereign" in content and "master" in content:
                print(f"  [OK] File contains Master Tier & Sovereign compliance badges.")
            else:
                print(f"  [MISSING] Master Tier / Sovereign indicators in {readme_path.name}.")
                repo_compliant = False
                total_compliance = False
        
        if repo_compliant:
            print(f"  [STATUS] COMPLIANT (MASTER TIER)")
        else:
            print(f"  [STATUS] NON-COMPLIANT")
            
    print(f"\n{'='*80}")
    if total_compliance:
        print(f"GLOBAL COMPLIANCE VERIFIED: WAVE 8 IS SOVEREIGN-NATIVE.")
    else:
        print(f"GLOBAL COMPLIANCE FAILED: Remediation required.")
    print(f"{'='*80}")

if __name__ == "__main__":
    validate_sovereignty()
