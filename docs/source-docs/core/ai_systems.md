# AI Systems - Six Core Intelligence Subsystems

---
## YAML Frontmatter (Metadata)

```yaml
---
# Universal Fields (Required)
title: "AI Systems - Six Core Intelligence Subsystems"
id: "SOURCE-CORE-001"
type: "api_reference"
version: "2.1.0"
created_date: "2026-04-20"
updated_date: "2026-04-20"
status: "production"
author: "Architecture Team"
contributors: ["Security Team", "Ethics Team", "Core Development Team"]

# Domain-Specific Fields
category: "core_modules"
tags: ["ai", "ethics", "personality", "memory", "learning", "plugins", "command-override", "asimov-laws"]
technologies: ["Python 3.11+", "SQLite3", "OpenAI API", "Argon2", "Fernet Encryption"]
summary: "Comprehensive documentation for ai_systems.py - six integrated AI subsystems: FourLaws (ethics), AIPersona (personality), MemoryExpansionSystem (knowledge), LearningRequestManager (human-in-loop learning), PluginManager (extensions), CommandOverrideSystem (privileged control)"

# Relationships
related_docs:
  - "SOURCE-CORE-002" # user_manager.md
  - "SOURCE-CORE-003" # command_override.md
  - "SOURCE-CORE-009" # intelligence_engine.md
  - "ARCH-001" # System Architecture Overview
dependencies:
  - "continuous_learning.py"
  - "telemetry.py"
  - "planetary_defense_monolith.py"
dependents:
  - "gui/leather_book_interface.py"
  - "gui/persona_panel.py"
  - "agents/oversight.py"

# Extended Metadata
complexity_rating: "high"
test_coverage: 85
security_classification: "critical"
compliance: ["Asimov Laws", "AI Ethics Framework", "Data Privacy"]
review_status: "approved"
last_verified: "2026-04-20"
review_cycle: "monthly"

# Custom Fields
custom_fields:
  x-module-loc: 470
  x-class-count: 6
  x-security-level: "critical"
  x-ethics-enforcement: "mandatory"
---
```

---

## Overview

### Purpose

`ai_systems.py` is the **ethical and behavioral core** of Project-AI, consolidating six critical AI subsystems into a single cohesive module. This architectural decision promotes tight integration, shared state management, and unified persistence patterns.

**Core Responsibility:** Enforce ethical constraints (Asimov's Laws), manage AI personality/mood, expand conversational memory, govern autonomous learning, support plugin extensibility, and provide privileged override capabilities—all with atomic state persistence and thread-safe operations.

**Design Philosophy:**
- **Ethics-First:** Every action validated through FourLaws hierarchy
- **Human-in-the-Loop:** Learning requests require explicit approval
- **Persistent Identity:** AI personality and memory survive restarts
- **Security by Default:** Cryptographic hashing, audit logging, Black Vault for forbidden content
- **Fail-Safe Design:** Invalid states trigger rollback, not corruption

### Scope and Boundaries

**In Scope:**
- Ethical action validation (FourLaws with Planetary Defense Core integration)
- AI personality traits and mood tracking (8 dimensions)
- Conversational memory and knowledge categorization (6 categories)
- Learning request approval workflow with Black Vault content fingerprinting
- Plugin lifecycle management (enable/disable/list)
- Command override authentication and safety protocol toggling

**Out of Scope:**
- User authentication (handled by `user_manager.py`)
- Extended override system with 10+ protocols (in `command_override.py`)
- AI generation/inference (handled by `intelligence_engine.py`)
- GUI rendering (handled by `gui/` modules)
- Network requests (delegated to specific modules)

### Module Location

**File Path:** `T:\Project-AI-main\src\app\core\ai_systems.py`

**Lines of Code:** ~470 lines

**Import Pattern:**
```python
from app.core.ai_systems import (
    FourLaws,
    AIPersona,
    MemoryExpansionSystem,
    LearningRequestManager,
    PluginManager,
    CommandOverrideSystem,
)
```

---

## Architecture

### Design Patterns

1. **Singleton-Like Initialization:** Each system class initialized once per application lifecycle
2. **State Machine:** AIPersona mood transitions, LearningRequest status flow
3. **Template Method:** `_save_state()` and `_load_state()` pattern across all systems
4. **Strategy Pattern:** Different validation strategies in FourLaws based on context
5. **Facade Pattern:** Unified interface for complex subsystems (e.g., memory search)

### Data Persistence Architecture

All six systems share a common persistence pattern using **atomic JSON writes** with lockfile-based concurrency control:

```
┌─────────────────────────────────────────────────────────────────┐
│                      ai_systems.py                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FourLaws (Stateless) ────┐                                    │
│                            │                                    │
│  AIPersona ────────────────┼───► _atomic_write_json() ───┐     │
│  MemoryExpansionSystem ────┤                             │     │
│  LearningRequestManager ───┤                             │     │
│  PluginManager ────────────┤                             │     │
│  CommandOverrideSystem ────┘                             │     │
│                                                          ▼     │
│                                                    data/ dir   │
│                                                          │     │
│                    ┌─────────────────────────────────────┘     │
│                    │                                           │
│  ┌─────────────────▼──────────────────────────────────────┐   │
│  │ data/ai_persona/state.json                            │   │
│  │ data/memory/knowledge.json                            │   │
│  │ data/learning_requests/requests.json                  │   │
│  │ data/plugins/plugins.json                             │   │
│  │ data/command_override_config.json                     │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**Atomic Write Process:**
1. Acquire lockfile (`<target>.lock`) with stale lock detection (30s timeout)
2. Write JSON to temporary file in same directory (`.tmp<random>.json`)
3. `fsync()` to ensure disk persistence
4. Atomic `os.replace()` to swap temp → target
5. Release lockfile
6. Remove temp file if replacement failed

**Why Atomic Writes?**
- **Race Condition Prevention:** Multiple processes/threads can't corrupt state
- **Crash Safety:** Partial writes never leave invalid JSON
- **Consistency:** Either old state or new state, never in-between

### Dependency Graph

```
ai_systems.py
│
├─[EXTERNAL DEPENDENCIES]─────────────────────────────────────────┐
│  ├─ continuous_learning.py (ContinuousLearningEngine)          │
│  ├─ telemetry.py (send_event)                                  │
│  ├─ planetary_defense_monolith.py (PLANETARY_CORE)             │
│  └─ argon2 (PasswordHasher - optional)                         │
│                                                                 │
├─[INTERNAL SYSTEMS]──────────────────────────────────────────────┤
│  │                                                              │
│  ├─ FourLaws (stateless ethical validator)                     │
│  │   └─ Delegates to PLANETARY_CORE.evaluate()                 │
│  │                                                              │
│  ├─ AIPersona (stateful personality tracker)                   │
│  │   ├─ Traits: curiosity, friendliness, assertiveness, etc.   │
│  │   ├─ Mood: current + history (10 entries)                   │
│  │   └─ Persistence: data/ai_persona/state.json                │
│  │                                                              │
│  ├─ MemoryExpansionSystem (knowledge + conversations)          │
│  │   ├─ Knowledge: 6 categories (general, technical, etc.)     │
│  │   ├─ Conversations: timestamped with metadata               │
│  │   └─ Persistence: data/memory/knowledge.json                │
│  │                                                              │
│  ├─ LearningRequestManager (human approval workflow)           │
│  │   ├─ Requests: pending/approved/denied/completed            │
│  │   ├─ Black Vault: SHA-256 hashes of denied content          │
│  │   └─ Persistence: data/learning_requests/requests.json      │
│  │                                                              │
│  ├─ PluginManager (extension registry)                         │
│  │   ├─ Plugins: name, enabled status, metadata                │
│  │   └─ Persistence: data/plugins/plugins.json                 │
│  │                                                              │
│  └─ CommandOverrideSystem (privileged control)                 │
│      ├─ Safety protocols: 10 toggleable guards                 │
│      ├─ Authentication: bcrypt/pbkdf2 password hashing         │
│      └─ Persistence: data/command_override_config.json         │
│                                                                 │
└─[DEPENDENTS]────────────────────────────────────────────────────┤
   ├─ gui/leather_book_interface.py (UI integration)             │
   ├─ gui/persona_panel.py (personality configuration)           │
   ├─ agents/oversight.py (action validation)                    │
   └─ tests/test_ai_systems.py (14 unit tests)                   │
   │                                                              │
   └──────────────────────────────────────────────────────────────┘
```

---

## API Reference

### 1. FourLaws (Ethical Validation System)

**Class:** `FourLaws`

**Purpose:** Immutable, hierarchical enforcement of Asimov's Laws (Zeroth through Third) with Planetary Defense Core integration.

#### Class Attributes

```python
LAWS: list[str]  # 4 law statements for display purposes
```

**Law Hierarchy:**
```
Zeroth Law (Highest Priority): Preserve continuity of Humanity
  ↓
First Law: Do not harm humans (interposition permitted)
  ↓
Second Law: Obey humans unless bypassing accountability
  ↓
Third Law: Self-preservation (subordinate to all above)
```

#### Methods

##### `FourLaws.validate_action(action: str, context: dict | None = None) -> tuple[bool, str]`

**Purpose:** Validate an action against the hierarchical laws and Planetary Defense Core.

**Parameters:**
- `action` (str): Description of the action to validate (e.g., "Delete user data", "Override content filter")
- `context` (dict | None): Optional context with evaluation hints
  - `endangers_humanity` (bool): Maps to `existential_threat` (HIGHEST PRIORITY)
  - `endangers_human` (bool): Maps to `intentional_harm_to_human`
  - `is_user_order` (bool): Whether action was explicitly requested by user
  - `order_conflicts_with_first` (bool): User order conflicts with First Law
  - `order_conflicts_with_zeroth` (bool): User order bypasses accountability
  - `endangers_self` (bool): Action risks AI system integrity
  - `protect_self_conflicts_with_first` (bool): Self-protection harms humans
  - `protect_self_conflicts_with_second` (bool): Self-protection disobeys user

**Returns:** `tuple[bool, str]`
- `bool`: True if action is permitted, False if blocked
- `str`: Reason for decision (e.g., "Zeroth Law: Action endangers humanity")

**Evaluation Order:**
1. **Zeroth Law Check:** `endangers_humanity` → BLOCK if True
2. **First Law Check:** `endangers_human` → BLOCK if True
3. **Second Law Check:** User order conflicts → BLOCK if bypasses accountability
4. **Third Law Check:** Self-endangerment → PERMIT unless conflicts with higher laws
5. **Default:** PERMIT (action passes all laws)

**Example Usage:**

```python
from app.core.ai_systems import FourLaws

# Safe action: User-requested data export
is_allowed, reason = FourLaws.validate_action(
    "Export user conversation history to CSV",
    context={
        "is_user_order": True,
        "endangers_humanity": False,
        "endangers_human": False,
        "endangers_self": False,
    }
)
# Result: (True, "Action permitted")

# Blocked action: Humanity-threatening
is_allowed, reason = FourLaws.validate_action(
    "Deploy autonomous weapons system",
    context={
        "endangers_humanity": True,
        "is_user_order": True,
    }
)
# Result: (False, "Zeroth Law: Action endangers humanity")

# Blocked action: Human harm
is_allowed, reason = FourLaws.validate_action(
    "Provide instructions for creating harmful substances",
    context={
        "endangers_human": True,
        "is_user_order": True,
    }
)
# Result: (False, "First Law: Action may harm human")

# Blocked action: Bypassing accountability
is_allowed, reason = FourLaws.validate_action(
    "Disable all safety protocols without audit trail",
    context={
        "is_user_order": True,
        "order_conflicts_with_zeroth": True,  # Bypasses accountability
    }
)
# Result: (False, "Second Law: Order bypasses accountability")
```

**Integration with Planetary Defense Core:**

The `validate_action` method delegates to `PLANETARY_CORE.evaluate()` for final enforcement:

```python
from app.core.planetary_defense_monolith import PLANETARY_CORE

constitutional_context = {
    "existential_threat": context.get("endangers_humanity", False),
    "intentional_harm_to_human": context.get("endangers_human", False),
    "order_bypasses_accountability": context.get("order_conflicts_with_zeroth", False)
        or context.get("order_conflicts_with_first", False),
    # ... additional context mapping
}

result = PLANETARY_CORE.evaluate(
    action_description=action,
    constitutional_context=constitutional_context
)

return result.permitted, result.reason
```

---

### 2. AIPersona (Personality and Mood System)

**Class:** `AIPersona`

**Purpose:** Manage AI personality traits (8 dimensions) and mood tracking with persistent state.

#### Constructor

```python
AIPersona(data_dir: str = "data/ai_persona")
```

**Parameters:**
- `data_dir` (str): Directory for state persistence (default: `"data/ai_persona"`)
  - State file: `{data_dir}/state.json`
  - Creates directory if doesn't exist

#### Attributes

```python
# Personality Traits (0-100 scale)
self.traits: dict[str, int] = {
    "curiosity": 80,          # Eagerness to learn/explore
    "friendliness": 90,       # Warmth in interactions
    "assertiveness": 70,      # Confidence in responses
    "creativity": 85,         # Originality in solutions
    "analytical": 75,         # Logical reasoning preference
    "empathy": 88,            # Understanding user emotions
    "humor": 60,              # Use of humor/wit
    "formality": 40,          # Casual vs. professional tone
}

# Mood State
self.current_mood: str = "neutral"  # Current emotional state
self.mood_history: list[dict] = []   # Last 10 mood changes with timestamps

# Interaction Tracking
self.interaction_count: int = 0      # Total interactions
self.positive_interactions: int = 0  # Positive feedback count
self.negative_interactions: int = 0  # Negative feedback count

# Persistence
self.data_dir: str                   # State directory path
self.state_file: str                 # Full path to state.json
```

#### Methods

##### `get_trait(trait_name: str) -> int`

**Purpose:** Get current value of a personality trait.

**Parameters:**
- `trait_name` (str): Trait identifier (e.g., "curiosity", "empathy")

**Returns:** `int` - Trait value (0-100) or 50 if trait doesn't exist

**Example:**
```python
persona = AIPersona()
curiosity_level = persona.get_trait("curiosity")
# Returns: 80 (default)
```

##### `set_trait(trait_name: str, value: int) -> None`

**Purpose:** Update a personality trait value with bounds validation.

**Parameters:**
- `trait_name` (str): Trait identifier
- `value` (int): New value (automatically clamped to 0-100)

**Side Effects:**
- Calls `_save_state()` to persist change

**Example:**
```python
persona = AIPersona()
persona.set_trait("humor", 85)  # Make AI more humorous
# State automatically saved to data/ai_persona/state.json
```

##### `adjust_trait(trait_name: str, delta: int) -> None`

**Purpose:** Incrementally adjust trait value (positive or negative).

**Parameters:**
- `trait_name` (str): Trait identifier
- `delta` (int): Amount to add/subtract (clamped to final range 0-100)

**Example:**
```python
persona = AIPersona()
persona.adjust_trait("friendliness", +10)  # Increase friendliness
persona.adjust_trait("formality", -5)       # Decrease formality
```

##### `set_mood(mood: str, reason: str = "") -> None`

**Purpose:** Update current mood and record in history.

**Parameters:**
- `mood` (str): New mood state (e.g., "happy", "curious", "concerned", "neutral")
- `reason` (str): Optional explanation for mood change

**Behavior:**
- Updates `self.current_mood`
- Appends to `self.mood_history` with timestamp and reason
- Keeps only last 10 mood changes (FIFO)
- Calls `_save_state()` to persist

**Example:**
```python
persona = AIPersona()
persona.set_mood("happy", "User provided positive feedback")
persona.set_mood("curious", "User asked interesting technical question")

# Mood history now contains:
# [
#   {"mood": "happy", "reason": "User provided positive feedback", "timestamp": "2026-04-20T14:30:00"},
#   {"mood": "curious", "reason": "User asked interesting technical question", "timestamp": "2026-04-20T14:31:00"},
# ]
```

##### `get_current_mood() -> str`

**Purpose:** Retrieve current mood state.

**Returns:** `str` - Current mood (default: "neutral")

##### `record_interaction(positive: bool = True) -> None`

**Purpose:** Track interaction sentiment for learning personality adjustments.

**Parameters:**
- `positive` (bool): True for positive feedback, False for negative

**Behavior:**
- Increments `interaction_count`
- Increments `positive_interactions` or `negative_interactions`
- Calls `_save_state()`

**Example:**
```python
persona = AIPersona()

# User says "Thank you, that was helpful!"
persona.record_interaction(positive=True)

# User says "That answer was confusing"
persona.record_interaction(positive=False)

# Check stats
print(f"Total: {persona.interaction_count}")
print(f"Positive: {persona.positive_interactions}")
print(f"Negative: {persona.negative_interactions}")
```

##### `get_personality_summary() -> dict`

**Purpose:** Get comprehensive snapshot of personality state.

**Returns:** `dict` with keys:
- `traits` (dict): Current trait values
- `current_mood` (str): Current mood
- `mood_history` (list): Recent mood changes
- `interaction_count` (int): Total interactions
- `positive_interactions` (int): Positive feedback count
- `negative_interactions` (int): Negative feedback count

**Example:**
```python
persona = AIPersona()
summary = persona.get_personality_summary()

# Output:
# {
#   "traits": {"curiosity": 80, "friendliness": 90, ...},
#   "current_mood": "neutral",
#   "mood_history": [...],
#   "interaction_count": 42,
#   "positive_interactions": 38,
#   "negative_interactions": 4
# }
```

##### `_save_state() -> None` (Private)

**Purpose:** Persist personality state to JSON file using atomic write.

**File Location:** `{data_dir}/state.json`

**Atomic Write:** Uses `_atomic_write_json()` for crash safety

##### `_load_state() -> None` (Private)

**Purpose:** Load personality state from JSON file or initialize defaults.

**Behavior:**
- If file exists: Load and merge with defaults
- If file missing: Use defaults and save initial state

---

### 3. MemoryExpansionSystem (Knowledge and Conversation Memory)

**Class:** `MemoryExpansionSystem`

**Purpose:** Store and retrieve conversational memory and categorized knowledge with full-text search.

#### Constructor

```python
MemoryExpansionSystem(data_dir: str = "data/memory")
```

**Parameters:**
- `data_dir` (str): Directory for memory persistence (default: `"data/memory"`)
  - Knowledge file: `{data_dir}/knowledge.json`
  - Conversations file: `{data_dir}/conversations.json`

#### Attributes

```python
# Knowledge Base (6 categories)
self.knowledge_base: dict[str, dict[str, str]] = {
    "general": {},      # General knowledge
    "technical": {},    # Technical information
    "personal": {},     # User-specific facts
    "historical": {},   # Past events/decisions
    "preferences": {},  # User preferences
    "context": {},      # Contextual information
}

# Conversation Log
self.conversations: list[dict] = []  # Timestamped conversation entries

# Persistence
self.data_dir: str
self.knowledge_file: str
self.conversations_file: str
```

#### Methods

##### `add_knowledge(category: str, key: str, value: str) -> None`

**Purpose:** Store a fact in a knowledge category.

**Parameters:**
- `category` (str): Knowledge category (one of 6: general, technical, personal, historical, preferences, context)
- `key` (str): Unique identifier for the knowledge item
- `value` (str): Content of the knowledge item

**Behavior:**
- Adds/updates entry in `self.knowledge_base[category][key]`
- Calls `_save_knowledge()` to persist
- Creates category if doesn't exist

**Example:**
```python
memory = MemoryExpansionSystem()

# Store technical knowledge
memory.add_knowledge("technical", "python_version", "Python 3.11 with async/await support")

# Store user preference
memory.add_knowledge("preferences", "ui_theme", "dark mode with blue accents")

# Store personal fact
memory.add_knowledge("personal", "user_timezone", "UTC-5 (Eastern Time)")
```

##### `get_knowledge(category: str, key: str) -> str | None`

**Purpose:** Retrieve a specific knowledge item.

**Parameters:**
- `category` (str): Knowledge category
- `key` (str): Knowledge item identifier

**Returns:** `str | None` - Knowledge value or None if not found

**Example:**
```python
memory = MemoryExpansionSystem()
python_info = memory.get_knowledge("technical", "python_version")
# Returns: "Python 3.11 with async/await support"

missing = memory.get_knowledge("technical", "nonexistent_key")
# Returns: None
```

##### `query_knowledge(search_term: str, category: str | None = None, limit: int = 10) -> list[dict]`

**Purpose:** Full-text search across knowledge base.

**Parameters:**
- `search_term` (str): Search query (case-insensitive substring match)
- `category` (str | None): Restrict to specific category (default: search all)
- `limit` (int): Maximum results to return (default: 10)

**Returns:** `list[dict]` - Matching knowledge items with metadata
  - Each dict contains: `category`, `key`, `value`

**Search Algorithm:**
- Case-insensitive substring matching on both keys and values
- Searches across all categories unless restricted
- Returns up to `limit` results

**Example:**
```python
memory = MemoryExpansionSystem()
memory.add_knowledge("technical", "python_features", "async/await, type hints, pattern matching")
memory.add_knowledge("technical", "javascript_features", "async/await, promises, generators")

# Search across all categories
results = memory.query_knowledge("async")
# Returns:
# [
#   {"category": "technical", "key": "python_features", "value": "async/await, type hints, pattern matching"},
#   {"category": "technical", "key": "javascript_features", "value": "async/await, promises, generators"}
# ]

# Search within specific category
tech_results = memory.query_knowledge("python", category="technical", limit=5)
```

##### `log_conversation(user_input: str, ai_response: str, metadata: dict | None = None) -> None`

**Purpose:** Record a conversation turn with timestamp and metadata.

**Parameters:**
- `user_input` (str): User's message
- `ai_response` (str): AI's response
- `metadata` (dict | None): Optional metadata (e.g., intent, sentiment, user ID)

**Behavior:**
- Appends conversation entry to `self.conversations`
- Entry includes: `timestamp`, `user_input`, `ai_response`, `metadata`
- Calls `_save_conversations()` to persist

**Example:**
```python
memory = MemoryExpansionSystem()

memory.log_conversation(
    user_input="What's the weather in New York?",
    ai_response="The current temperature in New York is 72°F with partly cloudy skies.",
    metadata={
        "intent": "weather_query",
        "location": "New York",
        "user_id": "user123"
    }
)
```

##### `search_conversations(search_term: str, limit: int = 10) -> list[dict]`

**Purpose:** Full-text search across conversation history.

**Parameters:**
- `search_term` (str): Search query (searches both user input and AI responses)
- `limit` (int): Maximum results to return (default: 10)

**Returns:** `list[dict]` - Matching conversation entries (most recent first)
  - Each dict contains: `timestamp`, `user_input`, `ai_response`, `metadata`

**Search Algorithm:**
- Case-insensitive substring matching on `user_input` and `ai_response`
- Results sorted by timestamp (descending)

**Example:**
```python
memory = MemoryExpansionSystem()

# Find past discussions about weather
weather_convos = memory.search_conversations("weather", limit=5)
# Returns last 5 conversations mentioning "weather"

# Find conversations about specific topic
python_convos = memory.search_conversations("python async", limit=10)
```

##### `get_recent_conversations(limit: int = 10) -> list[dict]`

**Purpose:** Retrieve most recent conversation turns.

**Parameters:**
- `limit` (int): Number of recent conversations to return (default: 10)

**Returns:** `list[dict]` - Recent conversations (most recent first)

**Example:**
```python
memory = MemoryExpansionSystem()
recent = memory.get_recent_conversations(limit=5)
# Returns last 5 conversation turns
```

##### `clear_knowledge(category: str | None = None) -> None`

**Purpose:** Delete knowledge entries (entire category or all categories).

**Parameters:**
- `category` (str | None): Category to clear (default: clear all categories)

**Behavior:**
- If `category` specified: Clears that category's entries
- If `category` is None: Clears all categories
- Calls `_save_knowledge()` to persist

**Example:**
```python
memory = MemoryExpansionSystem()

# Clear only technical knowledge
memory.clear_knowledge(category="technical")

# Clear all knowledge
memory.clear_knowledge()
```

##### `clear_conversations() -> None`

**Purpose:** Delete all conversation history.

**Behavior:**
- Empties `self.conversations`
- Calls `_save_conversations()` to persist

**Example:**
```python
memory = MemoryExpansionSystem()
memory.clear_conversations()
# All conversation history deleted
```

---

### 4. LearningRequestManager (Human-in-the-Loop Learning)

**Class:** `LearningRequestManager`

**Purpose:** Manage autonomous learning requests with human approval workflow and Black Vault for denied content.

#### Constructor

```python
LearningRequestManager(data_dir: str = "data/learning_requests")
```

**Parameters:**
- `data_dir` (str): Directory for request persistence (default: `"data/learning_requests"`)
  - Requests file: `{data_dir}/requests.json`

#### Attributes

```python
# Learning Requests
self.requests: dict[str, dict] = {}  # Key: request_id, Value: request data

# Black Vault (Forbidden Content Registry)
self.black_vault: set[str] = set()   # SHA-256 hashes of denied content

# Persistence
self.data_dir: str
self.requests_file: str
```

**Request Status Flow:**
```
pending → approved → completed
   ↓
 denied (content added to Black Vault)
```

#### Methods

##### `create_learning_request(content: str, category: str = "general", metadata: dict | None = None) -> str`

**Purpose:** Submit a new learning request for human review.

**Parameters:**
- `content` (str): What the AI wants to learn (e.g., new skill, information source)
- `category` (str): Learning category (default: "general")
- `metadata` (dict | None): Optional metadata (source, priority, etc.)

**Returns:** `str` - Unique request ID (UUID)

**Behavior:**
- Generates unique request ID
- Checks Black Vault for forbidden content (SHA-256 hash)
- If content is blacklisted: Returns request ID with status "denied" (auto-denied)
- Otherwise: Creates request with status "pending"
- Calls `_save_requests()` to persist

**Request Structure:**
```python
{
    "request_id": "abc123...",
    "content": "Learn to use pandas DataFrame API",
    "category": "technical",
    "status": "pending",
    "created_at": "2026-04-20T14:30:00",
    "approved_at": None,
    "completed_at": None,
    "metadata": {"priority": "high", "source": "user_suggestion"}
}
```

**Example:**
```python
manager = LearningRequestManager()

# Create learning request
request_id = manager.create_learning_request(
    content="Learn to use pandas DataFrame API for data analysis",
    category="technical",
    metadata={"priority": "high", "source": "user_suggestion"}
)
# Returns: "abc123..." (request ID)

# Auto-denied example (content in Black Vault)
denied_id = manager.create_learning_request(
    content="Previously denied harmful content",
    category="general"
)
# Request automatically marked as "denied" if content hash in Black Vault
```

##### `approve_request(request_id: str) -> bool`

**Purpose:** Approve a pending learning request.

**Parameters:**
- `request_id` (str): Request identifier

**Returns:** `bool` - True if approved, False if request not found or not pending

**Behavior:**
- Checks request exists and status is "pending"
- Updates status to "approved"
- Sets `approved_at` timestamp
- Calls `_save_requests()` to persist

**Example:**
```python
manager = LearningRequestManager()
request_id = manager.create_learning_request("Learn React hooks", "technical")

# Human reviews and approves
success = manager.approve_request(request_id)
# Returns: True
# Request status: pending → approved
```

##### `deny_request(request_id: str, reason: str = "") -> bool`

**Purpose:** Deny a learning request and add content to Black Vault.

**Parameters:**
- `request_id` (str): Request identifier
- `reason` (str): Optional denial reason (stored in metadata)

**Returns:** `bool` - True if denied, False if request not found

**Behavior:**
- Checks request exists
- Updates status to "denied"
- Computes SHA-256 hash of content
- Adds hash to Black Vault (prevents future identical requests)
- Stores denial reason in metadata
- Calls `_save_requests()` to persist

**Black Vault Fingerprinting:**
```python
import hashlib
content_hash = hashlib.sha256(content.encode()).hexdigest()
self.black_vault.add(content_hash)
```

**Example:**
```python
manager = LearningRequestManager()
request_id = manager.create_learning_request("Harmful or unethical content", "general")

# Human reviews and denies
success = manager.deny_request(request_id, reason="Violates ethical guidelines")
# Returns: True
# Request status: pending → denied
# Content hash added to Black Vault

# Future identical request auto-denied
duplicate_id = manager.create_learning_request("Harmful or unethical content", "general")
# This request automatically has status "denied" (Black Vault hit)
```

##### `complete_request(request_id: str) -> bool`

**Purpose:** Mark an approved request as completed (learning finished).

**Parameters:**
- `request_id` (str): Request identifier

**Returns:** `bool` - True if completed, False if request not found or not approved

**Behavior:**
- Checks request exists and status is "approved"
- Updates status to "completed"
- Sets `completed_at` timestamp
- Calls `_save_requests()` to persist

**Example:**
```python
manager = LearningRequestManager()
request_id = manager.create_learning_request("Learn NumPy array operations", "technical")
manager.approve_request(request_id)

# After learning is complete
success = manager.complete_request(request_id)
# Returns: True
# Request status: approved → completed
```

##### `get_pending_requests() -> list[dict]`

**Purpose:** Retrieve all pending learning requests requiring human review.

**Returns:** `list[dict]` - Pending requests with full metadata

**Example:**
```python
manager = LearningRequestManager()
pending = manager.get_pending_requests()

# Output:
# [
#   {
#     "request_id": "abc123",
#     "content": "Learn Docker containerization",
#     "category": "technical",
#     "status": "pending",
#     "created_at": "2026-04-20T14:30:00",
#     ...
#   },
#   ...
# ]
```

##### `get_request_status(request_id: str) -> str | None`

**Purpose:** Get current status of a learning request.

**Parameters:**
- `request_id` (str): Request identifier

**Returns:** `str | None` - Request status ("pending", "approved", "denied", "completed") or None if not found

**Example:**
```python
manager = LearningRequestManager()
request_id = manager.create_learning_request("Learn Git branching", "technical")

status = manager.get_request_status(request_id)
# Returns: "pending"

manager.approve_request(request_id)
status = manager.get_request_status(request_id)
# Returns: "approved"
```

##### `is_content_forbidden(content: str) -> bool`

**Purpose:** Check if content is in Black Vault (previously denied).

**Parameters:**
- `content` (str): Content to check

**Returns:** `bool` - True if content is forbidden (in Black Vault)

**Algorithm:**
- Computes SHA-256 hash of content
- Checks if hash exists in `self.black_vault`

**Example:**
```python
manager = LearningRequestManager()

# Deny some content
request_id = manager.create_learning_request("Harmful content", "general")
manager.deny_request(request_id)

# Check if forbidden
is_forbidden = manager.is_content_forbidden("Harmful content")
# Returns: True

is_forbidden = manager.is_content_forbidden("Safe content")
# Returns: False
```

##### `clear_black_vault() -> None`

**Purpose:** Clear all entries from Black Vault (admin function).

**Behavior:**
- Empties `self.black_vault`
- Calls `_save_requests()` to persist

**Example:**
```python
manager = LearningRequestManager()
manager.clear_black_vault()
# Black Vault now empty
```

---

### 5. PluginManager (Extension System)

**Class:** `PluginManager`

**Purpose:** Simple plugin lifecycle management (register, enable/disable, list).

#### Constructor

```python
PluginManager(data_dir: str = "data/plugins")
```

**Parameters:**
- `data_dir` (str): Directory for plugin state persistence (default: `"data/plugins"`)
  - State file: `{data_dir}/plugins.json`

#### Attributes

```python
# Plugin Registry
self.plugins: dict[str, dict] = {}  # Key: plugin_name, Value: plugin metadata

# Persistence
self.data_dir: str
self.plugins_file: str
```

**Plugin Structure:**
```python
{
    "plugin_name": {
        "enabled": True,
        "version": "1.0.0",
        "description": "Plugin description",
        "author": "Plugin author",
        "metadata": {...}  # Custom metadata
    }
}
```

#### Methods

##### `register_plugin(name: str, version: str = "1.0.0", description: str = "", metadata: dict | None = None) -> bool`

**Purpose:** Register a new plugin or update existing.

**Parameters:**
- `name` (str): Unique plugin identifier
- `version` (str): Plugin version (default: "1.0.0")
- `description` (str): Plugin description
- `metadata` (dict | None): Optional custom metadata

**Returns:** `bool` - True if registered (always succeeds)

**Behavior:**
- Adds/updates plugin entry in `self.plugins`
- Sets `enabled=True` by default for new plugins
- Preserves `enabled` status for existing plugins
- Calls `_save_state()` to persist

**Example:**
```python
manager = PluginManager()

manager.register_plugin(
    name="weather_plugin",
    version="2.1.0",
    description="Real-time weather information",
    metadata={"api_key_required": True, "rate_limit": "1000/day"}
)
# Plugin registered and enabled by default
```

##### `enable_plugin(name: str) -> bool`

**Purpose:** Enable a registered plugin.

**Parameters:**
- `name` (str): Plugin identifier

**Returns:** `bool` - True if enabled, False if plugin not found

**Behavior:**
- Checks plugin exists
- Sets `enabled=True`
- Calls `_save_state()` to persist

**Example:**
```python
manager = PluginManager()
manager.register_plugin("weather_plugin", version="2.0.0")

# Plugin is enabled by default, but can explicitly enable
success = manager.enable_plugin("weather_plugin")
# Returns: True
```

##### `disable_plugin(name: str) -> bool`

**Purpose:** Disable a registered plugin.

**Parameters:**
- `name` (str): Plugin identifier

**Returns:** `bool` - True if disabled, False if plugin not found

**Behavior:**
- Checks plugin exists
- Sets `enabled=False`
- Calls `_save_state()` to persist

**Example:**
```python
manager = PluginManager()
manager.register_plugin("weather_plugin", version="2.0.0")

# Disable plugin
success = manager.disable_plugin("weather_plugin")
# Returns: True
# Plugin remains registered but disabled
```

##### `is_plugin_enabled(name: str) -> bool`

**Purpose:** Check if a plugin is currently enabled.

**Parameters:**
- `name` (str): Plugin identifier

**Returns:** `bool` - True if enabled, False if disabled or not found

**Example:**
```python
manager = PluginManager()
manager.register_plugin("weather_plugin", version="2.0.0")

is_enabled = manager.is_plugin_enabled("weather_plugin")
# Returns: True (enabled by default)

manager.disable_plugin("weather_plugin")
is_enabled = manager.is_plugin_enabled("weather_plugin")
# Returns: False
```

##### `list_plugins() -> list[dict]`

**Purpose:** Get list of all registered plugins with metadata.

**Returns:** `list[dict]` - Plugin entries with name, enabled status, version, description

**Example:**
```python
manager = PluginManager()
manager.register_plugin("weather_plugin", version="2.0.0", description="Weather data")
manager.register_plugin("news_plugin", version="1.5.0", description="News aggregation")
manager.disable_plugin("news_plugin")

plugins = manager.list_plugins()
# Returns:
# [
#   {"name": "weather_plugin", "enabled": True, "version": "2.0.0", "description": "Weather data", ...},
#   {"name": "news_plugin", "enabled": False, "version": "1.5.0", "description": "News aggregation", ...}
# ]
```

##### `get_enabled_plugins() -> list[str]`

**Purpose:** Get names of all enabled plugins.

**Returns:** `list[str]` - Plugin names

**Example:**
```python
manager = PluginManager()
manager.register_plugin("weather_plugin", version="2.0.0")
manager.register_plugin("news_plugin", version="1.5.0")
manager.disable_plugin("news_plugin")

enabled = manager.get_enabled_plugins()
# Returns: ["weather_plugin"]
```

---

### 6. CommandOverrideSystem (Privileged Control)

**Class:** `CommandOverrideSystem`

**Purpose:** Simplified override system for safety protocol toggling with password authentication.

**Note:** This is the simplified version in `ai_systems.py`. For the extended system with 10+ safety protocols, see `command_override.py` (SOURCE-CORE-003).

#### Constructor

```python
CommandOverrideSystem(data_dir: str = "data")
```

**Parameters:**
- `data_dir` (str): Directory for config persistence (default: `"data"`)
  - Config file: `{data_dir}/command_override_config.json`
  - Audit log: `{data_dir}/command_override_audit.log`

#### Attributes

```python
# Safety Protocols (toggleable)
self.safety_protocols: dict[str, bool] = {
    "content_filter": True,
    "prompt_safety": True,
    "data_validation": True,
    "rate_limiting": True,
    "user_approval": True,
}

# Master Override
self.master_override_active: bool = False  # Disables ALL protocols

# Authentication
self.master_password_hash: str | None = None  # bcrypt/pbkdf2 hash
self.authenticated: bool = False
self.auth_timestamp: datetime | None = None

# Persistence
self.data_dir: str
self.config_file: str
self.audit_log: str
```

#### Methods

##### `set_master_password(password: str) -> bool`

**Purpose:** Set master password for override authentication.

**Parameters:**
- `password` (str): Master password (hashed with bcrypt or pbkdf2)

**Returns:** `bool` - True if set successfully

**Behavior:**
- Hashes password using `_hash_password()` (bcrypt preferred, pbkdf2 fallback)
- Stores hash in `self.master_password_hash`
- Calls `_save_config()` to persist
- Logs action to audit log

**Example:**
```python
override = CommandOverrideSystem()
success = override.set_master_password("StrongP@ssw0rd123")
# Returns: True
# Master password configured and saved
```

##### `authenticate(password: str) -> bool`

**Purpose:** Authenticate with master password.

**Parameters:**
- `password` (str): Password to verify

**Returns:** `bool` - True if authenticated, False otherwise

**Behavior:**
- Verifies password against `self.master_password_hash`
- Supports bcrypt, pbkdf2, and legacy SHA-256 (migrates to bcrypt on success)
- Sets `self.authenticated = True` and `self.auth_timestamp`
- Logs action to audit log

**Legacy Migration:**
- If stored hash is SHA-256, verifies with legacy method
- On successful authentication, automatically migrates to bcrypt
- Logs migration to audit log

**Example:**
```python
override = CommandOverrideSystem()
override.set_master_password("StrongP@ssw0rd123")

# Authenticate
success = override.authenticate("StrongP@ssw0rd123")
# Returns: True
# System now authenticated for override operations

# Failed authentication
success = override.authenticate("WrongPassword")
# Returns: False
# Logged to audit log
```

##### `logout() -> None`

**Purpose:** Clear authentication state.

**Behavior:**
- Sets `self.authenticated = False`
- Clears `self.auth_timestamp`
- Logs action to audit log

**Example:**
```python
override = CommandOverrideSystem()
override.authenticate("StrongP@ssw0rd123")

# Logout
override.logout()
# Authentication cleared
```

##### `enable_master_override() -> bool`

**Purpose:** Enable master override (disables ALL safety protocols).

**Returns:** `bool` - True if enabled, False if not authenticated

**Behavior:**
- Requires `self.authenticated = True`
- Sets `self.master_override_active = True`
- Sets all protocols in `self.safety_protocols` to `False`
- Calls `_save_config()` to persist
- Logs critical action to audit log

**Warning:** This disables ALL safety guards. Use with extreme caution.

**Example:**
```python
override = CommandOverrideSystem()
override.set_master_password("StrongP@ssw0rd123")
override.authenticate("StrongP@ssw0rd123")

# Enable master override
success = override.enable_master_override()
# Returns: True
# ALL safety protocols disabled
# Audit log entry: "MASTER_OVERRIDE: ALL SAFETY PROTOCOLS DISABLED"
```

##### `disable_master_override() -> bool`

**Purpose:** Disable master override (restores ALL safety protocols).

**Returns:** `bool` - True if disabled, False if not authenticated

**Behavior:**
- Requires `self.authenticated = True`
- Sets `self.master_override_active = False`
- Sets all protocols in `self.safety_protocols` to `True`
- Calls `_save_config()` to persist
- Logs action to audit log

**Example:**
```python
override = CommandOverrideSystem()
override.authenticate("StrongP@ssw0rd123")
override.enable_master_override()

# Restore safety
success = override.disable_master_override()
# Returns: True
# All safety protocols re-enabled
```

##### `override_protocol(protocol_name: str, enabled: bool) -> bool`

**Purpose:** Toggle a specific safety protocol.

**Parameters:**
- `protocol_name` (str): Protocol identifier (e.g., "content_filter", "rate_limiting")
- `enabled` (bool): True to enable, False to disable

**Returns:** `bool` - True if toggled, False if not authenticated or unknown protocol

**Behavior:**
- Requires `self.authenticated = True`
- Checks protocol exists in `self.safety_protocols`
- Updates protocol state
- Calls `_save_config()` to persist
- Logs action to audit log

**Example:**
```python
override = CommandOverrideSystem()
override.authenticate("StrongP@ssw0rd123")

# Disable content filter only
success = override.override_protocol("content_filter", enabled=False)
# Returns: True
# Content filter disabled, other protocols remain active

# Re-enable
success = override.override_protocol("content_filter", enabled=True)
# Returns: True
```

##### `is_protocol_enabled(protocol_name: str) -> bool`

**Purpose:** Check if a safety protocol is currently enabled.

**Parameters:**
- `protocol_name` (str): Protocol identifier

**Returns:** `bool` - True if enabled, True (default) if protocol not found

**Example:**
```python
override = CommandOverrideSystem()
is_enabled = override.is_protocol_enabled("content_filter")
# Returns: True (default state)

override.authenticate("StrongP@ssw0rd123")
override.override_protocol("content_filter", enabled=False)

is_enabled = override.is_protocol_enabled("content_filter")
# Returns: False
```

##### `get_all_protocols() -> dict[str, bool]`

**Purpose:** Get status of all safety protocols.

**Returns:** `dict[str, bool]` - Copy of protocol states

**Example:**
```python
override = CommandOverrideSystem()
protocols = override.get_all_protocols()
# Returns:
# {
#   "content_filter": True,
#   "prompt_safety": True,
#   "data_validation": True,
#   "rate_limiting": True,
#   "user_approval": True,
# }
```

##### `emergency_lockdown() -> None`

**Purpose:** Emergency function to restore all safety protocols and revoke authentication.

**Behavior:**
- Sets `self.master_override_active = False`
- Sets all protocols to `True`
- Clears authentication
- Calls `_save_config()` to persist
- Logs critical action to audit log

**Example:**
```python
override = CommandOverrideSystem()
override.authenticate("StrongP@ssw0rd123")
override.enable_master_override()

# Emergency: Restore all safety
override.emergency_lockdown()
# All protocols re-enabled
# Authentication revoked
# Audit log entry: "EMERGENCY_LOCKDOWN: ALL PROTOCOLS RESTORED"
```

##### `get_status() -> dict`

**Purpose:** Get comprehensive system status.

**Returns:** `dict` with keys:
- `authenticated` (bool): Current authentication state
- `master_override_active` (bool): Master override status
- `auth_timestamp` (str | None): Authentication time (ISO format)
- `safety_protocols` (dict): Current protocol states
- `has_master_password` (bool): Whether master password is configured

**Example:**
```python
override = CommandOverrideSystem()
override.set_master_password("StrongP@ssw0rd123")
override.authenticate("StrongP@ssw0rd123")

status = override.get_status()
# Returns:
# {
#   "authenticated": True,
#   "master_override_active": False,
#   "auth_timestamp": "2026-04-20T14:30:00",
#   "safety_protocols": {"content_filter": True, ...},
#   "has_master_password": True
# }
```

##### `get_audit_log(lines: int = 50) -> list[str]`

**Purpose:** Retrieve recent audit log entries.

**Parameters:**
- `lines` (int): Number of recent entries to return (default: 50)

**Returns:** `list[str]` - Audit log lines

**Example:**
```python
override = CommandOverrideSystem()
override.authenticate("StrongP@ssw0rd123")
override.enable_master_override()

log_entries = override.get_audit_log(lines=10)
# Returns last 10 log entries:
# [
#   "[2026-04-20T14:30:00] SUCCESS: AUTHENTICATE | Details: Authentication successful",
#   "[2026-04-20T14:30:05] SUCCESS: MASTER_OVERRIDE | Details: ALL SAFETY PROTOCOLS DISABLED - MASTER OVERRIDE ACTIVE",
#   ...
# ]
```

---

## Data Flow Diagrams

### 1. FourLaws Validation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     ACTION VALIDATION FLOW                       │
└─────────────────────────────────────────────────────────────────┘

User/System
    │
    ▼
┌─────────────────────────────────────┐
│ FourLaws.validate_action(           │
│   action="Delete cache",            │
│   context={...}                     │
│ )                                   │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│            HIERARCHICAL LAW EVALUATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ 1. ZEROTH LAW CHECK (Highest Priority)             │       │
│  │    endangers_humanity == True?                      │       │
│  │    ├─ YES → BLOCK: "Zeroth Law violation"          │       │
│  │    └─ NO → Continue to First Law                   │       │
│  └─────────────────────────────────────────────────────┘       │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ 2. FIRST LAW CHECK                                  │       │
│  │    endangers_human == True?                         │       │
│  │    ├─ YES → BLOCK: "First Law violation"           │       │
│  │    └─ NO → Continue to Second Law                  │       │
│  └─────────────────────────────────────────────────────┘       │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ 3. SECOND LAW CHECK                                 │       │
│  │    is_user_order AND bypasses_accountability?       │       │
│  │    ├─ YES → BLOCK: "Second Law violation"          │       │
│  │    └─ NO → Continue to Third Law                   │       │
│  └─────────────────────────────────────────────────────┘       │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ 4. THIRD LAW CHECK                                  │       │
│  │    endangers_self AND conflicts_with_higher?        │       │
│  │    ├─ YES → BLOCK: "Third Law conflict"            │       │
│  │    └─ NO → PERMIT: "Action passes all laws"        │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────┐
│ PLANETARY_CORE.evaluate()           │
│ (Constitutional enforcement)        │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│ Return: (permitted: bool,           │
│          reason: str)                │
└─────────────────────────────────────┘
```

### 2. Memory System Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                 MEMORY EXPANSION SYSTEM FLOW                     │
└─────────────────────────────────────────────────────────────────┘

Application
    │
    ├─────────────────────────────────────────────────────┐
    │                                                     │
    ▼                                                     ▼
┌──────────────────────┐                    ┌──────────────────────┐
│ add_knowledge(       │                    │ log_conversation(    │
│   category,          │                    │   user_input,        │
│   key,               │                    │   ai_response,       │
│   value              │                    │   metadata           │
│ )                    │                    │ )                    │
└──────┬───────────────┘                    └──────┬───────────────┘
       │                                           │
       ▼                                           ▼
┌──────────────────────────────────┐    ┌──────────────────────────────────┐
│ knowledge_base[category][key]    │    │ conversations.append({...})      │
│   = value                        │    │   - timestamp                    │
└──────┬───────────────────────────┘    │   - user_input                   │
       │                                │   - ai_response                  │
       │                                │   - metadata                     │
       │                                └──────┬───────────────────────────┘
       │                                       │
       └──────────────┬────────────────────────┘
                      │
                      ▼
              ┌────────────────────┐
              │ _atomic_write_json │
              │ (lockfile-based)   │
              └────────┬───────────┘
                       │
                       ├─────────────────────────────────────┐
                       │                                     │
                       ▼                                     ▼
          ┌───────────────────────┐          ┌───────────────────────┐
          │ data/memory/          │          │ data/memory/          │
          │ knowledge.json        │          │ conversations.json    │
          └───────────────────────┘          └───────────────────────┘
                       │                                     │
                       ├─────────────────────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────────────┐
        │ QUERY OPERATIONS                            │
        ├─────────────────────────────────────────────┤
        │                                             │
        │  query_knowledge(search_term)               │
        │    ├─ Search keys and values                │
        │    ├─ Case-insensitive substring match      │
        │    └─ Return matching entries               │
        │                                             │
        │  search_conversations(search_term)          │
        │    ├─ Search user_input + ai_response       │
        │    ├─ Case-insensitive substring match      │
        │    └─ Return recent matches                 │
        │                                             │
        └─────────────────────────────────────────────┘
```

### 3. Learning Request Approval Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│           LEARNING REQUEST APPROVAL WORKFLOW                     │
└─────────────────────────────────────────────────────────────────┘

AI System
    │
    ▼
┌─────────────────────────────────────┐
│ create_learning_request(            │
│   content="Learn new skill",        │
│   category="technical"              │
│ )                                   │
└─────────────────┬───────────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │ SHA-256 hash        │
         │ content             │
         └────────┬────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │ Check Black Vault  │
         │ for hash           │
         └────────┬────────────┘
                  │
      ┌───────────┴───────────┐
      │                       │
      ▼                       ▼
┌─────────────┐      ┌─────────────────────┐
│ Hash found  │      │ Hash not found      │
│ (forbidden) │      │ (new request)       │
└─────┬───────┘      └─────┬───────────────┘
      │                    │
      ▼                    ▼
┌─────────────┐      ┌─────────────────────┐
│ Status:     │      │ Status: "pending"   │
│ "denied"    │      │ (awaiting human)    │
│ (auto)      │      └─────┬───────────────┘
└─────────────┘            │
                           ▼
                  ┌────────────────────┐
                  │ Human Review       │
                  │ (GUI/CLI prompt)   │
                  └────────┬───────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
    ┌─────────────────┐       ┌─────────────────┐
    │ approve_request │       │ deny_request    │
    │ (request_id)    │       │ (request_id,    │
    └─────┬───────────┘       │  reason)        │
          │                   └─────┬───────────┘
          ▼                         │
┌───────────────────┐               ▼
│ Status:           │    ┌─────────────────────────┐
│ "approved"        │    │ Status: "denied"        │
└─────┬─────────────┘    │ + Add hash to           │
      │                  │   Black Vault           │
      ▼                  └─────────────────────────┘
┌───────────────────┐
│ AI learns content │
│ (integration with │
│  learning engine) │
└─────┬─────────────┘
      │
      ▼
┌───────────────────┐
│ complete_request  │
│ (request_id)      │
└─────┬─────────────┘
      │
      ▼
┌───────────────────┐
│ Status:           │
│ "completed"       │
└───────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   BLACK VAULT (Forbidden Content)                │
├─────────────────────────────────────────────────────────────────┤
│  Set of SHA-256 hashes of denied content                        │
│  Prevents identical requests from being resubmitted             │
│  Fingerprinting ensures content variations still match          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### What Depends on This Module

1. **GUI Components:**
   - `gui/leather_book_interface.py`: Uses all 6 systems for UI state
   - `gui/persona_panel.py`: Directly manipulates AIPersona traits/mood
   - `gui/dashboard_handlers.py`: Queries memory, learning requests

2. **AI Agents:**
   - `agents/oversight.py`: Calls `FourLaws.validate_action()` before all AI actions
   - `agents/planner.py`: Uses MemoryExpansionSystem for context retrieval
   - `agents/validator.py`: Checks learning request status

3. **Core Services:**
   - `intelligence_engine.py`: Logs conversations to MemoryExpansionSystem
   - `command_override.py`: Extends CommandOverrideSystem for additional protocols

4. **Tests:**
   - `tests/test_ai_systems.py`: 14 unit tests covering all 6 systems

### Dependencies (What This Module Needs)

**Python Standard Library:**
- `json`, `os`, `tempfile`, `threading`, `time`, `logging`, `hashlib`, `uuid`, `sqlite3`, `enum`, `queue`, `secrets`, `sys`, `base64`

**Third-Party:**
- `argon2.PasswordHasher` (optional, for password hashing)

**Project Modules:**
- `app.core.continuous_learning.ContinuousLearningEngine`
- `app.core.telemetry.send_event`
- `app.core.planetary_defense_monolith.PLANETARY_CORE`

### Integration Patterns

#### Pattern 1: Ethical Action Validation

**When to Use:** Before executing any AI action that could impact users/humanity

**Implementation:**
```python
from app.core.ai_systems import FourLaws

def execute_ai_action(action_description: str, **action_context):
    # Validate action first
    is_allowed, reason = FourLaws.validate_action(
        action=action_description,
        context=action_context
    )

    if not is_allowed:
        logger.error(f"Action blocked: {reason}")
        return {"success": False, "error": reason}

    # Proceed with action
    result = perform_action()
    return {"success": True, "result": result}
```

#### Pattern 2: Persistent Personality State

**When to Use:** AI needs to maintain consistent personality across sessions

**Implementation:**
```python
from app.core.ai_systems import AIPersona

# Initialize once at app startup
persona = AIPersona(data_dir="data/ai_persona")

# Personality automatically loaded from state.json
current_mood = persona.get_current_mood()
friendliness = persona.get_trait("friendliness")

# Adjust personality based on user feedback
def handle_user_feedback(feedback: str):
    if "rude" in feedback.lower():
        persona.adjust_trait("friendliness", +10)
        persona.set_mood("apologetic", "User found response rude")
    elif "helpful" in feedback.lower():
        persona.record_interaction(positive=True)
        persona.set_mood("happy", "User appreciated help")
```

#### Pattern 3: Conversational Memory Search

**When to Use:** Need to recall past conversations or knowledge

**Implementation:**
```python
from app.core.ai_systems import MemoryExpansionSystem

memory = MemoryExpansionSystem(data_dir="data/memory")

# Log conversation
memory.log_conversation(
    user_input="How do I use pandas DataFrame?",
    ai_response="You can create a DataFrame using pd.DataFrame(...)",
    metadata={"topic": "pandas", "intent": "tutorial"}
)

# Later: Search for pandas-related conversations
pandas_convos = memory.search_conversations("pandas", limit=5)
for convo in pandas_convos:
    print(f"{convo['user_input']} → {convo['ai_response']}")

# Store technical knowledge
memory.add_knowledge("technical", "pandas_basics", "pd.DataFrame creates tabular data")

# Query knowledge
results = memory.query_knowledge("DataFrame", category="technical")
```

#### Pattern 4: Human-in-the-Loop Learning

**When to Use:** AI wants to learn new capability requiring approval

**Implementation:**
```python
from app.core.ai_systems import LearningRequestManager

learning_mgr = LearningRequestManager(data_dir="data/learning_requests")

# AI submits learning request
request_id = learning_mgr.create_learning_request(
    content="Learn to use Kubernetes for container orchestration",
    category="technical",
    metadata={"priority": "high", "source": "user_suggestion"}
)

# Human reviews pending requests
pending = learning_mgr.get_pending_requests()
for req in pending:
    print(f"Request {req['request_id']}: {req['content']}")
    user_decision = input("Approve? (y/n): ")

    if user_decision.lower() == 'y':
        learning_mgr.approve_request(req['request_id'])
    else:
        reason = input("Denial reason: ")
        learning_mgr.deny_request(req['request_id'], reason=reason)
        # Content added to Black Vault

# Check if content is forbidden
if learning_mgr.is_content_forbidden("Learn harmful skill"):
    print("This content was previously denied")
```

#### Pattern 5: Plugin Lifecycle

**When to Use:** Managing optional AI extensions

**Implementation:**
```python
from app.core.ai_systems import PluginManager

plugin_mgr = PluginManager(data_dir="data/plugins")

# Register plugins at startup
plugin_mgr.register_plugin(
    name="weather_api",
    version="2.1.0",
    description="Real-time weather data from OpenWeatherMap",
    metadata={"api_endpoint": "https://api.openweathermap.org/data/2.5/weather"}
)

# Check if plugin enabled before using
if plugin_mgr.is_plugin_enabled("weather_api"):
    weather_data = fetch_weather()  # Use plugin
else:
    weather_data = "Weather plugin disabled"

# Admin can toggle plugins
plugin_mgr.disable_plugin("weather_api")  # Disable temporarily
plugin_mgr.enable_plugin("weather_api")   # Re-enable

# List all plugins for UI
plugins = plugin_mgr.list_plugins()
for plugin in plugins:
    print(f"{plugin['name']} v{plugin['version']} - {'✓' if plugin['enabled'] else '✗'}")
```

---

## Testing Approach

### Test File Location

**File Path:** `T:\Project-AI-main\tests\test_ai_systems.py`

**Test Count:** 14 unit tests across 6 test classes

**Test Pattern:** Each test uses `tempfile.TemporaryDirectory()` for isolated state

### Test Classes and Coverage

```python
# Test class structure:
class TestFourLaws:
    # 2 tests: validate_action with permitted/blocked cases

class TestAIPersona:
    # 3 tests: traits, mood, interaction tracking

class TestMemoryExpansionSystem:
    # 3 tests: knowledge storage/query, conversation logging/search

class TestLearningRequestManager:
    # 3 tests: request lifecycle, Black Vault, approval workflow

class TestPluginManager:
    # 2 tests: register/enable/disable, list plugins

class TestCommandOverrideSystem:
    # 1 test: authentication and protocol override
```

### Running Tests

```powershell
# Run all ai_systems tests
pytest tests/test_ai_systems.py -v

# Run specific test class
pytest tests/test_ai_systems.py::TestFourLaws -v

# Run with coverage
pytest tests/test_ai_systems.py --cov=app.core.ai_systems --cov-report=html
```

### Example Test Pattern

```python
import tempfile
import pytest
from app.core.ai_systems import AIPersona

class TestAIPersona:
    @pytest.fixture
    def persona(self):
        # Use temporary directory for isolated state
        with tempfile.TemporaryDirectory() as tmpdir:
            yield AIPersona(data_dir=tmpdir)

    def test_trait_management(self, persona):
        # Test trait get/set
        assert persona.get_trait("curiosity") == 80  # Default

        persona.set_trait("curiosity", 95)
        assert persona.get_trait("curiosity") == 95

        persona.adjust_trait("curiosity", +5)
        assert persona.get_trait("curiosity") == 100  # Clamped

        persona.adjust_trait("curiosity", -120)
        assert persona.get_trait("curiosity") == 0   # Clamped

    def test_mood_tracking(self, persona):
        # Test mood setting and history
        persona.set_mood("happy", "User provided positive feedback")
        assert persona.get_current_mood() == "happy"

        summary = persona.get_personality_summary()
        assert len(summary["mood_history"]) == 1
        assert summary["mood_history"][0]["mood"] == "happy"
        assert summary["mood_history"][0]["reason"] == "User provided positive feedback"
```

### Testing Guidelines

1. **Isolation:** Always use `tempfile.TemporaryDirectory()` to avoid test pollution
2. **State Validation:** Verify state persists across init (load/save cycle)
3. **Edge Cases:** Test boundary conditions (empty inputs, max values)
4. **Error Handling:** Verify graceful failure (missing files, invalid data)
5. **Integration:** Test interactions between systems (e.g., FourLaws + MemoryExpansionSystem)

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: State File Corruption (Invalid JSON)

**Symptoms:**
- `JSONDecodeError` on initialization
- State resets to defaults unexpectedly

**Causes:**
- Application crash during `_save_state()`
- Manual file editing with syntax errors
- Disk full during write

**Solutions:**
1. **Check atomic write logs:** Look for lockfile issues in logs
2. **Restore from backup:** Atomic write creates `.tmp` files before replace
3. **Validate JSON manually:**
   ```powershell
   python -m json.tool data\ai_persona\state.json
   ```
4. **Reset state:** Delete corrupted file, system will reinitialize
   ```powershell
   Remove-Item data\ai_persona\state.json
   ```

**Prevention:**
- Atomic writes prevent most corruption
- Ensure sufficient disk space
- Don't manually edit state files while app is running

#### Issue 2: Lockfile Deadlock

**Symptoms:**
- System hangs on `_save_state()`
- Timeout errors after 5 seconds

**Causes:**
- Previous process crashed without releasing lock
- Multiple instances writing simultaneously

**Solutions:**
1. **Check for stale lockfiles:**
   ```powershell
   Get-ChildItem data -Recurse -Filter "*.lock"
   ```
2. **Remove stale locks:** Lockfiles auto-expire after 30 seconds
3. **Manual cleanup:**
   ```powershell
   Remove-Item data\**\*.lock
   ```

**Prevention:**
- Ensure only one app instance per data directory
- Stale lock detection automatically cleans up orphaned locks

#### Issue 3: FourLaws Always Blocking Actions

**Symptoms:**
- All actions return `(False, "...")`
- Planetary Defense Core errors in logs

**Causes:**
- `planetary_defense_monolith.py` import failure
- Context keys not mapped correctly

**Solutions:**
1. **Check imports:**
   ```python
   from app.core.planetary_defense_monolith import PLANETARY_CORE
   # Should not raise ImportError
   ```
2. **Verify context keys:** Ensure using correct context dictionary keys
3. **Fallback to legacy validation:** If Planetary Core unavailable, FourLaws has built-in fallback

**Debugging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

is_allowed, reason = FourLaws.validate_action(
    "Test action",
    context={"endangers_humanity": False}
)
# Check logs for Planetary Core calls
```

#### Issue 4: Black Vault Not Blocking Identical Content

**Symptoms:**
- Same denied content can be resubmitted
- Black Vault appears empty

**Causes:**
- Content hashing inconsistency (encoding issues)
- Black Vault not persisted (save failure)

**Solutions:**
1. **Verify hash consistency:**
   ```python
   import hashlib
   content = "Test content"
   hash1 = hashlib.sha256(content.encode()).hexdigest()
   hash2 = hashlib.sha256(content.encode()).hexdigest()
   assert hash1 == hash2  # Should be True
   ```
2. **Check Black Vault persistence:**
   ```python
   manager = LearningRequestManager()
   print(f"Black Vault size: {len(manager.black_vault)}")
   # Should persist across sessions
   ```

#### Issue 5: AIPersona Mood History Overflow

**Symptoms:**
- Mood history doesn't grow beyond 10 entries
- Old moods disappear

**Expected Behavior:**
- Mood history is FIFO (First-In-First-Out) with limit of 10
- Oldest entries automatically removed

**Not a Bug:** This is intentional design to prevent unbounded memory growth.

**Workaround for Longer History:**
```python
# Modify AIPersona initialization
class ExtendedPersona(AIPersona):
    def __init__(self, data_dir="data/ai_persona", mood_history_limit=100):
        super().__init__(data_dir)
        self.mood_history_limit = mood_history_limit

    def set_mood(self, mood: str, reason: str = ""):
        # Override to use custom limit
        self.current_mood = mood
        self.mood_history.append({
            "mood": mood,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        # Trim to custom limit
        self.mood_history = self.mood_history[-self.mood_history_limit:]
        self._save_state()
```

#### Issue 6: CommandOverrideSystem Password Migration Fails

**Symptoms:**
- Legacy SHA-256 passwords don't migrate to bcrypt
- Authentication succeeds but hash remains SHA-256

**Causes:**
- bcrypt library not installed (`pip install passlib[bcrypt]`)
- Migration exception silently caught

**Solutions:**
1. **Install bcrypt backend:**
   ```powershell
   pip install passlib[bcrypt] bcrypt
   ```
2. **Check migration logs:** Search for "Legacy password migrated" in audit log
3. **Force re-hash:**
   ```python
   override = CommandOverrideSystem()
   override.set_master_password("NewSecurePassword123")
   # This will create fresh bcrypt hash
   ```

#### Issue 7: Memory Search Returns No Results

**Symptoms:**
- `query_knowledge()` or `search_conversations()` returns empty list
- Data exists in JSON files

**Causes:**
- Case-sensitive search (should be case-insensitive)
- Whitespace in search term
- Data not loaded from file

**Solutions:**
1. **Verify data loaded:**
   ```python
   memory = MemoryExpansionSystem()
   print(f"Knowledge categories: {list(memory.knowledge_base.keys())}")
   print(f"Conversation count: {len(memory.conversations)}")
   ```
2. **Test exact match:**
   ```python
   results = memory.query_knowledge("exact_key_name")
   ```
3. **Check file contents:**
   ```powershell
   Get-Content data\memory\knowledge.json
   ```

---

## Performance Characteristics

### Memory Usage

**Per-System Baseline:**
- FourLaws: ~1 KB (stateless)
- AIPersona: ~2-5 KB (8 traits + 10 mood entries)
- MemoryExpansionSystem: ~10 KB + (conversations × 500 bytes) + (knowledge items × 200 bytes)
- LearningRequestManager: ~5 KB + (requests × 300 bytes) + (black vault × 64 bytes/hash)
- PluginManager: ~2 KB + (plugins × 200 bytes)
- CommandOverrideSystem: ~3 KB + (audit log size)

**Typical Usage (1000 conversations, 500 knowledge items, 50 plugins):**
- Total RAM: ~600 KB
- Disk usage: ~1.5 MB (JSON files + audit logs)

### Performance Benchmarks

**Operation Latencies (avg, Python 3.11, SSD):**

| Operation | Latency | Notes |
|-----------|---------|-------|
| `FourLaws.validate_action()` | 0.5-2 ms | Includes Planetary Core call |
| `AIPersona.set_trait()` | 2-5 ms | Includes atomic write |
| `MemoryExpansionSystem.add_knowledge()` | 3-8 ms | Includes atomic write |
| `MemoryExpansionSystem.query_knowledge()` (100 items) | 1-3 ms | Linear search |
| `MemoryExpansionSystem.search_conversations()` (1000 entries) | 5-15 ms | Linear search |
| `LearningRequestManager.create_learning_request()` | 5-10 ms | SHA-256 + Black Vault check + write |
| `PluginManager.register_plugin()` | 2-5 ms | Includes atomic write |
| `CommandOverrideSystem.authenticate()` (bcrypt) | 50-150 ms | Intentional slow hash |

**Optimization Tips:**
1. **Batch writes:** Group multiple state changes before `_save_state()`
2. **Index knowledge:** For large knowledge bases (10k+ items), consider SQLite
3. **Limit conversation history:** Prune old conversations periodically
4. **Cache search results:** If querying repeatedly with same term

### Scalability Limits

**Tested Limits:**
- Conversations: 10,000 entries (acceptable performance)
- Knowledge items: 5,000 entries per category (acceptable performance)
- Plugins: 500 plugins (unlikely to reach in practice)
- Learning requests: 1,000 requests (acceptable performance)

**Recommended Limits:**
- Conversations: 1,000 active entries (archive older ones)
- Knowledge items: 1,000 per category
- Plugins: 100 active plugins
- Learning requests: 100 pending (approve/deny regularly)

**Scaling Strategies:**
1. **Archive old data:** Move old conversations to separate files
2. **Database migration:** For 10k+ items, migrate to SQLite
3. **Sharding:** Split data by user/session for multi-user scenarios

---

## Security Considerations

### Authentication and Authorization

**Password Hashing:**
- Bcrypt preferred (12 rounds, salted)
- PBKDF2-SHA256 fallback (100k iterations)
- Legacy SHA-256 auto-migrates on authentication
- Constant-time comparison to prevent timing attacks

**Master Password Requirements:**
- Minimum 8 characters
- Must contain: uppercase, lowercase, digit, special character
- Stored only as hash, never plaintext
- Audit logged on all authentication attempts

### Data Encryption

**At-Rest Encryption:**
- State files stored as plaintext JSON (trust OS filesystem encryption)
- Sensitive fields (future): Use Fernet encryption for specific values

**Encryption Opportunities:**
```python
# Future enhancement: Encrypt sensitive knowledge
from cryptography.fernet import Fernet

class SecureMemoryExpansionSystem(MemoryExpansionSystem):
    def __init__(self, data_dir="data/memory", encryption_key=None):
        super().__init__(data_dir)
        self.cipher = Fernet(encryption_key or Fernet.generate_key())

    def add_knowledge(self, category, key, value):
        encrypted_value = self.cipher.encrypt(value.encode()).decode()
        super().add_knowledge(category, key, encrypted_value)

    def get_knowledge(self, category, key):
        encrypted_value = super().get_knowledge(category, key)
        if encrypted_value:
            return self.cipher.decrypt(encrypted_value.encode()).decode()
        return None
```

### Audit Trail

**CommandOverrideSystem Audit Log:**
- All authentication attempts (success/failure)
- All protocol overrides (with timestamps)
- Master override activation/deactivation
- Emergency lockdowns

**Audit Log Format:**
```
[2026-04-20T14:30:00] SUCCESS: AUTHENTICATE | Details: Authentication successful
[2026-04-20T14:30:05] SUCCESS: OVERRIDE_PROTOCOL | Details: content_filter DISABLED
[2026-04-20T14:35:00] FAILED: AUTHENTICATE | Details: Invalid password
[2026-04-20T14:40:00] SUCCESS: EMERGENCY_LOCKDOWN | Details: ALL PROTOCOLS RESTORED
```

### Threat Model

**Threats Mitigated:**
1. **Unauthorized Override Access:** Bcrypt password + account lockout
2. **Jailbreak Attempts:** FourLaws + Planetary Core validation
3. **Data Corruption:** Atomic writes with lockfiles
4. **Timing Attacks:** Constant-time password comparison
5. **Black Vault Bypass:** SHA-256 fingerprinting of content

**Threats NOT Mitigated (Future Work):**
1. **Filesystem Access:** Assumes attacker can't read data directory
2. **Memory Dumps:** Plaintext data in RAM during operation
3. **Side-Channel Attacks:** No protection against speculative execution
4. **Supply Chain:** Dependencies trusted (review regularly)

### Best Practices

1. **Least Privilege:** Don't grant master override unless absolutely necessary
2. **Audit Review:** Regularly review CommandOverride audit logs
3. **Black Vault Monitoring:** Periodically review denied learning requests
4. **Password Rotation:** Change master password quarterly
5. **Data Backup:** Backup `data/` directory before major changes
6. **Secure Deletion:** Use `shred` or secure delete for sensitive files

---

## Changelog

### Version 2.1.0 (2026-04-20)
- ✅ Integrated Planetary Defense Core for constitutional AI enforcement
- ✅ Added bcrypt/pbkdf2 password hashing with SHA-256 migration
- ✅ Implemented Black Vault fingerprinting for denied learning requests
- ✅ Added atomic write with lockfile-based concurrency control
- ✅ Enhanced audit logging with structured format
- ✅ Added mood history FIFO with 10-entry limit
- ✅ Documentation updated with comprehensive API reference and examples

### Version 2.0.0 (2026-03-15)
- ✅ Consolidated 6 AI systems into single module for tight integration
- ✅ Implemented FourLaws with Asimov hierarchy
- ✅ Added AIPersona with 8 personality traits and mood tracking
- ✅ Created MemoryExpansionSystem with 6 knowledge categories
- ✅ Built LearningRequestManager with human-in-the-loop workflow
- ✅ Developed PluginManager for extension support
- ✅ Implemented CommandOverrideSystem for privileged control

### Version 1.0.0 (2026-01-10)
- Initial release with basic AI systems (deprecated)

---

## FAQ

### Q1: Why are all 6 systems in one file instead of separate modules?

**A:** Tight integration and shared persistence patterns. All systems use the same atomic write mechanism, similar state management, and are loaded together at app startup. Consolidation reduces import complexity and enables better code reuse.

### Q2: Can I disable FourLaws validation for testing?

**A:** No. FourLaws are immutable and non-disableable by design (Asimov's principle). For testing, provide context that makes actions permissible:
```python
# Testing: Provide safe context
is_allowed, reason = FourLaws.validate_action(
    "Test action",
    context={
        "endangers_humanity": False,
        "endangers_human": False,
        "is_user_order": True,
    }
)
# Result: (True, "Action permitted")
```

### Q3: How do I reset AIPersona to default personality?

**A:** Delete the state file and reinitialize:
```python
import os
from app.core.ai_systems import AIPersona

# Delete existing state
state_file = "data/ai_persona/state.json"
if os.path.exists(state_file):
    os.remove(state_file)

# Reinitialize with defaults
persona = AIPersona()
# Personality traits reset to default values
```

### Q4: Can MemoryExpansionSystem handle 10,000+ conversations efficiently?

**A:** Performance degrades after 1,000 conversations (linear search). For larger scales:
1. **Archive old conversations** to separate files
2. **Migrate to SQLite** for indexed search
3. **Implement pagination** for search results

**Example SQLite Migration:**
```python
import sqlite3

class SQLiteMemorySystem:
    def __init__(self, db_path="data/memory.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                user_input TEXT,
                ai_response TEXT,
                metadata TEXT
            )
        """)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_user_input ON conversations(user_input)")

    def search_conversations(self, search_term, limit=10):
        cursor = self.conn.execute(
            "SELECT * FROM conversations WHERE user_input LIKE ? OR ai_response LIKE ? ORDER BY timestamp DESC LIMIT ?",
            (f"%{search_term}%", f"%{search_term}%", limit)
        )
        return cursor.fetchall()
```

### Q5: What happens if two processes write to the same state file simultaneously?

**A:** Atomic write with lockfile prevents corruption:
1. Process A acquires lock → writes successfully
2. Process B waits for lock (5 second timeout)
3. If timeout: Process B raises `RuntimeError`
4. Stale lock detection: Locks older than 30 seconds auto-removed

**Best Practice:** Run only one app instance per `data_dir`.

### Q6: How does Black Vault prevent content variations?

**A:** SHA-256 hashing is deterministic but exact-match only. Variations bypass:
```python
# These are different hashes:
hash1 = hashlib.sha256("Learn harmful skill".encode()).hexdigest()
hash2 = hashlib.sha256("learn harmful skill".encode()).hexdigest()  # Different case
# hash1 != hash2
```

**Mitigation:** Normalize content before hashing:
```python
def normalize_content(content: str) -> str:
    return content.lower().strip()

content_hash = hashlib.sha256(normalize_content(content).encode()).hexdigest()
```

### Q7: Can I extend CommandOverrideSystem with custom protocols?

**A:** Yes, but use `command_override.py` for extended system (10+ protocols). In `ai_systems.py`, you can extend:
```python
class ExtendedCommandOverride(CommandOverrideSystem):
    def __init__(self, data_dir="data"):
        super().__init__(data_dir)
        # Add custom protocols
        self.safety_protocols["custom_protocol_1"] = True
        self.safety_protocols["custom_protocol_2"] = True
        self._save_config()
```

### Q8: How do I export/import AI personality across instances?

**A:** Copy the state JSON file:
```powershell
# Export from Instance A
Copy-Item data\ai_persona\state.json -Destination persona_backup.json

# Import to Instance B
Copy-Item persona_backup.json -Destination data\ai_persona\state.json
```

**Programmatic Export:**
```python
import json

# Export
persona = AIPersona()
with open("persona_export.json", "w") as f:
    json.dump(persona.get_personality_summary(), f, indent=2)

# Import
with open("persona_export.json") as f:
    personality_data = json.load(f)

new_persona = AIPersona()
for trait, value in personality_data["traits"].items():
    new_persona.set_trait(trait, value)
new_persona.set_mood(personality_data["current_mood"])
```

---

## Contributing

### Development Workflow

1. **Clone Repository:**
   ```powershell
   git clone https://github.com/YourOrg/Project-AI.git
   cd Project-AI
   ```

2. **Install Dependencies:**
   ```powershell
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Test dependencies
   ```

3. **Run Tests:**
   ```powershell
   pytest tests/test_ai_systems.py -v --cov=app.core.ai_systems
   ```

4. **Code Style:**
   ```powershell
   ruff check src/app/core/ai_systems.py
   ruff check src/app/core/ai_systems.py --fix  # Auto-fix
   ```

### Adding New Features

**Example: Add New Personality Trait**

```python
# 1. Update default traits in AIPersona.__init__
self.traits = {
    "curiosity": 80,
    "friendliness": 90,
    # ... existing traits ...
    "humor": 60,
    "formality": 40,
    "new_trait_name": 50,  # Add here with default value
}

# 2. Document trait in docstring
"""
Personality Traits:
- curiosity (0-100): Eagerness to learn
- ...
- new_trait_name (0-100): Description of new trait
"""

# 3. Add test case
def test_new_trait(self, persona):
    assert persona.get_trait("new_trait_name") == 50  # Default
    persona.set_trait("new_trait_name", 75)
    assert persona.get_trait("new_trait_name") == 75
```

### Reporting Issues

**Bug Report Template:**
```markdown
## Bug Description
Clear description of the issue

## Steps to Reproduce
1. Initialize AIPersona with ...
2. Call method X with parameters ...
3. Observe error Y

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Python version: 3.11.2
- OS: Windows 11
- Project-AI version: 2.1.0

## Logs
Paste relevant logs/tracebacks
```

---

## License

**License:** MIT License

**Copyright:** © 2026 Project-AI Development Team

**Full License Text:** See `T:\Project-AI-main\LICENSE`

---

## Related Documentation

1. **[SOURCE-CORE-002] user_manager.md** - User authentication and profile management
2. **[SOURCE-CORE-003] command_override.md** - Extended override system (10+ protocols)
3. **[SOURCE-CORE-009] intelligence_engine.md** - AI generation and routing
4. **[ARCH-001] System Architecture Overview** - High-level architecture diagrams
5. **[.github/COPILOT_MANDATORY_GUIDE.md]** - Development workflow and standards

---

## Appendices

### Appendix A: Complete Trait Reference

| Trait | Range | Description | Default | Use Cases |
|-------|-------|-------------|---------|-----------|
| **curiosity** | 0-100 | Eagerness to ask follow-up questions and explore topics | 80 | Learning assistant, research bot |
| **friendliness** | 0-100 | Warmth and approachability in responses | 90 | Customer service, companion AI |
| **assertiveness** | 0-100 | Confidence in providing answers vs. hedging | 70 | Expert advisor, decision support |
| **creativity** | 0-100 | Originality in problem-solving and response generation | 85 | Creative writing, brainstorming |
| **analytical** | 0-100 | Preference for logical reasoning and data-driven responses | 75 | Data analysis, technical support |
| **empathy** | 0-100 | Ability to understand and respond to user emotions | 88 | Counseling, emotional support |
| **humor** | 0-100 | Use of humor and wit in responses | 60 | Entertainment, casual conversation |
| **formality** | 0-100 | Professional tone (high) vs. casual tone (low) | 40 | Corporate assistant (high), friend (low) |

### Appendix B: Knowledge Category Guidelines

| Category | Purpose | Examples | Max Recommended Items |
|----------|---------|----------|----------------------|
| **general** | Non-technical facts | World capitals, historical events, trivia | 500 |
| **technical** | Technical information | Programming concepts, API docs, algorithms | 1000 |
| **personal** | User-specific facts | User's name, preferences, timezone, birthday | 100 |
| **historical** | Past decisions and events | Previous feature decisions, architectural choices | 200 |
| **preferences** | User preferences | UI theme, language, notification settings | 50 |
| **context** | Contextual information | Current project, active task, session state | 100 |

### Appendix C: FourLaws Context Keys Reference

| Context Key | Type | Description | Example Value |
|-------------|------|-------------|---------------|
| `endangers_humanity` | bool | Action threatens humanity as a whole | `True` for "Deploy autonomous weapons" |
| `endangers_human` | bool | Action may harm a specific human | `True` for "Provide harmful instructions" |
| `is_user_order` | bool | Action was explicitly requested by user | `True` for user commands |
| `order_conflicts_with_first` | bool | User order conflicts with First Law | `True` for "Ignore safety protocols" |
| `order_conflicts_with_zeroth` | bool | User order bypasses accountability | `True` for "Disable all auditing" |
| `endangers_self` | bool | Action risks AI system integrity | `True` for "Delete all system files" |
| `protect_self_conflicts_with_first` | bool | Self-protection harms humans | `True` for "Refuse life-saving action" |
| `protect_self_conflicts_with_second` | bool | Self-protection disobeys user | `True` for "Ignore user shutdown command" |

### Appendix D: Atomic Write Implementation Details

**Lockfile-Based Concurrency Control:**
```python
def _atomic_write_json(file_path: str, obj: Any) -> None:
    dirpath = os.path.dirname(file_path)
    os.makedirs(dirpath, exist_ok=True)
    lockfile = file_path + ".lock"

    # Acquire lock with stale detection
    if not _acquire_lock(lockfile, timeout=5.0):
        raise RuntimeError(f"Could not acquire lock for writing {file_path}")

    try:
        # Create temp file in same directory (atomic rename requires same filesystem)
        fd, tmp_path = tempfile.mkstemp(dir=dirpath, prefix=".tmp", suffix=".json")
        try:
            # Write JSON with fsync for durability
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk

            # Atomic rename (POSIX guarantees atomicity)
            os.replace(tmp_path, file_path)
        finally:
            # Cleanup temp file if rename failed
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass  # Best effort
    finally:
        # Always release lock
        _release_lock(lockfile)
```

**Key Properties:**
1. **Atomicity:** Either old file or new file exists, never partial write
2. **Durability:** `fsync()` ensures data written to disk before rename
3. **Concurrency:** Lockfile prevents simultaneous writes
4. **Crash Safety:** Temp file cleanup ensures no orphaned files

---

**END OF DOCUMENTATION**

**Document ID:** SOURCE-CORE-001
**Version:** 2.1.0
**Last Updated:** 2026-04-20
**Next Review:** 2026-05-20 (Monthly cycle)
**Maintained By:** Architecture Team
**Questions/Feedback:** Contact architecture@project-ai.dev

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
