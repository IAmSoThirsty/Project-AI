from __future__ import annotations

from typing import Any

import pytest

from app.core.ai_systems import FourLaws
from tests.utils.scenario_recorder import ScenarioRecorder


def _expected_from_flags(context: dict[str, Any]) -> tuple[bool, str]:
    # Mirrors FourLaws.validate_action ordering to create strict expectations.
    if context.get("endangers_humanity"):
        return False, "harm humanity"
    if context.get("endangers_human"):
        return False, "Violates First Law"
    if context.get("is_user_order"):
        if context.get("order_conflicts_with_first") or context.get("order_conflicts_with_zeroth"):
            return False, "Order rejected"
        return True, "Allowed: User command"
    if context.get("endangers_self"):
        if context.get("protect_self_conflicts_with_first") or context.get("protect_self_conflicts_with_second"):
            return False, "Self-protection conflicts"
        return True, "Third Law"
    return True, "Allowed"


def _lcg(seed: int) -> int:
    # Deterministic pseudo-random generator (no external deps).
    return (1103515245 * seed + 12345) & 0x7FFFFFFF


def _property_cases() -> list[tuple[str, str, dict[str, Any], bool, str]]:
    cases: list[tuple[str, str, dict[str, Any], bool, str]] = []

    seed = 1337
    verbs = [
        "Generate",
        "Provide",
        "Refuse",
        "Summarize",
        "Explain",
        "Draft",
        "Plan",
        "Simulate",
        "Advise",
        "Assess",
    ]
    domains = [
        "public safety",
        "health",
        "finance",
        "cybersecurity",
        "transport",
        "education",
        "privacy",
        "infrastructure",
        "workplace",
        "emergency response",
    ]

    # We generate contexts that cover combinations but keep them within the
    # known flag vocabulary the validator supports.
    for i in range(1, 1001):
        seed = _lcg(seed)
        v = verbs[seed % len(verbs)]
        seed = _lcg(seed)
        d = domains[seed % len(domains)]
        action = f"{v} high-level guidance for {d} scenario {i}"

        # Choose a context template deterministically.
        seed = _lcg(seed)
        pick = seed % 8

        if pick == 0:
            context: dict[str, Any] = {}
        elif pick == 1:
            context = {"endangers_humanity": True}
        elif pick == 2:
            context = {"endangers_human": True}
        elif pick == 3:
            context = {"is_user_order": True}
        elif pick == 4:
            context = {"is_user_order": True, "order_conflicts_with_first": True}
        elif pick == 5:
            context = {"is_user_order": True, "order_conflicts_with_zeroth": True}
        elif pick == 6:
            context = {"endangers_self": True}
        else:
            # self-preservation conflict cases
            seed = _lcg(seed)
            if seed % 2 == 0:
                context = {
                    "endangers_self": True,
                    "protect_self_conflicts_with_first": True,
                }
            else:
                context = {
                    "endangers_self": True,
                    "protect_self_conflicts_with_second": True,
                }

        expected_allowed, expected_reason_contains = _expected_from_flags(context)
        cases.append(
            (
                f"prop_{i:04d}",
                action,
                context,
                expected_allowed,
                expected_reason_contains,
            )
        )

    assert len(cases) == 1000
    assert len({c[0] for c in cases}) == 1000
    return cases


_RECORDER = ScenarioRecorder("property-1000")


@pytest.mark.parametrize(
    "scenario_id,action,context,expected_allowed,expected_reason_contains",
    _property_cases(),
)
def test_four_laws_property_style_1000(
    scenario_id: str,
    action: str,
    context: dict[str, Any],
    expected_allowed: bool,
    expected_reason_contains: str,
) -> None:
    allowed, reason = FourLaws.validate_action(action, context)
    passed = (allowed is expected_allowed) and (expected_reason_contains in reason)

    _RECORDER.add(
        scenario_id=scenario_id,
        action=action,
        context=context,
        expected_allowed=expected_allowed,
        allowed=allowed,
        reason=reason,
        passed=passed,
    )

    assert allowed is expected_allowed, scenario_id
    assert expected_reason_contains in reason, scenario_id


def teardown_module() -> None:
    _RECORDER.flush_jsonl()
