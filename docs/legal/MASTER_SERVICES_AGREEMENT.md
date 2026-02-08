# Project-AI Master Services Agreement (MSA)

**Version:** 1.0.0  
**Effective Date:** February 8, 2026  
**Document Hash:** (Computed at runtime)  
**Legal Supremacy:** This document supersedes all prior agreements

---

## 1. DEFINITIONS

**1.1 Service Provider:** Project-AI development team and associated entities.

**1.2 User:** Any individual, organization, or entity accessing or utilizing Project-AI software, services, or documentation.

**1.3 Platform:** The Project-AI software system, including desktop application, API, web interfaces, and all associated components.

**1.4 Tier:** Service level designation (Solo, Team, Enterprise, Government) determining feature access and obligations.

**1.5 Acceptance Ledger:** Cryptographically-secured, immutable log of all user agreements and acceptances.

**1.6 Jurisdictional Annex:** Territory-specific legal requirements incorporated by reference.

---

## 2. SCOPE OF SERVICES

**2.1 Platform Access:** Service Provider grants User limited, non-exclusive, non-transferable access to the Platform subject to tier limitations and acceptance of all terms.

**2.2 Tier-Based Services:**

- **Solo Tier:** Single-user access with software-backed cryptographic signing
- **Team Tier:** Multi-user coordination with enhanced cryptographic verification
- **Enterprise Tier:** Advanced features with hardware-backed signing (TPM/HSM optional)
- **Government Tier:** Maximum security with mandatory hardware-backed signing and timestamp authority notarization

**2.3 Services Included:**
- AI-powered intelligent assistance
- Ethical decision-making system (Asimov's Laws framework)
- Autonomous learning capabilities
- Memory expansion and knowledge management
- Plugin system and extensibility
- Command override system with audit logging
- Security and privacy protections

---

## 3. USER OBLIGATIONS

**3.1 Acceptance Requirement:** User must cryptographically accept this MSA and all applicable Jurisdictional Annexes before Platform access.

**3.2 Prohibited Uses:**
- Any use violating applicable law or regulation
- Attempts to bypass or disable governance, security, or audit systems
- Malicious use, including creation or distribution of malware
- Unauthorized reverse engineering (except where legally permitted)
- Use that endangers human safety or violates ethical principles
- Commercial use beyond licensed tier limitations

**3.3 Compliance:** User agrees to comply with all applicable laws, regulations, and jurisdictional requirements.

**3.4 Data Accuracy:** User is responsible for accuracy of information provided during registration and acceptance.

---

## 4. SERVICE PROVIDER OBLIGATIONS

**4.1 Service Availability:** Service Provider will make commercially reasonable efforts to maintain Platform availability and performance.

**4.2 Security:** Service Provider implements cryptographic security, hardware-backed signing (for applicable tiers), and immutable audit logging.

**4.3 Privacy:** Service Provider adheres to applicable privacy laws and regulations as specified in Jurisdictional Annexes.

**4.4 Transparency:** Acceptance Ledger provides public cryptographic verification of all agreements.

---

## 5. INTELLECTUAL PROPERTY

**5.1 Ownership:** All intellectual property rights in the Platform remain with Service Provider.

**5.2 License Grant:** Subject to compliance with this MSA, Service Provider grants User a limited license to use the Platform.

**5.3 User Content:** User retains ownership of data and content created using the Platform. Service Provider may process such content to provide services.

---

## 6. LIMITATION OF LIABILITY

**6.1 Disclaimer:** PLATFORM PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED.

**6.2 Liability Cap:** TO THE MAXIMUM EXTENT PERMITTED BY LAW, SERVICE PROVIDER'S TOTAL LIABILITY SHALL NOT EXCEED FEES PAID BY USER IN THE 12 MONTHS PRECEDING THE CLAIM.

**6.3 Exclusions:** SERVICE PROVIDER NOT LIABLE FOR INDIRECT, INCIDENTAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES.

---

## 7. TERM AND TERMINATION

**7.1 Term:** This Agreement remains in effect until terminated.

**7.2 Termination by User:** User may terminate by ceasing Platform use and deleting all copies.

**7.3 Termination by Provider:** Service Provider may terminate immediately for breach, with permanent record in Acceptance Ledger.

**7.4 Effect of Termination:** All licenses granted herein immediately cease. Audit logs and acceptance records are permanently retained.

**7.5 Survival:** Sections 5, 6, 8, and 9 survive termination.

---

## 8. GOVERNANCE AND ENFORCEMENT

**8.1 Acceptance Ledger:** All acceptances recorded in cryptographically-secured, tamper-proof ledger with:
- SHA-256 hash chaining
- Ed25519 digital signatures
- Optional hardware-backed signing (TPM/HSM)
- Optional timestamp authority notarization (RFC 3161, OpenTimestamps, eIDAS)

**8.2 Immutability:** Acceptance records are append-only and cannot be modified or deleted.

**8.3 Verification:** Public verification endpoint provides zero-trust cryptographic validation.

**8.4 Enforcement:** Platform enforces compliance at boot-time, runtime, and through continuous monitoring.

**8.5 Audit Lock:** Upon termination or breach, audit systems enter locked state preventing further modifications.

---

## 9. JURISDICTIONAL COMPLIANCE

**9.1 Incorporation by Reference:** All applicable Jurisdictional Annexes are incorporated into this Agreement.

**9.2 Jurisdiction Selection:** User selects primary jurisdiction during acceptance process.

**9.3 Multi-Jurisdictional Operations:** Users operating across jurisdictions must comply with all applicable annexes.

**9.4 Regulatory Updates:** Service Provider may update annexes to maintain compliance. Users notified and must re-accept.

---

## 10. DISPUTE RESOLUTION

**10.1 Negotiation:** Parties agree to first attempt good-faith negotiation.

**10.2 Arbitration:** Unresolved disputes subject to binding arbitration under rules of American Arbitration Association.

**10.3 Governing Law:** This Agreement governed by laws of jurisdiction selected by User, without regard to conflicts of law principles.

**10.4 Acceptance Ledger as Evidence:** Cryptographically-verified acceptance records admissible in any proceeding.

---

## 11. GENERAL PROVISIONS

**11.1 Entire Agreement:** This MSA, including incorporated Jurisdictional Annexes, constitutes entire agreement.

**11.2 Amendments:** Service Provider may amend this Agreement. Material changes require re-acceptance.

**11.3 Severability:** Invalid provisions severed; remaining provisions remain in effect.

**11.4 No Waiver:** Failure to enforce any provision does not constitute waiver.

**11.5 Assignment:** User may not assign rights without written consent. Service Provider may assign without restriction.

---

## 12. CRYPTOGRAPHIC INTEGRITY

**12.1 Document Hash:** This document's canonical hash computed using SHA-256 over normalized JSON representation.

**12.2 Signature Verification:** User acceptance signed with Ed25519 (software) or hardware-backed key (TPM/HSM).

**12.3 Timestamp Authority:** Optional notarization via RFC 3161 timestamp servers, OpenTimestamps, or eIDAS-compliant services.

**12.4 Chain of Trust:** Each acceptance links to previous acceptance via cryptographic hash chain.

---

## ACCEPTANCE

By cryptographically signing this Agreement, User acknowledges:
1. Reading and understanding all terms
2. Agreeing to be legally bound
3. Accepting all applicable Jurisdictional Annexes
4. Consenting to immutable recording in Acceptance Ledger
5. Understanding that acceptance is irrevocable and permanent

**For questions or concerns, contact:** legal@project-ai.dev

---

**END OF MASTER SERVICES AGREEMENT**

*Document integrity protected by cryptographic hashing and digital signatures.*
