"""
Prometheus Metrics HTTP Server for Project-AI

Provides HTTP endpoints for Prometheus to scrape metrics:
- /metrics - Main application metrics
- /ai-metrics - AI system specific metrics
- /security-metrics - Security and Cerberus metrics
- /plugin-metrics - Plugin system metrics
- /health - Health check endpoint

Can run standalone or be integrated into existing Flask/FastAPI server.
"""

import logging
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from app.monitoring.metrics_collector import collector
from app.monitoring.prometheus_exporter import metrics

logger = logging.getLogger(__name__)


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Prometheus metrics."""

    def log_message(self, format: str, *args: Any) -> None:
        """Override to use Python logging instead of printing."""
        logger.debug(f"{self.address_string()} - {format % args}")

    def do_GET(self) -> None:
        """Handle GET requests."""
        try:
            if self.path == '/metrics':
                self._serve_metrics()
            elif self.path == '/ai-metrics':
                self._serve_ai_metrics()
            elif self.path == '/security-metrics':
                self._serve_security_metrics()
            elif self.path == '/plugin-metrics':
                self._serve_plugin_metrics()
            elif self.path == '/health':
                self._serve_health()
            else:
                self.send_error(404, "Endpoint not found")
        except Exception as e:
            logger.error(f"Error handling request {self.path}: {e}")
            self.send_error(500, str(e))

    def _serve_metrics(self) -> None:
        """Serve main application metrics."""
        # Collect latest metrics from disk
        collector.collect_all_metrics()

        # Generate metrics
        metrics_output = metrics.generate_metrics()

        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; version=0.0.4')
        self.end_headers()
        self.wfile.write(metrics_output)

    def _serve_ai_metrics(self) -> None:
        """Serve AI system specific metrics."""
        # Collect AI-specific metrics
        collector.collect_all_metrics()

        # Generate metrics (same as main, but different endpoint for organization)
        metrics_output = metrics.generate_metrics()

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; version=0.0.4')
        self.end_headers()
        self.wfile.write(metrics_output)

    def _serve_security_metrics(self) -> None:
        """Serve security and Cerberus metrics."""
        collector.collect_all_metrics()

        metrics_output = metrics.generate_metrics()

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; version=0.0.4')
        self.end_headers()
        self.wfile.write(metrics_output)

    def _serve_plugin_metrics(self) -> None:
        """Serve plugin system metrics."""
        collector.collect_all_metrics()

        metrics_output = metrics.generate_metrics()

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; version=0.0.4')
        self.end_headers()
        self.wfile.write(metrics_output)

    def _serve_health(self) -> None:
        """Serve health check endpoint."""
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'service': 'project-ai-metrics'
        }

        import json
        response = json.dumps(health_status).encode('utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(response)


class MetricsServer:
    """Prometheus metrics HTTP server."""

    def __init__(self, host: str = '0.0.0.0', port: int = 8000):
        """Initialize metrics server.

        Args:
            host: Host to bind to
            port: Port to listen on
        """
        self.host = host
        self.port = port
        self.server: HTTPServer | None = None
        self.thread: threading.Thread | None = None
        self._running = False

    def start(self, daemon: bool = True) -> None:
        """Start the metrics server in a background thread.

        Args:
            daemon: Whether to run as daemon thread
        """
        if self._running:
            logger.warning("Metrics server already running")
            return

        try:
            self.server = HTTPServer((self.host, self.port), MetricsHandler)
            self._running = True

            self.thread = threading.Thread(
                target=self._run_server,
                daemon=daemon,
                name="PrometheusMetricsServer"
            )
            self.thread.start()

            logger.info(f"Prometheus metrics server started on {self.host}:{self.port}")
            logger.info(f"Metrics available at http://{self.host}:{self.port}/metrics")

        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")
            self._running = False
            raise

    def _run_server(self) -> None:
        """Run the HTTP server (internal method)."""
        if self.server:
            try:
                self.server.serve_forever()
            except Exception as e:
                logger.error(f"Metrics server error: {e}")
            finally:
                self._running = False

    def stop(self) -> None:
        """Stop the metrics server."""
        if not self._running:
            return

        self._running = False

        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("Prometheus metrics server stopped")

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)

    def is_running(self) -> bool:
        """Check if server is running.

        Returns:
            True if server is running
        """
        return self._running


def start_metrics_server(host: str = '0.0.0.0', port: int = 8000) -> MetricsServer:
    """Start Prometheus metrics server.

    Args:
        host: Host to bind to
        port: Port to listen on

    Returns:
        Running MetricsServer instance
    """
    server = MetricsServer(host, port)
    server.start()
    return server


if __name__ == '__main__':
    # Standalone mode for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    server = start_metrics_server(port=8000)

    try:
        print("Metrics server running. Press Ctrl+C to stop.")
        print("Available endpoints:")
        print("  http://localhost:8000/metrics - Main metrics")
        print("  http://localhost:8000/ai-metrics - AI system metrics")
        print("  http://localhost:8000/security-metrics - Security metrics")
        print("  http://localhost:8000/plugin-metrics - Plugin metrics")
        print("  http://localhost:8000/health - Health check")

        # Keep main thread alive
        while server.is_running():
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()
