from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any


class PluginRunner:
    """Simple subprocess-based plugin runner using JSONL over stdin/stdout.

    Protocol (JSON lines):
    - Host -> Plugin: {"id": "<uuid>", "method": "init", "params": {...}}
    - Plugin -> Host: {"id": "<uuid>", "result": {...}} or {"id":"<uuid>", "error": "..."}

    This runner is intentionally small: it starts the subprocess, sends an `init` call,
    waits for a response (with timeout), and returns the parsed result.
    """

    def __init__(self, plugin_script: str, timeout: float = 5.0):
        self.plugin_script = Path(plugin_script)
        self.timeout = timeout
        self.proc: subprocess.Popen | None = None

    def start(self) -> None:
        if not self.plugin_script.exists():
            raise FileNotFoundError(f"Plugin script not found: {self.plugin_script}")
        cmd = [sys.executable, str(self.plugin_script)]
        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    def stop(self) -> None:
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=1.0)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass
        self.proc = None

    def _readline_nonblocking(self, timeout: float = 0.1) -> str | None:
        if not self.proc or not self.proc.stdout:
            return None
        end = time.time() + timeout
        while time.time() < end:
            line = self.proc.stdout.readline()
            if line:
                return line.rstrip("\n")
            time.sleep(0.01)
        return None

    def call_init(self, params: dict[str, Any]) -> dict[str, Any]:
        if not self.proc:
            self.start()
        assert self.proc and self.proc.stdin and self.proc.stdout
        msg = {"id": "init-1", "method": "init", "params": params}
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()

        start = time.time()
        buffer = ""
        while time.time() - start < self.timeout:
            line = self._readline_nonblocking(timeout=0.1)
            if line is None:
                continue
            buffer = line
            try:
                obj = json.loads(buffer)
                if obj.get("id") == msg["id"]:
                    return obj
            except Exception:
                continue
        # timeout
        raise TimeoutError("Plugin did not respond to init within timeout")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("plugin_script")
    args = parser.parse_args()
    runner = PluginRunner(args.plugin_script)
    try:
        res = runner.call_init({"example": True})
        print("OK", res)
    finally:
        runner.stop()
