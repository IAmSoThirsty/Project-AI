# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / apply_path_integrity_fixes.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Path Integrity Corrector                               #



import json
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent.absolute()
MANIFEST = ROOT / "governance" / "PATH_INTEGRITY_MANIFEST.json"

def apply_fixes():
    if not MANIFEST.exists():
        print(f"Error: {MANIFEST} not found.")
        return

    with open(MANIFEST, "r", encoding="utf-8") as f:
        data = json.load(f)

    issues = data.get("issues", [])
    
    # Filter for high-confidence, non-environment, non-ambiguous fixes
    fixable = [
        i for i in issues 
        if i.get("severity") == "HIGH" 
        and not any(x in i["file"] for x in [".venv", ".venv_prod", "node_modules"])
        and not i["suggested_fix"].startswith("AMBIGUOUS")
        and ".venv" not in i["suggested_fix"]
    ]

    print(f"Found {len(fixable)} potential fixes.")

    # Group by file
    by_file = {}
    for i in fixable:
        path = i["file"]
        if path not in by_file:
            by_file[path] = []
        by_file[path].append(i)

    files_patched = 0
    total_fixes = 0

    for file_rel, file_issues in by_file.items():
        file_path = ROOT / file_rel
        if not file_path.exists():
            # Try switching backslashes to forward slashes for cross-plat
            file_path = ROOT / file_rel.replace('\\', '/')
            if not file_path.exists():
                print(f"Skipping missing file: {file_rel}")
                continue

        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except Exception as e:
            print(f"Error reading {file_rel}: {e}")
            continue

        patched = False
        # Sort issues by line number reverse to avoid any potential (though unlikely here) indexing drift
        # if we were adding/removing lines, but we are just replacing text on specific lines.
        file_issues.sort(key=lambda x: x["line"], reverse=True)

        for issue in file_issues:
            idx = issue["line"] - 1 # 1-indexed to 0-indexed
            if idx < 0 or idx >= len(lines):
                print(f"Line mismatch in {file_rel}: line {issue['line']} out of range.")
                continue

            old_line = lines[idx]
            broken = issue["broken_import"]
            fix = issue["suggested_fix"]

            # Precise replacement: only replace the broken import string if it exists in the line
            if broken in old_line:
                new_line = old_line.replace(broken, fix)
                if new_line != old_line:
                    lines[idx] = new_line
                    patched = True
                    total_fixes += 1
            else:
                # Potential misalignment or already fixed
                # Try simple match regardless of case if it fails once? No, let's be strict.
                pass

        if patched:
            try:
                file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                files_patched += 1
            except Exception as e:
                print(f"Error writing {file_rel}: {e}")

    print(f"Patching complete: {total_fixes} imports fixed across {files_patched} files.")

if __name__ == "__main__":
    apply_fixes()
