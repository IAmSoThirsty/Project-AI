# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_gui.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_gui.py


import sys
from pathlib import Path

# Add src to sys.path
PROJECT_ROOT = Path(__file__).parent.absolute()
SRC_PATH = PROJECT_ROOT / "src"
sys.path.append(str(SRC_PATH))

from PyQt6.QtWidgets import QApplication
from src.app.gui.leather_book_interface import LeatherBookInterface


def test_interface():
    _ = QApplication(sys.argv)
    window = LeatherBookInterface()
    window.show()
    # Close after a few seconds or allow manual inspection if running in a real environment
    # For now, just test import and initialization
    print("LeatherBookInterface initialized successfully.")
    # app.exec() # Don't block in automated test


if __name__ == "__main__":
    test_interface()
