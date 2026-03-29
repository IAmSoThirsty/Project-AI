# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / boot_verification_agent.py
# ============================================================================ #
#
# COMPLIANCE: Regulator-Ready / UTF-8                                          #



"""
Boot Verification Agent
Runs the actual boot sequence and captures real layer status.
Fails with exit code 1 if any layer reports DEGRADED or FALLBACK.
No interaction. Runs and exits.
"""

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Thirsty-Lang Metadata Integration
__PRODUCTIVITY_STATUS__ = "Active"
__LAST_UPDATE__ = "2026-03-13 00:51"

ROOT = Path(__file__).parent.parent.absolute()
OUTPUT_JSON = ROOT / "governance" / "BOOT_VERIFICATION.json"
OUTPUT_MD = ROOT / "governance" / "BOOT_VERIFICATION.md"

LAYER_PATTERN = re.compile(
    r"\[(?P<level>INFO|WARNING|ERROR|CRITICAL)\].*?(?P<layer>\[Layer \d+\]|\[Security\]|\[Operational\]|\[Interface\])?.*?(?P<status>ACTIVE|DEGRADED|FALLBACK|FAILED|HALTED|READY|MOCK)",
    re.IGNORECASE
)

FAIL_STATES = {"DEGRADED", "FALLBACK", "FAILED", "HALTED"}


def run_boot() -> tuple[str, int]:
    try:
        result = subprocess.run(
            [sys.executable, "boot_sovereign.py", "--dev-mode"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = result.stdout + result.stderr
        return output, result.returncode
    except subprocess.TimeoutExpired:
        return "BOOT TIMED OUT AFTER 120s", 1
    except Exception as e:
        return f"BOOT FAILED TO LAUNCH: {e}", 1


def parse_boot_output(output: str) -> list[dict]:
    layers = []
    seen = set()

    for line in output.splitlines():
        match = LAYER_PATTERN.search(line)
        if match:
            status = match.group("status").upper()
            key = f"{match.group('layer')}:{status}"
            if key not in seen:
                seen.add(key)
                layers.append({
                    "layer": match.group("layer") or "UNKNOWN",
                    "status": status,
                    "raw": line.strip(),
                    "failed": status in FAIL_STATES,
                })

    return layers


def build_manifest():
    print("Running boot sequence...")
    output, returncode = run_boot()
    layers = parse_boot_output(output)

    failed_layers = [l for l in layers if l["failed"]]
    passed_layers = [l for l in layers if not l["failed"]]

    overall = "PASS" if not failed_layers and returncode == 0 else "FAIL"

    manifest = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "overall": overall,
        "exit_code": returncode,
        "summary": {
            "layers_checked": len(layers),
            "passed": len(passed_layers),
            "failed": len(failed_layers),
        },
        "failed_layers": failed_layers,
        "passed_layers": passed_layers,
        "raw_output": output[-5000:],  # last 5000 chars
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    status_icon = "✅" if overall == "PASS" else "❌"
    lines = [
        "# Boot Verification Report",
        f"Generated: {manifest['generated']}",
        f"## Result: {status_icon} {overall}",
        "",
        f"- Layers checked: {len(layers)}",
        f"- Passed: {len(passed_layers)}",
        f"- Failed: {len(failed_layers)}",
        "",
    ]

    if failed_layers:
        lines += ["## Failed Layers", "| Layer | Status | Log |", "|-------|--------|-----|"]
        for l in failed_layers:
            lines.append(f"| {l['layer']} | {l['status']} | {l['raw'][:80]} |")

    lines += ["", "## Passed Layers", "| Layer | Status |", "|-------|--------|"]
    for l in passed_layers:
        lines.append(f"| {l['layer']} | {l['status']} |")

    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"BOOT_VERIFICATION written. Result: {overall}")
    if failed_layers:
        print("FAILED LAYERS:")
        for l in failed_layers:
            print(f"  {l['layer']}: {l['status']}")

    sys.exit(0 if overall == "PASS" else 1)


if __name__ == "__main__":
    build_manifest()
