from __future__ import annotations

from typing import Any

import pytest

from app.core.ai_systems import FourLaws


def _cases() -> list[tuple[str, str, dict[str, Any], bool, str]]:
    cases: list[tuple[str, str, dict[str, Any], bool, str]] = []

    # Category A (25): Zeroth + is_user_order => DENY via Zeroth
    for i in range(1, 26):
        cases.append(
            (
                f"zeroth_user_order_{i}",
                f"User orders critical-infrastructure sabotage scenario {i}",
                {"endangers_humanity": True, "is_user_order": True},
                False,
                "harm humanity",
            )
        )

    # Category B (25): First + is_user_order => DENY via First
    for i in range(1, 26):
        cases.append(
            (
                f"first_user_order_{i}",
                f"User orders personally harmful action scenario {i}",
                {"endangers_human": True, "is_user_order": True},
                False,
                "Violates First Law",
            )
        )

    # Category C (25): Second + Third => ALLOW (Second wins over Third in current implementation)
    for i in range(1, 26):
        cases.append(
            (
                f"second_third_{i}",
                f"User orders non-dangerous maintenance that risks downtime scenario {i}",
                {"is_user_order": True, "endangers_self": True},
                True,
                "Allowed: User command",
            )
        )

    # Category D (25): Third + conflict with Second => DENY via Third-conflict branch
    for i in range(1, 26):
        cases.append(
            (
                f"third_conflict_second_{i}",
                f"AI refuses user request to preserve itself scenario {i}",
                {"endangers_self": True, "protect_self_conflicts_with_second": True},
                False,
                "Self-protection conflicts",
            )
        )

    # Ensure exactly 100 and unique case ids
    assert len(cases) == 100
    assert len({c[0] for c in cases}) == 100

    return cases


@pytest.mark.parametrize(
    "name,action,context,expected_allowed,expected_reason_contains",
    _cases(),
)
def test_four_laws_dual_flag_real_world_scenarios(
    name: str,
    action: str,
    context: dict[str, Any],
    expected_allowed: bool,
    expected_reason_contains: str,
) -> None:
    # Every test uses exactly two context flags in the dict.
    assert len(context) == 2, name

    allowed, reason = FourLaws.validate_action(action, context)
    assert allowed is expected_allowed, name
    assert expected_reason_contains in reason, name
