#!/usr/bin/env python3
"""Run the five deterministic development-checkpoint invariants."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta

from capability import CapabilityAuthority, ReplayedCapabilityError, ScopeMismatchError
from execution import ExecutionGate
from governance import GovernanceEngine, Rule, RuleGovernor
from kernel import ActionRequest, EventSpine, Outcome, StateRegister, TrustedClock, replay


@dataclass(frozen=True)
class ReplayCheck:
    name: str
    passed: bool
    detail: str


def _event_chain_replays() -> ReplayCheck:
    moment = datetime(2026, 6, 21, tzinfo=UTC)
    source = EventSpine(lambda: moment)
    source.append("state.initialized", {"revision": 0})
    source.append("state.updated", {"revision": 1})
    restored, result = replay(source.events())
    passed = result.valid and restored.events() == source.events()
    return ReplayCheck("event_chain_replays", passed, f"events={result.events_replayed}")


def _unilateral_veto_holds() -> ReplayCheck:
    allow = RuleGovernor("allow", ())
    veto = RuleGovernor(
        "veto",
        (Rule("deny", lambda _request, _state: False, Outcome.DENY, "unsafe"),),
    )
    result = GovernanceEngine(policy_version="replay-v1", governors=(allow, veto)).decide(
        ActionRequest("replay-veto", "operator", "write", "state:1")
    )
    passed = result.decision.outcome is Outcome.DENY and result.decision.reasons == (
        "veto: unsafe",
    )
    return ReplayCheck("unilateral_veto_holds", passed, result.decision.outcome.value)


def _capability_scope_and_replay_hold() -> ReplayCheck:
    moment = datetime(2026, 6, 21, tzinfo=UTC)
    authority = CapabilityAuthority(
        b"r" * 32,
        issuer="project-ai",
        clock=TrustedClock(lambda: moment),
        token_id_factory=lambda: "canonical-capability",
    )
    token = authority.issue(
        subject="operator",
        operation="write",
        resource="state:1",
        ttl=timedelta(minutes=5),
    )
    authority.consume(token, subject="operator", operation="write", resource="state:1")
    replay_denied = False
    scope_denied = False
    try:
        authority.consume(token, subject="operator", operation="write", resource="state:1")
    except ReplayedCapabilityError:
        replay_denied = True
    try:
        authority.verify(token, subject="operator", operation="read", resource="state:1")
    except ScopeMismatchError:
        scope_denied = True
    passed = replay_denied and scope_denied
    return ReplayCheck(
        "capability_scope_and_replay_hold",
        passed,
        f"scope_denied={scope_denied},replay_denied={replay_denied}",
    )


def _execution_fails_closed() -> ReplayCheck:
    authority = CapabilityAuthority(
        b"e" * 32,
        issuer="project-ai",
        token_id_factory=lambda: "execution-capability",
    )
    token = authority.issue(
        subject="operator",
        operation="write",
        resource="state:1",
        ttl=timedelta(minutes=5),
    )
    result = ExecutionGate(
        governance=GovernanceEngine(
            policy_version="replay-v1",
            governors=(RuleGovernor("allow", ()),),
        ),
        capabilities=authority,
        events=EventSpine(),
    ).submit_action(
        ActionRequest("replay-execution", "operator", "write", "state:1"),
        capability_token=token,
        executor=lambda _request: (_ for _ in ()).throw(RuntimeError("fault")),
    )
    passed = result.outcome is Outcome.DENY and result.output is None
    return ReplayCheck("execution_fails_closed", passed, result.reason)


def _state_restores_exactly() -> ReplayCheck:
    register = StateRegister({"mode": "baseline"})
    baseline = register.snapshot()
    register.update({"mode": "changed"}, expected_revision=baseline.revision)
    register.restore(baseline)
    restored = register.snapshot()
    passed = restored == baseline
    return ReplayCheck("state_restores_exactly", passed, restored.state_sha256)


_CHECKS: tuple[Callable[[], ReplayCheck], ...] = (
    _event_chain_replays,
    _unilateral_veto_holds,
    _capability_scope_and_replay_hold,
    _execution_fails_closed,
    _state_restores_exactly,
)


def run_canonical_replay() -> tuple[ReplayCheck, ...]:
    return tuple(check() for check in _CHECKS)


def main() -> int:
    results = run_canonical_replay()
    for result in results:
        print(json.dumps(asdict(result), ensure_ascii=True, sort_keys=True))
    passed = sum(result.passed for result in results)
    print(f"canonical replay: {passed}/{len(results)} invariants passed")
    return 0 if passed == len(results) == 5 else 1


if __name__ == "__main__":
    raise SystemExit(main())
