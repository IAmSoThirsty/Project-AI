"""PSIA readiness gate — check registration, evaluation, status transitions."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


class NodeStatus(str, Enum):
    INITIALIZING = "initializing"
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    critical: bool = True
    duration_ms: float = 0.0


@dataclass
class ReadinessReport:
    status: NodeStatus
    checks: list[CheckResult]
    all_passed: bool
    critical_failures: int
    warnings: int


class ReadinessGate:
    def __init__(self, node_id: str = "", strict: bool = False) -> None:
        self._node_id = node_id
        self._strict = strict
        self._checks: list[tuple[str, Callable, bool]] = []
        self._last_report: ReadinessReport | None = None
        self._status = NodeStatus.INITIALIZING

    @property
    def node_id(self) -> str:
        return self._node_id

    @property
    def strict(self) -> bool:
        return self._strict

    @property
    def status(self) -> NodeStatus:
        if self._last_report is not None:
            return self._last_report.status
        return self._status

    @property
    def last_report(self) -> ReadinessReport | None:
        return self._last_report

    @property
    def is_operational(self) -> bool:
        if self._last_report is None:
            return False
        return self._last_report.status == NodeStatus.OPERATIONAL

    def register_check(
        self,
        name: str,
        fn: Callable[[], tuple[bool, str]],
        critical: bool = True,
    ) -> None:
        self._checks.append((name, fn, critical))

    def register_genesis_check(self, genesis: Any) -> None:
        def check() -> tuple[bool, str]:
            if genesis.is_completed:
                return (True, "Genesis completed")
            return (False, f"Genesis not completed: {getattr(genesis, 'status', 'unknown')}")
        self.register_check("genesis", check, critical=True)

    def register_ledger_check(self, ledger: Any) -> None:
        def check() -> tuple[bool, str]:
            if ledger.verify_chain():
                count = getattr(ledger, "sealed_block_count", 0)
                return (True, f"Chain verified, {count} blocks")
            return (False, "Chain verification failed")
        self.register_check("ledger", check, critical=True)

    def register_capability_check(self, authority: Any) -> None:
        def check() -> tuple[bool, str]:
            count = getattr(authority, "active_count", 0)
            return (True, f"Capability authority active, {count} tokens")
        self.register_check("capability_authority", check, critical=False)

    def evaluate(self) -> ReadinessReport:
        import time
        results: list[CheckResult] = []
        critical_failures = 0
        warnings = 0

        for name, fn, critical in self._checks:
            t0 = time.monotonic()
            try:
                passed, message = fn()
            except Exception as exc:
                passed = False
                message = f"exception: {exc}"
                critical = True
            duration_ms = (time.monotonic() - t0) * 1000

            results.append(CheckResult(
                name=name,
                passed=passed,
                message=message,
                critical=critical,
                duration_ms=duration_ms,
            ))
            if not passed:
                if critical:
                    critical_failures += 1
                else:
                    warnings += 1

        all_passed = critical_failures == 0 and warnings == 0

        if critical_failures > 0:
            status = NodeStatus.FAILED
        elif warnings > 0:
            status = NodeStatus.DEGRADED
        else:
            status = NodeStatus.OPERATIONAL

        self._last_report = ReadinessReport(
            status=status,
            checks=results,
            all_passed=all_passed,
            critical_failures=critical_failures,
            warnings=warnings,
        )
        return self._last_report
