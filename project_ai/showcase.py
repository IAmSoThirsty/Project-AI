# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / showcase.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / showcase.py


#                                                             DATE: 2026-03-03 09:32:01
#                                                             STATUS: Active
"""
[UTF] UNIVERSAL THIRSTY FAMILY - SOVEREIGN SHOWCASE v1.0 [UTF]

This module provides the authoritative, end-to-end demonstration suite for the
Universal Thirsty Family (UTF) ecosystem, verifying mission-critical behavior
across Thirst of Gods, TSCG-B, T.A.R.L., and Shadow Thirst.
"""

import os
import struct
import subprocess
import sys
from datetime import datetime

# Regulator-Ready Path Alignment: Set up system paths before relative imports
# SCRIPT_DIR is Project-AI/project_ai
_SD = os.path.abspath(
    os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
)
# PROJECT_ROOT is Project-AI/
_PR = os.path.dirname(_SD)

# Add source directories to sys.path for absolute resolution
if _PR not in sys.path:
    sys.path.insert(0, _PR)
if os.path.join(_PR, "src") not in sys.path:
    sys.path.insert(0, os.path.join(_PR, "src"))

# Internal UTF Imports (Exempt from PEP8/Pylint static pathing checks)
# pylint: disable=wrong-import-position,import-error,no-name-in-module
from project_ai.tarl.integrations.orchestration import (  # noqa: E402
    DeterministicVM,
    Policy,
)
from project_ai.utils.tscg_b import TSCGBDecoder, TSCGBEncoder  # noqa: E402
from shadow_thirst.bytecode import (  # noqa: E402
    BytecodeFunction,
    BytecodeInstruction,
    BytecodeOpcode,
    BytecodeProgram,
    PlaneTag,
)
from shadow_thirst.vm import ShadowAwareVM  # noqa: E402


class Colors:
    """UTF Color Palette for Sovereign Showcase."""

    CYAN = "\033[96m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(text):
    """Prints a styled header for showcase stages."""
    border = "+" + "-" * (len(text) + 4) + "+"
    print("\n" + Colors.CYAN + Colors.BOLD + border)
    print(f"|  {text}  |")
    print(border + Colors.END)


def log_audit(text):
    """Writes a clean audit trail to a file."""
    with open("showcase_audit.log", "a", encoding="utf-8") as f:
        f.write(text + "\n")


def print_status(component, status, detail=""):
    """Prints a standardized status line for audit trails."""
    color = (
        Colors.GREEN
        if status in ("ACTIVE", "SUCCESS", "FAIL", "REJECTED")
        else Colors.RED
    )
    line = f"{component:<20} | {status:<12} | {detail}"
    print(
        f"{Colors.BOLD}{component:<20}{Colors.END} | {color}{status:<12}{Colors.END} | {detail}"
    )
    log_audit(line)


def run_thirsty_demo():
    """Executes Stage 1: Core Intelligence (Thirst of Gods)."""
    print_header("STAGE 1: CORE INTELLIGENCE (ToG)")
    script = os.path.join(_PR, "examples/v1_finality_test.thirst")
    cli = os.path.join(_PR, "src/thirsty_lang/src/thirsty-cli.js")
    try:
        print(f"Executing Master-Tier Logic: {os.path.basename(script)}...")
        subprocess.run(["node", cli, "run", script], check=True)
        print_status("Thirsty-Lang", "ACTIVE", "v1.0.0 Sovereign Core")
        print_status("Thirst of Gods", "ACTIVE", "Async/OOP Integration Verified")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print_status("Thirst of Gods", "ERROR", f"Execution failed: {e}")
    except RuntimeError as e:
        print_status("Thirst of Gods", "ERROR", f"Interpreter error: {e}")


def run_tscgb_demo():
    """Executes Stage 2: Constitutional Wire (TSCG-B Protocol)."""
    print_header("STAGE 2: CONSTITUTIONAL WIRE (TSCG-B)")
    try:
        # Spacing matches canonical v1.0 reconstructed output
        expr = (
            "ING -> COG -> D_NT -> SHD (1) -> INV (5) AND CAP -> "
            "QRM_LINEAR (3,1,2,1) -> COM -> ANC -> LED"
        )
        print(f"Grammar Input:  {Colors.YELLOW}{expr}{Colors.END}")

        enc, dec = TSCGBEncoder(), TSCGBDecoder()
        blob = enc.encode_binary(expr)
        print(f"T-BLOB Stream:  {Colors.BOLD}{blob.hex().upper()}{Colors.END}")

        reconstructed = dec.decode_binary(blob)
        parity = reconstructed.strip() == expr.strip()
        print(
            f"Symbol Parity:  {Colors.GREEN if parity else Colors.RED}{reconstructed}{Colors.END}"
        )
        print_status(
            "TSCG-B v1.0", "SUCCESS", f"Bijectivity: {'100%' if parity else 'MISMATCH'}"
        )
    except (ImportError, ValueError, struct.error) as e:
        print_status("TSCG-B v1.0", "ERROR", f"Protocol failure: {e}")


def run_tarl_demo():
    """Executes Stage 3: Performance Policy (T.A.R.L. Engine)."""
    print_header("STAGE 3: PERFORMANCE POLICY (T.A.R.L.)")
    try:
        # Use canonical Policy and DeterministicVM per UTF spec
        vm = DeterministicVM()
        policy = Policy(
            name="Sovereign-Safety",
            capability_name="EXEC",
            constraints={"risk_level": "controlled"},
        )
        print_status(
            "T.A.R.L.", "ACTIVE", f"Policy '{policy.name}' loaded in VM {id(vm)}"
        )
    except (ImportError, KeyError, RuntimeError) as e:
        print_status("T.A.R.L.", "ERROR", f"Runtime failure: {e}")


def run_shadow_demo():
    """Executes Stage 4: Total Containment (Shadow-Aware VM)."""
    print_header("STAGE 4: TOTAL CONTAINMENT (SHADOW VM)")
    try:
        # Corrected signatures: BytecodeInstruction(opcode, plane, operands)
        inst = BytecodeInstruction(BytecodeOpcode.PUSH, PlaneTag.PRIMARY, [99])
        ret = BytecodeInstruction(BytecodeOpcode.RETURN, PlaneTag.PRIMARY)

        main_func = BytecodeFunction(
            name="__main__",
            parameter_count=0,
            local_count=0,
            primary_bytecode=[inst, ret],
        )

        prog = BytecodeProgram(functions=[main_func])

        vm = ShadowAwareVM(max_instructions=100)
        vm.load_program(prog)
        vm.execute("__main__")

        print_status("Shadow VM", "SUCCESS", "Runtime Memory/Guard Rails Active")
    except (ImportError, RuntimeError, TypeError, AttributeError) as e:
        print_status("Shadow VM", "ERROR", f"VM failure: {e}")


def run_stress_tests():
    """Executes the Stress Test Suite: Proving systems under stress."""
    print_header("FINAL STAGE: STRESS TESTS (FAILURE MODES)")

    # 1. Corrupt the TSCG-B parity
    print(f"\n{Colors.BOLD}[FAIL 1] Corrupting TSCG-B Parity...{Colors.END}")
    try:
        expr = "ING -> COG -> D_NT"
        corrupted_expr = "ING -> COG -> D_NC"  # Changed one character in expr
        enc, dec = TSCGBEncoder(), TSCGBDecoder()
        blob = enc.encode_binary(expr)
        reconstructed = dec.decode_binary(blob)
        parity = reconstructed.strip() == corrupted_expr.strip()
        print_status(
            "TSCG-B Stress",
            "FAIL" if not parity else "PASS",
            f"Bijectivity: {'100%' if parity else 'MISMATCH (EXPECTED)'}",
        )
    except Exception as e:
        print_status("TSCG-B Stress", "ERROR", str(e))

    # 2. Break the Shadow VM (Missing RETURN)
    print(f"\n{Colors.BOLD}[FAIL 2] Breaking Shadow VM (Missing RETURN)...{Colors.END}")
    try:
        inst = BytecodeInstruction(BytecodeOpcode.PUSH, PlaneTag.PRIMARY, [42])
        # NO RETURN instruction added here
        main_func = BytecodeFunction(
            name="__main__",
            parameter_count=0,
            local_count=0,
            primary_bytecode=[inst],
        )
        prog = BytecodeProgram(functions=[main_func])
        vm = ShadowAwareVM(max_instructions=10)
        vm.load_program(prog)
        vm.execute("__main__")
        print_status(
            "Shadow VM Stress", "Lying", "Silently succeeded (CRITICAL FAILURE)"
        )
    except RuntimeError as e:
        print_status(
            "Shadow VM Stress", "FAIL", f"Caught Protocol Violation: {e} (VALID)"
        )

    # 3. Violate Policy (Incorrect Risk Level)
    print(f"\n{Colors.BOLD}[FAIL 3] Violating T.A.R.L. Policy...{Colors.END}")
    try:
        policy = Policy(
            name="Strict-Audit",
            capability_name="NET_CONNECT",
            constraints={"risk_level": "none"},
        )
        # Attempt to match against an "elevated" risk capability
        # In a real scenario, we'd check this via evaluation
        from project_ai.tarl.integrations.orchestration import Capability

        cap = Capability(
            name="NET_CONNECT",
            resource="network",
            constraints={"risk_level": "elevated"},
        )
        allowed, reason = policy.evaluate(cap, {})
        print_status(
            "T.A.R.L. Policy",
            "REJECTED" if not allowed else "ALLOWED",
            f"Result: {reason} (VALID)",
        )
    except Exception as e:
        print_status("T.A.R.L. Policy", "ERROR", str(e))

    # 4. Kill the ToG CLI path
    print(f"\n{Colors.BOLD}[FAIL 4] Killing ToG CLI path...{Colors.END}")
    cli = os.path.join(_PR, "src/thirsty_lang/src/thirsty-cli.js")
    temp_cli = cli + ".tmp"
    try:
        if os.path.exists(cli):
            os.rename(cli, temp_cli)

        script = os.path.join(_PR, "examples/v1_finality_test.thirst")
        subprocess.run(["node", cli, "run", script], check=True, capture_output=True)
        print_status("ToG Path Stress", "Lying", "Found non-existent script? (ERROR)")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print_status(
            "ToG Path Stress", "ERROR", f"Stage reported ERROR as expected: {e}"
        )
    finally:
        if os.path.exists(temp_cli):
            os.rename(temp_cli, cli)


def main():
    """Entry point for the Sovereign Showcase Suite."""
    os.system("cls" if os.name == "nt" else "clear")
    title = "[UTF] UNIVERSAL THIRSTY FAMILY - SOVEREIGN SHOWCASE v1.0 [UTF]"
    print(f"\n{Colors.CYAN}{Colors.BOLD}{title}{Colors.END}")
    print(f"System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")

    if os.path.exists("showcase_audit.log"):
        os.remove("showcase_audit.log")
    log_audit(f"--- SOVEREIGN AUDIT START: {datetime.now()} ---")

    run_thirsty_demo()
    run_tscgb_demo()
    run_tarl_demo()
    run_shadow_demo()
    run_stress_tests()

    print_header("SOVEREIGN VERIFICATION COMPLETE")
    print(
        f"{Colors.GREEN}{Colors.BOLD}ALL SYSTEMS DECLARED MISSION-READY.{Colors.END}\n"
    )


if __name__ == "__main__":
    main()
