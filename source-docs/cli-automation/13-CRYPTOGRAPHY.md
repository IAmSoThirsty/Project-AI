---
title: Cryptographic Implementation
type: technical-reference
audience: [security-engineers, cryptographers]
classification: P0-Core
tags: [cryptography, ed25519, sha256, fernet]
created: 2024-01-20
status: current
---

# Cryptographic Implementation

**Production-grade cryptography for governance and security.**

## Algorithms Used

### Ed25519 Signatures

- **Purpose:** Role-based action authorization
- **Key Size:** 256-bit
- **Library:** cryptography (Python)

```python
from cryptography.hazmat.primitives.asymmetric import ed25519

# Generate keypair
private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# Sign message
signature = private_key.sign(message)

# Verify signature
public_key.verify(signature, message)
```

### SHA-256 Hashing

- **Purpose:** Audit trail hash chain
- **Output Size:** 256-bit (64 hex characters)

```python
import hashlib

hash_value = hashlib.sha256(content.encode()).hexdigest()
```

### Fernet Encryption

- **Purpose:** Sensitive data encryption (location history)
- **Algorithm:** AES-128-CBC with HMAC-SHA256
- **Library:** cryptography.fernet

```python
from cryptography.fernet import Fernet

# Generate key
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt
ciphertext = cipher.encrypt(plaintext)

# Decrypt
plaintext = cipher.decrypt(ciphertext)
```

## Security Considerations

- **Key rotation:** Rotate Ed25519 keys annually
- **Secure storage:** Store private keys in OS keyring
- **Entropy:** Use os.urandom() for random number generation

---

**AGENT-038: CLI & Automation Documentation Specialist**
