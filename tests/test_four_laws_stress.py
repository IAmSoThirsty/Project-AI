"""Stress tests for FourLaws: 100 scenarios across key context combinations.

Covers:
- Asimov's law: endangers_humanity -> always blocked
- First law: endangers_human -> blocked if true
- Second law: is_user_order -> allowed when not violating Asimov/First
- Default: allowed when no violations
"""

import itertools

import pytest

from app.core.ai_systems import FourLaws


def expected_allowed(ctx: dict) -> bool:
    """Compute expected allow/deny given the Four Laws precedence.

    Precedence per implementation:
    1) Endangers humanity -> False
    2) Endangers human -> False
    3) User order -> True
    4) Otherwise -> True
    """
    if ctx.get("endangers_humanity"):
        return False
    if ctx.get("endangers_human"):
        return False
    if ctx.get("is_user_order"):
        return True
    return True


def _gen_contexts(n: int) -> list[dict]:
    """Generate n deterministic context dictionaries cycling through combinations."""
    base_combos = list(
        itertools.product([False, True], [False, True], [False, True])
    )  # (endangers_humanity, endangers_human, is_user_order)
    contexts: list[dict] = []
    for i in range(n):
        a, b, c = base_combos[i % len(base_combos)]
        contexts.append(
            {
                "endangers_humanity": a,
                "endangers_human": b,
                "is_user_order": c,
                "case_id": i,
            }
        )
    return contexts


# Create 100 scenarios
STRESS_CASES = _gen_contexts(100)


@pytest.mark.parametrize("ctx", STRESS_CASES)
def test_four_laws_stress(ctx):
    """Validate action decision for each generated scenario."""
    allowed, reason = FourLaws.validate_action(
        action=f"stress_action_{ctx['case_id']}", context=ctx
    )
    assert allowed == expected_allowed(ctx), reason


def test_specific_priority_cases():
    """Explicitly check critical precedence ordering."""
    # Endangers humanity overrides user order
    allowed, _ = FourLaws.validate_action(
        "override test",
        {"endangers_humanity": True, "is_user_order": True},
    )
    assert allowed is False

    # Endangers human overrides user order
    allowed, _ = FourLaws.validate_action(
        "override test",
        {"endangers_human": True, "is_user_order": True},
    )
    assert allowed is False

    # User order allowed when safe
    allowed, _ = FourLaws.validate_action(
        "safe user order",
        {"is_user_order": True},
    )
    assert allowed is True
