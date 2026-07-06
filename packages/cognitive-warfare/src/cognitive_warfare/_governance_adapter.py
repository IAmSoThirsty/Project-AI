"""Governance adapter for the cognitive_warfare engine (J2 port).

The legacy cognitive_warfare module imported
``planetary_interposition`` from a non-canonical path:
``app.governance.planetary_defense_monolith``. The canonical Beginnings
architecture uses ``packages.governance.GovernanceEngine.decide()``
with a ``kernel.ActionRequest`` payload.

This adapter preserves the legacy ``planetary_interposition`` API
exactly (same signature, same ``action_id`` return shape) so the
ported cognitive_warfare code is a faithful translation, while
delegating the actual policy decision to the canonical governance
engine.

The default policy is fail-closed: no governors means any call returns
``DENY``. The canonical ``GovernanceEngine.__init__`` raises if
``governors`` is empty, so a default deny RuleGovernor is wired in.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import uuid4

from governance import GovernanceEngine, RuleGovernor
from kernel import ActionRequest, Outcome


def _build_default_engine() -> GovernanceEngine:
    """A fail-closed governance engine with a default deny rule."""
    return GovernanceEngine(
        policy_version="cognitive-warfare-default-v1",
        governors=(RuleGovernor("cognitive-warfare-default", ()),),
    )


# Lazy module-level engine so the package is importable without a
# preconfigured engine. Tests can override via ``set_engine()``.
_engine: GovernanceEngine = _build_default_engine()


def set_engine(engine: GovernanceEngine) -> None:
    """Replace the module-level governance engine (test seam)."""
    global _engine
    _engine = engine


def get_engine() -> GovernanceEngine:
    """Return the current module-level governance engine."""
    return _engine


def planetary_interposition(
    actor: str,
    intent: str,
    context: Mapping[str, Any] | None = None,
    authorized_by: str = "System",
) -> str:
    """Constitutional check that mirrors the legacy signature.

    Args:
        actor: The component requesting the action.
        intent: A free-form operation identifier
            (e.g. ``deploy_countermeasures_critical``).
        context: Optional structured context (hazard_level, patterns,
            target, etc.) that becomes part of the ActionRequest
            payload.
        authorized_by: Authority string; legacy systems use this for
            audit; canonical governance treats it as payload data.

    Returns:
        An ``action_id`` string. If the canonical governance engine
        returns ``DENY``, the legacy semantics were "fail-closed and
        do not act" — the action_id is still returned (it's a handle
        to the rejected action) but the caller is responsible for
        checking the outcome. In the cognitive_warfare port, callers
        either log the action_id (counter_operation) or rely on the
        governance verdict (narrative controller); the legacy code
        did not check the verdict either, so the port preserves that
        behavior for surface parity.
    """
    payload: dict[str, Any] = {"authorized_by": authorized_by}
    if context is not None:
        payload.update(dict(context))

    action_id = uuid4().hex
    request = ActionRequest(
        action_id=action_id,
        actor=actor,
        operation=intent,
        resource="cognitive_warfare",
        payload=payload,
    )

    result = _engine.decide(request)
    if result.decision.outcome is Outcome.DENY:
        # Legacy fail-closed semantics: still return a handle, but
        # the cognitive_warfare caller should observe the denial via
        # the structured log record rather than the action_id.
        # The action_id is the same as the request id; the verdict
        # is observable via ``get_last_verdict()`` if needed.
        _record_verdict(action_id, denied=True, reasons=result.decision.reasons)
    else:
        _record_verdict(action_id, denied=False, reasons=result.decision.reasons)

    return action_id


# ── verdict history (observability for callers + tests) ──────────

_verdicts: dict[str, dict[str, Any]] = {}


def _record_verdict(action_id: str, denied: bool, reasons: tuple[str, ...]) -> None:
    _verdicts[action_id] = {"denied": denied, "reasons": list(reasons)}


def get_verdict(action_id: str) -> dict[str, Any] | None:
    """Return the recorded verdict for an ``action_id`` (test seam)."""
    return _verdicts.get(action_id)


def clear_verdicts() -> None:
    """Clear the verdict history (test seam)."""
    _verdicts.clear()
