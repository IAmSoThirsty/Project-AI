import pytest
from PyQt6.QtWidgets import QApplication

from app.gui.leather_book_interface import LeatherBookInterface


@pytest.fixture(scope="session")
def qt_app():
    """Share a single QApplication instance across tests."""
    app = QApplication.instance() or QApplication([])
    yield app


def test_leather_book_interface_starts(qt_app):
    """Smoke test that the leather book window can initialize."""
    window = LeatherBookInterface()
    assert "Leather Book" in window.windowTitle()
    window.close()
