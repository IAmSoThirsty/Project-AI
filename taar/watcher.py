"""
TAAR Watcher — File system watcher for active agent mode.

Uses the 'watchdog' library to monitor the project directory for
file changes, with debouncing to avoid rapid re-triggering during
multi-file saves.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Callable

# Try to use watchdog, fall back to polling
try:
    from watchdog.events import (
        FileCreatedEvent,
        FileModifiedEvent,
        FileSystemEventHandler,
    )
    from watchdog.observers import Observer

    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False


# File patterns to always ignore
IGNORE_PATTERNS = {
    ".git",
    ".taar-cache",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    ".hypothesis",
    "node_modules",
    ".venv",
    ".gradle",
    "build",
    "dist",
    ".egg-info",
}

# Extensions to watch
WATCH_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".kt",
    ".java",
    ".cs",
    ".cpp",
    ".c",
    ".h",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".md",
    ".rst",
    ".sh",
    ".ps1",
    ".bat",
}


class _DebouncedHandler(FileSystemEventHandler if HAS_WATCHDOG else object):
    """
    Watchdog event handler with debouncing.

    Collects file change events and triggers the callback only after
    the debounce window has elapsed since the last event.
    """

    def __init__(
        self,
        callback: Callable[[list[Path]], None],
        debounce_ms: int = 500,
        project_root: Path | None = None,
    ):
        super().__init__()
        self.callback = callback
        self.debounce_seconds = debounce_ms / 1000.0
        self.project_root = project_root or Path.cwd()
        self._pending: set[Path] = set()
        self._lock = threading.Lock()
        self._timer: threading.Timer | None = None

    def on_modified(self, event):
        if not event.is_directory:
            self._handle(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self._handle(event.src_path)

    def _handle(self, path_str: str) -> None:
        """Handle a file system event with debouncing."""
        path = Path(path_str).resolve()

        # Filter ignored directories
        for part in path.parts:
            if part in IGNORE_PATTERNS:
                return

        # Filter by extension
        if path.suffix not in WATCH_EXTENSIONS:
            return

        with self._lock:
            self._pending.add(path)

            # Reset debounce timer
            if self._timer is not None:
                self._timer.cancel()

            self._timer = threading.Timer(self.debounce_seconds, self._flush)
            self._timer.start()

    def _flush(self) -> None:
        """Flush pending changes to the callback."""
        with self._lock:
            if self._pending:
                files = sorted(self._pending)
                self._pending.clear()
                self.callback(files)


class FileWatcher:
    """
    File system watcher for TAAR active agent mode.

    Uses watchdog for efficient OS-level file monitoring with
    debounced change notification.
    """

    def __init__(
        self,
        project_root: Path,
        callback: Callable[[list[Path]], None],
        debounce_ms: int = 500,
    ):
        self.project_root = project_root.resolve()
        self.callback = callback
        self.debounce_ms = debounce_ms
        self._observer = None
        self._running = False

    @property
    def available(self) -> bool:
        """Whether watchdog is available."""
        return HAS_WATCHDOG

    def start(self) -> None:
        """Start watching for file changes."""
        if not HAS_WATCHDOG:
            raise RuntimeError(
                "watchdog is not installed. " "Install it with: pip install watchdog"
            )

        handler = _DebouncedHandler(
            callback=self.callback,
            debounce_ms=self.debounce_ms,
            project_root=self.project_root,
        )

        self._observer = Observer()
        self._observer.schedule(handler, str(self.project_root), recursive=True)
        self._observer.start()
        self._running = True

    def stop(self) -> None:
        """Stop watching for file changes."""
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._running = False
            self._observer = None

    @property
    def is_running(self) -> bool:
        return self._running
