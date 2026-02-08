"""
Death accounting helpers for EMP Defense Engine.

Ensures consistent death tracking across all systems.
Every death must be categorized and totaled correctly.
"""

from engines.emp_defense.modules.sectorized_state import SectorizedWorldState


def record_deaths_starvation(state: SectorizedWorldState, count: int) -> None:
    """
    Record starvation deaths with proper accounting.

    Args:
        state: World state to update
        count: Number of starvation deaths
    """
    if count < 0:
        raise ValueError(f"Death count cannot be negative: {count}")

    state.deaths_starvation += count
    state.total_deaths += count
    state.global_population = max(0, state.global_population - count)


def record_deaths_disease(state: SectorizedWorldState, count: int) -> None:
    """
    Record disease deaths with proper accounting.

    Args:
        state: World state to update
        count: Number of disease deaths
    """
    if count < 0:
        raise ValueError(f"Death count cannot be negative: {count}")

    state.deaths_disease += count
    state.total_deaths += count
    state.global_population = max(0, state.global_population - count)


def record_deaths_violence(state: SectorizedWorldState, count: int) -> None:
    """
    Record violence deaths with proper accounting.

    Args:
        state: World state to update
        count: Number of violence deaths
    """
    if count < 0:
        raise ValueError(f"Death count cannot be negative: {count}")

    state.deaths_violence += count
    state.total_deaths += count
    state.global_population = max(0, state.global_population - count)


def record_deaths_exposure(state: SectorizedWorldState, count: int) -> None:
    """
    Record exposure/radiation deaths with proper accounting.

    Args:
        state: World state to update
        count: Number of exposure deaths
    """
    if count < 0:
        raise ValueError(f"Death count cannot be negative: {count}")

    state.deaths_exposure += count
    state.total_deaths += count
    state.global_population = max(0, state.global_population - count)


def record_deaths_other(state: SectorizedWorldState, count: int) -> None:
    """
    Record other deaths (accidents, executions, etc.) with proper accounting.

    Args:
        state: World state to update
        count: Number of other deaths
    """
    if count < 0:
        raise ValueError(f"Death count cannot be negative: {count}")

    state.deaths_other += count
    state.total_deaths += count
    state.global_population = max(0, state.global_population - count)


def validate_death_accounting(state: SectorizedWorldState) -> tuple[bool, str]:
    """
    Validate that death accounting is consistent.

    Invariant: total_deaths = sum(all death categories)

    Args:
        state: World state to validate

    Returns:
        (valid, message) tuple

    Examples:
        >>> state = SectorizedWorldState()
        >>> state.total_deaths = 100
        >>> state.deaths_starvation = 50
        >>> state.deaths_disease = 30
        >>> state.deaths_violence = 20
        >>> validate_death_accounting(state)
        (True, 'Death accounting valid')

        >>> state.total_deaths = 150  # Wrong!
        >>> validate_death_accounting(state)
        (False, 'Death mismatch: total=150, sum_categories=100')
    """
    sum_categories = (
        state.deaths_starvation
        + state.deaths_disease
        + state.deaths_violence
        + state.deaths_exposure
        + state.deaths_other
    )

    if state.total_deaths != sum_categories:
        return (
            False,
            f"Death mismatch: total={state.total_deaths}, sum_categories={sum_categories}",
        )

    # Also validate population accounting
    expected_pop = 8_000_000_000 - state.total_deaths
    if state.global_population != expected_pop and state.global_population > 0:
        return (
            False,
            f"Population mismatch: current={state.global_population}, expected={expected_pop}",
        )

    return True, "Death accounting valid"


def get_death_breakdown(state: SectorizedWorldState) -> dict[str, int | float]:
    """
    Get comprehensive death statistics.

    Args:
        state: World state to analyze

    Returns:
        Dictionary with death breakdown and percentages
    """
    if state.total_deaths == 0:
        return {
            "total_deaths": 0,
            "deaths_by_cause": {
                "starvation": 0,
                "disease": 0,
                "violence": 0,
                "exposure": 0,
                "other": 0,
            },
            "percentages": {
                "starvation": 0.0,
                "disease": 0.0,
                "violence": 0.0,
                "exposure": 0.0,
                "other": 0.0,
            },
            "mortality_rate": 0.0,
        }

    return {
        "total_deaths": state.total_deaths,
        "deaths_by_cause": {
            "starvation": state.deaths_starvation,
            "disease": state.deaths_disease,
            "violence": state.deaths_violence,
            "exposure": state.deaths_exposure,
            "other": state.deaths_other,
        },
        "percentages": {
            "starvation": (state.deaths_starvation / state.total_deaths) * 100,
            "disease": (state.deaths_disease / state.total_deaths) * 100,
            "violence": (state.deaths_violence / state.total_deaths) * 100,
            "exposure": (state.deaths_exposure / state.total_deaths) * 100,
            "other": (state.deaths_other / state.total_deaths) * 100,
        },
        "mortality_rate": (state.total_deaths / 8_000_000_000) * 100,
    }
