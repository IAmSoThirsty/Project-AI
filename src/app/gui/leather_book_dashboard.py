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

from PyQt6.QtCore import QTimer, Qt, QRect, QSize, pyqtSignal, QThread, QObject, QDateTime
from PyQt6.QtGui import QColor, QPainter, QFont, QPen, QBrush, QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QFrame, QScrollArea, QStackedWidget, QListWidget, QListWidgetItem
)
import math


class LeatherBookDashboard(QWidget):
    """Main dashboard with 6-zone layout on leather book."""
    
    send_message = pyqtSignal(str)
    
    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.username = username
        self.setStyleSheet(self._get_stylesheet())
        
        # Main layout - vertical split
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top section (Stats + Top Right Actions)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        top_layout.setContentsMargins(10, 10, 10, 10)
        
        # Top Left: Stats Panel
        self.stats_panel = StatsPanel(username)
        top_layout.addWidget(self.stats_panel, 1)
        
        # Top Right: Proactive Actions
        self.actions_panel = ProactiveActionsPanel()
        top_layout.addWidget(self.actions_panel, 1)
        
        main_layout.addLayout(top_layout, 1)
        
        # Middle section - AI Head and chat interface
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(10)
        middle_layout.setContentsMargins(10, 10, 10, 10)
        
        # Bottom Left: User Chat Input
        self.chat_input = UserChatPanel()
        self.chat_input.message_sent.connect(self._on_user_message)
        middle_layout.addWidget(self.chat_input, 1)
        
        # Center: AI Head
        self.ai_head = AINeuralHead()
        middle_layout.addWidget(self.ai_head, 2)
        
        # Bottom Right: AI Response/Thoughts
        self.ai_response = AIResponsePanel()
        middle_layout.addWidget(self.ai_response, 1)
        
        main_layout.addLayout(middle_layout, 2)
        
        # Background grid animation
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
        self.setStyleSheet("""
            QFrame {
                background-color: #0f0f0f;
                border: 2px solid #00ff00;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("SYSTEM STATS")
        title.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff; text-shadow: 0px 0px 10px #00ffff;")
        layout.addWidget(title)
        
        # User info
        user_label = QLabel(f"User: {username}")
        user_label.setStyleSheet("color: #00ff00;")
        layout.addWidget(user_label)
        
        # System uptime
        self.uptime_label = QLabel("Uptime: 00:00:00")
        self.uptime_label.setStyleSheet("color: #00ff00;")
        layout.addWidget(self.uptime_label)
        
        # Memory usage
        self.memory_label = QLabel("Memory: 45%")
        self.memory_label.setStyleSheet("color: #00ff00;")
        layout.addWidget(self.memory_label)
        
        # Processor
        self.processor_label = QLabel("CPU: 32%")
        self.processor_label.setStyleSheet("color: #00ff00;")
        layout.addWidget(self.processor_label)
        
        # Session time
        self.session_label = QLabel("Session: 00:00")
        self.session_label.setStyleSheet("color: #00ff00;")
        layout.addWidget(self.session_label)
        
        layout.addStretch()
        
        # Update stats timer
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self._update_stats)
        self.stats_timer.start(1000)
        
        self.uptime_seconds = 0
        self.session_seconds = 0
    
    def _update_stats(self):
        """Update displayed stats."""
        self.uptime_seconds += 1
        self.session_seconds += 1
        
        # Format as HH:MM:SS
        hours = self.uptime_seconds // 3600
        minutes = (self.uptime_seconds % 3600) // 60
        seconds = self.uptime_seconds % 60
        self.uptime_label.setText(f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Session
        sess_minutes = self.session_seconds // 60
        sess_seconds = self.session_seconds % 60
        self.session_label.setText(f"Session: {sess_minutes:02d}:{sess_seconds:02d}")
        
        # Simulate dynamic stats
        import random
        self.memory_label.setText(f"Memory: {40 + random.randint(-5, 5)}%")
        self.processor_label.setText(f"CPU: {25 + random.randint(-10, 15)}%")


class ProactiveActionsPanel(QFrame):
    """Top right panel showing AI proactive actions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #0f0f0f;
                border: 2px solid #00ff00;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("PROACTIVE ACTIONS")
        title.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff; text-shadow: 0px 0px 10px #00ffff;")
        layout.addWidget(title)
        
        # Action list with scroll
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
        
        # Sample actions
        actions = [
            "Analyzing user patterns",
            "Optimizing memory cache",
            "Updating knowledge base",
            "Processing data streams",
        ]
        
        for action in actions:
            action_item = QLabel(f"→ {action}")
            action_item.setStyleSheet("color: #00ff00; font-size: 10px;")
            actions_layout.addWidget(action_item)
        
        actions_layout.addStretch()
        scroll.setWidget(actions_widget)
        layout.addWidget(scroll, 1)
        
        # Action buttons
        analyze_btn = QPushButton("▶ ANALYZE")
        analyze_btn.setStyleSheet("""
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
        """)
        layout.addWidget(analyze_btn)
        
        optimize_btn = QPushButton("⚙ OPTIMIZE")
        optimize_btn.setStyleSheet("""
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
        """)
        layout.addWidget(optimize_btn)


class UserChatPanel(QFrame):
    """Bottom left panel for user chat input."""
    
    message_sent = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #0f0f0f;
                border: 2px solid #00ff00;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("YOUR MESSAGE")
        title.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff; text-shadow: 0px 0px 10px #00ffff;")
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
        self.status_label.setStyleSheet("color: #00ff00; text-align: center; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
    
    def start_thinking(self):
        """Start thinking animation."""
        self.is_thinking = True
        self.thinking_intensity = 0
        self.status_label.setText("THINKING...")
        self.status_label.setStyleSheet("color: #ffff00; text-align: center; font-weight: bold;")
    
    def stop_thinking(self):
        """Stop thinking animation."""
        self.is_thinking = False
        self.thinking_intensity = 0
        self.status_label.setText("RESPONDING")
        self.status_label.setStyleSheet("color: #00ff00; text-align: center; font-weight: bold;")
    
    def paintEvent(self, event):
        """Paint the neural head."""
        super().paintEvent(event)
        
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
    
    def paintEvent(self, event):
        """Paint the AI face."""
        super().paintEvent(event)
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
        painter.drawEllipse(center_x - head_radius, center_y - head_radius,
                           head_radius * 2, head_radius * 2)
        
        # Draw eyes with glow
        eye_y = center_y - 30
        eye_radius = 12
        
        # Left eye
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        painter.setBrush(QBrush(QColor(0, 255, 0)))
        painter.drawEllipse(center_x - 40 - eye_radius, eye_y - eye_radius,
                           eye_radius * 2, eye_radius * 2)
        
        # Right eye
        painter.drawEllipse(center_x + 40 - eye_radius, eye_y - eye_radius,
                           eye_radius * 2, eye_radius * 2)
        
        # Draw pupil with animation
        pupil_offset = int(10 * math.sin(self.animation_frame * 0.05))
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawEllipse(center_x - 40 + pupil_offset - 5, eye_y - 5,
                           10, 10)
        painter.drawEllipse(center_x + 40 + pupil_offset - 5, eye_y - 5,
                           10, 10)
        
        # Draw mouth (smile)
        mouth_points = []
        for i in range(60):
            x = center_x - 30 + i
            y = center_y + 40 + int(15 * math.cos(i * 0.05))
            mouth_points.append((x, y))
        
        painter.setPen(QPen(QColor(0, 255, 100), 2))
        for i in range(len(mouth_points) - 1):
            painter.drawLine(int(mouth_points[i][0]), int(mouth_points[i][1]),
                            int(mouth_points[i+1][0]), int(mouth_points[i+1][1]))
        
        self.animation_frame += 1


class AIResponsePanel(QFrame):
    """Bottom right panel for AI responses."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #0f0f0f;
                border: 2px solid #00ff00;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("AI RESPONSE")
        title.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff; text-shadow: 0px 0px 10px #00ffff;")
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
