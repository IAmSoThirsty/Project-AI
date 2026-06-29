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


class AtlasStatus(FrozenModel):
    status: Literal["available"] = "available"
    version: Literal["0.0.0.dev0"] = "0.0.0.dev0"
    stack: Literal["Atlas"] = "Atlas"
    authority: Literal["analysis_only"] = "analysis_only"
    protected_operations: tuple[Literal["sludge_narrative"], ...] = ("sludge_narrative",)
    subordination_notice: str


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
type JsonValue = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


class AtlasSludgeRequest(FrozenModel):
    rs_snapshot: dict[str, JsonValue] = Field(min_length=1)
    archetypes: (
        tuple[
            Literal[
                "hidden_elites",
                "suppressed_tech",
                "false_flags",
                "prophetic_inevitability",
            ],
            ...,
        ]
        | None
    ) = None


class AtlasSludgeNarrative(FrozenModel):
    archetypes: tuple[
        Literal[
            "hidden_elites",
            "suppressed_tech",
            "false_flags",
            "prophetic_inevitability",
        ],
        ...,
    ]
    branches: tuple[str, ...]
    contains_numeric_probabilities: Literal[False] = False
    fiction_banner: str
    is_sludge: Literal[True] = True
    narrative_id: str
    source_snapshot_sha256: str
    stack: Literal["SS"] = "SS"
    subordination_notice: str
    watermark: str


class AtlasSludgeResponse(FrozenModel):
    accepted: Literal[True] = True
    event: Literal["atlas.sludge_narrative"] = "atlas.sludge_narrative"
    hash: str
    narrative: AtlasSludgeNarrative


class AuditResponse(FrozenModel):
    chain_valid: Literal[True] = True
    count: int = Field(ge=0)
    records: tuple[dict[str, JsonScalar], ...]
