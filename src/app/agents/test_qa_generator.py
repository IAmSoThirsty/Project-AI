"""Test & QA Generator agent

Generates basic pytest stubs for generated modules and runs pytest to validate.
Conservative: it only creates simple asserts reflecting generated function signatures.
"""

from __future__ import annotations

import logging
import os
import subprocess
import time
from typing import Any

logger = logging.getLogger(__name__)


class TestQAGenerator:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir
        self._last_test_dir: str | None = None

    def generate_test_for_module(self, module_path: str) -> dict[str, Any]:
        # Create a unique subdirectory for this generation to avoid colliding with other test artifacts
        base = os.path.basename(module_path)
        modname = os.path.splitext(base)[0]
        base_tests_dir = os.path.join(self.data_dir, "generated_tests")
        run_dir = os.path.join(base_tests_dir, f"run_{int(time.time() * 1000)}")
        os.makedirs(run_dir, exist_ok=True)
        test_path = os.path.join(run_dir, f"test_{modname}.py")
        try:
            with open(module_path, encoding="utf-8") as f:
                src = f.read()
            funcs = [
                line.split("def ")[1].split("(")[0]
                for line in src.splitlines()
                if line.strip().startswith("def ")
            ]
            # Build a test that imports the module and calls functions that accept no required args
            lines = [
                "import importlib.util",
                "import sys",
                "import inspect",
                f"spec = importlib.util.spec_from_file_location('{modname}', r'{module_path}')",
                "mod = importlib.util.module_from_spec(spec)",
                "spec.loader.exec_module(mod)",
            ]
            for fn in funcs:
                # Add assertion the function exists
                lines.append(f"assert hasattr(mod, '{fn}')")
                # Add a guarded call: only call functions that take zero required parameters
                lines.append(f"_fn = getattr(mod, '{fn}')")
                lines.append("try:")
                lines.append("    sig = inspect.signature(_fn)")
                lines.append("    # count required params (no defaults)")
                lines.append(
                    "    req = [p for p in sig.parameters.values() if p.default is inspect._empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]"
                )
                lines.append("    if len(req) == 0:")
                lines.append(
                    "        # call the function and assert it does not raise and returns a truthy value"
                )
                lines.append("        res = _fn()")
                lines.append("        assert res or res is None or res == True")
                lines.append("except Exception:")
                lines.append("    raise")

            with open(test_path, "w", encoding="utf-8") as tf:
                tf.write("\n".join(lines) + "\n")

            # remember test dir for run_tests to execute
            self._last_test_dir = run_dir
            return {"success": True, "test_path": test_path, "test_dir": run_dir}
        except Exception as e:
            logger.exception("Failed to generate test for %s: %s", module_path, e)
            return {"success": False, "error": str(e)}

    def run_tests(self, tests_dir: str | None = None) -> dict[str, Any]:
        # Prefer running only the latest generated test directory to avoid unrelated tests
        run_dir = (
            tests_dir
            or self._last_test_dir
            or os.path.join(self.data_dir, "generated_tests")
        )
        if not os.path.exists(run_dir):
            return {"success": True, "ran": 0}
        try:
            res = subprocess.run(
                ["pytest", run_dir, "-q"], capture_output=True, text=True
            )
            return {
                "success": res.returncode == 0,
                "output": res.stdout + res.stderr,
                "returncode": res.returncode,
            }
        except Exception as e:
            logger.exception("Failed to run tests: %s", e)
            return {"success": False, "error": str(e)}
