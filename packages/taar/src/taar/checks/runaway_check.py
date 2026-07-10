"""builtin:runaway_check — detect runs exceeding timeout. Report only, never kills."""

from __future__ import annotations

from taar.checks._common import make_finding as _finding
from taar.context import ExecutionContext
from taar.locks import get_lock, is_lock_stale
from taar.models import BuiltinResult, ClassificationLevel, Finding


def runaway_check(ctx: ExecutionContext) -> BuiltinResult:
    """Detect runs that exceeded timeout. Report only — never kills."""
    findings: list[Finding] = []
    classification = ClassificationLevel.OPEN
    locks_root = ctx.config.locks_root

    for path in sorted(locks_root.glob("*.lock.json")):
        agent_id = path.name.removesuffix(".lock.json")
        try:
            lock = get_lock(agent_id, locks_root)
        except Exception:
            continue  # malformed locks are lock_check territory
        if lock is None:
            continue
        if is_lock_stale(lock):
            findings.append(
                _finding(
                    "high",
                    f"Run exceeded timeout: agent={lock.agent_id} run={lock.run_id} pid={lock.pid} expired={lock.expires_at}",
                    str(path),
                )
            )

    return BuiltinResult(
        0, f"runaway check: {len(findings)} finding(s)", "", findings, [], [], classification
    )
