"""Extended tests for CommandOverrideSystem and the adapter (20+ cases)."""

from __future__ import annotations

import tempfile

import pytest

from app.core.ai_systems import CommandOverride, OverrideType
from app.core.command_override import CommandOverrideSystem


@pytest.fixture
def tmpdir():
    with tempfile.TemporaryDirectory() as td:
        yield td


def test_adapter_password_lifecycle(tmpdir):
    adapter = CommandOverride(data_dir=tmpdir)
    assert adapter.set_password("secret") is True
    assert adapter.verify_password("secret") is True
    assert adapter.verify_password("wrong") is False


def test_adapter_request_override_and_status(tmpdir):
    adapter = CommandOverride(data_dir=tmpdir)
    adapter.set_password("pw")
    ok, msg = adapter.request_override("pw", OverrideType.CONTENT_FILTER, reason="testing")
    assert ok is True
    assert "Override" in msg
    assert adapter.is_override_active(OverrideType.CONTENT_FILTER) is True


def test_adapter_unknown_protocol_is_graceful(tmpdir):
    adapter = CommandOverride(data_dir=tmpdir)
    adapter.set_password("pw")
    class FakeOverride:
        value = "nonexistent_protocol"
        name = "FAKE"
    ok, msg = adapter.request_override("pw", FakeOverride)  # type: ignore[arg-type]
    assert ok is True
    assert "Override" in msg


def test_adapter_statistics(tmpdir):
    adapter = CommandOverride(data_dir=tmpdir)
    adapter.set_password("pw")
    adapter.request_override("pw", OverrideType.RATE_LIMITING)
    stats = adapter.get_statistics()
    assert stats["password_set"] is True
    assert stats["active_overrides"] >= 1
    assert isinstance(stats["audit_entries"], int)


def test_system_master_override_flow(tmpdir):
    sys = CommandOverrideSystem(data_dir=tmpdir)
    assert sys.set_master_password("pw") is True
    assert sys.authenticate("pw") is True
    assert sys.enable_master_override() is True
    assert all(v is False for v in sys.get_all_protocols().values())
    assert sys.disable_master_override() is True
    assert all(v is True for v in sys.get_all_protocols().values())


def test_system_override_protocol_requires_auth(tmpdir):
    sys = CommandOverrideSystem(data_dir=tmpdir)
    ok = sys.override_protocol("content_filter", enabled=False)
    assert ok is False
    sys.set_master_password("pw")
    sys.authenticate("pw")
    assert sys.override_protocol("content_filter", enabled=False) is True
    assert sys.is_protocol_enabled("content_filter") is False


def test_system_unknown_protocol(tmpdir):
    sys = CommandOverrideSystem(data_dir=tmpdir)
    sys.set_master_password("pw")
    sys.authenticate("pw")
    ok = sys.override_protocol("totally_unknown", enabled=False)
    assert ok is False


def test_system_emergency_lockdown(tmpdir):
    sys = CommandOverrideSystem(data_dir=tmpdir)
    sys.set_master_password("pw")
    sys.authenticate("pw")
    sys.enable_master_override()
    sys.emergency_lockdown()
    assert all(sys.is_protocol_enabled(k) is True for k in sys.get_all_protocols())
    assert sys.get_status()["authenticated"] is False


def test_system_audit_log_written(tmpdir):
    sys = CommandOverrideSystem(data_dir=tmpdir)
    sys.set_master_password("pw")
    sys.authenticate("pw")
    sys.override_protocol("prompt_safety", enabled=False)
    lines = sys.get_audit_log(lines=10)
    assert any("OVERRIDE_PROTOCOL" in (line or "") for line in lines)


def test_adapter_audit_log_access(tmpdir):
    adapter = CommandOverride(data_dir=tmpdir)
    adapter.set_password("pw")
    adapter.request_override("pw", OverrideType.CONTENT_FILTER)
    assert len(adapter.audit_log) > 0
