"""Unit tests for GUI input validation security fixes.

Tests sanitize_input, validate_length, and validate_email functions.
"""

import pytest

from app.security.data_validation import sanitize_input, validate_email, validate_length


class TestSanitizeInput:
    """Tests for sanitize_input function."""

    def test_xss_script_tags_removed(self):
        """Test that script tags are removed."""
        malicious = "<script>alert('xss')</script>"
        sanitized = sanitize_input(malicious)
        assert "<script>" not in sanitized.lower()
        assert "alert" not in sanitized.lower()

    def test_xss_event_handlers_removed(self):
        """Test that event handlers are removed."""
        malicious = "<img src=x onerror=alert('xss')>"
        sanitized = sanitize_input(malicious)
        assert "onerror" not in sanitized.lower()

    def test_javascript_urls_removed(self):
        """Test that javascript: URLs are removed."""
        malicious = "javascript:alert('xss')"
        sanitized = sanitize_input(malicious)
        assert "javascript:" not in sanitized.lower()

    def test_sql_injection_patterns_removed(self):
        """Test that SQL injection patterns are removed."""
        malicious = "'; DROP TABLE users--"
        sanitized = sanitize_input(malicious)
        assert "DROP TABLE" not in sanitized.upper()

        malicious2 = "' OR '1'='1"
        sanitized2 = sanitize_input(malicious2)
        assert "OR '1'='1" not in sanitized2

    def test_path_traversal_removed(self):
        """Test that path traversal attempts are removed."""
        malicious = "../../../etc/passwd"
        sanitized = sanitize_input(malicious)
        assert "../" not in sanitized

        malicious2 = "..\\..\\..\\windows\\system32"
        sanitized2 = sanitize_input(malicious2)
        assert "..\\" not in sanitized2

    def test_null_bytes_removed(self):
        """Test that null bytes are removed."""
        malicious = "username\x00password"
        sanitized = sanitize_input(malicious)
        assert "\x00" not in sanitized

    def test_max_length_enforced(self):
        """Test that max_length parameter works."""
        long_input = "a" * 200
        sanitized = sanitize_input(long_input, max_length=50)
        assert len(sanitized) == 50

    def test_empty_string_returns_empty(self):
        """Test that empty string is handled."""
        assert sanitize_input("") == ""
        assert sanitize_input("   ") == ""

    def test_non_string_returns_empty(self):
        """Test that non-string input returns empty string."""
        assert sanitize_input(None) == ""
        assert sanitize_input(123) == ""
        assert sanitize_input([]) == ""

    def test_normal_text_unchanged(self):
        """Test that normal text passes through."""
        normal = "This is normal text"
        sanitized = sanitize_input(normal)
        assert sanitized == normal


class TestValidateLength:
    """Tests for validate_length function."""

    def test_valid_length_within_bounds(self):
        """Test that valid lengths pass."""
        assert validate_length("user", min_len=3, max_len=50) is True
        assert validate_length("a" * 50, min_len=3, max_len=50) is True
        assert validate_length("password123", min_len=8, max_len=128) is True

    def test_too_short_rejected(self):
        """Test that too short strings are rejected."""
        assert validate_length("ab", min_len=3, max_len=50) is False
        assert validate_length("pass", min_len=8, max_len=128) is False

    def test_too_long_rejected(self):
        """Test that too long strings are rejected."""
        assert validate_length("a" * 51, min_len=3, max_len=50) is False
        assert validate_length("a" * 129, min_len=8, max_len=128) is False

    def test_no_max_length(self):
        """Test that None max_len allows any length."""
        assert validate_length("a" * 1000, min_len=0, max_len=None) is True

    def test_invalid_types_rejected(self):
        """Test that non-string types are rejected."""
        assert validate_length(None, min_len=3, max_len=50) is False
        assert validate_length(123, min_len=3, max_len=50) is False
        assert validate_length([], min_len=3, max_len=50) is False


class TestValidateEmail:
    """Tests for validate_email function."""

    def test_valid_emails_accepted(self):
        """Test that valid email formats are accepted."""
        assert validate_email("user@example.com") is True
        assert validate_email("test.user@domain.co.uk") is True
        assert validate_email("admin+tag@company.org") is True

    def test_invalid_emails_rejected(self):
        """Test that invalid email formats are rejected."""
        assert validate_email("not-an-email") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
        assert validate_email("user @example.com") is False
        assert validate_email("user@.com") is False
        assert validate_email("") is False

    def test_non_string_emails_rejected(self):
        """Test that non-string types are rejected."""
        assert validate_email(None) is False
        assert validate_email(123) is False
        assert validate_email([]) is False


class TestCombinedAttacks:
    """Tests for combined attack vectors."""

    def test_combined_xss_sql_path(self):
        """Test combined XSS + SQL + path traversal."""
        combined = "<script>alert('xss')</script>'; DROP TABLE users--../../../etc/passwd"
        sanitized = sanitize_input(combined, max_length=100)

        # All attack vectors should be neutralized
        assert "<script>" not in sanitized.lower()
        assert "DROP TABLE" not in sanitized.upper()
        assert "../" not in sanitized
        assert len(sanitized) <= 100

    def test_multiple_xss_vectors(self):
        """Test multiple XSS vectors in one input."""
        xss = '<script>evil()</script><img onerror="bad()">javascript:alert(1)'
        sanitized = sanitize_input(xss)

        assert "<script>" not in sanitized.lower()
        assert "onerror" not in sanitized.lower()
        assert "javascript:" not in sanitized.lower()


@pytest.mark.parametrize(
    "malicious_input,expected_removed",
    [
        ("<script>alert('xss')</script>", "<script>"),
        ("'; DROP TABLE users--", "DROP TABLE"),
        ("../../../etc/passwd", "../"),
        ("javascript:alert(1)", "javascript:"),
        ("<img onerror='alert(1)'>", "onerror"),
        ("' OR '1'='1", "OR '1'='1"),
    ],
)
def test_malicious_patterns_removed(malicious_input, expected_removed):
    """Parametrized test for various malicious patterns."""
    sanitized = sanitize_input(malicious_input)
    assert expected_removed.lower() not in sanitized.lower()
