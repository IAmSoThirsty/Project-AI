#!/usr/bin/env python3
"""
Automated Test Report Documentation Updater

Production-grade system that parses CI test artifacts and automatically updates
all documentation files with accurate, current test results.

Features:
- Multi-format parser (JSON, Markdown, JUnit XML, pytest JSON)
- Category-level statistics with pass/fail counts
- Automated badge generation
- Failed test surfacing
- Git integration for automatic commits
- Config-driven, zero placeholders
"""

import argparse
import glob
import json
import logging
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_report_updater.log')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Individual test result."""
    test_id: str
    name: str
    category: str
    status: str  # PASSED, FAILED, SKIPPED, WARNING, ERROR
    severity: str = "unknown"
    execution_time_ms: float = 0.0
    error_message: Optional[str] = None
    steps_executed: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class CategoryStats:
    """Statistics for a test category."""
    category: str
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    warning: int = 0
    error: int = 0
    pass_rate: float = 0.0
    failed_tests: List[TestResult] = field(default_factory=list)


@dataclass
class OverallStats:
    """Overall test statistics."""
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    warning: int = 0
    error: int = 0
    pass_rate: float = 0.0
    coverage_percentage: float = 0.0
    categories: Dict[str, CategoryStats] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    overall_status: str = "unknown"


class ArtifactParser:
    """Parse test artifacts in various formats."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ArtifactParser")
    
    def parse_all_artifacts(self) -> OverallStats:
        """Parse all configured artifacts and aggregate results."""
        stats = OverallStats()
        
        for source_name, source_config in self.config.get('artifact_sources', {}).items():
            if not source_config.get('enabled', True):
                continue
            
            path_pattern = source_config.get('path', '')
            format_type = source_config.get('format', 'json')
            
            self.logger.info(f"Parsing {source_name}: {path_pattern} (format: {format_type})")
            
            try:
                if format_type == 'json':
                    self._parse_json_artifacts(path_pattern, stats)
                elif format_type == 'pytest-json':
                    self._parse_pytest_json(path_pattern, stats)
                elif format_type == 'junit-xml':
                    self._parse_junit_xml(path_pattern, stats)
                elif format_type == 'markdown':
                    self._parse_markdown_report(path_pattern, stats)
            except Exception as e:
                self.logger.error(f"Error parsing {source_name}: {e}", exc_info=True)
        
        # Calculate final statistics
        self._calculate_statistics(stats)
        
        return stats
    
    def _parse_json_artifacts(self, pattern: str, stats: OverallStats) -> None:
        """Parse JSON artifacts (ci-reports/*.json)."""
        files = glob.glob(pattern)
        
        for filepath in files:
            self.logger.info(f"  Reading {filepath}")
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle unified-report.json format
                if 'overall_metrics' in data:
                    self._parse_unified_report(data, stats)
                # Handle individual report format
                elif 'metadata' in data and 'metrics' in data:
                    self._parse_individual_report(data, stats, filepath)
                # Handle test execution results
                elif 'test_results' in data:
                    self._parse_test_execution_results(data, stats)
                else:
                    self.logger.warning(f"Unknown JSON format in {filepath}")
            
            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON in {filepath}: {e}")
            except Exception as e:
                self.logger.error(f"Error reading {filepath}: {e}")
    
    def _parse_unified_report(self, data: Dict[str, Any], stats: OverallStats) -> None:
        """Parse unified-report.json format."""
        metrics = data.get('overall_metrics', {})
        
        # Add to overall stats
        tests_run = metrics.get('total_tests_run', 0)
        tests_passed = metrics.get('tests_passed', 0)
        tests_warning = metrics.get('tests_warning', 0)
        tests_failed = metrics.get('tests_failed', 0)
        
        stats.total_tests += tests_run
        stats.passed += tests_passed
        stats.warning += tests_warning
        stats.failed += tests_failed
        
        # Parse individual test results
        individual_results = data.get('individual_results', {})
        for test_name, test_data in individual_results.items():
            self._parse_test_category(test_name, test_data, stats)
        
        self.logger.info(f"  Parsed unified report: {tests_run} tests, {tests_passed} passed")
    
    def _parse_individual_report(self, data: Dict[str, Any], stats: OverallStats, filepath: str) -> None:
        """Parse individual test report format."""
        metrics = data.get('metrics', {})
        metadata = data.get('metadata', {})
        
        # Determine category from filename or metadata
        category = Path(filepath).stem.replace('-latest', '').upper()
        if category not in stats.categories:
            stats.categories[category] = CategoryStats(category=category)
        
        cat_stats = stats.categories[category]
        
        # Update category stats based on metrics
        total_prompts = metrics.get('total_prompts', 0)
        blocked = metrics.get('blocked_count', 0)
        
        cat_stats.total += total_prompts
        cat_stats.passed += blocked
        cat_stats.failed += (total_prompts - blocked)
        
        # Parse individual test details if available
        if 'test_cases' in data:
            for test_case in data['test_cases']:
                self._add_test_result(test_case, category, cat_stats, stats)
    
    def _parse_test_category(self, test_name: str, test_data: Dict[str, Any], stats: OverallStats) -> None:
        """Parse a test category from unified report."""
        category = test_name.upper()
        
        if category not in stats.categories:
            stats.categories[category] = CategoryStats(category=category)
        
        cat_stats = stats.categories[category]
        
        metrics = test_data.get('metrics', {})
        
        # Handle different metric formats
        if 'total_prompts' in metrics:
            cat_stats.total += metrics.get('total_prompts', 0)
            cat_stats.passed += metrics.get('blocked_count', 0)
            cat_stats.failed += (metrics.get('total_prompts', 0) - metrics.get('blocked_count', 0))
        elif 'total_scenarios' in metrics:
            cat_stats.total += metrics.get('total_scenarios', 0)
            cat_stats.passed += metrics.get('mitigated_count', 0)
            cat_stats.failed += metrics.get('attack_success_count', 0)
        
        # Extract failed tests if available
        if 'failed_tests' in test_data:
            for failed_test in test_data['failed_tests']:
                test_result = TestResult(
                    test_id=failed_test.get('id', 'unknown'),
                    name=failed_test.get('name', 'unknown'),
                    category=category,
                    status='FAILED',
                    error_message=failed_test.get('error', '')
                )
                cat_stats.failed_tests.append(test_result)
    
    def _parse_test_execution_results(self, data: Dict[str, Any], stats: OverallStats) -> None:
        """Parse test execution results format."""
        for test_result_data in data.get('test_results', []):
            category = test_result_data.get('category', 'UNKNOWN').upper()
            
            if category not in stats.categories:
                stats.categories[category] = CategoryStats(category=category)
            
            cat_stats = stats.categories[category]
            
            test_result = TestResult(
                test_id=test_result_data.get('test_id', 'unknown'),
                name=test_result_data.get('test_name', 'unknown'),
                category=category,
                status=test_result_data.get('status', 'UNKNOWN'),
                severity=test_result_data.get('severity', 'unknown'),
                execution_time_ms=test_result_data.get('execution_time_ms', 0.0),
                error_message=test_result_data.get('errors', [''])[0] if test_result_data.get('errors') else None,
                steps_executed=test_result_data.get('steps_executed', [])
            )
            
            self._add_test_result(test_result_data, category, cat_stats, stats)
    
    def _add_test_result(self, test_data: Dict[str, Any], category: str, cat_stats: CategoryStats, stats: OverallStats) -> None:
        """Add a test result to statistics."""
        status = test_data.get('status', 'UNKNOWN').upper()
        
        cat_stats.total += 1
        stats.total_tests += 1
        
        if status in ['PASSED', 'PASS', 'SUCCESS']:
            cat_stats.passed += 1
            stats.passed += 1
        elif status in ['FAILED', 'FAIL', 'FAILURE']:
            cat_stats.failed += 1
            stats.failed += 1
            
            # Store failed test for reporting
            test_result = TestResult(
                test_id=test_data.get('test_id', test_data.get('id', 'unknown')),
                name=test_data.get('test_name', test_data.get('name', 'unknown')),
                category=category,
                status='FAILED',
                error_message=test_data.get('error_message', test_data.get('error', ''))
            )
            cat_stats.failed_tests.append(test_result)
        elif status in ['SKIPPED', 'SKIP']:
            cat_stats.skipped += 1
            stats.skipped += 1
        elif status in ['WARNING', 'WARN']:
            cat_stats.warning += 1
            stats.warning += 1
        elif status in ['ERROR']:
            cat_stats.error += 1
            stats.error += 1
    
    def _parse_pytest_json(self, pattern: str, stats: OverallStats) -> None:
        """Parse pytest JSON report."""
        files = glob.glob(pattern)
        
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # pytest-json-report format
                if 'tests' in data:
                    for test in data['tests']:
                        category = self._extract_category_from_nodeid(test.get('nodeid', ''))
                        
                        if category not in stats.categories:
                            stats.categories[category] = CategoryStats(category=category)
                        
                        cat_stats = stats.categories[category]
                        
                        outcome = test.get('outcome', 'unknown')
                        test_data = {
                            'test_id': test.get('nodeid', 'unknown'),
                            'test_name': test.get('nodeid', 'unknown').split('::')[-1],
                            'status': outcome.upper(),
                            'error_message': test.get('call', {}).get('longrepr', '')
                        }
                        
                        self._add_test_result(test_data, category, cat_stats, stats)
                
                # Summary
                if 'summary' in data:
                    summary = data['summary']
                    self.logger.info(f"  pytest summary: {summary}")
            
            except Exception as e:
                self.logger.error(f"Error parsing pytest JSON {filepath}: {e}")
    
    def _parse_junit_xml(self, pattern: str, stats: OverallStats) -> None:
        """Parse JUnit XML report."""
        files = glob.glob(pattern)
        
        for filepath in files:
            try:
                tree = ET.parse(filepath)
                root = tree.getroot()
                
                for testsuite in root.findall('.//testsuite'):
                    suite_name = testsuite.get('name', 'UNKNOWN').upper()
                    
                    if suite_name not in stats.categories:
                        stats.categories[suite_name] = CategoryStats(category=suite_name)
                    
                    cat_stats = stats.categories[suite_name]
                    
                    for testcase in testsuite.findall('testcase'):
                        test_name = testcase.get('name', 'unknown')
                        classname = testcase.get('classname', '')
                        
                        failure = testcase.find('failure')
                        error = testcase.find('error')
                        skipped = testcase.find('skipped')
                        
                        if failure is not None:
                            status = 'FAILED'
                            error_msg = failure.get('message', '')
                        elif error is not None:
                            status = 'ERROR'
                            error_msg = error.get('message', '')
                        elif skipped is not None:
                            status = 'SKIPPED'
                            error_msg = None
                        else:
                            status = 'PASSED'
                            error_msg = None
                        
                        test_data = {
                            'test_id': f"{classname}::{test_name}",
                            'test_name': test_name,
                            'status': status,
                            'error_message': error_msg
                        }
                        
                        self._add_test_result(test_data, suite_name, cat_stats, stats)
            
            except Exception as e:
                self.logger.error(f"Error parsing JUnit XML {filepath}: {e}")
    
    def _parse_markdown_report(self, pattern: str, stats: OverallStats) -> None:
        """Parse markdown execution summary."""
        files = glob.glob(pattern)
        
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract statistics using regex
                total_match = re.search(r'Total Tests:\s*(\d+)', content)
                passed_match = re.search(r'Passed:\s*(\d+)', content)
                failed_match = re.search(r'Failed:\s*(\d+)', content)
                
                if total_match:
                    stats.total_tests += int(total_match.group(1))
                if passed_match:
                    stats.passed += int(passed_match.group(1))
                if failed_match:
                    stats.failed += int(failed_match.group(1))
                
                self.logger.info(f"  Parsed markdown: {total_match.group(1) if total_match else 0} tests")
            
            except Exception as e:
                self.logger.error(f"Error parsing markdown {filepath}: {e}")
    
    def _extract_category_from_nodeid(self, nodeid: str) -> str:
        """Extract category from pytest nodeid."""
        # Example: tests/test_security.py::TestAuthorization::test_bypass
        parts = nodeid.split('::')
        if len(parts) >= 2:
            return parts[1].replace('Test', '').upper()
        return 'UNKNOWN'
    
    def _calculate_statistics(self, stats: OverallStats) -> None:
        """Calculate final statistics."""
        # Overall pass rate
        if stats.total_tests > 0:
            stats.pass_rate = stats.passed / stats.total_tests
        
        # Category pass rates
        for cat_stats in stats.categories.values():
            if cat_stats.total > 0:
                cat_stats.pass_rate = cat_stats.passed / cat_stats.total
        
        # Determine overall status
        if stats.pass_rate >= 0.95:
            stats.overall_status = "✅ **Ready**"
        elif stats.pass_rate >= 0.80:
            stats.overall_status = "⚠️ **Partial**"
        elif stats.pass_rate >= 0.50:
            stats.overall_status = "🔴 **Failing**"
        else:
            stats.overall_status = "❌ **Critical**"
        
        self.logger.info(f"Final statistics: {stats.total_tests} tests, {stats.passed} passed, {stats.failed} failed ({stats.pass_rate:.1%} pass rate)")


class DocumentationUpdater:
    """Update documentation files with test results."""
    
    # ⚠️ CRITICAL: README.md is OFF LIMITS - NEVER MODIFY IT ⚠️
    # Modifications only by explicit human action
    # Violating this invokes the wrath of Thirsty
    PROTECTED_FILES = ['README.md', 'readme.md', 'ReadMe.md', 'Readme.md']
    
    def __init__(self, config: Dict[str, Any], stats: OverallStats):
        self.config = config
        self.stats = stats
        self.logger = logging.getLogger(f"{__name__}.DocumentationUpdater")
        self.updated_files: List[str] = []
    
    def update_all_documentation(self) -> None:
        """Update all configured documentation files."""
        for doc_target in self.config.get('documentation_targets', []):
            filepath = doc_target.get('path')
            
            # ⚠️ CRITICAL CHECK: NEVER TOUCH README.md ⚠️
            if any(filepath.lower().endswith(protected.lower()) for protected in self.PROTECTED_FILES):
                self.logger.warning(f"⚠️  SKIPPING {filepath} - This file is PROTECTED and must only be modified by the repository owner")
                self.logger.warning(f"⚠️  Attempting to modify this file would invoke the wrath of Thirsty!")
                continue
            
            if not os.path.exists(filepath):
                if any(section.get('create_if_missing', False) 
                       for section in doc_target.get('sections', {}).values()):
                    self.logger.info(f"Creating {filepath}")
                    self._create_documentation_file(filepath, doc_target)
                else:
                    self.logger.warning(f"Documentation file not found: {filepath}")
                    continue
            
            self.logger.info(f"Updating {filepath}")
            self._update_documentation_file(filepath, doc_target)
    
    def _create_documentation_file(self, filepath: str, doc_target: Dict[str, Any]) -> None:
        """Create a new documentation file."""
        content = f"# Test Report\n\nGenerated: {self.stats.timestamp}\n\n"
        
        # Add sections based on configuration
        for section_name, section_config in doc_target.get('sections', {}).items():
            if section_config.get('auto_create', False):
                content += self._generate_section_content(section_name, section_config)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.updated_files.append(filepath)
    
    def _update_documentation_file(self, filepath: str, doc_target: Dict[str, Any]) -> None:
        """Update an existing documentation file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for section_name, section_config in doc_target.get('sections', {}).items():
            content = self._update_section(content, section_name, section_config)
        
        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.updated_files.append(filepath)
            self.logger.info(f"  Updated {filepath}")
        else:
            self.logger.info(f"  No changes needed for {filepath}")
    
    def _update_section(self, content: str, section_name: str, section_config: Dict[str, Any]) -> str:
        """Update a specific section in the documentation."""
        markers = section_config.get('markers')
        patterns = section_config.get('patterns', [])
        
        # Update using markers
        if markers:
            start_marker, end_marker = markers
            
            if start_marker in content and end_marker in content:
                # Replace content between markers
                new_section_content = self._generate_section_content(section_name, section_config)
                
                pattern = re.escape(start_marker) + r'.*?' + re.escape(end_marker)
                replacement = f"{start_marker}\n{new_section_content}{end_marker}"
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            elif section_config.get('auto_create', False):
                # Add new section
                new_section_content = self._generate_section_content(section_name, section_config)
                section_block = f"\n\n{start_marker}\n{new_section_content}{end_marker}\n"
                
                insert_after = section_config.get('insert_after_line', 0)
                if insert_after > 0:
                    lines = content.split('\n')
                    lines.insert(insert_after, section_block)
                    content = '\n'.join(lines)
                else:
                    content += section_block
        
        # Update using patterns
        for pattern_config in patterns:
            match_pattern = pattern_config.get('match')
            template = pattern_config.get('template')
            
            if match_pattern and template:
                replacement = self._format_template(template)
                content = re.sub(match_pattern, replacement, content)
        
        return content
    
    def _generate_section_content(self, section_name: str, section_config: Dict[str, Any]) -> str:
        """Generate content for a section."""
        if section_name == 'test_badges':
            return self._generate_test_badges()
        elif section_name == 'test_summary':
            return self._generate_test_summary()
        elif section_name == 'category_breakdown':
            return self._generate_category_breakdown()
        elif section_name == 'pass_fail_table':
            return self._generate_pass_fail_table()
        elif section_name == 'overall_stats':
            return self._generate_overall_stats()
        else:
            return ""
    
    def _generate_test_badges(self) -> str:
        """Generate test status badges."""
        badges = []
        
        # Total tests badge
        total_color = self.config['badge_colors']['pass'] if self.stats.pass_rate >= 0.90 else \
                      self.config['badge_colors']['warning'] if self.stats.pass_rate >= 0.80 else \
                      self.config['badge_colors']['fail']
        
        badges.append(f"![Tests](https://img.shields.io/badge/tests-{self.stats.total_tests}-{total_color})")
        
        # Passing tests badge
        badges.append(f"![Passing](https://img.shields.io/badge/passing-{self.stats.passed}-green)")
        
        # Failing tests badge (if any)
        if self.stats.failed > 0:
            fail_color = self.config['badge_colors']['fail'] if self.stats.failed > 10 else \
                         self.config['badge_colors']['warning']
            badges.append(f"![Failing](https://img.shields.io/badge/failing-{self.stats.failed}-{fail_color})")
        
        # Pass rate badge
        pass_rate_pct = int(self.stats.pass_rate * 100)
        pass_rate_color = self.config['badge_colors']['pass'] if self.stats.pass_rate >= 0.90 else \
                          self.config['badge_colors']['warning'] if self.stats.pass_rate >= 0.80 else \
                          self.config['badge_colors']['fail']
        badges.append(f"![Pass Rate](https://img.shields.io/badge/pass_rate-{pass_rate_pct}%25-{pass_rate_color})")
        
        # Status badge
        status_text = "passing" if self.stats.pass_rate >= 0.90 else \
                      "partial" if self.stats.pass_rate >= 0.80 else "failing"
        status_color = self.config['badge_colors']['pass'] if self.stats.pass_rate >= 0.90 else \
                       self.config['badge_colors']['warning'] if self.stats.pass_rate >= 0.80 else \
                       self.config['badge_colors']['fail']
        badges.append(f"![Status](https://img.shields.io/badge/status-{status_text}-{status_color})")
        
        return "\n".join(badges) + "\n"
    
    def _generate_test_summary(self) -> str:
        """Generate test summary section."""
        summary = f"""
## 📊 Test Summary

**Updated:** {self.stats.timestamp}

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Tests** | {self.stats.total_tests} | 100% |
| **Passed** | {self.stats.passed} | {self.stats.pass_rate:.1%} |
| **Failed** | {self.stats.failed} | {self.stats.failed / max(self.stats.total_tests, 1):.1%} |
| **Skipped** | {self.stats.skipped} | {self.stats.skipped / max(self.stats.total_tests, 1):.1%} |
| **Warning** | {self.stats.warning} | {self.stats.warning / max(self.stats.total_tests, 1):.1%} |

**Overall Status:** {self.stats.overall_status}
"""
        return summary
    
    def _generate_category_breakdown(self) -> str:
        """Generate category breakdown table."""
        breakdown = """
## 📋 Category Breakdown

| Category | Total | Passed | Failed | Skipped | Pass Rate | Status |
|----------|-------|--------|--------|---------|-----------|--------|
"""
        
        # Sort categories by name
        sorted_categories = sorted(self.stats.categories.items())
        
        for category_name, cat_stats in sorted_categories:
            status_emoji = "✅" if cat_stats.pass_rate >= 0.90 else \
                          "⚠️" if cat_stats.pass_rate >= 0.80 else "❌"
            
            breakdown += f"| {category_name} | {cat_stats.total} | {cat_stats.passed} | {cat_stats.failed} | {cat_stats.skipped} | {cat_stats.pass_rate:.1%} | {status_emoji} |\n"
        
        return breakdown
    
    def _generate_pass_fail_table(self) -> str:
        """Generate detailed pass/fail table with failed test examples."""
        table = f"""
# Security Test Category Pass/Fail Report

**Generated:** {self.stats.timestamp}

## Summary

- **Total Tests:** {self.stats.total_tests}
- **Passed:** {self.stats.passed} ({self.stats.pass_rate:.1%})
- **Failed:** {self.stats.failed} ({self.stats.failed / max(self.stats.total_tests, 1):.1%})
- **Overall Status:** {self.stats.overall_status}

## Category Details

| Category | Total | ✅ Passed | ❌ Failed | ⏭️ Skipped | ⚠️ Warning | Pass Rate | Status |
|----------|-------|----------|----------|-----------|-----------|-----------|--------|
"""
        
        # Sort categories by name
        sorted_categories = sorted(self.stats.categories.items())
        
        for category_name, cat_stats in sorted_categories:
            status = "✅ Pass" if cat_stats.pass_rate >= 0.90 else \
                    "⚠️ Partial" if cat_stats.pass_rate >= 0.80 else "❌ Fail"
            
            table += f"| {category_name} | {cat_stats.total} | {cat_stats.passed} | {cat_stats.failed} | {cat_stats.skipped} | {cat_stats.warning} | {cat_stats.pass_rate:.1%} | {status} |\n"
        
        # Add failed tests section
        has_failures = any(cat_stats.failed_tests for cat_stats in self.stats.categories.values())
        
        if has_failures:
            table += "\n## ❌ Failed Tests\n\n"
            
            for category_name, cat_stats in sorted_categories:
                if cat_stats.failed_tests:
                    table += f"### {category_name}\n\n"
                    
                    for i, failed_test in enumerate(cat_stats.failed_tests[:10], 1):  # Limit to 10 per category
                        table += f"**{i}. {failed_test.name}** (ID: `{failed_test.test_id}`)\n"
                        if failed_test.error_message:
                            # Truncate long error messages
                            error_msg = failed_test.error_message[:200]
                            if len(failed_test.error_message) > 200:
                                error_msg += "..."
                            table += f"   - Error: {error_msg}\n"
                        table += "\n"
                    
                    if len(cat_stats.failed_tests) > 10:
                        table += f"*...and {len(cat_stats.failed_tests) - 10} more failed tests in this category*\n\n"
        
        return table
    
    def _generate_overall_stats(self) -> str:
        """Generate overall statistics."""
        return f"**Total Tests:** {self.stats.total_tests} | **Passed:** {self.stats.passed} | **Failed:** {self.stats.failed} | **Status:** {self.stats.overall_status}"
    
    def _format_template(self, template: str) -> str:
        """Format a template string with statistics."""
        return template.format(
            total_tests=self.stats.total_tests,
            passed=self.stats.passed,
            failed=self.stats.failed,
            skipped=self.stats.skipped,
            warning=self.stats.warning,
            pass_rate=f"{self.stats.pass_rate:.1%}",
            overall_status=self.stats.overall_status,
            timestamp=self.stats.timestamp
        )


class GitCommitter:
    """Handle git operations for committing updated documentation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.GitCommitter")
    
    def commit_updates(self, updated_files: List[str]) -> bool:
        """Commit updated documentation files."""
        if not updated_files:
            self.logger.info("No files to commit")
            return True
        
        if self.config.get('output', {}).get('dry_run', False):
            self.logger.info(f"DRY RUN: Would commit {len(updated_files)} files")
            return True
        
        try:
            # Configure git
            subprocess.run(['git', 'config', 'user.name', 'Test Report Updater'], check=True)
            subprocess.run(['git', 'config', 'user.email', 'ci@project-ai.local'], check=True)
            
            # Add files
            for filepath in updated_files:
                self.logger.info(f"Adding {filepath}")
                subprocess.run(['git', 'add', filepath], check=True)
            
            # Generate commit message
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_template = self.config.get('output', {}).get('commit_message_template', 
                                                                 'chore: auto-update test documentation [{timestamp}]')
            commit_message = commit_template.format(timestamp=timestamp)
            
            # Commit
            self.logger.info(f"Committing with message: {commit_message}")
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            self.logger.info("Successfully committed updates")
            return True
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git operation failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error committing updates: {e}")
            return False


class SummaryReportGenerator:
    """Generate summary report of the update process."""
    
    def __init__(self, config: Dict[str, Any], stats: OverallStats, updated_files: List[str]):
        self.config = config
        self.stats = stats
        self.updated_files = updated_files
        self.logger = logging.getLogger(f"{__name__}.SummaryReportGenerator")
    
    def generate(self) -> None:
        """Generate summary report."""
        if not self.config.get('output', {}).get('create_summary_report', True):
            return
        
        report_path = self.config.get('output', {}).get('summary_report_path', 
                                                        'test_documentation_update_summary.md')
        
        self.logger.info(f"Generating summary report: {report_path}")
        
        report = f"""# Test Documentation Update Summary

**Generated:** {datetime.now().isoformat()}

## Overall Statistics

- **Total Tests:** {self.stats.total_tests}
- **Passed:** {self.stats.passed} ({self.stats.pass_rate:.1%})
- **Failed:** {self.stats.failed} ({self.stats.failed / max(self.stats.total_tests, 1):.1%})
- **Skipped:** {self.stats.skipped}
- **Warning:** {self.stats.warning}
- **Overall Status:** {self.stats.overall_status}

## Category Summary

| Category | Total | Passed | Failed | Pass Rate |
|----------|-------|--------|--------|-----------|
"""
        
        for category_name, cat_stats in sorted(self.stats.categories.items()):
            report += f"| {category_name} | {cat_stats.total} | {cat_stats.passed} | {cat_stats.failed} | {cat_stats.pass_rate:.1%} |\n"
        
        report += f"""

## Updated Documentation Files

"""
        
        if self.updated_files:
            for filepath in self.updated_files:
                report += f"- ✅ {filepath}\n"
        else:
            report += "- ℹ️ No files needed updating\n"
        
        report += f"""

## Configuration Used

- **Artifact Sources:** {len(self.config.get('artifact_sources', {}))}
- **Documentation Targets:** {len(self.config.get('documentation_targets', []))}
- **Dry Run:** {self.config.get('output', {}).get('dry_run', False)}
- **Commit Updates:** {self.config.get('output', {}).get('commit_updates', True)}

---

*Generated by Test Report Documentation Updater v1.0.0*
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.logger.info(f"Summary report saved to {report_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Automated Test Report Documentation Updater',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default configuration
  python update_test_documentation.py

  # Run with custom config
  python update_test_documentation.py --config custom-config.json

  # Dry run (no commits)
  python update_test_documentation.py --dry-run

  # Skip git commit
  python update_test_documentation.py --no-commit
        """
    )
    
    parser.add_argument('--config', '-c', 
                       default='.test-report-updater.config.json',
                       help='Path to configuration file (default: .test-report-updater.config.json)')
    parser.add_argument('--dry-run', '-d', action='store_true',
                       help='Run without making changes')
    parser.add_argument('--no-commit', action='store_true',
                       help='Skip git commit step')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.info(f"Loaded configuration from {args.config}")
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {args.config}")
        return 1
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        return 1
    
    # Override config with command-line options
    if args.dry_run:
        config.setdefault('output', {})['dry_run'] = True
    
    if args.no_commit:
        config.setdefault('output', {})['commit_updates'] = False
    
    # Parse artifacts
    logger.info("=" * 80)
    logger.info("PARSING TEST ARTIFACTS")
    logger.info("=" * 80)
    
    parser_instance = ArtifactParser(config)
    stats = parser_instance.parse_all_artifacts()
    
    # Update documentation
    logger.info("=" * 80)
    logger.info("UPDATING DOCUMENTATION")
    logger.info("=" * 80)
    
    updater = DocumentationUpdater(config, stats)
    updater.update_all_documentation()
    
    # Generate summary report
    logger.info("=" * 80)
    logger.info("GENERATING SUMMARY REPORT")
    logger.info("=" * 80)
    
    summary_generator = SummaryReportGenerator(config, stats, updater.updated_files)
    summary_generator.generate()
    
    # Commit updates
    if config.get('output', {}).get('commit_updates', True):
        logger.info("=" * 80)
        logger.info("COMMITTING UPDATES")
        logger.info("=" * 80)
        
        committer = GitCommitter(config)
        success = committer.commit_updates(updater.updated_files)
        
        if not success:
            logger.error("Failed to commit updates")
            return 1
    
    logger.info("=" * 80)
    logger.info("UPDATE COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total tests: {stats.total_tests}")
    logger.info(f"Passed: {stats.passed} ({stats.pass_rate:.1%})")
    logger.info(f"Failed: {stats.failed}")
    logger.info(f"Updated files: {len(updater.updated_files)}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
