from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from project_ai_api import create_app
from project_ai_api.waterfall_workflows import build_waterfall_integration
from project_ai_waterfall import InProcessWaterfallTransport
from starlette.testclient import TestClient
from waterfall_adapter import WaterfallAdapter

from capability import CapabilityAuthority
from execution import ExecutionGate
from governance import GovernanceEngine, RuleGovernor
from kernel import EventSpine
from security import AppendOnlyAuditRelay

TOKEN = "waterfall-route-test-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}


class _V3QAllow:
    def decide(
        self,
        _task: dict[str, Any],
        _action: dict[str, Any],
        _authority: dict[str, Any] | None,
        _approval: dict[str, Any] | None,
    ) -> dict[str, str]:
        return {"decision": "allow"}


class _Runtime:
    def __init__(self) -> None:
        self.vpn = SimpleNamespace(start=self._start, get_status=self._status)
        self.firewall = SimpleNamespace(add_rule=self._add_rule)
        self.kill_switch = SimpleNamespace(
            trigger=self._trigger,
            is_triggered=lambda: self.triggered,
        )
        self.started = False
        self.triggered = False
        self.firewall_calls: list[tuple[str, dict[str, object]]] = []

    def _start(self) -> None:
        self.started = True

    def _status(self) -> dict[str, object]:
        return {"active": self.started}

    def _add_rule(self, firewall_type: str, rule: dict[str, object]) -> None:
        self.firewall_calls.append((firewall_type, rule))

    def _trigger(self, _reason: str, _component: str) -> None:
        self.triggered = True

    def get_status(self) -> dict[str, object]:
        return {"active": self.started, "triggered": self.triggered}


def _adapter(runtime: _Runtime) -> WaterfallAdapter:
    authority = CapabilityAuthority(b"w" * 32, issuer="waterfall-route-test")
    gate = ExecutionGate(
        governance=GovernanceEngine(
            policy_version="waterfall-route-test-v1",
            governors=(RuleGovernor("allow", ()),),
        ),
        capabilities=authority,
        events=EventSpine(),
        v3q_gate=_V3QAllow(),  # type: ignore[arg-type]
    )
    return WaterfallAdapter(
        execution_gate=gate,
        capability_authority=authority,
        transport=InProcessWaterfallTransport(runtime),
    )


def _client(tmp_path: Path, runtime: _Runtime) -> TestClient:
    return TestClient(
        create_app(
            api_token=TOKEN,
            audit_path=tmp_path / "audit.jsonl",
            dois=(),
            waterfall_runtime=runtime,
            waterfall_adapter=_adapter(runtime),
        )
    )


def test_waterfall_status_requires_machine_auth_and_reports_shared_gate(
    tmp_path: Path,
) -> None:
    runtime = _Runtime()
    client = _client(tmp_path, runtime)

    assert client.get("/api/v1/modules/waterfall/status").status_code == 401
    response = client.get("/api/v1/modules/waterfall/status", headers=AUTH)

    assert response.status_code == 200
    assert response.json()["configured"] is True
    assert response.json()["authority_contract"] == "project-ai-v3q-execution-gate"
    modules = client.get("/api/v1/modules").json()["modules"]
    waterfall = next(item for item in modules if item["id"] == "waterfall")
    assert waterfall["interface_status"] == "available"


def test_waterfall_operation_routes_gate_evidence_and_audit(tmp_path: Path) -> None:
    runtime = _Runtime()
    client = _client(tmp_path, runtime)

    response = client.post(
        "/api/v1/modules/waterfall/operations",
        headers=AUTH,
        json={
            "operation": "vpn.connect",
            "resource": "vpn:primary",
            "state": {"v3q_authority_proof": {"valid": True}},
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["outcome"] == "ALLOW"
    assert body["governance_evidence_sha256"]
    assert body["event_hash"]
    assert body["audit_hash"]
    assert runtime.started is True

    valid, count = _client_audit(tmp_path)
    assert valid is True
    assert count == 1


def _client_audit(tmp_path: Path) -> tuple[bool, int]:
    from security import AppendOnlyAuditRelay

    return AppendOnlyAuditRelay(tmp_path / "audit.jsonl").verify()


def test_waterfall_route_fails_closed_without_v3q_gate(tmp_path: Path) -> None:
    runtime = _Runtime()
    authority = CapabilityAuthority(b"x" * 32, issuer="no-v3q")
    gate = ExecutionGate(
        governance=GovernanceEngine(
            policy_version="no-v3q-v1",
            governors=(RuleGovernor("allow", ()),),
        ),
        capabilities=authority,
        events=EventSpine(),
    )
    adapter = WaterfallAdapter(
        execution_gate=gate,
        capability_authority=authority,
        transport=InProcessWaterfallTransport(runtime),
    )
    client = TestClient(
        create_app(
            api_token=TOKEN,
            audit_path=tmp_path / "audit.jsonl",
            dois=(),
            waterfall_runtime=runtime,
            waterfall_adapter=adapter,
        )
    )

    assert (
        client.get("/api/v1/modules/waterfall/status", headers=AUTH).json()["configured"] is False
    )
    response = client.post(
        "/api/v1/modules/waterfall/operations",
        headers=AUTH,
        json={"operation": "vpn.connect", "resource": "vpn:primary"},
    )
    assert response.status_code == 503
    assert runtime.started is False


def test_live_factory_stays_dormant_until_explicitly_enabled() -> None:
    runtime, adapter = build_waterfall_integration(
        enabled=False,
        config_path=None,
        execution_secret=None,
        audit_relay=None,
    )
    assert runtime is None
    assert adapter is None


def test_live_factory_requires_v3q_configuration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("THIRSTYS_V3Q_REQUIRED", "true")
    monkeypatch.setattr("project_ai_api.waterfall_workflows.build_gate", lambda **_: None)
    with pytest.raises(ValueError, match="V3Q trusted-key registry"):
        build_waterfall_integration(
            enabled=True,
            config_path=None,
            execution_secret="x" * 32,
            audit_relay=AppendOnlyAuditRelay(tmp_path / "audit.jsonl"),
        )
