# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / stub_hunter_agent.py
# ============================================================================ #
#
# COMPLIANCE: Regulator-Ready / UTF-8                                          #



"""
Stub Hunter Agent
Finds every stub, placeholder, mock, and unimplemented function
across the entire codebase. Ranks by impact.
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
OUTPUT_JSON = ROOT / "governance" / "STUB_MANIFEST.json"
OUTPUT_MD = ROOT / "governance" / "STUB_MANIFEST.md"

STUB_SIGNALS = [
    ("pass", "empty body"),
    ("raise NotImplementedError", "explicitly unimplemented"),
    ("# placeholder", "marked placeholder"),
    ("# stub", "marked stub"),
    ("# todo", "marked todo"),
    ("# fixme", "marked fixme"),
    ("# hack", "marked hack"),
    ("time.sleep(1)", "fake delay"),
    ("time.sleep(0.5)", "fake delay"),
    ('logger.info("✅', "success log with no logic"),
    ('logging.info("✅', "success log with no logic"),
    ("return {}", "empty return"),
    ("return []", "empty return"),
    ("return None  #", "stubbed return"),
    ("# mocking", "marked mock"),
    ("# not implemented", "not implemented"),
]


def analyze_function(node: ast.FunctionDef | ast.AsyncFunctionDef, source_lines: list[str]) -> dict | None:
    """Check if a function is a stub."""
    body = node.body

    # Single pass
    if len(body) == 1 and isinstance(body[0], ast.Pass):
        return {"reason": "empty body (pass only)", "severity": "HIGH"}

    # Just a docstring
    if len(body) == 1 and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        return {"reason": "docstring only, no implementation", "severity": "HIGH"}

    # Docstring + pass
    if len(body) == 2 and isinstance(body[0], ast.Expr) and isinstance(body[1], ast.Pass):
        return {"reason": "docstring + pass", "severity": "HIGH"}

    # Just raises NotImplementedError
    if len(body) <= 2:
        for n in ast.walk(ast.Module(body=body, type_ignores=[])):
            if isinstance(n, ast.Raise):
                return {"reason": "raises NotImplementedError only", "severity": "HIGH"}

    # Check source lines for stub signals
    start = node.lineno - 1
    end = node.end_lineno
    func_source = "\n".join(source_lines[start:end]).lower()

    for signal, reason in STUB_SIGNALS:
        if signal.lower() in func_source:
            return {"reason": reason, "severity": "MEDIUM"}

    return None


def scan_file(path: Path) -> list[dict]:
    stubs = []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
        source_lines = source.splitlines()
    except (SyntaxError, OSError):
        return []

    rel = str(path.relative_to(ROOT))

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result = analyze_function(node, source_lines)
            if result:
                stubs.append({
                    "file": rel,
                    "function": node.name,
                    "line": node.lineno,
                    "reason": result["reason"],
                    "severity": result["severity"],
                })

    # Also scan raw lines for inline stubs
    for i, line in enumerate(source_lines, 1):
        lower = line.strip().lower()
        for signal, reason in STUB_SIGNALS:
            if signal.lower() in lower and not any(s["line"] == i and s["file"] == rel for s in stubs):
                stubs.append({
                    "file": rel,
                    "function": "inline",
                    "line": i,
                    "reason": f"inline: {reason}",
                    "severity": "LOW",
                })
                break

    return stubs


def build_manifest():
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT, capture_output=True, text=True
    )
    py_files = [ROOT / p.strip() for p in result.stdout.splitlines()
                if p.strip().endswith(".py") and (ROOT / p.strip()).exists()]

    all_stubs = []
    for path in py_files:
        all_stubs.extend(scan_file(path))

    by_severity = {"HIGH": [], "MEDIUM": [], "LOW": []}
    for s in all_stubs:
        by_severity[s["severity"]].append(s)

    # Group by file
    by_file = {}
    for s in all_stubs:
        by_file.setdefault(s["file"], []).append(s)

    manifest = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_stubs": len(all_stubs),
            "high_priority": len(by_severity["HIGH"]),
            "medium_priority": len(by_severity["MEDIUM"]),
            "low_priority": len(by_severity["LOW"]),
            "files_affected": len(by_file),
        },
        "stubs_by_severity": by_severity,
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    lines = [
        "# Stub Manifest",
        f"Generated: {manifest['generated']}",
        f"Total stubs found: **{len(all_stubs)}**",
        f"High priority: **{len(by_severity['HIGH'])}** | Medium: {len(by_severity['MEDIUM'])} | Low: {len(by_severity['LOW'])}",
        "",
        "## High Priority — Implement These First",
        "| File | Function | Line | Reason |",
        "|------|----------|------|--------|",
    ]
    for s in sorted(by_severity["HIGH"], key=lambda x: x["file"]):
        lines.append(f"| `{s['file']}` | `{s['function']}` | {s['line']} | {s['reason']} |")

    lines += [
        "",
        "## Medium Priority",
        "| File | Function | Line | Reason |",
        "|------|----------|------|--------|",
    ]
    for s in sorted(by_severity["MEDIUM"], key=lambda x: x["file"]):
        lines.append(f"| `{s['file']}` | `{s['function']}` | {s['line']} | {s['reason']} |")

    lines += ["", "## Files Most Affected", "| File | Stub Count |", "|------|------------|"]
    for f, stubs in sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)[:30]:
        lines.append(f"| `{f}` | {len(stubs)} |")

    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"STUB_MANIFEST written. {len(all_stubs)} stubs found across {len(by_file)} files.")


if __name__ == "__main__":
    build_manifest()
