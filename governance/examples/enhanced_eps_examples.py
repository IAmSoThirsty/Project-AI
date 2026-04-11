"""
Enhanced EPS Examples - Comprehensive demonstrations of all features

This module provides complete examples for:
1. Z3 SMT Solving for property verification
2. Invariant Discovery from execution traces
3. Continuous Verification setup
4. Theorem Prover integration
5. Proof Artifact generation
"""

import asyncio
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

try:
    from z3 import Int, Real, Bool, And, Or, Not, Implies, ForAll
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False
    logger.warning("Z3 not available - some examples will be skipped")

from governance.existential_proof_enhanced import (
    EnhancedExistentialProof,
    TheoremProver,
    ProofStatus,
    InvariantCategory,
)

from governance.existential_proof import (
    InvariantType,
    ViolationSeverity,
)


def example_1_z3_property_verification():
    """
    Example 1: Z3 SMT Solver for Property Verification
    
    Demonstrates verifying mathematical and logical properties using Z3.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Z3 SMT SOLVER - PROPERTY VERIFICATION")
    print("=" * 80 + "\n")

    if not Z3_AVAILABLE:
        print("⚠️  Z3 not available. Install with: pip install z3-solver")
        return

    # Initialize Enhanced EPS
    eps = EnhancedExistentialProof(
        data_dir="governance/sovereign_data/examples",
        enable_z3=True,
        enable_continuous=False,
    )

    # Example 1.1: Verify arithmetic property
    print("1.1 Verifying arithmetic property: x + y == y + x (commutativity)")
    x = Int("x")
    y = Int("y")
    
    # Property: addition is commutative
    property_formula = (x + y == y + x)
    
    proof = eps.verify_property_with_z3(
        property_name="Addition Commutativity",
        property_formula=property_formula,
    )
    
    print(f"   Status: {proof.status.value}")
    print(f"   Verification time: {proof.verification_time_ms:.2f}ms")
    print()

    # Example 1.2: Verify safety property with assumptions
    print("1.2 Verifying safety property with constraints")
    entropy = Real("entropy")
    
    # Assumptions: entropy is bounded
    assumptions = [
        entropy >= 0.0,
        entropy <= 1.0,
    ]
    
    # Property: if entropy > 0.5, system is in safe state
    safety_property = Implies(entropy > 0.5, entropy > 0.0)
    
    proof = eps.verify_property_with_z3(
        property_name="Entropy Safety Bound",
        property_formula=safety_property,
        assumptions=assumptions,
    )
    
    print(f"   Status: {proof.status.value}")
    print(f"   Assumptions: {len(proof.assumptions)}")
    print()

    # Example 1.3: Verify invariant violation detection
    print("1.3 Detecting invariant violations with counterexamples")
    
    balance = Int("balance")
    withdrawal = Int("withdrawal")
    
    # Property that should fail: withdrawal can exceed balance
    invalid_property = (balance - withdrawal >= 0)
    
    proof = eps.verify_property_with_z3(
        property_name="Balance Invariant (Should Fail)",
        property_formula=invalid_property,
        assumptions=[balance >= 0, withdrawal >= 0],
    )
    
    print(f"   Status: {proof.status.value}")
    if proof.z3_model:
        print(f"   Counterexample found: {proof.z3_model}")
    print()

    # Generate human-readable proof
    print("1.4 Human-readable proof certificate:")
    print(proof.to_human_readable())


def example_2_invariant_discovery():
    """
    Example 2: Automatic Invariant Discovery from Traces
    
    Demonstrates discovering system invariants from execution traces.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: INVARIANT DISCOVERY FROM EXECUTION TRACES")
    print("=" * 80 + "\n")

    # Initialize Enhanced EPS
    eps = EnhancedExistentialProof(
        data_dir="governance/sovereign_data/examples",
        enable_z3=Z3_AVAILABLE,
        enable_continuous=False,
    )

    # Generate sample execution traces
    print("2.1 Generating sample execution traces...")
    traces = []
    
    # Simulate monotonically increasing counter
    for i in range(20):
        traces.append({
            "timestamp": 1000.0 + i,
            "counter": i,
            "entropy": 0.5 + (i * 0.01),
            "user_count": 10 + i,
            "active_sessions": 5,
        })
    
    print(f"   Generated {len(traces)} execution traces")
    print()

    # Discover invariants
    print("2.2 Discovering invariants...")
    discovered = eps.discover_invariants_from_traces(traces)
    
    print(f"   Discovered {len(discovered)} invariants:")
    for inv in discovered:
        print(f"   - [{inv.category.value}] {inv.description}")
        print(f"     Formula: {inv.formula}")
        print(f"     Confidence: {inv.confidence:.2f}")
        print(f"     Verified: {inv.verified}")
        print()

    # Example 2.3: Discover relationship invariants
    print("2.3 Discovering relationship invariants...")
    
    relationship_traces = []
    for i in range(15):
        total = i * 2
        part_a = i
        part_b = i
        relationship_traces.append({
            "total": total,
            "part_a": part_a,
            "part_b": part_b,
            "sum_check": part_a + part_b,  # Should equal total
        })
    
    eps_relationships = EnhancedExistentialProof(
        data_dir="governance/sovereign_data/examples_2",
    )
    
    discovered_rels = eps_relationships.discover_invariants_from_traces(
        relationship_traces
    )
    
    print(f"   Discovered {len(discovered_rels)} relationship invariants:")
    for inv in discovered_rels:
        if inv.category == InvariantCategory.FUNCTIONAL:
            print(f"   - {inv.description}")
            print(f"     Formula: {inv.formula}")
    print()


def example_3_continuous_verification():
    """
    Example 3: Continuous Verification of Critical Properties
    
    Demonstrates setting up real-time verification of system properties.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: CONTINUOUS VERIFICATION")
    print("=" * 80 + "\n")

    if not Z3_AVAILABLE:
        print("⚠️  Z3 not available - continuous verification requires Z3")
        return

    # Initialize Enhanced EPS with continuous verification
    eps = EnhancedExistentialProof(
        data_dir="governance/sovereign_data/examples",
        enable_z3=True,
        enable_continuous=True,
    )

    # Define critical properties to monitor
    print("3.1 Setting up continuous verification tasks...")
    
    properties = [
        ("Four Laws Compliance", "asimov_laws == true"),
        ("Entropy Lower Bound", "entropy > 0.1"),
        ("Hash Chain Integrity", "hash_chain_valid == true"),
        ("Human Oversight Active", "human_oversight == true"),
    ]
    
    # Add verification tasks
    for name, formula in properties:
        task_id = eps.continuous_verifier.add_verification_task(
            property_name=name,
            property_formula=formula,
            check_interval_seconds=10.0,  # Check every 10 seconds
        )
        print(f"   Added task: {name} (ID: {task_id})")
    
    print()
    print("3.2 Continuous verification tasks registered:")
    print(f"   Total tasks: {len(eps.continuous_verifier.tasks)}")
    print(f"   Check interval: 10 seconds")
    print()
    
    # Note: In production, would call:
    # asyncio.run(eps.continuous_verifier.run_continuous_verification())
    print("3.3 To start continuous verification:")
    print("   asyncio.run(eps.continuous_verifier.run_continuous_verification())")
    print()


def example_4_theorem_prover_integration():
    """
    Example 4: Theorem Prover Integration (Coq, Isabelle, Lean)
    
    Demonstrates integrating with external theorem provers.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: THEOREM PROVER INTEGRATION")
    print("=" * 80 + "\n")

    # Initialize Enhanced EPS
    eps = EnhancedExistentialProof(
        data_dir="governance/sovereign_data/examples",
        enable_z3=True,
        enable_continuous=False,
    )

    # Check available provers
    print("4.1 Checking available theorem provers...")
    available_provers = list(eps.theorem_provers.keys())
    
    if available_provers:
        print(f"   Available provers: {[p.value for p in available_provers]}")
    else:
        print("   ⚠️  No theorem provers available on system")
        print("   Install Coq: https://coq.inria.fr/")
        print("   Install Isabelle: https://isabelle.in.tum.de/")
        print("   Install Lean: https://leanprover.github.io/")
    print()

    # Example Coq proof script
    print("4.2 Example Coq proof script:")
    coq_proof = """
(* Simple theorem: addition is commutative *)
Theorem add_comm : forall n m : nat,
  n + m = m + n.
Proof.
  intros n m.
  induction n as [| n' IHn'].
  - simpl. rewrite <- plus_n_O. reflexivity.
  - simpl. rewrite IHn'. rewrite plus_n_Sm. reflexivity.
Qed.
"""
    print(coq_proof)
    
    if TheoremProver.COQ in available_provers:
        print("   Verifying with Coq...")
        try:
            proof = eps.verify_property_with_prover(
                prover=TheoremProver.COQ,
                proof_script=coq_proof,
                timeout_seconds=30,
            )
            print(f"   Status: {proof.status.value}")
            print(f"   Verification time: {proof.verification_time_ms:.2f}ms")
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print("   (Coq not available - proof not executed)")
    print()

    # Example Lean proof script
    print("4.3 Example Lean proof script:")
    lean_proof = """
-- Simple theorem: addition is commutative
theorem add_comm (n m : Nat) : n + m = m + n := by
  induction n with
  | zero => simp [Nat.zero_add, Nat.add_zero]
  | succ n ih => simp [Nat.succ_add, Nat.add_succ, ih]
"""
    print(lean_proof)
    
    if TheoremProver.LEAN in available_provers:
        print("   Verifying with Lean...")
        try:
            proof = eps.verify_property_with_prover(
                prover=TheoremProver.LEAN,
                proof_script=lean_proof,
                timeout_seconds=30,
            )
            print(f"   Status: {proof.status.value}")
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print("   (Lean not available - proof not executed)")
    print()


def example_5_proof_artifacts():
    """
    Example 5: Proof Artifact Generation and Reports
    
    Demonstrates generating human-readable proofs and comprehensive reports.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: PROOF ARTIFACTS AND COMPREHENSIVE REPORTS")
    print("=" * 80 + "\n")

    # Initialize Enhanced EPS
    eps = EnhancedExistentialProof(
        data_dir="governance/sovereign_data/examples",
        enable_z3=Z3_AVAILABLE,
        enable_continuous=False,
    )

    # Generate some violations and proofs for demonstration
    print("5.1 Generating sample violations and proofs...")
    
    from governance.existential_proof import InvariantViolation
    
    # Create a sample violation
    violation = InvariantViolation(
        violation_id="test_violation_001",
        timestamp=1234567890.0,
        invariant_type=InvariantType.ENTROPY_BOUNDS,
        severity=ViolationSeverity.ERROR,
        description="Entropy dropped below minimum threshold: 0.05 < 0.1",
        restorable=True,
        restoration_steps=["Reset entropy sources", "Re-seed from ORACLE_SEED"],
        evidence_hash="abc123def456",
        ledger_state_hash="fedcba987654",
    )
    
    # Record the violation
    eps.record_violation(violation)
    
    # Generate proof for the violation
    proof = eps.generate_violation_proof(violation)
    print(f"   Generated proof for violation: {violation.violation_id}")
    print()

    # Display human-readable proof
    print("5.2 Human-readable proof certificate:")
    print(proof.to_human_readable())
    print()

    # Generate comprehensive report
    print("5.3 Comprehensive verification report:")
    report = eps.generate_comprehensive_report()
    
    print(f"\nSUMMARY:")
    print(f"  Total Violations: {report['summary']['total_violations']}")
    print(f"  Critical Violations: {report['summary']['critical_violations']}")
    print(f"  Total Proofs: {report['summary']['total_proofs']}")
    print(f"  Verified Proofs: {report['summary']['verified_proofs']}")
    print(f"  Discovered Invariants: {report['summary']['discovered_invariants']}")
    print(f"  Verified Invariants: {report['summary']['verified_invariants']}")
    print()
    
    print(f"CAPABILITIES:")
    print(f"  Available Provers: {report['available_provers']}")
    print(f"  Z3 Available: {report['z3_available']}")
    print(f"  Continuous Verification: {report['continuous_verification_enabled']}")
    print()

    # Save full report
    report_path = Path("governance/sovereign_data/examples/verification_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    import json
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"5.4 Full report saved to: {report_path}")
    print()


def example_6_integration_workflow():
    """
    Example 6: Complete Integration Workflow
    
    Demonstrates a complete workflow using all EPS features together.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 6: COMPLETE INTEGRATION WORKFLOW")
    print("=" * 80 + "\n")

    # Initialize Enhanced EPS with all features
    print("6.1 Initializing Enhanced EPS with all features...")
    eps = EnhancedExistentialProof(
        data_dir="governance/sovereign_data/integration_demo",
        enable_z3=Z3_AVAILABLE,
        enable_continuous=True,
    )
    print("   ✓ Enhanced EPS initialized")
    print()

    # Step 1: Collect execution traces
    print("6.2 Collecting execution traces...")
    traces = []
    for i in range(30):
        traces.append({
            "timestamp": 1000.0 + i * 10,
            "entropy": 0.6 + (i * 0.005),
            "hash_chain_valid": True,
            "human_oversight": i % 5 == 0,  # Every 5th requires oversight
            "transaction_count": i * 2,
        })
    print(f"   ✓ Collected {len(traces)} traces")
    print()

    # Step 2: Discover invariants
    print("6.3 Discovering invariants from traces...")
    invariants = eps.discover_invariants_from_traces(traces)
    print(f"   ✓ Discovered {len(invariants)} invariants")
    for inv in invariants[:3]:  # Show first 3
        print(f"     - {inv.description} (confidence: {inv.confidence:.2f})")
    print()

    # Step 3: Verify properties with Z3
    if Z3_AVAILABLE:
        print("6.4 Verifying critical properties with Z3...")
        
        entropy = Real("entropy")
        property_formula = And(entropy >= 0.0, entropy <= 1.0)
        
        proof = eps.verify_property_with_z3(
            property_name="Entropy Bounds",
            property_formula=property_formula,
        )
        print(f"   ✓ Verification status: {proof.status.value}")
        print()

    # Step 4: Setup continuous verification
    print("6.5 Setting up continuous verification...")
    if eps.continuous_verifier:
        eps.continuous_verifier.add_verification_task(
            property_name="System Invariants",
            property_formula="entropy > 0.0 AND hash_chain_valid == true",
            check_interval_seconds=30.0,
        )
        print("   ✓ Continuous verification tasks registered")
    print()

    # Step 5: Generate comprehensive report
    print("6.6 Generating comprehensive verification report...")
    report = eps.generate_comprehensive_report()
    print(f"   ✓ Report generated with {report['summary']['total_proofs']} proofs")
    print()

    print("=" * 80)
    print("WORKFLOW COMPLETE - Enhanced EPS fully operational")
    print("=" * 80)


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  ENHANCED EXISTENTIAL PROOF SYSTEM - COMPREHENSIVE EXAMPLES".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    examples = [
        ("Z3 SMT Property Verification", example_1_z3_property_verification),
        ("Invariant Discovery", example_2_invariant_discovery),
        ("Continuous Verification", example_3_continuous_verification),
        ("Theorem Prover Integration", example_4_theorem_prover_integration),
        ("Proof Artifacts & Reports", example_5_proof_artifacts),
        ("Complete Integration Workflow", example_6_integration_workflow),
    ]
    
    for i, (name, example_func) in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Example {i} ({name}) failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + "  ALL EXAMPLES COMPLETED".center(78) + "║")
    print("╚" + "=" * 78 + "╝")
    print()


if __name__ == "__main__":
    main()
