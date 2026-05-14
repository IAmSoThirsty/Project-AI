"""
Waterfall Filter — inbound request filter (Thirstys-waterfall integration point).

Sits at the outermost edge of the execution pipeline, before the invariant
engine and the governance gate.  Every request that enters the system passes
through here first.

Thirstys-waterfall is vendored into Project-AI as ``thirstys_waterfall`` and is
loaded by default. If it cannot be imported, a safe passthrough filter is used
so the rest of the pipeline continues to work.

Waterfall contract
------------------
A waterfall module must expose:

    def filter(context: dict) -> WaterfallResult

Where WaterfallResult is (or duck-types to):

    @dataclass
    class WaterfallResult:
        allowed: bool
        context: dict          # possibly enriched/normalised context
        reason: str | None

The module is resolved via the WATERFALL_MODULE env-var, falling back to
"thirstys_waterfall.project_ai_filter".
"""

from __future__ import annotations

import importlib
import logging
import os
import threading
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

_WATERFALL_MODULE_ENV = "WATERFALL_MODULE"
_WATERFALL_DEFAULT = "thirstys_waterfall.project_ai_filter"


@dataclass
class WaterfallResult:
    allowed: bool
    context: dict[str, Any]
    reason: str | None = None


class WaterfallFilter:
    """
    Inbound request filter backed by Thirstys-waterfall (or built-in stub).

    Thread-safe singleton via get_waterfall_filter().
    """

    def __init__(self) -> None:
        self._filter_fn = self._load_filter_fn()

    def _load_filter_fn(self):
        module_path = os.environ.get(_WATERFALL_MODULE_ENV, _WATERFALL_DEFAULT)
        try:
            mod = importlib.import_module(module_path)
            fn = mod.filter
            logger.info("WaterfallFilter: loaded from %s", module_path)
            return fn
        except (ImportError, AttributeError):
            logger.warning(
                "WaterfallFilter: could not load %s; using passthrough",
                module_path,
            )
            return _passthrough

    def filter(self, context: dict[str, Any]) -> WaterfallResult:
        """
        Run the inbound filter.

        Returns WaterfallResult.  If allowed=False the caller MUST NOT
        proceed to the invariant engine or governance gate.
        """
        try:
            result = self._filter_fn(context)
            if isinstance(result, WaterfallResult):
                return result
            if hasattr(result, "allowed") and hasattr(result, "context"):
                return WaterfallResult(
                    allowed=bool(result.allowed),
                    context=dict(result.context),
                    reason=getattr(result, "reason", None),
                )
            # Duck-typing: assume dict-like
            return WaterfallResult(
                allowed=bool(result.get("allowed", True)),
                context=result.get("context", context),
                reason=result.get("reason"),
            )
        except Exception as exc:
            logger.error("WaterfallFilter.filter raised: %s — allowing through", exc)
            return WaterfallResult(allowed=True, context=context)


def _passthrough(context: dict[str, Any]) -> WaterfallResult:
    """Built-in passthrough — allows everything, returns context unchanged."""
    return WaterfallResult(allowed=True, context=context)


# ─────────────────────────────────────────────
# Singleton
# ─────────────────────────────────────────────

_filter_instance: WaterfallFilter | None = None
_filter_lock = threading.Lock()


def get_waterfall_filter() -> WaterfallFilter:
    """Get the singleton WaterfallFilter instance."""
    global _filter_instance
    with _filter_lock:
        if _filter_instance is None:
            _filter_instance = WaterfallFilter()
        return _filter_instance


__all__ = ["WaterfallFilter", "WaterfallResult", "get_waterfall_filter"]
