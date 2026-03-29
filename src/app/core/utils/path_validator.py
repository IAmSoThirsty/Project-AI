# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / path_validator.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / path_validator.py

"""Centralized path validation for Project-AI security.

Prevents path traversal attacks by ensuring all internal file operations
are restricted to designated base directories.
"""

import os
from pathlib import Path


def validate_path(path: str, base_dir: str, allow_missing: bool = True) -> str | None:
    """
    Validates that a path is within the base_dir and normalized.

    Returns the absolute path string if valid, None otherwise.
    """
    try:
        resolved_base = Path(base_dir).resolve()
        target_path = Path(os.path.abspath(path))

        # Check if target_path is a child of resolved_base
        if resolved_base in target_path.parents or target_path == resolved_base:
            return str(target_path)

        return None
    except Exception:
        return None


def secure_join(base: str, *parts: str) -> str | None:
    """Safely joins paths and validates they remain within base."""
    joined = os.path.join(base, *parts)
    return validate_path(joined, base)
