#!/usr/bin/env python3
"""
Thirsty-lang Python REPL
Interactive Read-Eval-Pour-Loop for Thirsty-lang
"""

import sys
import os
from thirsty_interpreter import ThirstyInterpreter


class ThirstyREPL:
    """Interactive REPL for Thirsty-lang"""
    
    def __init__(self):
        self.interpreter = ThirstyInterpreter()
        self.history = []
    
    def run(self):
        """Start the REPL"""
        print("╔════════════════════════════════════════════════════════════╗")
        print("║          💧 Thirsty-lang Python REPL 💧                   ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print()
        print("Welcome to Thirsty-lang Interactive Shell (Python Edition)")
        print("Type 'help' for help, 'exit' or Ctrl+D to quit")
        print("Type 'vars' to see current variables")
        print()
        
        while True:
            try:
                line = input("thirsty> ").strip()
                
                if not line:
                    continue
                
                # Handle special commands
                if line.lower() in ('exit', 'quit'):
                    print("Stay hydrated! 💧")
                    break
                
                if line.lower() == 'help':
                    self._show_help()
                    continue
                
                if line.lower() == 'vars':
                    self._show_variables()
                    continue
                
                if line.lower() == 'clear':
                    os.system('clear' if os.name != 'nt' else 'cls')
                    continue
                
                if line.lower() == 'history':
                    self._show_history()
                    continue
                
                # Execute the line
                self.history.append(line)
                try:
                    self.interpreter.execute_line(line)
                except Exception as e:
                    print(f"Error: {str(e)}", file=sys.stderr)
            
            except EOFError:
                print("\nStay hydrated! 💧")
                break
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
    
    def _show_help(self):
        """Display help information"""
        print("\n=== Thirsty-lang Commands ===")
        print("  drink <var> = <value>  - Declare a variable")
        print("  pour <expression>      - Print output")
        print("  sip <var>              - Get input")
        print()
        print("=== REPL Commands ===")
        print("  help     - Show this help")
        print("  vars     - Show all variables")
        print("  history  - Show command history")
        print("  clear    - Clear screen")
        print("  exit     - Exit REPL")
        print()
    
    def _show_variables(self):
        """Display current variables"""
        vars_dict = self.interpreter.get_variables()
        if not vars_dict:
            print("No variables defined")
        else:
            print("\n=== Current Variables ===")
            for name, value in vars_dict.items():
                print(f"  {name} = {repr(value)}")
            print()
    
    def _show_history(self):
        """Display command history"""
        if not self.history:
            print("No command history")
        else:
            print("\n=== Command History ===")
            for i, cmd in enumerate(self.history, 1):
                print(f"  {i}. {cmd}")
            print()


def main():
    """Main entry point for Python REPL"""
    repl = ThirstyREPL()
    repl.run()


if __name__ == '__main__':
    main()
