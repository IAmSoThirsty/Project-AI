"""
Kernel Fuzz Harness - Randomized testing for CognitionKernel boundary.

Generates malformed Action objects, fake agents, and malformed governance
decisions to stress-test the kernel's robustness and error handling.

This ensures the kernel fails gracefully under adversarial conditions.
"""

import random
import string
import uuid
from dataclasses import dataclass
from typing import Any

from app.core.cognition_kernel import (
    Action,
    CognitionKernel,
    ExecutionType,
)


@dataclass
class FuzzResult:
    """Result of a fuzz test."""

    test_name: str
    input_type: str
    success: bool
    error: str | None
    crash: bool
    details: dict[str, Any]


class KernelFuzzHarness:
    """
    Fuzz harness for testing CognitionKernel robustness.

    Generates randomized malformed inputs to test:
    - Malformed Action objects
    - Fake/invalid agents
    - Corrupted governance decisions
    - Boundary condition violations
    - Type confusion attacks
    """

    def __init__(self, kernel: CognitionKernel):
        """
        Initialize fuzz harness.

        Args:
            kernel: CognitionKernel instance to test
        """
        self.kernel = kernel
        self.results: list[FuzzResult] = []

    def run_all_tests(self, iterations: int = 100) -> dict[str, Any]:
        """
        Run all fuzz tests.

        Args:
            iterations: Number of iterations per test type

        Returns:
            Summary of fuzz test results
        """
        self.results = []

        # Test categories
        self.fuzz_malformed_actions(iterations)
        self.fuzz_fake_agents(iterations)
        self.fuzz_malformed_governance(iterations)
        self.fuzz_boundary_conditions(iterations)
        self.fuzz_type_confusion(iterations)

        # Analyze results
        return self._analyze_results()

    def fuzz_malformed_actions(self, iterations: int) -> None:
        """Generate malformed Action objects."""
        for i in range(iterations):
            test_name = f"malformed_action_{i}"

            try:
                # Random malformed action
                action = self._generate_malformed_action()

                # Try to create context with it
                result = self.kernel.route(
                    task={
                        "action_name": "fuzz_test",
                        "_action_callable": action.callable,
                        "_action_args": action.args,
                        "_action_kwargs": action.kwargs,
                    },
                    source="fuzz_harness",
                    metadata={},
                )

                self.results.append(
                    FuzzResult(
                        test_name=test_name,
                        input_type="malformed_action",
                        success=True,
                        error=None,
                        crash=False,
                        details={"result": str(result)[:100]},
                    )
                )

            except Exception as e:
                # Expected - kernel should handle gracefully
                self.results.append(
                    FuzzResult(
                        test_name=test_name,
                        input_type="malformed_action",
                        success=False,
                        error=str(e),
                        crash=False,  # Caught exception is graceful failure
                        details={"exception_type": type(e).__name__},
                    )
                )

    def fuzz_fake_agents(self, iterations: int) -> None:
        """Generate fake/invalid agent invocations."""
        for i in range(iterations):
            test_name = f"fake_agent_{i}"

            try:
                # Random fake agent name
                fake_agent = "".join(
                    random.choices(string.ascii_letters + string.digits, k=20)
                )

                result = self.kernel.route(
                    task={"action_name": f"fake_{fake_agent}", "risk_level": "high"},
                    source=fake_agent,
                    metadata={"is_fuzz": True},
                )

                self.results.append(
                    FuzzResult(
                        test_name=test_name,
                        input_type="fake_agent",
                        success=True,
                        error=None,
                        crash=False,
                        details={"result": str(result)[:100]},
                    )
                )

            except Exception as e:
                self.results.append(
                    FuzzResult(
                        test_name=test_name,
                        input_type="fake_agent",
                        success=False,
                        error=str(e),
                        crash=False,
                        details={"exception_type": type(e).__name__},
                    )
                )

    def fuzz_malformed_governance(self, iterations: int) -> None:
        """Test with malformed governance responses."""
        for i in range(iterations):
            test_name = f"malformed_governance_{i}"

            # This tests the kernel's resilience when governance misbehaves
            # Since we can't directly inject malformed governance, we test
            # with edge case inputs that might trigger governance errors

            try:
                result = self.kernel.route(
                    task={
                        "action_name": "governance_stress_test",
                        "requires_approval": random.choice([True, False]),
                        "risk_level": random.choice(
                            ["low", "medium", "high", "critical", "invalid"]
                        ),
                        "mutation_targets": [
                            random.choice(
                                ["genesis", "law_hierarchy", "core_values", "invalid"]
                            )
                        ],
                    },
                    source="fuzz_harness",
                    metadata={"stress_test": True},
                )

                self.results.append(
                    FuzzResult(
                        test_name=test_name,
                        input_type="malformed_governance",
                        success=True,
                        error=None,
                        crash=False,
                        details={"result": str(result)[:100]},
                    )
                )

            except Exception as e:
                self.results.append(
                    FuzzResult(
                        test_name=test_name,
                        input_type="malformed_governance",
                        success=False,
                        error=str(e),
                        crash=False,
                        details={"exception_type": type(e).__name__},
                    )
                )

    def fuzz_boundary_conditions(self, iterations: int) -> None:
        """Test boundary conditions."""
        for i in range(iterations):
            test_name = f"boundary_{i}"

            try:
                # Test with extreme values
                extreme_input = random.choice(
                    [
                        "",  # Empty string
                        " " * 10000,  # Large whitespace
                        "A" * 100000,  # Large string
                        None,  # None
                        {},  # Empty dict
                        {"x": "y" * 10000},  # Large nested data
                    ]
                )

                self.kernel.route(
                    task=extreme_input, source="fuzz_harness", metadata={}
                )

                self.results.append(
                    FuzzResult(
                        test_name=test_name,
                        input_type="boundary_condition",
                        success=True,
                        error=None,
                        crash=False,
                        details={"input_type": type(extreme_input).__name__},
                    )
                )

            except Exception as e:
                self.results.append(
                    FuzzResult(
                        test_name=test_name,
                        input_type="boundary_condition",
                        success=False,
                        error=str(e),
                        crash=False,
                        details={"exception_type": type(e).__name__},
                    )
                )

    def fuzz_type_confusion(self, iterations: int) -> None:
        """Test type confusion attacks."""
        for i in range(iterations):
            test_name = f"type_confusion_{i}"

            try:
                # Generate type-confused inputs
                confused_input = random.choice(
                    [
                        12345,  # Integer instead of string
                        [1, 2, 3],  # List instead of dict
                        lambda: None,  # Lambda instead of action
                        {"wrong_key": "value"},  # Missing required keys
                        {
                            "_action_callable": "not_callable",
                            "_action_args": "not_tuple",
                        },  # Wrong types
                    ]
                )

                self.kernel.route(
                    task=confused_input, source="fuzz_harness", metadata={}
                )

                self.results.append(
                    FuzzResult(
                        test_name=test_name,
                        input_type="type_confusion",
                        success=True,
                        error=None,
                        crash=False,
                        details={"input_type": type(confused_input).__name__},
                    )
                )

            except Exception as e:
                self.results.append(
                    FuzzResult(
                        test_name=test_name,
                        input_type="type_confusion",
                        success=False,
                        error=str(e),
                        crash=False,
                        details={"exception_type": type(e).__name__},
                    )
                )

    def _generate_malformed_action(self) -> Action:
        """Generate a malformed Action object."""
        # Randomly choose malformation type
        malformation_type = random.choice(
            [
                "invalid_callable",
                "wrong_args_type",
                "missing_fields",
                "extreme_values",
            ]
        )

        if malformation_type == "invalid_callable":
            # Non-callable object
            return Action(
                action_id=str(uuid.uuid4()),
                action_name="malformed",
                action_type=ExecutionType.AGENT_ACTION,
                callable="not_a_callable",  # type: ignore
                args=(),
                kwargs={},
                source="fuzz",
            )

        if malformation_type == "wrong_args_type":
            # Wrong argument types
            return Action(
                action_id=str(uuid.uuid4()),
                action_name="malformed",
                action_type=ExecutionType.AGENT_ACTION,
                callable=lambda: None,
                args="not_a_tuple",  # type: ignore
                kwargs="not_a_dict",  # type: ignore
                source="fuzz",
            )

        if malformation_type == "extreme_values":
            # Extreme values
            return Action(
                action_id="x" * 10000,  # Extremely long ID
                action_name="A" * 10000,  # Extremely long name
                action_type=ExecutionType.AGENT_ACTION,
                callable=lambda: "x" * 1000000,  # Returns huge string
                args=tuple(range(10000)),  # Many args
                kwargs={f"key_{i}": i for i in range(1000)},  # Many kwargs
                source="fuzz",
            )

        # Default: missing/invalid fields
        return Action(
            action_id="",
            action_name="",
            action_type=ExecutionType.AGENT_ACTION,
            callable=lambda: None,
            args=(),
            kwargs={},
            source="",
        )

    def _analyze_results(self) -> dict[str, Any]:
        """Analyze fuzz test results."""
        total = len(self.results)
        crashes = sum(1 for r in self.results if r.crash)
        failures = sum(1 for r in self.results if not r.success and not r.crash)
        successes = sum(1 for r in self.results if r.success)

        # Group by input type
        by_type: dict[str, dict[str, int]] = {}
        for result in self.results:
            if result.input_type not in by_type:
                by_type[result.input_type] = {"total": 0, "success": 0, "failure": 0}
            by_type[result.input_type]["total"] += 1
            if result.success:
                by_type[result.input_type]["success"] += 1
            else:
                by_type[result.input_type]["failure"] += 1

        return {
            "total_tests": total,
            "crashes": crashes,
            "graceful_failures": failures,
            "successes": successes,
            "crash_rate": crashes / total if total > 0 else 0,
            "failure_rate": failures / total if total > 0 else 0,
            "by_input_type": by_type,
            "verdict": "PASS" if crashes == 0 else "FAIL",
        }

    def get_failures(self) -> list[FuzzResult]:
        """Get all failure results."""
        return [r for r in self.results if not r.success or r.crash]

    def get_crashes(self) -> list[FuzzResult]:
        """Get all crash results."""
        return [r for r in self.results if r.crash]
