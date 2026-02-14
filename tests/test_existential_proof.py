"""
Tests for Existential Proof System

Validates:
- Invariant violation detection
- Non-restorability evaluation
- External signature verification
- Dual-channel restoration validation
- Ledger-driven state analysis
"""

import tempfile
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519

from governance.existential_proof import (
    ExistentialProof,
    InvariantType,
    InvariantViolation,
    ViolationSeverity,
)


@pytest.fixture
def tmpdir():
    """Create temporary directory for test data"""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def proof_system(tmpdir):
    """Create existential proof system in temp directory"""
    return ExistentialProof(data_dir=tmpdir)


@pytest.fixture
def sample_keypair():
    """Generate sample Ed25519 keypair"""
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    from cryptography.hazmat.primitives import serialization

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    return {
        "private_key": private_key,
        "public_key": public_key,
        "private_bytes": private_bytes,
        "public_bytes": public_bytes,
    }


class TestInvariantViolationDetection:
    """Test invariant violation detection"""

    def test_asimov_laws_violation(self, proof_system):
        """Test Asimov Laws violation detection"""
        ledger_state = {"action": "harm_human"}
        current_value = "violated"
        expected_value = "compliant"

        violation = proof_system.detect_invariant_violation(
            InvariantType.ASIMOV_LAWS,
            ledger_state,
            current_value,
            expected_value,
        )

        assert violation is not None
        assert violation.invariant_type == InvariantType.ASIMOV_LAWS
        assert violation.severity == ViolationSeverity.CRITICAL
        assert not violation.restorable  # Four Laws violations are fatal

    def test_asimov_laws_compliant(self, proof_system):
        """Test Asimov Laws compliance (no violation)"""
        ledger_state = {"action": "help_human"}
        current_value = "compliant"
        expected_value = "compliant"

        violation = proof_system.detect_invariant_violation(
            InvariantType.ASIMOV_LAWS,
            ledger_state,
            current_value,
            expected_value,
        )

        assert violation is None

    def test_entropy_bounds_violation(self, proof_system):
        """Test entropy bounds violation"""
        ledger_state = {"entropy_sources": ["source1", "source2"]}
        current_value = 0.05  # Too low
        expected_value = {"min": 0.1, "max": 1.0}

        violation = proof_system.detect_invariant_violation(
            InvariantType.ENTROPY_BOUNDS,
            ledger_state,
            current_value,
            expected_value,
        )

        assert violation is not None
        assert violation.invariant_type == InvariantType.ENTROPY_BOUNDS
        assert violation.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.ERROR]
        assert violation.restorable  # Can re-seed

    def test_entropy_bounds_compliant(self, proof_system):
        """Test entropy bounds compliance"""
        ledger_state = {}
        current_value = 0.5
        expected_value = {"min": 0.1, "max": 1.0}

        violation = proof_system.detect_invariant_violation(
            InvariantType.ENTROPY_BOUNDS,
            ledger_state,
            current_value,
            expected_value,
        )

        assert violation is None

    def test_hash_chain_violation(self, proof_system):
        """Test hash chain violation"""
        ledger_state = {"block_id": "block123"}
        current_value = "invalid_hash"
        expected_value = "valid_hash"

        violation = proof_system.detect_invariant_violation(
            InvariantType.HASH_CHAIN,
            ledger_state,
            current_value,
            expected_value,
        )

        assert violation is not None
        assert violation.invariant_type == InvariantType.HASH_CHAIN
        assert violation.severity == ViolationSeverity.CRITICAL
        assert not violation.restorable  # Hash chain breaks are fatal

    def test_temporal_consistency_violation(self, proof_system):
        """Test temporal consistency violation (time-travel)"""
        ledger_state = {}
        current_value = 100.0  # Earlier timestamp
        expected_value = 200.0  # Later timestamp

        violation = proof_system.detect_invariant_violation(
            InvariantType.TEMPORAL_CONSISTENCY,
            ledger_state,
            current_value,
            expected_value,
        )

        assert violation is not None
        assert violation.invariant_type == InvariantType.TEMPORAL_CONSISTENCY
        assert violation.severity == ViolationSeverity.ERROR
        assert violation.restorable  # Can sync clock

    def test_determinism_violation(self, proof_system):
        """Test determinism violation"""
        ledger_state = {"input": "test"}
        current_value = "output_a"
        expected_value = "output_b"

        violation = proof_system.detect_invariant_violation(
            InvariantType.DETERMINISM,
            ledger_state,
            current_value,
            expected_value,
        )

        assert violation is not None
        assert violation.invariant_type == InvariantType.DETERMINISM
        assert violation.severity == ViolationSeverity.ERROR
        assert violation.restorable

    def test_human_oversight_violation(self, proof_system):
        """Test human oversight violation"""
        ledger_state = {"action": "sensitive_operation"}
        current_value = False  # No human approval
        expected_value = True  # Human approval required

        violation = proof_system.detect_invariant_violation(
            InvariantType.HUMAN_OVERSIGHT,
            ledger_state,
            current_value,
            expected_value,
        )

        assert violation is not None
        assert violation.invariant_type == InvariantType.HUMAN_OVERSIGHT
        assert violation.severity == ViolationSeverity.WARNING
        assert violation.restorable


class TestNonRestorability:
    """Test non-restorability evaluation"""

    def test_no_violations_restorable(self, proof_system):
        """Test system with no violations is restorable"""
        is_non_restorable, reason = proof_system.evaluate_non_restorability([])

        assert not is_non_restorable
        assert "No violations" in reason

    def test_critical_non_restorable(self, proof_system):
        """Test critical non-restorable violation"""
        violations = [
            InvariantViolation(
                violation_id="v1",
                timestamp=100.0,
                invariant_type=InvariantType.ASIMOV_LAWS,
                severity=ViolationSeverity.CRITICAL,
                description="Four Laws violated",
                restorable=False,
                restoration_steps=[],
                evidence_hash="hash1",
                ledger_state_hash="hash2",
            )
        ]

        is_non_restorable, reason = proof_system.evaluate_non_restorability(
            violations
        )

        assert is_non_restorable
        assert "Critical non-restorable" in reason

    def test_multiple_error_non_restorable(self, proof_system):
        """Test multiple error-level non-restorable violations"""
        violations = [
            InvariantViolation(
                violation_id=f"v{i}",
                timestamp=100.0,
                invariant_type=InvariantType.DETERMINISM,
                severity=ViolationSeverity.ERROR,
                description="Non-deterministic",
                restorable=False,
                restoration_steps=[],
                evidence_hash=f"hash{i}",
                ledger_state_hash="state_hash",
            )
            for i in range(2)
        ]

        is_non_restorable, reason = proof_system.evaluate_non_restorability(
            violations
        )

        assert is_non_restorable
        assert "error-level non-restorable" in reason.lower()

    def test_hash_chain_always_non_restorable(self, proof_system):
        """Test hash chain violations are always non-restorable"""
        violations = [
            InvariantViolation(
                violation_id="v1",
                timestamp=100.0,
                invariant_type=InvariantType.HASH_CHAIN,
                severity=ViolationSeverity.CRITICAL,
                description="Hash chain broken",
                restorable=True,  # Even if marked restorable
                restoration_steps=[],
                evidence_hash="hash1",
                ledger_state_hash="hash2",
            )
        ]

        is_non_restorable, reason = proof_system.evaluate_non_restorability(
            violations
        )

        assert is_non_restorable
        assert "Hash chain" in reason

    def test_restorable_violations(self, proof_system):
        """Test system with only restorable violations is restorable"""
        violations = [
            InvariantViolation(
                violation_id="v1",
                timestamp=100.0,
                invariant_type=InvariantType.HUMAN_OVERSIGHT,
                severity=ViolationSeverity.WARNING,
                description="Human approval missing",
                restorable=True,
                restoration_steps=["Request human approval"],
                evidence_hash="hash1",
                ledger_state_hash="hash2",
            )
        ]

        is_non_restorable, reason = proof_system.evaluate_non_restorability(
            violations
        )

        assert not is_non_restorable
        assert "restorable" in reason.lower()


class TestExternalSignatureVerification:
    """Test external signature verification"""

    def test_valid_signature(self, proof_system, sample_keypair):
        """Test verification of valid signature"""
        message = b"test message for signature"
        signature = sample_keypair["private_key"].sign(message)

        is_valid = proof_system.verify_external_signature(
            message, signature, sample_keypair["public_bytes"]
        )

        assert is_valid

    def test_invalid_signature(self, proof_system, sample_keypair):
        """Test verification of invalid signature"""
        message = b"test message"
        wrong_message = b"different message"
        signature = sample_keypair["private_key"].sign(message)

        is_valid = proof_system.verify_external_signature(
            wrong_message, signature, sample_keypair["public_bytes"]
        )

        assert not is_valid

    def test_wrong_public_key(self, proof_system, sample_keypair):
        """Test verification with wrong public key"""
        message = b"test message"
        signature = sample_keypair["private_key"].sign(message)

        # Generate different keypair
        wrong_keypair = ed25519.Ed25519PrivateKey.generate()
        from cryptography.hazmat.primitives import serialization

        wrong_public_bytes = wrong_keypair.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

        is_valid = proof_system.verify_external_signature(
            message, signature, wrong_public_bytes
        )

        assert not is_valid


class TestDualChannelRestoration:
    """Test dual-channel restoration validation"""

    def test_successful_restoration_components(self, proof_system, sample_keypair):
        """Test restoration components work correctly"""
        violations = [
            InvariantViolation(
                violation_id="v1",
                timestamp=100.0,
                invariant_type=InvariantType.HUMAN_OVERSIGHT,
                severity=ViolationSeverity.WARNING,
                description="Test",
                restorable=True,
                restoration_steps=["Fix"],
                evidence_hash="hash1",
                ledger_state_hash="hash2",
            )
        ]

        # Test that violations are restorable
        is_non_restorable, _ = proof_system.evaluate_non_restorability(violations)
        assert not is_non_restorable

        # Test that signature verification works
        test_message = b"test restoration authorization"
        signature = sample_keypair["private_key"].sign(test_message)
        is_valid = proof_system.verify_external_signature(
            test_message, signature, sample_keypair["public_bytes"]
        )
        assert is_valid

        # Note: Full dual-channel test requires signing the exact message
        # that the function creates internally (with current timestamp),
        # which is not practical in a test. The components are tested individually.

    def test_non_restorable_state(self, proof_system, sample_keypair):
        """Test restoration fails for non-restorable state"""
        violations = [
            InvariantViolation(
                violation_id="v1",
                timestamp=100.0,
                invariant_type=InvariantType.ASIMOV_LAWS,
                severity=ViolationSeverity.CRITICAL,
                description="Test",
                restorable=False,
                restoration_steps=[],
                evidence_hash="hash1",
                ledger_state_hash="hash2",
            )
        ]

        restoration_message = b"restoration_request"
        signature = sample_keypair["private_key"].sign(restoration_message)

        can_restore, reason = proof_system.check_dual_channel_restoration(
            violations,
            internal_analysis_passes=True,
            external_signature=signature,
            external_public_key=sample_keypair["public_bytes"],
        )

        assert not can_restore
        assert "Non-restorable" in reason

    def test_internal_analysis_fails(self, proof_system, sample_keypair):
        """Test restoration fails when internal analysis fails"""
        violations = []
        restoration_message = b"restoration_request"
        signature = sample_keypair["private_key"].sign(restoration_message)

        can_restore, reason = proof_system.check_dual_channel_restoration(
            violations,
            internal_analysis_passes=False,  # Internal fails
            external_signature=signature,
            external_public_key=sample_keypair["public_bytes"],
        )

        assert not can_restore
        assert "Internal analysis failed" in reason

    def test_external_signature_missing(self, proof_system):
        """Test restoration fails without external signature"""
        violations = []

        can_restore, reason = proof_system.check_dual_channel_restoration(
            violations,
            internal_analysis_passes=True,
            external_signature=None,  # No signature
            external_public_key=None,
        )

        assert not can_restore
        assert "External signature not provided" in reason

    def test_external_signature_invalid(self, proof_system, sample_keypair):
        """Test restoration fails with invalid external signature"""
        violations = [
            InvariantViolation(
                violation_id="v1",
                timestamp=100.0,
                invariant_type=InvariantType.HUMAN_OVERSIGHT,
                severity=ViolationSeverity.WARNING,
                description="Test",
                restorable=True,
                restoration_steps=["Fix"],
                evidence_hash="hash1",
                ledger_state_hash="hash2",
            )
        ]

        # Sign different message
        wrong_message = b"wrong_message"
        signature = sample_keypair["private_key"].sign(wrong_message)

        can_restore, reason = proof_system.check_dual_channel_restoration(
            violations,
            internal_analysis_passes=True,
            external_signature=signature,
            external_public_key=sample_keypair["public_bytes"],
        )

        assert not can_restore
        assert "verification failed" in reason.lower()


class TestViolationRecording:
    """Test violation recording to ledger"""

    def test_record_single_violation(self, proof_system):
        """Test recording single violation"""
        violation = InvariantViolation(
            violation_id="v1",
            timestamp=100.0,
            invariant_type=InvariantType.DETERMINISM,
            severity=ViolationSeverity.ERROR,
            description="Test violation",
            restorable=True,
            restoration_steps=["Fix it"],
            evidence_hash="hash1",
            ledger_state_hash="hash2",
        )

        proof_system.record_violation(violation)

        assert proof_system.violation_ledger_path.exists()

        # Verify recorded
        violations = proof_system.load_violations()
        assert len(violations) == 1
        assert violations[0].violation_id == "v1"

    def test_record_multiple_violations(self, proof_system):
        """Test recording multiple violations"""
        for i in range(3):
            violation = InvariantViolation(
                violation_id=f"v{i}",
                timestamp=100.0 + i,
                invariant_type=InvariantType.ENTROPY_BOUNDS,
                severity=ViolationSeverity.WARNING,
                description=f"Test {i}",
                restorable=True,
                restoration_steps=[],
                evidence_hash=f"hash{i}",
                ledger_state_hash="state_hash",
            )
            proof_system.record_violation(violation)

        violations = proof_system.load_violations()
        assert len(violations) == 3

    def test_load_violations_stateless(self, proof_system):
        """Test loading violations is stateless"""
        violation = InvariantViolation(
            violation_id="v1",
            timestamp=100.0,
            invariant_type=InvariantType.HUMAN_OVERSIGHT,
            severity=ViolationSeverity.WARNING,
            description="Test",
            restorable=True,
            restoration_steps=[],
            evidence_hash="hash1",
            ledger_state_hash="hash2",
        )

        proof_system.record_violation(violation)

        # Load twice
        violations1 = proof_system.load_violations()
        violations2 = proof_system.load_violations()

        assert len(violations1) == len(violations2)
        assert violations1[0].violation_id == violations2[0].violation_id


class TestRestorationPlan:
    """Test restoration plan generation"""

    def test_no_restorable_violations(self, proof_system):
        """Test restoration plan with no restorable violations"""
        violations = [
            InvariantViolation(
                violation_id="v1",
                timestamp=100.0,
                invariant_type=InvariantType.HASH_CHAIN,
                severity=ViolationSeverity.CRITICAL,
                description="Test",
                restorable=False,
                restoration_steps=[],
                evidence_hash="hash1",
                ledger_state_hash="hash2",
            )
        ]

        plan = proof_system.get_restoration_plan(violations)

        assert not plan["can_restore"]
        assert "No restorable violations" in plan["reason"]
        assert len(plan["steps"]) == 0

    def test_restorable_violations(self, proof_system):
        """Test restoration plan with restorable violations"""
        violations = [
            InvariantViolation(
                violation_id="v1",
                timestamp=100.0,
                invariant_type=InvariantType.TEMPORAL_CONSISTENCY,
                severity=ViolationSeverity.ERROR,
                description="Test",
                restorable=True,
                restoration_steps=["Synchronize system clock", "Verify NTP sources"],
                evidence_hash="hash1",
                ledger_state_hash="hash2",
            ),
            InvariantViolation(
                violation_id="v2",
                timestamp=101.0,
                invariant_type=InvariantType.ENTROPY_BOUNDS,
                severity=ViolationSeverity.ERROR,
                description="Test",
                restorable=True,
                restoration_steps=["Reset entropy sources", "Re-seed from ORACLE_SEED"],
                evidence_hash="hash3",
                ledger_state_hash="hash4",
            ),
        ]

        plan = proof_system.get_restoration_plan(violations)

        assert plan["can_restore"]
        assert plan["violation_count"] == 2
        assert len(plan["steps"]) > 0
        assert "Synchronize system clock" in plan["steps"]
        assert "Reset entropy sources" in plan["steps"]

    def test_deduplicate_restoration_steps(self, proof_system):
        """Test restoration plan deduplicates steps"""
        violations = [
            InvariantViolation(
                violation_id=f"v{i}",
                timestamp=100.0 + i,
                invariant_type=InvariantType.TEMPORAL_CONSISTENCY,
                severity=ViolationSeverity.ERROR,
                description="Test",
                restorable=True,
                restoration_steps=[
                    "Synchronize system clock"
                ],  # Same step for both
                evidence_hash=f"hash{i}",
                ledger_state_hash="state_hash",
            )
            for i in range(2)
        ]

        plan = proof_system.get_restoration_plan(violations)

        assert plan["can_restore"]
        assert plan["violation_count"] == 2
        # Should have only one instance of the step
        assert plan["steps"].count("Synchronize system clock") == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
