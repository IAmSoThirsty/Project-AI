"""Thirstys Waterfall Web Interface Factory"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def create_app(config=None):
    """Application factory for Thirstys Waterfall web interface"""
    app = Flask(__name__)

    # Configuration
    app.config["JSON_SORT_KEYS"] = False
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
    
    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    # CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )

    # Logging
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    # Health check endpoint
    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint for container/load balancer"""
        return jsonify({
            "status": "healthy",
            "service": "thirstys-waterfall-web",
            "version": "1.0.0"
        }), 200

    # API status endpoint
    @app.route("/api/status", methods=["GET"])
    @limiter.limit("10 per minute")
    def api_status():
        """Get Thirstys Waterfall system status"""
        try:
            from thirstys_waterfall import ThirstysWaterfall
            waterfall = ThirstysWaterfall()
            status = waterfall.get_status()
            return jsonify(status), 200
        except Exception as e:
            app.logger.error(f"Status check failed: {e}")
            return jsonify({"error": str(e)}), 500

    # Root endpoint
    @app.route("/", methods=["GET"])
    def root():
        """Root endpoint"""
        return jsonify({
            "service": "Thirstys Waterfall Web Interface",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "status": "/api/status"
            }
        }), 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {error}")
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
