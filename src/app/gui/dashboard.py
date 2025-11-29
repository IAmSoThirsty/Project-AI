"""
Main dashboard window implementation.
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
)
from PyQt6.QtCore import QTimer, QPropertyAnimation
from PyQt6.QtGui import QColor
import os
import base64
from app.core.user_manager import UserManager
from app.core.intent_detection import IntentDetector
from app.core.learning_paths import LearningPathManager
from app.core.data_analysis import DataAnalyzer
from app.core.security_resources import SecurityResourceManager
from app.core.location_tracker import LocationTracker
from app.core.emergency_alert import EmergencyAlert
from app.core.network_utils import is_online, get_network_status


class DashboardWindow(QMainWindow):
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

        # Network status tracking
        self._is_online = True

        # Setup timers
        self.location_timer = QTimer()
        self.location_timer.timeout.connect(self.update_location)

        # Network status check timer (check every 30 seconds)
        self.network_timer = QTimer()
        self.network_timer.timeout.connect(self.check_network_status)

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

        # Start network monitoring
        self.network_timer.start(30000)  # Check every 30 seconds
        self.check_network_status()  # Initial check

    def check_network_status(self):
        """Check and update network status indicator."""
        online = is_online(timeout=2.0)
        if online != self._is_online:
            self._is_online = online
            self.update_network_indicator()

    def update_network_indicator(self):
        """Update the network status indicator in the status bar."""
        if self._is_online:
            status_text = "🌐 Online"
            self.network_indicator.setStyleSheet(
                "color: green; font-weight: bold; padding: 2px 8px;"
            )
        else:
            status_text = "📴 Offline Mode"
            self.network_indicator.setStyleSheet(
                "color: orange; font-weight: bold; padding: 2px 8px;"
            )
        self.network_indicator.setText(status_text)

    def update_page_number(self, index: int):
        """Update the footer with current page/chapter number."""
        total = max(1, self.tabs.count())
        try:
            page_text = f"Page {index+1} of {total}"
            self.page_label.setText(page_text)
        except Exception:
            pass

    def animate_tab_change(self, index: int):
        """Apply a quick fade-in animation to the newly selected tab to emulate a page turn."""
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
        """Setup the user interface"""
        self.setWindowTitle("AI Assistant")
        self.setGeometry(100, 100, 1200, 800)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Try to load external QSS stylesheet for the "book" appearance if present
        try:
            qss_path = os.path.join(os.path.dirname(__file__), 'styles.qss')
            if os.path.exists(qss_path):
                with open(qss_path, 'r', encoding='utf-8') as f:
                    qss = f.read()

                # embed assets as data URIs if present
                assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
                # parchment
                parchment_path = os.path.join(assets_dir, 'parchment.svg')
                if os.path.exists(parchment_path):
                    with open(parchment_path, 'rb') as af:
                        pdata = base64.b64encode(af.read()).decode('ascii')
                        qss = qss.replace('{PARCHMENT}', f'data:image/svg+xml;base64,{pdata}')
                # leather
                leather_path = os.path.join(assets_dir, 'leather.svg')
                if os.path.exists(leather_path):
                    with open(leather_path, 'rb') as af:
                        ldata = base64.b64encode(af.read()).decode('ascii')
                        qss = qss.replace('{LEATHER}', f'data:image/svg+xml;base64,{ldata}')

                self.setStyleSheet(qss)
            else:
                # fallback inline style
                self.setStyleSheet("""
                    QMainWindow { background-color: #f7f1e1; }
                    QTabWidget::pane { border: 1px solid #c9b79c; background: #fffdf6; }
                    QTabBar::tab { background: #e9dcc7; padding: 10px; margin: 2px; border-radius: 4px; }
                    QTabBar::tab:selected { background: #fff; font-weight: bold; }
                    QPushButton { background-color: #a67c52; color: white; border-radius: 4px; padding: 6px; }
                    QPushButton#alert_button { background-color: red; }
                """)
        except Exception:
            # if anything fails, keep default styles
            pass

        # Setup status bar with network indicator and page number
        status_bar = self.statusBar()
        status_bar.showMessage("")

        # Create a container widget for status bar items
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)

        # Network status indicator
        self.network_indicator = QLabel("🌐 Online")
        self.network_indicator.setStyleSheet(
            "color: green; font-weight: bold; padding: 2px 8px;"
        )
        status_layout.addWidget(self.network_indicator)

        # Spacer
        status_layout.addStretch()

        # Page number label
        self.page_label = QLabel("")
        status_layout.addWidget(self.page_label)

        status_bar.addPermanentWidget(status_widget, 1)

        # Keep page number update and add tab-change animation
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

    def setup_chat_tab(self):
        """Setup the chat interface tab"""
        chat_tab = QWidget()
        layout = QVBoxLayout(chat_tab)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Input area
        self.chat_input = QLineEdit()
        layout.addWidget(self.chat_input)

        # Send button
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button)

        self.tabs.addTab(chat_tab, "Chapter 1 — Chat")

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
        layout.addWidget(self.learning_path_display)

        self.tabs.addTab(tab, "Chapter 3 — Learning Paths")

    def setup_data_analysis_tab(self):
        """Setup the data analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # File selection
        load_button = QPushButton("Load Data File")
        load_button.clicked.connect(self.load_data_file)
        layout.addWidget(load_button)

        # Analysis options
        self.analysis_type = QComboBox()
        self.analysis_type.addItems(["Basic Stats", "Scatter Plot", "Histogram", "Box Plot", "Correlation", "Clustering"])
        layout.addWidget(self.analysis_type)

        # Column selection
        self.column_selector = QComboBox()
        layout.addWidget(self.column_selector)

        # Analyze button
        analyze_button = QPushButton("Analyze")
        analyze_button.clicked.connect(self.perform_analysis)
        layout.addWidget(analyze_button)

        # Results display
        self.analysis_display = QTextEdit()
        self.analysis_display.setReadOnly(True)
        layout.addWidget(self.analysis_display)

        self.tabs.addTab(tab, "Chapter 4 — Data Analysis")

    def setup_security_tab(self):
        """Setup the security resources tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Category selection
        self.security_category = QComboBox()
        self.security_category.addItems(self.security_manager.get_all_categories())
        self.security_category.currentTextChanged.connect(self.update_security_resources)
        layout.addWidget(self.security_category)

        # Resources list
        self.resources_list = QListWidget()
        self.resources_list.itemDoubleClicked.connect(self.open_security_resource)
        layout.addWidget(self.resources_list)

        # Favorite button
        favorite_button = QPushButton("Add to Favorites")
        favorite_button.clicked.connect(self.add_security_favorite)
        layout.addWidget(favorite_button)

        self.tabs.addTab(tab, "Chapter 5 — Security Resources")
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
        self.location_display = QTextEdit()
        self.location_display.setReadOnly(True)
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

        self.tabs.addTab(tab, "Chapter 6 — Location Tracking")

    def setup_emergency_tab(self):
        """Setup the emergency alert tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Emergency contacts setup
        contacts_label = QLabel("Emergency Contacts (comma-separated emails):")
        layout.addWidget(contacts_label)

        self.contacts_input = QLineEdit()
        layout.addWidget(self.contacts_input)

        save_contacts = QPushButton("Save Contacts")
        save_contacts.clicked.connect(self.save_emergency_contacts)
        layout.addWidget(save_contacts)

        # Emergency message
        message_label = QLabel("Emergency Message (optional):")
        layout.addWidget(message_label)

        self.emergency_message = QTextEdit()
        layout.addWidget(self.emergency_message)

        # Alert button
        self.alert_button = QPushButton("SEND EMERGENCY ALERT")
        self.alert_button.setObjectName("alert_button")
        self.alert_button.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.alert_button.clicked.connect(self.send_emergency_alert)
        layout.addWidget(self.alert_button)

        # Alert history
        history_label = QLabel("Alert History:")
        layout.addWidget(history_label)

        self.alert_history = QListWidget()
        layout.addWidget(self.alert_history)

        self.tabs.addTab(tab, "Chapter 7 — Emergency Alert")

    def send_message(self):
        """Handle sending a message"""
        message = self.chat_input.text()
        if message:
            self.chat_display.append(f"You: {message}")
            # Process message and get response
            response = self.process_message(message)
            self.chat_display.append(f"AI: {response}")
            self.chat_input.clear()

    def process_message(self, message):
        """Process user message and generate response"""
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
