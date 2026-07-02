"""Integration test: Atlas ContingencyTriggerFramework (J4.3).

Per docs/internal/J4_DISCOVERY.md Phase J4.3: the
ContingencyTriggerFramework is Layer 8 of ATLAS Omega
simulation. It implements a deterministic trigger system
with: condition evaluation (metric > threshold for
duration >= D), versioned and hashed playbooks, narrative
trigger blocking, and RS-only enforcement.

Honest scope:
- Tests the public surface: StackType, TriggerType,
  PlaybookAction, TriggerCondition, Playbook,
  TriggerActivation, ContingencyTriggerFramework,
  get_contingency_trigger_framework.
- Tests duration-based triggering (consecutive timesteps).
- Tests operator support (>, <, >=, <=, ==).
- Tests playbook hash + lock + integrity verification.
- Tests RS-only enforcement (non-RS raises).
- Tests narrative trigger rejection.
- Tests the framework lifecycle: register, evaluate,
  get_activation_history, get_statistics.
- Does NOT test the audit trail (the canonical atlas audit
  is tested separately).
"""

from __future__ import annotations

import pytest
from atlas.simulation.contingency_triggers import (
    ContingencyTriggerFramework,
    Playbook,
    PlaybookAction,
    StackType,
    TriggerCondition,
    TriggerType,
    get_contingency_trigger_framework,
)

# ── 1. Enums ──────────────────────────────────────


def test_stack_type_has_6_values() -> None:
    """StackType has the 6 expected values."""
    assert len(StackType) == 6
    assert StackType.RS.value == "reference_stack"
    assert StackType.SS.value == "sludge_stack"
    assert StackType.TS_0.value == "test_stack_0"


def test_trigger_type_has_4_values() -> None:
    """TriggerType has the 4 expected values."""
    assert len(TriggerType) == 4
    assert TriggerType.THRESHOLD.value == "threshold"
    assert TriggerType.DURATION.value == "duration"
    assert TriggerType.RATE.value == "rate"
    assert TriggerType.COMBINATION.value == "combination"


def test_playbook_action_has_5_values() -> None:
    """PlaybookAction has the 5 expected values."""
    assert len(PlaybookAction) == 5
    assert PlaybookAction.ALERT.value == "alert"
    assert PlaybookAction.MONITOR.value == "monitor"
    assert PlaybookAction.ANALYZE.value == "analyze"
    assert PlaybookAction.ESCALATE.value == "escalate"
    assert PlaybookAction.REPORT.value == "report"


# ── 2. TriggerCondition ───────────────────────────


def test_condition_default_construction() -> None:
    """TriggerCondition can be constructed with 4 required args."""
    c = TriggerCondition(
        condition_id="c1",
        metric_name="risk",
        threshold=0.7,
        operator=">",
    )
    assert c.condition_id == "c1"
    assert c.metric_name == "risk"
    assert c.threshold == 0.7
    assert c.operator == ">"
    assert c.duration_timesteps == 1
    assert c.consecutive_timesteps == 0


def test_condition_evaluate_greater_than() -> None:
    """TriggerCondition with '>' operator triggers on high value."""
    c = TriggerCondition(
        condition_id="c1",
        metric_name="x",
        threshold=0.7,
        operator=">",
        duration_timesteps=1,
    )
    assert c.evaluate(0.8) is True
    assert c.evaluate(0.5) is False


def test_condition_evaluate_less_than() -> None:
    """TriggerCondition with '<' operator triggers on low value."""
    c = TriggerCondition(
        condition_id="c1",
        metric_name="x",
        threshold=0.3,
        operator="<",
        duration_timesteps=1,
    )
    assert c.evaluate(0.2) is True
    assert c.evaluate(0.5) is False


def test_condition_evaluate_greater_equal() -> None:
    """TriggerCondition with '>=' operator triggers on equal-or-high."""
    c = TriggerCondition(
        condition_id="c1",
        metric_name="x",
        threshold=0.7,
        operator=">=",
        duration_timesteps=1,
    )
    assert c.evaluate(0.7) is True
    assert c.evaluate(0.6) is False


def test_condition_evaluate_less_equal() -> None:
    """TriggerCondition with '<=' operator triggers on equal-or-low."""
    c = TriggerCondition(
        condition_id="c1",
        metric_name="x",
        threshold=0.3,
        operator="<=",
        duration_timesteps=1,
    )
    assert c.evaluate(0.3) is True
    assert c.evaluate(0.4) is False


def test_condition_evaluate_equal() -> None:
    """TriggerCondition with '==' operator triggers on exact match."""
    c = TriggerCondition(
        condition_id="c1",
        metric_name="x",
        threshold=0.5,
        operator="==",
        duration_timesteps=1,
    )
    assert c.evaluate(0.5) is True
    assert c.evaluate(0.5000001) is True  # within tolerance
    assert c.evaluate(0.6) is False


def test_condition_evaluate_unknown_operator_raises() -> None:
    """TriggerCondition with unknown operator raises ValueError."""
    c = TriggerCondition(
        condition_id="c1",
        metric_name="x",
        threshold=0.5,
        operator="??",
        duration_timesteps=1,
    )
    with pytest.raises(ValueError, match="Unknown operator"):
        c.evaluate(0.5)


def test_condition_duration_tracking() -> None:
    """TriggerCondition with duration>1 needs consecutive timesteps."""
    c = TriggerCondition(
        condition_id="c1",
        metric_name="x",
        threshold=0.7,
        operator=">",
        duration_timesteps=2,
    )
    assert c.evaluate(0.8) is False  # consecutive=1, need 2
    assert c.evaluate(0.8) is True  # consecutive=2
    assert c.evaluate(0.3) is False  # reset
    assert c.evaluate(0.8) is False  # consecutive=1 again


def test_condition_reset() -> None:
    """TriggerCondition.reset clears consecutive + first_triggered."""
    c = TriggerCondition(
        condition_id="c1",
        metric_name="x",
        threshold=0.7,
        operator=">",
        duration_timesteps=2,
    )
    c.evaluate(0.8)
    assert c.consecutive_timesteps == 1
    c.reset()
    assert c.consecutive_timesteps == 0
    assert c.first_triggered is None


def test_condition_validate_clean() -> None:
    """TriggerCondition with valid params validates successfully."""
    c = TriggerCondition(
        condition_id="c1",
        metric_name="x",
        threshold=0.7,
        operator=">",
        duration_timesteps=1,
    )
    valid, errors = c.validate()
    assert valid
    assert errors == []


def test_condition_validate_empty_metric_name() -> None:
    """TriggerCondition with empty metric_name fails validation."""
    c = TriggerCondition(
        condition_id="c1",
        metric_name="",
        threshold=0.7,
        operator=">",
        duration_timesteps=1,
    )
    valid, errors = c.validate()
    assert not valid
    assert any("metric_name" in e for e in errors)


def test_condition_validate_invalid_operator() -> None:
    """TriggerCondition with invalid operator fails validation."""
    c = TriggerCondition(
        condition_id="c1",
        metric_name="x",
        threshold=0.7,
        operator="??",
        duration_timesteps=1,
    )
    valid, errors = c.validate()
    assert not valid
    assert any("operator" in e for e in errors)


def test_condition_validate_invalid_duration() -> None:
    """TriggerCondition with duration<1 fails validation."""
    c = TriggerCondition(
        condition_id="c1",
        metric_name="x",
        threshold=0.7,
        operator=">",
        duration_timesteps=0,
    )
    valid, errors = c.validate()
    assert not valid
    assert any("duration" in e for e in errors)


def test_condition_validate_nan_threshold() -> None:
    """TriggerCondition with NaN threshold fails validation."""
    c = TriggerCondition(
        condition_id="c1",
        metric_name="x",
        threshold=float("nan"),
        operator=">",
        duration_timesteps=1,
    )
    valid, errors = c.validate()
    assert not valid
    assert any("Invalid threshold" in e for e in errors)


# ── 3. Playbook ───────────────────────────────────


def test_playbook_default_construction() -> None:
    """Playbook can be constructed with id + version + name +
    description."""
    p = Playbook(
        playbook_id="pb1",
        version="1.0",
        name="Test",
        description="Test playbook",
    )
    assert p.playbook_id == "pb1"
    assert p.version == "1.0"
    assert p.name == "Test"
    assert p.actions == []
    assert p.conditions == []
    assert p.playbook_hash is None
    assert p.locked is False


def test_playbook_compute_hash_is_64_hex() -> None:
    """Playbook.compute_hash returns a 64-char hex string."""
    p = Playbook(
        playbook_id="pb1",
        version="1.0",
        name="Test",
        description="Test",
    )
    h = p.compute_hash()
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_playbook_compute_hash_deterministic() -> None:
    """Playbook.compute_hash is deterministic for same state."""
    p1 = Playbook(
        playbook_id="pb1",
        version="1.0",
        name="Test",
        description="Test",
        actions=[PlaybookAction.ALERT],
    )
    p2 = Playbook(
        playbook_id="pb1",
        version="1.0",
        name="Test",
        description="Test",
        actions=[PlaybookAction.ALERT],
    )
    assert p1.compute_hash() == p2.compute_hash()


def test_playbook_lock() -> None:
    """Playbook.lock sets the hash and locked flag."""
    p = Playbook(
        playbook_id="pb1",
        version="1.0",
        name="Test",
        description="Test",
    )
    p.lock()
    assert p.playbook_hash is not None
    assert p.locked is True


def test_playbook_verify_integrity_unlocked() -> None:
    """Playbook.verify_integrity returns True when not locked."""
    p = Playbook(
        playbook_id="pb1",
        version="1.0",
        name="Test",
        description="Test",
    )
    assert p.verify_integrity() is True


def test_playbook_verify_integrity_locked() -> None:
    """Playbook.verify_integrity returns True when locked + unchanged."""
    p = Playbook(
        playbook_id="pb1",
        version="1.0",
        name="Test",
        description="Test",
    )
    p.lock()
    assert p.verify_integrity() is True


def test_playbook_verify_integrity_tampered() -> None:
    """Playbook.verify_integrity returns False when tampered after lock."""
    p = Playbook(
        playbook_id="pb1",
        version="1.0",
        name="Test",
        description="Test",
    )
    p.lock()
    # Tamper with the playbook
    p.description = "Tampered"
    assert p.verify_integrity() is False


# ── 4. ContingencyTriggerFramework ────────────────


def test_framework_creation_with_rs() -> None:
    """ContingencyTriggerFramework can be created with StackType.RS."""
    fw = ContingencyTriggerFramework(stack=StackType.RS)
    assert fw.stack == StackType.RS
    assert fw.playbooks == {}
    assert fw.activations == []
    assert fw.timestep == 0


def test_framework_creation_with_non_rs_raises() -> None:
    """ContingencyTriggerFramework raises on non-RS stack."""
    with pytest.raises(ValueError, match="only allowed in RS stack"):
        ContingencyTriggerFramework(stack=StackType.SS)


def test_framework_register_playbook() -> None:
    """ContingencyTriggerFramework.register_playbook stores the playbook."""
    fw = ContingencyTriggerFramework(stack=StackType.RS)
    c = TriggerCondition(
        condition_id="c1",
        metric_name="risk",
        threshold=0.7,
        operator=">",
        duration_timesteps=1,
    )
    p = Playbook(
        playbook_id="pb1",
        version="1.0",
        name="Test",
        description="Test",
        conditions=[c],
    )
    fw.register_playbook(p)
    assert "pb1" in fw.playbooks
    assert p.locked is True
    assert p.playbook_hash is not None


def test_framework_register_invalid_playbook_raises() -> None:
    """ContingencyTriggerFramework.register_playbook raises on invalid conditions."""
    fw = ContingencyTriggerFramework(stack=StackType.RS)
    c = TriggerCondition(
        condition_id="c1",
        metric_name="",
        threshold=0.7,
        operator=">",
        duration_timesteps=1,
    )
    p = Playbook(
        playbook_id="pb1",
        version="1.0",
        name="Test",
        description="Test",
        conditions=[c],
    )
    with pytest.raises(ValueError, match="Invalid condition"):
        fw.register_playbook(p)


def test_framework_verify_all_playbooks_empty() -> None:
    """ContingencyTriggerFramework.verify_all_playbooks returns True
    when no playbooks."""
    fw = ContingencyTriggerFramework(stack=StackType.RS)
    valid, errors = fw.verify_all_playbooks()
    assert valid
    assert errors == []


def test_framework_verify_all_playbooks_all_valid() -> None:
    """ContingencyTriggerFramework.verify_all_playbooks returns True
    when all playbooks are valid."""
    fw = ContingencyTriggerFramework(stack=StackType.RS)
    p = Playbook(
        playbook_id="pb1",
        version="1.0",
        name="Test",
        description="Test",
    )
    fw.register_playbook(p)
    valid, errors = fw.verify_all_playbooks()
    assert valid
    assert errors == []


def test_framework_verify_all_playbooks_tampered() -> None:
    """ContingencyTriggerFramework.verify_all_playbooks detects tampered
    playbooks."""
    fw = ContingencyTriggerFramework(stack=StackType.RS)
    p = Playbook(
        playbook_id="pb1",
        version="1.0",
        name="Test",
        description="Test",
    )
    fw.register_playbook(p)
    p.description = "Tampered"
    valid, errors = fw.verify_all_playbooks()
    assert not valid
    assert any("pb1" in e for e in errors)


def test_framework_reject_narrative_trigger_raises() -> None:
    """ContingencyTriggerFramework.reject_narrative_trigger raises ValueError."""
    fw = ContingencyTriggerFramework(stack=StackType.RS)
    with pytest.raises(ValueError, match="Narrative triggers are BLOCKED"):
        fw.reject_narrative_trigger("some narrative trigger")


def test_framework_evaluate_triggers_no_match() -> None:
    """ContingencyTriggerFramework.evaluate_triggers returns empty when
    no conditions met."""
    fw = ContingencyTriggerFramework(stack=StackType.RS)
    c = TriggerCondition(
        condition_id="c1",
        metric_name="risk",
        threshold=0.7,
        operator=">",
        duration_timesteps=1,
    )
    p = Playbook(
        playbook_id="pb1",
        version="1.0",
        name="Test",
        description="Test",
        conditions=[c],
    )
    fw.register_playbook(p)
    activations = fw.evaluate_triggers({"risk": 0.5})
    assert activations == []


def test_framework_evaluate_triggers_with_match() -> None:
    """ContingencyTriggerFramework.evaluate_triggers returns activation
    when condition met."""
    fw = ContingencyTriggerFramework(stack=StackType.RS)
    c = TriggerCondition(
        condition_id="c1",
        metric_name="risk",
        threshold=0.7,
        operator=">",
        duration_timesteps=1,
    )
    p = Playbook(
        playbook_id="pb1",
        version="1.0",
        name="Test",
        description="Test",
        conditions=[c],
        actions=[PlaybookAction.ALERT],
    )
    fw.register_playbook(p)
    activations = fw.evaluate_triggers({"risk": 0.8})
    assert len(activations) == 1
    assert activations[0].playbook_id == "pb1"
    assert "c1" in activations[0].triggering_conditions
    assert PlaybookAction.ALERT in activations[0].recommended_actions


def test_framework_evaluate_triggers_missing_metric() -> None:
    """ContingencyTriggerFramework.evaluate_triggers handles missing metrics."""
    fw = ContingencyTriggerFramework(stack=StackType.RS)
    c = TriggerCondition(
        condition_id="c1",
        metric_name="risk",
        threshold=0.7,
        operator=">",
        duration_timesteps=1,
    )
    p = Playbook(
        playbook_id="pb1",
        version="1.0",
        name="Test",
        description="Test",
        conditions=[c],
    )
    fw.register_playbook(p)
    # 'risk' is missing
    activations = fw.evaluate_triggers({"other": 0.5})
    assert activations == []


def test_framework_evaluate_triggers_increments_timestep() -> None:
    """ContingencyTriggerFramework.evaluate_triggers advances timestep."""
    fw = ContingencyTriggerFramework(stack=StackType.RS)
    fw.evaluate_triggers({})
    assert fw.timestep == 1
    fw.evaluate_triggers({})
    assert fw.timestep == 2


def test_framework_get_activation_history() -> None:
    """ContingencyTriggerFramework.get_activation_history returns a copy."""
    fw = ContingencyTriggerFramework(stack=StackType.RS)
    c = TriggerCondition(
        condition_id="c1",
        metric_name="risk",
        threshold=0.7,
        operator=">",
        duration_timesteps=1,
    )
    p = Playbook(
        playbook_id="pb1",
        version="1.0",
        name="Test",
        description="Test",
        conditions=[c],
    )
    fw.register_playbook(p)
    fw.evaluate_triggers({"risk": 0.8})
    history = fw.get_activation_history()
    assert len(history) == 1
    # Should be a copy
    history.clear()
    assert len(fw.activations) == 1  # engine unaffected


def test_framework_get_statistics() -> None:
    """ContingencyTriggerFramework.get_statistics returns counts."""
    fw = ContingencyTriggerFramework(stack=StackType.RS)
    p = Playbook(
        playbook_id="pb1",
        version="1.0",
        name="Test",
        description="Test",
    )
    fw.register_playbook(p)
    fw.evaluate_triggers({})
    stats = fw.get_statistics()
    assert stats["playbooks"] == 1
    assert stats["total_activations"] == 0
    assert stats["timestep"] == 1
    assert stats["stack"] == "reference_stack"


# ── 5. Singleton factory ──────────────────────────


def test_get_contingency_trigger_framework_singleton() -> None:
    """get_contingency_trigger_framework returns the same instance."""
    import atlas.simulation.contingency_triggers as mod

    mod._framework = None
    f1 = get_contingency_trigger_framework()
    f2 = get_contingency_trigger_framework()
    assert f1 is f2


# ── 6. Public surface completeness ────────────────


def test_public_surface_complete() -> None:
    """All 8 public symbols are exported."""
    import atlas.simulation.contingency_triggers as m

    expected = {
        "StackType",
        "TriggerType",
        "PlaybookAction",
        "TriggerCondition",
        "Playbook",
        "TriggerActivation",
        "ContingencyTriggerFramework",
        "get_contingency_trigger_framework",
    }
    assert expected.issubset(set(m.__all__))
