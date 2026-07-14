"""Desktop application entrypoint."""

from __future__ import annotations

import os
import sys

from PyQt6.QtCore import QObject, QThread, QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication

from project_ai_desktop.api_supervisor import ApiSupervisor
from project_ai_desktop.main_window import MainWindow

_SUPERVISOR_JOIN_TIMEOUT_MS = 35_000


class ApiSupervisorThread(QThread):
    """Runs `ApiSupervisor.ensure_running()` off the Qt main thread."""

    ready = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(
        self, supervisor: ApiSupervisor | None = None, parent: QObject | None = None
    ) -> None:
        super().__init__(parent)
        self._supervisor = supervisor or ApiSupervisor()

    def run(self) -> None:
        outcome = self._supervisor.ensure_running()
        if outcome.ready:
            self.ready.emit(outcome.url)
        else:
            self.failed.emit(outcome.reason)

    def terminate_supervisor(self) -> None:
        """Join the worker, then terminate any process it spawned.

        Waiting first avoids a race on the supervisor's internal process
        handle: it is only ever set from inside `run()`, so it is only safe
        to read from another thread once `run()` has definitively finished.
        """
        self.wait(_SUPERVISOR_JOIN_TIMEOUT_MS)
        self._supervisor.terminate()


def run() -> int:
    application = QApplication.instance() or QApplication(sys.argv)
    application.setApplicationName("Project-AI Desktop")
    application.setApplicationVersion("0.0.0.dev0")
    window = MainWindow()
    window.show()

    supervisor_thread = ApiSupervisorThread(parent=application)
    supervisor_thread.ready.connect(window.set_api_endpoint)
    supervisor_thread.failed.connect(window.report_supervisor_status)
    application.aboutToQuit.connect(supervisor_thread.terminate_supervisor)
    supervisor_thread.start()

    if os.getenv("PROJECT_AI_DESKTOP_SMOKE") == "1":
        QTimer.singleShot(150, application.quit)
    return application.exec()


def entrypoint() -> None:
    raise SystemExit(run())
