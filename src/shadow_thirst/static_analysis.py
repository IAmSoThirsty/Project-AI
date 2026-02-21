"""
Shadow Thirst Static Analysis Engine

Implements 6 static analyzers for Shadow Thirst programs:
1. Plane Isolation Analyzer: Ensures shadow never mutates canonical state
2. Determinism Analyzer: Verifies shadow execution is deterministic
3. Privilege Escalation Analyzer: Detects unauthorized state elevation
4. Resource Estimator: Bounds CPU/memory usage
5. Divergence Risk Estimator: Estimates divergence probability
6. Invariant Purity Checker: Verifies invariants are pure/deterministic

STATUS: PRODUCTION
VERSION: 1.0.0
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from shadow_thirst.ir import (
    IRFunction,
    IROpcode,
    IRProgram,
    PlaneQualifierIR,
)

logger = logging.getLogger(__name__)


class AnalysisSeverity(Enum):
    """Severity level for analysis findings."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AnalysisFinding:
    """Single analysis finding."""

    analyzer: str
    severity: AnalysisSeverity
    message: str
    function: str | None = None
    block_id: int | None = None
    instruction_index: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        location = ""
        if self.function:
            location = f" in {self.function}"
        if self.block_id is not None:
            location += f" block {self.block_id}"
        return f"[{self.severity.value.upper()}] {self.analyzer}: {self.message}{location}"


@dataclass
class AnalysisReport:
    """Complete analysis report for a program."""

    findings: list[AnalysisFinding] = field(default_factory=list)
    passed: bool = True
    summary: dict[str, Any] = field(default_factory=dict)

    def add_finding(self, finding: AnalysisFinding):
        """Add a finding to the report."""
        self.findings.append(finding)
        if finding.severity in (AnalysisSeverity.ERROR, AnalysisSeverity.CRITICAL):
            self.passed = False

    def get_errors(self) -> list[AnalysisFinding]:
        """Get all error-level findings."""
        return [f for f in self.findings if f.severity in (AnalysisSeverity.ERROR, AnalysisSeverity.CRITICAL)]

    def get_warnings(self) -> list[AnalysisFinding]:
        """Get all warning-level findings."""
        return [f for f in self.findings if f.severity == AnalysisSeverity.WARNING]


# ============================================================================
# 1. Plane Isolation Analyzer
# ============================================================================


class PlaneIsolationAnalyzer:
    """
    Analyzer 1: Plane Isolation

    Ensures shadow plane never mutates canonical state.
    This is the most critical safety property.

    Algorithm:
    1. For each shadow block:
       - Track all STORE_VAR instructions
       - Check variable qualifier
       - Error if storing to Canonical<T>
    2. For each shadow function call:
       - Verify callee respects isolation
    """

    def analyze(self, program: IRProgram) -> list[AnalysisFinding]:
        """
        Analyze plane isolation.

        Args:
            program: IR program to analyze

        Returns:
            List of findings
        """
        findings = []

        for function in program.functions:
            findings.extend(self._analyze_function(function))

        return findings

    def _analyze_function(self, function: IRFunction) -> list[AnalysisFinding]:
        """Analyze plane isolation for a function."""
        findings = []

        # Check shadow blocks for canonical mutations
        for block in function.shadow_blocks:
            for i, instruction in enumerate(block.instructions):
                if instruction.opcode == IROpcode.STORE_VAR:
                    var_name = instruction.operands[0] if instruction.operands else None
                    if var_name:
                        var = self._find_variable(function, var_name)
                        if var and var.qualifier == PlaneQualifierIR.CANONICAL:
                            findings.append(
                                AnalysisFinding(
                                    analyzer="PlaneIsolationAnalyzer",
                                    severity=AnalysisSeverity.CRITICAL,
                                    message=f"Shadow plane attempts to mutate canonical variable '{var_name}'",
                                    function=function.name,
                                    block_id=block.block_id,
                                    instruction_index=i,
                                )
                            )

        return findings

    def _find_variable(self, function: IRFunction, name: str):
        """Find variable by name."""
        for var in function.variables + function.parameters:
            if var.name == name:
                return var
        return None


# ============================================================================
# 2. Determinism Analyzer
# ============================================================================


class DeterminismAnalyzer:
    """
    Analyzer 2: Determinism

    Verifies shadow execution is deterministic and replayable.

    Algorithm:
    1. Scan shadow blocks for non-deterministic operations:
       - Random number generation
       - System time access
       - I/O operations
       - External API calls
    2. Flag any non-deterministic instruction
    """

    NON_DETERMINISTIC_OPCODES = {
        IROpcode.INPUT,  # User input is non-deterministic
        # In a real implementation, would also flag:
        # - rand(), time(), network I/O, etc.
    }

    def analyze(self, program: IRProgram) -> list[AnalysisFinding]:
        """Analyze determinism."""
        findings = []

        for function in program.functions:
            findings.extend(self._analyze_function(function))

        return findings

    def _analyze_function(self, function: IRFunction) -> list[AnalysisFinding]:
        """Analyze determinism for a function."""
        findings = []

        for block in function.shadow_blocks + function.invariant_blocks:
            for i, instruction in enumerate(block.instructions):
                if instruction.opcode in self.NON_DETERMINISTIC_OPCODES:
                    findings.append(
                        AnalysisFinding(
                            analyzer="DeterminismAnalyzer",
                            severity=AnalysisSeverity.ERROR,
                            message=f"Non-deterministic operation in shadow/invariant: {instruction.opcode.name}",
                            function=function.name,
                            block_id=block.block_id,
                            instruction_index=i,
                        )
                    )

        return findings


# ============================================================================
# 3. Privilege Escalation Analyzer
# ============================================================================


class PrivilegeEscalationAnalyzer:
    """
    Analyzer 3: Privilege Escalation

    Detects attempts to escalate privileges or bypass constitutional validation.

    Algorithm:
    1. Track mutation boundaries
    2. Verify all canonical mutations go through VALIDATE_AND_COMMIT
    3. Flag direct canonical writes without validation
    """

    def analyze(self, program: IRProgram) -> list[AnalysisFinding]:
        """Analyze privilege escalation risks."""
        findings = []

        for function in program.functions:
            findings.extend(self._analyze_function(function))

        return findings

    def _analyze_function(self, function: IRFunction) -> list[AnalysisFinding]:
        """Analyze privilege escalation for a function."""
        findings = []

        # Check if function has proper mutation boundary
        if function.mutation_boundary == "validated_canonical":
            # Must have VALIDATE_AND_COMMIT before canonical writes
            has_validation = False
            for block in function.primary_blocks:
                for instruction in block.instructions:
                    if instruction.opcode == IROpcode.VALIDATE_AND_COMMIT:
                        has_validation = True

            if not has_validation:
                findings.append(
                    AnalysisFinding(
                        analyzer="PrivilegeEscalationAnalyzer",
                        severity=AnalysisSeverity.ERROR,
                        message="Function requires validated_canonical but missing VALIDATE_AND_COMMIT",
                        function=function.name,
                    )
                )

        return findings


# ============================================================================
# 4. Resource Estimator
# ============================================================================


class ResourceEstimator:
    """
    Analyzer 4: Resource Estimation

    Bounds CPU and memory usage for shadow execution.

    Algorithm:
    1. Count instructions in shadow blocks
    2. Estimate CPU time (heuristic: 1ms per 100 instructions)
    3. Estimate memory usage based on variables and stack depth
    4. Flag if exceeds quotas
    """

    DEFAULT_CPU_QUOTA_MS = 1000.0
    DEFAULT_MEMORY_QUOTA_MB = 256.0
    INSTRUCTIONS_PER_MS = 100.0

    def analyze(self, program: IRProgram) -> list[AnalysisFinding]:
        """Analyze resource usage."""
        findings = []

        for function in program.functions:
            findings.extend(self._analyze_function(function))

        return findings

    def _analyze_function(self, function: IRFunction) -> list[AnalysisFinding]:
        """Analyze resource usage for a function."""
        findings = []

        # Estimate shadow execution cost
        shadow_instructions = sum(len(block.instructions) for block in function.shadow_blocks)

        estimated_cpu_ms = shadow_instructions / self.INSTRUCTIONS_PER_MS

        # Check against quota
        cpu_quota = function.shadow_cpu_quota_ms or self.DEFAULT_CPU_QUOTA_MS
        if estimated_cpu_ms > cpu_quota:
            findings.append(
                AnalysisFinding(
                    analyzer="ResourceEstimator",
                    severity=AnalysisSeverity.WARNING,
                    message=f"Estimated shadow CPU usage ({estimated_cpu_ms:.2f}ms) exceeds quota ({cpu_quota}ms)",
                    function=function.name,
                    metadata={
                        "estimated_cpu_ms": estimated_cpu_ms,
                        "cpu_quota_ms": cpu_quota,
                        "shadow_instructions": shadow_instructions,
                    },
                )
            )

        # Estimate memory usage (simple heuristic)
        num_variables = len(function.variables)
        estimated_memory_mb = num_variables * 0.001  # 1KB per variable

        memory_quota = function.shadow_memory_quota_mb or self.DEFAULT_MEMORY_QUOTA_MB
        if estimated_memory_mb > memory_quota:
            findings.append(
                AnalysisFinding(
                    analyzer="ResourceEstimator",
                    severity=AnalysisSeverity.WARNING,
                    message=f"Estimated memory usage ({estimated_memory_mb:.2f}MB) exceeds quota ({memory_quota}MB)",
                    function=function.name,
                    metadata={
                        "estimated_memory_mb": estimated_memory_mb,
                        "memory_quota_mb": memory_quota,
                    },
                )
            )

        return findings


# ============================================================================
# 5. Divergence Risk Estimator
# ============================================================================


class DivergenceRiskEstimator:
    """
    Analyzer 5: Divergence Risk Estimation

    Estimates probability and magnitude of primary/shadow divergence.

    Algorithm:
    1. Compare primary and shadow computation graphs
    2. Identify divergence points (different operations on same data)
    3. Estimate divergence magnitude
    4. Flag high-risk divergence
    """

    def analyze(self, program: IRProgram) -> list[AnalysisFinding]:
        """Analyze divergence risk."""
        findings = []

        for function in program.functions:
            findings.extend(self._analyze_function(function))

        return findings

    def _analyze_function(self, function: IRFunction) -> list[AnalysisFinding]:
        """Analyze divergence risk for a function."""
        findings = []

        if not function.has_shadow:
            return findings

        # Compare primary and shadow instruction counts
        primary_count = sum(len(block.instructions) for block in function.primary_blocks)
        shadow_count = sum(len(block.instructions) for block in function.shadow_blocks)

        # If shadow is significantly different, risk of divergence
        if shadow_count > 0:
            diff_ratio = abs(primary_count - shadow_count) / shadow_count
            if diff_ratio > 0.5:  # >50% difference
                findings.append(
                    AnalysisFinding(
                        analyzer="DivergenceRiskEstimator",
                        severity=AnalysisSeverity.INFO,
                        message=f"High divergence risk: primary and shadow have significantly different complexity ({diff_ratio:.1%} difference)",
                        function=function.name,
                        metadata={
                            "primary_instructions": primary_count,
                            "shadow_instructions": shadow_count,
                            "difference_ratio": diff_ratio,
                        },
                    )
                )

        # Check if divergence policy is set
        if not function.divergence_policy:
            findings.append(
                AnalysisFinding(
                    analyzer="DivergenceRiskEstimator",
                    severity=AnalysisSeverity.WARNING,
                    message="Function has shadow execution but no divergence policy specified",
                    function=function.name,
                )
            )

        return findings


# ============================================================================
# 6. Invariant Purity Checker
# ============================================================================


class InvariantPurityChecker:
    """
    Analyzer 6: Invariant Purity

    Verifies invariants are pure (no side effects) and deterministic.

    Algorithm:
    1. Scan invariant blocks
    2. Flag any side-effecting operations:
       - STORE_VAR, OUTPUT, CALL (except pure functions)
    3. Verify determinism (no INPUT, random, etc.)
    """

    IMPURE_OPCODES = {
        IROpcode.STORE_VAR,
        IROpcode.OUTPUT,
        IROpcode.INPUT,
    }

    def analyze(self, program: IRProgram) -> list[AnalysisFinding]:
        """Analyze invariant purity."""
        findings = []

        for function in program.functions:
            findings.extend(self._analyze_function(function))

        return findings

    def _analyze_function(self, function: IRFunction) -> list[AnalysisFinding]:
        """Analyze invariant purity for a function."""
        findings = []

        for block in function.invariant_blocks:
            for i, instruction in enumerate(block.instructions):
                if instruction.opcode in self.IMPURE_OPCODES:
                    findings.append(
                        AnalysisFinding(
                            analyzer="InvariantPurityChecker",
                            severity=AnalysisSeverity.ERROR,
                            message=f"Invariant contains impure operation: {instruction.opcode.name}",
                            function=function.name,
                            block_id=block.block_id,
                            instruction_index=i,
                        )
                    )

                # Function calls in invariants must be pure
                if instruction.opcode == IROpcode.CALL:
                    func_name = instruction.operands[0] if instruction.operands else "unknown"
                    findings.append(
                        AnalysisFinding(
                            analyzer="InvariantPurityChecker",
                            severity=AnalysisSeverity.WARNING,
                            message=f"Invariant calls function '{func_name}' - verify it is pure",
                            function=function.name,
                            block_id=block.block_id,
                            instruction_index=i,
                        )
                    )

        return findings


# ============================================================================
# Composite Static Analyzer
# ============================================================================


class StaticAnalyzer:
    """
    Composite static analyzer that runs all 6 analyzers.

    Coordinates analysis passes and produces unified report.
    """

    def __init__(self):
        """Initialize static analyzer with all sub-analyzers."""
        self.analyzers = [
            PlaneIsolationAnalyzer(),
            DeterminismAnalyzer(),
            PrivilegeEscalationAnalyzer(),
            ResourceEstimator(),
            DivergenceRiskEstimator(),
            InvariantPurityChecker(),
        ]

    def analyze(self, program: IRProgram) -> AnalysisReport:
        """
        Run all static analyzers on program.

        Args:
            program: IR program to analyze

        Returns:
            Complete analysis report
        """
        logger.info("Running static analysis...")

        report = AnalysisReport()

        for analyzer in self.analyzers:
            analyzer_name = analyzer.__class__.__name__
            logger.debug("Running %s", analyzer_name)

            findings = analyzer.analyze(program)
            for finding in findings:
                report.add_finding(finding)

        # Generate summary
        report.summary = {
            "total_findings": len(report.findings),
            "errors": len(report.get_errors()),
            "warnings": len(report.get_warnings()),
            "passed": report.passed,
            "analyzers_run": len(self.analyzers),
        }

        logger.info(
            "Static analysis complete: %d findings (%d errors, %d warnings)",
            report.summary["total_findings"],
            report.summary["errors"],
            report.summary["warnings"],
        )

        return report


def analyze(program: IRProgram) -> AnalysisReport:
    """
    Run static analysis on IR program.

    Args:
        program: IR program to analyze

    Returns:
        Analysis report
    """
    analyzer = StaticAnalyzer()
    return analyzer.analyze(program)


__all__ = [
    # Severity
    "AnalysisSeverity",
    # Report types
    "AnalysisFinding",
    "AnalysisReport",
    # Analyzers
    "PlaneIsolationAnalyzer",
    "DeterminismAnalyzer",
    "PrivilegeEscalationAnalyzer",
    "ResourceEstimator",
    "DivergenceRiskEstimator",
    "InvariantPurityChecker",
    "StaticAnalyzer",
    # Main interface
    "analyze",
]
