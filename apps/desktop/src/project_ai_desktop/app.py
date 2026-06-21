"""Desktop application entrypoint."""

from __future__ import annotations

import os
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from project_ai_desktop.main_window import MainWindow


def run() -> int:
    application = QApplication.instance() or QApplication(sys.argv)
    application.setApplicationName("Project-AI Desktop")
    application.setApplicationVersion("0.0.0.dev0")
    window = MainWindow()
    window.show()
    if os.getenv("PROJECT_AI_DESKTOP_SMOKE") == "1":
        QTimer.singleShot(150, application.quit)
    return application.exec()


def entrypoint() -> None:
    raise SystemExit(run())
