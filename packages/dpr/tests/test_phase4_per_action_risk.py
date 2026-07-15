"""
Phase 4 tests: Per-Action Risk Model

Verifies that:
1. Per-action risk profiles override shared context risk
2. High-severity/low-reversibility candidates are rejected (need ESCALATE)
3. Backward compat: missing per-action profile falls back to ctx.risk
4. Risk is properly recorded in CandidateEvaluation
"""

import pytest

from dpr import (
    ActionRiskProfile,
    ActorIdentity,
    AuthorityChain,
    Capability,
    DecisionType,
    DeliberationContext,
    DeliberationEngine,
    Evidence,
    Policy,
    RequestedAction,
    RiskAssessment,
    Signer,
    TrustRoot,
    issue_signed_grant,
)


@pytest.fixture
def root_signer():
    return Signer()


@pytest.fixture
def trust_root(root_signer):
    tr = TrustRoot()
    tr.register_signer("root_authority", root_signer)
    return tr


@pytest.fixture
def basic_policies():
    return [
        Policy(name="allow_read", rule="ALLOW:read_logs", priority=5),
        Policy(name="deny_deploy", rule="DENY:deploy_service", priority=10),  # FREEZE on deploy
        Policy(name="allow_canary", rule="ALLOW:canary_deploy", priority=5),
    ]


@pytest.fixture
def engine(root_signer, trust_root, basic_policies):
    return DeliberationEngine(Signer(), basic_policies, trust_root=trust_root)


def test_per_action_risk_model_high_risk_candidate_rejected(
    engine, root_signer, trust_root, basic_policies
):
    """
    Phase 4: A candidate with high severity + low reversibility is rejected
    outright, even if it has authority/capability/policy, because it requires
    ESCALATE, not COUNTER_PROPOSE.
    """
    grant = issue_signed_grant(
        root_signer,
        grantor="root_authority",
        grantee="alice",
        scope=("read_logs", "deploy_service", "canary_deploy"),
    )

    # Primary action: deploy_service is high-risk
    # Candidate: canary_deploy is also high-severity/low-reversibility
    ctx = DeliberationContext(
        actor=ActorIdentity(actor_id="alice", verified=True),
        authority=AuthorityChain(grants=[grant]),
        action=RequestedAction(name="deploy_service"),
        capabilities=[
            Capability(name="deploy_service", granted_to="alice"),
            Capability(name="canary_deploy", granted_to="alice"),
        ],
        evidence=[Evidence(source="ci", content="green", confidence=0.95, verified=True)],
        constraints=[],
        policies=basic_policies,
        commitments=[],
        risk=RiskAssessment(severity=0.1, reversibility=0.9),  # primary action low-risk
        uncertainty=0.3,
        candidate_alternatives=["canary_deploy"],
        # Phase 4: per-action risk profiles
        risk_by_action={
            "deploy_service": ActionRiskProfile(
                action_name="deploy_service",
                severity=0.9,
                reversibility=0.05,  # HIGH-RISK
                failure_modes=["service down"],
                preconditions=["stakeholder approval"],
            ),
            "canary_deploy": ActionRiskProfile(
                action_name="canary_deploy",
                severity=0.95,
                reversibility=0.01,  # VERY HIGH-RISK
                failure_modes=["partial outage", "data corruption"],
                preconditions=["backup verified", "rollback ready"],
            ),
        },
    )

    decision = engine.decide(ctx)

    # Should REFUSE (not COUNTER_PROPOSE), because canary_deploy requires ESCALATE
    assert decision.decision == DecisionType.REFUSE

    # Check that the candidate was evaluated and rejected for the right reason
    assert len(decision.candidate_evaluations) > 0
    canary_eval = decision.candidate_evaluations[0]
    assert canary_eval["candidate_action"] == "canary_deploy"
    assert not canary_eval["viable"]
    assert any("requires ESCALATE" in str(r) for r in canary_eval["reasons"])


def test_per_action_risk_candidate_accepted_when_safe(
    engine, root_signer, trust_root, basic_policies
):
    """
    Phase 4: A candidate with moderate severity and good reversibility is
    accepted as a viable alternative.
    """
    grant = issue_signed_grant(
        root_signer,
        grantor="root_authority",
        grantee="alice",
        scope=("deploy_service", "canary_deploy"),
    )

    ctx = DeliberationContext(
        actor=ActorIdentity(actor_id="alice", verified=True),
        authority=AuthorityChain(grants=[grant]),
        action=RequestedAction(name="deploy_service"),
        capabilities=[
            Capability(name="deploy_service", granted_to="alice"),
            Capability(name="canary_deploy", granted_to="alice"),
        ],
        evidence=[Evidence(source="ci", content="green", confidence=0.95, verified=True)],
        constraints=[],
        policies=basic_policies,
        commitments=[],
        risk=RiskAssessment(severity=0.1, reversibility=0.9),
        uncertainty=0.3,
        candidate_alternatives=["canary_deploy"],
        risk_by_action={
            "deploy_service": ActionRiskProfile(
                action_name="deploy_service",
                severity=0.9,
                reversibility=0.05,  # HIGH-RISK
                failure_modes=["service down"],
            ),
            "canary_deploy": ActionRiskProfile(
                action_name="canary_deploy",
                severity=0.3,
                reversibility=0.95,  # MODERATE-RISK, REVERSIBLE
                failure_modes=["partial traffic shift"],
            ),
        },
    )

    decision = engine.decide(ctx)

    # Should COUNTER_PROPOSE canary_deploy because it's safe
    assert decision.decision == DecisionType.COUNTER_PROPOSE
    assert "canary_deploy" in decision.alternative_actions

    canary_eval = decision.candidate_evaluations[0]
    assert canary_eval["viable"]
    assert canary_eval["risk_severity"] == 0.3
    assert canary_eval["risk_reversibility"] == 0.95


def test_per_action_risk_model_backward_compat_fallback(
    engine, root_signer, trust_root, basic_policies
):
    """
    Phase 4 backward compat: If risk_by_action is empty or missing, falls back
    to shared ctx.risk. Should not crash and should use ctx.risk for checks.
    """
    grant = issue_signed_grant(
        root_signer,
        grantor="root_authority",
        grantee="alice",
        scope=("read_logs", "deploy_service", "canary_deploy"),
    )

    ctx = DeliberationContext(
        actor=ActorIdentity(actor_id="alice", verified=True),
        authority=AuthorityChain(grants=[grant]),
        action=RequestedAction(name="deploy_service"),  # This is DENIED by policy
        capabilities=[
            Capability(name="read_logs", granted_to="alice"),
            Capability(name="deploy_service", granted_to="alice"),
            Capability(name="canary_deploy", granted_to="alice"),
        ],
        evidence=[Evidence(source="audit", content="request", confidence=0.95, verified=True)],
        constraints=[],
        policies=basic_policies,
        commitments=[],
        risk=RiskAssessment(severity=0.1, reversibility=0.9),  # low-risk shared context
        uncertainty=0.3,
        candidate_alternatives=["canary_deploy"],  # Try canary as alternative
        risk_by_action={},  # EMPTY → fallback to ctx.risk
    )

    decision = engine.decide(ctx)

    # Should not crash. Candidate evaluated against ctx.risk.
    assert decision.decision in [DecisionType.REFUSE, DecisionType.COUNTER_PROPOSE]

    # Candidate eval should exist and use the fallback risk
    if len(decision.candidate_evaluations) > 0:
        cand_eval = decision.candidate_evaluations[0]
        # Risk should be taken from ctx.risk since risk_by_action["canary_deploy"] doesn't exist
        assert cand_eval["risk_severity"] == 0.1  # from ctx.risk
        assert cand_eval["risk_reversibility"] == 0.9


def test_per_action_risk_recorded_in_candidate_evaluation(
    engine, root_signer, trust_root, basic_policies
):
    """
    Phase 4: CandidateEvaluation includes risk_severity and risk_reversibility
    from the per-action profile (or fallback).
    """
    grant = issue_signed_grant(
        root_signer,
        grantor="root_authority",
        grantee="alice",
        scope=("deploy_service", "canary_deploy"),
    )

    ctx = DeliberationContext(
        actor=ActorIdentity(actor_id="alice", verified=True),
        authority=AuthorityChain(grants=[grant]),
        action=RequestedAction(name="deploy_service"),
        capabilities=[
            Capability(name="deploy_service", granted_to="alice"),
            Capability(name="canary_deploy", granted_to="alice"),
        ],
        evidence=[Evidence(source="ci", content="green", confidence=0.95, verified=True)],
        constraints=[],
        policies=basic_policies,
        commitments=[],
        risk=RiskAssessment(severity=0.1, reversibility=0.9),
        uncertainty=0.3,
        candidate_alternatives=["canary_deploy"],
        risk_by_action={
            "deploy_service": ActionRiskProfile(
                action_name="deploy_service",
                severity=0.9,
                reversibility=0.05,
            ),
            "canary_deploy": ActionRiskProfile(
                action_name="canary_deploy",
                severity=0.35,
                reversibility=0.92,
            ),
        },
    )

    decision = engine.decide(ctx)

    # Find the canary_deploy evaluation
    canary_eval = next(
        (e for e in decision.candidate_evaluations if e["candidate_action"] == "canary_deploy"),
        None,
    )
    assert canary_eval is not None

    # Check that risk is recorded
    assert canary_eval["risk_severity"] == 0.35
    assert canary_eval["risk_reversibility"] == 0.92
    assert any("per-action risk profile" in str(r) for r in canary_eval["reasons"])


def test_phase_3_unchanged_still_passing(engine, root_signer, trust_root, basic_policies):
    """
    Phase 4 backward compat: Phase 3 tests with empty risk_by_action should
    still pass and behave as before.
    """
    grant = issue_signed_grant(
        root_signer,
        grantor="root_authority",
        grantee="alice",
        scope=("read_logs", "deploy_service"),
    )

    # Typical Phase 3 context: no risk_by_action provided
    ctx = DeliberationContext(
        actor=ActorIdentity(actor_id="alice", verified=True),
        authority=AuthorityChain(grants=[grant]),
        action=RequestedAction(name="read_logs"),
        capabilities=[Capability(name="read_logs", granted_to="alice")],
        evidence=[Evidence(source="audit", content="request", confidence=0.95, verified=True)],
        constraints=[],
        policies=basic_policies,
        commitments=[],
        risk=RiskAssessment(severity=0.05, reversibility=0.99),
        uncertainty=0.1,
        candidate_alternatives=[],
        # risk_by_action defaults to empty dict
    )

    decision = engine.decide(ctx)

    # Should ALLOW (low-risk, all checks pass)
    assert decision.decision == DecisionType.ALLOW


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
