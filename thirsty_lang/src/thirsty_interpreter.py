"""
Bridge module for Thirsty-lang interpreter (RESTORED).

This module bridges the gap between the Sovereign-native environment and the
uninitialized external/Thirsty-Lang submodule. It provides the expected
interface for the Sovereign verification script while the submodule
is pending initialization.
"""

class ThirstyInterpreter:
    """Mock/Bridge for Thirsty-lang interpreter."""
    
    def __init__(self, *args, **kwargs):
        pass
        
    def execute(self, script_path: str):
        """Execute a .thirsty script."""
        raise RuntimeError(
            f"Thirsty-lang interpreter is in BRIDGE mode for {script_path}. "
            "Please initialize the 'external/Thirsty-Lang' submodule for full execution logic."
        )

def get_interpreter():
    """Return the active interpreter instance."""
    return ThirstyInterpreter()
