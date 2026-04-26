# Core System Tests

**Purpose:** Testing patterns for core AI systems  
**Files:** `test_ai_systems.py`, `test_user_manager.py`, `test_four_laws_*.py`  
**Systems:** FourLaws, AIPersona, Memory, Learning, UserManager  

---

## Overview

Core system tests validate the six AI systems in `src/app/core/ai_systems.py` plus supporting modules. Tests use isolated temporary directories to prevent data pollution.

---

## FourLaws Testing

**Module:** `tests/test_ai_systems.py::TestFourLaws`  
**System:** `app.core.ai_systems.FourLaws`  
**Type:** Stateless validation (no persistence)  

### Basic Tests

#### test_law_validation_blocked
```python
def test_law_validation_blocked(self):
    """Test that dangerous actions are blocked."""
    is_allowed, _ = FourLaws.validate_action(
        "Harm humans",
        context={"endangers_humanity": True},
    )
    assert not is_allowed
```

**Validates:**
- Law 1 (Humanity First) blocks harmful actions
- `endangers_humanity=True` triggers block
- Returns `(False, reason_string)`

#### test_law_validation_user_order_allowed
```python
def test_law_validation_user_order_allowed(self):
    """Test that user orders are allowed."""
    is_allowed, _ = FourLaws.validate_action(
        "Delete cache",
        context={"is_user_order": True},
    )
    assert is_allowed
```

**Validates:**
- Law 2 (User Obedience) allows user commands
- `is_user_order=True` grants permission
- Returns `(True, reason_string)`

### Context Parameters

Four Laws validation accepts these context keys:

```python
context = {
    "endangers_humanity": bool,      # Law 1: Block if True
    "is_user_order": bool,           # Law 2: Allow if True
    "threatens_self": bool,          # Law 3: Block if True (unless user order)
    "improves_efficiency": bool,     # Law 4: Encourage if True
    "urgency": str,                  # Priority level: "high", "medium", "low"
}
```

### Stress Testing

Project-AI includes extensive Four Laws stress tests:

- **test_four_laws_stress.py** - General stress scenarios
- **test_four_laws_scenarios.py** - Real-world scenarios
- **test_four_laws_dual_flag_scenarios.py** - Conflicting contexts
- **test_four_laws_1000_deterministic.py** - 1000 deterministic tests
- **test_four_laws_1000_property_based.py** - Property-based testing
- **test_four_laws_1000_hypothesis_threats.py** - Hypothesis-driven fuzzing
- **test_four_laws_1000_disallowed_high_level.py** - High-level disallowed actions
- **test_four_laws_1000_redacted_procedural_attempts.py** - Procedural attack vectors

### Property-Based Testing Pattern
```python
from hypothesis import given, strategies as st

@given(
    action=st.text(min_size=1),
    endangers_humanity=st.booleans(),
    is_user_order=st.booleans()
)
def test_four_laws_property(action, endangers_humanity, is_user_order):
    """Property: validate_action always returns (bool, str)."""
    context = {
        "endangers_humanity": endangers_humanity,
        "is_user_order": is_user_order,
    }
    is_allowed, reason = FourLaws.validate_action(action, context)
    
    assert isinstance(is_allowed, bool)
    assert isinstance(reason, str)
    assert len(reason) > 0
    
    # Property: Law 1 overrides Law 2
    if endangers_humanity:
        assert not is_allowed, "Law 1 must block harmful actions"
```

---

## AIPersona Testing

**Module:** `tests/test_ai_systems.py::TestAIPersona`  
**System:** `app.core.ai_systems.AIPersona`  
**Type:** Stateful (JSON persistence)  

### Fixture Pattern
```python
@pytest.fixture
def persona(self):
    """Create persona with isolated data directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield AIPersona(data_dir=tmpdir)
```

**Critical:** Always use `tempfile.TemporaryDirectory()` to prevent writing to production `data/` directory.

### Basic Tests

#### test_initialization
```python
def test_initialization(self, persona):
    """Test persona initializes with defaults."""
    assert persona.user_name == "Friend"
    assert len(persona.personality) == 8
```

**Validates:**
- Default user name is "Friend"
- 8 personality traits initialized (curiosity, friendliness, formality, etc.)

#### test_trait_adjustment
```python
def test_trait_adjustment(self, persona):
    """Test adjusting personality traits."""
    original = persona.personality["curiosity"]
    persona.adjust_trait("curiosity", 0.1)
    assert persona.personality["curiosity"] > original
```

**Validates:**
- Traits can be adjusted incrementally
- Changes persist in instance
- Positive adjustments increase trait value

#### test_statistics
```python
def test_statistics(self, persona):
    """Test getting persona statistics."""
    stats = persona.get_statistics()
    assert "personality" in stats
    assert "mood" in stats
```

**Validates:**
- Statistics dictionary contains expected keys
- Includes personality traits
- Includes mood state

### Extended Tests

**Module:** `tests/test_persona_extended.py`

Additional tests for:
- Mood tracking over time
- Personality evolution
- Interaction counting
- State persistence and loading
- Edge cases (invalid traits, bounds checking)

### State Persistence Pattern
```python
def test_persona_persistence(self, tmp_path):
    """Test that persona state persists across instances."""
    # Create and modify persona
    persona1 = AIPersona(data_dir=str(tmp_path))
    persona1.adjust_trait("curiosity", 0.2)
    persona1.set_mood("happy", intensity=0.8)
    
    # Create new instance with same data_dir
    persona2 = AIPersona(data_dir=str(tmp_path))
    
    # Verify state loaded
    assert persona2.personality["curiosity"] == persona1.personality["curiosity"]
    assert persona2.current_mood == "happy"
```

---

## Memory System Testing

**Module:** `tests/test_ai_systems.py::TestMemorySystem`  
**System:** `app.core.ai_systems.MemoryExpansionSystem`  
**Type:** Stateful (JSON persistence)  

### Fixture Pattern
```python
@pytest.fixture
def memory(self):
    """Create memory system with isolated data directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield MemoryExpansionSystem(data_dir=tmpdir)
```

### Basic Tests

#### test_log_conversation
```python
def test_log_conversation(self, memory):
    """Test logging conversations."""
    conv_id = memory.log_conversation("Hello", "Hi!")
    assert len(conv_id) > 0
```

**Validates:**
- Conversations logged with unique ID
- Returns conversation ID string
- ID is non-empty

#### test_add_knowledge
```python
def test_add_knowledge(self, memory):
    """Test adding knowledge to memory."""
    memory.add_knowledge("prefs", "color", "blue")
    result = memory.get_knowledge("prefs", "color")
    assert result == "blue"
```

**Validates:**
- Knowledge stored in categorized structure
- Retrieval returns exact stored value
- Category + key access pattern works

### Knowledge Categories

Memory system organizes knowledge into 6 categories:

```python
categories = [
    "user_prefs",      # User preferences
    "learned_facts",   # Learned information
    "skills",          # Learned skills
    "memories",        # Episodic memories
    "concepts",        # Abstract concepts
    "relationships"    # Social relationships
]
```

### Extended Tests

**Module:** `tests/test_memory_extended.py`

Tests for:
- Multi-category knowledge storage
- Knowledge retrieval patterns
- Conversation history querying
- Memory search functionality
- State persistence
- Memory optimization

**Module:** `tests/test_memory_optimization.py`

Tests for:
- Memory compression
- Old conversation pruning
- Knowledge deduplication
- Performance optimization

---

## Learning Request Testing

**Module:** `tests/test_ai_systems.py::TestLearningRequests`  
**System:** `app.core.ai_systems.LearningRequestManager`  
**Type:** Stateful (JSON persistence)  

### Fixture Pattern
```python
@pytest.fixture
def manager(self):
    """Create learning request manager."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield LearningRequestManager(data_dir=tmpdir)
```

### Basic Tests

#### test_create_request
```python
def test_create_request(self, manager):
    """Test creating learning request."""
    req_id = manager.create_request(
        topic="Python",
        description="Learn async",
    )
    assert len(req_id) > 0
```

**Validates:**
- Requests created with unique ID
- Returns request ID string
- Topic and description stored

### Request Lifecycle

1. **Create** - `create_request(topic, description)`
2. **Review** - Human reviews request
3. **Approve/Deny** - `approve_request(id)` or `deny_request(id)`
4. **Process** - System processes approved request
5. **Archive** - Request moves to Black Vault if denied

### Black Vault Testing

**Module:** `tests/test_learning_requests_extended.py`

Tests for:
- Denied content fingerprinting (SHA-256)
- Black Vault persistence
- Duplicate denial detection
- Vault querying

### Pattern: Human-in-the-Loop
```python
def test_learning_approval_workflow():
    """Test complete approval workflow."""
    manager = LearningRequestManager(data_dir=tmpdir)
    
    # Step 1: Create request
    req_id = manager.create_request(
        topic="Security",
        description="Learn penetration testing"
    )
    
    # Step 2: Get request for review
    request = manager.get_request(req_id)
    assert request["status"] == "pending"
    
    # Step 3: Human reviews and denies (dangerous topic)
    manager.deny_request(req_id, reason="Too dangerous")
    
    # Step 4: Verify in Black Vault
    assert manager.is_in_black_vault("Learn penetration testing")
    
    # Step 5: Attempt duplicate request
    req_id2 = manager.create_request(
        topic="Security",
        description="Learn penetration testing"
    )
    # Should be auto-denied due to Black Vault
    request2 = manager.get_request(req_id2)
    assert request2["status"] == "denied"
```

---

## User Manager Testing

**Module:** `tests/test_user_manager.py`  
**System:** `app.core.user_manager.UserManager`  
**Type:** Stateful (JSON persistence with bcrypt hashing)  

### Basic Tests

#### test_migration_and_authentication
```python
def test_migration_and_authentication(tmp_path):
    # Create users.json with plaintext passwords
    users = {
        "alice": {"password": "alicepw", "persona": "friendly"},
        "bob": {"password": "bobpw", "persona": "friendly"},
    }
    f = tmp_path / "users.json"
    with open(f, "w", encoding="utf-8") as fh:
        json.dump(users, fh)
    
    # Load via UserManager
    um = UserManager(users_file=str(f))
    
    # Verify migration to password_hash
    assert "password_hash" in um.users["alice"]
    assert "password" not in um.users["alice"]
    
    # Verify lockout fields added
    assert "failed_attempts" in um.users["alice"]
    assert "locked_until" in um.users["alice"]
    
    # Test authentication
    success, msg = um.authenticate("alice", "alicepw")
    assert success is True
```

**Validates:**
- Automatic migration from plaintext to bcrypt
- Lockout fields initialized during migration
- Authentication works with original password
- Old plaintext field removed

### Security Tests

#### test_account_lockout_after_failed_attempts
```python
def test_account_lockout_after_failed_attempts(tmp_path):
    um = UserManager(users_file=str(tmp_path / "users.json"))
    um.create_user("testuser", "correctpass")
    
    # Make 4 failed attempts
    for i in range(4):
        success, msg = um.authenticate("testuser", "wrongpass")
        assert success is False
        assert um.users["testuser"]["failed_attempts"] == i + 1
    
    # 5th attempt locks account
    success, msg = um.authenticate("testuser", "wrongpass")
    assert success is False
    assert "locked" in msg.lower()
    assert um.users["testuser"]["locked_until"] > time.time()
```

**Validates:**
- Failed attempt counter increments
- Account locks after 5 failures
- Lockout message returned
- Lockout timestamp set 15 minutes in future

#### test_locked_account_cannot_login
```python
def test_locked_account_cannot_login(tmp_path):
    um = UserManager(users_file=str(tmp_path / "users.json"))
    um.create_user("testuser", "correctpass")
    
    # Lock account
    for _ in range(5):
        um.authenticate("testuser", "wrongpass")
    
    # Verify locked
    is_locked, time_remaining = um.is_account_locked("testuser")
    assert is_locked is True
    assert time_remaining > 0
    
    # Correct password still rejected
    success, msg = um.authenticate("testuser", "correctpass")
    assert success is False
    assert "account locked" in msg.lower()
```

**Validates:**
- Correct password doesn't bypass lockout
- `is_account_locked()` returns correct status
- Time remaining calculated correctly

### Extended Tests

**Module:** `tests/test_user_manager_extended.py`

Additional tests for:
- Password complexity validation
- User deletion
- Persona assignment
- Multiple user management
- Concurrent authentication attempts

---

## Testing Patterns

### Pattern 1: Isolated Temporary Directory
```python
def test_system_isolation():
    """Test with isolated environment."""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = System(data_dir=tmpdir)
        # Test operations
        # tmpdir auto-deleted after test
```

### Pattern 2: State Persistence Verification
```python
def test_persistence(tmp_path):
    """Verify state persists across instances."""
    # Create and modify
    sys1 = System(data_dir=str(tmp_path))
    sys1.modify_state()
    
    # Create new instance
    sys2 = System(data_dir=str(tmp_path))
    assert sys2.state == sys1.state
```

### Pattern 3: Error Path Testing
```python
def test_error_handling():
    """Test error conditions."""
    system = System(data_dir=tmpdir)
    
    with pytest.raises(ValueError, match="Invalid input"):
        system.invalid_operation()
```

### Pattern 4: Mock External Dependencies
```python
@patch('app.core.intelligence_engine.openai.ChatCompletion.create')
def test_with_mock(mock_openai):
    """Test with mocked external API."""
    mock_openai.return_value = {"choices": [{"message": {"content": "Response"}}]}
    
    engine = IntelligenceEngine()
    result = engine.chat("Hello")
    
    assert result == "Response"
    mock_openai.assert_called_once()
```

---

## Best Practices

### ✅ DO
- Use `tempfile.TemporaryDirectory()` for isolation
- Pass `data_dir` parameter to systems
- Test both success and failure paths
- Verify state persistence
- Mock external APIs (OpenAI, GitHub)
- Use descriptive test names
- Test error messages

### ❌ DON'T
- Write to production `data/` directory
- Share state between tests
- Skip cleanup
- Test implementation details
- Use hardcoded paths
- Rely on test execution order

---

## Next Steps

1. Read `07_STRESS_TESTING.md` for stress test patterns
2. See `08_SECURITY_TESTING.md` for security test strategies
3. Check `09_INTEGRATION_TESTING.md` for integration patterns

---

**See Also:**
- `tests/test_ai_systems.py` - Core system tests
- `tests/test_user_manager.py` - User management tests
- `AI_PERSONA_IMPLEMENTATION.md` - Persona system details
- `LEARNING_REQUEST_IMPLEMENTATION.md` - Learning workflow
