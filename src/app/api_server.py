# [API Server Implementation]                   [2026-04-03 19:24]
#                                          Productivity: Active
"""Flask API server for the Project-AI sovereign runtime."""

from __future__ import annotations

import logging
import os
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from src.app.api_core import get_api_state, initialize_api_core, runtime_summary

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

logger = logging.getLogger(__name__)
_STATE_LOCK = threading.RLock()


def _configure_logging() -> None:
    """Attach a file handler for the API server if needed."""

    logs_dir = ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    target_path = str(logs_dir / "api.log")
    root_logger = logging.getLogger()

    for handler in root_logger.handlers:
        if isinstance(handler, logging.FileHandler) and getattr(
            handler, "baseFilename", None
        ) == target_path:
            break
    else:
        handler = logging.FileHandler(target_path, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        root_logger.addHandler(handler)

    if root_logger.level == logging.NOTSET:
        root_logger.setLevel(logging.INFO)


def _ensure_runtime() -> dict[str, object]:
    """Return the cached runtime state, bootstrapping it when needed."""

    with _STATE_LOCK:
        state = get_api_state(create=False)
        if state is None:
            state = initialize_api_core(headless=True)
        return state


@app.before_request
def startup_guard():
    """Ensure the sovereign runtime is available before handling requests."""

    try:
        _configure_logging()
        _ensure_runtime()
    except Exception as exc:  # pragma: no cover - exercised in failure paths
        logger.exception("API bootstrap failed")
        return jsonify(status="error", error=str(exc)), 503
    return None


@app.route("/")
def root():
    """Root service metadata."""

    state = _ensure_runtime()
    summary = runtime_summary(state, history_limit=5)
    return jsonify(
        service="Project-AI API",
        status="ok",
        initialized=summary["initialized"],
        headless=summary["headless"],
        agents=summary["council_hub"]["agent_count"],
    )


@app.route("/health")
def health():
    """Return a compact health snapshot."""

    state = _ensure_runtime()
    summary = runtime_summary(state, history_limit=3)
    return jsonify(
        status="ok",
        initialized=summary["initialized"],
        dependency_status=summary["dependency_status"],
        kernel=summary["kernel"]["statistics"],
        agents=summary["council_hub"]["agent_count"],
    )


@app.route("/api/v1/status")
def status():
    """Return a full runtime summary."""

    limit = request.args.get("limit", default=20, type=int) or 20
    return jsonify(runtime_summary(_ensure_runtime(), history_limit=limit))


@app.route("/api/v1/kernel/info")
def kernel_info():
    """Return kernel statistics and recent execution history."""

    limit = request.args.get("limit", default=20, type=int) or 20
    summary = runtime_summary(_ensure_runtime(), history_limit=limit)
    return jsonify(summary["kernel"])


@app.route("/api/v1/agents")
def agents():
    """Return the list of council agents."""

    summary = runtime_summary(_ensure_runtime(), history_limit=1)
    return jsonify(summary["council_hub"])


@app.route("/api/v1/security/status")
def security_status():
    """Return security component availability."""

    summary = runtime_summary(_ensure_runtime(), history_limit=1)
    return jsonify(
        security=summary["security"],
        enhanced_defenses=summary["enhanced_defenses"],
    )


@app.errorhandler(Exception)
def handle_exception(exc: Exception):  # pragma: no cover - failure path
    """Return JSON for unexpected errors."""

    if isinstance(exc, HTTPException):
        return exc

    logger.exception("Unhandled API error")
    return jsonify(status="error", error=type(exc).__name__, message=str(exc)), 500


def main() -> int:
    """Run the Flask API server."""

    _configure_logging()
    port = int(os.getenv("PORT", "5000"))
    host = os.getenv("HOST", "0.0.0.0")
    app.run(host=host, port=port, debug=False, use_reloader=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
