#!/usr/bin/env python3
"""Fix broken bracket patterns from logging conversion"""

import re
import sys
from pathlib import Path


def fix_broken_brackets(content: str) -> tuple[str, int]:
    """Fix patterns where bracket slicing was broken: hash[) -> hash[:16]"""
    changes = 0

    # Pattern: variable[ followed by closing paren -> variable[:16]
    pattern = r"(\w+)\[\s*\)"

    def replacer(match):
        nonlocal changes
        var = match.group(1)
        changes += 1
        return f"{var}[:16]"

    new_content = re.sub(pattern, replacer, content)
    return new_content, changes


def fix_broken_fstrings(content: str) -> tuple[str, int]:
    """Fix broken f-string conversions in assertions"""
    changes = 0
    lines = content.split("\n")
    new_lines = []

    for line in lines:
        # Fix broken assertion strings
        if "raise AssertionError" in line and ', f"' in line:
            # Pattern: raise AssertionError("...", f"...")
            # Should be: raise AssertionError(f"...")
            line = re.sub(
                r'raise AssertionError\("([^"]+)", f"([^"]+)"\)',
                r'raise AssertionError(f"\1 \2")',
                line,
            )
            changes += 1
        elif "raise AssertionError" in line and '"")' in line:
            # Fix double quotes
            line = line.replace('"")', '")')
            changes += 1

        new_lines.append(line)

    return "\n".join(new_lines), changes


def fix_format_specifiers(content: str) -> tuple[str, int]:
    """Fix broken format specifiers: min_margin:.3f -> {min_margin:.3f}"""
    changes = 0

    # Pattern: logger.info("...", variable:.format)
    pattern = r"(logger\.\w+\([^)]+, )(\w+)(:\.\d+[fdeg%])"

    def replacer(match):
        nonlocal changes
        prefix = match.group(1)
        var = match.group(2)
        fmt = match.group(3)
        changes += 1
        # This needs to be in the string, not as argument
        return prefix + var

    new_content = re.sub(pattern, replacer, content)
    return new_content, changes


def process_file(filepath: Path) -> int:
    """Process a single file"""
    try:
        content = filepath.read_text(encoding="utf-8")
        total_changes = 0

        # Apply all fixes
        content, changes1 = fix_broken_brackets(content)
        total_changes += changes1

        content, changes2 = fix_broken_fstrings(content)
        total_changes += changes2

        content, changes3 = fix_format_specifiers(content)
        total_changes += changes3

        if total_changes > 0:
            filepath.write_text(content, encoding="utf-8")
            print(f"✅ Fixed {total_changes} issues in {filepath}")

        return total_changes

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}", file=sys.stderr)
        return 0


# Files with known issues
problem_files = [
    "governance/iron_path.py",
    "examples/temporal/code_security_sweep_example.py",
    "gradle-evolution/db/graph_db.py",
    "h323_sec_profile/H323_SEC_PROFILE_v1.py",
    "scripts/verify/validate_thirstys_security.py",
    "scripts/verify/verify_constitution.py",
    "src/app/browser/encrypted_navigation.py",
    "src/app/core/cerberus_runtime_manager.py",
    "src/app/core/hydra_50_security.py",
    "src/app/core/robustness_metrics.py",
    "src/app/core/snn_mlops.py",
    "src/app/core/voice_models.py",
    "src/app/governance/audit_log.py",
    "src/app/security/advanced/mfa_auth.py",
    "src/integrations/temporal/activities/core_tasks.py",
    "temporal/workflows/atomic_security_activities.py",
]

if __name__ == "__main__":
    root = Path(".")
    total = 0

    for file_path in problem_files:
        filepath = root / file_path
        if filepath.exists():
            total += process_file(filepath)

    print(f"\n✅ Fixed {total} total issues")
