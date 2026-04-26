# [Headless Wrapper]                            [2026-04-03 19:24]
#                                          Productivity: Active
"""Headless bootstrap wrapper for Project-AI."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from src.app.api_core import initialize_api_core, runtime_summary
from src.block_pyqt6 import ensure_pyqt6_available

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    """Configure a reasonable default logger for wrapper entrypoints."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _bootstrap_headless() -> dict[str, Any]:
    """Bootstrap the sovereign runtime without launching a GUI."""

    os.environ.setdefault("HEADLESS_MODE", "1")
    os.environ.setdefault("QT_API", "pyqt6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    ensure_pyqt6_available()
    load_dotenv()
    return initialize_api_core(headless=True)


def main_headless() -> int:
    """Run the headless bootstrap path."""

    _configure_logging()
    state = _bootstrap_headless()
    summary = runtime_summary(state, history_limit=5)
    print("HEADLESS_RUNTIME_READY")
    print(
        f"kernel_executions={summary['kernel']['statistics'].get('total_executions', 0)} "
        f"agents={summary['council_hub']['agent_count']}"
    )
    return 0


def main_gui() -> int:
    """Run the GUI application path."""

    _configure_logging()
    ensure_pyqt6_available()
    from src.app.main import main as app_main

    app_main()
    return 0


def main() -> int:
    """Dispatch to headless or GUI mode based on environment."""

    mode = os.getenv("HEADLESS_MODE", "").strip().lower()
    if mode in {"1", "true", "yes", "on"}:
        return main_headless()
    return main_gui()


if __name__ == "__main__":
    raise SystemExit(main())
