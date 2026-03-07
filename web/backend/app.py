# [2026-03-02 10:34] | Productivity: Active | Status: ACTIVE [Sovereign 2.1 Hardened]
"""Flask backend for Project-AI's lightweight web API."""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import secrets

try:  # pragma: no cover - import guard for environments without Flask
    from flask import Flask, jsonify, request
except ModuleNotFoundError as exc:  # pragma: no cover
    raise RuntimeError(
        "Flask must be installed to use the Project-AI web backend."
    ) from exc

app = Flask(__name__)


logger = logging.getLogger(__name__)


def _hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    """Hash a password with PBKDF2-SHA256. Returns (hash, salt)."""
    if salt is None:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 100_000
    ).hex()
    return pw_hash, salt


def _verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verify a password against a stored hash."""
    pw_hash, _ = _hash_password(password, salt)
    return hmac.compare_digest(pw_hash, stored_hash)


def _load_users() -> dict[str, dict[str, str]]:
    """Load users from environment or return empty dict.

    In production, connect this to a real user database.
    For development, set BACKEND_DEMO_USERS=1 to enable demo accounts.
    """
    if os.getenv("BACKEND_DEMO_USERS", "").strip() == "1":
        # Demo accounts — only enabled when explicitly opted in
        demo_salt = "devsalt0000000000000000000000000"
        admin_hash, _ = _hash_password("change-me-immediately", demo_salt)
        guest_hash, _ = _hash_password("change-me-immediately", demo_salt)
        logger.warning(
            "BACKEND_DEMO_USERS=1 — demo accounts active. "
            "DO NOT use in production."
        )
        return {
            "admin": {"hash": admin_hash, "salt": demo_salt, "role": "superuser"},
            "guest": {"hash": guest_hash, "salt": demo_salt, "role": "viewer"},
        }
    return {}


_USERS: dict[str, dict[str, str]] = _load_users()
_TOKENS: dict[str, str] = {}  # token -> username


@app.route("/api/status")
def status():
    """Return a simple health snapshot."""
    return jsonify(status="ok", component="web-backend"), 200


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate a user and return a session token."""
    payload = request.get_json(silent=True)
    if not payload:
        return (
            jsonify(error="missing-json", message="Request must include JSON body."),
            400,
        )

    username = (payload.get("username") or "").strip()
    password = payload.get("password")
    if not username or not password:
        return (
            jsonify(
                error="missing-credentials", message="username and password required"
            ),
            400,
        )

    user = _USERS.get(username)
    if not user or not _verify_password(
        password, user.get("hash", ""), user.get("salt", "")
    ):
        return (
            jsonify(
                error="invalid-credentials", message="Username or password incorrect"
            ),
            401,
        )

    token = f"tok-{secrets.token_urlsafe(32)}"
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
        return (
            jsonify(error="missing-token", message="X-Auth-Token header required"),
            401,
        )
    username = _TOKENS.get(token)
    if not username:
        return (
            jsonify(error="invalid-token", message="Provided token is not recognized"),
            403,
        )
    user = _USERS.get(username, {})
    return jsonify(
        status="ok", user={"username": username, "role": user.get("role", "unknown")}
    )


@app.route("/api/debug/force-error")
def force_error():
    """Endpoint intentionally raising an exception to test error handler.

    Only available when FLASK_ENV=development.
    """
    if os.getenv("FLASK_ENV") != "development":
        return jsonify(error="not-found", message="Not found"), 404
    raise RuntimeError("forced debug failure")


@app.errorhandler(Exception)
def handle_unexpected_error(exc):  # pylint: disable=unused-variable
    """Return JSON payload for unexpected errors while logging details."""
    logger.exception("Unhandled Flask backend error", exc_info=exc)
    return jsonify(status="error", message=str(exc)), 500
