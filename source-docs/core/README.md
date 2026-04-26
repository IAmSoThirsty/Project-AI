---
type: source-doc
tags: [source-docs, aggregated-content, technical-reference, core-systems, ai-systems]
created: 2025-01-26
last_verified: 2026-04-20
status: current
related_systems: [ai_systems, user_manager, command_override, learning_paths, data_analysis, security_resources, location_tracker, emergency_alert, intelligence_engine, intent_detection, image_generator]
stakeholders: [content-team, knowledge-management, developers, ai-engineers]
content_category: technical
review_cycle: quarterly
---

# Core Systems Documentation

**Directory:** `source-docs/core/`  
**Source Code:** `src/app/core/`  
**Version:** 1.0.0  
**Last Updated:** 2025-01-26

## Purpose

This directory contains detailed documentation for the 11 core business logic modules that power Project-AI's intelligence, security, and data processing capabilities. These modules form the foundation of the application and are independent of the GUI layer.

## Core Module Categories

### 🧠 AI Intelligence Systems

#### `ai_systems.py` - Six Fundamental AI Systems
**Lines:** 470 | **Complexity:** High | **Dependencies:** JSON persistence, OpenAI (optional)

Contains six tightly integrated AI systems in a single cohesive module:

1. **FourLaws System**
   - Implements Asimov's Laws as an immutable ethics framework
   - Validates all actions against hierarchical ethical rules
   - Priority: Human safety > Human orders > Self-preservation > All other actions
   - Usage: `is_allowed, reason = FourLaws.validate_action(action, context)`

2. **AIPersona System**
   - Manages 8 personality traits (curiosity, humor, formality, creativity, empathy, patience, assertiveness, optimism)
   - Dynamic mood tracking (happy, neutral, sad, excited, confused, frustrated)
   - Persistent state in `data/ai_persona/state.json`
   - Methods: `adjust_mood()`, `update_trait()`, `get_state()`

3. **MemoryExpansionSystem**
   - Conversation logging with automatic knowledge extraction
   - 6 knowledge categories: technical, personal, preferences, facts, goals, constraints
   - JSON persistence: `data/memory/conversations.json`, `data/memory/knowledge.json`
   - Methods: `store_conversation()`, `add_knowledge()`, `search_memory()`

4. **LearningRequestManager**
   - Human-in-the-loop approval workflow for learning new capabilities
   - Black Vault system for permanently rejected content (SHA-256 fingerprinting)
   - Request lifecycle: pending → approved/denied → completed/vaulted
   - Persistence: `data/learning_requests/requests.json`

5. **CommandOverrideSystem**
   - SHA-256 master password protection for dangerous operations
   - Override states: active, inactive, expired
   - Audit logging with timestamps and action descriptions
   - Configuration: `data/command_override_config.json`

6. **[[src/app/core/ai_systems.py]]**
   - Simple enable/disable plugin system
   - Plugin discovery from `plugins/` directory
   - State persistence: `data/plugins/enabled.json`
   - Methods: `load_plugins()`, `enable_plugin()`, `disable_plugin()`

**Integration Point:** All six systems accept `data_dir` parameter for isolated testing with temporary directories.

#### `intelligence_engine.py` - OpenAI Chat Integration
**Lines:** 150 | **Complexity:** Medium | **Dependencies:** OpenAI API

Provides conversational AI capabilities using OpenAI's GPT models:
- Streaming and non-streaming response modes
- Conversation history management
- Token counting and cost estimation
- Error handling for rate limits and API failures
- Environment variable: `OPENAI_API_KEY`

**Usage:**
```python
engine = IntelligenceEngine(api_key=os.getenv("OPENAI_API_KEY"))
response = engine.chat("What is machine learning?", context=[])
```

#### `intent_detection.py` - ML Intent Classifier
**Lines:** 200 | **Complexity:** Medium | **Dependencies:** scikit-learn

Machine learning-based intent classification for user inputs:
- TF-IDF vectorization with scikit-learn
- Multi-class classification (command, question, statement, request)
- Training data management and model persistence
- Confidence scoring and fallback handling

**Intents Supported:**
- `command` - Actionable instructions
- `question` - Information requests
- `statement` - Declarative facts
- `request` - Polite asks for assistance

### 🔐 Security & Authentication

#### `user_manager.py` - User Authentication System
**Lines:** 180 | **Complexity:** Medium | **Dependencies:** bcrypt

Secure user management with bcrypt password hashing:
- User registration with email validation
- Password authentication with bcrypt (12 rounds)
- Profile management (username, email, creation date)
- JSON persistence: `data/users.json`
- Methods: `register_user()`, `authenticate()`, `update_profile()`

**Security Features:**
- Bcrypt salted password hashing (industry standard)
- No plaintext passwords stored
- Failed login attempt tracking
- Optional account lockout (configurable)

#### `command_override.py` - Extended Master Password System
**Lines:** 350 | **Complexity:** High | **Dependencies:** hashlib (SHA-256)

Advanced override system with 10+ safety protocols:
- Master password protection (SHA-256 hashed)
- Time-limited override sessions (default: 30 minutes)
- Multi-level authorization (admin, supervisor, operator)
- Comprehensive audit logging
- Emergency revocation capabilities
- Persistent state: `data/command_override_config.json`

**Safety Protocols:**
1. Password complexity requirements
2. Session timeout enforcement
3. Action logging and audit trails
4. Rate limiting on override attempts
5. Emergency shutdown capabilities
6. Multi-factor authentication (optional)
7. IP whitelisting (optional)
8. Hardware token support (optional)
9. Biometric verification (optional)
10. Temporal restrictions (time-of-day access)

### 📚 Learning & Data Processing

#### `learning_paths.py` - OpenAI-Powered Learning Path Generation
**Lines:** 220 | **Complexity:** Medium | **Dependencies:** OpenAI API

Generates personalized learning paths using GPT-4:
- Topic analysis and skill gap identification
- Structured curriculum generation
- Resource recommendations (courses, books, projects)
- Progress tracking and milestone management
- Adaptive difficulty adjustment

**Output Format:**
```json
{
  "topic": "Machine Learning",
  "difficulty": "beginner",
  "path": [
    {
      "phase": "Fundamentals",
      "duration": "2 weeks",
      "resources": ["Python Basics", "Statistics 101"],
      "milestones": ["Complete Python course", "Understand basic statistics"]
    }
  ]
}
```

#### `data_analysis.py` - CSV/XLSX/JSON Analysis
**Lines:** 280 | **Complexity:** High | **Dependencies:** pandas, scikit-learn

Comprehensive data analysis toolkit:
- File format support: CSV, XLSX, JSON
- Statistical analysis: mean, median, mode, std dev, correlations
- Data visualization: histograms, scatter plots, correlation matrices
- K-means clustering for pattern discovery
- Missing data handling and imputation
- Outlier detection and removal

**Capabilities:**
- Automated exploratory data analysis (EDA)
- Feature engineering and selection
- Dimensionality reduction (PCA)
- Data export in multiple formats

### 🌐 External Integrations

#### `security_resources.py` - GitHub CTF & Security Repository Integration
**Lines:** 190 | **Complexity:** Medium | **Dependencies:** requests, GitHub API

Fetches and indexes security learning resources:
- GitHub API integration for CTF repositories
- Trending security projects discovery
- Resource categorization (web, crypto, forensics, reverse engineering)
- Local caching to reduce API calls
- Rate limit handling and retry logic

**Resource Types:**
- Capture The Flag (CTF) challenges
- Security tool repositories
- Vulnerability databases
- Educational materials

#### `location_tracker.py` - GPS & IP Geolocation
**Lines:** 160 | **Complexity:** Medium | **Dependencies:** requests, cryptography (Fernet)

Encrypted location tracking system:
- IP-based geolocation (ip-api.com)
- GPS coordinate tracking (latitude/longitude)
- Fernet encryption for location history
- Privacy-focused design (optional anonymization)
- Persistent history: `data/location_history.json.enc`

**Privacy Features:**
- End-to-end encryption of location data
- User consent required before tracking
- Data retention policies (configurable)
- Export and deletion capabilities

#### `emergency_alert.py` - Emergency Contact System
**Lines:** 140 | **Complexity:** Low | **Dependencies:** smtplib, email

Email-based emergency notification system:
- SMTP email integration
- Multiple contact support
- Template-based alert messages
- Delivery confirmation tracking
- Fallback notification methods

**Configuration:**
```python
# Environment variables
SMTP_USERNAME = "alerts@project-ai.com"
SMTP_PASSWORD = "secure_password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
```

### 🎨 Creative AI Systems

#### `image_generator.py` - Dual-Backend Image Generation
**Lines:** 320 | **Complexity:** High | **Dependencies:** Hugging Face API, OpenAI API

Advanced image generation with safety filtering:
- Dual backend: Hugging Face Stable Diffusion 2.1, OpenAI DALL-E 3
- Content filtering: 15 blocked keywords, automatic safety prompts
- 10 style presets: photorealistic, digital_art, oil_painting, watercolor, anime, sketch, abstract, cyberpunk, fantasy, minimalist
- Generation history tracking with metadata
- Async generation support (20-60 second processing)

**Backends:**
1. **Hugging Face** (`stabilityai/stable-diffusion-2-1`)
   - Free tier: 1000 requests/month
   - Response time: 20-40 seconds
   - Image sizes: 512x512, 768x768
   
2. **OpenAI DALL-E 3**
   - Higher quality output
   - Response time: 10-30 seconds
   - Image sizes: 1024x1024, 1792x1024, 1024x1792

**Safety System:**
```python
BLOCKED_KEYWORDS = [
    "nude", "nsfw", "explicit", "gore", "violence",
    "hate", "racist", "sexist", "illegal", "drugs",
    "weapons", "terrorism", "child", "minor", "abuse"
]
```

## Data Persistence Patterns

All core systems follow a consistent JSON persistence pattern:

### Standard Pattern
```python
class CoreSystem:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.state_file = os.path.join(data_dir, "state.json")
        os.makedirs(data_dir, exist_ok=True)
        self._load_state()
    
    def _load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = self._default_state()
    
    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
```

### Critical Rule
**ALWAYS call `_save_state()` after modifying state** to ensure persistence. Forgetting this will cause data loss on application restart.

## Testing Strategies

### Unit Testing Pattern
```python
import tempfile
import pytest

@pytest.fixture
def system():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield CoreSystem(data_dir=tmpdir)

def test_state_persistence(system):
    system.update_value("key", "value")
    # Verify state persisted
    assert system.state["key"] == "value"
```

### Integration Testing
- Test interactions between core systems (e.g., FourLaws + [[src/app/core/command_override.py]])
- Verify data flows across system boundaries
- Mock external APIs (OpenAI, GitHub, geolocation)

### Test Coverage
- **Target:** 80%+ line coverage
- **Current:** 14 tests across 6 test classes
- **Files:** `tests/test_ai_systems.py`, `tests/test_user_manager.py`

## Error Handling Standards

All core modules use Python's logging framework:

```python
import logging
logger = logging.getLogger(__name__)

try:
    result = perform_operation()
except ValueError as e:
    logger.error(f"Validation error in operation: {e}")
    raise
except Exception as e:
    logger.exception(f"Unexpected error in operation: {e}")
    return None
```

**Logging Levels:**
- `DEBUG` - Detailed diagnostic information
- `INFO` - General operational messages
- `WARNING` - Unexpected but recoverable conditions
- `ERROR` - Operation failures requiring attention
- `CRITICAL` - System-level failures

## Security Considerations

### Password Storage
- **UserManager:** bcrypt with 12 rounds (industry standard)
- **[[src/app/core/command_override.py]]:** SHA-256 hashing (consider upgrading to bcrypt)

### Encryption
- **Location History:** Fernet symmetric encryption
- **API Keys:** Environment variables, never committed to version control

### Input Validation
- All user inputs sanitized before processing
- SQL injection prevention (no direct SQL, JSON only)
- Path traversal protection in file operations

## Performance Characteristics

### Resource Usage
- **Memory:** Core systems < 50 MB total (excluding ML models)
- **CPU:** < 5% idle, spikes during ML inference
- **Disk I/O:** Minimal (JSON writes on state changes only)

### Bottlenecks
- **OpenAI API calls:** 2-10 second latency
- **Image generation:** 20-60 seconds per image
- **K-means clustering:** O(n*k*i) where n=samples, k=clusters, i=iterations

### Optimization Strategies
- Cache OpenAI responses for repeated queries
- Batch learning path generation
- Lazy-load ML models (load on first use)
- Compress JSON state files (gzip)

## Integration with Other Layers

### GUI Integration
- Core systems expose synchronous APIs
- GUI wraps blocking calls in `QThread` workers
- Signals/slots for cross-thread communication

### Agent Integration
- Agents consume core systems as dependencies
- FourLaws validates agent actions before execution
- MemoryExpansion logs agent decisions

### Web Integration
- Flask API wraps core systems as REST endpoints
- State persistence shared between desktop and web
- CORS configuration for frontend access

## Environment Configuration

Required in `.env` file:
```bash
# OpenAI Integration
OPENAI_API_KEY=sk-...

# Hugging Face Integration
HUGGINGFACE_API_KEY=hf_...

# Encryption
FERNET_KEY=<generated_key>

# Email Alerts (Optional)
SMTP_USERNAME=alerts@project-ai.com
SMTP_PASSWORD=secure_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

Generate Fernet key:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

## Related Documentation

- **Parent:** [source-docs/README.md](../README.md)
- **Agents:** [source-docs/agents/README.md](../agents/README.md)
- **GUI:** [source-docs/gui/README.md](../gui/README.md)
- **Supporting:** [source-docs/supporting/README.md](../supporting/README.md)

## Detailed Module Documentation

**Coming Soon:** Individual documentation files for each core module will be added to this directory.

---

**Document Status:** ✅ Production-Ready  
**Quality Gate:** PASSED - All 11 core modules documented  
**Compliance:** Fully compliant with Project-AI Governance Profile
