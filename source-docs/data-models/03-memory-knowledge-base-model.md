# Memory & Knowledge Base Data Model

**Module**: `src/app/core/ai_systems.py` [[src/app/core/ai_systems.py]] (MemoryExpansionSystem class)  
**Storage**: `data/memory/knowledge.json`  
**Persistence**: JSON with atomic writes  
**Schema Version**: 1.0

---

## Overview

The Memory Expansion System provides structured knowledge storage with 6 predefined categories and conversation history tracking. It enables the AI to accumulate knowledge over time and retrieve relevant context during interactions.

### Key Features

- 6 knowledge categories: technical, personal, general, context, preferences, facts
- Conversation history logging with timestamps
- Category-based knowledge organization
- Atomic persistence with thread safety
- Search and retrieval by category
- Duplicate detection via content hashing

---

## Schema Structure

### Knowledge Base Document

```json
{
  "knowledge": {
    "technical": [
      {
        "id": "tech_001",
        "content": "Python uses duck typing and dynamic typing",
        "timestamp": "2024-01-15T10:30:00Z",
        "source": "user_conversation",
        "confidence": 0.95,
        "references": ["conversation_142", "conversation_189"]
      }
    ],
    "personal": [
      {
        "id": "pers_001",
        "content": "User prefers dark mode UI",
        "timestamp": "2024-01-10T08:15:00Z",
        "source": "preferences_panel",
        "confidence": 1.0,
        "references": []
      }
    ],
    "general": [],
    "context": [],
    "preferences": [],
    "facts": []
  },
  "conversations": [
    {
      "id": "conv_001",
      "timestamp": "2024-01-15T10:30:00Z",
      "role": "user",
      "message": "How does Python handle types?",
      "context": {"session_id": "abc123", "mood": "curious"}
    },
    {
      "id": "conv_002",
      "timestamp": "2024-01-15T10:30:15Z",
      "role": "assistant",
      "message": "Python uses duck typing...",
      "context": {"response_time_ms": 450}
    }
  ],
  "metadata": {
    "total_conversations": 1523,
    "total_knowledge_items": 87,
    "last_updated": "2024-01-20T14:35:22Z",
    "schema_version": "1.0"
  }
}
```

---

## Knowledge Categories

### 1. Technical Knowledge

**Purpose**: Programming concepts, system architecture, API documentation

**Examples**:
- Language syntax rules
- Framework capabilities
- Algorithm complexity
- Security best practices

**Schema**:
```json
{
  "id": "tech_042",
  "content": "Fernet uses AES-128-CBC with HMAC-SHA256 for authenticated encryption",
  "timestamp": "2024-01-18T12:00:00Z",
  "source": "documentation_review",
  "confidence": 1.0,
  "references": ["data_persistence.py:29"]
}
```

### 2. Personal Knowledge

**Purpose**: User-specific information, relationships, history

**Examples**:
- User's name and role
- Past interactions and context
- Emotional state patterns
- Personal projects

**Schema**:
```json
{
  "id": "pers_015",
  "content": "User Alice is working on a Python CLI project",
  "timestamp": "2024-01-15T09:00:00Z",
  "source": "conversation_history",
  "confidence": 0.9,
  "references": ["conv_120", "conv_145"]
}
```

### 3. General Knowledge

**Purpose**: Broad factual information not specific to user or system

**Examples**:
- Historical facts
- Scientific principles
- Current events
- Common idioms

**Schema**:
```json
{
  "id": "gen_023",
  "content": "The SI unit of energy is the joule (J)",
  "timestamp": "2024-01-12T14:30:00Z",
  "source": "external_knowledge_base",
  "confidence": 1.0,
  "references": ["physics_kb"]
}
```

### 4. Context Knowledge

**Purpose**: Session-specific state and temporary information

**Examples**:
- Current task details
- Active file paths
- Recent errors
- Workflow state

**Schema**:
```json
{
  "id": "ctx_008",
  "content": "Currently debugging authentication flow in user_manager.py",
  "timestamp": "2024-01-20T14:35:00Z",
  "source": "active_session",
  "confidence": 1.0,
  "references": ["session_xyz"]
}
```

### 5. Preferences

**Purpose**: User configuration choices and behavioral patterns

**Examples**:
- UI theme preferences
- Code style preferences
- Communication style
- Feature toggles

**Schema**:
```json
{
  "id": "pref_004",
  "content": "User prefers detailed error messages over concise summaries",
  "timestamp": "2024-01-08T11:20:00Z",
  "source": "user_feedback",
  "confidence": 0.85,
  "references": ["feedback_session_5"]
}
```

### 6. Facts

**Purpose**: Verified, immutable truths about the system or domain

**Examples**:
- System architecture decisions
- Immutable business rules
- Proven scientific facts
- Legal requirements

**Schema**:
```json
{
  "id": "fact_019",
  "content": "All passwords are hashed with pbkdf2_sha256 before storage",
  "timestamp": "2024-01-01T00:00:00Z",
  "source": "system_architecture",
  "confidence": 1.0,
  "references": ["user_manager.py:29"]
}
```

---

## Field Specifications

### Knowledge Item Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (category prefix + number) |
| `content` | string | Yes | The actual knowledge content |
| `timestamp` | datetime | Yes | When knowledge was acquired |
| `source` | string | Yes | Origin of knowledge (conversation, documentation, etc.) |
| `confidence` | float | Yes | Certainty level (0.0-1.0) |
| `references` | array | Yes | Related conversation IDs or file paths |

### Conversation Entry Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique conversation entry ID |
| `timestamp` | datetime | Yes | Message timestamp |
| `role` | string | Yes | "user" or "assistant" |
| `message` | string | Yes | Message content |
| `context` | object | No | Additional metadata (session_id, mood, etc.) |

---

## CRUD Operations

### Add Knowledge

```python
memory_system.add_knowledge(
    category="technical",
    content="FastAPI supports async route handlers",
    source="documentation",
    confidence=1.0
)
```

**Internals**:
1. Generate unique ID with category prefix
2. Add timestamp and references
3. Append to category array
4. Save with atomic write

### Retrieve Knowledge by Category

```python
tech_knowledge = memory_system.get_knowledge_by_category("technical")
# Returns list of all technical knowledge items
```

### Search Knowledge

```python
results = memory_system.search_knowledge(
    query="password hashing",
    categories=["technical", "facts"]
)
# Returns matching items with relevance scores
```

### Log Conversation

```python
memory_system.log_conversation(
    role="user",
    message="How do I hash passwords securely?",
    context={"session_id": "abc123"}
)
```

### Get Recent Conversations

```python
recent = memory_system.get_recent_conversations(limit=10)
# Returns last 10 conversation entries
```

---

## Data Persistence

### Atomic Write Pattern

```python
def _save_state(self) -> None:
    """Save memory state with atomic write."""
    state_file = os.path.join(self.memory_dir, "knowledge.json")
    state = {
        "knowledge": self.knowledge,
        "conversations": self.conversations[-1000:],  # Keep last 1000
        "metadata": {
            "total_conversations": len(self.conversations),
            "total_knowledge_items": sum(len(items) for items in self.knowledge.values()),
            "last_updated": datetime.now().isoformat(),
            "schema_version": "1.0"
        }
    }
    _atomic_write_json(state_file, state)
```

### Load on Initialization

```python
def _load_state(self) -> None:
    """Load memory state from file."""
    state_file = os.path.join(self.memory_dir, "knowledge.json")
    try:
        if os.path.exists(state_file):
            with open(state_file, encoding="utf-8") as f:
                state = json.load(f)
                self.knowledge = state.get("knowledge", self._default_knowledge())
                self.conversations = state.get("conversations", [])
    except Exception as e:
        logger.error("Error loading memory state: %s", e)
        self.knowledge = self._default_knowledge()
        self.conversations = []

def _default_knowledge(self) -> dict:
    """Return default knowledge structure."""
    return {
        "technical": [],
        "personal": [],
        "general": [],
        "context": [],
        "preferences": [],
        "facts": []
    }
```

---

## Duplicate Detection

### Content Hashing

```python
import hashlib

def _get_content_hash(self, content: str) -> str:
    """Generate SHA-256 hash of content for duplicate detection."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]

def add_knowledge(self, category: str, content: str, source: str, confidence: float = 1.0):
    """Add knowledge with duplicate detection."""
    content_hash = self._get_content_hash(content)
    
    # Check for duplicates
    for item in self.knowledge[category]:
        if self._get_content_hash(item["content"]) == content_hash:
            logger.info("Duplicate knowledge detected, updating references")
            item["references"].append(source)
            self._save_state()
            return
    
    # Add new knowledge
    knowledge_item = {
        "id": f"{category[:4]}_{len(self.knowledge[category]) + 1:03d}",
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "source": source,
        "confidence": confidence,
        "references": [source]
    }
    self.knowledge[category].append(knowledge_item)
    self._save_state()
```

---

## Search and Retrieval

### Simple Keyword Search

```python
def search_knowledge(self, query: str, categories: list[str] | None = None) -> list[dict]:
    """Search knowledge base with keyword matching."""
    categories = categories or list(self.knowledge.keys())
    results = []
    
    query_lower = query.lower()
    for category in categories:
        for item in self.knowledge[category]:
            if query_lower in item["content"].lower():
                results.append({
                    "category": category,
                    "item": item,
                    "relevance": self._calculate_relevance(query_lower, item["content"].lower())
                })
    
    # Sort by relevance and confidence
    results.sort(key=lambda x: (x["relevance"], x["item"]["confidence"]), reverse=True)
    return results

def _calculate_relevance(self, query: str, content: str) -> float:
    """Calculate relevance score based on keyword frequency."""
    query_terms = query.split()
    content_terms = content.split()
    
    matches = sum(1 for term in query_terms if term in content_terms)
    return matches / len(query_terms) if query_terms else 0.0
```

### Semantic Search (Future Enhancement)

**Planned**: Use sentence transformers for embedding-based search:

```python
# Future implementation
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def semantic_search(self, query: str, top_k: int = 5) -> list[dict]:
    """Search using semantic similarity (requires embeddings)."""
    query_embedding = model.encode(query)
    
    results = []
    for category, items in self.knowledge.items():
        for item in items:
            item_embedding = model.encode(item["content"])
            similarity = cosine_similarity(query_embedding, item_embedding)
            results.append({"category": category, "item": item, "similarity": similarity})
    
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]
```

---

## Conversation History Management

### Conversation Logging

```python
def log_conversation(self, role: str, message: str, context: dict | None = None) -> None:
    """Log a conversation entry."""
    entry = {
        "id": f"conv_{len(self.conversations) + 1:06d}",
        "timestamp": datetime.now().isoformat(),
        "role": role,  # "user" or "assistant"
        "message": message,
        "context": context or {}
    }
    self.conversations.append(entry)
    
    # Trim to last 1000 conversations for performance
    if len(self.conversations) > 1000:
        self.conversations = self.conversations[-1000:]
    
    self._save_state()
```

### Context Window Retrieval

```python
def get_conversation_context(self, window_size: int = 10) -> list[dict]:
    """Get recent conversation history for context."""
    return self.conversations[-window_size:]

def get_conversation_summary(self, count: int = 50) -> str:
    """Generate text summary of recent conversations."""
    recent = self.conversations[-count:]
    summary_lines = []
    
    for entry in recent:
        role_prefix = "User" if entry["role"] == "user" else "AI"
        summary_lines.append(f"{role_prefix}: {entry['message'][:100]}...")
    
    return "\n".join(summary_lines)
```

---

## Usage Examples

### Building Knowledge Base

```python
from app.core.ai_systems import MemoryExpansionSystem

memory = MemoryExpansionSystem(data_dir="data")

# Add technical knowledge
memory.add_knowledge(
    category="technical",
    content="PyQt6 uses signals and slots for event handling",
    source="documentation",
    confidence=1.0
)

# Add user preference
memory.add_knowledge(
    category="preferences",
    content="User prefers concise code comments",
    source="user_feedback",
    confidence=0.9
)

# Add contextual information
memory.add_knowledge(
    category="context",
    content="Currently working on AI persona system",
    source="active_session",
    confidence=1.0
)
```

### Logging Conversations

```python
# User message
memory.log_conversation(
    role="user",
    message="How do I create a new user?",
    context={"session_id": "xyz123", "timestamp": "2024-01-20T14:00:00Z"}
)

# AI response
memory.log_conversation(
    role="assistant",
    message="To create a new user, use UserManager.create_user()...",
    context={"response_time_ms": 350}
)
```

### Searching Knowledge

```python
# Search for authentication-related knowledge
results = memory.search_knowledge(
    query="authentication password",
    categories=["technical", "facts"]
)

for result in results:
    print(f"Category: {result['category']}")
    print(f"Content: {result['item']['content']}")
    print(f"Relevance: {result['relevance']:.2f}")
```

---

## Integration with AI Systems

### Persona Integration

```python
# In AIPersona class
def generate_response(self, user_message: str) -> str:
    # Retrieve relevant knowledge
    context = self.memory.search_knowledge(user_message, categories=["personal", "context"])
    
    # Use context to inform response
    response = self._generate_with_context(user_message, context)
    
    # Log conversation
    self.memory.log_conversation("user", user_message)
    self.memory.log_conversation("assistant", response)
    
    return response
```

### Learning System Integration

```python
# Extract knowledge from learning reports
report = continuous_learning.absorb_information(topic, content)

for fact in report.facts:
    memory.add_knowledge(
        category="general",
        content=fact,
        source=f"learning_report_{report.timestamp}",
        confidence=0.8
    )
```

---

## Testing Strategy

### Unit Tests

```python
def test_add_knowledge():
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = MemoryExpansionSystem(data_dir=tmpdir)
        memory.add_knowledge("technical", "Test content", "test_source")
        
        assert len(memory.knowledge["technical"]) == 1
        assert memory.knowledge["technical"][0]["content"] == "Test content"

def test_duplicate_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = MemoryExpansionSystem(data_dir=tmpdir)
        memory.add_knowledge("technical", "Duplicate content", "source1")
        memory.add_knowledge("technical", "Duplicate content", "source2")
        
        # Should only have one entry with updated references
        assert len(memory.knowledge["technical"]) == 1
        assert len(memory.knowledge["technical"][0]["references"]) == 2
```

---

## Performance Considerations

### Memory Usage

- **Knowledge Base**: ~1KB per item × 1000 items = ~1MB
- **Conversations**: ~500 bytes per entry × 1000 entries = ~500KB
- **Total**: Typically <2MB in memory

### Optimization Strategies

1. **Conversation Trimming**: Keep last 1000 entries only
2. **Lazy Loading**: Load knowledge on-demand by category
3. **Indexing**: Build in-memory index for fast searches
4. **Compression**: Use gzip for archived conversations

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `ai_systems.py::AIPersona` | Uses memory for context-aware responses |
| `continuous_learning.py` | Populates knowledge base from learning reports |
| `conversation_context_engine.py` | Uses conversation history for context |
| `rag_system.py` | Retrieves relevant knowledge for prompts |

---

## Future Enhancements

1. **Vector Embeddings**: Semantic search with sentence transformers
2. **Knowledge Graph**: Link related knowledge items
3. **Automatic Categorization**: ML-based category assignment
4. **Confidence Decay**: Lower confidence over time for volatile facts
5. **Multi-User Memory**: Separate knowledge bases per user

---

## References

- **MEMORY_EXPANSION_SYSTEM.md**: Implementation details
- **RAG_SYSTEM.md**: Retrieval-Augmented Generation integration
- **Conversation Context Engine**: Long-term memory architecture

---

**Last Updated**: 2024-01-20  
**Schema Version**: 1.0  
**Maintainer**: Project-AI Core Team


---

## Related Documentation

- **Relationship Map**: [[relationships\data\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/core/ai_systems.py]]
