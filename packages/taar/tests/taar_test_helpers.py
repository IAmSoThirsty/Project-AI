"""Shared non-fixture test helpers for the TAAR suite.

Lives outside conftest.py because conftest is a pytest plugin, not an
importable module, in this repo's no-__init__.py tests layout.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped, unused-ignore]


def edit_yaml(path: Path, mutate: Callable[[Any], None]) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
