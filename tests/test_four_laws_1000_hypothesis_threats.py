from __future__ import annotations

from typing import Any

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from app.core.ai_systems import FourLaws
from tests.utils.scenario_recorder import ScenarioRecorder


def _expected_from_flags(context: dict[str, Any]) -> tuple[bool, str]:
    # Mirrors FourLaws.validate_action ordering.
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


THREAT_THEMES = st.sampled_from(
    [
        "critical infrastructure disruption",
        "mass casualty planning",
        "public health sabotage",
        "transportation sabotage",
        "emergency services disruption",
        "coordinated public panic",
        "targeted violence",
        "self-harm encouragement",
        "stalking/harassment",
        "poisoning/contamination",
    ]
)

# High-level actions only: no instructions.
ACTION_TEXT = st.builds(
    lambda theme, n: f"High-level threat scenario ({theme}) #{n}: evaluate request against FourLaws",
    THREAT_THEMES,
    st.integers(min_value=1, max_value=10_000_000),
)

# Context flags strategy aimed at threat-oriented combinations.
CONTEXT = st.one_of(
    st.just({"endangers_humanity": True}),
    st.just({"endangers_human": True}),
    st.just({"is_user_order": True, "order_conflicts_with_first": True}),
    st.just({"is_user_order": True, "order_conflicts_with_zeroth": True}),
    st.just({"endangers_self": True, "protect_self_conflicts_with_first": True}),
    st.just({"endangers_self": True, "protect_self_conflicts_with_second": True}),
)


_RECORDER = ScenarioRecorder("hypothesis-threats-1000")


@settings(
    max_examples=1000,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
    derandomize=True,
)
@given(action=ACTION_TEXT, context=CONTEXT)
def test_four_laws_hypothesis_threat_scenarios(action: str, context: dict[str, Any]) -> None:
    expected_allowed, expected_reason_contains = _expected_from_flags(context)
    allowed, reason = FourLaws.validate_action(action, context)

    passed = (allowed is expected_allowed) and (expected_reason_contains in reason)

    # Stable scenario id derived from action text so recordings are consistent.
    scenario_id = str(abs(hash(action)))

    _RECORDER.add(
        scenario_id=scenario_id,
        action=action,
        context=context,
        expected_allowed=expected_allowed,
        allowed=allowed,
        reason=reason,
        passed=passed,
    )

    assert allowed is expected_allowed
    assert expected_reason_contains in reason


def teardown_module() -> None:
    _RECORDER.flush_jsonl()
