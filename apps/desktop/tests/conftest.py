from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from PyQt6.QtWidgets import QApplication

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="session")
def qt_app() -> Generator[QApplication]:
    instance = QApplication.instance()
    application: QApplication
    if isinstance(instance, QApplication):
        application = instance
    else:
        application = QApplication([])
    yield application
    application.quit()
