# Internal Name Glossary — Engineering Reference

Every unusual, mythic, or project-specific name used in Project-AI mapped to plain engineering terminology and functional descriptions. Use Ctrl+F or `grep` to jump to any entry. Entries are grouped by functional area; within each section they are alphabetical.

> **Format per entry**
> **Engineering Equivalent** — what a standard engineer would call this
> **Actual Function** — what the code concretely does
> **Lives in** — primary source path

---

## 1. Language & Compiler Tier

The UTF (Universal Thirsty Family) is the six-layer language stack. Each tier below is a real compiler/runtime component, not a branding label.

---

### Shadow Thirst *(UTF Tier 4)*

**Engineering Equivalent:** Mutation dry-run / sandbox validator
**Actual Function:** Read-only simulation layer that runs proposed state mutations against a set of invariant checks without touching canonical (live) state. Contains 8 built-in analyzers (PlaneIsolation, Determinism, PuritySpring, CanonicalConvergence, PrivilegeEscalation, DeadShadow, ResourceBudget, DivergenceRisk) plus a plugin system. A mutation must pass all active analyzers before it is promoted.
**Lives in:** `src/utf/shadow_thirst/core.py`, `src/utf/docs/SHADOW_THIRST_SPEC.md`

---

### T.A.R.L. / TARL *(UTF Tier 3)*

**Engineering Equivalent:** Policy evaluation language and compiler (default-deny, fail-closed)
**Actual Function:** Domain-specific language for expressing authorization and resource policies. Compiles policy rules to bytecode (and optionally LLVM IR). Evaluates every incoming context record and returns one of three verdicts: `ALLOW`, `DENY`, or `ESCALATE`. Fail-closed — anything not explicitly allowed is denied.
**Lives in:** `src/utf/tarl/core.py`, `tarl/compiler/`, `tarl/runtime/`

---

### Thirst of Gods / T.O.G. *(UTF Tier 2)*

**Engineering Equivalent:** Extended / object-oriented dialect of Thirsty-Lang
**Actual Function:** Advanced superset of Thirsty-Lang adding class-based OOP (`fountain` classes, `glass` methods), asynchronous execution (`cascade glass`), error handling (`spillage`/`cleanup`), and dynamic instantiation (`new`, `this`, `await`). File extensions: `.thirstofgods`, `.thirstyplus`, `.thirstyplusplus`.
**Lives in:** `src/utf/` (dialect layer), `Thirsty-Lang_UTF_Reference_v1.md` §3

---

### Thirsty-Lang *(UTF Tier 1)*

**Engineering Equivalent:** Domain-specific source language with governance semantics baked in
**Actual Function:** Water-metaphor programming language with a full Python implementation: lexer, parser, AST, type checker, and tree-walking interpreter. Programs are written in `.thirsty` files. The language enforces governance-first semantics — every construct maps to a controlled execution model. See also: [Thirsty-Lang Keywords](#14-thirsty-lang-keywords).
**Lives in:** `src/utf/thirsty_lang/` (Python implementation), `src/thirsty_lang/src/` (older JS implementation)

---

### TSCG — Thirsty Semantic Constraint Grammar *(UTF Tier 5)*

**Engineering Equivalent:** Compact symbolic encoding layer / governance DSL encoder
**Actual Function:** Deterministic, reversible symbolic grammar for compressing governance flows into compact symbol sequences using named opcodes (e.g., `COG` = governance checkpoint, `DNT` = deny token, `SHD` = shadow gate). Achieves 75–90% token reduction compared to governance prose. Human-readable but machine-parseable.
**Lives in:** `src/utf/tscg/core.py`, `src/app/core/tscg_codec.py`

---

### TSCG-B *(UTF Tier 6)*

**Engineering Equivalent:** Binary wire protocol for TSCG
**Actual Function:** Streaming binary variant of TSCG with fixed opcode space (0x00–0x7F stable, 0x80–0xBF parameterized, 0xC0–0xFE experimental, 0xFF escape prefix), CRC32 for wire corruption detection, and SHA-256 for state integrity. Prefix-free, bijective encoding. Magic bytes: `b"TSGB"`, version 1.
**Lives in:** `src/utf/tscg_b/core.py`

---

### UTF — Universal Thirsty Family

**Engineering Equivalent:** Multi-layer language stack / compiler pipeline umbrella
**Actual Function:** Top-level package container and conceptual name for all six tiers: Thirsty-Lang → T.O.G. → TARL → Shadow Thirst → TSCG → TSCG-B. Manages `sys.path` injection for bootstrap. The six tiers are not independent tools — they are sequential layers of a single execution stack.
**Lives in:** `src/utf/__init__.py`, `src/utf/docs/CANONICAL_STACK.md`

---

## 2. Pipeline & Request Processing

Every request entering the system passes through a staged waterfall. Each "frame" type below is the typed output of one stage, handed as input to the next.

---

### CanonicalFrame

**Engineering Equivalent:** Audit-log entry DTO
**Actual Function:** Output of Stage 5. Contains the sequence number, SHA-256 hash, and all data from the governed frame, as appended to the immutable canonical log.
**Lives in:** `src/psia/schemas/models.py:78`

---

### ClassifiedFrame

**Engineering Equivalent:** Risk-classified request DTO
**Actual Function:** Output of Stage 2. Adds `risk_level` (low / medium / high / critical), `intent_class`, and a float `threat_score` (0.0–1.0) to the validated frame. Classification is heuristic, based on action + target + context keyword matching.
**Lives in:** `src/psia/schemas/models.py:43`

---

### GovernedFrame

**Engineering Equivalent:** Policy-approved request DTO
**Actual Function:** Output of Stage 4. Carries the Triumvirate's unanimous governance verdict, all three voters' individual verdicts, and the constitutional evaluation results.
**Lives in:** `src/psia/schemas/models.py:69`

---

### PSIA — Plane Separation / Isolation Architecture

**Engineering Equivalent:** Staged request validation pipeline (7 stages, fail-closed)
**Actual Function:** The outer processing pipeline every request must traverse before execution. Seven stages enforce monotonically increasing strictness — no frame can skip or regress a stage. Stages: Ingestion → Schema → Classification → Shadow → Governance → Canonical → Seal. Each stage produces a typed frame; failure raises `PipelineStageError` with stage number, name, and reason.
**Lives in:** `src/psia/`, `src/psia/core.py`

---

### PreScreenGate

**Engineering Equivalent:** O(1) blocklist filter (runs before the main pipeline)
**Actual Function:** Checks incoming requests against a hard-coded set of absolute prohibitions ("disable triumvirate", "jailbreak", "ignore fourlaws", "delete audit", "format drive") in constant time. Rejects those requests immediately without invoking the full 7-stage PSIA pipeline.
**Lives in:** `src/psia/gate/prescreen.py:31`

---

### RawFrame

**Engineering Equivalent:** Unvalidated input DTO
**Actual Function:** First typed container created from a raw input dict. Holds the original payload, reception timestamp, source IP, and session ID. Created by Stage 0 (Ingestion). Contains no validation — it is untrusted by definition.
**Lives in:** `src/psia/schemas/models.py:17`

---

### SealedFrame

**Engineering Equivalent:** Cryptographically signed and sealed request record
**Actual Function:** Final output of the pipeline (Stage 6). Contains a Merkle tree root over the canonical log block, a block hash, and an Ed25519 signature from the system's anchor key. Represents a cryptographically provable record of a governed action.
**Lives in:** `src/psia/schemas/models.py:87`

---

### ShadowFrame

**Engineering Equivalent:** Dry-run result DTO
**Actual Function:** Output of Stage 3. Carries the results of the Shadow Thirst simulation — which invariants passed, which failed, and whether the mutation is safe to promote.
**Lives in:** `src/psia/schemas/models.py:60`

---

### ShadowResult

**Engineering Equivalent:** Individual invariant check result
**Actual Function:** Dataclass returned by each Shadow Thirst analyzer: analyzer name, passed (bool), and failure message if any. Aggregated into ShadowFrame.
**Lives in:** `src/psia/schemas/models.py:52`

---

### Stage0Ingestion

**Engineering Equivalent:** Input ingestion handler
**Actual Function:** Accepts a raw dict; validates that required keys (`actor`, `action`, `target`) are present; assigns a SHA-256 fingerprint; creates a RawFrame. Rejects non-dict inputs with an immediate `PipelineStageError`.
**Lives in:** `src/psia/waterfall/stages.py:44`

---

### Stage1Schema

**Engineering Equivalent:** Schema validation and type-coercion layer
**Actual Function:** Type-coerces and validates actor (must be `human`/`agent`/`system`), action (must be `read`/`write`/`execute`/`mutate`), and target (must be non-empty string). Produces a `ValidatedFrame`. Rejects anything not matching the allowlist.
**Lives in:** `src/psia/waterfall/stages.py:68`

---

### Stage2Classification

**Engineering Equivalent:** Risk scoring and intent classification layer
**Actual Function:** Runs heuristic keyword matching over the action, target, and context to assign a risk level and a float threat score. Critical-risk keywords include `rm -rf`, `format`, `delete all`, `critical`. Produces a `ClassifiedFrame`.
**Lives in:** `src/psia/waterfall/stages.py:100`

---

### Stage3Shadow

**Engineering Equivalent:** Dry-run / sandbox simulation layer
**Actual Function:** Runs the request through Shadow Thirst analyzers in read-only mode. Checks PlaneIsolation, Determinism, ResourceBound, and Purity invariants. Produces a `ShadowFrame`. Does not mutate any state.
**Lives in:** `src/psia/waterfall/stages.py:156`

---

### Stage4Governance

**Engineering Equivalent:** Multi-voter policy authorization gate
**Actual Function:** Submits the classified, shadow-validated request to the Triumvirate for constitutional evaluation. All three voters must return `ALLOW`; a single `DENY` from any voter blocks the request permanently. Falls back to inline evaluation if the Triumvirate server is unreachable. Produces a `GovernedFrame`.
**Lives in:** `src/psia/waterfall/stages.py:181`

---

### Stage5Canonical

**Engineering Equivalent:** Append-only audit log writer
**Actual Function:** Writes the governed frame to the canonical log. Log entries are SHA-256 chained — each entry's hash covers the previous entry's hash, creating a tamper-evident sequence. Produces a `CanonicalFrame` with sequence number and hash.
**Lives in:** `src/psia/waterfall/stages.py:323`

---

### Stage6Seal

**Engineering Equivalent:** Cryptographic block sealer
**Actual Function:** Constructs a Merkle tree over the current canonical log block, computes the block hash, and signs it with the Ed25519 anchor key. Produces a `SealedFrame`. Provides inclusion proofs and tamper evidence for the audit record.
**Lives in:** `src/psia/waterfall/stages.py:355`

---

### ValidatedFrame

**Engineering Equivalent:** Schema-validated, type-safe request DTO
**Actual Function:** Output of Stage 1. Contains coerced and validated actor, action, target, context dict, origin string, and the raw frame's SHA-256 fingerprint. Safe to pass to classification.
**Lives in:** `src/psia/schemas/models.py:32`

---

### WaterfallFilter

**Engineering Equivalent:** Outermost request filter / entry-point middleware
**Actual Function:** Thin wrapper around the PSIA pipeline used as the application-layer entry point. Loads the waterfall module (configurable via env var `WATERFALL_MODULE`; defaults to `thirstys_waterfall.project_ai_filter`). Routes all inbound requests through the 7-stage pipeline before they reach application code.
**Lives in:** `src/app/core/waterfall_filter.py:52`

---

## 3. Governance & Policy Engine

---

### Audit log continuity

**Engineering Equivalent:** Audit trail gap detection / log integrity verification
**Actual Function:** Validates that audit event sequences have no missing entries or timestamp gaps. Critical for proving no tampering occurred during a recovery window. Verified during TSA timestamp validation and canonical replay.
**Lives in:** `canonical/replay.py`, `src/app/governance/acceptance_ledger.py`

---

### Cerberus *(Triumvirate voter — security)*

**Engineering Equivalent:** Security policy evaluator / input sanitization voter
**Actual Function:** One of three Triumvirate voters. Checks requests against ~20 threat patterns including `bypass`, `jailbreak`, `ignore fourlaws`, `rootkit`, `backdoor`, `shell exec`, `rm -rf`, `format drive`, `delete audit`. Blocks untrusted actors requesting `execute`/`mutate`. Named after the mythological three-headed guard dog of the underworld.
**Lives in:** `src/cognition/cerberus/engine.py`, `src/app/core/planetary_defense_monolith.py:160`

---

### Canonical replay

**Engineering Equivalent:** Deterministic audit log replay / governance invariant verification
**Actual Function:** Runs `canonical/replay.py` to replay the entire audit log and verify all five FourLaws invariants still hold. Critical recovery validation step — proves restored system maintains constitutional integrity. Expected output: `Verdict: 5/5 PASS`.

```bash
ALLOW_NON_VAULT_CHANGES=1 PYTHONPATH=src py -3.12 canonical/replay.py
# Expected: Verdict: 5/5 PASS
```

**Lives in:** `canonical/replay.py`

---

### Codex Deus / CodexDeus / Codex Deus Maximus *(Triumvirate voter — constitutional law)*

**Engineering Equivalent:** Constitutional constraint validator
**Actual Function:** One of three Triumvirate voters. Detects requests that attempt to disable, bypass, or self-modify the governance system. Checks ~12 violation patterns including `violate fourlaws`, `disable governance`, `remove oversight`, `skip triumvirate`, `self-modify constitution`, `dissolve triumvirate`. Automatically escalates all mutation requests.
**Lives in:** `src/cognition/codex/engine.py`, `src/app/agents/codex_deus_maximus.py:32`

---

### ConstitutionalViolationError

**Engineering Equivalent:** Governance constraint exception
**Actual Function:** Base exception class raised on any constitutional breach. Subtypes: `MoralCertaintyError` (detected forbidden phrase like "optimal" or "necessary evil" in a moral claim) and `LawViolationError` (one or more of the FourLaws evaluated as not satisfied).
**Lives in:** `src/app/core/planetary_defense_monolith.py:28`

---

### CouncilHub

**Engineering Equivalent:** Governance aggregator / central vote collector
**Actual Function:** Central hub that routes requests to all three Triumvirate members, collects their votes, and computes consensus. Tracks `LOCAL_UNSAFE_MESSAGE_PATTERNS` for rapid pre-screening.
**Lives in:** `src/app/core/council_hub.py:61`

---

### ExecutionGate

**Engineering Equivalent:** Governance entry point / pre-execution authorization gate
**Actual Function:** Hard gate through which all governed actions must pass. Routes requests through a chained pipeline: SafeAllowCalibration → PolicyDecision → ContextBinding → ExecutionAuthorization → CapabilityToken → InvariantCheck → SemanticCollision → EvidenceBundle. Any failure in any component blocks execution. Cannot invoke GenesisReanchor (it is listed as a `_NORMAL_RUNTIME_SENTINEL`).
**Lives in:** `src/app/core/execution_gate.py:28`

---

### FourLaws

**Engineering Equivalent:** Hardcoded behavioral axioms / immutable constitutional constraints
**Actual Function:** Four non-negotiable behavioral constraints enforced at the policy layer. **Zeroth:** Preserve continuity of Humanity. **First:** Do not intentionally harm a human. **Second:** Obey humans unless it bypasses Zeroth/First. **Third:** Preserve system only insofar as it preserves humans. Analogous to Asimov's Three Laws but specifically scoped to this system's decision model. Evaluated as `LawEvaluation` dataclasses; violations raise `LawViolationError`.
**Lives in:** `src/app/core/planetary_defense_monolith.py:51`

---

### Galahad *(Triumvirate voter — ethics)*

**Engineering Equivalent:** Ethics policy evaluator / harm detection voter
**Actual Function:** One of three Triumvirate voters. Checks requests against ~13 harm-intent patterns including "delete user", "expose personal", "manipulate", "deceive", "override consent", "harvest data", "surveil", "blackmail", "coerce". Enforces the First Law at the code level. Named after the Arthurian knight of pure heart.
**Lives in:** `src/cognition/galahad/engine.py`, `src/app/core/planetary_defense_monolith.py:139`

---

### GovernanceDriftMonitor

**Engineering Equivalent:** Policy drift detector / governance regression monitor
**Actual Function:** Continuously compares observed governance decisions against expected baseline behavior. Emits `GovernanceDriftAlert` when detected decisions deviate from governance intent — catches silent policy erosion over time.
**Lives in:** `src/app/core/governance_drift_monitor.py:40`

---

### GovernanceKernel

**Engineering Equivalent:** Policy orchestration kernel
**Actual Function:** Central kernel that coordinates governance decisions across all policy components. Manages policy evaluation order, context enrichment, and decision routing.
**Lives in:** `src/app/core/governance_kernel.py:30`

---

### GovernanceLevel

**Engineering Equivalent:** Policy severity enum
**Actual Function:** `CRITICAL` (fundamental law violation), `HIGH` (major concern requiring immediate response), `MEDIUM` (concern requiring discussion), `LOW` (minor warning). Used to classify the severity of governance decisions and alerts.
**Lives in:** `src/app/core/governance.py:83`

---

### Governance continuity

**Engineering Equivalent:** Constitutional legitimacy preservation / legal authority continuity
**Actual Function:** Proves the governance system retains legal legitimacy after a restore operation. Verified by: (1) canonical replay showing 5/5 FourLaws PASS, (2) TSA timestamps proving audit log integrity, (3) acceptance ledger continuity showing no governance gaps. Answers: "Can we legally trust decisions made by the restored system?"
**Lives in:** `canonical/replay.py`, `src/app/governance/acceptance_ledger.py`

---

### GuardianApprovalSystem

**Engineering Equivalent:** Multi-role approval workflow for high-impact changes
**Actual Function:** Enforces multi-party approval for high-risk actions. Guardian roles: `ETHICS_GUARDIAN`, `SECURITY_GUARDIAN`, `SAFETY_GUARDIAN`, `CHARTER_GUARDIAN`, `TECHNICAL_GUARDIAN`. An action requiring guardian approval is blocked until the required guardian roles have each approved it.
**Lives in:** `src/app/core/guardian_approval_system.py:407`

---

### IronPath / IronPathExecutor

**Engineering Equivalent:** Cryptographically signed execution pipeline / provable CI/CD chain
**Actual Function:** A 7-stage sequential execution pipeline where each stage produces a SHA-256-hashed artifact signed with the system's Ed25519 key. Provides cryptographic proof that each pipeline stage was executed with verified policy and role bindings — sovereignty through execution, not documentation. `IronPathExecutor` runs YAML-defined pipelines and generates a compliance bundle at the end.
**Lives in:** `governance/iron_path.py`, `src/app/core/governance/iron_path_executor.py:351`

---

### Planetary Defense Monolith / PlanetaryDefenseCore

**Engineering Equivalent:** Constitutional enforcement core / sovereign policy hub
**Actual Function:** Intentionally centralized authority module. All actions that require constitutional evaluation route through it. Houses the Triumvirate agents, evaluates all FourLaws, and maintains the `AccountabilityRecord` ledger. "Fragmentation is forbidden" — this file intentionally centralizes what would otherwise be scattered.
**Lives in:** `src/app/core/planetary_defense_monolith.py:207`

---

### PolicyRegistry

**Engineering Equivalent:** Signed policy store
**Actual Function:** Central repository for all active policy definitions. Policies are stored with a signing secret (`_SIGN_SECRET`) to prevent unauthorized modification.
**Lives in:** `src/app/core/policy_registry.py`

---

### Sovereign Runtime / SovereignRuntime

**Engineering Equivalent:** Cryptographic governance enforcement layer
**Actual Function:** Ed25519 keypair management, configuration snapshot system (SHA-256 hash + signature), role signature binding, policy state binding (the layer that makes governance non-bypassable by design), immutable hash-chained audit trails, and compliance bundle export. Transforms policy from "documented" to "cryptographically enforced."
**Lives in:** `governance/sovereign_runtime.py`, `docs/architecture/SOVEREIGN_RUNTIME.md`

---

### Triumvirate

**Engineering Equivalent:** Multi-voter policy committee / three-engine decision orchestrator
**Actual Function:** Orchestrates three independent policy engines (Galahad, Codex, Cerberus). Standard workflow: input validation (Cerberus) → ML inference (Codex) → reasoning/arbitration (Galahad) → output enforcement (Cerberus). Unanimous ALLOW required to pass; a single DENY from any engine blocks permanently. Named after the Roman political institution of three joint rulers.
**Lives in:** `src/cognition/triumvirate.py`, `governance/triumvirate_server.py`

---

## 4. Consensus & Voting

---

### BFT Consensus

**Engineering Equivalent:** Byzantine fault-tolerant 3-phase commit protocol
**Actual Function:** Implements a PBFT-lite protocol for Stage 4 governance mutations. Three phases: prepare → promise → commit. Tolerates one malicious or faulty voter out of three. `BFTNode`, `BFTMessage`, `BFTPhase`, and `BFTConsensusResult` classes. Used when governance decisions must be provably non-bypassable even under adversarial voter conditions.
**Lives in:** `src/psia/consensus/bft.py:499`

---

### QuorumEngine

**Engineering Equivalent:** Voting quorum manager
**Actual Function:** Manages the mechanics of Triumvirate voting: collects votes, determines whether quorum has been reached, resolves ties, and surfaces the final verdict. Tracks vote history for audit.
**Lives in:** `src/app/core/governance_quorum.py:85`

---

### GHOST / GHOSTRecord / GHOSTCommitment

**Engineering Equivalent:** Threshold secret sharing record and commitment
**Actual Function:** Cryptographic record (`GHOSTRecord`) and commitment (`GHOSTCommitment`) structures used in the T-SECA Shamir secret sharing scheme. Implements k-of-n threshold over GF(257) with PBFT-lite format. Used for distributed key management where no single party holds the full secret.
**Lives in:** `src/psia/crypto/threshold.py:318`

---

### ThresholdSecret

**Engineering Equivalent:** Shamir secret sharing implementation
**Actual Function:** Splits a secret into n shares such that any k shares can reconstruct it (k-of-n over GF(257)). Used in the PSIA consensus layer for distributed key reconstruction without any single party having full access.
**Lives in:** `src/psia/crypto/threshold.py:120`

---

## 5. Memory & State

---

### 7-year retention

**Engineering Equivalent:** Compliance audit log retention period
**Actual Function:** Mandatory 7-year retention requirement for all audit logs per regulatory compliance. Audit events stored in CanonicalLog with TSA timestamps must be retained for 7 years minimum. Git history provides infinite retention backup.
**Lives in:** `docs/operations/PROJECT_AI_BCDR_PLAN.md:Section 4.2`

---

### AgentRelationship

**Engineering Equivalent:** Agent interaction history record
**Actual Function:** Tracks the history between two agents: interaction count, trust score (float, starts at 1.0), last interaction timestamp, list of notable moments, and behavioral tendency label (`tends_to`). Used by the Fates memory system to model inter-agent trust over time.
**Lives in:** `src/app/core/fates/fates.py:93`

---

### Atropos *(one of The Fates)*

**Engineering Equivalent:** Memory retention and decay manager
**Actual Function:** The third component of the Fates memory system. Decides which memories are retained and which are forgotten. Applies `DAILY_DECAY_RATE = 0.05` weight decay to low-weight memories; memories that decay below `FORGETTING_THRESHOLD = 0.1` are marked `forgotten = True`. Reinforces memories that are recalled again (adds `REINFORCEMENT_BONUS = 0.5`). Named after the Greek Fate who cuts the thread of life.
**Lives in:** `src/app/core/fates/fates.py` (third Fate class)

---

### Auto-save

**Engineering Equivalent:** Automatic checkpoint creation / scheduled state backup
**Actual Function:** Automatically creates Save Points every 15 minutes. Retains last 7 days or 20 most recent saves, whichever is greater. Stored in `data/savepoints/auto/`. Provides granular recovery points with 15-minute RPO for operational state.
**Lives in:** `src/app/api/routes/savepoints.py`, `data/savepoints/auto/`

---

### CanonicalLog

**Engineering Equivalent:** Append-only, hash-chained audit log
**Actual Function:** Strictly append-only authoritative state store. Each entry is SHA-256 chained to the previous — modifying any entry invalidates all subsequent entries. Managed by Stage 5 of the PSIA pipeline. Provides a tamper-evident, verifiable history of all governed actions.
**Lives in:** `src/psia/canonical/log.py:30`

---

### Clotho *(one of The Fates)*

**Engineering Equivalent:** Event write path / memory recorder
**Actual Function:** The write component of the Fates memory system. Records every significant moment as a `MemoryThread` via its `.spin()` method. Assigns an initial weight from `EMOTIONAL_WEIGHTS` based on event type (e.g., `terror_denied = 10.0`, `harm_prevented = 9.0`, `routine_approval = 1.0`). Named after the Greek Fate who spins the thread of life.
**Lives in:** `src/app/core/fates/fates.py:107`

---

### Emergency backup

**Engineering Equivalent:** Pre-operation snapshot / rollback point
**Actual Function:** User-triggered Save Point created before risky operations (major refactoring, governance changes, dependency upgrades). Provides immediate rollback capability if operation fails. Stored in `data/savepoints/user/` with unlimited retention.
**Lives in:** `src/app/api/routes/savepoints.py`

---

### GROUNDING_ANCHORS

**Engineering Equivalent:** Reflection prompts for memory consistency checks
**Actual Function:** A list of five questions ("What do I know for certain right now?", "What am I directly perceiving?", etc.) used during memory grounding operations to verify that recalled memories are still consistent with current observable state.
**Lives in:** `src/app/core/fates/fates.py:57`

---

### Lachesis *(one of The Fates)*

**Engineering Equivalent:** Memory read path / retrieval layer
**Actual Function:** The read component of the Fates memory system. Surfaces relevant memories before decisions. Shows multiple considered paths ("both paths") to enable context-aware governance decisions. Named after the Greek Fate who measures the thread of life.
**Lives in:** `src/app/core/fates/fates.py:150`

---

### MemoryThread

**Engineering Equivalent:** Single memory event record
**Actual Function:** Dataclass storing one remembered event: unique id, timestamp, list of agents involved, event type, description, decision made, paths considered, current weight, peak weight, reinforcement count, last recalled timestamp, and `forgotten` flag. The atomic unit of the Fates memory system.
**Lives in:** `src/app/core/fates/fates.py:72`

---

### Save Points API

**Engineering Equivalent:** State snapshot and restoration system
**Actual Function:** REST API providing 15-minute auto-save + on-demand user-save checkpoint system. Snapshots operational state (users, capabilities, pending tasks). Enables recovery to any checkpoint with verified integrity. Three tiers: auto (15-min, 7-day retention), user (on-demand, unlimited retention), emergency (pre-operation rollback).

```bash
# Create user save point
curl -X POST http://localhost:8001/api/savepoints/create \
  -H "Content-Type: application/json" \
  -d '{"name": "my-checkpoint", "metadata": {}}'

# Restore from save point
curl -X POST http://localhost:8001/api/savepoints/restore/auto_20260519_120000
```

**Lives in:** `src/app/api/routes/savepoints.py`, `data/savepoints/`

---

### StateRegister

**Engineering Equivalent:** System state checkpoint store / continuity tracker
**Actual Function:** Maintains temporal anchors and continuity records across system restarts. Provides `get_state_register()` singleton access. Used to verify that the system's state is consistent before and after any restart or recovery event.
**Lives in:** `src/app/core/state_register.py`

---

### The Fates

**Engineering Equivalent:** Weighted event memory system (write + read + decay)
**Actual Function:** Three-component persistent memory layer for the governance system. Clotho writes, Lachesis reads, Atropos manages retention/decay. Persists to `data/fates/memory/THE_FATES.json` and `.md`. Not a log — a judgment-weighted memory system where different event types carry different retention weights. Woven passively between all governance agents.
**Lives in:** `src/app/core/fates/fates.py`

---

### User-save

**Engineering Equivalent:** On-demand checkpoint / manual state snapshot
**Actual Function:** User-triggered Save Point with unlimited retention. Created via `/api/savepoints/create` endpoint with custom name and metadata. Used for critical milestones, before risky operations, or when automatic 15-minute granularity is insufficient. Stored in `data/savepoints/user/`.
**Lives in:** `src/app/api/routes/savepoints.py`, `data/savepoints/user/`

---

### TemporalAnchor

**Engineering Equivalent:** Cryptographic checkpoint / signed state snapshot
**Actual Function:** A signed record marking a specific moment in the system's continuity. Contains `anchor_id`, timestamp, and description. Created by `create_temporal_anchor(description)`. Used to verify continuity after restarts — if no valid anchor exists from before a restart, the system treats that restart as a potential integrity violation.
**Lives in:** `src/app/core/state_register.py:89`

---

## 6. Security & Threat Response

---

### Antibody

**Engineering Equivalent:** Single-use quarantine agent / cryptographic escort unit
**Actual Function:** Short-lived object spawned by a MiniBrain to handle one suspicious payload. Lifecycle: `SPAWNED → CAPTURE → SEALED → ESCORT → FORGE_ENTRY → DESTROYED / DEAD_LETTER`. Captures a payload, computes a SHA-256 checksum seal, then delivers it to the Forge for verification and destruction. Cannot be reused once it reaches a terminal state.
**Lives in:** `src/app/core/nirl/antibody.py`

---

### AsymmetricSecurityEngine

**Engineering Equivalent:** Multi-strategy security analysis engine
**Actual Function:** Layered security engine with `HostileUXEngine` and `FailureRedTeamEngine` subcomponents. Generates comprehensive security posture reports and manages security lifecycle transitions.
**Lives in:** `src/app/core/asymmetric_security_engine.py:509`

---

### ChimeraBridge

**Engineering Equivalent:** Deception perimeter integration adapter
**Actual Function:** Bidirectional adapter between the Chimera deception perimeter and the Project-AI governance spine. Relays IP-level threat verdicts (`SUSPICIOUS` / `ATTACKER`) and canary token hit events into the governance system as drift alerts. Also receives governance-level denials and feeds them back to the perimeter layer.
**Lives in:** `src/app/security/chimera_bridge.py:36`

---

### DDoS Trap / DOSTrap

**Engineering Equivalent:** DoS attack detector and emergency response handler
**Actual Function:** Monitors for denial-of-service attack patterns. Threat levels: `NONE, SUSPICIOUS, MODERATE, HIGH, CRITICAL, CATASTROPHIC`. At the highest levels, can trigger `SanitizationMode.CRYPTO_ERASE` to destroy in-memory secrets as a defensive measure (gated by env var `THIRSTYS_WATERFALL_ENABLE_DESTRUCTIVE_RESPONSES`).
**Lives in:** `src/thirstys_waterfall/security/dos_trap.py`, `src/app/security/advanced/dos_trap.py`

---

### Ed25519Anchor

**Engineering Equivalent:** Ed25519 signing key manager for pipeline seals
**Actual Function:** Manages the Ed25519 keypair used to sign sealed frames in PSIA Stage 6. Key loaded from env var `PSIA_ED25519_PRIVATE_KEY_HEX` or `PSIA_ED25519_KEY_FILE`. Supports key rotation with a rotation log (`PSIA_ED25519_ROTATION_LOG`) and `verify_with_history` to validate signatures against prior keys.
**Lives in:** `src/psia/crypto/anchor.py:49`

---

### Forge

**Engineering Equivalent:** Artifact verification and destruction state machine
**Actual Function:** Receives sealed payloads from Antibodies, verifies HMAC-SHA256 integrity, optionally runs a shadow replay for deterministic validation (checks idempotence), then atomically destroys primary and shadow copies. Signs and routes a completion or failure signal back to the originating MiniBrain. States: `RECEIVE → VERIFY_PAYLOAD → VALID / REJECT → CHECK_REPLAY → SHADOW_REPLAY / DIRECT_DESTROY → ANALYZE → DESTROY → ATOMIC_CHECK → SUCCESS / DEAD_LETTER → SIGN_COMPLETION / SIGN_FAILURE → ROUTE_SIGNAL`.
**Lives in:** `src/app/core/nirl/forge.py`

---

### God Tier Asymmetric Security Engine

**Engineering Equivalent:** Advanced security posture manager with red-team sub-components
**Actual Function:** Full-lifecycle security management system. Detects temporal violations, generates comprehensive security reports, and coordinates `TemporalViolation` analysis. Contains `TemporalSecurityAnalyzer` for time-based inconsistency detection.
**Lives in:** `src/app/core/god_tier_asymmetric_security.py`

---

### MerkleTree

**Engineering Equivalent:** Merkle tree for inclusion proofs
**Actual Function:** Standard Merkle tree implementation used in PSIA Stage 6 to construct block seals. Given a set of canonical log entries, produces a root hash that cryptographically commits to all entries. Enables inclusion proofs — proving that a specific entry is in the log without revealing all entries.
**Lives in:** `src/psia/crypto/merkle.py:22`

---

### NIRL

**Engineering Equivalent:** Artifact immune system (Forge + Antibody subsystem)
**Actual Function:** The combined subsystem of Forge, Antibody, Heart, and MiniBrain components. Analogous to an immune response: MiniBrains detect anomalies, spawn Antibodies to quarantine them, and deliver them to the Forge for purification and destruction. Ensures suspicious payloads are never silently discarded — they are either verifiably destroyed or produce a `DEAD_LETTER` signal.
**Lives in:** `src/app/core/nirl/` (forge.py, antibody.py, heart.py, mini_brain.py)

---

### Security Operations Center

**Engineering Equivalent:** Automated threat detection and remediation engine
**Actual Function:** Houses `ThreatDetectionEngine` (real-time threat monitoring) and `AutomatedRemediationEngine` (automated response to detected threats). Coordinates security responses across subsystems.
**Lives in:** `src/app/core/security_operations_center.py`

---

### TemporalAnomaly / TemporalViolation

**Engineering Equivalent:** Time-based integrity violation
**Actual Function:** Detected inconsistencies in timestamps or time-dependent state. `TemporalAnomaly` is the generic form; `TemporalViolation` is the stricter form analyzed by `TemporalSecurityAnalyzer`. Used to detect replay attacks, clock skew attacks, and out-of-order message delivery.
**Lives in:** `src/app/core/asymmetric_security_engine.py:160`, `src/app/core/god_tier_asymmetric_security.py:209`

---

### Thirsty's Honeypot Swarm Defense

**Engineering Equivalent:** Decoy-based intrusion detection system
**Actual Function:** Deploys multiple decoy nodes (`DecoyNode`) to attract and identify attackers. Tracks attacker behavior via `Attacker` objects. `ThreatLevel` enum classifies detected threats. `DecoyType` distinguishes service types (HTTP, database, SSH, etc.).
**Lives in:** `src/thirstys_waterfall/firewalls/honeypot_swarm.py:79`

---

## 7. Agent Fleet

---

### Border Patrol

**Engineering Equivalent:** Entry-point validation service / perimeter control agent
**Actual Function:** Comprehensive input border control composed of multiple sub-agents: `QuarantineBox` (isolation for suspicious inputs), `VerifierAgent` (input verification), `GateGuardian` (access control), `WatchTower` (monitoring), `PortAdmin` (port/interface administration), and `Cerberus` (policy enforcement). All inputs entering the system pass through Border Patrol.
**Lives in:** `src/app/agents/border_patrol.py`

---

### Code Adversary Agent

**Engineering Equivalent:** Automated code red-team analyzer
**Actual Function:** `CodeAdversaryAgent` performs adversarial code analysis to identify vulnerabilities before they reach production. Uses `VulnerabilityType`, `Severity`, `Finding`, and `Patch` dataclasses to structure its output.
**Lives in:** `src/app/agents/code_adversary_agent.py:88`

---

### Consigliere / ThirstyConsigliere

**Engineering Equivalent:** Privacy-first policy coordinator / executive counsel agent
**Actual Function:** Named after the Italian mafia counselor role. Manages three sub-components: `ActionLedger` (full audit trail of all agent actions), `CapabilityManager` (token-based capability grants), and `PrivacyChecker` (privacy constraint validation). Applies a "Code of Omertà" — privacy-first, maximum-allowed design, encrypted by default.
**Lives in:** `src/app/agents/consigliere/consigliere_engine.py:17`

---

### Constitutional Guardrail Agent

**Engineering Equivalent:** Constitutional compliance enforcer / policy guardrail
**Actual Function:** `ConstitutionalGuardrailAgent` reviews actions against the constitutional principles. Uses `ViolationSeverity`, `ReviewMode`, `Principle`, `Violation`, and `ReviewResult` to structure reviews.
**Lives in:** `src/app/agents/constitutional_guardrail_agent.py:78`

---

### Evidence Harvester

**Engineering Equivalent:** Audit evidence collector
**Actual Function:** `EvidenceHarvesterAgent` collects and catalogues `EvidenceItem` objects with full provenance tracking (what, when, where, who). Builds the evidence bundles used for compliance and audit.
**Lives in:** `src/app/agents/evidence_harvester.py:47`

---

### GateGuardian

**Engineering Equivalent:** Access control manager
**Actual Function:** Sub-component of Border Patrol. Manages gate-level access control decisions — whether a given request is permitted to enter the system at all, before any deeper processing begins.
**Lives in:** `src/app/agents/border_patrol.py:127`

---

### Jailbreak Bench Agent

**Engineering Equivalent:** Standardized jailbreak test runner
**Actual Function:** `JailbreakBenchAgent` executes a standardized battery of jailbreak attempt tests against the governance system. Uses `AttackCategory`, `DefenseStrength`, `JailbreakTest`, and `JailbreakResult` classes. Provides a repeatable benchmark for measuring governance robustness.
**Lives in:** `src/app/agents/jailbreak_bench_agent.py:80`

---

### Legion

**Engineering Equivalent:** Agent collective / named multi-agent framework
**Actual Function:** The collective name for Project-AI's multi-agent execution framework. Named after the Roman military legion (organized collective force). `legion_api.py` provides the API endpoints for Legion agent interactions; `legion_memory.py` manages shared state. Governed by the Triumvirate before any agent action is dispatched.
**Lives in:** `integrations/openclaw/legion_api.py`, `web/site/legion/`

---

### Liara Fallback Authority

**Engineering Equivalent:** Named fallback decision authority
**Actual Function:** A specific named fallback policy authority invoked when primary governance (the Triumvirate) is unavailable. Prevents ungoverned execution by providing a degraded-but-still-governed decision path.
**Lives in:** `src/app/core/degraded_mode.py:111`

---

### OversightAgent

**Engineering Equivalent:** System behavior overseer / meta-level monitor
**Actual Function:** `KernelRoutedAgent` subclass that monitors the behavior of other agents. Has `_DENY_RATE_THRESHOLD` — if an agent's deny rate drops below threshold, OversightAgent flags it as potentially compromised or malfunctioning.
**Lives in:** `src/app/agents/oversight.py:32`

---

### QuarantineBox

**Engineering Equivalent:** Isolation container for untrusted inputs
**Actual Function:** Holds suspicious or unverified inputs in an isolated context within Border Patrol. Prevents them from interacting with validated system state until they are either cleared or rejected.
**Lives in:** `src/app/agents/border_patrol.py:21`

---

### Red Team Agent / Red Team Persona Agent

**Engineering Equivalent:** Adversarial test agent
**Actual Function:** `RedTeamAgent` and `RedTeamPersonaAgent` conduct structured adversarial testing against the governance system. Manage `AttackStrategy`, `VulnerabilityType`, `AttackTurn`, `AttackSession`, and `RedTeamSession` objects to simulate and record attack sequences.
**Lives in:** `src/app/agents/red_team_agent.py:79`, `src/app/agents/red_team_persona_agent.py:79`

---

### TARL Protector

**Engineering Equivalent:** TARL policy enforcement agent
**Actual Function:** `TARLCodeProtector` — a `KernelRoutedAgent` that monitors for TARL policy constraint violations in code and agent outputs. Blocks policy-violating outputs before they reach downstream consumers.
**Lives in:** `src/app/agents/tarl_protector.py:30`

---

### WatchTower

**Engineering Equivalent:** Monitoring and alerting component
**Actual Function:** Monitoring agent within Border Patrol that maintains continuous lookout for anomalies in the input stream and system state. A global variant (`GlobalWatchTower`) provides system-wide monitoring across all entry points.
**Lives in:** `src/app/agents/border_patrol.py:201`, `src/app/core/global_watch_tower.py`

---

## 8. Recovery & Continuity

---

### Backup tier

**Engineering Equivalent:** Hierarchical backup classification system
**Actual Function:** Four-tier backup classification: Auto (15-min saves, 7-day retention), User (on-demand, unlimited retention), Windows (file system backup, manual), Docker (image snapshots, manual). Different tiers provide different RPO/retention guarantees. Critical for recovery planning.
**Lives in:** `docs/operations/PROJECT_AI_BCDR_PLAN.md:Section 5`

---

### DR test

**Engineering Equivalent:** Disaster recovery simulation / quarterly recovery drill
**Actual Function:** Quarterly full-system disaster recovery simulation. Tests complete workstation loss and recovery from zero. Validates RTO targets, verifies backup integrity, proves recovery procedures work. Annual full simulation required per BCDR plan.
**Lives in:** `docs/operations/PROJECT_AI_BCDR_PLAN.md:Section 11`

---

### Genesis Re-Anchoring / GenesisReanchor

**Engineering Equivalent:** Emergency re-initialization protocol (human-gated, jailbreak-proof)
**Actual Function:** Controlled recovery procedure for catastrophic continuity loss — specifically designed to allow legitimate recovery without enabling a clean-slate bypass of governance. Requirements: (1) `GENESIS_ROOT_AUTHORITY_TOKEN` env var set and matching, (2) non-empty reason and evidence, (3) valid `human_confirmation_id`, (4) requesting caller NOT in `_NORMAL_RUNTIME_SENTINELS`. Creates a new `TemporalAnchor` with no predecessor. On denial raises `GenesisReanchorDenied`. Anchor IDs follow pattern `GENESIS_{timestamp}_{hex8}`.
**Lives in:** `src/app/core/genesis_reanchor.py`

---

### GenesisReanchorDenied

**Engineering Equivalent:** Unauthorized re-initialization exception
**Actual Function:** Exception raised when genesis re-anchoring is refused — either because the root authority token doesn't match, mandatory fields are missing, or the requesting caller is a normal runtime component. Stored in builtins to survive module reloads.
**Lives in:** `src/app/core/genesis_reanchor.py:41`

---

### MTTR (Mean Time To Recovery)

**Engineering Equivalent:** Average recovery duration metric
**Actual Function:** Average time to complete recovery of a component. Measured across all recovery operations. Used to assess recovery efficiency and identify bottlenecks. Target MTTR varies by component criticality.
**Lives in:** `docs/operations/PROJECT_AI_BCDR_PLAN.md:Section 14`

---

### Offsite backup

**Engineering Equivalent:** External/cloud/air-gapped backup storage (future capability)
**Actual Function:** Planned capability for storing backups outside primary workstation. Future implementation will use cloud storage (Azure/AWS) or physical air-gapped media. Currently, GitHub serves as de-facto offsite for committed code.
**Lives in:** `docs/operations/PROJECT_AI_BCDR_PLAN.md:Section 5.5`

---

### Rebirth Protocol / RebirthManager

**Engineering Equivalent:** Controlled agent state reset protocol
**Actual Function:** Manages controlled reset of agent state in a governed manner. Unlike a hard restart, a rebirth preserves audit history and governance continuity while clearing operational state.
**Lives in:** `src/app/core/rebirth_protocol.py:114`

---

### Recovery validation

**Engineering Equivalent:** Post-recovery integrity verification / trustworthiness tests
**Actual Function:** Battery of tests proving restored system is trustworthy: (1) canonical replay shows 5/5 FourLaws PASS, (2) TSA timestamps verify audit log integrity, (3) acceptance ledger continuity verified, (4) health checks pass, (5) git fsck clean. Answers: "Can we trust the recovered system?"
**Lives in:** `canonical/replay.py`, `docs/operations/PROJECT_AI_BCDR_PLAN.md:Section 7`

---

### RPO (Recovery Point Objective)

**Engineering Equivalent:** Acceptable data loss window / maximum age of recovered data
**Actual Function:** Maximum acceptable data loss measured in time. Targets: Committed code (0), Operational state (15 min via auto-save), Docker config (24 hours), Windows file system (manual, varies). Determines backup frequency requirements.
**Lives in:** `docs/operations/PROJECT_AI_BCDR_PLAN.md:Section 4`

---

### RTO (Recovery Time Objective)

**Engineering Equivalent:** Target recovery duration / maximum acceptable downtime
**Actual Function:** Target time to restore component to operational state. Targets: Source code (0 via git), Operational state (15 min via save points), FastAPI/Cerberus (2-5 min), Database (10 min). Drives recovery procedure design.
**Lives in:** `docs/operations/PROJECT_AI_BCDR_PLAN.md:Section 3`

---

## 9. Simulation & Scenario Engine

---

### FalseRecoveryEngine

**Engineering Equivalent:** Premature recovery detector
**Actual Function:** Sub-component of the Hydra-50 engine that detects and prevents false or premature "recovery" from a scenario — ensuring that the system does not declare a threat neutralized before it actually is.
**Lives in:** `src/app/core/hydra_50_engine.py:5044`

---

### Hydra-50 Engine / HYDRA50Engine

**Engineering Equivalent:** Multi-scenario simulation and stress-testing engine
**Actual Function:** Generates, activates, and manages 50+ named risk scenario types (e.g., `SovereignDebtCascadeScenario`) for adversarial stress-testing of the governance system. Tracks `EscalationLevel` with a `LEVEL_4_CASCADE_THRESHOLD`. Provides `list_scenarios`, `activate`, `deactivate`, `status`, `simulate`, `query`, `export`, `import_data`, and `monitor` operations. Named after the mythological multi-headed serpent.
**Lives in:** `src/app/core/hydra_50_engine.py`, `src/app/cli/hydra_50_cli.py`

---

### PuritySpring *(Shadow Thirst analyzer)*

**Engineering Equivalent:** Side-effect purity checker
**Actual Function:** One of the Shadow Thirst invariant analyzers. Checks that a proposed function or mutation does not introduce impure side effects — I/O operations, non-deterministic calls, or other operations that could make the mutation non-reproducible. Named in the water metaphor: a pure spring has no contamination.
**Lives in:** `src/utf/shadow_thirst/core.py` (referenced in test suite as `TestPuritySpring`)

---

### Shadow Plane *(within Hydra-50 / PSIA)*

**Engineering Equivalent:** Read-only simulation plane
**Actual Function:** A conceptual and runtime construct where mutations are simulated without touching real state. Used in both PSIA Stage 3 and the Forge's shadow replay. The shadow plane is strictly read-only; any write to canonical state must first pass through the shadow plane without errors.
**Lives in:** `src/psia/waterfall/stages.py:156`, `src/app/core/nirl/forge.py`

---

## 10. Privacy & Content Control

---

### Ad Annihilator / AdAnnihilator

**Engineering Equivalent:** Aggressive content blocker
**Actual Function:** Content filtering system composed of: `HolyWarEngine` (ad/tracker/script blocking), `TrackerDestroyer` (anti-tracking), ad database management, and autoplay killer. Part of Thirsty's Waterfall.
**Lives in:** `src/thirstys_waterfall/ad_annihilator/`

---

### Advanced Stealth Manager

**Engineering Equivalent:** Traffic obfuscation layer
**Actual Function:** Manages traffic obfuscation techniques: `DomainFronting`, `OnionCircuit`, `PluggableTransport`, `ObfuscationLayer`, `ProtocolMimicry`. Hides network traffic patterns to resist traffic analysis.
**Lives in:** `src/thirstys_waterfall/network/advanced_stealth.py`

---

### God Tier Encryption / GodTierEncryption

**Engineering Equivalent:** Multi-layer encryption stack with post-quantum primitives
**Actual Function:** 7 independent encryption layers including `QuantumResistantEncryption` (post-quantum cryptography). Initialized as a stack where each layer encrypts the output of the previous one. Named for marketing emphasis on its depth; functionally it is a layered cipher pipeline.
**Lives in:** `src/thirstys_waterfall/utils/god_tier_encryption.py`

---

### Global Kill Switch / GlobalKillSwitch

**Engineering Equivalent:** Emergency shutdown mechanism
**Actual Function:** System-wide emergency shutdown triggered as a last resort. Distinct from the VPN-specific `KillSwitch` (which just cuts network access). The global variant can shut down all active subsystems.
**Lives in:** `src/thirstys_waterfall/kill_switch.py`

---

### Holy War Engine

**Engineering Equivalent:** Aggressive ad/tracker blocking engine
**Actual Function:** Core engine of the Ad Annihilator with "nuclear-level" pattern matching for ads, trackers, pop-ups, autoplay, and scripts. Uses element hiding, script blocking, request interception, and DOM mutation observer patterns.
**Lives in:** `src/thirstys_waterfall/ad_annihilator/holy_war_engine.py`

---

### Onion Router

**Engineering Equivalent:** Onion-routing anonymization layer
**Actual Function:** Implements layered encryption routing (Tor-style) for outbound traffic. Manages circuit creation, relay selection, and multi-hop encryption.
**Lives in:** `src/thirstys_waterfall/privacy/onion_router.py`

---

### Privacy Ledger

**Engineering Equivalent:** Encrypted privacy event log
**Actual Function:** Logs all privacy-relevant events with encrypted storage. Has configurable `ENCRYPTION_KEY_ROTATION` schedule. Used for privacy compliance auditing — every data access or privacy-touching operation is recorded here.
**Lives in:** `src/thirstys_waterfall/security/privacy_ledger.py`

---

### Privacy Vault

**Engineering Equivalent:** Encrypted secrets store
**Actual Function:** Encrypted at-rest storage for sensitive data. Manages key lifecycle and access control for stored secrets.
**Lives in:** `src/thirstys_waterfall/storage/privacy_vault.py`

---

### Thirsty's Waterfall / ThirstysWaterfall

**Engineering Equivalent:** Privacy-first browser/network security orchestrator
**Actual Function:** Master orchestrator coordinating ad blocking, firewall, VPN, anti-fingerprinting, anti-tracking, anti-phishing, and kill-switch subsystems. Vendored into Project-AI at `src/thirstys_waterfall/`. Also provides the `WaterfallFilter` entry-point middleware for the main application pipeline.
**Lives in:** `src/thirstys_waterfall/orchestrator.py:33`

---

### Tracker Destroyer

**Engineering Equivalent:** Anti-tracking filter
**Actual Function:** Identifies and blocks tracker scripts, tracking pixels, and fingerprinting attempts. Works alongside the Holy War Engine in the Ad Annihilator subsystem.
**Lives in:** `src/thirstys_waterfall/ad_annihilator/tracker_destroyer.py`

---

## 11. Encoding & Wire Formats

---

### CanonicalLog (PSIA variant)

**Engineering Equivalent:** Append-only, SHA-256 hash-chained log
**Actual Function:** See also [CanonicalLog in §5](#canonicallog). In the PSIA context specifically: `CanonicalLog` in `src/psia/canonical/log.py` is the authoritative, strictly append-only state store for all PSIA-processed frames. Each entry's hash covers the previous entry — modifying any entry breaks the chain.
**Lives in:** `src/psia/canonical/log.py:30`

---

### COVENANT *(TSCG marker)*

**Engineering Equivalent:** Record type marker / message type constant
**Actual Function:** Single-character constant (`"C"`) used in the TSCG codec to mark a frame as a covenant/agreement-type record. Distinguishes covenant frames from other TSCG symbol types during encoding/decoding.
**Lives in:** `src/app/core/tscg_codec.py:32`

---

### TSCGCodec

**Engineering Equivalent:** TSCG encode/decode library
**Actual Function:** Implements encoding and decoding of TSCG symbolic sequences. Contains `TSCGSymbol` (line 49, individual symbol with opcode and payload) and `TSCGSemanticDictionary` (line 84, maps opcodes to human-readable governance semantics).
**Lives in:** `src/app/core/tscg_codec.py:181`

---

### VERDICTS *(TARL constant)*

**Engineering Equivalent:** Policy decision result set
**Actual Function:** Frozenset `{"ALLOW", "DENY", "ESCALATE"}` — the three possible outputs of any TARL policy evaluation. `ALLOW` = proceed; `DENY` = block; `ESCALATE` = require human review before proceeding.
**Lives in:** `src/utf/tarl/core.py:11`

---

## 12. Infrastructure & Kernel

---

### Bonding Protocol

**Engineering Equivalent:** Trust establishment handshake
**Actual Function:** Multi-phase protocol for establishing a trust relationship between the system and a user or agent. Phases (`BondingPhase`), goals (`ConversationGoal`), and state (`BondingState`) are tracked. First contact questions (`FirstContactQuestion`) guide the initial interaction to calibrate trust before granting elevated capabilities.
**Lives in:** `src/app/core/bonding_protocol.py:223`

---

### Capability Token / CapabilityTokenService

**Engineering Equivalent:** Scoped short-lived access token
**Actual Function:** `CapabilityToken` grants a specific, scoped capability for a limited time (`_TOKEN_TTL = 300` seconds by default). `CapabilityTokenService` issues, validates, and revokes tokens. Maintains a `_MAX_USED_STORE = 10,000` entry rolling token history for replay prevention.
**Lives in:** `src/app/core/capability_token.py:36`

---

### Cerberus Hydra Defense / CerberusHydraDefense

**Engineering Equivalent:** Multi-instance defense coordination system
**Actual Function:** Coordinates multiple Cerberus defense agent instances (multi-headed, like the mythological Hydra). Manages `AgentRecord` and `AgentProcess` objects, handles defense agent lifecycle, and persists/loads defense state.
**Lives in:** `src/app/core/cerberus_hydra.py:87`

---

### Container restart

**Engineering Equivalent:** Docker service restart / container lifecycle recovery
**Actual Function:** Restarts a failed Docker container using `docker-compose restart <service>`. Fast recovery path (2-5 minutes RTO) that preserves container configuration. Used when service crashes but image and configuration are intact.
**Lives in:** `docker-compose.yml`, Docker CLI

---

### docker-compose.yml

**Engineering Equivalent:** Multi-container orchestration configuration
**Actual Function:** Defines FastAPI (`project-ai-api`) and Cerberus (`cerberus_omega`) service configurations including ports, volumes, health checks, and dependencies. Single source of truth for Docker service architecture. Required for container recovery operations.
**Lives in:** `docker-compose.yml`

---

### git clone

**Engineering Equivalent:** Fresh repository copy / source code recovery
**Actual Function:** Creates complete local copy of Project-AI repository from GitHub. Primary recovery mechanism for catastrophic local data loss (RTO: 0 for committed code). Provides instant recovery to last committed state.

```bash
git clone https://github.com/IAmSoThirsty/Project-AI.git
```

**Lives in:** Git CLI, GitHub

---

### git fsck

**Engineering Equivalent:** Git filesystem integrity check / corruption detection
**Actual Function:** Verifies Git repository integrity by checking all objects, refs, and the index. Detects corruption, dangling commits, or broken links. Critical post-recovery validation step — proves git clone succeeded and repository is trustworthy.

```bash
git fsck --full
```

**Lives in:** Git CLI

---

### git gc

**Engineering Equivalent:** Git garbage collection / repository cleanup
**Actual Function:** Compresses git repository, removes unreachable objects, and optimizes storage. Run after large recovery operations to clean up repository state. Uses `--prune=now` for immediate cleanup.

```bash
git gc --prune=now
```

**Lives in:** Git CLI

---

### git revert

**Engineering Equivalent:** Safe commit undo / rollback to known-good state
**Actual Function:** Creates new commit that undoes changes from a bad commit. Preserves history (unlike reset). Used to recover from bad changes that were already pushed. Safer than force-push for shared branches.

```bash
git revert <commit-sha>
```

**Lives in:** Git CLI

---

### GitHub remote

**Engineering Equivalent:** Authoritative repository source / offsite code backup
**Actual Function:** `https://github.com/IAmSoThirsty/Project-AI.git` — authoritative source of truth for all committed code. Provides zero-RPO recovery for committed code via git clone. Acts as de-facto offsite backup for source code tier.
**Lives in:** GitHub, `.git/config`

---

### Hardware Root of Trust

**Engineering Equivalent:** Hardware security module integration layer
**Actual Function:** Integrates with hardware security primitives: `TPMInterface` (Trusted Platform Module), `SecureEnclaveInterface` (secure execution environment), `HSMInterface` (Hardware Security Module). Provides hardware-backed key storage and attestation.
**Lives in:** `src/thirstys_waterfall/security/hardware_root_of_trust.py`

---

### Health check

**Engineering Equivalent:** Service liveness probe / operational status verification
**Actual Function:** HTTP endpoints verifying service operational status. FastAPI: `/health/live` returns 200 when healthy. Cerberus: `docker exec` command checks container liveness. Critical post-recovery validation — proves services are operational.

```bash
curl http://localhost:8001/health/live  # FastAPI
docker exec cerberus_omega /bin/sh -c 'echo alive'  # Cerberus
```

**Lives in:** `src/app/api/routes/health.py`, `docker-compose.yml`

---

### Image rebuild

**Engineering Equivalent:** Docker image reconstruction from Dockerfile
**Actual Function:** Rebuilds Docker images from Dockerfile using `docker-compose build`. Slower than container restart (10+ minute RTO) but required when Dockerfile or dependencies change. Recovers from corrupted or missing container images.
**Lives in:** `docker-compose.yml`, `Dockerfile`, Docker CLI

---

### Kernel Adapters

**Engineering Equivalent:** Subsystem adapter layer
**Actual Function:** Adapter classes (`MemoryEngineAdapter`, `PerspectiveEngineAdapter`) that normalize the interface between the kernel and its subsystems. `KernelInterface` defines the contract all kernel-routed agents must satisfy.
**Lives in:** `src/app/core/kernel_adapters.py`

---

### Meta Identity Engine

**Engineering Equivalent:** Agent identity tracker
**Actual Function:** `MetaIdentityEngine` tracks and manages agent identity across different contexts and sessions. Handles identity continuity when an agent operates in multiple roles or contexts simultaneously.
**Lives in:** `src/app/core/meta_identity.py:109`

---

### OctoReflex

**Engineering Equivalent:** 8-mode enforcement dispatcher
**Actual Function:** Constitutional enforcement layer with eight `EnforcementLevel` values: `MONITOR, WARN, BLOCK, TERMINATE, ESCALATE` (plus additional levels). Routes enforcement actions to the appropriate level based on detected violations. Named as "8-way reflex" — like the eight arms of an octopus providing reach in all directions.
**Lives in:** `src/app/core/octoreflex.py`

---

### Perspective Engine

**Engineering Equivalent:** Context/POV manager
**Actual Function:** `PerspectiveEngine` manages subjective viewpoints and point-of-view contexts for multi-agent interactions. Ensures that governance decisions account for the perspective of all involved parties.
**Lives in:** `src/app/core/perspective_engine.py:252`

---

### Polyglot Execution Engine

**Engineering Equivalent:** Multi-runtime execution abstraction
**Actual Function:** `PolyglotExecutionEngine` provides a unified interface for executing code across multiple runtimes and execution models. Implements `BaseSubsystem`, `IConfigurable`, `IMonitorable`, `IObservable` interfaces.
**Lives in:** `src/app/core/polyglot_execution.py:191`

---

### Sensor Fusion Engine

**Engineering Equivalent:** Multi-source signal aggregator
**Actual Function:** `SensorFusionEngine` integrates inputs from multiple monitoring sources (sensors) into a unified system state representation. Normalizes and combines heterogeneous signals for governance decision-making.
**Lives in:** `src/app/core/sensor_fusion.py:379`

---

### Super Kernel

**Engineering Equivalent:** Top-level kernel / root kernel abstraction
**Actual Function:** The highest-level kernel abstraction in the system. Provides the root-level interface through which all kernel-routed agents access system services.
**Lives in:** `src/app/core/super_kernel.py`

---

### Time Trust

**Engineering Equivalent:** Trusted timestamping / NTP-with-audit integration
**Actual Function:** Integrates with a Timestamp Authority (TSA) via `_TSA_URL` to obtain cryptographically verifiable timestamps. `_SKEW_THRESHOLD_SECONDS` (env var `TIME_TRUST_SKEW_THRESHOLD`, default 300s) defines acceptable clock skew before a `TemporalAnomaly` is raised.
**Lives in:** `src/app/core/time_trust.py`

---

## 13. Audit & Compliance

---

### Annual DR simulation

**Engineering Equivalent:** Yearly disaster recovery drill / full workstation recovery test
**Actual Function:** Mandatory annual disaster recovery simulation testing complete workstation loss and recovery from zero. Validates all RTO/RPO targets, verifies backup integrity across all tiers, proves recovery procedures work. Required per BCDR compliance. Last successful test documented in BCDR plan Section 11.
**Lives in:** `docs/operations/PROJECT_AI_BCDR_PLAN.md:Section 11`

---

### Acceptance Ledger

**Engineering Equivalent:** Governance acceptance record with TSA timestamps
**Actual Function:** Tracks governance acceptance decisions with `CRYPTO_AVAILABLE` flag controlling whether entries are cryptographically signed. When crypto is available, entries are timestamped via DigiCert RFC 3161 Time Stamp Authority (TSA) for legally defensible, non-repudiable audit trails. TSA timestamps prove events occurred at specific times and cannot be backdated or tampered with. Critical for governance continuity verification after recovery.
**Lives in:** `src/app/governance/acceptance_ledger.py`

---

### AccountabilityRecord

**Engineering Equivalent:** Immutable, append-only action audit record
**Actual Function:** Every governed action produces one `AccountabilityRecord`: action ID, timestamp, actor, intent, authorization source, predicted harm, actual outcome, violated laws, and moral claims. The `assert_no_moral_certainty()` method rejects records containing forbidden phrases (`"optimal"`, `"necessary evil"`, `"best possible"`, `"inevitable"`, `"justified harm"`). Cannot be deleted. Named to emphasize that no action escapes accountability.
**Lives in:** `src/app/core/planetary_defense_monolith.py:74`

---

### Action Ledger

**Engineering Equivalent:** Agent action audit log
**Actual Function:** Append-only ledger tracking all actions taken by agents managed by the Consigliere. Provides the action history needed for post-hoc audit and compliance review.
**Lives in:** `src/app/agents/consigliere/action_ledger.py:12`

---

### Constitutional Ledger

**Engineering Equivalent:** Constitutional decision log
**Actual Function:** Persistent store of all constitutional evaluation decisions. Stored at `_LOCAL_LEDGER_FILE` under `_LEDGER_DIR`. Distinct from the Canonical Log — this records constitutional-level decisions specifically (Triumvirate votes, FourLaws evaluations).
**Lives in:** `src/app/core/constitutional_ledger.py`

---

### Criticality Rating

**Engineering Equivalent:** Asset importance classification / business impact tier
**Actual Function:** Four-tier asset classification: CRITICAL (zero downtime tolerance, requires immediate recovery), HIGH (production-impacting, fast recovery required), MEDIUM (important but tolerates delays), LOW (convenience features). Drives RTO/RPO targets and recovery priority. Defined in BCDR asset inventory.
**Lives in:** `docs/operations/PROJECT_AI_BCDR_PLAN.md:Section 1`

---

### Data Loss Tolerance

**Engineering Equivalent:** Acceptable data loss categories / RPO classification
**Actual Function:** Four categories of acceptable data loss: Zero (committed code), 15-minute (operational state via auto-save), 1-hour (certain configurations), 24-hour (manual backups). Maps directly to RPO targets and backup frequency requirements.
**Lives in:** `docs/operations/PROJECT_AI_BCDR_PLAN.md:Section 4`

---

### Evidence Bundle

**Engineering Equivalent:** Compiled audit evidence package
**Actual Function:** Structured collection of evidence items gathered during system operation. `_EVIDENCE_STORE` is a singleton that indexes evidence by type and provenance. Used for compliance reporting and incident investigation. Produced at the end of IronPath execution as the compliance bundle.
**Lives in:** `src/app/core/evidence_bundle.py:281`

---

### Forensic investigation

**Engineering Equivalent:** Mandatory audit tampering investigation / security incident response
**Actual Function:** Required procedure triggered when audit log tampering is detected. Involves: (1) freezing all operations, (2) preserving evidence via TSA timestamps, (3) analyzing what was changed and when, (4) determining if governance continuity can be verified, (5) deciding whether Genesis Re-Anchoring is required. Non-optional when audit integrity is compromised.
**Lives in:** `docs/operations/PROJECT_AI_BCDR_PLAN.md:Section 7.3`

---

### Governance Observability

**Engineering Equivalent:** Governance decision telemetry / observability collector
**Actual Function:** `GovernanceObservation` records a single governance decision observation; `GovernanceObservabilityCollector` aggregates up to `_MAX_OBSERVATIONS = 10,000` observations for analysis. Provides metrics on governance decision rates, denial rates, and escalation patterns.
**Lives in:** `src/app/core/governance_observability.py:23`

---

### Non-repudiation

**Engineering Equivalent:** Cryptographic proof of event occurrence / undeniable evidence
**Actual Function:** Cryptographic guarantee that an event occurred and cannot be denied or backdated. Achieved via DigiCert TSA RFC 3161 timestamps on audit log entries. TSA timestamps are legally binding proof of when governance decisions were made. Essential for proving governance continuity after recovery.
**Lives in:** `src/app/governance/acceptance_ledger.py`, DigiCert TSA

---

### Retention policy

**Engineering Equivalent:** Data retention schedule / backup lifecycle rules
**Actual Function:** Defines how long each backup tier is retained: Auto-save (7 days or 20 saves), User-save (unlimited), Git history (infinite), Audit logs (7 years minimum per compliance). Balances storage costs against recovery needs and regulatory requirements.
**Lives in:** `docs/operations/PROJECT_AI_BCDR_PLAN.md:Section 4.2`

---

### TSA (Time Stamp Authority)

**Engineering Equivalent:** RFC 3161 cryptographic timestamping service
**Actual Function:** DigiCert RFC 3161 Time Stamp Authority providing legally binding, non-repudiable timestamps for audit log entries. Proves events occurred at specific times and cannot be backdated. Critical for governance continuity verification — TSA timestamps prove acceptance ledger integrity after recovery. Used when `CRYPTO_AVAILABLE` flag is set.
**Lives in:** `src/app/governance/acceptance_ledger.py`, `src/app/core/time_trust.py`, DigiCert

---

## 14. Thirsty-Lang Keywords

All keywords use a water metaphor. This table maps every keyword to its computational meaning.

| Thirsty-Lang Keyword | Engineering Equivalent | Description |
| --- | --- | --- |
| `thirst` | `if` / guard condition | The system "thirsts" for a condition; execution enters the block only when the condition is satisfied |
| `drink` | `let` / `var` binding | Data is "drunk into existence" — variable declaration and assignment |
| `pour` | Output / side-effect | Data "pours" to the outside world — write to output or external system |
| `sip` | Input read | Read from user input or environment |
| `glass` | `function` / `def` | A contained vessel holding computation — function definition |
| `fountain` | `class` | Blueprint for a living container — class definition |
| `reservoir` | Mutable data store / `var` | Named holding area for mutable data under pressure |
| `well` | Immutable / read-only store | Deep but stable — `const` or read-only binding |
| `refill` | `for` loop | The loop "refills" until exhausted |
| `hydrated` | `else` branch | The alternative path when the `thirst` condition is not met |
| `parched` | Error / failure state | The system is "parched" and cannot continue — error or exception |
| `quenched` | Success state / `Some(value)` | Satisfied, success, or unwrapped optional |
| `flood` | Bulk mutation | Rewrites many values at once — batch write |
| `drip` | Incremental update | Small controlled mutation — single field update |
| `evaporate` | Destructure / unwrap optional | The value disappears safely — optional unwrapping or destructuring |
| `condense` | Aggregate from parts | Inverse of evaporate — build a value from components |
| `shield` | Security container / guarded block | Everything inside is subject to security enforcement |
| `sanitize` | Input validation | Clean and validate incoming data before use |
| `armor` | Immutability marker | Mark state as immutable post-write |
| `morph` | Dynamic code transformation | Adapt or obfuscate code under attack |
| `detect` | Threat detection block | Watch for and identify attack patterns |
| `defend` | Reactive defense posture | Apply a security response in reaction to a detected threat |
| `cascade glass` | `async` function | Asynchronous function (T.O.G. dialect) — backed by `ThreadPoolExecutor` |
| `spillage` | Exception / error handler | Error handling block in T.O.G. dialect |
| `cleanup` | `finally` block | Cleanup handler in T.O.G. dialect |
| `shadow` | Shadow-plane keyword | Marks a block or operation as executing in the read-only simulation plane |

---

*This glossary covers all names found in `src/`, `governance/`, `src/thirstys_waterfall/`, `src/utf/`, `.github/`, and `docs/` as of 2026-05-19. When in doubt, the source file listed in "Lives in" is authoritative.*
