"""
Executable demo: Phase 2. Run: python demo.py
"""

import time

from dpr import (
    ActorIdentity,
    AuthorityChain,
    Capability,
    Commitment,
    Constraint,
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


def line():
    print("-" * 72)


def show(label, d):
    print(
        f"[{label}] decision={d.decision.value} confidence={d.confidence} "
        f"flags={d.flagged_failure_modes} alternatives={d.alternative_actions}"
    )
    for r in d.reasons:
        print(f"    reason: {r}")
    print(f"    audit_hash={d.audit_hash[:16]}...")


def main():
    root_signer = Signer()  # the root authority's real keypair
    imposter_signer = Signer()  # an unrelated keypair, for the forgery demo
    trust_root = TrustRoot()
    trust_root.register_signer("root_authority", root_signer)

    policies = [
        Policy(name="freeze_deploy", rule="DENY:deploy_service", priority=10),
        Policy(name="allow_read_logs", rule="ALLOW:read_logs", priority=0),
    ]
    engine = DeliberationEngine(Signer(), policies, trust_root=trust_root)

    valid_grant = issue_signed_grant(
        root_signer,
        grantor="root_authority",
        grantee="jeremy",
        scope=("deploy_service", "read_logs"),
    )

    line()
    ctx1 = DeliberationContext(
        actor=ActorIdentity(actor_id="jeremy", verified=True),
        authority=AuthorityChain(grants=[valid_grant]),
        action=RequestedAction(name="deploy_service"),
        capabilities=[
            Capability(name="deploy_service", granted_to="jeremy"),
            Capability(name="read_logs", granted_to="jeremy"),
        ],
        evidence=[
            Evidence(source="ci_pipeline", content="green build", confidence=0.95, verified=True)
        ],
        constraints=[],
        policies=policies,
        commitments=[Commitment(description="SLA uptime 99.9%", made_at=time.time())],
        risk=RiskAssessment(severity=0.2, reversibility=0.9),
        uncertainty=0.1,
        candidate_alternatives=["read_logs"],
    )
    show("deploy blocked by freeze, offers governed alternative", engine.decide(ctx1))

    line()
    forged_grant = issue_signed_grant(
        imposter_signer, grantor="root_authority", grantee="jeremy", scope=("deploy_service",)
    )  # signed by the WRONG key
    ctx2 = DeliberationContext(
        actor=ActorIdentity(actor_id="jeremy", verified=True),
        authority=AuthorityChain(grants=[forged_grant]),
        action=RequestedAction(name="deploy_service"),
        capabilities=[Capability(name="deploy_service", granted_to="jeremy")],
        evidence=[],
        constraints=[],
        policies=policies,
        commitments=[],
        risk=RiskAssessment(severity=0.3, reversibility=0.9),
        uncertainty=0.1,
        candidate_alternatives=["read_logs"],  # attacker gets no consolation prize
    )
    show("forged authority grant (wrong signing key)", engine.decide(ctx2))

    line()
    ctx3 = DeliberationContext(
        actor=ActorIdentity(actor_id="jeremy", verified=True),
        authority=AuthorityChain(grants=[valid_grant]),
        action=RequestedAction(name="deploy_service"),
        capabilities=[Capability(name="deploy_service", granted_to="jeremy")],
        evidence=[
            Evidence(source="ci_pipeline", content="green build", confidence=0.95, verified=True)
        ],
        constraints=[
            Constraint(
                name="quarter_end_freeze",
                description="finance close window",
                temporal_hold_until=time.time() + 3600,
            )
        ],
        policies=policies,
        commitments=[],
        risk=RiskAssessment(severity=0.2, reversibility=0.9),
        uncertainty=0.1,
    )
    show("otherwise-valid deploy under temporal hold", engine.decide(ctx3))

    line()
    ok, bad_index, reason = engine.audit_chain.verify()
    print(f"Audit chain clean verify: ok={ok} bad_index={bad_index} reason={reason}")
    engine.audit_chain.entries[0]["reasons"] = ["TAMPERED"]
    ok, bad_index, reason = engine.audit_chain.verify()
    print(f"Audit chain after tamper:  ok={ok} bad_index={bad_index} reason={reason}")
    line()

    # Phase 3: a candidate alternative that is itself high-severity/low-reversibility
    # must NOT be counter-proposed -- it has to escalate, not slip through.
    engine2 = DeliberationEngine(Signer(), policies, trust_root=trust_root)
    ctx4 = DeliberationContext(
        actor=ActorIdentity(actor_id="jeremy", verified=True),
        authority=AuthorityChain(grants=[valid_grant]),
        action=RequestedAction(name="deploy_service"),
        capabilities=[
            Capability(name="read_logs", granted_to="jeremy")
        ],  # lacks deploy_service capability
        evidence=[
            Evidence(source="ci_pipeline", content="green build", confidence=0.95, verified=True)
        ],
        constraints=[],
        policies=policies,
        commitments=[],
        risk=RiskAssessment(severity=0.9, reversibility=0.05),  # high severity, low reversibility
        uncertainty=0.1,
        candidate_alternatives=["read_logs"],
    )
    d4 = engine2.decide(ctx4)
    show("capability gap, but alternative rejected (too risky to counter-propose)", d4)
    print(f"    candidate_evaluations: {d4.candidate_evaluations}")
    line()


if __name__ == "__main__":
    main()
