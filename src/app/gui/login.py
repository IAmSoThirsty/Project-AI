"""Login dialog with a Table of Contents (book-like appearance).

Flow:
 - On first run (no users), prompt to create a secure admin account.
 - Show username/password prompt
 - On successful authentication, show a "Table of Contents" list of chapters
 - When the user selects a chapter and clicks Open, the dialog accepts and
   exposes selected_tab and username for the caller.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QMessageBox,
)
from app.core.user_manager import UserManager


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - My Best Friend AI (Book)")
        self.user_manager = UserManager()
        self.selected_tab = 0
        self.username = None
        self._build_ui()

        # If no users exist, prompt onboarding to create an admin account
        if not self.user_manager.users:
            self._onboard_admin()

    def _build_ui(self):
        self.layout = QVBoxLayout(self)

        # Login widgets
        self.layout.addWidget(QLabel("Username:"))
        self.user_input = QLineEdit()
        self.layout.addWidget(self.user_input)

        self.layout.addWidget(QLabel("Password:"))
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.pass_input)

        self.login_button = QPushButton("Log in")
        self.login_button.clicked.connect(self.try_login)
        self.layout.addWidget(self.login_button)

        # Table of Contents (hidden until login)
        self.toc = QListWidget()
        chapters = [
            "Chapter 1 — Chat",
            "Chapter 2 — Learning Paths",
            "Chapter 3 — Data Analysis",
            "Chapter 4 — Security Resources",
            "Chapter 5 — Location Tracking",
            "Chapter 6 — Emergency Alert",
        ]
        for c in chapters:
            self.toc.addItem(c)

        self.open_button = QPushButton("Open Chapter")
        self.open_button.clicked.connect(self.open_chapter)

    def _onboard_admin(self):
        """Prompt the user to create an admin account on first run."""
        msg = (
            "No users found. You must create an admin account to continue."
            " Please choose a secure username and password."
        )
        QMessageBox.information(self, "Onboarding", msg)

        # Replace login UI with admin creation widgets
        for w in (self.user_input, self.pass_input, self.login_button):
            w.hide()

        self.layout.addWidget(QLabel("Admin username:"))
        self.admin_user = QLineEdit()
        self.layout.addWidget(self.admin_user)

        self.layout.addWidget(QLabel("Admin password:"))
        self.admin_pass = QLineEdit()
        self.admin_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.admin_pass)

        self.create_admin_btn = QPushButton("Create Admin Account")
        self.create_admin_btn.clicked.connect(self.create_admin_account)
        self.layout.addWidget(self.create_admin_btn)

    def create_admin_account(self):
        username = self.admin_user.text().strip()
        password = self.admin_pass.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Onboarding", "Provide username and password for admin")
            return
        ok = self.user_manager.create_user(username, password, persona="admin")
        if ok:
            QMessageBox.information(self, "Onboarding", "Admin account created — please log in.")
            # Remove admin creation widgets and show login
            for w in (self.admin_user, self.admin_pass, self.create_admin_btn):
                w.hide()
            for w in (self.user_input, self.pass_input, self.login_button):
                w.show()
        else:
            QMessageBox.warning(self, "Onboarding", "Username already exists — choose another")

    def try_login(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Login", "Enter username and password")
            return
        if self.user_manager.authenticate(username, password):
            self.username = username
            # Show TOC
            self._show_toc()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid credentials")

    def _show_toc(self):
        # Clear login widgets and show TOC
        for w in (self.user_input, self.pass_input, self.login_button):
            w.hide()
        self.layout.addWidget(QLabel("Table of Contents"))
        self.layout.addWidget(self.toc)
        self.layout.addWidget(self.open_button)

    def open_chapter(self):
        idx = self.toc.currentRow()
        if idx < 0:
            warning_msg = "Please select a chapter from the Table of Contents"
            QMessageBox.warning(self, "Select Chapter", warning_msg)
            return
        self.selected_tab = idx
        self.accept()
