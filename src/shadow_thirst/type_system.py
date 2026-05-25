"""Shadow Thirst type system — plane-annotated types and safety checker.

Implements the type lattice from §8.4:
  Dual ≤ Primary, Dual ≤ Shadow, Invariant ≤ Shadow (and reflexive)
  Primary ≰ Shadow, Shadow ≰ Primary
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class PlaneAnnotation(Enum):
    PRIMARY = "Primary"
    SHADOW = "Shadow"
    INVARIANT = "Invariant"
    DUAL = "Dual"


class BaseType(Enum):
    INT = "Int"
    FLOAT = "Float"
    BOOL = "Bool"
    STRING = "String"
    ANY = "Any"


# Subtyping lattice: key ≤ all values in the set
_SUBTYPE_OF: dict[PlaneAnnotation, set[PlaneAnnotation]] = {
    PlaneAnnotation.DUAL: {
        PlaneAnnotation.PRIMARY,
        PlaneAnnotation.SHADOW,
        PlaneAnnotation.DUAL,
    },
    PlaneAnnotation.INVARIANT: {
        PlaneAnnotation.SHADOW,
        PlaneAnnotation.INVARIANT,
    },
    PlaneAnnotation.PRIMARY: {PlaneAnnotation.PRIMARY},
    PlaneAnnotation.SHADOW: {PlaneAnnotation.SHADOW},
}


@dataclass(frozen=True)
class AnnotatedType:
    base: BaseType
    plane: PlaneAnnotation

    def is_subtype_of(self, other: AnnotatedType) -> bool:
        if self.base != other.base:
            return False
        return other.plane in _SUBTYPE_OF.get(self.plane, {self.plane})

    def is_writable_to_canonical(self) -> bool:
        return self.plane == PlaneAnnotation.PRIMARY


@dataclass
class TypeViolation:
    rule_violated: str
    message: str
    line: int = 0

    def __str__(self) -> str:
        return f"[{self.rule_violated}] {self.message}"


class PlaneSafetyChecker:
    def __init__(self) -> None:
        self.violations: list[TypeViolation] = []
        self._context: PlaneAnnotation = PlaneAnnotation.PRIMARY

    def enter_context(self, plane: PlaneAnnotation) -> None:
        self._context = plane

    def check_write(
        self,
        target: str,
        target_plane: PlaneAnnotation,
        value_type: AnnotatedType,
        line: int = 0,
    ) -> bool:
        """Return True if the write is safe; False and record a violation otherwise."""
        if self._context == PlaneAnnotation.SHADOW and target_plane == PlaneAnnotation.PRIMARY:
            self.violations.append(TypeViolation(
                rule_violated="T-WRITE-CANONICAL",
                message=(
                    f"T-WRITE-CANONICAL violated: shadow context cannot write to "
                    f"canonical (Primary-plane) target '{target}' — INV-ROOT-2"
                ),
                line=line,
            ))
            return False
        return True

    def check_promote(
        self,
        value_type: AnnotatedType,
        commit_protocol_completed: bool,
        line: int = 0,
    ) -> bool:
        """Return True if promotion is allowed; False otherwise."""
        if not commit_protocol_completed:
            self.violations.append(TypeViolation(
                rule_violated="T-PROMOTE",
                message=(
                    "T-PROMOTE violated: shadow value cannot be promoted to canonical "
                    "without completing the commit protocol"
                ),
                line=line,
            ))
            return False
        return True

    def report(self) -> dict[str, Any]:
        return {
            "sound": len(self.violations) == 0,
            "violation_count": len(self.violations),
            "violations": [str(v) for v in self.violations],
        }

    def reset(self) -> None:
        self.violations = []
        self._context = PlaneAnnotation.PRIMARY
