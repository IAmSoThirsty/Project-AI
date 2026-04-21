# End-to-End Testing

**Purpose:** Complete system testing from user perspective  
**Directory:** `tests/e2e/`  
**Coverage:** Web backend, governance API, complete user flows  

---

## Overview

E2E tests validate:

1. **Web Backend Endpoints** - API functionality
2. **Complete User Flows** - Login to task completion
3. **Governance API** - Policy enforcement end-to-end
4. **System Integration** - All components working together

---

## Directory Structure

```
tests/e2e/
├── README.md                           # E2E test documentation
├── __init__.py
├── test_web_backend_endpoints.py       # Individual endpoint tests
├── test_web_backend_complete_e2e.py    # Complete backend flows
├── test_system_integration_e2e.py      # Full system E2E
└── test_governance_api_e2e.py          # Governance API E2E
```

---

## Web Backend Endpoint Testing

### test_web_backend_endpoints.py

**Purpose:** Test individual Flask API endpoints

#### Health Check
```python
def test_health_endpoint(client):
    """Test /api/health endpoint."""
    response = client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data
```

#### Authentication Endpoints
```python
def test_login_endpoint(client, test_user):
    """Test /api/login endpoint."""
    response = client.post("/api/login", json={
        "username": "testuser",
        "password": "testpass123"
    })
    
    assert response.status_code == 200
    data = response.json
    assert "token" in data
    assert "user" in data
    assert data["user"]["username"] == "testuser"

def test_logout_endpoint(client, authenticated_client):
    """Test /api/logout endpoint."""
    response = authenticated_client.post("/api/logout")
    
    assert response.status_code == 200
    data = response.json
    assert data["message"] == "Logged out successfully"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post("/api/login", json={
        "username": "nonexistent",
        "password": "wrongpass"
    })
    
    assert response.status_code == 401
    data = response.json
    assert "error" in data
    assert "invalid" in data["error"].lower()
```

#### Intent Processing
```python
def test_intent_endpoint(authenticated_client):
    """Test /api/intent endpoint."""
    response = authenticated_client.post("/api/intent", json={
        "intent": "What is machine learning?",
        "context": {"topic": "AI"}
    })
    
    assert response.status_code == 200
    data = response.json
    assert "response" in data
    assert len(data["response"]) > 0
    assert "processed" in data
    assert data["processed"] is True

def test_intent_without_auth(client):
    """Test intent endpoint requires authentication."""
    response = client.post("/api/intent", json={
        "intent": "test intent"
    })
    
    assert response.status_code == 401
```

#### Learning Request Endpoints
```python
def test_create_learning_request(authenticated_client):
    """Test creating learning request via API."""
    response = authenticated_client.post("/api/learning/request", json={
        "topic": "Python",
        "description": "Learn async programming"
    })
    
    assert response.status_code == 201
    data = response.json
    assert "request_id" in data
    assert data["status"] == "pending"

def test_get_learning_request(authenticated_client, learning_request_id):
    """Test retrieving learning request."""
    response = authenticated_client.get(
        f"/api/learning/request/{learning_request_id}"
    )
    
    assert response.status_code == 200
    data = response.json
    assert data["id"] == learning_request_id
    assert "topic" in data
    assert "status" in data

def test_approve_learning_request(authenticated_client, learning_request_id):
    """Test approving learning request."""
    response = authenticated_client.post(
        f"/api/learning/request/{learning_request_id}/approve"
    )
    
    assert response.status_code == 200
    data = response.json
    assert data["status"] == "approved"
```

#### Memory Endpoints
```python
def test_add_knowledge(authenticated_client):
    """Test adding knowledge via API."""
    response = authenticated_client.post("/api/memory/knowledge", json={
        "category": "user_prefs",
        "key": "theme",
        "value": "dark"
    })
    
    assert response.status_code == 201
    data = response.json
    assert data["stored"] is True

def test_get_knowledge(authenticated_client):
    """Test retrieving knowledge."""
    # First add knowledge
    authenticated_client.post("/api/memory/knowledge", json={
        "category": "user_prefs",
        "key": "language",
        "value": "en"
    })
    
    # Then retrieve it
    response = authenticated_client.get(
        "/api/memory/knowledge/user_prefs/language"
    )
    
    assert response.status_code == 200
    data = response.json
    assert data["value"] == "en"
```

---

## Complete Backend Flow Testing

### test_web_backend_complete_e2e.py

**Purpose:** Test complete user workflows through backend

#### Complete User Journey
```python
def test_complete_user_journey(client):
    """Test complete user journey from signup to AI interaction."""
    
    # Step 1: Health check
    health = client.get("/api/health")
    assert health.status_code == 200
    
    # Step 2: User registration
    signup = client.post("/api/signup", json={
        "username": "newuser",
        "password": "SecurePass123!",
        "email": "newuser@example.com"
    })
    assert signup.status_code == 201
    
    # Step 3: Login
    login = client.post("/api/login", json={
        "username": "newuser",
        "password": "SecurePass123!"
    })
    assert login.status_code == 200
    token = login.json["token"]
    
    # Step 4: Get user profile
    headers = {"Authorization": f"Bearer {token}"}
    profile = client.get("/api/user/profile", headers=headers)
    assert profile.status_code == 200
    assert profile.json["username"] == "newuser"
    
    # Step 5: Send intent
    intent = client.post("/api/intent", 
        headers=headers,
        json={"intent": "Hello, AI!"}
    )
    assert intent.status_code == 200
    assert "response" in intent.json
    
    # Step 6: Create learning request
    learning = client.post("/api/learning/request",
        headers=headers,
        json={
            "topic": "Python",
            "description": "Learn decorators"
        }
    )
    assert learning.status_code == 201
    request_id = learning.json["request_id"]
    
    # Step 7: Check learning request status
    status = client.get(f"/api/learning/request/{request_id}",
        headers=headers
    )
    assert status.status_code == 200
    assert status.json["status"] == "pending"
    
    # Step 8: Add knowledge to memory
    knowledge = client.post("/api/memory/knowledge",
        headers=headers,
        json={
            "category": "user_prefs",
            "key": "favorite_language",
            "value": "Python"
        }
    )
    assert knowledge.status_code == 201
    
    # Step 9: Retrieve knowledge
    stored = client.get(
        "/api/memory/knowledge/user_prefs/favorite_language",
        headers=headers
    )
    assert stored.status_code == 200
    assert stored.json["value"] == "Python"
    
    # Step 10: Logout
    logout = client.post("/api/logout", headers=headers)
    assert logout.status_code == 200
```

#### Error Recovery Flow
```python
def test_error_recovery_flow(client, authenticated_client):
    """Test system recovery from errors."""
    
    # Step 1: Cause validation error
    response = authenticated_client.post("/api/intent", json={
        "intent": ""  # Empty intent should fail
    })
    assert response.status_code == 400
    
    # Step 2: Verify system still functional
    health = client.get("/api/health")
    assert health.status_code == 200
    
    # Step 3: Send valid request
    response = authenticated_client.post("/api/intent", json={
        "intent": "Valid intent"
    })
    assert response.status_code == 200
    
    # Step 4: Verify error logged but not affecting subsequent requests
    assert response.json["errors_encountered"] == 0
```

---

## System Integration E2E

### test_system_integration_e2e.py

**Purpose:** Test full desktop + web system integration

#### Desktop to Web Integration
```python
def test_desktop_to_web_sync(desktop_app, web_client):
    """Test data sync between desktop and web versions."""
    
    # Step 1: Create user in desktop app
    desktop_app.user_manager.create_user("syncuser", "password123")
    
    # Step 2: Sync to cloud (mock)
    sync_result = desktop_app.cloud_sync.push_user_data("syncuser")
    assert sync_result["success"] is True
    
    # Step 3: Login via web
    response = web_client.post("/api/login", json={
        "username": "syncuser",
        "password": "password123"
    })
    assert response.status_code == 200
    
    # Step 4: Verify user data accessible
    token = response.json["token"]
    headers = {"Authorization": f"Bearer {token}"}
    profile = web_client.get("/api/user/profile", headers=headers)
    assert profile.json["username"] == "syncuser"
```

#### Multi-User Concurrent Access
```python
def test_concurrent_user_access(client):
    """Test multiple users accessing system concurrently."""
    from concurrent.futures import ThreadPoolExecutor
    
    users = [
        ("user1", "pass1"),
        ("user2", "pass2"),
        ("user3", "pass3"),
    ]
    
    # Create users
    for username, password in users:
        client.post("/api/signup", json={
            "username": username,
            "password": password
        })
    
    def user_workflow(username, password):
        # Login
        login = client.post("/api/login", json={
            "username": username,
            "password": password
        })
        token = login.json["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Send intent
        intent = client.post("/api/intent",
            headers=headers,
            json={"intent": f"Hello from {username}"}
        )
        return intent.status_code == 200
    
    # Execute workflows concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(user_workflow, username, password)
            for username, password in users
        ]
        results = [f.result() for f in futures]
    
    # Verify all succeeded
    assert all(results)
```

---

## Governance API E2E

### test_governance_api_e2e.py

**Purpose:** Test governance and policy enforcement end-to-end

#### Policy Enforcement Flow
```python
def test_governance_policy_enforcement(authenticated_client):
    """Test complete policy enforcement flow."""
    
    # Step 1: Attempt action requiring governance approval
    response = authenticated_client.post("/api/action/sensitive", json={
        "action": "delete_user_data",
        "user_id": "12345"
    })
    
    # Step 2: Verify governance check triggered
    assert response.status_code == 403
    data = response.json
    assert "governance" in data
    assert data["governance"]["requires_approval"] is True
    
    # Step 3: Get governance token
    governance_token = data["governance"]["token"]
    
    # Step 4: Request approval
    approval = authenticated_client.post("/api/governance/approve", json={
        "token": governance_token,
        "approver": "admin",
        "rationale": "User requested data deletion (GDPR)"
    })
    assert approval.status_code == 200
    
    # Step 5: Retry action with approval token
    response = authenticated_client.post("/api/action/sensitive", json={
        "action": "delete_user_data",
        "user_id": "12345",
        "governance_token": governance_token
    })
    
    # Step 6: Verify action executed
    assert response.status_code == 200
    assert response.json["executed"] is True
    assert "audit_id" in response.json
```

#### Compliance Audit Trail
```python
def test_compliance_audit_trail(authenticated_client):
    """Test complete audit trail for compliance."""
    
    # Step 1: Perform auditable action
    response = authenticated_client.post("/api/data/process", json={
        "data": "sensitive_data",
        "operation": "encrypt"
    })
    audit_id = response.json["audit_id"]
    
    # Step 2: Retrieve audit record
    audit = authenticated_client.get(f"/api/audit/{audit_id}")
    assert audit.status_code == 200
    
    audit_data = audit.json
    assert audit_data["action"] == "data_process"
    assert audit_data["operation"] == "encrypt"
    assert "timestamp" in audit_data
    assert "user" in audit_data
    
    # Step 3: Verify audit completeness
    required_fields = [
        "action", "user", "timestamp", "result",
        "ip_address", "user_agent"
    ]
    for field in required_fields:
        assert field in audit_data
```

---

## E2E Test Fixtures

### Common Fixtures

```python
@pytest.fixture
def client():
    """Create Flask test client."""
    from web.backend.app import create_app
    app = create_app(config="testing")
    with app.test_client() as client:
        yield client

@pytest.fixture
def test_user(client):
    """Create test user."""
    client.post("/api/signup", json={
        "username": "testuser",
        "password": "testpass123"
    })
    return {"username": "testuser", "password": "testpass123"}

@pytest.fixture
def authenticated_client(client, test_user):
    """Create authenticated test client."""
    response = client.post("/api/login", json=test_user)
    token = response.json["token"]
    
    class AuthenticatedClient:
        def __init__(self, client, token):
            self.client = client
            self.token = token
        
        def get(self, *args, **kwargs):
            kwargs.setdefault("headers", {})
            kwargs["headers"]["Authorization"] = f"Bearer {self.token}"
            return self.client.get(*args, **kwargs)
        
        def post(self, *args, **kwargs):
            kwargs.setdefault("headers", {})
            kwargs["headers"]["Authorization"] = f"Bearer {self.token}"
            return self.client.post(*args, **kwargs)
    
    return AuthenticatedClient(client, token)

@pytest.fixture
def learning_request_id(authenticated_client):
    """Create learning request and return ID."""
    response = authenticated_client.post("/api/learning/request", json={
        "topic": "Test Topic",
        "description": "Test Description"
    })
    return response.json["request_id"]
```

---

## Running E2E Tests

### Run All E2E Tests
```bash
pytest tests/e2e/ -v
```

### Run Specific E2E Suite
```bash
pytest tests/e2e/test_web_backend_endpoints.py -v
pytest tests/e2e/test_web_backend_complete_e2e.py -v
```

### Run with Backend Server
```bash
# Terminal 1: Start backend
cd web/backend
flask run

# Terminal 2: Run E2E tests
pytest tests/e2e/ --backend-url=http://localhost:5000
```

### Run in Docker
```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

---

## E2E Test Patterns

### Pattern 1: Complete User Flow
```python
def test_user_flow(client):
    # 1. Signup
    # 2. Login
    # 3. Perform actions
    # 4. Verify state
    # 5. Logout
    pass
```

### Pattern 2: Error Injection
```python
def test_error_handling(client, mocker):
    # Inject error
    mocker.patch('module.function', side_effect=Exception)
    
    # Verify graceful handling
    response = client.post("/api/action")
    assert response.status_code == 500
    assert "error" in response.json
```

### Pattern 3: State Verification
```python
def test_state_consistency(client, db):
    # Perform action via API
    client.post("/api/action")
    
    # Verify database state
    record = db.query(Model).first()
    assert record.status == "completed"
```

---

## Best Practices

### ✅ DO
- Test complete user workflows
- Use authenticated clients for protected endpoints
- Verify audit trails
- Test error recovery
- Use fixtures for common setup
- Test concurrent access

### ❌ DON'T
- Test individual functions (use unit tests)
- Skip authentication in E2E tests
- Ignore error responses
- Share state between E2E tests
- Hardcode URLs (use fixtures)
- Skip cleanup

---

## Next Steps

1. Read `11_GUI_TESTING.md` for GUI E2E patterns
2. See `12_TEST_MAINTENANCE.md` for maintaining E2E tests
3. Check `tests/e2e/README.md` for E2E-specific documentation

---

**See Also:**
- `tests/e2e/README.md` - E2E test documentation
- `tests/e2e/test_web_backend_complete_e2e.py` - Complete flows
- `web/backend/app.py` - Flask application
- `DEPLOYMENT.md` - E2E testing in CI/CD
