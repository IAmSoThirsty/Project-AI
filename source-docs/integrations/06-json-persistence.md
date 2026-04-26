# JSON Data Persistence & File Storage

## Overview

Project-AI uses JSON-based file storage as its primary persistence mechanism for user data, AI state, and configuration. This integration provides a lightweight, human-readable, and version-control-friendly alternative to traditional databases for desktop applications.

## Architecture

### Storage Layout

```
data/
├── users.json                      # User profiles with bcrypt password hashes
├── ai_persona/
│   └── state.json                  # AIPersona mood, traits, interaction counts
├── memory/
│   └── knowledge.json              # MemoryExpansionSystem knowledge base
├── learning_requests/
│   ├── requests.json               # Learning request queue with approval status
│   └── black_vault.json            # SHA-256 hashes of denied content
├── command_override_config.json    # CommandOverride states and audit logs
├── location_history_{username}.json  # Encrypted location tracking
├── learning_paths_{username}.json    # Generated learning paths
├── emergency_contacts.json           # Emergency alert system contacts
├── sync_metadata.json                # Cloud sync timestamps
└── conversation_logs/                # Chat history by username
    └── {username}_conversations.json
```

### Core Persistence Pattern

All modules follow a consistent pattern:

```python
import json
import os
from pathlib import Path

class PersistentModule:
    def __init__(self, data_dir="data/module_name"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.data_dir / "state.json"
        self.state = {}
        self._load_state()
    
    def _load_state(self):
        """Load state from JSON file."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
    
    def _save_state(self):
        """Save state to JSON file."""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
```

## Security Considerations

### Path Traversal Protection

```python
# src/app/security/path_security.py

import os
from pathlib import Path

def safe_path_join(base_dir: str, filename: str) -> str:
    """Join paths safely, preventing directory traversal attacks."""
    base = Path(base_dir).resolve()
    target = (base / filename).resolve()
    
    # Ensure target is within base directory
    if not str(target).startswith(str(base)):
        raise ValueError(f"Path traversal attempt: {filename}")
    
    return str(target)

def validate_filename(filename: str):
    """Validate filename to prevent path traversal."""
    if ".." in filename or "/" in filename or "\\" in filename:
        raise ValueError(f"Invalid filename: {filename}")
    
    # Additional checks for dangerous characters
    if any(c in filename for c in ['<', '>', ':', '"', '|', '?', '*']):
        raise ValueError(f"Filename contains invalid characters: {filename}")

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing dangerous characters."""
    # Remove path separators
    safe_name = filename.replace("/", "_").replace("\\", "_")
    
    # Remove special characters
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in ('.', '_', '-'))
    
    # Limit length
    return safe_name[:255]
```

### Usage in User Manager

```python
# src/app/core/user_manager.py

from app.security.path_security import safe_path_join, validate_filename, sanitize_filename

class UserManager:
    def __init__(self, users_file="users.json", data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Validate filename to prevent path traversal
        validate_filename(users_file)
        self.users_file = safe_path_join(data_dir, users_file)
        
        self.users = {}
        self._load_users()
    
    def save_user_data(self, username: str, data: dict):
        """Save user-specific data with sanitized filename."""
        safe_username = sanitize_filename(username)
        filepath = safe_path_join(self.data_dir, f"user_{safe_username}.json")
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
```

## Implementation Examples

### 1. User Manager (Password Hashing)

```python
# src/app/core/user_manager.py (excerpt)

import json
import os
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto",
)

class UserManager:
    def __init__(self, users_file="users.json", data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.users_file = safe_path_join(data_dir, users_file)
        self.users = {}
        self._load_users()
    
    def _load_users(self):
        """Load users from JSON file."""
        if os.path.exists(self.users_file):
            with open(self.users_file) as f:
                self.users = json.load(f)
            
            # Migrate plaintext passwords to hashes
            self._migrate_plaintext_passwords()
    
    def _migrate_plaintext_passwords(self):
        """Convert plaintext passwords to bcrypt hashes."""
        migrated = False
        for username, user_data in self.users.items():
            if isinstance(user_data, dict) and "password" in user_data and "password_hash" not in user_data:
                plaintext = user_data.pop("password")
                user_data["password_hash"] = pwd_context.hash(plaintext)
                migrated = True
        
        if migrated:
            self.save_users()
    
    def save_users(self):
        """Persist users to JSON file."""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def create_user(self, username: str, password: str, **kwargs) -> bool:
        """Create new user with hashed password."""
        if username in self.users:
            return False
        
        self.users[username] = {
            "password_hash": pwd_context.hash(password),
            "created_at": datetime.now().isoformat(),
            **kwargs
        }
        
        self.save_users()
        return True
    
    def verify_password(self, username: str, password: str) -> bool:
        """Verify password against stored hash."""
        if username not in self.users:
            return False
        
        user_data = self.users[username]
        password_hash = user_data.get("password_hash")
        
        if not password_hash:
            return False
        
        return pwd_context.verify(password, password_hash)
```

### 2. AI Persona State Management

```python
# src/app/core/ai_systems.py (excerpt)

class AIPersona:
    def __init__(self, data_dir="data/ai_persona"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.state_file = os.path.join(data_dir, "state.json")
        
        # Personality traits (0-100 scale)
        self.traits = {
            "friendliness": 85,
            "professionalism": 70,
            "humor": 60,
            "empathy": 90,
            "creativity": 75,
            "assertiveness": 50,
            "optimism": 80,
            "curiosity": 95
        }
        
        # Mood state
        self.mood = "neutral"
        self.mood_intensity = 0.5
        
        # Interaction metrics
        self.interaction_count = 0
        self.last_interaction = None
        
        self._load_state()
    
    def _load_state(self):
        """Load persona state from JSON."""
        if os.path.exists(self.state_file):
            with open(self.state_file) as f:
                data = json.load(f)
                self.traits = data.get("traits", self.traits)
                self.mood = data.get("mood", "neutral")
                self.mood_intensity = data.get("mood_intensity", 0.5)
                self.interaction_count = data.get("interaction_count", 0)
                self.last_interaction = data.get("last_interaction")
    
    def _save_state(self):
        """Persist persona state to JSON."""
        data = {
            "traits": self.traits,
            "mood": self.mood,
            "mood_intensity": self.mood_intensity,
            "interaction_count": self.interaction_count,
            "last_interaction": self.last_interaction,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def adjust_trait(self, trait_name: str, delta: int):
        """Adjust personality trait and persist change."""
        if trait_name in self.traits:
            self.traits[trait_name] = max(0, min(100, self.traits[trait_name] + delta))
            self._save_state()
    
    def set_mood(self, mood: str, intensity: float = 0.5):
        """Update mood state and persist."""
        self.mood = mood
        self.mood_intensity = max(0.0, min(1.0, intensity))
        self.last_interaction = datetime.now().isoformat()
        self._save_state()
```

### 3. Memory System with Categories

```python
# src/app/core/ai_systems.py (excerpt)

class MemoryExpansionSystem:
    def __init__(self, data_dir="data/memory"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.knowledge_file = os.path.join(data_dir, "knowledge.json")
        
        self.knowledge_base = {
            "facts": [],
            "procedures": [],
            "preferences": [],
            "episodic": [],
            "semantic": [],
            "skills": []
        }
        
        self._load_knowledge()
    
    def _load_knowledge(self):
        """Load knowledge base from JSON."""
        if os.path.exists(self.knowledge_file):
            with open(self.knowledge_file) as f:
                self.knowledge_base = json.load(f)
    
    def _save_knowledge(self):
        """Persist knowledge base to JSON."""
        with open(self.knowledge_file, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
    
    def add_knowledge(self, category: str, knowledge_item: dict):
        """Add knowledge to specified category."""
        if category not in self.knowledge_base:
            raise ValueError(f"Invalid category: {category}")
        
        knowledge_item["timestamp"] = datetime.now().isoformat()
        knowledge_item["id"] = hashlib.sha256(
            f"{category}{knowledge_item}".encode()
        ).hexdigest()[:16]
        
        self.knowledge_base[category].append(knowledge_item)
        self._save_knowledge()
    
    def search_knowledge(self, query: str, category: str = None) -> list[dict]:
        """Search knowledge base for query terms."""
        results = []
        categories = [category] if category else self.knowledge_base.keys()
        
        query_lower = query.lower()
        
        for cat in categories:
            for item in self.knowledge_base[cat]:
                item_str = json.dumps(item).lower()
                if query_lower in item_str:
                    results.append({**item, "category": cat})
        
        return results
```

### 4. Learning Request Queue

```python
# src/app/core/ai_systems.py (excerpt)

class LearningRequestManager:
    def __init__(self, data_dir="data/learning_requests"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.requests_file = os.path.join(data_dir, "requests.json")
        self.vault_file = os.path.join(data_dir, "black_vault.json")
        
        self.pending_requests = []
        self.black_vault = set()
        
        self._load_state()
    
    def _load_state(self):
        """Load requests and black vault from JSON."""
        if os.path.exists(self.requests_file):
            with open(self.requests_file) as f:
                self.pending_requests = json.load(f)
        
        if os.path.exists(self.vault_file):
            with open(self.vault_file) as f:
                self.black_vault = set(json.load(f))
    
    def _save_state(self):
        """Persist requests and black vault to JSON."""
        with open(self.requests_file, 'w') as f:
            json.dump(self.pending_requests, f, indent=2)
        
        with open(self.vault_file, 'w') as f:
            json.dump(list(self.black_vault), f, indent=2)
    
    def submit_request(self, content: str, justification: str) -> str:
        """Submit learning request for human approval."""
        # Check Black Vault
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        if content_hash in self.black_vault:
            return "DENIED: Content in Black Vault"
        
        # Create request
        request = {
            "id": secrets.token_hex(8),
            "content": content,
            "justification": justification,
            "status": "pending",
            "submitted_at": datetime.now().isoformat(),
            "content_hash": content_hash
        }
        
        self.pending_requests.append(request)
        self._save_state()
        
        return request["id"]
    
    def approve_request(self, request_id: str):
        """Approve learning request."""
        for request in self.pending_requests:
            if request["id"] == request_id:
                request["status"] = "approved"
                request["approved_at"] = datetime.now().isoformat()
                self._save_state()
                return True
        return False
    
    def deny_request(self, request_id: str, add_to_vault: bool = False):
        """Deny learning request and optionally add to Black Vault."""
        for request in self.pending_requests:
            if request["id"] == request_id:
                request["status"] = "denied"
                request["denied_at"] = datetime.now().isoformat()
                
                if add_to_vault:
                    self.black_vault.add(request["content_hash"])
                
                self._save_state()
                return True
        return False
```

## Testing Strategies

### Isolated Test Data Directories

```python
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_data_dir():
    """Create temporary data directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

def test_user_manager_persistence(temp_data_dir):
    """Test user data persistence in isolated environment."""
    from app.core.user_manager import UserManager
    
    # Create manager with temp directory
    manager1 = UserManager(users_file="test_users.json", data_dir=temp_data_dir)
    
    # Create user
    assert manager1.create_user("test_user", "test_password")
    
    # Verify persistence by creating new manager instance
    manager2 = UserManager(users_file="test_users.json", data_dir=temp_data_dir)
    assert "test_user" in manager2.users
    assert manager2.verify_password("test_user", "test_password")

def test_ai_persona_state_persistence(temp_data_dir):
    """Test AI persona state persistence."""
    from app.core.ai_systems import AIPersona
    
    # Create persona
    persona1 = AIPersona(data_dir=temp_data_dir)
    persona1.set_mood("happy", 0.8)
    persona1.adjust_trait("friendliness", 10)
    
    # Load persona in new instance
    persona2 = AIPersona(data_dir=temp_data_dir)
    assert persona2.mood == "happy"
    assert persona2.mood_intensity == 0.8
    assert persona2.traits["friendliness"] == 95  # 85 + 10
```

## Migration Strategies

### Schema Evolution

```python
class VersionedPersistence:
    """Base class for versioned JSON persistence."""
    
    SCHEMA_VERSION = 2
    
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.data = {}
        self._load_with_migration()
    
    def _load_with_migration(self):
        """Load data and apply migrations if needed."""
        if os.path.exists(self.data_file):
            with open(self.data_file) as f:
                self.data = json.load(f)
            
            # Check version and migrate
            current_version = self.data.get("_schema_version", 1)
            
            if current_version < self.SCHEMA_VERSION:
                self._migrate(current_version, self.SCHEMA_VERSION)
                self.data["_schema_version"] = self.SCHEMA_VERSION
                self._save()
    
    def _migrate(self, from_version: int, to_version: int):
        """Apply migrations between versions."""
        if from_version == 1 and to_version == 2:
            # Migration logic
            self._migrate_v1_to_v2()
    
    def _migrate_v1_to_v2(self):
        """Migrate from version 1 to version 2."""
        # Example: Add new field
        for user in self.data.get("users", {}).values():
            if "created_at" not in user:
                user["created_at"] = datetime.now().isoformat()
    
    def _save(self):
        """Save data to JSON file."""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
```

## Performance Optimization

### Lazy Loading

```python
class LazyLoadedKnowledgeBase:
    """Knowledge base with lazy loading for large datasets."""
    
    def __init__(self, data_dir="data/memory"):
        self.data_dir = data_dir
        self.knowledge_file = os.path.join(data_dir, "knowledge.json")
        self._knowledge_cache = None
    
    @property
    def knowledge_base(self) -> dict:
        """Lazy load knowledge base on first access."""
        if self._knowledge_cache is None:
            self._load_knowledge()
        return self._knowledge_cache
    
    def _load_knowledge(self):
        """Load knowledge from file."""
        if os.path.exists(self.knowledge_file):
            with open(self.knowledge_file) as f:
                self._knowledge_cache = json.load(f)
        else:
            self._knowledge_cache = {"facts": [], "procedures": []}
```

### Incremental Writes

```python
import filelock

class ThreadSafeJSONStorage:
    """Thread-safe JSON storage with file locking."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.lock = filelock.FileLock(f"{filepath}.lock")
    
    def read(self) -> dict:
        """Read data with file lock."""
        with self.lock:
            if os.path.exists(self.filepath):
                with open(self.filepath) as f:
                    return json.load(f)
            return {}
    
    def write(self, data: dict):
        """Write data with file lock."""
        with self.lock:
            with open(self.filepath, 'w') as f:
                json.dump(data, f, indent=2)
```

## Backup and Recovery

### Automatic Backups

```python
import shutil
from datetime import datetime

def backup_data_directory(data_dir: str = "data", backup_dir: str = "backups"):
    """Create timestamped backup of data directory."""
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
    
    shutil.copytree(data_dir, backup_path)
    logger.info(f"Created backup: {backup_path}")
    
    return backup_path

def restore_from_backup(backup_path: str, data_dir: str = "data"):
    """Restore data from backup."""
    if not os.path.exists(backup_path):
        raise ValueError(f"Backup not found: {backup_path}")
    
    # Remove existing data
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
    
    # Restore from backup
    shutil.copytree(backup_path, data_dir)
    logger.info(f"Restored from backup: {backup_path}")
```

## References

- [User Manager Implementation](../../src/app/core/user_manager.py)
- [AI Systems Implementation](../../src/app/core/ai_systems.py)
- [Path Security Module](../../src/app/security/path_security.py)

## Related Documentation

- [Security Architecture](../architecture/security.md)
- [User Authentication](../features/authentication.md)
- [AI Persona System](../features/ai-persona.md)
