"""
Learning Request Log GUI - Interface for managing AI learning requests.
"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class LearningRequestDialog(QDialog):
    """Dialog for managing AI learning requests."""

    def __init__(self, parent=None, request_log=None):
        super().__init__(parent)
        self.request_log = request_log
        self.setWindowTitle("Learning Request Log - AI Learning Requests")
        self.setMinimumSize(900, 700)
        self._setup_ui()
        self._refresh_requests()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_requests)
        self.refresh_timer.start(10000)  # Refresh every 10 seconds

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(
            "🤖 AI Learning Request Log\n\n"
            "The AI has discovered information and requests your approval to learn it.\n"
            "Approved requests are integrated into the AI's knowledge.\n"
            "Denied requests go to the Black Vault and become invisible to the AI."
        )
        header.setWordWrap(True)
        header.setStyleSheet(
            "font-weight: bold; padding: 10px; background-color: #f0f0f0;"
        )
        layout.addWidget(header)

        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QHBoxLayout()

        self.stat_total = QLabel("Total: 0")
        self.stat_pending = QLabel("⏳ Pending: 0")
        self.stat_pending.setStyleSheet("color: orange; font-weight: bold;")
        self.stat_approved = QLabel("✓ Approved: 0")
        self.stat_approved.setStyleSheet("color: green;")
        self.stat_denied = QLabel("✗ Denied: 0")
        self.stat_denied.setStyleSheet("color: red;")
        self.stat_vault = QLabel("🔒 Black Vault: 0")
        self.stat_vault.setStyleSheet("color: darkred; font-weight: bold;")

        stats_layout.addWidget(self.stat_total)
        stats_layout.addWidget(self.stat_pending)
        stats_layout.addWidget(self.stat_approved)
        stats_layout.addWidget(self.stat_denied)
        stats_layout.addWidget(self.stat_vault)
        stats_layout.addStretch()

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Pending requests list
        requests_group = QGroupBox("⏳ Pending Requests (Awaiting Your Approval)")
        requests_layout = QVBoxLayout()

        self.requests_list = QListWidget()
        self.requests_list.itemClicked.connect(self._on_request_selected)
        requests_layout.addWidget(self.requests_list)

        refresh_btn = QPushButton("🔄 Refresh Requests")
        refresh_btn.clicked.connect(self._refresh_requests)
        requests_layout.addWidget(refresh_btn)

        requests_group.setLayout(requests_layout)
        layout.addWidget(requests_group)

        # Request details
        details_group = QGroupBox("Request Details")
        details_layout = QVBoxLayout()

        self.details_display = QTextEdit()
        self.details_display.setReadOnly(True)
        details_layout.addWidget(self.details_display)

        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        # Action buttons
        action_layout = QHBoxLayout()

        self.approve_btn = QPushButton("✓ Approve & Integrate")
        self.approve_btn.clicked.connect(self._approve_request)
        self.approve_btn.setStyleSheet(
            "background-color: #44ff44; font-weight: bold; padding: 10px;"
        )
        self.approve_btn.setEnabled(False)

        self.deny_btn = QPushButton("✗ Deny & Black Vault")
        self.deny_btn.clicked.connect(self._deny_request)
        self.deny_btn.setStyleSheet(
            "background-color: #ff4444; color: white; font-weight: bold; padding: 10px;"
        )
        self.deny_btn.setEnabled(False)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        action_layout.addWidget(self.approve_btn)
        action_layout.addWidget(self.deny_btn)
        action_layout.addStretch()
        action_layout.addWidget(close_btn)

        layout.addLayout(action_layout)

    def _refresh_requests(self):
        """Refresh the pending requests list."""
        if not self.request_log:
            return

        # Update statistics
        stats = self.request_log.get_statistics()
        self.stat_total.setText(f"Total: {stats['total_requests']}")
        self.stat_pending.setText(f"⏳ Pending: {stats['pending_requests']}")
        self.stat_approved.setText(f"✓ Approved: {stats['approved_requests']}")
        self.stat_denied.setText(f"✗ Denied: {stats['denied_requests']}")
        self.stat_vault.setText(f"🔒 Black Vault: {stats['black_vault_items']}")

        # Get pending requests (for_ai=False so we can see them)
        pending = self.request_log.get_pending_requests(for_ai=False)

        # Clear and repopulate list
        self.requests_list.clear()
        for request in pending:
            priority = request.get("priority", "medium")
            priority_icon = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
            }.get(priority, "🟡")

            title = request.get("title", "Untitled")
            timestamp = request.get("timestamp", "")[:19]  # Remove microseconds

            item_text = f"{priority_icon} [{timestamp}] {title}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, request)
            self.requests_list.addItem(item)

        # Clear details if no selection
        if self.requests_list.count() == 0:
            self.details_display.clear()
            self.approve_btn.setEnabled(False)
            self.deny_btn.setEnabled(False)

    def _on_request_selected(self, item: QListWidgetItem):
        """Handle request selection."""
        request = item.data(Qt.ItemDataRole.UserRole)
        if not request:
            return

        # Display request details
        priority_label = {
            "critical": "🔴 CRITICAL",
            "high": "🟠 HIGH",
            "medium": "🟡 MEDIUM",
            "low": "🟢 LOW",
        }.get(request.get("priority", "medium"), "🟡 MEDIUM")

        details_text = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI LEARNING REQUEST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 TITLE:
{request.get('title', 'N/A')}

📅 SUBMITTED:
{request.get('timestamp', 'N/A')}

⚡ PRIORITY:
{priority_label}

📂 CATEGORY:
{request.get('category', 'general').title()}

🌐 SOURCE:
{request.get('source', 'N/A')}

🏷️ TAGS:
{', '.join(request.get('tags', []) or ['None'])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 AI JUSTIFICATION (Why the AI wants to learn this):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{request.get('justification', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 CONTENT (What the AI wants to learn):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{request.get('content', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ DECISION REQUIRED:

✓ APPROVE: The AI will integrate this knowledge and can use it
✗ DENY: This goes to Black Vault - AI can NEVER access it

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """

        self.details_display.setPlainText(details_text)

        # Enable action buttons
        self.approve_btn.setEnabled(True)
        self.deny_btn.setEnabled(True)

    def _approve_request(self):
        """Approve the selected request."""
        current_item = self.requests_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self, "No Selection", "Please select a request to approve."
            )
            return

        request = current_item.data(Qt.ItemDataRole.UserRole)
        if not request:
            return

        # Confirm approval
        reply = QMessageBox.question(
            self,
            "Confirm Approval",
            f"Approve this learning request?\n\n"
            f"Title: {request.get('title', 'N/A')}\n\n"
            f"The AI will integrate this knowledge and be able to use it in future interactions.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if reply == QMessageBox.StandardButton.Yes:
            request_id = request.get("id")
            if self.request_log.approve_request(request_id, user_notes="User approved"):
                QMessageBox.information(
                    self,
                    "Request Approved",
                    "✓ Learning request approved!\n\n"
                    "The knowledge has been integrated into the AI's memory.\n"
                    "The AI can now access and use this information.",
                )
                self._refresh_requests()
            else:
                QMessageBox.warning(self, "Error", "Failed to approve request.")

    def _deny_request(self):
        """Deny the selected request."""
        current_item = self.requests_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self, "No Selection", "Please select a request to deny."
            )
            return

        request = current_item.data(Qt.ItemDataRole.UserRole)
        if not request:
            return

        # Confirm denial
        reply = QMessageBox.critical(
            self,
            "Confirm Denial",
            f"⚠️ DENY this learning request and send to Black Vault?\n\n"
            f"Title: {request.get('title', 'N/A')}\n\n"
            f"WARNING: This content will be:\n"
            f"• Moved to the Black Vault\n"
            f"• Permanently inaccessible to the AI\n"
            f"• Filtered from future AI discoveries\n"
            f"• Treated as irrelevant if re-discovered\n\n"
            f"This action creates a permanent block for this content.\n"
            f"Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            request_id = request.get("id")
            reason = "User denied - not suitable for AI learning"

            if self.request_log.deny_request(request_id, reason=reason):
                QMessageBox.information(
                    self,
                    "Request Denied",
                    "✗ Learning request denied.\n\n"
                    "The content has been moved to the Black Vault.\n"
                    "The AI will never see or access this content.\n"
                    "If the AI re-discovers this information, it will be\n"
                    "automatically filtered and treated as irrelevant.",
                )
                self._refresh_requests()
            else:
                QMessageBox.warning(self, "Error", "Failed to deny request.")


class BlackVaultViewDialog(QDialog):
    """Dialog for viewing Black Vault contents (admin only - AI cannot access)."""

    def __init__(self, parent=None, request_log=None):
        super().__init__(parent)
        self.request_log = request_log
        self.setWindowTitle("🔒 Black Vault - Denied Content")
        self.setMinimumSize(800, 600)
        self._setup_ui()
        self._load_vault_contents()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Warning header
        header = QLabel(
            "🔒 BLACK VAULT - DENIED CONTENT\n\n"
            "⚠️ This contains all content denied to the AI.\n"
            "The AI cannot see, access, or retrieve anything here.\n"
            "If the AI re-discovers this content, it is automatically filtered."
        )
        header.setWordWrap(True)
        header.setStyleSheet(
            "font-weight: bold; padding: 10px; "
            "background-color: #330000; color: white;"
        )
        layout.addWidget(header)

        # Statistics
        self.vault_stats = QLabel("Vault Items: 0")
        self.vault_stats.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(self.vault_stats)

        # Vault contents list
        self.vault_list = QListWidget()
        self.vault_list.itemClicked.connect(self._on_vault_item_selected)
        layout.addWidget(QLabel("Denied Requests:"))
        layout.addWidget(self.vault_list)

        # Details display
        self.vault_details = QTextEdit()
        self.vault_details.setReadOnly(True)
        layout.addWidget(QLabel("Request Details:"))
        layout.addWidget(self.vault_details)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _load_vault_contents(self):
        """Load Black Vault contents."""
        if not self.request_log:
            return

        stats = self.request_log.get_statistics()
        self.vault_stats.setText(f"Vault Items: {stats['black_vault_items']}")

        self.vault_list.clear()

        # Load denied requests
        for request_id, request_info in self.request_log.request_index.items():
            if request_info.get("status") == "denied":
                request_data = self.request_log.get_request_by_id(
                    request_id, for_ai=False
                )
                if request_data:
                    title = request_data.get("title", "Untitled")
                    timestamp = request_data.get("denied_timestamp", "")[:19]

                    item_text = f"🔒 [{timestamp}] {title}"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, request_data)
                    self.vault_list.addItem(item)

    def _on_vault_item_selected(self, item: QListWidgetItem):
        """Handle vault item selection."""
        request = item.data(Qt.ItemDataRole.UserRole)
        if not request:
            return

        details_text = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔒 BLACK VAULT ENTRY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TITLE: {request.get('title', 'N/A')}
DENIED: {request.get('denied_timestamp', 'N/A')}
REASON: {request.get('denial_reason', 'N/A')}

ORIGINAL REQUEST:
Submitted: {request.get('timestamp', 'N/A')}
Category: {request.get('category', 'N/A')}
Source: {request.get('source', 'N/A')}

AI JUSTIFICATION:
{request.get('justification', 'N/A')}

DENIED CONTENT:
{request.get('content', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ This content is permanently inaccessible to the AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """

        self.vault_details.setPlainText(details_text)
