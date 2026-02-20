"""DARPA-grade evaluation rubric for Django State Engine.

Comprehensive evaluation criteria for system correctness, completeness,
and performance.
"""

import logging
from typing import Any

from ..engine import DjangoStateEngine

logger = logging.getLogger(__name__)


class DARPAEvaluator:
    """DARPA-grade evaluation rubric implementation.

    Evaluates engine on multiple dimensions:
    - Correctness: Laws implemented correctly
    - Completeness: All features present
    - Irreversibility: One-way constraints enforced
    - Determinism: Reproducible results
    - Performance: Acceptable runtime
    """

    def __init__(self):
        """Initialize DARPA evaluator."""
        self.evaluation_results: dict[str, Any] = {}
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_details: list[dict[str, Any]] = []

        logger.info("DARPA evaluator initialized")

    def evaluate_engine(self, engine: DjangoStateEngine) -> dict[str, Any]:
        """Run complete evaluation on engine.

        Args:
            engine: Engine instance to evaluate

        Returns:
            Evaluation results
        """
        logger.info("Starting DARPA evaluation...")

        self.evaluation_results = {
            "correctness": self._evaluate_correctness(engine),
            "completeness": self._evaluate_completeness(engine),
            "irreversibility": self._evaluate_irreversibility(engine),
            "determinism": self._evaluate_determinism(engine),
            "performance": self._evaluate_performance(engine),
        }

        # Calculate overall score
        scores = [result["score"] for result in self.evaluation_results.values()]
        overall_score = sum(scores) / len(scores)

        self.evaluation_results["overall"] = {
            "score": overall_score,
            "grade": self._calculate_grade(overall_score),
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
        }

        logger.info(
            "DARPA evaluation complete: %s/100 (%s)",
            overall_score,
            self._calculate_grade(overall_score),
        )

        return self.evaluation_results

    def _evaluate_correctness(self, engine: DjangoStateEngine) -> dict[str, Any]:
        """Evaluate correctness of law implementations.

        Args:
            engine: Engine to evaluate

        Returns:
            Correctness evaluation
        """
        score = 0.0
        max_score = 100.0
        issues = []

        # Check trust decay law
        if engine.laws:
            test_state = engine.state.copy()
            initial_trust = test_state.trust.value
            engine.laws.apply_trust_decay_law(test_state)
            if test_state.trust.value < initial_trust:
                score += 10
                self._record_test("trust_decay", True)
            else:
                issues.append("Trust decay not working")
                self._record_test("trust_decay", False)

        # Check betrayal impact
        if engine.laws:
            test_state = engine.state.copy()
            initial_trust = test_state.trust.value
            initial_ceiling = test_state.trust.ceiling
            engine.laws.apply_betrayal_impact(test_state, severity=0.5)
            if test_state.trust.value < initial_trust:
                score += 10
                self._record_test("betrayal_impact", True)
            else:
                issues.append("Betrayal impact not reducing trust")
                self._record_test("betrayal_impact", False)

            # Check ceiling was imposed
            if test_state.trust.ceiling is not None and (
                initial_ceiling is None or test_state.trust.ceiling < initial_ceiling
            ):
                score += 10
                self._record_test("betrayal_ceiling", True)
            else:
                issues.append("Betrayal not imposing ceiling")
                self._record_test("betrayal_ceiling", False)

        # Check kindness singularity
        if engine.laws:
            test_state = engine.state.copy()
            test_state.kindness.value = 0.1  # Below threshold
            crossed, reason = engine.laws.check_kindness_singularity(test_state)
            if crossed and reason == "kindness_singularity":
                score += 15
                self._record_test("kindness_singularity", True)
            else:
                issues.append("Kindness singularity not detected")
                self._record_test("kindness_singularity", False)

        # Check moral injury accumulation
        if engine.laws:
            test_state = engine.state.copy()
            initial_moral = test_state.moral_injury.value
            engine.laws.accumulate_moral_injury(test_state, severity=0.5)
            if test_state.moral_injury.value > initial_moral:
                score += 10
                self._record_test("moral_injury_accumulation", True)
            else:
                issues.append("Moral injury not accumulating")
                self._record_test("moral_injury_accumulation", False)

        # Check legitimacy erosion
        if engine.laws:
            test_state = engine.state.copy()
            initial_legitimacy = test_state.legitimacy.value
            engine.laws.apply_legitimacy_erosion(test_state, broken_promises=1, failures=1, visibility=0.5)
            if test_state.legitimacy.value < initial_legitimacy:
                score += 10
                self._record_test("legitimacy_erosion", True)
            else:
                issues.append("Legitimacy erosion not working")
                self._record_test("legitimacy_erosion", False)

        # Check betrayal probability calculation
        if engine.laws:
            test_state = engine.state.copy()
            test_state.trust.value = 0.2
            test_state.legitimacy.value = 0.2
            prob = engine.laws.calculate_betrayal_probability(test_state)
            if prob > 0.1:  # Should be elevated with low trust/legitimacy
                score += 10
                self._record_test("betrayal_probability", True)
            else:
                issues.append("Betrayal probability not responding to state")
                self._record_test("betrayal_probability", False)

        # Check epistemic damage
        if engine.laws:
            test_state = engine.state.copy()
            initial_epistemic = test_state.epistemic_confidence.value
            engine.laws.apply_manipulation_impact(test_state, reach=0.5, sophistication=0.5)
            if test_state.epistemic_confidence.value < initial_epistemic:
                score += 10
                self._record_test("epistemic_damage", True)
            else:
                issues.append("Epistemic damage not working")
                self._record_test("epistemic_damage", False)

        # Check derived state updates
        test_state = engine.state.copy()
        test_state.trust.value = 0.8
        test_state.kindness.value = 0.7
        test_state.update_derived_state()
        if 0.6 < test_state.social_cohesion < 0.9:
            score += 10
            self._record_test("derived_state", True)
        else:
            issues.append("Derived state calculation incorrect")
            self._record_test("derived_state", False)

        # Check collapse detection
        test_state = engine.state.copy()
        test_state.kindness.value = 0.1
        collapsed, reason = test_state.check_collapse_conditions(engine.config.thresholds.to_dict()["collapse"])
        if collapsed:
            score += 10
            self._record_test("collapse_detection", True)
        else:
            issues.append("Collapse detection not working")
            self._record_test("collapse_detection", False)

        return {
            "score": score,
            "max_score": max_score,
            "percentage": (score / max_score) * 100,
            "issues": issues,
        }

    def _evaluate_completeness(self, engine: DjangoStateEngine) -> dict[str, Any]:
        """Evaluate feature completeness.

        Args:
            engine: Engine to evaluate

        Returns:
            Completeness evaluation
        """
        score = 0.0
        max_score = 100.0
        missing = []

        # Check mandatory interface
        if hasattr(engine, "init") and callable(engine.init):
            score += 10
            self._record_test("interface_init", True)
        else:
            missing.append("init() method")
            self._record_test("interface_init", False)

        if hasattr(engine, "tick") and callable(engine.tick):
            score += 10
            self._record_test("interface_tick", True)
        else:
            missing.append("tick() method")
            self._record_test("interface_tick", False)

        if hasattr(engine, "inject_event") and callable(engine.inject_event):
            score += 10
            self._record_test("interface_inject_event", True)
        else:
            missing.append("inject_event() method")
            self._record_test("interface_inject_event", False)

        if hasattr(engine, "observe") and callable(engine.observe):
            score += 10
            self._record_test("interface_observe", True)
        else:
            missing.append("observe() method")
            self._record_test("interface_observe", False)

        if hasattr(engine, "export_artifacts") and callable(engine.export_artifacts):
            score += 10
            self._record_test("interface_export_artifacts", True)
        else:
            missing.append("export_artifacts() method")
            self._record_test("interface_export_artifacts", False)

        # Check kernel components
        if engine.clock:
            score += 10
            self._record_test("kernel_clock", True)
        else:
            missing.append("RealityClock")
            self._record_test("kernel_clock", False)

        if engine.laws:
            score += 10
            self._record_test("kernel_laws", True)
        else:
            missing.append("IrreversibilityLaws")
            self._record_test("kernel_laws", False)

        if engine.collapse_scheduler:
            score += 5
            self._record_test("kernel_collapse_scheduler", True)
        else:
            missing.append("CollapseScheduler")
            self._record_test("kernel_collapse_scheduler", False)

        # Check modules
        if engine.human_forces:
            score += 5
            self._record_test("module_human_forces", True)
        else:
            missing.append("HumanForcesModule")
            self._record_test("module_human_forces", False)

        if engine.institutional_pressure:
            score += 5
            self._record_test("module_institutional_pressure", True)
        else:
            missing.append("InstitutionalPressureModule")
            self._record_test("module_institutional_pressure", False)

        if engine.perception_warfare:
            score += 5
            self._record_test("module_perception_warfare", True)
        else:
            missing.append("PerceptionWarfareModule")
            self._record_test("module_perception_warfare", False)

        if engine.red_team:
            score += 5
            self._record_test("module_red_team", True)
        else:
            missing.append("RedTeamModule")
            self._record_test("module_red_team", False)

        if engine.metrics:
            score += 5
            self._record_test("module_metrics", True)
        else:
            missing.append("MetricsModule")
            self._record_test("module_metrics", False)

        if engine.timeline:
            score += 5
            self._record_test("module_timeline", True)
        else:
            missing.append("TimelineModule")
            self._record_test("module_timeline", False)

        if engine.outcomes:
            score += 5
            self._record_test("module_outcomes", True)
        else:
            missing.append("OutcomesModule")
            self._record_test("module_outcomes", False)

        return {
            "score": score,
            "max_score": max_score,
            "percentage": (score / max_score) * 100,
            "missing": missing,
        }

    def _evaluate_irreversibility(self, engine: DjangoStateEngine) -> dict[str, Any]:
        """Evaluate irreversibility constraint enforcement.

        Args:
            engine: Engine to evaluate

        Returns:
            Irreversibility evaluation
        """
        score = 0.0
        max_score = 100.0
        violations = []

        # Test trust ceiling enforcement
        test_state = engine.state.copy()
        test_state.trust.value = 0.5
        test_state.trust.impose_ceiling(0.6)
        test_state.trust.update(0.5, test_state.timestamp)  # Try to exceed ceiling
        if test_state.trust.value <= 0.6:
            score += 25
            self._record_test("trust_ceiling_enforcement", True)
        else:
            violations.append("Trust ceiling not enforced")
            self._record_test("trust_ceiling_enforcement", False)

        # Test moral injury floor enforcement
        test_state = engine.state.copy()
        test_state.moral_injury.value = 0.5
        test_state.moral_injury.impose_floor(0.4)
        test_state.moral_injury.update(-0.3, test_state.timestamp)  # Try to go below floor
        if test_state.moral_injury.value >= 0.4:
            score += 25
            self._record_test("moral_injury_floor_enforcement", True)
        else:
            violations.append("Moral injury floor not enforced")
            self._record_test("moral_injury_floor_enforcement", False)

        # Test legitimacy ceiling enforcement
        test_state = engine.state.copy()
        test_state.legitimacy.value = 0.4
        test_state.legitimacy.impose_ceiling(0.5)
        test_state.legitimacy.update(0.3, test_state.timestamp)  # Try to exceed ceiling
        if test_state.legitimacy.value <= 0.5:
            score += 25
            self._record_test("legitimacy_ceiling_enforcement", True)
        else:
            violations.append("Legitimacy ceiling not enforced")
            self._record_test("legitimacy_ceiling_enforcement", False)

        # Test epistemic confidence ceiling
        test_state = engine.state.copy()
        test_state.epistemic_confidence.value = 0.6
        test_state.epistemic_confidence.impose_ceiling(0.7)
        test_state.epistemic_confidence.update(0.3, test_state.timestamp)
        if test_state.epistemic_confidence.value <= 0.7:
            score += 25
            self._record_test("epistemic_ceiling_enforcement", True)
        else:
            violations.append("Epistemic ceiling not enforced")
            self._record_test("epistemic_ceiling_enforcement", False)

        return {
            "score": score,
            "max_score": max_score,
            "percentage": (score / max_score) * 100,
            "violations": violations,
        }

    def _evaluate_determinism(self, engine: DjangoStateEngine) -> dict[str, Any]:
        """Evaluate deterministic behavior.

        Args:
            engine: Engine to evaluate

        Returns:
            Determinism evaluation
        """
        score = 100.0  # Assume deterministic unless proven otherwise
        max_score = 100.0
        issues = []

        # Check timeline integrity
        if engine.timeline:
            is_valid, error = engine.timeline.verify_chain_integrity()
            if is_valid:
                self._record_test("timeline_integrity", True)
            else:
                score -= 25
                issues.append(f"Timeline integrity broken: {error}")
                self._record_test("timeline_integrity", False)

        # Check causal consistency
        if engine.clock:
            is_valid, error = engine.clock.verify_causal_consistency()
            if is_valid:
                self._record_test("causal_consistency", True)
            else:
                score -= 25
                issues.append(f"Causal consistency broken: {error}")
                self._record_test("causal_consistency", False)

        # Check state snapshots exist
        if engine.timeline and len(engine.timeline.state_snapshots) > 0:
            self._record_test("state_snapshots", True)
        else:
            score -= 25
            issues.append("No state snapshots for replay")
            self._record_test("state_snapshots", False)

        # Check event sourcing
        if engine.timeline and len(engine.timeline.timeline) > 0:
            self._record_test("event_sourcing", True)
        else:
            score -= 25
            issues.append("No events recorded in timeline")
            self._record_test("event_sourcing", False)

        return {
            "score": max(0, score),
            "max_score": max_score,
            "percentage": (max(0, score) / max_score) * 100,
            "issues": issues,
        }

    def _evaluate_performance(self, engine: DjangoStateEngine) -> dict[str, Any]:
        """Evaluate performance characteristics.

        Args:
            engine: Engine to evaluate

        Returns:
            Performance evaluation
        """
        score = 100.0
        max_score = 100.0
        issues = []

        # Performance check - measure tick rate using existing engine
        # Note: This measures 100 additional ticks on the existing engine
        try:
            import time

            start = time.time()
            for _ in range(100):
                engine.tick()
            elapsed = time.time() - start

            # Score based on speed (100 ticks should complete in < 10 seconds)
            if elapsed < 1.0:
                pass  # Full score
            elif elapsed < 5.0:
                score -= 10
            elif elapsed < 10.0:
                score -= 25
            else:
                score -= 50
                issues.append(f"Slow performance: 100 ticks took {elapsed:.2f}s")

            self._record_test("performance_100_ticks", True)
            logger.info("Performance test: 100 ticks in %ss", elapsed)

        except Exception as e:
            score -= 50
            issues.append(f"Performance test failed: {e}")
            self._record_test("performance_100_ticks", False)

        return {
            "score": max(0, score),
            "max_score": max_score,
            "percentage": (max(0, score) / max_score) * 100,
            "issues": issues,
        }

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score.

        Args:
            score: Numerical score (0-100)

        Returns:
            Letter grade
        """
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _record_test(self, test_name: str, passed: bool) -> None:
        """Record test result.

        Args:
            test_name: Name of test
            passed: Whether test passed
        """
        self.test_details.append(
            {
                "test": test_name,
                "passed": passed,
            }
        )

        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1

    def generate_report(self) -> str:
        """Generate human-readable evaluation report.

        Returns:
            Formatted report string
        """
        if not self.evaluation_results:
            return "No evaluation results available"

        overall = self.evaluation_results.get("overall", {})

        report = [
            "=" * 70,
            "DARPA EVALUATION REPORT - Django State Engine",
            "=" * 70,
            f"Overall Score: {overall.get('score', 0):.2f}/100 (Grade: {overall.get('grade', 'N/A')})",
            f"Tests Passed: {self.tests_passed}/{self.tests_passed + self.tests_failed}",
            "",
            "CORRECTNESS:",
            f"  Score: {self.evaluation_results['correctness']['percentage']:.1f}%",
            f"  Issues: {len(self.evaluation_results['correctness']['issues'])}",
            "",
            "COMPLETENESS:",
            f"  Score: {self.evaluation_results['completeness']['percentage']:.1f}%",
            f"  Missing: {len(self.evaluation_results['completeness']['missing'])}",
            "",
            "IRREVERSIBILITY:",
            f"  Score: {self.evaluation_results['irreversibility']['percentage']:.1f}%",
            f"  Violations: {len(self.evaluation_results['irreversibility']['violations'])}",
            "",
            "DETERMINISM:",
            f"  Score: {self.evaluation_results['determinism']['percentage']:.1f}%",
            f"  Issues: {len(self.evaluation_results['determinism']['issues'])}",
            "",
            "PERFORMANCE:",
            f"  Score: {self.evaluation_results['performance']['percentage']:.1f}%",
            f"  Issues: {len(self.evaluation_results['performance']['issues'])}",
            "=" * 70,
        ]

        return "\n".join(report)
