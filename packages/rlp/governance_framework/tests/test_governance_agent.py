"""Tests for the Governance Agent package.

Tests cover: governor (all 15 laws, priority order, evidence verification,
hostile review, blocker reports), tools (evidence records), continuity (read/write),
CLI parsing, and agent initialization.
"""

import os
import sys
import tempfile
import unittest

# Ensure the project root is on the path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)


# ─── Governor Tests ──────────────────────────────────────────────────────

class TestGovernorAllLawsChecked(unittest.TestCase):
    """Test that ActionCheck checks all 15 Core Operating Laws."""

    def setUp(self):
        from governance_agent.governor import ActionCheck, CORE_OPERATING_LAWS
        self.checker = ActionCheck()
        self.laws = CORE_OPERATING_LAWS

    def test_all_15_laws_defined(self):
        """Verify exactly 15 Core Operating Laws are defined."""
        self.assertEqual(len(self.laws), 15)

    def test_all_laws_have_id_and_name(self):
        """Verify every law has an id, name, description, and priority."""
        for law in self.laws:
            self.assertIn('id', law)
            self.assertIn('name', law)
            self.assertIn('description', law)
            self.assertIn('priority', law)

    def test_all_laws_have_check_function(self):
        """Verify every law has a corresponding check function in ActionCheck."""
        expected_ids = {law['id'] for law in self.laws}
        actual_ids = set(self.checker._check_functions.keys())
        self.assertEqual(expected_ids, actual_ids,
                         f"Missing check functions for laws: {expected_ids - actual_ids}")

    def test_check_function_exists(self):
        """Verify the checker has a check_action method."""
        self.assertTrue(hasattr(self.checker, 'check_action'))
        self.assertTrue(callable(self.checker.check_action))

    def test_check_action_returns_result(self):
        """Verify check_action returns an ActionCheckResult."""
        action = {'type': 'analyze', 'description': 'test action'}
        context = {'task': 'test', 'mode': 'single_file', 'step_number': 0}
        result = self.checker.check_action(action, context)
        self.assertTrue(hasattr(result, 'allowed'))
        self.assertTrue(hasattr(result, 'violations'))
        self.assertTrue(hasattr(result, 'warnings'))
        self.assertTrue(hasattr(result, 'blocker'))


class TestPriorityOrderSafetyOverInstruction(unittest.TestCase):
    """Test that Safety violations block even if User Instruction passes."""

    def setUp(self):
        from governance_agent.governor import ActionCheck
        self.checker = ActionCheck()

    def test_safety_violation_blocks(self):
        """Verify Law 15 (governance enforcement - priority 3) violations block."""
        action = {'type': 'write', 'description': 'Claim governance enforcement without proof'}
        context = {
            'task': 'test',
            'mode': 'single_file',
            'step_number': 0,
            'has_governance_proof': False
        }

        # Provide context that includes governance claim
        action_with_claim = {
            'type': 'present',
            'description': 'This system provides governance enforcement and runtime authority'
        }
        result = self.checker.check_action(action_with_claim, context)

        # Should be blocked or at least have violations
        law15_violation = any(v['law_id'] == 15 for v in result.violations)
        self.assertTrue(law15_violation or not result.allowed,
                        "Law 15 violation should be detected")

    def test_law_3_refusal_without_blocker_detected(self):
        """Verify refusing action without documented blocker is detected."""
        action = {'type': 'analyze', 'description': 'I cannot perform this action'}
        context = {
            'task': 'test',
            'mode': 'single_file',
            'step_number': 0,
            'blockers': []
        }
        result = self.checker.check_action(action, context)
        law3_violation = any(v['law_id'] == 3 for v in result.violations)
        self.assertTrue(law3_violation,
                        "Refusal without blocker should be detected as Law 3 violation")


class TestBlockedPresentationWithoutHostileReview(unittest.TestCase):
    """Test that presenting without hostile review is blocked."""

    def setUp(self):
        from governance_agent.governor import ActionCheck
        self.checker = ActionCheck()

    def test_presentation_requires_hostile_review(self):
        """Verify presenting output without hostile review is a Law 14 violation."""
        action = {'type': 'present', 'description': 'Present completed work'}
        context = {
            'task': 'test',
            'mode': 'single_file',
            'step_number': 1,
            'hostile_review_performed': False
        }
        result = self.checker.check_action(action, context)
        law14_violation = any(v['law_id'] == 14 for v in result.violations)
        self.assertTrue(law14_violation,
                        "Presenting without hostile review should be detected as Law 14 violation")


class TestEvidenceVerification(unittest.TestCase):
    """Test that EvidenceVerifier catches mismatched evidence."""

    def setUp(self):
        from governance_agent.governor import EvidenceVerifier
        self.verifier = EvidenceVerifier

    def test_verification_mismatch_detected(self):
        """Verify evidence verification catches status mismatches."""
        evidence_records = [
            {
                'action': 'write_file(/tmp/test.txt)',
                'status': 'failure',
                'output': {'path': '/tmp/test.txt'},
                'error': 'Permission denied',
                'evidence_captured': True
            }
        ]
        claim = {'type': 'write', 'target': '/tmp/test.txt'}
        result = self.verifier.verify(claim, evidence_records)
        self.assertFalse(result.verified)
        self.assertTrue(len(result.mismatches) > 0)

    def test_verification_success(self):
        """Verify evidence verification passes with matching records."""
        evidence_records = [
            {
                'action': 'write_file(/tmp/test_pass.txt)',
                'status': 'success',
                'output': {'path': '/tmp/test_pass.txt', 'bytes_written': 10},
                'error': None,
                'evidence_captured': True
            }
        ]
        claim = {'type': 'write', 'target': '/tmp/test_pass.txt'}
        result = self.verifier.verify(claim, evidence_records)
        self.assertTrue(result.verified)

    def test_missing_evidence_detected(self):
        """Verify missing evidence is detected."""
        result = self.verifier.verify(
            {'type': 'read', 'target': '/nonexistent/file.py'},
            []
        )
        self.assertFalse(result.verified)
        self.assertTrue('no evidence records' in result.summary.lower() or
                        'no matching evidence' in result.summary.lower())


class TestHostileReviewDetectsFakePath(unittest.TestCase):
    """Test that HostileReviewer flags non-existent file paths."""

    def setUp(self):
        from governance_agent.governor import HostileReviewer
        self.reviewer = HostileReviewer

    def test_fake_path_detected(self):
        """Verify hostile review flags non-existent file paths."""
        output = {
            'files': ['/nonexistent_dir/fake_file_xyz.py'],
            'claims': [],
            'commands': [],
            'diffs': []
        }
        context = {
            'mode': 'single_file',
            'evidence_records': [],
            'allowed_paths': []
        }
        result = self.reviewer.review(output, context)
        broken_paths = [f for f in result.findings if f.category == 'broken_paths']
        self.assertTrue(len(broken_paths) > 0,
                        "Hostile review should detect non-existent file paths")

    def test_valid_path_passes(self):
        """Verify hostile review passes for existing files."""
        # Create a temp file
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write("# test file\n")
            temp_path = f.name

        try:
            output = {
                'files': [temp_path],
                'claims': [],
                'commands': [],
                'diffs': []
            }
            context = {
                'mode': 'single_file',
                'evidence_records': [],
                'allowed_paths': []
            }
            result = self.reviewer.review(output, context)
            broken_paths = [f for f in result.findings if f.category == 'broken_paths']
            self.assertEqual(len(broken_paths), 0,
                             "Existing files should not trigger broken_paths findings")
        finally:
            os.unlink(temp_path)


class TestBlockerReportFormat(unittest.TestCase):
    """Test that BlockerReportFormatter produces correct format."""

    def setUp(self):
        from governance_agent.governor import BlockerReportFormatter
        self.formatter = BlockerReportFormatter

    def test_blocker_report_format(self):
        """Verify blocker report has Blocked/Impact/Minimum fix/Safe to continue."""
        blocker = {
            'blocked_reason': 'Test reason',
            'impact': 'Test impact',
            'minimum_fix': 'Test fix',
            'safe_to_continue': 'yes',
            'violations': []
        }
        report = self.formatter.format_with_violations(blocker)
        self.assertIn('Blocked:', report)
        self.assertIn('Impact:', report)
        self.assertIn('Minimum fix:', report)
        self.assertIn('Safe to continue:', report)
        self.assertIn('yes', report)


# ─── Tools Tests ─────────────────────────────────────────────────────────

class TestToolsReturnEvidence(unittest.TestCase):
    """Test that tools return proper EvidenceRecord dataclasses."""

    def setUp(self):
        from governance_agent.tools import (
            EvidenceRecord, read_file, write_file, run_command,
            list_directory, git_status, analyze_code
        )
        self.EvidenceRecord = EvidenceRecord
        self.read_file = read_file
        self.write_file = write_file
        self.run_command = run_command
        self.list_directory = list_directory
        self.analyze_code = analyze_code

    def test_evidence_record_has_required_fields(self):
        """Verify EvidenceRecord has all required fields."""
        record = self.EvidenceRecord(
            action='test',
            status='success',
            output='test output',
            error=None,
            evidence_captured=True
        )
        self.assertEqual(record.action, 'test')
        self.assertEqual(record.status, 'success')
        self.assertEqual(record.output, 'test output')
        self.assertIsNone(record.error)
        self.assertTrue(record.evidence_captured)

    def test_evidence_record_to_dict(self):
        """Verify EvidenceRecord.to_dict() works."""
        record = self.EvidenceRecord(
            action='test',
            status='success',
            output='data',
            evidence_captured=True
        )
        d = record.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d['action'], 'test')
        self.assertEqual(d['status'], 'success')

    def test_read_file_missing_returns_failure(self):
        """Verify read_file returns failure EvidenceRecord for missing file."""
        result = self.read_file('/nonexistent_file_path_12345.txt')
        self.assertEqual(result.status, 'failure')
        self.assertFalse(result.evidence_captured)
        self.assertIsNotNone(result.error)

    def test_write_file_returns_success(self):
        """Verify write_file returns success EvidenceRecord."""
        temp_path = '/tmp/governance_agent_test_write.txt'
        try:
            result = self.write_file(temp_path, 'test content')
            self.assertEqual(result.status, 'success')
            self.assertTrue(result.evidence_captured)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_run_command_returns_evidence(self):
        """Verify run_command returns EvidenceRecord with output."""
        result = self.run_command('echo "hello world"')
        self.assertEqual(result.status, 'success')
        self.assertTrue(result.evidence_captured)
        self.assertIsInstance(result.output, dict)
        self.assertIn('stdout', result.output)

    def test_list_directory_returns_evidence(self):
        """Verify list_directory returns EvidenceRecord with items."""
        result = self.list_directory(PROJECT_ROOT)
        self.assertEqual(result.status, 'success')
        self.assertTrue(result.evidence_captured)
        self.assertIn('items', result.output)

    def test_analyze_code_valid_syntax(self):
        """Verify analyze_code returns success for valid Python."""
        result = self.analyze_code(
            os.path.join(PROJECT_ROOT, 'governance_agent', 'tools.py')
        )
        self.assertEqual(result.status, 'success', f"Error: {result.error}")
        self.assertTrue(result.evidence_captured)
        output = result.output
        self.assertTrue(output.get('syntax_valid', False))
        self.assertTrue(len(output.get('imports', [])) > 0)


# ─── Continuity Tests ────────────────────────────────────────────────────

class TestContinuityReadWrite(unittest.TestCase):
    """Test continuity map create/read/update cycle."""

    def setUp(self):
        from governance_agent.continuity import (
            read_continuity_map, create_continuity_map,
            update_continuity_map, continuity_section,
            get_default_continuity_state
        )
        self.read_continuity_map = read_continuity_map
        self.create_continuity_map = create_continuity_map
        self.update_continuity_map = update_continuity_map
        self.continuity_section = continuity_section
        self.get_default_continuity_state = get_default_continuity_state
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_continuity_map(self):
        """Verify create_continuity_map creates a valid file."""
        path = os.path.join(self.temp_dir, 'CONTINUITY_MAP.md')
        state = self.get_default_continuity_state('test task', 'module')
        created = self.create_continuity_map(path, state)
        self.assertTrue(created)
        self.assertTrue(os.path.exists(path))

    def test_read_continuity_map(self):
        """Verify read_continuity_map reads created map."""
        path = os.path.join(self.temp_dir, 'CONTINUITY_MAP.md')
        state = self.get_default_continuity_state('test task', 'module')
        self.create_continuity_map(path, state)

        result = self.read_continuity_map(path)
        self.assertTrue(result['exists'])
        self.assertIn('sections', result)
        self.assertIn('Session Metadata', result['sections'])

    def test_read_nonexistent_map(self):
        """Verify read_continuity_map handles missing file."""
        result = self.read_continuity_map('/nonexistent/CONTINUITY_MAP.md')
        self.assertFalse(result['exists'])
        self.assertIsNotNone(result['error'])

    def test_continuity_section_format(self):
        """Verify continuity_section produces correct markdown."""
        section = self.continuity_section("Test Section", "Some content here")
        self.assertIn("## Test Section", section)
        self.assertIn("Some content here", section)

    def test_update_continuity_map(self):
        """Verify update_continuity_map modifies existing map."""
        path = os.path.join(self.temp_dir, 'CONTINUITY_MAP.md')
        state = self.get_default_continuity_state('test task', 'module')
        self.create_continuity_map(path, state)

        updated = self.update_continuity_map(path, {
            'Current State': '- **Overall status:** completed\n- **Safe to continue:** yes\n'
        })
        self.assertTrue(updated)

        result = self.read_continuity_map(path)
        current_section = result['sections'].get('Current State', '')
        self.assertIn('completed', current_section)


# ─── CLI Tests ───────────────────────────────────────────────────────────

class TestCLIParse(unittest.TestCase):
    """Test CLI argument parsing."""

    def setUp(self):
        from governance_agent.cli import create_parser
        self.parser = create_parser()

    def test_parser_requires_task(self):
        """Verify --task is required."""
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])

    def test_parser_accepts_all_options(self):
        """Verify all CLI options are accepted."""
        args = self.parser.parse_args([
            '--task', 'test task',
            '--mode', 'module',
            '--provider', 'openrouter',
            '--model', 'anthropic/claude-sonnet-4-20250514',
            '--dry-run',
            '--output-dir', '/tmp/test_output',
            '--verbose'
        ])
        self.assertEqual(args.task, 'test task')
        self.assertEqual(args.mode, 'module')
        self.assertEqual(args.provider, 'openrouter')
        self.assertEqual(args.model, 'anthropic/claude-sonnet-4-20250514')
        self.assertTrue(args.dry_run)
        self.assertEqual(args.output_dir, '/tmp/test_output')
        self.assertTrue(args.verbose)

    def test_parser_mode_choices(self):
        """Verify --mode only accepts valid choices."""
        # Valid modes
        for mode in ['single_file', 'patch', 'module', 'app', 'repo', 'governance_system']:
            args = self.parser.parse_args(['--task', 'test', '--mode', mode])
            self.assertEqual(args.mode, mode)

        # Invalid mode should fail
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['--task', 'test', '--mode', 'invalid_mode'])

    def test_parser_provider_choices(self):
        """Verify --provider only accepts valid choices."""
        for provider in ['openai', 'anthropic', 'openrouter', 'local']:
            args = self.parser.parse_args(['--task', 'test', '--provider', provider])
            self.assertEqual(args.provider, provider)

    def test_parser_defaults(self):
        """Verify parser defaults are correct."""
        args = self.parser.parse_args(['--task', 'test'])
        self.assertEqual(args.mode, 'module')
        self.assertEqual(args.provider, 'openai')
        self.assertIsNone(args.model)
        self.assertFalse(args.dry_run)
        self.assertEqual(args.output_dir, './governance_output')
        self.assertFalse(args.verbose)


# ─── Agent Initialization Tests ──────────────────────────────────────────

class TestAgentInitialization(unittest.TestCase):
    """Test GovernanceAgent initialization."""

    def test_agent_init_basic(self):
        """Verify GovernanceAgent initializes with basic parameters."""
        from governance_agent.agent import GovernanceAgent

        agent = GovernanceAgent(
            task='Test task',
            mode='module',
            provider='openai',
            model='gpt-4o',
            dry_run=True,
            output_dir='/tmp/gov_test_output',
            verbose=False
        )

        self.assertEqual(agent.task, 'Test task')
        self.assertEqual(agent.mode, 'module')
        self.assertEqual(agent.provider_name, 'openai')
        self.assertEqual(agent.model, 'gpt-4o')
        self.assertTrue(agent.dry_run)

        # Should have loaded system prompt
        self.assertTrue(len(agent.system_prompt) > 0,
                        "System prompt should be loaded")

        # Should have initialized context
        self.assertIn('task', agent.context)
        self.assertIn('mode', agent.context)
        self.assertIn('step_number', agent.context)
        self.assertEqual(agent.context['step_number'], 0)

    def test_agent_init_with_defaults(self):
        """Verify GovernanceAgent initializes with default values."""
        from governance_agent.agent import GovernanceAgent

        agent = GovernanceAgent(
            task='Default test',
            dry_run=True,
        )

        self.assertEqual(agent.mode, 'module')  # default
        self.assertEqual(agent.provider_name, 'openai')  # default
        self.assertIsNone(agent.model)  # default

    def test_agent_dry_run(self):
        """Verify dry_run mode works."""
        from governance_agent.agent import GovernanceAgent

        agent = GovernanceAgent(
            task='Dry run test',
            mode='single_file',
            dry_run=True,
            verbose=False
        )

        result = agent.run()

        self.assertIn('final_report', result)
        self.assertIn('steps', result)
        self.assertEqual(result['steps'], 1)  # Single_file mode executes 1 step


if __name__ == '__main__':
    unittest.main()