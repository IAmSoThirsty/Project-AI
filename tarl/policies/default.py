from tarl.policy import TarlPolicy
from tarl.spec import TarlDecision, TarlVerdict


def deny_unauthorized_mutation(ctx):
    if ctx.get("mutation") and not ctx.get("mutation_allowed"):
        return TarlDecision(
            verdict=TarlVerdict.DENY,
            reason="Mutation not permitted by TARL policy",
            metadata={"policy": "deny_unauthorized_mutation"},
        )
    return TarlDecision(TarlVerdict.ALLOW, "OK")


def escalate_on_unknown_agent(ctx):
    if ctx.get("agent") is None:
        return TarlDecision(
            verdict=TarlVerdict.ESCALATE,
            reason="Unknown agent identity",
            metadata={"policy": "escalate_on_unknown_agent"},
        )
    return TarlDecision(TarlVerdict.ALLOW, "OK")


DEFAULT_POLICIES = [
    TarlPolicy("deny_unauthorized_mutation", deny_unauthorized_mutation),
    TarlPolicy("escalate_on_unknown_agent", escalate_on_unknown_agent),
]
