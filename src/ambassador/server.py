"""Minimal ambassador HTTP server exposing a public API surface.

This is a lightweight, dependency-free demonstration server based on Python's
standard library. It is designed to be run inside the Project-AI monolith or as a
simple containerized microservice to provide a public interface for the ambassador.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import typing as _typing
from urllib.parse import urlparse

try:
    from ambassador.bridge import AmbassadorBridge
except Exception:
    AmbassadorBridge = None  # type: ignore

PORT = 8080


class AmbassadorRequestHandler(BaseHTTPRequestHandler):
    bridge = AmbassadorBridge() if AmbassadorBridge else None

    def __init__(self, *args, **kwargs):
        self._api_keys: _typing.List[str] = []  # type: ignore
        self._tenant_map: dict = {}  # type: ignore
        super().__init__(*args, **kwargs)
        # Lazy load on first request

    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def _load_api_keys(self):
        keys = os.environ.get("AMBASSADOR_API_KEYS", "")
        tenant_map_raw = os.environ.get("AMBASSADOR_TENANT_MAP", "{}")
        self._api_keys = [k.strip() for k in keys.split(",") if k.strip()]
        try:
            self._tenant_map = json.loads(tenant_map_raw)
        except Exception:
            self._tenant_map = {}
        return bool(self._api_keys or self._tenant_map)

    def _authenticate(self) -> bool:
        # If no keys configured, allow (default for local/dev)
        if not (self._api_keys or self._tenant_map):
            return True
        # API key gate
        header_key = self.headers.get("X-Api-Key") or self.headers.get("X-API-Key")
        if header_key and header_key in (self._api_keys or []):
            return True
        # Tenant gate
        tenant_id = self.headers.get("X-Tenant-Id") or self.headers.get("X-TENANT-ID")
        if tenant_id and isinstance(self._tenant_map, dict):
            if (
                tenant_id in self._tenant_map
                and self._tenant_map[tenant_id] == header_key
            ):
                return True
        return False

    def _require_auth(self) -> bool:
        if not (self._api_keys or self._tenant_map):
            return True
        if not self._authenticate():
            self._set_headers(401)
            self.wfile.write(json.dumps({"error": "unauthorized"}).encode())
            return False
        return True

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._set_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            return
        elif parsed.path == "/status":
            if self.bridge:
                self._set_headers()
                self.wfile.write(json.dumps(self.bridge.status()).encode())
            else:
                self._set_headers(503)
                self.wfile.write(json.dumps({"error": "gateway unavailable"}).encode())
            return
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode())
            return

    def do_POST(self):
        parsed = urlparse(self.path)
        # Initialize API key data once per instance
        if not getattr(self, "_api_keys", None):
            self._load_api_keys()
        if not self._require_auth():
            return
        if parsed.path == "/action":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length > 0 else b"{}"
            try:
                payload = json.loads(body.decode())
            except Exception:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                return
            tenant_id = payload.get("tenant_id") or payload.get("tenant")
            if not self.bridge:
                self._set_headers(503)
                self.wfile.write(json.dumps({"error": "gateway unavailable"}).encode())
                return
            response = self.bridge.handle_action(payload, tenant_id)
            self._set_headers()
            self.wfile.write(json.dumps(response).encode())
            return
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode())
            return


def run_server():
    httpd = HTTPServer(("0.0.0.0", PORT), AmbassadorRequestHandler)
    print(f"Ambassador public interface listening on port {PORT}")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
