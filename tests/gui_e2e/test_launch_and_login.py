#                                           [2026-03-03 13:45]
#                                          Productivity: Active
from __future__ import annotations

import pytest

# PyQt6 DLL errors - skip GUI E2E tests
pytestmark = pytest.mark.skip(reason="PyQt6 DLL not available")


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_launch_and_close(qapp):
    win = LeatherBookInterface()
    win.show()
    assert win is not None
    # avoid full event loop run; just verify construction
    win.close()


@pytest.mark.skip(
    reason="Interactive login requires mocking; scaffold added for future tests"
)
def test_login_flow(qapp):
    # Placeholder: implement with pytest-qt to simulate button clicks and text entry
    pass
