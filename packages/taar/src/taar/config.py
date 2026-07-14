"""TAAR configuration and path initialization.

taar.toml is optional. Missing config falls back to safe defaults.
Automation output directories are always created. Registry files are
NEVER created implicitly — a missing registry fails closed at run time.
"""

from __future__ import annotations

import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from taar.errors import ConfigError
from taar.models import FACILITY_MODES

DEFAULT_AUTOMATION_ROOT = ".project-ai/automation"

DEFAULT_GLOBAL_LIMITS: dict[str, int] = {
    "max_total_processes": 6,
    "max_active_workers": 3,
    "max_active_readers": 2,
    "max_active_writers": 1,
    "max_heavy_agents": 1,
    "max_git_mutators": 0,
    "max_patch_writers": 0,
    "max_branch_writers": 0,
}

DEFAULT_STALE_PATH_PATTERNS: list[str] = [
    "T:\\Project-AI-Beginnings",
    "T:/Project-AI-Beginnings",
    "T:\\Project-AI-main",
    "T:/Project-AI-main",
    "Project-AI-main",
]

_AUTOMATION_SUBDIRS = (
    "evidence",
    "reports",
    "digests",
    "patches",
    "quarantine",
    "audit",
    "locks",
    "cache",
)


@dataclass(frozen=True)
class TaarConfig:
    repo_root: Path
    automation_root: Path
    evidence_root: Path
    reports_root: Path
    digests_root: Path
    patches_root: Path
    quarantine_root: Path
    audit_root: Path
    locks_root: Path
    cache_root: Path
    state_db: Path
    registry_root: Path
    facility_mode: str = "GREEN"
    global_limits: dict[str, int] = field(default_factory=lambda: dict(DEFAULT_GLOBAL_LIMITS))
    stale_path_patterns: list[str] = field(
        default_factory=lambda: list(DEFAULT_STALE_PATH_PATTERNS)
    )


def resolve_repo_root(start: Path | None = None) -> Path:
    """Resolve the repo root: nearest ancestor containing taar.toml or .git,
    otherwise the starting directory itself.

    A repo marker sitting directly at the OS temp root (e.g. a stray ``.git``
    there on a developer machine) is ignored, so an isolated temp checkout
    never resolves its root to the temp area.
    """
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if candidate == _TEMP_DIR:
            continue
        if (candidate / "taar.toml").exists() or (candidate / ".git").exists():
            return candidate
    return current


_TEMP_DIR = Path(tempfile.gettempdir()).resolve()


def load_taar_config(repo_root: Path | None = None) -> TaarConfig:
    root = resolve_repo_root(repo_root)
    automation_rel = DEFAULT_AUTOMATION_ROOT
    facility_mode = "GREEN"
    limits = dict(DEFAULT_GLOBAL_LIMITS)
    stale_patterns = list(DEFAULT_STALE_PATH_PATTERNS)

    toml_path = root / "taar.toml"
    if toml_path.exists():
        try:
            raw = tomllib.loads(toml_path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            raise ConfigError(f"taar.toml is malformed: {exc}") from exc
        paths = raw.get("paths", {})
        automation_rel = paths.get("automation_root", automation_rel)
        facility = raw.get("facility", {})
        mode = str(facility.get("mode", facility_mode)).upper()
        if mode not in FACILITY_MODES:
            raise ConfigError(f"Unknown facility mode: {mode}")
        facility_mode = mode
        limits.update({k: int(v) for k, v in raw.get("limits", {}).items()})
        drift = raw.get("path_drift", {})
        if "stale_patterns" in drift:
            stale_patterns = [str(p) for p in drift["stale_patterns"]]

    automation_root = (root / automation_rel).resolve()
    config = TaarConfig(
        repo_root=root,
        automation_root=automation_root,
        evidence_root=automation_root / "evidence",
        reports_root=automation_root / "reports",
        digests_root=automation_root / "digests",
        patches_root=automation_root / "patches",
        quarantine_root=automation_root / "quarantine",
        audit_root=automation_root / "audit",
        locks_root=automation_root / "locks",
        cache_root=automation_root / "cache",
        state_db=automation_root / "state.db",
        registry_root=root / "registry",
        facility_mode=facility_mode,
        global_limits=limits,
        stale_path_patterns=stale_patterns,
    )
    ensure_automation_dirs(config)
    return config


def ensure_automation_dirs(config: TaarConfig) -> None:
    """Create automation output directories. Never creates registry files."""
    for sub in _AUTOMATION_SUBDIRS:
        (config.automation_root / sub).mkdir(parents=True, exist_ok=True)


def get_facility_mode(config: TaarConfig) -> str:
    return config.facility_mode


def load_global_limits(config: TaarConfig) -> dict[str, int]:
    return dict(config.global_limits)
