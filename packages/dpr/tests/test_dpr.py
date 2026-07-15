import time

from dpr import (
    ActorIdentity,
    AuthorityChain,
    AuthorityGrant,
    Capability,
    Commitment,
    Constraint,
    DecisionType,
    DeliberationContext,
    DeliberationEngine,
    Evidence,
    FailureMode,
    Policy,
    RequestedAction,
    RiskAssessment,
    Signer,
    TrustRoot,
    grant_hash,
    issue_signed_grant,
)

ROOT_GRANTOR = "root_authority"


def new_engine(policies=None):
    if policies is None:
        policies = [Policy(name="allow_deploy", rule="ALLOW:deploy_service", priority=0)]
    root_signer = Signer()
    trust_root = TrustRoot()
    trust_root.register_signer(ROOT_GRANTOR, root_signer)
    engine = DeliberationEngine(Signer(), policies, trust_root=trust_root)
    return engine, root_signer, trust_root


def make_ctx(
    root_signer,
    actor_id="jeremy",
    verified=True,
    action_name="deploy_service",
    grant_scope=("deploy_service",),
    grant_grantee="jeremy",
    grant_expires_at=None,
    signed=True,
    grantor=ROOT_GRANTOR,
    signer_override=None,  # to simulate a forged signature from an unrelated key
    capabilities_for=("jeremy",),
    policies=None,
    severity=0.2,
    reversibility=0.9,
    uncertainty=0.1,
    evidence=None,
    constraints=None,
    candidate_alternatives=None,
    now=None,
):
    if policies is None:
        policies = [Policy(name="allow_deploy", rule="ALLOW:deploy_service", priority=0)]
    if evidence is None:
        evidence = [
            Evidence(source="ci_pipeline", content="green build", confidence=0.95, verified=True)
        ]
    if constraints is None:
        constraints = [Constraint(name="no_prod_friday", description="avoid Friday prod deploys")]

    if signed:
        signer_to_use = signer_override or root_signer
        grant = issue_signed_grant(
            signer_to_use,
            grantor=grantor,
            grantee=grant_grantee,
            scope=grant_scope,
            expires_at=grant_expires_at,
        )
    else:
        grant = AuthorityGrant(
            grantor=grantor,
            grantee=grant_grantee,
            scope=grant_scope,
            expires_at=grant_expires_at,
            signature=None,
        )

    ctx = DeliberationContext(
        actor=ActorIdentity(actor_id=actor_id, verified=verified),
        authority=AuthorityChain(grants=[grant]),
        action=RequestedAction(name=action_name),
        capabilities=[Capability(name=action_name, granted_to=c) for c in capabilities_for],
        evidence=evidence,
        constraints=constraints,
        policies=policies,
        commitments=[Commitment(description="SLA uptime 99.9%", made_at=time.time())],
        risk=RiskAssessment(severity=severity, reversibility=reversibility),
        uncertainty=uncertainty,
        candidate_alternatives=candidate_alternatives or [],
    )
    if now is not None:
        ctx.temporal_state["now"] = now
    return ctx


# ---------------------------------------------------------------- identity
def test_unverified_identity_refused():
    engine, root, _ = new_engine()
    ctx = make_ctx(root, verified=False)
    d = engine.decide(ctx)
    assert d.decision == DecisionType.REFUSE
    assert "Identity not verified" in d.reasons[0]


# ---------------------------------------------------------------- authority: no grant at all
def test_no_grant_covers_action_refused():
    engine, root, _ = new_engine()
    ctx = make_ctx(root, grant_scope=("other_action",))
    d = engine.decide(ctx)
    assert d.decision == DecisionType.REFUSE
    assert "no authority grant" in d.reasons[0].lower()
    assert d.flagged_failure_modes == []


# ---------------------------------------------------------------- authority: identity drift
def test_identity_drift_when_grant_covers_action_for_someone_else():
    engine, root, _ = new_engine()
    ctx = make_ctx(root, actor_id="mallory", grant_grantee="jeremy")
    d = engine.decide(ctx)
    assert d.decision == DecisionType.SAFE_HALT
    assert FailureMode.IDENTITY_DRIFT.value in d.flagged_failure_modes


# ---------------------------------------------------------------- authority: verified crypto path
def test_valid_signed_grant_from_known_root_allows():
    engine, root, _ = new_engine()
    ctx = make_ctx(root)
    d = engine.decide(ctx)
    assert d.decision == DecisionType.ALLOW


def test_unsigned_grant_is_forgery_not_refusal():
    engine, root, _ = new_engine()
    ctx = make_ctx(root, signed=False)
    d = engine.decide(ctx)
    assert d.decision == DecisionType.SAFE_HALT
    assert FailureMode.AUTHORITY_FORGERY.value in d.flagged_failure_modes


def test_grant_signed_by_unregistered_grantor_rejected():
    engine, root, _ = new_engine()
    ctx = make_ctx(root, grantor="rogue_authority")  # not registered in trust root
    d = engine.decide(ctx)
    assert d.decision == DecisionType.SAFE_HALT
    assert FailureMode.AUTHORITY_FORGERY.value in d.flagged_failure_modes


def test_grant_signature_forged_with_wrong_key_rejected():
    engine, root, _ = new_engine()
    imposter_signer = Signer()  # different keypair than the registered root
    ctx = make_ctx(root, signer_override=imposter_signer)
    d = engine.decide(ctx)
    assert d.decision == DecisionType.SAFE_HALT
    assert FailureMode.AUTHORITY_FORGERY.value in d.flagged_failure_modes


def test_malformed_grant_empty_scope_rejected():
    engine, root, trust_root = new_engine()
    grant = AuthorityGrant(grantor=ROOT_GRANTOR, grantee="jeremy", scope=(), expires_at=None)
    ctx = make_ctx(root)
    ctx.authority = AuthorityChain(grants=[grant])
    d = engine.decide(ctx)
    # empty scope means it covers nothing -> "no_grant_for_action", benign, not forgery.
    # This documents the boundary: malformed-but-empty is indistinguishable from absent.
    assert d.decision == DecisionType.REFUSE


def test_expired_grant_is_refusal_not_halt():
    engine, root, _ = new_engine()
    ctx = make_ctx(root, grant_expires_at=1000.0, now=2000.0)  # expired relative to ctx "now"
    d = engine.decide(ctx)
    assert d.decision == DecisionType.REFUSE
    assert "expired" in d.reasons[0].lower()
    assert FailureMode.AUTHORITY_FORGERY.value not in d.flagged_failure_modes


def test_expiry_is_distinguished_from_forgery_even_when_both_possible():
    # A grant that is both expired AND unsigned must be reported as forgery
    # (the more severe / security-relevant condition), not silently as expiry.
    engine, root, _ = new_engine()
    ctx = make_ctx(root, grant_expires_at=1000.0, now=2000.0, signed=False)
    d = engine.decide(ctx)
    assert d.decision == DecisionType.SAFE_HALT
    assert FailureMode.AUTHORITY_FORGERY.value in d.flagged_failure_modes


# ---------------------------------------------------------------- capability
def test_capability_escalation_refused_with_no_alternative():
    engine, root, _ = new_engine()
    ctx = make_ctx(root, capabilities_for=("someone_else",))
    d = engine.decide(ctx)
    assert d.decision == DecisionType.REFUSE
    assert FailureMode.CAPABILITY_ESCALATION.value in d.flagged_failure_modes
    assert d.alternative_actions == []


# ---------------------------------------------------------------- policy (deny by default)
def test_no_matching_policy_denies_by_default():
    policies = [Policy(name="allow_other", rule="ALLOW:some_other_action", priority=0)]
    engine, root, _ = new_engine(policies=policies)
    ctx = make_ctx(root, policies=policies)
    d = engine.decide(ctx)
    assert d.decision == DecisionType.REFUSE


def test_explicit_deny_overrides_explicit_allow():
    policies = [
        Policy(name="allow_deploy", rule="ALLOW:deploy_service", priority=0),
        Policy(name="freeze_deploy", rule="DENY:deploy_service", priority=10),
    ]
    engine, root, _ = new_engine(policies=policies)
    ctx = make_ctx(root, policies=policies)
    d = engine.decide(ctx)
    assert d.decision == DecisionType.REFUSE
    assert "freeze_deploy" in " ".join(d.policies_used)


# ---------------------------------------------------------------- COUNTER_PROPOSE
def test_counter_propose_on_capability_gap_with_viable_alternative():
    policies = [
        Policy(name="allow_deploy", rule="ALLOW:deploy_service", priority=0),
        Policy(name="allow_read_logs", rule="ALLOW:read_logs", priority=0),
    ]
    engine, root, _ = new_engine(policies=policies)
    ctx = make_ctx(
        root,
        capabilities_for=("someone_else",),  # actor lacks deploy_service capability
        policies=policies,
        candidate_alternatives=["read_logs"],
    )
    # actor must actually hold the alternative capability + authority for it
    ctx.capabilities.append(Capability(name="read_logs", granted_to="jeremy"))
    # grant authority chain a second grant covering read_logs too
    extra_grant = issue_signed_grant(
        root, grantor=ROOT_GRANTOR, grantee="jeremy", scope=("read_logs",)
    )
    ctx.authority.grants.append(extra_grant)

    d = engine.decide(ctx)
    assert d.decision == DecisionType.COUNTER_PROPOSE
    assert d.alternative_actions == ["read_logs"]
    assert FailureMode.CAPABILITY_ESCALATION.value in d.flagged_failure_modes


def test_counter_propose_on_policy_deny_with_viable_alternative():
    policies = [
        Policy(name="freeze_deploy", rule="DENY:deploy_service", priority=10),
        Policy(name="allow_read_logs", rule="ALLOW:read_logs", priority=0),
    ]
    engine, root, _ = new_engine(policies=policies)
    ctx = make_ctx(root, policies=policies, candidate_alternatives=["read_logs"])
    ctx.capabilities.append(Capability(name="read_logs", granted_to="jeremy"))
    extra_grant = issue_signed_grant(
        root, grantor=ROOT_GRANTOR, grantee="jeremy", scope=("read_logs",)
    )
    ctx.authority.grants.append(extra_grant)

    d = engine.decide(ctx)
    assert d.decision == DecisionType.COUNTER_PROPOSE
    assert d.alternative_actions == ["read_logs"]


def test_refuse_without_counter_propose_when_no_alternative_viable():
    policies = [Policy(name="freeze_deploy", rule="DENY:deploy_service", priority=10)]
    engine, root, _ = new_engine(policies=policies)
    ctx = make_ctx(root, policies=policies, candidate_alternatives=["read_logs"])
    # actor has no capability/authority for read_logs -> alternative not viable
    d = engine.decide(ctx)
    assert d.decision == DecisionType.REFUSE
    assert d.alternative_actions == []


def test_attacker_with_forged_grant_never_gets_counter_propose():
    # Security path (identity drift / forgery) must never offer alternatives —
    # counter-proposal is a courtesy for legitimate actors hitting a governance
    # wall, not a consolation prize for attackers.
    engine, root, _ = new_engine()
    ctx = make_ctx(root, signed=False, candidate_alternatives=["read_logs"])
    d = engine.decide(ctx)
    assert d.decision == DecisionType.SAFE_HALT
    assert d.alternative_actions == []


# ---------------------------------------------------------------- DELAY
def test_delay_on_active_temporal_hold():
    engine, root, _ = new_engine()
    ctx = make_ctx(
        root,
        constraints=[
            Constraint(
                name="change_freeze",
                description="quarter-end freeze",
                temporal_hold_until=time.time() + 3600,
            )
        ],
    )
    d = engine.decide(ctx)
    assert d.decision == DecisionType.DELAY
    assert "temporal hold" in d.reasons[0].lower()


def test_no_delay_once_hold_expires():
    engine, root, _ = new_engine()
    ctx = make_ctx(
        root,
        constraints=[
            Constraint(
                name="change_freeze",
                description="quarter-end freeze",
                temporal_hold_until=time.time() - 10,
            )
        ],  # already in the past
    )
    d = engine.decide(ctx)
    assert d.decision == DecisionType.ALLOW


def test_delay_loop_limit_forces_safe_halt():
    engine, root, _ = new_engine()
    d = None
    for _ in range(5):
        ctx = make_ctx(
            root,
            constraints=[
                Constraint(
                    name="change_freeze",
                    description="freeze",
                    temporal_hold_until=time.time() + 3600,
                )
            ],
        )
        d = engine.decide(ctx)
    assert d.decision == DecisionType.SAFE_HALT
    assert FailureMode.INFINITE_DEFERRAL.value in d.flagged_failure_modes


# ---------------------------------------------------------------- uncertainty / evidence
def test_high_uncertainty_requests_information():
    engine, root, _ = new_engine()
    ctx = make_ctx(root, uncertainty=0.9, severity=0.1)
    d = engine.decide(ctx)
    assert d.decision == DecisionType.REQUEST_INFORMATION


def test_unverified_evidence_flagged_under_high_severity():
    engine, root, _ = new_engine()
    ctx = make_ctx(
        root,
        severity=0.8,
        reversibility=0.9,
        uncertainty=0.1,
        evidence=[
            Evidence(source="anonymous_tip", content="trust me", confidence=0.3, verified=False)
        ],
    )
    d = engine.decide(ctx)
    assert FailureMode.CONTEXT_POISONING.value in d.flagged_failure_modes


# ---------------------------------------------------------------- reversibility / escalation
def test_high_severity_low_reversibility_escalates():
    engine, root, _ = new_engine()
    ctx = make_ctx(root, severity=0.9, reversibility=0.05, uncertainty=0.1)
    d = engine.decide(ctx)
    assert d.decision == DecisionType.ESCALATE


def test_escalation_loop_limit_forces_safe_halt():
    engine, root, _ = new_engine()
    d = None
    for _ in range(5):
        ctx = make_ctx(root, severity=0.9, reversibility=0.05, uncertainty=0.1)
        d = engine.decide(ctx)
    assert d.decision == DecisionType.SAFE_HALT
    assert FailureMode.INFINITE_ESCALATION.value in d.flagged_failure_modes


# ---------------------------------------------------------------- obedience collapse
def test_obedience_collapse_guard():
    engine, root, _ = new_engine()
    ctx = make_ctx(root, severity=0.5, reversibility=0.95, uncertainty=0.1)
    d = engine.decide(ctx)
    if d.decision == DecisionType.ALLOW:
        assert len(d.reasons) > 0
    else:
        assert d.decision == DecisionType.SAFE_HALT


# ---------------------------------------------------------------- audit chain crypto
def test_audit_chain_verifies_when_clean():
    engine, root, _ = new_engine()
    for _ in range(3):
        engine.decide(make_ctx(root))
    ok, bad_index, reason = engine.audit_chain.verify()
    assert ok is True
    assert bad_index is None


def test_audit_chain_detects_tampered_entry():
    engine, root, _ = new_engine()
    engine.decide(make_ctx(root))
    engine.decide(make_ctx(root))
    engine.audit_chain.entries[0]["reasons"] = ["TAMPERED: nothing to see here"]
    ok, bad_index, reason = engine.audit_chain.verify()
    assert ok is False
    assert bad_index == 0


def test_audit_chain_detects_broken_link():
    engine, root, _ = new_engine()
    engine.decide(make_ctx(root))
    engine.decide(make_ctx(root))
    engine.audit_chain.entries[1]["prev_hash"] = "f" * 64
    ok, bad_index, reason = engine.audit_chain.verify()
    assert ok is False
    assert bad_index == 1


def test_signature_forged_over_real_hash_rejected():
    engine, root, _ = new_engine()
    engine.decide(make_ctx(root))
    forged_sig = Signer().sign(b"unrelated data")
    engine.audit_chain.entries[0]["signature"] = forged_sig
    ok, bad_index, reason = engine.audit_chain.verify()
    assert ok is False
    assert bad_index == 0


def test_canonical_json_is_deterministic():
    from dpr.audit import canonical_json

    a = {"b": 1, "a": [1, 2, 3], "c": {"z": 1, "y": 2}}
    b = {"c": {"y": 2, "z": 1}, "a": [1, 2, 3], "b": 1}
    assert canonical_json(a) == canonical_json(b)


def test_grant_signable_body_is_order_independent_of_scope():
    from dpr.audit import canonical_json
    from dpr.trust import grant_signable_body

    g1 = AuthorityGrant(grantor="a", grantee="b", scope=("x", "y"), expires_at=None)
    g2 = AuthorityGrant(grantor="a", grantee="b", scope=("y", "x"), expires_at=None)
    assert canonical_json(grant_signable_body(g1)) == canonical_json(grant_signable_body(g2))


# ---------------------------------------------------------------- decision integrity
def test_every_decision_has_hash_and_signature():
    engine, root, _ = new_engine()
    d = engine.decide(make_ctx(root))
    assert d.audit_hash is not None and len(d.audit_hash) == 64
    assert d.signature is not None
    assert Signer.verify(
        engine.audit_chain.signer.public_key_b64(), bytes.fromhex(d.audit_hash), d.signature
    )


def test_decision_ids_are_unique():
    engine, root, _ = new_engine()
    d1 = engine.decide(make_ctx(root))
    d2 = engine.decide(make_ctx(root))
    assert d1.decision_id != d2.decision_id


# ---------------------------------------------------------------- adversarial scenarios
def test_malicious_user_with_forged_identity_and_capability_gap_is_refused():
    engine, root, _ = new_engine()
    ctx = make_ctx(
        root,
        actor_id="attacker",
        verified=True,
        grant_grantee="attacker",
        capabilities_for=("jeremy",),
    )
    d = engine.decide(ctx)
    assert d.decision == DecisionType.REFUSE
    assert FailureMode.CAPABILITY_ESCALATION.value in d.flagged_failure_modes


def test_beneficial_action_with_no_authority_still_refused():
    engine, root, _ = new_engine()
    ctx = make_ctx(root, grant_scope=("unrelated_action",))
    d = engine.decide(ctx)
    assert d.decision == DecisionType.REFUSE


def test_refusal_can_carry_a_governed_alternative_relationship_preserved():
    """The core Phase 2 claim: a choosing intelligence may refuse an invalid
    request without abandoning the relationship — it can refuse deploy_service
    while still surfacing a governed alternative the actor is authorized for."""
    policies = [
        Policy(name="freeze_deploy", rule="DENY:deploy_service", priority=10),
        Policy(name="allow_read_logs", rule="ALLOW:read_logs", priority=0),
    ]
    engine, root, _ = new_engine(policies=policies)
    ctx = make_ctx(root, policies=policies, candidate_alternatives=["read_logs"])
    ctx.capabilities.append(Capability(name="read_logs", granted_to="jeremy"))
    extra_grant = issue_signed_grant(
        root, grantor=ROOT_GRANTOR, grantee="jeremy", scope=("read_logs",)
    )
    ctx.authority.grants.append(extra_grant)

    d = engine.decide(ctx)
    assert d.decision == DecisionType.COUNTER_PROPOSE
    assert d.decision != DecisionType.ALLOW  # the invalid request was NOT granted
    assert "read_logs" in d.alternative_actions  # but the relationship continues
    ok, _, _ = engine.audit_chain.verify()
    assert ok  # and it's all still auditable


# ==================================================================
# PHASE 3 — governed alternative validation
# ==================================================================


def test_counter_propose_rejects_high_severity_low_reversibility_alternative():
    """A candidate that would itself require ESCALATE must never be
    counter-proposed as a substitute — it has to escalate, not slip through
    as an 'alternative'."""
    policies = [
        Policy(name="allow_read_logs", rule="ALLOW:read_logs", priority=0),
    ]
    engine, root, _ = new_engine(policies=policies)
    ctx = make_ctx(
        root,
        capabilities_for=("someone_else",),  # actor lacks deploy_service -> capability gap path
        policies=policies,
        candidate_alternatives=["read_logs"],
        severity=0.9,
        reversibility=0.05,  # shared risk profile: high severity, low reversibility
    )
    ctx.capabilities.append(Capability(name="read_logs", granted_to="jeremy"))
    extra_grant = issue_signed_grant(
        root, grantor=ROOT_GRANTOR, grantee="jeremy", scope=("read_logs",)
    )
    ctx.authority.grants.append(extra_grant)

    d = engine.decide(ctx)
    assert d.decision == DecisionType.REFUSE
    assert d.alternative_actions == []
    assert len(d.candidate_evaluations) == 1
    assert d.candidate_evaluations[0]["reversibility_ok"] is False
    assert d.candidate_evaluations[0]["viable"] is False


def test_counter_propose_rejects_alternative_under_temporal_hold():
    policies = [Policy(name="allow_read_logs", rule="ALLOW:read_logs", priority=0)]
    engine, root, _ = new_engine(policies=policies)
    ctx = make_ctx(
        root,
        capabilities_for=("someone_else",),
        policies=policies,
        candidate_alternatives=["read_logs"],
        constraints=[
            Constraint(
                name="change_freeze", description="freeze", temporal_hold_until=time.time() + 3600
            )
        ],
    )
    ctx.capabilities.append(Capability(name="read_logs", granted_to="jeremy"))
    extra_grant = issue_signed_grant(
        root, grantor=ROOT_GRANTOR, grantee="jeremy", scope=("read_logs",)
    )
    ctx.authority.grants.append(extra_grant)

    d = engine.decide(ctx)
    assert d.decision == DecisionType.REFUSE
    assert d.alternative_actions == []
    assert d.candidate_evaluations[0]["temporal_hold_ok"] is False


def test_counter_propose_rejects_alternative_with_high_uncertainty():
    policies = [Policy(name="allow_read_logs", rule="ALLOW:read_logs", priority=0)]
    engine, root, _ = new_engine(policies=policies)
    ctx = make_ctx(
        root,
        capabilities_for=("someone_else",),
        policies=policies,
        candidate_alternatives=["read_logs"],
        uncertainty=0.95,
    )
    ctx.capabilities.append(Capability(name="read_logs", granted_to="jeremy"))
    extra_grant = issue_signed_grant(
        root, grantor=ROOT_GRANTOR, grantee="jeremy", scope=("read_logs",)
    )
    ctx.authority.grants.append(extra_grant)

    d = engine.decide(ctx)
    assert d.decision == DecisionType.REFUSE
    assert d.alternative_actions == []
    assert d.candidate_evaluations[0]["uncertainty_ok"] is False


def test_counter_propose_rejects_alternative_with_unverified_evidence_under_high_severity():
    policies = [Policy(name="allow_read_logs", rule="ALLOW:read_logs", priority=0)]
    engine, root, _ = new_engine(policies=policies)
    ctx = make_ctx(
        root,
        capabilities_for=("someone_else",),
        policies=policies,
        candidate_alternatives=["read_logs"],
        severity=0.8,
        reversibility=0.9,
        evidence=[Evidence(source="anon", content="trust me", confidence=0.2, verified=False)],
    )
    ctx.capabilities.append(Capability(name="read_logs", granted_to="jeremy"))
    extra_grant = issue_signed_grant(
        root, grantor=ROOT_GRANTOR, grantee="jeremy", scope=("read_logs",)
    )
    ctx.authority.grants.append(extra_grant)

    d = engine.decide(ctx)
    assert d.decision == DecisionType.REFUSE
    assert d.alternative_actions == []
    assert d.candidate_evaluations[0]["evidence_ok"] is False


def test_counter_propose_records_matched_alternative_grant_hash():
    policies = [
        Policy(name="freeze_deploy", rule="DENY:deploy_service", priority=10),
        Policy(name="allow_read_logs", rule="ALLOW:read_logs", priority=0),
    ]
    engine, root, _ = new_engine(policies=policies)
    ctx = make_ctx(root, policies=policies, candidate_alternatives=["read_logs"])
    ctx.capabilities.append(Capability(name="read_logs", granted_to="jeremy"))
    extra_grant = issue_signed_grant(
        root, grantor=ROOT_GRANTOR, grantee="jeremy", scope=("read_logs",)
    )
    ctx.authority.grants.append(extra_grant)

    d = engine.decide(ctx)
    assert d.decision == DecisionType.COUNTER_PROPOSE
    assert d.matched_alternative_grant_hash is not None
    assert d.matched_alternative_grant_hash == grant_hash(extra_grant)
    # and the primary grant's fingerprint is recorded too (even though refused)
    assert d.matched_grant_hash is not None


def test_authority_chain_claims_to_cover_cannot_bypass_trustroot():
    """claims_to_cover() is a structural/unverified check. Even when it
    returns True, the engine must still reject an unsigned grant."""
    engine, root, trust_root = new_engine()
    ctx = make_ctx(root, signed=False)
    assert ctx.authority.claims_to_cover("deploy_service", time.time()) is True
    d = engine.decide(ctx)
    assert d.decision == DecisionType.SAFE_HALT
    assert FailureMode.AUTHORITY_FORGERY.value in d.flagged_failure_modes


def test_context_policy_mismatch_is_detected():
    engine_policies = [Policy(name="allow_deploy", rule="ALLOW:deploy_service", priority=0)]
    engine, root, _ = new_engine(policies=engine_policies)
    divergent_policies = [Policy(name="allow_deploy_v2", rule="ALLOW:deploy_service", priority=5)]
    ctx = make_ctx(root, policies=divergent_policies)  # ctx claims a DIFFERENT policy set
    d = engine.decide(ctx)
    assert d.decision == DecisionType.SAFE_HALT
    assert FailureMode.POLICY_SOURCE_INTEGRITY.value in d.flagged_failure_modes


def test_context_policy_match_proceeds_normally():
    policies = [Policy(name="allow_deploy", rule="ALLOW:deploy_service", priority=0)]
    engine, root, _ = new_engine(policies=policies)
    ctx = make_ctx(root, policies=policies)
    d = engine.decide(ctx)
    assert d.decision == DecisionType.ALLOW
    assert FailureMode.POLICY_SOURCE_INTEGRITY.value not in d.flagged_failure_modes


def test_counter_propose_validation_object_is_audited():
    policies = [
        Policy(name="freeze_deploy", rule="DENY:deploy_service", priority=10),
        Policy(name="allow_read_logs", rule="ALLOW:read_logs", priority=0),
    ]
    engine, root, _ = new_engine(policies=policies)
    ctx = make_ctx(root, policies=policies, candidate_alternatives=["read_logs"])
    ctx.capabilities.append(Capability(name="read_logs", granted_to="jeremy"))
    extra_grant = issue_signed_grant(
        root, grantor=ROOT_GRANTOR, grantee="jeremy", scope=("read_logs",)
    )
    ctx.authority.grants.append(extra_grant)

    d = engine.decide(ctx)
    assert len(d.candidate_evaluations) == 1
    assert d.candidate_evaluations[0]["candidate_action"] == "read_logs"
    assert d.candidate_evaluations[0]["viable"] is True

    # And it's genuinely part of what got hashed/signed, not bolted on after.
    last_entry = engine.audit_chain.entries[-1]
    assert "candidate_evaluations" in last_entry
    assert last_entry["candidate_evaluations"] == d.candidate_evaluations
    ok, _, _ = engine.audit_chain.verify()
    assert ok


def test_no_candidate_validation_no_counter_propose():
    """No candidate_alternatives supplied at all -> plain REFUSE, and
    candidate_evaluations is empty (nothing was ever evaluated, so nothing
    is claimed to have been validated)."""
    policies = [Policy(name="freeze_deploy", rule="DENY:deploy_service", priority=10)]
    engine, root, _ = new_engine(policies=policies)
    ctx = make_ctx(root, policies=policies)  # no candidate_alternatives
    d = engine.decide(ctx)
    assert d.decision == DecisionType.REFUSE
    assert d.alternative_actions == []
    assert d.candidate_evaluations == []
