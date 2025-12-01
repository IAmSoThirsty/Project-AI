"""Shared leather book panels used by the interface."""

import math

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class TronFacePage(QFrame):  # pylint: disable=too-few-public-methods
    """Left page with a Tron-styled animated face."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._configure_frame()
        self._setup_layout()
        self._start_animation()

    def _configure_frame(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #0a0a0a;
                border-right: 3px solid #00ff00;
            }
        """)
        self.setMinimumWidth(400)

    def _setup_layout(self):
        """Prepare the layout and components for the Tron face panel."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(self._create_title())
        self.face_canvas = TronFaceCanvas()
        layout.addWidget(self.face_canvas, 1)
        layout.addLayout(self._create_status_layout())

    def _create_title(self) -> QLabel:
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
        return title

    def _create_status_layout(self) -> QVBoxLayout:
        status_layout = QVBoxLayout()
        status_label = QLabel("SYSTEM STATUS")
        status_label.setStyleSheet("color: #00ffff; font-weight: bold;")
        status_layout.addWidget(status_label)
        for status_name in [
            "Neural Sync",
            "Data Stream",
            "Memory Cache",
            "Security",
        ]:
            status_layout.addWidget(StatusIndicator(status_name, True))
        return status_layout

    def _start_animation(self):
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.face_canvas.animate)
        self.animation_timer.start(50)


class TronFaceCanvas(QFrame):  # pylint: disable=too-few-public-methods
    """Canvas that paints the Tron-style face and data streams."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #000000; border: 2px solid #00ff00;")
        self.setMinimumHeight(300)
        self.animation_frame = 0

    def paintEvent(self, a0):
        """Render the Tron assets whenever Qt requests a paint."""
        super().paintEvent(a0)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._draw_grid(painter)
        self._draw_wireframe_face(painter)
        self._draw_data_streams(painter)
        painter.end()

    def _draw_grid(self, painter):
        """Paint the neon grid behind the face."""
        pen = QPen(QColor(0, 255, 0, 30))
        pen.setWidth(1)
        painter.setPen(pen)
        width = self.width()
        height = self.height()
        grid_size = 20
        for x in range(0, width, grid_size):
            painter.drawLine(x, 0, x, height)
        for y in range(0, height, grid_size):
            painter.drawLine(0, y, width, y)

    def _draw_wireframe_face(self, painter):
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        face_radius = 60
        face_color = QColor(0, 255, 255, 100)
        painter.setPen(QPen(QColor(0, 255, 255), 2))
        painter.setBrush(QBrush(face_color))
        painter.drawEllipse(
            center_x - face_radius,
            center_y - face_radius,
            face_radius * 2,
            face_radius * 2,
        )
        eye_color = QColor(0, 255, 0)
        painter.setPen(QPen(eye_color, 2))
        painter.setBrush(QBrush(eye_color))
        eye_radius = 8 + int(5 * math.sin(self.animation_frame * 0.1))
        painter.drawEllipse(
            center_x - 20 - eye_radius,
            center_y - 15 - eye_radius,
            eye_radius * 2,
            eye_radius * 2,
        )
        painter.drawEllipse(
            center_x + 20 - eye_radius,
            center_y - 15 - eye_radius,
            eye_radius * 2,
            eye_radius * 2,
        )
        mouth_width = 40
        painter.setPen(QPen(QColor(0, 255, 100), 2))
        last_point = None
        for i in range(mouth_width):
            x_offset = i - mouth_width // 2
            y_offset = int(10 * math.cos(x_offset * 0.1))
            current_point = (center_x + x_offset, center_y + 30 + y_offset)
            if last_point is not None:
                painter.drawLine(
                    int(last_point[0]),
                    int(last_point[1]),
                    int(current_point[0]),
                    int(current_point[1]),
                )
            last_point = current_point

    def _draw_data_streams(self, painter):
        """Draw the circulating data stream arcs."""
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        pen = QPen(QColor(0, 255, 100, 150))
        pen.setWidth(1)
        painter.setPen(pen)
        for angle in range(0, 360, 30):
            rad_angle = math.radians(angle + self.animation_frame * 2)
            x1 = center_x + 80 * math.cos(rad_angle)
            y1 = center_y + 80 * math.sin(rad_angle)
            x2 = center_x + 100 * math.cos(rad_angle)
            y2 = center_y + 100 * math.sin(rad_angle)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def animate(self):
        self.animation_frame += 1
        self.update()


class StatusIndicator(QFrame):
    """LED-style indicator for system status."""

    def __init__(self, name: str, status: bool = True, parent=None):
        super().__init__(parent)
        self._build_ui(name, status)

    def _build_ui(self, name: str, status: bool):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        led = QLabel("●")
        led_color = "#00ff00" if status else "#ff0000"
        led.setStyleSheet(
            f"""
            QLabel {{
                color: {led_color};
                font-size: 14px;
                text-shadow: 0px 0px 5px {led_color};
            }}
        """
        )
        led.setMaximumWidth(20)
        layout.addWidget(led)
        name_label = QLabel(name)
        name_label.setStyleSheet("color: #00ffff;")
        layout.addWidget(name_label)
        value_label = QLabel("ACTIVE" if status else "INACTIVE")
        value_label.setStyleSheet(f"color: {led_color};")
        layout.addStretch()
        layout.addWidget(value_label)


class IntroInfoPage(QFrame):
    """Right page with login, glossary, and table of contents."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.tab_buttons: list[QPushButton] = []
        self.current_tab = 0
        self.username_input: QLineEdit | None = None
        self.password_input: QLineEdit | None = None
        self._configure_frame()
        self._setup_layout()
        self.update_tab_styling()

    def _configure_frame(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #2a2a1a;
                border-left: 3px solid #8b7355;
            }
        """)

    def _setup_layout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.addWidget(self._create_title())
        layout.addWidget(self._create_divider())
        self.tabs = ["LOGIN", "GLOSSARY", "CONTENTS"]
        self.current_tab = 0
        layout.addLayout(self._create_tab_buttons())
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self._create_login_page())
        self.content_stack.addWidget(self._create_glossary_page())
        self.content_stack.addWidget(self._create_contents_page())
        layout.addWidget(self.content_stack, 1)
        layout.addWidget(self._create_footer())

    def _create_title(self) -> QLabel:
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
        return title

    def _create_divider(self) -> QFrame:
        divider = QFrame()
        divider.setStyleSheet("background-color: #8b7355; min-height: 2px;")
        return divider

    def _create_tab_buttons(self) -> QHBoxLayout:
        """Create the horizontal tab button bar."""
        tab_layout = QHBoxLayout()
        for index, tab_name in enumerate(self.tabs):
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
            btn.clicked.connect(lambda _, idx=index: self.switch_tab(idx))
            self.tab_buttons.append(btn)
            tab_layout.addWidget(btn)
        return tab_layout

    def _create_footer(self) -> QLabel:
        footer = QLabel("© 2025 Project-AI | Advanced Neural Intelligence System")
        footer.setStyleSheet("color: #8b7355; font-size: 10px; padding-top: 20px;")
        return footer

    def _create_login_page(self) -> QWidget:
        """Build the LOGIN tab content."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self._add_login_header(layout)
        self._add_login_form(layout)
        layout.addStretch()
        return page

    def _add_login_header(self, layout: QVBoxLayout):
        """Render the welcome copy above the login form."""
        welcome = QLabel("Welcome to Project-AI")
        welcome.setStyleSheet(
            "color: #8b7355; font-size: 18px; font-weight: bold;"
        )
        layout.addWidget(welcome)
        description = QLabel(
            "An advanced neural intelligence system featuring integrated "
            "learning paths, data analysis, and real-time system monitoring. "
            "The interface you see represents the convergence of analytical "
            "precision and intuitive design."
        )
        description.setWordWrap(True)
        description.setStyleSheet(
            "color: #a0a0a0; font-size: 11px; line-height: 1.6;"
        )
        layout.addWidget(description)
        layout.addSpacing(20)

    def _add_login_form(self, layout: QVBoxLayout):
        """Add username/password inputs and the submit button."""
        username_label = QLabel("Username:")
        username_label.setStyleSheet("color: #8b7355; font-weight: bold;")
        layout.addWidget(username_label)
        self.username_input = QLineEdit()
        self._style_login_input(self.username_input)
        layout.addWidget(self.username_input)
        password_label = QLabel("Password:")
        password_label.setStyleSheet("color: #8b7355; font-weight: bold;")
        layout.addWidget(password_label)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._style_login_input(self.password_input)
        layout.addWidget(self.password_input)
        layout.addSpacing(20)
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

    @staticmethod
    def _style_login_input(input_field: QLineEdit):
        input_field.setStyleSheet("""
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

    def _create_glossary_page(self) -> QWidget:
        """Create the glossary tab listing key definitions."""
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
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        title = QLabel("GLOSSARY OF TERMS")
        title.setStyleSheet(
            "color: #8b7355; font-size: 14px; font-weight: bold; margin-bottom: 10px;"
        )
        layout.addWidget(title)
        for term, definition in glossary_items:
            term_label = QLabel(f"• {term}")
            term_label.setStyleSheet(
                "color: #8b7355; font-weight: bold; padding-top: 8px;"
            )
            layout.addWidget(term_label)
            def_label = QLabel(definition)
            def_label.setWordWrap(True)
            def_label.setStyleSheet(
                "color: #a0a0a0; font-size: 10px; padding-left: 20px; padding-bottom: 8px;"
            )
            layout.addWidget(def_label)
        layout.addStretch()
        return page

    def _create_contents_page(self) -> QWidget:
        """Generate the table of contents tab entries."""
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
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        title = QLabel("TABLE OF CONTENTS")
        title.setStyleSheet(
            "color: #8b7355; font-size: 14px; font-weight: bold; margin-bottom: 10px;"
        )
        layout.addWidget(title)
        for item, description in contents_items:
            item_label = QLabel(item)
            item_label.setStyleSheet(
                "color: #8b7355; font-weight: bold; padding-top: 8px;"
            )
            layout.addWidget(item_label)
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(
                "color: #a0a0a0; font-size: 10px; padding-left: 20px; padding-bottom: 8px;"
            )
            layout.addWidget(desc_label)
        layout.addStretch()
        return page

    def switch_tab(self, tab_index: int):
        """Switch the stacked widget to the requested tab index."""
        self.current_tab = tab_index
        self.content_stack.setCurrentIndex(tab_index)
        self.update_tab_styling()

    def update_tab_styling(self):
        """Highlight the currently active tab button."""
        for index, btn in enumerate(self.tab_buttons):
            if index == self.current_tab:
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
        """Attempt to authenticate and switch to the dashboard."""
        if not self.username_input or not self.password_input:
            return
        username = self.username_input.text()
        password = self.password_input.text()
        if username and password and self.parent_window is not None:
            self.parent_window.switch_to_main_dashboard(username)
        if username:
            self.username_input.clear()
        if password:
            self.password_input.clear()
