"""
Start Web Dashboard Server (Simplified - No WebSocket Required)

Opens the dashboard in browser with demo mode.
"""

import sys
import webbrowser
import http.server
import socketserver
import threading
from pathlib import Path

# Add kernel to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def start_simple_http_server(port=8000):
    """Start simple HTTP server for dashboard files"""

    dashboard_dir = Path(__file__).parent / "web_dashboard"

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(dashboard_dir), **kwargs)

        def log_message(self, format, *args):
            # Suppress server logs
            pass

    with socketserver.TCPServer(("", port), Handler) as httpd:
        print("\nDashboard HTTP Server running on http://localhost:" + str(port))
        print("   Serving files from: " + str(dashboard_dir))
        print("   Dashboard will run in DEMO MODE (simulated data)")
        print("   Press Ctrl+C to stop\n")

        # Open browser
        url = "http://localhost:" + str(port) + "/index.html"
        print("Opening dashboard in browser: " + url + "\n")
        webbrowser.open(url)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nDashboard server stopped")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("THIRSTY SUPER KERNEL - LIVE DASHBOARD")
    print("=" * 70 + "\n")

    start_simple_http_server(port=8080)
