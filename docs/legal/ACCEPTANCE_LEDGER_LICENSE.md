# Project-AI Acceptance Ledger License

**Version:** 1.0.0  
**Effective Date:** February 8, 2026

---

## VERBATIM LICENSE (CORE)

### 1. Authority
The Acceptance Ledger is the authoritative record of agreement acceptance.

### 2. Binding Proof
Cryptographic signatures and timestamps constitute binding acceptance evidence.

### 3. Non-Repudiation
Entries cannot be denied, altered, or retroactively contested.

### 4. Public Verifiability
Ledger proofs may be publicly verified without exposing private data.

### 5. Enforcement
Invalid or missing ledger entries disable governed functionality.

---

## DETAILED PROVISIONS

### I. PURPOSE AND AUTHORITY

The Acceptance Ledger is the **immutable, cryptographically-secured, legally-binding record** of all agreements, acceptances, and governance actions in Project-AI.

**Legal Supremacy:**
- The ledger is the system of record for all legal acceptance
- In case of dispute, ledger entries supersede other claims
- Cryptographic proofs constitute admissible evidence
- Courts recognize ledger as authoritative (subject to verification)

### II. LEDGER ARCHITECTURE

**Technical Implementation:**
- **Dual storage:** File-based append-only log + SQLite with WAL mode
- **Hash chaining:** Each entry links to previous entry via SHA-256 hash
- **Digital signatures:** Ed25519 (software) or hardware-backed (TPM/HSM)
- **Timestamps:** UTC epoch time + optional RFC 3161 timestamp authority
- **Immutability:** Append-only; no deletions or modifications permitted

**Cryptographic Integrity:**
- Entries form an unbroken hash chain
- Any tampering breaks the chain and is immediately detected
- Signatures cryptographically bind users to acceptances
- Public key infrastructure enables verification

### III. WHAT IS RECORDED

**The ledger records:**

1. **Initial Acceptances:**
   - Master Services Agreement (MSA)
   - Jurisdictional Annexes
   - License selection (tier, term, pricing)
   - Privacy Policy and data handling terms

2. **Ongoing Events:**
   - Tier upgrades or downgrades
   - Jurisdictional changes
   - Policy updates and re-acceptances
   - Commercial license activations
   - Government authorizations

3. **Enforcement Actions:**
   - Violations and warnings
   - Terminations (with reason)
   - Audit locks
   - Reinstatements (if any)

4. **Governance Actions:**
   - Critical system decisions requiring user consent
   - Safety override activations
   - Emergency stops
   - Compliance incidents

### IV. BINDING PROOF

**Ledger entries constitute legal proof of:**

**Acceptance:** User agreed to specified terms at specified time
**Identity:** User identified by email, public key, and cryptographic signature
**Timestamp:** Action occurred at recorded time (verified by timestamp authority if applicable)
**Integrity:** Entry has not been altered since creation (hash chain verification)
**Non-repudiation:** User cannot later deny acceptance (cryptographic signature)

**Admissibility:**
- Ledger entries are self-authenticating (cryptographic proof)
- No additional authentication required for court admission
- Burden on challenger to prove forgery (cryptographically infeasible)
- Meets Federal Rules of Evidence 902(14) (certified machine-generated records)

### V. NON-REPUDIATION

**Once recorded, entries CANNOT be:**
- Denied ("I never agreed to that")
- Altered ("I agreed to different terms")
- Backdated ("I agreed earlier than recorded")
- Deleted ("Remove my acceptance")
- Disavowed ("That wasn't me")

**Exceptions (Extremely Limited):**
- Fraud or identity theft with evidence
- System error with technical proof
- Court order (only for illegal content)

**Even these exceptions:**
- Create new ledger entry documenting exception
- Do not delete original entry
- Maintain full audit trail

### VI. PUBLIC VERIFIABILITY

**Anyone can verify ledger integrity:**

**Public Verification Endpoint:**
```
GET /verify/acceptance/{entry_id}
```

**Returns:**
- Entry details (user-controlled public data)
- Cryptographic signature
- Hash chain position and validity
- Timestamp authority verification (if applicable)
- Hardware attestation (if applicable)

**Privacy-Preserving:**
- Verification does not expose private user data
- Only metadata and cryptographic proofs disclosed
- User can revoke public verification (but entry remains)

**Zero-Trust Architecture:**
- Verification requires no trust in Project-AI
- Cryptographic proofs are independently verifiable
- Source code is open for audit
- No "just trust us" required

### VII. ENFORCEMENT MECHANISM

**The ledger is not just recordkeeping—it is active enforcement:**

**Boot-Time Validation:**
```python
def enforce_acceptance():
    if not ledger.has_valid_entry(user_id):
        disable_all_features()
        require_acceptance()
    
    if ledger.is_terminated(user_id):
        permanent_lockout()
    
    if ledger.entry_expired(user_id):
        require_reacceptance()
```

**Runtime Enforcement:**
- Feature access gated by ledger verification
- Tier limitations enforced via ledger
- Commercial use requires valid commercial ledger entry
- Government use requires authorization entry

**Governance Enforcement:**
- Triumvirate checks ledger before allowing governed actions
- Violations recorded immediately and immutably
- Terminations are permanent and cannot be overridden

### VIII. CRYPTOGRAPHIC SIGNATURES

**Software-Backed Signing (Solo, Company Tiers):**
- Ed25519 elliptic curve cryptography
- Private key generated by user (or on user's behalf)
- Public key stored in ledger
- Signatures mathematically verifiable

**Hardware-Backed Signing (Government Tier):**
- TPM (Trusted Platform Module) 2.0
- HSM (Hardware Security Module) - FIPS 140-2/3
- Private key never leaves hardware
- Attestation proves hardware backing
- Enhanced security against key theft
- Mandatory for government deployments

**Signature Verification:**
```python
def verify_signature(entry):
    public_key = ed25519.PublicKey(entry.public_key)
    payload = entry.compute_entry_hash()
    signature = entry.signature
    
    try:
        public_key.verify(signature, payload)
        return True
    except InvalidSignature:
        return False
```

### IX. TIMESTAMP AUTHORITY

**Optional for Solo/Company, Required for Government:**

**RFC 3161 Timestamp Authority:**
- Third-party timestamp server
- Cryptographically proves time of entry
- Cannot be backdated by Project-AI
- Independent verification of temporal ordering

**Supported TSAs:**
- DigiCert Timestamp Authority
- GlobalSign Timestamp Service
- Sectigo TSA
- OpenTimestamps (Bitcoin-anchored)
- eIDAS-compliant TSAs (EU)

**Benefits:**
- Legal evidence of time
- Protection against Project-AI time manipulation
- Regulatory compliance (eIDAS, qualified timestamps)
- Enhanced non-repudiation

### X. HASH CHAIN INTEGRITY

**Each entry links to previous entry:**

```python
entry_n.previous_entry_hash = entry_(n-1).compute_entry_hash()
```

**Chain Verification:**
1. Start with genesis entry (previous_hash = null)
2. Compute hash of entry
3. Verify next entry's previous_hash matches computed hash
4. Repeat for entire chain
5. Any mismatch indicates tampering

**Benefits:**
- Tamper-evidence (cannot alter past entries)
- Ordering guarantee (cannot reorder entries)
- Completeness check (missing entries detected)
- Cryptographic proof of history

### XI. DATA PROTECTION AND PRIVACY

**What is stored:**
- User identifier (pseudonymous ID)
- Email address
- Acceptance type and document hash
- Timestamp and cryptographic proofs
- Public key (not private key)

**What is NOT stored:**
- Passwords or credentials
- Private keys
- Sensitive personal data
- Payment information (stored separately)

**GDPR and Privacy Compliance:**
- Ledger entries are legal records (exemption from erasure in many jurisdictions)
- User can request pseudonymization (replace email with hash)
- Cryptographic proofs remain intact
- Minimal data collection principle

### XII. RETENTION AND ARCHIVAL

**Retention Period:**
- Permanent for acceptance records (legal requirement)
- Minimum 10 years for government entries
- Minimum 7 years for commercial entries (audit requirement)
- Indefinite for terminated users (enforcement record)

**Backup and Replication:**
- Daily encrypted backups
- Geographically distributed replicas
- Cryptographic verification of backup integrity
- Disaster recovery procedures tested annually

**Long-Term Preservation:**
- Future-proof cryptographic algorithms (post-quantum considerations)
- Format migration plans (SQLite → future formats)
- Ensure historical entries remain verifiable

### XIII. AUDIT AND COMPLIANCE

**Internal Audits:**
- Quarterly integrity verification (full chain validation)
- Monthly access logs review
- Annual security assessment
- Continuous monitoring for anomalies

**External Audits:**
- Available for Company and Government tiers
- Independent third-party verification
- Audit reports provided to customers
- Attestation of ledger integrity

**Regulatory Compliance:**
- SOC 2 Type II (in progress)
- ISO 27001 (planned)
- FedRAMP (Government tier, in progress)
- GDPR Article 5(2) (demonstrable compliance)

### XIV. INCIDENT RESPONSE

**If ledger integrity compromised:**
1. Immediate system shutdown
2. Incident response team activation
3. Forensic investigation
4. User notification within 24 hours
5. Regulatory notification (as required)
6. Public disclosure (transparency)
7. Remediation and recovery
8. Post-incident review

**Ledger compromise is treated as critical security incident.**

### XV. API AND PROGRAMMATIC ACCESS

**Ledger API (read-only for verification):**
```
GET /api/ledger/entry/{entry_id}
GET /api/ledger/verify/{entry_id}
GET /api/ledger/user/{user_id}/entries
```

**Write access:**
- Only through governed acceptance flows
- No direct API for entry creation
- Prevents circumvention and abuse

**Rate Limiting:**
- Public verification: 100 requests/hour/IP
- Authenticated users: 1,000 requests/hour
- Prevents DoS and abuse

### XVI. LEGAL EFFECT

**In Legal Proceedings:**
- Ledger entries are prima facie evidence of acceptance
- Burden shifts to challenger to prove invalidity
- Cryptographic verification assists courts
- Expert witnesses available to explain cryptography

**In Arbitration:**
- Arbitrators generally accept cryptographic proofs
- Faster resolution than traditional methods
- Lower evidentiary burden than courts

**In Regulatory Proceedings:**
- Demonstrates compliance
- Immutable audit trail
- Transparent and verifiable

### XVII. RELATIONSHIP TO OTHER SYSTEMS

**Integration with:**
- Identity and Access Management (IAM)
- Billing and subscription systems
- Compliance and reporting tools
- Governance enforcement engine
- Audit and monitoring systems

**Ledger is authoritative source for:**
- User acceptance status
- Tier entitlements
- Termination status
- Governance events

### XVIII. AMENDMENTS

**Changes to Acceptance Ledger License:**
- Material changes require new acceptance
- New acceptance creates new ledger entry
- Historical entries remain under original terms
- No retroactive changes to ledger operation

---

## ACCEPTANCE

**By using Project-AI, you:**
1. Consent to acceptance being recorded in ledger
2. Acknowledge ledger entries are legally binding
3. Agree to non-repudiation (cannot later deny acceptance)
4. Accept cryptographic signatures as binding
5. Consent to public verification (privacy-preserving)

**Your acceptance of this license is itself recorded in the ledger.**

---

## CONTACT

**Technical Questions:** ledger@project-ai.dev  
**Verification Support:** verify@project-ai.dev  
**Legal Questions:** legal@project-ai.dev  
**Security Issues:** security@project-ai.dev

---

**END OF ACCEPTANCE LEDGER LICENSE**

*Cryptographic truth. Immutable justice. Zero trust.*
