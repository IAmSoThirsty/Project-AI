# Enhanced Cryptographic War Engine - Examples

This directory contains practical examples demonstrating the Post-Quantum Cryptography (PQC) capabilities.

## Quick Examples

### 1. Basic PQC Setup

```python
from engines.crypto_war_enhanced import create_pqc_engine

# Create engine with high security
engine = create_pqc_engine(threat_level="high")

# Check status
status = engine.get_security_status()
print(f"Quantum Safe: {status['crypto_profile']['quantum_safe']}")
```

### 2. Quantum-Resistant Digital Signatures

```python
from engines.crypto_war_enhanced import EnhancedCryptoWarEngine, CryptoAlgorithm

engine = EnhancedCryptoWarEngine()

# Generate Dilithium signing key
keypair = engine.generate_pqc_keypair(
    algorithm=CryptoAlgorithm.DILITHIUM_3,
    key_id="document_signing_key"
)

# Sign a document
document = b"Important contract requiring long-term verification"
signature = engine.pqc_sign(document, "document_signing_key")

# Verify signature (even decades later)
is_valid = engine.pqc_verify(document, signature, "document_signing_key")
print(f"Signature valid: {is_valid}")
```

### 3. Quantum-Safe Key Exchange

```python
from engines.crypto_war_enhanced import EnhancedCryptoWarEngine, CryptoAlgorithm
from cryptography.fernet import Fernet
import base64

engine = EnhancedCryptoWarEngine()

# Generate Kyber key for key exchange
engine.generate_pqc_keypair(
    algorithm=CryptoAlgorithm.KYBER_768,
    key_id="exchange_key"
)

# Encapsulate shared secret
ciphertext, shared_secret = engine.pqc_encapsulate("exchange_key")

# Use shared secret for AES encryption
key = base64.urlsafe_b64encode(shared_secret)
cipher = Fernet(key)

message = b"Classified information"
encrypted = cipher.encrypt(message)

# Receiver decapsulates
recovered_secret = engine.pqc_decapsulate(ciphertext, "exchange_key")
key = base64.urlsafe_b64encode(recovered_secret)
cipher = Fernet(key)
decrypted = cipher.decrypt(encrypted)

print(f"Decrypted: {decrypted.decode()}")
```

### 4. Algorithm Agility - Dynamic Threat Response

```python
from engines.crypto_war_enhanced import (
    AlgorithmAgilityEngine,
    ThreatLevel
)

agility = AlgorithmAgilityEngine()

# Monitor threat intelligence
print(f"Current threat: {agility.current_threat_level.value}")

# Threat detected!
agility.update_threat_level(
    new_level=ThreatLevel.CRITICAL,
    reason="Quantum computer breakthrough announced",
    intelligence_source="NIST Quantum Alert"
)

# System automatically switches to stronger PQC
kem_algo = agility.recommend_algorithm("kem")
sig_algo = agility.recommend_algorithm("signature")

print(f"New KEM: {kem_algo.value}")
print(f"New Signature: {sig_algo.value}")
```

### 5. Migration from Classical to PQC

```python
from engines.crypto_war_enhanced import (
    MigrationEngine,
    CryptoAlgorithm
)

migration = MigrationEngine()

# Plan migration
plan = migration.plan_migration(
    source_algorithm=CryptoAlgorithm.RSA_2048,
    target_algorithm=CryptoAlgorithm.KYBER_768,
    data_count=1000
)

print(f"Migration phases: {plan['phases']}")
print(f"Estimated time: {plan['estimated_time_seconds']}s")
print(f"Downtime required: {plan['requires_downtime']}")

# Prepare data
data_items = [
    {"id": i, "encrypted_data": f"legacy_data_{i}"}
    for i in range(1000)
]

# Execute migration with automatic rollback capability
record = migration.execute_migration(plan, data_items)

print(f"Migration status: {record.status}")
print(f"Items migrated: {record.data_migrated}")
print(f"Rollback available: {record.rollback_available}")
```

### 6. Hybrid Cryptography (Classical + PQC)

```python
from engines.crypto_war_enhanced import (
    MigrationEngine,
    CryptoAlgorithm
)

migration = MigrationEngine()

# Enable hybrid mode for defense-in-depth
config = migration.enable_hybrid_mode(
    classical_algorithm=CryptoAlgorithm.RSA_4096,
    pqc_algorithm=CryptoAlgorithm.DILITHIUM_3
)

print(f"Hybrid mode: {config['mode']}")
print(f"Verification: {config['verification']}")
# Both classical AND PQC signatures must pass
```

### 7. Quantum Threat Assessment

```python
from engines.crypto_war_enhanced import EnhancedCryptoWarEngine, ThreatLevel

engine = EnhancedCryptoWarEngine(threat_level=ThreatLevel.MEDIUM)

# Assess quantum risk
assessment = engine.assess_quantum_threat()

print(f"Risk Level: {assessment['risk_level']}")
print(f"Quantum Safe: {assessment['quantum_safe']}")
print(f"Recommendation: {assessment['recommendation']}")
print(f"Vulnerable Algorithms: {assessment['affected_algorithms']}")

# Example output:
# Risk Level: medium
# Quantum Safe: False
# Recommendation: Migrate to PQC
# Vulnerable Algorithms: ['rsa-4096']
```

### 8. Long-Term Signatures with SPHINCS+

```python
from engines.crypto_war_enhanced import EnhancedCryptoWarEngine, CryptoAlgorithm

engine = EnhancedCryptoWarEngine()

# Use SPHINCS+ for maximum security and longevity
# Ideal for: code signing, firmware, legal documents
keypair = engine.generate_pqc_keypair(
    algorithm=CryptoAlgorithm.SPHINCS_PLUS_256F,
    key_id="code_signing_key"
)

# Sign firmware
firmware = b"Firmware binary data here..."
signature = engine.pqc_sign(
    firmware,
    "code_signing_key",
    algorithm=CryptoAlgorithm.SPHINCS_PLUS_256F
)

print(f"Signature size: {len(signature)} bytes")
# Note: SPHINCS+ signatures are large (~49KB) but incredibly secure
```

### 9. Lattice-Based Encryption (LWE/NTRU)

```python
from engines.crypto_war_enhanced import LWEScheme, NTRUScheme

# Learning With Errors (foundation of Kyber)
lwe = LWEScheme(n=256, q=3329)
public_key, private_key = lwe.keygen()

message = b"Secret data"
ciphertext = lwe.encrypt(message, public_key)
plaintext = lwe.decrypt(ciphertext, private_key)

# NTRU (fastest PQC encryption)
ntru = NTRUScheme(n=509, q=2048)
public_key, private_key = ntru.keygen()

ciphertext = ntru.encrypt(message, public_key)
plaintext = ntru.decrypt(ciphertext, private_key)
```

### 10. Complete Secure Communication Protocol

```python
from engines.crypto_war_enhanced import (
    EnhancedCryptoWarEngine,
    CryptoAlgorithm,
    ThreatLevel
)
from cryptography.fernet import Fernet
import base64

# === SENDER ===
sender = EnhancedCryptoWarEngine(threat_level=ThreatLevel.HIGH)

# Generate keys
sender.generate_pqc_keypair(CryptoAlgorithm.KYBER_768, "kem")
sender.generate_pqc_keypair(CryptoAlgorithm.DILITHIUM_3, "sig")

# Prepare message
message = b"CLASSIFIED: Operation details"

# Sign for authentication
signature = sender.pqc_sign(message, "sig")

# Encapsulate shared secret for confidentiality
ciphertext, shared_secret = sender.pqc_encapsulate("kem")

# Encrypt message with shared secret
key = base64.urlsafe_b64encode(shared_secret)
cipher = Fernet(key)
encrypted_message = cipher.encrypt(message)

# Send: (encrypted_message, ciphertext, signature, public_keys)

# === RECEIVER ===
receiver = EnhancedCryptoWarEngine(threat_level=ThreatLevel.HIGH)

# Import sender's public keys
receiver.keys["kem"] = sender.keys["kem"]
receiver.keys["sig"] = sender.keys["sig"]

# Decapsulate shared secret
recovered_secret = receiver.pqc_decapsulate(ciphertext, "kem")

# Decrypt message
key = base64.urlsafe_b64encode(recovered_secret)
cipher = Fernet(key)
decrypted_message = cipher.decrypt(encrypted_message)

# Verify signature
is_valid = receiver.pqc_verify(decrypted_message, signature, "sig")

if is_valid:
    print(f"✅ Authenticated message: {decrypted_message.decode()}")
else:
    print("❌ Authentication failed!")
```

### 11. Key Management and Export

```python
from engines.crypto_war_enhanced import EnhancedCryptoWarEngine, CryptoAlgorithm

engine = EnhancedCryptoWarEngine()

# Generate key
engine.generate_pqc_keypair(
    algorithm=CryptoAlgorithm.KYBER_1024,
    key_id="org_master_key"
)

# Export public key for distribution
exported = engine.export_keys("org_master_key")

print(f"Key ID: {exported['key_id']}")
print(f"Algorithm: {exported['algorithm']}")
print(f"Public Key: {exported['public_key'][:64]}...")  # First 64 chars
print(f"Created: {exported['created_at']}")

# Distribute public key to partners
# Keep private key secured in HSM/encrypted storage
```

### 12. Security Status Monitoring

```python
from engines.crypto_war_enhanced import create_pqc_engine

engine = create_pqc_engine(threat_level="critical")

# Generate some keys
engine.generate_pqc_keypair(CryptoAlgorithm.KYBER_1024, "key1")
engine.generate_pqc_keypair(CryptoAlgorithm.DILITHIUM_5, "key2")
engine.generate_pqc_keypair(CryptoAlgorithm.SPHINCS_PLUS_256F, "key3")

# Get comprehensive status
status = engine.get_security_status()

print(f"Threat Level: {status['threat_level']}")
print(f"Total Keys: {status['total_keys']}")
print(f"PQC Keys: {status['pqc_keys']}")
print(f"Security Bits: {status['crypto_profile']['security_bits']}")
print(f"Quantum Safe: {status['crypto_profile']['quantum_safe']}")
print(f"Migrations Completed: {status['migrations_completed']}")
print(f"Hybrid Mode: {status['hybrid_mode']}")
```

## Running the Examples

### Run Full Demo

```bash
python engines/crypto_war_enhanced.py
```

### Run Tests

```bash
pytest engines/test_crypto_war_enhanced.py -v
```

## Performance Benchmarks

Approximate performance on modern CPU:

| Operation | Algorithm | Time |
|-----------|-----------|------|
| Key Generation | Kyber768 | ~1ms |
| Key Generation | Dilithium3 | ~2ms |
| Key Generation | SPHINCS+128f | ~10ms |
| Encapsulation | Kyber768 | ~0.5ms |
| Decapsulation | Kyber768 | ~0.5ms |
| Signing | Dilithium3 | ~2ms |
| Verification | Dilithium3 | ~1ms |
| Signing | SPHINCS+256f | ~50-100ms |
| Verification | SPHINCS+256f | ~1-2ms |

## Size Comparisons

| Item | Classical (RSA-2048) | PQC (Kyber768/Dilithium3) |
|------|---------------------|---------------------------|
| Public Key | 270 bytes | 1,184 bytes (Kyber) |
| Private Key | 1,190 bytes | 2,400 bytes (Kyber) |
| Ciphertext | 256 bytes | 1,088 bytes (Kyber) |
| Signature | 256 bytes | 3,293 bytes (Dilithium) |

## Security Levels

| NIST Level | Classical Equivalent | PQC Examples |
|------------|---------------------|--------------|
| Level 1 | AES-128 | Kyber512 |
| Level 2 | SHA-256 collision | Dilithium2 |
| Level 3 | AES-192 | Kyber768, Dilithium3 ⭐ |
| Level 5 | AES-256 | Kyber1024, Dilithium5 |

## Best Practices

1. **Use Kyber768** for most key exchange (NIST Level 3)
2. **Use Dilithium3** for most signatures (NIST Level 3)
3. **Use SPHINCS+** only for long-term signatures (slower but most conservative)
4. **Enable hybrid mode** during migration period
5. **Monitor threat levels** and adjust algorithms accordingly
6. **Test performance** in your specific environment
7. **Plan migrations** carefully with rollback capability

## Further Reading

- See `POST_QUANTUM_CRYPTO_GUIDE.md` for comprehensive documentation
- See `crypto_war_enhanced.py` for implementation details
- See `test_crypto_war_enhanced.py` for more examples

## Production Deployment

⚠️ **IMPORTANT**: The current implementation uses hash-based simulation. For production:

1. Replace with `liboqs` or `PQClean` bindings
2. Use Hardware Security Modules (HSMs) for key storage
3. Implement constant-time operations for side-channel protection
4. Use hardware RNG for key generation
5. Follow NIST SP 800-208 and FIPS 140-3 guidelines

## Support

For questions or issues, consult the main documentation or examine the test suite for additional examples.
