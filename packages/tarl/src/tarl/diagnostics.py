"""
tarl.diagnostics — TARL diagnostic / error reporting primitives.

Diagnostics are structured messages with severity (ERROR / WARNING / INFO
/ HINT) and optional source location. The DiagnosticBatch aggregates
multiple diagnostics for batch reporting.

This is the minimum surface from legacy `tarl/diagnostics/__init__.py`:
- Severity (4-value enum)
- Diagnostic dataclass (severity, message, optional location)
- DiagnosticBatch aggregator

Architectural invariants (AGENTS.md v3):
- Downward-only deps: tarl.diagnostics imports only stdlib.
- Fail-closed: errors with severity=ERROR are flagged via has_errors.
- Deterministic: batch ordering preserved.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Severity(StrEnum):
    """Diagnostic severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


@dataclass(frozen=True)
class Location:
    """Optional source location for a diagnostic."""

    file: str
    line: int
    column: int | None = None


@dataclass(frozen=True)
class Diagnostic:
    """A single diagnostic message.

    Attributes:
        severity: ERROR / WARNING / INFO / HINT.
        message: Human-readable message.
        code: Optional machine-readable code (e.g. "E001").
        location: Optional source location.
    """

    severity: Severity
    message: str
    code: str | None = None
    location: Location | None = None


@dataclass
class DiagnosticBatch:
    """Aggregator for multiple diagnostics."""

    diagnostics: list[Diagnostic] = field(default_factory=list)

    def add(self, diagnostic: Diagnostic) -> None:
        if not isinstance(diagnostic, Diagnostic):
            raise TypeError(f"expected Diagnostic, got {type(diagnostic).__name__}")
        self.diagnostics.append(diagnostic)

    def extend(self, diagnostics: Iterable[Diagnostic]) -> None:
        for d in diagnostics:
            self.add(d)

    @property
    def has_errors(self) -> bool:
        return any(d.severity is Severity.ERROR for d in self.diagnostics)

    @property
    def errors(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.severity is Severity.ERROR]

    @property
    def warnings(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.severity is Severity.WARNING]

    def to_json(self) -> list[dict[str, Any]]:
        """Serialize to JSON-compatible list of dicts."""
        result: list[dict[str, Any]] = []
        for d in self.diagnostics:
            entry: dict[str, Any] = {
                "severity": d.severity.value,
                "message": d.message,
            }
            if d.code is not None:
                entry["code"] = d.code
            if d.location is not None:
                entry["location"] = {
                    "file": d.location.file,
                    "line": d.location.line,
                }
                if d.location.column is not None:
                    entry["location"]["column"] = d.location.column
            result.append(entry)
        return result


def make_diagnostic(
    *,
    severity: Severity | str,
    message: str,
    code: str | None = None,
    location: Location | None = None,
) -> Diagnostic:
    """Construct a Diagnostic with validation."""
    if isinstance(severity, Severity):
        sev = severity
    elif isinstance(severity, str):
        try:
            sev = Severity(severity)
        except ValueError as error:
            raise ValueError(
                f"severity must be one of {[s.value for s in Severity]}, got {severity!r}"
            ) from error
    else:
        raise TypeError(f"severity must be Severity or str, got {type(severity).__name__}")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("message must be a non-empty string")
    return Diagnostic(severity=sev, message=message, code=code, location=location)


__all__ = [
    "Diagnostic",
    "DiagnosticBatch",
    "Location",
    "Severity",
    "make_diagnostic",
]
