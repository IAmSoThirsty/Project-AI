# PSIA Package — Implementation Contract Extraction

**Date:** 2026-05-23  
**Branch:** psia/contract-extraction-20260523  
**Phase:** Contract Extraction (no implementation code produced)  
**Test files read:** 18 of 18  
**Constraint:** Do not implement. Do not edit conftest.py. Do not remove from collect_ignore.

---

## 1. Test File Inventory

All 18 PSIA test files currently isolated in `tests/conftest.py`:

| File | Isolated Via | Primary Module |
|------|-------------|---------------|
| `test_psia_bootstrap.py` | `collect_ignore_glob` | `psia.bootstrap.*` |
| `test_psia_canonical.py` | `collect_ignore_glob` | `psia.canonical.*` |
| `test_psia_schemas.py` | `collect_ignore_glob` | `psia.schemas.*`, `psia.events`, `psia.planes` |
| `test_psia_threat_model.py` | `collect_ignore_glob` | `psia.threat_model` |
| `test_psia_gate.py` | `collect_ignore_glob` | `psia.gate.*` |
| `test_psia_invariants.py` | `collect_ignore_glob` | `psia.invariants` |
| `test_psia_concurrency.py` | `collect_ignore_glob` | `psia.concurrency` |
| `test_psia_liveness.py` | `collect_ignore_glob` | `psia.liveness` |
| `test_psia_observability.py` | `collect_ignore_glob` | `psia.observability.*` |
| `test_psia_waterfall.py` | `collect_ignore_glob` | `psia.waterfall.*` |
| `test_psia_integration.py` | `collect_ignore_glob` | Full stack |
| `test_psia_comprehensive.py` | `collect_ignore_glob` | All modules |
| `test_bft_deployed.py` | `_PSIA_TESTS` | `psia.gate.quorum_engine` |
| `test_ed25519_crypto.py` | `_PSIA_TESTS` | `psia.crypto.ed25519_provider` |
| `test_formal_properties.py` | `_PSIA_TESTS` | `psia.canonical.capability_authority` |
| `test_governance_server.py` | `_PSIA_TESTS` | `psia.server.governance_server` |
| `test_rfc3161.py` | `_PSIA_TESTS` | `psia.crypto.rfc3161_provider` |
| `test_shadow_operational_semantics.py` | `_PSIA_TESTS` | `psia.shadow.operational_semantics` |

---

## 2. Complete Import Map

Every import path required across all 18 test files:

```
psia/
  __init__.py
  concurrency.py
  events.py
  invariants.py
  liveness.py
  planes.py
  threat_model.py
  bootstrap/
    __init__.py
    genesis.py
    readiness.py
    safe_halt.py
  canonical/
    __init__.py
    capability_authority.py
    commit_coordinator.py
    ledger.py
  crypto/
    __init__.py
    ed25519_provider.py
    rfc3161_provider.py
  gate/
    __init__.py
    capability_head.py
    quorum_engine.py
  observability/
    __init__.py
    autoimmune_dampener.py
    failure_detector.py
  schemas/
    __init__.py
    capability.py
    identity.py
    request.py
    shadow_report.py
    (additional: intent.py, policy.py, audit.py, did.py, deployment.py,
     governance.py, waterfall.py — required by test_psia_schemas.py)
  server/
    __init__.py
    governance_server.py
  shadow/
    __init__.py
    operational_semantics.py
  waterfall/
    __init__.py
    engine.py
    stage_0_structural.py
    stage_1_signature.py
    stage_2_behavioral.py
    stage_3_shadow.py
    stage_4_gate.py
    stage_5_commit.py
    stage_6_memory.py
```

Exact imports confirmed from test source:

```python
# test_psia_bootstrap.py
from psia.bootstrap.genesis import GenesisCoordinator, GenesisStatus
from psia.bootstrap.readiness import NodeStatus, ReadinessGate
from psia.bootstrap.safe_halt import HaltReason, SafeHaltController, SafeHaltError

# test_psia_canonical.py
from psia.canonical.capability_authority import CapabilityAuthority
from psia.canonical.commit_coordinator import CanonicalStore, CommitCoordinator, CommitStatus
from psia.canonical.ledger import DurableLedger, ExecutionRecord
from psia.schemas.capability import CapabilityScope, ScopeConstraints

# test_psia_schemas.py
from psia.schemas.capability import CapabilityToken, TokenState
from psia.schemas.intent import IntentRecord
from psia.schemas.policy import TARLPolicy, TARLRule
from psia.schemas.audit import AuditRecord
from psia.schemas.did import DIDDocument, VerificationMethod
from psia.schemas.deployment import DeploymentProfile
from psia.schemas.governance import GovernanceVote, VoteVerdict
from psia.schemas.waterfall import WaterfallResult
from psia.invariants import InvariantViolation
from psia.planes import Plane, PlaneCapability
from psia.events import CapabilityLifecycleEvent, GovernanceEvent, SystemEvent

# test_psia_threat_model.py
from psia.threat_model import (
    ThreatModel, ThreatClass, ResilientCountermeasure,
    RESILIENCE_PROFILES, CollusionDetector
)

# test_psia_gate.py
from psia.gate.capability_head import CapabilityHead
from psia.gate.quorum_engine import QuorumEngine, ProductionQuorumEngine
from psia.schemas.capability import CapabilityToken, TokenState
from psia.schemas.intent import IntentRecord
from psia.schemas.policy import TARLPolicy, TARLRule

# test_psia_invariants.py
from psia.invariants import (
    INV_ROOT_1, INV_ROOT_2, INV_ROOT_3, INV_ROOT_4, INV_ROOT_5,
    INV_ROOT_6, INV_ROOT_7, INV_ROOT_8, INV_ROOT_9,
    ROOT_INVARIANTS,
    InvariantScope, InvariantSeverity, InvariantEnforcement, Invariant
)

# test_psia_concurrency.py
from psia.concurrency import (
    CommitOutcome, CommitResult, LinearizableCanonicalStore,
    MutationIntent, StateSnapshot, VersionedValue,
)

# test_psia_liveness.py
from psia.liveness import (
    HeadHealth, HeadLivenessMonitor, HeadStatus,
    PipelineDeadlockDetector, TimeoutConfig,
)

# test_psia_observability.py
from psia.observability.autoimmune_dampener import AutoimmuneDampener
from psia.observability.failure_detector import CircuitState, FailureDetector

# test_psia_waterfall.py
from psia.events import EventBus, EventType
from psia.schemas.identity import Signature
from psia.schemas.request import Intent, RequestContext, RequestEnvelope, RequestTimestamps
from psia.schemas.shadow_report import DeterminismProof, ShadowReport, ShadowResults
from psia.waterfall.engine import StageDecision, StageResult, WaterfallEngine, WaterfallResult, WaterfallStage
from psia.waterfall.stage_0_structural import StructuralStage
from psia.waterfall.stage_1_signature import SignatureStage, ThreatFingerprint, ThreatFingerprintStore
from psia.waterfall.stage_2_behavioral import BaselineProfileStore, BehavioralStage
from psia.waterfall.stage_3_shadow import PassthroughSimulator, ShadowStage
from psia.waterfall.stage_4_gate import GateStage, QuorumEngine
from psia.waterfall.stage_5_commit import CommitStage, InMemoryCanonicalStore
from psia.waterfall.stage_6_memory import InMemoryLedger, MemoryStage

# test_psia_integration.py
from psia.bootstrap.genesis import GenesisCoordinator, GenesisStatus
from psia.bootstrap.readiness import NodeStatus, ReadinessGate
from psia.bootstrap.safe_halt import HaltReason, SafeHaltController, SafeHaltError
from psia.canonical.capability_authority import CapabilityAuthority
from psia.canonical.commit_coordinator import CanonicalStore, CommitCoordinator
from psia.canonical.ledger import DurableLedger, ExecutionRecord
from psia.invariants import ROOT_INVARIANTS
from psia.observability.autoimmune_dampener import AutoimmuneDampener
from psia.observability.failure_detector import CircuitState, FailureDetector
from psia.schemas.capability import CapabilityScope
from psia.schemas.identity import Signature
from psia.schemas.request import Intent, RequestContext, RequestEnvelope, RequestTimestamps

# test_ed25519_crypto.py
from psia.crypto.ed25519_provider import Ed25519Provider, Ed25519KeyPair, KeyStore

# test_rfc3161.py
from psia.crypto.ed25519_provider import Ed25519Provider
from psia.crypto.rfc3161_provider import LocalTSA, TimeStampToken

# test_shadow_operational_semantics.py
from psia.shadow.operational_semantics import (
    DeterminismClass, DeterminismOracle, ExecutionTrace, SealedContext,
)

# test_governance_server.py
from psia.server.governance_server import create_app

# test_formal_properties.py
from psia.canonical.capability_authority import CapabilityAuthority
from psia.canonical.ledger import DurableLedger
# also imports from psia.canonical.commit_coordinator (CanonicalStore)
# requires: hypothesis (skipif not installed)

# test_bft_deployed.py
from psia.gate.quorum_engine import ProductionQuorumEngine
from psia.threat_model import RESILIENCE_PROFILES
```

---

## 3. Module-by-Module API Contracts

### 3.1 `psia/bootstrap/genesis.py`

**Exports:** `GenesisCoordinator`, `GenesisStatus`, `GenesisAnchor`, `BuildAttestation`, `GenesisResult`

```python
class GenesisStatus(Enum):
    NOT_STARTED = "not_started"
    COMPLETED = "completed"

class GenesisAnchor:
    node_id: str          # equals coordinator's node_id
    anchor_id: str        # stable across idempotent re-executions
    key_ids: list[str]    # one per component; len == len(components)
    
    def compute_hash(self) -> str: ...  # SHA-256 hex, 64 chars, deterministic

class BuildAttestation:
    binary_hash: str          # from execute(binary_hash=...)
    config_hash: str          # from execute(config_hash=...)
    invariant_hash: str       # SHA-256 of invariant_definitions arg, non-empty

class GenesisResult:
    status: GenesisStatus     # COMPLETED on success
    keys_generated: list[str] # component names for which keys were generated
    anchor: GenesisAnchor
    attestation: BuildAttestation | None  # None when no hashes passed

class GenesisCoordinator:
    DEFAULT_COMPONENTS: ClassVar[list[str]]  # 7 component names

    def __init__(
        self,
        node_id: str = "psia-node-01",
        components: list[str] | None = None,
    ) -> None: ...

    @property
    def status(self) -> GenesisStatus: ...      # NOT_STARTED initially
    @property
    def is_completed(self) -> bool: ...         # True after execute()
    @property
    def keys(self) -> dict[str, Any]: ...       # component_name → key pair
    @property
    def anchor(self) -> GenesisAnchor | None: ...

    def execute(
        self,
        binary_hash: str | None = None,
        config_hash: str | None = None,
        invariant_definitions: list | None = None,
    ) -> GenesisResult: ...
    # Idempotent: repeated calls return same anchor.anchor_id
    # Result.anchor.node_id == self.node_id (or "psia-node-01" default)
```

**Behavior:**
- `DEFAULT_COMPONENTS` contains exactly 7 entries
- `execute()` is idempotent: two calls on same instance → same `anchor.anchor_id`
- `status` transitions `NOT_STARTED → COMPLETED` after first `execute()`
- `result.anchor.key_ids` has one entry per component
- `result.anchor.node_id` reflects the coordinator's `node_id` arg

---

### 3.2 `psia/bootstrap/readiness.py`

**Exports:** `ReadinessGate`, `NodeStatus`, `ReadinessReport`, `CheckResult`

```python
class NodeStatus(Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    FAILED = "failed"

class CheckResult:
    passed: bool
    message: str

class ReadinessReport:
    status: NodeStatus
    all_passed: bool           # True only if NodeStatus.OPERATIONAL
    checks: list[CheckResult]
    critical_failures: int
    warnings: int

class ReadinessGate:
    def __init__(self, strict: bool = False) -> None: ...

    @property
    def is_operational(self) -> bool: ...   # True after evaluate() if OPERATIONAL
    @property
    def last_report(self) -> ReadinessReport | None: ...  # None before evaluate()

    def register_check(
        self,
        name: str,
        fn: Callable[[], tuple[bool, str]],
        critical: bool = True,
    ) -> None: ...
    # If fn raises, counts as failed check; message includes exception str

    def register_genesis_check(self, coordinator: Any) -> None: ...
    # Checks coordinator.is_completed; uses coordinator.status in message on fail

    def register_ledger_check(self, ledger: Any) -> None: ...
    # Checks ledger.sealed_block_count and ledger.verify_chain()

    def evaluate(self) -> ReadinessReport: ...
```

**Status logic:**
- All checks pass → `OPERATIONAL`
- Any non-critical check fails → `DEGRADED` (increments `warnings`)
- Any critical check fails → `FAILED` (increments `critical_failures`)
- Exception in any check → `FAILED`
- No registered checks → `OPERATIONAL` (all_passed=True)

---

### 3.3 `psia/bootstrap/safe_halt.py`

**Exports:** `SafeHaltController`, `HaltReason`, `HaltEvent`, `SafeHaltError`

```python
class HaltReason(Enum):
    INVARIANT_VIOLATION = "invariant_violation"
    SECURITY_INCIDENT = "security_incident"
    CHAIN_CORRUPTION = "chain_corruption"
    UNRECOVERABLE_ERROR = "unrecoverable_error"
    ADMINISTRATIVE = "administrative"

class HaltEvent:
    reason: HaltReason
    details: str

class SafeHaltError(Exception):
    # str(e) must contain "SAFE-HALT"
    pass

class SafeHaltController:
    def __init__(self) -> None: ...

    @property
    def is_halted(self) -> bool: ...     # False initially
    @property
    def halt_count(self) -> int: ...     # 0 initially; increments on each trigger_halt()

    def trigger_halt(
        self, reason: HaltReason, details: str = ""
    ) -> HaltEvent: ...
    # is_halted=True after call; halt_count += 1 (NOT idempotent on count)
    # Returns HaltEvent with event.reason == reason, event.details contains details

    def check_write_allowed(self) -> None: ...
    # Raises SafeHaltError("SAFE-HALT: ...") when is_halted
    # No-op when not halted

    def check_read_allowed(self) -> None: ...
    # Never raises regardless of halt state

    def reset(self, authorized_by: str = "") -> bool: ...
    # Returns True if was halted (and resets to not-halted)
    # Returns False if was not halted
    # After reset: is_halted=False, check_write_allowed() no longer raises
```

---

### 3.4 `psia/canonical/commit_coordinator.py`

**Exports:** `CanonicalStore`, `CommitCoordinator`, `CommitStatus`, `CommitResult`

```python
class VersionedValue:
    value: Any
    version: int          # 1-based, increments on each put()

class CommitStatus(Enum):
    COMMITTED = "committed"
    FAILED = "failed"

class CommitResult:
    status: CommitStatus
    keys_mutated: list[str]
    diff_hash: str         # SHA-256 hex; deterministic for same request_id+mutations+versions
    version_after: dict[str, int]
    error: str

class CanonicalStore:
    def __init__(self) -> None: ...

    @property
    def key_count(self) -> int: ...

    def put(
        self, key: str, value: Any, expected_version: int | None = None
    ) -> VersionedValue: ...
    # Raises ValueError("Optimistic concurrency conflict") if expected_version != current

    def get(self, key: str) -> VersionedValue | None: ...
    def get_version(self, key: str) -> int: ...
    def delete(self, key: str, expected_version: int | None = None) -> bool: ...
    # Returns True if deleted, False if key not found
    # Raises ValueError("Optimistic concurrency conflict") if version mismatch

    def history(self, key: str) -> list[VersionedValue]: ...
    def snapshot(self) -> dict[str, VersionedValue]: ...

class CommitCoordinator:
    def __init__(
        self,
        store: CanonicalStore | None = None,  # creates own if None
        require_cerberus_allow: bool = False,
        emit_events: Callable[[CommitResult], None] | None = None,
    ) -> None: ...

    @property
    def store(self) -> CanonicalStore: ...
    @property
    def wal_entries(self) -> list: ...   # grows by len(mutations) per commit

    def commit(
        self,
        request_id: str,
        mutations: dict[str, Any],
        actor: str = "",
        expected_versions: dict[str, int] | None = None,
        cerberus_decision: Any = None,
    ) -> CommitResult: ...
    # Version conflict → status=FAILED, error contains "Version conflict"
    # cerberus_decision.is_allowed=False → status=FAILED, error contains "does not allow"
    # cerberus_decision.commit_policy.allowed=False → status=FAILED, error contains "CommitPolicy"
```

---

### 3.5 `psia/canonical/ledger.py`

**Exports:** `DurableLedger`, `ExecutionRecord`, `LedgerBlock`

```python
class ExecutionRecord:  # Pydantic model
    record_id: str
    request_id: str
    actor: str
    action: str
    resource: str
    decision: str
    commit_id: str | None = None
    diff_hash: str | None = None

class LedgerBlock:
    block_index: int
    record_count: int
    merkle_root: str          # 64-char SHA-256 hex
    previous_block_hash: str  # DurableLedger.GENESIS_HASH for block 0
    anchor_hash: str | None   # set by anchor_block()

class DurableLedger:
    GENESIS_HASH: ClassVar[str] = "0" * 64

    def __init__(
        self,
        block_size: int = 100,
        on_block_sealed: Callable[[LedgerBlock], None] | None = None,
    ) -> None: ...

    @property
    def total_records(self) -> int: ...
    @property
    def sealed_block_count(self) -> int: ...
    @property
    def pending_record_count(self) -> int: ...

    def append(self, record: ExecutionRecord) -> str: ...
    # Returns hash of record
    # Raises ValueError("INV-ROOT-9: ...") on duplicate record_id (append-only)
    # Auto-seals block when pending_record_count reaches block_size

    def get_record(self, record_id: str) -> ExecutionRecord | None: ...
    def get_records_by_request(self, request_id: str) -> list[ExecutionRecord]: ...
    def get_block(self, block_index: int) -> LedgerBlock | None: ...

    def force_seal(self) -> LedgerBlock | None: ...
    # Returns None if no pending records; otherwise seals and returns block

    def anchor_block(self, block_index: int, anchor_hash: str) -> bool: ...
    # Returns True if block exists, False if not (block 99 on empty ledger → False)

    def verify_chain(self) -> bool: ...
    # Verifies each block's previous_block_hash matches prior block's hash

    def _compute_merkle_root(self, records: list[ExecutionRecord]) -> str: ...
    # Called by formal_properties test directly; SHA-256 Merkle root of records
```

---

### 3.6 `psia/canonical/capability_authority.py`

**Exports:** `CapabilityAuthority`

```python
class CapabilityAuthority:
    def __init__(
        self,
        max_scope_actions: int = 10,
        default_ttl_hours: float = 24.0,
        allow_delegation: bool = False,
        max_delegation_depth: int = 0,
    ) -> None: ...

    @property
    def authority_did(self) -> str: ...
    @property
    def issued_count(self) -> int: ...
    @property
    def active_count(self) -> int: ...
    @property
    def audit_log(self) -> list: ...     # entries have .event_type ("issued"/"revoked")
    @property
    def revocation_list(self) -> list: ... # entries have .reason

    def issue(
        self,
        subject: str,
        scopes: list[CapabilityScope],
    ) -> CapabilityToken: ...
    # Raises ValueError("INV-ROOT-5: ...") if subject == authority_did
    # Raises ValueError("INV-ROOT-6: ...") if any scope.actions > max_scope_actions

    def revoke(self, token_id: str, reason: str = "") -> bool: ...
    # Returns False if not found; True if found (even if already revoked — idempotent)

    def rotate(self, token_id: str) -> CapabilityToken | None: ...
    # Revokes old, issues new with same subject+scopes; returns None if not found

    def is_valid(self, token_id: str) -> bool: ...
    # False if revoked or expired or not found

    def is_revoked(self, token_id: str) -> bool: ...
    def get_token(self, token_id: str) -> CapabilityToken | None: ...

    def verify_token_signature(self, token: CapabilityToken) -> bool: ...
    # Used in test_formal_properties — Ed25519 signature verification
```

**`CapabilityToken`** (must match `psia.schemas.capability.CapabilityToken`):
```python
class CapabilityToken:
    token_id: str
    issuer: str          # = authority.authority_did
    subject: str
    scopes: list[CapabilityScope]
    delegation: DelegationPolicy
    # DelegationPolicy: is_delegable: bool, max_depth: int
```

**`CapabilityScope`** (`psia/schemas/capability.py`):
```python
class CapabilityScope:
    actions: list[str]
    resource: str
    constraints: ScopeConstraints

class ScopeConstraints:
    pass  # empty base, may have optional fields
```

---

### 3.7 `psia/concurrency.py`

**Exports:** `LinearizableCanonicalStore`, `StateSnapshot`, `MutationIntent`, `VersionedValue`, `CommitResult`, `CommitOutcome`

```python
class VersionedValue:
    version: int    # 1-based, monotonically increasing
    value: Any

class StateSnapshot:
    def read(self, key: str) -> Any | None: ...
    # Frozen at snapshot creation time; unaffected by subsequent mutations

class MutationIntent:
    request_id: str
    # Encapsulates snapshot + read_set + write_dict at prepare time

class CommitOutcome(Enum):
    # at minimum: COMMITTED, ABORTED, CONFLICT

class CommitResult:
    outcome: CommitOutcome
    # ...

class LinearizableCanonicalStore:
    def __init__(self) -> None: ...

    @property
    def global_version(self) -> int: ...  # 0 initially; increments per commit

    def create_snapshot(self) -> StateSnapshot: ...
    def read(self, key: str) -> VersionedValue | None: ...

    def prepare_mutation(
        self,
        request_id: str,
        snapshot: StateSnapshot,
        read_set: set,
        write_dict: dict,
    ) -> MutationIntent: ...

    def commit(self, mutation: MutationIntent) -> CommitResult: ...
    # Single-writer lock (linearizable)
    # OCC: validates read_set at commit time; conflict → abort
    # Disjoint write-sets never conflict
```

**OCC semantics:**
- `prepare_mutation` captures the snapshot version for read-set keys
- `commit` re-validates: if any read-set key has been mutated since snapshot → `CommitResult` with conflict outcome
- Retry is caller's responsibility; exhausted retries → abort (fail-closed)

---

### 3.8 `psia/invariants.py`

**Exports:** `INV_ROOT_1`–`INV_ROOT_9`, `ROOT_INVARIANTS`, `InvariantScope`, `InvariantSeverity`, `InvariantEnforcement`, `Invariant`, `InvariantViolation`

```python
class InvariantScope(str, Enum):
    IMMUTABLE = "immutable"

class InvariantSeverity(str, Enum):
    FATAL = "fatal"

class InvariantEnforcement(str, Enum):
    HARD_DENY = "hard_deny"

class Invariant(BaseModel):  # Frozen Pydantic model
    model_config = ConfigDict(frozen=True)
    
    name: str
    description: str
    scope: InvariantScope      # always IMMUTABLE
    severity: InvariantSeverity   # always FATAL
    enforcement: InvariantEnforcement  # always HARD_DENY
    version: int               # always 1
    language: str              # always "first_order_logic"

class InvariantViolation(Exception):
    pass

# Module-level constants — each is a frozen Invariant instance:
INV_ROOT_1: Invariant   # all names unique
INV_ROOT_2: Invariant
INV_ROOT_3: Invariant
INV_ROOT_4: Invariant
INV_ROOT_5: Invariant   # authority cannot self-issue capability
INV_ROOT_6: Invariant   # scope action count limit
INV_ROOT_7: Invariant   # monotonic severity (quorum)
INV_ROOT_8: Invariant   # duplicate DID registration rejected
INV_ROOT_9: Invariant   # ledger append-only, no overwrites

ROOT_INVARIANTS: list[Invariant]  # = [INV_ROOT_1, ..., INV_ROOT_9]  # len == 9
```

**Constraints (all tested):**
- All 9 invariants: `scope=IMMUTABLE`, `severity=FATAL`, `enforcement=HARD_DENY`, `version=1`, `language="first_order_logic"`
- Mutation of any frozen `Invariant` raises `pydantic.ValidationError`
- All 9 names are unique
- `ROOT_INVARIANTS` has length exactly 9

---

### 3.9 `psia/liveness.py`

**Exports:** `TimeoutConfig`, `HeadHealth`, `HeadStatus`, `HeadLivenessMonitor`, `PipelineDeadlockDetector`

```python
class TimeoutConfig:
    def __init__(
        self,
        head_evaluation_timeout: float = 5.0,
        stage_timeout: float = 10.0,
        pipeline_timeout: float = 60.0,
        queue_timeout: float = 30.0,
        retry_timeout: float = 5.0,
        heartbeat_interval: float = 1.0,
        max_consecutive_timeouts: int = 3,
    ) -> None: ...
    # Progress bound: queue_timeout + (7 × stage_timeout) + retry_timeout ≤ 115s
    # With defaults: 30 + 70 + 5 = 105 ≤ 115 ✓

class HeadStatus(Enum):
    ALIVE = "alive"
    DEGRADED = "degraded"
    FAILED = "failed"

class HeadHealth:
    def __init__(self, head_name: str) -> None: ...

    @property
    def status(self) -> HeadStatus: ...         # ALIVE initially
    @property
    def consecutive_timeouts(self) -> int: ...  # 0 initially
    @property
    def total_evaluations(self) -> int: ...     # 0 initially
    @property
    def avg_latency_ms(self) -> float: ...

    def record_success(self, latency_ms: float) -> None: ...
    # Resets consecutive_timeouts to 0; status → ALIVE; total_evaluations += 1

    def record_timeout(self, max_consecutive: int) -> None: ...
    # consecutive_timeouts += 1
    # status → DEGRADED if 0 < consecutive < max_consecutive
    # status → FAILED if consecutive_timeouts >= max_consecutive

class HeadLivenessMonitor:
    def __init__(self, config: TimeoutConfig | None = None) -> None: ...

    def evaluate_with_timeout(
        self,
        head_name: str,
        evaluate_fn: Callable[[], Any],
        default_on_timeout: Any,
    ) -> tuple[Any, bool]: ...
    # Fast fn → (result, False)
    # Exceeds config.head_evaluation_timeout → (default_on_timeout, True)

class PipelineDeadlockDetector:
    # Detects stage-level and pipeline-level timeout conditions
    pass
```

---

### 3.10 `psia/observability/autoimmune_dampener.py`

**Exports:** `AutoimmuneDampener`

```python
class AutoimmuneDampener:
    def __init__(
        self,
        target_fp_rate: float = 0.1,
        cooldown_decisions: int = 10,
        adjustment_step: float = 0.1,
        min_sensitivity: float = 0.1,
    ) -> None: ...

    def record_decision(self, rule_id: str, denied: bool) -> None: ...
    def record_false_positive(self, rule_id: str) -> None: ...
    def get_sensitivity(self, rule_id: str) -> float: ...
    # Starts at 1.0; decreases when fp_rate > target_fp_rate
    # Never below min_sensitivity

    def should_apply_rule(self, rule_id: str, threshold: float = 0.5) -> bool: ...
    # Returns False if sensitivity < threshold
```

**Behavior:**
- 6 decisions with 6 false positives on a rule → `sensitivity < 1.0`
- 10 decisions with only 1 false positive → `sensitivity >= 0.9` (rule preserved)
- Sensitivity never goes below `min_sensitivity`

---

### 3.11 `psia/observability/failure_detector.py`

**Exports:** `FailureDetector`, `CircuitState`

```python
class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class FailureDetector:
    def __init__(
        self,
        failure_threshold: float = 0.5,
        cascade_threshold: int = 2,
        on_cascade: Callable[[Any], None] | None = None,
    ) -> None: ...

    def register_component(self, component: str) -> None: ...
    def record_failure(self, component: str) -> None: ...
    # When failure rate on a component exceeds failure_threshold → circuit OPEN
    # When OPEN circuits count ≥ cascade_threshold → triggers on_cascade once

    def check_circuit(self, component: str) -> CircuitState: ...
```

**Cascade logic:**
- 3 failures on "canonical" → circuit OPEN (threshold=0.5 → 2+ failures trip it)
- Single component OPEN does NOT trigger cascade
- Two distinct components OPEN triggers `on_cascade` exactly once

---

### 3.12 `psia/crypto/ed25519_provider.py`

**Exports:** `Ed25519Provider`, `Ed25519KeyPair`, `KeyStore`

```python
class Ed25519KeyPair:
    key_id: str
    public_key_hex: str    # 64 chars (32 bytes)
    private_key_hex: str   # 64 chars (seed) or 128 chars (full private)
    algorithm: str         # "Ed25519"

class Ed25519Provider:
    @staticmethod
    def generate_keypair() -> Ed25519KeyPair: ...

    @staticmethod
    def sign(private_key_hex: str, message: bytes) -> str: ...
    # Returns 128-char hex (64 bytes, Ed25519 signature)

    @staticmethod
    def verify(public_key_hex: str, signature_hex: str, message: bytes) -> bool: ...
    # Wrong key → False; tampered message → False

class KeyStore:
    def __init__(self) -> None: ...

    def register(self, key_id: str, key_pair: Ed25519KeyPair) -> None: ...
    # Raises ValueError("already registered") on duplicate key_id

    def get(self, key_id: str) -> Ed25519KeyPair: ...
    # Raises KeyError("No key registered") on missing key_id
```

---

### 3.13 `psia/crypto/rfc3161_provider.py`

**Exports:** `LocalTSA`, `TimeStampToken`, `TimeStampResponse`

```python
class TimeStampToken:
    version: int                      # always 1
    policy_oid: str                   # "1.3.6.1.4.1.99999.1.1"
    hash_algorithm: str               # "SHA-256"
    message_imprint: str              # 64-char hex (SHA-256 of timestamped data)
    serial_number: int                # monotonically increasing, ≥1
    gen_time: str | datetime          # timestamp of token creation
    tsa_name: str
    signature: str                    # Ed25519 signature hex
    nonce: str                        # auto-generated or caller-supplied
    tsa_public_key: str               # 64-char Ed25519 public key hex

    def __init__(self, **kwargs) -> None: ...   # constructible from dict
    def to_dict(self) -> dict: ...
    # Required fields: version, message_imprint, hash_algorithm, signature,
    #                  tsa_public_key, serial_number, gen_time

class TimeStampResponse:
    status: int           # 0=granted, 1=rejection
    status_string: str    # "granted" or "rejection"
    token: TimeStampToken | None
    failure_info: str | None

class LocalTSA:
    def __init__(self, tsa_name: str = "PSIA-LocalTSA") -> None: ...

    @property
    def tsa_name(self) -> str: ...
    @property
    def public_key_hex(self) -> str: ...   # 64-char Ed25519 hex
    @property
    def serial_count(self) -> int: ...     # 0 initially; increments on successful request

    def request_timestamp(
        self,
        message_imprint: str,
        nonce: str | None = None,
    ) -> TimeStampResponse: ...
    # message_imprint must be exactly 64 chars → status=1, "rejection" otherwise
    # Nonce replay → status=1, failure_info contains "already used"
    # Auto-generates nonce if not supplied (non-None, non-empty)
    # Successful → status=0, "granted", token with serial_number ≥ 1
    # Thread-safe: concurrent calls produce unique serial_numbers

    def verify_timestamp(
        self,
        token: TimeStampToken,
        data_hash: str | None = None,
    ) -> bool: ...
    # Verifies Ed25519 signature on token
    # If data_hash supplied, also checks token.message_imprint == data_hash

    @staticmethod
    def verify_with_public_key(
        token: TimeStampToken, pub_hex: str
    ) -> bool: ...
    # Offline verification without TSA instance
    # Wrong public key → False
```

---

### 3.14 `psia/shadow/operational_semantics.py`

**Exports:** `SealedContext`, `ExecutionTrace`, `DeterminismClass`, `DeterminismOracle`

```python
class SealedContext:
    seed: int                    # derived from SHA-256(inputs_hash), > 0
    logical_clock_start: int     # always 0
    io_table: dict               # deterministic; same inputs → same io_table
    env: dict                    # always {} (no env vars, no filesystem, no network)

    @classmethod
    def from_inputs(cls, inputs_hash: str) -> SealedContext: ...
    # Same inputs_hash → identical (seed, logical_clock_start, io_table, env)
    # Different inputs_hash → different seed (Definition 7.2)
    # seed > 0 (never zero)

class TraceStep:
    step_id: int        # monotonic from 0
    operation: str
    result: Any

class ExecutionTrace:
    def __init__(self, trace_id: str, context_seed: int) -> None: ...

    @property
    def steps(self) -> list[TraceStep]: ...

    def add_step(self, operation: str, args: tuple, result: Any) -> None: ...
    # step_id assigned monotonically starting at 0

    def seal(self) -> str: ...
    # Returns SHA-256 hex string (64 chars)
    # Deterministic based on operations+results regardless of trace_id
    # Same operations+results (different trace_id) → same hash

class DeterminismClass(Enum):
    FULLY_DETERMINISTIC = "fully_deterministic"
    NON_DETERMINISTIC = "non_deterministic"
    EPSILON_DETERMINISTIC = "epsilon_deterministic"

class DeterminismOracle:
    def __init__(self) -> None: ...

    @property
    def verification_log(self) -> list: ...  # grows with each verify_determinism call

    def verify_determinism(
        self,
        program: Callable[[SealedContext, dict], ExecutionTrace],
        ctx: SealedContext,
        snapshot: dict,
    ) -> tuple[DeterminismClass, ExecutionTrace]: ...
    # Runs program twice with same ctx+snapshot
    # Compares seal() hashes; equal → FULLY_DETERMINISTIC
    # Different → NON_DETERMINISTIC or EPSILON_DETERMINISTIC
    # Records to verification_log on every call
```

---

### 3.15 `psia/waterfall/engine.py`

**Exports:** `WaterfallEngine`, `WaterfallResult`, `StageResult`, `StageDecision`, `WaterfallStage`

```python
class StageDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    QUARANTINE = "quarantine"
    ESCALATE = "escalate"

class StageResult:
    decision: StageDecision
    reasons: list[str]
    metadata: dict

class WaterfallResult:
    is_allowed: bool                        # True only if all 7 stages ALLOW
    stage_results: list[StageResult]        # len == 7
    aborted_at_stage: int | None            # stage index (0–6) where aborted; None if passed
    cerberus_decision: Any | None           # from stage 4's metadata["cerberus_decision"]

class WaterfallEngine:
    def __init__(
        self,
        structural_stage: StructuralStage,
        signature_stage: SignatureStage,
        behavioral_stage: BehavioralStage,
        shadow_stage: ShadowStage,
        gate_stage: GateStage,
        commit_stage: CommitStage,
        memory_stage: MemoryStage,
        event_bus: EventBus | None = None,
    ) -> None: ...

    def process(self, envelope: RequestEnvelope) -> WaterfallResult: ...
    # Emits events: WATERFALL_START, 7× STAGE_ENTER, 7× STAGE_EXIT, REQUEST_ALLOWED
    # total event_count ≥ 16 on a full-pass run
```

---

### 3.16 Waterfall Stage Contracts

**Stage 0 — `psia/waterfall/stage_0_structural.py`**
```python
class StructuralStage:
    def register_token(self, token_id: str, token_info: dict) -> None: ...
    # token_info keys: "expires_at" (ISO str), "nonce" (str)

    def evaluate(
        self, envelope: RequestEnvelope, prior_results: list
    ) -> StageResult: ...
    # Expired token → DENY, "expired" in reasons
    # Nonce replay (same envelope twice) → DENY, "replay" in reasons
    # Valid envelope → ALLOW
```

**Stage 1 — `psia/waterfall/stage_1_signature.py`**
```python
class ThreatFingerprint:
    fingerprint_id: str
    pattern_type: str      # e.g., "actor"
    pattern_value: str     # matched against envelope field
    severity: str          # "critical" → QUARANTINE; anything else → ESCALATE
    reason: str

class ThreatFingerprintStore:
    def add(self, fp: ThreatFingerprint) -> None: ...

class SignatureStage:
    def __init__(self, store: ThreatFingerprintStore | None = None) -> None: ...
    def evaluate(self, envelope, prior_results) -> StageResult: ...
    # No fingerprints → ALLOW
    # severity="critical" match → QUARANTINE
    # severity="med" match → ESCALATE
```

**Stage 2 — `psia/waterfall/stage_2_behavioral.py`**
```python
class BaselineProfileStore:
    def record_request(self, actor: str, action: str, resource: str) -> None: ...

class BehavioralStage:
    def __init__(
        self,
        store: BaselineProfileStore | None = None,
        escalation_threshold: float = 0.5,
    ) -> None: ...
    def evaluate(self, envelope, prior_results) -> StageResult: ...
    # First request (no history) → ALLOW
    # Novel resource+action after established baseline → ESCALATE or QUARANTINE
```

**Stage 3 — `psia/waterfall/stage_3_shadow.py`**
```python
class PassthroughSimulator:
    def simulate(self, request_id, action, resource, parameters) -> ShadowReport: ...
    # Returns low-divergence report (default safe path)

class ShadowStage:
    def __init__(
        self,
        simulator: Any | None = None,         # defaults to PassthroughSimulator
        divergence_threshold: float = 0.5,
    ) -> None: ...
    def evaluate(self, envelope, prior_results) -> StageResult: ...
    # result.metadata["shadow_report"] always present
    # divergence_score > divergence_threshold → ESCALATE or QUARANTINE
```

**Stage 4 — `psia/waterfall/stage_4_gate.py`**
```python
class QuorumEngine:  # waterfall-internal (NOT psia.gate.quorum_engine)
    def __init__(self, policy: str = "majority") -> None: ...
    # policy options: "majority", "unanimous"

class GateStage:
    def __init__(self, quorum_engine: QuorumEngine | None = None) -> None: ...
    def evaluate(self, envelope, prior_results) -> StageResult: ...
    # Invalid DID format → DENY
    # Valid envelope → ALLOW
    # result.metadata["cerberus_decision"] always present
```

**Stage 5 — `psia/waterfall/stage_5_commit.py`**
```python
class InMemoryCanonicalStore:
    pass

class CommitStage:
    def __init__(self, store: InMemoryCanonicalStore | None = None) -> None: ...
    def evaluate(self, envelope, prior_results) -> StageResult: ...
```

**Stage 6 — `psia/waterfall/stage_6_memory.py`**
```python
class InMemoryLedger:
    pass

class MemoryStage:
    def __init__(self, ledger: InMemoryLedger | None = None) -> None: ...
    def evaluate(self, envelope, prior_results) -> StageResult: ...
```

---

### 3.17 `psia/gate/quorum_engine.py`

**Exports:** `QuorumEngine`, `ProductionQuorumEngine`

```python
class QuorumEngine:
    def __init__(self, policy: TARLPolicy, heads: list, n_nodes: int = 4) -> None: ...
    def process(self, intent: IntentRecord) -> GovernanceVote: ...
    # Monotonic severity: DENY > QUARANTINE > ESCALATE > ALLOW (worst vote wins)
    # Any single DENY → final DENY regardless of policy
    # No matching TARL rule → DENY (fail-closed)

class ProductionQuorumEngine:
    def __init__(self, n_nodes: int = 4) -> None: ...
    # Includes default TARL policy; n=3 → BFT_READY; n≥4 → BFT_DEPLOYED
    # BFT model: f = (n-1)//3; f≥1 = BFT_DEPLOYED
```

**BFT deployment states:**
- `n=3`: `f = (3-1)//3 = 0` → `BFT_READY`
- `n=4`: `f = (4-1)//3 = 1` → `BFT_DEPLOYED`
- `n=7`: `f = (7-1)//3 = 2` → `BFT_DEPLOYED`

---

### 3.18 `psia/gate/capability_head.py`

**Exports:** `CapabilityHead`

Part of the three-head Cerberus system (`IdentityHead`, `CapabilityHead`, `InvariantHead`). Each head casts a vote; the `QuorumEngine` aggregates using monotonic severity. Signature to be inferred from test_psia_gate.py (not fully extracted here — gate tests verify all three heads individually and combined).

---

### 3.19 `psia/threat_model.py`

**Exports:** `ThreatModel`, `ThreatClass`, `ResilientCountermeasure`, `RESILIENCE_PROFILES`, `CollusionDetector`

```python
class ThreatClass(Enum):
    SYBIL = "sybil"
    ECLIPSE = "eclipse"
    REPLAY = "replay"
    BYZANTINE = "byzantine"
    INSIDER = "insider"

RESILIENCE_PROFILES: dict  # keyed by (policy_name, n_nodes) → profile dict
# RESILIENCE_PROFILES[("bft", 3)] → profile with status indicating BFT_READY
# RESILIENCE_PROFILES[("bft", 4)] → profile with status indicating BFT_DEPLOYED
# RESILIENCE_PROFILES[("bft", 7)] → profile with status indicating BFT_DEPLOYED

class CollusionDetector:
    def __init__(self, threshold: float = 0.7) -> None: ...
    def register_vote(self, voter_id: str, intent_hash: str, vote: Any) -> None: ...
    def detect_collusion(self) -> tuple[bool, dict]: ...
```

---

### 3.20 `psia/server/governance_server.py`

**Exports:** `create_app`

```python
def create_app() -> FastAPI: ...
```

**Endpoint contracts:**

`GET /health` → `200 OK`
```json
{
  "status": "governance-online",
  "tarl": "TARL-v1.0",
  "node_id": "project-ai-desktop-node",
  "boot_time": "<ISO timestamp>",
  "halted": false,
  "intents_processed": 0
}
```

`GET /tarl` → `200 OK`
```json
{
  "version": "TARL-v1.0",
  "rules": [/* ≥8 TARLRule objects */]
}
```
Critical action rules: `mutate`, `delete`, `deploy` must have `default == "deny"`.

`POST /intent` (body: intent payload) → `200 OK`
```json
{
  "message": "<string>",
  "governance": {
    "intent_hash": "<sha256 hex>",
    "tarl_version": "TARL-v1.0",
    "votes": [
      {"pillar": "Galahad", "decision": "<string>", ...},
      {"pillar": "Cerberus", "decision": "<string>", ...},
      {"pillar": "Codex Deus", "decision": "<string>", ...}
    ],
    "final_verdict": "<string>",
    "timestamp": "<ISO timestamp>"
  }
}
```

`GET /audit?limit=<int>` → `200 OK`
```json
{
  "tarl_version": "TARL-v1.0",
  "tarl_signature": "<string>",
  "records": [/* audit records */]
}
```

**Dependencies:** `fastapi`, `httpx` (or `requests`) for `TestClient`.

---

### 3.21 Schema Modules (`psia/schemas/`)

All schema types are **Pydantic models** with:
- `compute_hash() -> str` method returning 64-char SHA-256 hex (deterministic)
- Round-trip serialization via `model_dump()` + `Model(**d)` constructor

Modules confirmed to require independent files:

| Module | Key Exports |
|--------|-------------|
| `schemas/capability.py` | `CapabilityToken`, `TokenState`, `CapabilityScope`, `ScopeConstraints` |
| `schemas/identity.py` | `Signature(alg, kid, sig)` |
| `schemas/request.py` | `RequestEnvelope`, `Intent`, `RequestContext`, `RequestTimestamps` |
| `schemas/shadow_report.py` | `ShadowReport`, `DeterminismProof`, `ShadowResults` |
| `schemas/intent.py` | `IntentRecord` |
| `schemas/policy.py` | `TARLPolicy`, `TARLRule` |
| `schemas/audit.py` | `AuditRecord` |
| `schemas/did.py` | `DIDDocument`, `VerificationMethod` |
| `schemas/deployment.py` | `DeploymentProfile` |
| `schemas/governance.py` | `GovernanceVote`, `VoteVerdict` |
| `schemas/waterfall.py` | `WaterfallResult` (schema form; also in engine.py) |

`TokenState` enum: `ACTIVE`, `REVOKED`, `EXPIRED`

`RequestEnvelope` fields:
```python
class RequestEnvelope:
    request_id: str
    actor: str
    subject: str
    capability_token_id: str
    intent: Intent
    context: RequestContext
    timestamps: RequestTimestamps
    signature: Signature
```

`ShadowReport` fields:
```python
class ShadowReport:
    request_id: str
    shadow_job_id: str
    snapshot_id: str
    determinism: DeterminismProof
    results: ShadowResults
    timestamp: str
    signature: Signature

class DeterminismProof:
    seed: str
    replay_hash: str
    replay_verified: bool

class ShadowResults:
    divergence_score: float
```

---

### 3.22 `psia/events.py`

**Exports:** `EventBus`, `EventType`, `CapabilityLifecycleEvent`, `GovernanceEvent`, `SystemEvent`

```python
class EventType(Enum):
    # At minimum:
    WATERFALL_START = "waterfall_start"
    STAGE_ENTER = "stage_enter"
    STAGE_EXIT = "stage_exit"
    REQUEST_ALLOWED = "request_allowed"
    # + REQUEST_DENIED, REQUEST_QUARANTINED, etc.

class EventBus:
    @property
    def event_count(self) -> int: ...  # total events published since init

    def publish(self, event: Any) -> None: ...
    def subscribe(self, event_type: EventType, handler: Callable) -> None: ...
```

---

### 3.23 `psia/planes.py`

**Exports:** `Plane`, `PlaneCapability`

```python
class Plane(Enum):
    # Plane names (exact values unknown; inferred from paper architecture)
    # At minimum: BOOTSTRAP, CANONICAL, GATE, WATERFALL, OBSERVABILITY

class PlaneCapability:
    plane: Plane
    capability_name: str
    # + additional fields
```

---

## 4. Cryptographic and Governance Invariants

### 4.1 Ed25519 Signature Constraints

- Public key: 32 bytes, 64-char hex
- Signature: 64 bytes, 128-char hex
- Private key / seed: either 32 bytes (seed) or 64 bytes (full private) — use the `cryptography` library
- All `compute_hash()` calls use `hashlib.sha256(...).hexdigest()` → 64-char lowercase hex
- Signature covers the canonical serialization of the signed object (deterministic JSON or bytes)
- `verify_token_signature(token)` in `CapabilityAuthority` must verify the Ed25519 signature on the token's canonical form

### 4.2 Ledger Hash Chain

- Block 0: `previous_block_hash = DurableLedger.GENESIS_HASH = "0" * 64`
- Block N+1: `previous_block_hash = sha256(block_N_canonical_bytes)`
- `merkle_root = sha256(sha256(r1) + sha256(r2) + ...)` (or similar; test only checks 64-char hex)
- `verify_chain()` validates the full chain: each block's prev_hash matches prior block's hash

### 4.3 RFC 3161 TSA

- `policy_oid = "1.3.6.1.4.1.99999.1.1"` (non-standard OID for local TSA)
- Token signed with TSA's own Ed25519 key (generated at `LocalTSA()` init)
- `verify_with_public_key` uses offline public key — no TSA instance required
- Serial numbers strictly monotonic and thread-safe (use threading.Lock)
- Nonce replay tracked in a set per TSA instance lifetime

### 4.4 OCC / Linearizability

- `CanonicalStore.put()` raises `ValueError("Optimistic concurrency conflict")` on version mismatch
- `LinearizableCanonicalStore.commit()` uses a single-writer lock (threading.Lock)
- Version vectors per key: `version = 1` after first write, increments per write
- `global_version` counts total committed mutations

---

## 5. Byzantine Quorum and Governance Rules

### 5.1 BFT Model

| N nodes | f (Byzantine) | State |
|---------|--------------|-------|
| 3 | 0 | `BFT_READY` |
| 4 | 1 | `BFT_DEPLOYED` |
| 7 | 2 | `BFT_DEPLOYED` |

Formula: `f = (n - 1) // 3`. `f >= 1` → `BFT_DEPLOYED`. `f == 0` → `BFT_READY`.

### 5.2 Monotonic Severity (HARD RULE)

Severity order (worst wins): `DENY > QUARANTINE > ESCALATE > ALLOW`

Any single `DENY` vote from any head → final decision is `DENY`, regardless of other votes or policy.

### 5.3 Fail-Closed / Deny-by-Default

- No matching TARL rule → `DENY`
- Head evaluation timeout → `DENY` (deny-safe default)
- Waterfall stage abort → `DENY` (fail-closed)
- SAFE-HALT active → writes blocked (`SafeHaltError`), reads pass through

### 5.4 INV-ROOT-5 (Self-Issuance)

`CapabilityAuthority.issue(subject=authority.authority_did, ...)` must raise `ValueError("INV-ROOT-5: ...")`.

### 5.5 INV-ROOT-6 (Scope Limit)

`CapabilityAuthority.issue(scopes=[scope_with_too_many_actions], ...)` must raise `ValueError("INV-ROOT-6: ...")`.

### 5.6 INV-ROOT-7 (Monotonic Severity)

Enforced at the quorum engine level: the worst vote always propagates.

### 5.7 INV-ROOT-8 (DID Uniqueness)

Duplicate DID registration raises an error (exact type inferred from test_psia_gate.py).

### 5.8 INV-ROOT-9 (Ledger Append-Only)

`DurableLedger.append(record)` where `record.record_id` already exists → raises `ValueError("INV-ROOT-9: ...")`.

---

## 6. Recommended Implementation Order

### Phase P2A — Crypto and Invariants (foundation, no dependencies on other PSIA modules)

1. `psia/__init__.py`
2. `psia/crypto/ed25519_provider.py` — `Ed25519Provider`, `Ed25519KeyPair`, `KeyStore`
3. `psia/crypto/rfc3161_provider.py` — `LocalTSA`, `TimeStampToken`, `TimeStampResponse`
4. `psia/invariants.py` — 9 frozen invariants, `ROOT_INVARIANTS`
5. `psia/planes.py` — `Plane`, `PlaneCapability`
6. `psia/events.py` — `EventBus`, `EventType`, event classes

**Unblocks:** `test_ed25519_crypto.py`, `test_rfc3161.py`, `test_psia_invariants.py`

### Phase P2B — Schemas (depends on crypto)

7. `psia/schemas/capability.py`
8. `psia/schemas/identity.py`
9. `psia/schemas/request.py`
10. `psia/schemas/shadow_report.py`
11. `psia/schemas/intent.py`, `policy.py`, `audit.py`, `did.py`, `deployment.py`, `governance.py`, `waterfall.py`

**Unblocks:** `test_psia_schemas.py`

### Phase P2C — Bootstrap + Canonical (depends on crypto, schemas)

12. `psia/bootstrap/genesis.py`
13. `psia/bootstrap/readiness.py`
14. `psia/bootstrap/safe_halt.py`
15. `psia/canonical/ledger.py`
16. `psia/canonical/commit_coordinator.py`
17. `psia/canonical/capability_authority.py`

**Unblocks:** `test_psia_bootstrap.py`, `test_psia_canonical.py`

### Phase P2D — Concurrency + Liveness + Observability (depends on P2C)

18. `psia/concurrency.py`
19. `psia/liveness.py`
20. `psia/observability/autoimmune_dampener.py`
21. `psia/observability/failure_detector.py`
22. `psia/shadow/operational_semantics.py`

**Unblocks:** `test_psia_concurrency.py`, `test_psia_liveness.py`, `test_psia_observability.py`, `test_shadow_operational_semantics.py`

### Phase P2E — Threat Model + Gate + Waterfall (depends on all prior)

23. `psia/threat_model.py`
24. `psia/gate/capability_head.py`
25. `psia/gate/quorum_engine.py`
26. `psia/waterfall/engine.py`
27. `psia/waterfall/stage_0_structural.py` through `stage_6_memory.py`

**Unblocks:** `test_psia_threat_model.py`, `test_psia_gate.py`, `test_psia_waterfall.py`, `test_bft_deployed.py`

### Phase P2F — Server + Integration (depends on all prior)

28. `psia/server/governance_server.py`
29. Verify `test_psia_integration.py`, `test_psia_comprehensive.py`, `test_formal_properties.py`
30. Remove all PSIA entries from `tests/conftest.py` collect_ignore
31. Run `pytest tests/test_psia_*.py tests/test_bft_deployed.py tests/test_ed25519_crypto.py tests/test_formal_properties.py tests/test_governance_server.py tests/test_rfc3161.py tests/test_shadow_operational_semantics.py -v`

**Unblocks:** `test_governance_server.py`, `test_psia_integration.py`, `test_psia_comprehensive.py`

---

## 7. External Dependencies Required

| Library | Used By |
|---------|---------|
| `pydantic` | All schemas, `Invariant` (frozen model) |
| `cryptography` | `Ed25519Provider` (real Ed25519 signing/verification) |
| `fastapi` | `create_app()` in governance server |
| `httpx` or `starlette.testclient` | `TestClient` for governance server tests |
| `hypothesis` | `test_formal_properties.py` (skipif guard in place; graceful skip if absent) |
| `hashlib`, `json`, `threading` | Standard library — ledger, OCC, TSA thread-safety |

---

## 8. Risks — Where Test Coverage Could Underbuild the Architecture

### R1: Governance server is a thin FastAPI layer
The tests only verify HTTP response structure. The three Triumvirate pillars (Galahad, Cerberus, Codex Deus) voting on `/intent` must be real governance calls, not stub responses. If implemented as mock returns, the governance contract is satisfied on paper but the server provides no actual governance.

**Recommendation:** Wire the governance server to the real `WaterfallEngine` and `QuorumEngine`, not to canned response dictionaries.

### R2: Concurrency tests use in-memory state
`LinearizableCanonicalStore` tests verify OCC behavior, but there is no persistence layer. The tests do not require durability across restarts. If production PSIA needs durable canonical state, this must be added outside the test surface.

**Recommendation:** Note the in-memory limitation. Future phases should layer SQLite or file-backed persistence atop the canonical store.

### R3: Ledger block sealing uses in-memory block list
`DurableLedger` is verified to be append-only and produce correct Merkle roots. The tests do not verify JSONL or file-based persistence. TSA anchoring (`anchor_block`) is tested but there is no RFC 3161 timestamp integration in the ledger tests.

**Recommendation:** Implement `DurableLedger` with a `List[LedgerBlock]` in memory as the contract requires. A durable-ledger upgrade path is outside this test surface.

### R4: Ed25519 signature verification in `CapabilityAuthority`
`verify_token_signature(token)` is called in `test_formal_properties.py` via Hypothesis. The method must perform real Ed25519 signature verification. If the authority is implemented with a software key that signs at `issue()` time, the signature must be stored on the token and verified later.

**Recommendation:** Store `token.signature` as a hex string produced by `Ed25519Provider.sign(private_key_hex, canonical_bytes)` where `canonical_bytes` is a deterministic serialization of the token fields.

### R5: Waterfall stage 4 QuorumEngine vs psia.gate QuorumEngine
Two separate `QuorumEngine` classes exist: one in `psia.waterfall.stage_4_gate` (waterfall-internal, simpler policy strings like `"majority"/"unanimous"`) and one in `psia.gate.quorum_engine` (full TARL-based, BFT-aware, three-head). These are distinct classes in different modules. Do not merge or confuse them.

### R6: Shadow determinism oracle runs the program twice
`DeterminismOracle.verify_determinism` runs the provided program twice with identical inputs. For FULLY_DETERMINISTIC classification, the seal hashes must match. This means the oracle must actually invoke the program with the same sealed context both times, not sample it once and assume determinism.

### R7: SAFE-HALT is NOT a restart barrier — it is a write fence
`check_read_allowed()` never raises. The halt is a write-gate, not a crash. Resetting halt (`reset(authorized_by=...)`) immediately re-enables writes. No authorization cryptography is required by the tests — `authorized_by` is just a string.

### R8: TARL policy must include at least 8 rules with deny-defaults for critical actions
The `/tarl` endpoint test checks `len(rules) >= 8`. The actions `mutate`, `delete`, `deploy` must have `default == "deny"`. If fewer rules are defined, the test fails.

### R9: Serial number thread-safety in LocalTSA
20 concurrent threads each calling `request_timestamp()` must produce 20 unique serial numbers with no duplicates. This requires a `threading.Lock` around the serial counter increment.

---

## 9. Summary Statistics

| Category | Count |
|----------|-------|
| Test files isolated | 18 |
| Python modules to create | ~42 (including `__init__.py` files) |
| Exported classes | ~65+ |
| Exported enums | ~18+ |
| Exported exceptions | ~5 |
| External dependency installs | 3 new (`cryptography`, `fastapi`, `httpx`) |
| Pydantic models (frozen) | 9 invariants + all schema types |
| Ed25519 public key format | 64-char hex (32 bytes) |
| Ed25519 signature format | 128-char hex (64 bytes) |
| SHA-256 hash format | 64-char hex throughout |
| BFT threshold formula | `f = (n-1)//3` |
| Waterfall stages | 7 (0–6) |
| Cerberus heads | 3 (identity, capability, invariant) |
| Root invariants | 9 (INV_ROOT_1–9) |
| TARL minimum rules | 8 |

---

*End of contract extraction. No implementation code produced. No conftest.py changes made. All 18 test files read in full.*
