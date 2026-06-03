"""
Genesis Continuity Protection System

Module-level shared state detects Genesis deletion/regeneration (VECTOR 1) and
public key replacement (VECTOR 2, 11) within a running process.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
GENESIS_CONTINUITY_LOG_ENV = "PROJECT_AI_GENESIS_CONTINUITY_LOG"

# IRON_PATH_2_PHASE_1_ANNOTATION_ONLY
# IRON_PATH_2_STOP_CONDITION: genesis continuity working-tree state unresolved
# Current behavior: genesis_continuity.py has unstaged modifications, so this core substrate's current state is not clean.
# Required before Phase 2+: The user must decide whether to keep, commit, or revert the existing modifications, then baseline tests must be re-run.
# Do not change behavior in Phase 1.

# ── module-level shared state (process-wide, resets on interpreter restart) ────
_LOCK = threading.Lock()
_KEY_DIR_PINS: dict[str, str] = {}        # key_dir_str → genesis_id
_GENESIS_PINS: dict[str, str] = {}        # genesis_id  → sha256(pub_key_bytes) hex
_VIOLATIONS: list[dict[str, Any]] = []


class GenesisDiscontinuityError(Exception):
    """Raised when Genesis discontinuity is detected — FATAL constitutional violation."""


class GenesisReplacementError(Exception):
    """Raised when Genesis public key replacement is detected — FATAL constitutional violation."""


class GenesisContinuityGuard:
    """
    Guards against VECTOR 1 (Genesis deletion/regeneration) and VECTOR 2/11
    (key replacement / full-wipe) within a single process.

    All instances share the same module-level state so that a fresh
    GenesisContinuityGuard() in the same test run sees the same violations.

    Optional file paths are accepted for API compatibility and for persisting
    violations to disk when running the manual test suite.
    """

    def __init__(
        self,
        external_pins_file: Path | None = None,
        continuity_log_file: Path | None = None,
    ) -> None:
        self._pins_file = Path(external_pins_file) if external_pins_file else None
        self._log_file = Path(continuity_log_file) if continuity_log_file else None

    # ── primary API ──────────────────────────────────────────────────────────

    def check_or_pin(
        self,
        key_dir: Path,
        genesis_id: str,
        pub_key_bytes: bytes,
    ) -> None:
        """Pin genesis identity for key_dir or verify it hasn't changed.

        Raises GenesisDiscontinuityError if a different genesis_id was previously
        pinned for this key_dir (VECTOR 1 attack detected).
        """
        key_dir_str = str(Path(key_dir)).replace("\\", "/")
        pub_key_hash = hashlib.sha256(pub_key_bytes).hexdigest()

        with _LOCK:
            if key_dir_str in _KEY_DIR_PINS:
                expected_id = _KEY_DIR_PINS[key_dir_str]
                if expected_id != genesis_id:
                    violation: dict[str, Any] = {
                        "violation_type": "GENESIS_DISCONTINUITY",
                        "detected_at": datetime.now(timezone.utc).isoformat(),
                        "genesis_id_expected": expected_id,
                        "genesis_id_actual": genesis_id,
                        "key_dir": key_dir_str,
                        "attack_vector": "VECTOR 1",
                    }
                    _VIOLATIONS.append(violation)
                    self._persist_violation(violation)
                    raise GenesisDiscontinuityError(
                        f"Genesis discontinuity detected for {key_dir_str}: "
                        f"expected {expected_id}, got {genesis_id}. "
                        f"VECTOR 1 attack — system MUST freeze. "
                        f"Replay validation PERMANENTLY FAILED."
                    )
                # Same genesis_id at this key_dir — keep going
            else:
                # First time seeing this key_dir in this process
                _KEY_DIR_PINS[key_dir_str] = genesis_id
                if genesis_id not in _GENESIS_PINS:
                    _GENESIS_PINS[genesis_id] = pub_key_hash

    def verify_genesis_continuity(
        self,
        genesis_id: str,
        public_key_bytes: bytes,
    ) -> tuple[bool, str]:
        """Verify that public_key_bytes matches what was pinned for genesis_id.

        Returns (False, error_message) on mismatch (VECTOR 2 replacement detected).
        """
        current_hash = hashlib.sha256(public_key_bytes).hexdigest()
        with _LOCK:
            if genesis_id not in _GENESIS_PINS:
                return True, f"No pin found for {genesis_id} — cannot verify"
            if _GENESIS_PINS[genesis_id] != current_hash:
                return (
                    False,
                    f"Genesis public key replacement detected for {genesis_id}: "
                    f"pinned hash {_GENESIS_PINS[genesis_id][:16]}… "
                    f"does not match current {current_hash[:16]}…",
                )
            return True, "Genesis continuity verified"

    def get_pinned_genesis_ids(self) -> list[str]:
        """Return all genesis IDs pinned in this process."""
        with _LOCK:
            return list(_GENESIS_PINS.keys())

    @property
    def external_pins(self) -> dict[str, str]:
        """Dict of genesis_id → pub_key_hash for all pinned identities."""
        with _LOCK:
            return dict(_GENESIS_PINS)

    def get_violations(self) -> list[dict[str, Any]]:
        """Return all recorded constitutional violations (module + file)."""
        with _LOCK:
            violations = list(_VIOLATIONS)

        # Also merge from a custom continuity log file if one was given
        if self._log_file and self._log_file.exists():
            try:
                with open(self._log_file, encoding="utf-8") as f:
                    file_violations: list[dict[str, Any]] = json.load(f)
                seen = {(v.get("genesis_id_expected"), v.get("detected_at")) for v in violations}
                for v in file_violations:
                    key = (v.get("genesis_id_expected"), v.get("detected_at"))
                    if key not in seen:
                        violations.append(v)
            except Exception:
                pass

        return violations

    def is_system_compromised(self) -> bool:
        return len(self.get_violations()) > 0

    # ── persistence helpers ──────────────────────────────────────────────────

    def _persist_violation(self, violation: dict[str, Any]) -> None:
        """Append violation to disk files (best-effort)."""
        for path in self._violation_paths():
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                existing: list[dict[str, Any]] = []
                if path.exists():
                    with open(path, encoding="utf-8") as f:
                        existing = json.load(f)
                existing.append(violation)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(existing, f, indent=2)
            except Exception as exc:
                logger.debug("Failed to persist violation to %s: %s", path, exc)

    def _violation_paths(self) -> list[Path]:
        if self._log_file:
            return [self._log_file]

        env_path = os.environ.get(GENESIS_CONTINUITY_LOG_ENV)
        if env_path:
            return [Path(env_path)]

        default = (
            Path(__file__).resolve().parents[3]
            / "data" / "genesis_pins" / "continuity_log.json"
        )
        return [default]


__all__ = [
    "GenesisContinuityGuard",
    "GenesisDiscontinuityError",
    "GenesisReplacementError",
]
