from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class InvariantScope(str, Enum):
    IMMUTABLE = "immutable"
    OPERATIONAL = "operational"
    CONSTITUTIONAL = "constitutional"


class InvariantSeverity(str, Enum):
    FATAL = "fatal"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class InvariantEnforcement(str, Enum):
    HARD_DENY = "hard_deny"
    QUARANTINE = "quarantine"
    RATE_LIMIT = "rate_limit"
    WARN = "warn"


class InvariantExpression(BaseModel):
    language: str = "first_order_logic"
    expr: str

    @field_validator("expr")
    @classmethod
    def expr_nonempty(cls, v: str) -> str:
        if not v:
            raise ValueError("expr must be non-empty")
        return v


class InvariantTestCase(BaseModel):
    name: str
    given: dict[str, Any]
    expect: str  # "allow" or "deny"


from psia.schemas.identity import Signature  # noqa: E402


class InvariantDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    invariant_id: str
    version: int
    scope: InvariantScope
    severity: InvariantSeverity
    enforcement: InvariantEnforcement
    expression: InvariantExpression
    tests: list[InvariantTestCase]
    signature: Signature

    @field_validator("version")
    @classmethod
    def version_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("version must be >= 1")
        return v

    @field_validator("tests")
    @classmethod
    def tests_nonempty(cls, v: list) -> list:
        if len(v) < 1:
            raise ValueError("tests must have at least one entry")
        return v
