#!/usr/bin/env python3
"""
Integration validation script for The_Triumvirate.

This script validates that the Project-AI repository is properly configured
to integrate The_Triumvirate when it becomes available.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


class Colors:
    """Terminal colors for output."""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_header(message):
    """Print a header message."""
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}{message}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")


def print_success(message):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.NC}")


def print_error(message):
    """Print an error message."""
    print(f"{Colors.RED}✗ {message}{Colors.NC}")


def print_warning(message):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.NC}")


def print_info(message):
    """Print an info message."""
    print(f"{Colors.BLUE}ℹ {message}{Colors.NC}")


def check_file_exists(file_path, description):
    """Check if a file exists."""
    if Path(file_path).exists():
        print_success(f"{description}: {file_path}")
        return True
    else:
        print_error(f"{description} not found: {file_path}")
        return False


def check_file_contains(file_path, search_text, description):
    """Check if a file contains specific text."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_text in content:
                print_success(f"{description}: Found in {file_path}")
                return True
            else:
                print_warning(f"{description}: Not found in {file_path}")
                return False
    except Exception as e:
        print_error(f"Error reading {file_path}: {e}")
        return False


def validate_documentation():
    """Validate that documentation files exist."""
    print_header("Validating Documentation")
    
    files = {
        "TRIUMVIRATE_INTEGRATION.md": "Main integration guide",
        "web/README.md": "Web quick start guide",
        "web/triumvirate/README.md": "Triumvirate placeholder",
        "README.md": "Main README (should mention Triumvirate)"
    }
    
    results = []
    for file_path, description in files.items():
        results.append(check_file_exists(file_path, description))
    
    # Check README mentions Triumvirate
    if Path("README.md").exists():
        results.append(
            check_file_contains(
                "README.md",
                "Triumvirate",
                "README mentions Triumvirate"
            )
        )
    
    return all(results)


def validate_configuration():
    """Validate configuration files."""
    print_header("Validating Configuration Files")
    
    results = []
    
    # Check .env.example
    if Path(".env.example").exists():
        checks = [
            ("ENABLE_TRIUMVIRATE", ".env.example has ENABLE_TRIUMVIRATE"),
            ("VITE_API_URL", ".env.example has VITE_API_URL"),
            ("TRIUMVIRATE_PORT", ".env.example has TRIUMVIRATE_PORT"),
        ]
        for text, description in checks:
            results.append(check_file_contains(".env.example", text, description))
    else:
        print_error(".env.example not found")
        results.append(False)
    
    # Check config/triumvirate.json
    if Path("config/triumvirate.json").exists():
        try:
            with open("config/triumvirate.json", 'r') as f:
                config = json.load(f)
                if "triumvirate" in config:
                    print_success("config/triumvirate.json is valid JSON")
                    results.append(True)
                else:
                    print_error("config/triumvirate.json missing 'triumvirate' key")
                    results.append(False)
        except json.JSONDecodeError as e:
            print_error(f"config/triumvirate.json is invalid JSON: {e}")
            results.append(False)
    else:
        print_error("config/triumvirate.json not found")
        results.append(False)
    
    # Check .gitignore
    if Path(".gitignore").exists():
        checks = [
            ("web/triumvirate/node_modules/", ".gitignore excludes node_modules"),
            ("web/triumvirate/dist/", ".gitignore excludes dist"),
        ]
        for text, description in checks:
            results.append(check_file_contains(".gitignore", text, description))
    else:
        print_error(".gitignore not found")
        results.append(False)
    
    return all(results)


def validate_scripts():
    """Validate integration scripts."""
    print_header("Validating Scripts")
    
    results = []
    
    # Check integration script exists and is executable
    script_path = "scripts/integrate_triumvirate.sh"
    if Path(script_path).exists():
        print_success(f"Integration script exists: {script_path}")
        
        # Check if executable
        if os.access(script_path, os.X_OK):
            print_success("Integration script is executable")
            results.append(True)
        else:
            print_warning("Integration script is not executable (may need chmod +x)")
            results.append(True)  # Not critical
        
        # Check script has main function
        results.append(
            check_file_contains(
                script_path,
                "main() {",
                "Script has main function"
            )
        )
    else:
        print_error(f"Integration script not found: {script_path}")
        results.append(False)
    
    return all(results)


def validate_package_json():
    """Validate package.json has Triumvirate scripts."""
    print_header("Validating package.json")
    
    results = []
    
    if not Path("package.json").exists():
        print_error("package.json not found")
        return False
    
    try:
        with open("package.json", 'r') as f:
            package = json.load(f)
            
        scripts = package.get("scripts", {})
        
        required_scripts = [
            "triumvirate:install",
            "triumvirate:dev",
            "triumvirate:build",
            "web:backend",
            "web:full"
        ]
        
        for script in required_scripts:
            if script in scripts:
                print_success(f"Script '{script}' exists")
                results.append(True)
            else:
                print_error(f"Script '{script}' missing")
                results.append(False)
        
    except json.JSONDecodeError as e:
        print_error(f"package.json is invalid JSON: {e}")
        return False
    
    return all(results)


def validate_docker_compose():
    """Validate Docker Compose configuration."""
    print_header("Validating Docker Compose")
    
    results = []
    
    # Check docker-compose.triumvirate.yml exists
    results.append(
        check_file_exists(
            "docker-compose.triumvirate.yml",
            "Triumvirate Docker Compose file"
        )
    )
    
    # Check it mentions triumvirate service
    if Path("docker-compose.triumvirate.yml").exists():
        results.append(
            check_file_contains(
                "docker-compose.triumvirate.yml",
                "triumvirate-frontend",
                "Docker Compose has triumvirate-frontend service"
            )
        )
    
    return all(results)


def validate_backend():
    """Validate Flask backend updates."""
    print_header("Validating Flask Backend")
    
    results = []
    
    backend_file = "web/backend/app.py"
    
    if not Path(backend_file).exists():
        print_error(f"Backend file not found: {backend_file}")
        return False
    
    # Check for CORS support
    checks = [
        ("ENABLE_TRIUMVIRATE", "Backend has ENABLE_TRIUMVIRATE flag"),
        ("CORS_ORIGINS", "Backend has CORS_ORIGINS configuration"),
        ("add_cors_headers", "Backend has CORS middleware"),
    ]
    
    for text, description in checks:
        results.append(check_file_contains(backend_file, text, description))
    
    # Verify Python syntax
    try:
        subprocess.run(
            ["python", "-m", "py_compile", backend_file],
            check=True,
            capture_output=True
        )
        print_success("Backend Python syntax is valid")
        results.append(True)
    except subprocess.CalledProcessError:
        print_error("Backend has Python syntax errors")
        results.append(False)
    except FileNotFoundError:
        print_warning("Python not available for syntax check")
    
    return all(results)


def validate_gitmodules():
    """Validate .gitmodules preparation."""
    print_header("Validating Git Submodules")
    
    results = []
    
    if Path(".gitmodules").exists():
        print_success(".gitmodules file exists")
        
        # Check for Triumvirate reference (commented or uncommented)
        with open(".gitmodules", 'r') as f:
            content = f.read()
            if "triumvirate" in content.lower():
                print_success(".gitmodules prepared for Triumvirate")
                results.append(True)
            else:
                print_warning(".gitmodules exists but no Triumvirate reference")
                results.append(True)  # Not critical
    else:
        print_warning(".gitmodules not found")
        results.append(True)  # Not critical
    
    return all(results)


def run_validation():
    """Run all validation checks."""
    print_header("Project-AI Triumvirate Integration Validation")
    print_info("Validating integration readiness...")
    
    # Change to project root if needed
    if not Path("README.md").exists():
        print_error("Please run this script from the Project-AI root directory")
        return False
    
    results = {
        "Documentation": validate_documentation(),
        "Configuration": validate_configuration(),
        "Scripts": validate_scripts(),
        "Package.json": validate_package_json(),
        "Docker Compose": validate_docker_compose(),
        "Backend": validate_backend(),
        "Git Submodules": validate_gitmodules()
    }
    
    # Summary
    print_header("Validation Summary")
    
    all_passed = all(results.values())
    
    for category, passed in results.items():
        if passed:
            print_success(f"{category}: PASSED")
        else:
            print_error(f"{category}: FAILED")
    
    print()
    if all_passed:
        print_success("✅ All validation checks passed!")
        print_info("The repository is ready for Triumvirate integration.")
        print_info("Run: ./scripts/integrate_triumvirate.sh when The_Triumvirate is available")
        return True
    else:
        print_error("❌ Some validation checks failed")
        print_info("Please review the errors above and fix them")
        return False


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
