import subprocess
from pathlib import Path

from cognition.audit import audit
from tarl.validate import validate

THIRSTY_CLI = Path(__file__).parent.parent / "src" / "thirsty_lang" / "src" / "cli.js"


def submit_tarl(tarl):
    validate(tarl)
    audit("TARL_SUBMIT", {"hash": tarl.hash(), "authority": tarl.authority})
    return {"accepted": True, "hash": tarl.hash()}


def execute_sovereign_module(module_path: str, function_name: str, *args):
    """Execute a Thirsty-Lang module function via the interpreter."""
    cmd = ["node", str(THIRSTY_CLI), module_path, function_name] + [
        str(a) for a in args
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        audit(
            "SOVEREIGN_EXECUTION",
            {"module": module_path, "function": function_name, "status": "SUCCESS"},
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        audit(
            "SOVEREIGN_EXECUTION_FAILURE",
            {"module": module_path, "function": function_name, "error": e.stderr},
        )
        raise RuntimeError(f"Sovereign execution failed: {e.stderr}") from e
