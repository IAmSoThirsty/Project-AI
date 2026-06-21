"""Validated HTTP models for the development gateway."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class HealthResponse(FrozenModel):
    status: Literal["live"] = "live"
    version: Literal["0.0.0.dev0"] = "0.0.0.dev0"


class DoiRecord(FrozenModel):
    title: str
    doi: str
    domain: str
    url: str


class DoiResponse(FrozenModel):
    dois: tuple[DoiRecord, ...]


class ReplayStatus(FrozenModel):
    status: Literal["not_run", "pass", "fail"] = "not_run"
    invariants_passed: int = Field(default=0, ge=0)
    invariants_total: int = Field(default=5, ge=1)
    updated_at: str = ""


class VerdictRequest(FrozenModel):
    action_id: str = Field(min_length=1, max_length=256)
    verdict: Literal["ALLOW", "DENY", "ESCALATE"]
    source: str = Field(default="chimera", min_length=1, max_length=128)


class CanaryRequest(FrozenModel):
    canary_value: str = Field(min_length=1, max_length=4096)
    context: str = Field(min_length=1, max_length=512)


class AuditWriteResponse(FrozenModel):
    accepted: Literal[True] = True
    event: str
    hash: str


type JsonScalar = str | int | float | bool | None


class AuditResponse(FrozenModel):
    chain_valid: Literal[True] = True
    count: int = Field(ge=0)
    records: tuple[dict[str, JsonScalar], ...]
