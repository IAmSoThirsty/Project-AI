from __future__ import annotations

import ast
import base64
import importlib
import io
import json
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Any, cast
from urllib.error import HTTPError, URLError

import pytest
from project_ai_desktop.capability_inspector import (
    CapabilityInspectionError,
    inspect_capability,
)
from project_ai_desktop.client import DesktopGateway, DesktopGatewayError, JsonObject
from project_ai_desktop.main_window import MainWindow
from project_ai_desktop.replay import run_replay_evidence_check
from PyQt6.QtWidgets import QApplication


def _token(*, expires_at: int = 200, version: object = 1) -> str:
    claims = {
        "expires_at": expires_at,
        "issued_at": 100,
        "issuer": "stage-14.5",
        "operation": "read",
        "resource": "audit",
        "subject": "operator",
        "token_id": "token-1",
        "version": version,
    }
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).rstrip(b"=").decode()
    return f"{payload}.signature"


class FakeGateway:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail

    def health(self) -> JsonObject:
        if self.fail:
            raise DesktopGatewayError("offline")
        return {"status": "live", "version": "0.0.0.dev0"}

    def replay_status(self) -> JsonObject:
        return {
            "status": "pass",
            "invariants_passed": 5,
            "invariants_total": 5,
            "updated_at": "now",
        }

    def audit(self, limit: int = 100) -> JsonObject:
        return {
            "chain_valid": True,
            "count": 1,
            "records": [
                {
                    "event": "chimera.verdict",
                    "action_id": "desktop",
                    "timestamp": "now",
                    "hash": "abc",
                }
            ],
        }


def test_capability_inspector_decodes_without_claiming_signature_verification() -> None:
    result = inspect_capability(_token(), now=datetime.fromtimestamp(150, UTC))
    assert result.subject == "operator"
    assert result.temporal_status == "UNEXPIRED"
    assert result.signature_status == "UNVERIFIED"
    assert (
        inspect_capability(_token(), now=datetime.fromtimestamp(250, UTC)).temporal_status
        == "EXPIRED"
    )


@pytest.mark.parametrize(
    "token", ["", "one-part", "bad.payload", "e30.signature", _token(version=True)]
)
def test_capability_inspector_rejects_invalid_tokens(token: str) -> None:
    with pytest.raises(CapabilityInspectionError):
        inspect_capability(token)


def test_replay_evidence_check_requires_five_coherent_signals() -> None:
    result = run_replay_evidence_check(FakeGateway())
    assert (result.passed, result.total) == (5, 5)
    assert all(check.passed for check in result.checks)


def test_gateway_validates_url_token_and_limits() -> None:
    with pytest.raises(ValueError):
        DesktopGateway("file:///tmp/api")
    with pytest.raises(ValueError):
        DesktopGateway("http://user:secret@localhost")
    with pytest.raises(ValueError):
        DesktopGateway("http://localhost", timeout=0)
    gateway = DesktopGateway("http://localhost")
    with pytest.raises(DesktopGatewayError, match="API token"):
        gateway.audit()
    with pytest.raises(ValueError, match="between 1 and 500"):
        DesktopGateway("http://localhost", token="token").audit(0)


def test_main_window_exposes_six_read_only_operator_pages(qt_app: QApplication) -> None:
    factory = lambda url, token, timeout: FakeGateway()  # noqa: E731
    window = MainWindow(factory)
    assert window.windowTitle().endswith("0.0.0.dev0")
    assert window.pages.count() == 6
    nav_labels = [item.text() for i in range(6) if (item := window.navigation.item(i)) is not None]
    assert nav_labels == list(MainWindow.PAGE_NAMES)

    window.refresh_status()
    assert "Gateway live" in window.status_summary.text()
    window.run_replay()
    assert window.replay_table.rowCount() == 5
    replay_cell = window.replay_table.item(0, 1)
    assert replay_cell is not None
    assert replay_cell.text() == "PASS"

    window.api_token_input.setText("operator-token")
    window.apply_settings()
    assert window.api_token_input.text() == ""
    window.load_audit()
    assert window.audit_table.rowCount() == 1

    window.capability_input.setPlainText(_token())
    window.inspect_token()
    assert window.capability_input.toPlainText() == ""
    assert '"signature_status": "UNVERIFIED"' in window.capability_output.toPlainText()
    window.close()


def test_main_window_fails_closed_on_gateway_and_invalid_capability(qt_app: QApplication) -> None:
    factory = lambda url, token, timeout: FakeGateway(fail=True)  # noqa: E731
    window = MainWindow(factory)
    window.refresh_status()
    assert window.status_summary.text() == "Unavailable"
    window.run_replay()
    assert window.replay_table.rowCount() == 0
    window.capability_input.setPlainText("invalid")
    window.inspect_token()
    assert window.capability_output.toPlainText().startswith("INVALID")
    window.close()


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
    return importlib.import_module("project_ai_desktop.client")


def test_gateway_sends_bearer_token_and_parses_audit(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_urlopen(request: Any, *, timeout: float) -> FakeResponse:
        captured.update(request=request, timeout=timeout)
        return FakeResponse(b'{"chain_valid":true,"count":0,"records":[]}')

    monkeypatch.setattr(_client_module(), "urlopen", fake_urlopen)
    gateway = DesktopGateway("https://api.example.test/", token="private", timeout=2.0)
    assert gateway.audit(12)["chain_valid"] is True
    request = captured["request"]
    assert request.full_url == "https://api.example.test/audit?limit=12"
    assert request.headers["Authorization"] == "Bearer private"
    assert captured["timeout"] == 2.0


def test_gateway_classifies_http_transport_and_json_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def http_error(*args: object, **kwargs: object) -> FakeResponse:
        raise HTTPError(
            "https://api.example.test/audit",
            401,
            "Unauthorized",
            hdrs=None,  # type: ignore[arg-type]
            fp=io.BytesIO(b'{"detail":"Invalid bearer token"}'),
        )

    monkeypatch.setattr(_client_module(), "urlopen", http_error)
    gateway = DesktopGateway("https://api.example.test", token="bad")
    with pytest.raises(DesktopGatewayError, match="HTTP 401: Invalid bearer token"):
        gateway.audit()

    def unavailable(*args: object, **kwargs: object) -> FakeResponse:
        raise URLError("connection refused")

    monkeypatch.setattr(_client_module(), "urlopen", unavailable)
    with pytest.raises(DesktopGatewayError, match="Gateway unavailable"):
        gateway.health()

    monkeypatch.setattr(
        _client_module(), "urlopen", lambda *args, **kwargs: FakeResponse(b"not-json")
    )
    with pytest.raises(DesktopGatewayError, match="invalid JSON"):
        gateway.health()


def test_desktop_has_no_authority_dependency_and_avoids_qsettings() -> None:
    """Governance-authority import boundary and QSettings avoidance.

    Renamed from ``..._or_persistent_token_store``: the desktop now
    deliberately persists one credential (see
    ``test_local_loopback_token_is_the_only_persisted_secret`` below), so
    that older name no longer described what this test actually checks. The
    assertions themselves are unchanged -- they never asserted "no
    persistence anywhere", only these three things.
    """
    app_root = Path(__file__).resolve().parents[1]
    metadata = tomllib.loads((app_root / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = cast(list[str], metadata["project"]["dependencies"])
    assert dependencies == ["PyQt6>=6.8.0"]

    forbidden = {"arbiter", "capability", "execution", "governance", "rlp"}
    imported: set[str] = set()
    source_text = ""
    for source in (app_root / "src" / "project_ai_desktop").glob("*.py"):
        text = source.read_text(encoding="utf-8")
        source_text += text
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".", maxsplit=1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".", maxsplit=1)[0])
    assert imported.isdisjoint(forbidden)
    assert "QSettings" not in source_text


def test_local_loopback_token_is_the_only_persisted_secret() -> None:
    """The desktop persists exactly one credential: a self-generated,
    loopback-only token for the api process it may spawn (``credentials.py``,
    used only by ``api_supervisor.py``). The Settings page's user-entered
    remote gateway token must stay in-memory only -- ``main_window.py`` must
    not import the persistence module or write that token anywhere.
    """
    app_root = Path(__file__).resolve().parents[1]
    main_window_source = (app_root / "src" / "project_ai_desktop" / "main_window.py").read_text(
        encoding="utf-8"
    )
    assert "credentials" not in main_window_source
    assert "In-memory settings applied; token was not persisted" in main_window_source
