# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / architect_of_flowing.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / architect_of_flowing.py


"""
The Architect of Flowing
Work runner and workflow orchestrator for Project-AI governance agents.

Maintains a verified execution queue. Runs agents in dependency order.
Verifies each output before proceeding. Writes a flowing log of system state.
No interaction. No chat. Runs and exits.
"""

import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 for high-fidelity output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).parent.parent.absolute()
TOOLS = ROOT / "tools"
FLOW_LOG = ROOT / "governance" / "FLOW_LOG.json"
FLOW_MD = ROOT / "governance" / "FLOW_LOG.md"
QUEUE_FILE = ROOT / "governance" / "WORK_QUEUE.json"


# ─────────────────────────────────────────────
# Work Unit Definition
# ─────────────────────────────────────────────

@dataclass
class WorkUnit:
    id: str
    name: str
    script: str                        # path relative to ROOT
    depends_on: list[str] = field(default_factory=list)
    output_files: list[str] = field(default_factory=list)  # files that must exist after run
    required: bool = True              # if False, failure is logged but doesn't halt flow
    timeout: int = 600                 # seconds


# ─────────────────────────────────────────────
# Canonical Work Queue
# ─────────────────────────────────────────────

CANONICAL_QUEUE: list[WorkUnit] = [
    WorkUnit(
        id="architect",
        name="Architect Agent",
        script="tools/architect_agent.py",
        output_files=["governance/ARCHITECT_MANIFEST.json", "governance/ARCHITECT_MANIFEST.md"],
        required=True,
    ),
    WorkUnit(
        id="dependency",
        name="Dependency Agent",
        script="tools/dependency_agent.py",
        depends_on=["architect"],
        output_files=["governance/DEPENDENCY_MANIFEST.json"],
        required=True,
    ),
    WorkUnit(
        id="path_integrity",
        name="Path Integrity Agent",
        script="tools/path_integrity_agent.py",
        depends_on=["architect"],
        output_files=["governance/PATH_INTEGRITY_MANIFEST.json"],
        required=True,
    ),
    WorkUnit(
        id="stub_hunter",
        name="Stub Hunter Agent",
        script="tools/stub_hunter_agent.py",
        depends_on=["architect"],
        output_files=["governance/STUB_MANIFEST.json"],
        required=True,
    ),
    WorkUnit(
        id="dead_code",
        name="Dead Code Agent",
        script="tools/dead_code_agent.py",
        depends_on=["architect"],
        output_files=["governance/DEAD_CODE_MANIFEST.json"],
        required=True,
    ),
    WorkUnit(
        id="completion_tracker",
        name="Completion Tracker",
        script="tools/completion_tracker_agent.py",
        depends_on=["architect", "stub_hunter"],
        output_files=["governance/COMPLETION_TRACKER.json"],
        required=True,
    ),
    WorkUnit(
        id="boot_verification",
        name="Boot Verification Agent",
        script="tools/boot_verification_agent.py",
        depends_on=["path_integrity"],
        output_files=["governance/BOOT_VERIFICATION.json"],
        required=False,  # boot may fail — log it, don't halt
    ),
    WorkUnit(
        id="the_fates",
        name="The Fates Memory Agent",
        script="tools/the_fates_agent.py",
        depends_on=["completion_tracker", "boot_verification"],
        output_files=["governance/memory/THE_FATES.json", "governance/memory/THE_FATES.md"],
        required=True,
    ),
]


# ─────────────────────────────────────────────
# Execution Result
# ─────────────────────────────────────────────

@dataclass
class ExecutionResult:
    unit_id: str
    name: str
    status: str          # PASS | FAIL | SKIP | MISSING_OUTPUT
    exit_code: int
    duration_seconds: float
    output_files_verified: list[str]
    missing_outputs: list[str]
    stdout_tail: str
    stderr_tail: str
    timestamp: str


# ─────────────────────────────────────────────
# The Architect of Flowing
# ─────────────────────────────────────────────

class ArchitectOfFlowing:

    def __init__(self, queue: list[WorkUnit] = CANONICAL_QUEUE):
        self.queue = {u.id: u for u in queue}
        self.results: dict[str, ExecutionResult] = {}
        self.flow_start = datetime.now(timezone.utc)

    def run(self):
        self._log_header()
        order = self._resolve_order()

        for unit_id in order:
            unit = self.queue[unit_id]
            result = self._execute(unit)
            self.results[unit_id] = result
            self._log_result(result)

            if result.status == "FAIL" and unit.required:
                self._log_halt(unit, result)
                self._write_outputs()
                sys.exit(1)

        self._write_outputs()
        failed = [r for r in self.results.values() if r.status in {"FAIL", "MISSING_OUTPUT"}]
        sys.exit(1 if failed else 0)

    def _resolve_order(self) -> list[str]:
        """Topological sort respecting depends_on."""
        order = []
        visited = set()

        def visit(uid: str):
            if uid in visited:
                return
            visited.add(uid)
            for dep in self.queue[uid].depends_on:
                if dep in self.queue:
                    visit(dep)
            order.append(uid)

        for uid in self.queue:
            visit(uid)

        return order

    def _execute(self, unit: WorkUnit) -> ExecutionResult:
        # Check dependencies passed
        for dep in unit.depends_on:
            if dep in self.results and self.results[dep].status not in {"PASS"}:
                return ExecutionResult(
                    unit_id=unit.id, name=unit.name,
                    status="SKIP", exit_code=-1,
                    duration_seconds=0.0,
                    output_files_verified=[],
                    missing_outputs=[],
                    stdout_tail=f"Skipped: dependency {dep} did not pass.",
                    stderr_tail="",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

        script_path = ROOT / unit.script
        if not script_path.exists():
            return ExecutionResult(
                unit_id=unit.id, name=unit.name,
                status="FAIL", exit_code=-1,
                duration_seconds=0.0,
                output_files_verified=[],
                missing_outputs=[unit.script],
                stdout_tail="Script not found.",
                stderr_tail="",
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        t0 = time.monotonic()
        try:
            proc = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=unit.timeout,
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                unit_id=unit.id, name=unit.name,
                status="FAIL", exit_code=-1,
                duration_seconds=unit.timeout,
                output_files_verified=[],
                missing_outputs=[],
                stdout_tail="",
                stderr_tail=f"TIMED OUT after {unit.timeout}s",
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        duration = time.monotonic() - t0

        # Verify output files exist
        verified = []
        missing = []
        for out in unit.output_files:
            p = ROOT / out
            if p.exists():
                verified.append(out)
            else:
                missing.append(out)

        status = "PASS"
        if proc.returncode != 0:
            status = "FAIL"
        elif missing:
            status = "MISSING_OUTPUT"

        return ExecutionResult(
            unit_id=unit.id,
            name=unit.name,
            status=status,
            exit_code=proc.returncode,
            duration_seconds=round(duration, 2),
            output_files_verified=verified,
            missing_outputs=missing,
            stdout_tail=proc.stdout[-1000:],
            stderr_tail=proc.stderr[-500:],
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def _write_outputs(self):
        flow_end = datetime.now(timezone.utc)
        total = (flow_end - self.flow_start).total_seconds()

        passed = [r for r in self.results.values() if r.status == "PASS"]
        failed = [r for r in self.results.values() if r.status in {"FAIL", "MISSING_OUTPUT"}]
        skipped = [r for r in self.results.values() if r.status == "SKIP"]

        manifest = {
            "generated": flow_end.isoformat(),
            "duration_seconds": round(total, 2),
            "overall": "PASS" if not failed else "FAIL",
            "summary": {
                "passed": len(passed),
                "failed": len(failed),
                "skipped": len(skipped),
            },
            "results": [asdict(r) for r in self.results.values()],
        }

        FLOW_LOG.parent.mkdir(parents=True, exist_ok=True)
        FLOW_LOG.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        overall_icon = "✅" if manifest["overall"] == "PASS" else "❌"
        lines = [
            "# The Architect of Flowing — Flow Log",
            f"Generated: {manifest['generated']}",
            f"Duration: {manifest['duration_seconds']}s",
            f"## Result: {overall_icon} {manifest['overall']}",
            f"Passed: {len(passed)} | Failed: {len(failed)} | Skipped: {len(skipped)}",
            "",
            "## Execution Log",
            "| Agent | Status | Duration | Output Verified |",
            "|-------|--------|----------|-----------------|",
        ]

        for r in self.results.values():
            icon = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️", "MISSING_OUTPUT": "⚠️"}.get(r.status, "?")
            lines.append(
                f"| {r.name} | {icon} {r.status} | {r.duration_seconds}s | {len(r.output_files_verified)} files |"
            )

        if failed:
            lines += ["", "## Failures", ""]
            for r in failed:
                lines.append(f"### {r.name}")
                lines.append(f"- Exit code: {r.exit_code}")
                if r.missing_outputs:
                    lines.append(f"- Missing outputs: {', '.join(r.missing_outputs)}")
                if r.stderr_tail:
                    lines.append(f"```\n{r.stderr_tail}\n```")

        FLOW_MD.write_text("\n".join(lines), encoding="utf-8")

    def _log_header(self):
        print(f"[Architect of Flowing] {self.flow_start.isoformat()}", flush=True)
        print(f"[Architect of Flowing] {len(self.queue)} agents queued", flush=True)
        print("-" * 60, flush=True)

    def _log_result(self, r: ExecutionResult):
        icon = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️", "MISSING_OUTPUT": "⚠️"}.get(r.status, "?")
        print(f"{icon} [{r.status:14s}] {r.name} ({r.duration_seconds}s)", flush=True)
        if r.stdout_tail.strip():
            for line in r.stdout_tail.strip().splitlines()[-2:]:
                print(f"           {line}", flush=True)

    def _log_halt(self, unit: WorkUnit, result: ExecutionResult):
        print("-" * 60, flush=True)
        print(f"[HALT] Required agent failed: {unit.name}", flush=True)
        print("[HALT] Downstream agents will not run.", flush=True)
        print(f"[HALT] Fix {unit.script} and re-run.", flush=True)


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    architect = ArchitectOfFlowing()
    architect.run()
