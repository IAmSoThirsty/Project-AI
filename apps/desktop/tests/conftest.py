from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from PyQt6.QtWidgets import QApplication

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="session")
def qt_app() -> Generator[QApplication]:
    instance = QApplication.instance()
    application = instance if isinstance(instance, QApplication) else QApplication([])
    yield application
    application.quit()
