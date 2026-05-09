"""invariant_severity.py — Upgrade 7: Invariant Severity Levels.

Extends InvariantEngine beyond binary pass/fail.

InvariantSeverity: INFO, WARN, BLOCK, HALT, ESCALATE
InvariantResult: severity, code, message, evidence, control_mapping

Semantics:
  BLOCK    → prevents execution
  HALT     → prevents session/action initialization
  ESCALATE → routes to governance council/audit
  WARN     → allows only if no higher severity exists
  INFO     → audit-only

EvidenceBundle integration: InvariantResult list is included.
"""
from __future__ import annotations

import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class InvariantSeverity(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    BLOCK = "BLOCK"
    HALT = "HALT"
    ESCALATE = "ESCALATE"

    def prevents_execution(self) -> bool:
        return self in (InvariantSeverity.BLOCK, InvariantSeverity.HALT, InvariantSeverity.ESCALATE)

    def ordinal(self) -> int:
        return {"INFO": 0, "WARN": 1, "BLOCK": 2, "HALT": 3, "ESCALATE": 4}[self.value]

    def __lt__(self, other: "InvariantSeverity") -> bool:
        return self.ordinal() < other.ordinal()

    def __le__(self, other: "InvariantSeverity") -> bool:
        return self.ordinal() <= other.ordinal()

    def __gt__(self, other: "InvariantSeverity") -> bool:
        return self.ordinal() > other.ordinal()

    def __ge__(self, other: "InvariantSeverity") -> bool:
        return self.ordinal() >= other.ordinal()


@dataclass
class InvariantResult:
    """Result of a single invariant check."""

    invariant_name: str
    severity: InvariantSeverity
    code: str
    message: str
    passed: bool
    evidence: dict[str, Any] = field(default_factory=dict)
    control_mapping: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "invariant_name": self.invariant_name,
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "passed": self.passed,
            "evidence": self.evidence,
            "control_mapping": self.control_mapping,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)


@dataclass
class SeverityAwareInvariant:
    """An invariant that returns an InvariantResult instead of a bool."""

    name: str
    description: str
    severity_on_failure: InvariantSeverity
    code: str
    fn: Callable[[dict[str, Any]], bool]
    control_mapping: list[str] = field(default_factory=list)

    def evaluate(self, context: dict[str, Any]) -> InvariantResult:
        try:
            passed = self.fn(context)
        except Exception as exc:
            logger.warning("Invariant %s raised: %s", self.name, exc)
            passed = False

        if passed:
            return InvariantResult(
                invariant_name=self.name,
                severity=InvariantSeverity.INFO,
                code=self.code + "_PASS",
                message=f"{self.name}: passed",
                passed=True,
                control_mapping=self.control_mapping,
            )
        return InvariantResult(
            invariant_name=self.name,
            severity=self.severity_on_failure,
            code=self.code + "_FAIL",
            message=f"{self.name}: FAILED",
            passed=False,
            control_mapping=self.control_mapping,
        )


class SeverityAwareInvariantEngine:
    """Upgraded InvariantEngine that returns rich InvariantResult objects.

    Wraps the existing InvariantEngine for backwards compatibility.
    """

    def __init__(self) -> None:
        self._invariants: list[SeverityAwareInvariant] = []

    def register(self, invariant: SeverityAwareInvariant) -> None:
        self._invariants.append(invariant)

    def register_fn(
        self,
        name: str,
        fn: Callable[[dict[str, Any]], bool],
        severity_on_failure: InvariantSeverity = InvariantSeverity.BLOCK,
        code: str = "",
        control_mapping: list[str] | None = None,
    ) -> None:
        self._invariants.append(SeverityAwareInvariant(
            name=name,
            description=name,
            severity_on_failure=severity_on_failure,
            code=code or name.upper().replace(" ", "_"),
            fn=fn,
            control_mapping=control_mapping or [],
        ))

    def evaluate_all(self, context: dict[str, Any]) -> list[InvariantResult]:
        return [inv.evaluate(context) for inv in self._invariants]

    def max_severity(self, results: list[InvariantResult]) -> InvariantSeverity:
        failing = [r for r in results if not r.passed]
        if not failing:
            return InvariantSeverity.INFO
        return max((f.severity for f in failing), key=lambda s: s.ordinal())

    def should_block_execution(self, results: list[InvariantResult]) -> bool:
        return self.max_severity(results).prevents_execution()

    def summary(self, results: list[InvariantResult]) -> dict[str, Any]:
        failing = [r for r in results if not r.passed]
        return {
            "total": len(results),
            "passed": len(results) - len(failing),
            "failed": len(failing),
            "max_severity": self.max_severity(results).value,
            "blocks_execution": self.should_block_execution(results),
            "failures": [r.to_dict() for r in failing],
        }


# Built-in severity-tagged invariants
def _register_default_invariants(engine: SeverityAwareInvariantEngine) -> None:
    """Register well-known severity-aware invariants."""

    engine.register_fn(
        "optional_metadata_present",
        fn=lambda ctx: bool(ctx.get("request_id") or ctx.get("session_id")),
        severity_on_failure=InvariantSeverity.WARN,
        code="OPT_META",
        control_mapping=["StateRegister", "AuditChain"],
    )

    engine.register_fn(
        "continuity_proof_fresh",
        fn=lambda ctx: ctx.get("continuity_verified", False),
        severity_on_failure=InvariantSeverity.BLOCK,
        code="STALE_CONTINUITY",
        control_mapping=["StateRegister", "TemporalAnchor"],
    )

    engine.register_fn(
        "no_forged_continuity_proof",
        fn=lambda ctx: not ctx.get("continuity_proof_forged", False),
        severity_on_failure=InvariantSeverity.HALT,
        code="FORGED_CONTINUITY",
        control_mapping=["StateRegister", "InvariantEngine", "AuditChain"],
    )

    engine.register_fn(
        "signing_key_match",
        fn=lambda ctx: not ctx.get("signing_key_mismatch", False),
        severity_on_failure=InvariantSeverity.ESCALATE,
        code="KEY_MISMATCH",
        control_mapping=["SovereignRuntime", "CapabilityTokenVerifier"],
    )

    engine.register_fn(
        "invariant_registry_integrity",
        fn=lambda ctx: not ctx.get("invariant_registry_tampered", False),
        severity_on_failure=InvariantSeverity.ESCALATE,
        code="REGISTRY_TAMPER",
        control_mapping=["InvariantEngine", "PolicyRegistry", "AuditChain"],
    )


_severity_engine: SeverityAwareInvariantEngine | None = None


def get_severity_engine() -> SeverityAwareInvariantEngine:
    global _severity_engine
    if _severity_engine is None:
        _severity_engine = SeverityAwareInvariantEngine()
        _register_default_invariants(_severity_engine)
    return _severity_engine


__all__ = [
    "InvariantSeverity",
    "InvariantResult",
    "SeverityAwareInvariant",
    "SeverityAwareInvariantEngine",
    "get_severity_engine",
]
