"""Cross-package integration: Iron Path + Triumvirate + Kernel threat + TARL gate.

This is the principal-architecture integration test. It exercises every
component built in the Wave 1 + Wave 2 rebuilds together to confirm
that the canonical execution pipeline (the Iron Path) properly composes:

* :class:`kernel.threat_detection.ThreatDetectionEngine` (kernel package,
  Wave 1)
* :class:`kernel.tarl_bridge.TarlGate` (kernel package, Wave 1)
* :class:`governance.engine.GovernanceEngine` (existing governance core)
* :class:`governance.triumvirate.TriumvirateGovernor` (Wave 2)
* :class:`governance.iron_path.IronPath` (Wave 2)

The integration test demonstrates that a complex action with both a
threat signal and a triumvirate consensus vote resolves to the
expected ``Decision`` and produces a coherent audit chain.
"""

from __future__ import annotations

from collections.abc import Mapping

from kernel.tarl_bridge import TarlGate
from kernel.threat_detection import ThreatDetectionEngine

from governance import (
    GovernanceEngine,
    IronPath,
    Quorum,
    Rule,
    RuleGovernor,
    TriumvirateGovernor,
)
from kernel import (
    ActionRequest,
    EventSpine,
    InvariantSeverity,
    InvariantViolation,
    Outcome,
    TrustedClock,
)


def request(actor: str = "alice", op: str = "write", resource: str = "record:1") -> ActionRequest:
    return ActionRequest("a-integration-1", actor, op, resource)


def build_full_pipeline(
    *,
    with_threat: bool = True,
    with_tarl: bool = True,
    triumvirate_quorum: Quorum = Quorum.MAJORITY,
) -> IronPath:
    """Build an Iron Path with every optional component wired in."""
    spine = EventSpine(clock=lambda: TrustedClock().now())

    safety = RuleGovernor("safety", ())
    policy = RuleGovernor("policy", ())
    capability = RuleGovernor("capability", ())
    triumvirate = TriumvirateGovernor(
        name="triumvirate",
        governors=(safety, policy, capability),
        quorum=triumvirate_quorum,
    )

    governance = GovernanceEngine(
        policy_version="iron-path-v1",
        governors=(triumvirate,),
    )
    threat_engine = ThreatDetectionEngine(spine) if with_threat else None
    tarl_gate = TarlGate(spine) if with_tarl else None

    return IronPath(
        spine=spine,
        governance=governance,
        threat_engine=threat_engine,
        tarl_gate=tarl_gate,
        policy_version="iron-path-v1",
    )


def test_pipeline_allows_safe_action_with_full_consensus() -> None:
    """Safe action + all three triumvirate members ALLOW → ALLOW."""
    path = build_full_pipeline()
    result = path.run(
        request(),
        threat_session="alice",
        threat_command="ls -la /tmp",
    )
    assert result.outcome is Outcome.ALLOW
    assert result.allowed is True
    assert result.threat_assessment is not None
    assert result.threat_assessment.severity is InvariantSeverity.INFO
    assert result.tarl_verdict is not None
    assert result.tarl_verdict.verdict == "ALLOW"
    assert result.governance_result is not None
    assert len(result.governance_result.votes) == 1
    assert result.governance_result.votes[0].governor == "triumvirate"


def test_pipeline_denies_action_with_blocking_threat() -> None:
    """A BLOCKING/CRITICAL threat must short-circuit governance → DENY."""
    spine = EventSpine(clock=lambda: TrustedClock().now())

    def max_predictor(cmd: str, _behavior: Mapping[str, object]) -> float:
        return 1.0

    threat_engine = ThreatDetectionEngine(spine, predictor=max_predictor)
    safety = RuleGovernor("safety", ())
    policy = RuleGovernor("policy", ())
    capability = RuleGovernor("capability", ())
    triumvirate = TriumvirateGovernor(
        name="triumvirate",
        governors=(safety, policy, capability),
        quorum=Quorum.MAJORITY,
    )
    governance = GovernanceEngine(policy_version="v1", governors=(triumvirate,))
    path = IronPath(
        spine=spine,
        governance=governance,
        threat_engine=threat_engine,
        policy_version="v1",
    )
    # "chmod 4755" matches privesc_setuid (0.7), "/etc/passwd" matches cred_password_files (0.8)
    # With predictor=1.0, combined score = 0.62 → BLOCKING
    result = path.run(
        request(),
        threat_session="attacker",
        threat_command="chmod 4755 /etc/passwd",
    )
    assert result.outcome is Outcome.DENY


def test_pipeline_escalates_when_triumvirate_cannot_reach_consensus() -> None:
    """All three triumvirate members ESCALATE → outcome is ESCALATE."""
    spine = EventSpine(clock=lambda: TrustedClock().now())

    def escalate(_request: ActionRequest, _state: Mapping[str, object]) -> InvariantViolation:
        # NOTE: RuleGovernor can only produce ESCALATE via a failing rule.
        # We construct three RuleGovernors each with a rule that fails.
        return None  # type: ignore[return-value]

    safety = RuleGovernor(
        "safety",
        (Rule("needs-human-review", lambda r, s: False, Outcome.ESCALATE, "safety review"),),
    )
    policy = RuleGovernor(
        "policy",
        (Rule("needs-human-review", lambda r, s: False, Outcome.ESCALATE, "policy review"),),
    )
    capability = RuleGovernor(
        "capability",
        (Rule("needs-human-review", lambda r, s: False, Outcome.ESCALATE, "capability review"),),
    )
    triumvirate = TriumvirateGovernor(
        name="triumvirate",
        governors=(safety, policy, capability),
        quorum=Quorum.MAJORITY,
    )
    governance = GovernanceEngine(policy_version="v1", governors=(triumvirate,))
    path = IronPath(
        spine=spine,
        governance=governance,
        threat_engine=None,
        tarl_gate=None,
        policy_version="v1",
    )
    result = path.run(request())
    # All three escalate → triumvirate (SUPERMAJORITY) denies; MAJORITY escalates.
    # We used MAJORITY → outcome is ESCALATE.
    assert result.outcome is Outcome.ESCALATE


def test_pipeline_blocks_on_invariant_before_governors_run() -> None:
    """BLOCKING invariant fires first; triumvirate is never consulted."""

    def blocking_invariant(
        _request: ActionRequest, _state: Mapping[str, object]
    ) -> InvariantViolation:
        return InvariantViolation("scope", "out-of-scope", InvariantSeverity.BLOCKING)

    spine = EventSpine(clock=lambda: TrustedClock().now())
    triumvirate = TriumvirateGovernor(
        name="triumvirate",
        governors=(
            RuleGovernor("a", ()),
            RuleGovernor("b", ()),
            RuleGovernor("c", ()),
        ),
    )
    from kernel import InvariantEngine

    governance = GovernanceEngine(
        policy_version="v1",
        governors=(triumvirate,),
        invariants=InvariantEngine((blocking_invariant,)),
    )
    path = IronPath(spine=spine, governance=governance, policy_version="v1")
    result = path.run(request())
    assert result.outcome is Outcome.DENY
    # Triumvirate did not produce a vote
    assert result.governance_result is not None
    assert result.governance_result.votes == ()


def test_pipeline_writes_to_audit_spine_for_every_action() -> None:
    """Every pipeline run must produce at least one audit event."""
    spine = EventSpine(clock=lambda: TrustedClock().now())
    threat_engine = ThreatDetectionEngine(spine)
    tarl = TarlGate(spine)
    triumvirate = TriumvirateGovernor(
        name="triumvirate",
        governors=(
            RuleGovernor("a", ()),
            RuleGovernor("b", ()),
            RuleGovernor("c", ()),
        ),
    )
    governance = GovernanceEngine(policy_version="v1", governors=(triumvirate,))
    path = IronPath(
        spine=spine,
        governance=governance,
        threat_engine=threat_engine,
        tarl_gate=tarl,
        policy_version="v1",
    )
    initial_events = len(spine.events())
    path.run(request(), threat_session="alice", threat_command="ls")
    final_events = len(spine.events())
    # Threat engine emits 1 event; tarl gate emits 1 event → at least 2
    assert final_events - initial_events >= 2


def test_pipeline_optional_components_can_be_disabled() -> None:
    """Iron Path with neither threat nor tarl still works (degraded mode)."""
    spine = EventSpine(clock=lambda: TrustedClock().now())
    triumvirate = TriumvirateGovernor(
        name="triumvirate",
        governors=(
            RuleGovernor("a", ()),
            RuleGovernor("b", ()),
            RuleGovernor("c", ()),
        ),
    )
    governance = GovernanceEngine(policy_version="v1", governors=(triumvirate,))
    path = IronPath(
        spine=spine,
        governance=governance,
        threat_engine=None,
        tarl_gate=None,
        policy_version="v1",
    )
    result = path.run(request())
    assert result.outcome is Outcome.ALLOW
    assert result.threat_assessment is None
    assert result.tarl_verdict is None


def test_pipeline_carries_request_identity_through_to_decision() -> None:
    """The decision's policy_version and the request's action_id are preserved."""
    path = build_full_pipeline()
    req = ActionRequest("a-trace-123", "operator", "delete", "record:sensitive")
    result = path.run(
        req,
        threat_session="operator",
        threat_command="ls /home",
    )
    assert result.request.action_id == "a-trace-123"
    assert result.request.actor == "operator"
    assert result.final_decision.policy_version == "iron-path-v1"
