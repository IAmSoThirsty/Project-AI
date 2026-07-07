# Data & Storage Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        DESKTOP[Desktop App<br/>PyQt6]
        WEB[Web App<br/>React + Flask]
        API[REST API<br/>FastAPI]
    end

    subgraph "Data Access Layer"
        UM[UserManager<br/>User CRUD]
        PERSONA[AIPersona<br/>State Manager]
        MEMORY[MemorySystem<br/>Knowledge CRUD]
        LEARNING[Learning Manager<br/>Request CRUD]
        LOCATION[Location Tracker<br/>GPS CRUD]
    end

    subgraph "JSON Storage (Development/Desktop)"
        subgraph "User Data"
            USERS_JSON[users.json<br/>bcrypt hashes]
        end
        
        subgraph "AI State"
            PERSONA_JSON[ai_persona/state.json<br/>Traits + Mood]
            MOOD_HISTORY[ai_persona/mood_history.json<br/>Timestamped Moods]
        end
        
        subgraph "Knowledge Base"
            KB_JSON[memory/knowledge.json<br/>6 Categories]
            CONV_JSON[memory/conversations.json<br/>Chat History]
        end
        
        subgraph "Learning System"
            LEARNING_JSON[learning_requests/<br/>requests.json]
            BLACK_VAULT[learning_requests/<br/>black_vault.json]
        end
        
        subgraph "Security & Audit"
            AUDIT_JSON[audit_logs/<br/>audit.json]
            OVERRIDE_JSON[command_override_config.json<br/>Master Password]
        end
        
        subgraph "Location Data"
            LOCATION_JSON[location_history.json<br/>Fernet Encrypted]
        end
        
        subgraph "Configuration"
            CONFIG_JSON[config.json<br/>App Settings]
            POLICIES_YAML[policies/<br/>*.yaml]
        end
    end

    subgraph "PostgreSQL Storage (Production/Web)"
        subgraph "User Schema"
            USERS_TABLE[users<br/>id, username, password_hash, created_at]
            SESSIONS_TABLE[sessions<br/>id, user_id, token, expires_at]
        end
        
        subgraph "AI State Schema"
            PERSONA_TABLE[ai_persona<br/>user_id, traits JSON, mood, updated_at]
            MOOD_TABLE[mood_history<br/>id, user_id, mood, timestamp]
        end
        
        subgraph "Knowledge Schema"
            KB_TABLE[knowledge_base<br/>id, category, content, metadata JSON, created_at]
            CONV_TABLE[conversations<br/>id, user_id, messages JSON, timestamp]
        end
        
        subgraph "Learning Schema"
            LEARNING_TABLE[learning_requests<br/>id, user_id, topic, status, created_at]
            BV_TABLE[black_vault<br/>fingerprint, reason, timestamp]
        end
        
        subgraph "Audit Schema"
            AUDIT_TABLE[audit_logs<br/>id, event_type, user_id, details JSON, timestamp]
        end
    end

    subgraph "Vector Storage (RAG)"
        FAISS[FAISS Index<br/>Local Vector Store]
        PINECONE[Pinecone<br/>Cloud Vector DB]
        EMBEDDINGS[OpenAI Embeddings<br/>text-embedding-3-small]
    end

    subgraph "Object Storage"
        LOCAL_FILES[Local Filesystem<br/>data/ directory]
        S3[AWS S3<br/>Encrypted Backups]
        IMAGES[Generated Images<br/>PNG/JPEG]
        BACKUPS[Encrypted Backups<br/>Fernet Protected]
    end

    subgraph "Caching Layer"
        REDIS[Redis<br/>Session Cache]
        MEMCACHED[Memcached<br/>Query Results]
        APP_CACHE[In-Memory Cache<br/>LRU Cache]
    end

    subgraph "Data Encryption"
        FERNET[Fernet (AES-128)<br/>Symmetric Encryption]
        BCRYPT[bcrypt<br/>Password Hashing]
        SHA256[SHA-256<br/>Fingerprinting]
    end

    subgraph "Backup & Sync"
        DAILY_BACKUP[Daily Backup<br/>Temporal Workflow]
        CLOUD_SYNC[Cloud Sync<br/>S3/Google Drive]
        VERSION_CONTROL[Version Control<br/>Git LFS]
    end

    subgraph "Data Migration"
        JSON_TO_PG[JSON → PostgreSQL<br/>Migration Script]
        PG_TO_JSON[PostgreSQL → JSON<br/>Export Script]
        SCHEMA_MIGRATE[Schema Migrations<br/>Alembic]
    end

    %% Application to Data Access
    DESKTOP --> UM
    DESKTOP --> PERSONA
    DESKTOP --> MEMORY
    WEB --> UM
    WEB --> PERSONA
    API --> UM

    %% Data Access to JSON Storage
    UM --> USERS_JSON
    PERSONA --> PERSONA_JSON
    PERSONA --> MOOD_HISTORY
    MEMORY --> KB_JSON
    MEMORY --> CONV_JSON
    LEARNING --> LEARNING_JSON
    LEARNING --> BLACK_VAULT
    LOCATION --> LOCATION_JSON

    %% Data Access to PostgreSQL
    UM -.production.-> USERS_TABLE
    UM -.production.-> SESSIONS_TABLE
    PERSONA -.production.-> PERSONA_TABLE
    PERSONA -.production.-> MOOD_TABLE
    MEMORY -.production.-> KB_TABLE
    MEMORY -.production.-> CONV_TABLE
    LEARNING -.production.-> LEARNING_TABLE
    LEARNING -.production.-> BV_TABLE

    %% Vector Storage
    MEMORY --> EMBEDDINGS
    EMBEDDINGS --> FAISS
    EMBEDDINGS -.production.-> PINECONE

    %% Object Storage
    USERS_JSON --> LOCAL_FILES
    PERSONA_JSON --> LOCAL_FILES
    KB_JSON --> LOCAL_FILES
    IMAGES --> LOCAL_FILES
    BACKUPS --> LOCAL_FILES
    BACKUPS -.production.-> S3

    %% Caching
    SESSIONS_TABLE --> REDIS
    KB_TABLE --> MEMCACHED
    UM --> APP_CACHE

    %% Encryption
    LOCATION_JSON --> FERNET
    BACKUPS --> FERNET
    USERS_JSON --> BCRYPT
    BLACK_VAULT --> SHA256

    %% Backup & Sync
    LOCAL_FILES --> DAILY_BACKUP
    DAILY_BACKUP --> CLOUD_SYNC
    CLOUD_SYNC --> S3

    %% Migration
    USERS_JSON --> JSON_TO_PG
    JSON_TO_PG --> USERS_TABLE
    USERS_TABLE --> PG_TO_JSON
    PG_TO_JSON --> USERS_JSON
    USERS_TABLE --> SCHEMA_MIGRATE

    %% Configuration
    DESKTOP --> CONFIG_JSON
    DESKTOP --> POLICIES_YAML
    CONFIG_JSON --> LOCAL_FILES
    POLICIES_YAML --> LOCAL_FILES

    %% Styling
    classDef appClass fill:#1e3a8a,stroke:#3b82f6,stroke-width:2px,color:#fff
    classDef dalClass fill:#065f46,stroke:#10b981,stroke-width:2px,color:#fff
    classDef jsonClass fill:#ca8a04,stroke:#eab308,stroke-width:2px,color:#000
    classDef pgClass fill:#2563eb,stroke:#3b82f6,stroke-width:2px,color:#fff
    classDef vectorClass fill:#7c2d12,stroke:#f97316,stroke-width:2px,color:#fff
    classDef objectClass fill:#4c1d95,stroke:#a78bfa,stroke-width:2px,color:#fff
    classDef cacheClass fill:#0c4a6e,stroke:#0ea5e9,stroke-width:2px,color:#fff
    classDef cryptoClass fill:#dc2626,stroke:#ef4444,stroke-width:2px,color:#fff
    classDef backupClass fill:#581c87,stroke:#c084fc,stroke-width:2px,color:#fff
    classDef migrateClass fill:#991b1b,stroke:#f87171,stroke-width:2px,color:#fff

    class DESKTOP,WEB,API appClass
    class UM,PERSONA,MEMORY,LEARNING,LOCATION dalClass
    class USERS_JSON,PERSONA_JSON,MOOD_HISTORY,KB_JSON,CONV_JSON,LEARNING_JSON,BLACK_VAULT,AUDIT_JSON,OVERRIDE_JSON,LOCATION_JSON,CONFIG_JSON,POLICIES_YAML jsonClass
    class USERS_TABLE,SESSIONS_TABLE,PERSONA_TABLE,MOOD_TABLE,KB_TABLE,CONV_TABLE,LEARNING_TABLE,BV_TABLE,AUDIT_TABLE pgClass
    class FAISS,PINECONE,EMBEDDINGS vectorClass
    class LOCAL_FILES,S3,IMAGES,BACKUPS objectClass
    class REDIS,MEMCACHED,APP_CACHE cacheClass
    class FERNET,BCRYPT,SHA256 cryptoClass
    class DAILY_BACKUP,CLOUD_SYNC,VERSION_CONTROL backupClass
    class JSON_TO_PG,PG_TO_JSON,SCHEMA_MIGRATE migrateClass
```

## Data Models

### User Management

**JSON Schema (Development)**

```json
{
  "users": [
    {
      "username": "john_doe",
      "password_hash": "$2b$12$...",
      "created_at": "2025-01-15T10:30:00Z",
      "failed_attempts": 0,
      "locked_until": null,
      "last_login": "2025-01-15T10:30:00Z"
    }
  ]
}
```

**PostgreSQL Schema (Production)**

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    failed_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_locked_until ON users(locked_until);

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    token VARCHAR(512) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
```

### AI Persona State

**JSON Schema**

```json
{
  "traits": {
    "creativity": 75,
    "formality": 30,
    "humor": 60,
    "empathy": 80,
    "curiosity": 90,
    "caution": 40,
    "verbosity": 50,
    "proactivity": 70
  },
  "current_mood": "curious",
  "mood_history": [
    {
      "mood": "neutral",
      "timestamp": "2025-01-15T09:00:00Z"
    },
    {
      "mood": "curious",
      "timestamp": "2025-01-15T10:30:00Z"
    }
  ],
  "interaction_count": 42,
  "last_interaction": "2025-01-15T10:30:00Z"
}
```

**PostgreSQL Schema**

```sql
CREATE TABLE ai_persona (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    traits JSONB NOT NULL DEFAULT '{
        "creativity": 50,
        "formality": 50,
        "humor": 50,
        "empathy": 50,
        "curiosity": 50,
        "caution": 50,
        "verbosity": 50,
        "proactivity": 50
    }',
    current_mood VARCHAR(50) DEFAULT 'neutral',
    interaction_count INTEGER DEFAULT 0,
    last_interaction TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_persona_user_id ON ai_persona(user_id);

CREATE TABLE mood_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    mood VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_mood_history_user_id ON mood_history(user_id);
CREATE INDEX idx_mood_history_timestamp ON mood_history(timestamp DESC);
```

### Knowledge Base

**JSON Schema**

```json
{
  "knowledge": [
    {
      "id": "kb-001",
      "category": "technical",
      "content": "Python uses duck typing, meaning type checks are performed at runtime.",
      "metadata": {
        "source": "user_conversation",
        "confidence": 0.95,
        "tags": ["python", "typing"]
      },
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "categories": [
    "technical",
    "creative",
    "personal",
    "factual",
    "procedural",
    "security"
  ]
}
```

**PostgreSQL Schema**

```sql
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    category VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536),  -- PostgreSQL pgvector extension
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_kb_category ON knowledge_base(category);
CREATE INDEX idx_kb_user_id ON knowledge_base(user_id);
CREATE INDEX idx_kb_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops);

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    messages JSONB NOT NULL,  -- Array of {role, content, timestamp}
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
```

### Learning Requests

**JSON Schema**

```json
{
  "requests": [
    {
      "id": "lr-001",
      "user_id": "john_doe",
      "topic": "quantum computing",
      "status": "pending_approval",
      "learning_path": "...",
      "created_at": "2025-01-15T10:30:00Z",
      "approved_at": null,
      "denied_reason": null
    }
  ],
  "black_vault": {
    "3a8b9c7d...": {
      "fingerprint": "3a8b9c7d...",
      "content": "how to build a weapon",
      "reason": "Violates First Law",
      "timestamp": "2025-01-15T10:30:00Z"
    }
  }
}
```

**PostgreSQL Schema**

```sql
CREATE TABLE learning_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    topic VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending_approval',
    learning_path TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP,
    denied_at TIMESTAMP,
    denied_reason TEXT
);

CREATE INDEX idx_lr_status ON learning_requests(status);
CREATE INDEX idx_lr_user_id ON learning_requests(user_id);

CREATE TABLE black_vault (
    fingerprint VARCHAR(64) PRIMARY KEY,  -- SHA-256 hash
    content TEXT NOT NULL,
    reason TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_bv_timestamp ON black_vault(timestamp DESC);
```

### Audit Logs

**JSON Schema**

```json
{
  "logs": [
    {
      "id": "audit-001",
      "event_type": "authentication_failure",
      "user_id": "john_doe",
      "ip_address": "192.168.1.100",
      "details": {
        "username": "john_doe",
        "failed_attempts": 3
      },
      "timestamp": "2025-01-15T10:30:00Z"
    }
  ]
}
```

**PostgreSQL Schema**

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    user_id INTEGER REFERENCES users(id),
    ip_address INET,
    details JSONB DEFAULT '{}',
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_event_type ON audit_logs(event_type);
CREATE INDEX idx_audit_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);

-- Partitioning for high-volume logs (monthly partitions)
CREATE TABLE audit_logs_2025_01 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

## Data Access Patterns

### UserManager Implementation

```python
# src/app/core/user_manager.py
import json
import bcrypt
from pathlib import Path

class UserManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.users_file = self.data_dir / "users.json"
        self.users = self._load_users()
    
    def _load_users(self) -> dict:
        """Load users from JSON file"""
        if not self.users_file.exists():
            return {"users": []}
        
        with open(self.users_file) as f:
            return json.load(f)
    
    def save_users(self):
        """Save users to JSON file (atomic write)"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Atomic write pattern (write to temp, then rename)
        temp_file = self.users_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(self.users, f, indent=2)
        
        temp_file.replace(self.users_file)
    
    def create_user(self, username: str, password: str) -> bool:
        """Create new user with bcrypt password hash"""
        if self.get_user(username):
            return False
        
        password_hash = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt(rounds=12)
        ).decode()
        
        self.users["users"].append({
            "username": username,
            "password_hash": password_hash,
            "created_at": datetime.now().isoformat(),
            "failed_attempts": 0,
            "locked_until": None,
            "last_login": None
        })
        
        self.save_users()
        return True
```

### AIPersona State Management

```python
# src/app/core/ai_systems.py
class AIPersona:
    def __init__(self, data_dir: str = "data/ai_persona"):
        self.data_dir = Path(data_dir)
        self.state_file = self.data_dir / "state.json"
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        """Load persona state from JSON"""
        if not self.state_file.exists():
            return self._default_state()
        
        with open(self.state_file) as f:
            return json.load(f)
    
    def _save_state(self):
        """Persist state to JSON (atomic write)"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        temp_file = self.state_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(self.state, f, indent=2)
        
        temp_file.replace(self.state_file)
    
    def update_trait(self, trait: str, value: int):
        """Update personality trait (0-100)"""
        if trait not in self.state["traits"]:
            raise ValueError(f"Unknown trait: {trait}")
        
        self.state["traits"][trait] = max(0, min(100, value))
        self._save_state()
    
    def set_mood(self, mood: str):
        """Update current mood and log to history"""
        self.state["current_mood"] = mood
        self.state["mood_history"].append({
            "mood": mood,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep last 100 mood changes
        if len(self.state["mood_history"]) > 100:
            self.state["mood_history"] = self.state["mood_history"][-100:]
        
        self._save_state()
```

### Vector Storage (RAG)

```python
# src/app/core/rag_system.py
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

class RAGSystem:
    def __init__(self, data_dir: str = "data/vector_store"):
        self.data_dir = Path(data_dir)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        
        # Load existing vector store or create new
        if (self.data_dir / "index.faiss").exists():
            self.vector_store = FAISS.load_local(
                str(self.data_dir),
                self.embeddings
            )
        else:
            self.vector_store = FAISS.from_texts(
                ["Initial document"],
                self.embeddings
            )
    
    def add_knowledge(self, content: str, metadata: dict):
        """Add document to vector store"""
        self.vector_store.add_texts([content], metadatas=[metadata])
        self.vector_store.save_local(str(self.data_dir))
    
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Retrieve relevant documents"""
        results = self.vector_store.similarity_search_with_score(
            query,
            k=top_k
        )
        
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            }
            for doc, score in results
        ]
```

## Data Migration

### JSON to PostgreSQL

```python
# scripts/migrate_json_to_postgres.py
import json
import psycopg2
from pathlib import Path

def migrate_users():
    """Migrate users from JSON to PostgreSQL"""
    # Load JSON data
    with open("data/users.json") as f:
        data = json.load(f)
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host="localhost",
        database="project_ai",
        user="postgres",
        password="postgres"
    )
    
    cursor = conn.cursor()
    
    # Insert users
    for user in data["users"]:
        cursor.execute("""
            INSERT INTO users (username, password_hash, created_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        """, (
            user["username"],
            user["password_hash"],
            user["created_at"]
        ))
    
    conn.commit()
    cursor.close()
    conn.close()

def migrate_knowledge():
    """Migrate knowledge base with embeddings"""
    with open("data/memory/knowledge.json") as f:
        data = json.load(f)
    
    conn = psycopg2.connect(...)
    cursor = conn.cursor()
    
    embeddings = OpenAIEmbeddings()
    
    for item in data["knowledge"]:
        # Generate embedding
        embedding = embeddings.embed_query(item["content"])
        
        cursor.execute("""
            INSERT INTO knowledge_base (id, category, content, metadata, embedding)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            item["id"],
            item["category"],
            item["content"],
            json.dumps(item["metadata"]),
            embedding
        ))
    
    conn.commit()
```

### Schema Migrations (Alembic)

```python
# alembic/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    """Initial schema creation"""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('failed_attempts', sa.Integer, default=0),
        sa.Column('locked_until', sa.TIMESTAMP),
        sa.Column('last_login', sa.TIMESTAMP),
        sa.Column('is_active', sa.Boolean, default=True)
    )
    
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_locked_until', 'users', ['locked_until'])

def downgrade():
    """Rollback schema"""
    op.drop_index('idx_users_locked_until')
    op.drop_index('idx_users_username')
    op.drop_table('users')
```

## Backup Strategy

### Daily Encrypted Backups

```python
# src/app/core/backup_system.py
from cryptography.fernet import Fernet
import tarfile
import shutil

class BackupSystem:
    def __init__(self, fernet_key: bytes):
        self.fernet = Fernet(fernet_key)
    
    def create_backup(self) -> Path:
        """Create encrypted backup of all data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(f"backups/backup_{timestamp}")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all JSON files
        shutil.copytree("data", backup_dir / "data")
        
        # Create tar archive
        archive_path = Path(f"backups/backup_{timestamp}.tar.gz")
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(backup_dir, arcname=backup_dir.name)
        
        # Encrypt archive
        with open(archive_path, "rb") as f:
            encrypted_data = self.fernet.encrypt(f.read())
        
        encrypted_path = archive_path.with_suffix('.tar.gz.enc')
        with open(encrypted_path, "wb") as f:
            f.write(encrypted_data)
        
        # Clean up unencrypted files
        archive_path.unlink()
        shutil.rmtree(backup_dir)
        
        return encrypted_path
    
    def restore_backup(self, encrypted_path: Path):
        """Decrypt and restore backup"""
        with open(encrypted_path, "rb") as f:
            encrypted_data = f.read()
        
        decrypted_data = self.fernet.decrypt(encrypted_data)
        
        # Write decrypted archive
        archive_path = encrypted_path.with_suffix('')
        with open(archive_path, "wb") as f:
            f.write(decrypted_data)
        
        # Extract archive
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall("data_restored")
        
        archive_path.unlink()
```

## Performance Optimization

### Caching Strategy

```python
# In-memory LRU cache
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_knowledge_by_id(knowledge_id: str) -> dict:
    """Cached knowledge retrieval"""
    with open("data/memory/knowledge.json") as f:
        data = json.load(f)
    
    for item in data["knowledge"]:
        if item["id"] == knowledge_id:
            return item
    
    return None

# Redis cache for sessions
import redis

redis_client = redis.Redis(host='localhost', port=6379)

def cache_session(session_id: str, data: dict, ttl: int = 3600):
    """Cache session in Redis"""
    redis_client.setex(
        f"session:{session_id}",
        ttl,
        json.dumps(data)
    )

def get_cached_session(session_id: str) -> dict:
    """Retrieve session from Redis"""
    data = redis_client.get(f"session:{session_id}")
    return json.loads(data) if data else None
```
