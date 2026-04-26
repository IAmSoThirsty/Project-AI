# [2026-04-03 23:25] | Productivity: Active | Status: ACTIVE [Sovereign 2.1 Hardened]
"""Flask backend for Project-AI's lightweight web API."""

from __future__ import annotations

import logging
import os
import sys

# Ensure the Project-AI source directory is in the path for security module imports
# Root is Sovereign-Governance-Substrate
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:  # pragma: no cover - import guard for environments without Flask
    from flask import Flask, jsonify, request
except ModuleNotFoundError as exc:  # pragma: no cover
    raise RuntimeError(
        "Flask must be installed to use the Project-AI web backend."
    ) from exc

# Sovereign Security Imports
from src.app.security.oauth2_provider import provider as oauth2_provider

app = Flask(__name__)


logger = logging.getLogger(__name__)

# In-memory demo credential store (to be replaced by Identity Engine)
# Hardened in Sovereign 2.1 - only for local testing.
_USERS: dict[str, dict[str, str]] = {
    "admin": {"password": "open-sesame", "role": "superuser"},
    "guest": {"password": "letmein", "role": "viewer"},
}


@app.route("/api/status")
def status():
    """Return a simple health snapshot."""
    return jsonify(status="ok", component="web-backend", sovereign_auth="active"), 200


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate a user and return a session token using OAuth2Provider."""
    payload = request.get_json(silent=True)
    if not payload:
        return (
            jsonify(error="missing-json", message="Request must include JSON body."),
            400,
        )

    username = (payload.get("username") or "").strip()
    password = payload.get("password")

    # 1. Validate Initial Credentials
    user = _USERS.get(username)
    if not user or user.get("password") != password:
        return (
            jsonify(
                error="invalid-credentials", message="Username or password incorrect"
            ),
            401,
        )

    # 2. Issue Sovereign OAuth2 Token
    try:
        # Generate an auth code for the web client
        code = oauth2_provider.authorize(
            client_id="sovereign-web-ui",
            response_type="code",
            scope=f"role:{user['role']}",
            redirect_uri="http://localhost:5000/callback"
        )

        # Immediate exchange for web-bound sessions (simplified flow for internal UI)
        token_data = oauth2_provider.exchange_token(
            code=code,
            client_id="sovereign-web-ui",
            client_secret="cert-hardened-secret-991"  # Defined in provider
        )

        return (
            jsonify(
                status="ok",
                token=token_data["access_token"],
                expires_in=token_data["expires_in"],
                user={"username": username, "role": user["role"]},
            ),
            200,
        )
    except Exception as e:
        logger.error("OAuth2 Error during login for %s: %s", username, str(e))
        return jsonify(error="auth_service_failure", message=str(e)), 500


@app.route("/api/auth/profile", methods=["GET"])
def profile():
    """Return user profile after validating via OAuth2Provider."""
    token = request.headers.get("X-Auth-Token")
    if not token:
        return (
            jsonify(error="missing-token", message="X-Auth-Token header required"),
            401,
        )

    # Validate via hardened provider
    token_metadata = oauth2_provider.validate_token(token)
    if not token_metadata:
        return (
            jsonify(error="invalid-token", message="Provided token is not recognized or expired"),
            403,
        )

    # In a real system, we'd map the token back to a user ID via the Identity Engine
    # For now, we mock it based on the token pattern or metadata
    return jsonify(
        status="ok",
        user={
            "client_id": token_metadata["client_id"],
            "scope": token_metadata["scope"]
        }
    )


@app.route("/api/debug/force-error")
def force_error():
    """Endpoint intentionally raising an exception to test error handler."""
    raise RuntimeError("forced debug failure")


@app.errorhandler(Exception)
def handle_unexpected_error(exc):  # pylint: disable=unused-variable
    """Return JSON payload for unexpected errors while logging details."""
    logger.exception("Unhandled Flask backend error", exc_info=exc)
    return jsonify(status="error", message=str(exc)), 500
