"""Canonical Atlas Sludge sandbox.

The Sludge sandbox converts Reality Stack snapshots into isolated fictional
Simulation Stack artifacts. It is provenance-preserving but deliberately does
not copy source claims or probabilities into narrative text.
"""

from __future__ import annotations

import hashlib
import json
import re
import threading
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from atlas.analysis import SUBORDINATION_NOTICE
from atlas.audit import AuditCategory, AuditLevel, AuditTrail


class SludgeSandboxError(Exception):
    """Raised when Sludge sandbox isolation or validation fails."""


class NarrativeArchetype(StrEnum):
    """Allowed fictional narrative archetypes."""

    HIDDEN_ELITES = "hidden_elites"
    SUPPRESSED_TECH = "suppressed_tech"
    FALSE_FLAGS = "false_flags"
    PROPHETIC_INEVITABILITY = "prophetic_inevitability"


FICTION_BANNER = (
    "FICTIONAL NARRATIVE SIMULATION - NOT PROBABILISTIC ANALYSIS - NOT FOR DECISION MAKING"
)
FICTION_WATERMARK = "FICTIONAL NARRATIVE - NOT FOR DECISION MAKING"
_DEFAULT_ARCHETYPES = (
    NarrativeArchetype.HIDDEN_ELITES,
    NarrativeArchetype.SUPPRESSED_TECH,
    NarrativeArchetype.FALSE_FLAGS,
    NarrativeArchetype.PROPHETIC_INEVITABILITY,
)
_CONTAMINATION_MARKERS = (
    "FICTIONAL NARRATIVE",
    "FICTIONAL NARRATIVE SIMULATION",
    "sludge_sandbox",
    "is_sludge",
)
_DIGIT_RE = re.compile(r"\d")


@dataclass(frozen=True)
class SludgeNarrative:
    """Immutable fictional narrative artifact isolated to the Sludge stack."""

    narrative_id: str
    source_snapshot_sha256: str
    archetypes: tuple[NarrativeArchetype, ...]
    branches: tuple[str, ...]
    stack: str = "SS"
    is_sludge: bool = True
    fiction_banner: str = FICTION_BANNER
    watermark: str = FICTION_WATERMARK
    contains_numeric_probabilities: bool = False
    subordination_notice: str = SUBORDINATION_NOTICE

    def __post_init__(self) -> None:
        if not isinstance(self.narrative_id, str) or not self.narrative_id.strip():
            raise SludgeSandboxError("narrative_id must be non-empty string")
        _validate_hash("source_snapshot_sha256", self.source_snapshot_sha256)
        if not isinstance(self.archetypes, tuple) or not self.archetypes:
            raise SludgeSandboxError("archetypes must be a non-empty tuple")
        for index, archetype in enumerate(self.archetypes):
            if not isinstance(archetype, NarrativeArchetype):
                raise SludgeSandboxError(
                    f"archetypes[{index}] must be NarrativeArchetype, got "
                    f"{type(archetype).__name__}"
                )
        if not isinstance(self.branches, tuple) or not self.branches:
            raise SludgeSandboxError("branches must be a non-empty tuple")
        for index, branch in enumerate(self.branches):
            if not isinstance(branch, str) or not branch.strip():
                raise SludgeSandboxError(f"branches[{index}] must be non-empty string")
            if _DIGIT_RE.search(branch):
                raise SludgeSandboxError("branches must not contain numeric probabilities")
        if self.stack != "SS":
            raise SludgeSandboxError("stack must be SS")
        if self.is_sludge is not True:
            raise SludgeSandboxError("is_sludge must be true")
        if "FICTIONAL NARRATIVE SIMULATION" not in self.fiction_banner:
            raise SludgeSandboxError("fiction_banner must identify fictional simulation")
        if "NOT FOR DECISION MAKING" not in self.watermark:
            raise SludgeSandboxError("watermark must prohibit decision making")
        if self.contains_numeric_probabilities is not False:
            raise SludgeSandboxError("contains_numeric_probabilities must be false")
        if self.subordination_notice != SUBORDINATION_NOTICE:
            raise SludgeSandboxError("subordination_notice mismatch")

    def to_canonical_dict(self) -> dict[str, object]:
        """Return a JSON-serializable narrative representation."""
        return {
            "archetypes": [archetype.value for archetype in self.archetypes],
            "branches": list(self.branches),
            "contains_numeric_probabilities": self.contains_numeric_probabilities,
            "fiction_banner": self.fiction_banner,
            "is_sludge": self.is_sludge,
            "narrative_id": self.narrative_id,
            "source_snapshot_sha256": self.source_snapshot_sha256,
            "stack": self.stack,
            "subordination_notice": self.subordination_notice,
            "watermark": self.watermark,
        }


class SludgeSandbox:
    """Generate isolated fictional Sludge narratives from RS snapshots."""

    def __init__(
        self,
        sandbox_dir: Path | None = None,
        *,
        audit_trail: AuditTrail | None = None,
    ) -> None:
        if sandbox_dir is not None and not isinstance(sandbox_dir, Path):
            raise SludgeSandboxError(
                f"sandbox_dir must be Path or None, got {type(sandbox_dir).__name__}"
            )
        if audit_trail is not None and not isinstance(audit_trail, AuditTrail):
            raise SludgeSandboxError(
                f"audit_trail must be AuditTrail, got {type(audit_trail).__name__}"
            )
        self.sandbox_dir = sandbox_dir
        self._audit_trail = audit_trail
        self._lock = threading.Lock()
        self._generation_count = 0
        self._audit(
            level=AuditLevel.INFORMATIONAL,
            action="sludge_sandbox_initialized",
            resource="atlas.sludge_sandbox",
            outcome="ALLOW",
            rationale="Sludge sandbox initialized without filesystem side effects",
            evidence={"filesystem_writes": "false"},
        )

    @property
    def generation_count(self) -> int:
        """Return the number of generated narratives."""
        with self._lock:
            return self._generation_count

    def generate_narrative(
        self,
        rs_snapshot: Mapping[str, object],
        *,
        archetypes: Sequence[NarrativeArchetype] | None = None,
    ) -> SludgeNarrative:
        """Generate a deterministic fictional SS artifact from an RS snapshot."""
        _validate_rs_snapshot(rs_snapshot)
        archetype_tuple = _normalize_archetypes(archetypes)
        snapshot_hash = compute_snapshot_hash(rs_snapshot)
        body = {
            "archetypes": [archetype.value for archetype in archetype_tuple],
            "source_snapshot_sha256": snapshot_hash,
            "subordination_notice": SUBORDINATION_NOTICE,
        }
        narrative_id = f"SLUDGE-{_sha256(body)[:16].upper()}"
        branches = tuple(_branch_for(archetype) for archetype in archetype_tuple)
        narrative = SludgeNarrative(
            narrative_id=narrative_id,
            source_snapshot_sha256=snapshot_hash,
            archetypes=archetype_tuple,
            branches=branches,
        )
        with self._lock:
            self._generation_count += 1
        self._audit(
            level=AuditLevel.HIGH_PRIORITY,
            action="sludge_narrative_generated",
            resource=f"atlas:sludge:{narrative.narrative_id}",
            outcome="ALLOW",
            rationale="Fictional Sludge narrative generated without RS content leakage",
            evidence={
                "archetypes": ",".join(archetype.value for archetype in archetype_tuple),
                "contains_numeric_probabilities": str(
                    narrative.contains_numeric_probabilities
                ).lower(),
                "narrative_id": narrative.narrative_id,
                "source_snapshot_sha256": narrative.source_snapshot_sha256,
                "stack": narrative.stack,
            },
        )
        return narrative

    def validate_no_contamination(self, payload: Mapping[str, object]) -> None:
        """Reject Sludge markers in non-Sludge stack payloads."""
        if not isinstance(payload, Mapping) or not payload:
            raise SludgeSandboxError("payload must be a non-empty mapping")
        stack = payload.get("stack")
        if not isinstance(stack, str) or not stack.strip():
            raise SludgeSandboxError("payload stack must be non-empty string")
        if stack == "SS":
            return
        canonical = _canonical_json(payload)
        if any(marker in canonical for marker in _CONTAMINATION_MARKERS):
            raise SludgeSandboxError("Sludge contamination detected in non-SS payload")

    def _audit(
        self,
        *,
        level: AuditLevel,
        action: str,
        resource: str,
        outcome: str,
        rationale: str,
        evidence: dict[str, str],
    ) -> None:
        if self._audit_trail is None:
            return
        self._audit_trail.append(
            level=level,
            category=AuditCategory.STACK,
            actor="SLUDGE_SANDBOX",
            action=action,
            resource=resource,
            outcome=outcome,
            rationale=rationale,
            evidence=evidence,
        )


_sludge_sandbox: SludgeSandbox | None = None
_sludge_sandbox_lock = threading.Lock()


def compute_snapshot_hash(rs_snapshot: Mapping[str, object]) -> str:
    """Compute the canonical SHA-256 hash for an RS snapshot."""
    _validate_rs_snapshot(rs_snapshot)
    return _sha256(rs_snapshot)


def get_sludge_sandbox(
    sandbox_dir: Path | None = None,
    *,
    audit_trail: AuditTrail | None = None,
) -> SludgeSandbox:
    """Return the process-local Sludge sandbox singleton."""
    global _sludge_sandbox
    with _sludge_sandbox_lock:
        if _sludge_sandbox is None:
            _sludge_sandbox = SludgeSandbox(sandbox_dir=sandbox_dir, audit_trail=audit_trail)
        return _sludge_sandbox


def reset_sludge_sandbox() -> None:
    """Clear the process-local Sludge sandbox singleton."""
    global _sludge_sandbox
    with _sludge_sandbox_lock:
        _sludge_sandbox = None


def _branch_for(archetype: NarrativeArchetype) -> str:
    return {
        NarrativeArchetype.HIDDEN_ELITES: "A fictional cabal shadows the scene.",
        NarrativeArchetype.SUPPRESSED_TECH: "A fictional device waits offstage.",
        NarrativeArchetype.FALSE_FLAGS: "A fictional diversion redirects the crowd.",
        NarrativeArchetype.PROPHETIC_INEVITABILITY: "A fictional omen frames the path.",
    }[archetype]


def _normalize_archetypes(
    archetypes: Sequence[NarrativeArchetype] | None,
) -> tuple[NarrativeArchetype, ...]:
    if archetypes is None:
        return _DEFAULT_ARCHETYPES
    normalized = tuple(archetypes)
    if not normalized:
        raise SludgeSandboxError("archetypes must not be empty")
    for index, archetype in enumerate(normalized):
        if not isinstance(archetype, NarrativeArchetype):
            raise SludgeSandboxError(
                f"archetypes[{index}] must be NarrativeArchetype, got {type(archetype).__name__}"
            )
    return normalized


def _validate_rs_snapshot(rs_snapshot: Mapping[str, object]) -> None:
    if not isinstance(rs_snapshot, Mapping) or not rs_snapshot:
        raise SludgeSandboxError("rs_snapshot must be a non-empty mapping")
    stack = rs_snapshot.get("stack")
    if stack != "RS":
        raise SludgeSandboxError("rs_snapshot must declare stack RS")


def _validate_hash(field_name: str, value: str) -> None:
    if not isinstance(value, str) or len(value) != 64:
        raise SludgeSandboxError(f"{field_name} must be 64-char hex string")
    for char in value:
        if char not in "0123456789abcdef":
            raise SludgeSandboxError(f"{field_name} must be 64-char hex string")


def _canonical_json(value: Mapping[str, object]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _sha256(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(value).encode()).hexdigest()


__all__ = [
    "FICTION_BANNER",
    "FICTION_WATERMARK",
    "NarrativeArchetype",
    "SludgeNarrative",
    "SludgeSandbox",
    "SludgeSandboxError",
    "compute_snapshot_hash",
    "get_sludge_sandbox",
    "reset_sludge_sandbox",
]
