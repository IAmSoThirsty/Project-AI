from __future__ import annotations

import json
from pathlib import Path

import pytest
from knowledge.repository_cli import main


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    (root / "src" / "service.py").write_text(
        "def search_repository(query):\n    return query\n", encoding="utf-8"
    )
    (root / "README.md").write_text(
        "# Repository\n\nOffline repository intelligence.\n", encoding="utf-8"
    )
    return root


def test_build_writes_artifacts_and_reports_ready(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo(tmp_path)
    output = tmp_path / "index"
    exit_code = main(["build", "--root", str(root), "--output", str(output)])
    assert exit_code == 0
    assert (output / "manifest.json").exists()
    assert (output / "records.json").exists()
    assert (output / "status.json").exists()
    payload = json.loads(capsys.readouterr().out)
    assert payload["state"] == "ready"
    assert payload["stale"] is False
    assert payload["indexed_chunks"] > 0


def test_status_after_build_reports_ready(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo(tmp_path)
    output = tmp_path / "index"
    assert main(["build", "--root", str(root), "--output", str(output)]) == 0
    capsys.readouterr()
    exit_code = main(["status", "--root", str(root), "--output", str(output)])
    assert exit_code == 0
    assert json.loads(capsys.readouterr().out)["state"] == "ready"


def test_status_on_missing_index_fails_closed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo(tmp_path)
    output = tmp_path / "absent"
    exit_code = main(["status", "--root", str(root), "--output", str(output)])
    assert exit_code == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["state"] == "missing"
    assert payload["stale"] is True


def test_status_detects_stale_index_after_source_change(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo(tmp_path)
    output = tmp_path / "index"
    assert main(["build", "--root", str(root), "--output", str(output)]) == 0
    capsys.readouterr()
    (root / "README.md").write_text("# Repository\n\nchanged content\n", encoding="utf-8")
    exit_code = main(["status", "--root", str(root), "--output", str(output)])
    assert exit_code == 2
    assert json.loads(capsys.readouterr().out)["stale"] is True


def test_unknown_command_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main(["inspect", "--root", str(tmp_path), "--output", str(tmp_path)])
