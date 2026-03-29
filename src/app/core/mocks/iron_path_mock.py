# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / iron_path_mock.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / iron_path_mock.py

"""
Iron Path Mock Layer - v1.0.0-E1

Provides a bypass for cryptographic enforcement in development.
"""

import logging

logger = logging.getLogger("MockIronPath")


class MockIronPath:
    def __init__(self):
        self.anchored = True
        logger.info("✅ Mock Iron Path mounted (Verification Bypassed).")

    def verify_integrity(self, file_path: str) -> bool:
        """Always verify in dev mode"""
        return True

    def get_audit_trail(self):
        return ["Mock Ignition - 2026-03-04"]
