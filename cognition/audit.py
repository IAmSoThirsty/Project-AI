# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / audit.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / Project-AI                                 #



"""
Sovereign Accountability Ledger (Audit)
Records critical substrate events to the governance plane.
"""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Resolve log path relative to the cognition directory
AUDIT_LOG_DIR = Path(__file__).parent.parent / "governance"
AUDIT_LOG = AUDIT_LOG_DIR / "governance_audit.log"


def audit(event: str, detail: Any | None = None) -> None:
    """Record a critical event to the Sovereign Audit Ledger."""
    timestamp = datetime.now(UTC).isoformat()
    log_entry = f"{timestamp} | {event} | {detail}\n"

    try:
        AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except OSError as e:
        # Emergency fallback to stderr if ledger is unreachable
        import sys

        print(f"CRITICAL: Ledger unreachable: {e}", file=sys.stderr)
