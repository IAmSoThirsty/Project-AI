# Enhanced Existential Proof System (EPS)

**Advanced Formal Verification & Theorem Proving for Sovereign Governance**

---

## Overview

The Enhanced Existential Proof System (EPS) extends the base EPS with state-of-the-art formal verification capabilities, integrating automated theorem proving, SMT solving, invariant discovery, and continuous verification into a unified framework.

### Key Features

1. **🔍 Automated Theorem Proving**
   - Integration with Coq, Isabelle, and Lean theorem provers
   - Formal verification of constitutional properties
   - Proof certificate generation

2. **⚡ SMT Solver Integration (Z3)**
   - Constraint solving and satisfiability checking
   - Property verification with counterexample generation
   - Mathematical and logical property verification

3. **🔬 Invariant Discovery Engine**
   - Automatic discovery of system invariants from execution traces
   - Range, relationship, and temporal invariant detection
   - Confidence scoring and verification

4. **🔄 Continuous Verification**
   - Real-time monitoring of critical system properties
   - Automated periodic verification checks
   - Failure tracking and alerting

5. **📜 Proof Artifact Generation**
   - Human-readable proof certificates
   - Comprehensive verification reports
   - Audit trail for all verifications

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         Enhanced Existential Proof System (EPS)             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Base EPS    │  │ SMT Solver   │  │  Theorem     │      │
│  │  (Violations)│  │   (Z3)       │  │  Provers     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │               │
│         └─────────────────┼──────────────────┘               │
│                           │                                  │
│         ┌─────────────────┴──────────────────┐               │
│         │    Verification Orchestrator       │               │
│         └─────────────────┬──────────────────┘               │
│                           │                                  │
│  ┌────────────────────────┼────────────────────────────┐    │
│  │                        │                            │    │
│  │  ┌─────────────────────▼────┐  ┌──────────────────▼┐    │
│  │  │ Invariant Discovery      │  │  Continuous       │    │
│  │  │ Engine                   │  │  Verifier         │    │
│  │  └──────────────────────────┘  └───────────────────┘    │
│  │                                                          │
│  └──────────────────────────────────────────────────────────┘
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Proof Artifact Generator                    │   │
│  │  (Human-Readable Certificates & Reports)             │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites

```bash
# Python 3.10+ required
python --version

# Install base dependencies
pip install -r requirements.txt

# Install Z3 SMT Solver
pip install z3-solver
```

### Optional: Theorem Provers

For full functionality, install one or more theorem provers:

**Coq:**
```bash
# Ubuntu/Debian
sudo apt-get install coq

# macOS
brew install coq

# Windows
# Download from https://coq.inria.fr/
```

**Isabelle:**
```bash
# Download from https://isabelle.in.tum.de/
# Follow installation instructions for your OS
```

**Lean:**
```bash
# Install via elan (recommended)
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# Or via package manager
# Ubuntu/Debian
sudo apt-get install lean

# macOS
brew install lean
```

---

## Quick Start

### Basic Usage

```python
from governance.existential_proof_enhanced import EnhancedExistentialProof

# Initialize Enhanced EPS
eps = EnhancedExistentialProof(
    data_dir="governance/sovereign_data",
    enable_z3=True,
    enable_continuous=True,
)

print("Enhanced EPS initialized!")
print(f"Z3 Available: {eps.smt_solver is not None}")
print(f"Theorem Provers: {list(eps.theorem_provers.keys())}")
```

### Verify Properties with Z3

```python
from z3 import Int, Real, And, Implies

# Define variables
entropy = Real("entropy")
min_entropy = 0.1
max_entropy = 1.0

# Define property: entropy must be in valid range
property_formula = And(
    entropy >= min_entropy,
    entropy <= max_entropy
)

# Verify the property
proof = eps.verify_property_with_z3(
    property_name="Entropy Bounds",
    property_formula=property_formula,
)

print(f"Verification Status: {proof.status.value}")
print(proof.to_human_readable())
```

### Discover Invariants from Traces

```python
# Collect execution traces
traces = []
for i in range(100):
    traces.append({
        "timestamp": 1000.0 + i,
        "counter": i,
        "entropy": 0.5 + (i * 0.001),
        "user_count": 10 + i,
    })

# Discover invariants
invariants = eps.discover_invariants_from_traces(traces)

for inv in invariants:
    print(f"Discovered: {inv.description}")
    print(f"  Formula: {inv.formula}")
    print(f"  Confidence: {inv.confidence:.2f}")
    print(f"  Verified: {inv.verified}")
```

### Continuous Verification

```python
import asyncio

# Add continuous verification tasks
eps.continuous_verifier.add_verification_task(
    property_name="Four Laws Compliance",
    property_formula="asimov_laws == true",
    check_interval_seconds=60.0,
)

eps.continuous_verifier.add_verification_task(
    property_name="Entropy Lower Bound",
    property_formula="entropy > 0.1",
    check_interval_seconds=30.0,
)

# Start continuous verification (in background)
asyncio.create_task(
    eps.continuous_verifier.run_continuous_verification()
)
```

### Theorem Prover Integration

```python
from governance.existential_proof_enhanced import TheoremProver

# Coq proof script
coq_proof = """
Theorem add_comm : forall n m : nat,
  n + m = m + n.
Proof.
  intros n m.
  induction n as [| n' IHn'].
  - simpl. rewrite <- plus_n_O. reflexivity.
  - simpl. rewrite IHn'. rewrite plus_n_Sm. reflexivity.
Qed.
"""

# Verify with Coq
if TheoremProver.COQ in eps.theorem_provers:
    proof = eps.verify_property_with_prover(
        prover=TheoremProver.COQ,
        proof_script=coq_proof,
        timeout_seconds=30,
    )
    print(f"Coq Verification: {proof.status.value}")
```

---

## Components

### 1. SMT Constraint Solver (Z3)

The SMT solver provides powerful constraint solving capabilities:

**Features:**
- Satisfiability checking (SAT/UNSAT/UNKNOWN)
- Counterexample generation
- Support for integers, reals, booleans, arrays, and more
- Quantifier support (ForAll, Exists)

**Example:**

```python
from z3 import Int, And, Or, Not

x = Int("x")
y = Int("y")

# Property: x + y > 10 when x > 5 and y > 5
property_formula = And(x > 5, y > 5, x + y > 10)

proof = eps.verify_property_with_z3(
    property_name="Sum Property",
    property_formula=property_formula,
)
```

### 2. Theorem Prover Interface

Integrates with external theorem provers for formal verification:

**Supported Provers:**
- **Coq**: Proof assistant with dependent types
- **Isabelle**: Higher-order logic theorem prover
- **Lean**: Modern proof assistant with mathlib

**Example:**

```python
# Lean proof
lean_proof = """
theorem example : ∀ n : Nat, n + 0 = n := by
  intro n
  rfl
"""

proof = eps.verify_property_with_prover(
    prover=TheoremProver.LEAN,
    proof_script=lean_proof,
)
```

### 3. Invariant Discovery Engine

Automatically discovers system invariants from execution traces:

**Discovery Types:**

1. **Range Invariants**: Value bounds (e.g., `x > 0`, `0 <= y <= 100`)
2. **Relationship Invariants**: Variable relationships (e.g., `x + y == z`)
3. **Temporal Invariants**: Time-based properties (e.g., monotonicity)

**Categories:**
- Safety: "Nothing bad happens"
- Liveness: "Something good eventually happens"
- Temporal: Time-based properties
- Functional: Functional correctness
- Security: Security properties
- Resource: Resource bounds

**Example:**

```python
# Traces with monotonic counter
traces = [
    {"counter": i, "total": i * 2}
    for i in range(50)
]

invariants = eps.discover_invariants_from_traces(traces)

# Output:
# - [temporal] counter is monotonically increasing
# - [safety] counter is always positive
# - [functional] total always equals counter * 2
```

### 4. Continuous Verifier

Provides real-time monitoring and verification:

**Features:**
- Configurable check intervals
- Automatic failure tracking
- Task enable/disable controls
- Verification history

**Example:**

```python
# Add task
task_id = eps.continuous_verifier.add_verification_task(
    property_name="Hash Chain Integrity",
    property_formula="hash_chain_valid == true",
    check_interval_seconds=60.0,
)

# Check status
status = eps.continuous_verifier.get_task_status(task_id)
print(f"Last check: {status['last_check']}")
print(f"Last status: {status['last_status']}")
print(f"Failures: {status['failure_count']}")
```

### 5. Proof Artifact Generator

Generates human-readable proof certificates and comprehensive reports:

**ProofArtifact Fields:**
- `proof_id`: Unique identifier
- `timestamp`: When verified
- `prover`: Which prover used
- `property_name`: Property name
- `property_description`: Property details
- `status`: Verification result
- `proof_steps`: Step-by-step proof
- `verification_time_ms`: Time taken
- `assumptions`: Assumptions made
- `lemmas_used`: Lemmas applied
- `z3_model`: Counterexample (if any)

**Example:**

```python
# Generate proof for violation
violation = eps.detect_invariant_violation(
    invariant_type=InvariantType.ENTROPY_BOUNDS,
    ledger_state=current_state,
    current_value=0.05,
    expected_value={"min": 0.1, "max": 1.0},
)

if violation:
    proof = eps.generate_violation_proof(violation)
    print(proof.to_human_readable())
    # Saves to proof_artifacts.jsonl
```

---

## API Reference

### EnhancedExistentialProof

Main class extending base EPS functionality.

#### Constructor

```python
EnhancedExistentialProof(
    data_dir: Path | str = "governance/sovereign_data",
    enable_z3: bool = True,
    enable_continuous: bool = True,
)
```

#### Methods

**verify_property_with_z3**
```python
def verify_property_with_z3(
    self,
    property_name: str,
    property_formula,  # Z3 formula
    assumptions: list = None,
) -> ProofArtifact
```

**verify_property_with_prover**
```python
def verify_property_with_prover(
    self,
    prover: TheoremProver,
    proof_script: str,
    timeout_seconds: int = 30,
) -> ProofArtifact
```

**discover_invariants_from_traces**
```python
def discover_invariants_from_traces(
    self,
    traces: list[dict[str, Any]],
) -> list[DiscoveredInvariant]
```

**start_continuous_verification**
```python
def start_continuous_verification(
    self,
    properties: list[tuple[str, str]],
    check_interval_seconds: float = 60.0,
)
```

**generate_violation_proof**
```python
def generate_violation_proof(
    self,
    violation: InvariantViolation,
) -> ProofArtifact
```

**generate_comprehensive_report**
```python
def generate_comprehensive_report(
    self
) -> dict[str, Any]
```

---

## Data Structures

### ProofArtifact

```python
@dataclass
class ProofArtifact:
    proof_id: str
    timestamp: float
    prover: TheoremProver
    property_name: str
    property_description: str
    status: ProofStatus
    proof_steps: list[str]
    verification_time_ms: float
    assumptions: list[str]
    lemmas_used: list[str]
    z3_model: Optional[dict[str, Any]]
    raw_output: str
```

### DiscoveredInvariant

```python
@dataclass
class DiscoveredInvariant:
    invariant_id: str
    category: InvariantCategory
    description: str
    formula: str
    confidence: float  # 0.0 to 1.0
    supporting_traces: int
    counterexamples: int
    discovered_at: float
    verified: bool
    verification_proof: Optional[ProofArtifact]
```

### ContinuousVerificationTask

```python
@dataclass
class ContinuousVerificationTask:
    task_id: str
    property_name: str
    property_formula: str
    check_interval_seconds: float
    prover: TheoremProver
    enabled: bool
    last_check: Optional[float]
    last_status: Optional[ProofStatus]
    failure_count: int
```

---

## Enums

### TheoremProver

```python
class TheoremProver(str, Enum):
    COQ = "coq"
    ISABELLE = "isabelle"
    LEAN = "lean"
    Z3 = "z3"
```

### ProofStatus

```python
class ProofStatus(str, Enum):
    VERIFIED = "verified"
    FAILED = "failed"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"
    PENDING = "pending"
```

### InvariantCategory

```python
class InvariantCategory(str, Enum):
    SAFETY = "safety"
    LIVENESS = "liveness"
    TEMPORAL = "temporal"
    FUNCTIONAL = "functional"
    SECURITY = "security"
    RESOURCE = "resource"
```

---

## Examples

See `governance/examples/enhanced_eps_examples.py` for comprehensive examples:

```bash
# Run all examples
python -m governance.examples.enhanced_eps_examples

# Example outputs:
# - Z3 property verification with counterexamples
# - Invariant discovery from traces
# - Continuous verification setup
# - Theorem prover integration
# - Proof artifact generation
# - Complete integration workflow
```

---

## Integration with Base EPS

The Enhanced EPS seamlessly integrates with the base EPS:

```python
from governance.existential_proof import InvariantType, ViolationSeverity
from governance.existential_proof_enhanced import EnhancedExistentialProof

# Initialize
eps = EnhancedExistentialProof()

# Use base EPS features
violation = eps.detect_invariant_violation(
    invariant_type=InvariantType.HASH_CHAIN,
    ledger_state={"prev_hash": "abc123"},
    current_value="xyz789",
    expected_value="def456",
)

# Enhanced: Generate formal proof of violation
if violation:
    proof = eps.generate_violation_proof(violation)
    print(proof.to_human_readable())
```

---

## Storage

All verification artifacts are stored in JSONL format:

```
governance/sovereign_data/
├── invariant_violations.jsonl      # Base EPS violations
├── proof_artifacts.jsonl           # Generated proofs
├── discovered_invariants.jsonl     # Discovered invariants
└── external_verifiers.json         # External verifier keys
```

**Loading Data:**

```python
# Load proof artifacts
proofs = eps.load_proof_artifacts()

# Load discovered invariants
invariants = eps.load_discovered_invariants()

# Load violations (from base EPS)
violations = eps.load_violations()
```

---

## Performance Considerations

### Z3 Solver

- **Fast**: Most properties verify in <10ms
- **Scalable**: Handles complex formulas with thousands of constraints
- **Timeout**: Configure timeout for unbounded problems

### Theorem Provers

- **Variable**: Verification time depends on proof complexity
- **Timeout**: Default 30s, configurable per proof
- **Parallel**: Run multiple provers in parallel

### Invariant Discovery

- **Trace Buffer**: Keep in-memory for performance
- **Batch Processing**: Process traces in batches
- **Confidence Threshold**: Filter low-confidence invariants

### Continuous Verification

- **Interval**: Adjust check intervals based on criticality
- **Background**: Runs asynchronously without blocking
- **Resource**: Minimal overhead for typical workloads

---

## Security Considerations

1. **Proof Integrity**
   - All proofs are cryptographically hashed
   - Stored in append-only JSONL files
   - Tamper-evident ledger integration

2. **External Verifiers**
   - Ed25519 signature verification
   - Public key infrastructure required
   - Dual-channel validation (internal + external)

3. **Theorem Prover Isolation**
   - Provers run in separate processes
   - Timeout enforcement prevents DoS
   - Sandboxing recommended for untrusted proofs

4. **SMT Solver Safety**
   - Z3 is memory-safe (C++ with Python bindings)
   - No unsafe operations in formula construction
   - Result validation before accepting

---

## Troubleshooting

### Z3 Not Available

```
Error: Z3 is not available
Solution: pip install z3-solver
```

### Theorem Prover Not Found

```
Error: Theorem prover 'coq' not available
Solution: Install Coq from https://coq.inria.fr/
Verify: coqc --version
```

### Continuous Verification Not Starting

```python
# Ensure continuous verification is enabled
eps = EnhancedExistentialProof(enable_continuous=True)

# Start the verification loop
asyncio.run(eps.continuous_verifier.run_continuous_verification())
```

### Low Invariant Discovery

```
Issue: Few invariants discovered
Solution:
- Collect more traces (minimum 10, recommended 50+)
- Ensure trace diversity (different states)
- Lower confidence threshold
```

---

## Roadmap

### Planned Features

- [ ] GPU-accelerated SMT solving
- [ ] Machine learning-based invariant discovery
- [ ] Integration with more theorem provers (F*, Dafny)
- [ ] Distributed verification for large systems
- [ ] Proof compression and optimization
- [ ] Interactive proof debugging

### Future Enhancements

- Property-based testing integration
- Fuzzing-guided invariant discovery
- Proof repair and suggestion
- Natural language proof generation
- Blockchain anchoring of proofs

---

## Contributing

Contributions are welcome! Areas of interest:

1. Additional theorem prover integrations
2. Improved invariant discovery algorithms
3. Performance optimizations
4. Documentation and examples
5. Test coverage

---

## References

### Z3 Theorem Prover
- **Paper**: "Z3: An Efficient SMT Solver" (TACAS 2008)
- **Docs**: https://microsoft.github.io/z3guide/

### Coq
- **Website**: https://coq.inria.fr/
- **Book**: Software Foundations (Pierce et al.)

### Isabelle
- **Website**: https://isabelle.in.tum.de/
- **Tutorial**: "Concrete Semantics with Isabelle/HOL"

### Lean
- **Website**: https://leanprover.github.io/
- **Book**: "Theorem Proving in Lean 4"

### Invariant Discovery
- **Daikon**: Dynamic invariant detection (Ernst et al., 2007)
- **ICE Learning**: Learning invariants from examples

---

## License

Part of the Sovereign Governance Substrate project.

See main repository LICENSE for details.

---

## Contact & Support

For questions, issues, or contributions:

- **Issues**: Open an issue in the repository
- **Discussions**: Use GitHub Discussions
- **Email**: Contact the Sovereign Governance team

---

**Enhanced EPS**: Formal verification meets sovereign governance. 🚀
