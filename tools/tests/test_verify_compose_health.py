from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).parents[1] / "verify_compose_health.py"
SPEC = importlib.util.spec_from_file_location("verify_compose_health", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _records() -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "Service": service,
            "ID": f"container-{service}",
            "State": "running",
            "Health": "healthy",
        }
        for service in sorted(MODULE.EXPECTED_SERVICES)
    )


def _install_runtime_stubs(
    monkeypatch: pytest.MonkeyPatch,
    *,
    api_version: str = "0.0.2",
    genesis_version: str = "0.0.2",
) -> None:
    monkeypatch.setattr(MODULE, "_compose_records", _records)
    monkeypatch.setattr(MODULE, "_container_security", lambda _container_id: (True, "secure"))

    def http_text(url: str) -> str:
        if url.endswith("/health/live"):
            return json.dumps({"status": "live", "version": api_version})
        return "live"

    monkeypatch.setattr(MODULE, "_http_text", http_text)
    monkeypatch.setattr(
        MODULE,
        "_run",
        lambda _arguments: json.dumps(
            {
                "status": "live",
                "service": "genesis",
                "version": genesis_version,
                "authority": "evidence-only",
            }
        ),
    )


def test_api_version_requires_live_versioned_json() -> None:
    assert MODULE._api_version('{"status":"live","version":"0.0.2"}') == ("0.0.2", None)
    assert MODULE._api_version("not-json")[0] is None
    assert MODULE._api_version('{"status":"starting","version":"0.0.2"}')[0] is None
    assert MODULE._api_version('{"status":"live","version":""}')[0] is None


def test_main_accepts_consistent_container_versions(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_runtime_stubs(monkeypatch)

    assert MODULE.main() == 0


def test_main_rejects_container_version_drift(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_runtime_stubs(monkeypatch, genesis_version="0.0.1")

    assert MODULE.main() == 1
