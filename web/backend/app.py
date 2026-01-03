"""Flask backend for Project-AI's lightweight web API."""

from __future__ import annotations

import logging
import os

try:  # pragma: no cover - import guard for environments without Flask
    from flask import Flask, jsonify, request
except ModuleNotFoundError as exc:  # pragma: no cover
    raise RuntimeError(
        "Flask must be installed to use the Project-AI web backend."
    ) from exc

app = Flask(__name__)

# CORS configuration for Triumvirate integration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5000").split(",")
ENABLE_TRIUMVIRATE = os.getenv("ENABLE_TRIUMVIRATE", "false").lower() == "true"


logger = logging.getLogger(__name__)

# In-memory demo credential store used purely for backend tests.
_USERS: dict[str, dict[str, str]] = {
    "admin": {"password": "open-sesame", "role": "superuser"},
    "guest": {"password": "letmein", "role": "viewer"},
}
_TOKENS: dict[str, str] = {}  # token -> username


# CORS middleware for Triumvirate frontend
@app.after_request
def add_cors_headers(response):
    """Add CORS headers to allow Triumvirate frontend to communicate."""
    origin = request.headers.get("Origin")
    if origin in CORS_ORIGINS or not ENABLE_TRIUMVIRATE:
        response.headers["Access-Control-Allow-Origin"] = origin or "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Auth-Token"
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.route("/api/status")
def status():
    """Return a simple health snapshot."""
    return jsonify(
        status="ok", 
        component="web-backend",
        triumvirate_enabled=ENABLE_TRIUMVIRATE
    ), 200


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate a user and return a session token."""
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify(error="missing-json", message="Request must include JSON body."), 400

    username = (payload.get("username") or "").strip()
    password = payload.get("password")
    if not username or not password:
        return jsonify(error="missing-credentials", message="username and password required"), 400

    user = _USERS.get(username)
    if not user or user.get("password") != password:
        return jsonify(error="invalid-credentials", message="Username or password incorrect"), 401

    token = f"token-{username}"
    _TOKENS[token] = username
    return (
        jsonify(
            status="ok",
            token=token,
            user={"username": username, "role": user["role"]},
        ),
        200,
    )


@app.route("/api/auth/profile", methods=["GET"])
def profile():
    """Return user profile if a valid token is provided."""
    token = request.headers.get("X-Auth-Token")
    if not token:
        return jsonify(error="missing-token", message="X-Auth-Token header required"), 401
    username = _TOKENS.get(token)
    if not username:
        return jsonify(error="invalid-token", message="Provided token is not recognized"), 403
    user = _USERS.get(username, {})
    return jsonify(status="ok", user={"username": username, "role": user.get("role", "unknown")})


@app.route("/api/debug/force-error")
def force_error():
    """Endpoint intentionally raising an exception to test error handler."""
    raise RuntimeError("forced debug failure")


@app.errorhandler(Exception)
def handle_unexpected_error(exc):  # pylint: disable=unused-variable
    """Return JSON payload for unexpected errors while logging details."""
    logger.exception("Unhandled Flask backend error", exc_info=exc)
    return jsonify(status="error", message=str(exc)), 500
