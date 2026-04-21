# Web Application Deployment (React + Flask)

## Overview

Project-AI includes a web-based version featuring a React 18 frontend (Vite build system) and Flask REST API backend. The web architecture supports development mode (hot reload) and production deployment (Docker, cloud hosting), with clear separation between frontend and backend services.

## Architecture Overview

### Service Separation

```
Web Architecture/
├── Frontend (React + Vite)
│   ├── Port: 3000 (dev), 80/443 (prod)
│   ├── Build Tool: Vite 4.x
│   ├── State: Zustand
│   └── Router: React Router v6
├── Backend (Flask + Python)
│   ├── Port: 5000 (dev), 8000 (prod)
│   ├── WSGI Server: Gunicorn
│   ├── API: RESTful endpoints
│   └── Core: Wraps src/app/core modules
└── Data Layer
    ├── PostgreSQL (production)
    ├── SQLite (development)
    └── Redis (caching, sessions)
```

### Technology Stack

**Frontend**:
- React 18.2
- TypeScript 5.x
- Vite 4.x (build tool)
- Zustand (state management)
- React Router v6
- Material-UI (MUI) v5
- Axios (HTTP client)

**Backend**:
- Flask 3.0
- Flask-CORS (cross-origin)
- Flask-SQLAlchemy (ORM)
- Flask-Login (authentication)
- Gunicorn (WSGI server)
- Python 3.11+

**Database**:
- PostgreSQL 15 (production)
- SQLite (development)

**Caching**:
- Redis 7.x (sessions, rate limiting)

## Project Structure

```
web/
├── backend/
│   ├── app.py                      # Flask application entry point
│   ├── requirements.txt            # Python dependencies
│   ├── config.py                   # Configuration (dev/prod)
│   ├── wsgi.py                     # Gunicorn entry point
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                 # /api/auth/* endpoints
│   │   ├── chat.py                 # /api/chat/* endpoints
│   │   ├── persona.py              # /api/persona/* endpoints
│   │   ├── image.py                # /api/image/* endpoints
│   │   └── knowledge.py            # /api/knowledge/* endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                 # User model
│   │   └── chat.py                 # Chat message model
│   ├── services/
│   │   ├── ai_service.py           # Wraps src/app/core/ai_systems.py
│   │   ├── image_service.py        # Wraps src/app/core/image_generator.py
│   │   └── knowledge_service.py    # Wraps src/app/core/memory
│   └── migrations/                 # Alembic database migrations
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   ├── public/
│   │   └── assets/
│   └── src/
│       ├── main.tsx                # React entry point
│       ├── App.tsx                 # Root component
│       ├── components/
│       │   ├── Chat/
│       │   │   ├── ChatBox.tsx
│       │   │   ├── MessageList.tsx
│       │   │   └── MessageInput.tsx
│       │   ├── Persona/
│       │   │   ├── PersonaPanel.tsx
│       │   │   └── TraitSlider.tsx
│       │   ├── ImageGen/
│       │   │   └── ImageGenerator.tsx
│       │   └── Layout/
│       │       ├── Navbar.tsx
│       │       └── Sidebar.tsx
│       ├── pages/
│       │   ├── Dashboard.tsx
│       │   ├── Chat.tsx
│       │   ├── Persona.tsx
│       │   └── Settings.tsx
│       ├── store/
│       │   ├── authStore.ts        # Zustand authentication state
│       │   ├── chatStore.ts        # Chat history state
│       │   └── personaStore.ts     # AI persona state
│       ├── api/
│       │   └── client.ts           # Axios API client
│       ├── hooks/
│       │   ├── useAuth.ts
│       │   └── useWebSocket.ts
│       └── styles/
│           └── theme.ts            # MUI theme configuration
└── docker-compose.override.yml     # Development services
```

## Backend Configuration

### Flask Application

**Location**: `web/backend/app.py` [[web/backend/app.py]]

```python
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'sqlite:///legion_web.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Import routes
from routes import auth, chat, persona, image, knowledge
app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(chat.bp, url_prefix='/api/chat')
app.register_blueprint(persona.bp, url_prefix='/api/persona')
app.register_blueprint(image.bp, url_prefix='/api/image')
app.register_blueprint(knowledge.bp, url_prefix='/api/knowledge')

# Health check endpoint
@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "version": "1.0.0"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### Configuration Management

**Location**: `web/backend/config.py`

```python
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///legion_web_dev.db'
    CORS_ORIGINS = ['http://localhost:3000']

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    # Use PostgreSQL connection pooling
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

### API Routes Example

**Location**: `web/backend/routes/chat.py`

```python
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.ai_service import AIService

bp = Blueprint('chat', __name__)
ai_service = AIService()

@bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """Send message to AI and get response."""
    data = request.get_json()
    message = data.get('message')
    
    if not message:
        return jsonify({"error": "Message required"}), 400
    
    try:
        # Get AI response using core AI systems
        response = ai_service.chat(
            user_id=current_user.id,
            message=message
        )
        return jsonify({
            "message": message,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/history', methods=['GET'])
@login_required
def get_history():
    """Get chat history for current user."""
    limit = request.args.get('limit', 50, type=int)
    messages = ChatMessage.query.filter_by(user_id=current_user.id)\
                                 .order_by(ChatMessage.timestamp.desc())\
                                 .limit(limit)\
                                 .all()
    return jsonify([msg.to_dict() for msg in messages])
```

### Service Layer (Wrapper)

**Location**: `web/backend/services/ai_service.py`

```python
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from app.core.ai_systems import AIPersona, MemoryExpansionSystem, FourLaws
from app.core.intelligence_engine import IntelligenceEngine

class AIService:
    """Wrapper around core AI systems for web API."""
    
    def __init__(self, data_dir='data'):
        self.persona = AIPersona(data_dir=data_dir)
        self.memory = MemoryExpansionSystem(data_dir=data_dir)
        self.four_laws = FourLaws()
        self.intelligence = IntelligenceEngine()
    
    def chat(self, user_id: str, message: str) -> str:
        """Process chat message through AI systems."""
        # Validate action with Four Laws
        is_allowed, reason = self.four_laws.validate_action(
            action=f"Respond to: {message}",
            context={"is_user_order": True}
        )
        
        if not is_allowed:
            return f"Cannot respond: {reason}"
        
        # Get AI response
        response = self.intelligence.chat(message)
        
        # Update persona state
        self.persona.update_interaction()
        
        # Store in memory
        self.memory.log_conversation(user_id, message, response)
        
        return response
    
    def get_persona_state(self) -> dict:
        """Get current AI persona state."""
        return self.persona.get_state()
    
    def update_persona(self, traits: dict):
        """Update persona traits."""
        for trait, value in traits.items():
            if hasattr(self.persona, trait):
                setattr(self.persona, trait, value)
        self.persona._save_state()
```

## Frontend Configuration

### Vite Configuration

**Location**: `web/frontend/vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@store': path.resolve(__dirname, './src/store'),
      '@api': path.resolve(__dirname, './src/api')
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui': ['@mui/material', '@emotion/react', '@emotion/styled']
        }
      }
    }
  }
})
```

### API Client

**Location**: `web/frontend/src/api/client.ts`

```typescript
import axios, { AxiosInstance } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // Request interceptor (add auth token)
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor (handle errors)
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Unauthorized - redirect to login
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Chat endpoints
  async sendMessage(message: string) {
    const response = await this.client.post('/chat/send', { message })
    return response.data
  }

  async getChatHistory(limit = 50) {
    const response = await this.client.get('/chat/history', { params: { limit } })
    return response.data
  }

  // Persona endpoints
  async getPersona() {
    const response = await this.client.get('/persona')
    return response.data
  }

  async updatePersona(traits: Record<string, number>) {
    const response = await this.client.post('/persona/update', traits)
    return response.data
  }

  // Image generation
  async generateImage(prompt: string, style: string) {
    const response = await this.client.post('/image/generate', { prompt, style })
    return response.data
  }
}

export const apiClient = new ApiClient()
export default apiClient
```

### Zustand State Store

**Location**: `web/frontend/src/store/chatStore.ts`

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { apiClient } from '@api/client'

interface Message {
  id: string
  message: string
  response: string
  timestamp: string
}

interface ChatState {
  messages: Message[]
  loading: boolean
  sendMessage: (message: string) => Promise<void>
  loadHistory: () => Promise<void>
  clearHistory: () => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      messages: [],
      loading: false,

      sendMessage: async (message: string) => {
        set({ loading: true })
        try {
          const response = await apiClient.sendMessage(message)
          set((state) => ({
            messages: [response, ...state.messages],
            loading: false
          }))
        } catch (error) {
          console.error('Failed to send message:', error)
          set({ loading: false })
        }
      },

      loadHistory: async () => {
        set({ loading: true })
        try {
          const messages = await apiClient.getChatHistory()
          set({ messages, loading: false })
        } catch (error) {
          console.error('Failed to load history:', error)
          set({ loading: false })
        }
      },

      clearHistory: () => {
        set({ messages: [] })
      }
    }),
    {
      name: 'chat-storage',
      partialize: (state) => ({ messages: state.messages })
    }
  )
)
```

## Docker Compose Development

### Development Override

**Location**: `docker-compose.override.yml`

```yaml
version: '3.8'

services:
  # Backend (Flask)
  web-backend:
    build:
      context: ./web/backend
    container_name: project-ai-backend-dev
    ports:
      - "5000:5000"
    environment:
      FLASK_ENV: development
      FLASK_APP: app.py
      DATABASE_URL: postgresql://postgres:postgres@db:5432/legion_web
      REDIS_URL: redis://redis:6379/0
    volumes:
      - ./web/backend:/app
      - ./data:/app/data
      - ./src:/app/src  # Mount core modules
    command: flask run --host=0.0.0.0 --port=5000
    depends_on:
      - db
      - redis

  # Frontend (React + Vite)
  web-frontend:
    build:
      context: ./web/frontend
    container_name: project-ai-frontend-dev
    ports:
      - "3000:3000"
    environment:
      - CHOKIDAR_USEPOLLING=true
      - VITE_API_URL=http://localhost:5000/api
    volumes:
      - ./web/frontend:/app
      - /app/node_modules  # Anonymous volume for node_modules
    working_dir: /app
    command: sh -c "npm install && npm run dev -- --host 0.0.0.0 --port 3000"

  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: project-ai-db-dev
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: legion_web
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: project-ai-redis-dev
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Starting Development Environment

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

**Access**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000/api
- API Docs: http://localhost:5000/api/docs (if using Flask-RESTX)

## Production Deployment

### Environment Variables

**Backend** (`.env` [[.env]]):
```bash
# Flask
SECRET_KEY=<strong-random-secret>
FLASK_ENV=production

# Database
DATABASE_URL=postgresql://user:pass@host:5432/legion_web

# Redis
REDIS_URL=redis://host:6379/0

# OpenAI
OPENAI_API_KEY=sk-...

# HuggingFace
HUGGINGFACE_API_KEY=hf_...

# Security
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Logging
LOG_LEVEL=INFO
```

**Frontend** (`.env.production`):
```bash
VITE_API_URL=https://api.yourdomain.com
```

### Production Docker Compose

**Location**: `docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  backend:
    image: projectai/web-backend:latest
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    command: gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
    expose:
      - "8000"
    depends_on:
      - db
      - redis

  frontend:
    image: projectai/web-frontend:latest
    restart: unless-stopped
    expose:
      - "80"

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend

  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: legion_web
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  postgres_data:
  redis_data:
```

### Nginx Configuration

**Location**: `nginx.conf`

```nginx
http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # API proxy
        location /api/ {
            proxy_pass http://backend/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 300s;
        }

        # Frontend static files
        location / {
            proxy_pass http://frontend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # WebSocket support (if needed)
        location /ws/ {
            proxy_pass http://backend/ws/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

### Building Production Images

**Backend Dockerfile** (`web/backend/Dockerfile.prod`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY . .

# Copy core modules
COPY ../../src /app/src

# Create data directory
RUN mkdir -p /app/data

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "wsgi:app"]
```

**Frontend Dockerfile** (`web/frontend/Dockerfile.prod`):
```dockerfile
# Build stage
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Build and Push**:
```bash
# Build images
docker build -t projectai/web-backend:latest -f web/backend/Dockerfile.prod .
docker build -t projectai/web-frontend:latest -f web/frontend/Dockerfile.prod web/frontend

# Push to registry
docker push projectai/web-backend:latest
docker push projectai/web-frontend:latest
```

## Cloud Deployment Options

### Option 1: Vercel (Frontend) + Railway (Backend)

**Vercel (Frontend)**:
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd web/frontend
vercel --prod
```

**Railway (Backend)**:
1. Create Railway project
2. Connect GitHub repo
3. Add environment variables
4. Deploy from `web/backend` directory

### Option 2: Heroku (Full Stack)

**Backend** (`Procfile`):
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app
```

**Deploy**:
```bash
# Login
heroku login

# Create app
heroku create legion-mini-backend

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis
heroku addons:create heroku-redis:hobby-dev

# Deploy
git push heroku main
```

### Option 3: AWS (ECS + RDS)

See `web/DEPLOYMENT.md` for detailed AWS deployment guide.

## Performance Optimization

### Frontend Optimization

1. **Code Splitting**:
```typescript
// Lazy load routes
const Dashboard = lazy(() => import('@pages/Dashboard'))
const Chat = lazy(() => import('@pages/Chat'))

<Suspense fallback={<Loading />}>
  <Routes>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/chat" element={<Chat />} />
  </Routes>
</Suspense>
```

2. **Asset Optimization**:
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom'],
          'ui': ['@mui/material']
        }
      }
    }
  }
})
```

### Backend Optimization

1. **Database Connection Pooling**:
```python
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

2. **Caching with Redis**:
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': os.getenv('REDIS_URL')})

@app.route('/api/persona')
@cache.cached(timeout=300)
def get_persona():
    return jsonify(ai_service.get_persona_state())
```

3. **Gunicorn Workers**:
```bash
# Calculate workers: (2 x CPU cores) + 1
gunicorn -w 9 -b 0.0.0.0:8000 wsgi:app
```

## Monitoring and Logging

### Application Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Health Checks

```python
@app.route('/health')
def health():
    try:
        db.session.execute('SELECT 1')
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500
```

## Related Documentation

- `01_docker_architecture.md` - Containerization
- `07_container_security.md` - Security hardening
- `08_configuration_management.md` - Environment configuration
- `10_cicd_docker_pipeline.md` - Automated deployment

## References

- **Flask Documentation**: https://flask.palletsprojects.com/
- **React Documentation**: https://react.dev/
- **Vite Documentation**: https://vitejs.dev/
- **Docker Compose**: https://docs.docker.com/compose/
- **Gunicorn**: https://docs.gunicorn.org/
