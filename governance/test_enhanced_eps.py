"""
Test script for Enhanced Existential Proof System

Quick validation that all components are working correctly.
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """Test that all modules can be imported"""
    print("=" * 80)
    print("TEST 1: Module Imports")
    print("=" * 80)
    
    try:
        from governance.existential_proof_enhanced import (
            EnhancedExistentialProof,
            TheoremProver,
            ProofStatus,
            ProofArtifact,
            DiscoveredInvariant,
            InvariantCategory,
            SMTConstraintSolver,
            TheoremProverInterface,
            InvariantDiscoveryEngine,
            ContinuousVerifier,
        )
        print("✓ All modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_z3_availability():
    """Test Z3 solver availability"""
    print("\n" + "=" * 80)
    print("TEST 2: Z3 Availability")
    print("=" * 80)
    
    try:
        from z3 import Int, Real, Bool, And, Or, Not
        print("✓ Z3 is available")
        return True
    except ImportError:
        print("⚠ Z3 not available (install with: pip install z3-solver)")
        return False


def test_basic_initialization():
    """Test basic EPS initialization"""
    print("\n" + "=" * 80)
    print("TEST 3: Basic Initialization")
    print("=" * 80)
    
    try:
        from governance.existential_proof_enhanced import EnhancedExistentialProof
        
        eps = EnhancedExistentialProof(
            data_dir="governance/sovereign_data/test",
            enable_z3=True,
            enable_continuous=True,
        )
        
        print(f"✓ Enhanced EPS initialized")
        print(f"  - Data directory: {eps.data_dir}")
        print(f"  - Z3 available: {eps.smt_solver is not None}")
        print(f"  - Continuous verifier: {eps.continuous_verifier is not None}")
        print(f"  - Invariant engine: {eps.invariant_engine is not None}")
        print(f"  - Available theorem provers: {list(eps.theorem_provers.keys())}")
        
        return True
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_z3_verification():
    """Test Z3 property verification"""
    print("\n" + "=" * 80)
    print("TEST 4: Z3 Property Verification")
    print("=" * 80)
    
    try:
        from z3 import Int, Real, And
        from governance.existential_proof_enhanced import EnhancedExistentialProof
        
        eps = EnhancedExistentialProof(
            data_dir="governance/sovereign_data/test",
            enable_z3=True,
            enable_continuous=False,
        )
        
        # Test simple property
        x = Int("x")
        y = Int("y")
        property_formula = (x + y == y + x)
        
        proof = eps.verify_property_with_z3(
            property_name="Addition Commutativity",
            property_formula=property_formula,
        )
        
        print(f"✓ Property verified")
        print(f"  - Status: {proof.status.value}")
        print(f"  - Time: {proof.verification_time_ms:.2f}ms")
        print(f"  - Proof steps: {len(proof.proof_steps)}")
        
        return proof.status.value == "verified"
        
    except ImportError:
        print("⚠ Z3 not available - skipping test")
        return True
    except Exception as e:
        print(f"✗ Z3 verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_invariant_discovery():
    """Test invariant discovery engine"""
    print("\n" + "=" * 80)
    print("TEST 5: Invariant Discovery")
    print("=" * 80)
    
    try:
        from governance.existential_proof_enhanced import EnhancedExistentialProof
        
        eps = EnhancedExistentialProof(
            data_dir="governance/sovereign_data/test",
            enable_z3=False,
            enable_continuous=False,
        )
        
        # Generate test traces
        traces = []
        for i in range(20):
            traces.append({
                "counter": i,
                "timestamp": 1000.0 + i,
                "entropy": 0.5 + (i * 0.01),
            })
        
        # Discover invariants
        invariants = eps.discover_invariants_from_traces(traces)
        
        print(f"✓ Invariant discovery completed")
        print(f"  - Traces processed: {len(traces)}")
        print(f"  - Invariants discovered: {len(invariants)}")
        
        for inv in invariants[:3]:  # Show first 3
            print(f"  - {inv.description} (confidence: {inv.confidence:.2f})")
        
        return True
        
    except Exception as e:
        print(f"✗ Invariant discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_violation_proof():
    """Test violation proof generation"""
    print("\n" + "=" * 80)
    print("TEST 6: Violation Proof Generation")
    print("=" * 80)
    
    try:
        from governance.existential_proof_enhanced import EnhancedExistentialProof
        from governance.existential_proof import (
            InvariantViolation,
            InvariantType,
            ViolationSeverity,
        )
        
        eps = EnhancedExistentialProof(
            data_dir="governance/sovereign_data/test",
            enable_z3=False,
            enable_continuous=False,
        )
        
        # Create test violation
        violation = InvariantViolation(
            violation_id="test_001",
            timestamp=1234567890.0,
            invariant_type=InvariantType.ENTROPY_BOUNDS,
            severity=ViolationSeverity.ERROR,
            description="Test violation for proof generation",
            restorable=True,
            restoration_steps=["Step 1", "Step 2"],
            evidence_hash="abc123",
            ledger_state_hash="def456",
        )
        
        # Generate proof
        proof = eps.generate_violation_proof(violation)
        
        print(f"✓ Violation proof generated")
        print(f"  - Proof ID: {proof.proof_id}")
        print(f"  - Status: {proof.status.value}")
        print(f"  - Proof steps: {len(proof.proof_steps)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Violation proof generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comprehensive_report():
    """Test comprehensive report generation"""
    print("\n" + "=" * 80)
    print("TEST 7: Comprehensive Report")
    print("=" * 80)
    
    try:
        from governance.existential_proof_enhanced import EnhancedExistentialProof
        
        eps = EnhancedExistentialProof(
            data_dir="governance/sovereign_data/test",
            enable_z3=True,
            enable_continuous=True,
        )
        
        # Generate report
        report = eps.generate_comprehensive_report()
        
        print(f"✓ Report generated")
        print(f"  Summary:")
        for key, value in report['summary'].items():
            print(f"    - {key}: {value}")
        
        print(f"  Capabilities:")
        print(f"    - Z3: {report['z3_available']}")
        print(f"    - Continuous: {report['continuous_verification_enabled']}")
        print(f"    - Provers: {report['available_provers']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  Enhanced EPS - Quick Validation Test".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    tests = [
        ("Module Imports", test_imports),
        ("Z3 Availability", test_z3_availability),
        ("Basic Initialization", test_basic_initialization),
        ("Z3 Verification", test_z3_verification),
        ("Invariant Discovery", test_invariant_discovery),
        ("Violation Proof", test_violation_proof),
        ("Comprehensive Report", test_comprehensive_report),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
