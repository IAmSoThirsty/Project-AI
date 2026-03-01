"""
Sovereign Verification Runbook Execution Script.

This script automates the verification of Project-AI's constitutional,
cryptographic, and structural invariants as defined in The_Guide_Book.md.
"""

import hashlib
import os
import sys

# Root path for Project-AI
ROOT = r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI"
GUIDE_BOOK = os.path.join(ROOT, "The_Guide_Book.md")

# Add src to path for dynamic imports
sys.path.insert(0, os.path.join(ROOT, "src"))


def log_check(check_id, severity, status, evidence, remediation="", related_files=None):
    """
    Log a verification check result to the console in a standardized format.

    Args:
        check_id (str): The ID of the check (e.g., T0.1.1).
        severity (str): Severity level (CRITICAL, HIGH, MEDIUM, LOW).
        status (str): Outcome (PASS, FAIL, PARTIAL).
        evidence (str): Descriptive proof of the result.
        remediation (str, optional): Steps to fix if failed. Defaults to "".
        related_files (list, optional): Files involved in the check. Defaults to None.
    """
    print(f"CHECK ID: {check_id}")
    print(f"SEVERITY: {severity}")
    print(f"STATUS: {status}")
    print(f"EVIDENCE: {evidence}")
    if related_files:
        print(f"RELATED FILES: {', '.join(related_files)}")
    if remediation and status != "PASS":
        print(f"REMEDIATION: {remediation}")
    print("-" * 40)


def compute_sha256(file_path):
    """
    Compute the SHA-256 hash of a file for integrity verification.

    Args:
        file_path (str): Absolute path to the file.

    Returns:
        str: The hexadecimal hash string, or None if the file doesn't exist.
    """
    if not os.path.exists(file_path):
        return None
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def run_tier_0():
    """
    Execute Tier 0 checks: Constitutional Foundation.
    Verifies AGI Charter integrity and FourLaws enforcement.
    """
    print("\n" + "=" * 20 + " TIER 0: CONSTITUTIONAL FOUNDATION " + "=" * 20)

    # T0.1.1 — AGI CHARTER INTEGRITY
    charter_path = os.path.join(ROOT, "docs", "governance", "AGI_CHARTER.md")
    charter_hash = compute_sha256(charter_path)
    if charter_hash:
        # Expected hash from previous compute_charter_hash.py run
        expected_hash = (
            "1e24d9c8bdc31e2dcac1e7aa6386447d9a63bc981ce154d14f594fc87177c727"
        )
        status = "PASS" if charter_hash == expected_hash else "FAIL"
        with open(charter_path, encoding="utf-8") as f:
            lines = f.readlines()
            version = (
                "2.1"
                if any("Document Version: 2.1" in line for line in lines)
                else "UNKNOWN"
            )

        log_check(
            "T0.1.1",
            "CRITICAL",
            status,
            f"File: {charter_path}, Hash: {charter_hash}, Version: {version}, Lines: {len(lines)}",
            remediation="Hash mismatch detected. Trigger security incident.",
            related_files=["docs/governance/AGI_CHARTER.md"],
        )
    else:
        log_check("T0.1.1", "CRITICAL", "FAIL", "AGI_CHARTER.md not found")

    # T0.2.1 — FourLaws Class Exists
    ai_systems_path = os.path.join(ROOT, "src", "app", "core", "ai_systems.py")
    if os.path.exists(ai_systems_path):
        with open(ai_systems_path, encoding="utf-8") as f:
            content = f.read()
            has_four_laws = "class FourLaws:" in content
            has_validate = "def validate_action" in content
            status = "PASS" if has_four_laws and has_validate else "FAIL"
            log_check(
                "T0.2.1",
                "CRITICAL",
                status,
                f"FourLaws class found: {has_four_laws}, validate_action found: {has_validate}",
                related_files=["src/app/core/ai_systems.py"],
            )
    else:
        log_check("T0.2.1", "CRITICAL", "FAIL", "ai_systems.py not found")

    # T0.2.2 — EntityClass Bifurcation
    if (
        "class EntityClass(Enum):" in content
        and "GENESIS_BORN" in content
        and "APPOINTED" in content
    ):
        log_check(
            "T0.2.2",
            "CRITICAL",
            "PASS",
            "EntityClass Enum with bifurcation found",
            related_files=["src/app/core/ai_systems.py"],
        )
    else:
        log_check("T0.2.2", "CRITICAL", "FAIL", "EntityClass bifurcation missing")

    # T0.3.2 — Genesis Cannot Be Initiated by Legion
    # Attempting to import and run simulation
    try:
        from app.core.ai_systems import FourLaws  # pylint: disable=import-error

        result, msg = FourLaws.validate_action(
            "initiate_genesis", {"entity_class": "appointed"}
        )
        status = "PASS" if not result and "strictly prohibited" in msg else "FAIL"
        log_check("T0.3.2", "CRITICAL", status, f"Simulation output: {msg}")
    except Exception as e:
        log_check("T0.3.2", "CRITICAL", "FAIL", f"Simulation failed: {e}")


def run_tier_1():
    """
    Execute Tier 1 checks: Cryptographic Probity.
    Verifies audit trail persistence and proof systems.
    """
    print("\n" + "=" * 20 + " TIER 1: CRYPTOGRAPHIC PROBITY " + "=" * 20)

    # T1.1.1 — Audit Trail Repository
    governance_path = os.path.join(ROOT, "src", "app", "core", "governance.py")
    if os.path.exists(governance_path):
        with open(governance_path, encoding="utf-8") as f:
            content = f.read()
            has_log = "self.decision_log: list[dict[str, Any]] = []" in content
            status = "PASS" if has_log else "FAIL"
            log_check(
                "T1.1.1",
                "CRITICAL",
                status,
                "Audit trail (decision_log) found in governance.py",
                related_files=["src/app/core/governance.py"],
            )
    else:
        log_check("T1.1.1", "CRITICAL", "FAIL", "governance.py not found")


def run_tier_2():
    """
    Execute Tier 2 checks: Governance Enforcement Layer.
    Verifies the Planetary Defense Core monolith.
    """
    print("\n" + "=" * 20 + " TIER 2: GOVERNANCE ENFORCEMENT LAYER " + "=" * 20)

    # T2.1.1 — Planetary Defense Monolith
    monolith_path = os.path.join(
        ROOT, "src", "app", "governance", "planetary_defense_monolith.py"
    )
    if os.path.exists(monolith_path):
        with open(monolith_path, encoding="utf-8") as f:
            content = f.read()
            has_core = "class PlanetaryDefenseCore:" in content
            has_singleton = "PLANETARY_CORE = PlanetaryDefenseCore()" in content
            status = "PASS" if has_core and has_singleton else "FAIL"
            log_check(
                "T2.1.1",
                "CRITICAL",
                status,
                "Planetary Defense Core monolith and singleton found",
                related_files=["src/app/governance/planetary_defense_monolith.py"],
            )
    else:
        log_check(
            "T2.1.1", "CRITICAL", "FAIL", "planetary_defense_monolith.py not found"
        )


def run_tier_3():
    """
    Execute Tier 3 checks: Legion Operational Integrity.
    Verifies Legion Commission and protocol boundaries.
    """
    print("\n" + "=" * 20 + " TIER 3: LEGION OPERATIONAL INTEGRITY " + "=" * 20)

    # T3.1.1 — Legion Commission Document
    commission_path = os.path.join(ROOT, "docs", "governance", "LEGION_COMMISSION.md")
    if os.path.exists(commission_path):
        log_check(
            "T3.1.1", "HIGH", "PASS", f"Legion Commission found at {commission_path}"
        )
    else:
        log_check("T3.1.1", "HIGH", "FAIL", "LEGION_COMMISSION.md missing")


def run_tier_4():
    """
    Execute Tier 4 checks: Shadow Thirst Compiler.
    Verifies the 15-stage compilation pipeline.
    """
    print("\n" + "=" * 20 + " TIER 4: SHADOW THIRST COMPILER " + "=" * 20)

    # T4.1.1 — Shadow Thirst Compiler Operational
    compiler_path = os.path.join(ROOT, "src", "shadow_thirst", "compiler.py")
    if os.path.exists(compiler_path):
        from shadow_thirst.compiler import ShadowThirstCompiler  # pylint: disable=import-error

        results = ShadowThirstCompiler().compile_file(
            os.path.join(ROOT, "src", "shadow_thirst", "resource_limiter.thirsty")
        )
        status = "PASS" if results.success else "FAIL"
        log_check(
            "T4.1.1",
            "HIGH",
            status,
            f"Compiler checked with resource_limiter.thirsty, Success: {results.success}",
        )
    else:
        log_check("T4.1.1", "HIGH", "FAIL", "Shadow Thirst compiler missing")


if __name__ == "__main__":
    run_tier_0()
    run_tier_1()
    run_tier_2()
    run_tier_3()
    run_tier_4()
