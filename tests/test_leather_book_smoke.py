#                                           [2026-03-03 13:45]
#                                          Productivity: Active
import pytest

# PyQt6 DLL errors - skip GUI tests
pytestmark = pytest.mark.skip(reason="PyQt6 DLL not available")


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
