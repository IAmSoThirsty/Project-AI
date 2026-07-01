from __future__ import annotations

import ast
import importlib
import io
import json
import os
import tomllib
from email.message import Message
from pathlib import Path
from types import ModuleType
from typing import Any, cast
from urllib.error import HTTPError, URLError

import pytest
from project_ai_cli import GatewayError, HttpGateway
from project_ai_cli.app import app
from project_ai_cli.client import JsonObject
from typer.testing import CliRunner


class FakeGateway:
    def __init__(self) -> None:
        self.requests: list[tuple[str, str, JsonObject | None, bool]] = []
        self.response: JsonObject = {"status": "ok"}
        self.error: GatewayError | None = None

    def request(
        self,
        method: str,
        path: str,
        *,
        payload: JsonObject | None = None,
        protected: bool = False,
    ) -> JsonObject:
        self.requests.append((method, path, payload, protected))
        if self.error is not None:
            raise self.error
        return self.response


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def gateway(monkeypatch: pytest.MonkeyPatch) -> FakeGateway:
    fake = FakeGateway()
    app_module = importlib.import_module("project_ai_cli.app")
    monkeypatch.setattr(app_module, "HttpGateway", lambda *args, **kwargs: fake)
    return fake


@pytest.mark.parametrize(
    ("command", "path"),
    [
        ("health", "/health/live"),
        ("dois", "/dois"),
        ("replay", "/replay/status"),
        ("atlas-status", "/atlas/status"),
    ],
)
def test_public_commands_use_get_gateway_routes(
    runner: CliRunner, gateway: FakeGateway, command: str, path: str
) -> None:
    result = runner.invoke(app, [command])
    assert result.exit_code == 0
    assert gateway.requests == [("GET", path, None, False)]
    assert '"status": "ok"' in result.stdout


def test_audit_is_protected_and_bounded(runner: CliRunner, gateway: FakeGateway) -> None:
    result = runner.invoke(app, ["audit", "--limit", "12"])
    assert result.exit_code == 0
    assert gateway.requests == [("GET", "/audit?limit=12", None, True)]
    assert runner.invoke(app, ["audit", "--limit", "0"]).exit_code == 2


def test_verdict_accepts_only_canonical_outcomes(runner: CliRunner, gateway: FakeGateway) -> None:
    result = runner.invoke(app, ["verdict", "action-13", "DENY", "--source", "test"])
    assert result.exit_code == 0
    assert gateway.requests == [
        (
            "POST",
            "/chimera/verdict",
            {"action_id": "action-13", "verdict": "DENY", "source": "test"},
            True,
        )
    ]
    assert runner.invoke(app, ["verdict", "action-13", "APPROVE"]).exit_code == 2


def test_canary_reads_secret_from_file_not_arguments(
    tmp_path: Path, runner: CliRunner, gateway: FakeGateway
) -> None:
    raw_canary = "CHIMERA-CANARY-private-stage-13"
    value_file = tmp_path / "canary.txt"
    value_file.write_text(raw_canary + "\n", encoding="utf-8")
    result = runner.invoke(
        app, ["canary", "--value-file", str(value_file), "--context", "cli-test"]
    )
    assert result.exit_code == 0
    assert raw_canary not in result.stdout
    assert gateway.requests[0][1:] == (
        "/chimera/canary",
        {"canary_value": raw_canary, "context": "cli-test"},
        True,
    )


def test_atlas_sludge_reads_snapshot_file_and_uses_protected_gateway(
    tmp_path: Path, runner: CliRunner, gateway: FakeGateway
) -> None:
    snapshot = {"stack": "RS", "claim": "local claim", "probability": 0.61}
    snapshot_file = tmp_path / "snapshot.json"
    snapshot_file.write_text(json.dumps(snapshot), encoding="utf-8")
    result = runner.invoke(
        app,
        [
            "atlas-sludge",
            "--snapshot-file",
            str(snapshot_file),
            "--archetype",
            "hidden_elites",
            "--archetype",
            "false_flags",
        ],
    )
    assert result.exit_code == 0
    assert gateway.requests == [
        (
            "POST",
            "/atlas/sludge",
            {
                "rs_snapshot": snapshot,
                "archetypes": ["hidden_elites", "false_flags"],
            },
            True,
        )
    ]


def test_atlas_sludge_rejects_non_object_snapshot_before_gateway(
    tmp_path: Path, runner: CliRunner, gateway: FakeGateway
) -> None:
    snapshot_file = tmp_path / "snapshot.json"
    snapshot_file.write_text("[]", encoding="utf-8")
    result = runner.invoke(app, ["atlas-sludge", "--snapshot-file", str(snapshot_file)])
    assert result.exit_code == 1
    assert "snapshot file must contain a JSON object" in result.stderr
    assert gateway.requests == []


def test_empty_canary_file_fails_before_gateway(
    tmp_path: Path, runner: CliRunner, gateway: FakeGateway
) -> None:
    value_file = tmp_path / "empty.txt"
    value_file.write_text("\n", encoding="utf-8")
    result = runner.invoke(
        app, ["canary", "--value-file", str(value_file), "--context", "cli-test"]
    )
    assert result.exit_code == 1
    assert "canary file is empty" in result.stderr
    assert gateway.requests == []


def test_gateway_error_is_concise_and_nonzero(runner: CliRunner, gateway: FakeGateway) -> None:
    gateway.error = GatewayError("Invalid bearer token", status_code=401)
    result = runner.invoke(app, ["audit"])
    assert result.exit_code == 1
    assert result.stderr.strip() == "Error: HTTP 401: Invalid bearer token"


def test_http_gateway_requires_token_before_protected_network_request() -> None:
    gateway = HttpGateway("http://127.0.0.1:8000", token=None, timeout=1.0)
    with pytest.raises(GatewayError, match="PROJECT_AI_API_TOKEN"):
        gateway.request("GET", "/audit", protected=True)


@pytest.mark.parametrize(
    "url",
    ["localhost:8000", "file:///tmp/api", "http://user:secret@localhost:8000"],
)
def test_http_gateway_rejects_unsafe_or_ambiguous_urls(url: str) -> None:
    with pytest.raises(ValueError):
        HttpGateway(url, token=None, timeout=1.0)


class FakeResponse:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.body


def _client_module() -> ModuleType:
    return importlib.import_module("project_ai_cli.client")


def test_http_gateway_sends_json_and_bearer_token(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_urlopen(request: Any, *, timeout: float) -> FakeResponse:
        captured.update(request=request, timeout=timeout)
        return FakeResponse(b'{"accepted":true}')

    monkeypatch.setattr(_client_module(), "urlopen", fake_urlopen)
    gateway = HttpGateway("https://api.example.test/", token="private-token", timeout=2.5)
    result = gateway.request(
        "post", "/chimera/verdict", payload={"verdict": "DENY"}, protected=True
    )
    request = captured["request"]
    assert result == {"accepted": True}
    assert captured["timeout"] == 2.5
    assert request.full_url == "https://api.example.test/chimera/verdict"
    assert request.method == "POST"
    assert request.headers["Authorization"] == "Bearer private-token"
    assert request.data == b'{"verdict": "DENY"}'


def test_http_gateway_reports_structured_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args: object, **kwargs: object) -> FakeResponse:
        raise HTTPError(
            "https://api.example.test/audit",
            401,
            "Unauthorized",
            hdrs=Message(),
            fp=io.BytesIO(b'{"detail":"Invalid bearer token"}'),
        )

    monkeypatch.setattr(_client_module(), "urlopen", fail)
    gateway = HttpGateway("https://api.example.test", token="bad", timeout=1.0)
    with pytest.raises(GatewayError, match="HTTP 401: Invalid bearer token"):
        gateway.request("GET", "/audit", protected=True)


def test_http_gateway_reports_unavailable_and_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unavailable(*args: object, **kwargs: object) -> FakeResponse:
        raise URLError("connection refused")

    monkeypatch.setattr(_client_module(), "urlopen", unavailable)
    gateway = HttpGateway("http://127.0.0.1:8000", token=None, timeout=1.0)
    with pytest.raises(GatewayError, match="Gateway unavailable"):
        gateway.request("GET", "/health/live")

    monkeypatch.setattr(
        _client_module(), "urlopen", lambda *args, **kwargs: FakeResponse(b"not-json")
    )
    with pytest.raises(GatewayError, match="invalid JSON"):
        gateway.request("GET", "/health/live")


def test_http_gateway_rejects_bad_paths_timeout_and_non_object_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ValueError, match="timeout"):
        HttpGateway("http://127.0.0.1:8000", token=None, timeout=0)
    gateway = HttpGateway("http://127.0.0.1:8000", token=None, timeout=1.0)
    with pytest.raises(ValueError, match="host-relative"):
        gateway.request("GET", "//attacker.example/path")

    monkeypatch.setattr(_client_module(), "urlopen", lambda *args, **kwargs: FakeResponse(b"[]"))
    with pytest.raises(GatewayError, match="non-object"):
        gateway.request("GET", "/health/live")


def test_cli_has_no_direct_execution_dependency_or_command(runner: CliRunner) -> None:
    package_root = Path(__file__).resolve().parents[1]
    metadata = tomllib.loads((package_root / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = cast(list[str], metadata["project"]["dependencies"])
    # The CLI's *execution* dependencies are still only typer. The
    # additional `thirsty-lang` dep (Phase T4) is a LANGUAGE TOOL
    # exposed via the `lang` sub-app, not a kernel-adjacent
    # execution/governance package. It does NOT give the CLI the
    # ability to actuate; the bridge is a passthrough that forwards
    # argv to the language's argparse-based CLI.
    execution_dependencies = [d for d in dependencies if not d.startswith("thirsty-lang")]
    assert execution_dependencies == ["typer>=0.16.0"]

    forbidden = {"arbiter", "capability", "execution", "governance", "rlp"}
    imported: set[str] = set()
    for source in (package_root / "src" / "project_ai_cli").glob("*.py"):
        tree = ast.parse(source.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".", maxsplit=1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".", maxsplit=1)[0])
    assert imported.isdisjoint(forbidden)

    help_result = runner.invoke(app, ["--help"], env={**os.environ, "NO_COLOR": "1"})
    assert help_result.exit_code == 0
    assert "execute" not in help_result.stdout.lower()
    assert "actuate" not in help_result.stdout.lower()
