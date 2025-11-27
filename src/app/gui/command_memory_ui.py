"""
Command & Memory GUI - Interface for command override and memory expansion systems.
"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class CommandOverrideDialog(QDialog):
    """Dialog for command override system control."""

    def __init__(self, parent=None, command_system=None):
        super().__init__(parent)
        self.command_system = command_system
        self.setWindowTitle("Command Override System")
        self.setMinimumSize(600, 500)
        self._setup_ui()
        self._load_status()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Authentication section
        auth_group = QGroupBox("Authentication")
        auth_layout = QVBoxLayout()

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter master password")
        auth_layout.addWidget(QLabel("Master Password:"))
        auth_layout.addWidget(self.password_input)

        auth_buttons = QHBoxLayout()
        self.auth_button = QPushButton("Authenticate")
        self.auth_button.clicked.connect(self._authenticate)
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self._logout)
        auth_buttons.addWidget(self.auth_button)
        auth_buttons.addWidget(self.logout_button)
        auth_layout.addLayout(auth_buttons)

        self.auth_status = QLabel("Status: Not Authenticated")
        auth_layout.addWidget(self.auth_status)

        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)

        # Master override section
        master_group = QGroupBox("Master Override")
        master_layout = QVBoxLayout()

        master_label = QLabel(
            "⚠️ WARNING: Master override disables ALL safety protocols!"
        )
        master_label.setStyleSheet("color: red; font-weight: bold;")
        master_layout.addWidget(master_label)

        master_buttons = QHBoxLayout()
        self.enable_master_btn = QPushButton("Enable Master Override")
        self.enable_master_btn.clicked.connect(self._enable_master_override)
        self.enable_master_btn.setStyleSheet("background-color: #ff4444;")

        self.disable_master_btn = QPushButton("Disable Master Override")
        self.disable_master_btn.clicked.connect(self._disable_master_override)
        self.disable_master_btn.setStyleSheet("background-color: #44ff44;")

        master_buttons.addWidget(self.enable_master_btn)
        master_buttons.addWidget(self.disable_master_btn)
        master_layout.addLayout(master_buttons)

        self.master_status = QLabel("Master Override: Inactive")
        master_layout.addWidget(self.master_status)

        master_group.setLayout(master_layout)
        layout.addWidget(master_group)

        # Individual protocols section
        protocols_group = QGroupBox("Safety Protocols")
        protocols_layout = QVBoxLayout()

        self.protocol_checkboxes = {}
        protocols = [
            ("content_filter", "Content Filtering"),
            ("prompt_safety", "Prompt Safety Checks"),
            ("data_validation", "Data Validation"),
            ("rate_limiting", "Rate Limiting"),
            ("user_approval", "User Approval"),
            ("api_safety", "API Safety Checks"),
            ("ml_safety", "ML Safety Constraints"),
            ("plugin_sandbox", "Plugin Sandboxing"),
            ("cloud_encryption", "Cloud Encryption"),
            ("emergency_only", "Emergency Restrictions"),
        ]

        for protocol_id, protocol_name in protocols:
            checkbox = QCheckBox(protocol_name)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(
                lambda state, pid=protocol_id: self._toggle_protocol(pid, state)
            )
            self.protocol_checkboxes[protocol_id] = checkbox
            protocols_layout.addWidget(checkbox)

        protocols_group.setLayout(protocols_layout)
        layout.addWidget(protocols_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh Status")
        self.refresh_btn.clicked.connect(self._load_status)

        self.emergency_btn = QPushButton("EMERGENCY LOCKDOWN")
        self.emergency_btn.clicked.connect(self._emergency_lockdown)
        self.emergency_btn.setStyleSheet(
            "background-color: #ff0000; color: white; font-weight: bold;"
        )

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.emergency_btn)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _authenticate(self):
        """Authenticate with master password."""
        if not self.command_system:
            QMessageBox.warning(self, "Error", "Command system not available")
            return

        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, "Error", "Please enter a password")
            return

        # If no password is set, set it
        if not self.command_system.master_password_hash:
            if self.command_system.set_master_password(password):
                QMessageBox.information(
                    self, "Success", "Master password set successfully"
                )
                self._load_status()
            else:
                QMessageBox.warning(self, "Error", "Failed to set master password")
            return

        # Authenticate
        if self.command_system.authenticate(password):
            QMessageBox.information(self, "Success", "Authentication successful")
            self._load_status()
        else:
            QMessageBox.warning(self, "Error", "Authentication failed")

        self.password_input.clear()

    def _logout(self):
        """Logout from command system."""
        if self.command_system:
            self.command_system.logout()
            self._load_status()
            QMessageBox.information(self, "Logout", "Logged out successfully")

    def _enable_master_override(self):
        """Enable master override."""
        if not self.command_system:
            return

        reply = QMessageBox.warning(
            self,
            "Confirm Master Override",
            "⚠️ WARNING: This will disable ALL safety protocols!\n\n"
            "Are you absolutely sure you want to proceed?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.command_system.enable_master_override():
                QMessageBox.information(
                    self,
                    "Master Override",
                    "Master override enabled - ALL SAFETY PROTOCOLS DISABLED",
                )
                self._load_status()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to enable master override (authentication required)",
                )

    def _disable_master_override(self):
        """Disable master override."""
        if not self.command_system:
            return

        if self.command_system.disable_master_override():
            QMessageBox.information(
                self,
                "Master Override",
                "Master override disabled - Safety protocols restored",
            )
            self._load_status()
        else:
            QMessageBox.warning(self, "Error", "Failed to disable master override")

    def _toggle_protocol(self, protocol_id: str, state: int):
        """Toggle a specific protocol."""
        if not self.command_system:
            return

        enabled = state == Qt.CheckState.Checked.value
        self.command_system.override_protocol(protocol_id, enabled)

    def _emergency_lockdown(self):
        """Trigger emergency lockdown."""
        if not self.command_system:
            return

        reply = QMessageBox.critical(
            self,
            "Confirm Emergency Lockdown",
            "This will immediately enable ALL safety protocols and revoke authentication.\n\n"
            "Proceed with emergency lockdown?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.command_system.emergency_lockdown()
            QMessageBox.information(
                self,
                "Emergency Lockdown",
                "Emergency lockdown activated - All protocols restored",
            )
            self._load_status()

    def _load_status(self):
        """Load and display current status."""
        if not self.command_system:
            return

        status = self.command_system.get_status()

        # Update auth status
        if status["authenticated"]:
            self.auth_status.setText("Status: Authenticated ✓")
            self.auth_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.auth_status.setText("Status: Not Authenticated")
            self.auth_status.setStyleSheet("color: red;")

        # Update master override status
        if status["master_override_active"]:
            self.master_status.setText("Master Override: ACTIVE ⚠️")
            self.master_status.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.master_status.setText("Master Override: Inactive")
            self.master_status.setStyleSheet("color: green;")

        # Update protocol checkboxes
        for protocol_id, checkbox in self.protocol_checkboxes.items():
            enabled = status["safety_protocols"].get(protocol_id, True)
            checkbox.blockSignals(True)  # Prevent triggering toggle
            checkbox.setChecked(enabled)
            checkbox.blockSignals(False)


class MemoryExpansionDialog(QDialog):
    """Dialog for memory expansion system control."""

    def __init__(self, parent=None, memory_system=None):
        super().__init__(parent)
        self.memory_system = memory_system
        self.setWindowTitle("Memory Expansion System")
        self.setMinimumSize(700, 600)
        self._setup_ui()
        self._load_statistics()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._load_statistics)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Tabs
        tabs = QTabWidget()

        # Statistics tab
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)

        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        stats_layout.addWidget(QLabel("Memory Statistics:"))
        stats_layout.addWidget(self.stats_display)

        refresh_stats_btn = QPushButton("Refresh Statistics")
        refresh_stats_btn.clicked.connect(self._load_statistics)
        stats_layout.addWidget(refresh_stats_btn)

        tabs.addTab(stats_tab, "Statistics")

        # Autonomous Learning tab
        learning_tab = QWidget()
        learning_layout = QVBoxLayout(learning_tab)

        learning_info = QLabel(
            "Autonomous learning allows the AI to explore and learn from the web in the background.\n"
            "The AI will search for relevant information and store it in the knowledge base."
        )
        learning_info.setWordWrap(True)
        learning_layout.addWidget(learning_info)

        learning_interval_layout = QHBoxLayout()
        learning_interval_layout.addWidget(QLabel("Learning Interval (seconds):"))
        self.learning_interval_spin = QSpinBox()
        self.learning_interval_spin.setRange(60, 86400)  # 1 minute to 24 hours
        self.learning_interval_spin.setValue(3600)  # 1 hour default
        learning_interval_layout.addWidget(self.learning_interval_spin)
        learning_layout.addLayout(learning_interval_layout)

        learning_buttons = QHBoxLayout()
        self.start_learning_btn = QPushButton("Start Autonomous Learning")
        self.start_learning_btn.clicked.connect(self._start_learning)
        self.stop_learning_btn = QPushButton("Stop Autonomous Learning")
        self.stop_learning_btn.clicked.connect(self._stop_learning)
        learning_buttons.addWidget(self.start_learning_btn)
        learning_buttons.addWidget(self.stop_learning_btn)
        learning_layout.addLayout(learning_buttons)

        self.learning_status = QLabel("Status: Stopped")
        learning_layout.addWidget(self.learning_status)

        learning_layout.addStretch()
        tabs.addTab(learning_tab, "Autonomous Learning")

        # Search tab
        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)

        search_input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search query...")
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self._search_memory)
        search_input_layout.addWidget(self.search_input)
        search_input_layout.addWidget(search_btn)
        search_layout.addLayout(search_input_layout)

        self.search_results = QListWidget()
        self.search_results.itemDoubleClicked.connect(self._view_memory_item)
        search_layout.addWidget(QLabel("Search Results:"))
        search_layout.addWidget(self.search_results)

        tabs.addTab(search_tab, "Search Memory")

        # Organization tab
        org_tab = QWidget()
        org_layout = QVBoxLayout(org_tab)

        org_info = QLabel(
            "Memory organization helps manage and optimize the stored memory data.\n"
            "This includes archiving old conversations, compressing files, and optimizing retrieval."
        )
        org_info.setWordWrap(True)
        org_layout.addWidget(org_info)

        organize_btn = QPushButton("Organize Memory Now")
        organize_btn.clicked.connect(self._organize_memory)
        org_layout.addWidget(organize_btn)

        self.org_results = QTextEdit()
        self.org_results.setReadOnly(True)
        org_layout.addWidget(QLabel("Organization Results:"))
        org_layout.addWidget(self.org_results)

        org_layout.addStretch()
        tabs.addTab(org_tab, "Organization")

        layout.addWidget(tabs)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _load_statistics(self):
        """Load and display memory statistics."""
        if not self.memory_system:
            return

        stats = self.memory_system.get_statistics()

        stats_text = f"""
Memory Statistics:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Conversations: {stats['total_conversations']}
Total Actions: {stats['total_actions']}
Total Knowledge Items: {stats['total_knowledge_items']}
Total Learned Items: {stats['total_learned_items']}

Memory Size: {stats.get('memory_size_mb', 0)} MB
Learning Enabled: {stats.get('learning_enabled', False)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """

        self.stats_display.setPlainText(stats_text)

        # Update learning status
        if stats.get("learning_enabled", False):
            self.learning_status.setText("Status: Running ✓")
            self.learning_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.learning_status.setText("Status: Stopped")
            self.learning_status.setStyleSheet("color: red;")

    def _start_learning(self):
        """Start autonomous learning."""
        if not self.memory_system:
            return

        interval = self.learning_interval_spin.value()
        self.memory_system.learning_interval = interval

        if self.memory_system.start_autonomous_learning():
            QMessageBox.information(
                self, "Learning Started", "Autonomous learning has been started"
            )
            self._load_statistics()
        else:
            QMessageBox.warning(self, "Error", "Learning is already running")

    def _stop_learning(self):
        """Stop autonomous learning."""
        if not self.memory_system:
            return

        if self.memory_system.stop_autonomous_learning():
            QMessageBox.information(
                self, "Learning Stopped", "Autonomous learning has been stopped"
            )
            self._load_statistics()
        else:
            QMessageBox.warning(self, "Error", "Learning is not running")

    def _search_memory(self):
        """Search memory."""
        if not self.memory_system:
            return

        query = self.search_input.text()
        if not query:
            return

        results = self.memory_system.search_memory(query, limit=20)

        self.search_results.clear()
        for result in results:
            result_type = result["type"]
            result_data = result["data"]

            if result_type == "conversation":
                summary = result_data.get("summary", "No summary")
                self.search_results.addItem(f"[Conversation] {summary}")
            elif result_type == "action":
                action_type = result_data.get("action_type", "Unknown")
                self.search_results.addItem(f"[Action] {action_type}")
            elif result_type == "knowledge":
                title = result_data.get("title", "Untitled")
                self.search_results.addItem(f"[Knowledge] {title}")

    def _view_memory_item(self, item):
        """View a memory item in detail."""
        # Placeholder for viewing memory details
        QMessageBox.information(self, "Memory Item", f"Selected: {item.text()}")

    def _organize_memory(self):
        """Organize memory."""
        if not self.memory_system:
            return

        results = self.memory_system.organize_memory()

        results_text = f"""
Memory Organization Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Archived Conversations: {results.get('archived_conversations', 0)}
Archived Actions: {results.get('archived_actions', 0)}
Compressed Files: {results.get('compressed_files', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """

        self.org_results.setPlainText(results_text)
        QMessageBox.information(
            self, "Organization Complete", "Memory organization completed successfully"
        )
