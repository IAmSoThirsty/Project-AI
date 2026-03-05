#                                           [2026-03-04 10:40]
#                                          Productivity: Active
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
