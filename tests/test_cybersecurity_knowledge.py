"""
Tests for cybersecurity knowledge integration.
"""

import os
import tempfile
import unittest

from app.core.ai_systems import MemoryExpansionSystem
from app.core.cybersecurity_knowledge import CybersecurityKnowledge


class TestCybersecurityKnowledge(unittest.TestCase):
    """Test the cybersecurity knowledge module."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cyber_knowledge = CybersecurityKnowledge(data_dir=self.temp_dir)

    def test_get_all_content(self):
        """Test getting all content."""
        content = self.cyber_knowledge.get_all_content()
        self.assertIsInstance(content, dict)
        self.assertIn("title", content)
        self.assertIn("malware", content)
        self.assertIn("system_exploitation", content)
        self.assertIn("web_attacks", content)
        self.assertIn("proactive_defense", content)

    def test_get_section(self):
        """Test getting a specific section."""
        malware = self.cyber_knowledge.get_section("malware")
        self.assertIsNotNone(malware)
        self.assertIn("strategic_importance", malware)
        self.assertIn("virus_lifecycle", malware)
        self.assertIn("case_study_love_letter", malware)

    def test_get_subsection(self):
        """Test getting a subsection."""
        love_letter = self.cyber_knowledge.get_subsection(
            "malware", "case_study_love_letter"
        )
        self.assertIsNotNone(love_letter)
        self.assertEqual(love_letter["name"], "ILOVEYOU (Love Letter) Worm")
        self.assertEqual(love_letter["year"], 2000)

    def test_search_content(self):
        """Test searching for keywords."""
        # Search for 'buffer overflow'
        results = self.cyber_knowledge.search_content("buffer overflow")
        self.assertGreater(len(results), 0)
        self.assertTrue(
            any("buffer" in result["content"].lower() for result in results)
        )

        # Search for 'Love Letter'
        results = self.cyber_knowledge.search_content("Love Letter")
        self.assertGreater(len(results), 0)

    def test_export_to_json(self):
        """Test exporting to JSON."""
        filepath = self.cyber_knowledge.export_to_json()
        self.assertTrue(os.path.exists(filepath))

        # Verify the file contains valid JSON
        import json

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
            self.assertIn("title", data)

    def test_integration_with_memory_system(self):
        """Test integration with MemoryExpansionSystem."""
        memory_system = MemoryExpansionSystem(data_dir=self.temp_dir)
        self.cyber_knowledge.integrate_with_memory_system(memory_system)

        # Verify sections were added
        malware = memory_system.get_knowledge("cybersecurity_education", "malware")
        self.assertIsNotNone(malware)
        self.assertIn("strategic_importance", malware)

        web_attacks = memory_system.get_knowledge(
            "cybersecurity_education", "web_attacks"
        )
        self.assertIsNotNone(web_attacks)
        self.assertIn("strategic_importance", web_attacks)

        title = memory_system.get_knowledge("cybersecurity_education", "title")
        self.assertIsNotNone(title)
        self.assertIn("Digital Threats", title)

    def test_get_summary(self):
        """Test getting a summary."""
        summary = self.cyber_knowledge.get_summary()
        self.assertIsInstance(summary, str)
        self.assertIn("Introduction", summary)
        self.assertIn("Malware", summary)
        self.assertIn("System Exploitation", summary)
        self.assertIn("Web Attacks", summary)
        self.assertIn("Proactive Defense", summary)
        self.assertIn("Secure Implementation", summary)


if __name__ == "__main__":
    unittest.main()
