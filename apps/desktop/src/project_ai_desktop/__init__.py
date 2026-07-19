"""Project-AI read-only operator desktop."""

from project_ai_desktop._version import DESKTOP_VERSION
from project_ai_desktop.app import run
from project_ai_desktop.main_window import MainWindow

__version__ = DESKTOP_VERSION

__all__ = ["MainWindow", "run"]
