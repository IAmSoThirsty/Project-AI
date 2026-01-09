#!/usr/bin/env python3
"""
Thirsty-lang Python Interpreter
A Python implementation of the Thirsty-lang interpreter
"""

import re
import sys
from typing import Any


class ThirstyInterpreter:
    """Main interpreter class for Thirsty-lang"""

    def __init__(self):
        self.variables: dict[str, Any] = {}
        self.output: list[str] = []

    def interpret(self, code: str) -> list[str]:
        """
        Interpret Thirsty-lang code and return output
        
        Args:
            code: Thirsty-lang source code as a string
            
        Returns:
            List of output strings
        """
        self.output = []
        lines = code.strip().split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('//') or line.startswith('#'):
                continue

            try:
                self._execute_line(line)
            except Exception as e:
                error_msg = f"Error on line {line_num}: {str(e)}"
                print(error_msg, file=sys.stderr)
                self.output.append(f"ERROR: {error_msg}")

        return self.output

    def execute_line(self, line: str):
        """Execute a single line of Thirsty-lang code (public interface)"""
        return self._execute_line(line)

    def _execute_line(self, line: str):
        """Execute a single line of Thirsty-lang code"""

        # Variable declaration: drink varname = value
        drink_match = re.match(r'drink\s+(\w+)\s*=\s*(.+)', line)
        if drink_match:
            var_name = drink_match.group(1)
            value_expr = drink_match.group(2).strip()
            self.variables[var_name] = self._evaluate_expression(value_expr)
            return

        # Output statement: pour expression
        pour_match = re.match(r'pour\s+(.+)', line)
        if pour_match:
            expr = pour_match.group(1).strip()
            value = self._evaluate_expression(expr)
            output_str = str(value)
            print(output_str)
            self.output.append(output_str)
            return

        # Input statement: sip varname
        sip_match = re.match(r'sip\s+(\w+)', line)
        if sip_match:
            var_name = sip_match.group(1)
            user_input = input(f"Enter value for {var_name}: ")
            self.variables[var_name] = user_input
            return

        raise SyntaxError(f"Unknown statement: {line}")

    def _evaluate_expression(self, expr: str) -> Any:
        """Evaluate an expression and return its value"""
        expr = expr.strip()

        # String literal
        if (expr.startswith('"') and expr.endswith('"')) or \
           (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        # Number literal
        try:
            if '.' in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            pass

        # Variable reference
        if expr in self.variables:
            return self.variables[expr]

        # Boolean literals
        if expr.lower() == 'true':
            return True
        if expr.lower() == 'false':
            return False

        # If we can't evaluate, return as string
        return expr

    def get_variables(self) -> dict[str, Any]:
        """Return current variable state"""
        return self.variables.copy()


def run_file(filename: str):
    """Run a Thirsty-lang file"""
    try:
        with open(filename, encoding='utf-8') as f:
            code = f.read()

        interpreter = ThirstyInterpreter()
        interpreter.interpret(code)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point for the Python interpreter"""
    if len(sys.argv) < 2:
        print("Usage: python3 thirsty_interpreter.py <file.thirsty>")
        sys.exit(1)

    filename = sys.argv[1]
    run_file(filename)


if __name__ == '__main__':
    main()
