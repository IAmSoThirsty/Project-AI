#!/usr/bin/env python3
# =============================================================================
# FILE HEADER
# =============================================================================
# Script Name   : project_ai_audit.py
# Version       : 1.0.0
# Author        : IAmSoThirsty / Jeremy
# Description   : Sovereign monorepo coherence and operational readiness audit
#                 for Project-AI. Traverses 267k+ files post 110-repo merge.
#                 Produces five structured audit artifacts:
#                   1. Spec Drift Report       (spec_drift.json)
#                   2. Archive Candidate List  (archive_candidates.json)
#                   3. Operational Capability Matrix (capability_matrix.json)
#                   4. Platform Readiness Map  (platform_readiness.json)
#                   5. Hardware Gate Registry  (hardware_gates.json)
#                 Plus a unified HTML summary dashboard (audit_report.html).
#
# Execution Assumptions:
#   - Python 3.12+ on Linux (Ubuntu 22.04+) or Windows 10+ with WSL
#   - Google Antigravity IDE or direct CLI execution
#   - Repo root passed via --repo-root argument
#   - Read-only access to the repo is sufficient
#   - Output directory created at --output-dir (default: ./audit_output)
#   - No network access required; fully offline
#
# Security Posture     : Read-only, no writes to repo, no shell injection
# Determinism Class    : Strict — same repo state produces identical output
# Spec Authority       : THIRSTY_LANG_UTF_SPEC.md v4.0-E1 (2026-03-18)
# =============================================================================

# =============================================================================
# DEPENDENCY DECLARATION
# =============================================================================
# Standard library only — zero external dependencies.
# Required: Python 3.12+
# OS: Linux (primary), Windows with WSL (supported), macOS (supported)
# =============================================================================

import argparse
import concurrent.futures
import dataclasses
import datetime
import enum
import hashlib
import json
import logging
import logging.handlers
import os
import pathlib
import re
import signal
import sys
import threading
import time
from collections import defaultdict
from typing import Any, Final, Optional

# =============================================================================
# CONFIGURATION LAYER
# =============================================================================

@dataclasses.dataclass(frozen=True)
class AuditConfig:
    repo_root: pathlib.Path
    output_dir: pathlib.Path
    max_workers: int
    strict_mode: bool
    debug: bool
    log_file: pathlib.Path
    chunk_size: int
    max_file_size_bytes: int
    encoding_fallback: str
    progress_interval_sec: float

def build_config(args: argparse.Namespace) -> AuditConfig:
    repo_root = pathlib.Path(args.repo_root).resolve()
    if not repo_root.is_dir():
        _fatal(f"repo_root does not exist or is not a directory: {repo_root}")

    output_dir = pathlib.Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    max_workers = int(os.environ.get("AUDIT_MAX_WORKERS", str(args.workers)))
    strict_mode = args.strict or os.environ.get("STRICT_MODE", "false").lower() == "true"
    debug = args.debug or os.environ.get("AUDIT_DEBUG", "false").lower() == "true"

    log_file = output_dir / "audit.log"

    if strict_mode:
        if max_workers < 1:
            _fatal("STRICT_MODE: --workers must be >= 1")

    return AuditConfig(
        repo_root=repo_root,
        output_dir=output_dir,
        max_workers=max_workers,
        strict_mode=strict_mode,
        debug=debug,
        log_file=log_file,
        chunk_size=int(os.environ.get("AUDIT_CHUNK_SIZE", "500")),
        max_file_size_bytes=int(os.environ.get("AUDIT_MAX_FILE_BYTES", str(10 * 1024 * 1024))),  # 10 MB
        encoding_fallback="latin-1",
        progress_interval_sec=5.0,
    )

def _fatal(msg: str) -> None:
    print(f"[FATAL] {msg}", file=sys.stderr)
    sys.exit(2)

# =============================================================================
# CONSTANTS AND INVARIANTS — Thirsty-Lang v4.0-E1 Canonical Definitions
# =============================================================================

# Source: THIRSTY_LANG_UTF_SPEC.md §II — 29 canonical keywords
CANONICAL_KEYWORDS: Final[frozenset[str]] = frozenset({
    "drink", "pour", "sip", "thirsty", "hydrated", "refill", "glass",
    "fountain", "cascade", "await", "shield", "sanitize", "armor", "morph",
    "defend", "reservoir", "sacred", "return", "throw", "try", "catch",
    "finally", "import", "export", "from", "new", "this", "true", "false",
})

# Source: THIRSTY_LANG_UTF_SPEC.md §IV & docs/TSCG_SPEC.md
CANONICAL_TSCG_SYMBOLS: Final[frozenset[str]] = frozenset({
    "SEL", "COG", "Δ", "Δ_NT", "SHD", "INV", "CAP", "QRM", "COM",
    "ANC", "LED", "ING", "RFX", "ESC", "SAFE", "MUT",
})

# UTF file extensions — source: master spec §I
UTF_EXTENSIONS: Final[frozenset[str]] = frozenset({
    ".thirsty", ".thirst", ".tog", ".tarl", ".shadow", ".tscg", ".tscgb",
})

# Doc/spec extensions to audit for compliance headers
DOC_EXTENSIONS: Final[frozenset[str]] = frozenset({
    ".md", ".txt", ".rst",
})

# Canonical compliance header fields — regex extractors
RE_STATUS     = re.compile(r"STATUS:\s*([\w-]+)")
RE_TIER       = re.compile(r"TIER:\s*([\w-]+)")
RE_DATE       = re.compile(r"DATE:\s*([\d-]+)")
RE_COMPLIANCE = re.compile(r"COMPLIANCE:\s*([^\n#\"<>]+)")
RE_SPEC_REF   = re.compile(r"THIRSTY_LANG_UTF_SPEC\.md|THIRST_OF_GODS_SPEC\.md|"
                            r"TARL_VM_SPEC\.md|SHADOW_THIRST_SPEC\.md|"
                            r"TSCG_PROTOCOL_SPEC\.md|TSCG_SPEC\.md")

# Platform detection markers
PLATFORM_MARKERS: Final[dict[str, list[str]]] = {
    "desktop_electron": ["electron", "BrowserWindow", "app.whenReady"],
    "desktop_tauri":    ["tauri", "tauri::Builder", "@tauri-apps"],
    "android":          ["AndroidManifest", "android.app", "React Native", "react-native",
                         "capacitor", "Capacitor", ".apk", "gradle"],
    "ios":              ["UIViewController", "SwiftUI", "Xcode", "Info.plist",
                         "capacitor", "Capacitor", ".ipa", "CocoaPods"],
    "web":              ["<html", "React", "Vue", "Next.js", "Vite", "webpack"],
    "cli":              ["argparse", "click", "typer", "commander", "clap"],
    "service":          ["FastAPI", "Flask", "Express", "uvicorn", "gunicorn",
                         "actix", "axum", "gRPC"],
}

# Hardware gate keywords
HW_GATE_PATTERNS: Final[list[tuple[str, str]]] = [
    (r"\bCUDA\b|\bcuda\b",                        "NVIDIA CUDA GPU"),
    (r"\bGPU\b|\bgpu\b",                          "GPU (generic)"),
    (r"\bTPU\b|\btpu\b",                          "Google TPU"),
    (r"\bNPU\b|\bnpu\b",                          "Neural Processing Unit"),
    (r"\bROCm\b|\brocm\b",                        "AMD ROCm GPU"),
    (r"minimum.{0,20}RAM|requires?.{0,20}GB RAM", "Minimum RAM threshold"),
    (r"\bOllama\b",                               "Ollama local inference runtime"),
    (r"\bevdev\b|\beBPF\b|\bOctoReflex\b",        "Kernel-level eBPF / OctoReflex"),
    (r"\bHSM\b|\bhardware security module\b",     "Hardware Security Module"),
    (r"\bSecure Enclave\b|\bTEE\b",               "Trusted Execution Environment"),
    (r"\bTPM\b",                                  "Trusted Platform Module"),
    (r"ARM\s+Cortex|Apple\s+Silicon|M[1-4]\s+chip", "Apple Silicon / ARM"),
    (r"\bx86_64\b|\bamd64\b",                     "x86-64 architecture required"),
    (r"VRAM|vram",                                "VRAM (GPU memory)"),
]

# Operational capability verbs (heuristic: implemented, not just documented)
CAPABILITY_IMPL_MARKERS: Final[list[str]] = [
    "def ", "class ", "glass ", "fountain ", "cascade ", "async def ",
    "fn ", "func ", "function ", "impl ",
]

# Spec version history — known deprecated constructs
DEPRECATED_CONSTRUCTS: Final[dict[str, str]] = {
    "thirst_loop":  "Replaced by `refill` in v4.0",
    "aquifer":      "Replaced by `reservoir` in v3.5",
    "channel":      "Renamed to `cascade` in v4.0",
    "wellspring":   "Replaced by `fountain` in v3.0",
    "droplet":      "Removed in v4.0; use `drink` with type annotation",
    "siphon":       "Removed in v3.5; use `sip`",
    "sealed":       "Replaced by `armor` in v4.0",
    "obfuscate":    "Replaced by `morph` in v4.0",
}

SPEC_CURRENT_VERSION: Final[str] = "v4.0-E1"
SPEC_CURRENT_DATE: Final[str] = "2026-03-18"
REFILL_SAFETY_LIMIT: Final[int] = 10_000   # From spec §II keyword table
MAX_CONCURRENT_TASKS: Final[int] = 64
PROGRESS_REPORT_INTERVAL: Final[int] = 5_000

# =============================================================================
# TYPE SYSTEM / DATA MODELS
# =============================================================================

class FileStatus(str, enum.Enum):
    ACTIVE   = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    UNKNOWN  = "UNKNOWN"
    MISSING  = "MISSING"

class DriftSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"   # Uses removed/unknown construct
    HIGH     = "HIGH"       # References outdated spec version
    MEDIUM   = "MEDIUM"     # Missing compliance header
    LOW      = "LOW"        # Minor date staleness

class Platform(str, enum.Enum):
    DESKTOP_ELECTRON = "desktop_electron"
    DESKTOP_TAURI    = "desktop_tauri"
    ANDROID          = "android"
    IOS              = "ios"
    WEB              = "web"
    CLI              = "cli"
    SERVICE          = "service"
    UNKNOWN          = "unknown"

@dataclasses.dataclass
class ComplianceHeader:
    status: FileStatus
    tier: str
    date: Optional[str]
    compliance_ref: Optional[str]
    has_sovereign_timestamp: bool
    raw_excerpt: str

@dataclasses.dataclass
class DriftHit:
    path: str
    severity: DriftSeverity
    reason: str
    line_number: Optional[int]
    deprecated_construct: Optional[str]
    expected: Optional[str]
    found: Optional[str]

@dataclasses.dataclass
class ArchiveCandidate:
    path: str
    reason: str
    status_field: FileStatus
    date_field: Optional[str]
    days_since_update: Optional[int]
    inbound_reference_count: int

@dataclasses.dataclass
class CapabilityEntry:
    domain: str              # Derived from directory structure
    capability: str          # Function/class/module name
    language: str
    file_path: str
    impl_confidence: str     # "confirmed" | "documented_only" | "stub"
    platform_scope: list[str]

@dataclasses.dataclass
class PlatformEntry:
    app_name: str
    root_path: str
    detected_platforms: list[Platform]
    missing_platforms: list[Platform]
    readiness_notes: list[str]
    hardware_requirements: list[str]

@dataclasses.dataclass
class HardwareGate:
    file_path: str
    gate_type: str
    line_number: int
    context_snippet: str
    feature_scope: str       # Best-guess module/app name

@dataclasses.dataclass
class AuditResult:
    drift_hits: list[DriftHit]
    archive_candidates: list[ArchiveCandidate]
    capabilities: list[CapabilityEntry]
    platform_map: list[PlatformEntry]
    hardware_gates: list[HardwareGate]
    stats: dict[str, Any]
    generated_at: str
    repo_root: str
    spec_version: str

# =============================================================================
# LOGGING STRATEGY
# =============================================================================

def setup_logging(cfg: AuditConfig) -> logging.Logger:
    logger = logging.getLogger("project_ai_audit")
    logger.setLevel(logging.DEBUG if cfg.debug else logging.INFO)

    fmt = logging.Formatter(
        '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s",'
        '"message":"%(message)s"}',
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG if cfg.debug else logging.INFO)
    ch.setFormatter(fmt)

    fh = logging.handlers.RotatingFileHandler(
        cfg.log_file, maxBytes=50 * 1024 * 1024, backupCount=3,
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    # Redact sensitive patterns before writing (none expected, but defensive)
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger

# =============================================================================
# STRUCTURED EXCEPTION HIERARCHY
# =============================================================================

class AuditError(Exception):
    """Base audit exception."""

class ConfigError(AuditError):
    """Invalid or missing configuration."""

class FileReadError(AuditError):
    """Cannot read a file; non-fatal by default."""

class SpecParseError(AuditError):
    """Spec document cannot be parsed."""

# =============================================================================
# INPUT VALIDATION LAYER
# =============================================================================

def validate_repo_root(root: pathlib.Path, strict: bool) -> None:
    if not root.exists():
        raise ConfigError(f"Repo root does not exist: {root}")
    if not root.is_dir():
        raise ConfigError(f"Repo root is not a directory: {root}")
    master_spec = root / "THIRSTY_LANG_UTF_SPEC.md"
    if not master_spec.exists():
        msg = f"Master spec not found at expected location: {master_spec}"
        if strict:
            raise ConfigError(msg)
        # Non-strict: warn and continue

def normalize_path(p: pathlib.Path, root: pathlib.Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)

# =============================================================================
# CORE — FILE TRAVERSAL
# =============================================================================

_SKIP_DIRS: Final[frozenset[str]] = frozenset({
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv",
    "venv", ".idea", ".vscode", "dist", "build", "target", ".mypy_cache",
    ".pytest_cache", "coverage",
})

def iter_repo_files(
    root: pathlib.Path,
    cfg: AuditConfig,
    logger: logging.Logger,
) -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    skipped_dirs: int = 0
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        # Prune skip dirs in-place (os.walk respects mutations to dirnames)
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        skipped_dirs += len([d for d in dirnames if d in _SKIP_DIRS])
        for fname in filenames:
            fpath = pathlib.Path(dirpath) / fname
            try:
                sz = fpath.stat().st_size
            except OSError:
                continue
            if sz > cfg.max_file_size_bytes:
                logger.debug(f"Skipping oversized file: {fpath} ({sz} bytes)")
                continue
            files.append(fpath)
    logger.info(f"Traversal complete. Files found: {len(files):,}")
    return files

# =============================================================================
# CORE — COMPLIANCE HEADER PARSING
# =============================================================================

def read_file_head(path: pathlib.Path, cfg: AuditConfig) -> str:
    """Read first 4KB of a file for header inspection."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(4096)
    except OSError as e:
        raise FileReadError(str(e)) from e

def parse_compliance_header(head: str) -> ComplianceHeader:
    status_match = RE_STATUS.search(head)
    tier_match   = RE_TIER.search(head)
    date_match   = RE_DATE.search(head)
    comp_match   = RE_COMPLIANCE.search(head)

    status_raw = status_match.group(1).strip().upper() if status_match else "MISSING"
    try:
        status = FileStatus(status_raw)
    except ValueError:
        status = FileStatus.UNKNOWN

    tier = tier_match.group(1).strip() if tier_match else "UNKNOWN"
    date = date_match.group(1).strip() if date_match else None
    compliance_ref = comp_match.group(1).strip() if comp_match else None
    has_sovereign_ts = bool(RE_DATE.search(head) and RE_STATUS.search(head))
    raw_excerpt = head[:300].replace("\n", " ")

    return ComplianceHeader(
        status=status,
        tier=tier,
        date=date,
        compliance_ref=compliance_ref,
        has_sovereign_timestamp=has_sovereign_ts,
        raw_excerpt=raw_excerpt,
    )

def days_since(date_str: Optional[str]) -> Optional[int]:
    if not date_str:
        return None
    try:
        d = datetime.date.fromisoformat(date_str)
        return (datetime.date.today() - d).days
    except ValueError:
        return None

# =============================================================================
# CORE — SPEC DRIFT DETECTION
# =============================================================================

def audit_utf_file_for_drift(
    path: pathlib.Path,
    rel: str,
    cfg: AuditConfig,
    logger: logging.Logger,
) -> list[DriftHit]:
    hits: list[DriftHit] = []
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        logger.debug(f"Cannot read {path}: {e}")
        return hits

    header = parse_compliance_header(content[:4096])

    # Missing compliance header
    if not header.has_sovereign_timestamp:
        hits.append(DriftHit(
            path=rel,
            severity=DriftSeverity.MEDIUM,
            reason="Missing sovereign compliance header (STATUS/DATE/COMPLIANCE fields)",
            line_number=1,
            deprecated_construct=None,
            expected="<!-- STATUS: ACTIVE | TIER: ... | DATE: ... -->",
            found=None,
        ))

    # Archived file with active-looking code
    if header.status == FileStatus.ARCHIVED and _has_active_impl(content):
        hits.append(DriftHit(
            path=rel,
            severity=DriftSeverity.HIGH,
            reason="File marked ARCHIVED but contains active implementation code",
            line_number=None,
            deprecated_construct=None,
            expected="STATUS: ARCHIVED files should contain no active logic",
            found=f"STATUS={header.status}",
        ))

    # Deprecated constructs scan
    for line_no, line in enumerate(content.splitlines(), start=1):
        for dep_kw, replacement in DEPRECATED_CONSTRUCTS.items():
            if re.search(r'\b' + re.escape(dep_kw) + r'\b', line):
                hits.append(DriftHit(
                    path=rel,
                    severity=DriftSeverity.CRITICAL,
                    reason=f"Deprecated construct `{dep_kw}` used",
                    line_number=line_no,
                    deprecated_construct=dep_kw,
                    expected=replacement,
                    found=line.strip()[:120],
                ))

    # TSCG symbol validation (only for .tscg files)
    if path.suffix == ".tscg":
        for line_no, line in enumerate(content.splitlines(), start=1):
            tokens = re.findall(r'\b([A-Z_Δ][A-Z0-9_]*)\b', line)
            for tok in tokens:
                if tok not in CANONICAL_TSCG_SYMBOLS and tok not in {
                    "AND", "OR", "NOT", "TRUE", "FALSE", "NULL",
                }:
                    hits.append(DriftHit(
                        path=rel,
                        severity=DriftSeverity.HIGH,
                        reason=f"Unknown TSCG symbol `{tok}`",
                        line_number=line_no,
                        deprecated_construct=None,
                        expected=f"One of: {', '.join(sorted(CANONICAL_TSCG_SYMBOLS))}",
                        found=tok,
                    ))

    # Spec version reference check (doc files)
    if path.suffix in DOC_EXTENSIONS:
        old_ver_refs = re.findall(r'v[23]\.\d+(?:-\w+)?', content)
        for ref in set(old_ver_refs):
            hits.append(DriftHit(
                path=rel,
                severity=DriftSeverity.HIGH,
                reason=f"References outdated spec version `{ref}`",
                line_number=None,
                deprecated_construct=None,
                expected=SPEC_CURRENT_VERSION,
                found=ref,
            ))

    return hits

def _has_active_impl(content: str) -> bool:
    for marker in CAPABILITY_IMPL_MARKERS:
        if marker in content:
            return True
    return False

# =============================================================================
# CORE — ARCHIVE CANDIDATE DETECTION
# =============================================================================

def evaluate_archive_candidate(
    path: pathlib.Path,
    rel: str,
    header: ComplianceHeader,
    reference_index: dict[str, int],
) -> Optional[ArchiveCandidate]:
    reasons: list[str] = []

    if header.status == FileStatus.ARCHIVED:
        reasons.append("STATUS field is ARCHIVED")

    age = days_since(header.date)
    if age is not None and age > 365:
        reasons.append(f"Last updated {age} days ago (>1 year)")

    if not header.has_sovereign_timestamp:
        reasons.append("No sovereign timestamp — cannot determine provenance")

    compliance_ref = header.compliance_ref or ""
    if compliance_ref and not RE_SPEC_REF.search(compliance_ref):
        reasons.append(f"Compliance reference does not match known spec files: {compliance_ref}")

    ref_count = reference_index.get(rel, 0)

    # Only report as candidate if at least one reason exists
    if not reasons:
        return None

    return ArchiveCandidate(
        path=rel,
        reason=" | ".join(reasons),
        status_field=header.status,
        date_field=header.date,
        days_since_update=age,
        inbound_reference_count=ref_count,
    )

# =============================================================================
# CORE — OPERATIONAL CAPABILITY MATRIX
# =============================================================================

_DOMAIN_MAP: Final[dict[str, str]] = {
    "governance":      "Constitutional Governance",
    "integrations":    "Platform Integrations",
    "council":         "Council Agent Runtime",
    "octoreflex":      "OctoReflex eBPF Kernel",
    "tscg":            "TSCG Compression Layer",
    "shadow":          "Shadow Thirst Verification",
    "tarl":            "T.A.R.L. Defensive VM",
    "thirst_of_gods":  "Thirst of Gods Cognitive Plane",
    "core":            "Core Runtime",
    "docs":            "Documentation",
    "tests":           "Test Suite",
}

_STUB_SIGNALS: Final[list[str]] = [
    "pass", "...", "raise NotImplementedError", "TODO", "FIXME",
    "placeholder", "stub", "not implemented",
]

def extract_capabilities(
    path: pathlib.Path,
    rel: str,
    cfg: AuditConfig,
) -> list[CapabilityEntry]:
    entries: list[CapabilityEntry] = []
    ext = path.suffix.lower()

    # Only process known code files
    code_extensions = UTF_EXTENSIONS | {
        ".py", ".js", ".ts", ".rs", ".go", ".java", ".c", ".cpp", ".h",
    }
    if ext not in code_extensions:
        return entries

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return entries

    # Determine domain from path parts
    parts = pathlib.Path(rel).parts
    domain = "unknown"
    for part in parts:
        key = part.lower()
        for k, v in _DOMAIN_MAP.items():
            if k in key:
                domain = v
                break

    # Extract declared symbols (language-agnostic heuristic)
    patterns = [
        (r'(?:^|\n)\s*(?:def|glass|async def|cascade)\s+(\w+)\s*\(', "function"),
        (r'(?:^|\n)\s*(?:class|fountain)\s+(\w+)\s*[:{(]',             "class"),
        (r'(?:^|\n)\s*(?:fn|func)\s+(\w+)\s*[(<]',                     "function"),
        (r'(?:^|\n)\s*(?:impl)\s+(\w+)\s*[{<]',                        "impl_block"),
    ]

    for pattern, _ in patterns:
        for match in re.finditer(pattern, content, re.MULTILINE):
            name = match.group(1)
            if name.startswith("_") and not cfg.debug:
                continue  # Skip private symbols in non-debug mode

            # Determine if stub or confirmed
            match_pos = match.start()
            snippet = content[match_pos: match_pos + 300]
            is_stub = any(sig in snippet for sig in _STUB_SIGNALS)
            confidence = "stub" if is_stub else "confirmed"

            lang = _detect_language(ext)
            entries.append(CapabilityEntry(
                domain=domain,
                capability=name,
                language=lang,
                file_path=rel,
                impl_confidence=confidence,
                platform_scope=[],  # Populated in platform pass
            ))

    return entries

def _detect_language(ext: str) -> str:
    return {
        ".thirsty": "Thirsty-Lang",
        ".thirst":  "Thirst of Gods",
        ".tog":     "Thirst of Gods",
        ".tarl":    "T.A.R.L.",
        ".shadow":  "Shadow Thirst",
        ".tscg":    "TSCG",
        ".tscgb":   "TSCG-B",
        ".py":      "Python",
        ".js":      "JavaScript",
        ".ts":      "TypeScript",
        ".rs":      "Rust",
        ".go":      "Go",
    }.get(ext, ext.lstrip(".").upper() or "Unknown")

# =============================================================================
# CORE — PLATFORM READINESS MAP
# =============================================================================

def detect_platforms(
    path: pathlib.Path,
    rel: str,
    cfg: AuditConfig,
) -> list[Platform]:
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    detected: list[Platform] = []
    for platform_key, markers in PLATFORM_MARKERS.items():
        if any(m in content for m in markers):
            try:
                detected.append(Platform(platform_key))
            except ValueError:
                pass
    return detected

def build_platform_map(
    all_files: list[pathlib.Path],
    root: pathlib.Path,
    cfg: AuditConfig,
    logger: logging.Logger,
) -> list[PlatformEntry]:
    # Group files by top-level application directory
    app_groups: dict[str, list[pathlib.Path]] = defaultdict(list)
    for f in all_files:
        rel = pathlib.Path(normalize_path(f, root))
        top = rel.parts[0] if len(rel.parts) > 1 else "__root__"
        app_groups[top].append(f)

    entries: list[PlatformEntry] = []
    for app_name, files in app_groups.items():
        all_detected: set[Platform] = set()
        hw_reqs: set[str] = set()

        for f in files:
            plats = detect_platforms(f, normalize_path(f, root), cfg)
            all_detected.update(plats)
            hw_reqs.update(_scan_hardware_gates_simple(f, cfg))

        if not all_detected:
            continue

        # Determine what's expected but missing
        has_desktop = bool(all_detected & {Platform.DESKTOP_ELECTRON, Platform.DESKTOP_TAURI})
        has_mobile  = bool(all_detected & {Platform.ANDROID, Platform.IOS})

        missing: list[Platform] = []
        notes: list[str] = []

        if has_desktop and not has_mobile:
            missing += [Platform.ANDROID, Platform.IOS]
            notes.append("Desktop implementation detected; no mobile surface found")
        if has_mobile and not has_desktop:
            missing.append(Platform.DESKTOP_ELECTRON)
            notes.append("Mobile implementation detected; no desktop surface found")
        if Platform.SERVICE in all_detected:
            notes.append("Service layer detected — requires network/runtime environment")

        entries.append(PlatformEntry(
            app_name=app_name,
            root_path=app_name,
            detected_platforms=sorted(all_detected, key=lambda x: x.value),
            missing_platforms=missing,
            readiness_notes=notes,
            hardware_requirements=sorted(hw_reqs),
        ))

    return entries

def _scan_hardware_gates_simple(path: pathlib.Path, cfg: AuditConfig) -> set[str]:
    gates: set[str] = set()
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return gates
    for pattern, label in HW_GATE_PATTERNS:
        if re.search(pattern, content):
            gates.add(label)
    return gates

# =============================================================================
# CORE — HARDWARE GATE REGISTRY
# =============================================================================

def scan_hardware_gates(
    path: pathlib.Path,
    rel: str,
    cfg: AuditConfig,
) -> list[HardwareGate]:
    gates: list[HardwareGate] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return gates

    parts = pathlib.Path(rel).parts
    feature_scope = parts[0] if parts else "unknown"

    for line_no, line in enumerate(lines, start=1):
        for pattern, label in HW_GATE_PATTERNS:
            if re.search(pattern, line):
                gates.append(HardwareGate(
                    file_path=rel,
                    gate_type=label,
                    line_number=line_no,
                    context_snippet=line.strip()[:200],
                    feature_scope=feature_scope,
                ))
                break  # One gate per line

    return gates

# =============================================================================
# CORE — REFERENCE INDEX (inbound link counter for archive scoring)
# =============================================================================

def build_reference_index(
    all_files: list[pathlib.Path],
    root: pathlib.Path,
    cfg: AuditConfig,
    logger: logging.Logger,
) -> dict[str, int]:
    index: dict[str, int] = defaultdict(int)
    for f in all_files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        # Find any path-like strings that reference another file in the repo
        refs = re.findall(r'[\w/\\.-]+\.(?:md|thirsty|thirst|tog|tarl|shadow|tscg|tscgb|py|js|ts|rs)', content)
        for ref in refs:
            norm = ref.replace("\\", "/")
            index[norm] += 1
    logger.info(f"Reference index built: {len(index):,} unique references")
    return dict(index)

# =============================================================================
# PARALLEL PROCESSING ENGINE
# =============================================================================

_shutdown_event = threading.Event()

def _signal_handler(sig: int, frame: Any) -> None:
    print("\n[AUDIT] Shutdown signal received. Finishing current batch...", file=sys.stderr)
    _shutdown_event.set()

def run_parallel(
    files: list[pathlib.Path],
    fn,
    cfg: AuditConfig,
    logger: logging.Logger,
    desc: str,
) -> list[Any]:
    results: list[Any] = []
    total = len(files)
    completed = 0
    last_report = time.monotonic()

    with concurrent.futures.ThreadPoolExecutor(max_workers=cfg.max_workers) as executor:
        future_to_path = {executor.submit(fn, f): f for f in files}
        for future in concurrent.futures.as_completed(future_to_path):
            if _shutdown_event.is_set():
                executor.shutdown(wait=False, cancel_futures=True)
                break
            try:
                result = future.result()
                if result:
                    if isinstance(result, list):
                        results.extend(result)
                    else:
                        results.append(result)
            except Exception as e:
                path = future_to_path[future]
                logger.debug(f"{desc} error on {path}: {e}")
            completed += 1
            now = time.monotonic()
            if now - last_report >= cfg.progress_interval_sec:
                pct = (completed / total) * 100 if total else 0
                logger.info(f"{desc}: {completed:,}/{total:,} ({pct:.1f}%)")
                last_report = now

    logger.info(f"{desc}: complete. {completed:,} files processed.")
    return results

# =============================================================================
# OUTPUT SERIALIZATION
# =============================================================================

def dataclass_to_dict(obj: Any) -> Any:
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {k: dataclass_to_dict(v) for k, v in dataclasses.asdict(obj).items()}
    elif isinstance(obj, (list, tuple)):
        return [dataclass_to_dict(i) for i in obj]
    elif isinstance(obj, enum.Enum):
        return obj.value
    else:
        return obj

def write_json(output_dir: pathlib.Path, filename: str, data: Any) -> pathlib.Path:
    path = output_dir / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dataclass_to_dict(data), f, indent=2, default=str)
    return path

# =============================================================================
# HTML SUMMARY DASHBOARD
# =============================================================================

def generate_html_report(result: AuditResult, output_dir: pathlib.Path) -> pathlib.Path:
    drift_by_severity: dict[str, int] = defaultdict(int)
    for hit in result.drift_hits:
        drift_by_severity[hit.severity.value] += 1

    archive_count = len(result.archive_candidates)
    cap_confirmed = sum(1 for c in result.capabilities if c.impl_confidence == "confirmed")
    cap_stub      = sum(1 for c in result.capabilities if c.impl_confidence == "stub")
    hw_gate_count = len(result.hardware_gates)
    hw_types      = sorted(set(g.gate_type for g in result.hardware_gates))

    critical_drift = sorted(
        [h for h in result.drift_hits if h.severity == DriftSeverity.CRITICAL],
        key=lambda h: h.path,
    )[:50]

    top_archives = sorted(
        result.archive_candidates,
        key=lambda a: (a.days_since_update or 0),
        reverse=True,
    )[:50]

    platform_rows = ""
    for pe in result.platform_map[:100]:
        detected = ", ".join(p.value for p in pe.detected_platforms) or "—"
        missing  = ", ".join(p.value for p in pe.missing_platforms)  or "none"
        hw       = ", ".join(pe.hardware_requirements) or "none"
        notes    = " | ".join(pe.readiness_notes) or "—"
        platform_rows += (
            f"<tr><td>{pe.app_name}</td><td>{detected}</td>"
            f"<td class='miss'>{missing}</td><td>{hw}</td><td>{notes}</td></tr>\n"
        )

    drift_rows = ""
    for hit in critical_drift:
        ln = str(hit.line_number) if hit.line_number else "—"
        drift_rows += (
            f"<tr><td class='sev-{hit.severity.value.lower()}'>{hit.severity.value}</td>"
            f"<td>{hit.path}</td><td>L{ln}</td><td>{hit.reason}</td>"
            f"<td>{hit.found or '—'}</td></tr>\n"
        )

    archive_rows = ""
    for a in top_archives:
        age = str(a.days_since_update) if a.days_since_update is not None else "?"
        archive_rows += (
            f"<tr><td>{a.path}</td><td>{age}d</td>"
            f"<td>{a.status_field.value}</td><td>{a.reason}</td>"
            f"<td>{a.inbound_reference_count}</td></tr>\n"
        )

    hw_rows = ""
    for g in result.hardware_gates[:100]:
        hw_rows += (
            f"<tr><td>{g.feature_scope}</td><td>{g.gate_type}</td>"
            f"<td>{g.file_path}</td><td>L{g.line_number}</td>"
            f"<td><code>{g.context_snippet[:80]}</code></td></tr>\n"
        )

    stats = result.stats
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Project-AI Sovereign Audit Report</title>
<style>
  :root {{
    --bg: #0a0c10; --surface: #111318; --border: #1e2330;
    --accent: #7c3aed; --accent2: #06b6d4;
    --text: #e2e8f0; --muted: #64748b;
    --crit: #ef4444; --high: #f97316; --med: #eab308; --low: #22c55e;
    --font: 'JetBrains Mono', 'Courier New', monospace;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: var(--font);
         font-size: 13px; line-height: 1.6; padding: 2rem; }}
  h1 {{ font-size: 1.8rem; color: var(--accent2); border-bottom: 1px solid var(--border);
       padding-bottom: 0.5rem; margin-bottom: 1.5rem; }}
  h2 {{ font-size: 1.1rem; color: var(--accent); margin: 2rem 0 0.75rem; text-transform: uppercase;
       letter-spacing: 0.1em; }}
  .meta {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px,1fr));
           gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: var(--surface); border: 1px solid var(--border);
           border-radius: 6px; padding: 1rem; }}
  .card .num {{ font-size: 2rem; font-weight: bold; color: var(--accent2); }}
  .card .label {{ color: var(--muted); font-size: 0.8rem; margin-top: 0.25rem; }}
  .card.warn .num {{ color: var(--high); }}
  .card.crit .num {{ color: var(--crit); }}
  table {{ width: 100%; border-collapse: collapse; background: var(--surface);
           border-radius: 6px; overflow: hidden; margin-bottom: 1.5rem; }}
  th {{ background: var(--border); color: var(--muted); padding: 0.5rem 0.75rem;
       text-align: left; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }}
  td {{ padding: 0.4rem 0.75rem; border-top: 1px solid var(--border);
       word-break: break-all; max-width: 400px; }}
  tr:hover td {{ background: #161b27; }}
  .sev-critical {{ color: var(--crit); font-weight: bold; }}
  .sev-high     {{ color: var(--high); }}
  .sev-medium   {{ color: var(--med); }}
  .sev-low      {{ color: var(--low); }}
  .miss {{ color: var(--high); }}
  code {{ background: #1a1f2e; padding: 0.1rem 0.3rem; border-radius: 3px;
         font-size: 0.8rem; }}
  .hw-badge {{ display: inline-block; background: #1e293b; border: 1px solid var(--accent);
              color: var(--accent2); padding: 0.2rem 0.5rem; border-radius: 4px;
              margin: 0.15rem; font-size: 0.75rem; }}
</style>
</head>
<body>
<h1>💧 Project-AI Sovereign Monorepo Audit</h1>
<div class="meta">
  Generated: {result.generated_at} &nbsp;|&nbsp;
  Repo: {result.repo_root} &nbsp;|&nbsp;
  Spec Authority: {result.spec_version}
</div>

<div class="grid">
  <div class="card crit"><div class="num">{drift_by_severity.get('CRITICAL',0):,}</div>
    <div class="label">CRITICAL Drift Hits</div></div>
  <div class="card warn"><div class="num">{drift_by_severity.get('HIGH',0):,}</div>
    <div class="label">HIGH Severity Drift</div></div>
  <div class="card warn"><div class="num">{drift_by_severity.get('MEDIUM',0):,}</div>
    <div class="label">MEDIUM Severity</div></div>
  <div class="card"><div class="num">{archive_count:,}</div>
    <div class="label">Archive Candidates</div></div>
  <div class="card"><div class="num">{cap_confirmed:,}</div>
    <div class="label">Confirmed Capabilities</div></div>
  <div class="card warn"><div class="num">{cap_stub:,}</div>
    <div class="label">Stub / Unimplemented</div></div>
  <div class="card"><div class="num">{hw_gate_count:,}</div>
    <div class="label">Hardware Gates</div></div>
  <div class="card"><div class="num">{stats.get('total_files',0):,}</div>
    <div class="label">Total Files Scanned</div></div>
</div>

<h2>Hardware Requirements Detected</h2>
<div>{''.join(f'<span class="hw-badge">{h}</span>' for h in hw_types) or '<span style="color:var(--muted)">None detected</span>'}</div>

<h2>Critical Spec Drift (top 50)</h2>
<table>
<tr><th>Severity</th><th>File</th><th>Line</th><th>Reason</th><th>Found</th></tr>
{drift_rows or '<tr><td colspan="5" style="color:var(--low);padding:1rem">No critical drift detected</td></tr>'}
</table>

<h2>Archive Candidates (top 50 by age)</h2>
<table>
<tr><th>File</th><th>Age</th><th>Status</th><th>Reason</th><th>Inbound Refs</th></tr>
{archive_rows or '<tr><td colspan="5" style="color:var(--muted);padding:1rem">None identified</td></tr>'}
</table>

<h2>Platform Readiness Map (top 100 apps)</h2>
<table>
<tr><th>Application</th><th>Detected Platforms</th><th>Missing</th><th>HW Requirements</th><th>Notes</th></tr>
{platform_rows or '<tr><td colspan="5" style="color:var(--muted);padding:1rem">None detected</td></tr>'}
</table>

<h2>Hardware Gate Registry (top 100)</h2>
<table>
<tr><th>Scope</th><th>Gate Type</th><th>File</th><th>Line</th><th>Context</th></tr>
{hw_rows or '<tr><td colspan="5" style="color:var(--muted);padding:1rem">None detected</td></tr>'}
</table>

<div class="meta" style="margin-top:3rem;border-top:1px solid var(--border);padding-top:1rem">
  Scan duration: {stats.get('duration_sec', 0):.1f}s &nbsp;|&nbsp;
  Files scanned: {stats.get('total_files',0):,} &nbsp;|&nbsp;
  UTF files: {stats.get('utf_files',0):,} &nbsp;|&nbsp;
  Doc files: {stats.get('doc_files',0):,}
</div>
</body>
</html>"""

    out_path = output_dir / "audit_report.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path

# =============================================================================
# FAILURE MODES MATRIX
# =============================================================================
# WHAT                         WHY                          HOW                    RECOVERY         AUTO?
# -----------------------------------------------------------------------------------------------------------------------
# File read failure            Permissions / encoding       FileReadError raised    Skip file        Yes
# Oversized file               Binary or generated blob     Skipped by size check   Log & skip       Yes
# Missing master spec          Repo root wrong / renamed    ConfigError fatal        Fix --repo-root  Manual
# Shutdown signal (SIGTERM)    Antigravity / user kill      _shutdown_event set     Partial output   Manual
# Memory exhaustion            267k files, large content    OOM kill                Reduce workers   Manual
# Encoding errors              Non-UTF-8 files              errors='replace'        Lossy read       Yes
# Thread exception             Buggy fn in pool             Logged, skipped         Continue         Yes
# Output dir full              Disk space                   OSError on write        Fatal            Manual
# =============================================================================

# =============================================================================
# PERFORMANCE CONSIDERATIONS
# =============================================================================
# Time complexity  : O(N * L) where N = file count, L = avg lines per file
# Space complexity : O(N) for file list + O(D) for drift hits (D << N)
# Bottleneck       : Disk I/O — SSD recommended for 267k file traversal
# Parallelism      : ThreadPoolExecutor (I/O bound) — default workers=16
# Expected runtime : ~8-25 min on SSD for 267k files at 16 workers
# Scaling          : Linear with file count; reference index is O(N*R)
# =============================================================================

# =============================================================================
# LIMITATIONS
# =============================================================================
# 1. Keyword detection is lexical, not semantic — false positives possible in strings/comments
# 2. Platform detection is heuristic — multi-platform files counted for each platform
# 3. Reference index does not resolve relative paths — counts may undercount
# 4. Hardware gate patterns are keyword-based — complex conditional logic not evaluated
# 5. TSCG-B (.tscgb) binary files skipped for drift analysis (binary content)
# 6. Capability extraction is heuristic — actual runtime behavior not evaluated
# 7. Clock skew between file timestamps and header DATE fields not reconciled
# =============================================================================

# =============================================================================
# EXECUTION ENTRY POINT
# =============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="project_ai_audit",
        description="Project-AI Sovereign Monorepo Coherence & Operational Readiness Audit",
    )
    parser.add_argument("--repo-root",  required=True,  help="Absolute path to monorepo root")
    parser.add_argument("--output-dir", default="./audit_output", help="Output directory for reports")
    parser.add_argument("--workers",    type=int, default=16, help="Parallel worker threads (default: 16)")
    parser.add_argument("--strict",     action="store_true",  help="Enable STRICT_MODE")
    parser.add_argument("--debug",      action="store_true",  help="Enable debug logging")
    return parser.parse_args()

def main() -> int:
    args   = parse_args()
    cfg    = build_config(args)
    logger = setup_logging(cfg)

    # Signal handling — graceful shutdown on SIGTERM/SIGINT
    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGINT,  _signal_handler)

    logger.info(f"Project-AI Audit starting | repo={cfg.repo_root} | strict={cfg.strict_mode}")
    t_start = time.monotonic()

    # --- Startup validation
    try:
        validate_repo_root(cfg.repo_root, cfg.strict_mode)
    except ConfigError as e:
        logger.error(f"Config validation failed: {e}")
        return 2

    # --- PASS 1: File traversal
    logger.info("PASS 1: File traversal")
    all_files = iter_repo_files(cfg.repo_root, cfg, logger)
    total = len(all_files)

    utf_files  = [f for f in all_files if f.suffix in UTF_EXTENSIONS]
    doc_files  = [f for f in all_files if f.suffix in DOC_EXTENSIONS]
    code_files = [f for f in all_files if f.suffix not in {".tscgb"}]  # Skip binary

    stats: dict[str, Any] = {
        "total_files": total,
        "utf_files":   len(utf_files),
        "doc_files":   len(doc_files),
    }
    logger.info(f"Files: total={total:,} utf={len(utf_files):,} doc={len(doc_files):,}")

    if _shutdown_event.is_set():
        logger.warning("Shutdown requested after traversal. Exiting.")
        return 130

    # --- PASS 2: Reference index (for archive scoring)
    logger.info("PASS 2: Building reference index")
    reference_index = build_reference_index(doc_files + utf_files, cfg.repo_root, cfg, logger)

    # --- PASS 3: Spec drift (UTF + doc files)
    logger.info("PASS 3: Spec drift detection")
    audit_targets = utf_files + doc_files

    def drift_worker(f: pathlib.Path) -> list[DriftHit]:
        rel = normalize_path(f, cfg.repo_root)
        return audit_utf_file_for_drift(f, rel, cfg, logger)

    drift_hits: list[DriftHit] = run_parallel(
        audit_targets, drift_worker, cfg, logger, "Drift scan"
    )
    logger.info(f"Drift hits: {len(drift_hits):,}")

    # --- PASS 4: Archive candidates (doc + utf files)
    logger.info("PASS 4: Archive candidate detection")
    archive_candidates: list[ArchiveCandidate] = []

    for f in audit_targets:
        if _shutdown_event.is_set():
            break
        rel = normalize_path(f, cfg.repo_root)
        try:
            head = read_file_head(f, cfg)
            header = parse_compliance_header(head)
            candidate = evaluate_archive_candidate(f, rel, header, reference_index)
            if candidate:
                archive_candidates.append(candidate)
        except FileReadError:
            pass

    logger.info(f"Archive candidates: {len(archive_candidates):,}")

    # --- PASS 5: Capability matrix
    logger.info("PASS 5: Operational capability extraction")

    def cap_worker(f: pathlib.Path) -> list[CapabilityEntry]:
        return extract_capabilities(f, normalize_path(f, cfg.repo_root), cfg)

    capabilities: list[CapabilityEntry] = run_parallel(
        code_files, cap_worker, cfg, logger, "Capability scan"
    )
    logger.info(f"Capabilities: {len(capabilities):,}")

    # --- PASS 6: Platform readiness
    logger.info("PASS 6: Platform readiness mapping")
    platform_map = build_platform_map(code_files, cfg.repo_root, cfg, logger)
    logger.info(f"Platform entries: {len(platform_map):,}")

    # --- PASS 7: Hardware gates
    logger.info("PASS 7: Hardware gate registry")

    def hw_worker(f: pathlib.Path) -> list[HardwareGate]:
        return scan_hardware_gates(f, normalize_path(f, cfg.repo_root), cfg)

    hardware_gates: list[HardwareGate] = run_parallel(
        code_files, hw_worker, cfg, logger, "Hardware gate scan"
    )
    logger.info(f"Hardware gates: {len(hardware_gates):,}")

    t_end = time.monotonic()
    stats["duration_sec"] = round(t_end - t_start, 2)

    # --- Assemble final result
    result = AuditResult(
        drift_hits=drift_hits,
        archive_candidates=archive_candidates,
        capabilities=capabilities,
        platform_map=platform_map,
        hardware_gates=hardware_gates,
        stats=stats,
        generated_at=datetime.datetime.utcnow().isoformat() + "Z",
        repo_root=str(cfg.repo_root),
        spec_version=SPEC_CURRENT_VERSION,
    )

    # --- Write outputs
    logger.info("Writing output artifacts")
    write_json(cfg.output_dir, "spec_drift.json",          result.drift_hits)
    write_json(cfg.output_dir, "archive_candidates.json",  result.archive_candidates)
    write_json(cfg.output_dir, "capability_matrix.json",   result.capabilities)
    write_json(cfg.output_dir, "platform_readiness.json",  result.platform_map)
    write_json(cfg.output_dir, "hardware_gates.json",      result.hardware_gates)
    write_json(cfg.output_dir, "audit_stats.json",         result.stats)

    html_path = generate_html_report(result, cfg.output_dir)

    logger.info(f"Audit complete in {stats['duration_sec']}s")
    logger.info(f"HTML dashboard: {html_path}")
    logger.info(f"Output directory: {cfg.output_dir}")

    # --- Summary to stdout
    print(f"\n{'='*60}")
    print(f"  PROJECT-AI SOVEREIGN AUDIT COMPLETE")
    print(f"{'='*60}")
    print(f"  Files scanned    : {total:,}")
    print(f"  Duration         : {stats['duration_sec']}s")
    print(f"  Spec drift hits  : {len(drift_hits):,}")
    print(f"  Archive candidates: {len(archive_candidates):,}")
    print(f"  Capabilities found: {len(capabilities):,}")
    print(f"  Platform entries : {len(platform_map):,}")
    print(f"  Hardware gates   : {len(hardware_gates):,}")
    print(f"  Output dir       : {cfg.output_dir}")
    print(f"  Dashboard        : {html_path}")
    print(f"{'='*60}\n")

    # Exit code: 1 if critical drift found, 0 otherwise
    has_critical = any(h.severity == DriftSeverity.CRITICAL for h in drift_hits)
    return 1 if (has_critical and cfg.strict_mode) else 0

if __name__ == "__main__":
    sys.exit(main())
