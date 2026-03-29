# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / governance_mock.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / governance_mock.py

"""
Governance Mock Layer - v1.0.0-E1

Provides a zero-latency mock for development environments.
"""

import logging

logger = logging.getLogger("MockGovernance")


class MockGovernance:
    def __init__(self):
        self.status = "ACTIVE_MOCK"
        logger.info("✅ Mock Governance Layer online.")

    def check_policy(self, action: str) -> bool:
        """Always allow in dev mode"""
        logger.debug("[Mock] Policy check for '%s': ALLOWED", action)
        return True

    def get_status(self):
        return {"mode": "DEVELOPER", "governance": "MOCKED"}
