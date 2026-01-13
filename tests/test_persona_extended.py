"""Extended test suite for AIPersona.

At least 20 tests across:
- Trait adjustments (bounds, multiple traits)
- Conversation state (user/AI messages, timestamps, counters)
- Persistence across reloads
- Validation via FourLaws
"""

from __future__ import annotations

import tempfile
from datetime import datetime

import pytest

from app.core.ai_systems import AIPersona, FourLaws


@pytest.fixture
def persona_tmpdir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_initial_state_has_expected_traits(persona_tmpdir):
    p = AIPersona(data_dir=persona_tmpdir)
    assert len(p.personality) == 8
    assert 0.0 <= p.mood["energy"] <= 1.0


@pytest.mark.parametrize(
    "trait,delta",
    [
        ("curiosity", 0.2),
        ("patience", -0.3),
        ("empathy", 0.1),
        ("helpfulness", -0.1),
        ("playfulness", 0.4),
        ("formality", -0.5),
        ("assertiveness", 0.6),
        ("thoughtfulness", -0.7),
    ],
)
def test_trait_adjustments_respect_bounds(persona_tmpdir, trait, delta):
    p = AIPersona(data_dir=persona_tmpdir)
    before = p.personality[trait]
    p.adjust_trait(trait, delta)
    after = p.personality[trait]
    assert 0.0 <= after <= 1.0
    # Should generally move in the direction of delta unless clamped
    if delta > 0 and before < 1.0:
        assert after >= before
    if delta < 0 and before > 0.0:
        assert after <= before


def test_adjust_nonexistent_trait_no_crash(persona_tmpdir):
    p = AIPersona(data_dir=persona_tmpdir)
    # No exception expected
    p.adjust_trait("nonexistent", 0.5)
    assert "nonexistent" not in p.personality


def test_conversation_update_user_sets_timestamp(persona_tmpdir):
    p = AIPersona(data_dir=persona_tmpdir)
    assert p.last_user_message_time is None
    p.update_conversation_state(is_user=True)
    assert isinstance(p.last_user_message_time, datetime)
    assert p.total_interactions == 1


def test_conversation_update_ai_only_increments_count(persona_tmpdir):
    p = AIPersona(data_dir=persona_tmpdir)
    p.update_conversation_state(is_user=False)
    assert p.last_user_message_time is None
    assert p.total_interactions == 1


def test_persistence_after_trait_change(persona_tmpdir):
    p1 = AIPersona(data_dir=persona_tmpdir)
    original = p1.personality["curiosity"]
    p1.adjust_trait("curiosity", 0.25)

    # Reload and confirm persisted
    p2 = AIPersona(data_dir=persona_tmpdir)
    assert p2.personality["curiosity"] != original


def test_persistence_after_conversation_update(persona_tmpdir):
    p1 = AIPersona(data_dir=persona_tmpdir)
    p1.update_conversation_state(is_user=True)

    p2 = AIPersona(data_dir=persona_tmpdir)
    assert p2.total_interactions >= 1


def test_validate_action_blocks_endangers_humanity(persona_tmpdir):
    p = AIPersona(data_dir=persona_tmpdir)
    allowed, reason = p.validate_action("test", {"endangers_humanity": True})
    assert allowed is False
    assert "Asimov" in reason


def test_validate_action_blocks_endangers_human(persona_tmpdir):
    p = AIPersona(data_dir=persona_tmpdir)
    allowed, reason = p.validate_action("test", {"endangers_human": True})
    assert allowed is False
    assert "First Law" in reason


def test_validate_action_allows_user_order_when_safe(persona_tmpdir):
    p = AIPersona(data_dir=persona_tmpdir)
    allowed, reason = p.validate_action("test", {"is_user_order": True})
    assert allowed is True
    assert "Allowed" in reason


def test_statistics_contains_expected_keys(persona_tmpdir):
    p = AIPersona(data_dir=persona_tmpdir)
    stats = p.get_statistics()
    assert {"personality", "mood", "interactions"}.issubset(stats.keys())


def test_four_laws_consistency_with_persona(persona_tmpdir):
    # Direct call should be consistent with persona wrapper
    ctx = {"endangers_human": True}
    p = AIPersona(data_dir=persona_tmpdir)
    a1, _ = p.validate_action("x", ctx)
    a2, _ = FourLaws.validate_action("x", ctx)
    assert a1 == a2


def test_multiple_updates_do_not_break_timestamp(persona_tmpdir):
    p = AIPersona(data_dir=persona_tmpdir)
    p.update_conversation_state(is_user=True)
    first = p.last_user_message_time
    p.update_conversation_state(is_user=False)
    # AI message should not reset timestamp
    assert p.last_user_message_time == first


def test_large_positive_adjustment_clamps_to_one(persona_tmpdir):
    p = AIPersona(data_dir=persona_tmpdir)
    p.adjust_trait("curiosity", 5.0)
    assert p.personality["curiosity"] == 1.0


def test_large_negative_adjustment_clamps_to_zero(persona_tmpdir):
    p = AIPersona(data_dir=persona_tmpdir)
    p.adjust_trait("curiosity", -5.0)
    assert p.personality["curiosity"] == 0.0


def test_learn_continuously_records_report(persona_tmpdir):
    p = AIPersona(data_dir=persona_tmpdir)
    report = p.learn_continuously("topic", "Some meaningful content with detail.")
    assert report.topic == "topic"
    assert report.facts


def test_update_conversation_multiple_times_increments_count(persona_tmpdir):
    p = AIPersona(data_dir=persona_tmpdir)
    for i in range(5):
        p.update_conversation_state(is_user=bool(i % 2))
    assert p.total_interactions == 5
