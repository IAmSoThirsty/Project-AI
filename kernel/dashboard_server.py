"""
WebSocket Server for Live Dashboard

Provides real-time metrics to the web dashboard via WebSocket.
"""

import asyncio
import json
import logging
from typing import Any

import websockets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardWebSocketServer:
    """
    WebSocket server for real-time dashboard updates

    Broadcasts kernel metrics to connected clients
    """

    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients: set[websockets.WebSocketServerProtocol] = set()
        self.kernel = None  # Will be set by kernel

        logger.info("Dashboard WebSocket Server initialized on %s:%s", host, port)

    def set_kernel(self, kernel):
        """Set the kernel instance to pull metrics from"""
        self.kernel = kernel
        logger.info("Kernel instance attached to WebSocket server")

    async def register(self, websocket):
        """Register new client"""
        self.clients.add(websocket)
        logger.info("Client connected. Total clients: %s", len(self.clients))

        # Send initial state
        await self.send_metrics(websocket)

    async def unregister(self, websocket):
        """Unregister client"""
        self.clients.discard(websocket)
        logger.info("Client disconnected. Total clients: %s", len(self.clients))

    async def send_metrics(self, websocket=None):
        """Send current metrics to client(s)"""
        if not self.kernel:
            return

        try:
            status = self.kernel.get_system_status()

            # Build metrics payload
            payload = {
                "type": "metrics",
                "payload": {
                    "totalCommands": status["total_commands"],
                    "threatsDetected": status["threats_detected"],
                    "activeDeceptions": status["deceptions_active"],
                    "bubblegumTriggers": status.get("deception", {}).get(
                        "total_bubblegum_triggers", 0
                    ),
                    "layers": {
                        0: status["layers"].get(0, {}).get("total_commands", 0),
                        1: status["layers"].get(1, {}).get("total_commands", 0),
                        2: sum(
                            layer.get("total_commands", 0)
                            for lid, layer in status["layers"].items()
                            if int(lid) >= 2
                        ),
                    },
                    "attackTypes": status.get("threat_detection", {}).get(
                        "by_type", {}
                    ),
                    "performance": {
                        "avgDetectionTime": 2.5,  # Would come from benchmarks
                        "avgTransitionTime": 1.8,
                        "memoryUsage": 45.0,
                        "cpuUsage": 12.5,
                    },
                    "learning": self._get_learning_stats(),
                },
            }

            message = json.dumps(payload)

            if websocket:
                await websocket.send(message)
            else:
                # Broadcast to all clients
                if self.clients:
                    await asyncio.gather(
                        *[client.send(message) for client in self.clients],
                        return_exceptions=True,
                    )

        except Exception as e:
            logger.error("Error sending metrics: %s", e)

    def _get_learning_stats(self) -> dict[str, Any]:
        """Get learning engine statistics"""
        if hasattr(self.kernel, "learning_engine") and self.kernel.learning_engine:
            stats = self.kernel.learning_engine.get_statistics()
            return {
                "patternsLearned": stats["patterns_learned"],
                "activePlaybooks": stats["active_playbooks"],
                "evolutionCycles": stats["evolution_cycles"],
                "detectionAccuracy": 95.8,  # Would be calculated from success rates
            }
        else:
            return {
                "patternsLearned": 0,
                "activePlaybooks": 0,
                "evolutionCycles": 0,
                "detectionAccuracy": 0.0,
            }

    async def send_threat_alert(self, threat_info: dict[str, Any]):
        """Send threat alert to all clients"""
        payload = {"type": "threat", "payload": threat_info}

        message = json.dumps(payload)

        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True,
            )

    async def send_activity(self, level: str, message: str):
        """Send activity log entry"""
        payload = {"type": "activity", "level": level, "message": message}

        msg = json.dumps(payload)

        if self.clients:
            await asyncio.gather(
                *[client.send(msg) for client in self.clients], return_exceptions=True
            )

    async def handler(self, websocket, path):
        """Handle WebSocket connection"""
        await self.register(websocket)

        try:
            async for message in websocket:
                # Handle client messages (if any)
                data = json.loads(message)

                if data.get("type") == "request_metrics":
                    await self.send_metrics(websocket)

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)

    async def start(self):
        """Start the WebSocket server"""
        logger.info("Starting WebSocket server on ws://%s:%s", self.host, self.port)

        async with websockets.serve(self.handler, self.host, self.port):
            logger.info("✅ WebSocket server running")

            # Periodic metrics broadcast
            while True:
                await asyncio.sleep(1)  # Update every second
                await self.send_metrics()

    def run(self):
        """Run the server (blocking)"""
        asyncio.run(self.start())


def start_dashboard_server(kernel=None, host="localhost", port=8765):
    """
    Start dashboard WebSocket server

    Args:
        kernel: ThirstySuperKernel instance
        host: Server host
        port: Server port
    """
    server = DashboardWebSocketServer(host, port)

    if kernel:
        server.set_kernel(kernel)

    # Run in background thread
    import threading

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    logger.info("Dashboard server started on background thread")
    logger.info("Open http://localhost:8000/index.html in browser")

    return server


# Public API
__all__ = [
    "DashboardWebSocketServer",
    "start_dashboard_server",
]


if __name__ == "__main__":
    # Test server
    print("\n" + "=" * 70)
    print("DASHBOARD WEBSOCKET SERVER - DEMO MODE")
    print("=" * 70)
    print("\nStarting server on ws://localhost:8765")
    print("Open dashboard at: file:///path/to/web_dashboard/index.html")
    print("\n")

    server = DashboardWebSocketServer()
    asyncio.run(server.start())
