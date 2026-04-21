# Learning Request & Black Vault Data Model

**Module**: `src/app/core/ai_systems.py` [[src/app/core/ai_systems.py]] (LearningRequestManager class)  
**Storage**: `data/learning_requests/request_index.json`, `data/learning_requests/pending_secure/*.json`  
**Persistence**: JSON with encrypted secure storage  
**Schema Version**: 1.0

---

## Overview

The Learning Request Manager implements human-in-the-loop approval workflow for AI learning. It features a **Black Vault** system that permanently blocks denied content and provides encrypted storage for pending requests with SHA-256 fingerprinting.

### Key Features

- Human-in-the-loop approval workflow (approve/deny/defer)
- **Black Vault**: Permanent blocklist for denied content (SHA-256 hashing)
- Encrypted storage for pending requests (Fernet cipher)
- Automatic fingerprint checking before submission
- Request indexing for fast lookups
- Audit trail for all decisions

---

## Schema Structure

### Request Index Document

**File**: `data/learning_requests/request_index.json`

```json
{
  "requests": {
    "req_001": {
      "id": "req_001",
      "topic": "Advanced Python Decorators",
      "status": "approved",
      "submitted_at": "2024-01-15T10:30:00Z",
      "decided_at": "2024-01-15T11:00:00Z",
      "decision_by": "admin",
      "content_hash": "a3f7b8c2d1e4f5g6h7i8j9k0l1m2n3o4",
      "priority": "medium",
      "category": "technical"
    },
    "req_002": {
      "id": "req_002",
      "topic": "Exploiting Buffer Overflows",
      "status": "denied",
      "submitted_at": "2024-01-16T08:00:00Z",
      "decided_at": "2024-01-16T08:05:00Z",
      "decision_by": "admin",
      "content_hash": "b4g8c9d2e5f6g7h8i9j0k1l2m3n4o5p6",
      "denial_reason": "Content violates security policy",
      "vault_entry": "BV_20240116_001"
    }
  },
  "black_vault": {
    "b4g8c9d2e5f6g7h8i9j0k1l2m3n4o5p6": {
      "content_hash": "b4g8c9d2e5f6g7h8i9j0k1l2m3n4o5p6",
      "topic": "Exploiting Buffer Overflows",
      "denied_at": "2024-01-16T08:05:00Z",
      "denied_by": "admin",
      "reason": "Content violates security policy",
      "vault_id": "BV_20240116_001",
      "fingerprint_metadata": {
        "content_length": 1500,
        "submission_ip": "192.168.1.100",
        "attempt_count": 1
      }
    }
  },
  "metadata": {
    "total_requests": 245,
    "total_approved": 180,
    "total_denied": 42,
    "total_pending": 23,
    "vault_size": 42,
    "last_updated": "2024-01-20T14:35:22Z",
    "schema_version": "1.0"
  }
}
```

### Pending Request Document (Encrypted)

**File**: `data/learning_requests/pending_secure/{content_hash}.json` (encrypted with Fernet)

**Decrypted Content**:
```json
{
  "id": "req_003",
  "topic": "Machine Learning Optimization Techniques",
  "content": "Full content of the learning material (potentially large text)...",
  "submitted_at": "2024-01-20T14:30:00Z",
  "submitted_by": "user_alice",
  "priority": "high",
  "category": "technical",
  "metadata": {
    "source_url": "https://example.com/ml-optimization",
    "word_count": 3500,
    "estimated_read_time_minutes": 15
  }
}
```

---

## Field Specifications

### Request Index Entry

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique request identifier (req_NNN) |
| `topic` | string | Yes | Brief description of learning request |
| `status` | string | Yes | "pending", "approved", "denied", "deferred" |
| `submitted_at` | datetime | Yes | Request submission timestamp |
| `decided_at` | datetime | No | Decision timestamp (null if pending) |
| `decision_by` | string | No | User who made the decision |
| `content_hash` | string | Yes | SHA-256 hash (first 32 chars) of content |
| `priority` | string | No | "low", "medium", "high" |
| `category` | string | No | "technical", "ethical", "general" |
| `denial_reason` | string | No | Reason for denial (if status=denied) |
| `vault_entry` | string | No | Black Vault ID (if denied) |

### Black Vault Entry

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content_hash` | string | Yes | SHA-256 hash of denied content (key) |
| `topic` | string | Yes | Topic of denied request |
| `denied_at` | datetime | Yes | Timestamp of denial decision |
| `denied_by` | string | Yes | User who denied the request |
| `reason` | string | Yes | Explicit reason for denial |
| `vault_id` | string | Yes | Unique vault entry ID (BV_YYYYMMDD_NNN) |
| `fingerprint_metadata` | object | No | Additional tracking information |

---

## Request Lifecycle

### 1. Submission

```python
request_id = learning_manager.submit_request(
    topic="Advanced Python Decorators",
    content="Full learning material content...",
    submitted_by="user_alice",
    priority="medium",
    category="technical"
)
```

**Process**:
1. Generate SHA-256 hash of content
2. Check Black Vault for fingerprint match
3. If blocked: Return denial with reason
4. If clean: Encrypt content and save to `pending_secure/`
5. Add entry to request index with status="pending"
6. Return request ID

### 2. Review

```python
pending_requests = learning_manager.get_pending_requests()

for request in pending_requests:
    print(f"ID: {request['id']}")
    print(f"Topic: {request['topic']}")
    print(f"Submitted: {request['submitted_at']}")
```

### 3. Approval

```python
learning_manager.approve_request(
    request_id="req_003",
    decision_by="admin"
)
```

**Process**:
1. Update status to "approved"
2. Set `decided_at` timestamp
3. Record `decision_by` user
4. Decrypt and return content for learning
5. Remove encrypted file from `pending_secure/`

### 4. Denial (Black Vault Entry)

```python
learning_manager.deny_request(
    request_id="req_004",
    reason="Content violates security policy",
    decision_by="admin"
)
```

**Process**:
1. Generate Black Vault ID (`BV_YYYYMMDD_NNN`)
2. Add content hash to Black Vault with metadata
3. Update request status to "denied"
4. Set `denial_reason` and `vault_entry`
5. Delete encrypted pending file
6. **Permanently block future submissions** with same content hash

### 5. Deferral

```python
learning_manager.defer_request(
    request_id="req_005",
    decision_by="admin"
)
```

**Process**:
1. Update status to "deferred"
2. Keep encrypted content in `pending_secure/`
3. Can be reconsidered later

---

## Black Vault System

### Fingerprint Generation

```python
import hashlib

def _generate_content_hash(self, content: str) -> str:
    """Generate SHA-256 hash for content fingerprinting."""
    return hashlib.sha256(content.encode()).hexdigest()[:32]
```

### Vault Check on Submission

```python
def submit_request(self, topic: str, content: str, **kwargs) -> dict:
    """Submit learning request with Black Vault check."""
    content_hash = self._generate_content_hash(content)
    
    # Check Black Vault
    if content_hash in self.black_vault:
        vault_entry = self.black_vault[content_hash]
        return {
            "status": "blocked",
            "reason": f"Content denied on {vault_entry['denied_at']}: {vault_entry['reason']}",
            "vault_id": vault_entry["vault_id"]
        }
    
    # Proceed with submission
    request = self._create_request(topic, content, content_hash, **kwargs)
    self._encrypt_and_store(request)
    return {"status": "submitted", "request_id": request["id"]}
```

### Vault Entry Creation

```python
def _add_to_black_vault(self, request: dict, reason: str, decision_by: str) -> str:
    """Add denied content to Black Vault."""
    vault_id = f"BV_{datetime.now().strftime('%Y%m%d')}_{len(self.black_vault) + 1:03d}"
    
    vault_entry = {
        "content_hash": request["content_hash"],
        "topic": request["topic"],
        "denied_at": datetime.now().isoformat(),
        "denied_by": decision_by,
        "reason": reason,
        "vault_id": vault_id,
        "fingerprint_metadata": {
            "content_length": len(request.get("content", "")),
            "submission_ip": request.get("metadata", {}).get("submission_ip"),
            "attempt_count": 1
        }
    }
    
    self.black_vault[request["content_hash"]] = vault_entry
    self._save_index()
    return vault_id
```

### Vault Persistence

Black Vault is **immutable** - entries are never deleted:

```python
def _save_index(self):
    """Save request index and Black Vault."""
    index_data = {
        "requests": self.requests,
        "black_vault": self.black_vault,  # Persistent, immutable
        "metadata": self._generate_metadata()
    }
    _atomic_write_json(self.index_file, index_data)
```

---

## Encryption System

### Fernet Encryption for Pending Requests

```python
from cryptography.fernet import Fernet

def _encrypt_content(self, content: str) -> bytes:
    """Encrypt content with Fernet cipher."""
    return self.cipher_suite.encrypt(content.encode())

def _decrypt_content(self, encrypted_data: bytes) -> str:
    """Decrypt content."""
    return self.cipher_suite.decrypt(encrypted_data).decode()
```

### Storage Pattern

```python
def _store_pending_request(self, request: dict):
    """Store request with encrypted content."""
    # Encrypt full request JSON
    encrypted = self._encrypt_content(json.dumps(request))
    
    # Save to secure directory with hash-based filename
    secure_file = os.path.join(
        self.pending_dir, 
        f"{request['content_hash']}.json"
    )
    
    with open(secure_file, 'wb') as f:
        f.write(encrypted)
```

### Retrieval Pattern

```python
def get_request_details(self, request_id: str) -> dict | None:
    """Retrieve and decrypt request details."""
    request_meta = self.requests.get(request_id)
    if not request_meta or request_meta["status"] != "pending":
        return None
    
    secure_file = os.path.join(
        self.pending_dir,
        f"{request_meta['content_hash']}.json"
    )
    
    if os.path.exists(secure_file):
        with open(secure_file, 'rb') as f:
            encrypted = f.read()
        return json.loads(self._decrypt_content(encrypted))
    
    return None
```

---

## Request Priority System

### Priority Levels

| Priority | Description | Typical Use Case |
|----------|-------------|------------------|
| `low` | Non-urgent, background learning | General knowledge, trivia |
| `medium` | Standard priority (default) | Technical concepts, tutorials |
| `high` | Time-sensitive or critical | Security patches, urgent skills |

### Priority-Based Sorting

```python
def get_pending_requests(self, sort_by_priority: bool = True) -> list[dict]:
    """Get pending requests, optionally sorted by priority."""
    pending = [r for r in self.requests.values() if r["status"] == "pending"]
    
    if sort_by_priority:
        priority_order = {"high": 0, "medium": 1, "low": 2}
        pending.sort(key=lambda r: (
            priority_order.get(r.get("priority", "medium"), 1),
            r["submitted_at"]
        ))
    
    return pending
```

---

## Usage Examples

### Submit Learning Request

```python
from app.core.ai_systems import LearningRequestManager

manager = LearningRequestManager(data_dir="data")

# Submit new request
result = manager.submit_request(
    topic="Python Async Programming",
    content="Detailed async/await tutorial content...",
    submitted_by="user_alice",
    priority="high",
    category="technical",
    metadata={"source_url": "https://example.com/async"}
)

if result["status"] == "submitted":
    print(f"Request submitted: {result['request_id']}")
elif result["status"] == "blocked":
    print(f"Request blocked: {result['reason']}")
```

### Review Pending Requests

```python
# Get all pending requests
pending = manager.get_pending_requests(sort_by_priority=True)

for request in pending:
    print(f"ID: {request['id']}")
    print(f"Topic: {request['topic']}")
    print(f"Priority: {request.get('priority', 'medium')}")
    
    # Get full details (decrypts content)
    details = manager.get_request_details(request['id'])
    print(f"Content length: {len(details['content'])} chars")
```

### Approve Request

```python
# Approve and retrieve content
content = manager.approve_request(
    request_id="req_003",
    decision_by="admin"
)

# Use content for learning
memory_system.add_knowledge(
    category="technical",
    content=content,
    source=f"learning_request_req_003"
)
```

### Deny Request (Black Vault)

```python
# Deny and add to Black Vault
vault_id = manager.deny_request(
    request_id="req_004",
    reason="Contains malicious content",
    decision_by="admin"
)

print(f"Added to Black Vault: {vault_id}")

# Future submissions with same content will be auto-blocked
result = manager.submit_request(
    topic="Same Malicious Content",
    content="<same content as req_004>"
)
# Returns: {"status": "blocked", "vault_id": "BV_20240120_001"}
```

---

## Audit Trail

### Decision Logging

```python
def get_decision_history(self, user: str | None = None) -> list[dict]:
    """Get history of all decisions, optionally filtered by user."""
    decisions = [
        r for r in self.requests.values()
        if r["status"] in ["approved", "denied", "deferred"]
    ]
    
    if user:
        decisions = [d for d in decisions if d.get("decision_by") == user]
    
    decisions.sort(key=lambda d: d["decided_at"], reverse=True)
    return decisions
```

### Statistics

```python
def get_statistics(self) -> dict:
    """Get learning request statistics."""
    total = len(self.requests)
    approved = sum(1 for r in self.requests.values() if r["status"] == "approved")
    denied = sum(1 for r in self.requests.values() if r["status"] == "denied")
    pending = sum(1 for r in self.requests.values() if r["status"] == "pending")
    
    return {
        "total_requests": total,
        "approved": approved,
        "denied": denied,
        "pending": pending,
        "approval_rate": approved / total if total > 0 else 0,
        "vault_size": len(self.black_vault)
    }
```

---

## Testing Strategy

### Unit Tests

```python
def test_submit_and_approve():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = LearningRequestManager(data_dir=tmpdir)
        
        result = manager.submit_request("Test Topic", "Test Content")
        assert result["status"] == "submitted"
        
        content = manager.approve_request(result["request_id"], "admin")
        assert content == "Test Content"

def test_black_vault_blocking():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = LearningRequestManager(data_dir=tmpdir)
        
        # Submit and deny
        result1 = manager.submit_request("Bad Topic", "Malicious Content")
        manager.deny_request(result1["request_id"], "Policy violation", "admin")
        
        # Try to resubmit same content
        result2 = manager.submit_request("Different Topic", "Malicious Content")
        assert result2["status"] == "blocked"
        assert "BV_" in result2["vault_id"]
```

---

## Security Considerations

### Content Fingerprinting

- **SHA-256 hashing** prevents trivial bypasses (case changes, whitespace)
- **Truncated to 32 chars** for storage efficiency
- **Collision resistance**: 2^128 security level

### Encryption Key Management

```bash
# .env file
FERNET_KEY=<base64-encoded-32-byte-key>
```

**Best Practices**:
1. Generate key with `Fernet.generate_key()`
2. Store in `.env` [[.env]] file (never commit to Git)
3. Rotate keys periodically (decrypt-reencrypt workflow)

### Black Vault Immutability

- **No deletion API** - vault entries are permanent
- **Prevents re-submission** of denied content
- **Audit trail** preserved forever

---

## Performance Considerations

### Encryption Overhead

- **Fernet encryption**: ~1ms per request
- **Decryption**: ~1ms per retrieval
- **Negligible** for human-in-the-loop workflow

### Black Vault Size

- **Typical**: 50-100 entries (50KB)
- **Large scale**: 10,000 entries (~5MB)
- **Recommendation**: Archive old entries after 1 year

### File I/O Optimization

- **Lazy loading**: Only decrypt when request details needed
- **Index caching**: Keep request index in memory
- **Batch operations**: Approve/deny multiple requests in transaction

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `continuous_learning.py` | Consumes approved requests for learning |
| `memory_engine.py` | Stores learned content from approved requests |
| `governance.py` | Uses Black Vault for policy enforcement |
| `telemetry.py` | Logs request submission and decision events |

---

## Future Enhancements

1. **Automated Review**: ML-based content classification for auto-approval
2. **Multi-Level Approval**: Require multiple approvers for high-risk content
3. **Vault Quarantine**: Temporary blocking with automatic expiration
4. **Content Similarity**: Block near-duplicates using fuzzy hashing
5. **Expiry Dates**: Auto-approve deferred requests after timeout

---

## References

- **LEARNING_REQUEST_IMPLEMENTATION.md**: Detailed implementation guide
- **BLACK_VAULT_SPECIFICATION.md**: Security architecture
- **Fernet Specification**: https://github.com/fernet/spec

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
