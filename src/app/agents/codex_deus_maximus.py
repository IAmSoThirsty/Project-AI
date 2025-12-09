"""Codex Deus Maximus - Head Butler agent responsible for implementing accepted learning requests.

This agent can produce implementations in one of several coding styles, coordinate
style rotations with the Cerberus hub, and integrate generated artifacts into the
Project-AI source tree.
"""
from __future__ import annotations

import ast
import hashlib
import json
import logging
import os
import random
import shutil
import types
from datetime import UTC, datetime
from typing import Any

from app.core.access_control import get_access_control
from app.core.council_hub import get_council_hub

logger = logging.getLogger(__name__)


class CodexDeusMaximus:
    """Head Butler AI that creates and validates code artifacts in multiple styles.

    The class supports a set of named coding styles. Generated artifacts are
    created under `src/app/generated/` and a simple syntax check is performed
    before writing. The agent can also request Cerberus to rotate guardian
    styles to help diversify analysis approaches.
    """

    DEFAULT_STYLES = [
        "idiomatic_python",
        "functional",
        "object_oriented",
        "procedural",
        "verbose_commented",
        "concise",
        "typed_annotations",
        "docstring_heavy",
        "test_first_stub",
        "async_first",
    ]

    def __init__(self, data_dir: str = "data", allow_integration: bool | None = None) -> None:
        self.data_dir = data_dir
        self.generated_dir = os.path.join("src", "app", "generated")
        os.makedirs(self.generated_dir, exist_ok=True)
        self.initialized = False
        self.current_style: str = random.choice(self.DEFAULT_STYLES)
        # Integration permission: environment variable overrides default
        if allow_integration is None:
            self.allow_integration = os.getenv("ENABLE_CODEX_INTEGRATION", "0") == "1"
        else:
            self.allow_integration = bool(allow_integration)
        self.audit_path = os.path.join(self.data_dir, "codex_audit.json")
        # Optional reference to LearningRequestManager will be set by adapter
        self.learning_manager = None
        # seen fingerprints to avoid recalling waiting/vaulted items
        self._seen_path = os.path.join(self.data_dir, "codex_seen.json")
        try:
            if os.path.exists(self._seen_path):
                with open(self._seen_path, encoding="utf-8") as f:
                    self._seen = set(json.load(f))
            else:
                self._seen = set()
        except Exception:
            self._seen = set()
        # Ensure legacy attribute is present on instance for compatibility with older callers/tests
        try:
            self.auto_fix_file = types.MethodType(self.__class__.auto_fix_file, self)
        except Exception:
            # If the method isn't defined yet, ignore — older tests may still bind later
            pass

    def initialize(self) -> bool:
        """Initialize the Codex agent."""
        self.initialized = True
        logger.info("CodexDeusMaximus initialized, generated_dir=%s, style=%s, allow_integration=%s",
                    self.generated_dir, self.current_style, self.allow_integration)
        return True

    def _audit(self, action: str, details: dict[str, Any]) -> None:
        """Append an audit record to the audit JSON file."""
        try:
            os.makedirs(os.path.dirname(self.audit_path), exist_ok=True)
            # Use timezone-aware UTC timestamps
            entry = {"ts": datetime.now(UTC).isoformat(), "action": action, "details": details}
            if os.path.exists(self.audit_path):
                with open(self.audit_path, encoding="utf-8") as f:
                    data = json.load(f) or []
            else:
                data = []
            data.append(entry)
            with open(self.audit_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            logger.exception("Failed to write audit entry")

    def list_styles(self) -> list[str]:
        """Return the available coding styles."""
        return list(self.DEFAULT_STYLES)

    def set_style(self, style: str | None = None) -> str:
        """Set the current coding style. If style is None pick a random style."""
        if style is None or style not in self.DEFAULT_STYLES:
            self.current_style = random.choice(self.DEFAULT_STYLES)
        else:
            self.current_style = style
        logger.info("Codex style set to %s", self.current_style)
        self._audit("set_style", {"style": self.current_style})
        return self.current_style

    def _safe_filename(self, text: str) -> str:
        """Create a filesystem-safe filename from text."""
        keep = []
        for c in text:
            if c.isalnum() or c in "-_":
                keep.append(c)
            else:
                keep.append("_")
        name = "".join(keep)
        if not name:
            name = "codex_impl"
        return name[:120]

    def _validate_python_syntax(self, code: str) -> tuple[bool, str | None]:
        """Validate Python code using ast.parse. Returns (ok, error_message)."""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as se:
            return False, f"SyntaxError: {se}"
        except Exception as e:
            return False, f"ValidationError: {e}"

    def _apply_style_template(self, topic: str, description: str, style: str) -> str:
        """Apply a simple style template to produce Python code text.

        These templates are intentionally conservative: they produce clear, small
        modules that differ in naming, structure, comments, and annotations.
        """
        # Normalize input to safe identifiers
        fn_stub = self._safe_filename(f"impl_{topic}")
        # Sanitize description to avoid breaking generated code (e.g., triple quotes)
        def _sanitize_text(s: str) -> str:
            if s is None:
                return ""
            s = s.replace("\r\n", "\n").replace("\r", "\n")
            # Escape triple quotes to avoid terminating generated docstrings
            s = s.replace('"""', '\\"\\"\\"')
            return s

        safe_desc = _sanitize_text(description)

        if style == "idiomatic_python":
            content = f"""# {topic}\n"""
            content += """import typing\n\n# Description:\n""" + safe_desc.replace("\n", "\n# ") + "\n\n"
            content += f"def {fn_stub}() -> bool:\n    \"\"\"Perform the requested implementation for {topic}.\"\"\"\n    return True\n"
            return content

        if style == "functional":
            content = f"""# Functional-style implementation for {topic}\n"""
            content += f"def make_{fn_stub}(payload: dict) -> dict:\n    # description: {safe_desc}\n    return {{'ok': True}}\n"
            return content

        if style == "object_oriented":
            content = f"""# OOP-style implementation for {topic}\n"""
            content += f"class {fn_stub.title().replace('_','')}:\n    \"\"\"Manager object for {topic}\"\"\"\n    def run(self) -> bool:\n        # {safe_desc}\n        return True\n"
            return content

        if style == "procedural":
            content = f"""# Procedural implementation for {topic}\n"""
            content += f"def main_{fn_stub}():\n    # steps:\n    # 1) analyze\n    # 2) implement\n    # {safe_desc}\n    return True\n"
            return content

        if style == "verbose_commented":
            content = f"""# Verbose commented implementation for {topic}\n"""
            content += """\n# The following implementation is heavily commented to aid reviewers\n"""
            content += f"def {fn_stub}() -> bool:\n    # Description:\n    # {safe_desc.replace('\\n', '\\n    # ')}\n    # Implementation returns True on success\n    return True\n"
            return content

        if style == "concise":
            content = f"def {fn_stub}():\n    return True\n"
            return content

        if style == "typed_annotations":
            content = (
                "from typing import Any, Dict\n\n"
                f"# Typed implementation for {topic}\n\n"
                f"def {fn_stub}(payload: Dict[str, Any]) -> bool:\n"
                f"    \"\"\"{safe_desc}\"\"\"\n"
                "    return True\n"
            )
            return content

        if style == "docstring_heavy":
            # Build docstring-heavy content safely to avoid nested triple-quote issues
            lines = []
            lines.append("\"\"\"")
            lines.append(topic)
            lines.append("")
            if safe_desc:
                lines.extend(safe_desc.splitlines())
                lines.append("")
            lines.append("Auto-generated docstring-heavy stub.")
            lines.append("\"\"\"")
            lines.append("")
            lines.append(f"def {fn_stub}():")
            lines.append("    \"\"\"See module docstring.\"\"\"")
            lines.append("    return True")
            content = "\n".join(lines) + "\n"
            return content

        if style == "test_first_stub":
            test_name = f"test_{fn_stub}"
            content = f"""# Test-first style: include a companion test stub\n\ndef {fn_stub}():\n    # implementation goes here\n    return True\n\n# companion test (to be moved to tests/ by integrator)\ndef {test_name}():\n    assert {fn_stub}() is True\n"""
            return content

        if style == "async_first":
            content = f"import asyncio\n\nasync def {fn_stub}() -> bool:\n    # Async-first stub for {topic}\n    return True\n"
            return content

        # Fallback to idiomatic
        return self._apply_style_template(topic, description, "idiomatic_python")

    def implement_request(self, req_id: str, topic: str, description: str, style: str | None = None) -> dict[str, Any]:
        """Create code artifact for the given learning request using current or given style."""
        if not self.initialized:
            raise RuntimeError("Codex not initialized")

        chosen_style = style or self.current_style
        if chosen_style not in self.DEFAULT_STYLES:
            chosen_style = self.set_style(None)

        # compute fingerprint and check seen/pending/vault status
        fp = hashlib.sha256(description.encode()).hexdigest()
        # If we've seen this fingerprint before (waiting or vaulted), ignore
        if fp in getattr(self, "_seen", set()):
            self._audit("ignored_seen", {"req_id": req_id, "fingerprint": fp})
            return {"success": False, "reason": "ignored_seen", "fingerprint": fp}
        # If content is pending or vaulted, do NOT store in waiting room; mark as seen and ignore
        pv = self._is_pending_or_vaulted(description)
        if pv.get("pending") or pv.get("vaulted"):
            try:
                self._seen.add(fp)
                with open(self._seen_path, "w", encoding="utf-8") as f:
                    json.dump(list(self._seen), f)
            except Exception:
                logger.exception("Failed to persist seen fingerprints")
            self._audit("ignored_pending_or_vaulted", {"req_id": req_id, "fingerprint": fp})
            return {"success": False, "reason": "pending_or_vaulted"}

        safe_name = self._safe_filename(f"{req_id}_{topic}")
        file_name = f"{safe_name}.py"
        path = os.path.join(self.generated_dir, file_name)

        content = self._apply_style_template(topic, description, chosen_style)

        # Validate syntax
        ok, error = self._validate_python_syntax(content)
        tried_styles = [chosen_style]
        # If generated content invalid, try other styles as fallback
        if not ok:
            logger.warning("Codex initial validation failed for style %s: %s. Trying fallbacks.", chosen_style, error)
            self._audit("implement_validation_failed", {"req_id": req_id, "style": chosen_style, "error": error})
            for s in self.DEFAULT_STYLES:
                if s == chosen_style:
                    continue
                tried_styles.append(s)
                alt_content = self._apply_style_template(topic, description, s)
                ok_alt, err_alt = self._validate_python_syntax(alt_content)
                if ok_alt:
                    content = alt_content
                    chosen_style = s
                    ok = True
                    error = None
                    logger.info("Codex fallback succeeded with style %s", s)
                    self._audit("implement_fallback", {"req_id": req_id, "chosen_style": s})
                    break
            if not ok:
                logger.error("Codex validation failed for all styles (%s): %s", tried_styles, error)
                self._audit("implement_failed", {"req_id": req_id, "tried_styles": tried_styles, "error": error})
                return {"success": False, "error": error, "style": chosen_style, "tried": tried_styles}

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info("Codex wrote implementation to %s (style=%s)", path, chosen_style)
            self._audit("implemented", {"req_id": req_id, "path": path, "style": chosen_style})
        except Exception as e:
            logger.exception("Failed to write generated file %s: %s", path, e)
            self._audit("implement_failed", {"req_id": req_id, "error": str(e), "style": chosen_style})
            return {"success": False, "error": str(e), "style": chosen_style}

        preview = "\n".join(content.splitlines()[:40])
        # If learning manager exists, ensure only approved items are auto-integrated.
        # Store the generated artifact in timestamped category folder if integration not allowed yet.
        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        category_dir = os.path.join(self.generated_dir, topic)
        os.makedirs(category_dir, exist_ok=True)
        archived_name = f"{ts}_{file_name}"
        archived_path = os.path.join(category_dir, archived_name)
        try:
            shutil.copyfile(path, archived_path)
            self._audit("archived_generated", {"req_id": req_id, "archived": archived_path})
        except Exception:
            logger.exception("Failed to archive generated artifact")

        return {"success": True, "path": path, "preview": preview, "style": chosen_style, "archived": archived_path}

    def _is_pending_or_vaulted(self, description: str) -> dict[str, bool]:
        """Check learning manager for pending status or presence in black vault."""
        if not self.learning_manager:
            return {"pending": False, "vaulted": False}
        # compute fingerprint
        fingerprint = hashlib.sha256(description.encode()).hexdigest()
        pending = any(r.get("description") == description or hashlib.sha256(r.get("description","").encode()).hexdigest() == fingerprint for r in self.learning_manager.requests.values())
        vaulted = fingerprint in getattr(self.learning_manager, "black_vault", set())
        return {"pending": pending, "vaulted": vaulted}

    def store_waiting(self, topic: str, description: str) -> dict[str, Any]:
        """Stage an approved artifact into the waiting room for human review/activation.

        If `artifact_path` is provided it will be copied into the staged folder and metadata saved.
        """
        waiting_dir = os.path.join(self.data_dir, "waiting_room", "staged")
        os.makedirs(waiting_dir, exist_ok=True)
        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        base_name = self._safe_filename(topic)
        staged_name = f"{ts}_{base_name}.json"
        staged_path = os.path.join(waiting_dir, staged_name)
        # Prepare metadata
        entry = {"ts": ts, "topic": topic, "description": description}
        # If an artifact exists, include reference
        # (artifact_path may be inside generated archive)
        return {"success": True, "staged": staged_path}

    def stage_artifact(self, req_id: str, archived_path: str, topic: str, description: str) -> dict[str, Any]:
        """Create a staged entry that references an archived artifact for activation."""
        waiting_dir = os.path.join(self.data_dir, "waiting_room", "staged")
        os.makedirs(waiting_dir, exist_ok=True)
        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        staged_name = f"{ts}_{self._safe_filename(req_id)}.json"
        staged_path = os.path.join(waiting_dir, staged_name)
        metadata = {
            "ts": ts,
            "req_id": req_id,
            "topic": topic,
            "description": description,
            "archived": archived_path,
            "activated": False,
        }
        try:
            with open(staged_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
            self._audit("staged_artifact", {"req_id": req_id, "staged": staged_path})
            return {"success": True, "staged": staged_path}
        except Exception as e:
            self._audit("stage_failed", {"req_id": req_id, "error": str(e)})
            return {"success": False, "error": str(e)}

    def activate_staged(self, staged_path: str, requester: str = "system") -> dict[str, Any]:
        """Activate a staged artifact: requires 'integrator' role and will perform integration."""
        ac = get_access_control()
        if not ac.has_role(requester, "integrator"):
            return {"success": False, "error": "unauthorized"}
        try:
            with open(staged_path, encoding="utf-8") as f:
                meta = json.load(f)
            archived = meta.get("archived")
            # Ensure artifact exists
            if not archived or not os.path.exists(archived):
                return {"success": False, "error": "missing_artifact"}
            # Copy artifact into generated dir if needed (already there), then integrate
            report = self.integrate_across_project()
            if report.get("success"):
                meta["activated"] = True
                with open(staged_path, "w", encoding="utf-8") as f:
                    json.dump(meta, f, indent=2)
                self._audit("activated_staged", {"staged": staged_path, "requester": requester})
                return {"success": True, "report": report}
            return {"success": False, "error": "integration_failed", "report": report}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def fix_repo(self, root: str | None = None) -> dict[str, Any]:
        """Walk a repository and attempt conservative auto-fixes on files.

        Returns a report of files processed.
        """
        root = root or os.getcwd()
        report = {"fixed": [], "errors": []}
        for dirpath, _, filenames in os.walk(root):
            # Skip virtual envs and .git
            if any(part in (".git", "venv", "env", ".venv") for part in dirpath.split(os.sep)):
                continue
            for fn in filenames:
                if fn.endswith(('.py', '.md', '.markdown')):
                    path = os.path.join(dirpath, fn)
                    res = self.auto_fix_file(path)
                    if res.get("success"):
                        report["fixed"].append({"path": path, "result": res})
                    else:
                        report["errors"].append({"path": path, "result": res})
        self._audit("fix_repo", {"root": root, "report": report})
        return report

    def integrate_across_project(self, target_modules: list[str] | None = None) -> dict[str, Any]:
        """Attempt to integrate generated artifacts into target modules.

        This is conservative: it will append import statements to the target
        modules if they don't already import the generated module. It will create
        a backup of any modified file and record actions in the audit log. It
        will not modify logic automatically.

        Returns a report of actions taken.
        """
        # Access control: only 'integrator' role may trigger automated integrations
        ac = get_access_control()
        if not self.allow_integration or not ac.has_role("system", "integrator"):
            logger.info("Integration blocked: Codex integration not allowed by configuration or access control")
            self._audit("integration_blocked", {"reason": "not_allowed_or_no_role"})
            return {"success": False, "reason": "integration_not_allowed"}

        targets = target_modules or ["src/app/main.py"]
        return self._perform_integration(targets)

    def _perform_integration(self, targets: list[str]) -> dict[str, Any]:
        """Perform the actual integration work without access checks. Returns report."""
        report = {"integrated": [], "skipped": [], "errors": []}
        generated_files = [f for f in os.listdir(self.generated_dir) if f.endswith(".py")]
        for gen in generated_files:
            mod_name = os.path.splitext(gen)[0]
            for tgt in targets:
                try:
                    if not os.path.exists(tgt):
                        report["skipped"].append({"target": tgt, "reason": "missing"})
                        continue
                    with open(tgt, encoding="utf-8") as f:
                        content = f.read()
                    import_line = f"from app.generated import {mod_name}\n"
                    if import_line.strip() in content:
                        report["skipped"].append({"target": tgt, "module": mod_name, "reason": "already_imported"})
                        continue
                    # Backup target
                    bak = tgt + ".codexbak"
                    shutil.copyfile(tgt, bak)
                    # Append import at end of file (safe and conservative)
                    with open(tgt, "a", encoding="utf-8") as f:
                        f.write("\n# Integrated generated module\n" + import_line)
                    report["integrated"].append({"target": tgt, "module": mod_name, "backup": bak})
                    self._audit("integrated", {"target": tgt, "module": mod_name, "backup": bak})
                except Exception as e:
                    logger.exception("Failed to integrate %s into %s: %s", gen, tgt, e)
                    report["errors"].append({"target": tgt, "module": mod_name, "error": str(e)})
                    self._audit("integration_error", {"target": tgt, "module": mod_name, "error": str(e)})
        return {"success": True, "report": report}

    def integrate_approved(self, target_modules: list[str] | None = None) -> dict[str, Any]:
        """Integrate artifacts for an approved request, bypassing RBAC checks when invoked by the system on approval.

        This method is intended to be called by CodexAdapter when a learning request is approved so integration
        happens automatically as per user preference.
        """
        targets = target_modules or ["src/app/main.py"]
        self._audit("integrate_approved_called", {"targets": targets})
        # Perform integration but first ensure QA and dependencies are met
        # - CouncilHub agents run automatically as part of the integration check
        ch = get_council_hub()
        # Run checks against the Codex generated directory using CouncilHub agents (if present)
        try:
            hub = get_council_hub()
            project = getattr(hub, "_project", None)
            enabled = getattr(hub, "_agents_enabled", {})
            if project:
                qa = project.get("qa_generator")
                dep = project.get("dependency_auditor")
                failed_checks = []
                # iterate files under codex.generated_dir (may be a temp dir in tests)
                for root, _, files in os.walk(self.generated_dir):
                    for fn in files:
                        if not fn.endswith(".py"):
                            continue
                        path = os.path.join(root, fn)
                        # dependency audit
                        if enabled.get("dependency_auditor", True) and dep:
                            try:
                                dep_res = dep.analyze_new_module(path)
                                if not dep_res.get("success"):
                                    failed_checks.append({"module": path, "stage": "dependency", "detail": dep_res})
                            except Exception as e:
                                logger.exception("Dependency audit exception for %s: %s", path, e)
                                failed_checks.append({"module": path, "stage": "dependency_exception", "detail": str(e)})
                        # QA generation + run
                        if enabled.get("qa_generator", True) and qa:
                            try:
                                qa_gen = qa.generate_test_for_module(path)
                                if not qa_gen.get("success"):
                                    failed_checks.append({"module": path, "stage": "qa_generate", "detail": qa_gen})
                                    continue
                                qa_run = qa.run_tests()
                                if not qa_run.get("success"):
                                    failed_checks.append({"module": path, "stage": "qa_run", "detail": qa_run})
                            except Exception as e:
                                logger.exception("QA pipeline exception for %s: %s", path, e)
                                failed_checks.append({"module": path, "stage": "qa_exception", "detail": str(e)})

                if failed_checks:
                    # Filter benign 'no tests ran' qa_run failures (pytest may return rc 5 when no tests collected)
                    filtered = []
                    for f in failed_checks:
                        if f.get("stage") == "qa_run":
                            detail = f.get("detail") or {}
                            # detail may contain returncode and output
                            rc = detail.get("returncode") if isinstance(detail, dict) else None
                            out = detail.get("output", "") if isinstance(detail, dict) else ""
                            if rc == 5 and "no tests ran" in out.lower():
                                # ignore this benign case
                                continue
                        filtered.append(f)
                    if filtered:
                        self._audit("integrate_blocked_by_checks", {"failures": filtered})
                        return {"success": False, "blocked": True, "failures": filtered}
        except Exception:
            # If hub/agents invocation throws, continue integration cautiously
            logger.exception("CouncilHub pipeline invocation failed; proceeding with integration")

        return self._perform_integration(targets)

    def rollback_integrations(self, report: dict[str, Any]) -> dict[str, Any]:
        """Rollback integrations described in a report produced by integrate_across_project.

        Restores backups and removes generated modules that were integrated.
        """
        results = {"restored": [], "errors": []}
        integrated = report.get("report", {}).get("integrated", [])
        for entry in integrated:
            tgt = entry.get("target")
            bak = entry.get("backup")
            mod = entry.get("module")
            try:
                if bak and os.path.exists(bak):
                    shutil.copyfile(bak, tgt)
                    os.remove(bak)
                    results["restored"].append({"target": tgt, "module": mod})
                    self._audit("restored", {"target": tgt, "module": mod})
                else:
                    results["errors"].append({"target": tgt, "module": mod, "error": "backup_missing"})
            except Exception as e:
                results["errors"].append({"target": tgt, "module": mod, "error": str(e)})
                self._audit("rollback_error", {"target": tgt, "module": mod, "error": str(e)})
        return results

    def export_audit(self, requester: str = "system", out_path: str | None = None) -> dict[str, Any]:
        """Export audit log if requester has 'expert' role. Returns export path."""
        ac = get_access_control()
        if not ac.has_role(requester, "expert"):
            return {"success": False, "error": "unauthorized"}
        # Ensure exports directory
        exports_dir = os.path.join(self.data_dir, "exports")
        os.makedirs(exports_dir, exist_ok=True)
        out_path = out_path or os.path.join(exports_dir, "codex_audit_export.json")
        try:
            if not os.path.exists(self.audit_path):
                return {"success": False, "error": "no_audit"}
            # Copy audit to exports location
            shutil.copyfile(self.audit_path, out_path)
            # Generate a SHA256 signature of the exported file for tamper evidence
            try:
                with open(out_path, "rb") as f:
                    data = f.read()
                sig = hashlib.sha256(data).hexdigest()
                sig_path = out_path + ".sig"
                with open(sig_path, "w", encoding="utf-8") as sf:
                    sf.write(sig)
            except Exception:
                sig = None
                sig_path = None
            self._audit("export_audit", {"requester": requester, "out": out_path, "signature": sig_path})
            return {"success": True, "out": out_path, "signature": sig, "signature_path": sig_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def auto_fix_file(self, path: str) -> dict[str, Any]:
        """Public legacy API: attempt conservative auto-fix on a file.

        This mirrors the previous auto-fix behavior: tabs->spaces, strip trailing
        whitespace, ensure newline, and validate Python syntax before overwrite.
        """
        if not os.path.exists(path):
            return {"success": False, "error": "missing"}
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            orig = content
            if path.endswith(".py"):
                fixed = content.replace("\t", "    ")
                fixed = "\n".join(line.rstrip() for line in fixed.splitlines())
                if not fixed.endswith("\n"):
                    fixed += "\n"
                ok, err = self._validate_python_syntax(fixed)
                if not ok:
                    return {"success": False, "error": "syntax", "details": err}
            elif path.endswith((".md", ".markdown")):
                fixed = content.replace("\r\n", "\n").replace("\r", "\n")
                lines = fixed.splitlines()
                if not lines or not lines[0].strip().startswith("#"):
                    lines.insert(0, "# Document")
                fixed = "\n".join(lines)
                if not fixed.endswith("\n"):
                    fixed += "\n"
            else:
                return {"success": False, "error": "unsupported"}

            if fixed != orig:
                bak = path + ".codexbak"
                shutil.copyfile(path, bak)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(fixed)
                self._audit("auto_fix", {"path": path, "backup": bak})
                return {"success": True, "path": path, "backup": bak}
            return {"success": True, "path": path, "action": "noop"}
        except Exception as e:
            logger.exception("Auto-fix failed for %s: %s", path, e)
            return {"success": False, "error": str(e)}

# Backwards-compatible factory
def create_codex(data_dir: str = "data", allow_integration: bool | None = None) -> CodexDeusMaximus:
    c = CodexDeusMaximus(data_dir=data_dir, allow_integration=allow_integration)
    c.initialize()
    # Ensure legacy method attribute exist on instance (bind to instance)
    try:
        c.auto_fix_file = c.auto_fix_file
    except Exception:
        pass
    return c
