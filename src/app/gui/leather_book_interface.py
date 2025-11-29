"""
Leather Book Interface - Main container with left/right page layout.

Creates an old leather book aesthetic with:
- Left page: Futuristic Tron-themed digital face
- Right page: User login, glossary, table of contents
- 3D elements with modern graphics
"""
import math

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class LeatherBookInterface(QMainWindow):
    """Main window with leather book aesthetic."""

    page_changed = pyqtSignal(int)  # Signal for page changes
    user_logged_in = pyqtSignal(str)  # Signal for user login

    def __init__(self, username: str | None = None):
        super().__init__()
        self.username = username
        self.current_page = 0  # 0 = login/intro, 1 = main dashboard

        # Setup window
        self.setWindowTitle("Project-AI: Leather Book Interface")
        self.setGeometry(100, 100, 1920, 1080)
        self.setStyleSheet(self._get_stylesheet())

        # Create main container
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create left page (Tron digital face)
        self.left_page = TronFacePage(self)

        # Create right page (Login/Info)
        self.right_page = IntroInfoPage(self)

        # Create stacked widget for page switching
        self.page_container = QStackedWidget()
        self.page_container.addWidget(self.right_page)  # Page 0: Intro

        # Add pages to layout
        self.main_layout.addWidget(self.left_page, 2)  # 40% width
        self.main_layout.addWidget(self.page_container, 3)  # 60% width

        # Apply leather texture effect
        self._apply_leather_texture()

        # Show main window
        self.show()

    def _get_stylesheet(self) -> str:
        """Return QSS stylesheet for leather book theme."""
        return """
        QMainWindow {
            background-color: #1a1a1a;
        }
        QLabel {
            color: #e0e0e0;
        }
        QPushButton {
            background-color: #2a2a2a;
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 8px;
            border-radius: 4px;
            font-weight: bold;
            text-shadow: 0px 0px 10px #00ff00;
        }
        QPushButton:hover {
            background-color: #3a3a3a;
            border: 2px solid #00ffff;
            color: #00ffff;
            text-shadow: 0px 0px 15px #00ffff;
        }
        QPushButton:pressed {
            background-color: #1a1a1a;
        }
        QLineEdit {
            background-color: #1a1a1a;
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 5px;
            font-weight: bold;
        }
        QLineEdit:focus {
            border: 2px solid #00ffff;
        }
        QTextEdit {
            background-color: #1a1a1a;
            border: 2px solid #00ff00;
            color: #00ff00;
        }
        """

    def _apply_leather_texture(self):
        """Apply leather texture and shadows."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(0, 10)
        self.main_widget.setGraphicsEffect(shadow)

    def switch_to_main_dashboard(self, username: str):
        """Switch from intro page to main dashboard."""
        self.username = username
        self.user_logged_in.emit(username)

        # Import and create dashboard
        from leather_book_dashboard import LeatherBookDashboard

        # Create dashboard
        dashboard = LeatherBookDashboard(username)

        # Connect image generation signal
        dashboard.actions_panel.image_gen_requested.connect(self.switch_to_image_generation)

        # Add to page container
        if self.page_container.count() > 1:
            self.page_container.removeWidget(self.page_container.widget(1))

        self.page_container.addWidget(dashboard)
        self.page_container.setCurrentIndex(1)
        self.current_page = 1

    def switch_to_image_generation(self):
        """Switch to image generation interface."""
        from app.gui.image_generation import ImageGenerationInterface

        # Create image generation interface
        image_gen = ImageGenerationInterface()

        # Add to page container
        if self.page_container.count() > 2:
            self.page_container.removeWidget(self.page_container.widget(2))

        self.page_container.addWidget(image_gen)
        self.page_container.setCurrentIndex(2)
        self.current_page = 2

    def switch_to_dashboard(self):
        """Switch back to dashboard."""
        if self.page_container.count() > 1:
            self.page_container.setCurrentIndex(1)
            self.current_page = 1


class TronFacePage(QFrame):
    """Left page with 3D animated Tron digital face."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #0a0a0a;
                border-right: 3px solid #00ff00;
            }
        """)
        self.setMinimumWidth(400)

        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("NEURAL INTERFACE")
        title_font = QFont("Courier New", 16, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("""
            QLabel {
                color: #00ff00;
                text-shadow: 0px 0px 10px #00ff00;
                padding: 10px;
            }
        """)
        layout.addWidget(title)

        # Digital face canvas
        self.face_canvas = TronFaceCanvas()
        layout.addWidget(self.face_canvas, 1)

        # Status indicators
        status_layout = QVBoxLayout()

        # System status
        status_label = QLabel("SYSTEM STATUS")
        status_label.setStyleSheet("color: #00ffff; font-weight: bold;")
        status_layout.addWidget(status_label)

        # Individual status lights
        for status_name in [
            "Neural Sync",
            "Data Stream",
            "Memory Cache",
                "Security"]:
            status_item = StatusIndicator(status_name, True)
            status_layout.addWidget(status_item)

        layout.addLayout(status_layout)

        # Startup animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.face_canvas.animate)
        self.animation_timer.start(50)


class TronFaceCanvas(QFrame):
    """Canvas for rendering 3D Tron face."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "background-color: #000000; border: 2px solid #00ff00;")
        self.setMinimumHeight(300)
        self.animation_frame = 0

    def paintEvent(self, a0):
        """Paint the Tron digital face."""
        super().paintEvent(a0)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw grid background
        self._draw_grid(painter)

        # Draw digital face (wireframe style)
        self._draw_wireframe_face(painter)

        # Draw data streams
        self._draw_data_streams(painter)

        painter.end()

    def _draw_grid(self, painter):
        """Draw Tron-style grid background."""
        pen = QPen(QColor(0, 255, 0, 30))
        pen.setWidth(1)
        painter.setPen(pen)

        width = self.width()
        height = self.height()
        grid_size = 20

        # Vertical lines
        for x in range(0, width, grid_size):
            painter.drawLine(x, 0, x, height)

        # Horizontal lines
        for y in range(0, height, grid_size):
            painter.drawLine(0, y, width, y)

    def _draw_wireframe_face(self, painter):
        """Draw a simple wireframe face in center."""
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2

        # Head circle
        face_radius = 60
        face_color = QColor(0, 255, 255, 100)
        painter.setPen(QPen(QColor(0, 255, 255), 2))
        painter.setBrush(QBrush(face_color))
        painter.drawEllipse(center_x - face_radius, center_y - face_radius,
                            face_radius * 2, face_radius * 2)

        # Eyes
        eye_color = QColor(0, 255, 0)
        painter.setPen(QPen(eye_color, 2))
        painter.setBrush(QBrush(eye_color))
        eye_radius = 8 + int(5 * math.sin(self.animation_frame * 0.1))
        painter.drawEllipse(
            center_x - 20 - eye_radius,
            center_y - 15 - eye_radius,
            eye_radius * 2,
            eye_radius * 2)
        painter.drawEllipse(
            center_x + 20 - eye_radius,
            center_y - 15 - eye_radius,
            eye_radius * 2,
            eye_radius * 2)

        # Mouth (digital smile)
        mouth_width = 40
        mouth_points = []
        for i in range(mouth_width):
            x_offset = i - mouth_width // 2
            y_offset = int(10 * math.cos(x_offset * 0.1))
            mouth_points.append(
                (center_x + x_offset, center_y + 30 + y_offset))

        painter.setPen(QPen(QColor(0, 255, 100), 2))
        for i in range(len(mouth_points) - 1):
            painter.drawLine(int(mouth_points[i][0]), int(mouth_points[i][1]), int(
                mouth_points[i + 1][0]), int(mouth_points[i + 1][1]))

    def _draw_data_streams(self, painter):
        """Draw animated data streams around face."""
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2

        pen = QPen(QColor(0, 255, 100, 150))
        pen.setWidth(1)
        painter.setPen(pen)

        # Draw rotating orbital lines
        for angle in range(0, 360, 30):
            rad_angle = math.radians(angle + self.animation_frame * 2)
            x1 = center_x + 80 * math.cos(rad_angle)
            y1 = center_y + 80 * math.sin(rad_angle)
            x2 = center_x + 100 * math.cos(rad_angle)
            y2 = center_y + 100 * math.sin(rad_angle)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def animate(self):
        """Update animation frame."""
        self.animation_frame += 1
        self.update()


class StatusIndicator(QFrame):
    """Individual status indicator with LED-like appearance."""

    def __init__(self, name: str, status: bool = True, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # LED indicator
        led = QLabel("●")
        led_color = "#00ff00" if status else "#ff0000"
        led.setStyleSheet(f"""
            QLabel {{
                color: {led_color};
                font-size: 14px;
                text-shadow: 0px 0px 5px {led_color};
            }}
        """)
        led.setMaximumWidth(20)
        layout.addWidget(led)

        # Status name
        name_label = QLabel(name)
        name_label.setStyleSheet("color: #00ffff;")
        layout.addWidget(name_label)

        # Status value
        value_label = QLabel("ACTIVE" if status else "INACTIVE")
        value_label.setStyleSheet(f"color: {led_color};")
        layout.addStretch()
        layout.addWidget(value_label)


class IntroInfoPage(QFrame):
    """Right page with login, glossary, and table of contents."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent

        self.setStyleSheet("""
            QFrame {
                background-color: #2a2a1a;
                border-left: 3px solid #8b7355;
            }
        """)

        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel("PROJECT-AI")
        title_font = QFont("Georgia", 24, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("""
            QLabel {
                color: #8b7355;
                text-shadow: 0px 2px 4px #000000;
                padding: 10px;
            }
        """)
        layout.addWidget(title)

        # Divider
        divider = QFrame()
        divider.setStyleSheet("background-color: #8b7355; min-height: 2px;")
        layout.addWidget(divider)

        # Create tabs for different sections
        self.tabs = ["LOGIN", "GLOSSARY", "CONTENTS"]
        self.current_tab = 0

        # Tab buttons
        tab_layout = QHBoxLayout()
        self.tab_buttons = []
        for i, tab_name in enumerate(self.tabs):
            btn = QPushButton(tab_name)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #8b7355;
                    padding: 8px;
                    text-decoration: underline;
                    font-weight: bold;
                }
                QPushButton:hover {
                    color: #a0826d;
                }
            """)
            btn.clicked.connect(lambda checked, idx=i: self.switch_tab(idx))
            self.tab_buttons.append(btn)
            tab_layout.addWidget(btn)
        layout.addLayout(tab_layout)

        # Content area
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self._create_login_page())
        self.content_stack.addWidget(self._create_glossary_page())
        self.content_stack.addWidget(self._create_contents_page())
        layout.addWidget(self.content_stack, 1)

        # Footer
        footer = QLabel(
            "© 2025 Project-AI | Advanced Neural Intelligence System")
        footer.setStyleSheet(
            "color: #8b7355; font-size: 10px; padding-top: 20px;")
        layout.addWidget(footer)

        self.update_tab_styling()

    def _create_login_page(self) -> QWidget:
        """Create login page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Welcome text
        welcome = QLabel("Welcome to Project-AI")
        welcome.setStyleSheet(
            "color: #8b7355; font-size: 18px; font-weight: bold;")
        layout.addWidget(welcome)

        description = QLabel(
            "An advanced neural intelligence system featuring integrated "
            "learning paths, data analysis, and real-time system monitoring. "
            "The interface you see represents the convergence of analytical "
            "precision and intuitive design."
        )
        description.setWordWrap(True)
        description.setStyleSheet(
            "color: #a0a0a0; font-size: 11px; line-height: 1.6;")
        layout.addWidget(description)

        layout.addSpacing(20)

        # Login form
        from PyQt6.QtWidgets import QLineEdit

        username_label = QLabel("Username:")
        username_label.setStyleSheet("color: #8b7355; font-weight: bold;")
        layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a0f;
                border: 2px solid #8b7355;
                color: #e0e0e0;
                padding: 8px;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 2px solid #a0826d;
            }
        """)
        layout.addWidget(self.username_input)

        password_label = QLabel("Password:")
        password_label.setStyleSheet("color: #8b7355; font-weight: bold;")
        layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a0f;
                border: 2px solid #8b7355;
                color: #e0e0e0;
                padding: 8px;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 2px solid #a0826d;
            }
        """)
        layout.addWidget(self.password_input)

        layout.addSpacing(20)

        # Login button
        login_btn = QPushButton("ENTER SYSTEM")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b7355;
                border: 2px solid #8b7355;
                color: #ffffff;
                padding: 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #a0826d;
                border: 2px solid #a0826d;
            }
        """)
        login_btn.clicked.connect(self._handle_login)
        layout.addWidget(login_btn)

        layout.addStretch()

        return page

    def _create_glossary_page(self) -> QWidget:
        """Create glossary page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("GLOSSARY OF TERMS")
        title.setStyleSheet(
            "color: #8b7355; font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        glossary_items = [
            ("Neural Interface", "Core system for AI communication and decision processing"),
            ("Intent Detector", "Analyzes user input to determine underlying intentions"),
            ("Learning Paths", "Personalized educational sequences adapted to user progress"),
            ("Data Analyzer", "Processes and visualizes complex datasets in real-time"),
            ("Security Manager", "Maintains system integrity and access controls"),
            ("Memory Expansion", "Extends processing capabilities through dynamic memory allocation"),
            ("Command Override", "Emergency system control for critical situations"),
            ("Location Tracker", "Geographic and contextual position monitoring"),
        ]

        for term, definition in glossary_items:
            term_label = QLabel(f"• {term}")
            term_label.setStyleSheet(
                "color: #8b7355; font-weight: bold; padding-top: 8px;")
            layout.addWidget(term_label)

            def_label = QLabel(definition)
            def_label.setWordWrap(True)
            def_label.setStyleSheet(
                "color: #a0a0a0; font-size: 10px; padding-left: 20px; padding-bottom: 8px;")
            layout.addWidget(def_label)

        layout.addStretch()
        return page

    def _create_contents_page(self) -> QWidget:
        """Create table of contents page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("TABLE OF CONTENTS")
        title.setStyleSheet(
            "color: #8b7355; font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        contents_items = [
            ("1. System Overview", "Neural Interface Architecture and Core Components"),
            ("2. User Management", "Account Management and Security Protocols"),
            ("3. AI Learning", "Adaptive Learning Paths and Knowledge Expansion"),
            ("4. Data Analysis", "Analytics Dashboard and Visualization Tools"),
            ("5. System Monitoring", "Real-time Monitoring and Emergency Protocols"),
            ("6. Settings & Configuration", "Customization and System Preferences"),
            ("7. Advanced Features", "Extended Capabilities and Integration Options"),
            ("8. Support & Documentation", "Help Resources and Technical References"),
        ]

        for item, description in contents_items:
            item_label = QLabel(item)
            item_label.setStyleSheet(
                "color: #8b7355; font-weight: bold; padding-top: 8px;")
            layout.addWidget(item_label)

            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(
                "color: #a0a0a0; font-size: 10px; padding-left: 20px; padding-bottom: 8px;")
            layout.addWidget(desc_label)

        layout.addStretch()
        return page

    def switch_tab(self, tab_index: int):
        """Switch to different tab."""
        self.current_tab = tab_index
        self.content_stack.setCurrentIndex(tab_index)
        self.update_tab_styling()

    def update_tab_styling(self):
        """Update styling for active tab."""
        for i, btn in enumerate(self.tab_buttons):
            if i == self.current_tab:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        color: #a0826d;
                        padding: 8px;
                        text-decoration: underline;
                        font-weight: bold;
                        border-bottom: 2px solid #8b7355;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        color: #8b7355;
                        padding: 8px;
                        text-decoration: none;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        color: #a0826d;
                    }
                """)

    def _handle_login(self):
        """Handle login button click."""
        username = self.username_input.text()
        password = self.password_input.text()

        if username and password:
            if self.parent_window is not None:
                self.parent_window.switch_to_main_dashboard(username)
            # Reset fields
            self.username_input.clear()
            self.password_input.clear()
        else:
            # Show error
            pass
