"""
3D Visualization Component for Project-AI Dashboard.

Provides 3D rendering capabilities for AI system visualization including:
- Persona state visualization in 3D space
- Agent network topology
- Memory expansion graph
- Real-time system metrics in 3D
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QRadialGradient
from PyQt6.QtWidgets import QWidget

if TYPE_CHECKING:
    from PyQt6.QtGui import QPaintEvent


class Visualization3DWidget(QWidget):
    """3D-style visualization widget using QPainter transformations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rotation_angle = 0.0
        self.elevation_angle = 30.0
        self.zoom_level = 1.0
        self.nodes = []  # 3D nodes to render
        self.connections = []  # Connections between nodes

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_rotation)
        self.timer.start(50)  # 20 FPS

        self.setMinimumSize(400, 400)

    def _update_rotation(self):
        """Update rotation for animation effect."""
        self.rotation_angle = (self.rotation_angle + 1) % 360
        self.update()

    def add_node(
        self, x: float, y: float, z: float, label: str = "", color: QColor = None
    ):
        """Add a 3D node to the visualization."""
        if color is None:
            color = QColor(0, 255, 255)  # Tron cyan
        self.nodes.append({"x": x, "y": y, "z": z, "label": label, "color": color})

    def add_connection(self, from_idx: int, to_idx: int):
        """Add a connection between two nodes."""
        self.connections.append((from_idx, to_idx))

    def _project_3d_to_2d(self, x: float, y: float, z: float) -> tuple[float, float]:
        """Project 3D coordinates to 2D screen space with perspective."""
        # Apply rotation
        angle_rad = math.radians(self.rotation_angle)
        x_rot = x * math.cos(angle_rad) - z * math.sin(angle_rad)
        z_rot = x * math.sin(angle_rad) + z * math.cos(angle_rad)

        # Apply elevation
        elev_rad = math.radians(self.elevation_angle)
        y_elev = y * math.cos(elev_rad) - z_rot * math.sin(elev_rad)
        z_elev = y * math.sin(elev_rad) + z_rot * math.cos(elev_rad)

        # Perspective projection
        fov = 500.0
        scale = fov / (fov + z_elev)

        # Center and scale
        center_x = self.width() / 2
        center_y = self.height() / 2

        screen_x = center_x + (x_rot * scale * self.zoom_level * 50)
        screen_y = center_y + (y_elev * scale * self.zoom_level * 50)

        return screen_x, screen_y

    def paintEvent(self, event: QPaintEvent):
        """Paint the 3D visualization."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        bg_gradient = QRadialGradient(
            QPointF(self.width() / 2, self.height() / 2),
            max(self.width(), self.height()) / 2,
        )
        bg_gradient.setColorAt(0, QColor(20, 30, 60))
        bg_gradient.setColorAt(1, QColor(5, 10, 20))
        painter.fillRect(self.rect(), QBrush(bg_gradient))

        # Draw connections
        painter.setPen(QPen(QColor(0, 200, 200, 100), 2))
        for from_idx, to_idx in self.connections:
            if from_idx < len(self.nodes) and to_idx < len(self.nodes):
                from_node = self.nodes[from_idx]
                to_node = self.nodes[to_idx]

                from_x, from_y = self._project_3d_to_2d(
                    from_node["x"], from_node["y"], from_node["z"]
                )
                to_x, to_y = self._project_3d_to_2d(
                    to_node["x"], to_node["y"], to_node["z"]
                )

                painter.drawLine(int(from_x), int(from_y), int(to_x), int(to_y))

        # Draw nodes
        for node in self.nodes:
            screen_x, screen_y = self._project_3d_to_2d(node["x"], node["y"], node["z"])

            # Create glow effect
            glow = QRadialGradient(QPointF(screen_x, screen_y), 20)
            glow.setColorAt(0, node["color"])
            glow.setColorAt(
                0.5,
                QColor(
                    node["color"].red(),
                    node["color"].green(),
                    node["color"].blue(),
                    150,
                ),
            )
            glow.setColorAt(
                1,
                QColor(
                    node["color"].red(), node["color"].green(), node["color"].blue(), 0
                ),
            )

            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(screen_x, screen_y), 15, 15)

            # Draw node core
            painter.setBrush(QBrush(node["color"]))
            painter.drawEllipse(QPointF(screen_x, screen_y), 8, 8)

            # Draw label
            if node["label"]:
                painter.setPen(QPen(QColor(255, 255, 255)))
                painter.drawText(
                    QRectF(screen_x - 50, screen_y + 20, 100, 20),
                    Qt.AlignmentFlag.AlignCenter,
                    node["label"],
                )

        painter.end()

    def set_zoom(self, zoom: float):
        """Set zoom level."""
        self.zoom_level = max(0.5, min(2.0, zoom))
        self.update()

    def set_elevation(self, elevation: float):
        """Set elevation angle."""
        self.elevation_angle = max(0, min(90, elevation))
        self.update()

    def clear(self):
        """Clear all nodes and connections."""
        self.nodes.clear()
        self.connections.clear()
        self.update()


class AISystemVisualization3D(Visualization3DWidget):
    """Specialized 3D visualization for AI system components."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ai_system_nodes()

    def _setup_ai_system_nodes(self):
        """Setup nodes representing AI system components."""
        # Central AI Core
        self.add_node(0, 0, 0, "AI Core", QColor(255, 100, 255))

        # Four Laws System
        self.add_node(-2, 2, -1, "Four Laws", QColor(0, 255, 0))

        # Persona System
        self.add_node(2, 2, -1, "Persona", QColor(0, 200, 255))

        # Memory System
        self.add_node(-2, -2, 1, "Memory", QColor(255, 200, 0))

        # Learning System
        self.add_node(2, -2, 1, "Learning", QColor(255, 50, 50))

        # Agents
        self.add_node(0, 3, 2, "Agents", QColor(150, 150, 255))

        # Connections to core
        for i in range(1, 6):
            self.add_connection(0, i)
