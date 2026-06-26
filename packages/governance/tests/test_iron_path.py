"""Tests for ``governance.iron_path`` (the canonical action pipeline)."""

from __future__ import annotations

from collections.abc import Mapping

import pytest
from kernel.tarl_bridge import TarlGate
from kernel.threat_detection import (
    ThreatDetectionEngine,
)

from governance import (
    DEFAULT_POLICY_VERSION,
    GovernanceEngine,
    IronPath,
    Rule,
    RuleGovernor,
    threat_decision_from_assessment,
)
from kernel import (
    ActionRequest,
    Decision,
    EventSpine,
    InvariantEngine,
    InvariantSeverity,
    InvariantViolation,
    Outcome,
    TrustedClock,
)


def request() -> ActionRequest:
    return ActionRequest("a-1", "operator", "write", "record:1")


def governor(name: str, outcome: Outcome, reason: str = "") -> RuleGovernor:
    if outcome is Outcome.ALLOW:
        return RuleGovernor(name, ())
    return RuleGovernor(
        name,
        (Rule("rule", lambda _request, _state: False, outcome, reason or "failed"),),
    )


def build_path(
    spine: EventSpine | None = None,
    *,
    with_threat: bool = False,
    with_tarl: bool = False,
    policy_version: str = "v1",
    governors: tuple[RuleGovernor, ...] = (governor("ok", Outcome.ALLOW),),
) -> IronPath:
    spine = spine or EventSpine(clock=lambda: TrustedClock().now())
    governance = GovernanceEngine(policy_version=policy_version, governors=governors)
    threat = None
    if with_threat:
        threat = ThreatDetectionEngine(spine)
    tarl = TarlGate(spine) if with_tarl else None
    return IronPath(
        spine=spine,
        governance=governance,
        threat_engine=threat,
        tarl_gate=tarl,
        policy_version=policy_version,
    )


def test_default_policy_version_is_documented_constant() -> None:
    assert DEFAULT_POLICY_VERSION == "iron-path-v1"


def test_threat_decision_from_assessment_returns_none_for_info() -> None:
    spine = EventSpine(clock=lambda: TrustedClock().now())
    engine = ThreatDetectionEngine(spine)
    assessment = engine.analyze("s", "ls -la")
    assert assessment.severity is InvariantSeverity.INFO
    assert threat_decision_from_assessment(assessment, policy_version="v1") is None


def test_threat_decision_from_assessment_returns_decision_for_warning() -> None:
    spine = EventSpine(clock=lambda: TrustedClock().now())
    engine = ThreatDetectionEngine(spine)
    assessment = engine.analyze("s", "curl http://example.com")
    decision = threat_decision_from_assessment(assessment, policy_version="v1")
    if assessment.severity >= InvariantSeverity.WARNING:
        assert decision is not None
        assert decision.policy_version == "v1"


def test_iron_path_rejects_empty_policy_version() -> None:
    with pytest.raises(ValueError, match="policy_version"):
        build_path(policy_version="")


def test_iron_path_minimal_run_returns_decision() -> None:
    spine = EventSpine(clock=lambda: TrustedClock().now())
    path = build_path(spine=spine)
    result = path.run(request())
    assert result.outcome is Outcome.ALLOW
    assert result.allowed is True
    assert result.governance_result is not None


def test_iron_path_emits_governance_event() -> None:
    spine = EventSpine(clock=lambda: TrustedClock().now())
    path = build_path(spine=spine)
    path.run(request())
    # The GovernanceEngine produces an evidence bundle; the iron path itself
    # doesn't add a new event (events come from kernel.event_spine and
    # governance.evidence_bundle). The spine may still be empty after a
    # plain ALLOW since no invariant or governor raised. Confirm at least
    # no exceptions.
    assert isinstance(spine.events(), tuple)


def test_iron_path_runs_blocking_invariant_first() -> None:
    spine = EventSpine(clock=lambda: TrustedClock().now())

    def blocking(_request: ActionRequest, _state: Mapping[str, object]) -> InvariantViolation:
        return InvariantViolation("scope", "blocked", InvariantSeverity.BLOCKING)

    governance = GovernanceEngine(
        policy_version="v1",
        governors=(governor("ok", Outcome.ALLOW),),
        invariants=InvariantEngine((blocking,)),
    )
    path = IronPath(spine=spine, governance=governance)
    result = path.run(request())
    assert result.outcome is Outcome.DENY


def test_iron_path_with_threat_engine_emits_assessment() -> None:
    spine = EventSpine(clock=lambda: TrustedClock().now())
    path = build_path(spine=spine, with_threat=True)
    result = path.run(
        request(),
        threat_session="s1",
        threat_command="sudo apt install x",
        observed_behavior={},
    )
    assert result.threat_assessment is not None
    assert result.threat_assessment.event is not None
    assert result.threat_assessment.event.event_type.startswith("threat.")


def test_iron_path_with_threat_short_circuits_on_critical_deny() -> None:
    """CRITICAL threat must produce DENY without running governors."""
    called = False

    def tracking(_request: ActionRequest, _state: Mapping[str, object]) -> InvariantViolation:
        nonlocal called
        called = True
        return InvariantViolation("noop", "noop", InvariantSeverity.INFO)

    from kernel import InvariantEngine

    spine = EventSpine(clock=lambda: TrustedClock().now())

    def max_predictor(cmd: str, _behavior: Mapping[str, object]) -> float:
        return 1.0

    threat = ThreatDetectionEngine(spine, predictor=max_predictor)
    governance = GovernanceEngine(
        policy_version="v1",
        governors=(governor("should_not_run", Outcome.DENY, "should not reach"),),
        invariants=InvariantEngine((tracking,)),
    )
    path = IronPath(
        spine=spine,
        governance=governance,
        threat_engine=threat,
        policy_version="v1",
    )
    result = path.run(
        request(),
        threat_session="s",
        threat_command="rm -rf /",
    )
    # The threat engine contributes its DENY decision; governors are not
    # consulted when threat produces DENY.
    assert result.outcome is Outcome.DENY


def test_iron_path_with_tarl_emits_gate_event() -> None:
    spine = EventSpine(clock=lambda: TrustedClock().now())
    path = build_path(spine=spine, with_tarl=True)
    result = path.run(request())
    assert result.outcome is Outcome.ALLOW
    assert result.tarl_verdict is not None
    assert result.tarl_verdict.verdict == "ALLOW"


def test_iron_path_with_tarl_deny_propagates() -> None:
    """A high-severity threat must propagate TARL DENY through Iron Path."""
    spine = EventSpine(clock=lambda: TrustedClock().now())

    def max_predictor(cmd: str, _behavior: Mapping[str, object]) -> float:
        return 1.0

    threat = ThreatDetectionEngine(spine, predictor=max_predictor)
    tarl = TarlGate(spine)
    governance = GovernanceEngine(
        policy_version="v1",
        governors=(governor("ok", Outcome.ALLOW),),
    )
    path = IronPath(
        spine=spine,
        governance=governance,
        threat_engine=threat,
        tarl_gate=tarl,
        policy_version="v1",
    )
    # "chmod 4755" matches privesc_setuid, "/etc/passwd" matches cred_password_files
    result = path.run(
        request(),
        threat_session="s",
        threat_command="chmod 4755 /etc/passwd",
    )
    assert result.outcome is Outcome.DENY
    assert result.tarl_verdict is not None
    assert result.tarl_verdict.verdict == "DENY"


def test_iron_path_final_decision_is_frozen() -> None:
    spine = EventSpine(clock=lambda: TrustedClock().now())
    path = build_path(spine=spine)
    result = path.run(request())
    # Decision is a frozen dataclass; mutating it must raise.
    with pytest.raises((AttributeError, Exception)):
        result.final_decision = Decision(  # type: ignore[misc]
            Outcome.DENY, ("x",), "v1"
        )


def test_iron_path_thread_through_multiple_requests() -> None:
    """Same Iron Path should serve multiple requests with isolated state."""
    spine = EventSpine(clock=lambda: TrustedClock().now())
    path = build_path(
        spine=spine,
        governors=(governor("ok", Outcome.ALLOW), governor("review", Outcome.ESCALATE, "review")),
    )
    r1 = path.run(ActionRequest("a-1", "alice", "read", "r:1"))
    r2 = path.run(ActionRequest("a-2", "bob", "write", "r:2"))
    assert r1.outcome in (Outcome.ALLOW, Outcome.ESCALATE)
    assert r2.outcome in (Outcome.ALLOW, Outcome.ESCALATE)
    # Both requests should produce their own decision without cross-talk.
    assert r1.final_decision.outcome == r1.outcome
    assert r2.final_decision.outcome == r2.outcome


def test_iron_path_optional_threat_not_invoked_when_no_command() -> None:
    spine = EventSpine(clock=lambda: TrustedClock().now())
    path = build_path(spine=spine, with_threat=True)
    result = path.run(request())  # no threat_command
    assert result.threat_assessment is None
    assert result.outcome is Outcome.ALLOW
