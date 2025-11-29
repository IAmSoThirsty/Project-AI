"""User management widget: list/create/delete/update/approve users.

This widget depends on `UserManager` for persistence. It provides a simple
moderate UI to manage users (create, delete, set roles, approve accounts,
reset passwords, and set a profile picture path).
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
    QFileDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QCheckBox,
)
from PyQt6.QtGui import QPixmap
from app.core.user_manager import UserManager
import os


class UserManagementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_manager = UserManager()
        self._build_ui()
        self.refresh_user_list()

    def _build_ui(self):
        self.layout = QVBoxLayout(self)

        self.user_list = QListWidget()
        self.user_list.currentTextChanged.connect(self.on_user_selected)
        self.layout.addWidget(QLabel("Users:"))
        self.layout.addWidget(self.user_list)

        # Buttons row
        btn_row = QHBoxLayout()
        self.create_btn = QPushButton("Create User")
        self.create_btn.clicked.connect(self.create_user_dialog)
        btn_row.addWidget(self.create_btn)

        self.delete_btn = QPushButton("Delete User")
        self.delete_btn.clicked.connect(self.delete_user)
        btn_row.addWidget(self.delete_btn)

        self.approve_btn = QPushButton("Approve / Revoke")
        self.approve_btn.clicked.connect(self.toggle_approve)
        btn_row.addWidget(self.approve_btn)

        self.reset_pw_btn = QPushButton("Reset Password")
        self.reset_pw_btn.clicked.connect(self.reset_password)
        btn_row.addWidget(self.reset_pw_btn)

        self.layout.addLayout(btn_row)

        # Details area
        self.details_label = QLabel("Select a user to see details and edit settings.")
        self.layout.addWidget(self.details_label)

        form_row = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel("Username:"))
        self.username_field = QLineEdit()
        left.addWidget(self.username_field)

        left.addWidget(QLabel("Role:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        left.addWidget(self.role_combo)

        left.addWidget(QLabel("Profile picture (path):"))
        pic_row = QHBoxLayout()
        self.pic_field = QLineEdit()
        pic_row.addWidget(self.pic_field)
        self.pic_btn = QPushButton("Browse")
        self.pic_btn.clicked.connect(self.browse_picture)
        pic_row.addWidget(self.pic_btn)
        left.addLayout(pic_row)

        # Avatar preview
        left.addWidget(QLabel("Avatar preview:"))
        self.avatar_preview = QLabel()
        self.avatar_preview.setFixedSize(96, 96)
        self.avatar_preview.setStyleSheet("border:1px solid #ccc; background: #fff;")
        left.addWidget(self.avatar_preview)

        form_row.addLayout(left)

        right = QVBoxLayout()
        self.approved_label = QLabel("Approved: False")
        right.addWidget(self.approved_label)

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_changes)
        right.addWidget(self.save_btn)

        form_row.addLayout(right)
        self.layout.addLayout(form_row)

    def refresh_user_list(self):
        self.user_list.clear()
        for username in sorted(self.user_manager.users.keys()):
            self.user_list.addItem(username)
        # clear preview
        self.avatar_preview.clear()

    def on_user_selected(self, username: str):
        if not username:
            return
        user_data = self.user_manager.get_user_data(username)
        self.username_field.setText(username)
        self.role_combo.setCurrentText(user_data.get('role', 'user'))
        self.pic_field.setText(user_data.get('profile_picture', ''))
        self.approved_label.setText(f"Approved: {user_data.get('approved', False)}")

    def browse_picture(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select profile picture",
            os.getcwd(),
            "Images (*.png *.jpg *.jpeg *.bmp)",
        )
        if filename:
            self.pic_field.setText(filename)
            pixmap = QPixmap(filename)
            if not pixmap.isNull():
                self.avatar_preview.setPixmap(pixmap.scaled(96, 96))

    def create_user_dialog(self):
        dialog = CreateUserDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            username, password, approved, role, profile_picture_path = dialog.get_values()
            success = self.user_manager.create_user(username, password)
            if success:
                self.user_manager.update_user(
                    username, approved=approved, role=role, profile_picture=profile_picture_path
                )
                QMessageBox.information(self, "Created", f"User '{username}' created.")
                self.refresh_user_list()
            else:
                QMessageBox.warning(self, "Exists", "User already exists")

    def delete_user(self):
        username = self.user_list.currentItem().text() if self.user_list.currentItem() else None
        if not username:
            QMessageBox.warning(self, "Delete", "Select a user to delete")
            return
        if username == self.user_manager.current_user:
            QMessageBox.warning(self, "Delete", "Cannot delete currently logged-in user")
            return
        confirm = QMessageBox.question(self, "Confirm Delete", f"Delete user '{username}'? This is irreversible.")
        if confirm == QMessageBox.StandardButton.Yes:
            deletion_successful = self.user_manager.delete_user(username)
            if deletion_successful:
                QMessageBox.information(self, "Deleted", "User deleted")
                self.refresh_user_list()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete user")

    def toggle_approve(self):
        username = self.user_list.currentItem().text() if self.user_list.currentItem() else None
        if not username:
            QMessageBox.warning(self, "Approve", "Select a user first")
            return
        user_data = self.user_manager.users.get(username, {})
        new_approval_status = not user_data.get('approved', False)
        self.user_manager.update_user(username, approved=new_approval_status)
        self.on_user_selected(username)
        QMessageBox.information(self, "Updated", f"User '{username}' approved set to {new_approval_status}")

    def reset_password(self):
        username = self.user_list.currentItem().text() if self.user_list.currentItem() else None
        if not username:
            QMessageBox.warning(self, "Reset Password", "Select a user first")
            return
        dialog = ResetPasswordDialog(username, parent=self)
        if dialog.exec() == QDialog.Accepted:
            new_password = dialog.get_password()
            if new_password:
                self.user_manager.set_password(username, new_password)
                QMessageBox.information(self, "Password", "Password updated")

    def save_changes(self):
        username = self.username_field.text().strip()
        if not username:
            QMessageBox.warning(self, "Save", "Username cannot be empty")
            return
        role = self.role_combo.currentText()
        profile_picture_path = self.pic_field.text().strip()
        approved = True if self.approved_label.text().endswith('True') else False
        selected_username = self.user_list.currentItem().text()
        update_successful = self.user_manager.update_user(
            selected_username, role=role, profile_picture=profile_picture_path, approved=approved
        )
        if update_successful:
            QMessageBox.information(self, "Saved", "User updated")
            self.refresh_user_list()
        else:
            QMessageBox.warning(self, "Error", "Failed to save user")


class CreateUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create User")
        self.setModal(True)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Username:"))
        self.username = QLineEdit()
        layout.addWidget(self.username)

        layout.addWidget(QLabel("Password:"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        self.approved_cb = QCheckBox("Approved")
        self.approved_cb.setChecked(True)
        layout.addWidget(self.approved_cb)

        layout.addWidget(QLabel("Role:"))
        self.role = QComboBox()
        self.role.addItems(["user", "admin"])
        layout.addWidget(self.role)

        pic_row = QHBoxLayout()
        self.pic_field_d = QLineEdit()
        pic_row.addWidget(self.pic_field_d)
        self.pic_btn_d = QPushButton("Browse")
        self.pic_btn_d.clicked.connect(self._browse)
        pic_row.addWidget(self.pic_btn_d)
        layout.addLayout(pic_row)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _browse(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select profile picture",
            os.getcwd(),
            "Images (*.png *.jpg *.jpeg *.bmp)",
        )
        if filename:
            self.pic_field_d.setText(filename)

    def get_values(self):
        return (self.username.text().strip(), self.password.text(), self.approved_cb.isChecked(), self.role.currentText(), self.pic_field_d.text().strip())


class ResetPasswordDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Reset Password: {username}")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("New password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_password(self):
        return self.password_input.text()
