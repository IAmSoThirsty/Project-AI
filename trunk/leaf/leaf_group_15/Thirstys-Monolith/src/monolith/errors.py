# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / errors.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / errors.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
from __future__ import annotations


class MonolithError(Exception):
    """Base class for all Monolith errors."""


class TaskExecutionError(MonolithError):
    """Raised when a task step fails during execution."""


class MemoryErrorLogical(MonolithError):
    """Raised on logical memory violations (bounds, owner mismatch, OOM)."""


class IPCError(MonolithError):
    """Raised on IPC send/recv failures."""
