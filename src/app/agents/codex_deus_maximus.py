"""Codex Deus Maximus - Schematic Guardian.
Repurposed to solely focus on repository integrity, structure validation, and auto-correction.
"""

from __future__ import annotations

import ast
import hashlib
import json
import logging
import os
import shutil
import types
from datetime import UTC, datetime
from typing import Any

# Lazy imports for GPT‑OSS 1208 are performed inside _load_gpt_oss_model()
from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

# --- CONFIGURATION ---
logger = logging.getLogger("SchematicGuardian")
logging.basicConfig(level=logging.INFO)

# Define the "Schematic" (Required Structure)
REQUIRED_DIRS = [
    ".github/workflows",
    "src",
]


class CodexDeusMaximus(KernelRoutedAgent):
    """Schematic Guardian AI that enforces repository structure and code standards."""

    def __init__(
        self,
        data_dir: str = "data",
        kernel: CognitionKernel | None = None,
        allow_integration: bool = False,
    ) -> None:
        # Initialize kernel routing (COGNITION KERNEL INTEGRATION)
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium",
        )
        self.data_dir = data_dir
        self.audit_path = os.path.join(self.data_dir, "schematic_audit.json")
        self.allow_integration = allow_integration
        self.generated_dir = os.path.join(self.data_dir, "generated")
        self.staging_dir = os.path.join(self.data_dir, "staged")
        # Ensure legacy method binding for compatibility
        try:
            self.auto_fix_file = types.MethodType(self.__class__.auto_fix_file, self)
        except Exception as e:
            # Log binding failure for debugging but continue initialization
            logger.warning("Failed to bind auto_fix_file method: %s", e)
        # Initialize GPT-OSS 1208 model placeholder (lazy load)
        self._gpt_model = None
        self._gpt_tokenizer = None
        self._gpt_torch = None

    def initialize(self) -> bool:
        logger.info("Schematic Guardian initialized. Mode: STRICT ENFORCEMENT.")
        return True

    def _audit(self, action: str, details: dict[str, Any]) -> None:
        """Log actions to the audit trail."""
        try:
            os.makedirs(os.path.dirname(self.audit_path), exist_ok=True)
            entry = {
                "ts": datetime.now(UTC).isoformat(),
                "action": action,
                "details": details,
            }
            with open(self.audit_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            logger.error("Failed to write audit entry.")

    def run_schematic_enforcement(self, root: str | None = None) -> dict[str, Any]:
        """The Main Routine: Validates structure and fixes files."""
        # Route through kernel (COGNITION KERNEL ROUTING)
        logger.debug("Calling _execute_through_kernel for run_schematic_enforcement")
        return self._execute_through_kernel(
            self._do_run_schematic_enforcement,
            action_args=(root,),
        )

    def _do_run_schematic_enforcement(self, root: str | None = None) -> dict[str, Any]:
        """Internal implementation of schematic enforcement."""
        root = root or os.getcwd()
        report = {
            "structure_check": self._validate_structure(root),
            "fixes": [],
            "errors": [],
        }

        logger.info("Enforcing schematics on %s...", root)

        # Walk the repo to fix code files
        for dirpath, _, filenames in os.walk(root):
            # Ignore hidden/system folders
            if any(
                part.startswith(".")
                or part in ("venv", "env", "__pycache__", "build", "dist")
                for part in dirpath.split(os.sep)
            ):
                continue

            for fn in filenames:
                path = os.path.join(dirpath, fn)

                # Enforce formatting on specific types
                if fn.endswith((".py", ".md", ".json", ".yml", ".yaml")):
                    res = self.auto_fix_file(path)
                    if res.get("success") and res.get("action") == "fixed":
                        report["fixes"].append(
                            {"path": path, "backup": res.get("backup")}
                        )
                    elif not res.get("success"):
                        report["errors"].append(
                            {"path": path, "error": res.get("error")}
                        )

        self._audit("enforcement_run", report)
        return report

    def _validate_structure(self, root: str) -> dict[str, Any]:
        """Ensure the repository adheres to the required folder schematic."""
        missing = []
        for d in REQUIRED_DIRS:
            if not os.path.exists(os.path.join(root, d)):
                missing.append(d)

        status = "HEALTHY" if not missing else "BROKEN"
        if missing:
            logger.warning("Schematic Violation: Missing directories %s", missing)

        return {"status": status, "missing_directories": missing}

    def auto_fix_file(self, path: str) -> dict[str, Any]:
        """Strictly enforces formatting standards (Tabs->Spaces, EOF Newline, Syntax Check)."""
        # Route through kernel (COGNITION KERNEL ROUTING)
        logger.debug("Calling _execute_through_kernel for auto_fix_file")
        return self._execute_through_kernel(
            self._do_auto_fix_file,
            action_args=(path,),
        )

    def _do_auto_fix_file(self, path: str) -> dict[str, Any]:
        """Internal implementation of auto fix."""
        if not os.path.exists(path):
            return {"success": False, "error": "missing"}

        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            orig = content
            fixed = content

            # --- RULE 1: Python Specifics ---
            if path.endswith(".py"):
                fixed = fixed.replace("\t", "    ")  # No tabs
                fixed = "\n".join(
                    line.rstrip() for line in fixed.splitlines()
                )  # No trailing whitespace

                # Safety: Check syntax before accepting
                try:
                    ast.parse(fixed)
                except SyntaxError as e:
                    return {"success": False, "error": f"syntax_error: {str(e)}"}

            # --- RULE 2: General Text Files (.md, .yml, .yaml, .json) ---
            elif path.endswith((".md", ".yml", ".yaml", ".json")):
                fixed = fixed.replace("\r\n", "\n").replace("\r", "\n")  # UNIX endings

            # --- RULE 3: End of File Newline ---
            if fixed and not fixed.endswith("\n"):
                fixed += "\n"

            # Apply Changes
            if fixed != orig:
                bak = path + ".bak"
                shutil.copyfile(path, bak)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(fixed)
                return {"success": True, "action": "fixed", "backup": bak}

            return {"success": True, "action": "noop"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def implement_request(
        self, request_id: str, topic: str, description: str
    ) -> dict[str, Any]:
        """Create a generated implementation artifact without integrating it."""
        os.makedirs(self.generated_dir, exist_ok=True)
        module_name = self._safe_module_name(topic)
        path = os.path.join(self.generated_dir, f"{module_name}.py")
        content = (
            f'"""Generated implementation for {topic}."""\n\n'
            f"def {module_name}():\n"
            f"    return {description!r}\n"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        result = {"success": True, "request_id": request_id, "path": path}
        self._audit("implementation_created", result)
        return result

    def integrate_across_project(
        self, target_modules: list[str] | None = None
    ) -> dict[str, Any]:
        """Legacy integration entry point; blocked unless explicitly enabled."""
        if not self.allow_integration:
            return {"success": False, "error": "integration_not_allowed"}
        return self.integrate_approved(target_modules=target_modules)

    def integrate_approved(
        self, target_modules: list[str] | None = None
    ) -> dict[str, Any]:
        """Append imports for generated artifacts to approved target modules."""
        if not self.allow_integration:
            return {"success": False, "error": "integration_not_allowed"}

        integrated = []
        errors = []
        target_modules = target_modules or []
        generated_modules = self._generated_module_names()

        for target in target_modules:
            if not os.path.exists(target):
                errors.append({"target": target, "error": "missing"})
                continue

            backup = target + ".codexbak"
            shutil.copyfile(target, backup)
            with open(target, encoding="utf-8") as f:
                content = f.read()

            additions = [
                f"from app.generated import {module}"
                for module in generated_modules
                if f"from app.generated import {module}" not in content
            ]
            if additions:
                if content and not content.endswith("\n"):
                    content += "\n"
                content += "\n".join(additions) + "\n"
                with open(target, "w", encoding="utf-8") as f:
                    f.write(content)
            integrated.append({"target": target, "backup": backup})

        report = {"success": not errors, "integrated": integrated, "errors": errors}
        self._audit("integration_approved", report)
        return report

    def rollback_integrations(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Restore any recorded integration backups."""
        report = payload.get("report", payload) if isinstance(payload, dict) else {}
        restored = []
        for item in report.get("integrated", []):
            target = item.get("target")
            backup = item.get("backup")
            if target and backup and os.path.exists(backup):
                shutil.copyfile(backup, target)
                restored.append(target)
        result = {"success": True, "restored": restored}
        self._audit("integration_rollback", result)
        return result

    def stage_artifact(
        self, request_id: str, artifact_path: str, topic: str, description: str
    ) -> dict[str, Any]:
        """Copy a generated artifact into the staging area for later activation."""
        if not os.path.exists(artifact_path):
            return {"success": False, "error": "missing_artifact"}
        os.makedirs(self.staging_dir, exist_ok=True)
        staged = os.path.join(self.staging_dir, os.path.basename(artifact_path))
        shutil.copyfile(artifact_path, staged)
        metadata = {
            "request_id": request_id,
            "topic": topic,
            "description": description,
            "artifact": staged,
        }
        with open(staged + ".json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        result = {"success": True, "staged": staged}
        self._audit("artifact_staged", result)
        return result

    def activate_staged(self, staged_path: str, requester: str = "system") -> dict[str, Any]:
        """Activate a staged artifact only for users with the integrator role."""
        from app.core.access_control import get_access_control

        if not get_access_control().has_role(requester, "integrator"):
            return {"success": False, "error": "integrator_role_required"}
        if not os.path.exists(staged_path):
            return {"success": False, "error": "missing_staged_artifact"}
        os.makedirs(self.generated_dir, exist_ok=True)
        active_path = os.path.join(self.generated_dir, os.path.basename(staged_path))
        shutil.copyfile(staged_path, active_path)
        result = {"success": True, "activated": active_path}
        self._audit("artifact_activated", result)
        return result

    def export_audit(self, requester: str = "system") -> dict[str, Any]:
        """Export the audit log with a SHA-256 sidecar signature."""
        from app.core.access_control import get_access_control

        access = get_access_control()
        if not (access.has_role(requester, "expert") or access.has_role(requester, "integrator")):
            return {"success": False, "error": "insufficient_role"}
        if not os.path.exists(self.audit_path):
            return {"success": False, "error": "missing_audit"}

        out = os.path.join(self.data_dir, "codex_audit_export.json")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        shutil.copyfile(self.audit_path, out)
        with open(out, "rb") as f:
            signature = hashlib.sha256(f.read()).hexdigest()
        signature_path = out + ".sha256"
        with open(signature_path, "w", encoding="utf-8") as f:
            f.write(signature + "\n")
        return {
            "success": True,
            "out": out,
            "signature": signature,
            "signature_path": signature_path,
        }

    def _generated_module_names(self) -> list[str]:
        if not os.path.isdir(self.generated_dir):
            return []
        return [
            os.path.splitext(name)[0]
            for name in sorted(os.listdir(self.generated_dir))
            if name.endswith(".py") and not name.startswith("_")
        ]

    @staticmethod
    def _safe_module_name(value: str) -> str:
        module = "".join(ch if ch.isalnum() else "_" for ch in value.lower()).strip("_")
        return module or "generated_impl"

    # ---------------------------------------------------------------------
    # GPT-OSS 1208 integration
    # ---------------------------------------------------------------------
    def _load_gpt_oss_model(self) -> None:
        """Lazy‑load the GPT‑OSS 1208 model and tokenizer.

        The heavy `torch` and `transformers` imports are performed **inside**
        this method so that the rest of the agent can be used without pulling
        in those large libraries. If the import or download fails we fall
        back to a dummy response.
        """
        if self._gpt_model is None or self._gpt_tokenizer is None:
            try:
                # Local imports – they only happen when we actually need the model
                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer

                logger.info("Loading GPT‑OSS 1208 model…")
                model_name = "gpt-oss-120b"
                self._gpt_tokenizer = AutoTokenizer.from_pretrained(
                    model_name, trust_remote_code=True
                )
                self._gpt_model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    device_map="auto",
                    torch_dtype=torch.float16,
                    trust_remote_code=True,
                )
                self._gpt_model.eval()
                self._gpt_torch = torch
                logger.info("GPT‑OSS 1208 model loaded successfully.")
            except Exception as e:
                logger.warning(
                    "Failed to load GPT‑OSS 1208 model (%s). Falling back to dummy response.",
                    e,
                )
                self._gpt_model = None
                self._gpt_tokenizer = None
                self._gpt_torch = None

    def generate_gpt_oss(self, prompt: str, max_new_tokens: int = 512) -> str:
        """Generate a response from GPT‑OSS 1208.

        Parameters
        ----------
        prompt: str
            The user prompt or system instruction.
        max_new_tokens: int, optional
            Maximum number of tokens to generate (default 512).
        """
        self._load_gpt_oss_model()
        # If loading failed, return a simple placeholder response.
        if self._gpt_model is None or self._gpt_tokenizer is None:
            logger.info("Returning dummy GPT‑OSS response (model not loaded).")
            return f"[Dummy GPT‑OSS response] {prompt}"
        torch = self._gpt_torch
        if torch is None:
            logger.info("Returning dummy GPT‑OSS response (torch runtime not loaded).")
            return f"[Dummy GPT‑OSS response] {prompt}"
        inputs = self._gpt_tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to(self._gpt_model.device) for k, v in inputs.items()}
        with torch.no_grad():
            output = self._gpt_model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self._gpt_tokenizer.eos_token_id,
            )
        response = self._gpt_tokenizer.decode(output[0], skip_special_tokens=True)
        # Remove the original prompt from the output
        if response.startswith(prompt):
            response = response[len(prompt) :]
        return response.strip()


# Factory
def create_codex(
    data_dir: str = "data", allow_integration: bool = False
) -> CodexDeusMaximus:
    c = CodexDeusMaximus(data_dir=data_dir, allow_integration=allow_integration)
    c.initialize()
    return c
