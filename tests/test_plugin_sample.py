"""Tests for the sample marketplace plugin."""

from __future__ import annotations

import json
from pathlib import Path

from app.plugins import sample_plugin


def test_sample_plugin_initializes_with_user_order() -> None:
    assert sample_plugin.initialize({"is_user_order": True}) is True


def test_sample_plugin_blocks_dangerous_context() -> None:
    assert sample_plugin.initialize({"endangers_human": True}) is False


def test_sample_plugin_blocks_requires_explicit_order_without_user_prompt() -> None:
    assert sample_plugin.initialize({"requires_explicit_order": True}) is False


def test_plugin_descriptor_contains_required_fields() -> None:
    descriptor = Path(sample_plugin.__file__).with_name("plugin.json")
    assert descriptor.exists()
    data = json.loads(descriptor.read_text(encoding="utf-8"))
    assert data["name"] == "marketplace_sample_plugin"
    assert data.get("four_laws_safe") is True
    assert data.get("hooks", [])
    assert "before_action" in data["hooks"]
    assert data.get("safe_for_learning") is False
