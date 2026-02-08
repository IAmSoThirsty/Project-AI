"""
Verifiability API
=================

External verifiability API endpoints for build verification and forensics.
Provides cryptographic proof interfaces for external auditors.
"""

import logging
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

from ..audit.audit_integration import BuildAuditIntegration
from ..capsules.capsule_engine import CapsuleEngine
from ..capsules.replay_engine import ReplayEngine

logger = logging.getLogger(__name__)


class VerifiabilityAPI:
    """
    REST API for external build verification and forensics.
    Provides cryptographic proof interfaces.
    """

    def __init__(
        self,
        capsule_engine: CapsuleEngine,
        replay_engine: ReplayEngine,
        audit_integration: BuildAuditIntegration,
        host: str = "0.0.0.0",
        port: int = 8080
    ):
        """
        Initialize verifiability API.

        Args:
            capsule_engine: Capsule engine instance
            replay_engine: Replay engine instance
            audit_integration: Audit integration instance
            host: API host
            port: API port
        """
        self.capsule_engine = capsule_engine
        self.replay_engine = replay_engine
        self.audit_integration = audit_integration
        self.host = host
        self.port = port

        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for external access

        self._register_routes()
        logger.info("Verifiability API initialized on %s:%s", host, port)

    def _register_routes(self) -> None:
        """Register API routes."""

        @self.app.route("/api/v1/health", methods=["GET"])
        def health():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "verifiability-api",
            })

        @self.app.route("/api/v1/capsules", methods=["GET"])
        def list_capsules():
            """List all build capsules."""
            try:
                capsules = [
                    {
                        "capsule_id": cap.capsule_id,
                        "tasks": cap.tasks,
                        "input_count": len(cap.inputs),
                        "output_count": len(cap.outputs),
                        "merkle_root": cap.merkle_root,
                        "timestamp": cap.timestamp,
                    }
                    for cap in self.capsule_engine.capsules.values()
                ]

                return jsonify({
                    "capsules": capsules,
                    "count": len(capsules),
                })
            except Exception as e:
                logger.error(f"Error listing capsules: {e}", exc_info=True)
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/v1/capsules/<capsule_id>", methods=["GET"])
        def get_capsule(capsule_id):
            """Get specific capsule details."""
            try:
                capsule = self.capsule_engine.capsules.get(capsule_id)
                if not capsule:
                    return jsonify({"error": "Capsule not found"}), 404

                return jsonify(capsule.to_dict())
            except Exception as e:
                logger.error(f"Error getting capsule: {e}", exc_info=True)
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/v1/capsules/<capsule_id>/verify", methods=["POST"])
        def verify_capsule(capsule_id):
            """Verify capsule integrity."""
            try:
                is_valid, error = self.capsule_engine.verify_capsule(capsule_id)

                return jsonify({
                    "capsule_id": capsule_id,
                    "valid": is_valid,
                    "error": error,
                    "timestamp": datetime.utcnow().isoformat(),
                })
            except Exception as e:
                logger.error(f"Error verifying capsule: {e}", exc_info=True)
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/v1/capsules/<capsule_id>/replay", methods=["POST"])
        async def replay_capsule(capsule_id):
            """Replay build from capsule."""
            try:
                data = request.get_json() or {}
                verify_outputs = data.get("verify_outputs", True)

                result = await self.replay_engine.replay_build(
                    capsule_id,
                    verify_outputs=verify_outputs
                )

                return jsonify({
                    "capsule_id": result.capsule_id,
                    "success": result.success,
                    "differences": result.differences,
                    "error": result.error,
                    "timestamp": result.timestamp,
                })
            except Exception as e:
                logger.error(f"Error replaying capsule: {e}", exc_info=True)
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/v1/capsules/diff", methods=["POST"])
        def capsule_diff():
            """Compare two capsules."""
            try:
                data = request.get_json()
                capsule_id1 = data.get("capsule_id1")
                capsule_id2 = data.get("capsule_id2")

                if not capsule_id1 or not capsule_id2:
                    return jsonify({
                        "error": "Both capsule_id1 and capsule_id2 required"
                    }), 400

                diff = self.capsule_engine.compute_capsule_diff(
                    capsule_id1,
                    capsule_id2
                )

                return jsonify(diff)
            except Exception as e:
                logger.error(f"Error computing diff: {e}", exc_info=True)
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/v1/audit/events", methods=["GET"])
        def get_audit_events():
            """Get recent audit events."""
            try:
                limit = request.args.get("limit", 100, type=int)
                events = self.audit_integration.get_audit_buffer(limit=limit)

                return jsonify({
                    "events": events,
                    "count": len(events),
                })
            except Exception as e:
                logger.error(f"Error getting audit events: {e}", exc_info=True)
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/v1/audit/report", methods=["GET"])
        def get_audit_report():
            """Generate audit report."""
            try:
                start_str = request.args.get("start_time")
                end_str = request.args.get("end_time")

                start_time = (
                    datetime.fromisoformat(start_str)
                    if start_str else None
                )
                end_time = (
                    datetime.fromisoformat(end_str)
                    if end_str else None
                )

                report = self.audit_integration.generate_audit_report(
                    start_time=start_time,
                    end_time=end_time
                )

                return jsonify(report)
            except Exception as e:
                logger.error(f"Error generating report: {e}", exc_info=True)
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/v1/proof/<capsule_id>", methods=["GET"])
        def get_cryptographic_proof(capsule_id):
            """Get cryptographic proof package for capsule."""
            try:
                capsule = self.capsule_engine.capsules.get(capsule_id)
                if not capsule:
                    return jsonify({"error": "Capsule not found"}), 404

                # Verify integrity
                is_valid, error = self.capsule_engine.verify_capsule(capsule_id)

                # Generate proof package
                proof = {
                    "capsule_id": capsule_id,
                    "merkle_root": capsule.merkle_root,
                    "integrity_verified": is_valid,
                    "verification_error": error,
                    "timestamp": datetime.utcnow().isoformat(),
                    "capsule_data": capsule.to_dict(),
                }

                return jsonify(proof)
            except Exception as e:
                logger.error(f"Error generating proof: {e}", exc_info=True)
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/v1/statistics", methods=["GET"])
        def get_statistics():
            """Get API statistics."""
            try:
                return jsonify({
                    "capsule_count": len(self.capsule_engine.capsules),
                    "replay_history_count": len(
                        self.replay_engine.get_replay_history(limit=10000)
                    ),
                    "audit_buffer_size": len(
                        self.audit_integration.get_audit_buffer(limit=10000)
                    ),
                    "timestamp": datetime.utcnow().isoformat(),
                })
            except Exception as e:
                logger.error(f"Error getting statistics: {e}", exc_info=True)
                return jsonify({"error": str(e)}), 500

    def run(self, debug: bool = False) -> None:
        """
        Run the API server.

        Args:
            debug: Enable debug mode
        """
        try:
            logger.info("Starting verifiability API on %s:%s", self.host, self.port)
            self.app.run(host=self.host, port=self.port, debug=debug)
        except Exception as e:
            logger.error(f"Error running API: {e}", exc_info=True)
            raise

    def get_app(self) -> Flask:
        """
        Get Flask app instance.

        Returns:
            Flask app
        """
        return self.app


__all__ = ["VerifiabilityAPI"]
