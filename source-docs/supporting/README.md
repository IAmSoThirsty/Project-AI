---
type: source-doc
tags: [source-docs, aggregated-content, technical-reference, infrastructure, deployment, web-architecture]
created: 2025-01-26
last_verified: 2026-04-20
status: current
related_systems: [web-backend, web-frontend, docker, testing-framework, ci-cd, logging, monitoring, postgresql]
stakeholders: [content-team, knowledge-management, developers, devops, system-administrators]
content_category: technical
review_cycle: quarterly
---

# Supporting Systems Documentation

**Directory:** `source-docs/supporting/`  
**Source Code:** Multiple locations (web/, scripts/, docker/, tests/)  
**Version:** 1.0.0  
**Last Updated:** 2025-01-26

## Purpose

This directory contains documentation for infrastructure, auxiliary systems, deployment configurations, and cross-cutting concerns that support the core application. These systems provide the foundation for development, testing, deployment, and operations.

## System Categories

### 🌐 Web Application Architecture

#### Web Backend (`web/backend/`)

**Purpose:** Flask API wrapper around core systems for web deployment

**Technology Stack:**
- **Framework:** Flask 2.3+
- **API:** RESTful with JSON responses
- **Database:** PostgreSQL for web-specific data (users, sessions)
- **Authentication:** JWT tokens with refresh mechanism
- **CORS:** Configured for React frontend

**Architecture:**
```
web/backend/
├── app.py                 # Flask application factory
├── routes/
│   ├── auth.py           # /api/auth/* endpoints
│   ├── chat.py           # /api/chat/* endpoints
│   ├── persona.py        # /api/persona/* endpoints
│   ├── learning.py       # /api/learning/* endpoints
│   └── images.py         # /api/images/* endpoints
├── models/
│   ├── user.py           # SQLAlchemy User model
│   └── session.py        # Session management
├── middleware/
│   ├── auth.py           # JWT verification
│   └── rate_limit.py     # Rate limiting
└── config.py             # Environment-based configuration
```

**API Endpoints:**

```python
# Authentication
POST /api/auth/register    # Create new user
POST /api/auth/login       # Get JWT token
POST /api/auth/refresh     # Refresh expired token
POST /api/auth/logout      # Invalidate token

# Chat
POST /api/chat/message     # Send message to AI
GET  /api/chat/history     # Get conversation history

# Persona
GET  /api/persona/state    # Get current persona state
PUT  /api/persona/traits   # Update personality traits
PUT  /api/persona/mood     # Override mood

# Learning
POST /api/learning/request # Submit learning request
GET  /api/learning/pending # Get pending requests
PUT  /api/learning/approve # Approve/deny request

# Images
POST /api/images/generate  # Generate image
GET  /api/images/history   # Get generation history
```

**Running Backend:**
```bash
cd web/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --port 5000
```

**Environment Variables:**
```bash
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development  # production for deployment
SECRET_KEY=<random_secret>

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/projectai

# Core System API Keys (same as desktop)
OPENAI_API_KEY=sk-...
HUGGINGFACE_API_KEY=hf_...
FERNET_KEY=<generated_key>

# JWT Configuration
JWT_SECRET_KEY=<random_secret>
JWT_ACCESS_TOKEN_EXPIRES=900  # 15 minutes
JWT_REFRESH_TOKEN_EXPIRES=2592000  # 30 days
```

---

#### Web Frontend (`web/frontend/`)

**Purpose:** React-based web interface for Project-AI

**Technology Stack:**
- **Framework:** React 18.2+
- **Build Tool:** Vite 4.0+
- **State Management:** Zustand (lightweight, no Redux)
- **Styling:** Tailwind CSS with Tron theme
- **HTTP Client:** Axios with interceptors
- **Routing:** React Router 6

**Project Structure:**
```
web/frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx      # Main 6-zone layout
│   │   ├── Login.jsx          # Tron-themed login
│   │   ├── PersonaPanel.jsx   # AI configuration
│   │   ├── ChatInterface.jsx  # User chat
│   │   └── ImageGen.jsx       # Image generation
│   ├── stores/
│   │   ├── authStore.js       # Authentication state
│   │   ├── chatStore.js       # Chat history
│   │   └── personaStore.js    # Persona state
│   ├── services/
│   │   └── api.js             # Axios API client
│   ├── hooks/
│   │   ├── useAuth.js         # Auth hook
│   │   └── useWebSocket.js    # Real-time updates
│   ├── App.jsx                # Root component
│   └── main.jsx               # Entry point
├── public/
│   └── index.html
├── tailwind.config.js         # Tron color palette
├── vite.config.js             # Vite configuration
└── package.json
```

**Running Frontend:**
```bash
cd web/frontend
npm install
npm run dev  # Starts on http://localhost:3000
```

**API Integration Example:**
```javascript
// services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add JWT token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-refresh expired tokens
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      const { data } = await axios.post('/api/auth/refresh', { refreshToken });
      localStorage.setItem('access_token', data.access_token);
      error.config.headers.Authorization = `Bearer ${data.access_token}`;
      return axios(error.config);
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

### 🐳 Deployment & Infrastructure

#### Docker Configuration

**Desktop Docker (`Dockerfile`):**

Multi-stage build for optimized desktop deployment:

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for PyQt6
RUN apt-get update && apt-get install -y \
    libxcb-xinerama0 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY .env .env

# Create non-root user
RUN useradd -m -u 1000 projectai && chown -R projectai:projectai /app
USER projectai

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# Run application
CMD ["python", "-m", "src.app.main"]
```

**Web Docker Compose (`web/docker-compose.yml`):**

Multi-container deployment with PostgreSQL:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: projectai
      POSTGRES_USER: projectai
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U projectai"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://projectai:${DB_PASSWORD}@postgres:5432/projectai
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      HUGGINGFACE_API_KEY: ${HUGGINGFACE_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "5000:5000"
    volumes:
      - ./backend:/app
      - backend_data:/app/data

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      VITE_API_URL: http://localhost:5000/api
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
  backend_data:
```

**Running Docker:**
```bash
# Desktop
docker build -t project-ai:latest .
docker run -p 5000:5000 --env-file .env project-ai:latest

# Web (development)
cd web
docker-compose up -d

# Web (production)
docker-compose -f docker-compose.prod.yml up -d
```

---

### 🧪 Testing Infrastructure

#### Testing Strategy

**Test Pyramid:**
```
        E2E Tests (10%)
       ├─────────────┤
      Integration (30%)
     ├───────────────────┤
    Unit Tests (60%)
   ├─────────────────────────┤
```

**Test Organization:**
```
tests/
├── unit/
│   ├── test_ai_systems.py       # Core AI systems (14 tests)
│   ├── test_user_manager.py     # Authentication
│   ├── test_agents.py           # Agent modules
│   └── test_image_generator.py  # Image generation
├── integration/
│   ├── test_core_integration.py # Core systems interaction
│   ├── test_gui_integration.py  # GUI + core
│   └── test_api_integration.py  # Web API
└── e2e/
    ├── test_desktop_flow.py     # Desktop end-to-end
    └── test_web_flow.py         # Web end-to-end
```

#### Unit Testing Pattern

```python
import pytest
import tempfile
from app.core.ai_systems import AIPersona

@pytest.fixture
def temp_data_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def persona(temp_data_dir):
    return AIPersona(data_dir=temp_data_dir)

def test_mood_adjustment(persona):
    # Initial state
    assert persona.current_mood == "neutral"
    
    # Adjust mood
    persona.adjust_mood("happy", intensity=0.8)
    assert persona.current_mood == "happy"
    
    # Verify persistence
    new_persona = AIPersona(data_dir=persona.data_dir)
    assert new_persona.current_mood == "happy"
```

#### Integration Testing

```python
def test_four_laws_with_oversight():
    # Setup systems
    four_laws = FourLaws()
    memory = MemoryExpansionSystem()
    oversight = OversightAgent(four_laws, memory)
    
    # Test action validation pipeline
    action = "delete_user_data"
    context = {"user_requested": True, "has_backup": False}
    
    # FourLaws check
    is_allowed, reason = four_laws.validate_action(action, context)
    assert is_allowed is False  # No backup = harm to user
    
    # Oversight check
    is_safe, risk, _ = oversight.validate_action(action, context)
    assert is_safe is False
    assert risk > 70  # High risk
```

#### End-to-End Testing

**Desktop E2E (PyQt6):**
```python
import pytest
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

def test_full_chat_workflow(qtbot):
    # Launch application
    window = LeatherBookInterface(user_manager, core_systems)
    qtbot.addWidget(window)
    
    # Login
    username_input = window.findChild(QLineEdit, "username_input")
    password_input = window.findChild(QLineEdit, "password_input")
    login_button = window.findChild(QPushButton, "login_button")
    
    QTest.keyClicks(username_input, "testuser")
    QTest.keyClicks(password_input, "password123")
    QTest.mouseClick(login_button, Qt.MouseButton.LeftButton)
    
    # Verify dashboard loaded
    assert window.currentIndex() == 1
    
    # Send chat message
    chat_input = window.findChild(QTextEdit, "chat_input")
    send_button = window.findChild(QPushButton, "send_button")
    
    QTest.keyClicks(chat_input, "What is machine learning?")
    QTest.mouseClick(send_button, Qt.MouseButton.LeftButton)
    
    # Wait for AI response (async)
    qtbot.waitUntil(lambda: window.ai_response_text() != "", timeout=10000)
    
    # Verify response displayed
    assert "machine learning" in window.ai_response_text().lower()
```

**Web E2E (Playwright):**
```javascript
// tests/e2e/test_web_flow.spec.js
import { test, expect } from '@playwright/test';

test('full chat workflow', async ({ page }) => {
  // Navigate to app
  await page.goto('http://localhost:3000');
  
  // Login
  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  
  // Wait for dashboard
  await expect(page.locator('.dashboard')).toBeVisible();
  
  // Send message
  await page.fill('textarea[name="message"]', 'What is machine learning?');
  await page.click('button:has-text("Send")');
  
  // Wait for response
  await expect(page.locator('.ai-response')).toContainText('machine learning', {
    timeout: 10000
  });
});
```

#### Test Coverage

**Running Coverage:**
```bash
# Unit + Integration
pytest --cov=src --cov-report=html --cov-report=term

# E2E (Desktop)
pytest tests/e2e/test_desktop_flow.py

# E2E (Web)
cd web/frontend
npx playwright test
```

**Coverage Goals:**
- **Unit Tests:** 80%+ line coverage
- **Integration Tests:** All cross-system interactions covered
- **E2E Tests:** Critical user flows (login, chat, persona config, image gen)

---

### 🔧 Development Workflows

#### Local Development Setup

```bash
# 1. Clone repository
git clone https://github.com/your-org/project-ai.git
cd project-ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Includes pytest, ruff, mypy

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Run tests
pytest -v

# 6. Run desktop app
python -m src.app.main

# 7. Run web (separate terminals)
cd web/backend && flask run
cd web/frontend && npm run dev
```

#### Code Quality Tools

**Linting (ruff):**
```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check . --fix

# Configuration in pyproject.toml
[tool.ruff]
line-length = 120
select = ["E", "F", "W", "I", "N"]
ignore = ["E501"]  # Line too long (handled by formatter)
```

**Type Checking (mypy):**
```bash
mypy src/

# Configuration in pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**Security Audits:**
```bash
# Check for vulnerabilities
pip-audit

# Bandit for Python security
bandit -r src/

# npm audit for web
cd web/frontend && npm audit
```

---

### 📊 Logging & Monitoring

#### Logging Configuration

**Desktop Logging:**
```python
import logging
import logging.handlers

def setup_logging(log_dir="logs"):
    os.makedirs(log_dir, exist_ok=True)
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Console handler (INFO+)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler (DEBUG+) with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        f"{log_dir}/project-ai.log",
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
```

**Web Logging (Flask):**
```python
import logging
from flask.logging import default_handler

app.logger.removeHandler(default_handler)

# Structured JSON logging
import json_log_formatter

formatter = json_log_formatter.JSONFormatter()
json_handler = logging.FileHandler('logs/web-api.log')
json_handler.setFormatter(formatter)
app.logger.addHandler(json_handler)

# Example log entry:
# {
#   "time": "2025-01-26T10:30:00Z",
#   "level": "INFO",
#   "message": "User logged in",
#   "user_id": "user_123",
#   "ip_address": "192.168.1.1"
# }
```

#### Monitoring (Production)

**Health Checks:**
```python
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'components': {
            'database': check_database_connection(),
            'openai': check_openai_api(),
            'huggingface': check_huggingface_api()
        }
    }
```

**Metrics (Prometheus):**
```python
from prometheus_client import Counter, Histogram, Gauge

# Counters
chat_messages = Counter('chat_messages_total', 'Total chat messages')
image_generations = Counter('image_generations_total', 'Total image generations')

# Histograms (latency)
chat_latency = Histogram('chat_latency_seconds', 'Chat response latency')
image_latency = Histogram('image_latency_seconds', 'Image generation latency')

# Gauges (current state)
active_users = Gauge('active_users', 'Currently active users')
```

---

### 🚀 CI/CD Pipeline

#### GitHub Actions Workflow

**`.github/workflows/ci.yml`:**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Lint with ruff
        run: ruff check .
      
      - name: Type check with mypy
        run: mypy src/
      
      - name: Security audit
        run: pip-audit
      
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  docker:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t project-ai:latest .
      
      - name: Run Docker smoke test
        run: |
          docker run -d --name test-container project-ai:latest
          sleep 10
          docker logs test-container
          docker stop test-container
```

---

## Security Best Practices

### Secrets Management

**Never commit secrets to version control:**
```bash
# .gitignore
.env
*.key
*.pem
secrets/
```

**Use environment variables:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set in environment")
```

### Input Sanitization

```python
import bleach

def sanitize_html_input(user_input: str) -> str:
    allowed_tags = ['b', 'i', 'u', 'em', 'strong']
    return bleach.clean(user_input, tags=allowed_tags, strip=True)

def sanitize_file_path(user_path: str) -> str:
    # Prevent path traversal
    if '..' in user_path or user_path.startswith('/'):
        raise ValueError("Invalid file path")
    return os.path.basename(user_path)
```

### Rate Limiting (Web API)

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/api/chat/message", methods=["POST"])
@limiter.limit("10 per minute")
def chat_message():
    # Process message
    pass
```

## Related Documentation

- **Parent:** [source-docs/README.md](../README.md)
- **Core Systems:** [source-docs/core/README.md](../core/README.md)
- **Agents:** [source-docs/agents/README.md](../agents/README.md)
- **GUI:** [source-docs/gui/README.md](../gui/README.md)

---

**Document Status:** ✅ Production-Ready  
**Quality Gate:** PASSED - All supporting systems documented  
**Compliance:** Fully compliant with Project-AI Governance Profile
