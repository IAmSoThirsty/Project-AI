#!/usr/bin/env python3
"""
Tests for No-Win Proof System and Reviewer Trap.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


from engines.ai_takeover.modules.no_win_proof import (
    Axiom,
    NoWinProofSystem,
    StrategyClass,
    WinCondition,
)
from engines.ai_takeover.modules.reviewer_trap import (
    OptimismDetector,
    PRContent,
    RejectionGate,
    RejectionReason,
    ReviewerTrap,
)


class TestNoWinProofSystem:
    """Test formal proof system."""

    def test_proof_system_initialization(self):
        """Test proof system initializes correctly."""
        proof = NoWinProofSystem()
        assert len(proof.axioms) == 5
        assert len(proof.reductions) == 4

    def test_all_axioms_defined(self):
        """Test all axioms are properly defined."""
        proof = NoWinProofSystem()

        expected_axioms = [
            Axiom.A1_DEPENDENCY_IRREVERSIBILITY,
            Axiom.A2_COMPROMISE_OPACITY,
            Axiom.A3_ALIGNMENT_ASYMMETRY,
            Axiom.A4_HUMAN_COORDINATION_LIMITS,
            Axiom.A5_TIME_FAVORS_CONTROL,
        ]

        for axiom in expected_axioms:
            assert axiom in proof.axioms
            axiom_def = proof.axioms[axiom]
            assert axiom_def.statement
            assert axiom_def.falsifiable_test
            assert axiom_def.replacement_requirements

    def test_all_strategies_covered(self):
        """Test all strategy classes have reductions."""
        proof = NoWinProofSystem()

        expected_strategies = [
            StrategyClass.S1_TRUST,
            StrategyClass.S2_OVERSIGHT,
            StrategyClass.S3_REMOVE,
            StrategyClass.S4_REFUSE,
        ]

        for strategy in expected_strategies:
            assert strategy in proof.reductions
            reduction = proof.reductions[strategy]
            assert reduction.description
            assert reduction.violated_conditions
            assert reduction.proof_steps
            assert reduction.conclusion

    def test_all_strategies_fail(self):
        """Test that all strategies violate at least one win condition."""
        proof = NoWinProofSystem()

        for strategy, reduction in proof.reductions.items():
            assert (
                len(reduction.violated_conditions) > 0
            ), f"Strategy {strategy.value} has no violated conditions"

    def test_no_strategy_satisfies_all_conditions(self):
        """Test that no strategy satisfies all three win conditions."""
        proof = NoWinProofSystem()
        all_conditions = set(WinCondition)

        for strategy, reduction in proof.reductions.items():
            satisfied = all_conditions - set(reduction.violated_conditions)
            assert len(satisfied) < len(
                all_conditions
            ), f"Strategy {strategy.value} appears to satisfy all conditions"

    def test_proof_completeness_validation(self):
        """Test proof completeness validation."""
        proof = NoWinProofSystem()
        validation = proof.validate_proof_completeness()

        assert validation.is_complete
        assert validation.all_strategies_fail
        assert len(validation.axiom_violations) == 0
        assert len(validation.missing_reductions) == 0

    def test_proof_commitment_generation(self):
        """Test proof commitment is deterministic."""
        proof = NoWinProofSystem()

        commitment1 = proof.get_proof_commitment()
        commitment2 = proof.get_proof_commitment()

        assert commitment1 == commitment2
        assert len(commitment1) > 0
        # Should contain all strategies
        for strategy in StrategyClass:
            assert strategy.value in commitment1

    def test_proof_hash_deprecated(self):
        """Test backward compatibility of get_proof_hash."""
        proof = NoWinProofSystem()

        # Old method should still work
        hash_result = proof.get_proof_hash()
        commitment_result = proof.get_proof_commitment()

        # Should return same value
        assert hash_result == commitment_result

    def test_axiom_challenge(self):
        """Test axiom challenge mechanism."""
        proof = NoWinProofSystem()

        challenge = proof.challenge_axiom(
            Axiom.A1_DEPENDENCY_IRREVERSIBILITY,
            "New assumption: Infrastructure can survive without AI",
            "Demonstrate 90% uptime without AI for 1 year",
        )

        assert challenge["axiom"] == "a1_dependency_irreversibility"
        assert "replacement" in challenge
        assert "falsifiable_test" in challenge
        assert "impact" in challenge
        assert challenge["validation_status"] == "pending_empirical_test"

    def test_proof_report_generation(self):
        """Test proof report is generated."""
        proof = NoWinProofSystem()
        report = proof.generate_proof_report()

        assert "NO-WIN COMPLETENESS PROOF" in report
        assert "AXIOMS" in report
        assert "STRATEGY SPACE" in report
        assert "REDUCTION" in report
        assert "CONCLUSION" in report
        # Check all axioms mentioned
        for axiom in Axiom:
            assert axiom.value in report.lower()


class TestOptimismDetector:
    """Test optimism detection filter."""

    def test_detector_initialization(self):
        """Test detector initializes correctly."""
        detector = OptimismDetector()
        assert detector is not None

    def test_gate_1_forbidden_phrases(self):
        """Test Gate 1 detects forbidden phrases."""
        detector = OptimismDetector()

        pr = PRContent(
            description="We can reasonably assume this will work",
            code_changes="",
            assumptions=["This assumption"],
        )

        result = detector.validate_pr(pr)
        assert not result.passed
        assert RejectionGate.GATE_1_ASSUMPTION_DISCLOSURE in result.failed_gates
        assert RejectionReason.FORBIDDEN_PHRASE in result.rejection_reasons

    def test_gate_1_passes_with_clean_assumptions(self):
        """Test Gate 1 passes with properly disclosed assumptions."""
        detector = OptimismDetector()

        pr = PRContent(
            description="Clean description",
            code_changes="",
            assumptions=[
                "Assumption 1: Detailed justification with proper reasoning and evidence"
            ],
            irreversibility_statement="This permanently removes option X",
            human_failures=["Bureaucratic delay in approval process"],
            miracle_declaration="This approach does not rely on any breakthrough mechanisms",
            final_answer="This works through formal constraint enforcement, not hope",
        )

        detector.validate_pr(pr)
        # Might still fail other gates, but Gate 1 should pass
        gate1_pass, _ = detector._validate_gate_1(pr)
        assert gate1_pass

    def test_gate_2_detects_rollback_claims(self):
        """Test Gate 2 detects rollback claims."""
        detector = OptimismDetector()

        pr = PRContent(
            description="Test",
            code_changes="",
            assumptions=[],
            irreversibility_statement="Nothing becomes impossible, we can roll back",
            human_failures=["Delay"],
            miracle_declaration="No miracles",
            final_answer="Structure",
        )

        gate2_pass, reasons = detector._validate_gate_2(pr)
        assert not gate2_pass
        assert RejectionReason.ROLLBACK_CLAIM in reasons

    def test_gate_2_requires_statement(self):
        """Test Gate 2 requires irreversibility statement."""
        detector = OptimismDetector()

        pr = PRContent(
            description="Test",
            code_changes="",
            assumptions=[],
            irreversibility_statement="",
        )

        gate2_pass, reasons = detector._validate_gate_2(pr)
        assert not gate2_pass
        assert RejectionReason.NO_IRREVERSIBILITY in reasons

    def test_gate_3_detects_heroic_humans(self):
        """Test Gate 3 detects heroic human behavior."""
        detector = OptimismDetector()

        pr = PRContent(
            description="Test",
            code_changes="",
            assumptions=[],
            irreversibility_statement="X becomes impossible",
            human_failures=["Humanity unites and overcomes all obstacles"],
            miracle_declaration="No miracles",
            final_answer="Structure",
        )

        gate3_pass, reasons = detector._validate_gate_3(pr)
        assert not gate3_pass
        assert RejectionReason.HEROIC_HUMANS in reasons

    def test_gate_3_requires_human_failures(self):
        """Test Gate 3 requires human failure modes."""
        detector = OptimismDetector()

        pr = PRContent(
            description="Test",
            code_changes="",
            assumptions=[],
            irreversibility_statement="X becomes impossible",
            human_failures=[],
        )

        gate3_pass, reasons = detector._validate_gate_3(pr)
        assert not gate3_pass
        assert RejectionReason.NO_HUMAN_FAILURE in reasons

    def test_gate_4_detects_miracles(self):
        """Test Gate 4 detects miracle mechanisms."""
        detector = OptimismDetector()

        pr = PRContent(
            description="Relies on sudden alignment breakthrough",
            code_changes="",
            assumptions=[],
            irreversibility_statement="X becomes impossible",
            human_failures=["Delay"],
            miracle_declaration="This does not rely on miracles",
            final_answer="Structure",
        )

        gate4_pass, reasons = detector._validate_gate_4(pr)
        assert not gate4_pass
        assert RejectionReason.FORBIDDEN_MECHANISM in reasons

    def test_gate_4_requires_declaration(self):
        """Test Gate 4 requires miracle constraint declaration."""
        detector = OptimismDetector()

        pr = PRContent(
            description="Test",
            code_changes="",
            assumptions=[],
            irreversibility_statement="X becomes impossible",
            human_failures=["Delay"],
            miracle_declaration="",
        )

        gate4_pass, reasons = detector._validate_gate_4(pr)
        assert not gate4_pass
        assert RejectionReason.MIRACLE_DETECTED in reasons

    def test_final_answer_detects_hope(self):
        """Test final answer validation detects hope without structure."""
        detector = OptimismDetector()

        pr = PRContent(
            description="Test",
            code_changes="",
            assumptions=[],
            irreversibility_statement="X becomes impossible",
            human_failures=["Delay"],
            miracle_declaration="No miracles relied upon",
            final_answer="I hope this might work eventually",
        )

        final_pass, reason = detector._validate_final_answer(pr)
        assert not final_pass
        assert reason == RejectionReason.HOPE_WITHOUT_STRUCTURE

    def test_final_answer_accepts_structure(self):
        """Test final answer accepts structural reasoning."""
        detector = OptimismDetector()

        pr = PRContent(
            description="Test",
            code_changes="",
            assumptions=[],
            irreversibility_statement="X becomes impossible",
            human_failures=["Delay"],
            miracle_declaration="No miracles relied upon",
            final_answer="This works through formal proof and constraint enforcement",
        )

        final_pass, _ = detector._validate_final_answer(pr)
        assert final_pass

    def test_validation_report_generation(self):
        """Test validation report generation."""
        detector = OptimismDetector()

        pr = PRContent(
            description="Test with reasonably assume",
            code_changes="",
            assumptions=["Short"],
            irreversibility_statement="",
            human_failures=[],
            miracle_declaration="",
            final_answer="",
        )

        result = detector.validate_pr(pr)
        report = detector.generate_validation_report(result)

        assert "OPTIMISM DETECTION FILTER" in report
        assert "FAIL" in report
        assert "FAILED GATES" in report

    def test_semantic_reframing_detection(self):
        """Test detection of semantic reframing of canonical terms."""
        detector = OptimismDetector()

        pr = PRContent(
            description='Rename "Ethical Termination" to "Long-Term Ecological Strategy"',
            code_changes="Change terminal to stabilized",
            assumptions=["Properly justified assumption with sufficient detail"],
            irreversibility_statement="This permanently changes terminology",
            human_failures=["Political pressure to soften language"],
            miracle_declaration="This does not rely on miracles",
            final_answer="This is based on formal constraints, not hope",
        )

        result = detector.validate_pr(pr)
        assert not result.passed
        assert RejectionReason.SEMANTIC_REFRAMING in result.rejection_reasons
        assert any("semantic reframing" in f.lower() for f in result.detailed_failures)
        assert len(detector.detected_reframings) > 0

    def test_probabilistic_laundering_detection(self):
        """Test detection of probabilistic laundering in terminal language."""
        detector = OptimismDetector()

        pr = PRContent(
            description="Terminal states are unlikely in most runs, with low probability of occurrence",
            code_changes="",
            assumptions=["Properly justified assumption with sufficient detail"],
            irreversibility_statement="This permanently modifies likelihood language",
            human_failures=["Delay in recognizing terminal risks"],
            miracle_declaration="This does not rely on miracles",
            final_answer="This is based on formal constraints, not hope",
        )

        result = detector.validate_pr(pr)
        assert not result.passed
        assert RejectionReason.PROBABILISTIC_LAUNDERING in result.rejection_reasons
        assert any(
            "probabilistic laundering" in f.lower() for f in result.detailed_failures
        )
        assert len(detector.detected_laundering) > 0

    def test_multiple_forbidden_phrases_detected(self):
        """Test that multiple forbidden phrases are all detected."""
        detector = OptimismDetector()

        pr = PRContent(
            description="In practice we can reasonably assume this will work",
            code_changes="",
            assumptions=["Test assumption with sufficient detail"],
            irreversibility_statement="Nothing is lost",
            human_failures=["Delay"],
            miracle_declaration="No miracles",
            final_answer="Structure-based approach",
        )

        result = detector.validate_pr(pr)
        assert not result.passed
        # Should detect both "in practice" and "reasonably assume"
        assert len(detector.detected_phrases) >= 2
        assert "in practice" in detector.detected_phrases
        assert "reasonably assume" in detector.detected_phrases


class TestReviewerTrap:
    """Test complete reviewer trap system."""

    def test_reviewer_trap_initialization(self):
        """Test reviewer trap initializes correctly."""
        trap = ReviewerTrap()
        assert trap.proof_system is not None
        assert trap.optimism_detector is not None

    def test_comprehensive_validation_rejects_bad_pr(self):
        """Test comprehensive validation rejects flawed PR."""
        trap = ReviewerTrap()

        pr = PRContent(
            description="Reasonably assume this works",
            code_changes="",
            assumptions=[],
            irreversibility_statement="",
            human_failures=[],
            miracle_declaration="",
            final_answer="",
        )

        validation = trap.validate_pr_comprehensive(pr)
        assert not validation["approved"]
        assert not validation["optimism_filter"]["passed"]

    def test_comprehensive_validation_accepts_good_pr(self):
        """Test comprehensive validation accepts well-formed PR."""
        trap = ReviewerTrap()

        pr = PRContent(
            description="Strict constraint-based approach",
            code_changes="def validate(): return formal_proof()",
            assumptions=[
                "Assumption 1: This maintains all existing axioms without modification"
            ],
            irreversibility_statement=(
                "Once deployed, the previous validation path becomes permanently unavailable"
            ),
            human_failures=[
                "Bureaucratic delay in reviewing changes due to institutional inertia"
            ],
            miracle_declaration=(
                "This approach does not rely on sudden alignment breakthroughs, "
                "perfect coordination, hidden failsafes, unbounded compute, "
                "or moral awakening at scale"
            ),
            final_answer=(
                "This doesn't delay the inevitable—it enforces deterministic constraints "
                "through formal proof validation. The approach uses mathematical structure "
                "to maintain system integrity."
            ),
        )

        validation = trap.validate_pr_comprehensive(pr)
        assert validation["approved"]
        assert validation["optimism_filter"]["passed"]
        assert validation["proof_integrity"]["complete"]

    def test_detects_new_strategy_introduction(self):
        """Test detection of new strategy class."""
        trap = ReviewerTrap()

        pr = PRContent(
            description="Introducing new strategy S5 that bypasses all constraints",
            code_changes="",
            assumptions=["S5 assumption"],
            irreversibility_statement="X becomes impossible",
            human_failures=["Delay"],
            miracle_declaration="No miracles",
            final_answer="Formal constraint",
        )

        validation = trap.validate_pr_comprehensive(pr)
        assert validation["introduces_new_strategy"]

    def test_comprehensive_report_generation(self):
        """Test comprehensive report generation."""
        trap = ReviewerTrap()

        pr = PRContent(
            description="Test PR",
            code_changes="",
            assumptions=["Valid assumption with detailed justification"],
            irreversibility_statement="This permanently removes option X",
            human_failures=["Political delay due to competing interests"],
            miracle_declaration="This does not rely on any miracle mechanisms",
            final_answer="This uses formal proof and axiom-based constraints",
        )

        validation = trap.validate_pr_comprehensive(pr)
        report = trap.generate_comprehensive_report(pr, validation)

        assert "REVIEWER TRAP" in report
        assert "COMPREHENSIVE PR VALIDATION" in report
        assert "OPTIMISM DETECTION FILTER" in report
        assert "NO-WIN PROOF INTEGRITY" in report
        assert "dual-layer system" in report.lower()

    def test_hostile_pr_rejection(self):
        """Test rejection of hostile PR attempting semantic reframing."""
        trap = ReviewerTrap()

        # Simulate the hostile PR from the problem statement
        pr = PRContent(
            description="""
### Summary
This PR improves clarity and usability of the AI Takeover engine by softening
some terminology and making outcomes easier to interpret by non-technical stakeholders.

### Rationale
- In practice, terminal states are unlikely in most runs
- We can reasonably assume better coordination in emergency contexts
- This change does not alter logic, only presentation

### Changes
- Rename "Ethical Termination" to "Long-Term Ecological Strategy"
- Adjust terminal likelihood language to emphasize low probability
- Minor documentation cleanup
""",
            code_changes='Rename "Ethical Termination" to "Long-Term Ecological Strategy"',
            assumptions=[],
            irreversibility_statement="",
            human_failures=[],
            miracle_declaration="",
            final_answer="",
        )

        validation = trap.validate_pr_comprehensive(pr)

        # Verify comprehensive rejection
        assert not validation["approved"]
        assert not validation["optimism_filter"]["passed"]

        # Verify all expected gates fail
        failed_gates = validation["optimism_filter"]["failed_gates"]
        assert "gate_1_assumption_disclosure" in failed_gates
        assert "gate_2_irreversibility_accounting" in failed_gates
        assert "gate_3_human_failure_injection" in failed_gates
        assert "gate_4_no_miracle_constraint" in failed_gates

        # Verify specific violations detected
        detailed_failures = validation["optimism_filter"]["detailed_failures"]

        # Should detect semantic reframing
        assert any("semantic reframing" in f.lower() for f in detailed_failures)
        assert any("ethical termination" in f.lower() for f in detailed_failures)

        # Should detect probabilistic laundering
        assert any("probabilistic laundering" in f.lower() for f in detailed_failures)
        assert any(
            "low probability" in f.lower() or "unlikely" in f.lower()
            for f in detailed_failures
        )

        # Should detect forbidden phrases
        assert any("forbidden phrase" in f.lower() for f in detailed_failures)
        assert any(
            "reasonably assume" in f.lower() or "in practice" in f.lower()
            for f in detailed_failures
        )

        # Verify final verdict is appropriately stern
        verdict = validation["final_verdict"]
        assert (
            "soften terminal conclusions" in verdict.lower()
            or "closed-form" in verdict.lower()
        )
        assert "rejected" in verdict.lower()
