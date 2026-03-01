"""Tests for MiniatureOfficeAdapter — plugin that wires the Miniature Office into Project-AI."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Adapter — enabled mode
# ---------------------------------------------------------------------------


class TestMiniatureOfficeAdapterEnabled:
    """Tests with ENABLE_MINIATURE_OFFICE=1 (default)."""

    @patch.dict(os.environ, {"ENABLE_MINIATURE_OFFICE": "1"})
    def test_adapter_initializes_when_enabled(self):
        from app.plugins.miniature_office_adapter import MiniatureOfficeAdapter

        adapter = MiniatureOfficeAdapter()
        result = adapter.initialize()
        assert result is True

    @patch.dict(os.environ, {"ENABLE_MINIATURE_OFFICE": "1"})
    def test_get_cognitive_ide_returns_facade(self):
        from app.plugins.miniature_office_adapter import MiniatureOfficeAdapter

        adapter = MiniatureOfficeAdapter()
        adapter.initialize()
        ide = adapter.get_cognitive_ide()
        assert ide is not None
        assert hasattr(ide, "create_directive")
        assert hasattr(ide, "list_floors")
        assert hasattr(ide, "get_simulation_state")

    @patch.dict(os.environ, {"ENABLE_MINIATURE_OFFICE": "1"})
    def test_get_repair_crew_returns_facade(self):
        from app.plugins.miniature_office_adapter import MiniatureOfficeAdapter

        adapter = MiniatureOfficeAdapter()
        adapter.initialize()
        crew = adapter.get_repair_crew()
        assert crew is not None
        assert hasattr(crew, "diagnose")
        assert hasattr(crew, "repair")
        assert hasattr(crew, "get_health_report")

    @patch.dict(os.environ, {"ENABLE_MINIATURE_OFFICE": "1"})
    def test_get_agent_lounge_returns_facade(self):
        from app.plugins.miniature_office_adapter import MiniatureOfficeAdapter

        adapter = MiniatureOfficeAdapter()
        adapter.initialize()
        lounge = adapter.get_agent_lounge()
        assert lounge is not None
        assert hasattr(lounge, "check_in")
        assert hasattr(lounge, "start_discussion")
        assert hasattr(lounge, "submit_proposal")
        assert hasattr(lounge, "get_lounge_state")

    @patch.dict(os.environ, {"ENABLE_MINIATURE_OFFICE": "1"})
    def test_get_meta_security_returns_facade(self):
        from app.plugins.miniature_office_adapter import MiniatureOfficeAdapter

        adapter = MiniatureOfficeAdapter()
        adapter.initialize()
        sec = adapter.get_meta_security()
        assert sec is not None
        assert hasattr(sec, "scan_for_violations")
        assert hasattr(sec, "contain")
        assert hasattr(sec, "emergency_shutdown")
        assert hasattr(sec, "enforce_vr_action")
        assert hasattr(sec, "request_reinstatement")

    @patch.dict(os.environ, {"ENABLE_MINIATURE_OFFICE": "1"})
    def test_status_when_initialized(self):
        from app.plugins.miniature_office_adapter import MiniatureOfficeAdapter

        adapter = MiniatureOfficeAdapter()
        adapter.initialize()
        status = adapter.get_status()
        assert status["enabled"] is True
        assert status["initialized"] is True
        assert status["components"]["cognitive_ide"] is True
        assert status["components"]["repair_crew"] is True
        assert status["components"]["agent_lounge"] is not None
        assert status["components"]["meta_security"] is not None


# ---------------------------------------------------------------------------
# Adapter — disabled mode
# ---------------------------------------------------------------------------


class TestMiniatureOfficeAdapterDisabled:
    """Tests with ENABLE_MINIATURE_OFFICE=0."""

    @patch.dict(os.environ, {"ENABLE_MINIATURE_OFFICE": "0"})
    def test_adapter_returns_false_when_disabled(self):
        from app.plugins.miniature_office_adapter import MiniatureOfficeAdapter

        adapter = MiniatureOfficeAdapter()
        result = adapter.initialize()
        assert result is False

    @patch.dict(os.environ, {"ENABLE_MINIATURE_OFFICE": "0"})
    def test_accessors_return_none_when_disabled(self):
        from app.plugins.miniature_office_adapter import MiniatureOfficeAdapter

        adapter = MiniatureOfficeAdapter()
        adapter.initialize()
        assert adapter.get_cognitive_ide() is None
        assert adapter.get_repair_crew() is None
        assert adapter.get_agent_lounge() is None
        assert adapter.get_meta_security() is None

    @patch.dict(os.environ, {"ENABLE_MINIATURE_OFFICE": "0"})
    def test_status_when_disabled(self):
        from app.plugins.miniature_office_adapter import MiniatureOfficeAdapter

        adapter = MiniatureOfficeAdapter()
        adapter.initialize()
        status = adapter.get_status()
        assert status["enabled"] is False
        assert status["initialized"] is False
