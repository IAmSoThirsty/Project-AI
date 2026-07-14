"""Cross-package integration test for companion.cognition + companion.voice_bonding.

Verifies:
- The controllers compose correctly (independent state, no shared
  state register collisions).
- Pluggable strategies work end-to-end.
- The Thought/VoiceBondingScore validation runs before state mutation
  (fail-closed at validation).
- Recording a thought bumps revision exactly once.
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from capability import CapabilityAuthority
from companion import (
    BOND_IDENTITY_OPERATION,
    CognitionController,
    CognitionError,
    Thought,
    VoiceBondingController,
    VoiceBondingError,
    VoiceBondingScore,
)
from execution import ExecutionGate
from governance import GovernanceEngine, RuleGovernor
from kernel import EventSpine


@pytest.fixture
def capabilities() -> CapabilityAuthority:
    return CapabilityAuthority(
        b"c" * 32,
        issuer="project-ai",
        token_id_factory=iter(f"cap-{i}" for i in range(100)).__next__,
    )


@pytest.fixture
def gate(capabilities: CapabilityAuthority) -> ExecutionGate:
    allow_governor = RuleGovernor("primary", rules=())
    governance = GovernanceEngine(policy_version="v1", governors=[allow_governor])
    return ExecutionGate(
        governance=governance,
        capabilities=capabilities,
        events=EventSpine(),
    )


def _issue_capability(capabilities: CapabilityAuthority, operation: str, resource: str) -> str:
    return capabilities.issue(
        subject="quench-1",
        operation=operation,
        resource=resource,
        ttl=timedelta(minutes=5),
    )


def _valid_thought() -> Thought:
    return Thought(
        thought_type="observation",
        content="integration test",
        confidence=0.7,
        source="test",
        timestamp="2026-06-25T00:00:00Z",
    )


def _valid_score() -> VoiceBondingScore:
    return VoiceBondingScore(
        model_id="model-int",
        expression="neutral",
        score=0.4,
        timestamp="2026-06-25T00:00:00Z",
    )


# ---------------------------------------------------------------------------
# Composition: independent state, no collisions
# ---------------------------------------------------------------------------


def test_two_controllers_have_independent_state() -> None:
    cognition = CognitionController()
    voice = VoiceBondingController()
    cognition.record_thought(_valid_thought(), expected_revision=0)
    voice.record_interaction(_valid_score(), expected_revision=0)
    assert len(cognition.thoughts) == 1
    assert len(voice.history) == 1
    # Cognition and voice-bonding state registers are distinct.
    assert cognition.snapshot().revision == 1
    assert voice.snapshot().revision == 1


def test_controllers_do_not_share_keys() -> None:
    cognition = CognitionController()
    voice = VoiceBondingController()
    cognition.record_thought(_valid_thought(), expected_revision=0)
    voice.record_interaction(_valid_score(), expected_revision=0)
    cognition_keys = set(cognition.snapshot().values.keys())
    voice_keys = set(voice.snapshot().values.keys())
    assert cognition_keys.isdisjoint(voice_keys)


# ---------------------------------------------------------------------------
# Pluggable strategies end-to-end
# ---------------------------------------------------------------------------


def test_custom_cognition_strategy_drives_state() -> None:
    def word_count(thoughts: list) -> str:  # type: ignore[type-arg]
        return f"count={len(thoughts)}"

    ctrl = CognitionController(strategy=word_count)  # type: ignore[arg-type]
    ctrl.record_thought(_valid_thought(), expected_revision=0)
    ctrl.record_thought(_valid_thought(), expected_revision=1)
    ctrl.record_thought(_valid_thought(), expected_revision=2)
    assert ctrl.current_state == "count=3"


def test_custom_voice_profile_advances_phase() -> None:
    """A custom profile can drive the bonding phase directly."""

    def fast_bond(_p: str, _e: str, _s: float) -> str:
        return "bonded"

    ctrl = VoiceBondingController(profile=fast_bond)  # type: ignore[arg-type]
    ctrl.record_interaction(_valid_score(), expected_revision=0)
    assert ctrl.current_phase == "bonded"


# ---------------------------------------------------------------------------
# Fail-closed: validation runs before mutation
# ---------------------------------------------------------------------------


def test_invalid_thought_does_not_mutate_state() -> None:
    ctrl = CognitionController()
    initial_thoughts = len(ctrl.thoughts)
    initial_rev = ctrl.snapshot().revision
    with pytest.raises(CognitionError):
        ctrl.record_thought(
            Thought(
                thought_type="revelation",  # unknown type
                content="x",
                confidence=0.5,
                source="y",
                timestamp="z",
            ),
            expected_revision=0,
        )
    assert len(ctrl.thoughts) == initial_thoughts
    assert ctrl.snapshot().revision == initial_rev


def test_invalid_score_does_not_mutate_state() -> None:
    ctrl = VoiceBondingController()
    initial_history = len(ctrl.history)
    initial_rev = ctrl.snapshot().revision
    with pytest.raises(VoiceBondingError):
        ctrl.record_interaction(
            VoiceBondingScore(
                model_id="",
                expression="neutral",
                score=0.5,
                timestamp="z",
            ),
            expected_revision=0,
        )
    assert len(ctrl.history) == initial_history
    assert ctrl.snapshot().revision == initial_rev


# ---------------------------------------------------------------------------
# Atomicity: each call bumps revision exactly once
# ---------------------------------------------------------------------------


def test_cognition_record_bumps_revision_exactly_once() -> None:
    ctrl = CognitionController()
    ctrl.record_thought(_valid_thought(), expected_revision=0)
    ctrl.record_thought(_valid_thought(), expected_revision=1)
    ctrl.record_thought(_valid_thought(), expected_revision=2)
    assert ctrl.snapshot().revision == 3


def test_voice_bonding_record_bumps_revision_exactly_once() -> None:
    ctrl = VoiceBondingController()
    ctrl.record_interaction(_valid_score(), expected_revision=0)
    ctrl.record_interaction(_valid_score(), expected_revision=1)
    assert ctrl.snapshot().revision == 2


# ---------------------------------------------------------------------------
# Capabilities: capability authority is set up but not used here
# (companion controllers don't route through the gate in Phase E; this
# test exists to verify the fixture wiring is correct).
# ---------------------------------------------------------------------------


def test_gate_fixture_is_wired(capabilities: CapabilityAuthority, gate: ExecutionGate) -> None:
    token = _issue_capability(capabilities, BOND_IDENTITY_OPERATION, "companion:quench-1")
    assert isinstance(token, str)
    assert token != ""
    assert gate is not None
