from __future__ import annotations

from types import SimpleNamespace

import pytest
from project_ai_waterfall import InProcessWaterfallTransport


class _VPN:
    def __init__(self) -> None:
        self.started = False

    def start(self) -> None:
        self.started = True

    def get_status(self) -> dict[str, object]:
        return {"active": self.started}


class _Firewall:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def add_rule(self, firewall_type: str, rule: dict[str, object]) -> None:
        self.calls.append((firewall_type, rule))


class _KillSwitch:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def trigger(self, reason: str, component: str) -> None:
        self.calls.append((reason, component))

    def is_triggered(self) -> bool:
        return bool(self.calls)


def _runtime() -> SimpleNamespace:
    return SimpleNamespace(vpn=_VPN(), firewall=_Firewall(), kill_switch=_KillSwitch())


def test_vpn_connect_maps_to_copied_runtime() -> None:
    runtime = _runtime()
    result = InProcessWaterfallTransport(runtime).execute("vpn.connect", "vpn:primary", {})
    assert result == {"active": True}
    assert runtime.vpn.started is True


def test_firewall_rule_change_requires_rule_payload() -> None:
    runtime = _runtime()
    with pytest.raises(ValueError, match="rule object"):
        InProcessWaterfallTransport(runtime).execute(
            "firewall.rule_change", "firewall:primary", {"firewall_type": "software"}
        )


def test_kill_switch_trigger_maps_reason_and_component() -> None:
    runtime = _runtime()
    result = InProcessWaterfallTransport(runtime).execute(
        "kill_switch.trigger",
        "kill-switch:local",
        {"reason": "test", "component": "vpn"},
    )
    assert result["triggered"] is True
    assert runtime.kill_switch.calls == [("test", "vpn")]
