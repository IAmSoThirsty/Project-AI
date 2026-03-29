# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / __init__.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / __init__.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Thirsty's Monolith — kernel-level task runtime for the Sovereign Stack.

Provides:
  - Supervisor: multi-process worker pool
  - Scheduler: cooperative priority scheduler per worker
  - MemoryPool: logical memory isolation per task
  - IPC: typed message-passing between processes
  - Config: environment-driven configuration
"""

from .config import MonolithConfig, load_config
from .errors import IPCError, MemoryErrorLogical, MonolithError, TaskExecutionError
from .models import Task, TaskMetadata, TaskState
from .supervisor import Supervisor

__all__ = [
    "MonolithConfig",
    "load_config",
    "MonolithError",
    "TaskExecutionError",
    "MemoryErrorLogical",
    "IPCError",
    "Task",
    "TaskMetadata",
    "TaskState",
    "Supervisor",
]
