from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen


def _wait_for_port_file(port_file: Path, *, timeout: float = 10.0) -> int:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if port_file.exists():
            content = port_file.read_text(encoding="utf-8").strip()
            if content:
                return int(content)
        time.sleep(0.05)
    raise TimeoutError(f"port file {port_file} was not written within {timeout}s")


def test_server_binds_atomically_and_serves_health(tmp_path: Path) -> None:
    port_file = tmp_path / "api.port"
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "project_ai_api.server",
            "--host",
            "127.0.0.1",
            "--port",
            "0",
            "--port-file",
            str(port_file),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        port = _wait_for_port_file(port_file)
        assert port > 0

        deadline = time.monotonic() + 10.0
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                with urlopen(f"http://127.0.0.1:{port}/health/live", timeout=1.0) as response:
                    assert response.status == 200
                    return
            except OSError as error:  # server not accepting connections yet
                last_error = error
                time.sleep(0.1)
        raise AssertionError(f"health check never succeeded: {last_error}")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5.0)
