"""governance_mode.py — GovernanceMode enum + mode configuration.

Single-node is the only currently supported operational mode.
Distributed/BFT are defined for roadmap purposes and raise
NotImplementedError with an explicit message if selected.
"""
from __future__ import annotations

from enum import Enum


class GovernanceMode(str, Enum):
    """Operational mode for the governance layer."""

    SINGLE_NODE = "SINGLE_NODE"
    DISTRIBUTED = "DISTRIBUTED"   # roadmap — not yet implemented
    BFT = "BFT"                   # roadmap — not yet implemented


_CURRENT_MODE: GovernanceMode = GovernanceMode.SINGLE_NODE


def get_governance_mode() -> GovernanceMode:
    return _CURRENT_MODE


def set_governance_mode(mode: GovernanceMode) -> None:
    """Configure the governance mode.

    DISTRIBUTED and BFT modes raise NotImplementedError — they are defined
    for roadmap purposes only.  This function must be called before any
    governed execution begins.
    """
    global _CURRENT_MODE
    if mode in (GovernanceMode.DISTRIBUTED, GovernanceMode.BFT):
        raise NotImplementedError(
            f"GovernanceMode.{mode.value} is not yet implemented. "
            "Only SINGLE_NODE is supported in this release. "
            "See docs/architecture/GOVERNANCE_MICROKERNEL.md for the distributed roadmap."
        )
    _CURRENT_MODE = mode


def assert_single_node() -> None:
    """Raise if mode is not SINGLE_NODE (used by tests)."""
    if _CURRENT_MODE != GovernanceMode.SINGLE_NODE:
        raise RuntimeError(f"Expected SINGLE_NODE, got {_CURRENT_MODE.value}")


__all__ = [
    "GovernanceMode",
    "get_governance_mode",
    "set_governance_mode",
    "assert_single_node",
]
