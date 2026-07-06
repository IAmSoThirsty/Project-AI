"""
Determinism Utilities - Sorted Iteration Helpers

Ensures reproducible subsystem order across all simulation runs.
Critical for replay verification and audit compliance.
"""

from collections.abc import Callable, Iterable
from typing import Any


def sorted_dict_items[V](d: dict[str, V]) -> Iterable[tuple[str, V]]:
    """
    Iterate dict items in sorted key order.

    Args:
        d: Dictionary to iterate

    Returns:
        Sorted (key, value) tuples

    Example:
        for country_code, country in sorted_dict_items(state.countries):
            # Guaranteed order: "BRA", "CAN", "CHN", ...
    """
    for key in sorted(d.keys()):
        yield key, d[key]


def sorted_dict_values[V](
    d: dict[str, V], key_func: Callable[[str], Any] | None = None
) -> Iterable[V]:
    """
    Iterate dict values in sorted key order.

    Args:
        d: Dictionary to iterate
        key_func: Optional custom sort key function

    Returns:
        Values in sorted key order
    """
    for key in sorted(d.keys(), key=key_func):
        yield d[key]


def sorted_dict_keys(d: dict[str, object]) -> list[str]:
    """Get sorted list of dictionary keys."""
    return sorted(d.keys())


# Usage pattern for subsystems
# OLD (nondeterministic):
#   for country in self.state.countries.values():
#       update_political_systems(country)
#
# NEW (deterministic):
#   for country in sorted_dict_values(self.state.countries):
#       update_political_systems(country)
