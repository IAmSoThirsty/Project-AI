# Sovereign Vault - Implementation Phase Plan

**Three-Phase Deployment Strategy**  
**Rationale: Do Not Bind Hardware to Unproven Architecture**

---

## Strategic Principle

> "USB token initialization is the moment you start creating real trust state. If you initialize tokens before proving the security model, you risk baking weak assumptions into: recovery, identity binding, audit continuity, operational workflow."

**Engineering Mandate:** Prove the architecture before binding hardware.

---

## Phase 1: Proof Gates (CURRENT PHASE)

**Objective:** Implement minimum proof-bearing versions of 5 blocking proofs.

**Not:** Implement all possible hardening  
**Instead:** Implement enough to prove each security property holds

### Proof 5: Enforced Vault/Launcher Separation ⏳

**Priority:** 1 (Quick win, architectural clarity)

**Implementation:**

- Remove `execute_tool()` method from vault
- Add `read_tool_to_buffer()` method (memory-only)
- Document separation: vault stores, launcher executes
- Update architecture diagrams

**Validation:**

- ✅ No execution methods in vault class
- ✅ Read-only tool access documented
- ✅ Launcher system clearly separated

**Timeline:** 30 minutes

---

### Proof 3: Zero Plaintext Residue ⏳

**Priority:** 2 (Foundation for security)

**Minimum Proof Implementation:**
```python
class SecureMemory:

    - Disable core dumps (resource.RLIMIT_CORE = 0)
    - Secure memory wipe (triple overwrite with barrier)
    - Log sanitization (redact keys/passphrases)
    - Document shell history suppression

```

**What We're Proving:**

- Keys wiped from memory after use
- No keys in log files
- No keys in crash dumps
- Shell history protection documented

**What We're NOT Implementing (yet):**

- mlock() (requires root, platform-specific)
- tmpfs enforcement (OS-dependent)
- Full memory page locking

**Validation:**

- ✅ Memory wiping tested (inspect buffer after wipe)
- ✅ Log sanitization tested (keys not in logs)
- ✅ Core dumps disabled (ulimit -c shows 0)

**Timeline:** 2 hours

---

### Proof 1: Token Clone Resistance ⏳

**Priority:** 3 (Enables secure token binding)

**Minimum Proof Implementation:**
```python
class RobustUSBFingerprint:

    - Multi-factor device fingerprint (serial + partition UUID + filesystem UUID)
    - Scoring system (100% = all match, 80% = acceptable, <50% = fail)
    - Stable across reinsert (test: unplug/replug)
    - Fails on clone (test: copy files to different USB)

```

**What We're Proving:**

- Fingerprint stable across reinsert/reboot
- Fingerprint fails when files copied to different USB
- No false positives (legitimate reinsert passes)
- No false negatives (clone attempt detected)

**What We're NOT Implementing (yet):**

- Challenge-response protocol
- Timing analysis
- TPM PCR binding

**Validation:**

- ✅ Test: Reinsert same USB 10 times (should pass)
- ✅ Test: Copy token to different USB (should fail)
- ✅ Test: Reboot with USB inserted (should pass)

**Timeline:** 3 hours

---

### Proof 4: Tamper-Evident Audit Continuity ⏳

**Priority:** 4 (Enables tamper detection)

**Minimum Proof Implementation:**
```python
class TamperEvidentAudit:

    - Verify audit log integrity on mount
    - External Merkle root pinning (simple file-based)
    - Detect gaps in log sequence
    - Constitutional freeze on tamper

```

**What We're Proving:**

- Audit log tampering detected
- Vault refuses to mount if logs modified
- Merkle roots pinned externally survive vault compromise

**What We're NOT Implementing (yet):**

- Blockchain anchoring
- RFC 3161 timestamp verification (already have infrastructure)
- Hardware-protected storage (TPM NV RAM)

**Validation:**

- ✅ Test: Modify audit log entry (mount should fail)
- ✅ Test: Delete audit entries (mount should fail)
- ✅ Test: Intact logs (mount should succeed)

**Timeline:** 3 hours

---

### Proof 2: Lawful Recovery Path ⏳

**Priority:** 5 (Prevents self-denial)

**Minimum Proof Implementation:**
```python
class VaultRecovery:

    - Shamir Secret Sharing (split master key)
    - Recovery escrow creation (3-of-5 example)
    - Administrative override ceremony (documented procedure)
    - Constitutional audit of recovery attempt

```

**What We're Proving:**

- Lost USB doesn't permanently seal vault
- Recovery requires quorum (multiple trustees)
- All recovery attempts audited
- Administrative override requires justification + time delay

**What We're NOT Implementing (yet):**

- Full trustee identity verification system
- Out-of-band verification (phone calls, video)
- Automated time-delay enforcement
- Integration with external identity providers

**Validation:**

- ✅ Test: Create escrow, lose USB, recover from shards
- ✅ Test: Recovery requires threshold (2-of-3 not enough if threshold is 3)
- ✅ Test: Recovery logged in constitutional audit

**Timeline:** 4 hours

---

## Phase 1 Exit Criteria

Before proceeding to Phase 2 (USB token initialization):

1. ✅ **Proof 5:** Vault class has no execution methods
2. ✅ **Proof 3:** Memory wiping tested, log sanitization active
3. ✅ **Proof 1:** Fingerprint survives reinsert, fails on clone
4. ✅ **Proof 4:** Audit tampering detected, mount refused
5. ✅ **Proof 2:** Recovery from escrow tested and documented

**Total Estimated Time:** ~12 hours of focused implementation

---

## Phase 2: USB Token Initialization (BLOCKED)

**Unlocks when:** Phase 1 exit criteria met

**Objective:** Initialize USB token with proven architecture

**Actions:**

- Create USB token with robust fingerprint
- Generate master key with escrow backup
- Pin initial Merkle roots externally
- Document recovery ceremony procedures
- Test token mount/unmount cycle

**Deliverable:** One functional USB token with proven security properties

---

## Phase 3: Controlled Pilot (BLOCKED)

**Unlocks when:** Phase 2 complete

**Objective:** Validate operational workflow with real tools

**Test Scenario:**

- **Tool:** One noncritical penetration testing tool (e.g., nmap)
- **Token:** One test USB token (not production)
- **Drill:**
  1. Mount vault with USB token
  2. Add test tool to vault
  3. Read tool to buffer (verify decryption)
  4. Unmount vault (verify key wipe)
  5. Simulate USB loss (trigger recovery)
  6. Tamper with audit log (verify detection)
  7. Clone USB token (verify rejection)

**Success Criteria:**

- All 5 proofs validated in operational workflow
- No false positives or false negatives
- Recovery ceremony executable
- Audit trail complete and tamper-evident

---

## Current Status

**Phase:** 1 (Proof Gates)  
**Started:** 2026-04-10T00:45:00Z  
**Progress:** 0/5 proofs implemented  
**Blocking:** Phase 2 (USB token initialization)  
**Blocking:** Phase 3 (Controlled pilot)

**Next Action:** Implement Proof 5 (Vault/Launcher Separation)

---

## Risk Management

**Risk:** Pressure to skip proofs and initialize USB token early  
**Mitigation:** This document. Re-read strategic principle.

**Risk:** Scope creep (implementing all possible hardening)  
**Mitigation:** Focus on minimum proof-bearing versions only.

**Risk:** Proof implementation takes too long  
**Mitigation:** Time-boxed implementation (~12 hours total).

---

## Acknowledgment

**Principal Architect Directive:**
> "Do not bind hardware to an architecture you already know is unproven."

**Implementation Plan:** Three-phase deployment  
**Current Phase:** Proof gates (minimum proof-bearing versions)  
**Next Phase:** USB token initialization (after proofs)  
**Final Phase:** Controlled pilot (validation)

**This is the disciplined path to production-grade secure storage.**

---

**Status:** Phase 1 in progress (0/5 proofs complete)  
**Timeline:** ~12 hours to Phase 1 completion  
**Blocking:** Hardware binding until architecture proven

---

*"First prove the architecture. Then bind the hardware. Then validate the workflow."*
