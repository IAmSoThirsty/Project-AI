#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Build Cognition Engine
=======================

Integrates Project-AI's cognition engine with Gradle build intelligence.
Provides deliberation, learning, and adaptive build optimization.
"""

import logging
from typing import Any

from cognition.boundary import check_boundary
from cognition.invariants import InvariantChecker
from project_ai.engine.cognition.deliberation_engine import DeliberationEngine

logger = logging.getLogger(__name__)


class BuildCognitionEngine:
    """
    Applies cognitive deliberation to build decisions.
    Learns from build patterns and optimizes future executions.
    """

    def __init__(
        self,
        deliberation_engine: DeliberationEngine,
        config: dict[str, Any] | None = None,
    ):
        """
        Initialize build cognition engine.

        Args:
            deliberation_engine: Project-AI deliberation engine
            config: Optional configuration overrides
        """
        self.deliberation = deliberation_engine
        self.config = config or {}
        self.invariant_checker = InvariantChecker()

        # Build-specific cognitive state
        self.build_patterns: dict[str, list[dict[str, Any]]] = {}
        self.optimization_history: list[dict[str, Any]] = []
        self.failure_patterns: dict[str, int] = {}

        logger.info("Build cognition engine initialized")

    def deliberate_build_plan(
        self, tasks: list[str], context: dict[str, Any]
    ) -> tuple[list[str], dict[str, Any]]:
        """
        Deliberate on optimal build task ordering and execution.

        Args:
            tasks: List of build tasks to execute
            context: Build context (dependencies, cache state, etc.)

        Returns:
            Tuple of (optimized_tasks, reasoning)
        """
        try:
            # Check cognitive boundaries
            if not check_boundary("build_planning", len(tasks)):
                logger.warning("Task count %s exceeds cognitive boundary", len(tasks))
                return tasks, {"warning": "Boundary exceeded, using original order"}

            # Analyze build patterns
            patterns = self._analyze_patterns(tasks, context)

            # Use deliberation engine for optimization
            deliberation_input = {
                "tasks": tasks,
                "context": context,
                "patterns": patterns,
                "history": self._get_relevant_history(tasks),
            }

            result = self.deliberation.deliberate(
                decision_type="build_optimization", inputs=deliberation_input
            )

            optimized_tasks = result.get("optimized_order", tasks)
            reasoning = result if isinstance(result, dict) else {"reasoning": result}

            # Validate invariants
            if not self._validate_task_order(optimized_tasks, context):
                logger.warning("Task order violates invariants, reverting")
                return tasks, {"warning": "Invariant violation, using original order"}

            # Record optimization
            self._record_optimization(tasks, optimized_tasks, reasoning)

            logger.info("Build plan optimized: %s tasks", len(tasks))
            return optimized_tasks, reasoning

        except Exception as e:
            logger.error("Error deliberating build plan: %s", e, exc_info=True)
            return tasks, {"error": str(e)}

    def learn_from_build(
        self,
        tasks_or_build_id: list[str] | str,
        execution_or_tasks: dict[str, Any] | list[str],
        success_or_performance: bool | dict[str, Any],
    ) -> None:
        """
        Learn from build execution to improve future decisions.

        Args:
            tasks: Executed tasks
            execution_data: Execution metrics (duration, cache hits, etc.)
            success: Whether build succeeded
        """
        try:
            # Compatibility call shape A:
            # learn_from_build(tasks, execution_data, success)
            if isinstance(tasks_or_build_id, list) and isinstance(
                execution_or_tasks, dict
            ):
                tasks = tasks_or_build_id
                execution_data = execution_or_tasks
                success = bool(success_or_performance)
            # Compatibility call shape B (legacy tests):
            # learn_from_build(build_id, tasks, performance)
            elif isinstance(tasks_or_build_id, str) and isinstance(
                execution_or_tasks, list
            ) and isinstance(success_or_performance, dict):
                build_id = tasks_or_build_id
                tasks = execution_or_tasks
                execution_data = dict(success_or_performance)
                execution_data.setdefault("build_id", tasks_or_build_id)
                success = bool(execution_data.get("success", True))
            else:
                raise TypeError("Unsupported learn_from_build argument pattern")

            # Record pattern
            pattern_key = self._compute_pattern_key(tasks)

            if pattern_key not in self.build_patterns:
                self.build_patterns[pattern_key] = []

            pattern_entry = {
                "tasks": tasks,
                "execution_data": execution_data,
                "success": success,
                "timestamp": execution_data.get("timestamp"),
            }

            self.build_patterns[pattern_key].append(pattern_entry)

            # Legacy compatibility: expose build-id keyed history when provided.
            if "build_id" in execution_data:
                build_id_key = str(execution_data["build_id"])
                self.build_patterns.setdefault(build_id_key, []).append(pattern_entry)

            # Update failure patterns
            if not success:
                for task in tasks:
                    self.failure_patterns[task] = self.failure_patterns.get(task, 0) + 1

            # Prune old patterns (keep last 100 per pattern)
            if len(self.build_patterns[pattern_key]) > 100:
                self.build_patterns[pattern_key] = self.build_patterns[pattern_key][
                    -100:
                ]

            logger.debug("Learned from build: %s, success=%s", pattern_key, success)

        except Exception as e:
            logger.error("Error learning from build: %s", e, exc_info=True)

    def get_optimization_stats(self) -> dict[str, Any]:
        """Return aggregate optimization statistics."""
        total = len(self.optimization_history)
        return {
            "total_optimizations": total,
            "known_patterns": len(self.build_patterns),
            "failure_patterns": len(self.failure_patterns),
        }

    def suggest_optimizations(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Suggest build optimizations based on learned patterns.

        Args:
            context: Current build context

        Returns:
            List of optimization suggestions
        """
        try:
            suggestions = []

            # Analyze failure patterns
            if self.failure_patterns:
                high_failure_tasks = [
                    task for task, count in self.failure_patterns.items() if count > 3
                ]

                if high_failure_tasks:
                    suggestions.append(
                        {
                            "type": "failure_prevention",
                            "description": "Tasks with high failure rates detected",
                            "tasks": high_failure_tasks,
                            "recommendation": "Consider adding pre-checks or retry logic",
                        }
                    )

            # Analyze parallelization opportunities
            parallel_opportunities = self._find_parallel_opportunities(context)
            if parallel_opportunities:
                suggestions.append(
                    {
                        "type": "parallelization",
                        "description": "Tasks can be parallelized",
                        "task_groups": parallel_opportunities,
                        "recommendation": "Enable parallel execution for these task groups",
                    }
                )

            # Analyze caching opportunities
            cache_opportunities = self._find_cache_opportunities(context)
            if cache_opportunities:
                suggestions.append(
                    {
                        "type": "caching",
                        "description": "Tasks suitable for caching",
                        "tasks": cache_opportunities,
                        "recommendation": "Enable caching for these tasks",
                    }
                )

            logger.info("Generated %s optimization suggestions", len(suggestions))
            return suggestions

        except Exception as e:
            logger.error("Error suggesting optimizations: %s", e, exc_info=True)
            return []

    def _analyze_patterns(
        self, tasks: list[str], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze build patterns from history."""
        pattern_key = self._compute_pattern_key(tasks)
        historical_patterns = self.build_patterns.get(pattern_key, [])

        if not historical_patterns:
            return {"status": "no_history"}

        # Compute pattern statistics
        success_rate = sum(1 for p in historical_patterns if p["success"]) / len(
            historical_patterns
        )

        avg_duration = sum(
            p["execution_data"].get("duration_seconds", 0) for p in historical_patterns
        ) / len(historical_patterns)

        return {
            "status": "patterns_found",
            "success_rate": success_rate,
            "average_duration": avg_duration,
            "sample_count": len(historical_patterns),
        }

    def _validate_task_order(self, tasks: list[str], context: dict[str, Any]) -> bool:
        """Validate task order against dependency invariants."""
        try:
            dependencies = context.get("dependencies", {})

            task_positions = {task: idx for idx, task in enumerate(tasks)}

            # Check all dependencies are satisfied
            for task, deps in dependencies.items():
                if task not in task_positions:
                    continue

                task_pos = task_positions[task]

                for dep in deps:
                    if dep in task_positions:
                        dep_pos = task_positions[dep]
                        if dep_pos >= task_pos:
                            logger.warning(
                                f"Dependency violation: {task} depends on {dep} "
                                f"but {dep} comes later"
                            )
                            return False

            return True

        except Exception as e:
            logger.error("Error validating task order: %s", e, exc_info=True)
            return False

    def _compute_pattern_key(self, tasks: list[str]) -> str:
        """Compute a pattern key for task list."""
        import hashlib

        task_str = "|".join(sorted(tasks))
        return hashlib.sha256(task_str.encode()).hexdigest()[:16]

    def _get_relevant_history(self, tasks: list[str]) -> list[dict[str, Any]]:
        """Get relevant historical data for tasks."""
        pattern_key = self._compute_pattern_key(tasks)
        return self.build_patterns.get(pattern_key, [])[-10:]  # Last 10

    def _record_optimization(
        self, original: list[str], optimized: list[str], reasoning: dict[str, Any]
    ) -> None:
        """Record optimization decision."""
        from datetime import datetime

        self.optimization_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "original": original,
                "optimized": optimized,
                "reasoning": reasoning,
            }
        )

        # Keep last 1000 optimizations
        if len(self.optimization_history) > 1000:
            self.optimization_history = self.optimization_history[-1000:]

    def _find_parallel_opportunities(self, context: dict[str, Any]) -> list[list[str]]:
        """Find tasks that can be parallelized."""
        # Simplified: tasks with no dependencies can be parallel
        dependencies = context.get("dependencies", {})
        independent_tasks = [
            task for task in context.get("all_tasks", []) if not dependencies.get(task)
        ]

        if len(independent_tasks) > 1:
            return [independent_tasks]

        return []

    def _find_cache_opportunities(self, context: dict[str, Any]) -> list[str]:
        """Find tasks suitable for caching."""
        # Tasks that frequently appear in patterns are cache candidates
        task_frequency = {}
        for patterns in self.build_patterns.values():
            for pattern in patterns:
                for task in pattern["tasks"]:
                    task_frequency[task] = task_frequency.get(task, 0) + 1

        # Return tasks that appear frequently (>10 times)
        return [task for task, freq in task_frequency.items() if freq > 10]


__all__ = ["BuildCognitionEngine"]
