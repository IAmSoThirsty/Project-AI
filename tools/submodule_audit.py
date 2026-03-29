# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / submodule_audit.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / submodule_audit.py


import os
import subprocess
from datetime import datetime

def run_command(cmd, cwd=None):
    try:
        result = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def audit_submodule(path, name):
    print(f"--- Auditing Submodule: {name} at {path} ---")
    
    # 1. Purge Unity files if any (consistency check)
    # Using a cautious approach to find and delete
    # dir /s /b *Unity* | xargs rm (simplified logic)
    # For Windows, we'll use a safer python loop
    for root, dirs, files in os.walk(path):
        for item in dirs + files:
            if "Unity" in item:
                full_path = os.path.join(root, item)
                print(f"  [PURGE] Removing legacy Unity asset: {full_path}")
                try:
                    if os.path.isdir(full_path):
                        subprocess.run(f'git rm -rf "{full_path}" --ignore-unmatch', cwd=path, shell=True)
                    else:
                        subprocess.run(f'git rm -f "{full_path}" --ignore-unmatch', cwd=path, shell=True)
                except:
                    pass

    # 2. Check for changes
    stdout, stderr, code = run_command("git status --porcelain", cwd=path)
    if stdout:
        print(f"  [SYCHRONIZING] Changes detected in {name}")
        run_command("git add .", cwd=path)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        commit_msg = f"[Sovereign] Submodule Internal Sync [{timestamp}] Productivity: Active"
        run_command(f'git commit -m "{commit_msg}"', cwd=path)
        print(f"  [SUCCESS] committed changes in {name}")
    else:
        print(f"  [CLEAN] No changes in {name}")

def main():
    root_dir = os.getcwd()
    print(f"Starting Recursive Sovereign Audit in: {root_dir}")
    
    # Get list of submodules
    stdout, stderr, code = run_command("git submodule status --recursive")
    if code != 0:
        print(f"Error getting submodule status: {stderr}")
        return

    submodules = []
    for line in stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            # Format usually: [commit] [path] [branch]
            # Path might have spaces, parts[1] is the start
            path = parts[1]
            submodules.append(path)

    for sub_path in submodules:
        full_path = os.path.join(root_dir, sub_path)
        if os.path.exists(full_path):
            audit_submodule(full_path, sub_path)

    # Final stage in parent
    print("--- Finalizing Parent Repository ---")
    run_command("git add .", cwd=root_dir)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_command(f'git commit -m "[Sovereign] Global Submodule Audit Completion [{timestamp}]"', cwd=root_dir)
    print("Sovereign Audit Complete.")

if __name__ == "__main__":
    main()
