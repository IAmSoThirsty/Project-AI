# Backend API Client

**Module:** `src/app/core/backend_client.py`  
**Type:** Core Infrastructure  
**Dependencies:** requests  
**Related Modules:** user_manager.py (authentication integration)

---

## Overview

The Backend API Client provides HTTP client functionality for interacting with Project-AI's Flask web backend, with structured authentication, profile fetching, and status endpoints.

### Core Features

- **RESTful API Client**: HTTP wrapper for Flask backend endpoints
- **Structured Authentication**: Type-safe `AuthResult` dataclass
- **Session Management**: Persistent session with token headers
- **Error Handling**: Robust error extraction and reporting
- **URL Normalization**: Automatic HTTPS enforcement and validation

---

## Architecture

```
BackendAPIClient
├── Session Management (requests.Session)
├── Base URL Normalization (HTTPS enforcement)
├── Authentication Flow (login → token → profile)
├── Status Heartbeat (/api/status)
└── Error Handling (structured error messages)
```

---

## Core Classes

### BackendAPIClient

```python
from app.core.backend_client import BackendAPIClient

# Initialize with default URL (from environment)
client = BackendAPIClient()  # Uses PROJECT_AI_BACKEND_URL env var

# Initialize with custom URL
client = BackendAPIClient(base_url="https://api.project-ai.example")

# Initialize with custom session
import requests
session = requests.Session()
session.headers["User-Agent"] = "Project-AI/2.1.0"
client = BackendAPIClient(base_url="https://api.example.com", session=session)

# Custom timeout
client = BackendAPIClient(timeout=10.0)  # 10 seconds (default: 5.0)
```

---

## Authentication

### AuthResult Dataclass

```python
@dataclass
class AuthResult:
    """Structured response for login attempts."""
    success: bool
    message: str
    token: str | None = None
    user: dict[str, Any] | None = None

# Example usage
result = client.authenticate("admin", "password123")
if result.success:
    print(f"Token: {result.token}")
    print(f"User: {result.user['username']}")
else:
    print(f"Auth failed: {result.message}")
```

### Authenticate Method

```python
def authenticate(self, username: str, password: str) -> AuthResult:
    """
    Attempt login then fetch profile.
    
    Workflow:
    1. POST /api/auth/login with credentials
    2. Extract token from response
    3. GET /api/auth/profile with token
    4. Return structured AuthResult
    """
    result = client.authenticate("admin", "SecureP@ss123")
    
    if result.success:
        # Token is automatically stored in session headers
        print(f"Logged in as {result.user['username']}")
        print(f"Role: {result.user['role']}")
    else:
        print(f"Login failed: {result.message}")
        # Common errors:
        # - "Invalid credentials"
        # - "Account locked"
        # - "Backend did not return token"
```

### Login Endpoint

```python
def login(self, username: str, password: str) -> dict[str, Any]:
    """
    Low-level login endpoint.
    
    POST /api/auth/login
    Request: {"username": "admin", "password": "password"}
    Response: {"token": "eyJ...", "user": {...}}
    """
    payload = {"username": username, "password": password}
    response = self.session.post(
        self._url("/api/auth/login"),
        json=payload,
        timeout=self.timeout
    )
    response.raise_for_status()
    return self._safe_json(response)

# Usage
try:
    login_data = client.login("admin", "password")
    print(f"Token: {login_data['token']}")
except requests.HTTPError as e:
    print(f"Login failed: {client._extract_error(e)}")
```

### Get Profile

```python
def get_profile(self, token: str | None = None) -> dict[str, Any]:
    """
    Fetch user profile.
    
    GET /api/auth/profile
    Headers: X-Auth-Token: <token>
    Response: {"user": {"username": "admin", "role": "admin", ...}}
    """
    # Use stored token or provide custom token
    profile = client.get_profile()  # Uses self.token
    # OR
    profile = client.get_profile(token="custom_token")
    
    print(f"Username: {profile['user']['username']}")
    print(f"Role: {profile['user']['role']}")
    print(f"Approved: {profile['user']['approved']}")

# Internal implementation
headers = {"X-Auth-Token": auth_token}
response = self.session.get(
    self._url("/api/auth/profile"),
    headers=headers,
    timeout=self.timeout
)
```

---

## Status Endpoint

```python
def get_status(self) -> dict[str, Any]:
    """
    Fetch backend status heartbeat.
    
    GET /api/status
    Response: {"status": "online", "timestamp": "2026-04-20T14:00:00Z"}
    """
    status = client.get_status()
    print(f"Backend status: {status['status']}")
    print(f"Timestamp: {status['timestamp']}")

# Health check example
def check_backend_health():
    try:
        status = client.get_status()
        return status["status"] == "online"
    except Exception:
        return False

if check_backend_health():
    print("✅ Backend is online")
else:
    print("❌ Backend is offline")
```

---

## URL Normalization

### Base URL Handling

```python
@staticmethod
def _normalize_base_url(url: str) -> str:
    """
    Normalize base URL with HTTPS enforcement.
    
    Rules:
    1. If no scheme: Add "https://"
    2. If "http://": Log warning (insecure)
    3. Remove trailing slash
    """
    # Examples:
    "api.example.com" → "https://api.example.com"
    "http://localhost:5000" → "http://localhost:5000" (warning logged)
    "https://api.example.com/" → "https://api.example.com"

# Usage in initialization
client = BackendAPIClient(base_url="api.project-ai.example")
# Automatically converted to: https://api.project-ai.example
```

### URL Construction

```python
def _url(self, path: str) -> str:
    """Construct full URL from path."""
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{self.base_url}{path}"

# Examples:
client._url("/api/status") → "https://api.example.com/api/status"
client._url("api/users") → "https://api.example.com/api/users"
```

---

## Error Handling

### Error Extraction

```python
@staticmethod
def _extract_error(exc: requests.HTTPError) -> str:
    """
    Extract human-readable error message from HTTP exception.
    
    Extraction priority:
    1. JSON response: {"message": "..."}
    2. JSON response: {"error": "..."}
    3. Response body text
    4. Status code + reason
    5. Exception string
    """
    # Example responses:
    # {"message": "Invalid credentials"} → "Invalid credentials"
    # {"error": "User not found"} → "User not found"
    # "<html>404 Not Found</html>" → "404 Not Found"
    # No response → "ConnectionError: ..."

# Usage
try:
    result = client.login("admin", "wrong_password")
except requests.HTTPError as e:
    error_msg = client._extract_error(e)
    print(f"Login error: {error_msg}")
    # Output: "Login error: Invalid credentials"
```

### Exception Hierarchy

```python
# Handled exceptions
requests.HTTPError         # 4xx/5xx responses
requests.RequestException  # Network errors, timeouts
requests.Timeout           # Timeout errors
ValueError                 # Missing token, invalid URL
```

### Error Handling Patterns

```python
from app.core.backend_client import BackendAPIClient, AuthResult
import requests

client = BackendAPIClient()

# Pattern 1: authenticate() method (returns AuthResult)
result = client.authenticate("admin", "password")
if not result.success:
    print(f"Auth failed: {result.message}")
    # Handle error (show login UI, etc.)

# Pattern 2: login() method (raises exceptions)
try:
    login_data = client.login("admin", "password")
    token = login_data["token"]
except requests.HTTPError as e:
    error_msg = client._extract_error(e)
    if "Invalid credentials" in error_msg:
        print("Wrong username or password")
    elif "Account locked" in error_msg:
        print("Account is locked. Try again later.")
except requests.Timeout:
    print("Backend request timed out")
except requests.RequestException as e:
    print(f"Network error: {e}")
```

---

## Integration Examples

### With GUI Login Form

```python
from PyQt6.QtWidgets import QLineEdit, QPushButton, QLabel
from app.core.backend_client import BackendAPIClient

class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.client = BackendAPIClient()
        self.init_ui()
    
    def init_ui(self):
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)
        
        self.status_label = QLabel("")
    
    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        result = self.client.authenticate(username, password)
        
        if result.success:
            self.status_label.setText(f"✅ Logged in as {result.user['username']}")
            self.status_label.setStyleSheet("color: green;")
            # Navigate to main application
            self.navigate_to_dashboard(result.token, result.user)
        else:
            self.status_label.setText(f"❌ {result.message}")
            self.status_label.setStyleSheet("color: red;")
```

### Session Persistence

```python
import json

class PersistentBackendClient(BackendAPIClient):
    """Backend client with token persistence."""
    
    def __init__(self, token_file="data/.auth_token"):
        super().__init__()
        self.token_file = token_file
        self._load_token()
    
    def _load_token(self):
        """Load token from file."""
        if os.path.exists(self.token_file):
            with open(self.token_file) as f:
                data = json.load(f)
                self.token = data.get("token")
                if self.token:
                    self._set_token(self.token)
    
    def authenticate(self, username, password):
        """Authenticate and persist token."""
        result = super().authenticate(username, password)
        if result.success:
            # Save token
            with open(self.token_file, 'w') as f:
                json.dump({"token": result.token}, f)
        return result
    
    def logout(self):
        """Clear token."""
        self.token = None
        if os.path.exists(self.token_file):
            os.remove(self.token_file)

# Usage
client = PersistentBackendClient()
if client.token:
    print("Already logged in (using saved token)")
else:
    result = client.authenticate("admin", "password")
```

### Backend Health Monitor

```python
import time
import schedule

class BackendHealthMonitor:
    def __init__(self, backend_url):
        self.client = BackendAPIClient(base_url=backend_url)
        self.is_online = False
    
    def check_health(self):
        """Check backend health."""
        try:
            status = self.client.get_status()
            self.is_online = status["status"] == "online"
            print(f"✅ Backend online at {status['timestamp']}")
        except Exception as e:
            self.is_online = False
            print(f"❌ Backend offline: {e}")
    
    def start_monitoring(self, interval=60):
        """Start periodic health checks."""
        schedule.every(interval).seconds.do(self.check_health)
        
        while True:
            schedule.run_pending()
            time.sleep(1)

# Usage
monitor = BackendHealthMonitor("https://api.project-ai.example")
monitor.start_monitoring(interval=30)  # Check every 30 seconds
```

---

## Configuration

### Environment Variables

```bash
# Backend URL (default: https://127.0.0.1:5000)
export PROJECT_AI_BACKEND_URL="https://api.project-ai.example"

# Request timeout (seconds)
export PROJECT_AI_TIMEOUT=10.0
```

### Configuration File

```json
{
  "backend": {
    "url": "https://api.project-ai.example",
    "timeout": 10.0,
    "verify_ssl": true,
    "retry_count": 3,
    "retry_backoff": 2.0
  }
}
```

---

## Testing

```python
import unittest
from unittest.mock import Mock, patch
from app.core.backend_client import BackendAPIClient, AuthResult

class TestBackendAPIClient(unittest.TestCase):
    def setUp(self):
        self.client = BackendAPIClient(base_url="https://test.example.com")
    
    @patch('requests.Session.get')
    def test_get_status(self, mock_get):
        """Test status endpoint."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "online"}
        mock_get.return_value = mock_response
        
        status = self.client.get_status()
        self.assertEqual(status["status"], "online")
    
    @patch('requests.Session.post')
    @patch('requests.Session.get')
    def test_authenticate(self, mock_get, mock_post):
        """Test authentication flow."""
        # Mock login response
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "token": "test_token",
            "user": {"username": "test_user"}
        }
        mock_post.return_value = mock_post_response
        
        # Mock profile response
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "user": {"username": "test_user", "role": "user"}
        }
        mock_get.return_value = mock_get_response
        
        result = self.client.authenticate("test_user", "password")
        
        self.assertTrue(result.success)
        self.assertEqual(result.token, "test_token")
        self.assertEqual(result.user["username"], "test_user")
```

---

## Troubleshooting

### "ConnectionError: Failed to connect"
```python
# Check backend URL
print(client.base_url)

# Verify backend is running
curl https://api.project-ai.example/api/status
```

### "HTTPError: 401 Unauthorized"
```python
# Token expired or invalid
# Re-authenticate
result = client.authenticate("admin", "password")
```

### "Timeout: Request timed out"
```python
# Increase timeout
client = BackendAPIClient(timeout=30.0)  # 30 seconds
```

---

**Last Updated:** 2026-04-20  
**Module Version:** 1.0.0  
**Author:** AGENT-036 (Data & Infrastructure Documentation Specialist)
