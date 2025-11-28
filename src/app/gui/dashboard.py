"""
Main dashboard window implementation.
Mass Effect / Sci-Fi themed interface with digital AI face construct.
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QLabel,
    QComboBox,
    QListWidget,
    QGraphicsOpacityEffect,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import QTimer, QPropertyAnimation, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray
import os
import base64
from app.core.user_manager import UserManager
from app.core.intent_detection import IntentDetector
from app.core.learning_paths import LearningPathManager
from app.core.data_analysis import DataAnalyzer
from app.core.security_resources import SecurityResourceManager
from app.core.location_tracker import LocationTracker
from app.core.emergency_alert import EmergencyAlert
from app.gui.dashboard_handlers import DashboardHandlers


class DashboardWindow(DashboardHandlers, QMainWindow):
    def __init__(self, username: str = None, initial_tab: int = 0):
        super().__init__()
        # Initialize core components
        self.user_manager = UserManager()
        self.intent_detector = IntentDetector()
        self.learning_manager = LearningPathManager()
        self.data_analyzer = DataAnalyzer()
        self.security_manager = SecurityResourceManager()
        self.location_tracker = LocationTracker()
        self.emergency_alert = EmergencyAlert()

        # Setup timers
        self.location_timer = QTimer()
        self.location_timer.timeout.connect(self.update_location)

        # If username provided, set current user
        if username:
            self.user_manager.current_user = username

        self.setup_ui()
        # Select initial chapter/tab (book-like)
        try:
            self.tabs.setCurrentIndex(initial_tab)
        except Exception:
            pass
        # Initialize page number
        self.update_page_number(self.tabs.currentIndex())

    def update_page_number(self, index: int):
        """Update the footer with current tab info (sci-fi style)."""
        total = max(1, self.tabs.count())
        tab_name = self.tabs.tabText(index) if index >= 0 else ""
        try:
            self.statusBar().showMessage(f"◈ {tab_name} | Tab {index+1} of {total} | System Online")
        except Exception:
            self.statusBar().showMessage("")

    def animate_tab_change(self, index: int):
        """Apply a quick fade-in animation for holographic transition effect."""
        try:
            widget = self.tabs.widget(index)
            if widget is None:
                return
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            anim = QPropertyAnimation(effect, b"opacity", self)
            anim.setDuration(300)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.start(QPropertyAnimation.DeleteWhenStopped)
        except Exception:
            # animations are cosmetic; ignore errors
            pass

    def setup_ui(self):
        """Setup the user interface with Sci-Fi theme"""
        self.setWindowTitle("AI Assistant")
        self.setGeometry(100, 100, 1200, 800)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Load sci-fi themed QSS stylesheet
        try:
            qss_path = os.path.join(os.path.dirname(__file__), 'styles.qss')
            if os.path.exists(qss_path):
                with open(qss_path, 'r', encoding='utf-8') as f:
                    qss = f.read()

                # Embed sci-fi assets as data URIs
                assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
                # Sci-fi background
                scifi_bg_path = os.path.join(assets_dir, 'scifi_background.svg')
                if os.path.exists(scifi_bg_path):
                    with open(scifi_bg_path, 'rb') as af:
                        bgdata = base64.b64encode(af.read()).decode('ascii')
                        data_uri = f'data:image/svg+xml;base64,{bgdata}'
                        qss = qss.replace('{SCIFI_BG}', data_uri)

                self.setStyleSheet(qss)
            else:
                # Fallback inline sci-fi style
                self.setStyleSheet("""
                    QMainWindow { background-color: #0a0e17; }
                    QWidget { color: #e0f4ff; }
                    QTabWidget::pane {
                        border: 1px solid rgba(0, 200, 255, 0.3);
                        background: rgba(10, 20, 40, 0.95);
                    }
                    QTabBar::tab {
                        background: #1a2a4a; color: #80c0e0;
                        padding: 12px; margin: 2px; border-radius: 4px;
                    }
                    QTabBar::tab:selected {
                        background: #1a3a60; color: #00d4ff; font-weight: bold;
                    }
                    QPushButton {
                        background-color: #1a3050; color: #00d4ff;
                        border: 1px solid rgba(0, 200, 255, 0.5);
                        border-radius: 4px; padding: 8px;
                    }
                    QPushButton#alert_button {
                        background-color: #8a2020; color: #ff4040;
                    }
                    QLineEdit, QTextEdit {
                        background: rgba(10, 20, 35, 0.9);
                        color: #c0e8ff;
                        border: 1px solid rgba(0, 180, 255, 0.3);
                    }
                """)
        except Exception:
            # If styling fails, apply basic sci-fi colors
            pass

        # Status bar with sci-fi styling
        self.statusBar().showMessage("System Online")
        # Update status and animate on tab change
        self.tabs.currentChanged.connect(self.update_page_number)
        self.tabs.currentChanged.connect(self.animate_tab_change)

        # Add tabs
        self.setup_chat_tab()
        self.setup_learning_paths_tab()
        self.setup_data_analysis_tab()
        self.setup_security_tab()
        self.setup_location_tab()
        self.setup_emergency_tab()
        # Add Users management tab if widget is available
        try:
            from app.gui.user_management import UserManagementWidget
            self.user_mgmt = UserManagementWidget()
            self.tabs.addTab(self.user_mgmt, "Users")
        except Exception:
            # non-fatal: keep going without Users tab
            pass

    def _load_ai_face_svg(self) -> QPixmap:
        """Load the AI face SVG and return as QPixmap."""
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        ai_face_path = os.path.join(assets_dir, 'ai_face.svg')
        pixmap = QPixmap(150, 150)
        pixmap.fill(Qt.GlobalColor.transparent)

        if os.path.exists(ai_face_path):
            try:
                with open(ai_face_path, 'rb') as f:
                    svg_data = f.read()
                renderer = QSvgRenderer(QByteArray(svg_data))
                from PyQt6.QtGui import QPainter
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
            except Exception:
                pass
        return pixmap

    def setup_chat_tab(self):
        """Setup the chat interface tab with AI digital face construct and status monitors."""
        chat_tab = QWidget()
        main_layout = QVBoxLayout(chat_tab)

        # Top section: AI Face and system monitors
        top_section = QHBoxLayout()

        # AI Face display (digital construct)
        ai_frame = QFrame()
        ai_frame.setObjectName("ai_face_frame")
        ai_frame.setFixedSize(160, 160)
        ai_layout = QVBoxLayout(ai_frame)
        ai_layout.setContentsMargins(5, 5, 5, 5)

        self.ai_face_label = QLabel()
        self.ai_face_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ai_pixmap = self._load_ai_face_svg()
        self.ai_face_label.setPixmap(ai_pixmap)
        ai_layout.addWidget(self.ai_face_label)

        top_section.addWidget(ai_frame)

        # System Status Monitors Panel
        monitors_panel = QVBoxLayout()

        # AI Status header
        ai_status_header = QLabel("◈ AI ASSISTANT STATUS ◈")
        ai_status_header.setStyleSheet("""
            color: #00d4ff;
            font-size: 14px;
            font-weight: bold;
            padding: 4px 8px;
        """)
        monitors_panel.addWidget(ai_status_header)

        # Status monitor frame
        status_monitor = QFrame()
        status_monitor.setStyleSheet("""
            QFrame {
                background: rgba(10, 25, 45, 0.8);
                border: 1px solid rgba(0, 200, 255, 0.4);
                border-radius: 4px;
                padding: 8px;
            }
        """)
        status_layout = QVBoxLayout(status_monitor)
        status_layout.setSpacing(4)

        # System status indicators
        self.status_online = QLabel("● SYSTEM STATUS: ONLINE")
        self.status_online.setStyleSheet("color: #40ff80; font-size: 11px;")
        status_layout.addWidget(self.status_online)

        self.status_memory = QLabel("● MEMORY: NOMINAL")
        self.status_memory.setStyleSheet("color: #40ff80; font-size: 11px;")
        status_layout.addWidget(self.status_memory)

        self.status_network = QLabel("● NETWORK: CONNECTED")
        self.status_network.setStyleSheet("color: #40ff80; font-size: 11px;")
        status_layout.addWidget(self.status_network)

        self.status_ai = QLabel("● AI CORE: READY")
        self.status_ai.setStyleSheet("color: #00d4ff; font-size: 11px;")
        status_layout.addWidget(self.status_ai)

        monitors_panel.addWidget(status_monitor)
        monitors_panel.addStretch()

        top_section.addLayout(monitors_panel)

        # Right side: Additional stats panel
        stats_panel = QVBoxLayout()

        stats_header = QLabel("◈ SYSTEM METRICS ◈")
        stats_header.setStyleSheet("""
            color: #00d4ff;
            font-size: 14px;
            font-weight: bold;
            padding: 4px 8px;
        """)
        stats_panel.addWidget(stats_header)

        # Stats monitor frame
        stats_monitor = QFrame()
        stats_monitor.setStyleSheet("""
            QFrame {
                background: rgba(10, 25, 45, 0.8);
                border: 1px solid rgba(0, 200, 255, 0.4);
                border-radius: 4px;
                padding: 8px;
            }
        """)
        stats_inner = QVBoxLayout(stats_monitor)
        stats_inner.setSpacing(4)

        self.stat_uptime = QLabel("◆ UPTIME: 00:00:00")
        self.stat_uptime.setStyleSheet("color: #a0d4ff; font-size: 11px;")
        stats_inner.addWidget(self.stat_uptime)

        self.stat_messages = QLabel("◆ MESSAGES: 0")
        self.stat_messages.setStyleSheet("color: #a0d4ff; font-size: 11px;")
        stats_inner.addWidget(self.stat_messages)

        self.stat_response = QLabel("◆ AVG RESPONSE: <1ms")
        self.stat_response.setStyleSheet("color: #a0d4ff; font-size: 11px;")
        stats_inner.addWidget(self.stat_response)

        self.stat_user = QLabel(f"◆ USER: {self.user_manager.current_user or 'GUEST'}")
        self.stat_user.setStyleSheet("color: #80c0e0; font-size: 11px;")
        stats_inner.addWidget(self.stat_user)

        stats_panel.addWidget(stats_monitor)
        stats_panel.addStretch()

        top_section.addLayout(stats_panel)
        top_section.addStretch()

        main_layout.addLayout(top_section)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("""
            background-color: rgba(0, 200, 255, 0.3);
            max-height: 2px;
            margin: 10px 0;
        """)
        main_layout.addWidget(separator)

        # Chat display with styled object name
        self.chat_display = QTextEdit()
        self.chat_display.setObjectName("ai_chat_display")
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText(
            "◈ COMMUNICATION TERMINAL ACTIVE ◈\n\n"
            "Type your message below to interact with the AI Assistant."
        )
        main_layout.addWidget(self.chat_display)

        # Input area with sci-fi styling
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Enter your message...")
        self.chat_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.chat_input)

        # Send button with sci-fi styling
        send_button = QPushButton("Send")
        send_button.setMinimumWidth(100)
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button)

        main_layout.addLayout(input_layout)

        # Message counter for stats
        self.message_count = 0

        self.tabs.addTab(chat_tab, "Chat")

    def setup_tasks_tab(self):
        """Setup the tasks management tab"""
        tasks_tab = QWidget()
        layout = QVBoxLayout(tasks_tab)

        # Tasks list
        self.tasks_display = QTextEdit()
        layout.addWidget(self.tasks_display)

        # Add task button
        add_task_button = QPushButton("Add Task")
        add_task_button.clicked.connect(self.add_task)
        layout.addWidget(add_task_button)

        self.tabs.addTab(tasks_tab, "Chapter 2 — Tasks")

    def setup_learning_paths_tab(self):
        """Setup the learning paths tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Interest input
        interest_label = QLabel("What would you like to learn?")
        layout.addWidget(interest_label)

        self.interest_input = QLineEdit()
        self.interest_input.setPlaceholderText("Enter skill or knowledge area...")
        layout.addWidget(self.interest_input)

        # Skill level selection
        level_label = QLabel("Select your skill level:")
        layout.addWidget(level_label)

        self.skill_level = QComboBox()
        self.skill_level.addItems(["Beginner", "Intermediate", "Advanced"])
        layout.addWidget(self.skill_level)

        # Generate button
        generate_button = QPushButton("Generate Learning Path")
        generate_button.clicked.connect(self.generate_learning_path)
        layout.addWidget(generate_button)

        # Display area
        self.learning_path_display = QTextEdit()
        self.learning_path_display.setReadOnly(True)
        self.learning_path_display.setPlaceholderText(
            "Learning path will be displayed here..."
        )
        layout.addWidget(self.learning_path_display)

        self.tabs.addTab(tab, "Learning Paths")

    def setup_data_analysis_tab(self):
        """Setup the data analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # File selection
        load_button = QPushButton("Load Data File")
        load_button.clicked.connect(self.load_data_file)
        layout.addWidget(load_button)

        # Analysis options
        analysis_label = QLabel("Select Analysis Type:")
        layout.addWidget(analysis_label)
        self.analysis_type = QComboBox()
        self.analysis_type.addItems([
            "Basic Stats",
            "Scatter Plot",
            "Histogram",
            "Box Plot",
            "Correlation",
            "Clustering"
        ])
        layout.addWidget(self.analysis_type)

        # Column selection
        column_label = QLabel("Select Column:")
        layout.addWidget(column_label)
        self.column_selector = QComboBox()
        layout.addWidget(self.column_selector)

        # Analyze button
        analyze_button = QPushButton("Analyze")
        analyze_button.clicked.connect(self.perform_analysis)
        layout.addWidget(analyze_button)

        # Results display
        self.analysis_display = QTextEdit()
        self.analysis_display.setReadOnly(True)
        self.analysis_display.setPlaceholderText(
            "Analysis results will be displayed here..."
        )
        layout.addWidget(self.analysis_display)

        self.tabs.addTab(tab, "Data Analysis")

    def setup_security_tab(self):
        """Setup the security resources tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Category selection
        category_label = QLabel("Select Category:")
        layout.addWidget(category_label)
        self.security_category = QComboBox()
        self.security_category.addItems(self.security_manager.get_all_categories())
        self.security_category.currentTextChanged.connect(self.update_security_resources)
        layout.addWidget(self.security_category)

        # Resources list
        resources_label = QLabel("Available Resources:")
        layout.addWidget(resources_label)
        self.resources_list = QListWidget()
        self.resources_list.itemDoubleClicked.connect(self.open_security_resource)
        layout.addWidget(self.resources_list)

        # Favorite button
        favorite_button = QPushButton("Add to Favorites")
        favorite_button.clicked.connect(self.add_security_favorite)
        layout.addWidget(favorite_button)

        self.tabs.addTab(tab, "Security Resources")
        self.update_security_resources()

    def setup_location_tab(self):
        """Setup the location tracking tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Location toggle
        self.location_toggle = QPushButton("Start Location Tracking")
        self.location_toggle.clicked.connect(self.toggle_location_tracking)
        layout.addWidget(self.location_toggle)

        # Current location display
        location_label = QLabel("Current Location:")
        layout.addWidget(location_label)
        self.location_display = QTextEdit()
        self.location_display.setReadOnly(True)
        self.location_display.setPlaceholderText(
            "Location data will be displayed when tracking is active..."
        )
        layout.addWidget(self.location_display)

        # Location history
        history_label = QLabel("Location History:")
        layout.addWidget(history_label)

        self.location_history = QListWidget()
        layout.addWidget(self.location_history)

        # Clear history button
        clear_button = QPushButton("Clear History")
        clear_button.clicked.connect(self.clear_location_history)
        layout.addWidget(clear_button)

        self.tabs.addTab(tab, "Location Tracking")

    def setup_emergency_tab(self):
        """Setup the emergency alert tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Warning header
        warning_label = QLabel("⚠ EMERGENCY ALERT SYSTEM ⚠")
        warning_label.setStyleSheet("""
            color: #ff4040;
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
            background: rgba(150, 30, 30, 0.3);
            border: 1px solid rgba(255, 80, 80, 0.5);
            border-radius: 4px;
        """)
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(warning_label)

        # Emergency contacts setup
        contacts_label = QLabel("Emergency Contacts (comma-separated emails):")
        layout.addWidget(contacts_label)

        self.contacts_input = QLineEdit()
        self.contacts_input.setPlaceholderText("Enter email addresses...")
        layout.addWidget(self.contacts_input)

        save_contacts = QPushButton("Save Contacts")
        save_contacts.clicked.connect(self.save_emergency_contacts)
        layout.addWidget(save_contacts)

        # Emergency message
        message_label = QLabel("Emergency Message (optional):")
        layout.addWidget(message_label)

        self.emergency_message = QTextEdit()
        self.emergency_message.setPlaceholderText(
            "Enter additional message details..."
        )
        layout.addWidget(self.emergency_message)

        # Alert button
        self.alert_button = QPushButton("SEND EMERGENCY ALERT")
        self.alert_button.setObjectName("alert_button")
        self.alert_button.clicked.connect(self.send_emergency_alert)
        layout.addWidget(self.alert_button)

        # Alert history
        history_label = QLabel("Alert History:")
        layout.addWidget(history_label)

        self.alert_history = QListWidget()
        layout.addWidget(self.alert_history)

        self.tabs.addTab(tab, "Emergency Alert")

    def send_message(self):
        """Handle sending a message with sci-fi styled output."""
        message = self.chat_input.text()
        if message:
            # Update message counter
            self.message_count += 1
            if hasattr(self, 'stat_messages'):
                self.stat_messages.setText(f"◆ MESSAGES: {self.message_count}")
            
            # User message with styled prefix
            user_prefix = '<span style="color: #80c0e0;">◈ You:</span>'
            self.chat_display.append(f'{user_prefix} {message}')
            # Process message and get response
            response = self.process_message(message)
            # AI response with styled prefix
            ai_prefix = '<span style="color: #00d4ff;">◈ AI:</span>'
            self.chat_display.append(f'{ai_prefix} {response}')
            self.chat_display.append("")  # Add spacing
            self.chat_input.clear()

    def process_message(self, message):
        """Process user message and generate response."""
        intent = self.intent_detector.predict(message)
        # Handle different intents and generate appropriate response
        return f"Detected intent: {intent}"  # Placeholder response

    def add_task(self):
        """Add a new task"""
        # Implement task addition logic
        pass

    def update_persona(self):
        """Update user persona"""
        # Implement persona update logic
        pass
