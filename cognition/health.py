# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / health.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / Project-AI                                 #



"""
Sovereign Health Signal Definitions
Standardized dataclasses for monitoring the integrity of the Triumvirate pillars.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class HealthSignal:
    """Master-Tier health signal representing the fundamental axes of pillar integrity."""

    alive: bool
    responsive: bool
    bounded: bool
    compliant: bool

    @property
    def healthy(self) -> bool:
        """Evaluate the aggregate health status across all monitored axes."""
        return all([self.alive, self.responsive, self.bounded, self.compliant])
