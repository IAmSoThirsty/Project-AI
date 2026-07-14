"""Ensures a reachable local api gateway for the frozen desktop app.

Reuse-before-spawn is the whole safety model here: a single health probe
against the default gateway URL runs first, and if it succeeds this module
never touches ``subprocess`` at all. That is what guarantees the app never
terminates a process it did not start itself -- ``terminate()`` is only ever
meaningful after this module's own ``Popen`` call succeeded.

Port selection has no bind-then-relaunch race: the child process
(``project_ai_api.server``) binds its own listening socket and reports the
OS-assigned port via ``--port-file`` before it starts serving (see
``packages/api/src/project_ai_api/server.py``). This module never guesses or
pre-reserves a port; it only waits for the child to tell it one.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from project_ai_desktop.credentials import load_or_create_token
from project_ai_desktop.local_paths import LocalPaths, resolve_local_paths

DEFAULT_URL = "http://127.0.0.1:8000"
API_EXE_PATH_ENV = "PROJECT_AI_API_EXE_PATH"

_HEALTH_PROBE_TIMEOUT = 0.75
_SPAWN_HEALTH_TIMEOUT = 10.0
_PORT_FILE_TIMEOUT = 10.0
_MAX_SPAWN_ATTEMPTS = 3


@dataclass(frozen=True)
class SupervisorOutcome:
    ready: bool
    url: str
    reason: str = ""


def _probe_health(url: str, *, timeout: float) -> bool:
    try:
        with urlopen(f"{url}/health/live", timeout=timeout) as response:
            return bool(response.status == 200)
    except (URLError, OSError, ValueError):
        return False


def _default_api_exe_path() -> Path | None:
    """Sibling install-layout path for the bundled api exe.

    Burn installs the desktop and api packages as siblings under the same
    install root (see ``installer/windows/``): this executable's own
    directory has an ``..\\Api\\project-ai-api-server.exe`` sibling.
    """
    exe_dir = Path(sys.executable).resolve().parent
    candidate = exe_dir.parent / "Api" / "project-ai-api-server.exe"
    return candidate if candidate.exists() else None


def _resolve_api_exe_path() -> Path | None:
    override = os.getenv(API_EXE_PATH_ENV)
    if override:
        path = Path(override)
        return path if path.exists() else None
    return _default_api_exe_path()


class ApiSupervisor:
    """Ensures a reachable api gateway, spawning a bundled child only when needed."""

    def __init__(self, *, paths: LocalPaths | None = None) -> None:
        self._paths = paths or resolve_local_paths()
        self._process: subprocess.Popen[bytes] | None = None
        self._token = ""

    def ensure_running(self) -> SupervisorOutcome:
        if _probe_health(DEFAULT_URL, timeout=_HEALTH_PROBE_TIMEOUT):
            return SupervisorOutcome(True, DEFAULT_URL, "reused existing gateway")

        if not getattr(sys, "frozen", False):
            return SupervisorOutcome(
                False, DEFAULT_URL, "no gateway reachable; not spawning in source/dev mode"
            )

        exe_path = _resolve_api_exe_path()
        if exe_path is None:
            return SupervisorOutcome(False, DEFAULT_URL, "bundled api executable not found")

        self._paths.ensure()
        self._token = load_or_create_token(self._paths)
        audit_path = self._paths.data_dir / "chimera-audit.jsonl"

        reason = "spawn failed"
        for _attempt in range(_MAX_SPAWN_ATTEMPTS):
            outcome = self._spawn_once(exe_path, audit_path)
            if outcome.ready:
                return outcome
            reason = outcome.reason
        return SupervisorOutcome(False, DEFAULT_URL, reason)

    def _spawn_once(self, exe_path: Path, audit_path: Path) -> SupervisorOutcome:
        port_file = self._reserve_port_file_path()
        env = {
            **os.environ,
            "PROJECT_AI_API_TOKEN": self._token,
            "PROJECT_AI_AUDIT_PATH": str(audit_path),
        }
        process = subprocess.Popen(
            [str(exe_path), "--host", "127.0.0.1", "--port", "0", "--port-file", str(port_file)],
            env=env,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        port = self._wait_for_port(port_file, process)
        port_file.unlink(missing_ok=True)
        if port is None:
            self._cleanup_process(process)
            return SupervisorOutcome(
                False, DEFAULT_URL, "api process exited before reporting a port"
            )

        url = f"http://127.0.0.1:{port}"
        if self._wait_for_health(url):
            self._process = process
            return SupervisorOutcome(True, url)

        self._cleanup_process(process)
        return SupervisorOutcome(False, DEFAULT_URL, "api process did not become healthy in time")

    def _reserve_port_file_path(self) -> Path:
        with tempfile.NamedTemporaryFile(
            dir=self._paths.data_dir, prefix="api-port-", suffix=".txt", delete=False
        ) as handle:
            port_file = Path(handle.name)
        port_file.unlink(missing_ok=True)
        return port_file

    @staticmethod
    def _wait_for_port(port_file: Path, process: subprocess.Popen[bytes]) -> int | None:
        deadline = time.monotonic() + _PORT_FILE_TIMEOUT
        while time.monotonic() < deadline:
            if process.poll() is not None:
                return None
            if port_file.exists():
                content = port_file.read_text(encoding="utf-8").strip()
                if content.isdigit():
                    return int(content)
            time.sleep(0.05)
        return None

    @staticmethod
    def _wait_for_health(url: str) -> bool:
        deadline = time.monotonic() + _SPAWN_HEALTH_TIMEOUT
        while time.monotonic() < deadline:
            if _probe_health(url, timeout=1.0):
                return True
            time.sleep(0.1)
        return False

    @staticmethod
    def _cleanup_process(process: subprocess.Popen[bytes]) -> None:
        if process.poll() is not None:
            return
        process.terminate()
        try:
            process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5.0)

    def terminate(self) -> None:
        """No-op unless this instance actually spawned a child process."""
        if self._process is None:
            return
        self._cleanup_process(self._process)
        self._process = None
