# Migration Guide: Classical to Post-Quantum Cryptography

**Comprehensive guide for transitioning from classical cryptography to PQC**

## Table of Contents

1. [Overview](#overview)
2. [Why Migrate Now](#why-migrate-now)
3. [Migration Phases](#migration-phases)
4. [Pre-Migration Checklist](#pre-migration-checklist)
5. [Migration Strategies](#migration-strategies)
6. [Step-by-Step Guide](#step-by-step-guide)
7. [Rollback Procedures](#rollback-procedures)
8. [Testing & Validation](#testing--validation)
9. [Common Issues](#common-issues)
10. [Timeline Recommendations](#timeline-recommendations)

---

## Overview

This guide provides a systematic approach to migrating from classical cryptography (RSA, ECC) to post-quantum cryptography (Kyber, Dilithium, SPHINCS+).

**Migration Goals**:
- ✅ Zero data loss
- ✅ Minimal downtime
- ✅ Backward compatibility during transition
- ✅ Rollback capability
- ✅ Comprehensive verification

---

## Why Migrate Now

### The Quantum Threat Timeline

| Year | Quantum Computing Milestone | Cryptographic Impact |
|------|----------------------------|---------------------|
| 2024-2025 | 100-1000 qubits (research) | No immediate threat |
| 2026-2028 | Early error correction | **Start migrations** |
| 2028-2030 | Cryptographically Relevant QC | **Critical period** |
| 2030+ | Widespread quantum capability | Classical crypto broken |

### "Harvest Now, Decrypt Later"

Adversaries are collecting encrypted data TODAY to decrypt when quantum computers become available. Data encrypted with RSA/ECC is at risk.

**Protected Data Lifetime**:
- Medical records: 50+ years
- Financial records: 7-10 years
- Government classified: 25+ years
- Personal communications: indefinite

If your data needs to remain confidential beyond 2030, migrate NOW.

### Regulatory Pressure

- **NIST**: Published PQC standards (2022-2024)
- **NSA CNSA 2.0**: Quantum-resistant by 2030
- **EU**: Quantum-safe requirements emerging
- **Financial Sector**: PCI-DSS updates expected

---

## Migration Phases

### Phase 1: Assessment (1-2 weeks)

**Objectives**:
- Inventory current cryptographic assets
- Identify data sensitivity and lifetime
- Map dependencies
- Estimate migration scope

**Deliverables**:
- Crypto asset inventory
- Risk assessment
- Migration plan

### Phase 2: Preparation (2-4 weeks)

**Objectives**:
- Install PQC libraries
- Train team
- Set up test environment
- Create rollback procedures

**Deliverables**:
- Test environment
- Migration scripts
- Training materials

### Phase 3: Hybrid Deployment (4-8 weeks)

**Objectives**:
- Deploy PQC alongside classical crypto
- Run both systems in parallel
- Monitor performance
- Validate interoperability

**Deliverables**:
- Hybrid crypto system
- Performance metrics
- Validation reports

### Phase 4: Gradual Migration (8-16 weeks)

**Objectives**:
- Migrate data incrementally
- Re-encrypt sensitive data
- Rotate keys
- Monitor for issues

**Deliverables**:
- Migrated data
- New key infrastructure
- Migration reports

### Phase 5: Verification (2-4 weeks)

**Objectives**:
- Verify all data migrated
- Test PQC operations
- Performance tuning
- Security audit

**Deliverables**:
- Verification report
- Performance report
- Security audit

### Phase 6: Cutover (1-2 weeks)

**Objectives**:
- Switch to PQC-only
- Disable classical crypto
- Monitor stability
- Document final state

**Deliverables**:
- PQC-only system
- Final documentation
- Lessons learned

### Phase 7: Cleanup (2-4 weeks)

**Objectives**:
- Remove classical crypto artifacts
- Archive old keys (for historical decryption)
- Update documentation
- Continuous monitoring

**Deliverables**:
- Clean system
- Archived keys
- Updated docs

---

## Pre-Migration Checklist

### Inventory

- [ ] List all cryptographic operations (encryption, signing, key exchange)
- [ ] Identify algorithms in use (RSA, ECC, AES, etc.)
- [ ] Document key sizes and lifetimes
- [ ] Map data sensitivity levels
- [ ] Identify compliance requirements

### Technical Readiness

- [ ] Sufficient computing resources (CPU, memory)
- [ ] Network bandwidth for larger PQC messages
- [ ] Storage for larger keys/signatures
- [ ] Backup systems in place
- [ ] Monitoring tools configured

### Organizational Readiness

- [ ] Executive sponsorship
- [ ] Budget allocated
- [ ] Team trained on PQC
- [ ] Stakeholders informed
- [ ] Change management process

### Risk Assessment

- [ ] Identified critical systems
- [ ] Documented dependencies
- [ ] Created rollback plan
- [ ] Defined success criteria
- [ ] Established communication plan

---

## Migration Strategies

### Strategy 1: Big Bang Migration

**Description**: Migrate everything at once during maintenance window

**Pros**:
- ✅ Fastest migration
- ✅ Simpler coordination
- ✅ Clear cutover point

**Cons**:
- ❌ Requires downtime
- ❌ Higher risk
- ❌ Difficult rollback

**Best for**: Small systems, non-critical applications

### Strategy 2: Gradual Migration (Recommended)

**Description**: Migrate incrementally over time

**Pros**:
- ✅ Zero/minimal downtime
- ✅ Lower risk
- ✅ Easy rollback
- ✅ Learn as you go

**Cons**:
- ❌ Longer timeline
- ❌ Complex coordination
- ❌ Hybrid system complexity

**Best for**: Large systems, critical applications

### Strategy 3: Hybrid Cryptography

**Description**: Run classical AND PQC simultaneously

**Pros**:
- ✅ Defense in depth
- ✅ Backward compatible
- ✅ Gradual transition
- ✅ Maximum security

**Cons**:
- ❌ Higher overhead
- ❌ Complex implementation
- ❌ Larger message sizes

**Best for**: High-security systems, transitional period

---

## Step-by-Step Guide

### Step 1: Install Enhanced Crypto Engine

```python
# Verify installation
from engines.crypto_war_enhanced import create_pqc_engine

engine = create_pqc_engine(threat_level="medium")
print(f"Engine ready: {engine is not None}")
```

### Step 2: Inventory Current Cryptography

```python
from engines.crypto_war_enhanced import MigrationEngine, CryptoAlgorithm

migration = MigrationEngine()

# Document current state
current_assets = {
    "encryption": "RSA-2048",
    "signatures": "RSA-2048",
    "key_exchange": "ECDH-P256",
    "data_count": 10000
}

print(f"Current assets: {current_assets}")
```

### Step 3: Plan Migration

```python
# Plan migration from RSA to Kyber
plan = migration.plan_migration(
    source_algorithm=CryptoAlgorithm.RSA_2048,
    target_algorithm=CryptoAlgorithm.KYBER_768,
    data_count=current_assets["data_count"]
)

print(f"Migration ID: {plan['migration_id']}")
print(f"Phases: {plan['phases']}")
print(f"Estimated time: {plan['estimated_time_seconds']}s")
print(f"Complexity: {plan['complexity_score']}")
```

### Step 4: Enable Hybrid Mode

```python
# Run both classical and PQC during migration
hybrid_config = migration.enable_hybrid_mode(
    classical_algorithm=CryptoAlgorithm.RSA_2048,
    pqc_algorithm=CryptoAlgorithm.KYBER_768
)

print(f"Hybrid mode enabled: {hybrid_config['mode']}")
print(f"Verification strategy: {hybrid_config['verification']}")
```

### Step 5: Test in Staging

```python
from engines.crypto_war_enhanced import EnhancedCryptoWarEngine, CryptoAlgorithm

# Create test engine
test_engine = EnhancedCryptoWarEngine()

# Test PQC operations
print("\n=== Testing PQC Operations ===")

# Test 1: Key generation
keypair = test_engine.generate_pqc_keypair(
    algorithm=CryptoAlgorithm.KYBER_768,
    key_id="test_key"
)
print(f"✓ Key generation successful")

# Test 2: Encapsulation/Decapsulation
ciphertext, secret1 = test_engine.pqc_encapsulate("test_key")
secret2 = test_engine.pqc_decapsulate(ciphertext, "test_key")
print(f"✓ KEM operations successful")

# Test 3: Signatures
sig_key = test_engine.generate_pqc_keypair(
    algorithm=CryptoAlgorithm.DILITHIUM_3,
    key_id="sig_key"
)
message = b"Test message"
signature = test_engine.pqc_sign(message, "sig_key")
is_valid = test_engine.pqc_verify(message, signature, "sig_key")
print(f"✓ Signature operations successful: {is_valid}")
```

### Step 6: Migrate Data in Batches

```python
# Prepare data for migration
data_items = [
    {"id": i, "encrypted_data": f"legacy_encrypted_{i}", "algorithm": "rsa-2048"}
    for i in range(100)  # Start with small batch
]

# Execute migration
record = migration.execute_migration(plan, data_items)

print(f"\n=== Migration Batch Complete ===")
print(f"Status: {record.status}")
print(f"Items migrated: {record.data_migrated}/{len(data_items)}")
print(f"Verification hash: {record.verification_hash}")
print(f"Rollback available: {record.rollback_available}")
```

### Step 7: Verify Migration

```python
# Verify migration integrity
is_valid = migration.verify_migration(record.migration_id)

if is_valid:
    print("✓ Migration verification PASSED")
else:
    print("✗ Migration verification FAILED - initiating rollback")
    migration.rollback_migration(record.migration_id)
```

### Step 8: Monitor Performance

```python
import time

# Performance testing
print("\n=== Performance Metrics ===")

# Classical RSA (for comparison)
# ... your existing RSA code ...

# PQC Kyber
start = time.time()
for _ in range(100):
    ciphertext, secret = test_engine.pqc_encapsulate("test_key")
kyber_time = (time.time() - start) / 100

print(f"Kyber encapsulation: {kyber_time*1000:.2f}ms per operation")

# Dilithium signatures
start = time.time()
for _ in range(100):
    sig = test_engine.pqc_sign(b"test", "sig_key")
dilithium_time = (time.time() - start) / 100

print(f"Dilithium signing: {dilithium_time*1000:.2f}ms per operation")
```

### Step 9: Full Cutover

```python
from engines.crypto_war_enhanced import ThreatLevel

# After successful gradual migration, switch to PQC-only
engine = EnhancedCryptoWarEngine(threat_level=ThreatLevel.HIGH)

# Generate production PQC keys
prod_keys = {
    "kem": engine.generate_pqc_keypair(CryptoAlgorithm.KYBER_768, "prod_kem"),
    "sig": engine.generate_pqc_keypair(CryptoAlgorithm.DILITHIUM_3, "prod_sig")
}

# Disable classical crypto
# (implementation-specific)

print("\n=== PQC-Only Mode Active ===")
status = engine.get_security_status()
print(f"Quantum safe: {status['crypto_profile']['quantum_safe']}")
print(f"PQC keys: {status['pqc_keys']}/{status['total_keys']}")
```

---

## Rollback Procedures

### Scenario 1: Migration Fails Validation

```python
# If verification fails
if not migration.verify_migration(record.migration_id):
    print("Migration failed validation - rolling back...")
    
    success = migration.rollback_migration(record.migration_id)
    
    if success:
        print("✓ Rollback successful - system restored")
    else:
        print("✗ Rollback failed - manual intervention required")
        # Trigger incident response
```

### Scenario 2: Performance Issues

```python
# If PQC causes unacceptable performance degradation
from engines.crypto_war_enhanced import AlgorithmAgilityEngine, ThreatLevel

agility = AlgorithmAgilityEngine()

# Temporarily downgrade to hybrid mode
migration.enable_hybrid_mode(
    classical_algorithm=CryptoAlgorithm.RSA_4096,
    pqc_algorithm=CryptoAlgorithm.KYBER_768
)

print("Reverted to hybrid mode for performance optimization")
```

### Scenario 3: Compatibility Issues

```python
# If PQC breaks interoperability with legacy systems
print("Compatibility issue detected")
print("Maintaining classical crypto for legacy interfaces")
print("PQC used only for internal operations")

# Implement protocol negotiation
# Legacy systems use RSA
# Modern systems use PQC
```

---

## Testing & Validation

### Unit Tests

```bash
# Run PQC test suite
pytest engines/test_crypto_war_enhanced.py -v
```

### Integration Tests

```python
# Test end-to-end workflow
def test_migration_integration():
    engine = EnhancedCryptoWarEngine()
    migration = MigrationEngine()
    
    # 1. Generate PQC keys
    engine.generate_pqc_keypair(CryptoAlgorithm.KYBER_768, "test")
    
    # 2. Migrate sample data
    data = [{"id": i} for i in range(10)]
    plan = migration.plan_migration(
        CryptoAlgorithm.RSA_2048,
        CryptoAlgorithm.KYBER_768,
        len(data)
    )
    record = migration.execute_migration(plan, data)
    
    # 3. Verify
    assert migration.verify_migration(record.migration_id)
    assert record.status == "completed"
    
    print("✓ Integration test passed")

test_migration_integration()
```

### Performance Tests

```python
import time

def benchmark_pqc():
    engine = EnhancedCryptoWarEngine()
    
    # Benchmark key generation
    start = time.time()
    engine.generate_pqc_keypair(CryptoAlgorithm.KYBER_768, "bench")
    keygen_time = time.time() - start
    
    # Benchmark encapsulation
    start = time.time()
    ct, ss = engine.pqc_encapsulate("bench")
    encap_time = time.time() - start
    
    # Benchmark decapsulation
    start = time.time()
    ss2 = engine.pqc_decapsulate(ct, "bench")
    decap_time = time.time() - start
    
    print(f"Keygen: {keygen_time*1000:.2f}ms")
    print(f"Encap:  {encap_time*1000:.2f}ms")
    print(f"Decap:  {decap_time*1000:.2f}ms")

benchmark_pqc()
```

### Security Validation

```python
# Verify quantum safety
assessment = engine.assess_quantum_threat()

assert assessment['quantum_safe'] == True
assert assessment['risk_level'] == 'low'

print("✓ Security validation passed")
```

---

## Common Issues

### Issue 1: Large Signature Sizes

**Problem**: SPHINCS+ signatures are ~49KB

**Solutions**:
1. Use Dilithium instead (~3.3KB signatures)
2. Compress signatures before transmission
3. Use batch verification
4. Reserve SPHINCS+ for long-term signatures only

### Issue 2: Performance Overhead

**Problem**: PQC operations slower than classical

**Solutions**:
1. Use hardware acceleration if available
2. Implement caching for repeated operations
3. Use faster variants (e.g., Kyber512 vs Kyber1024)
4. Parallelize operations

### Issue 3: Backward Compatibility

**Problem**: Legacy systems don't support PQC

**Solutions**:
1. Use hybrid mode (classical + PQC)
2. Implement protocol negotiation
3. Maintain classical endpoints for legacy clients
4. Gradual client upgrades

### Issue 4: Storage Requirements

**Problem**: PQC keys/signatures require more storage

**Solutions**:
1. Upgrade storage capacity
2. Compress archived signatures
3. Implement key rotation to purge old keys
4. Use cloud storage for archives

---

## Timeline Recommendations

### Small Organization (<100 systems)

- **Total**: 3-6 months
- Assessment: 2 weeks
- Preparation: 3 weeks
- Hybrid: 4 weeks
- Migration: 6 weeks
- Verification: 2 weeks
- Cutover: 1 week
- Cleanup: 2 weeks

### Medium Organization (100-1000 systems)

- **Total**: 6-12 months
- Assessment: 4 weeks
- Preparation: 6 weeks
- Hybrid: 8 weeks
- Migration: 12 weeks
- Verification: 4 weeks
- Cutover: 2 weeks
- Cleanup: 4 weeks

### Large Organization (1000+ systems)

- **Total**: 12-24 months
- Assessment: 8 weeks
- Preparation: 12 weeks
- Hybrid: 16 weeks
- Migration: 24 weeks
- Verification: 8 weeks
- Cutover: 4 weeks
- Cleanup: 8 weeks

---

## Success Criteria

- [ ] All sensitive data re-encrypted with PQC
- [ ] Zero data loss during migration
- [ ] Performance within acceptable limits
- [ ] All systems verified quantum-safe
- [ ] Rollback procedures tested
- [ ] Team trained on PQC operations
- [ ] Documentation updated
- [ ] Compliance requirements met
- [ ] Monitoring in place
- [ ] Incident response plan updated

---

## Post-Migration

### Ongoing Monitoring

```python
# Regular security status checks
def monitor_security():
    engine = create_pqc_engine()
    status = engine.get_security_status()
    
    print(f"Quantum safe: {status['crypto_profile']['quantum_safe']}")
    print(f"PQC coverage: {status['pqc_keys']}/{status['total_keys']}")
    
    # Alert if quantum safety compromised
    if not status['crypto_profile']['quantum_safe']:
        send_alert("Quantum safety compromised!")

# Run daily
import schedule
schedule.every().day.at("09:00").do(monitor_security)
```

### Key Rotation

```python
# Rotate keys periodically (e.g., annually)
def rotate_keys():
    engine = EnhancedCryptoWarEngine()
    
    # Generate new keys
    new_key = engine.generate_pqc_keypair(
        algorithm=CryptoAlgorithm.KYBER_768,
        key_id=f"prod_key_{datetime.now().year}"
    )
    
    # Migrate to new key
    # ... migration logic ...
    
    # Archive old key (for historical decryption)
    # ... archival logic ...
    
    print(f"Key rotated: {new_key.metadata['key_id']}")

# Run annually
schedule.every().year.do(rotate_keys)
```

### Continuous Improvement

- Monitor NIST PQC updates
- Track quantum computing advances
- Update algorithms as needed
- Participate in PQC community
- Share lessons learned

---

## Resources

- [NIST PQC Project](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [NSA CNSA 2.0](https://media.defense.gov/2022/Sep/07/2003071834/-1/-1/0/CSA_CNSA_2.0_ALGORITHMS_.PDF)
- [Post-Quantum Crypto Guide](POST_QUANTUM_CRYPTO_GUIDE.md)
- [PQC Examples](PQC_EXAMPLES.md)

---

**Last Updated**: 2026-03-05  
**Version**: 1.0.0  
**Status**: Production Ready
