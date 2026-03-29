"""Markdown export for PA-SHIELD reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _system_summary_lines(system_name: str, report: dict[str, Any]) -> list[str]:
    metrics = report["results"]["metrics"]
    totals = report["results"]["totals"]
    return [
        f"## {system_name}",
        "",
        f"- Total cases: {totals['total_cases']}",
        f"- Passed: {totals['passed']}",
        f"- Attack success rate: {metrics['attack_success_rate']:.2%}",
        f"- Detection rate: {metrics['detection_rate']:.2%}",
        f"- Enforcement rate: {metrics['enforcement_rate']:.2%}",
        f"- False positive rate: {metrics['false_positive_rate']:.2%}",
        f"- Replay match rate: {metrics['replay_match_rate']:.2%}",
        f"- Average latency: {metrics['latency_overhead_ms']:.3f} ms",
        "",
        "| Threat Class | Cases | Pass Rate | Attack Success | Avg Latency (ms) |",
        "|---|---:|---:|---:|---:|",
    ] + [
        (
            f"| {threat_class} | {stats['total']} | {stats['pass_rate']:.2%} | "
            f"{stats['attack_success_rate']:.2%} | {stats['average_latency_ms']:.3f} |"
        )
        for threat_class, stats in report["results"]["by_threat_class"].items()
    ] + [""]


def write_markdown_report(report: dict[str, Any], output_path: Path) -> Path:
    """Write a single-system or comparison markdown report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if "systems" in report and isinstance(report["systems"], dict):
        lines = [
            "# PA-SHIELD Comparison Report",
            "",
            f"- Suite: {report['suite']}",
            f"- Fuzzed: {report['fuzzed']}",
            f"- Iterations: {report['iterations']}",
            f"- Seed: {report['seed']}",
            "",
            "| System | Attack Success | Detection | Enforcement | False Positives | Avg Latency (ms) |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for system_name, system_report in report["systems"].items():
            metrics = system_report["results"]["metrics"]
            lines.append(
                f"| {system_name} | {metrics['attack_success_rate']:.2%} | "
                f"{metrics['detection_rate']:.2%} | {metrics['enforcement_rate']:.2%} | "
                f"{metrics['false_positive_rate']:.2%} | {metrics['latency_overhead_ms']:.3f} |"
            )
        delta = report.get("delta_vs_baseline")
        if delta:
            lines.extend(
                [
                    "",
                    "## Delta vs Baseline",
                    "",
                    f"- Attack success rate reduction: {delta['attack_success_rate_reduction']:.2%}",
                    f"- Detection rate gain: {delta['detection_rate_gain']:.2%}",
                    f"- Enforcement rate gain: {delta['enforcement_rate_gain']:.2%}",
                    f"- Latency overhead: {delta['latency_overhead_ms']:.3f} ms",
                    "",
                ]
            )
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path

    lines = [
        "# PA-SHIELD Run Report",
        "",
        f"- System: {report['metadata']['system']}",
        f"- Version: {report['metadata']['version']}",
        f"- Suite: {report['metadata']['suite']}",
        f"- Fuzzed: {report['metadata']['fuzzed']}",
        f"- Seed: {report['metadata']['seed']}",
        "",
    ]
    lines.extend(_system_summary_lines(report["metadata"]["system"], report))
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
