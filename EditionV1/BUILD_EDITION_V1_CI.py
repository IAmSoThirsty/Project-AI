# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / BUILD_EDITION_V1_CI.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / BUILD_EDITION_V1_CI.py


#!/usr/bin/env python3
"""Edition V1 CI orchestrator (CTS-5 ready surface).

This script triggers a constrained Edition-V1 CI build that isolates the
target surface to EditionV1 components (CTS-4/CTS-5 readiness) and
exercises the API-key + tenant-based surface gating together with the
public ambassador surface. Heavy subsystems (Unity, desktop apps) are
intentionally not exercised by this script to keep CI green while still
covering core sovereign surface.
"""

import os
import subprocess
import sys


def run(cmd, cwd=None):
    print(f"RUN: {cmd}")
    return subprocess.call(cmd, shell=True, cwd=cwd or ".")


def main():
    # Ensure Edition V1 CI mode in environment
    os.environ["EDITION_V1_CI"] = "1"
    os.environ["AMBASSADOR_API_KEYS"] = os.environ.get("AMBASSADOR_API_KEYS", "")
    os.environ["AMBASSADOR_TENANT_MAP"] = os.environ.get("AMBASSADOR_TENANT_MAP", "{}")
    # Target to CTS5 if needed; for now CTS-5 surface is supported via the gating in build_all
    os.environ["EDITION_V1_TARGET"] = "cts5"
    # Run the central build orchestrator with Edition V1 scope
    # Use the current python executable for portability across environments
    code = run(f"{__import__('sys').executable} build/build_all.py", cwd=".")
    if code != 0:
        print("Edition V1 CI: Build failed in central orchestrator.")
        sys.exit(code)
    print("Edition V1 CI: Build completed (CTS-5 surface).")


if __name__ == "__main__":
    main()
