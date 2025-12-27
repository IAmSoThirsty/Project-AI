from __future__ import annotations

import json
import os
import runpy
import sys
import traceback
import platform
from pathlib import Path

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
        # 100 MB address space
        resource.setrlimit(resource.RLIMIT_AS, (100 * 1024 * 1024, resource.RLIM_INFINITY))
        # 2 seconds CPU time
        resource.setrlimit(resource.RLIMIT_CPU, (2, 4))
        # limit file descriptors
        resource.setrlimit(resource.RLIMIT_NOFILE, (16, 64))
    except Exception:
        pass


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
