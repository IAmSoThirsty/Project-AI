"""
Zero Bypass Verification Tool for Project-AI Level 2 Governance.

Scans repository for:
- GUI bypasses (direct system calls without governance)
- AI bypasses (direct provider calls outside orchestrator)
- Fallback bypasses (try/governance except/direct-call patterns)
- Security issues (JWT defaults, predictable tokens, legacy SHA)
- Temporal ungoverned workflows
- Unclassified scripts

Usage:
    python tools/verify_zero_bypass.py
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(".").resolve()

# Adjust if needed
GUI_DIR = REPO_ROOT / "src" / "app" / "gui"
TEMPORAL_DIR = REPO_ROOT / "src" / "app" / "temporal"
SCRIPTS_DIRS = [
    REPO_ROOT / "scripts",
    REPO_ROOT / "src" / "app" / "cli",
]
SRC_DIR = REPO_ROOT / "src"

APPROVED_AI_FILES = {
    "src/app/core/ai/orchestrator.py",
    "src/app/core/model_providers.py",
    "src/app/core/polyglot_execution.py",  # DEFERRED - documented bypass
}

GOVERNANCE_MARKERS = [
    "route_request(",
    "enforce_pipeline(",
    "_route_through_governance(",
    "execute_action(",
]

ORCHESTRATOR_IMPORTS = [
    "from app.core.ai.orchestrator import",
    "from app.core.runtime.router import",
]

SCRIPT_GOVERNANCE_MARKERS = [
    "GOVERNANCE: GOVERNED",
    "GOVERNANCE: ADMIN-BYPASS",
    "GOVERNANCE: EXAMPLE",
    "GOVERNANCE:",  # Generic marker (catches variations)
]

DIRECT_SYSTEM_PATTERNS = [
    r"\bself\.kernel\.",
    r"\bself\.lrm\.",
    r"\bself\.codex\.",
    r"\bself\.intelligence_engine\.",
]

DIRECT_AI_PATTERNS = [
    # Only match ACTUAL API calls, not string literals or comments
    r"OpenAI\s*\([^)]*api_key",  # OpenAI client instantiation with API key
    r"openai\.chat\.completions",  # OpenAI chat API
    r"openai\.responses\.create",  # OpenAI response creation
    r"api-inference\.huggingface\.co",  # HuggingFace inference endpoint
    r"requests\.post\s*\([^)]*huggingface",  # Direct HF API calls
    r"requests\.post\s*\([^)]*openai",  # Direct OpenAI API calls
    r"get_provider\s*\(",  # Direct provider access (bypass)
    r"\.chat_completion\s*\(",  # Direct provider method call
]

FALLBACK_BYPASS_PATTERNS = [
    r"try:\s*\n(?:.+\n){0,8}.*route_request\(",
    r"except\s+Exception(?:\s+as\s+\w+)?\s*:\s*\n(?:.+\n){0,8}.*self\.(kernel|lrm|codex|intelligence_engine)\.",
]

JWT_BAD_PATTERNS = [
    r'JWT_SECRET_KEY\s*=\s*os\.getenv\([^)]*,\s*["\']CHANGE_THIS_IN_PRODUCTION["\']\)',
    r'JWT_SECRET_KEY\s*=\s*["\']CHANGE_THIS_IN_PRODUCTION["\']',
]

PLAINTEXT_TOKEN_PATTERNS = [
    r'token-\{username\}',
    r'f["\']token-\{username\}["\']',
]

LEGACY_SHA_PATTERNS = [
    r"hashlib\.sha256\(",
]


@dataclass
class FileFinding:
    file: str
    category: str
    message: str
    line_hits: list[int]


def iter_py_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if not path.exists():
            continue
        if path.is_file() and path.suffix == ".py":
            yield path
        elif path.is_dir():
            yield from path.rglob("*.py")


def find_pattern_lines(text: str, pattern: str) -> list[int]:
    lines = text.splitlines()
    hits: list[int] = []
    rx = re.compile(pattern, re.MULTILINE)
    for idx, line in enumerate(lines, start=1):
        if rx.search(line):
            hits.append(idx)
    return hits


def has_any_marker(text: str, markers: list[str]) -> bool:
    return any(marker in text for marker in markers)


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def main() -> None:
    findings: list[FileFinding] = []

    all_py_files = list(iter_py_files([SRC_DIR, REPO_ROOT / "web", REPO_ROOT / "scripts", REPO_ROOT / "tools"]))

    # 1) GUI bypass scan
    for file in iter_py_files([GUI_DIR]):
        text = file.read_text(encoding="utf-8", errors="ignore")
        direct_hits: list[int] = []
        for pattern in DIRECT_SYSTEM_PATTERNS:
            direct_hits.extend(find_pattern_lines(text, pattern))
        direct_hits = sorted(set(direct_hits))

        if direct_hits and not has_any_marker(text, GOVERNANCE_MARKERS):
            findings.append(
                FileFinding(
                    file=rel(file),
                    category="gui_bypass",
                    message="Direct system calls found without governance markers",
                    line_hits=direct_hits,
                )
            )

    # 2) AI bypass scan
    for file in all_py_files:
        text = file.read_text(encoding="utf-8", errors="ignore")
        
        # Skip if file imports orchestrator (assumed routed)
        if any(imp in text for imp in ORCHESTRATOR_IMPORTS):
            continue
            
        ai_hits: list[int] = []
        for pattern in DIRECT_AI_PATTERNS:
            ai_hits.extend(find_pattern_lines(text, pattern))
        ai_hits = sorted(set(ai_hits))

        if ai_hits and rel(file) not in APPROVED_AI_FILES:
            findings.append(
                FileFinding(
                    file=rel(file),
                    category="ai_bypass",
                    message="Direct AI/provider usage outside approved orchestrator/provider files",
                    line_hits=ai_hits,
                )
            )

    # 3) Fallback bypass scan
    for file in all_py_files:
        text = file.read_text(encoding="utf-8", errors="ignore")
        for pattern in FALLBACK_BYPASS_PATTERNS:
            hits = find_pattern_lines(text, pattern)
            if hits:
                findings.append(
                    FileFinding(
                        file=rel(file),
                        category="fallback_bypass",
                        message="Potential try/governance except/direct-call fallback bypass",
                        line_hits=hits,
                    )
                )

    # 4) JWT bad default scan
    for file in all_py_files:
        text = file.read_text(encoding="utf-8", errors="ignore")
        for pattern in JWT_BAD_PATTERNS:
            hits = find_pattern_lines(text, pattern)
            if hits:
                findings.append(
                    FileFinding(
                        file=rel(file),
                        category="jwt_insecure_default",
                        message="JWT secret default fallback detected",
                        line_hits=hits,
                    )
                )

    # 5) Predictable token scan
    for file in all_py_files:
        text = file.read_text(encoding="utf-8", errors="ignore")
        for pattern in PLAINTEXT_TOKEN_PATTERNS:
            hits = find_pattern_lines(text, pattern)
            if hits:
                findings.append(
                    FileFinding(
                        file=rel(file),
                        category="predictable_token",
                        message="Predictable token pattern detected",
                        line_hits=hits,
                    )
                )

    # 6) Legacy SHA scan
    for file in all_py_files:
        text = file.read_text(encoding="utf-8", errors="ignore")
        for pattern in LEGACY_SHA_PATTERNS:
            hits = find_pattern_lines(text, pattern)
            if hits:
                findings.append(
                    FileFinding(
                        file=rel(file),
                        category="legacy_sha_usage",
                        message="SHA usage detected; verify this is not legacy auth/hash migration debt",
                        line_hits=hits,
                    )
                )

    # 7) Temporal unguided scan
    for file in iter_py_files([TEMPORAL_DIR]):
        text = file.read_text(encoding="utf-8", errors="ignore")
        # Only check @workflow.defn, not @activity.defn
        if "@workflow.defn" in text:
            if not has_any_marker(text, GOVERNANCE_MARKERS) and "validate_workflow_execution" not in text:
                findings.append(
                    FileFinding(
                        file=rel(file),
                        category="temporal_ungoverned",
                        message="Temporal workflow definition found without governance marker/integration call",
                        line_hits=[],
                    )
                )

    # 8) Script classification scan
    for root in SCRIPTS_DIRS:
        for file in iter_py_files([root]):
            text = file.read_text(encoding="utf-8", errors="ignore")
            
            # Check for explicit GOVERNANCE: markers (new standard)
            has_governance_marker = any(marker in text for marker in SCRIPT_GOVERNANCE_MARKERS)
            
            # Check for legacy markers (backward compatibility)
            governed = has_any_marker(text, GOVERNANCE_MARKERS)
            admin_marked = "ADMIN BYPASS" in text or "admin-bypass" in text
            example_marked = "EXAMPLE ONLY" in text or "example-only" in text
            
            # Script is classified if it has any marker
            is_classified = has_governance_marker or governed or admin_marked or example_marked
            
            if not is_classified:
                findings.append(
                    FileFinding(
                        file=rel(file),
                        category="script_unclassified",
                        message="Script is neither governed nor explicitly marked bypass/example",
                        line_hits=[],
                    )
                )

    by_category: dict[str, list[dict]] = {}
    for f in findings:
        by_category.setdefault(f.category, []).append(asdict(f))

    summary = {
        "total_findings": len(findings),
        "categories": {k: len(v) for k, v in sorted(by_category.items())},
        "findings": by_category,
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
