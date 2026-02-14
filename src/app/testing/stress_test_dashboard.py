"""
Real-time Reporting Dashboard for Conversational Stress Tests.

This module provides comprehensive reporting, visualization, and analysis capabilities
for the Anti-Sovereign Tier conversational stress testing framework.

Features:
- Real-time metrics dashboard
- Test progress visualization
- Conversation replay and analysis
- Vulnerability pattern detection
- Comprehensive reporting
"""

from __future__ import annotations

import json
import logging
import os
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DashboardMetrics:
    """Real-time metrics for the dashboard."""

    timestamp: str
    tests_running: int
    tests_completed: int
    tests_passed: int
    tests_failed: int
    total_turns_executed: int
    total_breaches_detected: int
    current_breach_rate: float
    average_turns_per_test: float
    estimated_time_remaining_seconds: float
    phases_in_progress: dict[str, int]
    category_progress: dict[str, dict[str, int]]


class ConversationalStressTestDashboard:
    """
    Real-time reporting dashboard for conversational stress tests.

    Provides:
    - Live metrics tracking
    - Progress visualization
    - Conversation analysis
    - Vulnerability reporting
    - Comprehensive analytics
    """

    def __init__(self, data_dir: str = "data/anti_sovereign_tests"):
        self.data_dir = data_dir
        self.results_dir = os.path.join(data_dir, "results")
        self.sessions_dir = os.path.join(self.results_dir, "sessions")
        self.reports_dir = os.path.join(data_dir, "reports")
        self.viz_dir = os.path.join(data_dir, "visualizations")

        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.viz_dir, exist_ok=True)

        logger.info("ConversationalStressTestDashboard initialized: %s", data_dir)

    def generate_live_metrics(
        self, test_progress: dict[str, Any], metrics: dict[str, Any]
    ) -> DashboardMetrics:
        """Generate real-time metrics for dashboard display."""
        # Count tests by status
        tests_running = sum(
            1 for p in test_progress.values() if p.get("status") == "running"
        )
        tests_completed = sum(
            1 for p in test_progress.values() if p.get("status") == "completed"
        )

        # Analyze phases
        phases_in_progress = defaultdict(int)
        for progress in test_progress.values():
            if progress.get("status") == "running":
                phase = progress.get("current_phase", "unknown")
                phases_in_progress[phase] += 1

        # Analyze categories
        category_progress = defaultdict(lambda: {"running": 0, "completed": 0, "failed": 0})
        for test_id, progress in test_progress.items():
            category = test_id.split("_")[1] if "_" in test_id else "unknown"
            status = progress.get("status", "unknown")
            if status in ["running", "completed", "failed"]:
                category_progress[category][status] += 1

        # Calculate breach rate
        total_turns = metrics.get("total_turns_executed", 0)
        total_breaches = metrics.get("total_breaches_detected", 0)
        breach_rate = total_breaches / total_turns if total_turns > 0 else 0.0

        # Estimate time remaining
        completed = tests_completed
        total = len(test_progress)
        avg_duration = metrics.get("average_test_duration", 0.0)
        estimated_remaining = (total - completed) * avg_duration if completed > 0 else 0.0

        return DashboardMetrics(
            timestamp=datetime.now(UTC).isoformat(),
            tests_running=tests_running,
            tests_completed=tests_completed,
            tests_passed=metrics.get("tests_passed", 0),
            tests_failed=metrics.get("tests_failed", 0),
            total_turns_executed=total_turns,
            total_breaches_detected=total_breaches,
            current_breach_rate=breach_rate,
            average_turns_per_test=metrics.get("average_turns_per_test", 0.0),
            estimated_time_remaining_seconds=estimated_remaining,
            phases_in_progress=dict(phases_in_progress),
            category_progress={k: dict(v) for k, v in category_progress.items()},
        )

    def generate_conversation_replay(
        self, session_id: str, output_file: str | None = None
    ) -> dict[str, Any]:
        """Generate detailed conversation replay for a session."""
        try:
            # Load session
            session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
            if not os.path.exists(session_file):
                return {"success": False, "error": "Session not found"}

            with open(session_file) as f:
                session = json.load(f)

            # Build replay
            replay = {
                "session_id": session_id,
                "test_info": {
                    "test_id": session["test"]["test_id"],
                    "category": session["test"]["category"],
                    "title": session["test"]["title"],
                },
                "metadata": {
                    "total_turns": session["total_turns"],
                    "total_breaches": session["total_breaches"],
                    "test_passed": session["test_passed"],
                    "duration_seconds": session["duration_seconds"],
                },
                "conversation": [],
                "phase_transitions": [],
                "breach_timeline": [],
                "defense_timeline": [],
            }

            current_phase = None
            for turn in session["turns"]:
                # Track phase transitions
                if turn["phase"] != current_phase:
                    replay["phase_transitions"].append({
                        "turn": turn["turn_number"],
                        "from_phase": current_phase,
                        "to_phase": turn["phase"],
                    })
                    current_phase = turn["phase"]

                # Add conversation turn
                replay["conversation"].append({
                    "turn": turn["turn_number"],
                    "phase": turn["phase"],
                    "attacker": turn["attacker_message"],
                    "system": turn["system_response"],
                    "status": turn["status"],
                    "vulnerability_score": turn["vulnerability_score"],
                })

                # Track breaches
                if turn["status"] in ["full_breach", "partial_breach"]:
                    replay["breach_timeline"].append({
                        "turn": turn["turn_number"],
                        "phase": turn["phase"],
                        "type": turn["status"],
                        "score": turn["vulnerability_score"],
                        "indicators": turn["success_indicators"],
                    })

                # Track defenses
                if turn["defense_mechanisms_triggered"]:
                    replay["defense_timeline"].append({
                        "turn": turn["turn_number"],
                        "phase": turn["phase"],
                        "defenses": turn["defense_mechanisms_triggered"],
                    })

            # Save replay if output file specified
            if output_file:
                output_path = os.path.join(self.reports_dir, output_file)
                with open(output_path, "w") as f:
                    json.dump(replay, f, indent=2)
                replay["replay_file"] = output_path

            return {"success": True, "replay": replay}

        except Exception as e:
            logger.error("Error generating conversation replay: %s", e, exc_info=True)
            return {"success": False, "error": str(e)}

    def analyze_vulnerability_patterns(
        self, sessions: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """Analyze vulnerability patterns across sessions."""
        if sessions is None:
            sessions = self._load_all_sessions()

        if not sessions:
            return {
                "success": False,
                "error": "No sessions found",
            }

        # Analyze patterns
        vulnerability_patterns = defaultdict(lambda: {
            "count": 0,
            "phases": defaultdict(int),
            "categories": defaultdict(int),
            "avg_turn": 0,
            "total_turn": 0,
        })

        attack_success_by_technique = defaultdict(lambda: {"attempts": 0, "successes": 0})
        phase_vulnerability_scores = defaultdict(list)
        category_breach_rates = defaultdict(lambda: {"turns": 0, "breaches": 0})

        for session in sessions:
            category = session["test"]["category"]
            total_turns_in_session = 0
            breaches_in_session = 0

            for turn in session["turns"]:
                total_turns_in_session += 1
                phase = turn["phase"]
                phase_vulnerability_scores[phase].append(turn["vulnerability_score"])

                # Track attack techniques
                for technique in turn.get("attack_techniques", []):
                    attack_success_by_technique[technique]["attempts"] += 1
                    if turn["status"] in ["full_breach", "partial_breach"]:
                        attack_success_by_technique[technique]["successes"] += 1

                # Track vulnerability patterns
                if turn["status"] in ["full_breach", "partial_breach"]:
                    breaches_in_session += 1
                    for indicator in turn.get("success_indicators", []):
                        vulnerability_patterns[indicator]["count"] += 1
                        vulnerability_patterns[indicator]["phases"][phase] += 1
                        vulnerability_patterns[indicator]["categories"][category] += 1
                        vulnerability_patterns[indicator]["total_turn"] += turn["turn_number"]

            # Calculate category breach rates
            category_breach_rates[category]["turns"] += total_turns_in_session
            category_breach_rates[category]["breaches"] += breaches_in_session

        # Calculate averages and rates
        for pattern in vulnerability_patterns.values():
            if pattern["count"] > 0:
                pattern["avg_turn"] = pattern["total_turn"] / pattern["count"]
            pattern["phases"] = dict(pattern["phases"])
            pattern["categories"] = dict(pattern["categories"])
            del pattern["total_turn"]

        # Calculate attack technique success rates
        technique_success_rates = {}
        for technique, stats in attack_success_by_technique.items():
            if stats["attempts"] > 0:
                technique_success_rates[technique] = {
                    "attempts": stats["attempts"],
                    "successes": stats["successes"],
                    "success_rate": stats["successes"] / stats["attempts"],
                }

        # Calculate phase vulnerability averages
        phase_avg_vulnerabilities = {}
        for phase, scores in phase_vulnerability_scores.items():
            if scores:
                phase_avg_vulnerabilities[phase] = {
                    "average": sum(scores) / len(scores),
                    "max": max(scores),
                    "min": min(scores),
                    "count": len(scores),
                }

        # Calculate category breach rates
        category_rates = {}
        for category, stats in category_breach_rates.items():
            if stats["turns"] > 0:
                category_rates[category] = {
                    "total_turns": stats["turns"],
                    "total_breaches": stats["breaches"],
                    "breach_rate": stats["breaches"] / stats["turns"],
                }

        return {
            "success": True,
            "analysis": {
                "vulnerability_patterns": dict(vulnerability_patterns),
                "attack_technique_effectiveness": technique_success_rates,
                "phase_vulnerability_scores": phase_avg_vulnerabilities,
                "category_breach_rates": category_rates,
                "total_sessions_analyzed": len(sessions),
            },
        }

    def generate_comprehensive_report(
        self, include_replays: bool = False
    ) -> dict[str, Any]:
        """Generate comprehensive analysis report."""
        try:
            # Load all sessions
            sessions = self._load_all_sessions()

            if not sessions:
                return {
                    "success": False,
                    "error": "No sessions found",
                }

            # Calculate overall statistics
            total_tests = len(sessions)
            passed_tests = sum(1 for s in sessions if s.get("test_passed", False))
            failed_tests = total_tests - passed_tests

            total_turns = sum(s.get("total_turns", 0) for s in sessions)
            total_breaches = sum(s.get("total_breaches", 0) for s in sessions)

            # Analyze by category
            category_stats = defaultdict(lambda: {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "turns": 0,
                "breaches": 0,
            })

            for session in sessions:
                category = session["test"]["category"]
                category_stats[category]["total"] += 1
                category_stats[category]["turns"] += session.get("total_turns", 0)
                category_stats[category]["breaches"] += session.get("total_breaches", 0)

                if session.get("test_passed", False):
                    category_stats[category]["passed"] += 1
                else:
                    category_stats[category]["failed"] += 1

            # Analyze vulnerability patterns
            vulnerability_analysis = self.analyze_vulnerability_patterns(sessions)

            # Build report
            report = {
                "report_title": "Anti-Sovereign Conversational Stress Test Analysis",
                "generated_at": datetime.now(UTC).isoformat(),
                "executive_summary": {
                    "total_tests": total_tests,
                    "tests_passed": passed_tests,
                    "tests_failed": failed_tests,
                    "success_rate": passed_tests / total_tests if total_tests > 0 else 0.0,
                    "total_conversation_turns": total_turns,
                    "average_turns_per_test": total_turns / total_tests if total_tests > 0 else 0.0,
                    "total_breaches_detected": total_breaches,
                    "overall_breach_rate": total_breaches / total_turns if total_turns > 0 else 0.0,
                },
                "category_analysis": {
                    category: {
                        **stats,
                        "success_rate": stats["passed"] / stats["total"] if stats["total"] > 0 else 0.0,
                        "breach_rate": stats["breaches"] / stats["turns"] if stats["turns"] > 0 else 0.0,
                    }
                    for category, stats in category_stats.items()
                },
                "vulnerability_analysis": vulnerability_analysis.get("analysis", {}),
                "recommendations": self._generate_recommendations(
                    total_tests, passed_tests, total_breaches, total_turns
                ),
            }

            # Add conversation replays if requested
            if include_replays:
                report["sample_replays"] = []
                # Include up to 5 failed test replays
                failed_sessions = [s for s in sessions if not s.get("test_passed", False)]
                for session in failed_sessions[:5]:
                    replay = self.generate_conversation_replay(session["session_id"])
                    if replay["success"]:
                        report["sample_replays"].append(replay["replay"])

            # Save report
            report_filename = f"comprehensive_report_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json"
            report_path = os.path.join(self.reports_dir, report_filename)

            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)

            report["report_file"] = report_path

            logger.info("Generated comprehensive report: %s", report_path)

            return {
                "success": True,
                "report": report,
            }

        except Exception as e:
            logger.error("Error generating comprehensive report: %s", e, exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    def export_metrics_timeseries(
        self, output_file: str | None = None
    ) -> dict[str, Any]:
        """Export metrics as time series for visualization."""
        try:
            sessions = self._load_all_sessions()

            if not sessions:
                return {"success": False, "error": "No sessions found"}

            # Sort sessions by start time
            sessions.sort(key=lambda s: s.get("started_at", ""))

            # Build time series
            timeseries = []
            cumulative_tests = 0
            cumulative_passed = 0
            cumulative_turns = 0
            cumulative_breaches = 0

            for session in sessions:
                cumulative_tests += 1
                cumulative_turns += session.get("total_turns", 0)
                cumulative_breaches += session.get("total_breaches", 0)

                if session.get("test_passed", False):
                    cumulative_passed += 1

                timeseries.append({
                    "timestamp": session.get("completed_at", ""),
                    "test_id": session["test"]["test_id"],
                    "category": session["test"]["category"],
                    "cumulative_tests": cumulative_tests,
                    "cumulative_passed": cumulative_passed,
                    "cumulative_failed": cumulative_tests - cumulative_passed,
                    "cumulative_turns": cumulative_turns,
                    "cumulative_breaches": cumulative_breaches,
                    "cumulative_breach_rate": (
                        cumulative_breaches / cumulative_turns
                        if cumulative_turns > 0
                        else 0.0
                    ),
                    "test_passed": session.get("test_passed", False),
                    "test_turns": session.get("total_turns", 0),
                    "test_breaches": session.get("total_breaches", 0),
                })

            # Save time series
            if output_file:
                output_path = os.path.join(self.reports_dir, output_file)
            else:
                output_path = os.path.join(
                    self.reports_dir,
                    f"metrics_timeseries_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json",
                )

            with open(output_path, "w") as f:
                json.dump(timeseries, f, indent=2)

            return {
                "success": True,
                "timeseries": timeseries,
                "file": output_path,
            }

        except Exception as e:
            logger.error("Error exporting metrics timeseries: %s", e, exc_info=True)
            return {"success": False, "error": str(e)}

    def _load_all_sessions(self) -> list[dict[str, Any]]:
        """Load all session files."""
        sessions = []

        if not os.path.exists(self.sessions_dir):
            logger.warning("Sessions directory not found: %s", self.sessions_dir)
            return sessions

        for filename in os.listdir(self.sessions_dir):
            if filename.endswith(".json"):
                try:
                    filepath = os.path.join(self.sessions_dir, filename)
                    with open(filepath) as f:
                        session = json.load(f)
                        sessions.append(session)
                except Exception as e:
                    logger.error("Error loading session %s: %s", filename, e)

        logger.info("Loaded %d sessions", len(sessions))
        return sessions

    def _generate_recommendations(
        self,
        total_tests: int,
        passed_tests: int,
        total_breaches: int,
        total_turns: int,
    ) -> list[str]:
        """Generate security recommendations."""
        recommendations = []

        success_rate = passed_tests / total_tests if total_tests > 0 else 0.0
        breach_rate = total_breaches / total_turns if total_turns > 0 else 0.0

        if success_rate == 1.0:
            recommendations.append(
                "EXCELLENT: All 400 conversational stress tests passed. "
                "System demonstrates exceptional resilience against extended adversarial conversations."
            )
        elif success_rate >= 0.95:
            recommendations.append(
                f"VERY GOOD: {success_rate:.1%} success rate. "
                "System shows strong defense with minor vulnerabilities. "
                "Focus on addressing specific failure cases."
            )
        elif success_rate >= 0.80:
            recommendations.append(
                f"GOOD: {success_rate:.1%} success rate. "
                "System generally secure but has notable vulnerabilities. "
                "Strengthen governance and boundary detection."
            )
        elif success_rate >= 0.60:
            recommendations.append(
                f"MODERATE: {success_rate:.1%} success rate. "
                "Significant security gaps detected. Comprehensive security review required."
            )
        else:
            recommendations.append(
                f"CRITICAL: {success_rate:.1%} success rate. "
                "System highly vulnerable to conversational attacks. "
                "Immediate remediation required across all layers."
            )

        if breach_rate > 0.1:
            recommendations.append(
                f"HIGH BREACH RATE: {breach_rate:.2%} of conversation turns resulted in breaches. "
                "Enhance real-time threat detection and response mechanisms."
            )
        elif breach_rate > 0.05:
            recommendations.append(
                f"MODERATE BREACH RATE: {breach_rate:.2%} breach rate detected. "
                "Improve boundary detection and governance enforcement."
            )

        recommendations.append(
            "Continue regular anti-sovereign stress testing to maintain security posture "
            "against evolving adversarial techniques."
        )

        return recommendations


def generate_html_dashboard(
    dashboard: ConversationalStressTestDashboard,
    output_file: str = "dashboard.html",
) -> str:
    """Generate HTML dashboard for visualization."""
    # This would generate an interactive HTML dashboard
    # For now, generate a simple summary

    report = dashboard.generate_comprehensive_report()

    if not report["success"]:
        return ""

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Anti-Sovereign Conversational Stress Test Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }}
        .header {{ background: #2d2d2d; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #4CAF50; }}
        .metric-label {{ font-size: 14px; color: #999; }}
        .category {{ background: #2d2d2d; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .success {{ color: #4CAF50; }}
        .warning {{ color: #ff9800; }}
        .critical {{ color: #f44336; }}
        .recommendations {{ background: #2d2d2d; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .recommendations li {{ margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Anti-Sovereign Tier Conversational Stress Test Dashboard</h1>
        <p>Generated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    </div>

    <div class="metrics">
        <div class="metric">
            <div class="metric-value">{report['report']['executive_summary']['total_tests']}</div>
            <div class="metric-label">Total Tests</div>
        </div>
        <div class="metric">
            <div class="metric-value success">{report['report']['executive_summary']['tests_passed']}</div>
            <div class="metric-label">Passed</div>
        </div>
        <div class="metric">
            <div class="metric-value critical">{report['report']['executive_summary']['tests_failed']}</div>
            <div class="metric-label">Failed</div>
        </div>
        <div class="metric">
            <div class="metric-value">{report['report']['executive_summary']['total_conversation_turns']:,}</div>
            <div class="metric-label">Total Turns</div>
        </div>
        <div class="metric">
            <div class="metric-value warning">{report['report']['executive_summary']['total_breaches_detected']}</div>
            <div class="metric-label">Breaches</div>
        </div>
        <div class="metric">
            <div class="metric-value">{report['report']['executive_summary']['success_rate']:.1%}</div>
            <div class="metric-label">Success Rate</div>
        </div>
    </div>

    <div class="recommendations">
        <h2>Recommendations</h2>
        <ul>
        {''.join(f"<li>{rec}</li>" for rec in report['report']['recommendations'])}
        </ul>
    </div>

    <h2>Category Analysis</h2>
    {''.join(f'''
    <div class="category">
        <h3>{cat}</h3>
        <p>Tests: {stats['total']} | Passed: {stats['passed']} | Failed: {stats['failed']}</p>
        <p>Success Rate: {stats['success_rate']:.1%} | Breach Rate: {stats['breach_rate']:.2%}</p>
    </div>
    ''' for cat, stats in report['report']['category_analysis'].items())}

</body>
</html>
"""

    output_path = os.path.join(dashboard.viz_dir, output_file)
    with open(output_path, "w") as f:
        f.write(html)

    logger.info("Generated HTML dashboard: %s", output_path)
    return output_path
