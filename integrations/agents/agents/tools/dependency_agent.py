import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: agents / dependency_agent.py
# ============================================================================ #
"""
Dependency Agent
Maps every import across every Python file.
Flags unresolved imports, circular dependencies, and missing modules.
No interaction. Runs and exits.
"""

import ast
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent.absolute()
OUTPUT_JSON = ROOT / "governance" / "DEPENDENCY_MANIFEST.json"
OUTPUT_MD = ROOT / "governance" / "DEPENDENCY_MANIFEST.md"


def get_python_files():
    result = subprocess.run(
        ["git", "ls-files", "*.py"],
        cwd=ROOT, capture_output=True, text=True
    )
    # Also find recursively
    all_py = list(ROOT.rglob("*.py"))
    git_files = {ROOT / p.strip() for p in result.stdout.splitlines() if p.strip()}
    return [p for p in all_py if p in git_files or True]  # include all tracked


def extract_imports(path: Path) -> list[dict]:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except (SyntaxError, OSError):
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({"type": "import", "module": alias.name, "line": node.lineno})
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append({"type": "from", "module": module, "line": node.lineno})
    return imports


def resolve_import(module: str) -> str:
    """Check if an import resolves to a file in the repo or installed package."""
    if not module:
        return "EMPTY"

    # Check if it's a stdlib module
    import sys
    if module.split(".")[0] in sys.stdlib_module_names:
        return "STDLIB"

    # Check if it resolves to a file in the repo
    parts = module.replace(".", "/")
    candidates = [
        ROOT / f"{parts}.py",
        ROOT / parts / "__init__.py",
        ROOT / "src" / f"{parts}.py",
        ROOT / "src" / parts / "__init__.py",
    ]
    for c in candidates:
        if c.exists():
            return "RESOLVED"

    # Check if installed
    try:
        __import__(module.split(".")[0])
        return "INSTALLED"
    except ImportError:
        logger.warning('Encountered non-terminal exception in %s' % __name__)

    return "UNRESOLVED"


def detect_circular(dep_graph: dict) -> list[list[str]]:
    """Simple DFS cycle detection."""
    visited = set()
    path = []
    cycles = []

    def dfs(node):
        if node in path:
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        path.append(node)
        for neighbor in dep_graph.get(node, []):
            dfs(neighbor)
        path.pop()

    for node in dep_graph:
        dfs(node)

    return cycles


def build_manifest():
    py_files = get_python_files()
    all_imports = []
    unresolved = []
    dep_graph = defaultdict(list)
    file_results = []

    for path in py_files:
        rel = str(path.relative_to(ROOT))
        imports = extract_imports(path)
        file_imports = []

        for imp in imports:
            status = resolve_import(imp["module"])
            entry = {**imp, "status": status, "file": rel}
            file_imports.append(entry)
            all_imports.append(entry)

            if status == "UNRESOLVED":
                unresolved.append(entry)

            if status == "RESOLVED":
                dep_graph[rel].append(imp["module"])

        file_results.append({
            "file": rel,
            "total_imports": len(file_imports),
            "unresolved": [i for i in file_imports if i["status"] == "UNRESOLVED"],
            "resolved": len([i for i in file_imports if i["status"] == "RESOLVED"]),
            "stdlib": len([i for i in file_imports if i["status"] == "STDLIB"]),
            "installed": len([i for i in file_imports if i["status"] == "INSTALLED"]),
        })

    cycles = detect_circular(dict(dep_graph))

    by_status = defaultdict(int)
    for imp in all_imports:
        by_status[imp["status"]] += 1

    manifest = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_files_analyzed": len(py_files),
            "total_imports": len(all_imports),
            "by_status": dict(by_status),
            "unresolved_count": len(unresolved),
            "circular_dependency_chains": len(cycles),
        },
        "unresolved_imports": unresolved,
        "circular_dependencies": cycles,
        "files": sorted(file_results, key=lambda x: len(x["unresolved"]), reverse=True),
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(manifest, indent=2))

    lines = [
        "# Dependency Manifest",
        f"Generated: {manifest['generated']}",
        "",
        "## Summary",
        f"- Total files: {manifest['summary']['total_files_analyzed']}",
        f"- Total imports: {manifest['summary']['total_imports']}",
        f"- **Unresolved: {manifest['summary']['unresolved_count']}**",
        f"- Circular chains: {manifest['summary']['circular_dependency_chains']}",
        "",
        "## Unresolved Imports (Bugs)",
        "| File | Module | Line |",
        "|------|--------|------|",
    ]
    for u in unresolved:
        lines.append(f"| `{u['file']}` | `{u['module']}` | {u['line']} |")

    if cycles:
        lines += ["", "## Circular Dependencies", ""]
        for i, cycle in enumerate(cycles, 1):
            lines.append(f"{i}. {' → '.join(cycle)}")

    lines += ["", "## Files by Unresolved Count",
              "| File | Unresolved | Resolved | Stdlib | Installed |",
              "|------|------------|----------|--------|-----------|"]
    for f in manifest["files"][:50]:  # top 50
        lines.append(
            f"| `{f['file']}` | {len(f['unresolved'])} | {f['resolved']} | {f['stdlib']} | {f['installed']} |"
        )

    OUTPUT_MD.write_text("\n".join(lines))
    print(f"DEPENDENCY_MANIFEST written. {len(unresolved)} unresolved imports found.")


if __name__ == "__main__":
    build_manifest()
