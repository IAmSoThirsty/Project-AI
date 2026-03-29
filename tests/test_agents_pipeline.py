# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_agents_pipeline.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_agents_pipeline.py


import unittest
import tempfile
import shutil
from pathlib import Path
from app.core.council_hub import CouncilHub

class TestAgentsPipeline(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.hub = CouncilHub()
        self.hub.register_project("TestProject")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_curator_integration(self):
        # Create a fake report and run curator
        report = {"topic": "t1", "neutral_summary": "a summary", "facts": ["fact1"]}
        res = self.hub._project["curator"].curate([report])
        self.assertGreaterEqual(res.get("added"), 0)

    def test_qa_and_dependency(self):
        # Create a fake generated module
        gen_dir = self.test_dir / "generated"
        gen_dir.mkdir()
        module = gen_dir / "impl_sample.py"
        module.write_text("def impl_sample():\n    return True\n")
        codex = self.hub._project.get("qa_generator")
        dep = self.hub._project.get("dependency_auditor")
        # Generate test
        res = codex.generate_test_for_module(str(module))
        self.assertTrue(res.get("success"))
        # Run dependency auditor
        res2 = dep.analyze_new_module(str(module))
        self.assertTrue(res2.get("success"))
