"""
Main dashboard window implementation with cloud sync, advanced ML, and plugin support.
"""

import base64
import os
from typing import Optional

from PyQt6.QtCore import QPropertyAnimation, QTimer
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
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

from app.core.ai_persona import AIPersona
from app.core.cloud_sync import CloudSyncManager
from app.core.command_override import CommandOverrideSystem
from app.core.data_analysis import DataAnalyzer
from app.core.emergency_alert import EmergencyAlert
from app.core.intent_detection import IntentDetector
from app.core.learning_paths import LearningPathManager
from app.core.learning_request_log import LearningRequestLog
from app.core.location_tracker import LocationTracker
from app.core.memory_expansion import MemoryExpansionSystem
from app.core.ml_models import AdvancedMLManager
from app.core.plugin_system import PluginManager
from app.core.security_resources import SecurityResourceManager
from app.core.user_manager import UserManager
from app.gui.ai_persona_ui import AIPersonaDialog
from app.gui.command_memory_ui import CommandOverrideDialog, MemoryExpansionDialog
from app.gui.learning_request_ui import LearningRequestDialog
from app.gui.settings_dialog import SettingsDialog


class DashboardWindow(QMainWindow):
    def __init__(self, username: Optional[str] = None, initial_tab: int = 0):
        super().__init__()
        # Initialize core components
        self.user_manager = UserManager()
        self.intent_detector = IntentDetector()
        self.learning_manager = LearningPathManager()
        self.data_analyzer = DataAnalyzer()
        self.security_manager = SecurityResourceManager()
        self.location_tracker = LocationTracker()
        self.emergency_alert = EmergencyAlert()

        # Initialize new advanced features
        self.cloud_sync = CloudSyncManager()
        self.ml_manager = AdvancedMLManager()
        self.plugin_manager = PluginManager()

        # Initialize command override and memory expansion systems
        self.command_override = CommandOverrideSystem()
        self.memory_expansion = MemoryExpansionSystem(
            command_override=self.command_override
        )

        # Initialize learning request log (pass memory_expansion for integration)
        self.learning_request_log = LearningRequestLog(
            memory_system=self.memory_expansion
        )

        # Initialize AI Persona system (with memory integration and user name)
        self.ai_persona = AIPersona(
            memory_system=self.memory_expansion,
            user_name=username if username else "User",
        )

        # Initialize plugins with context
        plugin_context = {
            "user_manager": self.user_manager,
            "ml_manager": self.ml_manager,
            "cloud_sync": self.cloud_sync,
            "command_override": self.command_override,
            "memory_expansion": self.memory_expansion,
            "learning_request_log": self.learning_request_log,
            "ai_persona": self.ai_persona,
        }
        self.plugin_manager.initialize_all_plugins(plugin_context)

        # Setup proactive conversation timer
        self.proactive_timer = QTimer()
        self.proactive_timer.timeout.connect(self._check_proactive_conversation)
        self.proactive_timer.start(60000)  # Check every minute

        # Setup timers
        self.location_timer = QTimer()
        self.location_timer.timeout.connect(self.update_location)

        # If username provided, set current user and sync
        if username:
            self.user_manager.current_user = username
            # Auto-sync user data from cloud
            self._perform_cloud_sync(username)
            # Log session start to memory
            self.memory_expansion.store_action(
                "session_start",
                {"username": username, "timestamp": self._get_timestamp()},
                "User session initiated",
                tags=["session", "login"],
            )

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
            anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        except Exception:
            # animations are cosmetic; ignore errors
            pass

    def _perform_cloud_sync(self, username: str) -> None:
        """Perform cloud synchronization for user data."""
        try:
            if self.cloud_sync.sync_enabled:
                user_data = self.user_manager.users.get(username, {})
                synced_data = self.cloud_sync.auto_sync(username, user_data)
                if synced_data != user_data:
                    self.user_manager.users[username] = synced_data
                    self.user_manager.save_users()
        except Exception as e:
            print(f"Cloud sync error: {e}")

    # Handler Methods
    def update_location(self) -> None:
        """Update location tracking display."""
        try:
            if hasattr(self, "location_display"):
                location = self.location_tracker.get_current_location()
                if location:
                    self.location_display.append(
                        f"Location updated: {location.get('address', 'Unknown')}"
                    )
        except Exception as e:
            print(f"Location update error: {e}")

    def toggle_location_tracking(self) -> None:
        """Toggle location tracking on/off."""
        try:
            if self.location_timer.isActive():
                self.location_timer.stop()
                if hasattr(self, "location_toggle"):
                    self.location_toggle.setText("Start Tracking")
            else:
                self.location_timer.start(300000)  # 5 minutes
                if hasattr(self, "location_toggle"):
                    self.location_toggle.setText("Stop Tracking")
                self.update_location()
        except Exception as e:
            print(f"Toggle tracking error: {e}")

    def clear_location_history(self) -> None:
        """Clear location tracking history."""
        try:
            from PyQt6.QtWidgets import QMessageBox

            if hasattr(self, "location_display"):
                self.location_display.clear()
            QMessageBox.information(
                self, "Location History", "Location history cleared successfully."
            )
        except Exception as e:
            print(f"Clear history error: {e}")

    def update_security_resources(self) -> None:
        """Update security resources list."""
        try:
            if hasattr(self, "security_list"):
                resources = self.security_manager.get_resources()
                self.security_list.clear()
                for resource in resources:
                    self.security_list.addItem(resource.get("name", "Unknown"))
        except Exception as e:
            print(f"Security update error: {e}")

    def open_security_resource(self) -> None:
        """Open selected security resource."""
        try:
            from PyQt6.QtWidgets import QMessageBox

            if hasattr(self, "security_list"):
                current_item = self.security_list.currentItem()
                if current_item:
                    QMessageBox.information(
                        self, "Security Resource", f"Opening: {current_item.text()}"
                    )
        except Exception as e:
            print(f"Open resource error: {e}")

    def add_security_favorite(self) -> None:
        """Add current security resource to favorites."""
        try:
            from PyQt6.QtWidgets import QMessageBox

            if hasattr(self, "security_list"):
                current_item = self.security_list.currentItem()
                if current_item:
                    QMessageBox.information(
                        self, "Favorites", f"Added to favorites: {current_item.text()}"
                    )
        except Exception as e:
            print(f"Add favorite error: {e}")

    def generate_learning_path(self) -> None:
        """Generate a new learning path."""
        try:
            if hasattr(self, "learning_output"):
                topic = "Python Programming"
                if hasattr(self, "learning_topic"):
                    topic = self.learning_topic.text() or topic
                path = self.learning_manager.generate_path(topic)
                self.learning_output.setPlainText(str(path))
        except Exception as e:
            print(f"Generate path error: {e}")
            if hasattr(self, "learning_output"):
                self.learning_output.setPlainText(f"Error: {e}")

    def load_data_file(self) -> None:
        """Load a data file for analysis."""
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox

            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Data File",
                "",
                "Data Files (*.csv *.xlsx *.json);;All Files (*)",
            )
            if file_path:
                success = self.data_analyzer.load_file(file_path)
                if success and hasattr(self, "data_info"):
                    self.data_info.setText(f"Loaded: {file_path}")
                else:
                    QMessageBox.warning(self, "Load Error", "Failed to load data file")
        except Exception as e:
            print(f"Load data error: {e}")

    def perform_analysis(self) -> None:
        """Perform data analysis on loaded data."""
        try:
            if hasattr(self, "analysis_output"):
                results = self.data_analyzer.analyze()
                self.analysis_output.setPlainText(str(results))
        except Exception as e:
            print(f"Analysis error: {e}")
            if hasattr(self, "analysis_output"):
                self.analysis_output.setPlainText(f"Error: {e}")

    def save_emergency_contacts(self) -> None:
        """Save emergency contact information."""
        try:
            from PyQt6.QtWidgets import QMessageBox

            if hasattr(self, "contacts_input"):
                _ = self.contacts_input.toPlainText()
                # Save contacts logic here (contacts would be processed here)
                QMessageBox.information(
                    self, "Emergency Contacts", "Emergency contacts saved successfully."
                )
        except Exception as e:
            print(f"Save contacts error: {e}")

    def send_emergency_alert(self) -> None:
        """Send emergency alert to contacts."""
        try:
            from PyQt6.QtWidgets import QMessageBox

            reply = QMessageBox.question(
                self,
                "Emergency Alert",
                "Send emergency alert to all contacts?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                success = self.emergency_alert.send_alert()
                if success:
                    QMessageBox.information(
                        self, "Alert Sent", "Emergency alert sent successfully."
                    )
                else:
                    QMessageBox.warning(
                        self, "Alert Failed", "Failed to send emergency alert."
                    )
        except Exception as e:
            print(f"Send alert error: {e}")

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
                "assets",
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

            act_home = QAction(
                _icon("home.svg", QStyle.StandardPixmap.SP_DesktopIcon), "Home", self
            )

            act_refresh = QAction(
                _icon("refresh.svg", QStyle.StandardPixmap.SP_BrowserReload),
                "Refresh",
                self,
            )

            act_help = QAction(
                _icon("help.svg", QStyle.StandardPixmap.SP_DialogHelpButton),
                "Help",
                self,
            )

            act_settings = QAction(
                _icon("help.svg", QStyle.StandardPixmap.SP_FileDialogDetailedView),
                "Settings",
                self,
            )

            # New advanced features
            act_command = QAction("⚠️ Command Override", self)
            act_command.setToolTip("Command Override System - Control safety protocols")

            act_memory = QAction("🧠 Memory", self)
            act_memory.setToolTip("Memory Expansion System - AI memory and learning")

            act_requests = QAction("📋 Learning Requests", self)
            act_requests.setToolTip(
                "Learning Request Log - AI learning approval system"
            )

            act_persona = QAction("🤖 AI Persona", self)
            act_persona.setToolTip(
                "AI Persona & Four Laws - Configure AI personality and ethics"
            )

            toolbar.addAction(act_home)
            toolbar.addAction(act_refresh)
            toolbar.addSeparator()
            toolbar.addAction(act_help)
            toolbar.addAction(act_settings)
            toolbar.addSeparator()
            toolbar.addAction(act_command)
            toolbar.addAction(act_memory)
            toolbar.addAction(act_requests)
            toolbar.addAction(act_persona)

            # Connect actions
            act_settings.triggered.connect(self.open_settings_dialog)
            act_command.triggered.connect(self.open_command_override_dialog)
            act_memory.triggered.connect(self.open_memory_expansion_dialog)
            act_requests.triggered.connect(self.open_learning_request_dialog)
            act_persona.triggered.connect(self.open_ai_persona_dialog)
            act_memory.triggered.connect(self.open_memory_expansion_dialog)
            act_requests.triggered.connect(self.open_learning_request_dialog)
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
            qss_path = os.path.join(os.path.dirname(__file__), "styles.qss")
            if os.path.exists(qss_path):
                with open(qss_path, "r", encoding="utf-8") as f:
                    qss = f.read()

                # embed assets as data URIs if present
                assets_dir = os.path.join(os.path.dirname(__file__), "assets")
                # parchment
                parchment_path = os.path.join(assets_dir, "parchment.svg")
                if os.path.exists(parchment_path):
                    with open(parchment_path, "rb") as af:
                        pdata = base64.b64encode(af.read()).decode("ascii")
                        pdata_uri = f"data:image/svg+xml;base64,{pdata}"
                        qss = qss.replace("{PARCHMENT}", pdata_uri)
                # leather
                leather_path = os.path.join(assets_dir, "leather.svg")
                if os.path.exists(leather_path):
                    with open(leather_path, "rb") as af:
                        ldata = base64.b64encode(af.read()).decode("ascii")
                        ldata_uri = f"data:image/svg+xml;base64,{ldata}"
                        qss = qss.replace("{LEATHER}", ldata_uri)

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
            theme = settings.get("theme", "light")
            if theme == "dark":
                dark_path = os.path.join(os.path.dirname(__file__), "styles_dark.qss")
                if os.path.exists(dark_path):
                    with open(dark_path, "r", encoding="utf-8") as df:
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
            size = int(settings.get("ui_scale", 10))
            app = QApplication.instance()
            if isinstance(app, QApplication):
                app.setFont(QFont("Segoe UI", size))
        except Exception:
            # ignore font errors
            pass

        # Reload the stylesheet so theme changes are applied
        qss_path = os.path.join(
            os.path.dirname(__file__),
            "styles.qss",
        )
        try:
            if os.path.exists(qss_path):
                with open(qss_path, "r", encoding="utf-8") as f:
                    qss = f.read()
                self._apply_stylesheet_from_settings(qss)
        except Exception:
            pass

    def open_settings_dialog(self):
        """Open the settings dialog and persist/apply new settings."""
        current = SettingsDialog.load_settings()
        dlg = SettingsDialog(self, current=current)
        if dlg.exec() == QDialog.DialogCode.Accepted:
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
        self.security_category.addItems(self.security_manager.get_all_categories())
        self.security_category.currentTextChanged.connect(
            self.update_security_resources
        )
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
        self.alert_button.setStyleSheet(
            "background-color: red;" " color: white;" " font-weight: bold;"
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

            # Update AI persona conversation state (user message)
            if hasattr(self, "ai_persona"):
                self.ai_persona.update_conversation_state(
                    is_user_message=True, message_length=len(message)
                )

            # Process message and get response
            response = self.process_message(message)
            self.chat_display.append(f"AI: {response}")
            self.chat_input.clear()

            # Update AI persona conversation state (AI response)
            if hasattr(self, "ai_persona"):
                self.ai_persona.update_conversation_state(
                    is_user_message=False, message_length=len(response)
                )

            # Store conversation in memory
            if hasattr(self, "memory_expansion"):
                self.memory_expansion.store_conversation(
                    user_message=message,
                    ai_response=response,
                    context={"intent": self.intent_detector.predict(message)},
                    tags=["chat", "conversation"],
                )

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

    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        from datetime import datetime

        return datetime.now().isoformat()

    def open_command_override_dialog(self):
        """Open the command override control dialog."""
        try:
            dialog = CommandOverrideDialog(self, self.command_override)
            dialog.exec()
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.warning(
                self, "Error", f"Failed to open command override dialog: {e}"
            )

    def open_memory_expansion_dialog(self):
        """Open the memory expansion control dialog."""
        try:
            dialog = MemoryExpansionDialog(self, self.memory_expansion)
            dialog.exec()
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.warning(
                self, "Error", f"Failed to open memory expansion dialog: {e}"
            )

    def open_learning_request_dialog(self):
        """Open the learning request log dialog."""
        try:
            dialog = LearningRequestDialog(self, self.learning_request_log)
            dialog.exec()
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.warning(
                self, "Error", f"Failed to open learning request dialog: {e}"
            )

    def open_ai_persona_dialog(self):
        """Open the AI persona configuration dialog."""
        try:
            dialog = AIPersonaDialog(self, self.ai_persona)
            dialog.exec()
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.warning(self, "Error", f"Failed to open AI persona dialog: {e}")

    def _check_proactive_conversation(self):
        """Check if AI should initiate proactive conversation."""
        try:
            should_initiate, reason = self.ai_persona.should_initiate_conversation()

            if should_initiate:
                # Generate proactive message
                message = self.ai_persona.generate_proactive_message()

                # Display in chat (add to conversation)
                if hasattr(self, "chat_display"):
                    self.chat_display.append(f"\n🤖 AI (Proactive): {message}\n")

                # Update conversation state
                self.ai_persona.update_conversation_state(is_user_message=False)

                # Log to memory
                if self.memory_expansion:
                    self.memory_expansion.store_conversation(
                        user_message="",
                        ai_response=message,
                        context={"type": "proactive_initiation"},
                        tags=["proactive", "ai_initiated"],
                    )
        except Exception as e:
            print(f"Error checking proactive conversation: {e}")
