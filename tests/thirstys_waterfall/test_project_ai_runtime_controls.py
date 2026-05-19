import os

import pytest

from thirstys_waterfall.runtime_controls import (
    ACTIVE_CONTROLS_ENV,
    DESTRUCTIVE_RESPONSES_ENV,
    WaterfallActivationRequired,
    require_active_controls,
    require_destructive_responses,
)


def test_active_controls_require_explicit_activation(monkeypatch):
    monkeypatch.delenv(ACTIVE_CONTROLS_ENV, raising=False)

    with pytest.raises(WaterfallActivationRequired):
        require_active_controls({"project_ai": {"allow_active_controls": False}})

    require_active_controls({"project_ai": {"allow_active_controls": True}})


def test_active_controls_can_be_enabled_for_process(monkeypatch):
    monkeypatch.setenv(ACTIVE_CONTROLS_ENV, "1")

    require_active_controls()


def test_destructive_responses_require_separate_activation(monkeypatch):
    monkeypatch.delenv(DESTRUCTIVE_RESPONSES_ENV, raising=False)

    with pytest.raises(WaterfallActivationRequired):
        require_destructive_responses(
            {"project_ai": {"allow_destructive_responses": False}}
        )

    require_destructive_responses(
        {"project_ai": {"allow_destructive_responses": True}}
    )


def test_destructive_response_env_is_distinct_from_active_controls(monkeypatch):
    monkeypatch.setenv(ACTIVE_CONTROLS_ENV, "1")
    monkeypatch.delenv(DESTRUCTIVE_RESPONSES_ENV, raising=False)

    with pytest.raises(WaterfallActivationRequired):
        require_destructive_responses()

    assert os.environ[ACTIVE_CONTROLS_ENV] == "1"
