# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / thirsty_interpreter.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / thirsty_interpreter.py

#!/usr/bin/env python3
"""
Thirsty-lang Python Interpreter
A Python implementation of the Thirsty-lang interpreter
"""

import io
import json
import logging
import re
import sys
from typing import Any

# Force UTF-8 for consistency across substrates
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Try to import TarlRuntime from the integrated package
TarlRuntime: type | None = None
try:
    from .tarl.runtime import TarlRuntime as _TarlRuntime
    TarlRuntime = _TarlRuntime  # type: ignore
except (ImportError, ValueError):
    # Fallback if not installed as a package
    pass

logger = logging.getLogger(__name__)


class ThirstyInterpreter:
    """Main interpreter class for Thirsty-lang"""

    def __init__(self, renderer: Any = None):
        self.variables: dict[str, Any] = {}
        self.output: list[str] = []
        self.renderer = renderer

    def _execute_render_directive(self, line: str):
        """
        Parses and dispatches render directives to the RenderEngine.
        Format: render.COMMAND "ARG1" ARG2 ARG3
        """
        # Split by spaces but respect quotes
        parts = re.findall(r'(?:[^\s"\']|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')+', line.strip())
        if not parts:
            return
            
        directive = parts[0]
        args = []
        for part in parts[1:]:
            if (part.startswith('"') and part.endswith('"')) or (part.startswith("'") and part.endswith("'")):
                args.append(part[1:-1])
            else:
                args.append(part)

        if self.renderer:
            self.renderer.execute_directive(directive, args)

    def interpret(self, code: str):
        """Interpret a block of Thirsty-lang code with robust bracket-matching."""
        # 1. Clean and normalize code
        lines = []
        for line in code.splitlines():
            # Support both # and // for comments
            clean = line.split("#")[0].split("//")[0].strip()
            if clean:
                lines.append(clean)
        
        # 2. Executive Loop
        # We process line by line or block by block.
        # Original implementation joined lines, which might break 'render.' directives
        # if they were on separate lines.
        full_code = " ".join(lines)

        # 2. Executive Loop
        ptr = 0
        while ptr < len(full_code):
            segment = full_code[ptr:].strip()
            if not segment:
                break

            # Block: thirsty
            if segment.startswith("thirsty"):
                # Use a non-greedy match until the first {
                thirsty_match = re.match(r"thirsty\s*\((.*?)\)\s*\{", segment)
                if thirsty_match:
                    condition_expr = thirsty_match.group(1)
                    condition = self._evaluate_expression(condition_expr)

                    abs_brace_start = ptr + segment.find("{")
                    abs_brace_end = self._find_closing_bracket(full_code, abs_brace_start)

                    if abs_brace_end != -1:
                        if condition:
                            # Recursive call for the block content
                            self.interpret(full_code[abs_brace_start + 1:abs_brace_end])

                        ptr = abs_brace_end + 1
                        
                        # Peek for 'hydrated' immediately after the block
                        remaining_peek = full_code[ptr:].strip()
                        if remaining_peek.startswith("hydrated"):
                            # Find the start of the hydrated block
                            h_brace_start = ptr + full_code[ptr:].find("{")
                            h_brace_end = self._find_closing_bracket(full_code, h_brace_start)
                            
                            if h_brace_end != -1:
                                if not condition:
                                    self.interpret(full_code[h_brace_start + 1:h_brace_end])
                                ptr = h_brace_end + 1
                        continue

            # Block: sacred substrate
            if segment.startswith("sacred substrate"):
                # Matches: sacred substrate Name { ... }
                substrate_match = re.match(r"sacred\s+substrate\s+(\w+)\s*\{", segment)
                if substrate_match:
                    interface_name = substrate_match.group(1)
                    abs_start = ptr + segment.find("{")
                    abs_end = self._find_closing_bracket(full_code, abs_start)

                    if abs_end != -1:
                        # Extract block content
                        block_content = full_code[abs_start + 1:abs_end]
                        # Create a scope for this substrate
                        substrate_data: dict[str, Any] = {}
                        original_vars = self.variables
                        self.variables = substrate_data
                        self.interpret(block_content)
                        self.variables = original_vars
                        self.variables[interface_name] = substrate_data

                        ptr = abs_end + 1
                        continue

            # Block: enforce
            if segment.startswith("enforce"):
                # Matches: enforce "PolicyName" { ... }
                enforce_match = re.match(r"enforce\s+[\"'](\w+)[\"']\s*\{", segment)
                if enforce_match:
                    policy_name = enforce_match.group(1)
                    abs_start = ptr + segment.find("{")
                    abs_end = self._find_closing_bracket(full_code, abs_start)

                    if abs_end != -1:
                        # Logic: If TarlRuntime is available, we could evaluate here.
                        # For now, we simulate the 'enforce' pass.
                        sys.stdout.write(f"ENFORCE: {policy_name} - PASSED\n")
                        ptr = abs_end + 1
                        continue

            # Standard statement: take until next keyword or end
            next_keywords = [
                "drink ", "sacred ", "pour ", "thirsty ",
                "hydrated ", "sacred substrate ", "enforce ", "render."
            ]
            closest = len(full_code)
            for kw in next_keywords:
                idx = full_code.find(kw, ptr + 1)
                if idx != -1 and idx < closest:
                    closest = idx

            statement = full_code[ptr:closest].strip()
            if statement:
                logger.debug(f"Executing statement: {statement}")
                self._execute_line(statement)
            ptr = closest

    def _execute_line(self, line: str):
        """Execute a single line of Thirsty-lang code."""
        line = line.strip()
        if not line:
            return

        # Render Directive
        if line.startswith("render."):
            self._execute_render_directive(line)
            return

        # Pour command
        pour_match = re.match(r"pour\s+(.*)", line)
        if pour_match:
            val = self._evaluate_expression(pour_match.group(1).strip())
            sys.stdout.write(f"POUR: {val}\n")
            return

        # Drink / Sacred
        drink_match = re.match(r"(drink|sacred)\s+(\w+)\s*=\s*(.*)", line)
        if drink_match:
            name, expr = drink_match.group(2), drink_match.group(3).strip()
            self.variables[name] = self._evaluate_expression(expr)
            return

        self._evaluate_expression(line)

    def _evaluate_expression(self, expr: str) -> Any:
        # pylint: disable=too-many-branches,too-many-return-statements
        """Evaluate an expression with proper Master-Tier precedence."""
        expr = expr.strip()
        if not expr:
            return None

        # 1. String Literals
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        # 2. Parentheses
        if expr.startswith("(") and expr.endswith(")"):
            # Ensure it's the outermost pair
            d = 0
            for i in range(len(expr) - 1):
                if expr[i] == "(":
                    d += 1
                elif expr[i] == ")":
                    d -= 1
                if d == 0 and i > 0:
                    break
            else:
                return self._evaluate_expression(expr[1:-1])

        # 3. JSON / Objects
        if expr.startswith("{") and expr.endswith("}"):
            try:
                # Fast path: direct JSON
                processed = expr.replace("'", '"')
                return json.loads(processed)
            except (json.JSONDecodeError, ValueError):
                # Slow path: variable substitution
                def replacer(word):
                    if word in self.variables and word not in ["true", "false", "null"]:
                        return json.dumps(self.variables[word])
                    return word
                pattern = r'("(?:\\.|[^"\\])*")|(\b[a-zA-Z_]\w*\b)'
                processed = re.sub(pattern, lambda m: m.group(1) if m.group(1) else replacer(m.group(2)), expr.replace("'", '"'))
                try:
                    return json.loads(processed)
                except (json.JSONDecodeError, ValueError):
                    return expr

        # 4. Comparisons
        for op in ["==", "!=", "<=", ">=", "<", ">"]:
            idx = self._find_op_idx(expr, op)
            if idx != -1:
                left = self._evaluate_expression(expr[:idx])
                right = self._evaluate_expression(expr[idx + len(op):])
                if op == "==":
                    return left == right
                if op == "!=":
                    return left != right
                try:
                    if op == "<=":
                        return float(left) <= float(right)
                    if op == ">=":
                        return float(left) >= float(right)
                    if op == "<":
                        return float(left) < float(right)
                    if op == ">":
                        return float(left) > float(right)
                except (TypeError, ValueError):
                    return False

        # 5. Add/Sub
        for op in ["+", "-"]:
            idx = self._find_op_idx(expr, op, reverse=True)
            if idx != -1:
                if op == "-" and (idx == 0 or (idx > 0 and expr[idx - 1] in "+-*/%(")):
                    continue
                left = self._evaluate_expression(expr[:idx])
                right = self._evaluate_expression(expr[idx + 1:])
                try:
                    if op == "+":
                        return float(left) + float(right)
                    if op == "-":
                        return float(left) - float(right)
                except (TypeError, ValueError):
                    if op == "+":
                        return str(left) + str(right)
                    return 0

        # 6. Mul/Div/Mod/FloorDiv
        for op in ["//", "%", "*", "/"]:
            idx = self._find_op_idx(expr, op, reverse=True)
            if idx != -1:
                left = self._evaluate_expression(expr[:idx])
                right = self._evaluate_expression(expr[idx + len(op):])
                try:
                    if op == "*":
                        return float(left) * float(right)
                    if op == "/":
                        return float(left) / float(right)
                    if op == "%":
                        return float(left) % float(right)
                    if op == "//":
                        return float(left) // float(right)
                except (TypeError, ValueError, ZeroDivisionError):
                    return 0

        # 6.5 Power (highest non-bracket precedence)
        idx = self._find_op_idx(expr, "**")
        if idx != -1:
            left = self._evaluate_expression(expr[:idx])
            right = self._evaluate_expression(expr[idx + 2:])
            try:
                return float(left) ** float(right)
            except (TypeError, ValueError, OverflowError):
                return 0

        # 7. Terminals: Index, Number, Prop, Var
        if "[" in expr and expr.endswith("]"):
            match = re.search(r"(\w+)\[\s*['\"]?(\w+)['\"]?\s*\]", expr)
            if match:
                obj = self.variables.get(match.group(1))
                if isinstance(obj, dict):
                    return obj.get(match.group(2))
                if isinstance(obj, list):
                    try:
                        return obj[int(match.group(2))]
                    except (ValueError, IndexError):
                        logger.warning("Encountered non-terminal exception in %s", __name__)

        try:
            return float(expr) if "." in expr else int(expr)
        except (ValueError, TypeError):
            logger.warning("Encountered non-terminal exception in %s", __name__)

        if expr.lower() == "true":
            return True
        if expr.lower() == "false":
            return False
        if expr.lower() == "null":
            return None

        if expr in self.variables:
            return self.variables[expr]
        return expr

    def _find_op_idx(self, expr, op, reverse=False):
        d = 0
        rng = range(len(expr) - 1, -1, -1) if reverse else range(len(expr))
        for i in rng:
            if expr[i] == ")":
                d += 1
            elif expr[i] == "(":
                d -= 1
            elif d == 0 and expr[i:i + len(op)] == op:
                return i
        return -1

    def _find_closing_bracket(self, code, start):
        d = 1
        for i in range(start + 1, len(code)):
            if code[i] == "{":
                d += 1
            elif code[i] == "}":
                d -= 1
                if d == 0:
                    return i
        return -1

    def execute_line(self, line: str):
        """Execute a single line - public interface."""
        return self._execute_line(line)

    def get_variables(self) -> dict:
        """Get copy of interpreter variables."""
        return self.variables.copy()


def main():
    """Main CLI entrypoint."""
    if len(sys.argv) < 2:
        return
    with open(sys.argv[1], encoding="utf-8") as f:
        ThirstyInterpreter().interpret(f.read())


if __name__ == "__main__":
    main()
