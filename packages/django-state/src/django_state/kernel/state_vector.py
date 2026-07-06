"""State vector module for kernel.

Re-exports StateVector from schemas for kernel namespace.
"""

from django_state.schemas.state_schema import StateDimension, StateVector

__all__ = ["StateDimension", "StateVector"]


# Port provenance (J2 scenario engine port)
