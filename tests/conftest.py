"""Pytest conftest for Project-AI.

Centralizes test setup such as adding the project's `src/` to sys.path so tests
can import the `app` package without each test mutating sys.path.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def pytest_configure(config):
    """Pytest hook - ensure src is available early for all tests."""
    # already inserted above; this ensures IDE/test runners pick it up too
    return None
