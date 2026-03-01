"""
PSIA Invariant Definition Schema — hard constraints on canonical state.

Implements §3.5 of the PSIA v1.0 specification.

An InvariantDefinition is a formally specified constraint that must hold
for any canonical state transition.  Invariants are:
- Scoped (immutable, constitutional, operational)
- Severity-classified (fatal through low)
- Enforceable (hard_deny, quarantine, rate_limit, require_shadow, require_quorum)
- Tested (embedded unit test cases)
- Signed by governance keys
"""

from __future__ import annotations

import enum
from typing import Any

from pydantic import BaseModel, Field

from psia.schemas.identity import Signature


class InvariantScope(str, enum.Enum):
    """Scope classification for invariants."""

    IMMUTABLE = "immutable"
    CONSTITUTIONAL = "constitutional"
    OPERATIONAL = "operational"


class InvariantSeverity(str, enum.Enum):
    """Severity level of invariant violations."""

    FATAL = "fatal"
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class InvariantEnforcement(str, enum.Enum):
    """Enforcement action when an invariant is violated."""

    HARD_DENY = "hard_deny"
    QUARANTINE = "quarantine"
    RATE_LIMIT = "rate_limit"
    REQUIRE_SHADOW = "require_shadow"
    REQUIRE_QUORUM = "require_quorum"


class InvariantExpression(BaseModel):
    """Formal expression defining the invariant predicate."""

    language: str = Field(
        "first_order_logic",
        description="Expression language: first_order_logic or dsl",
    )
    expr: str = Field(..., description="The invariant expression string")

    model_config = {"frozen": True}


class InvariantTestCase(BaseModel):
    """Embedded unit test case for an invariant."""

    name: str = Field(..., description="Test case name")
    given: dict[str, Any] = Field(..., description="Input state (S) and delta (Δ)")
    expect: str = Field(..., description="Expected decision: allow or deny")

    model_config = {"frozen": True}


class InvariantDefinition(BaseModel):
    """
    PSIA Invariant Definition — a hard constraint on canonical state.

    Invariants are the formal guarantees of the PSIA system.
    Root invariants (INV-ROOT-*) are immutable and fatal; they can
    never be relaxed or removed.

    Invariants:
        - ``invariant_id`` is globally unique (inv_...)
        - ``version`` is monotonically increasing
        - ``tests`` must contain at least one test case
        - ``signature`` is computed by a governance key
    """

    invariant_id: str = Field(..., description="Unique invariant ID (inv_...)")
    version: int = Field(1, ge=1, description="Monotonically increasing version")
    scope: InvariantScope = Field(..., description="Scope classification")
    severity: InvariantSeverity = Field(..., description="Violation severity")
    enforcement: InvariantEnforcement = Field(..., description="Enforcement action")
    expression: InvariantExpression = Field(
        ..., description="Formal invariant expression"
    )
    tests: list[InvariantTestCase] = Field(
        ..., min_length=1, description="Embedded test cases"
    )
    signature: Signature = Field(..., description="Governance signer signature")

    model_config = {"frozen": True}


__all__ = [
    "InvariantScope",
    "InvariantSeverity",
    "InvariantEnforcement",
    "InvariantExpression",
    "InvariantTestCase",
    "InvariantDefinition",
]
