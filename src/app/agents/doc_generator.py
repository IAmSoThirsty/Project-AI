"""Documentation Generator agent

Generates basic Markdown API documentation for generated modules.
"""

from __future__ import annotations

import importlib.util
import inspect
import logging
import os
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class DocGenerator(KernelRoutedAgent):
    def __init__(self, data_dir: str = "data", kernel: CognitionKernel | None = None) -> None:
        # Initialize kernel routing (COGNITION KERNEL INTEGRATION)
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",
        )
        self.data_dir = data_dir
        self.docs_dir = os.path.join(self.data_dir, "docs")
        os.makedirs(self.docs_dir, exist_ok=True)

    def generate_for_module(self, module_path: str) -> dict[str, Any]:
        # Route through kernel (COGNITION KERNEL ROUTING)
        return self._execute_through_kernel(
            self._do_generate_for_module,
            module_path,
            operation_name="generate_documentation",
            risk_level="low",
            metadata={"module_path": module_path},
        )

    def _do_generate_for_module(self, module_path: str) -> dict[str, Any]:
        """Internal implementation of documentation generation."""
        base = os.path.basename(module_path)
        modname = os.path.splitext(base)[0]
        out_path = os.path.join(self.docs_dir, f"{modname}.md")
        try:
            spec = importlib.util.spec_from_file_location(modname, module_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            lines = [f"# Module {modname}", ""]
            for name, obj in inspect.getmembers(mod):
                if inspect.isfunction(obj) or inspect.isclass(obj):
                    doc = inspect.getdoc(obj) or ""
                    lines.append(f"## {name}")
                    lines.append(doc)
                    lines.append("")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return {"success": True, "out": out_path}
        except Exception as e:
            logger.exception("Doc generation failed for %s: %s", module_path, e)
            return {"success": False, "error": str(e)}
