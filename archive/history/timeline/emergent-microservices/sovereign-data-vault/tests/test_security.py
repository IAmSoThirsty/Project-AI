# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-10 | TIME: 21:02               #
# COMPLIANCE: Regulator-Ready / UTF-8                                          #
# ============================================================================ #

# Date: 2026-03-10 | Time: 20:37 | Status: Active | Tier: Master
#                                           [2026-03-10 18:58]
#                                          Productivity: Active
# ============================================================================ #
#                                                            DATE: 2026-03-10 #
#                                                          TIME: 15:01:57 PST #
#                                                        PRODUCTIVITY: Active #
# ============================================================================ #

#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""Test security functions"""

import pytest

from security.__init__ import (
    create_jwt_token,
    sanitize_input,
    verify_api_key,
    verify_jwt_token,
)


def test_verify_api_key():
    """Test API key verification"""
    # Valid key
    assert verify_api_key("changeme") is True

    # Invalid key
    assert verify_api_key("invalid") is False


def test_create_and_verify_jwt_token():
    """Test JWT token creation and verification"""
    # Create token
    token = create_jwt_token("user123", {"role": "admin"})
    assert token is not None

    # Verify token
    payload = verify_jwt_token(token)
    assert payload is not None
    assert payload["sub"] == "user123"
    assert payload["role"] == "admin"


def test_verify_invalid_jwt_token():
    """Test invalid JWT token"""
    payload = verify_jwt_token("invalid.token.here")
    assert payload is None


def test_sanitize_input():
    """Test input sanitization"""
    # Remove null bytes
    assert sanitize_input("test\x00value") == "testvalue"

    # Truncate long input
    long_text = "a" * 2000
    assert len(sanitize_input(long_text, max_length=100)) == 100

    # Strip whitespace
    assert sanitize_input("  test  ") == "test"
