from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from thirstys_standard_runtime.authority import generate_keypair  # noqa: E402
from thirstys_standard_runtime.strict_yaml import load  # noqa: E402


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def manifest(root: Path) -> dict[str, Any]:
    return load(root / "thirstys-standard-v3q.manifest.yaml")


@pytest.fixture
def owner_keys() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    private, public = generate_keypair(
        "owner-test",
        "Jeremy / Thirsty",
        ["authority", "approval", "ratification", "execution_record"],
    )
    return private, public, {"keys": [public]}
