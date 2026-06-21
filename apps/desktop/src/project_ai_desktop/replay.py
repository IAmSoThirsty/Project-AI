"""Deterministic desktop checks around canonical replay evidence."""

from __future__ import annotations

from dataclasses import dataclass

from project_ai_desktop.client import Gateway


@dataclass(frozen=True)
class ReplayCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class DesktopReplayResult:
    checks: tuple[ReplayCheck, ...]

    @property
    def passed(self) -> int:
        return sum(check.passed for check in self.checks)

    @property
    def total(self) -> int:
        return len(self.checks)


def run_replay_evidence_check(gateway: Gateway) -> DesktopReplayResult:
    health = gateway.health()
    replay = gateway.replay_status()
    status = replay.get("status")
    passed = replay.get("invariants_passed")
    total = replay.get("invariants_total")
    coherent = (
        isinstance(passed, int)
        and isinstance(total, int)
        and (
            (status == "pass" and passed == total == 5)
            or (status == "not_run" and passed == 0 and total == 5)
            or (status == "fail" and 0 <= passed < total == 5)
        )
    )
    checks = (
        ReplayCheck("gateway_live", health.get("status") == "live", str(health.get("status"))),
        ReplayCheck(
            "development_version",
            health.get("version") == "0.0.0.dev0",
            str(health.get("version")),
        ),
        ReplayCheck("canonical_total", total == 5, f"total={total}"),
        ReplayCheck(
            "passed_range",
            isinstance(passed, int) and isinstance(total, int) and 0 <= passed <= total,
            f"passed={passed}",
        ),
        ReplayCheck("status_coherent", coherent, f"status={status}"),
    )
    return DesktopReplayResult(checks)
