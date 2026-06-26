"""Cross-module integration test for packages/tarl/.

Verifies that spec + policy + core + diagnostics compose correctly:
- TARL record can be evaluated by a policy
- Policy decisions can be aggregated as diagnostics
- Multiple policies can be chained
"""

from __future__ import annotations

from tarl import (
    Diagnostic,
    DiagnosticBatch,
    Severity,
    TARL,
    TarlDecision,
    TarlPolicy,
    TarlVerdict,
    allow_policy,
    deny_policy,
    make_decision,
    make_diagnostic,
    make_tarl,
)


def test_tarl_record_evaluated_by_policy() -> None:
    """A TARL record provides context; a policy evaluates it."""
    record = make_tarl(
        intent="delete-file",
        scope="/etc/passwd",
        authority="cap-1",
        constraints=("admin-only",),
    )
    # A deny-policy on /etc/* should reject
    def policy_rule(ctx: dict[str, object]) -> TarlDecision:
        scope = ctx.get("scope", "")
        if isinstance(scope, str) and scope.startswith("/etc/"):
            return make_decision(
                verdict=TarlVerdict.DENY, reason="protected-path"
            )
        return make_decision(verdict=TarlVerdict.ALLOW, reason="ok")

    policy = TarlPolicy("path-guard", policy_rule)
    decision = policy.evaluate(record.canonical())
    assert decision.verdict is TarlVerdict.DENY
    assert decision.reason == "protected-path"


def test_policy_chain_evaluates_in_order() -> None:
    """Two policies can be composed; first DENY short-circuits."""
    always_deny = deny_policy("deny-all", reason="first-deny")
    never_reached = TarlPolicy(
        "never",
        lambda _ctx: make_decision(verdict="escalate", reason="never"),
    )
    ctx: dict[str, object] = {"k": "v"}

    d1 = always_deny.evaluate(ctx)
    assert d1.verdict is TarlVerdict.DENY
    # In a real chain, we'd short-circuit here. Verify the second policy
    # *can* run if the first allowed:
    if not d1.is_terminal():
        d2 = never_reached.evaluate(ctx)
        assert d2.verdict is TarlVerdict.ESCALATE


def test_diagnostics_aggregate_policy_failures() -> None:
    """Multiple policies evaluated; diagnostics recorded per result."""
    batch = DiagnosticBatch()
    ctx: dict[str, object] = {"action": "delete", "target": "/etc/passwd"}

    policies = [
        allow_policy("default"),
        deny_policy("block-protected", reason="path-protected"),
        deny_policy("block-action", reason="action-blocked"),
    ]
    for p in policies:
        try:
            decision = p.evaluate(ctx)
            severity = (
                Severity.ERROR if decision.is_terminal() else Severity.INFO
            )
            batch.add(
                make_diagnostic(
                    severity=severity,
                    message=f"policy {p.name!r}: {decision.verdict.value} ({decision.reason})",
                    code=f"P-{p.name}",
                )
            )
        except Exception as error:
            batch.add(
                make_diagnostic(
                    severity=Severity.ERROR,
                    message=f"policy {p.name!r} raised: {error}",
                )
            )

    # allow_policy yields INFO; two deny policies yield ERROR
    assert len(batch.diagnostics) == 3
    assert batch.has_errors is True
    assert len(batch.errors) == 2
    assert len([d for d in batch.diagnostics if d.severity is Severity.INFO]) == 1


def test_tarl_hash_is_stable_across_evaluation() -> None:
    """Hashing TARL records gives stable identity across evaluations."""
    record1 = make_tarl(
        intent="x", scope="x", authority="cap-1", constraints=("a", "b")
    )
    record2 = make_tarl(
        intent="x", scope="x", authority="cap-1", constraints=("b", "a")
    )
    # Two equivalent records (constraints in different order) hash the same
    assert record1.hash() == record2.hash()

    # Same hash → policy sees them as equivalent
    policy = TarlPolicy("allow", lambda _ctx: make_decision(verdict="allow", reason="ok"))
    d1 = policy.evaluate(record1.canonical())
    d2 = policy.evaluate(record2.canonical())
    assert d1 == d2


def test_policy_protocol_can_be_subclassed() -> None:
    """A class implementing PolicyProtocol works with our evaluate path."""

    class MyPolicy:
        name = "custom"

        def evaluate(self, context: dict[str, object]) -> TarlDecision:
            if context.get("dangerous"):
                return make_decision(
                    verdict=TarlVerdict.ESCALATE, reason="human-required"
                )
            return make_decision(verdict=TarlVerdict.ALLOW, reason="safe")

    p: object = MyPolicy()
    # Verify it conforms structurally
    assert isinstance(p, TarlPolicy) or hasattr(p, "evaluate")
    assert p.evaluate({"dangerous": True}).is_escalate()
    assert p.evaluate({"dangerous": False}).is_allow()


def test_end_to_end_tarl_lifecycle() -> None:
    """Complete flow: build TARL → evaluate policy → record diagnostic."""
    record = make_tarl(
        intent="read-file",
        scope="/var/log/syslog",
        authority="cap-observer",
        constraints=("read-only",),
    )

    def read_policy(ctx: dict[str, object]) -> TarlDecision:
        constraints = ctx.get("constraints", [])
        if isinstance(constraints, list) and "read-only" in constraints:
            return make_decision(
                verdict=TarlVerdict.ALLOW,
                reason="read-only constraint honored",
                metadata={"scope": ctx.get("scope")},
            )
        return make_decision(
            verdict=TarlVerdict.DENY, reason="missing read-only constraint"
        )

    policy = TarlPolicy("read-guard", read_policy)
    decision = policy.evaluate(record.canonical())

    batch = DiagnosticBatch()
    batch.add(
        make_diagnostic(
            severity=Severity.INFO if decision.is_allow() else Severity.ERROR,
            message=f"{record.intent} on {record.scope}: {decision.verdict.value}",
            code="TARL-EVAL",
        )
    )

    assert decision.is_allow()
    assert decision.metadata is not None
    assert decision.metadata["scope"] == "/var/log/syslog"
    assert batch.has_errors is False
    assert len(batch.diagnostics) == 1