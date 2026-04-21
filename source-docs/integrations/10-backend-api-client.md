# Flask Backend API Client

## Overview
The BackendAPIClient (src/app/core/backend_client.py) provides HTTP client for communicating with Project-AI's Flask web backend, enabling desktop-to-web synchronization.

## Architecture
`
Desktop Application
    ↓
BackendAPIClient (requests library)
    ↓
Flask REST API (port 5000)
    ↓
PostgreSQL Database
`

## Configuration
`ash
PROJECT_AI_BACKEND_URL=https://127.0.0.1:5000  # Default localhost
`

## Implementation
`python
# src/app/core/backend_client.py
from requests import Session

class BackendAPIClient:
    def __init__(self, base_url: str = None, timeout: float = 5.0):
        self.base_url = base_url or os.getenv('PROJECT_AI_BACKEND_URL', 'https://127.0.0.1:5000')
        self.session = Session()
        self.timeout = timeout
        self.token = None
    
    def get_status(self) -> dict:
        response = self.session.get(f'{self.base_url}/api/status', timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def login(self, username: str, password: str) -> dict:
        payload = {'username': username, 'password': password}
        response = self.session.post(
            f'{self.base_url}/api/auth/login',
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def authenticate(self, username: str, password: str) -> AuthResult:
        try:
            login_data = self.login(username, password)
            self.token = login_data.get('token')
            return AuthResult(success=True, message='Authenticated', token=self.token, user=login_data.get('user'))
        except Exception as e:
            return AuthResult(success=False, message=str(e))
`

## Usage Patterns
`python
from app.core.backend_client import BackendAPIClient

# Initialize client
client = BackendAPIClient()

# Check backend health
status = client.get_status()
print(f\"Backend status: {status['status']}\")

# Authenticate
result = client.authenticate('username', 'password')
if result.success:
    print(f'Token: {result.token}')
else:
    print(f'Auth failed: {result.message}')

# Make authenticated request
profile = client.get_profile(token=result.token)
`

## References
- Requests library: https://requests.readthedocs.io
- Flask backend: web/backend/app.py


---

## Related Documentation

- **Relationship Map**: [[relationships\integrations\README.md]]
