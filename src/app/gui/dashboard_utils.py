"""Dashboard utilities for error handling and async operations."""

import asyncio
import logging
from collections.abc import Callable
from typing import Any

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)


class DashboardErrorHandler:
    """Centralized error handling for dashboard operations."""

    @staticmethod
    def handle_exception(
        exception: Exception,
        context: str = "Operation",
        show_dialog: bool = True,
        parent=None,
    ) -> None:
        """Handle an exception with logging and optional dialog."""
        error_message = f"{context}: {str(exception)}"
        logger.error(error_message, exc_info=True)

        if show_dialog:
            QMessageBox.critical(parent, "Error", error_message)

    @staticmethod
    def handle_warning(
        message: str,
        context: str = "Warning",
        show_dialog: bool = False,
        parent=None,
    ) -> None:
        """Handle a warning with logging and optional dialog."""
        logger.warning("%s: %s", context, message)
        if show_dialog:
            QMessageBox.warning(parent, context, message)

    @staticmethod
    def validate_input(
        value: Any,
        input_type: type,
        required: bool = True,
        context: str = "Input",
    ) -> bool:
        """Validate user input."""
        if required and (value is None or value == ""):
            DashboardErrorHandler.handle_warning(f"{context} is required", context)
            return False

        if value is not None and not isinstance(value, input_type):
            DashboardErrorHandler.handle_warning(
                f"{context} must be {input_type.__name__}",
                context,
            )
            return False

        return True


class AsyncWorker(QRunnable):
    """Worker thread for async operations."""

    class Signals(QObject):
        """Signals for AsyncWorker."""

        finished = pyqtSignal()
        error = pyqtSignal(Exception)
        result = pyqtSignal(object)

    def __init__(self, func: Callable, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = self.Signals()

    def run(self):
        """Run the async function."""
        try:
            result = self.func(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            logger.error("AsyncWorker error: %s", e)
            self.signals.error.emit(e)
        finally:
            self.signals.finished.emit()


class DashboardAsyncManager:
    """Manager for async operations in dashboard."""

    def __init__(self):
        """Initialize async manager."""
        self.thread_pool = QThreadPool()
        self.active_tasks = {}

    def run_async(
        self,
        task_id: str,
        func: Callable,
        on_result: Callable | None = None,
        on_error: Callable | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Run a function asynchronously in thread pool."""
        worker = AsyncWorker(func, *args, **kwargs)

        if on_result:
            worker.signals.result.connect(on_result)
        if on_error:
            worker.signals.error.connect(on_error)

        def on_finished():
            self.active_tasks.pop(task_id, None)
            logger.debug("Async task %s finished", task_id)

        worker.signals.finished.connect(on_finished)
        self.active_tasks[task_id] = worker
        self.thread_pool.start(worker)
        logger.debug("Started async task %s", task_id)

    def wait_for_task(self, task_id: str, timeout_ms: int = 5000) -> bool:
        """Wait for a specific task to complete."""
        start_time = 0
        while task_id in self.active_tasks:
            if start_time > timeout_ms:
                logger.warning("Task %s timeout after %sms", task_id, timeout_ms)
                return False
            asyncio.sleep(0.1)
            start_time += 100
        return True

    def cancel_all_tasks(self) -> None:
        """Cancel all active tasks."""
        self.thread_pool.clear()
        self.active_tasks.clear()
        logger.info("All async tasks cancelled")


class DashboardValidationManager:
    """Manager for input validation and sanitization."""

    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """Validate username format."""
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters"
        if len(username) > 50:
            return False, "Username must be less than 50 characters"
        if not username.replace("_", "").replace("-", "").isalnum():
            return False, "Username can only contain alphanumeric characters, - and _"
        return True, ""

    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """Validate email format."""
        if "@" not in email or "." not in email:
            return False, "Invalid email format"
        local, domain = email.rsplit("@", 1)
        if not local or not domain or "." not in domain:
            return False, "Invalid email format"
        return True, ""

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validate password strength."""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if not any(c.isupper() for c in password):
            return False, "Password must contain uppercase letter"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain digit"
        return True, ""

    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input."""
        if not value:
            return ""
        # Remove control characters
        cleaned = "".join(char for char in value if ord(char) >= 32 or char == "\n")
        # Limit length
        return cleaned[:max_length]


class DashboardLogger:
    """Enhanced logging for dashboard operations."""

    def __init__(self, name: str = "Dashboard"):
        """Initialize logger."""
        self.logger = logging.getLogger(name)

    def log_operation(self, operation: str, details: dict = None) -> None:
        """Log a dashboard operation."""
        msg = f"Operation: {operation}"
        if details:
            msg += f" | {details}"
        self.logger.info(msg)

    def log_user_action(self, user: str, action: str, details: dict = None) -> None:
        """Log a user action."""
        msg = f"User '{user}' performed '{action}'"
        if details:
            msg += f" | {details}"
        self.logger.info(msg)

    def log_performance(self, operation: str, duration_ms: float) -> None:
        """Log operation performance."""
        if duration_ms > 1000:
            level = self.logger.warning
        elif duration_ms > 500:
            level = self.logger.info
        else:
            level = self.logger.debug
        level(f"Performance: {operation} took {duration_ms:.0f}ms")


class DashboardConfiguration:
    """Configuration manager for dashboard."""

    # Default settings
    DEFAULTS = {
        "window_width": 1400,
        "window_height": 900,
        "window_x": 80,
        "window_y": 60,
        "auto_save_interval": 300,  # seconds
        "async_timeout": 5000,  # ms
        "log_level": "INFO",
        "theme": "dark",
    }

    def __init__(self, config_dict: dict = None):
        """Initialize configuration."""
        self.config = self.DEFAULTS.copy()
        if config_dict:
            self.config.update(config_dict)

    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.config.copy()
