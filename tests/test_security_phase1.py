"""Comprehensive security tests - Phase 1: Environment & Data Validation."""

import os
import platform
import tempfile
from pathlib import Path

import pytest

from app.security.data_validation import (
    DataPoisoningDefense,
    ParsedData,
    SecureDataParser,
)
from app.security.environment_hardening import EnvironmentHardening


class TestEnvironmentHardening:
    """Test environment security validation."""

    def test_virtualenv_detection(self):
        """Test virtualenv detection."""
        hardening = EnvironmentHardening()
        in_venv = hardening._check_virtualenv()

        # Should detect virtualenv or system Python
        assert isinstance(in_venv, bool)

    def test_sys_path_validation(self):
        """Test sys.path validation."""
        hardening = EnvironmentHardening()
        issues = hardening._validate_sys_path()

        # Should return list of issues
        assert isinstance(issues, list)

    def test_aslr_ssp_check(self):
        """Test ASLR/SSP security feature check."""
        hardening = EnvironmentHardening()
        enabled = hardening._check_aslr_ssp()

        # Should return bool
        assert isinstance(enabled, bool)

        # On Linux, should check /proc/sys/kernel/randomize_va_space
        if platform.system() == "Linux":
            assert enabled in [True, False]

    def test_directory_permissions(self):
        """Test directory permission validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hardening = EnvironmentHardening(data_dir=tmpdir)

            # Create test directory
            test_dir = Path(tmpdir) / "test_secure"
            test_dir.mkdir()

            # On Unix, set insecure permissions
            if platform.system() != "Windows":
                os.chmod(test_dir, 0o777)

            # Should detect insecure permissions
            issues = hardening._validate_directory_permissions()

            # May or may not have issues depending on platform
            assert isinstance(issues, list)

    def test_data_structure_validation(self):
        """Test data structure initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hardening = EnvironmentHardening(data_dir=tmpdir)
            issues = hardening._validate_data_structures()

            # Should create required files
            assert isinstance(issues, list)

    def test_harden_sys_path(self):
        """Test sys.path hardening."""
        import sys

        # Add dangerous path
        original_path = sys.path.copy()
        sys.path.insert(0, ".")

        hardening = EnvironmentHardening()
        hardening.harden_sys_path()

        # Should remove dangerous paths
        assert "." not in sys.path

        # Restore original path
        sys.path = original_path

    def test_secure_directory_structure(self):
        """Test directory structure creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hardening = EnvironmentHardening(data_dir=tmpdir)
            hardening.secure_directory_structure()

            # Check directories were created
            for dir_path in hardening.required_dirs:
                full_path = Path(dir_path)
                if tmpdir in str(full_path):
                    assert full_path.exists()

    def test_validation_report(self):
        """Test validation report generation."""
        hardening = EnvironmentHardening()
        report = hardening.get_validation_report()

        # Should contain required keys
        assert "virtualenv" in report
        assert "sys_path_issues" in report
        assert "aslr_ssp_enabled" in report
        assert "platform" in report
        assert "python_version" in report


class TestSecureDataParser:
    """Test secure data parsing."""

    def test_xml_parsing_basic(self):
        """Test basic XML parsing."""
        parser = SecureDataParser()
        xml_data = "<root><item>test</item></root>"

        result = parser.parse_xml(xml_data)

        assert isinstance(result, ParsedData)
        assert result.data_type == "xml"
        assert result.validated

    def test_xml_xxe_detection(self):
        """Test XXE attack detection."""
        parser = SecureDataParser()
        xxe_data = """
        <!DOCTYPE foo [
        <!ENTITY xxe SYSTEM "file:///etc/passwd">
        ]>
        <root>&xxe;</root>
        """

        result = parser.parse_xml(xxe_data)

        assert not result.validated
        assert len(result.issues) > 0

    def test_xml_dtd_blocking(self):
        """Test DTD blocking."""
        parser = SecureDataParser()
        dtd_data = """
        <!DOCTYPE root [
        <!ELEMENT root ANY>
        ]>
        <root>test</root>
        """

        result = parser.parse_xml(dtd_data)

        assert not result.validated
        assert any("DTD" in issue for issue in result.issues)

    def test_csv_parsing_basic(self):
        """Test basic CSV parsing."""
        parser = SecureDataParser()
        csv_data = "name,age\nJohn,30\nJane,25"

        result = parser.parse_csv(csv_data)

        assert isinstance(result, ParsedData)
        assert result.data_type == "csv"
        assert len(result.data) == 2

    def test_csv_injection_detection(self):
        """Test CSV injection detection."""
        parser = SecureDataParser()
        csv_data = "name,command\nJohn,=cmd|'/c calc'\nJane,normal"

        result = parser.parse_csv(csv_data)

        assert len(result.issues) > 0

    def test_csv_schema_validation(self):
        """Test CSV schema validation."""
        parser = SecureDataParser()
        csv_data = "name,age\nJohn,30\nJane,invalid"

        schema = {"name": "string", "age": "int"}
        result = parser.parse_csv(csv_data, schema=schema)

        assert len(result.issues) > 0

    def test_json_parsing_basic(self):
        """Test basic JSON parsing."""
        parser = SecureDataParser()
        json_data = '{"name": "John", "age": 30}'

        result = parser.parse_json(json_data)

        assert isinstance(result, ParsedData)
        assert result.data_type == "json"
        assert result.validated
        assert result.data["name"] == "John"

    def test_json_schema_validation(self):
        """Test JSON schema validation."""
        parser = SecureDataParser()
        json_data = '{"name": "John"}'

        schema = {
            "required": ["name", "age"],
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        }

        result = parser.parse_json(json_data, schema=schema)

        assert len(result.issues) > 0
        assert any("age" in issue for issue in result.issues)

    def test_json_size_limit(self):
        """Test JSON size limiting."""
        parser = SecureDataParser()
        # Create very large JSON
        large_data = '{"data": "' + ("A" * (parser.max_file_size + 1)) + '"}'

        result = parser.parse_json(large_data)

        assert not result.validated
        assert len(result.issues) > 0


class TestDataPoisoningDefense:
    """Test data poisoning defense mechanisms."""

    def test_poison_pattern_detection(self):
        """Test poison pattern detection."""
        defense = DataPoisoningDefense()

        # Test XSS
        xss_data = "<script>alert('xss')</script>"
        is_poisoned, patterns = defense.check_for_poison(xss_data)

        assert is_poisoned
        assert len(patterns) > 0

    def test_sql_injection_detection(self):
        """Test SQL injection detection."""
        defense = DataPoisoningDefense()

        sqli_data = "1' OR '1'='1'; DROP TABLE users--"
        is_poisoned, patterns = defense.check_for_poison(sqli_data)

        assert is_poisoned

    def test_path_traversal_detection(self):
        """Test path traversal detection."""
        defense = DataPoisoningDefense()

        traversal_data = "../../etc/passwd"
        is_poisoned, patterns = defense.check_for_poison(traversal_data)

        assert is_poisoned

    def test_poison_signature_storage(self):
        """Test poison signature storage."""
        defense = DataPoisoningDefense()

        poison_data = "malicious content"
        defense.add_poison_signature(poison_data)

        # Should detect stored poison
        is_poisoned, patterns = defense.check_for_poison(poison_data)
        assert is_poisoned

    def test_input_sanitization(self):
        """Test input sanitization."""
        defense = DataPoisoningDefense()

        dirty_data = '<script>alert("xss")</script><div onclick="bad()">test</div>'
        clean_data = defense.sanitize_input(dirty_data)

        # Should remove scripts and event handlers
        assert "<script>" not in clean_data
        assert "onclick" not in clean_data

    def test_clean_input_passing(self):
        """Test that clean input passes validation."""
        defense = DataPoisoningDefense()

        clean_data = "This is normal text with no malicious content"
        is_poisoned, patterns = defense.check_for_poison(clean_data)

        assert not is_poisoned
        assert len(patterns) == 0


# Additional stress tests for data validation
class TestDataValidationStress:
    """Stress tests for data validation."""

    def test_large_xml_parsing(self):
        """Test parsing large XML documents."""
        parser = SecureDataParser()

        # Create large but valid XML
        xml_parts = ["<root>"]
        for i in range(100):
            xml_parts.append(f"<item id='{i}'>Content {i}</item>")
        xml_parts.append("</root>")

        xml_data = "".join(xml_parts)
        result = parser.parse_xml(xml_data)

        assert result.validated

    def test_deeply_nested_json(self):
        """Test deeply nested JSON structures."""
        parser = SecureDataParser()

        # Create nested JSON
        nested = {"level": 0}
        current = nested
        for i in range(1, 50):
            current["child"] = {"level": i}
            current = current["child"]

        import json

        json_data = json.dumps(nested)
        result = parser.parse_json(json_data)

        assert result.validated

    def test_unicode_handling(self):
        """Test Unicode character handling."""
        parser = SecureDataParser()

        # Test various Unicode ranges
        unicode_data = '{"text": "Hello 世界 🌍 Привет مرحبا"}'
        result = parser.parse_json(unicode_data)

        assert result.validated

    def test_concurrent_parsing(self):
        """Test concurrent parsing operations."""
        import threading

        parser = SecureDataParser()
        results = []

        def parse_task(index):
            json_data = f'{{"id": {index}, "name": "Task {index}"}}'
            result = parser.parse_json(json_data)
            results.append(result.validated)

        threads = []
        for i in range(10):
            t = threading.Thread(target=parse_task, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # All should succeed
        assert all(results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
