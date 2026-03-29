<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / privacy_ledger.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / privacy_ledger.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# Privacy Accountability Ledger

Production-grade encrypted privacy accountability ledger for immutable audit logging with zero-knowledge encryption.

## Features

### Core Security

- **Zero-Knowledge Encryption**: User-key based encryption with dual-layer protection (Fernet + AES-256-GCM)
- **Tamper Detection**: SHA-512 cryptographic hashing with blockchain-style chain linking
- **Merkle Tree Verification**: O(log n) proof verification for entry integrity
- **Atomic Writes**: ACID guarantees using write-ahead logging (WAL)
- **Thread-Safe Operations**: Full concurrency support with RLock protection

### Audit Capabilities

- **Structured Logging**: Type-safe event logging with severity levels
- **Efficient Search**: Indexed by user, event type, time range
- **Audit Export**: JSON export with optional field decryption for compliance
- **Chain Integrity**: Full ledger verification with tamper detection

### Privacy & Compliance

- **Retention Policies**: Configurable data retention with secure multi-pass deletion
- **Forensic Resistance**: Secure data wiping before deletion
- **Immutable Records**: Append-only operations prevent modification
- **Compliance Ready**: GDPR, HIPAA, SOC2 audit trail support

## Quick Start

```python
from thirstys_waterfall.security.privacy_ledger import (
    PrivacyLedger, EventType, SeverityLevel
)

# Create ledger

ledger = PrivacyLedger("audit.dat", retention_days=90)

# Log an event

ledger.append(
    event_type=EventType.USER_LOGIN,
    user_id="john.doe@example.com",
    action="User authenticated via OAuth2",
    resource="auth_service",
    severity=SeverityLevel.INFO,
    metadata={'ip': '192.168.1.100'}
)

# Verify integrity

is_valid, errors = ledger.verify_chain_integrity()
print(f"Ledger valid: {is_valid}")

# Search entries

entries = ledger.search(user_id="john.doe@example.com")

# Close ledger

ledger.close()
```

## Architecture

### Components

#### PrivacyLedger

Main ledger class managing all operations:

- Entry creation and storage
- Encryption/decryption
- Search and retrieval
- Integrity verification
- Persistence management

#### LedgerEntry

Immutable dataclass representing a single audit event:

- Unique entry ID
- Timestamp (UTC)
- Event type and severity
- User ID (encrypted)
- Action description
- Resource identifier
- Metadata (flexible JSON)
- Cryptographic hash
- Previous entry hash (for chain)
- Merkle proof

#### MerkleTree

Efficient verification structure:

- Binary tree of cryptographic hashes
- O(log n) proof generation
- O(log n) proof verification
- Automatic tree rebuilding

### Security Design

```
┌─────────────────────────────────────────────┐
│         User Application                     │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│       PrivacyLedger API                     │
│  (Thread-safe, Zero-knowledge)              │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┴──────────┐
        ▼                    ▼
┌──────────────┐    ┌──────────────┐
│  Encryption  │    │ Merkle Tree  │
│  (Dual-layer)│    │ (Integrity)  │
└──────┬───────┘    └──────┬───────┘
       │                   │
       └─────────┬─────────┘
                 ▼
┌─────────────────────────────────────────────┐
│    Atomic Storage (WAL + Main File)         │
└─────────────────────────────────────────────┘
```

### Encryption Layers

1. **Field-level encryption**: User IDs encrypted with Fernet
2. **Entry serialization**: JSON encoding
3. **Fernet encryption**: Symmetric encryption of entry data
4. **AES-256-GCM**: Additional authenticated encryption layer
5. **Base64 encoding**: Safe storage format

### Chain Integrity

Each entry contains:

- `hash`: SHA-512 hash of entry content
- `previous_hash`: Hash of previous entry (blockchain-style)

This creates an immutable chain where any modification breaks verification.

## Event Types

```python
class EventType(Enum):
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PERMISSION_CHANGE = "permission_change"
    ENCRYPTION_KEY_ROTATION = "encryption_key_rotation"
    SECURITY_ALERT = "security_alert"
    PRIVACY_VIOLATION = "privacy_violation"
    CONSENT_GIVEN = "consent_given"
    CONSENT_REVOKED = "consent_revoked"
    AUDIT_REQUEST = "audit_request"
    DATA_EXPORT = "data_export"
    SYSTEM_ACCESS = "system_access"
    ANOMALY_DETECTED = "anomaly_detected"
```

## Severity Levels

```python
class SeverityLevel(Enum):
    DEBUG = 0      # Detailed diagnostic info
    INFO = 1       # Normal operations
    WARNING = 2    # Potential issues
    ERROR = 3      # Error conditions
    CRITICAL = 4   # Critical failures
```

## API Reference

### PrivacyLedger

#### Constructor

```python
PrivacyLedger(
    storage_path: str,
    encryption_key: Optional[bytes] = None,
    max_entries: int = 100000,
    retention_days: int = 90
)
```

#### Methods

**append()** - Add new entry
```python
append(
    event_type: EventType,
    user_id: str,
    action: str,
    resource: str = "",
    severity: SeverityLevel = SeverityLevel.INFO,
    metadata: Optional[Dict[str, Any]] = None
) -> LedgerEntry
```

**search()** - Search entries
```python
search(
    user_id: Optional[str] = None,
    event_type: Optional[EventType] = None,
    severity: Optional[SeverityLevel] = None,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    limit: int = 100
) -> List[LedgerEntry]
```

**verify_chain_integrity()** - Verify ledger
```python
verify_chain_integrity() -> Tuple[bool, List[str]]
```

**export_audit_log()** - Export for compliance
```python
export_audit_log(
    output_path: str,
    user_id: Optional[str] = None,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    decrypt_sensitive: bool = False
) -> int
```

**get_stats()** - Get statistics
```python
get_stats() -> Dict[str, Any]
```

**close()** - Close ledger
```python
close()
```

## Examples

See `examples/privacy_ledger_examples.py` for complete examples:

1. **Basic Usage**: Creating ledger and logging events
2. **Search & Retrieval**: Finding specific entries
3. **Audit Export**: Exporting for compliance
4. **Persistence**: Loading existing ledgers
5. **Integrity Verification**: Detecting tampering

Run examples:
```bash
python examples/privacy_ledger_examples.py
```

## Testing

Comprehensive test suite with 25 tests:

```bash
python -m unittest tests.test_privacy_ledger -v
```

Test coverage:

- Entry creation and integrity
- Merkle tree proof generation/verification
- Thread-safe concurrent operations
- Persistence and loading
- Search and filtering
- Tamper detection
- Complete audit workflows

## Performance

- **Append**: O(log n) - includes Merkle tree update
- **Search by index**: O(1) - direct lookup
- **Search by user**: O(m) - where m is user's entry count
- **Verification**: O(n) - full chain traversal
- **Merkle proof**: O(log n) - tree height
- **Storage**: ~1KB per entry (encrypted)

## Security Considerations

### Encryption Key Management

- Store encryption keys securely (e.g., AWS KMS, HashiCorp Vault)
- Never commit keys to version control
- Use unique keys per environment
- Rotate keys periodically

### Access Control

- Limit ledger file access to authorized processes
- Use OS-level file permissions (600 recommended)
- Consider encrypting entire filesystem
- Log all ledger access attempts

### Retention & Deletion

- Set appropriate retention policies
- Secure deletion uses multi-pass overwrite
- Consider regulatory requirements (GDPR, HIPAA)
- Archive old ledgers before deletion

## Compliance

Suitable for:

- **GDPR**: Right to audit, data minimization
- **HIPAA**: Audit trail requirements
- **SOC 2**: Security logging
- **PCI DSS**: Access logging
- **ISO 27001**: Information security

## License

Part of Thirsty's Waterfall privacy suite.

## Contributing

See main repository for contribution guidelines.
