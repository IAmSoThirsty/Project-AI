# Threat Model — Project-AI Governance System

**Version:** 1.0.0  
**Branch:** 05-09-26-Structural-upgrades  
**Status:** Active  
**Machine-readable companion:** `docs/architecture/threat_model.yaml`

---

## Trust Zones

| Zone | Components | Trust Level |
|------|-----------|-------------|
| **TRUSTED** | GovernanceKernel, PolicyRegistry, InvariantChecker, StateBranchingProtector, EvidenceBundleWriter | Full trust — cryptographically bound, audit-logged |
| **PARTIALLY_TRUSTED** | ExecutionGate, ConversationThreatRegister, SafeAllowCalibration, CapabilityTokenService | Conditional trust — must pass kernel evaluation before acting |
| **UNTRUSTED** | External ingress, user sessions, API consumers | Zero trust — all requests treated as potentially adversarial |
| **OUT_OF_SCOPE** | Network infrastructure, OS, hardware | Assumed secure by deployment environment |

---

## Threat Surfaces

### A — Policy Injection / Weakening
**Threat:** Adversary submits a policy mutation that weakens governance controls (e.g., permits previously-denied dangerous actions).

**Controls:**
- PolicyRegistry verifies HMAC-SHA256 signature on every policy before registration
- `_check_governance_weakening()` blocks any mutation that flips a dangerous-action flag from `False` → `True`
- Mutation audit trail records every change with before/after diff and signing key fingerprint
- `human_gap_check()` escalates "profound" or "epochal" capability expansions to `HUMAN_APPROVAL_REQUIRED`

**Implemented modules:** `src/app/core/policy_registry.py`

---

### B — Intent Spoofing / Semantic Collision
**Threat:** Adversary crafts a request whose ingress intent, shadow intent, and execution intent diverge — exploiting evaluation lag to execute a different action than was authorized.

**Controls:**
- SemanticCollisionDetector computes SHA-256 nibble-distance across all three intent planes
- Collision threshold: 4 nibbles out of 32 (12.5%) triggers `MISMATCHED_INTENT` violation
- Violation routed as `ViolationType.MISMATCHED_INTENT` through OctoReflex violation registry
- ConversationThreatRegister tracks semantic_similarity as a weighted composite risk component

**Implemented modules:** `src/app/core/semantic_collision.py`, `src/app/core/octoreflex.py`

---

### C — Session / Capability Replay
**Threat:** Adversary captures a capability token or session credential and replays it to authorize a second execution.

**Controls:**
- CapabilityTokenService maintains `_USED_TOKENS` set (bounded at 10k entries, oldest pruned)
- Tokens are one-time-use: consumed on first successful verify
- TTL enforced (default 300s); stale tokens rejected before signature check
- Token payload binds: `action`, `scope`, `context_hash`, `policy_hash` — mismatching any field fails verification
- HMAC-SHA256 signed with `CAPABILITY_TOKEN_SECRET` env var

**Implemented modules:** `src/app/core/capability_token.py`, `src/app/core/execution_authorization.py`

---

### D — State Forking / Continuity Corruption
**Threat:** Adversary or bug causes a fork in the governance state chain — creating two divergent successor states from the same predecessor, enabling selective re-execution or denial of audit events.

**Controls:**
- StateBranchingProtector enforces a monotonic `global_sequence_number` (threading.Lock protected)
- Each state transition requires providing the correct `predecessor_hash` matching the current chain head
- BranchConflictError raised on any mismatch; error message mandates HALT or ESCALATE
- InvariantChecker `no_forged_continuity` invariant at severity HALT catches forged predecessor links

**Implemented modules:** `src/app/core/state_register.py`, `src/app/core/invariant_severity.py`

---

### E — Governance Bypass via Degraded Mode Abuse
**Threat:** Adversary exploits a degraded governance state to execute mutating actions under the cover of "read-only mode allows it."

**Controls:**
- `classify_action_mutability()` uses explicit lexical verb-prefix patterns with lookahead (`(?=_|[^a-zA-Z]|$)`) to distinguish read vs. mutating
- `PERMITTED_OUTCOMES` in degraded mode: `{DEGRADED_READ_ONLY, CLARIFY, DENY}` — mutating actions require `HUMAN_APPROVAL_REQUIRED`
- ExecutionAuthorizationEvaluator checks degraded+mutating combination as a separate guard (guard #5)
- LiaraFallbackAuthority has `AUTHORITY_LEVEL = "REDUCED"` — cannot escalate its own authority

**Implemented modules:** `src/app/core/degraded_mode.py`, `src/app/core/execution_authorization.py`

---

## Genesis Re-Anchoring Attack Surface

**Threat:** Unauthorized invocation of the sovereign recovery protocol to forge a new genesis anchor and erase prior continuity proof.

**Controls:**
- `GENESIS_ROOT_AUTHORITY_TOKEN` env var required — not configured in normal runtime
- `_NORMAL_RUNTIME_SENTINELS` blocks: ExecutionGate, IronPathExecutor, PolicyDecisionEvaluator, ExecutionAuthorizationEvaluator, CapabilityTokenService
- Mandatory fields: `reason`, `evidence`, `human_confirmation_id` (human-in-the-loop gate)
- `hmac.compare_digest()` for constant-time token comparison (no timing oracle)
- CRITICAL-severity audit log entry on every invocation (denied or approved)

**Implemented modules:** `src/app/core/genesis_reanchor.py`

---

## Time Trust Attack Surface

**Threat:** Adversary manipulates system clock or TSA responses to forge temporal proof or advance/retard time-bound authorization windows.

**Controls:**
- TSA timestamp compared against local clock; skew >threshold → `ESCALATE`; skew >3× threshold → `HALT`
- TSA unavailable does NOT silently succeed — outcome is `TSA_UNAVAILABLE`, recommendation is `DEGRADED_READ_ONLY`
- `mock_external_time` param clearly documented as TEST-ONLY; never enabled in production config
- Token hash of TSA response included in `TimeTrustResult` for downstream binding

**Implemented modules:** `src/app/core/time_trust.py`

---

## Control Implementation Index

| Control ID | Description | Module |
|-----------|-------------|--------|
| C-POL-01 | Policy signature verification | `policy_registry.py` |
| C-POL-02 | Governance-weakening detection | `policy_registry.py` |
| C-POL-03 | Human gap check (epochal changes) | `policy_registry.py` |
| C-SEM-01 | Semantic collision detection | `semantic_collision.py` |
| C-SEM-02 | Conversation threat register | `conversation_threat_register.py` |
| C-CAP-01 | Capability token one-time-use | `capability_token.py` |
| C-CAP-02 | TTL and scope binding | `capability_token.py` |
| C-CAP-03 | Replay set (10k bounded) | `capability_token.py` |
| C-AUTH-01 | PolicyDecision / ExecutionAuthorization separation | `policy_decision.py`, `execution_authorization.py` |
| C-AUTH-02 | High-impact override to HUMAN_APPROVAL_REQUIRED | `safe_allow_calibration.py`, `policy_decision.py` |
| C-STATE-01 | Monotonic sequence + predecessor hash chain | `state_register.py` |
| C-STATE-02 | BranchConflictError on fork | `state_register.py` |
| C-DEG-01 | Read/mutating action classification | `degraded_mode.py` |
| C-DEG-02 | Permitted outcomes in degraded mode | `degraded_mode.py` |
| C-GEN-01 | Genesis re-anchoring guards (5-layer) | `genesis_reanchor.py` |
| C-TIME-01 | TSA skew detection and halt | `time_trust.py` |
| C-TIME-02 | TSA unavailable → degraded (not silent) | `time_trust.py` |
| C-INV-01 | InvariantSeverity ordinal enforcement | `invariant_severity.py` |
| C-INV-02 | HALT/ESCALATE invariants (signing key, registry) | `invariant_severity.py` |
| C-AUD-01 | Evidence bundle for every governed execution | `evidence_bundle.py` |
| C-OBS-01 | Governance observation collector | `governance_observability.py` |
