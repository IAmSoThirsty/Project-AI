#!/usr/bin/env python3
"""
Health check script for Project AI services.
Verifies all components are running and accessible.
"""

import sys

import requests


def check_api_health() -> tuple[bool, str]:
    """Check if API is healthy."""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, f"API Online - {data.get('status', 'unknown')}"
        return False, f"API returned {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "API not reachable"
    except Exception as e:
        return False, f"API error: {str(e)}"


def check_tarl() -> tuple[bool, str]:
    """Check if TARL is accessible."""
    try:
        response = requests.get("http://localhost:8001/tarl", timeout=5)
        if response.status_code == 200:
            data = response.json()
            version = data.get("version", "unknown")
            rule_count = len(data.get("rules", []))
            return True, f"TARL v{version} - {rule_count} rules"
        return False, f"TARL returned {response.status_code}"
    except Exception as e:
        return False, f"TARL error: {str(e)}"


def check_audit() -> tuple[bool, str]:
    """Check if audit log is accessible."""
    try:
        response = requests.get("http://localhost:8001/audit?limit=1", timeout=5)
        if response.status_code == 200:
            data = response.json()
            record_count = len(data.get("records", []))
            return True, f"Audit accessible - {record_count} records"
        return False, f"Audit returned {response.status_code}"
    except Exception as e:
        return False, f"Audit error: {str(e)}"


def main():
    """Run all health checks."""
    print("🏥 Project AI Health Check\n")
    print("=" * 60)

    checks = [
        ("API Health", check_api_health),
        ("TARL Accessibility", check_tarl),
        ("Audit Log", check_audit),
    ]

    results = []
    for name, check_func in checks:
        success, message = check_func()
        status = "✅" if success else "❌"
        print(f"{status} {name}: {message}")
        results.append(success)

    print("=" * 60)

    if all(results):
        print("\n✨ All systems operational!\n")
        return 0
    else:
        print("\n⚠️  Some systems are not operational\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
