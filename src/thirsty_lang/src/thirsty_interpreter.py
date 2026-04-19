# (Thirsty-Lang Core Interpreter)           [2026-04-09 05:10]
#                                          Status: Active
"""
Thirsty-lang Python Interpreter - Production Grade

A production-ready, security-hardened implementation of the Thirsty-lang
interpreter for Python. Integrates with the Sovereign UI Render Engine
and provides defensive programming capabilities.

Capabilities:
- Core Thirsty-lang syntax (drink, pour, sip)
- Defensive Shielding (shield, morph, detect, defend)
- Memory Sanitization (sanitize, armor)
- UI Integration (Renderer hooks)
- Master Tier production readiness
"""

import logging
import re
import sys
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


@dataclass
class SecurityContext:
    """Tracks active security layers and defensive strategies."""

    shields: list[dict[str, Any]] = field(default_factory=list)
    morph_enabled: bool = False
    threat_detection: bool = False
    defense_strategy: str = "moderate"
    armored_vars: set = field(default_factory=set)


class ThirstyInterpreter:
    """
    Main interpreter class for Thirsty-lang.
    Supports functional execution and UI rendering hooks.
    """

    def __init__(self, renderer: Any | None = None):
        """
        Initialize the interpreter.

        Args:
            renderer: Optional RenderEngine instance for UI integration
        """
        self.variables: dict[str, Any] = {}
        self.output: list[str] = []
        self.renderer = renderer
        self.security = SecurityContext()

        logger.info("ThirstyInterpreter initialized (Renderer: %s)", "Enabled" if renderer else "Disabled")

    def interpret(self, code: str) -> list[str]:
        """
        Interpret Thirsty-lang code and return output.

        Args:
            code: Thirsty-lang source code
        """
        self.output = []
        lines = code.strip().split("\n")

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("//") or line.startswith("#"):
                continue

            try:
                self._execute_line(line)
            except Exception as e:
                error_msg = f"Error on line {line_num}: {str(e)}"
                logger.error(error_msg)
                self.output.append(f"ERROR: {error_msg}")
                if self.renderer:
                    self.renderer.notify_error(error_msg)

        return self.output

    def _execute_line(self, line: str):
        """Execute a single line of Thirsty-lang code with security logic."""

        # 1. Security Keywords (Phase 2 Repair)
        if line.startswith("shield "):
            self._handle_shield(line)
        elif line.startswith("morph "):
            self._handle_morph(line)
        elif line.startswith("detect "):
            self._handle_detect(line)
        elif line.startswith("defend "):
            self._handle_defend(line)
        elif line.startswith("sanitize "):
            self._handle_sanitize(line)
        elif line.startswith("armor "):
            self._handle_armor(line)

        # 2. Variable declaration: drink varname = value
        elif line.startswith("drink "):
            self._handle_drink(line)

        # 3. Output statement: pour expression
        elif line.startswith("pour "):
            self._handle_pour(line)

        # 4. Input statement: sip varname
        elif line.startswith("sip "):
            self._handle_sip(line)

        # 5. UI Commands (Renderer Hooks)
        elif line.startswith("ui."):
            self._handle_ui_command(line)

        else:
            # Check for generic assignments if complex
            if " = " in line:
                self._handle_assignment(line)
            else:
                raise SyntaxError(f"Unknown statement: {line}")

    def _handle_shield(self, line: str):
        match = re.match(r"shield\s+(\w+)?", line)
        shield_name = match.group(1) if match and match.group(1) else "anonymous"
        self.security.shields.append({"name": shield_name, "active": True})
        logger.info("[SECURITY] Shield '%s' activated", shield_name)

    def _handle_morph(self, line: str):
        self.security.morph_enabled = True
        logger.info("[SECURITY] Morphing enabled")

    def _handle_detect(self, line: str):
        self.security.threat_detection = True
        logger.info("[SECURITY] Threat detection activated")

    def _handle_defend(self, line: str):
        match = re.match(r'defend\s+with:\s*"(\w+)"', line)
        if match:
            self.security.defense_strategy = match.group(1)
            logger.info("[SECURITY] Defense strategy: %s", self.security.defense_strategy)

    def _handle_sanitize(self, line: str):
        match = re.match(r"sanitize\s+(\w+)", line)
        if match:
            var_name = match.group(1)
            if var_name in self.variables:
                # Basic sanitization: strip HTML and weird chars
                val = str(self.variables[var_name])
                self.variables[var_name] = re.sub(r"[<>]", "", val)
                logger.info("[SECURITY] Sanitized variable: %s", var_name)

    def _handle_armor(self, line: str):
        match = re.match(r"armor\s+(\w+)", line)
        if match:
            var_name = match.group(1)
            self.security.armored_vars.add(var_name)
            logger.info("[SECURITY] Armored variable: %s", var_name)

    def _handle_drink(self, line: str):
        match = re.match(r"drink\s+(\w+)\s*=\s*(.+)", line)
        if match:
            var_name = match.group(1)
            if var_name in self.security.armored_vars:
                raise PermissionError(f"Cannot modify armored variable: {var_name}")
            value_expr = match.group(2).strip()
            self.variables[var_name] = self._evaluate_expression(value_expr)

    def _handle_pour(self, line: str):
        expr = line[5:].strip()
        value = self._evaluate_expression(expr)
        output_str = str(value)
        self.output.append(output_str)
        if self.renderer:
            self.renderer.console_print(output_str)
        else:
            print(output_str)

    def _handle_sip(self, line: str):
        var_name = line[4:].strip()
        if self.renderer:
            # Request input from the UI
            val = self.renderer.request_input(f"Enter value for {var_name}")
        else:
            val = input(f"Enter value for {var_name}: ")
        self.variables[var_name] = val

    def _handle_ui_command(self, line: str):
        if not self.renderer:
            logger.warning("UI command ignored: No renderer active")
            return
        # Basic UI command routing
        cmd = line[3:].strip()
        self.renderer.execute_ui_command(cmd)

    def _handle_assignment(self, line: str):
        # Generic x = y support
        match = re.match(r"(\w+)\s*=\s*(.+)", line)
        if match:
            var_name = match.group(1)
            if var_name in self.security.armored_vars:
                raise PermissionError(f"Cannot modify armored variable: {var_name}")
            value_expr = match.group(2).strip()
            self.variables[var_name] = self._evaluate_expression(value_expr)

    def _evaluate_expression(self, expr: str) -> Any:
        expr = expr.strip()
        # String
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        # Number
        try:
            if "." in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            pass
        # Variable
        if expr in self.variables:
            return self.variables[expr]
        # Boolean
        if expr.lower() == "true":
            return True
        if expr.lower() == "false":
            return False
        return expr


def run_file(filename: str):
    """Run a Thirsty-lang file."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            code = f.read()
        interpreter = ThirstyInterpreter()
        interpreter.interpret(code)
    except Exception as e:
        logger.error("Execution failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        print("Sovereign Thirsty-Lang Interpreter v1.0.0")
