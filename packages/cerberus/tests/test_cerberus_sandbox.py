"""Tests for cerberus.security.modules.sandbox.

Honest scope: covers PluginSandbox code validation (blocklist hits and
word-boundary non-hits), restricted-builtins execution, AgentSandbox
violation translation and real-subprocess execute_code (happy path +
timeout), and ContainerSandbox argv construction / fail-closed paths with a
monkeypatched subprocess (Docker is not assumed present). POSIX resource
limits (rlimits) are NOT exercised — the suite runs on Windows where they
are a documented no-op; the module's own docstring records that in-process
execution is a guard rail, not an isolation boundary.
"""

import subprocess
import sys
from typing import Any

import pytest
from cerberus.security import (
    AgentSandbox,
    ContainerSandbox,
    PluginSandbox,
    SandboxConfig,
    SandboxViolation,
)


class TestPluginValidation:
    @pytest.mark.parametrize(
        "code,blocked",
        [
            ("eval('1+1')", "eval"),
            ("exec('pass')", "exec"),
            ("compile(source, name, mode)", "compile"),
            ("__import__('os')", "__import__"),
            ("open('/etc/passwd')", "open"),
            ("x = input()", "input"),
        ],
    )
    def test_blocked_functions_rejected(self, code: str, blocked: str) -> None:
        with pytest.raises(SandboxViolation, match=f"Blocked function: {blocked}"):
            PluginSandbox().execute_plugin(code, None)

    @pytest.mark.parametrize("module", ["os", "sys", "subprocess", "socket", "shutil"])
    def test_blocked_imports_rejected(self, module: str) -> None:
        with pytest.raises(SandboxViolation, match=f"Blocked import: {module}"):
            PluginSandbox().execute_plugin(f"import {module}", None)

    def test_word_boundaries_do_not_false_positive(self) -> None:
        # 'input_data' must not trip 'input'; 'executed' must not trip 'exec';
        # 'osmodule' must not trip the 'os' import pattern.
        code = (
            "def process(input_data):\n"
            "    executed = str(input_data)\n"
            "    osmodule = len(executed)\n"
            "    return osmodule\n"
        )
        assert PluginSandbox().execute_plugin(code, "abcd") == 4


class TestPluginExecution:
    def test_plugin_runs_with_safe_builtins_and_allowed_modules(self) -> None:
        code = "def process(x):\n    return json.dumps(sorted(x))\n"
        assert PluginSandbox().execute_plugin(code, [3, 1, 2]) == "[1, 2, 3]"

    def test_missing_process_function_rejected(self) -> None:
        with pytest.raises(SandboxViolation, match="must define 'process'"):
            PluginSandbox().execute_plugin("x = 1", None)

    def test_unsafe_builtin_unavailable_at_runtime(self) -> None:
        code = "def process(x):\n    print(x)\n"
        with pytest.raises(NameError):
            PluginSandbox().execute_plugin(code, "hi")

    def test_allowed_module_list_is_mutable(self) -> None:
        sandbox = PluginSandbox()
        sandbox.add_allowed_module("statistics")
        code = "def process(x):\n    return statistics.mean(x)\n"
        assert sandbox.execute_plugin(code, [1, 2, 3]) == 2
        sandbox.remove_allowed_module("statistics")
        assert "statistics" not in sandbox.allowed_modules


class TestAgentSandbox:
    def test_memory_error_translated_to_violation(self) -> None:
        def exhaust() -> None:
            raise MemoryError

        with pytest.raises(SandboxViolation, match="Memory limit exceeded"):
            AgentSandbox().execute(exhaust)

    def test_other_exceptions_propagate(self) -> None:
        def boom() -> None:
            raise RuntimeError("unrelated")

        with pytest.raises(RuntimeError, match="unrelated"):
            AgentSandbox().execute(boom)

    def test_execute_code_runs_real_subprocess(self) -> None:
        result = AgentSandbox().execute_code("print('sandboxed-ok')")
        assert result["success"] is True
        assert result["returncode"] == 0
        assert "sandboxed-ok" in result["stdout"]

    def test_execute_code_timeout_fails_closed(self) -> None:
        with pytest.raises(SandboxViolation, match="Execution timeout"):
            AgentSandbox().execute_code("import time\ntime.sleep(30)", timeout=1)

    def test_sandboxed_env_drops_loader_injection_vars(self) -> None:
        env = AgentSandbox()._get_sandboxed_env()
        assert env["PYTHONPATH"] == ""
        for var in ("LD_PRELOAD", "LD_LIBRARY_PATH", "DYLD_INSERT_LIBRARIES"):
            assert var not in env

    def test_config_defaults(self) -> None:
        config = SandboxConfig()
        assert config.network_enabled is False
        assert config.filesystem_readonly is True


class TestContainerSandbox:
    def test_docker_absent_fails_closed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def no_docker(*args: Any, **kwargs: Any) -> None:
            raise FileNotFoundError("docker")

        monkeypatch.setattr(subprocess, "run", no_docker)
        with pytest.raises(SandboxViolation, match="Docker not available"):
            ContainerSandbox().execute(["python", "-V"])

    def test_timeout_fails_closed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def hangs(*args: Any, **kwargs: Any) -> None:
            raise subprocess.TimeoutExpired(cmd="docker", timeout=1)

        monkeypatch.setattr(subprocess, "run", hangs)
        with pytest.raises(SandboxViolation, match="Container execution timeout"):
            ContainerSandbox().execute(["python", "-V"], timeout=1)

    def test_isolation_flags_in_argv(self, monkeypatch: pytest.MonkeyPatch) -> None:
        captured: dict[str, list[str]] = {}

        def record(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
            captured["cmd"] = cmd
            return subprocess.CompletedProcess(cmd, returncode=0, stdout=b"ok", stderr=b"")

        monkeypatch.setattr(subprocess, "run", record)
        result = ContainerSandbox(memory_limit="256m", cpu_limit="2").execute(["echo", "hi"])

        assert result["success"] is True
        cmd = captured["cmd"]
        assert "--network=none" in cmd
        assert "--read-only" in cmd
        assert "--memory=256m" in cmd
        assert "--cpus=2" in cmd
        assert cmd[-2:] == ["echo", "hi"]


def test_execute_code_uses_current_interpreter() -> None:
    result = AgentSandbox().execute_code("import sys\nprint(sys.version_info.major)")
    assert result["stdout"].strip() == str(sys.version_info.major)
