# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / total_architect_scan.py
# ============================================================================ #
#
# COMPLIANCE: Regulator-Ready / UTF-8                                          #


import subprocess
import os
import json
from datetime import datetime

class TotalArchitect:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.manifest = {
            "generated": datetime.now().isoformat(),
            "overall_completion": 0,
            "categories": {},
            "files": []
        }
        self.categories_found = {}

    def run_command(self, cmd):
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.root_dir)
        return result.stdout.splitlines()

    def categorize(self, path):
        path_lower = path.lower()
        ext = os.path.splitext(path_lower)[1]
        
        if any(x in path_lower for x in ['archive/', 'history/', 'timeline/', '.bak', '.old']):
            return 'ARCHIVED'
        if any(x in path_lower for x in ['test', 'mock', 'fixture', 'demo']):
            return 'MOCK'
        if ext in ['.md', '.txt', '.pdf', '.rtf', '.docx', '.html']:
            return 'DOC'
        if ext in ['.yaml', '.yml', '.json', '.toml', '.xml', '.ini', '.conf', '.config', '.env', '.lock', '.properties']:
            return 'CONFIG'
        if ext in ['.thirsty', '.tarl', '.tog', '.shadow', '.tscgb', '.tscg', '.proto', '.avsc', '.sql', '.cypher', '.tla', '.tex']:
            return 'SPEC'
        if ext in ['.py', '.js', '.ts', '.tsx', '.go', '.rs', '.c', '.cpp', '.h', '.cs', '.java', '.sh', '.bat', '.ps1', '.kt']:
            return 'EXECUTABLE'
        if any(x in path_lower for x in ['dockerfile', '.dockerignore', '.helmignore', 'makefile']):
            return 'INFRA'
        if 'stub' in path_lower:
            return 'STUB'
        return 'UNKNOWN'

    def audit(self):
        print("--- Auditing Tracked Files ---")
        tracked = self.run_command("git ls-files")
        for f in tracked:
            cat = self.categorize(f)
            self.manifest["files"].append({"path": f, "status": "TRACKED", "category": cat})
            self.categories_found[cat] = self.categories_found.get(cat, 0) + 1

        print("--- Auditing Untracked Files ---")
        untracked = self.run_command("git ls-files --others --exclude-standard")
        for f in untracked:
            cat = self.categorize(f)
            self.manifest["files"].append({"path": f, "status": "UNTRACKED", "category": cat})
            self.categories_found[cat] = self.categories_found.get(cat, 0) + 1

        print("--- Auditing Submodules ---")
        submodules = self.run_command("git submodule status --recursive")
        for s in submodules:
            # Format:  <sha> <path> (tags)
            parts = s.strip().split()
            if len(parts) >= 2:
                sha = parts[0]
                path = parts[1]
                self.manifest["files"].append({"path": path, "status": "SUBMODULE", "category": "INFRA", "sha": sha})
                self.categories_found["INFRA"] = self.categories_found.get("INFRA", 0) + 1

        print("--- Auditing .Git Meta ---")
        # Custom check for hooks
        hooks_dir = os.path.join(self.root_dir, ".git", "hooks")
        if os.path.exists(hooks_dir):
            for h in os.listdir(hooks_dir):
                if not h.endswith(".sample"):
                    self.manifest["files"].append({"path": f".git/hooks/{h}", "status": "GIT_INTERNAL", "category": "EXECUTABLE"})
                    self.categories_found["EXECUTABLE"] = self.categories_found.get("EXECUTABLE", 0) + 1

        self.manifest["categories"] = self.categories_found
        
        # Calculate completion (simple heuristic for this audit)
        total_files = len(self.manifest["files"])
        executable_files = self.categories_found.get("EXECUTABLE", 0)
        # Tracking 'maturity' based on EXECUTABLE vs total logic
        self.manifest["overall_completion"] = int((executable_files / total_files) * 100) if total_files > 0 else 0

    def save(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=2)

    def generate_markdown(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write("# ⚖️ TOTAL ARCHITECT MANIFEST\n")
            f.write(f"**Generated**: {self.manifest['generated']} | **Overall Completion**: {self.manifest['overall_completion']}%\n\n")
            
            f.write("## 🏛️ Council Statistics\n")
            f.write("| Category | Count |\n|---|---|\n")
            for cat, count in sorted(self.categories_found.items()):
                f.write(f"| {cat} | {count} |\n")
            
            f.write("\n## 📁 Comprehensive Audit (Partial View)\n")
            f.write("| Path | Status | Category |\n|---|---|---|\n")
            # Show first 50 and last 50 for brevity in MD
            files = self.manifest["files"]
            display_files = files[:50] + files[-50:] if len(files) > 100 else files
            for file in display_files:
                f.write(f"| `{file['path']}` | {file['status']} | {file['category']} |\n")
            
            if len(files) > 100:
                f.write(f"\n... and {len(files) - 100} more files. See JSON for details.\n")

if __name__ == "__main__":
    root = os.getcwd()
    ta = TotalArchitect(root)
    ta.audit()
    ta.save("governance/TOTAL_ARCHITECT_MANIFEST.json")
    ta.generate_markdown("governance/TOTAL_ARCHITECT_MANIFEST.md")
    print(f"Audit Complete. Found {len(ta.manifest['files'])} nodes.")
