# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / restore_thirst_branding.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / restore_thirst_branding.py


import os
import re

# Restoration of the Thirst of Gods Branding
# As per user correction: "Restore anything labeled Thirst Of Gods"

AUDIT_LOG_FILE = "governance/THEATRICAL_NAMING_AUDIT.md"

def restore_thirst():
    if not os.path.exists(AUDIT_LOG_FILE):
        print(f"Audit log {AUDIT_LOG_FILE} not found. Skipping restoration.")
        return

    with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Find rows where "Thirst of Gods" (or variants) was replaced
    # Format: | Original Name | Associated File | Replacement Term | Type |
    matches = re.findall(r"\| (Thirst[ _]of[ _]Gods|THIRST[ _]OF[ _]GODS) \| `(.*?)` \| (.*?) \| (.*?) \|", content)

    for original, file_path, replacement, entry_type in matches:
        full_path = os.path.join(os.getcwd(), file_path)
        if not os.path.exists(full_path):
            print(f"File not found: {full_path}")
            continue

        print(f"Restoring '{original}' in {file_path} (replacing '{replacement}')")
        
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                file_content = f.read()
            
            # Revert the replacement
            # Note: We use escape for replacement in case it has special characters
            new_content = file_content.replace(replacement, original)
            
            if new_content != file_content:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Successfully restored '{original}' in {file_path}")
            else:
                print(f"No changes needed for {file_path} (already restored or replacement not found)")
        except Exception as e:
            print(f"Failed to restore {file_path}: {e}")

if __name__ == "__main__":
    restore_thirst()
