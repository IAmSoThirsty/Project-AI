from __future__ import annotations

import json
import logging
import os
import platform
import runpy
import sys
import traceback

# Optional resource limits (POSIX)
try:
    import resource
except Exception:
    resource = None


def apply_limits():
    """Apply conservative resource limits when available (POSIX only)."""
    if resource is None or platform.system() == "Windows":
        return
    try:
        setrlimit = getattr(resource, "setrlimit", None)
        rlimit_as = getattr(resource, "RLIMIT_AS", None)
        rlim_infty = getattr(resource, "RLIM_INFINITY", None)
        rlimit_cpu = getattr(resource, "RLIMIT_CPU", None)
        rlimit_nofile = getattr(resource, "RLIMIT_NOFILE", None)

        if callable(setrlimit) and rlimit_as is not None and rlim_infty is not None:
            setrlimit(rlimit_as, (100 * 1024 * 1024, rlim_infty))
        if callable(setrlimit) and rlimit_cpu is not None:
            setrlimit(rlimit_cpu, (2, 4))
        if callable(setrlimit) and rlimit_nofile is not None:
            setrlimit(rlimit_nofile, (16, 64))
    except Exception as e:
        # Log resource limit application failure but continue
        # Resource limits are best-effort and may not be available on all platforms
        logger = logging.getLogger(__name__)
        logger.debug("Failed to apply resource limits: %s", e)


def run_module(module_path: str) -> dict:
    """Execute the module at module_path in a constrained environment and return a report dict.

    Designed to be safe to call inside a separate process (via ProcessPoolExecutor).
    """
    out = {"module": module_path, "stdout": "", "stderr": "", "exception": None}
    try:
        apply_limits()
        # change working dir to module dir
        mod_dir = os.path.dirname(os.path.abspath(module_path))
        if mod_dir:
            os.chdir(mod_dir)
        # Execute the module in isolated run_path
        runpy.run_path(module_path, run_name="__main__")
    except SystemExit as se:
        out["stderr"] = f"SystemExit: {se}"
        out["exit_code"] = getattr(se, "code", None)
    except Exception:
        out["exception"] = traceback.format_exc()
    return out


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "missing module path"}))
        sys.exit(2)
    module_path = sys.argv[1]
    report = run_module(module_path)
    print(json.dumps(report))


if __name__ == "__main__":
    main()
