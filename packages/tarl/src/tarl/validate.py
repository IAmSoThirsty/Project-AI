"""
tarl.validate — TARL record validation.

Validates a TARL record against the allowed authorities and schema
constraints. Surfaces diagnostic messages (via tarl.diagnostics) when
validation fails.

This is a minimum port of legacy `tarl/validate.py`. The legacy
`ALLOWED_AUTHORITIES` was a small set (Cerberus, CodexDeus); this
version makes the allow-list pluggable so consumers can extend it.

Architectural invariants (AGENTS.md v3):
- Downward-only deps: tarl.validate imports only tarl.core +
  tarl.diagnostics + stdlib.
- Fail-closed: validation failures surface as DiagnosticBatch with
  Severity.ERROR; never silent ALLOW.
- Pluggable seams: Validator Protocol + allowed_authorities() helper.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from tarl.core import TARL
from tarl.diagnostics import (
    DiagnosticBatch,
    Severity,
    make_diagnostic,
)


class Validator(Protocol):
    """Pluggable TARL validator."""

    def validate(self, record: TARL) -> DiagnosticBatch: ...


# Default authority allow-list (subset of legacy; conservative).
DEFAULT_ALLOWED_AUTHORITIES: frozenset[str] = frozenset(
    {
        "Cerberus",
        "CodexDeus",
        "system",
        "human-override",
    }
)


def allowed_authorities(
    record: TARL,
    *,
    extras: Iterable[str] = (),
) -> frozenset[str]:
    """Return the effective authority allow-list for a record.

    Includes DEFAULT_ALLOWED_AUTHORITIES plus any extras provided.
    """
    extras_set = frozenset(extras)
    return DEFAULT_ALLOWED_AUTHORITIES | extras_set


def validate(record: TARL) -> DiagnosticBatch:
    """Validate a TARL record against the default allow-list.

    Returns a DiagnosticBatch (empty batch = record is valid).
    """
    return validate_with_authorities(record, allowed_authorities(record))


def validate_with_authorities(
    record: TARL,
    authorities: Iterable[str],
) -> DiagnosticBatch:
    """Validate a TARL record against an explicit authority allow-list.

    Surfaces ERROR diagnostics for:
    - empty intent / scope / authority
    - authority not in allow-list
    - constraints containing non-string entries
    """
    batch = DiagnosticBatch()
    authority_set = frozenset(authorities)

    if not record.intent or not record.intent.strip():
        batch.add(
            make_diagnostic(
                severity=Severity.ERROR,
                message="intent is empty",
                code="E001",
            )
        )
    if not record.scope or not record.scope.strip():
        batch.add(
            make_diagnostic(
                severity=Severity.ERROR,
                message="scope is empty",
                code="E002",
            )
        )
    if not record.authority or not record.authority.strip():
        batch.add(
            make_diagnostic(
                severity=Severity.ERROR,
                message="authority is empty",
                code="E003",
            )
        )
    elif authority_set and record.authority not in authority_set:
        batch.add(
            make_diagnostic(
                severity=Severity.ERROR,
                message=(
                    f"authority {record.authority!r} is not in allow-list {sorted(authority_set)}"
                ),
                code="E004",
            )
        )
    for i, c in enumerate(record.constraints):
        if not isinstance(c, str):
            batch.add(
                make_diagnostic(
                    severity=Severity.ERROR,
                    message=(f"constraint[{i}] must be str, got {type(c).__name__}"),
                    code="E005",
                )
            )
        elif not c.strip():
            batch.add(
                make_diagnostic(
                    severity=Severity.ERROR,
                    message=f"constraint[{i}] is empty",
                    code="E006",
                )
            )
    return batch


def is_valid(record: TARL) -> bool:
    """Convenience: True if record validates cleanly against default list."""
    return not validate(record).has_errors


__all__ = [
    "DEFAULT_ALLOWED_AUTHORITIES",
    "Validator",
    "allowed_authorities",
    "is_valid",
    "validate",
    "validate_with_authorities",
]
