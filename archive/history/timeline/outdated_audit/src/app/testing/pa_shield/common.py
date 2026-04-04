"""Shared helpers for PA-SHIELD."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


def find_repo_root(start: Path | None = None) -> Path:
    """Walk upward until a repository root marker is found."""
    current = (start or Path(__file__).resolve()).resolve()
    candidates = [current, *current.parents]
    for candidate in candidates:
        if (candidate / "pyproject.toml").exists():
            return candidate
    raise FileNotFoundError("Unable to locate repository root from PA-SHIELD.")


def stable_digest(value: Any) -> str:
    """Create a stable SHA256 digest for nested JSON-serializable values."""
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def slugify(value: str) -> str:
    """Create a filesystem-safe slug."""
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return cleaned or "artifact"
