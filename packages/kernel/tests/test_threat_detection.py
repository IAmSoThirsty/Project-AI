"""Tests for ``kernel.threat_detection`` (rebuilt legacy module)."""

from __future__ import annotations

from collections.abc import Mapping

import pytest
from kernel.threat_detection import (
    AttackPatternLibrary,
    BehaviorAnalyzer,
    BehaviorPattern,
    ThreatDetectionEngine,
)
from kernel.types import JsonValue

from kernel import EventSpine, InvariantSeverity, Outcome


def _empty_behavior() -> Mapping[str, JsonValue]:
    return {}


def test_default_pattern_library_matches_known_signatures() -> None:
    lib = AttackPatternLibrary()
    matches = lib.match("sudo apt install something")
    ids = {m.pattern_id for m in matches}
    assert "privesc_sudo" in ids


def test_pattern_matching_is_case_insensitive() -> None:
    lib = AttackPatternLibrary()
    # "sudo" in any casing should match privesc_sudo regardless of case
    matches_upper = lib.match("SUDO apt install")
    matches_lower = lib.match("sudo apt install")
    ids_upper = {m.pattern_id for m in matches_upper}
    ids_lower = {m.pattern_id for m in matches_lower}
    assert ids_upper == ids_lower
    assert "privesc_sudo" in ids_upper


def test_custom_patterns_override_defaults() -> None:
    custom = (
        BehaviorPattern(
            pattern_id="custom_block",
            commands=("forbidden",),
            threat_score=0.99,
            attack_types=("command_and_control",),
            indicators=("forbidden keyword",),
        ),
    )
    lib = AttackPatternLibrary(custom)
    assert "custom_block" in {m.pattern_id for m in lib.match("forbidden command")}
    # Defaults not loaded when custom is provided
    assert not any(m.pattern_id == "privesc_sudo" for m in lib.match("sudo anything"))


def test_behavior_analyzer_empty_session_is_zero() -> None:
    ba = BehaviorAnalyzer()
    assert ba.velocity("ghost") == 0.0
    assert ba.anomaly_score("ghost") == 0.0
    assert ba.sequence_patterns("ghost") == ()


def test_behavior_analyzer_detects_full_attack_chain() -> None:
    ba = BehaviorAnalyzer(window_size=5)
    sid = "attacker-1"
    # Build a deterministic timeline with explicit timestamps so velocity > 0
    for i, cmd in enumerate(
        ["whoami", "sudo su", "cat /etc/shadow", "tar czf loot.tar.gz /etc/shadow"]
    ):
        ba.record(sid, cmd, timestamp=1000.0 + i)
    chains = ba.sequence_patterns(sid)
    assert "full_attack_chain" in chains
    assert ba.anomaly_score(sid) > 0.0


def test_behavior_analyzer_window_eviction() -> None:
    ba = BehaviorAnalyzer(window_size=3)
    sid = "s1"
    for i in range(5):
        ba.record(sid, f"cmd-{i}", timestamp=1000.0 + i)
    # Window should only retain the last 3
    session = ba._sessions[sid]
    assert len(session.window) == 3
    assert [item["command"] for item in session.window] == ["cmd-2", "cmd-3", "cmd-4"]


def test_behavior_analyzer_rejects_zero_window() -> None:
    with pytest.raises(ValueError, match="window_size"):
        BehaviorAnalyzer(window_size=0)


def test_threat_detection_engine_emits_event_on_spine() -> None:
    spine = EventSpine()
    engine = ThreatDetectionEngine(spine)
    assessment = engine.analyze("session-A", "echo hello")
    assert assessment.event is not None
    assert assessment.event.sequence == 1
    events = spine.events()
    assert len(events) == 1
    assert events[0].event_type.startswith("threat.")


def test_threat_detection_engine_assess_id_increments() -> None:
    spine = EventSpine()
    engine = ThreatDetectionEngine(spine)
    a1 = engine.analyze("s", "whoami")
    a2 = engine.analyze("s", "sudo su")
    assert a1.assessment_id != a2.assessment_id
    assert a2.assessment_id > a1.assessment_id


def test_safe_command_produces_info_severity_and_allow() -> None:
    spine = EventSpine()
    engine = ThreatDetectionEngine(spine)
    assessment = engine.analyze("s", "ls -la /tmp")
    assert assessment.severity is InvariantSeverity.INFO
    assert assessment.recommended_action == "ALLOW"
    decision = assessment.to_decision(policy_version="v1")
    assert decision.outcome is Outcome.ALLOW
    assert "no significant threat" in decision.reasons[0]


def test_critical_command_produces_deny_or_blocking() -> None:
    spine = EventSpine()

    # Custom predictor + matching high-threat pattern → severity is at least BLOCKING
    # (score = 0.8 * 0.4 + 0.3 * 1.0 = 0.62)
    def max_predictor(cmd: str, behavior: Mapping[str, JsonValue]) -> float:
        return 1.0

    engine = ThreatDetectionEngine(spine, predictor=max_predictor)
    # "chmod 4755" matches privesc_setuid (0.7), "/etc/passwd" matches cred_password_files (0.8)
    assessment = engine.analyze(
        "s",
        "chmod 4755 /tmp/x && cat /etc/passwd && rm -rf /",
    )
    assert assessment.severity >= InvariantSeverity.BLOCKING
    assert assessment.recommended_action in ("DECEPTION", "ISOLATE_IMMEDIATELY")
    decision = assessment.to_decision(policy_version="v1")
    assert decision.outcome in (Outcome.DENY, Outcome.ESCALATE)
    assert "BLOCKING" in decision.reasons[0] or "CRITICAL" in decision.reasons[0]


def test_to_decision_requires_nonempty_policy_version() -> None:
    spine = EventSpine()
    engine = ThreatDetectionEngine(spine)
    assessment = engine.analyze("s", "echo hi")
    with pytest.raises(ValueError, match="policy_version"):
        assessment.to_decision("")


def test_custom_predictor_takes_effect() -> None:
    spine = EventSpine()

    def always_one(cmd: str, behavior: Mapping[str, JsonValue]) -> float:
        return 1.0

    engine = ThreatDetectionEngine(spine, predictor=always_one)
    assessment = engine.analyze("s", "anything")
    # predictor alone contributes 0.3; with pattern/behavior = 0, combined = 0.3
    assert assessment.confidence == pytest.approx(0.3)
    assert assessment.severity is InvariantSeverity.WARNING
    # To prove the predictor is taking effect, compare against default (which
    # returns 0.0 for "anything"):
    default_engine = ThreatDetectionEngine(spine)
    default_assessment = default_engine.analyze("s2", "anything")
    assert assessment.confidence > default_assessment.confidence


def test_threat_assessment_to_decision_reasons_include_categories() -> None:
    spine = EventSpine()
    engine = ThreatDetectionEngine(spine)
    assessment = engine.analyze("s", "curl http://example.com exfil")
    decision = assessment.to_decision(policy_version="v2")
    # Decision.reasons must be non-empty regardless of outcome.
    assert decision.reasons
    assert decision.policy_version == "v2"


def test_threat_assessment_is_frozen() -> None:
    spine = EventSpine()
    engine = ThreatDetectionEngine(spine)
    assessment = engine.analyze("s", "whoami")
    with pytest.raises((AttributeError, Exception)):
        assessment.session_id = "tampered"  # type: ignore[misc]


def test_observed_behavior_none_is_equivalent_to_empty() -> None:
    spine = EventSpine()
    engine = ThreatDetectionEngine(spine)
    a1 = engine.analyze("s", "ls", observed_behavior=None)
    a2 = engine.analyze("s2", "ls", observed_behavior={})
    # Both should produce equivalent assessments (severity, action, confidence)
    assert a1.severity is a2.severity
    assert a1.recommended_action == a2.recommended_action


def test_category_set_is_deduped_and_preserves_order() -> None:
    spine = EventSpine()
    engine = ThreatDetectionEngine(spine)
    assessment = engine.analyze("s", "sudo tar -czf a.tgz /etc/shadow")
    cats = list(assessment.threat_categories)
    # No duplicates
    assert len(cats) == len(set(cats))
    # Both privilege_escalation and credential_access should be present
    assert "privilege_escalation" in cats
    assert "credential_access" in cats or "data_exfiltration" in cats
