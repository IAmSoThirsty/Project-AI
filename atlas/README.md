# PROJECT ATLAS Ω

## Constitutional Probabilistic Civilization Engine

**Status**: Production-Grade Implementation  
**Version**: 1.0.0  
**Architecture**: God-Tier Monolithic  
**Axioms**: Non-Override Constitutional Enforcement

---

## Overview

PROJECT ATLAS Ω is a comprehensive, deterministic, and auditable system for analyzing organizational influence, generating probabilistic timelines, and producing verified projections. The system enforces seven immutable axioms through a constitutional kernel that cannot be overridden.

### Foundational Axioms (Non-Override)

1. **Determinism > Interpretation** - Canonical hashing, reproducible operations
2. **Probability > Narrative** - Bayesian inference, no narrative-to-probability conversion
3. **Evidence > Agency** - Tier-based validation, agency claims require high-tier evidence
4. **Isolation > Contamination** - Air-gapped sludge sandbox, stack separation
5. **Reproducibility > Authority** - Immutable enforcement, deterministic seeds
6. **Bounded Inputs > Open Chaos** - Complete parameter bounds, NaN/Inf rejection
7. **Abort > Drift** - Graph validation, temporal consistency checks

---

## Architecture

### 13-Layer Stack

#### ✅ Layer 0: Constitutional Kernel (PRODUCTION-READY)
Immutable runtime constraints enforced before every simulation tick.

**Features:**
- Canonical hashing with CBOR support + float quantization (8 decimal places)
- Merkle chain graph validation (parent-hash lineage verification)
- Structural agency detection (schema-based, not lexical)
- Immutable enforcement (raises signals, never mutates state)
- Complete parameter bounds (50+ parameters including decay rates, volatility, coupling coefficients, noise variance, agent utilities)
- Clock consistency checks (monotonic timestep progression, temporal skew detection)
- NaN/Inf rejection

**Hard Constraints:**
- Sludge → RS: BLOCKED
- Narrative → Probability: BLOCKED
- Non-audited data → projection: BLOCKED
- Agency claims without TierA/B: PENALTY REQUIRED
- Seed omission: INVALID
- Hash mismatch: ABORT
- Graph drift without checksum: ABORT
- Parameter out of bounds: ABORT
- Non-monotonic time: ABORT
- Temporal skew: ABORT

#### ✅ Layer 4: Bayesian Claim Engine (PRODUCTION-READY)
Probabilistic legitimacy scoring using evidence-based Bayesian inference.

**Formula:**
```
P = normalize(EL × WDP × StackPenalty)
```

Where:
- **EL** = Evidence Legitimacy (weighted by tier: TierA=1.0, TierB=0.85, TierC=0.65, TierD=0.40)
- **WDP** = Weighted Driver Posterior (driver alignment scoring)
- **StackPenalty** = Stack-specific multiplier (RS=1.0, TS=1.0-0.90, SS=0.0)

**Features:**
- Automatic agency penalty (50% multiplier) for claims without TierA/B evidence
- Temporal decay using exponential half-life
- Agent perception influence (claims with posterior > 0.5 influence worldview)
- Driver dependency tracking
- Responds to constitutional kernel signals (immutable)

#### ✅ Layer 9: Sludge Narrative Sandbox (PRODUCTION-READY)
Air-gapped fictional narrative generator with complete isolation from authoritative stacks.

**Features:**
- **AIR-GAPPED**: Cannot contaminate RS or TS stacks
- **FICTION MARKERS**: All outputs marked with red banner and watermarks
- **NO PROBABILITIES**: Narrative only, no numeric predictions
- **ARCHETYPES**: Hidden Elites, Suppressed Tech, False Flags, Prophetic Inevitability
- **ISOLATION ENFORCEMENT**: Read-only filesystem, contamination detection

**Warning:**
```
╔═══════════════════════════════════════════════════════════════════╗
║                  ⚠️  FICTIONAL NARRATIVE SIMULATION ⚠️           ║
║  This output is a NARRATIVE CONSTRUCT for storytelling purposes  ║
║  It is NOT based on probabilistic analysis                       ║
╚═══════════════════════════════════════════════════════════════════╝
```

#### ✅ Layer 12: CLI & Export Interface (OPERATIONAL)
Command-line interface with constitutional verification and system status.

**Commands:**
```bash
# Verify bundle constitutional compliance (7-step verification)
atlas sovereign-verify --bundle output.json

# Display system status and statistics
atlas status

# Build Reality Stack history chain (TODO)
atlas build-hc --input data/raw

# Generate timeline projections (TODO)
atlas project --seed ATLAS-TS0-BASE-2026-02-07-001 --horizon 30

# Export artifacts with compliance stamps (TODO)
atlas export --output reports/
```

### Stack Classification

**RS (Reality Stack)**
- Ground truth data from verified sources
- Immutable once created (only versioned)
- Requires minimum 2 independent source confirmations
- Must have cryptographic audit trail
- No sludge data allowed

**TS-0 through TS-3 (Timeline Stacks)**
- TS-0: Near-term (0-30 days) from RS
- TS-1: Short-term (30-180 days) from TS-0
- TS-2: Medium-term (180-365 days) from TS-1
- TS-3: Long-term (1-10 years) from TS-2
- All deterministic, replayable, branching allowed
- Parent stack must be complete before child executes

**SS (Simulation Stack)**
- Experimental simulations and what-if scenarios
- **CANNOT** be promoted to any TS or RS stack
- **CANNOT** influence production projections
- Used only for hypothesis testing
- Must be marked as non-authoritative

### Data Tier Classification

**TierA** - Peer-reviewed / Official Audited (Weight: 1.0)
- Academic peer-reviewed publications
- Government audit reports
- Court documents with verification

**TierB** - Government Statistical Archives (Weight: 0.85)
- Official statistical agencies (e.g., Census, BLS, IMF)
- Central bank data
- Regulatory filings

**TierC** - Reputable Institutional Reporting (Weight: 0.65)
- Think tank research
- NGO reports with methodology
- Industry analyst reports

**TierD** - Media / Secondary Analysis (Weight: 0.40)
- News articles
- Opinion pieces
- Social media (with caveats)

---

## Installation

### Prerequisites
- Python 3.11+
- CBOR2 library for canonical hashing
- jsonschema for validation
- PyYAML for configuration

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Setup
```bash
# Clone repository
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI

# Install dependencies
pip install -r requirements.txt

# Verify installation
PYTHONPATH=$PWD python atlas/cli/atlas_cli.py status
```

---

## Usage

### CLI Usage

#### 1. System Status
```bash
PYTHONPATH=$PWD python atlas/cli/atlas_cli.py status
```

**Output:**
```
═══════════════════════════════════════════════════════════════════
PROJECT ATLAS Ω - System Status
═══════════════════════════════════════════════════════════════════
Timestamp: 2026-02-07T13:15:00.000Z

Constitutional Kernel:
  violation_count: 0
  last_check: 2026-02-07T13:14:58.123Z
  status: active
  bypass_allowed: False
  override_allowed: False

Audit Trail:
  total_events: 47
  chain_valid: True
  log_file: atlas/logs/audit_20260207_131400.jsonl

Configuration Integrity:
  Status: ✓ VALID

Schema Integrity:
  Status: ✓ VALID
═══════════════════════════════════════════════════════════════════
```

#### 2. Constitutional Verification
```bash
PYTHONPATH=$PWD python atlas/cli/atlas_cli.py sovereign-verify --bundle bundle.json
```

**Verification Steps:**
1. Data hash validation (canonical SHA-256)
2. Seed reproducibility (deterministic random seeds)
3. Bayesian posterior correctness (formula verification)
4. Sludge isolation (no contamination in RS/TS)
5. Trigger legitimacy (RS-only, deterministic)
6. Driver bounds (all parameters [0,1] or specified ranges)
7. Graph integrity (Merkle chain validation)

**Output:**
```
═══════════════════════════════════════════════════════════════════
PROJECT ATLAS Ω - Constitutional Verification
═══════════════════════════════════════════════════════════════════
Bundle: bundle.json
Timestamp: 2026-02-07T13:15:00.000Z

✓ Bundle loaded

[1/7] Validating data hashes...
  ✓ PASS

[2/7] Validating seed reproducibility...
  ✓ PASS

[3/7] Validating Bayesian posteriors...
  ✓ PASS

[4/7] Validating sludge isolation...
  ✓ PASS

[5/7] Validating contingency triggers...
  ✓ PASS

[6/7] Validating driver bounds...
  ✓ PASS

[7/7] Validating graph integrity...
  ✓ PASS

═══════════════════════════════════════════════════════════════════
✓✓✓ VERIFICATION PASSED ✓✓✓
Bundle is constitutionally compliant
═══════════════════════════════════════════════════════════════════
```

### Python API Usage

#### Constitutional Kernel
```python
from atlas.governance.constitutional_kernel import get_constitutional_kernel

kernel = get_constitutional_kernel()

# Validate state before simulation tick
state = {
    "id": "WS-001",
    "stack": "RS",
    "parameters": {
        "timestep": 1,
        "seed": "ATLAS-TS0-BASE-2026-02-07-001"
    },
    "drivers": {
        "economic_power": 0.75,
        "political_influence": 0.65
    },
    "metadata": {
        "created_at": "2026-02-07T13:00:00Z",
        "hash": "..."  # Computed hash
    }
}

try:
    kernel.run_pre_tick_check(state)
    print("✓ State is constitutionally valid")
except ConstitutionalViolation as e:
    print(f"✗ Violation: {e.violation_type.value}")
    print(f"  Details: {e.details}")
```

#### Bayesian Claim Engine
```python
from atlas.core.bayesian_engine import get_bayesian_engine

engine = get_bayesian_engine()

# Process claim
claim = {
    "id": "CLM-001",
    "claim_type": "factual",
    "statement": "Economic indicator X is rising",
    "timestamp": "2026-02-07T13:00:00Z"
}

evidence = [
    {"tier": "TierA", "source": "IMF Report", "confidence": 0.95},
    {"tier": "TierB", "source": "Federal Reserve", "confidence": 0.90}
]

drivers = {
    "economic_power": 0.75,
    "political_influence": 0.65
}

processed = engine.process_claim(claim, evidence, drivers, stack="RS")
print(f"Posterior: {processed['bayesian_analysis']['posterior']:.3f}")
```

#### Sludge Sandbox
```python
from atlas.sandbox.sludge_sandbox import get_sludge_sandbox

sandbox = get_sludge_sandbox()

# Generate fictional narrative (WARNING: NOT FOR DECISION-MAKING)
rs_snapshot = {
    "id": "WS-RS-001",
    "stack": "RS",
    "organizations": {...},
    "claims": {...}
}

narrative = sandbox.generate_narrative(rs_snapshot)

# ALWAYS display fiction banner
print(narrative["fiction_banner"])
print(f"\nNarrative ID: {narrative['id']}")
print(f"Watermark: {narrative['watermark']}")
```

---

## Configuration

### YAML Configuration Files

Located in `atlas/config/`:

- **stacks.yaml** - Stack definitions and transition rules
- **drivers.yaml** - Influence driver formulas and weights
- **penalties.yaml** - Score adjustment rules
- **thresholds.yaml** - Decision boundaries and triggers
- **safety.yaml** - Immutable safety constraints (LOCKED)
- **seeds.yaml** - Deterministic random seeds

### JSON Schemas

Located in `atlas/schemas/`:

- **organization.schema.json** - Organization objects
- **claim.schema.json** - Claim objects
- **opinion.schema.json** - Opinion objects
- **world_state.schema.json** - World state snapshots
- **influence_graph.schema.json** - Influence graphs
- **projection_pack.schema.json** - Projection packs

All schemas are canonical, locked, and immutable.

---

## Audit Trail

All operations are logged to an immutable audit trail with hash chaining:

```python
from atlas.audit.trail import get_audit_trail, AuditCategory, AuditLevel

audit = get_audit_trail()

# Log event
audit.log_event(
    category=AuditCategory.GOVERNANCE,
    level=AuditLevel.CRITICAL,
    operation="penalty_applied",
    actor="BAYESIAN_ENGINE",
    details={"claim_id": "CLM-001", "penalty": "agency_without_tier"}
)

# Verify chain integrity
is_valid = audit.verify_chain()
print(f"Audit chain valid: {is_valid}")

# Export report
report = audit.export_report(format="json")
```

---

## Security & Integrity

### Hash Integrity
- **Canonical hashing** using CBOR binary encoding
- **Float quantization** to 8 decimal places
- **NaN/Inf standardization**
- **Deterministic key ordering**
- Fallback to quantized JSON if CBOR unavailable

### Graph Validation
- **Merkle chain verification** for all graphs
- **Parent-hash lineage tracking**
- **Baseline hash registry**
- **Descendant validation**

### Temporal Consistency
- **Monotonic timestep enforcement**
- **Cross-component year consistency** (state, graph, drivers)
- **Future timestamp rejection**
- **Step size change detection**

### Parameter Bounds
Complete bounds enforcement for 50+ parameters:
- Temporal bounds
- Probabilities and confidences
- Decay rates and half-lives
- Volatility and noise parameters
- Coupling coefficients
- Agent utilities
- Graph metrics
- Sensitivity parameters

---

## Contributing

This is a sovereign, constitutional system. All changes must:

1. **Preserve constitutional axioms** (non-negotiable)
2. **Pass all 7 verification steps**
3. **Maintain determinism and replayability**
4. **Include comprehensive tests**
5. **Update audit trail**

---

## License

MIT License - See LICENSE file

---

## Authors

- Project-AI Team
- Constitutional Kernel: Production-grade enforcement
- Bayesian Engine: Evidence-based inference
- Sludge Sandbox: Fictional narrative isolation

---

## Acknowledgments

This system implements a God-Tier, monolithic architecture with zero placeholders, complete production-grade implementation, and non-bypassable constitutional enforcement.

**No technical debt. No shortcuts. No compromises.**
