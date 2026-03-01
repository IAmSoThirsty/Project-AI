"""
TAAR Scheduler — DAG-based task scheduling with topological ordering.

Coordinates which runners execute in what order based on the
dependency graph impact analysis and runner priority configuration.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path

from taar.cache import ResultCache
from taar.config import TaarConfig
from taar.executor import Executor, RunReport, TaskResult
from taar.graph import ImpactResult


@dataclass
class ScheduledTask:
    """A task scheduled for execution."""

    runner_name: str
    files: list[Path]
    test_files: list[Path] = field(default_factory=list)
    priority: int = 3


class Scheduler:
    """
    Schedules and dispatches runner tasks based on impact analysis.

    Takes an ImpactResult from the dependency graph and converts it
    into a prioritized execution plan, then dispatches through the
    Executor.
    """

    def __init__(self, config: TaarConfig, cache: ResultCache):
        self.config = config
        self.executor = Executor(config, cache)

    def plan(self, impact: ImpactResult) -> list[ScheduledTask]:
        """
        Create an execution plan from impact analysis results.

        Returns tasks sorted by priority (lowest number = runs first).
        """
        tasks = []

        for runner_name, files in impact.affected_runners.items():
            runner = self.config.enabled_runners.get(runner_name)
            if runner is None:
                continue

            # Determine test files for this runner
            test_files = [
                f
                for f in impact.extra_test_files
                if any(
                    f.as_posix().endswith(ext)
                    for ext in (".py", ".js", ".ts", ".kt", ".cs")
                )
            ]

            # Min priority of all commands in this runner
            min_priority = min((cmd.priority for cmd in runner.commands), default=3)

            tasks.append(
                ScheduledTask(
                    runner_name=runner_name,
                    files=files,
                    test_files=test_files,
                    priority=min_priority,
                )
            )

        # Sort by priority
        tasks.sort(key=lambda t: t.priority)
        return tasks

    async def execute(
        self,
        impact: ImpactResult,
        on_result: callable | None = None,
    ) -> RunReport:
        """
        Execute all scheduled tasks and return an aggregate report.

        Tasks with different priorities run sequentially (lower first).
        Tasks with the same priority run concurrently.

        Args:
            impact: Impact analysis result from the dependency graph.
            on_result: Optional callback invoked after each TaskResult.

        Returns:
            RunReport with all results.
        """
        tasks = self.plan(impact)
        report = RunReport()

        import time

        overall_start = time.perf_counter()

        # Group by priority
        priority_groups: dict[int, list[ScheduledTask]] = {}
        for task in tasks:
            priority_groups.setdefault(task.priority, []).append(task)

        for priority in sorted(priority_groups.keys()):
            group = priority_groups[priority]

            # Execute same-priority runners concurrently
            coros = []
            for task in group:
                runner = self.config.enabled_runners.get(task.runner_name)
                if runner:
                    coros.append(
                        self.executor.execute_runner(
                            runner, task.files, task.test_files
                        )
                    )

            group_results = await asyncio.gather(*coros, return_exceptions=True)

            for result_list in group_results:
                if isinstance(result_list, Exception):
                    report.results.append(
                        TaskResult(
                            runner_name="scheduler",
                            command_name="dispatch",
                            passed=False,
                            return_code=-1,
                            duration=0,
                            output=str(result_list),
                        )
                    )
                else:
                    for result in result_list:
                        report.results.append(result)
                        if on_result:
                            on_result(result)

            # Fail fast across priority groups
            if self.config.fail_fast and report.failed_results:
                break

        report.total_duration = time.perf_counter() - overall_start
        return report
