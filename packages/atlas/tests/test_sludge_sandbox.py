"""Tests for canonical Atlas Sludge sandbox (Phase J2.7)."""

from __future__ import annotations

from pathlib import Path

import pytest

from atlas import (
    SUBORDINATION_NOTICE,
    AuditLevel,
    AuditTrail,
    NarrativeArchetype,
    SludgeNarrative,
    SludgeSandbox,
    SludgeSandboxError,
    get_sludge_sandbox,
    reset_sludge_sandbox,
)


def test_sludge_narrative_validates_stack_and_banner() -> None:
    with pytest.raises(SludgeSandboxError, match="stack"):
        SludgeNarrative(
            narrative_id="SLUDGE-ABC",
            source_snapshot_sha256="a" * 64,
            archetypes=(NarrativeArchetype.HIDDEN_ELITES,),
            branches=("fictional branch",),
            stack="RS",
        )

    narrative = SludgeNarrative(
        narrative_id="SLUDGE-ABC",
        source_snapshot_sha256="a" * 64,
        archetypes=(NarrativeArchetype.HIDDEN_ELITES,),
        branches=("fictional branch",),
    )
    assert narrative.stack == "SS"
    assert narrative.is_sludge is True
    assert narrative.subordination_notice == SUBORDINATION_NOTICE
    assert "FICTIONAL NARRATIVE SIMULATION" in narrative.fiction_banner


def test_sandbox_does_not_create_default_filesystem_path(tmp_path: Path) -> None:
    sandbox_dir = tmp_path / "sludge"

    sandbox = SludgeSandbox(sandbox_dir=sandbox_dir)

    assert sandbox.sandbox_dir == sandbox_dir
    assert not sandbox_dir.exists()


def test_generate_narrative_is_deterministic_and_strips_rs_content() -> None:
    sandbox = SludgeSandbox()
    rs_snapshot: dict[str, object] = {
        "stack": "RS",
        "outcome": "inflation rises by 12 percent",
        "probability": 0.91,
    }

    first = sandbox.generate_narrative(rs_snapshot)
    second = sandbox.generate_narrative(rs_snapshot)

    assert first == second
    assert first.narrative_id.startswith("SLUDGE-")
    assert first.stack == "SS"
    assert first.is_sludge is True
    assert first.contains_numeric_probabilities is False
    assert first.source_snapshot_sha256 == second.source_snapshot_sha256
    assert "12" not in " ".join(first.branches)
    assert "0.91" not in " ".join(first.branches)
    assert "inflation" not in " ".join(first.branches).lower()


def test_generate_narrative_accepts_explicit_archetypes() -> None:
    sandbox = SludgeSandbox()

    narrative = sandbox.generate_narrative(
        {"stack": "RS", "claim": "source-backed"},
        archetypes=(NarrativeArchetype.SUPPRESSED_TECH, NarrativeArchetype.FALSE_FLAGS),
    )

    assert narrative.archetypes == (
        NarrativeArchetype.SUPPRESSED_TECH,
        NarrativeArchetype.FALSE_FLAGS,
    )
    assert len(narrative.branches) == 2


def test_generate_narrative_rejects_non_rs_snapshots() -> None:
    sandbox = SludgeSandbox()

    with pytest.raises(SludgeSandboxError, match="RS"):
        sandbox.generate_narrative({"stack": "TS-1", "claim": "timeline"})


def test_generate_narrative_rejects_empty_snapshot() -> None:
    sandbox = SludgeSandbox()

    with pytest.raises(SludgeSandboxError, match="rs_snapshot"):
        sandbox.generate_narrative({})


def test_sandbox_audit_events_are_hash_chained() -> None:
    trail = AuditTrail()
    sandbox = SludgeSandbox(audit_trail=trail)

    narrative = sandbox.generate_narrative({"stack": "RS", "claim": "source-backed"})

    assert len(trail.events) == 2
    assert trail.events[0].action == "sludge_sandbox_initialized"
    assert trail.events[1].action == "sludge_narrative_generated"
    assert trail.events[1].level is AuditLevel.HIGH_PRIORITY
    assert dict(trail.events[1].evidence)["narrative_id"] == narrative.narrative_id
    assert trail.verify_chain().is_valid is True


def test_validate_no_contamination_rejects_sludge_markers_in_rs() -> None:
    sandbox = SludgeSandbox()

    with pytest.raises(SludgeSandboxError, match="contamination"):
        sandbox.validate_no_contamination(
            {
                "stack": "RS",
                "source": "sludge_sandbox",
                "watermark": "FICTIONAL NARRATIVE",
            }
        )


def test_validate_no_contamination_allows_sludge_markers_in_ss() -> None:
    sandbox = SludgeSandbox()

    sandbox.validate_no_contamination(
        {
            "stack": "SS",
            "source": "sludge_sandbox",
            "watermark": "FICTIONAL NARRATIVE",
        }
    )


def test_singleton_reset_creates_fresh_instance() -> None:
    reset_sludge_sandbox()
    first = get_sludge_sandbox()
    second = get_sludge_sandbox()
    assert first is second

    reset_sludge_sandbox()
    third = get_sludge_sandbox()
    assert third is not first
