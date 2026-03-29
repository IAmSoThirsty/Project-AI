# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / archive_agent.py
# ============================================================================ #
import os
import shutil
from datetime import datetime



               #
# COMPLIANCE: Absolute Sovereignty Archive Protocol                            #



ARCHIVE_DIR = r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI\archive\history"
ORPHANED_DIR = r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI\archive\orphaned"
DATE_STAMP = datetime.now().strftime("%Y%m%d")

CANDIDATES = [
    r"src\app\gui\archive\dashboard_utils_legacy.py",
    r"src\app\gui\archive\dashboard_main_legacy.py",
    r"src\app\gui\archive\dashboard_handlers_legacy.py",
    # Add other identified legacy files here
]

def execute_archive():
    if not os.path.exists(ARCHIVE_DIR): os.makedirs(ARCHIVE_DIR)
    
    for relative_path in CANDIDATES:
        full_path = os.path.join(r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI", relative_path)
        if os.path.exists(full_path):
            # Preserve path in filename
            new_name = relative_path.replace("\\", "_").replace("/", "_") + f"_{DATE_STAMP}.py"
            target_path = os.path.join(ARCHIVE_DIR, new_name)
            
            shutil.move(full_path, target_path)
            
            # Create .archive.md companion
            with open(target_path + ".archive.md", 'w') as f:
                f.write(f"# ARCHIVE RECORD\n\n- **Original Path**: {relative_path}\n- **Archive Date**: {DATE_STAMP}\n- **Reason**: Superseded by Phase 12/13 sovereign implementation.\n")
            
            print(f"ARCHIVED: {relative_path} -> {new_name}")

if __name__ == "__main__":
    execute_archive()
