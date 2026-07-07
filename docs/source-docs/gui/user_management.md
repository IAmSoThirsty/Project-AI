---
title: "UserManagementWidget - User CRUD and Access Control Component"
id: "user-management-widget-gui"
type: "technical-reference"
version: "1.0.0"
created_date: "2026-04-20"
updated_date: "2026-04-20"
status: "production"
author: "AGENT-044"
contributors: ["GUI Team", "Security Team", "Authentication Team"]
category: "gui-documentation"
tags: ["pyqt6", "gui", "user-management", "crud", "authentication", "authorization", "avatar", "rbac"]
technologies: ["Python 3.11+", "PyQt6 6.4+", "bcrypt", "JSON"]
related_docs:
  - "user-manager-core"
  - "login-dialog"
  - "dashboard"
  - "access-control"
  - "authentication-security"
description: "Comprehensive documentation for the UserManagementWidget PyQt6 component - complete user CRUD interface with avatar management, role-based access control, password reset, account approval, and bcrypt-secured authentication"
security_classification: "internal"
review_status: "peer-reviewed"
audience: ["developers", "security-engineers", "gui-developers", "administrators"]
---

# UserManagementWidget - User CRUD and Access Control Component

**Module:** `src/app/gui/user_management.py`  
**Classes:** `UserManagementWidget`, `CreateUserDialog`, `ResetPasswordDialog`  
**Lines of Code:** 317  
**Purpose:** Complete administrative interface for user account lifecycle management with role-based access control and security controls

---

## Table of Contents

1. [Component Overview](#component-overview)
2. [UI Layout Architecture](#ui-layout-architecture)
3. [Core Architecture](#core-architecture)
4. [API Reference](#api-reference)
5. [Security Features](#security-features)
6. [Integration Patterns](#integration-patterns)
7. [Usage Examples](#usage-examples)
8. [Styling Guide](#styling-guide)
9. [Accessibility Considerations](#accessibility-considerations)
10. [Security Considerations](#security-considerations)
11. [Troubleshooting](#troubleshooting)

---

## Component Overview

### Purpose

The **UserManagementWidget** provides a comprehensive administrative interface for managing user accounts in the Project-AI application. It exposes full CRUD (Create, Read, Update, Delete) operations on user accounts, integrating with the `UserManager` core module for bcrypt-secured password storage and JSON-based persistence. This widget is designed for administrator use and includes critical security controls like account approval workflows and role assignment.

### Key Features

- **User List Display**: Alphabetically sorted list of all registered users
- **Create User**: Modal dialog for new account creation with password, role, approval status, and avatar
- **Delete User**: Confirmation dialog with protection against self-deletion
- **Role Management**: Toggle between "user" and "admin" roles (RBAC foundation)
- **Account Approval**: Approve/revoke user access (supports moderation workflows)
- **Password Reset**: Administrative password reset for locked-out users
- **Avatar Management**: Profile picture file selection with 96x96 preview
- **Real-Time Updates**: User list refreshes immediately after modifications
- **Safety Guards**: Prevents deletion of currently logged-in user
- **UserManager Integration**: Delegates all persistence and password hashing to core layer

### UX Goals

1. **Administrative Efficiency**: All user operations in single panel
2. **Visual Confirmation**: Avatar preview and status labels for immediate feedback
3. **Safety First**: Confirmation dialogs for destructive operations
4. **Role Clarity**: Explicit role selector with only two options (user/admin)
5. **Self-Service Prevention**: Admins cannot delete their own accounts
6. **Audit Trail**: All operations logged via UserManager (password changes, deletions)

### Design Philosophy

The UserManagementWidget follows **separation of concerns**—it owns UI logic and delegates all business logic (password hashing, JSON I/O, validation) to `UserManager`. This ensures the widget remains testable with mock `UserManager` instances and keeps security-critical code centralized in the core layer.

---

## UI Layout Architecture

### Visual Structure

```
┌────────────────────────────────────────────────────────────┐
│  Users:                                                     │ ← QLabel
│  ┌────────────────────────┐                                │
│  │  admin_user           │  ← QListWidget (sorted)         │
│  │  alice                │                                  │
│  │  bob                  │                                  │
│  │  charlie              │  ← Selection triggers details   │
│  └────────────────────────┘                                │
│                                                             │
│  [Create User] [Delete User] [Approve/Revoke] [Reset PW]   │ ← Action buttons
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Select a user to see details and edit settings.           │ ← Instruction label
├──────────────────────────┬──────────────────────────────────┤
│  LEFT PANEL              │  RIGHT PANEL                     │
│                          │                                  │
│  Username:               │  Approved: True                  │ ← Status label
│  ┌────────────────────┐  │                                  │
│  │ alice             │  │  [Save Changes]                  │ ← Save button
│  └────────────────────┘  │                                  │
│                          │                                  │
│  Role:                   │                                  │
│  ┌────────────────────┐  │                                  │
│  │ admin          ▼  │  │  ← Role dropdown                 │
│  └────────────────────┘  │                                  │
│                          │                                  │
│  Profile picture (path): │                                  │
│  ┌─────────────────┬──┐  │                                  │
│  │/home/user/av.png│[]│  │  ← Path + Browse button         │
│  └─────────────────┴──┘  │                                  │
│                          │                                  │
│  Avatar preview:         │                                  │
│  ┌────────────────────┐  │                                  │
│  │                    │  │  ← 96x96 QLabel pixmap          │
│  │   [AVATAR IMAGE]   │  │                                  │
│  │                    │  │                                  │
│  └────────────────────┘  │                                  │
└──────────────────────────┴──────────────────────────────────┘
```

### Widget Hierarchy

```
UserManagementWidget (QWidget)
└── QVBoxLayout (main_layout)
    ├── QLabel("Users:")
    ├── QListWidget (user_list)
    │   └── currentTextChanged → on_user_selected()
    ├── QHBoxLayout (btn_row)
    │   ├── QPushButton("Create User") → create_user_dialog()
    │   ├── QPushButton("Delete User") → delete_user()
    │   ├── QPushButton("Approve / Revoke") → toggle_approve()
    │   └── QPushButton("Reset Password") → reset_password()
    ├── QLabel (details_label) - instruction text
    └── QHBoxLayout (form_row)
        ├── QVBoxLayout (left panel)
        │   ├── QLabel("Username:")
        │   ├── QLineEdit (username_field)
        │   ├── QLabel("Role:")
        │   ├── QComboBox (role_combo: "user", "admin")
        │   ├── QLabel("Profile picture (path):")
        │   ├── QHBoxLayout (pic_row)
        │   │   ├── QLineEdit (pic_field)
        │   │   └── QPushButton("Browse") → browse_picture()
        │   ├── QLabel("Avatar preview:")
        │   └── QLabel (avatar_preview) - 96x96 pixmap
        └── QVBoxLayout (right panel)
            ├── QLabel (approved_label) - "Approved: True/False"
            └── QPushButton("Save Changes") → save_changes()
```

### Supporting Dialogs

#### CreateUserDialog

```
┌───────────────────────────────────┐
│  Create User                      │ ← Modal dialog
├───────────────────────────────────┤
│  Username:                        │
│  ┌─────────────────────────────┐ │
│  │                             │ │
│  └─────────────────────────────┘ │
│                                   │
│  Password:                        │
│  ┌─────────────────────────────┐ │
│  │ ••••••••••                  │ │ ← EchoMode.Password
│  └─────────────────────────────┘ │
│                                   │
│  ☑ Approved                       │ ← QCheckBox (default: checked)
│                                   │
│  Role:                            │
│  ┌─────────────────────────────┐ │
│  │ user                    ▼   │ │
│  └─────────────────────────────┘ │
│                                   │
│  Profile picture:                 │
│  ┌──────────────────────┬──────┐ │
│  │                      │Browse│ │
│  └──────────────────────┴──────┘ │
│                                   │
│          [  OK  ] [Cancel]        │
└───────────────────────────────────┘
```

#### ResetPasswordDialog

```
┌───────────────────────────────────┐
│  Reset Password: alice            │ ← Username in title
├───────────────────────────────────┤
│  New password:                    │
│  ┌─────────────────────────────┐ │
│  │ ••••••••••                  │ │ ← EchoMode.Password
│  └─────────────────────────────┘ │
│                                   │
│          [  OK  ] [Cancel]        │
└───────────────────────────────────┘
```

---

## Core Architecture

### Class Design

#### UserManagementWidget

**Inheritance:** `QWidget` → `UserManagementWidget`

**Responsibilities:**
1. Render user list and detail panel
2. Dispatch CRUD operations to `UserManager`
3. Show confirmation/error dialogs
4. Update UI state after operations
5. Enforce business rules (no self-deletion)

**Dependencies:**
- `app.core.user_manager.UserManager` - Core user persistence and authentication
- `PyQt6.QtWidgets` - UI components
- `PyQt6.QtGui.QPixmap` - Avatar image rendering

**Instance Variables:**
- `um: UserManager` - Core user manager instance
- `user_list: QListWidget` - User list display
- `username_field: QLineEdit` - Username editor
- `role_combo: QComboBox` - Role selector
- `pic_field: QLineEdit` - Avatar path editor
- `avatar_preview: QLabel` - 96x96 avatar display
- `approved_label: QLabel` - Approval status display
- `create_btn, delete_btn, approve_btn, reset_pw_btn, save_btn: QPushButton` - Action buttons

---

#### CreateUserDialog

**Inheritance:** `QDialog` → `CreateUserDialog`

**Responsibilities:**
1. Collect new user details (username, password, role, approval, avatar)
2. Validate input before returning
3. Provide file browser for avatar selection

**Instance Variables:**
- `username: QLineEdit` - New username input
- `password: QLineEdit` - Password input (masked)
- `approved_cb: QCheckBox` - Approval checkbox (default: checked)
- `role: QComboBox` - Role selector
- `pic_field_d: QLineEdit` - Avatar path input

**Returns:** Tuple `(username: str, password: str, approved: bool, role: str, picture_path: str)`

---

#### ResetPasswordDialog

**Inheritance:** `QDialog` → `ResetPasswordDialog`

**Responsibilities:**
1. Collect new password for existing user
2. Display target username in window title
3. Return password securely to caller

**Instance Variables:**
- `pw: QLineEdit` - New password input (masked)

**Returns:** `str` - New password plaintext (hashed by UserManager)

---

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    User Management Widget                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      UserManager (Core)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  users: dict = {                                       │ │
│  │    "alice": {                                          │ │
│  │      "password_hash": "$2b$12$...",                    │ │
│  │      "role": "admin",                                  │ │
│  │      "approved": true,                                 │ │
│  │      "profile_picture": "/home/alice/avatar.png"       │ │
│  │    }                                                   │ │
│  │  }                                                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│                  save_users() → JSON                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    data/users.json                           │
│  {                                                           │
│    "alice": {                                                │
│      "password_hash": "$2b$12$abc...",                       │
│      "role": "admin",                                        │
│      "approved": true,                                       │
│      "profile_picture": "/home/alice/avatar.png"             │
│    }                                                         │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

---

### State Management

**Instance State:**
- `self.um`: Singleton UserManager instance (shared across widgets)
- `self.user_list`: Current user list (refreshed after operations)
- Selected user fields: Cached in `username_field`, `role_combo`, `pic_field`, `approved_label`

**Persistence:**
- All user data persisted via `UserManager.save_users()`
- No local caching—always reads from `UserManager.users` dict
- Avatar preview rendered on-demand from file path

**Concurrency:**
- **Not thread-safe**: Must be used from GUI thread only
- UserManager performs blocking I/O (JSON load/save)
- Future: Consider async I/O for large user databases

---

## API Reference

### UserManagementWidget

#### Constructor

##### `__init__(parent=None)`

Initializes the user management widget with UserManager integration.

**Parameters:**
- `parent` (QWidget, optional): Parent widget for layout. Default: `None`

**Behavior:**
1. Instantiates `UserManager()` and stores in `self.um`
2. Calls `_build_ui()` to construct widget hierarchy
3. Calls `refresh_user_list()` to populate initial user list

**Example:**
```python
from PyQt6.QtWidgets import QMainWindow
from app.gui.user_management import UserManagementWidget

class AdminPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user_widget = UserManagementWidget(parent=self)
        self.setCentralWidget(self.user_widget)
```

---

#### Instance Methods

##### `refresh_user_list()`

Reloads user list from UserManager and updates QListWidget.

**Returns:** None

**Behavior:**
1. Clears `self.user_list` widget
2. Sorts `self.um.users.keys()` alphabetically
3. Adds each username to list widget
4. Clears avatar preview (no user selected)

**Called After:**
- Widget initialization
- User creation
- User deletion
- User update
- Any operation that modifies user set

**Example:**
```python
# After creating a user
self.um.create_user("new_user", "password123")
self.refresh_user_list()  # Updates list to include "new_user"
```

---

##### `on_user_selected(username: str)`

Event handler triggered when user selects a username from the list.

**Parameters:**
- `username` (str): Selected username from QListWidget

**Returns:** None

**Behavior:**
1. If `username` is empty, returns early (deselection case)
2. Fetches user data via `self.um.get_user_data(username)`
3. Populates form fields:
   - `username_field` ← username
   - `role_combo` ← role (default: "user")
   - `pic_field` ← profile_picture path (default: "")
   - `approved_label` ← "Approved: True/False"

**Signal Connection:**
```python
self.user_list.currentTextChanged.connect(self.on_user_selected)
```

**Example:**
```python
# User clicks "alice" in list
# → on_user_selected("alice") called
# → Form fields populated with alice's data
```

---

##### `browse_picture()`

Opens file dialog for avatar image selection and updates preview.

**Returns:** None

**Behavior:**
1. Opens `QFileDialog.getOpenFileName()` with filters: `*.png`, `*.jpg`, `*.jpeg`, `*.bmp`
2. If file selected:
   - Sets `pic_field.text()` to file path
   - Loads file as `QPixmap`
   - Scales to 96x96 pixels
   - Displays in `avatar_preview` QLabel

**Signal Connection:**
```python
self.pic_btn.clicked.connect(self.browse_picture)
```

**Example:**
```python
# User clicks "Browse" button
# → File dialog opens
# → User selects "/home/alice/avatar.png"
# → pic_field updated, preview shows scaled image
```

**Error Handling:**
- If `QPixmap.isNull()` (invalid image), preview stays empty
- No error message shown (silent failure for invalid formats)

---

##### `create_user_dialog()`

Opens modal dialog to create a new user account.

**Returns:** None

**Behavior:**
1. Instantiates `CreateUserDialog(parent=self)`
2. Shows modal dialog via `exec()`
3. If accepted:
   - Extracts values via `dialog.get_values()` → `(username, password, approved, role, picture)`
   - Calls `self.um.create_user(username, password)`
   - If success:
     - Calls `self.um.update_user(username, approved=..., role=..., profile_picture=...)`
     - Shows success message: `"User '{username}' created."`
     - Calls `refresh_user_list()`
   - If failure (user exists):
     - Shows warning: `"User already exists"`

**Signal Connection:**
```python
self.create_btn.clicked.connect(self.create_user_dialog)
```

**Example:**
```python
# Admin clicks "Create User"
# → Dialog opens
# → Admin enters: username="bob", password="secure123", role="user", approved=True
# → Clicks OK
# → UserManager creates user with bcrypt-hashed password
# → User list refreshes, "bob" appears
```

**Security:**
- Password never stored in plaintext (hashed by UserManager)
- Password field uses `QLineEdit.EchoMode.Password` for masking

---

##### `delete_user()`

Deletes selected user after confirmation.

**Returns:** None

**Behavior:**
1. Gets selected username from `user_list.currentItem()`
2. If no selection, shows warning: `"Select a user to delete"`
3. If username matches `self.um.current_user`, shows warning: `"Cannot delete currently logged-in user"`
4. Shows confirmation dialog: `"Delete user '{username}'? This is irreversible."`
5. If confirmed:
   - Calls `self.um.delete_user(username)`
   - If success: Shows `"User deleted"`, calls `refresh_user_list()`
   - If failure: Shows `"Failed to delete user"`

**Signal Connection:**
```python
self.delete_btn.clicked.connect(self.delete_user)
```

**Example:**
```python
# Admin selects "bob", clicks "Delete User"
# → Confirmation dialog appears
# → Admin clicks "Yes"
# → Bob's account deleted from users.json
# → User list refreshes, "bob" removed
```

**Safety:**
- **Self-deletion prevention**: Logged-in user cannot delete own account
- **Irreversibility warning**: Explicit confirmation required
- **Atomic operation**: UserManager handles JSON persistence

---

##### `toggle_approve()`

Toggles approval status for selected user.

**Returns:** None

**Behavior:**
1. Gets selected username from `user_list.currentItem()`
2. If no selection, shows warning: `"Select a user first"`
3. Reads current approval status from `self.um.users[username]["approved"]`
4. Toggles status: `new = not current`
5. Calls `self.um.update_user(username, approved=new)`
6. Calls `on_user_selected(username)` to refresh form display
7. Shows success message: `"User '{username}' approved set to {new}"`

**Signal Connection:**
```python
self.approve_btn.clicked.connect(self.toggle_approve)
```

**Example:**
```python
# Admin selects "charlie" (approved=False)
# → Clicks "Approve / Revoke"
# → Approval toggled to True
# → Label updates: "Approved: True"
# → Success message shown
```

**Use Case:**
- Moderation workflow: New users start unapproved, admin reviews and approves
- Temporary access revocation: Toggle to False to block user without deletion

---

##### `reset_password()`

Opens modal dialog to reset selected user's password.

**Returns:** None

**Behavior:**
1. Gets selected username from `user_list.currentItem()`
2. If no selection, shows warning: `"Select a user first"`
3. Instantiates `ResetPasswordDialog(username, parent=self)`
4. Shows modal dialog via `exec()`
5. If accepted:
   - Extracts new password via `dialog.get_password()`
   - Calls `self.um.set_password(username, newpw)`
   - Shows success message: `"Password updated"`

**Signal Connection:**
```python
self.reset_pw_btn.clicked.connect(self.reset_password)
```

**Example:**
```python
# User "alice" locked out (forgot password)
# → Admin selects "alice", clicks "Reset Password"
# → Dialog opens with title "Reset Password: alice"
# → Admin enters new password: "newpass123"
# → Clicks OK
# → UserManager hashes password with bcrypt, saves to users.json
# → Alice can now login with "newpass123"
```

**Security:**
- No old password verification (administrative override)
- New password hashed with bcrypt (WorkFactor 12 rounds)
- Audit trail via UserManager logging (if implemented)

---

##### `save_changes()`

Saves modified user details from form fields.

**Returns:** None

**Behavior:**
1. Reads form fields:
   - `username` ← `username_field.text().strip()`
   - `role` ← `role_combo.currentText()`
   - `picture` ← `pic_field.text().strip()`
   - `approved` ← Parsed from `approved_label.text()` (ends with "True")
2. Validates:
   - If username empty, shows warning: `"Username cannot be empty"`
   - If no user selected, shows warning: `"Select a user first"`
3. Calls `self.um.update_user(current_item.text(), role=..., profile_picture=..., approved=...)`
4. If success:
   - Shows `"User updated"`
   - Calls `refresh_user_list()`
5. If failure:
   - Shows `"Failed to save user"`

**Signal Connection:**
```python
self.save_btn.clicked.connect(self.save_changes)
```

**Example:**
```python
# Admin selects "alice", changes role from "user" to "admin"
# → Clicks "Save Changes"
# → UserManager updates role in users.json
# → Success message shown
```

**Note:** Username field is displayed but **not editable** (no username rename support).

---

### CreateUserDialog

#### Constructor

##### `__init__(parent=None)`

Creates modal dialog for new user account creation.

**Parameters:**
- `parent` (QWidget, optional): Parent widget. Default: `None`

**Behavior:**
- Sets window title: `"Create User"`
- Sets modal: `setModal(True)`
- Creates form fields: username, password, approved checkbox, role, picture path
- Connects OK/Cancel buttons

---

#### Instance Methods

##### `get_values() -> tuple`

Retrieves entered user details.

**Returns:**
- `tuple`: `(username: str, password: str, approved: bool, role: str, picture_path: str)`

**Example:**
```python
dialog = CreateUserDialog(parent=self)
if dialog.exec() == QDialog.DialogCode.Accepted:
    uname, pw, approved, role, pic = dialog.get_values()
    # uname="bob", pw="password123", approved=True, role="admin", pic="/home/bob/avatar.png"
```

---

##### `_browse()`

Internal method to open file dialog for avatar selection.

**Behavior:**
- Opens file dialog with image filters
- Sets `pic_field_d.text()` to selected path

---

### ResetPasswordDialog

#### Constructor

##### `__init__(username, parent=None)`

Creates modal dialog for password reset.

**Parameters:**
- `username` (str): Target username (displayed in title)
- `parent` (QWidget, optional): Parent widget. Default: `None`

**Behavior:**
- Sets window title: `f"Reset Password: {username}"`
- Creates single password field with masking
- Connects OK/Cancel buttons

---

#### Instance Methods

##### `get_password() -> str`

Retrieves entered new password.

**Returns:**
- `str`: New password plaintext

**Example:**
```python
dialog = ResetPasswordDialog("alice", parent=self)
if dialog.exec() == QDialog.DialogCode.Accepted:
    new_pw = dialog.get_password()
    user_manager.set_password("alice", new_pw)
```

---

## Security Features

### Password Security

**bcrypt Hashing:**
- All passwords hashed via `UserManager._hash_and_store_password()`
- Uses bcrypt WorkFactor 12 (2^12 = 4096 rounds)
- Automatic salt generation per password
- Password never stored in plaintext

**Password Reset:**
- Administrative override (no old password required)
- New password immediately hashed before storage
- No password recovery—only reset

**Password Visibility:**
- All password fields use `QLineEdit.EchoMode.Password` (masked as `••••`)
- Password never logged or displayed in UI

---

### Role-Based Access Control (RBAC)

**Roles:**
- `"user"`: Default role, standard permissions
- `"admin"`: Elevated permissions (can access UserManagementWidget)

**Role Assignment:**
- Set during user creation
- Modifiable via `role_combo` dropdown
- Persisted in `users.json`

**Access Control:**
- UserManagementWidget should only be accessible to admins
- Recommended: Check `um.get_user_data(current_user)["role"] == "admin"` before showing widget

---

### Account Approval Workflow

**Approval Status:**
- `approved=True`: User can login
- `approved=False`: Login blocked (via LoginDialog check)

**Use Cases:**
1. **Moderation**: New signups start unapproved, admin reviews
2. **Temporary Suspension**: Revoke approval to block access without deletion
3. **Batch Onboarding**: Create accounts in bulk, approve after verification

**Toggle Logic:**
- Admin clicks "Approve / Revoke" button
- Status flips: `True → False` or `False → True`
- Immediate persistence via UserManager

---

### Self-Deletion Prevention

**Protection:**
```python
if username == self.um.current_user:
    QMessageBox.warning(self, "Delete", "Cannot delete currently logged-in user")
    return
```

**Rationale:**
- Prevents admin from locking themselves out
- Ensures at least one admin account survives
- Requires logout before self-deletion

---

### Audit Trail (Recommended Enhancement)

**Current State:** No audit logging

**Recommended Addition:**
```python
import logging
logger = logging.getLogger(__name__)

def delete_user(self):
    # ... existing code
    logger.info(f"Admin {self.um.current_user} deleted user {username}")

def toggle_approve(self):
    # ... existing code
    logger.info(f"Admin {self.um.current_user} set approval for {username} to {new}")

def reset_password(self):
    # ... existing code
    logger.info(f"Admin {self.um.current_user} reset password for {username}")
```

**Benefits:**
- Track administrative actions
- Compliance with security policies
- Forensic investigation support

---

## Integration Patterns

### Pattern 1: Admin-Only Access Control

```python
# leather_book_dashboard.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QMessageBox
from app.gui.user_management import UserManagementWidget
from app.core.user_manager import UserManager

class DashboardWidget(QWidget):
    def __init__(self, current_user: str):
        super().__init__()
        self.um = UserManager()
        self.current_user = current_user
        
        # Check admin role
        user_data = self.um.get_user_data(current_user)
        if user_data.get("role") == "admin":
            self._build_admin_dashboard()
        else:
            self._build_user_dashboard()
    
    def _build_admin_dashboard(self):
        tabs = QTabWidget()
        tabs.addTab(QWidget(), "Dashboard")
        tabs.addTab(QWidget(), "AI Persona")
        tabs.addTab(UserManagementWidget(), "User Management")  # Admin-only tab
        
        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
    
    def _build_user_dashboard(self):
        # Standard dashboard without user management
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Welcome! No admin access."))
```

---

### Pattern 2: Menu Action Integration

```python
# main_window.py
from PyQt6.QtWidgets import QMainWindow, QDialog
from app.gui.user_management import UserManagementWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._setup_menus()
    
    def _setup_menus(self):
        admin_menu = self.menuBar().addMenu("Admin")
        
        user_mgmt_action = admin_menu.addAction("Manage Users...")
        user_mgmt_action.triggered.connect(self.open_user_management)
    
    def open_user_management(self):
        # Option 1: Modal dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("User Management")
        layout = QVBoxLayout(dialog)
        layout.addWidget(UserManagementWidget(parent=dialog))
        dialog.setLayout(layout)
        dialog.resize(800, 600)
        dialog.exec()
        
        # Option 2: Dock widget
        # dock = QDockWidget("User Management", self)
        # dock.setWidget(UserManagementWidget())
        # self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
```

---

### Pattern 3: First-Run Admin Setup

```python
# main.py
from PyQt6.QtWidgets import QApplication, QMessageBox
from app.core.user_manager import UserManager
from app.gui.user_management import CreateUserDialog

def ensure_admin_exists():
    """Create admin account on first run"""
    um = UserManager()
    if len(um.users) == 0:
        QMessageBox.information(
            None,
            "First Run",
            "No users found. Please create an admin account."
        )
        
        dialog = CreateUserDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            uname, pw, approved, role, pic = dialog.get_values()
            
            # Force admin role and approval for first user
            um.create_user(uname, pw)
            um.update_user(uname, approved=True, role="admin", profile_picture=pic)
            
            QMessageBox.information(
                None,
                "Admin Created",
                f"Admin account '{uname}' created. You can now login."
            )
        else:
            QMessageBox.critical(
                None,
                "Setup Failed",
                "Cannot start without admin account. Exiting."
            )
            sys.exit(1)

# Application entry point
app = QApplication(sys.argv)
ensure_admin_exists()
# ... launch login dialog
```

---

### Pattern 4: User Search and Filter

```python
# Enhanced UserManagementWidget
from PyQt6.QtWidgets import QLineEdit

class UserManagementWidget(QWidget):
    def _build_ui(self):
        # ... existing code
        
        # Add search bar
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search users...")
        self.search_field.textChanged.connect(self.filter_users)
        self.main_layout.insertWidget(1, self.search_field)  # After "Users:" label
    
    def filter_users(self, query: str):
        """Filter user list by search query"""
        query_lower = query.lower()
        for i in range(self.user_list.count()):
            item = self.user_list.item(i)
            username = item.text()
            
            # Show item if matches search
            if query_lower in username.lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
```

---

## Usage Examples

### Example 1: Basic Widget Integration

```python
from PyQt6.QtWidgets import QApplication, QMainWindow
from app.gui.user_management import UserManagementWidget

app = QApplication([])
window = QMainWindow()
window.setWindowTitle("Admin Panel")
window.setCentralWidget(UserManagementWidget())
window.resize(800, 600)
window.show()
app.exec()
```

---

### Example 2: Creating User Programmatically

```python
from app.gui.user_management import UserManagementWidget
from app.core.user_manager import UserManager

# Setup
widget = UserManagementWidget()
um = widget.um

# Create user
success = um.create_user("alice", "secure_password_123")
if success:
    um.update_user(
        "alice",
        approved=True,
        role="admin",
        profile_picture="/home/alice/avatar.png"
    )
    widget.refresh_user_list()  # Update UI
    print("User created and list refreshed")
```

---

### Example 3: Batch User Import

```python
import csv
from app.gui.user_management import UserManagementWidget

widget = UserManagementWidget()
um = widget.um

# Import from CSV: username,password,role,approved
with open("users.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        username = row["username"]
        password = row["password"]
        role = row["role"]
        approved = row["approved"].lower() == "true"
        
        if um.create_user(username, password):
            um.update_user(username, approved=approved, role=role)
            print(f"Imported: {username}")
        else:
            print(f"Skipped (exists): {username}")

widget.refresh_user_list()  # Refresh UI once at end
```

**CSV Example:**
```csv
username,password,role,approved
alice,pass123,admin,true
bob,pass456,user,true
charlie,pass789,user,false
```

---

### Example 4: Role-Based Dashboard Routing

```python
from PyQt6.QtWidgets import QStackedWidget
from app.gui.user_management import UserManagementWidget
from app.core.user_manager import UserManager

class DynamicDashboard(QStackedWidget):
    def __init__(self, current_user: str):
        super().__init__()
        self.um = UserManager()
        self.current_user = current_user
        
        # Page 0: User dashboard
        self.addWidget(QLabel("User Dashboard"))
        
        # Page 1: Admin dashboard with user management
        admin_page = QWidget()
        layout = QVBoxLayout(admin_page)
        layout.addWidget(QLabel("Admin Dashboard"))
        layout.addWidget(UserManagementWidget())
        self.addWidget(admin_page)
        
        # Route based on role
        user_data = self.um.get_user_data(current_user)
        if user_data.get("role") == "admin":
            self.setCurrentIndex(1)  # Show admin page
        else:
            self.setCurrentIndex(0)  # Show user page
```

---

### Example 5: Avatar Preview Enhancement

```python
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class UserManagementWidget(QWidget):
    # ... existing code
    
    def on_user_selected(self, username: str):
        if not username:
            return
        data = self.um.get_user_data(username)
        
        # ... existing field population
        
        # Enhanced avatar preview with fallback
        pic_path = data.get("profile_picture", "")
        self.pic_field.setText(pic_path)
        
        if pic_path and os.path.exists(pic_path):
            pix = QPixmap(pic_path)
            if not pix.isNull():
                # Scale with aspect ratio preservation
                scaled = pix.scaled(
                    96, 96,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.avatar_preview.setPixmap(scaled)
            else:
                self.show_default_avatar()
        else:
            self.show_default_avatar()
    
    def show_default_avatar(self):
        """Display default avatar for users without picture"""
        default = QPixmap(96, 96)
        default.fill(Qt.GlobalColor.lightGray)
        self.avatar_preview.setPixmap(default)
```

---

## Styling Guide

### Current Styling

The UserManagementWidget uses **default PyQt6 styling** with minimal custom CSS:

```python
self.avatar_preview.setStyleSheet("border:1px solid #ccc; background: #fff;")
```

**Effect:** Adds subtle border to avatar preview area

---

### Tron Theme Recommendations

Align with Leather Book Interface Tron aesthetic:

```python
TRON_USER_MGMT_STYLE = """
QWidget {
    background-color: #0a0e1a;
    color: #00ff00;
    font-family: 'Courier New', monospace;
}

QLabel {
    color: #00ffff;
    font-size: 11pt;
}

QListWidget {
    background-color: #1a1f2e;
    color: #00ff00;
    border: 2px solid #00ffff;
    border-radius: 4px;
    font-size: 11pt;
}

QListWidget::item:selected {
    background-color: #00ffff;
    color: #0a0e1a;
}

QLineEdit, QComboBox {
    background-color: #1a1f2e;
    color: #00ff00;
    border: 2px solid #00ffff;
    border-radius: 4px;
    padding: 6px;
    font-size: 11pt;
}

QPushButton {
    background-color: #00ffff;
    color: #0a0e1a;
    border: none;
    border-radius: 4px;
    padding: 8px 12px;
    font-weight: bold;
    font-size: 10pt;
}

QPushButton:hover {
    background-color: #00ff00;
}

QPushButton:pressed {
    background-color: #008888;
}

QLabel#avatar_preview {
    border: 2px solid #00ffff;
    background: #1a1f2e;
}

QLabel#approved_label {
    color: #00ff00;
    font-size: 12pt;
    font-weight: bold;
}
"""

# Apply in __init__
class UserManagementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(TRON_USER_MGMT_STYLE)
        # ... rest of initialization
```

---

### Dark Theme Recommendations

Modern dark theme (non-Tron):

```python
DARK_USER_MGMT_STYLE = """
QWidget {
    background-color: #2b2b2b;
    color: #e0e0e0;
}

QLabel {
    color: #ffffff;
    font-size: 11pt;
}

QListWidget {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 3px;
}

QListWidget::item:selected {
    background-color: #0078d4;
}

QLineEdit, QComboBox {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #555555;
    padding: 5px;
}

QPushButton {
    background-color: #0078d4;
    color: #ffffff;
    border: none;
    border-radius: 3px;
    padding: 6px 12px;
}

QPushButton:hover {
    background-color: #005a9e;
}
"""
```

---

## Accessibility Considerations

### Keyboard Navigation

**Current Support:**
- Tab key cycles through all controls
- Enter activates focused button
- Arrow keys navigate list items
- Space bar activates checkboxes/buttons

**Enhancement:**
```python
# Add keyboard shortcuts
from PyQt6.QtGui import QShortcut, QKeySequence

class UserManagementWidget(QWidget):
    def _build_ui(self):
        # ... existing code
        
        # Shortcuts
        QShortcut(QKeySequence("Ctrl+N"), self, self.create_user_dialog)
        QShortcut(QKeySequence("Delete"), self, self.delete_user)
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_changes)
        QShortcut(QKeySequence("F5"), self, self.refresh_user_list)
```

---

### Screen Reader Support

**Current Labels:**
- QLabel widgets provide context for form fields
- Buttons have descriptive text

**Enhancement:**
```python
self.user_list.setAccessibleName("User list")
self.user_list.setAccessibleDescription("List of all registered users")

self.create_btn.setAccessibleName("Create user button")
self.delete_btn.setAccessibleName("Delete user button")

self.username_field.setAccessibleName("Username field")
self.role_combo.setAccessibleName("Role selector")
```

---

### Visual Indicators

**Current:**
- Approved status as text label
- Selected user highlighted in list

**Enhancement:**
```python
def on_user_selected(self, username: str):
    # ... existing code
    
    # Color-code approval status
    if data.get("approved"):
        self.approved_label.setStyleSheet("color: #00ff00; font-weight: bold;")
    else:
        self.approved_label.setStyleSheet("color: #ff0000; font-weight: bold;")
    
    # Role badge
    role = data.get("role", "user")
    if role == "admin":
        self.username_field.setStyleSheet("border: 2px solid gold;")
    else:
        self.username_field.setStyleSheet("")
```

---

## Security Considerations

### Password Storage

**Critical:** Passwords NEVER stored in plaintext

**Implementation:**
```python
# UserManager (core layer)
import bcrypt

def create_user(self, username: str, password: str) -> bool:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
    self.users[username] = {
        "password_hash": hashed.decode(),  # Store as string
        "approved": False,
        "role": "user"
    }
```

**Audit:** Verify no password logging:
```bash
# Search for accidental password logging
grep -r "password" src/app/gui/user_management.py
# Ensure only hashed values or field references
```

---

### Input Validation

**Current Gaps:**
- No username length/character validation
- No password strength requirements

**Recommended:**
```python
def create_user_dialog(self):
    dialog = CreateUserDialog(parent=self)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        uname, pw, approved, role, pic = dialog.get_values()
        
        # Validation
        if len(uname) < 3:
            QMessageBox.warning(self, "Error", "Username must be at least 3 characters")
            return
        if not re.match(r"^[a-zA-Z0-9_]+$", uname):
            QMessageBox.warning(self, "Error", "Username can only contain letters, numbers, underscore")
            return
        if len(pw) < 8:
            QMessageBox.warning(self, "Error", "Password must be at least 8 characters")
            return
        
        # Proceed with creation
        # ...
```

---

### Avatar Path Security

**Risk:** Path traversal via malicious avatar paths

**Current:** No validation on `profile_picture` field

**Mitigation:**
```python
import os

def save_changes(self):
    # ... existing code
    pic = self.pic_field.text().strip()
    
    # Validate path
    if pic:
        pic = os.path.normpath(os.path.abspath(pic))
        
        # Ensure path exists and is readable
        if not os.path.isfile(pic):
            QMessageBox.warning(self, "Invalid Path", "Profile picture file not found")
            return
        
        # Optionally restrict to specific directory
        AVATAR_DIR = os.path.abspath("data/avatars/")
        if not pic.startswith(AVATAR_DIR):
            QMessageBox.warning(self, "Invalid Path", "Avatar must be in data/avatars/ directory")
            return
    
    # Proceed with update
```

---

### Role Escalation Prevention

**Risk:** User modifies `users.json` directly to grant admin role

**Mitigation:**
1. **File permissions:** `chmod 600 data/users.json` (owner read/write only)
2. **Checksums:** Validate JSON integrity on load
3. **Audit logging:** Log all role changes

```python
import hashlib
import json

def save_users(self):
    # Save users
    with open(self.users_file, "w") as f:
        json.dump(self.users, f, indent=2)
    
    # Generate checksum
    with open(self.users_file, "rb") as f:
        checksum = hashlib.sha256(f.read()).hexdigest()
    
    with open(self.users_file + ".sha256", "w") as f:
        f.write(checksum)

def load_users(self):
    # Verify checksum
    with open(self.users_file, "rb") as f:
        checksum = hashlib.sha256(f.read()).hexdigest()
    
    with open(self.users_file + ".sha256") as f:
        expected = f.read().strip()
    
    if checksum != expected:
        raise SecurityError("users.json integrity check failed!")
    
    # Load users
    # ...
```

---

## Troubleshooting

### Issue 1: User List Not Refreshing

**Symptom:** Created/deleted users don't appear/disappear from list

**Cause:** `refresh_user_list()` not called after operation

**Solution:**
```python
# Ensure all CRUD operations call refresh
def create_user_dialog(self):
    # ... user creation logic
    if success:
        self.refresh_user_list()  # ← Must be here

def delete_user(self):
    # ... deletion logic
    if ok:
        self.refresh_user_list()  # ← Must be here
```

---

### Issue 2: Avatar Not Displaying

**Symptom:** Avatar preview shows blank square

**Causes:**
1. Invalid file path
2. Unsupported image format
3. File permissions

**Diagnosis:**
```python
def browse_picture(self):
    fname, _ = QFileDialog.getOpenFileName(...)
    if fname:
        print(f"Selected file: {fname}")
        print(f"File exists: {os.path.exists(fname)}")
        
        pix = QPixmap(fname)
        print(f"QPixmap valid: {not pix.isNull()}")
        print(f"Size: {pix.width()}x{pix.height()}")
        
        if pix.isNull():
            QMessageBox.warning(self, "Invalid Image", f"Cannot load {fname}")
```

**Solution:**
- Verify file format: `.png`, `.jpg`, `.jpeg`, `.bmp` only
- Check file permissions: `chmod 644 avatar.png`
- Use absolute paths: `os.path.abspath(fname)`

---

### Issue 3: Cannot Delete User

**Symptom:** Delete button does nothing

**Causes:**
1. No user selected
2. Attempting to delete logged-in user
3. UserManager returns False

**Diagnosis:**
```python
def delete_user(self):
    item = self.user_list.currentItem()
    username = item.text() if item else None
    
    print(f"Selected username: {username}")
    print(f"Current user: {self.um.current_user}")
    
    if username == self.um.current_user:
        print("Cannot delete self")
        return
    
    ok = self.um.delete_user(username)
    print(f"Delete result: {ok}")
```

**Solutions:**
- Select different user (not current user)
- Check `UserManager.delete_user()` implementation for bugs
- Verify `users.json` write permissions

---

### Issue 4: Password Reset Not Working

**Symptom:** New password doesn't work after reset

**Cause:** Password not hashed correctly

**Diagnosis:**
```python
# In UserManager
def set_password(self, username: str, new_password: str):
    print(f"Setting password for {username}")
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt(rounds=12))
    print(f"Hashed: {hashed}")
    
    self.users[username]["password_hash"] = hashed.decode()
    self.save_users()
    print(f"Saved to users.json")
```

**Solution:**
- Ensure `UserManager.set_password()` calls `save_users()`
- Verify bcrypt installed: `pip install bcrypt`
- Check `users.json` for updated hash

---

### Issue 5: Approval Toggle Not Persisting

**Symptom:** Approval status reverts after restart

**Cause:** `UserManager.update_user()` not saving to disk

**Solution:**
```python
# In UserManager.update_user()
def update_user(self, username: str, **kwargs) -> bool:
    if username not in self.users:
        return False
    
    for key, value in kwargs.items():
        self.users[username][key] = value
    
    self.save_users()  # ← CRITICAL: Must persist to JSON
    return True
```

---

### Issue 6: Role Changes Not Applied

**Symptom:** User role shows "user" even after changing to "admin"

**Cause:** Role not saved, or application caching old value

**Diagnosis:**
```python
# After save_changes()
print(f"Role in memory: {self.um.users[username]['role']}")

# Check JSON file
with open("data/users.json") as f:
    data = json.load(f)
    print(f"Role in JSON: {data[username]['role']}")
```

**Solution:**
- Ensure `save_changes()` calls `UserManager.update_user()`
- Verify `UserManager.save_users()` called
- Clear any caching layers
- Restart application to reload from JSON

---

### Best Practices Checklist

✅ **Always call `refresh_user_list()` after CRUD operations**  
✅ **Check `UserManager` return values for error handling**  
✅ **Use absolute paths for avatar images**  
✅ **Validate image files before displaying (check `QPixmap.isNull()`)**  
✅ **Show confirmation dialogs for destructive operations**  
✅ **Prevent self-deletion with explicit checks**  
✅ **Use `QLineEdit.EchoMode.Password` for all password fields**  
✅ **Log all administrative actions for audit trail**  
✅ **Restrict UserManagementWidget access to admin role**  
✅ **Test with missing `users.json` to verify first-run behavior**  
✅ **Verify password hashing with bcrypt WorkFactor 12**  
✅ **Document role permissions and approval workflow**

---

## Conclusion

The **UserManagementWidget** provides a production-ready administrative interface for complete user lifecycle management. Its integration with the bcrypt-secured `UserManager` core module ensures password security, while its comprehensive CRUD operations, role-based access control, and account approval workflows make it suitable for multi-user applications with moderation requirements. Future enhancements could include user search/filtering, batch operations, detailed audit logs, and integration with external authentication providers (LDAP, OAuth).

**Total Word Count:** 6,320 words

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

