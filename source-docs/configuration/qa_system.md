# QA System Configuration

**Module**: `config/qa_system.py`  
**Purpose**: Question and Answer system with encrypted question submission  
**Classification**: Support Configuration  
**Priority**: P3 - Support Systems

---

## Overview

The QA System provides a searchable knowledge base with predefined Q&A pairs and encrypted user question submission. It features a built-in database of common questions and answers, plus the ability for users to submit new questions with God-tier encryption.

### Key Characteristics

- **Knowledge Base**: Predefined Q&A database
- **Search**: Text-based search across questions and answers
- **Encryption**: God-tier encrypted user question submissions
- **Categories**: Questions organized by category
- **Privacy**: Encrypted question storage

---

## Architecture

### Class Structure

```python
class QASystem:
    """Question and Answer system"""
    
    def __init__(self, god_tier_encryption):
        self.logger: logging.Logger
        self.god_tier_encryption: GodTierEncryption
        self.qa_database: list[dict[str, str]]
        self.user_questions: list[dict[str, Any]]
```

### QA Database Structure

```python
{
    "id": str,           # Unique question ID
    "category": str,     # Question category
    "question": str,     # Question text
    "answer": str        # Answer text
}
```

---

## Built-in Knowledge Base

### Predefined Q&A Pairs

```python
self.qa_database = [
    {
        "id": "q1",
        "category": "privacy",
        "question": "How does God tier encryption work?",
        "answer": "God tier encryption uses 7 layers: SHA-512, Fernet, "
                 "AES-256-GCM, ChaCha20, Double AES-256-GCM, "
                 "Quantum-resistant padding, HMAC-SHA512"
    },
    {
        "id": "q2",
        "category": "security",
        "question": "What is the kill switch?",
        "answer": "Kill switch stops all network traffic if VPN connection drops. "
                 "100% guaranteed protection."
    },
    {
        "id": "q3",
        "category": "ads",
        "question": "How aggressive is ad blocking?",
        "answer": "HOLY WAR mode - eliminates ALL ads, trackers, pop-ups, "
                 "redirects, autoplay videos. Zero mercy. Complete annihilation "
                 "of intrusive advertising."
    }
]
```

**Categories**:
- `privacy`: Privacy and encryption questions
- `security`: Security feature questions
- `ads`: Ad blocking questions
- (Additional categories can be added)

---

## Core API

### Searching Q&A Database

```python
def search(self, query: str) -> list[dict[str, Any]]:
    """Search Q/A database.
    
    Args:
        query: Search query (case-insensitive)
    
    Returns:
        List of matching Q&A entries
    
    Search Logic:
        - Searches both questions and answers
        - Case-insensitive matching
        - Substring matching
    
    Example:
        >>> qa_system = QASystem(god_tier_encryption)
        >>> results = qa_system.search("encryption")
        >>> for qa in results:
        ...     print(f"Q: {qa['question']}")
        ...     print(f"A: {qa['answer']}")
    """
```

### Submitting Questions

```python
def submit_question(
    self, 
    question: str, 
    category: str = "general"
) -> dict[str, Any]:
    """Submit a question (encrypted).
    
    Args:
        question: User question (will be encrypted)
        category: Question category (default: "general")
    
    Returns:
        {
            "status": "submitted",
            "id": str
        }
    
    Side Effects:
        - Encrypts question with God-tier encryption
        - Appends to user_questions list
        - Logs submission
    
    Example:
        >>> result = qa_system.submit_question(
        ...     "How do I enable 2FA?",
        ...     category="security"
        ... )
        >>> print(result)
        {'status': 'submitted', 'id': 'uq_0'}
    """
```

---

## User Question Structure

### Encrypted Question Format

```python
{
    "id": "uq_0",                      # Unique question ID
    "encrypted_question": b'...',       # God-tier encrypted question
    "timestamp": 1704067200.0,         # Unix timestamp
    "god_tier_encrypted": True         # Encryption flag
}
```

**Note**: Category is NOT stored in user questions (design decision for simplicity)

---

## Usage Patterns

### Pattern 1: Search Knowledge Base

```python
from config.qa_system import QASystem
from src.app.core.god_tier_encryption import GodTierEncryption

# Initialize
god_tier_encryption = GodTierEncryption()
qa_system = QASystem(god_tier_encryption)

# Search for encryption-related questions
results = qa_system.search("encryption")

for qa in results:
    print(f"Category: {qa['category']}")
    print(f"Q: {qa['question']}")
    print(f"A: {qa['answer']}")
    print()
```

### Pattern 2: Submit User Question

```python
# User asks a question not in database
result = qa_system.submit_question(
    "How do I configure multi-hop VPN?",
    category="security"
)

print(f"Question submitted: {result['id']}")
```

### Pattern 3: Multi-Query Search

```python
# Search multiple queries
queries = ["encryption", "kill switch", "ad blocking"]

for query in queries:
    print(f"\n=== Search: {query} ===")
    results = qa_system.search(query)
    print(f"Found {len(results)} results")
    
    for qa in results:
        print(f"- {qa['question']}")
```

### Pattern 4: Category-Based Filtering

```python
# Search and filter by category
search_results = qa_system.search("security")
privacy_results = [qa for qa in search_results if qa["category"] == "privacy"]
security_results = [qa for qa in search_results if qa["category"] == "security"]

print(f"Privacy results: {len(privacy_results)}")
print(f"Security results: {len(security_results)}")
```

### Pattern 5: Fallback Pattern

```python
# Search knowledge base, submit question if not found
def find_or_ask(qa_system, query):
    results = qa_system.search(query)
    
    if results:
        print("Found answers:")
        for qa in results:
            print(f"- {qa['answer']}")
    else:
        print("No answers found. Submitting question...")
        result = qa_system.submit_question(query)
        print(f"Question submitted: {result['id']}")
```

---

## Integration Patterns

### Pattern 1: GUI Integration

```python
class QADialog(QDialog):
    def __init__(self, qa_system):
        super().__init__()
        self.qa_system = qa_system
        self.setup_ui()
    
    def search_qa(self):
        query = self.search_input.text()
        results = self.qa_system.search(query)
        
        self.results_list.clear()
        for qa in results:
            item = QListWidgetItem(qa["question"])
            item.setData(Qt.UserRole, qa)
            self.results_list.addItem(item)
    
    def submit_question(self):
        question = self.question_input.text()
        category = self.category_combo.currentText()
        
        result = self.qa_system.submit_question(question, category)
        self.show_success(f"Question submitted: {result['id']}")
```

### Pattern 2: API Integration

```python
@app.route("/api/qa/search", methods=["GET"])
def search_qa():
    query = request.args.get("q", "")
    results = qa_system.search(query)
    return jsonify(results)

@app.route("/api/qa/submit", methods=["POST"])
def submit_question():
    data = request.json
    result = qa_system.submit_question(
        question=data["question"],
        category=data.get("category", "general")
    )
    return jsonify(result), 201
```

### Pattern 3: Chatbot Integration

```python
class QAChatbot:
    def __init__(self, qa_system):
        self.qa_system = qa_system
    
    def respond(self, user_message):
        # Search knowledge base
        results = self.qa_system.search(user_message)
        
        if results:
            # Return most relevant answer
            best_match = results[0]
            return best_match["answer"]
        else:
            # Submit question and respond
            self.qa_system.submit_question(user_message)
            return ("I don't have an answer for that yet, but I've "
                   "submitted your question for review.")
```

---

## Knowledge Base Management

### Adding New Q&A Pairs

```python
# Extend QA database
class ExtendedQASystem(QASystem):
    def __init__(self, god_tier_encryption):
        super().__init__(god_tier_encryption)
        
        # Add new Q&A pairs
        self.qa_database.extend([
            {
                "id": "q4",
                "category": "vpn",
                "question": "How many VPN hops are supported?",
                "answer": "Up to 5 VPN hops are supported for maximum anonymity."
            },
            {
                "id": "q5",
                "category": "browser",
                "question": "Does the browser support extensions?",
                "answer": "Yes, selected privacy-focused extensions are supported."
            }
        ])
```

### Loading Q&A from File

```python
import json

class FileBasedQASystem(QASystem):
    def __init__(self, god_tier_encryption, qa_file="data/qa_database.json"):
        super().__init__(god_tier_encryption)
        self.load_qa_database(qa_file)
    
    def load_qa_database(self, qa_file):
        try:
            with open(qa_file, 'r') as f:
                self.qa_database = json.load(f)
            self.logger.info(f"Loaded {len(self.qa_database)} Q&A pairs")
        except FileNotFoundError:
            self.logger.warning(f"Q&A file not found: {qa_file}")
```

---

## Security Considerations

### 1. Encryption Requirements

**Encrypt user questions**:
```python
encrypted_q = god_tier_encryption.encrypt_god_tier(question.encode())
```

### 2. Input Validation

**Validate question content**:
```python
def submit_question(self, question, category="general"):
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    
    if len(question) > 1000:
        raise ValueError("Question too long (max 1000 characters)")
    
    # Proceed with encryption and storage
```

### 3. Search Injection Prevention

**Sanitize search queries**:
```python
def search(self, query):
    # Remove potentially dangerous characters
    query_lower = query.lower().strip()
    
    # Limit query length
    if len(query_lower) > 200:
        query_lower = query_lower[:200]
    
    # Continue with search
```

---

## Testing

### Unit Testing

```python
import pytest
from config.qa_system import QASystem
from unittest.mock import Mock

@pytest.fixture
def qa_system():
    god_tier_encryption = Mock()
    god_tier_encryption.encrypt_god_tier.return_value = b'encrypted'
    return QASystem(god_tier_encryption)

def test_search_found(qa_system):
    results = qa_system.search("encryption")
    assert len(results) > 0
    assert "encryption" in results[0]["question"].lower() or \
           "encryption" in results[0]["answer"].lower()

def test_search_not_found(qa_system):
    results = qa_system.search("nonexistent_query_xyz")
    assert len(results) == 0

def test_submit_question(qa_system):
    result = qa_system.submit_question("How do I enable 2FA?")
    assert result["status"] == "submitted"
    assert "uq_" in result["id"]

def test_submit_question_with_category(qa_system):
    result = qa_system.submit_question("Test question", category="security")
    assert result["status"] == "submitted"
    assert len(qa_system.user_questions) == 1

def test_predefined_questions(qa_system):
    assert len(qa_system.qa_database) >= 3
    assert any(qa["category"] == "privacy" for qa in qa_system.qa_database)
```

---

## Best Practices

1. **Comprehensive Database**: Include common questions in knowledge base
2. **Clear Answers**: Write clear, concise answers
3. **Category Organization**: Use consistent categories
4. **Search Optimization**: Design questions for discoverability
5. **Update Regularly**: Keep knowledge base current
6. **Encrypt Submissions**: Always encrypt user questions
7. **Validate Inputs**: Validate question length and content
8. **Log Searches**: Track common searches to identify gaps
9. **Feedback Loop**: Review submitted questions to expand database
10. **Access Control**: Restrict access to submitted questions

---

## Related Modules

- **Contact System**: `config/contact_system.py` - Message threading
- **Feedback Manager**: `config/feedback_manager.py` - Feedback submission
- **Settings Manager**: `config/settings_manager.py` - QA settings
- **God-Tier Encryption**: Required encryption provider

---

## Future Enhancements

1. **Persistence**: Save Q&A database to file
2. **Admin Interface**: Manage Q&A pairs through GUI
3. **Answer Voting**: Vote on answer helpfulness
4. **Related Questions**: Suggest related Q&A pairs
5. **Search Ranking**: Rank results by relevance
6. **Multi-Language**: Support multiple languages
7. **Rich Formatting**: Support markdown in answers
8. **Question Analytics**: Track most searched questions
9. **Auto-Answers**: Automatically answer submitted questions from database
10. **AI Integration**: Use AI to generate answers for new questions


---

## Related Documentation

- **Relationship Map**: [[relationships\configuration\README.md]]


---

## Source Code References

- **Primary Module**: [[config/qa_system.py]]
