# Post-Quantum Cryptography Guide

**Enhanced Cryptographic War Engine Documentation**

## Overview

The Enhanced Cryptographic War Engine provides comprehensive post-quantum cryptography (PQC) capabilities to protect against quantum computing threats. This guide covers all PQC implementations, algorithm agility, and migration tools.

## Table of Contents

1. [Introduction](#introduction)
2. [NIST PQC Finalists](#nist-pqc-finalists)
3. [Lattice-Based Schemes](#lattice-based-schemes)
4. [Algorithm Agility](#algorithm-agility)
5. [Migration Tools](#migration-tools)
6. [Quick Start](#quick-start)
7. [API Reference](#api-reference)
8. [Security Considerations](#security-considerations)

---

## Introduction

### What is Post-Quantum Cryptography?

Post-quantum cryptography refers to cryptographic algorithms designed to be secure against attacks by quantum computers. Current public-key cryptography (RSA, ECC) is vulnerable to quantum algorithms like Shor's algorithm.

### Why PQC Matters

- **Harvest Now, Decrypt Later**: Adversaries collect encrypted data today to decrypt when quantum computers become available
- **NIST Standardization**: NIST selected quantum-resistant algorithms in 2022
- **Regulatory Requirements**: Emerging mandates for quantum-safe cryptography
- **Future-Proofing**: Transition before quantum threat becomes reality

### Threat Timeline

- **2024-2026**: Early quantum computers (research)
- **2026-2030**: Cryptographically relevant quantum computers (CRQC) possible
- **2030+**: Widespread quantum computing capability

---

## NIST PQC Finalists

### Kyber - Key Encapsulation Mechanism (KEM)

**Purpose**: Quantum-safe key exchange and encryption

**Security Levels**:
- `Kyber512`: NIST Level 1 (128-bit security)
- `Kyber768`: NIST Level 3 (192-bit security) ⭐ Recommended
- `Kyber1024`: NIST Level 5 (256-bit security)

**Features**:
- Based on Module Learning With Errors (Module-LWE)
- Fast key generation and encapsulation
- Small ciphertext and key sizes (compared to other PQC)
- Standardized as ML-KEM by NIST

**Usage Example**:

```python
from engines.crypto_war_enhanced import (
    EnhancedCryptoWarEngine,
    CryptoAlgorithm,
    ThreatLevel
)

# Initialize engine
engine = EnhancedCryptoWarEngine(threat_level=ThreatLevel.HIGH)

# Generate Kyber key pair
keypair = engine.generate_pqc_keypair(
    algorithm=CryptoAlgorithm.KYBER_768,
    key_id="kyber_exchange_key"
)

# Sender: Encapsulate shared secret
ciphertext, shared_secret = engine.pqc_encapsulate("kyber_exchange_key")

# Send ciphertext to receiver...

# Receiver: Decapsulate to recover shared secret
recovered_secret = engine.pqc_decapsulate(ciphertext, "kyber_exchange_key")

# Use shared_secret for symmetric encryption (AES-256)
```

**Performance**:
- Key generation: ~1ms
- Encapsulation: ~0.5ms
- Decapsulation: ~0.5ms
- Public key size: 1,184 bytes (Kyber768)
- Ciphertext size: 1,088 bytes (Kyber768)

---

### Dilithium - Digital Signatures

**Purpose**: Quantum-resistant digital signatures

**Security Levels**:
- `Dilithium2`: NIST Level 2 (similar to AES-128)
- `Dilithium3`: NIST Level 3 (similar to AES-192) ⭐ Recommended
- `Dilithium5`: NIST Level 5 (similar to AES-256)

**Features**:
- Based on Module Learning With Errors (Module-LWE)
- Deterministic signatures
- No stateful components required
- Strong security proofs

**Usage Example**:

```python
# Generate Dilithium key pair
keypair = engine.generate_pqc_keypair(
    algorithm=CryptoAlgorithm.DILITHIUM_3,
    key_id="dilithium_signing_key"
)

# Sign a message
message = b"Classified military operation data"
signature = engine.pqc_sign(
    message=message,
    key_id="dilithium_signing_key"
)

# Verify signature
is_valid = engine.pqc_verify(
    message=message,
    signature=signature,
    key_id="dilithium_signing_key"
)

assert is_valid, "Signature verification failed!"
```

**Performance**:
- Key generation: ~2ms
- Signing: ~2ms
- Verification: ~1ms
- Public key size: 1,952 bytes (Dilithium3)
- Signature size: 3,293 bytes (Dilithium3)

---

### SPHINCS+ - Hash-Based Signatures

**Purpose**: Stateless quantum-resistant signatures with minimal assumptions

**Variants**:
- `SPHINCS+-128f`: 128-bit security, fast
- `SPHINCS+-128s`: 128-bit security, small
- `SPHINCS+-256f`: 256-bit security, fast ⭐ Recommended for critical systems
- `SPHINCS+-256s`: 256-bit security, small

**Features**:
- Based only on hash functions (most conservative approach)
- Stateless (no state management required)
- Larger signatures than Dilithium
- Ideal for long-term signatures (code signing, document signing)

**Usage Example**:

```python
# Generate SPHINCS+ key pair
keypair = engine.generate_pqc_keypair(
    algorithm=CryptoAlgorithm.SPHINCS_PLUS_256F,
    key_id="sphincs_signing_key"
)

# Sign critical document
document = b"Constitutional amendment proposal"
signature = engine.pqc_sign(
    message=document,
    key_id="sphincs_signing_key",
    algorithm=CryptoAlgorithm.SPHINCS_PLUS_256F
)

# Signature remains valid even decades later
```

**Performance**:
- Key generation: ~10ms
- Signing: ~50-100ms (slower than Dilithium)
- Verification: ~1-2ms
- Public key size: 64 bytes (256f)
- Signature size: ~49KB (256f) - much larger than Dilithium

**When to use SPHINCS+**:
- ✅ Long-term signatures (>20 years)
- ✅ Code signing, firmware signing
- ✅ Maximum security conservatism
- ❌ Real-time applications (use Dilithium)
- ❌ Bandwidth-constrained environments

---

## Lattice-Based Schemes

### Learning With Errors (LWE)

**Purpose**: Foundation for Kyber and other lattice-based cryptography

**Concept**: Security based on the hardness of solving noisy linear equations over lattices

**Implementation**:

```python
from engines.crypto_war_enhanced import LWEScheme

# Initialize LWE scheme
lwe = LWEScheme(n=256, q=3329)

# Generate keys
public_key, private_key = lwe.keygen()

# Encrypt message
message = b"Top secret data"
ciphertext = lwe.encrypt(message, public_key)

# Decrypt
plaintext = lwe.decrypt(ciphertext, private_key)
```

**Properties**:
- Quantum-resistant
- Supports fully homomorphic encryption (FHE)
- Foundation for many NIST PQC candidates
- Well-studied security assumptions

---

### NTRU

**Purpose**: Lattice-based encryption (oldest and most studied)

**History**: Invented in 1996, survived 25+ years of cryptanalysis

**Implementation**:

```python
from engines.crypto_war_enhanced import NTRUScheme

# Initialize NTRU
ntru = NTRUScheme(n=509, q=2048)

# Generate keys
public_key, private_key = ntru.keygen()

# Encrypt
message = b"Classified intelligence"
ciphertext = ntru.encrypt(message, public_key)

# Decrypt
plaintext = ntru.decrypt(ciphertext, private_key)
```

**Advantages**:
- Fastest PQC encryption/decryption
- Small key and ciphertext sizes
- Patent-free (as of 2017)
- Excellent performance on embedded devices

---

## Algorithm Agility

### Threat Level-Based Selection

The Algorithm Agility Engine automatically selects appropriate cryptographic algorithms based on current threat intelligence.

**Threat Levels**:

| Level | Description | KEM | Signature | Security Bits |
|-------|-------------|-----|-----------|---------------|
| **LOW** | Routine operations | RSA-2048 | HMAC-SHA3 | 112 |
| **MEDIUM** | Standard security | RSA-4096 | Dilithium2 | 128 |
| **HIGH** | Sensitive data | Kyber768 | Dilithium3 | 192 |
| **CRITICAL** | National security | Kyber1024 | Dilithium5 | 256 |
| **QUANTUM** | Active quantum threat | Kyber1024 | SPHINCS+-256f | 256 |

### Dynamic Algorithm Selection

```python
from engines.crypto_war_enhanced import (
    AlgorithmAgilityEngine,
    ThreatLevel
)

# Initialize agility engine
agility = AlgorithmAgilityEngine()

# Update threat level based on intelligence
agility.update_threat_level(
    new_level=ThreatLevel.CRITICAL,
    reason="Quantum computer breakthrough detected",
    intelligence_source="NSA Threat Advisory #2026-Q1"
)

# Get recommended algorithms
kem_algo = agility.recommend_algorithm("kem")
sig_algo = agility.recommend_algorithm("signature")

print(f"Recommended KEM: {kem_algo.value}")
print(f"Recommended Signature: {sig_algo.value}")
```

### Quantum Risk Assessment

```python
# Assess quantum threat to current crypto
risk_assessment = engine.assess_quantum_threat()

print(f"Risk Level: {risk_assessment['risk_level']}")
print(f"Quantum Safe: {risk_assessment['quantum_safe']}")
print(f"Recommendation: {risk_assessment['recommendation']}")
print(f"Vulnerable Algorithms: {risk_assessment['affected_algorithms']}")
```

**Output Example**:
```
Risk Level: critical
Quantum Safe: True
Recommendation: Continue monitoring
Vulnerable Algorithms: []
```

---

## Migration Tools

### Classical to PQC Migration

The Migration Engine provides automated tools for transitioning from classical to post-quantum cryptography.

### Migration Phases

1. **Preparation**: Inventory current cryptographic assets
2. **Hybrid Deployment**: Run classical + PQC in parallel
3. **Gradual Migration**: Incrementally migrate data
4. **Verification**: Validate migration integrity
5. **Cutover**: Switch to PQC-only
6. **Cleanup**: Remove classical crypto artifacts

### Planning Migration

```python
from engines.crypto_war_enhanced import (
    MigrationEngine,
    CryptoAlgorithm
)

# Initialize migration engine
migration = MigrationEngine()

# Plan migration
plan = migration.plan_migration(
    source_algorithm=CryptoAlgorithm.RSA_2048,
    target_algorithm=CryptoAlgorithm.KYBER_768,
    data_count=10000
)

print(f"Migration ID: {plan['migration_id']}")
print(f"Complexity Score: {plan['complexity_score']}")
print(f"Estimated Time: {plan['estimated_time_seconds']}s")
print(f"Phases: {plan['phases']}")
print(f"Requires Downtime: {plan['requires_downtime']}")
```

### Executing Migration

```python
# Prepare data for migration
data_items = [
    {"id": 1, "encrypted_data": "...", "algorithm": "rsa-2048"},
    {"id": 2, "encrypted_data": "...", "algorithm": "rsa-2048"},
    # ... more items
]

# Execute migration
record = migration.execute_migration(
    migration_plan=plan,
    data_items=data_items
)

print(f"Status: {record.status}")
print(f"Items Migrated: {record.data_migrated}")
print(f"Verification Hash: {record.verification_hash}")
print(f"Rollback Available: {record.rollback_available}")
```

### Hybrid Mode (Classical + PQC)

Hybrid cryptography provides defense-in-depth during migration:

```python
# Enable hybrid mode
hybrid_config = migration.enable_hybrid_mode(
    classical_algorithm=CryptoAlgorithm.RSA_4096,
    pqc_algorithm=CryptoAlgorithm.DILITHIUM_3
)

print(f"Mode: {hybrid_config['mode']}")
print(f"Strategy: {hybrid_config['strategy']}")
print(f"Verification: {hybrid_config['verification']}")
```

**Benefits**:
- ✅ Protection against quantum AND classical attacks
- ✅ Gradual transition without breaking changes
- ✅ Fallback to classical if PQC issues arise
- ✅ Compliance with transitional standards

### Rollback Support

```python
# If migration fails, rollback
success = migration.rollback_migration(
    migration_id=plan['migration_id']
)

if success:
    print("Migration rolled back successfully")
else:
    print("Rollback failed - manual intervention required")
```

---

## Quick Start

### Basic Setup

```python
from engines.crypto_war_enhanced import create_pqc_engine

# Create PQC engine with default settings
engine = create_pqc_engine(threat_level="high")

# Check security status
status = engine.get_security_status()
print(f"Threat Level: {status['threat_level']}")
print(f"Quantum Safe: {status['crypto_profile']['quantum_safe']}")
```

### Complete Example: Secure Communication

```python
from engines.crypto_war_enhanced import (
    EnhancedCryptoWarEngine,
    CryptoAlgorithm,
    ThreatLevel
)

# Initialize engine
engine = EnhancedCryptoWarEngine(threat_level=ThreatLevel.HIGH)

# === SENDER SIDE ===

# 1. Generate Kyber key pair for key exchange
sender_kyber = engine.generate_pqc_keypair(
    algorithm=CryptoAlgorithm.KYBER_768,
    key_id="sender_kem"
)

# 2. Generate Dilithium key pair for signatures
sender_dilithium = engine.generate_pqc_keypair(
    algorithm=CryptoAlgorithm.DILITHIUM_3,
    key_id="sender_sig"
)

# 3. Prepare message
message = b"CLASSIFIED: Operation Quantum Shield initiated"

# 4. Sign message
signature = engine.pqc_sign(message, "sender_sig")

# 5. Encapsulate shared secret
ciphertext, shared_secret = engine.pqc_encapsulate("sender_kem")

# 6. Use shared_secret for symmetric encryption (AES-256)
from cryptography.fernet import Fernet
import base64
key = base64.urlsafe_b64encode(shared_secret)
cipher = Fernet(key)
encrypted_message = cipher.encrypt(message)

# Send: (encrypted_message, ciphertext, signature)

# === RECEIVER SIDE ===

# 7. Decapsulate to recover shared secret
recovered_secret = engine.pqc_decapsulate(ciphertext, "sender_kem")

# 8. Decrypt message
key = base64.urlsafe_b64encode(recovered_secret)
cipher = Fernet(key)
decrypted_message = cipher.decrypt(encrypted_message)

# 9. Verify signature
is_valid = engine.pqc_verify(decrypted_message, signature, "sender_sig")

if is_valid:
    print(f"✅ Secure message received: {decrypted_message.decode()}")
else:
    print("❌ Signature verification failed!")
```

---

## API Reference

### EnhancedCryptoWarEngine

Main class for PQC operations.

#### Constructor

```python
EnhancedCryptoWarEngine(threat_level: ThreatLevel = ThreatLevel.MEDIUM)
```

#### Methods

**`generate_pqc_keypair(algorithm, key_id=None)`**
- Generate post-quantum key pair
- Returns: `PQCKeyPair`

**`pqc_sign(message, key_id, algorithm=None)`**
- Sign message with PQC signature
- Returns: `bytes` (signature)

**`pqc_verify(message, signature, key_id)`**
- Verify PQC signature
- Returns: `bool`

**`pqc_encapsulate(key_id, algorithm=None)`**
- Encapsulate shared secret (KEM)
- Returns: `Tuple[bytes, bytes]` (ciphertext, shared_secret)

**`pqc_decapsulate(ciphertext, key_id)`**
- Decapsulate shared secret
- Returns: `bytes` (shared_secret)

**`assess_quantum_threat()`**
- Assess quantum computing threat
- Returns: `Dict[str, Any]`

**`migrate_to_pqc(data_items, target_algorithm)`**
- Migrate data to PQC
- Returns: `MigrationRecord`

**`get_security_status()`**
- Get comprehensive security status
- Returns: `Dict[str, Any]`

**`export_keys(key_id)`**
- Export public key for distribution
- Returns: `Dict[str, Any]`

---

### AlgorithmAgilityEngine

Dynamic algorithm selection based on threat level.

#### Methods

**`update_threat_level(new_level, reason, intelligence_source=None)`**
- Update threat level
- Returns: `CryptoProfile`

**`get_current_profile()`**
- Get current crypto profile
- Returns: `CryptoProfile`

**`recommend_algorithm(operation, data_sensitivity="high")`**
- Recommend algorithm for operation
- Operations: "kem", "signature", "hash", "symmetric"
- Returns: `CryptoAlgorithm`

**`assess_quantum_risk()`**
- Assess quantum risk
- Returns: `Dict[str, Any]`

---

### MigrationEngine

Automated migration from classical to PQC.

#### Methods

**`plan_migration(source_algorithm, target_algorithm, data_count)`**
- Plan migration
- Returns: `Dict[str, Any]`

**`execute_migration(migration_plan, data_items)`**
- Execute migration
- Returns: `MigrationRecord`

**`enable_hybrid_mode(classical_algorithm, pqc_algorithm)`**
- Enable hybrid crypto
- Returns: `Dict[str, Any]`

**`verify_migration(migration_id)`**
- Verify migration integrity
- Returns: `bool`

**`rollback_migration(migration_id)`**
- Rollback migration
- Returns: `bool`

---

## Security Considerations

### Implementation Notes

**⚠️ IMPORTANT**: The current implementation uses cryptographically secure hash functions to simulate PQC operations. For production deployment:

1. **Use Production Libraries**:
   - `liboqs` (Open Quantum Safe project)
   - `PQClean` reference implementations
   - NIST finalist official implementations

2. **Side-Channel Protection**:
   - Constant-time operations
   - Memory wiping after key operations
   - Protection against timing attacks

3. **Key Management**:
   - Hardware Security Modules (HSMs) for key storage
   - Proper key rotation policies
   - Secure key backup and recovery

4. **Random Number Generation**:
   - Use hardware RNG when available
   - NIST SP 800-90A compliant DRBG
   - Regular entropy pool monitoring

### Best Practices

#### Key Lifecycle

```python
# 1. Generate keys with proper algorithm selection
keypair = engine.generate_pqc_keypair(
    algorithm=CryptoAlgorithm.KYBER_768,
    key_id="production_key_2026"
)

# 2. Export public key for distribution
public_key_data = engine.export_keys("production_key_2026")

# 3. Store private key securely (HSM, encrypted storage)
# DO NOT store private keys in plaintext!

# 4. Rotate keys regularly (e.g., annually)
# 5. Revoke compromised keys immediately
# 6. Maintain key backup with access controls
```

#### Signature Verification

```python
# ALWAYS verify signatures before trusting data
is_valid = engine.pqc_verify(message, signature, key_id)

if not is_valid:
    raise SecurityError("Signature verification failed - potential tampering!")

# Only proceed with verified data
process_secure_data(message)
```

#### Hybrid Cryptography

For critical systems during PQC transition:

```python
# Use both classical and PQC
# Message must pass BOTH verifications

# Classical signature (RSA-4096)
classical_sig = sign_rsa(message, rsa_private_key)

# PQC signature (Dilithium)
pqc_sig = engine.pqc_sign(message, "dilithium_key")

# Verify both
if not (verify_rsa(message, classical_sig, rsa_public_key) and
        engine.pqc_verify(message, pqc_sig, "dilithium_key")):
    raise SecurityError("Dual signature verification failed!")
```

### Performance Optimization

#### Batch Operations

```python
# Generate multiple keys in batch
key_ids = []
for i in range(100):
    keypair = engine.generate_pqc_keypair(
        algorithm=CryptoAlgorithm.KYBER_768,
        key_id=f"batch_key_{i}"
    )
    key_ids.append(f"batch_key_{i}")
```

#### Signature Caching

```python
# Cache signature verification results for repeated checks
signature_cache = {}

def verify_with_cache(message, signature, key_id):
    cache_key = hashlib.sha256(message + signature).hexdigest()
    
    if cache_key in signature_cache:
        return signature_cache[cache_key]
    
    result = engine.pqc_verify(message, signature, key_id)
    signature_cache[cache_key] = result
    return result
```

### Compliance

#### FIPS Compatibility

- Kyber, Dilithium, SPHINCS+ are NIST-selected algorithms
- Awaiting FIPS 140-3 validation
- Use alongside FIPS-approved classical crypto during transition

#### Standards

- **NIST SP 800-208**: Stateful Hash-Based Signatures
- **NIST SP 800-186**: Discrete Logarithm-Based Crypto (transitioning away)
- **RFC 8391**: XMSS (Stateful Hash-Based Signatures)
- **CNSA 2.0**: NSA Commercial National Security Algorithm Suite

---

## Troubleshooting

### Common Issues

#### Issue: Large Signature Sizes

**Problem**: SPHINCS+ signatures are ~49KB

**Solution**:
```python
# For bandwidth-constrained scenarios, use Dilithium
engine.generate_pqc_keypair(
    algorithm=CryptoAlgorithm.DILITHIUM_3,  # ~3.3KB signatures
    key_id="bandwidth_optimized"
)
```

#### Issue: Slow Signing with SPHINCS+

**Problem**: SPHINCS+ signing takes 50-100ms

**Solution**:
```python
# Use SPHINCS+ only for long-term signatures
# Use Dilithium for real-time applications

if signature_lifetime == "long_term":
    algorithm = CryptoAlgorithm.SPHINCS_PLUS_256F
else:
    algorithm = CryptoAlgorithm.DILITHIUM_3  # Fast signing (~2ms)
```

#### Issue: Migration Downtime

**Problem**: Can't afford downtime during migration

**Solution**:
```python
# Use hybrid mode for zero-downtime migration
migration.enable_hybrid_mode(
    classical_algorithm=CryptoAlgorithm.RSA_4096,
    pqc_algorithm=CryptoAlgorithm.KYBER_768
)

# Gradually migrate data while both systems run in parallel
```

---

## Demo Script

Run the included demo to see all features:

```bash
python engines/crypto_war_enhanced.py
```

**Expected Output**:
```
=== Enhanced Cryptographic War Engine Demo ===

1. Generating Dilithium key pair...
   Algorithm: dilithium-3
   Public key size: 1952 bytes
   Private key size: 4000 bytes

2. Signing message with Dilithium...
   Signature size: 3293 bytes
   Verification: PASSED

3. Kyber key encapsulation...
   Ciphertext size: 1088 bytes
   Shared secret size: 32 bytes
   Decapsulation: SUCCESS

4. Quantum threat assessment...
   Risk level: low
   Quantum safe: True
   Recommendation: Continue monitoring

5. Migration to PQC...
   Migration ID: a1b2c3d4e5f6...
   Status: completed
   Items migrated: 10

6. Security status report...
   Threat level: high
   Total keys: 2
   PQC keys: 2
   Migrations: 1

=== Demo Complete ===
```

---

## Further Reading

### NIST PQC Resources

- [NIST PQC Project](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [Kyber Specification](https://pq-crystals.org/kyber/)
- [Dilithium Specification](https://pq-crystals.org/dilithium/)
- [SPHINCS+ Specification](https://sphincs.org/)

### Implementation Libraries

- [liboqs](https://github.com/open-quantum-safe/liboqs) - Open Quantum Safe
- [PQClean](https://github.com/PQClean/PQClean) - Clean PQC implementations
- [Bouncy Castle](https://www.bouncycastle.org/) - Crypto library with PQC support

### Security Analysis

- [ETSI Quantum-Safe Cryptography](https://www.etsi.org/technologies/quantum-safe-cryptography)
- [BSI Technical Guidelines](https://www.bsi.bund.de/EN/Topics/Cryptography/cryptography_node.html)
- [ANSSI Recommendations](https://www.ssi.gouv.fr/)

---

## Support

For questions or issues:
- Review this documentation
- Check the demo script
- Examine the source code in `crypto_war_enhanced.py`

**Security Issues**: Report immediately through secure channels

---

**Last Updated**: 2026-03-05  
**Version**: 1.0.0  
**Status**: Production Ready (with production library integration)
