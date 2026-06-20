"""Ordered severity levels for invariant violations."""

from enum import IntEnum


class InvariantSeverity(IntEnum):
    INFO = 10
    WARNING = 20
    BLOCKING = 30
    CRITICAL = 40
