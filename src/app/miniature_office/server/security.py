"""
Security middleware and helpers for production deployment
"""

import os
from functools import wraps
from typing import Callable

from flask import jsonify, request


def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' cdn.socket.io; "
        "script-src 'self' 'unsafe-inline' cdn.socket.io; "
        "style-src 'self' 'unsafe-inline'"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


def validate_request_size(max_size=16 * 1024 * 1024):  # 16MB default (matches Flask config)
    """
    Decorator to validate request size.
    Default matches app.config['MAX_CONTENT_LENGTH'].
    Use smaller limits for specific endpoints if needed.
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            content_length = request.content_length
            if content_length and content_length > max_size:
                return jsonify({"error": "Request too large", "max_size": max_size}), 413
            return f(*args, **kwargs)

        return wrapper

    return decorator


def validate_json_request(f: Callable) -> Callable:
    """Decorator to validate JSON requests"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.method in ["POST", "PUT", "PATCH"]:
            if not request.is_json:
                return jsonify({"error": "Content-Type must be application/json"}), 415
        return f(*args, **kwargs)

    return wrapper


# NOTE: rate_limit_check is not currently used.
# For production rate limiting, integrate Redis with flask-limiter:
# pip install flask-limiter redis
# from flask_limiter import Limiter
# limiter = Limiter(app, key_func=get_remote_address, storage_uri="redis://localhost:6379")
# @limiter.limit("10 per minute")


def configure_cors(app, allowed_origins=None):
    """Configure CORS for the Flask app"""
    if allowed_origins is None:
        # Default to environment variable or wildcard
        origins_str = os.getenv("CORS_ORIGINS", "*")
        if origins_str == "*":
            allowed_origins = "*"
        else:
            allowed_origins = [o.strip() for o in origins_str.split(",")]

    @app.after_request
    def apply_cors(response):
        if allowed_origins == "*":
            response.headers["Access-Control-Allow-Origin"] = "*"
        elif request.origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = request.origin

        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Max-Age"] = "3600"
        return response

    return app


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not isinstance(text, str):
        text = str(text)

    # Truncate to max length
    text = text[:max_length]

    # Remove potentially dangerous characters
    # This is basic sanitization - adjust based on your needs
    dangerous_chars = ["<", ">", '"', "'", "&", ";", "|", "`"]
    for char in dangerous_chars:
        text = text.replace(char, "")

    return text.strip()
