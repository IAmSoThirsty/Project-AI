import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: agents / dead_code_agent.py
# ============================================================================ #
"""
Dead Code Agent
Finds classes and functions that are defined but never called or referenced
anywhere in the codebase. These are candidates for deletion or completion.
No interaction. Runs and exits.
"""

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent.absolute()
OUTPUT_JSON = ROOT / "governance" / "DEAD_CODE_MANIFEST.json"
OUTPUT_MD = ROOT / "governance" / "DEAD_CODE_MANIFEST.md"


def get_py_files():
    result = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True
    )
    return [ROOT / p.strip() for p in result.stdout.splitlines()
            if p.strip().endswith(".py") and (ROOT / p.strip()).exists()]


def extract_definitions(path: Path) -> list[dict]:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except (SyntaxError, OSError):
        return []

    rel = str(path.relative_to(ROOT))
    defs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            # Skip private, dunder, and test functions
            if node.name.startswith("__") and node.name.endswith("__"):
                continue
            defs.append({
                "name": node.name,
                "type": "class" if isinstance(node, ast.ClassDef) else "function",
                "file": rel,
                "line": node.lineno,
            })
    return defs


def extract_all_references(files: list[Path]) -> set[str]:
    refs = set()
    for path in files:
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        try:
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    refs.add(node.id)
                elif isinstance(node, ast.Attribute):
                    refs.add(node.attr)
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        refs.add(node.func.id)
        except SyntaxError:
            # Fall back to raw string scan
            for line in source.splitlines():
                line = line.strip()
                if not line.startswith("#"):
                    words = line.replace("(", " ").replace(")", " ").replace(".", " ").split()
                    refs.update(words)
    return refs


def build_manifest():
    py_files = get_py_files()
    all_defs = []
    for path in py_files:
        all_defs.extend(extract_definitions(path))

    all_refs = extract_all_references(py_files)

    dead = []
    for d in all_defs:
        if d["name"] not in all_refs:
            dead.append(d)

    by_type = {"class": [], "function": []}
    for d in dead:
        by_type[d["type"]].append(d)

    manifest = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_definitions": len(all_defs),
            "dead_code_items": len(dead),
            "dead_classes": len(by_type["class"]),
            "dead_functions": len(by_type["function"]),
        },
        "dead_code": sorted(dead, key=lambda x: (x["type"], x["file"])),
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(manifest, indent=2))

    lines = [
        "# Dead Code Manifest",
        f"Generated: {manifest['generated']}",
        f"Total definitions: {len(all_defs)}",
        f"Potentially dead: **{len(dead)}** ({len(by_type['class'])} classes, {len(by_type['function'])} functions)",
        "",
        "> Note: 'dead' means no reference found in the codebase. May still be called dynamically or via config.",
        "",
        "## Dead Classes",
        "| Class | File | Line |",
        "|-------|------|------|",
    ]
    for d in by_type["class"]:
        lines.append(f"| `{d['name']}` | `{d['file']}` | {d['line']} |")

    lines += ["", "## Dead Functions", "| Function | File | Line |", "|----------|------|------|"]
    for d in by_type["function"]:
        lines.append(f"| `{d['name']}` | `{d['file']}` | {d['line']} |")

    OUTPUT_MD.write_text("\n".join(lines))
    print(f"DEAD_CODE_MANIFEST written. {len(dead)} potentially dead definitions found.")


if __name__ == "__main__":
    build_manifest()
