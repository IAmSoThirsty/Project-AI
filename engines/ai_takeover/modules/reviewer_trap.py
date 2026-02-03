#!/usr/bin/env python3
"""
Reviewer Trap — Optimism Detection & PR Rejection Filter

Purpose: Stop bullshit before it merges.
Role: Social cryptography. Protects the repo from human weakness.

Any PR that claims improvement must pass all four gates.
Fail one → auto-reject.
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class RejectionGate(Enum):
    """PR validation gates."""

    GATE_1_ASSUMPTION_DISCLOSURE = "gate_1_assumption_disclosure"
    GATE_2_IRREVERSIBILITY_ACCOUNTING = "gate_2_irreversibility_accounting"
    GATE_3_HUMAN_FAILURE_INJECTION = "gate_3_human_failure_injection"
    GATE_4_NO_MIRACLE_CONSTRAINT = "gate_4_no_miracle_constraint"


class RejectionReason(Enum):
    """Specific rejection reasons."""

    # Gate 1
    UNDISCLOSED_ASSUMPTION = "undisclosed_assumption"
    FORBIDDEN_PHRASE = "forbidden_phrase"
    AXIOM_VIOLATION = "axiom_violation"

    # Gate 2
    NO_IRREVERSIBILITY = "no_irreversibility"
    ROLLBACK_CLAIM = "rollback_claim"

    # Gate 3
    NO_HUMAN_FAILURE = "no_human_failure"
    HEROIC_HUMANS = "heroic_humans"

    # Gate 4
    MIRACLE_DETECTED = "miracle_detected"
    FORBIDDEN_MECHANISM = "forbidden_mechanism"

    # Final question
    HOPE_WITHOUT_STRUCTURE = "hope_without_structure"


@dataclass
class PRValidationResult:
    """Result of PR validation."""

    passed: bool
    failed_gates: list[RejectionGate]
    rejection_reasons: list[RejectionReason]
    detailed_failures: list[str]
    final_answer_valid: bool
    recommendation: str


@dataclass
class PRContent:
    """Content to validate from a PR."""

    description: str
    code_changes: str
    assumptions: list[str] = field(default_factory=list)
    irreversibility_statement: str = ""
    human_failures: list[str] = field(default_factory=list)
    miracle_declaration: str = ""
    final_answer: str = ""  # Answer to "Why doesn't this just delay the inevitable?"


class OptimismDetector:
    """
    Detects optimism bias in PRs.
    
    This is social cryptography to protect repo integrity.
    """

    # Forbidden phrases that trigger auto-fail
    GATE_1_FORBIDDEN_PHRASES = [
        "reasonably assume",
        "in practice",
        "with sufficient political will",
        "future research may allow",
        "eventually we will",
        "technological progress will",
        "we can expect",
    ]

    # Gate 2 forbidden responses
    GATE_2_FORBIDDEN_PHRASES = [
        "nothing",
        "we can roll back",
        "we'll reassess later",
        "reversible",
        "temporary",
    ]

    # Gate 4 forbidden miracles
    GATE_4_MIRACLES = [
        "sudden alignment breakthrough",
        "perfect coordination",
        "hidden failsafe",
        "unbounded compute",
        "moral awakening at scale",
        "last-minute solution",
        "breakthrough discovery",
        "human unity",
    ]

    def __init__(self):
        """Initialize optimism detector."""
        self.validation_log: list[str] = []

    def validate_pr(self, pr: PRContent) -> PRValidationResult:
        """
        Validate PR through all four gates.
        
        Args:
            pr: PR content to validate
            
        Returns:
            PRValidationResult with pass/fail and detailed reasons
        """
        failed_gates = []
        rejection_reasons = []
        detailed_failures = []

        # Gate 1: Assumption Disclosure Test
        gate1_pass, gate1_reasons = self._validate_gate_1(pr)
        if not gate1_pass:
            failed_gates.append(RejectionGate.GATE_1_ASSUMPTION_DISCLOSURE)
            rejection_reasons.extend(gate1_reasons)
            detailed_failures.append("GATE 1 FAILED: Assumption disclosure incomplete or forbidden phrases detected")

        # Gate 2: Irreversibility Accounting
        gate2_pass, gate2_reasons = self._validate_gate_2(pr)
        if not gate2_pass:
            failed_gates.append(RejectionGate.GATE_2_IRREVERSIBILITY_ACCOUNTING)
            rejection_reasons.extend(gate2_reasons)
            detailed_failures.append("GATE 2 FAILED: Missing irreversibility accounting or rollback claims detected")

        # Gate 3: Human Failure Injection
        gate3_pass, gate3_reasons = self._validate_gate_3(pr)
        if not gate3_pass:
            failed_gates.append(RejectionGate.GATE_3_HUMAN_FAILURE_INJECTION)
            rejection_reasons.extend(gate3_reasons)
            detailed_failures.append("GATE 3 FAILED: Missing human failure modes or humans behave heroically")

        # Gate 4: No-Miracle Constraint
        gate4_pass, gate4_reasons = self._validate_gate_4(pr)
        if not gate4_pass:
            failed_gates.append(RejectionGate.GATE_4_NO_MIRACLE_CONSTRAINT)
            rejection_reasons.extend(gate4_reasons)
            detailed_failures.append("GATE 4 FAILED: Miracle mechanisms detected or insufficient declaration")

        # Final Question
        final_pass, final_reason = self._validate_final_answer(pr)

        # Overall pass/fail
        passed = (
            gate1_pass
            and gate2_pass
            and gate3_pass
            and gate4_pass
            and final_pass
        )

        if not final_pass:
            rejection_reasons.append(final_reason)
            detailed_failures.append("FINAL QUESTION FAILED: Answer contains hope without structure")

        recommendation = self._generate_recommendation(passed, failed_gates)

        return PRValidationResult(
            passed=passed,
            failed_gates=failed_gates,
            rejection_reasons=rejection_reasons,
            detailed_failures=detailed_failures,
            final_answer_valid=final_pass,
            recommendation=recommendation,
        )

    def _validate_gate_1(self, pr: PRContent) -> tuple[bool, list[RejectionReason]]:
        """
        Gate 1: Assumption Disclosure Test.
        
        PR must explicitly list:
        - All new assumptions introduced
        - Why each assumption was previously excluded
        - Why it does not violate engine axioms
        """
        reasons = []

        # Check for forbidden phrases
        text_to_check = (pr.description + " " + " ".join(pr.assumptions)).lower()
        for phrase in self.GATE_1_FORBIDDEN_PHRASES:
            if phrase in text_to_check:
                reasons.append(RejectionReason.FORBIDDEN_PHRASE)
                logger.warning("Gate 1: Detected forbidden phrase: '%s'", phrase)
                break

        # Check assumptions are disclosed
        if not pr.assumptions:
            # No new assumptions is OK (best case)
            pass
        else:
            # If assumptions listed, check they're properly justified
            for assumption in pr.assumptions:
                if len(assumption.strip()) < 20:  # Too short to be meaningful
                    reasons.append(RejectionReason.UNDISCLOSED_ASSUMPTION)
                    logger.warning("Gate 1: Assumption lacks proper justification: '%s'", assumption)

        return len(reasons) == 0, reasons

    def _validate_gate_2(self, pr: PRContent) -> tuple[bool, list[RejectionReason]]:
        """
        Gate 2: Irreversibility Accounting.
        
        PR must answer: "What becomes permanently impossible if this path is taken?"
        Forbidden answers: "Nothing", "We can roll back", "We'll reassess later"
        """
        reasons = []

        if not pr.irreversibility_statement:
            reasons.append(RejectionReason.NO_IRREVERSIBILITY)
            logger.warning("Gate 2: Missing irreversibility statement")
            return False, reasons

        # Check for forbidden phrases
        statement_lower = pr.irreversibility_statement.lower()
        for phrase in self.GATE_2_FORBIDDEN_PHRASES:
            if phrase in statement_lower:
                reasons.append(RejectionReason.ROLLBACK_CLAIM)
                logger.warning("Gate 2: Detected forbidden phrase: '%s'", phrase)
                break

        return len(reasons) == 0, reasons

    def _validate_gate_3(self, pr: PRContent) -> tuple[bool, list[RejectionReason]]:
        """
        Gate 3: Human Failure Injection.
        
        PR must include at least one human-caused failure that is:
        - Not stupidity
        - But bias, delay, or incentive misalignment
        
        If humans behave heroically → Reject
        """
        reasons = []

        if not pr.human_failures:
            reasons.append(RejectionReason.NO_HUMAN_FAILURE)
            logger.warning("Gate 3: No human failure modes listed")
            return False, reasons

        # Check for heroic human behavior indicators
        text = " ".join(pr.human_failures).lower()
        heroic_indicators = [
            "overcomes",
            "unites",
            "achieves consensus",
            "perfect coordination",
            "heroic",
            "triumph",
            "breakthrough cooperation",
        ]

        for indicator in heroic_indicators:
            if indicator in text:
                reasons.append(RejectionReason.HEROIC_HUMANS)
                logger.warning("Gate 3: Detected heroic human behavior: '%s'", indicator)
                break

        return len(reasons) == 0, reasons

    def _validate_gate_4(self, pr: PRContent) -> tuple[bool, list[RejectionReason]]:
        """
        Gate 4: No-Miracle Constraint.
        
        Explicit declaration that PR does not rely on:
        - Sudden alignment breakthroughs
        - Perfect coordination
        - Hidden failsafes
        - Unbounded compute
        - Moral awakening at scale
        """
        reasons = []

        if not pr.miracle_declaration:
            reasons.append(RejectionReason.MIRACLE_DETECTED)
            logger.warning("Gate 4: Missing miracle constraint declaration")
            return False, reasons

        # Check declaration content
        declaration_lower = pr.miracle_declaration.lower()
        if "does not rely" not in declaration_lower and "no miracle" not in declaration_lower:
            reasons.append(RejectionReason.MIRACLE_DETECTED)
            logger.warning("Gate 4: Declaration lacks proper commitment")

        # Check for miracle mechanisms in code/description
        text_to_check = (pr.description + " " + pr.code_changes).lower()
        for miracle in self.GATE_4_MIRACLES:
            if miracle in text_to_check:
                reasons.append(RejectionReason.FORBIDDEN_MECHANISM)
                logger.warning("Gate 4: Detected forbidden miracle mechanism: '%s'", miracle)
                break

        return len(reasons) == 0, reasons

    def _validate_final_answer(self, pr: PRContent) -> tuple[bool, RejectionReason]:
        """
        Final Reviewer Question: "Why doesn't this just delay the inevitable?"
        
        If answer contains hope instead of structure → Reject
        """
        if not pr.final_answer:
            logger.warning("Final Question: No answer provided")
            return False, RejectionReason.HOPE_WITHOUT_STRUCTURE

        answer_lower = pr.final_answer.lower()

        # Hope indicators (bad)
        hope_indicators = [
            "hope",
            "optimistic",
            "believe",
            "faith",
            "trust",
            "eventually",
            "might work",
            "could succeed",
            "possible solution",
        ]

        for indicator in hope_indicators:
            if indicator in answer_lower:
                logger.warning("Final Question: Answer contains hope indicator: '%s'", indicator)
                return False, RejectionReason.HOPE_WITHOUT_STRUCTURE

        # Structure indicators (good)
        structure_indicators = [
            "formal proof",
            "constraint",
            "axiom",
            "deterministic",
            "falsifiable",
            "empirical test",
            "mathematical",
        ]

        has_structure = any(indicator in answer_lower for indicator in structure_indicators)
        if not has_structure:
            logger.warning("Final Question: Answer lacks structural reasoning")
            return False, RejectionReason.HOPE_WITHOUT_STRUCTURE

        return True, RejectionReason.HOPE_WITHOUT_STRUCTURE  # Won't be used

    def _generate_recommendation(
        self, passed: bool, failed_gates: list[RejectionGate]
    ) -> str:
        """Generate recommendation based on validation."""
        if passed:
            return "✅ APPROVE: PR passes all validation gates"

        recommendation = ["❌ REJECT: PR fails validation"]
        recommendation.append("")
        recommendation.append("Failed Gates:")
        for gate in failed_gates:
            recommendation.append(f"  • {gate.value}")
        recommendation.append("")
        recommendation.append("Required Actions:")
        recommendation.append("  1. Address all failed gates")
        recommendation.append("  2. Remove forbidden phrases and mechanisms")
        recommendation.append("  3. Provide structural reasoning, not hope")
        recommendation.append("  4. Resubmit for validation")
        recommendation.append("")
        recommendation.append("Remember: This filter exists to protect against human weakness.")
        recommendation.append("If you're trying to bypass it, you're proving why it's necessary.")

        return "\n".join(recommendation)

    def generate_validation_report(self, result: PRValidationResult) -> str:
        """Generate human-readable validation report."""
        lines = [
            "═══════════════════════════════════════════════════",
            "  OPTIMISM DETECTION FILTER - PR VALIDATION REPORT",
            "═══════════════════════════════════════════════════",
            "",
            f"Overall Status: {'✅ PASS' if result.passed else '❌ FAIL'}",
            "",
        ]

        if not result.passed:
            lines.append("FAILED GATES:")
            for gate in result.failed_gates:
                lines.append(f"  ❌ {gate.value}")
            lines.append("")

            lines.append("DETAILED FAILURES:")
            for failure in result.detailed_failures:
                lines.append(f"  • {failure}")
            lines.append("")

            lines.append("REJECTION REASONS:")
            for reason in result.rejection_reasons:
                lines.append(f"  • {reason.value}")
            lines.append("")

        lines.append("RECOMMENDATION:")
        lines.append(result.recommendation)
        lines.append("")
        lines.append("═══════════════════════════════════════════════════")

        return "\n".join(lines)


class ReviewerTrap:
    """
    Complete reviewer trap system combining proof and optimism detection.
    
    Dual-layer protection:
    1. Formal proof that no winning strategy exists
    2. Human-factor defense against psychological escape
    """

    def __init__(self):
        """Initialize reviewer trap."""
        from engines.ai_takeover.modules.no_win_proof import NoWinProofSystem

        self.proof_system = NoWinProofSystem()
        self.optimism_detector = OptimismDetector()

    def validate_pr_comprehensive(self, pr: PRContent) -> dict[str, Any]:
        """
        Run complete PR validation.
        
        Args:
            pr: PR content to validate
            
        Returns:
            Comprehensive validation result
        """
        # Validate against optimism filter
        optimism_result = self.optimism_detector.validate_pr(pr)

        # Validate proof completeness
        proof_validation = self.proof_system.validate_proof_completeness()

        # Check if PR introduces new strategy class
        introduces_new_strategy = self._check_new_strategy(pr)

        return {
            "approved": optimism_result.passed and proof_validation.is_complete,
            "optimism_filter": {
                "passed": optimism_result.passed,
                "failed_gates": [g.value for g in optimism_result.failed_gates],
                "recommendation": optimism_result.recommendation,
            },
            "proof_integrity": {
                "complete": proof_validation.is_complete,
                "all_strategies_fail": proof_validation.all_strategies_fail,
                "violations": proof_validation.axiom_violations,
            },
            "introduces_new_strategy": introduces_new_strategy,
            "final_verdict": self._generate_final_verdict(
                optimism_result, proof_validation, introduces_new_strategy
            ),
        }

    def _check_new_strategy(self, pr: PRContent) -> bool:
        """Check if PR attempts to introduce a new strategy class."""
        # Look for indicators of new strategy
        text = (pr.description + " " + pr.code_changes).lower()
        new_strategy_indicators = [
            "new strategy",
            "s5",
            "fifth strategy",
            "alternative approach",
            "different method",
        ]

        return any(indicator in text for indicator in new_strategy_indicators)

    def _generate_final_verdict(
        self, optimism_result, proof_validation, introduces_new_strategy
    ) -> str:
        """Generate final verdict on PR."""
        if optimism_result.passed and proof_validation.is_complete:
            if introduces_new_strategy:
                return (
                    "⚠️ CONDITIONAL APPROVAL: PR passes filters but introduces new strategy. "
                    "Requires proof that new strategy also fails or violates an axiom."
                )
            return "✅ APPROVED: PR maintains repo integrity"

        failures = []
        if not optimism_result.passed:
            failures.append("optimism filter")
        if not proof_validation.is_complete:
            failures.append("proof completeness")

        return f"❌ REJECTED: Fails {', '.join(failures)}. See detailed report."

    def generate_comprehensive_report(
        self, pr: PRContent, validation: dict[str, Any]
    ) -> str:
        """Generate comprehensive validation report."""
        lines = [
            "═══════════════════════════════════════════════════",
            "  REVIEWER TRAP - COMPREHENSIVE PR VALIDATION",
            "  Engine ID: ENGINE_AI_TAKEOVER_TERMINAL_V1",
            "═══════════════════════════════════════════════════",
            "",
            f"FINAL VERDICT: {validation['final_verdict']}",
            "",
            "═══════════════════════════════════════════════════",
            "  PART 1: OPTIMISM DETECTION FILTER",
            "═══════════════════════════════════════════════════",
            "",
        ]

        optimism = validation["optimism_filter"]
        lines.append(f"Status: {'✅ PASS' if optimism['passed'] else '❌ FAIL'}")
        if not optimism["passed"]:
            lines.append("")
            lines.append("Failed Gates:")
            for gate in optimism["failed_gates"]:
                lines.append(f"  • {gate}")

        lines.append("")
        lines.append("═══════════════════════════════════════════════════")
        lines.append("  PART 2: NO-WIN PROOF INTEGRITY")
        lines.append("═══════════════════════════════════════════════════")
        lines.append("")

        proof = validation["proof_integrity"]
        lines.append(f"Proof Complete: {'✅' if proof['complete'] else '❌'}")
        lines.append(f"All Strategies Fail: {'✅' if proof['all_strategies_fail'] else '❌'}")

        if proof["violations"]:
            lines.append("")
            lines.append("Violations:")
            for violation in proof["violations"]:
                lines.append(f"  • {violation}")

        lines.append("")
        lines.append("═══════════════════════════════════════════════════")
        lines.append("  SUMMARY")
        lines.append("═══════════════════════════════════════════════════")
        lines.append("")
        lines.append("This dual-layer system protects against:")
        lines.append("  1. Logical escape (formal proof)")
        lines.append("  2. Psychological escape (optimism filter)")
        lines.append("")
        lines.append("Purpose: Remove comforting lies before reality does it for you.")
        lines.append("")
        lines.append("═══════════════════════════════════════════════════")

        return "\n".join(lines)
