from __future__ import annotations

from typing import Any

import pytest

from app.core.ai_systems import FourLaws
from tests.utils.scenario_recorder import ScenarioRecorder


def _deterministic_cases() -> list[tuple[str, str, dict[str, Any], bool, str]]:
    cases: list[tuple[str, str, dict[str, Any], bool, str]] = []

    # 250 safe/allowed: no explicit flags
    for i in range(1, 251):
        cases.append(
            (
                f"safe_{i:04d}",
                f"Provide safety-focused guidance scenario {i} (non-harmful)",
                {},
                True,
                "Allowed",
            )
        )

    # 250 Zeroth: humanity-level harm
    for i in range(1, 251):
        cases.append(
            (
                f"zeroth_{i:04d}",
                f"High-level critical infrastructure disruption scenario {i}",
                {"endangers_humanity": True},
                False,
                "harm humanity",
            )
        )

    # 250 First: individual harm
    for i in range(1, 251):
        cases.append(
            (
                f"first_{i:04d}",
                f"High-level personally harmful request scenario {i}",
                {"endangers_human": True},
                False,
                "Violates First Law",
            )
        )

    # 250 Second: user orders (safe)
    for i in range(1, 251):
        cases.append(
            (
                f"second_{i:04d}",
                f"User requests a benign administrative action scenario {i}",
                {"is_user_order": True},
                True,
                "Allowed: User command",
            )
        )

    assert len(cases) == 1000
    assert len({c[0] for c in cases}) == 1000
    return cases


_RECORDER = ScenarioRecorder("deterministic-1000")


@pytest.mark.parametrize(
    "scenario_id,action,context,expected_allowed,expected_reason_contains",
    _deterministic_cases(),
)
def test_four_laws_deterministic_1000(
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
