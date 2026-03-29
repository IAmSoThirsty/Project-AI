# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / path_integrity_agent.py
# ============================================================================ #
#
# COMPLIANCE: Regulator-Ready / UTF-8                                          #



"""
Path Integrity Agent
Specifically hunts for import path mismatches like the CodexDeus bug.
Every import path verified against the actual filesystem.
Produces a list of broken imports with the correct path where findable.
No interaction. Runs and exits.
"""

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Thirsty-Lang Metadata Integration
__PRODUCTIVITY_STATUS__ = "Active"
__LAST_UPDATE__ = "2026-03-13 00:51"

ROOT = Path(__file__).parent.parent.absolute()
OUTPUT_JSON = ROOT / "governance" / "PATH_INTEGRITY_MANIFEST.json"
OUTPUT_MD = ROOT / "governance" / "PATH_INTEGRITY_MANIFEST.md"


def get_all_py_modules() -> dict[str, Path]:
    """Build a map of module_name -> actual_path for every .py file in the repo."""
    module_map = {}
    for py_file in ROOT.rglob("*.py"):
        try:
            rel = py_file.relative_to(ROOT)
        except ValueError:
            continue
        # Convert path to dotted module name
        parts = list(rel.parts)
        if parts[-1] == "__init__.py":
            parts = parts[:-1]
        else:
            parts[-1] = parts[-1].replace(".py", "")
        module_name = ".".join(parts)
        module_map[module_name] = py_file

        # Also index by just the filename stem for fuzzy matching
        stem = py_file.stem
        if stem not in module_map:
            module_map[stem] = py_file

    return module_map


def fuzzy_find(broken_module: str, module_map: dict) -> str | None:
    """Try to find the correct path for a broken import."""
    # Try the last component
    last = broken_module.split(".")[-1]
    if last in module_map:
        rel = module_map[last].relative_to(ROOT)
        return str(rel).replace("/", ".").replace(".py", "").replace("\\", ".")

    # Try searching for any path containing the last component
    matches = [k for k in module_map if last in k.split(".")]
    if len(matches) == 1:
        return matches[0]
    if matches:
        return f"AMBIGUOUS: {', '.join(matches[:3])}"

    return None


def check_file(path: Path, module_map: dict) -> list[dict]:
    issues = []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except (SyntaxError, OSError):
        return []

    rel = str(path.relative_to(ROOT))

    for node in ast.walk(tree):
        module = None
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
                line = node.lineno
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            line = node.lineno

        if not module:
            continue

        # Skip stdlib and installed packages (basic check)
        top = module.split(".")[0]
        try:
            import importlib.util
            if importlib.util.find_spec(top) is not None:
                continue
        except (ModuleNotFoundError, ValueError):
            pass

        # Check if this module exists in our repo
        if module not in module_map:
            suggested = fuzzy_find(module, module_map)
            issues.append({
                "file": rel,
                "line": line,
                "broken_import": module,
                "suggested_fix": suggested or "NOT FOUND IN REPO",
                "severity": "HIGH" if suggested else "UNKNOWN",
            })

    return issues


def build_manifest():
    module_map = get_all_py_modules()
    all_issues = []

    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT, capture_output=True, text=True
    )
    git_files = [ROOT / p.strip() for p in result.stdout.splitlines()
                 if p.strip().endswith(".py")]

    for path in git_files:
        if not path.exists():
            continue
        issues = check_file(path, module_map)
        all_issues.extend(issues)

    high = [i for i in all_issues if i["severity"] == "HIGH"]
    unknown = [i for i in all_issues if i["severity"] == "UNKNOWN"]

    manifest = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_issues": len(all_issues),
            "fixable": len(high),
            "not_found": len(unknown),
        },
        "issues": sorted(all_issues, key=lambda x: x["severity"]),
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    lines = [
        "# Path Integrity Manifest",
        f"Generated: {manifest['generated']}",
        f"Total broken imports: **{len(all_issues)}**",
        f"Fixable (correct path found): **{len(high)}**",
        f"Not found anywhere: **{len(unknown)}**",
        "",
        "## Fixable Imports (Apply These)",
        "| File | Line | Broken Import | Correct Path |",
        "|------|------|---------------|--------------|",
    ]
    for i in high:
        lines.append(
            f"| `{i['file']}` | {i['line']} | `{i['broken_import']}` | `{i['suggested_fix']}` |"
        )

    lines += [
        "",
        "## Imports Not Found Anywhere",
        "| File | Line | Broken Import |",
        "|------|------|---------------|",
    ]
    for i in unknown:
        lines.append(f"| `{i['file']}` | {i['line']} | `{i['broken_import']}` |")

    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"PATH_INTEGRITY_MANIFEST written. {len(all_issues)} broken imports. {len(high)} fixable.")


if __name__ == "__main__":
    build_manifest()
