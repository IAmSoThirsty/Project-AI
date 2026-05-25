"""Shadow Thirst static analysis — plane isolation, determinism, resource estimation."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from shadow_thirst.ir_generator import IR, IRBasicBlock
from shadow_thirst.parser import DrinkStmt, CallExpr


class AnalysisSeverity(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


@dataclass
class Finding:
    severity: AnalysisSeverity
    message: str
    analyzer: str = ""

    def __str__(self) -> str:
        return self.message


@dataclass
class AnalysisReport:
    findings: list[Finding] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(f.severity == AnalysisSeverity.ERROR for f in self.findings)

    def get_errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == AnalysisSeverity.ERROR]

    def get_warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == AnalysisSeverity.WARNING]


# ── Analyzers ────────────────────────────────────────────────────────────────

_NON_DETERMINISTIC_CALLS = {"now", "random", "input", "stdin", "time", "clock"}


def _analyze_plane_isolation(ir: IR) -> list[Finding]:
    findings: list[Finding] = []
    for func in ir.functions:
        for bb in func.shadow_blocks:
            for stmt in bb.statements:
                if isinstance(stmt, DrinkStmt):
                    ann = stmt.type_annotation
                    if ann is not None and ann.is_canonical():
                        findings.append(Finding(
                            severity=AnalysisSeverity.ERROR,
                            message=(
                                f"Shadow block in '{func.name}' declares canonical-typed variable "
                                f"'{stmt.name}' — violates INV-ROOT-2 (shadow cannot produce canonical writes)"
                            ),
                            analyzer="PlaneIsolationAnalyzer",
                        ))
    return findings


def _analyze_determinism(ir: IR) -> list[Finding]:
    findings: list[Finding] = []

    def _check_expr(expr: Any) -> list[str]:
        violations: list[str] = []
        if isinstance(expr, CallExpr):
            if expr.func.lower() in _NON_DETERMINISTIC_CALLS:
                violations.append(expr.func)
            for arg in expr.args:
                violations.extend(_check_expr(arg))
        return violations

    def _check_block(bb: IRBasicBlock) -> list[str]:
        violations: list[str] = []
        for stmt in bb.statements:
            if isinstance(stmt, DrinkStmt):
                violations.extend(_check_expr(stmt.value))
            elif hasattr(stmt, "value"):
                violations.extend(_check_expr(stmt.value))
            elif hasattr(stmt, "expr"):
                violations.extend(_check_expr(stmt.expr))
        return violations

    for func in ir.functions:
        for bb in func.shadow_blocks:
            for call_name in _check_block(bb):
                findings.append(Finding(
                    severity=AnalysisSeverity.ERROR,
                    message=(
                        f"Shadow block in '{func.name}' calls non-deterministic operation '{call_name}' "
                        f"— shadow execution must be deterministic"
                    ),
                    analyzer="DeterminismAnalyzer",
                ))
    return findings


def _analyze_resources(ir: IR) -> list[Finding]:
    findings: list[Finding] = []
    for func in ir.functions:
        total_stmts = sum(
            len(bb.statements)
            for bb in func.primary_blocks + func.shadow_blocks
        )
        findings.append(Finding(
            severity=AnalysisSeverity.INFO,
            message=f"Function '{func.name}' has {total_stmts} executable statements",
            analyzer="ResourceEstimator",
        ))
    return findings


def analyze(ir: IR) -> AnalysisReport:
    findings: list[Finding] = []
    findings.extend(_analyze_plane_isolation(ir))
    findings.extend(_analyze_determinism(ir))
    findings.extend(_analyze_resources(ir))
    return AnalysisReport(findings=findings)
