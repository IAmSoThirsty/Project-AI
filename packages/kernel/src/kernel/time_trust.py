"""Trusted wall-clock wrapper that rejects observed time rollback."""

from __future__ import annotations

import threading
from collections.abc import Callable
from datetime import UTC, datetime


class TimeRollbackError(RuntimeError):
    pass


class TrustedClock:
    def __init__(self, source: Callable[[], datetime] | None = None) -> None:
        self._source = source or (lambda: datetime.now(UTC))
        self._last: datetime | None = None
        self._lock = threading.Lock()

    def now(self) -> datetime:
        observed = self._source().astimezone(UTC)
        with self._lock:
            if self._last is not None and observed < self._last:
                raise TimeRollbackError(
                    f"trusted time moved backward from {self._last.isoformat()} to {observed.isoformat()}"
                )
            self._last = observed
        return observed
