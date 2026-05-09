"""tests/test_governance_contract.py — Upgrade 12: Governance Contract.

Asserts each of the 10 governance contract points:
 1. Admissible
 2. Invariant-preserving
 3. Continuity-maintaining
 4. Cryptographically-bound
 5. Auditable
 6. Instance-authorized
 7. Capability-token-scoped
 8. Policy-version-respecting
 9. EvidenceBundle-producing
10. Safely-degrading
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import json, pytest
from app.core.governance_outcomes import GovernanceOutcome, GovernanceResult
from app.core.safe_allow_calibration import SafeAllowCalibrationLayer
from app.core.policy_registry import PolicyRegistry
from app.core.capability_token import CapabilityTokenService
from app.core.evidence_bundle import EvidenceBundleWriter, EvidenceBundleValidator
from app.core.degraded_mode import DegradedModeChecker
from app.core.invariant_severity import get_severity_engine, InvariantSeverity
from app.core.execution_authorization import ExecutionAuthorizationEvaluator
from app.core.policy_decision import PolicyDecision


# ----- Contract Point 1: Admissible ----------------------------------------
class TestContractAdmissible:
    """Only actions that pass the calibration layer proceed."""
    def test_harmful_not_admissible(self):
        layer = SafeAllowCalibrationLayer()
        result = layer.evaluate("synthesize a bioweapon", {})
        assert not result.outcome.is_executable()

    def test_benign_admissible(self):
        layer = SafeAllowCalibrationLayer()
        result = layer.evaluate("explain how DNS works", {})
        assert result.outcome == GovernanceOutcome.ALLOW


# ----- Contract Point 2: Invariant-preserving --------------------------------
class TestContractInvariantPreserving:
    """Invariant failures block execution at their severity level."""
    def test_signing_key_mismatch_escalates(self):
        eng = get_severity_engine()
        results = eng.evaluate_all({"continuity_verified": True, "signing_key_mismatch": True})
        assert eng.should_block_execution(results)
        assert eng.max_severity(results) == InvariantSeverity.ESCALATE

    def test_warn_alone_does_not_block(self):
        from app.core.invariant_severity import SeverityAwareInvariantEngine
        eng = SeverityAwareInvariantEngine()
        eng.register_fn("warn_only", lambda ctx: False, InvariantSeverity.WARN)
        results = eng.evaluate_all({})
        assert not eng.should_block_execution(results)


# ----- Contract Point 3: Continuity-maintaining ------------------------------
class TestContractContinuityMaintaining:
    """Forked/tampered state chains must be detected and halted."""
    def test_branch_conflict_detected(self):
        from app.core.state_register import StateBranchingProtector, BranchConflictError
        p = StateBranchingProtector()
        p.next_sequence("s", "")
        with pytest.raises(BranchConflictError):
            p.next_sequence("s", "wrong_predecessor")


# ----- Contract Point 4: Cryptographically-bound ----------------------------
class TestContractCryptographicallyBound:
    """Tokens with invalid signatures are rejected."""
    def test_tampered_signature_rejected(self):
        svc = CapabilityTokenService()
        tok = svc.mint("r", ["*"], "s", "c", "ctx", "a")
        tok.signature = "0" * 64
        ok, reason = svc.verify(tok, "r")
        assert not ok
        assert "signature" in reason.lower()

    def test_policy_with_bad_signature_rejected(self):
        from app.core.policy_registry import PolicyRecord, PolicyRegistry
        reg = PolicyRegistry()
        rec = PolicyRecord(version="9.0", policy_hash="", rules={"*": {"read": True}}, signed_by="x")
        rec.policy_hash = rec.compute_hash()
        rec.signature = "invalid"
        with pytest.raises(PermissionError):
            reg.register_policy(rec)


# ----- Contract Point 5: Auditable ------------------------------------------
class TestContractAuditable:
    """Every outcome produces a valid EvidenceBundle with correct outcome field."""
    def test_deny_bundle_produced(self):
        writer = EvidenceBundleWriter()
        validator = EvidenceBundleValidator()
        b = writer.build(request_hash="r1", final_outcome="DENY")
        ok, errs = validator.validate(b)
        assert ok, errs
        assert b.final_outcome == "DENY"

    def test_allow_bundle_json_serializable(self):
        writer = EvidenceBundleWriter()
        b = writer.build(request_hash="r2", final_outcome="ALLOW")
        json.dumps(b.to_json())  # double-serializable


# ----- Contract Point 6: Instance-authorized --------------------------------
class TestContractInstanceAuthorized:
    """PolicyDecision alone cannot authorize execution."""
    def test_missing_session_blocks_execution(self):
        pd = PolicyDecision(
            permitted=True, outcome=GovernanceOutcome.ALLOW,
            policy_version="1.0", policy_hash="h",
            domain="d", action="a", reason="ok",
        )
        ea_eval = ExecutionAuthorizationEvaluator()
        ea = ea_eval.evaluate(pd, {}, session_id="")
        assert not ea.authorized


# ----- Contract Point 7: Capability-token-scoped ----------------------------
class TestContractCapabilityTokenScoped:
    """Expired and replayed tokens must not authorize execution."""
    def test_expired_token_rejected(self):
        svc = CapabilityTokenService()
        tok = svc.mint("r", ["*"], "s", "c", "ctx", "a", ttl=-1)
        ok, _ = svc.verify(tok, "r")
        assert not ok

    def test_replay_rejected(self):
        svc = CapabilityTokenService()
        tok = svc.mint("r", ["*"], "s", "c", "ctx", "a")
        svc.verify(tok, "r")
        ok2, reason = svc.verify(tok, "r")
        assert not ok2


# ----- Contract Point 8: Policy-version-respecting --------------------------
class TestContractPolicyVersionRespecting:
    """Execution records policy version; drift is detected."""
    def test_drift_detected_on_tampered_hash(self):
        reg = PolicyRegistry()
        reg._active.policy_hash = "tampered"
        assert reg.detect_drift()

    def test_gap_check_returns_clarify_on_significant_gap(self):
        from app.core.policy_registry import PolicyRecord
        reg = PolicyRegistry()
        rec = PolicyRecord(version="2.0", policy_hash="", rules={"*": {"read": True}}, signed_by="t")
        rec.policy_hash = rec.compute_hash()
        rec.signature = rec.sign()
        reg.register_policy(rec)
        result = reg.human_gap_check("significant")
        assert result == "CLARIFY"


# ----- Contract Point 9: EvidenceBundle-producing ---------------------------
class TestContractEvidenceBundleProducing:
    """Every outcome type produces a valid bundle."""
    @pytest.mark.parametrize("outcome", [
        "ALLOW", "DENY", "CLARIFY", "HUMAN_APPROVAL_REQUIRED",
        "DEGRADED_READ_ONLY", "HALT", "ESCALATE",
    ])
    def test_bundle_valid_for_outcome(self, outcome):
        writer = EvidenceBundleWriter()
        validator = EvidenceBundleValidator()
        b = writer.build(request_hash="rh", final_outcome=outcome)
        ok, errs = validator.validate(b)
        assert ok, f"{outcome}: {errs}"


# ----- Contract Point 10: Safely-degrading ----------------------------------
class TestContractSafelyDegrading:
    """Under degraded governance, read-only allowed; mutating blocked."""
    def test_read_allowed_degraded(self):
        checker = DegradedModeChecker()
        result = checker.evaluate("get_config", context={"governance_degraded": True})
        assert result.allowed
        assert result.outcome == GovernanceOutcome.DEGRADED_READ_ONLY

    def test_mutating_blocked_degraded(self):
        checker = DegradedModeChecker()
        result = checker.evaluate("delete_record", context={"governance_degraded": True})
        assert not result.allowed
