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
    QCheckBox,
    QSlider,
    QMessageBox,
)
from PyQt6.QtCore import QTimer, QPropertyAnimation, Qt, pyqtSignal, QObject
import os
import base64
from app.core.user_manager import UserManager
from app.core.intent_detection import IntentDetector
from app.core.learning_paths import LearningPathManager
from app.core.data_analysis import DataAnalyzer
from app.core.security_resources import SecurityResourceManager
from app.core.location_tracker import LocationTracker
from app.core.emergency_alert import EmergencyAlert
from app.core.voice_assistant import VoiceAssistant


class SpeechSignals(QObject):
    """Signals for thread-safe speech recognition updates."""
    speech_recognized = pyqtSignal(str)


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
        self.voice_assistant = VoiceAssistant()

        # Setup speech signals for thread-safe GUI updates
        self.speech_signals = SpeechSignals()
        self.speech_signals.speech_recognized.connect(self._on_speech_recognized)

        # Conversation history for context-aware responses
        self.conversation_history = []

        # Voice settings
        self.voice_enabled = True
        self.auto_listen = False

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

        # Status bar will show a page number like a book footer
        self.statusBar().showMessage("")
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
        """Setup the chat interface tab with voice capabilities"""
        chat_tab = QWidget()
        layout = QVBoxLayout(chat_tab)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Input area
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type a message or use voice input...")
        self.chat_input.returnPressed.connect(self.send_message)
        layout.addWidget(self.chat_input)

        # Button row for send and voice controls
        button_row = QHBoxLayout()

        # Send button
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        button_row.addWidget(send_button)

        # Voice input button (push-to-talk)
        self.voice_input_button = QPushButton("🎤 Voice Input")
        self.voice_input_button.setToolTip("Click to speak a message")
        self.voice_input_button.clicked.connect(self.start_voice_input)
        button_row.addWidget(self.voice_input_button)

        # Continuous listening toggle
        self.listen_toggle = QPushButton("🎧 Auto-Listen: OFF")
        self.listen_toggle.setCheckable(True)
        self.listen_toggle.setToolTip("Toggle continuous voice listening")
        self.listen_toggle.clicked.connect(self.toggle_continuous_listening)
        button_row.addWidget(self.listen_toggle)

        layout.addLayout(button_row)

        # Voice settings row
        voice_settings = QHBoxLayout()

        # Voice output toggle
        self.voice_output_checkbox = QCheckBox("🔊 Voice Output")
        self.voice_output_checkbox.setChecked(True)
        self.voice_output_checkbox.setToolTip("Enable/disable AI voice responses")
        self.voice_output_checkbox.stateChanged.connect(self._on_voice_output_changed)
        voice_settings.addWidget(self.voice_output_checkbox)

        # Speech rate slider
        voice_settings.addWidget(QLabel("Speed:"))
        self.speech_rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.speech_rate_slider.setMinimum(100)
        self.speech_rate_slider.setMaximum(250)
        self.speech_rate_slider.setValue(175)
        self.speech_rate_slider.setToolTip("Adjust speech speed")
        self.speech_rate_slider.valueChanged.connect(self._on_speech_rate_changed)
        voice_settings.addWidget(self.speech_rate_slider)

        # Clear conversation button
        clear_button = QPushButton("Clear Chat")
        clear_button.clicked.connect(self.clear_conversation)
        voice_settings.addWidget(clear_button)

        layout.addLayout(voice_settings)

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
        """Handle sending a message (text or voice)"""
        message = self.chat_input.text().strip()
        if message:
            self._process_and_respond(message)
            self.chat_input.clear()

    def _process_and_respond(self, message: str):
        """Process user message and generate AI response."""
        self.chat_display.append(f"<b>You:</b> {message}")

        # Add to conversation history for context
        self.conversation_history.append({"role": "user", "content": message})

        # Get AI response with conversation context
        response = self.voice_assistant.get_ai_response(
            message,
            context=self.conversation_history[-10:]  # Keep last 10 exchanges
        )

        # Add AI response to history
        self.conversation_history.append({"role": "assistant", "content": response})

        # Display response
        self.chat_display.append(f"<b>AI:</b> {response}")

        # Speak response if voice output is enabled
        if self.voice_enabled:
            self.voice_assistant.speak_async(response)

    def process_message(self, message):
        """Process user message and generate response (legacy method)."""
        intent = self.intent_detector.predict(message)
        # Use AI for conversational response
        return self.voice_assistant.get_ai_response(message)

    def start_voice_input(self):
        """Start listening for voice input (push-to-talk)."""
        self.voice_input_button.setText("🎤 Listening...")
        self.voice_input_button.setEnabled(False)
        self.chat_display.append("<i>Listening for voice input...</i>")

        # Run recognition in background thread
        import threading

        def recognize():
            text = self.voice_assistant.listen_once(timeout=10, phrase_limit=30)
            # Use signal to update GUI from main thread
            if text:
                self.speech_signals.speech_recognized.emit(text)
            else:
                self.speech_signals.speech_recognized.emit("")

        thread = threading.Thread(target=recognize, daemon=True)
        thread.start()

    def _on_speech_recognized(self, text: str):
        """Handle recognized speech (called from main thread via signal)."""
        self.voice_input_button.setText("🎤 Voice Input")
        self.voice_input_button.setEnabled(True)

        if text:
            self.chat_input.setText(text)
            # Automatically send if in auto-listen mode
            if self.auto_listen:
                self.send_message()
            else:
                self.chat_display.append(f"<i>Heard: {text}</i>")
        else:
            self.chat_display.append("<i>Could not understand audio. Please try again.</i>")

        # Continue listening if auto-listen is on
        if self.auto_listen:
            QTimer.singleShot(500, self.start_voice_input)

    def toggle_continuous_listening(self):
        """Toggle continuous voice listening mode."""
        self.auto_listen = self.listen_toggle.isChecked()

        if self.auto_listen:
            self.listen_toggle.setText("🎧 Auto-Listen: ON")
            self.chat_display.append("<i>Continuous listening enabled. Speak to interact.</i>")
            self.start_voice_input()
        else:
            self.listen_toggle.setText("🎧 Auto-Listen: OFF")
            self.chat_display.append("<i>Continuous listening disabled.</i>")

    def _on_voice_output_changed(self, state):
        """Handle voice output checkbox change."""
        self.voice_enabled = (state == Qt.CheckState.Checked.value)

    def _on_speech_rate_changed(self, value):
        """Handle speech rate slider change."""
        self.voice_assistant.set_voice_rate(value)

    def clear_conversation(self):
        """Clear the chat display and conversation history."""
        self.chat_display.clear()
        self.conversation_history.clear()
        self.chat_display.append("<i>Conversation cleared.</i>")

    def add_task(self):
        """Add a new task"""
        # Implement task addition logic
        pass

    def update_persona(self):
        """Update user persona"""
        # Implement persona update logic
        pass
