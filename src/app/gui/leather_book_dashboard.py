"""
Leather Book Main Dashboard - Post-login interface with 6-zone layout.

Layout:
- Top Left: Stats Panel
- Middle: AI Head/Face (central visual)
- Bottom Left: User Chat Input
- Bottom Right: AI Response/Thoughts
- Top Right: Proactive AI Actions
- Background: 3D grid visualization
"""

import math
import random

from PyQt6.QtCore import QDateTime, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea,
                             QTextEdit, QVBoxLayout, QWidget)

# ============================================================================
# STYLE CONSTANTS
# ============================================================================

# Common panel stylesheet - used by StatsPanel, ProactiveActionsPanel, UserChatPanel
PANEL_STYLESHEET = """
    QFrame {
        background-color: #0f0f0f;
        border: 2px solid #00ff00;
        border-radius: 5px;
    }
"""

# Font constant - used for panel titles
TITLE_FONT = QFont("Courier New", 12, QFont.Weight.Bold)

# Color styles - used for text styling
STYLE_CYAN_GLOW = "color: #00ffff; text-shadow: 0px 0px 10px #00ffff;"
STYLE_GREEN_TEXT = "color: #00ff00;"

ACTION_BUTTON_STYLESHEET = """
    QPushButton {
        background-color: #1a1a1a;
        border: 2px solid #00ff00;
        color: #00ff00;
        padding: 8px;
        font-weight: bold;
        font-size: 10px;
    }
    QPushButton:hover {
        border: 2px solid #00ffff;
        color: #00ffff;
    }
"""

PROACTIVE_ACTIONS = (
    "Analyzing user patterns",
    "Optimizing memory cache",
    "Updating knowledge base",
    "Processing data streams",
    "Monitoring global intelligence",
    "Watch Tower security scan",
    "News intelligence updates",
)


class LeatherBookDashboard(QWidget):
    """Main dashboard with 6-zone layout on leather book."""

    send_message = pyqtSignal(str)

    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.username = username
        self.setStyleSheet(self._get_stylesheet())

        self._build_main_layout()
        self._build_top_section()
        self._build_middle_section()
        self._setup_animation_timer()

    def _build_main_layout(self) -> None:
        """Initialize the dashboard's main vertical layout."""
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

    def _build_top_section(self) -> None:
        """Construct the top row containing stats and proactive actions."""
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        top_layout.setContentsMargins(10, 10, 10, 10)

        self.stats_panel = StatsPanel(self.username)
        top_layout.addWidget(self.stats_panel, 1)

        self.actions_panel = ProactiveActionsPanel()
        top_layout.addWidget(self.actions_panel, 1)

        self._main_layout.addLayout(top_layout, 1)

    def _build_middle_section(self) -> None:
        """Construct the central layout with chat input, AI head, and responses."""
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(10)
        middle_layout.setContentsMargins(10, 10, 10, 10)

        self.chat_input = UserChatPanel()
        self.chat_input.message_sent.connect(self._on_user_message)
        middle_layout.addWidget(self.chat_input, 1)

        self.ai_head = AINeuralHead()
        middle_layout.addWidget(self.ai_head, 2)

        self.ai_response = AIResponsePanel()
        middle_layout.addWidget(self.ai_response, 1)

        self._main_layout.addLayout(middle_layout, 2)

    def _setup_animation_timer(self) -> None:
        """Wire up the animation timer that powers the dashboard background."""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animations)
        self.animation_timer.start(50)

    def _get_stylesheet(self) -> str:
        """Return stylesheet for dashboard."""
        return """
        QWidget {
            background-color: #0a0a0a;
        }
        QLabel {
            color: #00ff00;
        }
        QTextEdit {
            background-color: #1a1a1a;
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 5px;
            text-shadow: 0px 0px 5px #00ff00;
        }
        QPushButton {
            background-color: #1a1a1a;
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 8px;
            font-weight: bold;
            text-shadow: 0px 0px 5px #00ff00;
        }
        QPushButton:hover {
            background-color: #2a2a2a;
            border: 2px solid #00ffff;
            color: #00ffff;
            text-shadow: 0px 0px 10px #00ffff;
        }
        """

    def _on_user_message(self, message: str):
        """Handle user message."""
        self.send_message.emit(message)
        # Simulate AI thinking
        self.ai_head.start_thinking()
        # Add message to response panel
        self.ai_response.add_user_message(message)

    def add_ai_response(self, response: str):
        """Add AI response to display."""
        self.ai_response.add_ai_response(response)
        self.ai_head.stop_thinking()

    def _update_animations(self):
        """Update all animations."""
        self.ai_head.update()
        self.stats_panel.update()


class StatsPanel(QFrame):
    """Top left panel showing system stats."""

    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.username = username
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        self._setup_stat_labels(layout)
        layout.addStretch()
        self._configure_stats_timer()

    def _update_stats(self):
        """Update displayed stats."""
        self.uptime_seconds += 1
        self.session_seconds += 1

        self.uptime_label.setText(self._format_uptime())
        self.session_label.setText(self._format_session_duration())
        self._update_dynamic_stats()

    def _format_uptime(self) -> str:
        """Return uptime formatted as HH:MM:SS."""
        hours, remainder = divmod(self.uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}"

    def _format_session_duration(self) -> str:
        """Return session duration formatted as MM:SS."""
        minutes, seconds = divmod(self.session_seconds, 60)
        return f"Session: {minutes:02d}:{seconds:02d}"

    def _update_dynamic_stats(self) -> None:
        """Simulate variable memory and CPU usage values."""
        memory_percent = 40 + self._rng.randint(-5, 5)
        cpu_percent = 25 + self._rng.randint(-10, 15)
        self.memory_label.setText(f"Memory: {memory_percent}%")
        self.processor_label.setText(f"CPU: {cpu_percent}%")

    def _setup_stat_labels(self, layout: QVBoxLayout) -> None:
        title = QLabel("SYSTEM STATS")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(STYLE_CYAN_GLOW)
        layout.addWidget(title)

        user_label = QLabel(f"User: {self.username}")
        user_label.setStyleSheet(STYLE_GREEN_TEXT)
        layout.addWidget(user_label)

        self.uptime_label = QLabel("Uptime: 00:00:00")
        self.uptime_label.setStyleSheet(STYLE_GREEN_TEXT)
        layout.addWidget(self.uptime_label)

        self.memory_label = QLabel("Memory: 45%")
        self.memory_label.setStyleSheet(STYLE_GREEN_TEXT)
        layout.addWidget(self.memory_label)

        self.processor_label = QLabel("CPU: 32%")
        self.processor_label.setStyleSheet(STYLE_GREEN_TEXT)
        layout.addWidget(self.processor_label)

        self.session_label = QLabel("Session: 00:00")
        self.session_label.setStyleSheet(STYLE_GREEN_TEXT)
        layout.addWidget(self.session_label)

    def _configure_stats_timer(self) -> None:
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self._update_stats)
        self.stats_timer.start(1000)

        self.uptime_seconds = 0
        self.session_seconds = 0
        self._rng = random.Random()


class ProactiveActionsPanel(QFrame):
    """Top right panel showing AI proactive actions."""

    image_gen_requested = pyqtSignal()  # Signal to request image generation interface

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        layout.addWidget(self._create_title())
        layout.addWidget(self._create_action_scroll(), 1)
        layout.addWidget(self._create_action_button("▶ ANALYZE"))
        layout.addWidget(self._create_action_button("⚙ OPTIMIZE"))

        image_gen_btn = self._create_action_button("🎨 GENERATE IMAGES")
        image_gen_btn.clicked.connect(self.image_gen_requested.emit)
        layout.addWidget(image_gen_btn)

    def _create_title(self) -> QLabel:
        title = QLabel("PROACTIVE ACTIONS")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(STYLE_CYAN_GLOW)
        return title

    def _create_action_scroll(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #1a1a1a;
                border: 1px solid #00ff00;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #00ff00;
            }
        """)
        scroll.setWidgetResizable(True)

        actions_widget = QWidget()
        actions_layout = QVBoxLayout(actions_widget)
        actions_layout.setSpacing(5)

        for action in PROACTIVE_ACTIONS:
            action_item = QLabel(f"→ {action}")
            action_item.setStyleSheet("color: #00ff00; font-size: 10px;")
            actions_layout.addWidget(action_item)

        actions_layout.addStretch()
        scroll.setWidget(actions_widget)
        return scroll

    def _create_action_button(self, label: str) -> QPushButton:
        btn = QPushButton(label)
        btn.setStyleSheet(ACTION_BUTTON_STYLESHEET)
        return btn


class UserChatPanel(QFrame):
    """Bottom left panel for user chat input."""

    message_sent = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        title = QLabel("YOUR MESSAGE")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(STYLE_CYAN_GLOW)
        layout.addWidget(title)

        # Chat input
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Enter your message...")
        self.input_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                border: 2px solid #00ff00;
                color: #00ff00;
                padding: 8px;
                font-family: Courier New;
                font-size: 11px;
            }
            QTextEdit:focus {
                border: 2px solid #00ffff;
            }
        """)
        layout.addWidget(self.input_text, 1)

        # Send button
        send_btn = QPushButton("SEND ▶")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff00;
                border: 2px solid #00ff00;
                color: #000000;
                padding: 10px;
                font-weight: bold;
                font-size: 11px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #00ffff;
                border: 2px solid #00ffff;
            }
            QPushButton:pressed {
                background-color: #008800;
            }
        """)
        send_btn.clicked.connect(self._send_message)
        layout.addWidget(send_btn)

    def _send_message(self):
        """Send message."""
        text = self.input_text.toPlainText().strip()
        if text:
            self.message_sent.emit(text)
            self.input_text.clear()


class AINeuralHead(QFrame):
    """Central AI head visualization with animations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #000000;
                border: 3px solid #00ffff;
                border-radius: 10px;
            }
        """)
        self.setMinimumSize(300, 400)

        self.animation_frame = 0
        self.is_thinking = False
        self.thinking_intensity = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("NEURAL INTERFACE")
        title.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff; text-shadow: 0px 0px 10px #00ffff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Face canvas
        self.canvas = AIFaceCanvas()
        layout.addWidget(self.canvas, 1)

        # Status indicator
        self.status_label = QLabel("READY")
        self.status_label.setStyleSheet(
            "color: #00ff00; text-align: center; font-weight: bold;"
        )
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

    def start_thinking(self):
        """Start thinking animation."""
        self.is_thinking = True
        self.thinking_intensity = 0
        self.status_label.setText("THINKING...")
        self.status_label.setStyleSheet(
            "color: #ffff00; text-align: center; font-weight: bold;"
        )

    def stop_thinking(self):
        """Stop thinking animation."""
        self.is_thinking = False
        self.thinking_intensity = 0
        self.status_label.setText("RESPONDING")
        self.status_label.setStyleSheet(
            "color: #00ff00; text-align: center; font-weight: bold;"
        )

    def paintEvent(self, a0):
        """Paint the neural head."""
        super().paintEvent(a0)

        if self.is_thinking:
            self.thinking_intensity = min(self.thinking_intensity + 1, 255)
        else:
            self.thinking_intensity = max(self.thinking_intensity - 5, 0)

        self.animation_frame += 1
        self.canvas.update()


class AIFaceCanvas(QFrame):
    """Canvas for rendering AI face."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation_frame = 0
        self.setStyleSheet("background-color: #000000; border: 2px solid #00ff00;")

    def paintEvent(self, a0):
        """Paint the AI face."""
        super().paintEvent(a0)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2

        # Draw grid background
        pen = QPen(QColor(0, 255, 0, 20))
        pen.setWidth(1)
        painter.setPen(pen)
        for i in range(0, width, 30):
            painter.drawLine(i, 0, i, height)
        for i in range(0, height, 30):
            painter.drawLine(0, i, width, i)

        # Draw head (large circle)
        head_radius = 80
        painter.setPen(QPen(QColor(0, 255, 255), 3))
        painter.setBrush(QBrush(QColor(0, 50, 100, 50)))
        painter.drawEllipse(
            center_x - head_radius,
            center_y - head_radius,
            head_radius * 2,
            head_radius * 2,
        )

        # Draw eyes with glow
        eye_y = center_y - 30
        eye_radius = 12

        # Left eye
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        painter.setBrush(QBrush(QColor(0, 255, 0)))
        painter.drawEllipse(
            center_x - 40 - eye_radius,
            eye_y - eye_radius,
            eye_radius * 2,
            eye_radius * 2,
        )

        # Right eye
        painter.drawEllipse(
            center_x + 40 - eye_radius,
            eye_y - eye_radius,
            eye_radius * 2,
            eye_radius * 2,
        )

        # Draw pupil with animation
        pupil_offset = int(10 * math.sin(self.animation_frame * 0.05))
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawEllipse(center_x - 40 + pupil_offset - 5, eye_y - 5, 10, 10)
        painter.drawEllipse(center_x + 40 + pupil_offset - 5, eye_y - 5, 10, 10)

        # Draw mouth (smile)
        mouth_points = []
        for i in range(60):
            x = center_x - 30 + i
            y = center_y + 40 + int(15 * math.cos(i * 0.05))
            mouth_points.append((x, y))

        painter.setPen(QPen(QColor(0, 255, 100), 2))
        for i in range(len(mouth_points) - 1):
            painter.drawLine(
                int(mouth_points[i][0]),
                int(mouth_points[i][1]),
                int(mouth_points[i + 1][0]),
                int(mouth_points[i + 1][1]),
            )

        self.animation_frame += 1


class AIResponsePanel(QFrame):
    """Bottom right panel for AI responses."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        title = QLabel("AI RESPONSE")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(STYLE_CYAN_GLOW)
        layout.addWidget(title)

        # Response display
        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)
        self.response_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                border: 2px solid #00ff00;
                color: #00ff00;
                padding: 8px;
                font-family: Courier New;
                font-size: 10px;
            }
        """)
        layout.addWidget(self.response_text, 1)

        # Clear button
        clear_btn = QPushButton("CLEAR")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                border: 2px solid #00ff00;
                color: #00ff00;
                padding: 6px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                border: 2px solid #00ffff;
                color: #00ffff;
            }
        """)
        clear_btn.clicked.connect(self.response_text.clear)
        layout.addWidget(clear_btn)

    def add_user_message(self, message: str):
        """Add user message to response panel."""
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.response_text.append(f"[{timestamp}] USER: {message}\n")

    def add_ai_response(self, response: str):
        """Add AI response to panel."""
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.response_text.append(f"[{timestamp}] AI: {response}\n")
