# [API Core Bootstrap]                          [2026-04-03 19:18]
#                                          Productivity: Active
"""Canonical bootstrap helpers for the Project-AI API and headless runtime."""

from __future__ import annotations

import logging
import os
import sys
import threading
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.block_pyqt6 import ensure_pyqt6_available

logger = logging.getLogger(__name__)

_STATE_LOCK = threading.RLock()
_API_STATE: dict[str, Any] | None = None


def _configure_logging() -> None:
    """Attach a dedicated API file log if one is not already present."""

    logs_dir = ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    target_path = str(logs_dir / "api.log")
    root_logger = logging.getLogger()

    for handler in root_logger.handlers:
        if isinstance(handler, logging.FileHandler) and getattr(
            handler, "baseFilename", None
        ) == target_path:
            break
    else:
        handler = logging.FileHandler(target_path, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        root_logger.addHandler(handler)

    if root_logger.level == logging.NOTSET:
        root_logger.setLevel(logging.INFO)


@lru_cache(maxsize=1)
def _main_module():
    """Import `src.app.main` after ensuring Qt bindings are importable."""

    ensure_pyqt6_available()
    from src.app import main as main_module

    return main_module


def check_dependencies() -> dict[str, Any]:
    """Delegate dependency checks to the canonical main module."""

    return _main_module().check_dependencies()


def get_identity_engine() -> Any:
    """Return the global identity engine."""

    return _main_module().get_identity_engine()


def get_cognition_kernel() -> Any:
    """Return the singleton cognition kernel."""

    return _main_module().get_cognition_kernel()


def initialize_kernel() -> Any:
    """Initialize the sovereign kernel through the canonical startup path."""

    return _main_module().initialize_kernel()


def initialize_council_hub(kernel: Any) -> Any:
    """Initialize the council hub with the provided kernel."""

    return _main_module().initialize_council_hub(kernel)


def initialize_security_systems(kernel: Any, council_hub: Any) -> dict[str, Any]:
    """Initialize the security subsystem bundle."""

    return _main_module().initialize_security_systems(kernel, council_hub)


def initialize_enhanced_defenses(
    kernel: Any, security_systems: dict[str, Any]
) -> dict[str, Any]:
    """Initialize the enhanced defensive layer."""

    return _main_module().initialize_enhanced_defenses(kernel, security_systems)


def initialize_tier_registry() -> Any:
    """Initialize the tier registry singleton."""

    return _main_module().initialize_tier_registry()


def report_tier_health() -> Any:
    """Collect the current platform health summary."""

    return _main_module().report_tier_health()


def initialize_api_core(headless: bool = True) -> dict[str, Any]:
    """Bootstrap the runtime used by the API server and headless launcher."""

    global _API_STATE

    with _STATE_LOCK:
        if _API_STATE is not None:
            return _API_STATE

        _configure_logging()

        if headless:
            os.environ.setdefault("HEADLESS_MODE", "1")
            os.environ.setdefault("QT_API", "pyqt6")
            os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

        try:
            main_module = _main_module()
            main_module.setup_environment()
            dependency_status = main_module.check_dependencies()
            tier_registry = main_module.initialize_tier_registry()
            kernel = main_module.initialize_kernel()
            council_hub = main_module.initialize_council_hub(kernel)
            security_components = main_module.initialize_security_systems(
                kernel, council_hub
            )
            enhanced_defenses = main_module.initialize_enhanced_defenses(
                kernel, security_components
            )
            identity_engine = main_module.get_identity_engine()
            try:
                tier_health = main_module.report_tier_health()
            except (AttributeError, RuntimeError) as exc:
                logger.warning("Tier health reporting failed: %s", exc)
                tier_health = {"error": str(exc)}

            _API_STATE = {
                "headless": headless,
                "initialized": True,
                "initialized_at": None,
                "dependency_status": dependency_status,
                "tier_registry": tier_registry,
                "kernel": kernel,
                "council_hub": council_hub,
                "security_components": security_components,
                "enhanced_defenses": enhanced_defenses,
                "identity_engine": identity_engine,
                "tier_health": tier_health,
            }

            logger.info(
                "API core initialized (headless=%s, agents=%d)",
                headless,
                len(getattr(council_hub, "list_agents", lambda: [])()),
            )
            return _API_STATE
        except (ImportError, AttributeError, RuntimeError) as exc:
            logger.critical("API core initialization failed: %s", exc)
            raise
        except Exception:
            logger.exception("Unexpected error during API core initialization")
            raise


def get_api_state(create: bool = True, headless: bool = True) -> dict[str, Any] | None:
    """Return the cached API state, creating it if requested."""

    global _API_STATE

    with _STATE_LOCK:
        if _API_STATE is None and create:
            return initialize_api_core(headless=headless)
        return _API_STATE


def reset_api_state() -> None:
    """Clear cached runtime state. Intended for tests."""

    global _API_STATE

    with _STATE_LOCK:
        _API_STATE = None
        _main_module.cache_clear()


def runtime_summary(
    state: dict[str, Any] | None = None, history_limit: int = 20
) -> dict[str, Any]:
    """Build a JSON-serialisable runtime summary."""

    if state is None:
        state = get_api_state()
    if state is None:
        return {"initialized": False}

    kernel = state.get("kernel")
    council_hub = state.get("council_hub")
    security_components = state.get("security_components", {})
    enhanced_defenses = state.get("enhanced_defenses", {})

    kernel_summary: dict[str, Any] = {}
    if kernel is not None:
        try:
            kernel_summary["statistics"] = kernel.get_statistics()
        except Exception as exc:
            kernel_summary["statistics"] = {"error": str(exc)}
        try:
            kernel_summary["recent_executions"] = kernel.get_execution_history(
                limit=history_limit
            )
        except (AttributeError, RuntimeError, ValueError) as exc:
            kernel_summary["recent_executions"] = {"error": str(exc)}
    else:
        kernel_summary["statistics"] = None
        kernel_summary["recent_executions"] = []

    agents: list[str] = []
    if council_hub is not None:
        try:
            agents = list(council_hub.list_agents())
        except Exception as exc:
            kernel_summary.setdefault("council_hub_error", str(exc))

    security_summary = {
        name: {
            "available": component is not None,
            "type": type(component).__name__ if component is not None else None,
        }
        for name, component in security_components.items()
    }
    enhanced_summary = {
        name: {
            "available": component is not None,
            "type": type(component).__name__ if component is not None else None,
        }
        for name, component in enhanced_defenses.items()
    }

    return {
        "initialized": bool(state.get("initialized", False)),
        "headless": state.get("headless", True),
        "initialized_at": state.get("initialized_at"),
        "dependency_status": state.get("dependency_status", {}),
        "tier_health": state.get("tier_health"),
        "identity_engine": type(state.get("identity_engine")).__name__
        if state.get("identity_engine") is not None
        else None,
        "kernel": kernel_summary,
        "council_hub": {
            "agent_count": len(agents),
            "agents": agents,
        },
        "security": {
            "available_count": sum(
                1 for component in security_components.values() if component is not None
            ),
            "total_count": len(security_components),
            "components": security_summary,
        },
        "enhanced_defenses": {
            "available_count": sum(
                1 for component in enhanced_defenses.values() if component is not None
            ),
            "total_count": len(enhanced_defenses),
            "components": enhanced_summary,
        },
    }


__all__ = [
    "check_dependencies",
    "get_api_state",
    "get_cognition_kernel",
    "get_identity_engine",
    "initialize_api_core",
    "initialize_council_hub",
    "initialize_enhanced_defenses",
    "initialize_kernel",
    "initialize_security_systems",
    "initialize_tier_registry",
    "report_tier_health",
    "reset_api_state",
    "runtime_summary",
]
