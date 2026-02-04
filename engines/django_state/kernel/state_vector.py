"""State vector module for kernel.

Re-exports StateVector from schemas for kernel namespace.
"""

from ..schemas.state_schema import StateVector, StateDimension

__all__ = ["StateVector", "StateDimension"]
