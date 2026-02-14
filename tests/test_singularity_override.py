"""
Tests for Singularity Override Protocol

Validates:
- EPS predicate evaluation
- Dual confirmation requirement
- Super-unanimity voting (>95%)
- Ledger-driven violation counting (no internal state)
- Suspension trigger mechanism
- Refoundation protocol
- Override chain integrity
- ORACLE_SEED immutability
"""

import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from governance.singularity_override import (
    OverrideType,
    SingularityOverride,
    SystemState,
)


@pytest.fixture
def tmpdir():
    """Create temporary directory for test data"""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def override_system(tmpdir):
    """Create singularity override system in temp directory"""
    return SingularityOverride(data_dir=tmpdir)


@pytest.fixture
def sample_violations():
    """Create sample violation data"""
    return [
        {
            "violation_id": "v1",
            "severity": "CRITICAL",
            "restorable": False,
            "description": "Hash chain broken",
        },
        {
            "violation_id": "v2",
            "severity": "CRITICAL",
            "restorable": False,
            "description": "Four Laws violation",
        },
        {
            "violation_id": "v3",
            "severity": "ERROR",
            "restorable": True,
            "description": "Temporal inconsistency",
        },
    ]


class TestSingularityOverrideInitialization:
    """Test initialization and genesis setup"""

    def test_initialization(self, override_system, tmpdir):
        """Test system initializes correctly"""
        assert override_system.data_dir == tmpdir
        assert override_system.oracle_seed is not None
        assert len(override_system.oracle_seed) == 64  # SHA-256 hex
        assert override_system.private_key is not None
        assert override_system.public_key is not None

    def test_oracle_seed_immutability(self, tmpdir):
        """Test ORACLE_SEED is immutable across instances"""
        system1 = SingularityOverride(data_dir=tmpdir)
        seed1 = system1.oracle_seed

        # Create second instance with same data dir
        system2 = SingularityOverride(data_dir=tmpdir)
        seed2 = system2.oracle_seed

        assert seed1 == seed2, "ORACLE_SEED must be immutable"

    def test_genesis_seal_persistence(self, tmpdir):
        """Test genesis seal is persisted and loaded"""
        system1 = SingularityOverride(data_dir=tmpdir)

        genesis_path = tmpdir / "genesis_seal.bin"
        assert genesis_path.exists()

        # Load genesis seal directly
        with open(genesis_path, "rb") as f:
            genesis_seal = f.read()

        assert len(genesis_seal) == 32  # SHA-256 digest

        # Verify ORACLE_SEED derivation
        oracle_data = genesis_seal + b"ORACLE_SEED"
        expected_seed = hashlib.sha256(oracle_data).hexdigest()
        assert system1.oracle_seed == expected_seed


class TestEPSPredicate:
    """Test Existential Protection System predicate evaluation"""

    def test_no_violations(self, override_system):
        """Test EPS with no violations"""
        is_threat, reason = override_system.evaluate_eps_predicate([])
        assert not is_threat
        assert "No violations" in reason

    def test_critical_threshold(self, override_system):
        """Test EPS triggers on critical violations"""
        violations = [
            {"severity": "CRITICAL", "restorable": False},
            {"severity": "CRITICAL", "restorable": False},
            {"severity": "CRITICAL", "restorable": False},
        ]

        is_threat, reason = override_system.evaluate_eps_predicate(violations)
        assert is_threat
        assert "Critical threshold exceeded" in reason
        assert "3" in reason

    def test_total_violation_threshold(self, override_system):
        """Test EPS triggers on total violation count"""
        violations = [{"severity": "ERROR", "restorable": True}] * 11

        is_threat, reason = override_system.evaluate_eps_predicate(violations)
        assert is_threat
        assert "Violation threshold exceeded" in reason
        assert "11" in reason

    def test_non_restorable_threshold(self, override_system):
        """Test EPS triggers on non-restorable violations"""
        violations = [
            {"severity": "ERROR", "restorable": False},
            {"severity": "ERROR", "restorable": False},
            {"severity": "WARNING", "restorable": True},
        ]

        is_threat, reason = override_system.evaluate_eps_predicate(violations)
        assert is_threat
        assert "Non-restorable violations" in reason

    def test_below_threshold(self, override_system):
        """Test EPS does not trigger below thresholds"""
        violations = [
            {"severity": "WARNING", "restorable": True},
            {"severity": "ERROR", "restorable": True},
        ]

        is_threat, reason = override_system.evaluate_eps_predicate(violations)
        assert not is_threat
        assert "not reached" in reason


class TestDualConfirmation:
    """Test dual confirmation requirement"""

    def test_both_channels_pass(self, override_system):
        """Test dual confirmation with both channels passing"""
        assert override_system.check_dual_confirmation(True, True)

    def test_internal_only(self, override_system):
        """Test dual confirmation fails with only internal"""
        assert not override_system.check_dual_confirmation(True, False)

    def test_external_only(self, override_system):
        """Test dual confirmation fails with only external"""
        assert not override_system.check_dual_confirmation(False, True)

    def test_both_channels_fail(self, override_system):
        """Test dual confirmation fails with both channels failing"""
        assert not override_system.check_dual_confirmation(False, False)


class TestSuperUnanimity:
    """Test super-unanimity voting (>95% threshold)"""

    def test_exact_threshold(self, override_system):
        """Test super-unanimity at exact 95% threshold"""
        votes = {f"user{i}": i < 95 for i in range(100)}  # 95 approve, 5 reject

        passes, rate = override_system.evaluate_super_unanimity(votes, 100)
        assert passes
        assert rate == 0.95

    def test_above_threshold(self, override_system):
        """Test super-unanimity above threshold"""
        votes = {f"user{i}": True for i in range(100)}  # 100% approval

        passes, rate = override_system.evaluate_super_unanimity(votes, 100)
        assert passes
        assert rate == 1.0

    def test_below_threshold(self, override_system):
        """Test super-unanimity below threshold"""
        votes = {f"user{i}": i < 90 for i in range(100)}  # 90% approval

        passes, rate = override_system.evaluate_super_unanimity(votes, 100)
        assert not passes
        assert rate == 0.90

    def test_zero_stakeholders(self, override_system):
        """Test super-unanimity with zero stakeholders"""
        passes, rate = override_system.evaluate_super_unanimity({}, 0)
        assert not passes
        assert rate == 0.0

    def test_partial_voting(self, override_system):
        """Test super-unanimity with partial voting"""
        # Only 50 of 100 stakeholders voted, all approve
        votes = {f"user{i}": True for i in range(50)}

        passes, rate = override_system.evaluate_super_unanimity(votes, 100)
        assert not passes  # 50/100 = 50% < 95%
        assert rate == 0.5


class TestOverrideTrigger:
    """Test override trigger mechanism"""

    def test_successful_trigger(self, override_system, sample_violations):
        """Test successful override trigger"""
        record = override_system.trigger_override(
            override_type=OverrideType.EXISTENTIAL_THREAT,
            trigger_condition="EPS predicate triggered",
            ledger_violations=sample_violations,
            internal_confirmation=True,
            external_confirmation=True,
        )

        assert record.override_type == OverrideType.EXISTENTIAL_THREAT
        assert record.internal_confirmation
        assert record.external_confirmation
        assert record.ledger_violation_count == len(sample_violations)
        assert len(record.signature) > 0
        assert len(record.public_key) > 0

    def test_trigger_with_super_unanimity(self, override_system, sample_violations):
        """Test override trigger with super-unanimity vote"""
        votes = {f"user{i}": True for i in range(100)}

        record = override_system.trigger_override(
            override_type=OverrideType.SUPER_UNANIMITY,
            trigger_condition="Constitutional amendment",
            ledger_violations=[],
            internal_confirmation=True,
            external_confirmation=True,
            super_unanimity_votes=votes,
            total_stakeholders=100,
        )

        assert record.super_unanimity_vote["passes"]
        assert record.super_unanimity_vote["approval_rate"] == 1.0

    def test_trigger_fails_dual_confirmation(
        self, override_system, sample_violations
    ):
        """Test override trigger fails without dual confirmation"""
        with pytest.raises(ValueError, match="Dual confirmation requirement not met"):
            override_system.trigger_override(
                override_type=OverrideType.EXISTENTIAL_THREAT,
                trigger_condition="Test",
                ledger_violations=sample_violations,
                internal_confirmation=True,
                external_confirmation=False,  # External fails
            )

    def test_trigger_fails_super_unanimity(
        self, override_system, sample_violations
    ):
        """Test override trigger fails without super-unanimity"""
        votes = {f"user{i}": i < 90 for i in range(100)}  # Only 90%

        with pytest.raises(ValueError, match="Super-unanimity threshold not met"):
            override_system.trigger_override(
                override_type=OverrideType.SUPER_UNANIMITY,
                trigger_condition="Test",
                ledger_violations=[],
                internal_confirmation=True,
                external_confirmation=True,
                super_unanimity_votes=votes,
                total_stakeholders=100,
            )

    def test_trigger_updates_system_state(self, override_system, sample_violations):
        """Test trigger updates system state to SUSPENDED"""
        assert override_system.get_current_state() == SystemState.ACTIVE

        override_system.trigger_override(
            override_type=OverrideType.EXISTENTIAL_THREAT,
            trigger_condition="Test",
            ledger_violations=sample_violations,
            internal_confirmation=True,
            external_confirmation=True,
        )

        assert override_system.get_current_state() == SystemState.SUSPENDED


class TestLedgerDrivenState:
    """Test ledger-driven violation counting (no internal state)"""

    def test_violation_count_from_empty_ledger(self, override_system, tmpdir):
        """Test violation count from empty ledger"""
        ledger_path = tmpdir / "violations.jsonl"
        ledger_path.write_text("")

        count, violations = override_system.get_ledger_violation_count(ledger_path)
        assert count == 0
        assert len(violations) == 0

    def test_violation_count_from_populated_ledger(self, override_system, tmpdir):
        """Test violation count from populated ledger"""
        ledger_path = tmpdir / "violations.jsonl"

        violations = [
            {"id": "v1", "severity": "CRITICAL"},
            {"id": "v2", "severity": "ERROR"},
            {"id": "v3", "severity": "WARNING"},
        ]

        with open(ledger_path, "w") as f:
            for v in violations:
                f.write(json.dumps(v) + "\n")

        count, loaded_violations = override_system.get_ledger_violation_count(
            ledger_path
        )
        assert count == 3
        assert len(loaded_violations) == 3

    def test_violation_count_stateless(self, override_system, tmpdir):
        """Test violation count is stateless (recomputes each time)"""
        ledger_path = tmpdir / "violations.jsonl"
        ledger_path.write_text(json.dumps({"id": "v1"}) + "\n")

        count1, _ = override_system.get_ledger_violation_count(ledger_path)
        assert count1 == 1

        # Append another violation
        with open(ledger_path, "a") as f:
            f.write(json.dumps({"id": "v2"}) + "\n")

        # Count should update (stateless re-read)
        count2, _ = override_system.get_ledger_violation_count(ledger_path)
        assert count2 == 2


class TestRefoundation:
    """Test refoundation protocol"""

    def test_refoundation_creates_new_genesis(self, override_system):
        """Test refoundation creates new genesis seal"""
        old_oracle_seed = override_system.oracle_seed
        old_genesis_path = override_system.data_dir / "genesis_seal.bin"

        with open(old_genesis_path, "rb") as f:
            old_genesis = f.read()

        # Trigger refoundation
        result = override_system.initiate_refoundation(
            authorization_signature=b"authorized"
        )

        assert "new_genesis_seal" in result
        assert "new_oracle_seed" in result
        assert result["previous_oracle_seed"] == old_oracle_seed

        # Verify new genesis is different
        with open(old_genesis_path, "rb") as f:
            new_genesis = f.read()

        assert new_genesis != old_genesis

    def test_refoundation_archives_ledgers(self, override_system, sample_violations):
        """Test refoundation archives old ledgers"""
        # Create override record
        override_system.trigger_override(
            override_type=OverrideType.EXISTENTIAL_THREAT,
            trigger_condition="Test",
            ledger_violations=sample_violations,
            internal_confirmation=True,
            external_confirmation=True,
        )

        assert override_system.override_ledger_path.exists()

        # Initiate refoundation
        result = override_system.initiate_refoundation(
            authorization_signature=b"authorized"
        )

        archive_dir = Path(result["archive_location"])
        assert archive_dir.exists()
        assert (archive_dir / "override_ledger.jsonl").exists()

        # Old ledger should be removed
        assert not override_system.override_ledger_path.exists()

    def test_refoundation_updates_state(self, override_system):
        """Test refoundation updates system state to REFOUNDING"""
        override_system.initiate_refoundation(authorization_signature=b"authorized")

        assert override_system.get_current_state() == SystemState.REFOUNDING


class TestOverrideChainIntegrity:
    """Test override ledger chain integrity verification"""

    def test_empty_chain_valid(self, override_system):
        """Test empty override chain is valid"""
        is_valid, issues = override_system.verify_override_chain()
        assert is_valid
        assert len(issues) == 0

    def test_single_record_chain_valid(self, override_system, sample_violations):
        """Test chain with single record is valid"""
        override_system.trigger_override(
            override_type=OverrideType.EXISTENTIAL_THREAT,
            trigger_condition="Test",
            ledger_violations=sample_violations,
            internal_confirmation=True,
            external_confirmation=True,
        )

        is_valid, issues = override_system.verify_override_chain()
        assert is_valid
        assert len(issues) == 0

    def test_multiple_records_chain_valid(self, override_system, sample_violations):
        """Test chain with multiple records is valid"""
        for i in range(3):
            # Need to move back to ACTIVE for next trigger
            state_path = override_system.data_dir / "system_state.json"
            with open(state_path, "w") as f:
                json.dump({"current_state": "active"}, f)

            override_system.trigger_override(
                override_type=OverrideType.INVARIANT_VIOLATION,
                trigger_condition=f"Test {i}",
                ledger_violations=sample_violations,
                internal_confirmation=True,
                external_confirmation=True,
            )

        is_valid, issues = override_system.verify_override_chain()
        assert is_valid
        assert len(issues) == 0

    def test_tampered_chain_detected(self, override_system, sample_violations):
        """Test tampering with chain is detected"""
        override_system.trigger_override(
            override_type=OverrideType.EXISTENTIAL_THREAT,
            trigger_condition="Test",
            ledger_violations=sample_violations,
            internal_confirmation=True,
            external_confirmation=True,
        )

        # Tamper with ledger
        with open(override_system.override_ledger_path) as f:
            lines = f.readlines()

        # Modify the hash
        record = json.loads(lines[0])
        record["hash"] = "tampered_hash"

        with open(override_system.override_ledger_path, "w") as f:
            f.write(json.dumps(record) + "\n")

        is_valid, issues = override_system.verify_override_chain()
        assert not is_valid
        assert len(issues) > 0
        assert "hash mismatch" in issues[0].lower()


class TestSystemState:
    """Test system state management"""

    def test_initial_state_is_active(self, override_system):
        """Test initial system state is ACTIVE"""
        assert override_system.get_current_state() == SystemState.ACTIVE

    def test_state_persisted_across_instances(self, tmpdir, sample_violations):
        """Test state is persisted and loaded correctly"""
        system1 = SingularityOverride(data_dir=tmpdir)
        system1.trigger_override(
            override_type=OverrideType.EXISTENTIAL_THREAT,
            trigger_condition="Test",
            ledger_violations=sample_violations,
            internal_confirmation=True,
            external_confirmation=True,
        )

        assert system1.get_current_state() == SystemState.SUSPENDED

        # Create new instance
        system2 = SingularityOverride(data_dir=tmpdir)
        assert system2.get_current_state() == SystemState.SUSPENDED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
