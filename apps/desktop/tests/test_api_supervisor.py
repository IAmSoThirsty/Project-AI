from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest
from project_ai_desktop import api_supervisor as supervisor_module
from project_ai_desktop.api_supervisor import DEFAULT_URL, ApiSupervisor
from project_ai_desktop.local_paths import resolve_local_paths


class _FakeProcess:
    def __init__(self, port_file: Path, port: int, *, write_port: bool = True) -> None:
        self.port_file = port_file
        self.port = port
        self.terminated = False
        self.killed = False
        self._alive = True
        if write_port:
            port_file.write_text(str(port), encoding="utf-8")
            self._exited = False
        else:
            self._exited = True
            self._alive = False

    def poll(self) -> int | None:
        return None if self._alive else 0

    def terminate(self) -> None:
        self.terminated = True
        self._alive = False

    def kill(self) -> None:
        self.killed = True
        self._alive = False

    def wait(self, timeout: float | None = None) -> int:
        return 0


@pytest.fixture
def paths(tmp_path: Path) -> Any:
    return resolve_local_paths({"LOCALAPPDATA": str(tmp_path)})


def test_reuse_path_never_spawns(monkeypatch: pytest.MonkeyPatch, paths: Any) -> None:
    monkeypatch.setattr(supervisor_module, "_probe_health", lambda url, timeout: True)

    def fail_popen(*args: object, **kwargs: object) -> None:
        raise AssertionError("Popen must not be called when the default gateway is reachable")

    monkeypatch.setattr(supervisor_module.subprocess, "Popen", fail_popen)

    outcome = ApiSupervisor(paths=paths).ensure_running()
    assert outcome.ready
    assert outcome.url == DEFAULT_URL
    assert "reused" in outcome.reason


def test_dev_mode_never_spawns_when_unreachable(
    monkeypatch: pytest.MonkeyPatch, paths: Any
) -> None:
    monkeypatch.setattr(supervisor_module, "_probe_health", lambda url, timeout: False)
    monkeypatch.delattr(sys, "frozen", raising=False)

    def fail_popen(*args: object, **kwargs: object) -> None:
        raise AssertionError("Popen must not be called outside frozen/installed mode")

    monkeypatch.setattr(supervisor_module.subprocess, "Popen", fail_popen)

    outcome = ApiSupervisor(paths=paths).ensure_running()
    assert not outcome.ready
    assert "not spawning" in outcome.reason


def test_spawn_path_passes_token_audit_path_and_uses_dynamic_port(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, paths: Any
) -> None:
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(
        supervisor_module, "_probe_health", lambda url, timeout=None: url != DEFAULT_URL
    )

    fake_exe = tmp_path / "project-ai-api-server.exe"
    fake_exe.write_bytes(b"")
    monkeypatch.setattr(supervisor_module, "_resolve_api_exe_path", lambda: fake_exe)

    captured: dict[str, Any] = {}

    def fake_popen(args: list[str], *, env: dict[str, str], **kwargs: object) -> _FakeProcess:
        captured["args"] = args
        captured["env"] = env
        port_file = Path(args[args.index("--port-file") + 1])
        return _FakeProcess(port_file, port=54321)

    monkeypatch.setattr(supervisor_module.subprocess, "Popen", fake_popen)

    outcome = ApiSupervisor(paths=paths).ensure_running()

    assert outcome.ready
    assert outcome.url == "http://127.0.0.1:54321"
    assert captured["env"]["PROJECT_AI_API_TOKEN"]
    assert captured["env"]["PROJECT_AI_AUDIT_PATH"] == str(paths.data_dir / "chimera-audit.jsonl")


def test_terminate_is_noop_when_nothing_spawned(paths: Any) -> None:
    supervisor = ApiSupervisor(paths=paths)
    supervisor.terminate()  # must not raise


def test_terminate_terminates_spawned_process(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, paths: Any
) -> None:
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(
        supervisor_module, "_probe_health", lambda url, timeout=None: url != DEFAULT_URL
    )

    fake_exe = tmp_path / "project-ai-api-server.exe"
    fake_exe.write_bytes(b"")
    monkeypatch.setattr(supervisor_module, "_resolve_api_exe_path", lambda: fake_exe)

    spawned: list[_FakeProcess] = []

    def fake_popen(args: list[str], *, env: dict[str, str], **kwargs: object) -> _FakeProcess:
        port_file = Path(args[args.index("--port-file") + 1])
        process = _FakeProcess(port_file, port=11111)
        spawned.append(process)
        return process

    monkeypatch.setattr(supervisor_module.subprocess, "Popen", fake_popen)

    supervisor = ApiSupervisor(paths=paths)
    outcome = supervisor.ensure_running()
    assert outcome.ready
    supervisor.terminate()

    assert spawned[0].terminated


def test_spawn_health_timeout_reports_failure_without_raising(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, paths: Any
) -> None:
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(supervisor_module, "_SPAWN_HEALTH_TIMEOUT", 0.2)
    monkeypatch.setattr(supervisor_module, "_MAX_SPAWN_ATTEMPTS", 1)
    monkeypatch.setattr(supervisor_module, "_probe_health", lambda url, timeout=None: False)

    fake_exe = tmp_path / "project-ai-api-server.exe"
    fake_exe.write_bytes(b"")
    monkeypatch.setattr(supervisor_module, "_resolve_api_exe_path", lambda: fake_exe)

    spawned: list[_FakeProcess] = []

    def fake_popen(args: list[str], *, env: dict[str, str], **kwargs: object) -> _FakeProcess:
        port_file = Path(args[args.index("--port-file") + 1])
        process = _FakeProcess(port_file, port=22222)
        spawned.append(process)
        return process

    monkeypatch.setattr(supervisor_module.subprocess, "Popen", fake_popen)

    outcome = ApiSupervisor(paths=paths).ensure_running()

    assert not outcome.ready
    assert "did not become healthy" in outcome.reason
    assert spawned[0].terminated


def test_spawn_process_exit_before_port_reports_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, paths: Any
) -> None:
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(supervisor_module, "_PORT_FILE_TIMEOUT", 0.2)
    monkeypatch.setattr(supervisor_module, "_MAX_SPAWN_ATTEMPTS", 1)
    monkeypatch.setattr(supervisor_module, "_probe_health", lambda url, timeout=None: False)

    fake_exe = tmp_path / "project-ai-api-server.exe"
    fake_exe.write_bytes(b"")
    monkeypatch.setattr(supervisor_module, "_resolve_api_exe_path", lambda: fake_exe)

    def fake_popen(args: list[str], *, env: dict[str, str], **kwargs: object) -> _FakeProcess:
        port_file = Path(args[args.index("--port-file") + 1])
        return _FakeProcess(port_file, port=0, write_port=False)

    monkeypatch.setattr(supervisor_module.subprocess, "Popen", fake_popen)

    outcome = ApiSupervisor(paths=paths).ensure_running()

    assert not outcome.ready
    assert "exited before reporting a port" in outcome.reason
