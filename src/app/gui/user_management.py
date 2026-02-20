"""User management widget: list/create/delete/update/approve users.

This widget depends on `UserManager` for persistence. It provides a simple
moderate UI to manage users (create, delete, set roles, approve accounts,
reset passwords, and set a profile picture path).
"""

import os

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.user_manager import UserManager

# UI Constants
SELECT_USER_FIRST_MSG = "Select a user first"


class UserManagementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.um = UserManager()
        self._build_ui()
        self.refresh_user_list()

    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)

        self.user_list = QListWidget()
        self.user_list.currentTextChanged.connect(self.on_user_selected)
        self.main_layout.addWidget(QLabel("Users:"))
        self.main_layout.addWidget(self.user_list)

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

        self.main_layout.addLayout(btn_row)

        # Details area
        details_text = "Select a user to see details and edit settings."
        self.details_label = QLabel(details_text)
        self.main_layout.addWidget(self.details_label)

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
        self.main_layout.addLayout(form_row)

    def refresh_user_list(self):
        self.user_list.clear()
        for uname in sorted(self.um.users.keys()):
            self.user_list.addItem(uname)
        # clear preview
        self.avatar_preview.clear()

    def on_user_selected(self, username: str):
        if not username:
            return
        data = self.um.get_user_data(username)
        self.username_field.setText(username)
        self.role_combo.setCurrentText(data.get("role", "user"))
        self.pic_field.setText(data.get("profile_picture", ""))
        self.approved_label.setText(f"Approved: {data.get('approved', False)}")

    def browse_picture(self):
        fname, _ = QFileDialog.getOpenFileName(
            self,
            "Select profile picture",
            os.getcwd(),
            "Images (*.png *.jpg *.jpeg *.bmp)",
        )
        if fname:
            self.pic_field.setText(fname)
            pix = QPixmap(fname)
            if not pix.isNull():
                self.avatar_preview.setPixmap(pix.scaled(96, 96))

    def create_user_dialog(self):
        dlg = CreateUserDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            uname, pw, approved, role, pic = dlg.get_values()
            success = self.um.create_user(uname, pw)
            if success:
                self.um.update_user(
                    uname,
                    approved=approved,
                    role=role,
                    profile_picture=pic,
                )
                created_msg = f"User '{uname}' created."
                QMessageBox.information(self, "Created", created_msg)
                self.refresh_user_list()
            else:
                QMessageBox.warning(self, "Exists", "User already exists")

    def delete_user(self):
        item = self.user_list.currentItem()
        username = item.text() if item else None
        if not username:
            QMessageBox.warning(self, "Delete", "Select a user to delete")
            return
        if username == self.um.current_user:
            QMessageBox.warning(self, "Delete", "Cannot delete currently logged-in user")
            return
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete user '{username}'? This is irreversible.",
        )
        if confirm == QMessageBox.StandardButton.Yes:
            ok = self.um.delete_user(username)
            if ok:
                QMessageBox.information(self, "Deleted", "User deleted")
                self.refresh_user_list()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete user")

    def toggle_approve(self):
        item = self.user_list.currentItem()
        username = item.text() if item else None
        if not username:
            QMessageBox.warning(self, "Approve", SELECT_USER_FIRST_MSG)
            return
        data = self.um.users.get(username, {})
        new = not data.get("approved", False)
        self.um.update_user(username, approved=new)
        self.on_user_selected(username)
        updated_msg = f"User '{username}' approved set to {new}"
        QMessageBox.information(self, "Updated", updated_msg)

    def reset_password(self):
        item = self.user_list.currentItem()
        username = item.text() if item else None
        if not username:
            QMessageBox.warning(self, "Reset Password", SELECT_USER_FIRST_MSG)
            return
        dlg = ResetPasswordDialog(username, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            newpw = dlg.get_password()
            if newpw:
                self.um.set_password(username, newpw)
                QMessageBox.information(self, "Password", "Password updated")

    def save_changes(self):
        username = self.username_field.text().strip()
        if not username:
            QMessageBox.warning(
                self,
                "Save",
                "Username cannot be empty",
            )
            return
        role = self.role_combo.currentText()
        pic = self.pic_field.text().strip()
        approved = self.approved_label.text().endswith("True")
        current_item = self.user_list.currentItem()
        if current_item is None:
            QMessageBox.warning(self, "Save", "Select a user first")
            return
        ok = self.um.update_user(
            current_item.text(),
            role=role,
            profile_picture=pic,
            approved=approved,
        )
        if ok:
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

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _browse(self):
        fname, _ = QFileDialog.getOpenFileName(
            self,
            "Select profile picture",
            os.getcwd(),
            "Images (*.png *.jpg *.jpeg *.bmp)",
        )
        if fname:
            self.pic_field_d.setText(fname)

    def get_values(self):
        return (
            self.username.text().strip(),
            self.password.text(),
            self.approved_cb.isChecked(),
            self.role.currentText(),
            self.pic_field_d.text().strip(),
        )


class ResetPasswordDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Reset Password: {username}")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("New password:"))
        self.pw = QLineEdit()
        self.pw.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pw)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_password(self):
        return self.pw.text()
