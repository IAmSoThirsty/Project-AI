# Contact System Configuration

**Module**: `config/contact_system.py`  
**Purpose**: Encrypted message threading system for support communication  
**Classification**: Support Configuration  
**Priority**: P3 - Support Systems

---

## Overview

The Contact System provides encrypted message threading for support categories including improvements, features, code of conduct suggestions, and security reports. All messages are encrypted with God-tier encryption before storage.

### Key Characteristics

- **Encryption**: God-tier 7-layer encryption for all messages
- **Threading**: Organized by category threads
- **Categories**: 4 predefined support categories
- **Metadata**: Timestamp and encryption status per message
- **Privacy**: No plaintext message storage

---

## Architecture

### Class Structure

```python
class ContactSystem:
    """Contact and messaging system"""
    
    def __init__(self, god_tier_encryption):
        self.logger: logging.Logger
        self.god_tier_encryption: GodTierEncryption
        self.threads: dict[str, list[dict[str, Any]]]
```

### Thread Categories

```python
self.threads = {
    "improvements": [],      # System improvement suggestions
    "features": [],          # Feature requests
    "code_of_conduct": [],  # Code of conduct suggestions
    "security": []           # Security vulnerability reports
}
```

---

## Core API

### Sending Messages

```python
def send_message(self, thread: str, message: str) -> dict[str, Any]:
    """Send a message (encrypted).
    
    Args:
        thread: Thread category (improvements, features, code_of_conduct, security)
        message: Message content (will be encrypted)
    
    Returns:
        {
            "status": "sent",
            "id": str,
            "thread": str
        }
    
    Error Returns:
        {
            "error": "Unknown thread: {thread}"
        }
    
    Side Effects:
        - Encrypts message with God-tier encryption
        - Appends to thread
        - Logs operation
    
    Example:
        >>> contact = ContactSystem(god_tier_encryption)
        >>> result = contact.send_message("security", "Found XSS vulnerability")
        >>> print(result)
        {'status': 'sent', 'id': 'msg_0', 'thread': 'security'}
    """
```

### Retrieving Threads

```python
def get_thread(self, thread: str) -> list[dict[str, Any]]:
    """Get messages in a thread.
    
    Args:
        thread: Thread category
    
    Returns:
        List of encrypted messages:
        [
            {
                "id": str,
                "encrypted_content": bytes,
                "timestamp": float,
                "god_tier_encrypted": bool
            },
            ...
        ]
    
    Note:
        Returns copy of thread - modifications don't affect stored messages
    
    Example:
        >>> messages = contact.get_thread("security")
        >>> for msg in messages:
        ...     print(f"Message {msg['id']} at {msg['timestamp']}")
    """
```

---

## Message Structure

### Encrypted Message Format

```python
{
    "id": "msg_0",                      # Unique message ID
    "encrypted_content": b'...',         # God-tier encrypted message
    "timestamp": 1704067200.0,          # Unix timestamp
    "god_tier_encrypted": True          # Encryption flag
}
```

**Fields**:
- `id`: Auto-generated message ID (format: `msg_{index}`)
- `encrypted_content`: Encrypted message bytes
- `timestamp`: Unix timestamp (seconds since epoch)
- `god_tier_encrypted`: Always `True` for this system

---

## Usage Patterns

### Pattern 1: Reporting Security Issue

```python
from config.contact_system import ContactSystem
from src.app.core.god_tier_encryption import GodTierEncryption

# Initialize
god_tier_encryption = GodTierEncryption()
contact = ContactSystem(god_tier_encryption)

# Send security report
result = contact.send_message(
    thread="security",
    message="SQL injection vulnerability in /api/users endpoint"
)

print(f"Report submitted: {result['id']}")
```

### Pattern 2: Feature Request

```python
# Send feature request
result = contact.send_message(
    thread="features",
    message="Add dark mode support for dashboard"
)

if result.get("status") == "sent":
    print(f"Feature request submitted: {result['id']}")
```

### Pattern 3: Retrieving Thread

```python
# Get all security messages
security_messages = contact.get_thread("security")

print(f"Total security reports: {len(security_messages)}")

for msg in security_messages:
    # Decrypt message
    decrypted = god_tier_encryption.decrypt_god_tier(msg["encrypted_content"])
    message_text = decrypted.decode()
    
    # Process message
    print(f"{msg['id']}: {message_text}")
```

### Pattern 4: Multi-Category Messaging

```python
# Send to multiple categories
categories = ["improvements", "features", "code_of_conduct"]
base_message = "User feedback: "

for category in categories:
    message = f"{base_message}Specific to {category}"
    result = contact.send_message(category, message)
    print(f"Sent to {category}: {result['id']}")
```

### Pattern 5: Error Handling

```python
# Handle invalid thread
result = contact.send_message("invalid_thread", "message")

if "error" in result:
    print(f"Error: {result['error']}")
    # Fall back to default thread
    result = contact.send_message("improvements", "message")
```

---

## Integration Patterns

### Pattern 1: GUI Integration

```python
class ContactDialog(QDialog):
    def __init__(self, contact_system):
        super().__init__()
        self.contact_system = contact_system
        
    def send_message(self):
        thread = self.thread_selector.currentText()
        message = self.message_field.toPlainText()
        
        result = self.contact_system.send_message(thread, message)
        
        if result.get("status") == "sent":
            self.show_success(f"Message sent: {result['id']}")
        else:
            self.show_error(result.get("error", "Unknown error"))
```

### Pattern 2: API Integration

```python
@app.route("/api/contact", methods=["POST"])
def send_contact_message():
    data = request.json
    thread = data.get("thread")
    message = data.get("message")
    
    result = contact_system.send_message(thread, message)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result), 201
```

### Pattern 3: Admin Dashboard

```python
class AdminDashboard:
    def __init__(self, contact_system, god_tier_encryption):
        self.contact_system = contact_system
        self.god_tier_encryption = god_tier_encryption
    
    def view_thread(self, thread_name):
        messages = self.contact_system.get_thread(thread_name)
        
        decrypted_messages = []
        for msg in messages:
            content = self.god_tier_encryption.decrypt_god_tier(
                msg["encrypted_content"]
            )
            decrypted_messages.append({
                "id": msg["id"],
                "content": content.decode(),
                "timestamp": msg["timestamp"]
            })
        
        return decrypted_messages
```

---

## Security Considerations

### 1. Encryption Requirements

**All messages encrypted**:
```python
# Message never stored in plaintext
encrypted_msg = god_tier_encryption.encrypt_god_tier(message.encode())
```

**Decryption only when needed**:
```python
# Decrypt on-demand
content = god_tier_encryption.decrypt_god_tier(msg["encrypted_content"])
```

### 2. Thread Validation

**Validate thread before use**:
```python
if thread not in self.threads:
    return {"error": f"Unknown thread: {thread}"}
```

### 3. Access Control

**Restrict thread access**:
```python
class SecureContactSystem(ContactSystem):
    def get_thread(self, thread, user_role):
        if thread == "security" and user_role != "admin":
            raise PermissionError("Security thread requires admin access")
        return super().get_thread(thread)
```

---

## Testing

### Unit Testing

```python
import pytest
from config.contact_system import ContactSystem
from unittest.mock import Mock

@pytest.fixture
def contact_system():
    god_tier_encryption = Mock()
    god_tier_encryption.encrypt_god_tier.return_value = b'encrypted'
    return ContactSystem(god_tier_encryption)

def test_send_message(contact_system):
    result = contact_system.send_message("security", "test message")
    
    assert result["status"] == "sent"
    assert result["thread"] == "security"
    assert "msg_" in result["id"]

def test_invalid_thread(contact_system):
    result = contact_system.send_message("invalid", "test")
    
    assert "error" in result
    assert "Unknown thread" in result["error"]

def test_get_thread(contact_system):
    # Send messages
    contact_system.send_message("security", "msg1")
    contact_system.send_message("security", "msg2")
    
    # Get thread
    messages = contact_system.get_thread("security")
    
    assert len(messages) == 2
    assert messages[0]["id"] == "msg_0"
    assert messages[1]["id"] == "msg_1"

def test_multiple_threads(contact_system):
    contact_system.send_message("security", "sec1")
    contact_system.send_message("features", "feat1")
    
    sec_messages = contact_system.get_thread("security")
    feat_messages = contact_system.get_thread("features")
    
    assert len(sec_messages) == 1
    assert len(feat_messages) == 1
```

---

## Best Practices

1. **Always Encrypt**: Never bypass encryption for messages
2. **Thread Validation**: Validate thread names before use
3. **Error Handling**: Handle encryption errors gracefully
4. **Access Control**: Restrict sensitive threads (e.g., security)
5. **Audit Logging**: Log message submissions for audit trail
6. **Rate Limiting**: Prevent spam with rate limits
7. **Thread Isolation**: Keep threads independent
8. **Decrypt Sparingly**: Only decrypt when displaying to authorized users
9. **Secure Transport**: Use HTTPS for API endpoints
10. **Backup Encrypted**: Backup encrypted messages, not plaintext

---

## Related Modules

- **Feedback Manager**: `config/feedback_manager.py` - Structured feedback
- **QA System**: `config/qa_system.py` - Question/answer system
- **Settings Manager**: `config/settings_manager.py` - Support settings
- **God-Tier Encryption**: Required encryption provider

---

## Future Enhancements

1. **Message Persistence**: Save messages to encrypted file
2. **Thread Metadata**: Add thread descriptions, owners
3. **Message Replies**: Support threaded conversations
4. **Message Search**: Encrypted search capabilities
5. **Message Attachments**: Support file attachments
6. **Message Notifications**: Alert on new messages
7. **Message Priorities**: Priority levels for urgent messages
8. **Message Tags**: Tagging for categorization
9. **Message History**: Full history with pagination
10. **Message Analytics**: Analytics on message patterns


---

## Related Documentation

- **Relationship Map**: [[relationships\configuration\README.md]]


---

## Source Code References

- **Primary Module**: [[config/contact_system.py]]
