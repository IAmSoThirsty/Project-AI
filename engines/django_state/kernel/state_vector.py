#                                           [2026-03-05 10:03]
#                                          Productivity: Active
"""State vector module for kernel.

Re-exports StateVector from schemas for kernel namespace.
"""

from ..schemas.state_schema import StateDimension, StateVector

__all__ = ["StateVector", "StateDimension"]
