"""Regression tests for governance pipeline fixes.

These tests focus on security-critical behaviors that previously regressed.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.core.governance import pipeline


class TestGovernancePipelineRegressions:
    def test_validate_rejects_prefix_bypass_action(self):
        """Unknown actions must be rejected even when prefix matches known families."""
        context = {
            "source": "desktop",
            "payload": {},
            "action": "codex.unknown_action",
        }

        with pytest.raises(ValueError, match="not in registry"):
            pipeline._validate(context)

    def test_user_login_handles_tuple_auth_result(self, monkeypatch: pytest.MonkeyPatch):
        """UserManager.authenticate returns tuple(bool, message) and must not bypass."""

        class FakeUserManager:
            def __init__(self):
                self.users = {}

            def authenticate(self, username, password):
                return (False, "Invalid credentials")

        monkeypatch.setattr("app.core.user_manager.UserManager", FakeUserManager)

        with pytest.raises(PermissionError, match="Invalid credentials"):
            pipeline._execute(
                {
                    "action": "user.login",
                    "payload": {"username": "bad-user", "password": "bad-pass"},
                    "source": "web",
                    "user": {},
                }
            )

    def test_resolve_user_context_from_token(self, monkeypatch: pytest.MonkeyPatch):
        """JWT token should resolve username/role when explicit user context is absent."""
        token_payload = SimpleNamespace(username="alice", role="admin")
        monkeypatch.setattr(
            "app.core.security.auth.verify_jwt_token",
            lambda token: token_payload,
        )

        context = {
            "source": "web",
            "action": "ai.chat",
            "payload": {"prompt": "hello", "token": "jwt-token"},
            "user": {},
        }

        resolved = pipeline._resolve_user_context(context)

        assert resolved["username"] == "alice"
        assert resolved["role"] == "admin"
        assert context["user"]["username"] == "alice"

    def test_gate_blocks_anonymous_ai_chat_without_token(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        """AI actions requiring authenticated users must reject anonymous calls."""
        monkeypatch.setattr(
            "app.core.ai_systems.FourLaws.validate_action",
            lambda action, context=None: (True, "ok"),
        )

        context = {
            "source": "web",
            "action": "ai.chat",
            "payload": {"prompt": "hello"},
            "user": {},
        }

        with pytest.raises(PermissionError, match="requires role"):
            pipeline._gate(context, simulation={})

    def test_persona_update_returns_non_none_result(self, monkeypatch: pytest.MonkeyPatch):
        """persona.update must return structured result to satisfy commit consistency checks."""

        class FakePersona:
            def __init__(self):
                self.personality = {"curiosity": 0.5}

            def adjust_trait(self, trait, delta):
                self.personality[trait] = self.personality.get(trait, 0.0) + delta

        monkeypatch.setattr("app.core.ai_systems.AIPersona", FakePersona)

        result = pipeline._execute(
            {
                "action": "persona.update",
                "payload": {"trait": "curiosity", "value": 0.2},
                "source": "desktop",
                "user": {"username": "tester", "role": "user"},
            }
        )

        assert isinstance(result, dict)
        assert result["status"] == "updated"
        assert result["trait"] == "curiosity"
        assert result["value"] is not None
