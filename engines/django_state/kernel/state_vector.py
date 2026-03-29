# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / state_vector.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / state_vector.py

#
# COMPLIANCE: Sovereign Substrate / state_vector.py


"""State vector module for kernel.

Re-exports StateVector from schemas for kernel namespace.
"""

from ..schemas.state_schema import StateDimension, StateVector

__all__ = ["StateVector", "StateDimension"]
