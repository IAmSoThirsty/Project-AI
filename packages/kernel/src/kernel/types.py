"""Canonical data types shared by downward-only Project-AI packages."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


class Outcome(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"


@dataclass(frozen=True)
class ActionRequest:
    action_id: str
    actor: str
    operation: str
    resource: str
    payload: Mapping[str, JsonValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("action_id", "actor", "operation", "resource"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must not be empty")
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


@dataclass(frozen=True)
class Decision:
    outcome: Outcome
    reasons: tuple[str, ...]
    policy_version: str

    def __post_init__(self) -> None:
        if not self.policy_version.strip():
            raise ValueError("policy_version must not be empty")
        if self.outcome is not Outcome.ALLOW and not self.reasons:
            raise ValueError("non-ALLOW decisions require a reason")
