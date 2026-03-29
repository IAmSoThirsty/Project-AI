# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / temporal_reasoning.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / temporal_reasoning.py

#
# COMPLIANCE: Sovereign Substrate / Temporal Weight Engine for Project-AI.



"""
Temporal Weight Engine for Project-AI.

Translates elapsed duration between user sessions into weighted cognitive context.
Bridges the gap between raw timestamps (last_accessed) and the state register.

Logic:
- Short deltas (seconds/minutes) -> High continuity weight (1.0)
- Medium deltas (hours) -> Context stabilization weight (0.8 - 0.9)
- Long deltas (days) -> Context decay/recall weight (0.4 - 0.7)
- Extreme deltas (weeks+) -> "Rebirth" re-orientation weight (< 0.3)
"""

import logging
import datetime
try:
    UTC = datetime.UTC
except AttributeError:
    UTC = datetime.timezone.utc
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class TemporalWeightEngine:
    """
    Calculates contextual weights based on time deltas.
    Used to adjust the AI's cognitive state based on interaction lapses.
    """

    def __init__(self):
        # Weighting thresholds in seconds
        self.CONTINUITY_THRESHOLD = 300       # 5 minutes
        self.STABILIZATION_THRESHOLD = 14400  # 4 hours
        self.DECAY_THRESHOLD = 86400         # 1 day
        self.ORIENTATION_THRESHOLD = 604800   # 1 week

    def calculate_weight(self, last_accessed_iso: str) -> float:
        """
        Calculates a weight between 0.0 and 1.0 based on elapsed time.
        """
        try:
            last_accessed = datetime.fromisoformat(last_accessed_iso)
            if last_accessed.tzinfo is None:
                last_accessed = last_accessed.replace(tzinfo=UTC)

            now = datetime.now(UTC)
            delta = (now - last_accessed).total_seconds()

            if delta <= self.CONTINUITY_THRESHOLD:
                return 1.0
            elif delta <= self.STABILIZATION_THRESHOLD:
                # Linear scale from 1.0 to 0.8
                return 1.0 - (0.2 * (delta / self.STABILIZATION_THRESHOLD))
            elif delta <= self.DECAY_THRESHOLD:
                # Linear scale from 0.8 to 0.5
                return 0.8 - (0.3 * (delta / self.DECAY_THRESHOLD))
            elif delta <= self.ORIENTATION_THRESHOLD:
                # Linear scale from 0.5 to 0.2
                return 0.5 - (0.3 * (delta / self.ORIENTATION_THRESHOLD))
            else:
                return 0.1  # Minimal baseline weight

        except Exception as e:
            logger.error("Failed to calculate temporal weight: %s", e)
            return 0.5  # Default "uncertain" weight

    def get_contextual_state(self, last_accessed_iso: str) -> dict[str, Any]:
        """
        Provides a structured state update based on temporal analysis.
        """
        weight = self.calculate_weight(last_accessed_iso)

        if weight >= 0.9:
            status = "CONTINUOUS"
        elif weight >= 0.7:
            status = "STABILIZED"
        elif weight >= 0.4:
            status = "RECALL_REQUIRED"
        else:
            status = "REORIENTATION_REQUIRED"

        return {
            "temporal_weight": weight,
            "session_continuity": status,
            "timestamp": datetime.now(UTC).isoformat()
        }
