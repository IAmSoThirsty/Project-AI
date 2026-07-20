"""Explicit transport from Project-AI's gate to a copied Waterfall runtime."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, cast

from kernel import JsonValue


class _VpnRuntime(Protocol):
    def start(self) -> None: ...

    def get_status(self) -> JsonValue: ...


class _FirewallRuntime(Protocol):
    def add_rule(self, firewall_type: str, rule: dict[str, JsonValue]) -> None: ...


class _KillSwitchRuntime(Protocol):
    def trigger(self, reason: str, component: str) -> None: ...

    def is_triggered(self) -> bool: ...


class WaterfallRuntime(Protocol):
    """Typed subset consumed from either the copied or standalone runtime."""

    vpn: _VpnRuntime
    firewall: _FirewallRuntime
    kill_switch: _KillSwitchRuntime

    def get_status(self) -> JsonValue: ...


class InProcessWaterfallTransport:
    """Map the adapter allow-list to the copied Waterfall runtime.

    This transport is intentionally not a gate. It is called only by
    ``WaterfallAdapter`` after ``ExecutionGate`` has authorized the request.
    """

    def __init__(self, runtime: WaterfallRuntime) -> None:
        self._runtime = runtime

    def execute(
        self,
        operation: str,
        resource: str,
        payload: Mapping[str, JsonValue],
    ) -> JsonValue:
        if operation == "vpn.connect":
            self._runtime.vpn.start()
            return self._runtime.vpn.get_status()

        if operation == "firewall.rule_change":
            firewall_type = self._string(payload, "firewall_type")
            rule = payload.get("rule")
            if not isinstance(rule, dict):
                raise ValueError("firewall.rule_change requires a rule object")
            self._runtime.firewall.add_rule(
                firewall_type,
                cast("dict[str, JsonValue]", dict(rule)),
            )
            return {"resource": resource, "firewall": firewall_type, "updated": True}

        if operation == "kill_switch.trigger":
            reason = self._string(payload, "reason")
            component = self._string(payload, "component")
            self._runtime.kill_switch.trigger(reason, component)
            return {
                "resource": resource,
                "triggered": self._runtime.kill_switch.is_triggered(),
            }

        raise ValueError(f"unsupported Waterfall operation: {operation}")

    @staticmethod
    def _string(payload: Mapping[str, JsonValue], name: str) -> str:
        value: Any = payload.get(name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Waterfall operation requires non-empty {name}")
        return value
