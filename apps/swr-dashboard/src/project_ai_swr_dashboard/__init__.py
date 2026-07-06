"""Project-AI SWR Dashboard (J3.8 port).

Flask-based read-only web dashboard for the SWR core
(WarRoomCore facade, J6.1). The dashboard surfaces scenarios,
results, leaderboards, and top-line counts.

Public surface:

  - ``create_app()`` — Flask app factory; builds the dashboard with a
    fresh governed WarRoomCore instance.
  - ``entrypoint()`` — module-level entry point for the
    ``project-ai-swr-dashboard`` console script.
  - ``get_swr()`` — lazy WarRoomCore factory (same shape as
    ``swr.cli.get_swr()``: default allow-all governance stack).
"""

from __future__ import annotations

from project_ai_swr_dashboard.app import create_app, entrypoint, get_swr

__version__ = "0.0.0.dev0"

__all__ = [
    "create_app",
    "entrypoint",
    "get_swr",
]
