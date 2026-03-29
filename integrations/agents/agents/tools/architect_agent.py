import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: agents / architect_agent.py
# ============================================================================ #
"""
Principal Architect Agent
Walks the entire git-tracked file tree, categorizes every file,
estimates completion, and writes a structured manifest.
No interaction. No mocking. Runs and exits.
"""

import ast
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent.absolute()
OUTPUT_JSON = ROOT / "governance" / "ARCHITECT_MANIFEST.json"
OUTPUT_MD = ROOT / "governance" / "ARCHITECT_MANIFEST.md"

CATEGORIES = {
    "EXECUTABLE", "STUB", "MOCK", "ARCHIVED",
    "CONFIG", "INFRA", "SPEC", "DOC", "UNKNOWN"
}

DOC_EXTENSIONS = {".md", ".rst", ".txt"}
CONFIG_EXTENSIONS = {".yaml", ".yml", ".toml", ".json", ".env", ".ini", ".cfg"}
INFRA_PATTERNS = {"docker", "dockerfile", "k8s", "terraform", ".github", "helm"}
SPEC_PATTERNS = {"spec", "constitution", "charter", "governance", ".thirsty", ".tarl", ".tscg"}
ARCHIVE_PATTERNS = {"archive", "archived", "legacy", "deprecated"}


def get_git_files():
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT, capture_output=True, text=True
    )
    return [p.strip() for p in result.stdout.splitlines() if p.strip()]


def categorize(path: str) -> str:
    p = Path(path)
    lower = path.lower()

    if any(a in lower for a in ARCHIVE_PATTERNS):
        return "ARCHIVED"
    if p.suffix in DOC_EXTENSIONS:
        return "DOC"
    if p.suffix in CONFIG_EXTENSIONS:
        return "CONFIG"
    if any(pat in lower for pat in INFRA_PATTERNS):
        return "INFRA"
    if any(pat in lower for pat in SPEC_PATTERNS):
        return "SPEC"
    if p.suffix in {".py", ".js", ".ts", ".go", ".rs"}:
        return _categorize_code(path)
    return "UNKNOWN"


def _categorize_code(path: str) -> str:
    full = ROOT / path
    try:
        source = full.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "UNKNOWN"

    if not source.strip():
        return "STUB"

    stub_signals = [
        "pass", "raise NotImplementedError", "# placeholder",
        "# stub", "# todo", "logger.info(\"✅\")", "time.sleep(1)",
        "return {}", "return None  # placeholder"
    ]
    lines = [l.strip().lower() for l in source.splitlines()]
    real_lines = [l for l in lines if l and not l.startswith("#")]

    stub_count = sum(1 for l in real_lines if any(s in l for s in stub_signals))
    if real_lines and stub_count / len(real_lines) > 0.5:
        return "STUB"

    if "mock" in path.lower() or "fake" in path.lower():
        return "MOCK"

    return "EXECUTABLE"


def estimate_completion(path: str, category: str) -> tuple[str, str]:
    if category in {"DOC", "CONFIG", "INFRA", "SPEC", "ARCHIVED"}:
        return "100%", "Non-code asset"
    if category == "UNKNOWN":
        return "0%", "Could not analyze"

    full = ROOT / path
    try:
        source = full.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "0%", "Unreadable"

    if not source.strip():
        return "0%", "Empty file"

    score = 0
    notes = []

    # Has real logic
    if len([l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]) > 10:
        score += 25
    else:
        notes.append("minimal logic")

    # Has docstrings or comments explaining intent
    if '"""' in source or "'''" in source:
        score += 10

    # Has imports that look resolvable
    if "import" in source:
        score += 15

    # Has class or function definitions
    if "def " in source or "class " in source:
        score += 25
    else:
        notes.append("no functions or classes")

    # Has error handling
    if "try:" in source or "except" in source:
        score += 10

    # Has tests nearby
    test_path = ROOT / path.replace("src/", "tests/").replace(".py", "_test.py")
    alt_test = ROOT / f"tests/test_{Path(path).name}"
    if test_path.exists() or alt_test.exists():
        score += 15
        notes.append("has tests")
    else:
        notes.append("no tests found")

    if category == "STUB":
        score = min(score, 25)
        notes.insert(0, "stub implementation")
    if category == "MOCK":
        score = min(score, 40)
        notes.insert(0, "mock implementation")

    pct = f"{min(score, 100)}%"
    return pct, "; ".join(notes) if notes else "looks complete"


def infer_purpose(path: str) -> str:
    full = ROOT / path
    try:
        source = full.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "unreadable"

    # Try to get module docstring
    try:
        tree = ast.parse(source)
        docstring = ast.get_docstring(tree)
        if docstring:
            return docstring.splitlines()[0][:120]
    except SyntaxError:
        logger.warning('Encountered non-terminal exception in %s' % __name__)

    # Fall back to first comment
    for line in source.splitlines()[:10]:
        line = line.strip()
        if line.startswith("#") and len(line) > 5:
            return line.lstrip("#").strip()[:120]

    # Fall back to filename inference
    name = Path(path).stem.replace("_", " ").replace("-", " ")
    return f"Inferred from filename: {name}"


def build_manifest():
    files = get_git_files()
    results = []
    category_counts = {c: 0 for c in CATEGORIES}
    completion_scores = []

    doc_dirs = {}

    for path in files:
        category = categorize(path)
        category_counts[category] = category_counts.get(category, 0) + 1

        if category == "DOC":
            d = str(Path(path).parent)
            doc_dirs[d] = doc_dirs.get(d, 0) + 1
            continue

        purpose = infer_purpose(path)
        completion, notes = estimate_completion(path, category)

        try:
            pct = int(completion.replace("%", ""))
            completion_scores.append(pct)
        except ValueError:
            logger.warning('Encountered non-terminal exception in %s' % __name__)

        results.append({
            "path": path,
            "category": category,
            "purpose": purpose,
            "completion": completion,
            "notes": notes,
        })

    overall = f"{int(sum(completion_scores)/len(completion_scores))}%" if completion_scores else "0%"

    manifest = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_files": len(files),
            "by_category": category_counts,
            "doc_directories": doc_dirs,
            "estimated_completion": overall,
        },
        "files": sorted(results, key=lambda x: (x["category"], x["completion"]), reverse=False),
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(manifest, indent=2))

    # Write markdown report
    lines = [
        "# Architect Manifest",
        f"Generated: {manifest['generated']}",
        f"Overall Completion: **{overall}**",
        "",
        "## Summary",
        "| Category | Count |",
        "|----------|-------|",
    ]
    for cat, count in sorted(category_counts.items()):
        lines.append(f"| {cat} | {count} |")

    lines += ["", "## File Analysis", "| Path | Category | Completion | Purpose | Notes |",
              "|------|----------|------------|---------|-------|"]

    for f in manifest["files"]:
        lines.append(
            f"| `{f['path']}` | {f['category']} | {f['completion']} | {f['purpose'][:60]} | {f['notes'][:60]} |"
        )

    lines += ["", "## Documentation Directories", "| Directory | File Count |", "|-----------|------------|"]
    for d, count in sorted(doc_dirs.items()):
        lines.append(f"| `{d}` | {count} |")

    OUTPUT_MD.write_text("\n".join(lines))
    print(f"ARCHITECT_MANIFEST written. {len(files)} files analyzed. Overall: {overall}")


if __name__ == "__main__":
    build_manifest()
