"""Login dialog with Mass Effect / Sci-Fi themed interface.

Flow:
 - On first run (no users), prompt to create a secure admin account.
 - Show username/password prompt with holographic styling
 - On successful authentication, show a Mission Select screen
 - When the user selects a module and clicks Access, the dialog accepts and
   exposes selected_tab and username for the caller.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QMessageBox,
    QFrame,
)
from PyQt6.QtCore import Qt
from app.core.user_manager import UserManager


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Assistant — Login")
        self.setFixedSize(500, 400)
        self.user_manager = UserManager()
        self.selected_tab = 0
        self.username = None
        self._apply_sci_fi_style()
        self._build_ui()

        # If no users exist, prompt onboarding to create an admin account
        if not self.user_manager.users:
            self._onboard_admin()

    def _apply_sci_fi_style(self):
        """Apply Mass Effect / Sci-Fi styling to the dialog."""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0e17,
                    stop:0.5 #0d1526,
                    stop:1 #0a0e17);
            }
            QLabel {
                color: #a0d4ff;
                font-weight: 500;
            }
            QLineEdit {
                background: rgba(10, 20, 35, 0.9);
                color: #c0e8ff;
                border: 1px solid rgba(0, 180, 255, 0.4);
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(0, 220, 255, 0.7);
                background: rgba(15, 25, 45, 0.95);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a3050,
                    stop:0.5 #0d2040,
                    stop:1 #1a3050);
                color: #00d4ff;
                border: 1px solid rgba(0, 200, 255, 0.5);
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #254060,
                    stop:0.5 #153050,
                    stop:1 #254060);
                color: #40e0ff;
                border: 1px solid rgba(0, 220, 255, 0.7);
            }
            QListWidget {
                background: rgba(10, 20, 35, 0.9);
                color: #a0d4ff;
                border: 1px solid rgba(0, 180, 255, 0.3);
                border-radius: 4px;
                outline: none;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid rgba(0, 180, 255, 0.1);
            }
            QListWidget::item:hover {
                background: rgba(0, 180, 255, 0.15);
            }
            QListWidget::item:selected {
                background: rgba(0, 200, 255, 0.25);
                color: #ffffff;
                border-left: 3px solid #00d4ff;
            }
        """)

    def _build_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header_label = QLabel("◈ System Access ◈")
        header_label.setStyleSheet("""
            color: #00d4ff;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(header_label)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: rgba(0, 200, 255, 0.3);")
        self.layout.addWidget(sep)

        # Login widgets
        self.layout.addWidget(QLabel("Username:"))
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Enter username...")
        self.layout.addWidget(self.user_input)

        self.layout.addWidget(QLabel("Password:"))
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setPlaceholderText("Enter password...")
        self.pass_input.returnPressed.connect(self.try_login)
        self.layout.addWidget(self.pass_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.try_login)
        self.layout.addWidget(self.login_button)

        # Module Select (hidden until login)
        self.toc = QListWidget()
        modules = [
            "Chat — AI Communication",
            "Learning Paths — Skills Development",
            "Data Analysis — Analytics Center",
            "Security Resources — Security Tools",
            "Location Tracking — GPS Tracking",
            "Emergency Alert — Alert System",
        ]
        for m in modules:
            self.toc.addItem(m)

        self.open_button = QPushButton("Open Module")
        self.open_button.clicked.connect(self.open_chapter)

    def _onboard_admin(self):
        """Prompt the user to create an admin account on first run."""
        msg = (
            "Welcome!\n\n"
            "No users found in database.\n"
            "Please create an admin account to continue."
        )
        QMessageBox.information(self, "Onboarding", msg)

        # Replace login UI with admin creation widgets
        for w in (self.user_input, self.pass_input, self.login_button):
            w.hide()

        self.layout.addWidget(QLabel("Admin Username:"))
        self.admin_user = QLineEdit()
        self.admin_user.setPlaceholderText("Enter admin username...")
        self.layout.addWidget(self.admin_user)

        self.layout.addWidget(QLabel("Admin Password:"))
        self.admin_pass = QLineEdit()
        self.admin_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.admin_pass.setPlaceholderText("Enter secure password...")
        self.layout.addWidget(self.admin_pass)

        self.create_admin_btn = QPushButton("Create Admin Account")
        self.create_admin_btn.clicked.connect(self.create_admin_account)
        self.layout.addWidget(self.create_admin_btn)

    def create_admin_account(self):
        username = self.admin_user.text().strip()
        password = self.admin_pass.text().strip()
        if not username or not password:
            msg = "Please provide username and password for admin account."
            QMessageBox.warning(self, "Validation", msg)
            return
        ok = self.user_manager.create_user(username, password, persona="admin")
        if ok:
            msg = "Admin account created successfully!\n\nYou may now login."
            QMessageBox.information(self, "Success", msg)
            # Remove admin creation widgets and show login
            for w in (self.admin_user, self.admin_pass, self.create_admin_btn):
                w.hide()
            for w in (self.user_input, self.pass_input, self.login_button):
                w.show()
        else:
            msg = "Username already exists. Please choose another."
            QMessageBox.warning(self, "Conflict", msg)

    def try_login(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()
        if not username or not password:
            msg = "Please enter username and password."
            QMessageBox.warning(self, "Validation", msg)
            return
        if self.user_manager.authenticate(username, password):
            self.username = username
            # Show Module Select
            self._show_toc()
        else:
            msg = "Invalid credentials. Please try again."
            QMessageBox.warning(self, "Login Failed", msg)

    def _show_toc(self):
        # Clear login widgets and show Module Select
        for w in (self.user_input, self.pass_input, self.login_button):
            w.hide()

        # Find and hide the labels above the input fields
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, QLabel):
                text = widget.text()
                if "Username" in text or "Password" in text:
                    widget.hide()

        select_label = QLabel("◈ Select Module ◈")
        select_label.setStyleSheet("""
            color: #00d4ff;
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
        """)
        select_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(select_label)
        self.layout.addWidget(self.toc)
        self.layout.addWidget(self.open_button)

    def open_chapter(self):
        idx = self.toc.currentRow()
        if idx < 0:
            msg = "Please select a module to access."
            QMessageBox.warning(self, "Selection Required", msg)
            return
        self.selected_tab = idx
        self.accept()
