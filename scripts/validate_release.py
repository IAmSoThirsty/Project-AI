#!/usr/bin/env python3
"""
Release Validation Script for Project-AI
Validates that a release package contains all required artifacts and dependencies.
"""

import json
import sys
from pathlib import Path

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class ReleaseValidator:
    """Validates Project-AI release packages."""

    def __init__(self, release_dir: str, version: str = "1.0.0"):
        self.release_dir = Path(release_dir)
        self.version = version
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def validate_all(self) -> tuple[bool, dict]:
        """Run all validations and return results."""
        # Only print if not in JSON mode (checked later in main)
        if not hasattr(self, "_json_mode"):
            self._json_mode = False

        if not self._json_mode:
            print(f"\n{BLUE}{'=' * 70}{RESET}")
            print(f"{BLUE}Project-AI v{self.version} Release Validation{RESET}")
            print(f"{BLUE}{'=' * 70}{RESET}\n")
            print(f"📦 Release directory: {self.release_dir}\n")

        # Run validation checks
        self._validate_directory_structure()
        self._validate_backend()
        self._validate_web()
        self._validate_android()
        self._validate_desktop()
        self._validate_docs()
        self._validate_manifest()
        self._validate_dependencies()

        # Generate report
        report = self._generate_report()

        if not self._json_mode:
            self._print_summary()

        return len(self.errors) == 0, report

    def _validate_directory_structure(self):
        """Validate basic directory structure."""
        if not self._json_mode:
            print(f"{BLUE}[1/8] Validating directory structure...{RESET}")

        required_dirs = ["backend", "web", "android", "desktop", "docs"]

        for dir_name in required_dirs:
            dir_path = self.release_dir / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.info.append(f"✓ Found directory: {dir_name}/")
                if not self._json_mode:
                    print(f"  {GREEN}✓{RESET} {dir_name}/")
            else:
                self.warnings.append(f"Missing directory: {dir_name}/")
                if not self._json_mode:
                    print(f"  {YELLOW}⚠{RESET} {dir_name}/ (missing)")

    def _validate_backend(self):
        """Validate backend artifacts."""
        if not self._json_mode:
            print(f"\n{BLUE}[2/8] Validating backend...{RESET}")

        backend_dir = self.release_dir / "backend"
        if not backend_dir.exists():
            self.errors.append("Backend directory missing")
            if not self._json_mode:
                print(f"  {RED}✗{RESET} Backend directory not found")
            return

        # Check required files and directories
        required_items = [
            ("api", True),
            ("tarl", True),
            ("config", True),
            ("governance", True),
            ("start_api.py", False),
            ("requirements.txt", False),
            (".env", False),
            ("start.sh", False),
            ("start.bat", False),
        ]

        for item_name, is_dir in required_items:
            item_path = backend_dir / item_name
            if item_path.exists():
                if is_dir and item_path.is_dir():
                    if not self._json_mode:
                        print(f"  {GREEN}✓{RESET} {item_name}/")
                elif not is_dir and item_path.is_file():
                    if not self._json_mode:
                        print(f"  {GREEN}✓{RESET} {item_name}")
                else:
                    self.errors.append(
                        f"Backend: {item_name} type mismatch (expected {'dir' if is_dir else 'file'})"
                    )
                    if not self._json_mode:
                        print(f"  {RED}✗{RESET} {item_name} (type mismatch)")
            else:
                self.errors.append(f"Backend: Missing {item_name}")
                if not self._json_mode:
                    print(f"  {RED}✗{RESET} {item_name} (missing)")

    def _validate_web(self):
        """Validate web frontend artifacts."""
        if not self._json_mode:
            print(f"\n{BLUE}[3/8] Validating web frontend...{RESET}")

        web_dir = self.release_dir / "web"
        if not web_dir.exists():
            self.warnings.append("Web directory missing")
            if not self._json_mode:
                print(f"  {YELLOW}⚠{RESET} Web directory not found")
            return

        # Check for essential web files
        essential_files = ["index.html"]
        for file_name in essential_files:
            file_path = web_dir / file_name
            if file_path.exists():
                if not self._json_mode:
                    print(f"  {GREEN}✓{RESET} {file_name}")
            else:
                self.warnings.append(f"Web: Missing {file_name}")
                if not self._json_mode:
                    print(f"  {YELLOW}⚠{RESET} {file_name} (missing)")

        # Check if DEPLOY.md exists
        if (web_dir / "DEPLOY.md").exists():
            if not self._json_mode:
                print(f"  {GREEN}✓{RESET} DEPLOY.md")
        else:
            self.info.append("Web: DEPLOY.md not found")

    def _validate_android(self):
        """Validate Android artifacts."""
        if not self._json_mode:
            print(f"\n{BLUE}[4/8] Validating Android app...{RESET}")

        android_dir = self.release_dir / "android"
        if not android_dir.exists():
            self.warnings.append("Android directory missing")
            if not self._json_mode:
                print(f"  {YELLOW}⚠{RESET} Android directory not found")
            return

        # Check for APK
        apk_found = False
        for apk_file in android_dir.glob("*.apk"):
            apk_found = True
            size = apk_file.stat().st_size / (1024 * 1024)
            if not self._json_mode:
                print(f"  {GREEN}✓{RESET} {apk_file.name} ({size:.2f} MB)")

        if not apk_found:
            self.warnings.append("Android: No APK found")
            if not self._json_mode:
                print(f"  {YELLOW}⚠{RESET} No APK files found")

        # Check for INSTALL.md
        if (android_dir / "INSTALL.md").exists():
            if not self._json_mode:
                print(f"  {GREEN}✓{RESET} INSTALL.md")
        else:
            self.info.append("Android: INSTALL.md not found")

    def _validate_desktop(self):
        """Validate desktop artifacts."""
        if not self._json_mode:
            print(f"\n{BLUE}[5/8] Validating desktop apps...{RESET}")

        desktop_dir = self.release_dir / "desktop"
        if not desktop_dir.exists():
            self.warnings.append("Desktop directory missing")
            if not self._json_mode:
                print(f"  {YELLOW}⚠{RESET} Desktop directory not found")
            return

        # Check for any desktop build artifacts
        installers_found = False
        patterns = ["*.exe", "*.dmg", "*.AppImage", "*.deb", "*.rpm"]

        for pattern in patterns:
            for installer in desktop_dir.glob(pattern):
                installers_found = True
                size = installer.stat().st_size / (1024 * 1024)
                if not self._json_mode:
                    print(f"  {GREEN}✓{RESET} {installer.name} ({size:.2f} MB)")

        if not installers_found:
            self.warnings.append("Desktop: No installers found")
            if not self._json_mode:
                print(f"  {YELLOW}⚠{RESET} No desktop installers found")

        # Check for INSTALL.md
        if (desktop_dir / "INSTALL.md").exists():
            if not self._json_mode:
                print(f"  {GREEN}✓{RESET} INSTALL.md")
        else:
            self.info.append("Desktop: INSTALL.md not found")

    def _validate_docs(self):
        """Validate documentation."""
        if not self._json_mode:
            print(f"\n{BLUE}[6/8] Validating documentation...{RESET}")

        # Check root-level docs
        required_docs = [
            "README.md",
            "CONSTITUTION.md",
            "CHANGELOG.md",
            "LICENSE",
            "SECURITY.md",
        ]

        for doc_name in required_docs:
            doc_path = self.release_dir / doc_name
            if doc_path.exists():
                if not self._json_mode:
                    print(f"  {GREEN}✓{RESET} {doc_name}")
            else:
                self.warnings.append(f"Documentation: Missing {doc_name}")
                if not self._json_mode:
                    print(f"  {YELLOW}⚠{RESET} {doc_name} (missing)")

        # Check docs directory
        docs_dir = self.release_dir / "docs"
        if docs_dir.exists() and docs_dir.is_dir():
            doc_count = len(list(docs_dir.glob("**/*.md")))
            if not self._json_mode:
                print(f"  {GREEN}✓{RESET} docs/ directory ({doc_count} files)")
        else:
            self.warnings.append("docs/ directory missing")
            if not self._json_mode:
                print(f"  {YELLOW}⚠{RESET} docs/ directory (missing)")

    def _validate_manifest(self):
        """Validate against MANIFEST.in."""
        if not self._json_mode:
            print(f"\n{BLUE}[7/8] Validating against MANIFEST.in...{RESET}")

        # Find MANIFEST.in in project root (parent of release dir)
        manifest_path = Path(__file__).parent.parent / "MANIFEST.in"

        if not manifest_path.exists():
            self.warnings.append("MANIFEST.in not found")
            if not self._json_mode:
                print(f"  {YELLOW}⚠{RESET} MANIFEST.in not found in project root")
            return

        # Just verify we can read it
        try:
            with open(manifest_path) as f:
                lines = f.readlines()
            if not self._json_mode:
                print(f"  {GREEN}✓{RESET} MANIFEST.in readable ({len(lines)} lines)")
        except Exception as e:
            self.errors.append(f"MANIFEST.in read error: {e}")
            if not self._json_mode:
                print(f"  {RED}✗{RESET} Failed to read MANIFEST.in")

    def _validate_dependencies(self):
        """Check for dependency files."""
        if not self._json_mode:
            print(f"\n{BLUE}[8/8] Validating dependencies...{RESET}")

        backend_dir = self.release_dir / "backend"
        if backend_dir.exists():
            req_file = backend_dir / "requirements.txt"
            if req_file.exists():
                try:
                    with open(req_file) as f:
                        deps = [
                            line.strip()
                            for line in f
                            if line.strip() and not line.startswith("#")
                        ]
                    if not self._json_mode:
                        print(
                            f"  {GREEN}✓{RESET} Backend requirements.txt ({len(deps)} dependencies)"
                        )
                except Exception as e:
                    self.warnings.append(f"Could not parse requirements.txt: {e}")
            else:
                self.errors.append("Backend requirements.txt missing")

    def _generate_report(self) -> dict:
        """Generate validation report."""
        return {
            "version": self.version,
            "release_directory": str(self.release_dir),
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "validation_passed": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "summary": {
                "total_checks": (
                    len(self.errors) + len(self.warnings) + len(self.info)
                ),
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "info": len(self.info),
            },
        }

    def _print_summary(self):
        """Print validation summary."""
        print(f"\n{BLUE}{'=' * 70}{RESET}")
        print(f"{BLUE}Validation Summary{RESET}")
        print(f"{BLUE}{'=' * 70}{RESET}\n")

        # Errors
        if self.errors:
            print(f"{RED}✗ ERRORS ({len(self.errors)}):{RESET}")
            for error in self.errors:
                print(f"  • {error}")
            print()

        # Warnings
        if self.warnings:
            print(f"{YELLOW}⚠ WARNINGS ({len(self.warnings)}):{RESET}")
            for warning in self.warnings:
                print(f"  • {warning}")
            print()

        # Result
        if len(self.errors) == 0:
            print(f"{GREEN}✓ VALIDATION PASSED{RESET}")
            print(
                f"\nRelease package is ready for distribution with {len(self.warnings)} warning(s)."
            )
        else:
            print(f"{RED}✗ VALIDATION FAILED{RESET}")
            print(
                f"\nRelease package has {len(self.errors)} error(s) that must be fixed."
            )

        print()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate Project-AI release package")
    parser.add_argument(
        "release_dir",
        nargs="?",
        default="releases/project-ai-v1.0.0",
        help="Path to release directory (default: releases/project-ai-v1.0.0)",
    )
    parser.add_argument(
        "--version", default="1.0.0", help="Version number (default: 1.0.0)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON report instead of human-readable format",
    )
    parser.add_argument(
        "--output", "-o", help="Write JSON report to file (implies --json)"
    )

    args = parser.parse_args()

    # Create validator
    validator = ReleaseValidator(args.release_dir, args.version)
    validator._json_mode = args.json or args.output is not None

    # Run validation
    passed, report = validator.validate_all()

    # Output JSON if requested
    if args.json or args.output:
        json_output = json.dumps(report, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(json_output)
            if not args.json:
                # Only print message if not in JSON-to-stdout mode
                print(f"\n📄 Report written to: {args.output}")
        else:
            print(json_output)

    # Exit with appropriate code
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
