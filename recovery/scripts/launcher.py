#!/usr/bin/env python3
# (Master Launch Vector)                    [2026-04-09 04:26]
#                                          Status: Active
# This file owns nothing. It starts the engine and steps aside.
import sys
import os

# Add src to path for relative imports if needed
sys.path.append(os.path.join(os.getcwd(), "src"))

from thirsty_lang.src.thirsty_interpreter import ThirstyInterpreter
from app.ui.render_engine import RenderEngine

def main():
    renderer = RenderEngine()
    interpreter = ThirstyInterpreter(renderer=renderer)
    
    # Start the renderer loop in the main thread (DPG requirement)
    renderer.start()
    
    # Load and execute the boot script
    boot_script = "src/app/sovereign/sovereign_boot.thirsty"
    if os.path.exists(boot_script):
        with open(boot_script, "r", encoding="utf-8") as f:
            interpreter.interpret(f.read())
    else:
        print(f"Error: {boot_script} not found.")
        renderer.shutdown()
        return

    # Main loop for DPG
    while renderer.is_running():
        renderer.frame()
    
    renderer.shutdown()

if __name__ == "__main__":
    main()
