"""
Web interface adapter: Routes Flask requests through governance pipeline.

This is a THIN adapter that preserves all web functionality while
ensuring every request flows through the runtime router.

Old behavior: Flask → Direct business logic
New behavior: Flask → Router → Governance → AI Orchestrator → Systems
"""

from __future__ import annotations

import logging

try:
    from flask import Flask, jsonify, request
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "Flask must be installed to use the Project-AI web backend."
    ) from exc

from app.core.runtime.router import route_request
from app.core.security.middleware import configure_cors, configure_rate_limiting

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Configure security middleware
configure_cors(app)
configure_rate_limiting(app)


@app.route("/api/status")
def status():
    """Health check endpoint."""
    return jsonify(status="ok", component="web-backend"), 200


@app.route("/api/auth/login", methods=["POST"])
def login():
    """
    Authenticate user via governance pipeline.
    
    Old: Direct authentication with plaintext passwords
    New: Routes through governance → secure auth (argon2/JWT)
    """
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify(error="missing-json", message="Request must include JSON body."), 400

    # Route through governance pipeline
    response = route_request(
        source="web",
        payload={
            "action": "user.login",
            "username": payload.get("username"),
            "password": payload.get("password"),
        },
    )

    if response["status"] == "success":
        role = response["result"].get("role", "user")
        username = response["result"].get("username")
        return jsonify(
            status="ok",
            success=True,
            token=response["result"]["token"],
            user={"username": username, "role": role},
        ), 200
    else:
        return jsonify(
            status="error",
            success=False,
            error="invalid-credentials",
            message=response.get("error", "Authentication failed"),
        ), 401


@app.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    """
    AI chat endpoint via orchestrator.
    
    Old: Direct OpenAI calls
    New: Routes through governance → AI orchestrator (fallback support)
    """
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify(error="missing-json"), 400

    # Extract auth token
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else None

    # Route through governance pipeline
    response = route_request(
        source="web",
        payload={
            "action": "ai.chat",
            "task_type": "chat",
            "prompt": payload.get("prompt", ""),
            "model": payload.get("model"),
            "provider": payload.get("provider"),
            "token": token,
        },
    )

    if response["status"] == "success":
        return jsonify(result=response["result"], metadata=response["metadata"]), 200
    else:
        return jsonify(error=response.get("error", "AI request failed")), 500


@app.route("/api/ai/image", methods=["POST"])
def ai_image():
    """
    AI image generation via orchestrator.
    
    Old: Direct OpenAI/HuggingFace calls
    New: Routes through governance → AI orchestrator
    """
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify(error="missing-json"), 400

    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else None

    response = route_request(
        source="web",
        payload={
            "action": "ai.image",
            "task_type": "image",
            "prompt": payload.get("prompt", ""),
            "model": payload.get("model"),
            "provider": payload.get("provider"),
            "size": payload.get("size", "1024x1024"),
            "token": token,
        },
    )

    if response["status"] == "success":
        return jsonify(result=response["result"], metadata=response["metadata"]), 200
    else:
        return jsonify(error=response.get("error", "Image generation failed")), 500


@app.route("/api/persona/update", methods=["POST"])
def persona_update():
    """Update AI persona traits via governance pipeline."""
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify(error="missing-json"), 400

    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else None

    response = route_request(
        source="web",
        payload={
            "action": "persona.update",
            "trait": payload.get("trait"),
            "value": payload.get("value"),
            "token": token,
        },
    )

    if response["status"] == "success":
        return jsonify(success=True, result=response["result"]), 200
    else:
        return jsonify(success=False, error=response.get("error")), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
