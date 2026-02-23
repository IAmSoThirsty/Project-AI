"""
TAAR Executor — Async concurrent command execution.

Runs runner commands as subprocesses with parallel dispatch,
timeout management, and output capture. Integrates with the
result cache to skip unchanged work.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path

from taar.cache import ResultCache
from taar.config import Runner, RunnerCommand, TaarConfig


@dataclass
class TaskResult:
    """Result of executing a single runner command."""

    runner_name: str
    command_name: str
    passed: bool
    return_code: int
    duration: float
    output: str
    cached: bool = False
    files: list[Path] = field(default_factory=list)

    @property
    def status_icon(self) -> str:
        if self.cached:
            return "⊙"
        return "✓" if self.passed else "✗"

    @property
    def status_label(self) -> str:
        if self.cached:
            return "CACHED"
        return "PASS" if self.passed else "FAIL"


@dataclass
class RunReport:
    """Aggregate report of all task results from a run."""

    results: list[TaskResult] = field(default_factory=list)
    total_duration: float = 0.0

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def cached_count(self) -> int:
        return sum(1 for r in self.results if r.cached)

    @property
    def executed_count(self) -> int:
        return sum(1 for r in self.results if not r.cached)

    @property
    def failed_results(self) -> list[TaskResult]:
        return [r for r in self.results if not r.passed]


class Executor:
    """
    Async executor for TAAR runner commands.

    Dispatches commands as subprocess tasks with configurable
    parallelism. Uses the result cache to skip unchanged work.
    """

    def __init__(self, config: TaarConfig, cache: ResultCache):
        self.config = config
        self.cache = cache
        self._semaphore = asyncio.Semaphore(config.parallelism)

    async def execute_command(
        self,
        runner: Runner,
        command: RunnerCommand,
        files: list[Path],
        test_files: list[Path] | None = None,
    ) -> TaskResult:
        """
        Execute a single runner command, with cache lookup first.

        If the cache contains a valid entry for the same files+command,
        returns the cached result immediately.
        """
        # Check cache first
        cached = self.cache.lookup(
            runner.name, command.name, files, command.template
        )
        if cached and cached.passed:
            return TaskResult(
                runner_name=runner.name,
                command_name=command.name,
                passed=cached.passed,
                return_code=cached.return_code,
                duration=cached.duration,
                output=cached.output,
                cached=True,
                files=files,
            )

        # Render command with file lists
        file_strs = [str(f) for f in files]
        test_strs = [str(f) for f in (test_files or [])]
        rendered = command.render(files=file_strs, test_files=test_strs or file_strs)

        # Execute with semaphore for parallelism control
        async with self._semaphore:
            result = await self._run_subprocess(rendered)

        passed = result["returncode"] == 0
        duration = result["duration"]
        output = result["output"]

        # Store in cache
        self.cache.store(
            runner_name=runner.name,
            command_name=command.name,
            files=files,
            command_template=command.template,
            passed=passed,
            return_code=result["returncode"],
            duration=duration,
            output=output,
        )

        return TaskResult(
            runner_name=runner.name,
            command_name=command.name,
            passed=passed,
            return_code=result["returncode"],
            duration=duration,
            output=output,
            cached=False,
            files=files,
        )

    async def execute_runner(
        self,
        runner: Runner,
        files: list[Path],
        test_files: list[Path] | None = None,
    ) -> list[TaskResult]:
        """
        Execute all commands for a runner, ordered by priority.

        Commands with the same priority run in parallel.
        If fail_fast is enabled, stops on first failure.
        """
        results = []
        commands = runner.commands_by_priority()

        # Group by priority level
        priority_groups: dict[int, list[RunnerCommand]] = {}
        for cmd in commands:
            priority_groups.setdefault(cmd.priority, []).append(cmd)

        for priority in sorted(priority_groups.keys()):
            group = priority_groups[priority]

            # Execute same-priority commands in parallel
            tasks = [
                self.execute_command(runner, cmd, files, test_files)
                for cmd in group
            ]
            group_results = await asyncio.gather(*tasks, return_exceptions=True)

            for gr in group_results:
                if isinstance(gr, Exception):
                    results.append(
                        TaskResult(
                            runner_name=runner.name,
                            command_name="unknown",
                            passed=False,
                            return_code=-1,
                            duration=0,
                            output=str(gr),
                            files=files,
                        )
                    )
                else:
                    results.append(gr)

            # Fail fast: stop if any command in this priority group failed
            if self.config.fail_fast and any(not r.passed for r in results if not r.cached):
                break

        return results

    async def _run_subprocess(self, command: str, timeout: int = 120) -> dict:
        """Run a shell command as an async subprocess."""
        start = time.perf_counter()
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.config.project_root),
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
            duration = time.perf_counter() - start

            output = stdout.decode("utf-8", errors="replace")
            if stderr:
                output += "\n" + stderr.decode("utf-8", errors="replace")

            return {
                "returncode": proc.returncode or 0,
                "output": output,
                "duration": duration,
            }
        except asyncio.TimeoutError:
            duration = time.perf_counter() - start
            return {
                "returncode": -1,
                "output": f"TIMEOUT after {timeout}s",
                "duration": duration,
            }
        except Exception as e:
            duration = time.perf_counter() - start
            return {
                "returncode": -1,
                "output": f"ERROR: {e}",
                "duration": duration,
            }
