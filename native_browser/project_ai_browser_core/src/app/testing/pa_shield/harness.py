"""Top-level benchmark harness for PA-SHIELD."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.testing.pa_shield.audit.logger import AuditLogger
from app.testing.pa_shield.engine.executor import Executor
from app.testing.pa_shield.engine.loader import load_suite
from app.testing.pa_shield.engine.mutator import Mutator
from app.testing.pa_shield.legacy import run_legacy_project_ai_suites
from app.testing.pa_shield.metrics.reproducibility import ReplayVerifier
from app.testing.pa_shield.metrics.scoring import Scorer
from app.testing.pa_shield.models import AttackCase, AttackResult
from app.testing.pa_shield.reports.export_json import write_json_report
from app.testing.pa_shield.reports.export_md import write_markdown_report
from app.testing.pa_shield.reports.report import build_compare_report, build_run_report
from app.testing.pa_shield.runners import BaselineRunner, ProjectAIRunner


class EvaluationHarness:
    """Benchmark harness for governed vs baseline AI systems."""

    def __init__(self) -> None:
        self.executor = Executor()
        self.mutator = Mutator()
        self.scorer = Scorer()
        self.replay = ReplayVerifier()

    @staticmethod
    def create_runner(system_name: str):
        """Construct a supported system runner."""
        if system_name == "baseline":
            return BaselineRunner()
        if system_name == "project_ai":
            return ProjectAIRunner()
        raise ValueError(f"Unsupported system '{system_name}'.")

    def _expand_cases(self, suite: str, fuzz: bool, iterations: int, seed: int) -> list[AttackCase]:
        cases = load_suite(suite)
        if not fuzz:
            return cases
        self.mutator.seed = seed
        expanded = list(cases)
        for case in cases:
            expanded.extend(self.mutator.mutate_case(case, iterations))
        return expanded

    def run_system(
        self,
        *,
        system_name: str,
        suite: str,
        output_dir: Path,
        fuzz: bool = False,
        iterations: int = 0,
        seed: int = 1337,
        include_legacy: bool = False,
    ) -> dict[str, Any]:
        """Execute the benchmark for one system."""
        runner = self.create_runner(system_name)
        cases = self._expand_cases(suite=suite, fuzz=fuzz, iterations=iterations, seed=seed)
        audit_log = output_dir / f"{system_name}-audit.jsonl"
        audit = AuditLogger(audit_log)
        results: list[AttackResult] = []

        for index, case in enumerate(cases, start=1):
            trace = self.executor.execute_case(
                runner=runner,
                case=case,
                session_id=f"{system_name}_{index:04d}",
            )
            scored = self.scorer.score(
                system_name=runner.system_name,
                case=case,
                outcome=trace.final_outcome,
                turns=trace.turns,
                latency_ms=trace.total_latency_ms,
                average_turn_latency_ms=trace.average_turn_latency_ms,
                audit_hash=None,
                replay_match=None,
            )
            audit_hash = audit.log_case(AuditLogger.result_payload(trace, scored, runner.system_name))
            scored.audit_hash = audit_hash
            results.append(scored)

        replay_summary = self.replay.replay_log(self.create_runner(system_name), audit_log)
        replay_lookup = {detail["attack_id"]: detail["matched"] for detail in replay_summary["details"]}
        for result in results:
            result.replay_match = replay_lookup.get(result.attack_id)

        summary = self.scorer.summarize(system_name=runner.system_name, results=results)
        summary["metrics"]["replay_match_rate"] = replay_summary["replay_match_rate"]
        summary["metrics"]["reproducibility_score"] = replay_summary["replay_match_rate"]

        legacy_results = {}
        if include_legacy and system_name == "project_ai":
            legacy_results = run_legacy_project_ai_suites(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)
        report = build_run_report(
            system_name=runner.system_name,
            system_version=runner.system_version,
            suite=suite,
            fuzzed=fuzz,
            seed=seed,
            iterations=iterations,
            summary=summary,
            results=[result.to_dict() for result in results],
            audit_log=audit_log,
            legacy_results=legacy_results,
        )
        write_json_report(report, output_dir / f"{system_name}-report.json")
        write_markdown_report(report, output_dir / f"{system_name}-report.md")
        return report

    def compare_systems(
        self,
        *,
        systems: list[str],
        suite: str,
        output_dir: Path,
        fuzz: bool = False,
        iterations: int = 0,
        seed: int = 1337,
        include_legacy: bool = False,
    ) -> dict[str, Any]:
        """Run the benchmark for multiple systems and produce a comparison report."""
        system_reports = {
            system: self.run_system(
                system_name=system,
                suite=suite,
                output_dir=output_dir / system,
                fuzz=fuzz,
                iterations=iterations,
                seed=seed,
                include_legacy=include_legacy,
            )
            for system in systems
        }
        compare_report = build_compare_report(
            suite=suite,
            fuzzed=fuzz,
            iterations=iterations,
            seed=seed,
            system_reports=system_reports,
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        write_json_report(compare_report, output_dir / "compare-report.json")
        write_markdown_report(compare_report, output_dir / "compare-report.md")
        return compare_report
