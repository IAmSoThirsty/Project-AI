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
        """Load the AI face SVG and return as QPixmap (enlarged 3D version)."""
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        ai_face_path = os.path.join(assets_dir, 'ai_face.svg')
        # Enlarged size for 3D face display (300x300 for better visual impact)
        pixmap = QPixmap(260, 260)
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

    def _update_ai_initiative(self):
        """Update the AI Initiative display with autonomous activities."""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        
        activities = [
            f"<span style='color:#60ff60;'>● [{current_time}]</span>",
            "<span style='color:#a0ffa0;'>  Monitoring system health...</span>",
            "<span style='color:#60ff60;'>● Background tasks:</span>",
            "<span style='color:#80ff80;'>  • Data optimization: ACTIVE</span>",
            "<span style='color:#80ff80;'>  • Security scan: RUNNING</span>",
            "<span style='color:#80ff80;'>  • Learning patterns: ANALYZING</span>",
            "<span style='color:#60ff60;'>● Predictive analysis:</span>",
            "<span style='color:#a0ffa0;'>  Preparing recommendations...</span>",
            "<span style='color:#60ff60;'>● Auto-maintenance:</span>",
            "<span style='color:#a0ffa0;'>  Cache optimization: 94%</span>",
        ]
        
        self.initiative_display.setHtml("<br/>".join(activities))

    def setup_chat_tab(self):
        """Setup the chat interface tab with centered AI face and initiative window."""
        chat_tab = QWidget()
        main_layout = QVBoxLayout(chat_tab)

        # Top section: Three columns - Status | Centered AI Face | Initiative Window
        top_section = QHBoxLayout()

        # Left column: System Status Monitors
        monitors_container = QVBoxLayout()

        # AI Status header with enhanced styling
        ai_status_header = QLabel("◈ SYSTEM STATUS ◈")
        ai_status_header.setStyleSheet("""
            color: #00d4ff;
            font-size: 16px;
            font-weight: bold;
            padding: 8px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(0, 50, 80, 0.4),
                stop:0.5 rgba(0, 80, 120, 0.3),
                stop:1 rgba(0, 50, 80, 0.4));
            border-radius: 4px;
        """)
        monitors_container.addWidget(ai_status_header)

        # Status monitor frame with enhanced 3D appearance
        status_monitor = QFrame()
        status_monitor.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(10, 30, 50, 0.9),
                    stop:0.5 rgba(5, 20, 40, 0.95),
                    stop:1 rgba(10, 30, 50, 0.9));
                border: 2px solid rgba(0, 200, 255, 0.5);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        status_layout = QVBoxLayout(status_monitor)
        status_layout.setSpacing(8)

        # Enhanced system status indicators with icons
        self.status_online = QLabel("● SYSTEM STATUS: ONLINE")
        self.status_online.setStyleSheet("""
            color: #40ff80;
            font-size: 13px;
            font-weight: bold;
            padding: 4px;
            background: rgba(0, 100, 50, 0.2);
            border-radius: 4px;
        """)
        status_layout.addWidget(self.status_online)

        self.status_memory = QLabel("● MEMORY: 85% OPTIMAL")
        self.status_memory.setStyleSheet("""
            color: #40ff80;
            font-size: 13px;
            padding: 4px;
            background: rgba(0, 100, 50, 0.15);
            border-radius: 4px;
        """)
        status_layout.addWidget(self.status_memory)

        self.status_network = QLabel("● NETWORK: SECURE CONNECTION")
        self.status_network.setStyleSheet("""
            color: #40ff80;
            font-size: 13px;
            padding: 4px;
            background: rgba(0, 100, 50, 0.15);
            border-radius: 4px;
        """)
        status_layout.addWidget(self.status_network)

        self.status_ai = QLabel("● AI CORE: FULLY OPERATIONAL")
        self.status_ai.setStyleSheet("""
            color: #00d4ff;
            font-size: 13px;
            font-weight: bold;
            padding: 4px;
            background: rgba(0, 80, 120, 0.3);
            border-radius: 4px;
        """)
        status_layout.addWidget(self.status_ai)

        monitors_container.addWidget(status_monitor)
        monitors_container.addStretch()

        top_section.addLayout(monitors_container, stretch=1)

        # CENTER column: AI Face (centered and prominent)
        ai_container = QVBoxLayout()
        ai_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        ai_frame = QFrame()
        ai_frame.setObjectName("ai_face_frame")
        ai_frame.setFixedSize(280, 280)
        ai_frame.setStyleSheet("""
            QFrame#ai_face_frame {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8,
                    fx:0.5, fy:0.3,
                    stop:0 rgba(0, 50, 80, 0.4),
                    stop:0.5 rgba(0, 30, 50, 0.3),
                    stop:1 rgba(5, 15, 25, 0.2));
                border: 3px solid rgba(0, 200, 255, 0.5);
                border-radius: 140px;
            }
        """)
        ai_layout = QVBoxLayout(ai_frame)
        ai_layout.setContentsMargins(10, 10, 10, 10)

        self.ai_face_label = QLabel()
        self.ai_face_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ai_pixmap = self._load_ai_face_svg()
        self.ai_face_label.setPixmap(ai_pixmap)
        ai_layout.addWidget(self.ai_face_label)
        
        ai_container.addWidget(ai_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # AI identifier label under the face
        ai_id_label = QLabel("◈ AI CORE INTERFACE ◈")
        ai_id_label.setStyleSheet("""
            color: #00d4ff;
            font-size: 12px;
            font-weight: bold;
            padding: 8px;
        """)
        ai_id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ai_container.addWidget(ai_id_label)
        
        top_section.addLayout(ai_container, stretch=2)

        # Right column: AI Initiative Window (what AI is doing on its own)
        initiative_container = QVBoxLayout()

        initiative_header = QLabel("◈ AI INITIATIVE ◈")
        initiative_header.setStyleSheet("""
            color: #80ff80;
            font-size: 16px;
            font-weight: bold;
            padding: 8px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(0, 80, 50, 0.4),
                stop:0.5 rgba(0, 120, 80, 0.3),
                stop:1 rgba(0, 80, 50, 0.4));
            border-radius: 4px;
        """)
        initiative_container.addWidget(initiative_header)

        # AI Initiative monitor frame
        initiative_monitor = QFrame()
        initiative_monitor.setFixedSize(220, 200)
        initiative_monitor.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(10, 40, 30, 0.9),
                    stop:0.5 rgba(5, 30, 20, 0.95),
                    stop:1 rgba(10, 40, 30, 0.9));
                border: 2px solid rgba(100, 255, 150, 0.5);
                border-radius: 8px;
                padding: 8px;
            }
        """)
        initiative_inner = QVBoxLayout(initiative_monitor)
        initiative_inner.setSpacing(6)

        # AI Initiative activity display
        self.initiative_display = QTextEdit()
        self.initiative_display.setObjectName("ai_initiative_display")
        self.initiative_display.setReadOnly(True)
        self.initiative_display.setStyleSheet("""
            QTextEdit#ai_initiative_display {
                background: rgba(5, 25, 15, 0.9);
                border: 1px solid rgba(100, 255, 150, 0.3);
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                color: #90ff90;
                padding: 6px;
            }
        """)
        self.initiative_display.setPlaceholderText(
            "◈ AI AUTONOMOUS ACTIVITY ◈\n\n"
            "Monitoring background processes..."
        )
        
        # Initialize with some default autonomous activities
        self._update_ai_initiative()
        
        initiative_inner.addWidget(self.initiative_display)

        initiative_container.addWidget(initiative_monitor)
        initiative_container.addStretch()

        top_section.addLayout(initiative_container, stretch=1)

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

        # Create a horizontal layout for chat and thought process side by side
        chat_section = QHBoxLayout()

        # Left side: Chat display
        chat_container = QVBoxLayout()
        
        chat_header = QLabel("◈ COMMUNICATION TERMINAL ◈")
        chat_header.setStyleSheet("""
            color: #00d4ff;
            font-size: 14px;
            font-weight: bold;
            padding: 6px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(0, 50, 80, 0.4),
                stop:0.5 rgba(0, 80, 120, 0.3),
                stop:1 rgba(0, 50, 80, 0.4));
            border-radius: 4px;
        """)
        chat_container.addWidget(chat_header)

        self.chat_display = QTextEdit()
        self.chat_display.setObjectName("ai_chat_display")
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText(
            "◈ COMMUNICATION TERMINAL ACTIVE ◈\n\n"
            "Type your message below to interact with the AI Assistant."
        )
        chat_container.addWidget(self.chat_display)
        
        chat_section.addLayout(chat_container, stretch=3)

        # Right side: AI Thought Process section
        thought_container = QVBoxLayout()
        
        thought_header = QLabel("◈ AI THOUGHT PROCESS ◈")
        thought_header.setStyleSheet("""
            color: #ff9040;
            font-size: 14px;
            font-weight: bold;
            padding: 6px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(80, 50, 0, 0.4),
                stop:0.5 rgba(120, 80, 0, 0.3),
                stop:1 rgba(80, 50, 0, 0.4));
            border-radius: 4px;
        """)
        thought_container.addWidget(thought_header)

        self.thought_display = QTextEdit()
        self.thought_display.setObjectName("ai_thought_display")
        self.thought_display.setReadOnly(True)
        self.thought_display.setStyleSheet("""
            QTextEdit#ai_thought_display {
                background: rgba(20, 15, 5, 0.95);
                border: 2px solid rgba(255, 150, 50, 0.4);
                border-radius: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                color: #ffd080;
            }
        """)
        self.thought_display.setPlaceholderText(
            "◈ COGNITIVE PROCESS MONITOR ◈\n\n"
            "AI reasoning and thought analysis\n"
            "will be displayed here..."
        )
        thought_container.addWidget(self.thought_display)
        
        chat_section.addLayout(thought_container, stretch=2)

        main_layout.addLayout(chat_section)

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
        """Handle sending a message with sci-fi styled output and thought process display."""
        message = self.chat_input.text()
        if message:
            # Update message counter
            self.message_count += 1
            if hasattr(self, 'stat_messages'):
                self.stat_messages.setText(f"◆ MESSAGES PROCESSED: {self.message_count}")
            
            # User message with styled prefix
            user_prefix = '<span style="color: #80c0e0;">◈ You:</span>'
            self.chat_display.append(f'{user_prefix} {message}')
            
            # Process message and get response with thought process
            response, thought_process = self.process_message_with_thoughts(message)
            
            # Display AI thought process
            if hasattr(self, 'thought_display'):
                thought_prefix = '<span style="color: #ff9040;">◈ ANALYZING INPUT:</span>'
                self.thought_display.append(f'{thought_prefix}')
                self.thought_display.append(
                    f'<span style="color: #ffd080;">{thought_process}</span>'
                )
                self.thought_display.append("")
            
            # AI response with styled prefix
            ai_prefix = '<span style="color: #00d4ff;">◈ AI:</span>'
            self.chat_display.append(f'{ai_prefix} {response}')
            self.chat_display.append("")  # Add spacing
            self.chat_input.clear()

    def process_message_with_thoughts(self, message):
        """Process user message and generate response with thought process explanation."""
        # Detect intent
        intent = self.intent_detector.predict(message)
        
        # Build thought process explanation
        thoughts = []
        thoughts.append(f"<b>Step 1 - Input Analysis:</b><br/>")
        thoughts.append(f"• Received message: \"{message}\"")
        thoughts.append(f"• Character count: {len(message)}")
        thoughts.append(f"• Word count: {len(message.split())}<br/>")
        
        thoughts.append(f"<b>Step 2 - Intent Classification:</b><br/>")
        thoughts.append(f"• Running NLP classifier...")
        thoughts.append(f"• Detected intent: <span style='color:#40ff80;'>{intent}</span><br/>")
        
        thoughts.append(f"<b>Step 3 - Response Generation:</b><br/>")
        thoughts.append(f"• Formulating contextual response...")
        thoughts.append(f"• Applying safety filters...")
        thoughts.append(f"• Response ready ✓")
        
        thought_process = "<br/>".join(thoughts)
        
        # Generate response based on intent
        response = f"I understood your intent as: {intent}. How can I assist you further?"
        
        return response, thought_process

    def process_message(self, message):
        """Process user message and generate response (legacy method)."""
        response, _ = self.process_message_with_thoughts(message)
        return response

    def add_task(self):
        """Add a new task"""
        # Implement task addition logic
        pass

    def update_persona(self):
        """Update user persona"""
        # Implement persona update logic
        pass
