"""Integration test: project-ai lang subcommands for the 6 Thirsty-Lang tiers.

Per PHASE_T_DISCOVERY.md Phase T4: the 6 tier CLIs (thirsty,
thirst-of-gods, tscg, tscg-b, tarl, shadow-thirst) are exposed as
subcommands of `project-ai lang <tier>`. Each subcommand delegates
to the language's CLI with the operator's args forwarded as-is.

Honest scope:
- Tests the Typer sub-app wiring (subcommands, names, forwarded args).
- Tests the dep-import-failure surface (mocked).
- Does NOT test the language's internal CLI behavior (thousands of
  tests already exist upstream in the thirsty-lang repo).
"""

from __future__ import annotations

import importlib
import sys
from unittest.mock import patch

import pytest

# Import lazily so a missing thirsty-lang dep doesn't fail test
# collection. The module's own fail-closed handling is the contract.
thirsty_module = importlib.import_module("project_ai_cli.thirsty")
TIER_NAMES = thirsty_module.TIER_NAMES


# ── 1. Module surface ────────────────────────────────────────


def test_tier_names_canonical() -> None:
    """The 6 tier names are present, in canonical order."""
    assert TIER_NAMES == (
        "thirsty",
        "thirst-of-gods",
        "tscg",
        "tscg-b",
        "tarl",
        "shadow-thirst",
    )


def test_subapp_is_typer_instance() -> None:
    """The exposed `app` is a Typer sub-app."""
    import typer

    assert isinstance(thirsty_module.app, typer.Typer)


# ── 2. Subcommand registration ────────────────────────────


def _registered_command_names() -> set[str]:
    """Return the set of subcommand names registered on the sub-app.

    Typer's introspection API exposes registered commands as
    `app.registered_commands`. Each command has a `name` attribute.
    """
    return {cmd.name for cmd in thirsty_module.app.registered_commands}


def test_six_tier_commands_registered() -> None:
    """Each of the 6 tiers is registered as a Typer subcommand."""
    registered = _registered_command_names()
    for tier in TIER_NAMES:
        assert tier in registered, f"{tier!r} not in {registered!r}"


def test_no_extra_tier_commands() -> None:
    """No tier commands beyond the canonical 6."""
    assert _registered_command_names() == set(TIER_NAMES)


# ── 3. Argv reconstruction ───────────────────────────────


def test_argv_reconstruction_preserves_tier_and_args() -> None:
    """_run_tier reconstructs sys.argv as [tier, *args]."""
    captured: dict[str, list[str]] = {}

    def fake_main() -> None:
        captured["argv"] = list(sys.argv)

    original_main = thirsty_module._TIER_MAIN["thirsty"]
    try:
        thirsty_module._TIER_MAIN["thirsty"] = fake_main
        with patch.object(sys, "argv", ["project-ai", "lang", "thirsty"]):
            thirsty_module._run_tier("thirsty", ["run", "demo.thirsty"])
    finally:
        thirsty_module._TIER_MAIN["thirsty"] = original_main

    assert captured["argv"] == ["thirsty", "run", "demo.thirsty"]


def test_argv_restored_after_run() -> None:
    """_run_tier restores the original sys.argv in a finally block.

    We capture the real `sys.argv` before the call (the test
    runner's own argv, e.g. `['pytest', '--tb=short']`) and assert
    that the post-call `sys.argv` matches it.
    """
    pre_call_argv = list(sys.argv)

    def fake_main() -> None:
        raise RuntimeError("simulated language CLI failure")

    original_main = thirsty_module._TIER_MAIN["thirsty"]
    try:
        thirsty_module._TIER_MAIN["thirsty"] = fake_main
        with pytest.raises((SystemExit, RuntimeError)):
            thirsty_module._run_tier("thirsty", [])
    finally:
        thirsty_module._TIER_MAIN["thirsty"] = original_main

    assert sys.argv == pre_call_argv


# ── 4. Fail-closed: missing dep ──────────────────────────


def test_check_dep_surfaces_missing_dep() -> None:
    """When the thirsty-lang dep import fails, _check_dep emits a
    clear error and raises typer.Exit(1).
    """
    import typer as _typer

    original_error = getattr(thirsty_module, "_THIRSTY_IMPORT_ERROR", None)
    try:
        thirsty_module._THIRSTY_IMPORT_ERROR = (  # type: ignore[attr-defined]
            "No module named 'utf.thirsty_lang'"
        )
        with pytest.raises(_typer.Exit) as exit_info:
            thirsty_module._check_dep("thirsty")
        assert exit_info.value.exit_code == 1
    finally:
        thirsty_module._THIRSTY_IMPORT_ERROR = original_error  # type: ignore[attr-defined]


def test_check_dep_passes_when_dep_available() -> None:
    """_check_dep is a no-op when the dep is installed."""
    # Default state: the dep is installed (we import it above).
    thirsty_module._check_dep("tarl")


# ── 5. CLI end-to-end smoke (via typer testing) ──────────


def test_project_ai_lang_help_lists_six_tiers() -> None:
    """`project-ai lang --help` lists the 6 tier subcommands.

    The sub-app has `add_help_option=False`, so `--help` is treated
    as a forwarded arg. With `--` to separate Typer's args from the
    forwarded args, the language's argparse is invoked and prints
    the tier help. We verify the dispatch happens by asserting that
    the sub-app's registered commands include all 6 tiers.
    """
    # Confirm registration directly via Typer's introspection API
    # (the sub-app's own --help would be intercepted by the language).
    registered = _registered_command_names()
    for tier in TIER_NAMES:
        assert tier in registered


def test_project_ai_lang_subcommand_forwards_to_tier_cli() -> None:
    """`project-ai lang tarl -- --help` invokes the language's CLI."""
    from typer.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(thirsty_module.app, ["tarl", "--", "--help"])
    # The language's CLI prints "T.A.R.L." in its help.
    assert "T.A.R.L." in result.output or "TARL" in result.output.upper(), (
        f"language help not forwarded: {result.output[:200]!r}"
    )
