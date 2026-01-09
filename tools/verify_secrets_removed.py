#!/usr/bin/env python3
"""
Verify that secrets have been removed from git tracking and history.
Run this script after cleaning git history to ensure secrets are gone.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str]:
    """Run a shell command and return exit code and output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode, result.stdout
    except Exception as e:
        return 1, str(e)


def check_git_tracking() -> bool:
    """Check if sensitive files are in git tracking."""
    print("🔍 Checking git tracking...")
    
    sensitive_patterns = [".env", ".vs/"]
    issues = []
    
    for pattern in sensitive_patterns:
        code, output = run_command(["git", "ls-files", pattern])
        if output.strip():
            issues.append(f"  ❌ {pattern} is still tracked in git")
            for line in output.strip().split("\n"):
                issues.append(f"     - {line}")
    
    if issues:
        print("\n".join(issues))
        return False
    
    print("  ✅ No sensitive files in git tracking")
    return True


def check_git_history() -> bool:
    """Check if sensitive files exist in git history."""
    print("\n🔍 Checking git history...")
    
    sensitive_files = [".env", ".vs"]
    issues = []
    
    for file in sensitive_files:
        code, output = run_command(["git", "log", "--all", "--oneline", "--", file])
        if output.strip():
            issues.append(f"  ❌ {file} found in git history")
            issues.append(f"     Commits: {output.strip()}")
    
    if issues:
        print("\n".join(issues))
        return False
    
    print("  ✅ No sensitive files in git history")
    return True


def check_gitignore() -> bool:
    """Check if .gitignore has necessary patterns."""
    print("\n🔍 Checking .gitignore...")
    
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("  ❌ .gitignore not found")
        return False
    
    content = gitignore_path.read_text()
    required_patterns = [
        ".env",
        ".vs/",
        "*.key",
        "*.pem",
    ]
    
    issues = []
    for pattern in required_patterns:
        if pattern not in content:
            issues.append(f"  ❌ Pattern '{pattern}' not in .gitignore")
    
    if issues:
        print("\n".join(issues))
        return False
    
    print("  ✅ .gitignore has required patterns")
    return True


def check_env_file() -> bool:
    """Check if .env file is sanitized."""
    print("\n🔍 Checking .env file...")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("  ℹ️  .env file not found (this is OK if using environment variables)")
        return True
    
    content = env_path.read_text()
    
    # Check for patterns that look like real secrets
    suspicious_patterns = [
        ("sk-proj-", "OpenAI API key"),
        ("hf_", "Hugging Face token"),
        ("@gmail.com", "Gmail address"),
        ("AKIA", "AWS access key"),
    ]
    
    issues = []
    for pattern, description in suspicious_patterns:
        if pattern in content:
            # Check if it's just on a line with an equals sign and nothing after
            for line in content.split("\n"):
                if pattern in line and "=" in line:
                    parts = line.split("=", 1)
                    # Check if there's a value after the equals sign (not just whitespace or angle brackets)
                    if len(parts) > 1 and parts[1].strip() and not parts[1].strip().startswith(('<', '>')):
                        issues.append(f"  ⚠️  Potential {description} found in .env")
    
    if issues:
        print("\n".join(issues))
        print("  ⚠️  Please verify .env contains only placeholder values")
        return False
    
    print("  ✅ .env file appears sanitized")
    return True


def main():
    """Main verification function."""
    print("=" * 60)
    print("🔐 Secret Verification Tool")
    print("=" * 60)
    print()
    
    # Change to repository root
    try:
        subprocess.run(["git", "rev-parse", "--git-dir"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ Not in a git repository")
        sys.exit(1)
    
    results = []
    results.append(check_git_tracking())
    results.append(check_git_history())
    results.append(check_gitignore())
    results.append(check_env_file())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL CHECKS PASSED")
        print("=" * 60)
        print("\n✨ Repository appears clean of secrets!")
        print("\nNext steps:")
        print("1. Ensure all exposed credentials have been rotated")
        print("2. Update your local .env with NEW credentials")
        print("3. Test the application with new credentials")
        sys.exit(0)
    else:
        print("❌ SOME CHECKS FAILED")
        print("=" * 60)
        print("\n⚠️  Issues found - please address them before proceeding")
        print("\nSee CREDENTIAL_ROTATION_REQUIRED.md for detailed instructions")
        sys.exit(1)


if __name__ == "__main__":
    main()
