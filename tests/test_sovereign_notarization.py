"""Tests for sovereign_audit_log TSA notarization wiring."""

import base64
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest


def _stub_heavy_deps():
    """Stub crypto + internal deps so we can import sovereign_audit_log."""
    stubs = {}
    for mod_name in [
        "cryptography",
        "cryptography.hazmat",
        "cryptography.hazmat.backends",
        "cryptography.hazmat.primitives",
        "cryptography.hazmat.primitives.asymmetric",
        "cryptography.hazmat.primitives.asymmetric.ed25519",
        "cryptography.hazmat.primitives.hashes",
        "cryptography.hazmat.primitives.serialization",
        "app.governance.audit_log",
        "app.governance.external_merkle_anchor",
        "app.governance.genesis_continuity",
        "app.governance.tsa_anchor_manager",
        "app.governance.tsa_provider",
        "src.app.governance.audit_log",
        "src.app.governance.external_merkle_anchor",
        "src.app.governance.genesis_continuity",
        "src.app.governance.tsa_anchor_manager",
    ]:
        if mod_name not in sys.modules:
            stubs[mod_name] = MagicMock()

    sys.modules.update(stubs)


_stub_heavy_deps()


def _find_audit_class():
    """Find the class that has _request_notarization in the sovereign_audit_log module."""
    import importlib

    mod = importlib.import_module("app.governance.sovereign_audit_log")

    for attr_name in dir(mod):
        cls = getattr(mod, attr_name, None)
        if isinstance(cls, type) and hasattr(cls, "_request_notarization"):
            return cls
    return None


class TestNotarization:
    """Tests specifically for _request_notarization wiring."""

    def test_notarization_disabled_returns_none(self):
        """When notarization is disabled, _request_notarization returns None."""
        cls = _find_audit_class()
        if cls is None:
            pytest.skip("Could not find class with _request_notarization")

        fake = MagicMock(spec=cls)
        fake.notarization_enabled = False
        fake.tsa_provider = None

        result = cls._request_notarization(fake, b"test-data")
        assert result is None

    def test_notarization_enabled_calls_tsa(self):
        """When notarization is enabled, _request_notarization calls TSAProvider."""
        cls = _find_audit_class()
        if cls is None:
            pytest.skip("Could not find class with _request_notarization")

        mock_token = MagicMock()
        mock_token.raw_der = b"\x30\x03\x01\x01\xff"
        mock_token.serial_number = "123456"
        mock_token.tsa_time = None

        mock_tsa = MagicMock()
        mock_tsa.request_timestamp.return_value = mock_token

        fake = MagicMock(spec=cls)
        fake.notarization_enabled = True
        fake.tsa_provider = mock_tsa

        result = cls._request_notarization(fake, b"test-data")
        assert result is not None
        # Must be valid base64
        decoded = base64.b64decode(result)
        assert decoded == mock_token.raw_der
        mock_tsa.request_timestamp.assert_called_once_with(b"test-data")

    def test_notarization_error_returns_none(self):
        """TSA errors are non-fatal — returns None."""
        cls = _find_audit_class()
        if cls is None:
            pytest.skip("Could not find class with _request_notarization")

        mock_tsa = MagicMock()
        mock_tsa.request_timestamp.side_effect = RuntimeError("TSA unreachable")

        fake = MagicMock(spec=cls)
        fake.notarization_enabled = True
        fake.tsa_provider = mock_tsa

        result = cls._request_notarization(fake, b"test-data")
        assert result is None
