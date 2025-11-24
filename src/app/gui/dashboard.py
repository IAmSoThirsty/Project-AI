"""
Main dashboard window implementation.
"""

import base64
import os

from PyQt6.QtCore import QPropertyAnimation, QTimer
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QGraphicsOpacityEffect,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QStyle,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from app.core.data_analysis import DataAnalyzer
from app.core.emergency_alert import EmergencyAlert
from app.core.intent_detection import IntentDetector
from app.core.learning_paths import LearningPathManager
from app.core.location_tracker import LocationTracker
from app.core.security_resources import SecurityResourceManager
from app.core.user_manager import UserManager
from app.gui.settings_dialog import SettingsDialog


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
        """Update the footer with current page/chapter number."""
        total = max(1, self.tabs.count())
        try:
            self.statusBar().showMessage(f"Page {index+1} of {total}")
        except Exception:
            self.statusBar().showMessage("")

    def animate_tab_change(self, index: int):
        """Apply a quick fade-in animation to the newly selected tab to
        emulate a page turn.
        """
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
        # Larger default window for better usability
        self.setGeometry(80, 60, 1400, 900)

        # Add a small toolbar with common actions for a modern feel
        try:
            toolbar = QToolBar("Main")
            toolbar.setMovable(False)
            self.addToolBar(toolbar)

            style = self.style()
            # Prefer bundled SVG assets for crisp icons; fall back to style icons
            assets_dir = os.path.join(
                os.path.dirname(__file__),
                'assets',
            )

            def _icon(name, fallback_pixmap):
                path = os.path.join(assets_dir, name)
                try:
                    if os.path.exists(path):
                        from PyQt6.QtGui import QIcon

                        return QIcon(path)
                except Exception:
                    pass
                return style.standardIcon(fallback_pixmap)

            act_home = QAction(_icon('home.svg',
                                     QStyle.StandardPixmap.SP_DesktopIcon),
                               "Home", self)

            act_refresh = QAction(_icon('refresh.svg',
                                        QStyle.StandardPixmap.SP_BrowserReload),
                                  "Refresh", self)

            act_help = QAction(_icon('help.svg',
                                     QStyle.StandardPixmap.SP_DialogHelpButton),
                               "Help", self)

            act_settings = QAction(_icon('help.svg',
                                         QStyle.StandardPixmap.SP_FileDialogDetailedView),
                                   "Settings", self)

            toolbar.addAction(act_home)
            toolbar.addAction(act_refresh)
            toolbar.addSeparator()
            toolbar.addAction(act_help)
            toolbar.addAction(act_settings)
            # connect settings action
            act_settings.triggered.connect(self.open_settings_dialog)
        except Exception:
            # toolbar is cosmetic — ignore failures
            pass

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        # provide comfortable spacing and margins for a modern UI
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Try to load external QSS stylesheet for the "book" appearance
        # if present
        try:
            qss_path = os.path.join(
                os.path.dirname(__file__), 'styles.qss'
            )
            if os.path.exists(qss_path):
                with open(qss_path, 'r', encoding='utf-8') as f:
                    qss = f.read()

                # embed assets as data URIs if present
                assets_dir = os.path.join(
                    os.path.dirname(__file__), 'assets'
                )
                # parchment
                parchment_path = os.path.join(assets_dir, 'parchment.svg')
                if os.path.exists(parchment_path):
                    with open(parchment_path, 'rb') as af:
                        pdata = base64.b64encode(af.read()).decode('ascii')
                        pdata_uri = f'data:image/svg+xml;base64,{pdata}'
                        qss = qss.replace('{PARCHMENT}', pdata_uri)
                # leather
                leather_path = os.path.join(assets_dir, 'leather.svg')
                if os.path.exists(leather_path):
                    with open(leather_path, 'rb') as af:
                        ldata = base64.b64encode(af.read()).decode('ascii')
                        ldata_uri = f'data:image/svg+xml;base64,{ldata}'
                        qss = qss.replace('{LEATHER}', ldata_uri)

                # Apply stylesheet according to saved settings (light/dark)
                self._apply_stylesheet_from_settings(qss)
            else:
                # fallback inline style (kept short per line for linters)
                self._apply_stylesheet_from_settings(qss)
                # _apply_stylesheet_from_settings will call setStyleSheet internally
                # but if it fails, ensure a minimal fallback is applied:
                try:
                    fallback_qss = (
                        "QMainWindow { background-color: #f7f1e1; }\n"
                        "QTabWidget::pane { border: 1px solid #c9b79c; }\n"
                        "QTabWidget::pane { background: #fffdf6; }\n"
                        "QTabBar::tab { background: #e9dcc7; padding: 10px; }\n"
                        "QTabBar::tab { margin: 2px; border-radius: 4px; }\n"
                        "QTabBar::tab:selected { background: #fff; }\n"
                        "QPushButton { background-color: #a67c52; color: white; }\n"
                        "QPushButton { border-radius: 4px; padding: 6px; }\n"
                        "QPushButton#alert_button { background-color: red; }\n"
                    )
                    self.setStyleSheet(fallback_qss)
                except Exception:
                    # ignore fallback stylesheet failures
                    pass
        except Exception:
            # if anything fails, keep default styles
            pass

        # Status bar will show a page number like a book footer
        self.statusBar().showMessage("")
        # Apply initial saved settings (font size and theme)
        try:
            settings = SettingsDialog.load_settings()
            self._apply_settings(settings)
        except Exception:
            pass
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
        # Add Image Generation tab
        try:
            from app.gui.image_generation import ImageGenerationTab
            self.image_gen_tab = ImageGenerationTab()
            self.tabs.addTab(self.image_gen_tab, "🎨 AI Image Generation")
        except Exception:
            # non-fatal: keep going without Image Generation tab
            pass
        # Add Users management tab if widget is available
        try:
            from app.gui.user_management import UserManagementWidget
            self.user_mgmt = UserManagementWidget()
            self.tabs.addTab(self.user_mgmt, "Users")
        except Exception:
            # non-fatal: keep going without Users tab
            pass

    def _apply_stylesheet_from_settings(self, base_qss: str):
        """Apply stylesheet depending on saved theme setting (light/dark).

        If theme is dark and a `styles_dark.qss` file exists, that file is
        used. Otherwise the provided `base_qss` is applied.
        """
        try:
            settings = SettingsDialog.load_settings()
            theme = settings.get('theme', 'light')
            if theme == 'dark':
                dark_path = os.path.join(
                    os.path.dirname(__file__), 'styles_dark.qss'
                )
                if os.path.exists(dark_path):
                    with open(dark_path, 'r', encoding='utf-8') as df:
                        dark_qss = df.read()
                    self.setStyleSheet(dark_qss)
                    return
            # default: apply provided base qss
            self.setStyleSheet(base_qss)
        except Exception:
            # best-effort: try to apply base qss
            try:
                self.setStyleSheet(base_qss)
            except Exception:
                pass

    def _apply_settings(self, settings: dict):
        """Apply runtime settings such as UI scale and reload stylesheet."""
        try:
            size = int(settings.get('ui_scale', 10))
            QApplication.instance().setFont(QFont("Segoe UI", size))
        except Exception:
            # ignore font errors
            pass

        # Reload the stylesheet so theme changes are applied
        qss_path = os.path.join(
            os.path.dirname(__file__),
            'styles.qss',
        )
        try:
            if os.path.exists(qss_path):
                with open(qss_path, 'r', encoding='utf-8') as f:

                    qss = f.read()
                self._apply_stylesheet_from_settings(qss)
        except Exception:
            pass

    def open_settings_dialog(self):
        """Open the settings dialog and persist/apply new settings."""
        current = SettingsDialog.load_settings()
        dlg = SettingsDialog(self, current=current)
        if dlg.exec() == dlg.Accepted:
            new = dlg.get_values()
            ok = SettingsDialog.save_settings(new)
            if ok:
                self._apply_settings(new)

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
        analysis_items = [
            "Basic Stats",
            "Scatter Plot",
            "Histogram",
            "Box Plot",
            "Correlation",
            "Clustering",
        ]
        self.analysis_type.addItems(analysis_items)
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
        self.security_category.addItems(
            self.security_manager.get_all_categories()
        )
        self.security_category.currentTextChanged.connect(
            self.update_security_resources
        )
        layout.addWidget(self.security_category)

        # Resources list
        self.resources_list = QListWidget()
        self.resources_list.itemDoubleClicked.connect(
            self.open_security_resource
        )
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
        self.alert_button.setStyleSheet(
            "background-color: red;"
            " color: white;"
            " font-weight: bold;"
        )
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
