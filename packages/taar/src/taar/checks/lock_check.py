"""builtin:lock_check — report active, stale, malformed locks. Never deletes."""

from __future__ import annotations

from taar.checks._common import make_finding as _finding
from taar.classification import escalate
from taar.context import ExecutionContext
from taar.locks import get_lock, is_lock_stale
from taar.models import BuiltinResult, ClassificationLevel, Finding


def lock_check(ctx: ExecutionContext) -> BuiltinResult:
    """Report active, stale, malformed, and orphan locks. Never deletes."""
    findings: list[Finding] = []
    classification = ClassificationLevel.OPEN
    locks_root = ctx.config.locks_root

    for path in sorted(locks_root.glob("*.lock.json")):
        agent_id = path.name.removesuffix(".lock.json")
        try:
            lock = get_lock(agent_id, locks_root)
        except Exception as exc:  # LockError — malformed lock is a BLACK signal
            findings.append(_finding("high", f"Malformed lock record: {exc}", str(path)))
            classification = escalate(classification, ClassificationLevel.BLACK)
            continue
        if lock is None:
            continue
        if lock.agent_id not in ctx.registry.agents_by_id:
            findings.append(_finding("high", f"Lock for unknown agent {lock.agent_id}", str(path)))
            classification = escalate(classification, ClassificationLevel.BLACK)
        elif is_lock_stale(lock):
            findings.append(
                _finding(
                    "medium",
                    f"Stale lock: agent={lock.agent_id} run={lock.run_id} expired={lock.expires_at}",
                    str(path),
                )
            )
        else:
            findings.append(
                _finding(
                    "info",
                    f"Active lock: agent={lock.agent_id} run={lock.run_id} pid={lock.pid}",
                    str(path),
                )
            )

    return BuiltinResult(
        0, f"lock check: {len(findings)} finding(s)", "", findings, [], [], classification
    )
