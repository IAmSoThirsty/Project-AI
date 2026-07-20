from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = (
    PACKAGE_ROOT / "tools" / "create_owner_key.py",
    Path(__file__).resolve().parents[3]
    / "docs"
    / "governance"
    / "thirstys-standard-v3q-manifest"
    / "tools"
    / "create_owner_key.py",
)


def run_tool(script: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *arguments],
        capture_output=True,
        check=False,
        text=True,
    )


@pytest.mark.parametrize("script", SCRIPTS)
def test_rotation_requires_explicit_replacement_key_id(script: Path, tmp_path: Path) -> None:
    result = run_tool(
        script,
        "--private-out",
        str(tmp_path / "owner-private.json"),
        "--public-out",
        str(tmp_path / "owner-public.json"),
    )

    assert result.returncode != 0
    assert "--key-id" in result.stderr


@pytest.mark.parametrize("script", SCRIPTS)
def test_rotation_rejects_retired_key_id(script: Path, tmp_path: Path) -> None:
    result = run_tool(
        script,
        "--key-id",
        "owner-primary",
        "--private-out",
        str(tmp_path / "owner-private.json"),
        "--public-out",
        str(tmp_path / "owner-public.json"),
    )

    assert result.returncode != 0
    assert "owner-primary is retired" in result.stderr
    assert not (tmp_path / "owner-private.json").exists()


@pytest.mark.parametrize("script", SCRIPTS)
def test_rotation_rejects_private_output_inside_checkout(script: Path) -> None:
    private_path = PACKAGE_ROOT / ".test-owner-private.json"
    public_path = PACKAGE_ROOT / ".test-owner-public.json"
    try:
        result = run_tool(
            script,
            "--key-id",
            "owner-test-rotation",
            "--private-out",
            str(private_path),
            "--public-out",
            str(public_path),
        )
    finally:
        private_path.unlink(missing_ok=True)
        public_path.unlink(missing_ok=True)

    assert result.returncode != 0
    assert "inside the repository checkout" in result.stderr


@pytest.mark.parametrize("script", SCRIPTS)
def test_rotation_writes_replacement_key_only_off_repo(script: Path, tmp_path: Path) -> None:
    private_path = tmp_path / "owner-private.json"
    public_path = tmp_path / "owner-public.json"
    result = run_tool(
        script,
        "--key-id",
        "owner-test-rotation",
        "--private-out",
        str(private_path),
        "--public-out",
        str(public_path),
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(private_path.read_text(encoding="utf-8"))["key_id"] == "owner-test-rotation"
    assert json.loads(public_path.read_text(encoding="utf-8"))["key_id"] == "owner-test-rotation"
