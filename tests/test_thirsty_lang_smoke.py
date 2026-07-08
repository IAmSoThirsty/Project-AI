"""Thirsty-Lang integration smoke test.

Verifies the workspace can import the six tiers of the domain sovereign
language (thirsty-lang 0.8.1) and that the language's CLI entrypoints
are on PATH after `uv sync`. Per Phase T1 of PHASE_T_DISCOVERY.md.

This test is intentionally minimal — it is the T1 acceptance gate.
Subsequent phases (T2 governance, T3 audit proofs, T4 CLI surface,
T5 atlas+swr specs, T7 shadow convergence) add real integration
tests at their respective layers.

Honest scope:
- Imports of the 6 tier modules (utf.thirsty_lang, utf.thirst_of_gods,
  utf.tscg, utf.tscg_b, utf.tarl, utf.shadow_thirst)
- The language package's __version__ attribute is 0.8.1
- The package's CLI entrypoint functions are importable and callable
  (no execution — the dry-run guard is on the cli module's main())

Subordinate to the canonical kernel: the language is a tool, not a
peer. This test only proves the dep is wired; it does NOT prove the
language is being USED to write code (that's the point of T2+).
"""

from __future__ import annotations

import importlib
import shutil
import subprocess

import pytest

# The 6 tiers from PHASE_T_DISCOVERY.md §1
TIERS = (
    "utf.thirsty_lang",
    "utf.thirst_of_gods",
    "utf.tscg",
    "utf.tscg_b",
    "utf.tarl",
    "utf.shadow_thirst",
)


@pytest.mark.parametrize("tier", TIERS)
def test_tier_module_importable(tier: str) -> None:
    """Each of the 6 tiers must be importable from the installed `utf` package."""
    module = importlib.import_module(tier)
    assert module is not None
    assert hasattr(module, "__file__"), f"{tier} missing __file__"


def test_thirsty_lang_version_pinned() -> None:
    """The installed version must match the discovery's pin (0.8.1)."""
    # The `utf` package does not export `__version__`; query package metadata.
    from importlib.metadata import version

    installed = version("thirsty-lang")
    assert installed == "0.8.1", f"expected 0.8.1, got {installed}"


@pytest.mark.parametrize(
    "entrypoint",
    ["thirsty", "thirst-of-gods", "tscg", "tscg-b", "tarl", "shadow-thirst"],
)
def test_cli_entrypoint_on_path(entrypoint: str) -> None:
    """Each tier's CLI script must be on PATH after `uv sync`."""
    exe = shutil.which(entrypoint)
    assert exe is not None, f"CLI {entrypoint!r} not on PATH; run `uv sync`"


def test_cli_entrypoints_invokable() -> None:
    """Each tier's CLI must respond to --help without erroring out.

    The CLI is resolved from the running venv's Scripts directory, not
    from PATH. This avoids picking up a stale install in a different
    venv (e.g. the Hermes agent venv) that may have the script but not
    the package's dependencies.
    """
    import sys
    from pathlib import Path

    venv_scripts = Path(sys.executable).parent
    for entrypoint in ("thirsty", "tarl"):
        exe: Path | str | None = venv_scripts / (entrypoint + ".exe" if sys.platform == "win32" else entrypoint)
        if not Path(str(exe)).exists():
            exe = shutil.which(entrypoint)
            if exe is None:
                pytest.skip(f"{entrypoint} not on PATH and not in venv")
        result = subprocess.run(
            [str(exe), "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        # --help exits 0; some CLIs exit 1 if they have a bug in arg parsing
        assert result.returncode == 0, f"{entrypoint} --help failed: {result.stderr[:200]}"
        # And produces real help text, not an empty page
        assert "usage" in result.stdout.lower() or "options" in result.stdout.lower(), (
            f"{entrypoint} --help produced no usage text"
        )


def test_no_namespace_collision_with_packages_tarl() -> None:
    """The language installs as `utf.tarl` (dotted namespace), not bare `tarl`.

    Beginnings' own `packages/tarl/` is a workspace package that exports
    the bare `tarl` Python module. Per PHASE_T_DISCOVERY.md §7 risk 2,
    a name collision was the rationale for a proposed Phase T6 rename.
    Verified at discovery time: the language's setuptools config includes
    `utf.*` and `utf`, not `tarl`. So `import tarl` resolves to Beginnings'
    own package, and `import utf.tarl` resolves to the language. This
    test guards against the language's setuptools config changing in a
    future release to expose bare `tarl`.
    """
    import tarl  # Beginnings' own package

    assert tarl.__file__ is not None
    # Beginnings' tarl lives under packages/tarl/src/tarl/
    assert (
        "packages\\tarl" in tarl.__file__.replace("/", "\\") or "packages/tarl" in tarl.__file__
    ), f"bare `tarl` should resolve to Beginnings' package, got {tarl.__file__}"
    # And the language's tarl is the dotted utf.tarl
    utf_tarl = importlib.import_module("utf.tarl")
    assert utf_tarl is not tarl, "utf.tarl and tarl must be distinct modules"
