import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: cerberus-containment-service / __init__.py
# ============================================================================ #
"""Separate from Triumvirate's rule evaluation — this is the enforcement layer. When Cerberus says deny, this service actually executes the containment. Rate limiting, circuit breaking, quarantine, isolation. The difference between a governance decision and a governance action."""
__version__ = "1.0.0"
