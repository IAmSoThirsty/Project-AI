"""
HTML Reporter for E2E Tests

Generates human-readable HTML reports with visualizations.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class HTMLReporter:
    """Generates HTML reports for E2E tests."""

    def __init__(self, output_dir: Path | None = None):
        """Initialize HTML reporter.

        Args:
            output_dir: Directory for HTML reports
        """
        self.output_dir = output_dir or Path(__file__).parent.parent / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self,
        test_results: dict[str, Any],
        coverage_metrics: dict[str, Any] | None = None,
        artifacts: dict[str, Any] | None = None,
    ) -> Path:
        """Generate HTML report.

        Args:
            test_results: Test execution results
            coverage_metrics: Coverage information
            artifacts: Test artifacts

        Returns:
            Path to generated HTML report
        """
        html_content = self._generate_html(
            test_results,
            coverage_metrics,
            artifacts,
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"e2e_report_{timestamp}.html"
        report_file.write_text(html_content)
        logger.info(f"Generated HTML report: {report_file}")
        return report_file

    def _generate_html(
        self,
        test_results: dict[str, Any],
        coverage_metrics: dict[str, Any] | None,
        artifacts: dict[str, Any] | None,
    ) -> str:
        """Generate HTML content.

        Args:
            test_results: Test execution results
            coverage_metrics: Coverage information
            artifacts: Test artifacts

        Returns:
            HTML content string
        """
        # Extract statistics
        total = test_results.get("total_tests", 0)
        passed = test_results.get("passed", 0)
        failed = test_results.get("failed", 0)
        skipped = test_results.get("skipped", 0)
        duration = test_results.get("total_duration", 0)

        pass_rate = (passed / total * 100) if total > 0 else 0

        # Build HTML
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E2E Test Report - Project AI</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}

        header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}

        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}

        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}

        .stat-card .label {{
            font-size: 1em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .stat-card.passed .value {{ color: #28a745; }}
        .stat-card.failed .value {{ color: #dc3545; }}
        .stat-card.skipped .value {{ color: #ffc107; }}
        .stat-card.total .value {{ color: #007bff; }}
        .stat-card.duration .value {{ font-size: 2em; }}

        .section {{
            padding: 30px;
            border-bottom: 1px solid #e9ecef;
        }}

        .section h2 {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #2c3e50;
            border-left: 4px solid #667eea;
            padding-left: 15px;
        }}

        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #e9ecef;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
            transition: width 1s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}

        .test-list {{
            margin-top: 20px;
        }}

        .test-item {{
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }}

        .test-item.passed {{ border-left-color: #28a745; }}
        .test-item.failed {{ border-left-color: #dc3545; }}
        .test-item.skipped {{ border-left-color: #ffc107; }}

        .test-item .test-name {{
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .test-item .test-info {{
            font-size: 0.9em;
            color: #666;
        }}

        .coverage-section {{
            background: #f8f9fa;
        }}

        .coverage-meter {{
            width: 100%;
            height: 50px;
            background: #e9ecef;
            border-radius: 25px;
            overflow: hidden;
            position: relative;
            margin: 20px 0;
        }}

        .coverage-fill {{
            height: 100%;
            transition: width 1s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1.2em;
        }}

        .coverage-fill.excellent {{ background: linear-gradient(90deg, #28a745 0%, #20c997 100%); }}
        .coverage-fill.good {{ background: linear-gradient(90deg, #ffc107 0%, #fd7e14 100%); }}
        .coverage-fill.poor {{ background: linear-gradient(90deg, #dc3545 0%, #c82333 100%); }}

        footer {{
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }}

        .timestamp {{
            color: #ecf0f1;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏛️ Project AI - E2E Test Report</h1>
            <div class="subtitle">Comprehensive End-to-End Testing Results</div>
        </header>

        <div class="stats-grid">
            <div class="stat-card total">
                <div class="label">Total Tests</div>
                <div class="value">{total}</div>
            </div>
            <div class="stat-card passed">
                <div class="label">Passed</div>
                <div class="value">{passed}</div>
            </div>
            <div class="stat-card failed">
                <div class="label">Failed</div>
                <div class="value">{failed}</div>
            </div>
            <div class="stat-card skipped">
                <div class="label">Skipped</div>
                <div class="value">{skipped}</div>
            </div>
            <div class="stat-card duration">
                <div class="label">Duration</div>
                <div class="value">{duration:.2f}s</div>
            </div>
        </div>

        <div class="section">
            <h2>Test Success Rate</h2>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {pass_rate}%">
                    {pass_rate:.1f}% Pass Rate
                </div>
            </div>
        </div>
"""

        # Add coverage section if available
        if coverage_metrics:
            coverage_pct = coverage_metrics.get("coverage_percentage", 0)
            coverage_class = (
                "excellent" if coverage_pct >= 80
                else "good" if coverage_pct >= 60
                else "poor"
            )

            html += f"""
        <div class="section coverage-section">
            <h2>Test Coverage</h2>
            <div class="coverage-meter">
                <div class="coverage-fill {coverage_class}" style="width: {coverage_pct}%">
                    {coverage_pct:.1f}% Coverage
                </div>
            </div>
            <div class="test-info">
                <p>Total Statements: {coverage_metrics.get('total_statements', 0)}</p>
                <p>Covered Statements: {coverage_metrics.get('covered_statements', 0)}</p>
                <p>Missing Statements: {coverage_metrics.get('missing_statements', 0)}</p>
            </div>
        </div>
"""

        # Add test results section
        test_suites = test_results.get("test_suites", [])
        if test_suites:
            html += """
        <div class="section">
            <h2>Test Results</h2>
            <div class="test-list">
"""
            for suite in test_suites:
                suite_name = suite.get("suite_name", "Unknown Suite")
                html += f"<h3>{suite_name}</h3>"

                for test in suite.get("tests", []):
                    test_name = test.get("test_name", "Unknown Test")
                    status = test.get("status", "unknown")
                    test_duration = test.get("duration", 0)

                    html += f"""
                <div class="test-item {status}">
                    <div class="test-name">{test_name}</div>
                    <div class="test-info">
                        Status: {status.upper()} | Duration: {test_duration:.3f}s
                    </div>
                </div>
"""

            html += """
            </div>
        </div>
"""

        # Add artifacts section if available
        if artifacts:
            html += f"""
        <div class="section">
            <h2>Test Artifacts</h2>
            <div class="test-info">
                <p>Logs: {artifacts.get('logs', 0)}</p>
                <p>Screenshots: {artifacts.get('screenshots', 0)}</p>
                <p>API Dumps: {artifacts.get('dumps', 0)}</p>
                <p>Error Traces: {artifacts.get('errors', 0)}</p>
            </div>
        </div>
"""

        # Close HTML
        html += f"""
        <footer>
            <div class="timestamp">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
            <div>Project AI - Production-Grade E2E Testing Framework</div>
        </footer>
    </div>
</body>
</html>
"""

        return html
