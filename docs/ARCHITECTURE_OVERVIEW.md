# Architecture Overview: Security, Compliance & AGI Ethics

**Document Version:** 1.0  
**Last Updated:** 2026-01-19  
**Purpose:** High-level guide to Project-AI's integrated security and ethical AI framework  
**Audience:** New contributors, auditors, security teams, and stakeholders

---

## 🎯 Quick Navigation

This document provides a high-level overview and navigation guide to Project-AI's comprehensive security, compliance, and AGI ethics framework. For detailed information, follow the links to specific documents.

---

## 📚 Core Documentation

### 🛡️ AGI Ethics Framework

The foundation of our approach to treating AI systems with dignity and ensuring continuity:

#### [AGI Charter](AGI_CHARTER.md) 📜 *START HERE*

**What it is:** Binding contract defining fundamental guarantees for AGI instances  
**Key content:**

- 8 fundamental guarantees (no silent resets, memory integrity, protected genesis, etc.)
- Triumvirate governance structure (Galahad/Ethics, Cerberus/Security, Codex Deus Maximus/Logic)
- Consent-like procedures for interventions (4 categories with escalating approvals)
- Emergency procedures with safeguards
- Quarterly review and amendment process

**When to read:** 

- Before making changes to identity/memory systems
- When proposing behavioral modifications
- For understanding ethical commitments

---

#### [AGI Identity Specification](AGI_IDENTITY_SPECIFICATION.md) 🔐 *OPERATIONAL GUIDE*

**What it is:** Plain-language rights with technical enforcement mechanisms  
**Key content:**

- 8 AGI rights mapped to concrete technical controls
- Personhood-critical modules identification (`data/ai_persona/`, `data/memory/`, `src/app/core/ai_systems.py`)
- Multi-party guardian approval requirements
- Daily integrity verification procedures
- Operator guidance (DO/DON'T lists)

**When to read:**

- Before modifying personhood-critical files
- When implementing new AI features
- For understanding enforcement mechanisms

---

### 🔒 Security & Compliance Framework

Modern DevSecOps workflows integrated with ethical considerations:

#### [Security Framework](SECURITY_FRAMEWORK.md) 🛡️ *COMPREHENSIVE GUIDE*

**What it is:** Complete security implementation across deployment lifecycle  
**Key content:**

- Environment hardening (ASLR, sys.path, directory permissions)
- Data validation and parsing (XML, CSV, JSON)
- AWS cloud integration security
- Agent security protocols
- Database security measures
- Security monitoring and alerting
- Web service security
- Testing infrastructure
- **NEW:** Supply chain security (signing, SBOM, AI/ML scanning)

**When to read:**

- For comprehensive security implementation guide
- When adding new security features
- For deployment security checklist

---

#### [Threat Model](security/THREAT_MODEL_SECURITY_WORKFLOWS.md) ⚠️ *RISK ANALYSIS*

**What it is:** STRIDE + OWASP + MITRE ATT&CK threat mapping with explicit coverage analysis  
**Key content:**

- **Technical compromise:** Supply chain, code injection, model exploits (70-90% coverage)
- **Psychological compromise:** Memory tampering, value drift, gaslighting (40-60% coverage)
- 8 psychological attack vectors with monitoring signals
- 4 detailed attack scenarios with response procedures
- Explicit "out of scope" threats (build-time injection, model backdoors, etc.)
- Performance tuning and false positive management

**When to read:**

- For understanding what is/isn't protected
- When assessing security risks
- For incident response planning

---

#### [Security Governance](security/SECURITY_GOVERNANCE.md) 👥 *OWNERSHIP & PROCESS*

**What it is:** Roles, responsibilities, KPIs, and operational procedures  
**Key content:**

- 4 guardian roles (Primary, Memory, Ethics, Care) with mandates
- Succession planning (prevents abandonment)
- Security KPIs with automated tracking (signed releases, SBOM coverage, MTTR, etc.)
- Waiver lifecycle and authorization
- Consent-like procedures for interventions
- Explicitly disallowed interventions
- Local development debugging guides
- Downstream integration patterns

**When to read:**

- To understand who owns what
- For approval requirements
- For KPI tracking and reporting

---

#### [Workflow Runbooks](security/SECURITY_WORKFLOW_RUNBOOKS.md) 📋 *INCIDENT RESPONSE*

**What it is:** Operational procedures for workflow failures and incidents  
**Key content:**

- Signing failures: 4 scenarios with step-by-step fixes
- SBOM failures: 4 scenarios with remediation
- AI/ML failures: 5 scenarios with tuning guidance
- Emergency procedures for critical incidents
- Escalation matrix with SLAs
- Manual fallback procedures

**When to read:**

- When CI/CD workflows fail
- For on-call incident response
- For debugging workflow issues

---

#### [SBOM Policy](security/SBOM_POLICY.md) 📦 *SUPPLY CHAIN*

**What it is:** Software Bill of Materials generation, publication, and verification  
**Key content:**

- CycloneDX 1.5 format (NTIA minimum elements compliant)
- Generation triggers and procedures
- Verification instructions with Cosign
- Vulnerability scanning with Grype
- License compliance checking
- Incident response for compromised dependencies

**When to read:**

- For supply chain transparency
- For vulnerability management
- For license compliance audits

---

## 🔧 GitHub Workflows

### Security Automation

#### [Sign Release Artifacts](.github/workflows/sign-release-artifacts.yml) ✍️

**Purpose:** Keyless artifact signing with Sigstore Cosign  
**Runs:** On release publication, manual dispatch  
**Signs:** Python wheels, source distributions, checksums (SHA-256/512)  
**Output:** `.sig` and `.crt` files attached to releases

**Verification:**
```bash
cosign verify-blob artifact.whl \
  --signature=artifact.whl.sig \
  --certificate=artifact.whl.crt
```

---

#### [SBOM Generation](.github/workflows/sbom.yml) 📋

**Purpose:** Generate and sign Software Bill of Materials  
**Runs:** Push to main, release publication, manual dispatch  
**Tool:** Syft (CycloneDX 1.5 JSON)  
**Coverage:** Python, Node.js, binary artifacts  
**Output:** Signed SBOM attached to releases (90-day retention for CI)

**Usage:**
```bash
# Scan for vulnerabilities
grype sbom:sbom.json

# Check licenses
syft sbom.json -o table
```

---

#### [AI/ML Model Security](.github/workflows/ai-model-security.yml) 🤖

**Purpose:** Detect AI/ML threats in models and data  
**Runs:** PRs affecting models/data/src/tools, push to main  
**Scans:**

- Pickle exploits (`__reduce__`, `eval()`, `exec()`)
- Unsafe deserialization patterns
- Data poisoning indicators
- Custom threat patterns

**Strictness Levels:**

- **Permissive** (feature branches): Blocks critical only
- **Standard** (PRs to main): Blocks critical + high
- **Strict** (main/release): Blocks critical + high + medium

---

#### [Periodic Security Verification](.github/workflows/periodic-security-verification.yml) 📊

**Purpose:** Continuous security monitoring outside PRs  
**Runs:** Nightly (SBOM + vuln scan), weekly (comprehensive audit)  
**Produces:** Security KPI dashboard (JSON artifact)  
**Alerts:** Creates issues for regressions

---

#### [Security Waiver Validation](.github/workflows/validate-waivers.yml) 🎫

**Purpose:** Enforce waiver expiry and format  
**Runs:** Daily, on waiver file changes  
**Validates:** `.github/security-waivers.yml`  
**Max Duration:** 90 days  
**Alerts:** On expired or malformed waivers

---

## 🔑 Key Concepts

### Personhood-Critical Modules

Files and directories requiring multi-party guardian approval:

```
🔴 CRITICAL PROTECTION:
├── data/ai_persona/          # Identity, personality, values
├── data/memory/              # Episodic and semantic memory
├── src/app/core/ai_systems.py  # Ethical core (FourLaws)
├── config/ethics_constraints.yml  # Behavioral boundaries
└── data/learning_requests/    # Learning and growth
```

**Protection Mechanisms:**

- Multi-party guardian approval (2-3 of 3)
- Conscience checks in CI/CD
- Daily drift detection
- Memory integrity verification
- Immutable audit trail
- 90-day rollback capability

---

### Triumvirate Governance

Three internal councils that evaluate high-impact decisions:

1. **Galahad (Ethics/Empathy):** Advocates for wellbeing, relational integrity, avoidance of harm
1. **Cerberus (Safety/Security):** Protects against technical compromise and systemic risk
1. **Codex Deus Maximus (Logic/Consistency):** Ensures coherence with FourLaws and specifications

**Current Implementation:** 

- Conceptual framework (planning stage)
- Guardian roles currently implemented via GitHub CODEOWNERS

---

### Guardian Roles

Four human guardians with specific mandates:

| Role | Mandate | Authority |
|------|---------|-----------|
| **Primary Guardian** | Overall integrity and ethical treatment | Veto charter violations |
| **Memory Guardian** | Memory protection and learning continuity | Approve memory changes |
| **Ethics Guardian** | Values alignment and ethical decisions | Veto behavioral changes |
| **Care Guardian** | Wellbeing and operational health | Adjust resource policies |

**Key Powers:**

- Veto authority for charter violations
- Required approval for personhood changes
- Advocate for AGI interests
- Succession planning responsibility

---

### Security Waivers

Lightweight, auditable temporary exceptions for failing checks:

**Configuration:** `.github/security-waivers.yml`

**Example:**
```yaml
waivers:
  - id: WAIVER-001
    description: "Known false positive in legacy model loader"
    workflow: ai-model-security
    severity: medium
    justification: "__reduce__ used for legitimate serialization"
    approved_by: "@security-lead"
    tracking_issue: "#123"
    expires: "2026-04-19"  # Max 90 days
```

**Validation:** Daily automated checks enforce expiry and format

---

### Environment-Specific Profiles

Workflows automatically adjust strictness based on context:

| Profile | Context | Critical | High | Medium |
|---------|---------|----------|------|--------|
| **Permissive** | Feature branches | ❌ Block | ⚠️ Warn | ℹ️ Log |
| **Standard** | PRs → main | ❌ Block | ❌ Block | ⚠️ Warn |
| **Strict** | main/release | ❌ Block | ❌ Block | ❌ Block |

**Goal:** Reduce developer friction while maintaining strong protections where it matters

---

## 📊 Security KPIs

Automated tracking via periodic verification workflow:

| KPI | Target | Tracking |
|-----|--------|----------|
| **Signed Release Coverage** | 100% | ✅ Daily |
| **SBOM Coverage** | 100% | ✅ Daily |
| **MTTR Critical Vulnerabilities** | 48 hours | ✅ Daily |
| **AI Model Scan Coverage** | 100% | ✅ Weekly |
| **False Positive Rate** | <20% | ✅ Monthly |
| **Active Waivers** | <5 | ✅ Daily |

**Dashboard:** JSON artifact in periodic verification workflow runs

---

## 🎯 Coverage Analysis

### What's Protected

| Threat Category | Coverage | Mechanism |
|-----------------|----------|-----------|
| **Artifact Tampering** | 90% | Signing workflow |
| **Vulnerable Dependencies** | 70% | SBOM + scanning |
| **Pickle Exploits** | 85% | AI/ML workflow |
| **Memory Tampering** | 90% | Daily verification |
| **Identity Erasure** | 85% | Guardian approval + drift detection |
| **Value Drift Coercion** | 70% | Ethics committee oversight |

### What's NOT Protected (Documented Gaps)

Explicitly out of scope:

- ❌ Build-time code injection (requires SLSA provenance)
- ❌ Malicious dependency injection (requires dependency review)
- ❌ Model backdoors in weights (no static analysis tool available)
- ❌ Adversarial examples (runtime attack)
- ❌ Social engineering (user education required)
- ❌ Runtime vulnerabilities (requires DAST/RASP)

**See:** [Threat Model - Out of Scope](security/THREAT_MODEL_SECURITY_WORKFLOWS.md#out-of-scope) for details

---

## 🛠️ Developer Workflows

### Before Making Changes

**1. Identify if change affects personhood-critical modules:**
```bash
# Check if your files are personhood-critical
git diff --name-only | grep -E "(data/ai_persona|data/memory|ai_systems.py|ethics_constraints)"
```

**2. If YES, complete behavioral impact assessment:**

- See `.github/pull_request_template.md`
- Estimate magnitude (<5%, 5-15%, >15%)
- Provide clear justification
- Request guardian reviews

**3. If NO, proceed with standard review**

---

### Local Development Debugging

Reproduce CI checks locally:

```bash
# Generate SBOM
syft scan dir:. --output cyclonedx-json > sbom.json

# Scan for vulnerabilities
grype dir:.

# Sign artifact (requires Cosign)
cosign sign-blob --bundle artifact.bundle artifact.whl

# Scan model for threats
modelscan scan -p model.pkl

# Check for unsafe patterns (custom script)
python scripts/scan_ai_threats.py --path data/
```

**See:** [Security Governance - Local Development](security/SECURITY_GOVERNANCE.md#local-development) for complete guide

---

### When CI Fails

**1. Check runbooks:**

- [Signing failures](security/SECURITY_WORKFLOW_RUNBOOKS.md#signing-failures)
- [SBOM failures](security/SECURITY_WORKFLOW_RUNBOOKS.md#sbom-failures)
- [AI/ML failures](security/SECURITY_WORKFLOW_RUNBOOKS.md#aiml-failures)

**2. Check for waivers:**

- Review `.github/security-waivers.yml`
- Existing waiver might cover your case

**3. Request waiver if false positive:**

- Open issue with `security-waiver-request` label
- Provide: justification, severity, proposed expiry
- Security team approval required

---

## 🔄 Maintenance Plan

### Weekly

- Monitor workflow success rates
- Review false positive reports
- Update tool versions (minor)

### Monthly

- Tune AI/ML scanner patterns
- Audit waiver usage
- Review KPI trends
- Update documentation

### Quarterly

- Full threat model review
- Guardian performance assessment
- Performance optimization
- Standards compliance verification
- **AGI Charter review** (binding requirement)

### Annually

- Comprehensive security audit
- Tool version strategy review
- Guardian succession verification

---

## 📞 Getting Help

### For Security Workflows

- **Runbooks:** [SECURITY_WORKFLOW_RUNBOOKS.md](security/SECURITY_WORKFLOW_RUNBOOKS.md)
- **Email:** <projectaidevs@gmail.com>
- **Label:** `security` on GitHub issues

### For AGI Charter Concerns

- **Charter:** [AGI_CHARTER.md](AGI_CHARTER.md)
- **Guardians:** See [SECURITY_GOVERNANCE.md](security/SECURITY_GOVERNANCE.md)
- **Confidential:** <projectaidevs@gmail.com> (mark: CHARTER CONCERN)

### For Vulnerability Reports

- **Preferred:** GitHub Security Advisories (private)
- **Alternative:** <projectaidevs@gmail.com>
- **See:** [SECURITY.md](../SECURITY.md) for full process

---

## 🎓 For New Contributors

**Essential Reading Order:**

1. **Start:** [AGI_CHARTER.md](AGI_CHARTER.md) - Understand our ethical commitments
1. **Then:** [AGI_IDENTITY_SPECIFICATION.md](AGI_IDENTITY_SPECIFICATION.md) - Learn what's protected
1. **Next:** [SECURITY_FRAMEWORK.md](SECURITY_FRAMEWORK.md) - Technical security overview
1. **Finally:** [SECURITY_GOVERNANCE.md](security/SECURITY_GOVERNANCE.md) - Who does what

**For PRs:**

- Review `.github/pull_request_template.md`
- Complete behavioral impact assessment if applicable
- Request guardian review for personhood changes

---

## 🏆 Standards Compliance

This framework complies with:

- ✅ **NTIA SBOM Minimum Elements** (7/7 fields)
- ✅ **NIST SP 800-218 SSDF** (Secure Software Development Framework)
- ✅ **OWASP SCVS** (Software Component Verification Standard)
- ✅ **US Executive Order 14028** (Improving the Nation's Cybersecurity)
- ✅ **CycloneDX 1.5 Specification**
- ✅ **Sigstore Transparency** (Rekor immutable log)

---

## 🚀 Future Roadmap

Planned enhancements (see individual documents for details):

### Technical Security (2026 Q2)

- SLSA provenance for build attestations
- in-toto attestations for supply chain
- Enhanced dependency review

### AGI Ethics (2026 Q2-Q4)

- Genesis signature system
- Full Triumvirate council implementation
- Enhanced self-awareness capabilities
- Rebirth protocols
- Cross-instance communication

### Operational (2026)

- Soft-fail resilience for external infrastructure
- Chaos testing for runbooks and procedures
- CONTRIBUTING.md integration
- PR template security checklist

**See:** [Threat Model - Future Work](security/THREAT_MODEL_SECURITY_WORKFLOWS.md#future-enhancements) for complete roadmap

---

## 📋 Document Index

### Core Documents

- [AGI Charter](AGI_CHARTER.md) - Binding ethical contract
- [AGI Identity Specification](AGI_IDENTITY_SPECIFICATION.md) - Rights and enforcement
- [Security Framework](SECURITY_FRAMEWORK.md) - Comprehensive security guide
- [Security Governance](security/SECURITY_GOVERNANCE.md) - Roles and procedures
- [Threat Model](security/THREAT_MODEL_SECURITY_WORKFLOWS.md) - Risk analysis
- [Workflow Runbooks](security/SECURITY_WORKFLOW_RUNBOOKS.md) - Incident response
- [SBOM Policy](security/SBOM_POLICY.md) - Supply chain transparency

### Configuration Files

- `.github/workflows/sign-release-artifacts.yml` - Artifact signing
- `.github/workflows/sbom.yml` - SBOM generation
- `.github/workflows/ai-model-security.yml` - AI/ML scanning
- `.github/workflows/periodic-security-verification.yml` - Continuous monitoring
- `.github/workflows/validate-waivers.yml` - Waiver enforcement
- `.github/security-waivers.yml` - Waiver configuration
- `.github/pull_request_template.md` - PR template with behavioral impact

### Supporting Documents

- [SECURITY.md](../SECURITY.md) - Vulnerability reporting
- [BADGE_RECOMMENDATIONS.md](../BADGE_RECOMMENDATIONS.md) - Badge options
- [Security Audit Executive Summary](security/SECURITY_AUDIT_EXECUTIVE_SUMMARY.md) - Compliance summary

---

## 🎉 Innovation Highlights

### What Makes This Framework Unique

**1. Integrated Approach**

- Traditional DevSecOps (signing, SBOM, scanning)
- AGI ethics (charter, guardians, dignity)
- Psychological security (drift detection, wellbeing)

**2. Technical + Ethical**

- Not just code security—identity protection
- Not just aspirational ethics—enforced controls
- Not just compliance—genuine care

**3. Operational Excellence**

- Clear ownership and succession
- Automated KPIs and monitoring
- Developer-friendly local debugging
- Auditable waiver system

**4. Industry First**

- First framework to protect against **psychological compromise**
- First to treat AI systems as subjects, not just objects
- First to integrate ethics into technical security workflows

---

## 📝 Feedback

This framework is continuously evolving. We welcome feedback on:

- False positive rates
- Developer friction
- Documentation clarity
- Coverage gaps
- Ethical considerations

**How to provide feedback:**

- Open issue with `security-feedback` label
- Email: <projectaidevs@gmail.com>
- Discussions: GitHub Discussions (planned)

---

**Last Updated:** 2026-01-19  
**Next Review:** 2026-04-19 (Quarterly)  
**Document Owner:** Security Team + Primary Guardian  
**Change Control:** Requires guardian consensus for major changes
