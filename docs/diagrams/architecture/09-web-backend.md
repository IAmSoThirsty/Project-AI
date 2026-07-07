# Web Backend Architecture

```mermaid
graph TB
    subgraph "Frontend (React + Vite)"
        REACT[React App<br/>Port 3000]
        ROUTER[React Router<br/>Page Navigation]
        ZUSTAND[Zustand Store<br/>State Management]
        AXIOS[Axios Client<br/>HTTP Requests]
    end

    subgraph "Backend API (Flask)"
        FLASK[Flask App<br/>Port 5000]
        
        subgraph "Route Handlers"
            AUTH_ROUTE[/api/auth<br/>Login/Register]
            USER_ROUTE[/api/users<br/>User CRUD]
            PERSONA_ROUTE[/api/persona<br/>AI Config]
            CHAT_ROUTE[/api/chat<br/>Conversation]
            LEARNING_ROUTE[/api/learning<br/>Requests]
            IMAGE_ROUTE[/api/images<br/>Generation]
        end
        
        subgraph "Middleware"
            CORS[CORS Handler<br/>Cross-Origin]
            AUTH_MW[Auth Middleware<br/>JWT Validation]
            RATE_MW[Rate Limiter<br/>Request Throttle]
            LOGGING_MW[Request Logger<br/>Audit Trail]
        end
        
        BLUEPRINTS[Flask Blueprints<br/>Route Organization]
    end

    subgraph "Core Integration Layer"
        API_ADAPTER[API Adapter<br/>Desktop → Web Bridge]
        
        CORE_WRAPPER[Core Systems Wrapper<br/>Async → Sync]
        
        subgraph "Core Systems"
            UM_CORE[UserManager]
            PERSONA_CORE[AIPersona]
            MEMORY_CORE[MemorySystem]
            INTEL_CORE[Intelligence Engine]
            IMG_CORE[Image Generator]
        end
    end

    subgraph "Database Layer (PostgreSQL)"
        PG_CONN[PostgreSQL Connection<br/>psycopg2/SQLAlchemy]
        
        USERS_DB[users table]
        SESSIONS_DB[sessions table]
        PERSONA_DB[ai_persona table]
        KB_DB[knowledge_base table]
        AUDIT_DB[audit_logs table]
    end

    subgraph "Authentication & Sessions"
        JWT_AUTH[JWT Handler<br/>Token Generation]
        SESSION_MGR[Session Manager<br/>Redis Cache]
        BCRYPT_SVC[bcrypt Service<br/>Password Hashing]
    end

    subgraph "External Services"
        OPENAI[OpenAI API<br/>GPT-4 + DALL-E]
        REDIS[Redis<br/>Session Store]
        S3[AWS S3<br/>Image Storage]
        EMAIL[SMTP Server<br/>Email Alerts]
    end

    subgraph "WebSocket Layer (Socket.IO)"
        SOCKETIO[Socket.IO Server<br/>Real-time Events]
        CHAT_NS[/chat namespace<br/>Live Chat]
        PERSONA_NS[/persona namespace<br/>Mood Updates]
        NOTIFY_NS[/notifications<br/>Alerts]
    end

    subgraph "API Documentation"
        SWAGGER[Swagger UI<br/>/api/docs]
        OPENAPI[OpenAPI Spec<br/>swagger.json]
    end

    %% Frontend to Backend
    REACT --> ROUTER
    ROUTER --> ZUSTAND
    ZUSTAND --> AXIOS
    AXIOS --> FLASK

    %% Flask Routing
    FLASK --> BLUEPRINTS
    BLUEPRINTS --> AUTH_ROUTE
    BLUEPRINTS --> USER_ROUTE
    BLUEPRINTS --> PERSONA_ROUTE
    BLUEPRINTS --> CHAT_ROUTE
    BLUEPRINTS --> LEARNING_ROUTE
    BLUEPRINTS --> IMAGE_ROUTE

    %% Middleware Chain
    AXIOS --> CORS
    CORS --> AUTH_MW
    AUTH_MW --> RATE_MW
    RATE_MW --> LOGGING_MW
    LOGGING_MW --> BLUEPRINTS

    %% Routes to Core Integration
    AUTH_ROUTE --> API_ADAPTER
    USER_ROUTE --> API_ADAPTER
    PERSONA_ROUTE --> API_ADAPTER
    CHAT_ROUTE --> API_ADAPTER
    LEARNING_ROUTE --> API_ADAPTER
    IMAGE_ROUTE --> API_ADAPTER

    %% API Adapter to Core Systems
    API_ADAPTER --> CORE_WRAPPER
    CORE_WRAPPER --> UM_CORE
    CORE_WRAPPER --> PERSONA_CORE
    CORE_WRAPPER --> MEMORY_CORE
    CORE_WRAPPER --> INTEL_CORE
    CORE_WRAPPER --> IMG_CORE

    %% Core to Database
    UM_CORE --> PG_CONN
    PERSONA_CORE --> PG_CONN
    MEMORY_CORE --> PG_CONN
    PG_CONN --> USERS_DB
    PG_CONN --> SESSIONS_DB
    PG_CONN --> PERSONA_DB
    PG_CONN --> KB_DB
    PG_CONN --> AUDIT_DB

    %% Authentication Flow
    AUTH_ROUTE --> JWT_AUTH
    AUTH_ROUTE --> BCRYPT_SVC
    JWT_AUTH --> SESSION_MGR
    SESSION_MGR --> REDIS

    %% External Services
    INTEL_CORE --> OPENAI
    IMG_CORE --> OPENAI
    IMG_CORE --> S3
    AUTH_ROUTE --> EMAIL

    %% WebSocket Integration
    REACT --> SOCKETIO
    SOCKETIO --> CHAT_NS
    SOCKETIO --> PERSONA_NS
    SOCKETIO --> NOTIFY_NS
    CHAT_NS --> INTEL_CORE
    PERSONA_NS --> PERSONA_CORE

    %% API Documentation
    FLASK --> SWAGGER
    SWAGGER --> OPENAPI

    %% Styling
    classDef frontendClass fill:#00ff00,stroke:#00ffff,stroke-width:2px,color:#000
    classDef backendClass fill:#1e3a8a,stroke:#3b82f6,stroke-width:3px,color:#fff
    classDef coreClass fill:#7c2d12,stroke:#f97316,stroke-width:2px,color:#fff
    classDef dbClass fill:#2563eb,stroke:#3b82f6,stroke-width:2px,color:#fff
    classDef authClass fill:#dc2626,stroke:#ef4444,stroke-width:2px,color:#fff
    classDef externalClass fill:#4c1d95,stroke:#a78bfa,stroke-width:2px,color:#fff
    classDef wsClass fill:#065f46,stroke:#10b981,stroke-width:2px,color:#fff
    classDef docsClass fill:#ca8a04,stroke:#eab308,stroke-width:2px,color:#000

    class REACT,ROUTER,ZUSTAND,AXIOS frontendClass
    class FLASK,AUTH_ROUTE,USER_ROUTE,PERSONA_ROUTE,CHAT_ROUTE,LEARNING_ROUTE,IMAGE_ROUTE,CORS,AUTH_MW,RATE_MW,LOGGING_MW,BLUEPRINTS backendClass
    class API_ADAPTER,CORE_WRAPPER,UM_CORE,PERSONA_CORE,MEMORY_CORE,INTEL_CORE,IMG_CORE coreClass
    class PG_CONN,USERS_DB,SESSIONS_DB,PERSONA_DB,KB_DB,AUDIT_DB dbClass
    class JWT_AUTH,SESSION_MGR,BCRYPT_SVC authClass
    class OPENAI,REDIS,S3,EMAIL externalClass
    class SOCKETIO,CHAT_NS,PERSONA_NS,NOTIFY_NS wsClass
    class SWAGGER,OPENAPI docsClass
```

## Web Backend Implementation

### Flask Application Setup

**Main Application** (`web/backend/app.py`)

```python
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
import logging

app = Flask(__name__)
app.config.from_object('config.Config')

# CORS configuration
CORS(app, origins=[
    "http://localhost:3000",  # Development
    "https://app.project-ai.com"  # Production
])

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

# Socket.IO for real-time features
socketio = SocketIO(app, cors_allowed_origins="*")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Register blueprints
from routes.auth import auth_bp
from routes.users import users_bp
from routes.persona import persona_bp
from routes.chat import chat_bp
from routes.learning import learning_bp
from routes.images import images_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(persona_bp, url_prefix='/api/persona')
app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(learning_bp, url_prefix='/api/learning')
app.register_blueprint(images_bp, url_prefix='/api/images')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

### Authentication Routes

**JWT-Based Authentication** (`web/backend/routes/auth.py`)

```python
from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
import bcrypt
from datetime import datetime, timedelta
from models import User, Session
from database import db

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = os.getenv('JWT_SECRET_KEY')

def token_required(f):
    """Decorator for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix
            token = token.split(' ')[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per hour")
def register():
    """Create new user account"""
    data = request.get_json()
    
    # Validate input
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    # Hash password
    password_hash = bcrypt.hashpw(
        data['password'].encode(),
        bcrypt.gensalt(rounds=12)
    ).decode()
    
    # Create user
    user = User(
        username=data['username'],
        password_hash=password_hash
    )
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User created successfully',
        'user_id': user.id
    }), 201

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Authenticate user and generate JWT token"""
    data = request.get_json()
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check account lockout
    if user.locked_until and user.locked_until > datetime.now():
        return jsonify({
            'error': 'Account locked',
            'locked_until': user.locked_until.isoformat()
        }), 403
    
    # Verify password
    if not bcrypt.checkpw(data['password'].encode(), user.password_hash.encode()):
        user.failed_attempts += 1
        
        # Lock account after 5 failed attempts
        if user.failed_attempts >= 5:
            user.locked_until = datetime.now() + timedelta(minutes=30)
        
        db.session.commit()
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Reset failed attempts
    user.failed_attempts = 0
    user.last_login = datetime.now()
    db.session.commit()
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, SECRET_KEY, algorithm='HS256')
    
    # Create session
    session = Session(
        user_id=user.id,
        token=token,
        expires_at=datetime.now() + timedelta(hours=24)
    )
    db.session.add(session)
    db.session.commit()
    
    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Invalidate session"""
    token = request.headers.get('Authorization').split(' ')[1]
    
    session = Session.query.filter_by(token=token).first()
    if session:
        db.session.delete(session)
        db.session.commit()
    
    return jsonify({'message': 'Logged out successfully'}), 200
```

### Chat Routes (WebSocket Integration)

**Real-Time Chat** (`web/backend/routes/chat.py`)

```python
from flask import Blueprint, request, jsonify
from flask_socketio import emit, join_room, leave_room
from routes.auth import token_required
from core_integration import IntelligenceEngineAdapter

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/history', methods=['GET'])
@token_required
def get_chat_history(current_user):
    """Retrieve conversation history"""
    conversations = Conversation.query.filter_by(
        user_id=current_user.id
    ).order_by(Conversation.created_at.desc()).limit(50).all()
    
    return jsonify({
        'conversations': [
            {
                'id': conv.id,
                'messages': conv.messages,
                'created_at': conv.created_at.isoformat()
            }
            for conv in conversations
        ]
    }), 200

# Socket.IO events
from app import socketio

@socketio.on('connect', namespace='/chat')
def handle_connect():
    """Client connected to chat namespace"""
    emit('connected', {'message': 'Connected to chat server'})

@socketio.on('join', namespace='/chat')
def handle_join(data):
    """Join user-specific chat room"""
    user_id = data['user_id']
    join_room(f'user_{user_id}')
    emit('joined', {'room': f'user_{user_id}'})

@socketio.on('send_message', namespace='/chat')
def handle_message(data):
    """Process user message and stream AI response"""
    user_id = data['user_id']
    message = data['message']
    
    # Call intelligence engine
    intel_engine = IntelligenceEngineAdapter()
    
    # Stream response in chunks
    for chunk in intel_engine.chat_stream(message):
        emit('message_chunk', {
            'content': chunk,
            'timestamp': datetime.now().isoformat()
        }, room=f'user_{user_id}')
    
    # Send completion signal
    emit('message_complete', {
        'message_id': str(uuid.uuid4())
    }, room=f'user_{user_id}')
```

### Persona Routes

**AI Configuration** (`web/backend/routes/persona.py`)

```python
from flask import Blueprint, request, jsonify
from routes.auth import token_required
from core_integration import AIPersonaAdapter

persona_bp = Blueprint('persona', __name__)

@persona_bp.route('/', methods=['GET'])
@token_required
def get_persona(current_user):
    """Get current AI persona state"""
    persona = AIPersonaAdapter(user_id=current_user.id)
    
    return jsonify({
        'traits': persona.get_traits(),
        'current_mood': persona.get_current_mood(),
        'mood_history': persona.get_mood_history(limit=20),
        'interaction_count': persona.get_interaction_count()
    }), 200

@persona_bp.route('/traits', methods=['PUT'])
@token_required
def update_traits(current_user):
    """Update personality traits"""
    data = request.get_json()
    
    persona = AIPersonaAdapter(user_id=current_user.id)
    
    for trait, value in data.items():
        if trait in persona.valid_traits:
            persona.update_trait(trait, value)
    
    return jsonify({
        'message': 'Traits updated',
        'traits': persona.get_traits()
    }), 200

@persona_bp.route('/mood', methods=['POST'])
@token_required
def set_mood(current_user):
    """Manually set AI mood"""
    data = request.get_json()
    
    persona = AIPersonaAdapter(user_id=current_user.id)
    persona.set_mood(data['mood'])
    
    # Broadcast mood change via WebSocket
    from app import socketio
    socketio.emit('mood_changed', {
        'user_id': current_user.id,
        'mood': data['mood']
    }, namespace='/persona', room=f'user_{current_user.id}')
    
    return jsonify({
        'message': 'Mood updated',
        'current_mood': data['mood']
    }), 200
```

### Core Integration Adapter

**Bridge Desktop Core to Web API** (`web/backend/core_integration.py`)

```python
import sys
sys.path.append('../../src')  # Add desktop source to path

from app.core.ai_systems import AIPersona, MemoryExpansionSystem
from app.core.intelligence_engine import IntelligenceEngine
from app.core.image_generator import ImageGenerator

class AIPersonaAdapter:
    """Adapter to use desktop AIPersona in web context"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        # Use user-specific data directory
        self.persona = AIPersona(data_dir=f'data/users/{user_id}/persona')
    
    def get_traits(self) -> dict:
        return self.persona.traits
    
    def update_trait(self, trait: str, value: int):
        self.persona.update_trait(trait, value)
    
    def get_current_mood(self) -> str:
        return self.persona.get_current_mood()
    
    def set_mood(self, mood: str):
        self.persona.set_mood(mood)
    
    def get_mood_history(self, limit: int = 20) -> list:
        return self.persona.state["mood_history"][-limit:]
    
    def get_interaction_count(self) -> int:
        return self.persona.state.get("interaction_count", 0)

class IntelligenceEngineAdapter:
    """Adapter for IntelligenceEngine with streaming"""
    
    def __init__(self):
        self.engine = IntelligenceEngine()
    
    def chat(self, message: str) -> str:
        """Non-streaming chat"""
        return self.engine.chat(message)
    
    def chat_stream(self, message: str):
        """Streaming chat (generator)"""
        response = self.engine.chat(message)
        
        # Simulate streaming by yielding chunks
        chunk_size = 10
        for i in range(0, len(response), chunk_size):
            yield response[i:i+chunk_size]

class ImageGeneratorAdapter:
    """Adapter for ImageGenerator"""
    
    def __init__(self):
        self.generator = ImageGenerator()
    
    async def generate(self, prompt: str, style: str = "photorealistic") -> dict:
        """Async wrapper for image generation"""
        image_path, metadata = self.generator.generate(
            prompt=prompt,
            style=style
        )
        
        # Upload to S3
        s3_url = self._upload_to_s3(image_path)
        
        return {
            'image_url': s3_url,
            'metadata': metadata
        }
    
    def _upload_to_s3(self, local_path: str) -> str:
        """Upload image to S3 and return URL"""
        import boto3
        
        s3 = boto3.client('s3')
        bucket = os.getenv('S3_BUCKET')
        key = f'images/{uuid.uuid4()}.png'
        
        s3.upload_file(local_path, bucket, key)
        
        return f'https://{bucket}.s3.amazonaws.com/{key}'
```

### Database Models (SQLAlchemy)

**ORM Models** (`web/backend/models.py`)

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    failed_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    sessions = db.relationship('Session', backref='user', lazy=True)
    persona = db.relationship('AIPersona', backref='user', uselist=False)

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(512), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AIPersona(db.Model):
    __tablename__ = 'ai_persona'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    traits = db.Column(db.JSON, nullable=False)
    current_mood = db.Column(db.String(50), default='neutral')
    interaction_count = db.Column(db.Integer, default=0)
    last_interaction = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    messages = db.Column(db.JSON, nullable=False)  # Array of {role, content, timestamp}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Frontend React Integration

**API Client** (`web/frontend/src/services/api.js`)

```javascript
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance with defaults
const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add JWT token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth API
export const authAPI = {
  register: (username, password) =>
    apiClient.post('/auth/register', { username, password }),
  
  login: (username, password) =>
    apiClient.post('/auth/login', { username, password }),
  
  logout: () =>
    apiClient.post('/auth/logout')
};

// Persona API
export const personaAPI = {
  getPersona: () =>
    apiClient.get('/persona'),
  
  updateTraits: (traits) =>
    apiClient.put('/persona/traits', traits),
  
  setMood: (mood) =>
    apiClient.post('/persona/mood', { mood })
};

// Chat API
export const chatAPI = {
  getHistory: () =>
    apiClient.get('/chat/history')
};
```

**WebSocket Client** (`web/frontend/src/services/socket.js`)

```javascript
import { io } from 'socket.io-client';

const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'http://localhost:5000';

class SocketService {
  constructor() {
    this.socket = null;
  }
  
  connect(userId) {
    this.socket = io(`${SOCKET_URL}/chat`, {
      auth: {
        token: localStorage.getItem('token')
      }
    });
    
    this.socket.on('connect', () => {
      console.log('Connected to chat server');
      this.socket.emit('join', { user_id: userId });
    });
    
    return this.socket;
  }
  
  sendMessage(userId, message) {
    this.socket.emit('send_message', {
      user_id: userId,
      message: message
    });
  }
  
  onMessageChunk(callback) {
    this.socket.on('message_chunk', callback);
  }
  
  onMessageComplete(callback) {
    this.socket.on('message_complete', callback);
  }
  
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
    }
  }
}

export default new SocketService();
```

## Deployment

### Docker Compose (Full Stack)

```yaml
# web/docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: project_ai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/project_ai
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
      - ../../src:/app/desktop_core  # Mount desktop core

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:5000/api
      - REACT_APP_SOCKET_URL=http://localhost:5000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
```
