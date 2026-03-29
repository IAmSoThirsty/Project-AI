# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / sovereign_runtime.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / sovereign_runtime.py

import os
import sys
import hashlib
import hmac
import subprocess
import tempfile
from datetime import datetime



               #
# COMPLIANCE: Sovereign-Native / Anti-Reverse Engineering                      #



# Master-Tier Secret for HMAC (Must match Hardener)
SOVEREIGN_KEY = b"Thirsty-Project-AI-Sovereign-Integrity-Seal-2026"

class SovereignRuntime:
    """
    Sovereign Runtime Environment.
    
    Verifies the integrity of "Sealed" (.tscgb) tools and executes them
    with zero-persistence to prevent reverse engineering and tampering.
    """

    def verify_and_hydrate(self, sealed_path: str):
        """
        Verifies the signature and returns the human-readable (in-memory) code.
        """
        if not os.path.exists(sealed_path):
            raise FileNotFoundError(f"Sealed tool not found: {sealed_path}")

        with open(sealed_path, 'rb') as f:
            data = f.read()

        # [MAGIC][VER][SIGNATURE][PAYLOAD]
        magic = data[:4]
        if magic != b"PASH":
            raise ValueError("Invalid Sovereign Seal: Magic Mismatch")

        version = data[4:5]
        signature = data[5:37] # HMAC-SHA256 is 32 bytes
        payload = data[37:]

        # Verify Integrity
        expected_signature = hmac.new(SOVEREIGN_KEY, payload, hashlib.sha256).digest()
        
        if not hmac.compare_digest(signature, expected_signature):
            print(f"🛑 CRITICAL: Integrity Violation detected in {sealed_path}!")
            print("🛑 THE SOVEREIGN PROTOCOL HAS BEEN BREACHED.")
            sys.exit(1)

        return payload.decode('utf-8')

    def execute_sealed(self, sealed_path: str, args: list = None):
        """
        Runs a sealed tool based on its original language intent.
        """
        code = self.verify_and_hydrate(sealed_path)
        
        # Determine execution path based on suffix (we keep .py.tscgb or .js.tscgb logic)
        if ".py" in sealed_path:
            self._execute_python(code, args or [], sealed_path)
        elif ".js" in sealed_path:
            self._execute_javascript(code, args or [], sealed_path)
        else:
            print(f"Error: Unknown tool type for {sealed_path}")

    def _execute_python(self, code: str, args: list, sealed_path: str):
        """Verified memory execution of Python code."""
        # Setup sys.argv for the target script
        old_argv = sys.argv
        sys.argv = [sys.argv[0]] + args
        
        try:
            # Multi-layer isolation
            # We simulate the file path of the original script for unittest discovery
            original_path = os.path.abspath(sealed_path.replace(".tscgb", ""))
            namespace = {
                "__name__": "__main__",
                "__file__": original_path
            }
            # Ensure the directory of the script is in sys.path
            sys.path.insert(0, os.path.dirname(original_path))
            exec(code, namespace)
        except Exception as e:
            print(f"Error executing python tool: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            sys.argv = old_argv

    def _execute_javascript(self, code: str, args: list, sealed_path: str):
        """Verified piping of JavaScript code to Node.js."""
        # Use the directory of the sealed file as CWD to allow relative requires
        cwd = os.path.dirname(os.path.abspath(sealed_path))
        
        cmd = ["node", "-"] + args
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
            cwd=cwd,
            encoding='utf-8'
        )
        try:
            process.communicate(input=code)
        except Exception as e:
            print(f"Error communicating with node: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
            
        if process.returncode != 0:
            sys.exit(process.returncode)

def main():
    if len(sys.argv) < 2:
        print("Sovereign Runtime Environment")
        print("Usage: python scripts/sovereign_runtime.py <tool.tscgb> [args...]")
        sys.exit(0)

    runtime = SovereignRuntime()
    runtime.execute_sealed(sys.argv[1], sys.argv[2:])

if __name__ == "__main__":
    main()
