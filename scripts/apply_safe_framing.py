#!/usr/bin/env python3
"""
Apply Safe Framing to Whitepapers

Automatically updates whitepapers to comply with Security Validation Claims Policy
by replacing prohibited claims with approved framing language and adding validation
status disclaimers.

Usage:
    python scripts/apply_safe_framing.py --preview  # Show changes without applying
    python scripts/apply_safe_framing.py --apply    # Apply changes to files
    python scripts/apply_safe_framing.py --file docs/whitepapers/SPECIFIC.md --apply

This script implements Option 2 from PRODUCTION_READINESS_COMPLIANCE_REPORT.md
"""

import argparse
import glob
import re
import sys
from pathlib import Path
from typing import List, Tuple

DISCLAIMER_TEMPLATE = """---

## Validation Status Disclaimer

**Document Classification:** Technical Specification

This whitepaper describes the design, architecture, and implementation of the system. The information presented represents:

- ✅ **Code Complete:** Implementation finished, unit tests passing
- ✅ **Configuration Validated:** Automated tests confirm configuration correctness
- 🔄 **Runtime Validation:** Full adversarial validation is ongoing
- 🔄 **Production Hardening:** Security controls align with enterprise hardening patterns

### Important Notes

1. **Not Production-Certified:** This system has not completed the full runtime validation protocol required for production-ready certification as defined in `.github/SECURITY_VALIDATION_POLICY.md`.

2. **Design Intent:** All security features, enforcement capabilities, and operational metrics described represent design intent and implementation goals. Actual runtime behavior should be independently validated in your specific deployment environment.

3. **Ongoing Validation:** The Project-AI team is actively conducting adversarial testing and runtime validation. This section will be updated as validation milestones are achieved.

4. **Use at Your Own Risk:** Organizations deploying this system should conduct their own comprehensive security assessments, penetration testing, and operational validation before production use.

5. **Metrics Context:** Any performance or reliability metrics mentioned (e.g., uptime percentages, latency measurements, readiness scores) are based on development environment testing and may not reflect production performance.

**Validation Status:** In Progress
**Last Updated:** 2026-02-20
**Next Review:** Upon completion of runtime validation protocol

For the complete validation protocol requirements, see `.github/SECURITY_VALIDATION_POLICY.md`.

---
"""


class SafeFramingTransformer:
    """Transforms whitepapers to use safe framing language"""

    def __init__(self):
        self.replacements = [
            # Status field replacements
            (
                re.compile(
                    r"\*\*Status:\*\*\s+Production\s+Implementation", re.IGNORECASE
                ),
                "**Status:** Technical Specification (Implementation Complete, Validation Ongoing)",
            ),
            (
                re.compile(
                    r"\*\*Status:\*\*\s+Production\s+Integration", re.IGNORECASE
                ),
                "**Status:** Technical Specification (Integration Complete, Validation Ongoing)",
            ),
            # Production-ready replacements
            (
                re.compile(
                    r"Production-[Rr]eady:\s+(\d+/100\s+readiness\s+score,\s+[\d.]+%\s+uptime,\s+P\d+\s+latency\s+\d+ms)"
                ),
                r"Implementation Status: Development complete with \1. Full operational validation ongoing.",
            ),
            (
                re.compile(r"### Desktop Application \(Production-Ready\)"),
                "### Desktop Application (Feature Complete, Validation Ongoing)",
            ),
            (
                re.compile(r"Production-ready,\s+(\d+/100\s+readiness\s+score)"),
                r"Development complete, \1, full production hardening in progress",
            ),
            (
                re.compile(r"Production-ready implementation"),
                "Full implementation (runtime validation ongoing)",
            ),
            # Runtime enforcement replacements
            (
                re.compile(r"^(\s*)(2\.\s+Runtime\s+Enforcement:)", re.MULTILINE),
                r"\1\2 (Implementation Complete)",
            ),
            (
                re.compile(r"We bring runtime enforcement of"),
                "This system implements runtime enforcement of",
            ),
            (
                re.compile(
                    r"runtime enforcement of formally-specified invariants to general-purpose systems\."
                ),
                "runtime enforcement of formally-specified invariants to general-purpose systems (implementation complete, adversarial validation ongoing).",
            ),
            # Specific metric replacements
            (
                re.compile(r"(\d+\.\d+%\s+uptime)"),
                r"High availability design (target: \1, operational validation ongoing)",
            ),
            (
                re.compile(r"(\d+/100)\s+production\s+score"),
                r"\1 configuration validation score",
            ),
        ]

    def transform_content(self, content: str, filename: str) -> Tuple[str, List[str]]:
        """
        Transform content to use safe framing language

        Returns:
            Tuple of (transformed_content, list_of_changes_made)
        """
        changes = []
        new_content = content

        # Apply replacements
        for pattern, replacement in self.replacements:
            matches = list(pattern.finditer(new_content))
            if matches:
                new_content = pattern.sub(replacement, new_content)
                changes.append(
                    f"Replaced {len(matches)} instance(s) of: {pattern.pattern[:60]}..."
                )

        # Add disclaimer if not present
        if "## Validation Status Disclaimer" not in new_content:
            # Find insertion point (before References section or at end)
            if "## References" in new_content or "## 21. References" in new_content:
                # Insert before references
                new_content = re.sub(
                    r"(##\s+(?:\d+\.\s+)?References)",
                    DISCLAIMER_TEMPLATE + r"\n\1",
                    new_content,
                    count=1,
                )
                changes.append(
                    "Added Validation Status Disclaimer before References section"
                )
            else:
                # Append at end
                new_content = new_content.rstrip() + "\n\n" + DISCLAIMER_TEMPLATE
                changes.append("Added Validation Status Disclaimer at end of document")

        return new_content, changes

    def preview_changes(self, filepath: str) -> None:
        """Preview changes that would be made to a file"""
        print(f"\n{'='*80}")
        print(f"FILE: {filepath}")
        print(f"{'='*80}")

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                original_content = f.read()
        except Exception as e:
            print(f"ERROR: Cannot read file: {e}")
            return

        new_content, changes = self.transform_content(original_content, filepath)

        if not changes:
            print("✅ No changes needed - already compliant")
            return

        print(f"\n{len(changes)} change(s) will be made:\n")
        for i, change in enumerate(changes, 1):
            print(f"  {i}. {change}")

        # Show diff statistics
        original_lines = original_content.count("\n")
        new_lines = new_content.count("\n")
        diff_lines = new_lines - original_lines

        print(f"\nStatistics:")
        print(f"  Original lines: {original_lines}")
        print(f"  New lines: {new_lines}")
        print(f"  Difference: {diff_lines:+d} lines")

    def apply_changes(self, filepath: str, dry_run: bool = False) -> bool:
        """Apply safe framing changes to a file"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                original_content = f.read()
        except Exception as e:
            print(f"ERROR: Cannot read {filepath}: {e}")
            return False

        new_content, changes = self.transform_content(original_content, filepath)

        if not changes:
            print(f"✅ {filepath}: No changes needed")
            return True

        if not dry_run:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"✅ {filepath}: {len(changes)} change(s) applied")
                return True
            except Exception as e:
                print(f"ERROR: Cannot write {filepath}: {e}")
                return False
        else:
            print(f"🔍 {filepath}: Would apply {len(changes)} change(s) (dry-run)")
            return True


def main():
    parser = argparse.ArgumentParser(
        description="Apply safe framing to whitepapers for policy compliance"
    )
    parser.add_argument(
        "--preview", action="store_true", help="Preview changes without applying them"
    )
    parser.add_argument("--apply", action="store_true", help="Apply changes to files")
    parser.add_argument(
        "--file", help="Specific file to process (default: all whitepapers)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate applying changes without writing files",
    )

    args = parser.parse_args()

    if not args.preview and not args.apply and not args.dry_run:
        parser.print_help()
        print("\nERROR: Must specify --preview, --apply, or --dry-run")
        return 1

    # Determine files to process
    if args.file:
        files = [args.file]
    else:
        files = glob.glob("docs/whitepapers/*.md")

    if not files:
        print("ERROR: No whitepaper files found")
        return 1

    transformer = SafeFramingTransformer()

    print("=" * 80)
    print("SAFE FRAMING TRANSFORMER")
    print("=" * 80)
    print(
        f"\nMode: {'PREVIEW' if args.preview else 'APPLY' if args.apply else 'DRY-RUN'}"
    )
    print(f"Files: {len(files)}")
    print()

    # Preview mode
    if args.preview:
        for filepath in sorted(files):
            transformer.preview_changes(filepath)
        print("\n" + "=" * 80)
        print("To apply these changes, run with --apply")
        print("=" * 80)
        return 0

    # Apply mode
    success_count = 0
    for filepath in sorted(files):
        if transformer.apply_changes(filepath, dry_run=args.dry_run):
            success_count += 1

    print("\n" + "=" * 80)
    print(f"SUMMARY: {success_count}/{len(files)} files processed successfully")
    print("=" * 80)

    if args.apply and not args.dry_run:
        print("\n✅ Safe framing applied. Run validation to confirm:")
        print("   python scripts/validate_production_claims.py --all")

    return 0 if success_count == len(files) else 1


if __name__ == "__main__":
    sys.exit(main())
