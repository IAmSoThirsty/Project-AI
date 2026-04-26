"""Compatibility exports for ``app.cli`` package imports.

Historically this repository had both:
- ``src/app/cli.py`` (Typer application with command groups), and
- ``src/app/cli/`` (package directory for HYDRA-50 CLI components).

Python resolves ``import app.cli`` to the package directory, which made
``from app.cli import app`` fail in consumers expecting the Typer app defined
in ``src/app/cli.py``.

This shim bridges the two layouts by loading ``src/app/cli.py`` explicitly and
re-exporting ``app`` and ``__version__``.
"""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType


def _load_main_cli_module() -> ModuleType:
	"""Load the historical ``src/app/cli.py`` module for compatibility."""
	cli_module_path = Path(__file__).resolve().parent.parent / "cli.py"
	spec = spec_from_file_location("app._main_cli", cli_module_path)
	if spec is None or spec.loader is None:
		raise ImportError(f"Unable to load CLI module from {cli_module_path}")

	module = module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


_main_cli = _load_main_cli_module()

app = _main_cli.app
__version__ = getattr(_main_cli, "__version__", "1.0.0")

__all__ = ["app", "__version__"]
