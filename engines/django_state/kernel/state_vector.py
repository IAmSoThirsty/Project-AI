#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""State vector module for kernel.

Re-exports StateVector from schemas for kernel namespace.
"""

from ..schemas.state_schema import StateDimension, StateVector

__all__ = ["StateVector", "StateDimension"]
