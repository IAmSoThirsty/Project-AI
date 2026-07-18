from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from thirstys_standard_runtime.authority import generate_keypair, sign_document  # noqa: E402
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


def signed_proof(
    private: dict[str, Any],
    *,
    purpose: str,
    proof_id: str,
    scope: list[str],
    actions: list[str],
    principal_id: str = "Jeremy / Thirsty",
    action_id: str | None = None,
    expired: bool = False,
) -> dict[str, Any]:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "proof_id": proof_id,
        "principal_id": principal_id,
        "issued_at": (now - timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
        "expires_at": (now - timedelta(minutes=1) if expired else now + timedelta(hours=1))
        .isoformat()
        .replace("+00:00", "Z"),
        "scope": scope,
        "allowed_actions": actions,
        "nonce": "0123456789abcdef0123456789abcdef",
    }
    if action_id:
        payload["action_id"] = action_id
    return sign_document(payload, private, purpose)
