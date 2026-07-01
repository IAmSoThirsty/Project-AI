"""Thirsty-Lang CLI surface for the operator.

Per PHASE_T_DISCOVERY.md Phase T4: the 6 tier CLIs from Thirsty-Lang
(thirsty, thirst-of-gods, tscg, tscg-b, tarl, shadow-thirst) are
exposed as subcommands of the `project-ai` operator CLI. Each
subcommand delegates to the language's CLI `main()` function with
the operator's command-line arguments forwarded as-is.

Subordination contract:
  - Thirsty-Lang is a TOOL. The Python operator CLI is the
    authoritative surface. The 6 subcommands are convenience
    pass-throughs; they do not augment or replace the existing
    `project-ai` commands.
  - Fail-closed: if the `thirsty-lang` dep is missing, every
    subcommand exits with a clear error. We do not silently
    degrade.
  - The forwarding is via `sys.argv` reconstruction: the language's
    CLI uses `argparse` and reads from `sys.argv`. We rebuild argv
    with the tier name + the operator's args, invoke `main()`, then
    restore the original argv.

This module is registered as a Typer sub-app on the top-level
`project-ai` CLI. Operators invoke:

    project-ai thirsty run demo.thirsty --trace
    project-ai tarl eval policy.tarl --context '{"role":"admin"}'
    project-ai tscg prove src.thirst
    etc.

The 6 subcommands are: thirsty, thirst-of-gods, tscg, tscg-b, tarl,
shadow-thirst.
"""

from __future__ import annotations

import sys
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Final

import typer

if TYPE_CHECKING:
    from collections.abc import Callable as _Callable
    from typing import Any as _Any

    # Stub types so the runtime assignments below type-check when
    # the dep is unavailable. The runtime imports at the try-block
    # override these with the real callables.
    _thirsty_main: _Callable[[], _Any]
    _thirst_of_gods_main: _Callable[[], _Any]
    _tscg_main: _Callable[[], _Any]
    _tscg_b_main: _Callable[[], _Any]
    _tarl_main: _Callable[[], _Any]
    _shadow_thirst_main: _Callable[[], _Any]
else:
    _thirsty_main = None
    _thirst_of_gods_main = None
    _tscg_main = None
    _tscg_b_main = None
    _tarl_main = None
    _shadow_thirst_main = None

# Tier CLIs are imported lazily so a missing thirsty-lang dep does
# not crash the rest of the CLI. Each tier is fail-closed: a missing
# `main()` surfaces as a RuntimeError to the operator with a clear
# message.
try:
    from utf.shadow_thirst.cli import main as _shadow_thirst_main_runtime
    from utf.tarl.cli import main as _tarl_main_runtime
    from utf.thirst_of_gods.cli import main as _thirst_of_gods_main_runtime
    from utf.thirsty_lang.cli import main as _thirsty_main_runtime
    from utf.tscg.cli import main as _tscg_main_runtime
    from utf.tscg_b.cli import main as _tscg_b_main_runtime

    _thirsty_main = _thirsty_main_runtime
    _thirst_of_gods_main = _thirst_of_gods_main_runtime
    _tscg_main = _tscg_main_runtime
    _tscg_b_main = _tscg_b_main_runtime
    _tarl_main = _tarl_main_runtime
    _shadow_thirst_main = _shadow_thirst_main_runtime
    _THIRSTY_IMPORT_ERROR: str | None = None
except ImportError as _import_error:  # pragma: no cover - fail-closed
    _THIRSTY_IMPORT_ERROR = str(_import_error)


# The 6 tier names, in canonical order. Used to build the Typer
# sub-app command list and to validate operator input.
TIER_NAMES: Final[tuple[str, ...]] = (
    "thirsty",
    "thirst-of-gods",
    "tscg",
    "tscg-b",
    "tarl",
    "shadow-thirst",
)


# Map tier name -> the language's CLI main() function. Used by the
# generic `invoke_tier` helper so each subcommand is a one-liner
# Typer binding.
_TIER_MAIN: Final[Mapping[str, Any]] = {
    "thirsty": _thirsty_main,
    "thirst-of-gods": _thirst_of_gods_main,
    "tscg": _tscg_main,
    "tscg-b": _tscg_b_main,
    "tarl": _tarl_main,
    "shadow-thirst": _shadow_thirst_main,
}


# Typer sub-app exposed as a single nested group: `project-ai thirsty ...`,
# `project-ai tarl ...`, etc. The actual command names are the tier
# names. We register the sub-app on the parent via `app.add_typer`.
#
# `add_help_option=False` at the sub-app level disables Typer's
# auto-injected `--help` option so the operator's `--help` is
# forwarded to the language's argparse-based CLI (which has its
# own --help).
app = typer.Typer(
    name="lang",
    help=(
        "Thirsty-Lang tier CLIs. The 6 tier CLIs (thirsty, thirst-of-gods, "
        "tscg, tscg-b, tarl, shadow-thirst) are exposed as subcommands. "
        "Each subcommand delegates to the language's CLI with the "
        "operator's arguments forwarded as-is."
    ),
    no_args_is_help=True,
    add_completion=False,
    add_help_option=False,
    invoke_without_command=True,
)


def _check_dep(tier: str) -> None:
    """Verify the dep is available; emit a clear error if not."""
    if _THIRSTY_IMPORT_ERROR is not None:
        typer.echo(
            f"Error: thirsty-lang is not installed "
            f"(required for `project-ai {tier}`): {_THIRSTY_IMPORT_ERROR}",
            err=True,
        )
        raise typer.Exit(code=1)
    main_fn = _TIER_MAIN.get(tier)
    if main_fn is None:
        typer.echo(
            f"Error: tier {tier!r} main() is unavailable in this build",
            err=True,
        )
        raise typer.Exit(code=1)


def _run_tier(tier: str, args: list[str]) -> None:
    """Invoke the tier's main() with the operator's args forwarded.

    Reconstructs `sys.argv` to `[tier, *args]`, invokes the tier's
    `main()`, then restores the original argv in a `finally` block
    to keep the host CLI's argv intact.
    """
    _check_dep(tier)
    main_fn = _TIER_MAIN[tier]
    original_argv = sys.argv
    try:
        # The sub-app's `add_help_option=False` means Typer does not
        # strip --help from the forwarded args. But if the operator
        # typed `project-ai lang <tier>` with no args, Typer's
        # `no_args_is_help=False` (set on the command) means we
        # receive `args=None` and we forward `[]` — the language's
        # argparse will then print its own usage and exit 2.
        sys.argv = [tier, *args]
        main_fn()
    except SystemExit as exit_event:
        # The language's CLIs raise SystemExit on parse errors or
        # bad input. Propagate so Typer sees the proper exit code.
        # The exit code is normally an int; `None` is treated as 0.
        code = exit_event.code if isinstance(exit_event.code, int) else 1
        raise typer.Exit(code=code) from None
    except Exception as exc:
        typer.echo(
            f"Error: tier {tier!r} failed: {type(exc).__name__}: {exc}",
            err=True,
        )
        raise typer.Exit(code=1) from exc
    finally:
        sys.argv = original_argv


# Register each tier as a Typer subcommand. We use `context_settings`
# to capture the trailing args (everything after the tier name) and
# forward them.
@app.callback(invoke_without_command=True)
def _lang_root(
    ctx: typer.Context,
) -> None:
    """Thirsty-Lang tier CLI passthrough. See subcommands below."""
    if ctx.invoked_subcommand is None:
        typer.echo(
            "Specify a tier: " + ", ".join(TIER_NAMES),
            err=True,
        )
        raise typer.Exit(code=1)


def _make_tier_command(tier: str) -> Any:
    """Build a Typer command that forwards to `tier`'s main().

    Per the sub-app's `add_help_option=False`, the operator's
    `--help` is NOT intercepted by Typer; it flows through to the
    forwarded args, where the language's argparse-based CLI prints
    its own help text.
    """

    def cmd(
        ctx: typer.Context,
        args: list[str] = typer.Argument(
            None,
            help=(
                f"Arguments forwarded to the {tier} tier CLI. "
                f"Run `project-ai lang {tier} -- --help` to see the "
                f"language's own help (the leading `--` separates "
                f"Typer's args from the forwarded args)."
            ),
        ),
    ) -> None:
        if args is None:
            args = []
        _run_tier(tier, args)

    cmd.__name__ = tier.replace("-", "_")
    cmd.__doc__ = f"Forward to the {tier} tier CLI."
    return app.command(
        tier,
        add_help_option=False,
        no_args_is_help=False,
    )(cmd)


# Register the 6 tier commands at import time. This is the
# canonical, declarative list — adding a new tier means adding a
# name to TIER_NAMES + a CLI entry in the language's setuptools
# config; the registration here follows automatically.
for _tier in TIER_NAMES:
    _make_tier_command(_tier)


__all__ = [
    "TIER_NAMES",
    "app",
]
