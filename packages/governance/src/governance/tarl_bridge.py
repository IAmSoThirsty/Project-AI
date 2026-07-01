"""Subordinate TARL policy bridge for the governance engine.

Per PHASE_T_DISCOVERY.md Phase T2: the canonical Project-AI governance
policy is described in `docs/policy/project_ai_governance.tarl`. This
module loads and evaluates that policy via `utf.tarl.runtime`.

Subordination contract:
  - The TARL evaluation is ADVISORY only. The Python GovernanceEngine
    remains authoritative for the final verdict.
  - The bridge fails closed: any TARL error (parse failure, runtime
    failure, missing file, etc.) returns a DENY `TarlBridgeDecision`
    that the engine translates into a DENY vote via the
    `TarlAdvisoryGovernor` defined below.
  - The bridge never grants authority. A TARL ALLOW does not override
    a Python DENY; a TARL DENY surfaces to the engine, which may then
    apply its own rules on top.

Architectural invariants (AGENTS.md v3):
  - Downward-only deps: this module imports `kernel` (canonical types)
    and `utf.tarl.*` (PyPI dep `thirsty-lang==0.8.1`). No upward imports.
  - Fail-closed: every error path returns DENY.
  - Deterministic: same policy + same context = same decision.
  - Strict typing: mypy --strict clean.

This module is the entry point; it is wrapped by `TarlAdvisoryGovernor`
so the existing `GovernanceEngine.decide()` flow can consult it
through the same `Governor` protocol as the other governors.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final

from governance.types import Vote
from kernel import ActionRequest, Outcome

if TYPE_CHECKING:
    from utf.tarl.core import PolicyParser as _PolicyParserType
    from utf.tarl.runtime import TarlRuntime as _TarlRuntimeType
else:
    _PolicyParserType = object  # type: ignore[assignment,misc]
    _TarlRuntimeType = object  # type: ignore[assignment,misc]

# utf.tarl.* is the PyPI dep `thirsty-lang==0.8.1` (Phase T1). The dotted
# `utf.tarl` namespace is the language's fifth tier (TARL); the bare
# `tarl` Python module is Beginnings' own packages/tarl/ runtime, which
# is a different thing. See tests/test_thirsty_lang_smoke.py for the
# namespace-collision guard.
#
# Import the symbols at module load. The dep is pinned in pyproject.toml;
# if it's missing, the import block raises ImportError and the bridge
# sets the symbols to None for the fail-closed branch.
_PolicyParser: _PolicyParserType | None
_TarlRuntime: _TarlRuntimeType | None
try:
    from utf.tarl.core import PolicyParser as _PolicyParser  # type: ignore[assignment]
    from utf.tarl.runtime import TarlRuntime as _TarlRuntime  # type: ignore[assignment]

    _TARL_IMPORT_ERROR: str | None = None
except ImportError as _import_error:  # pragma: no cover - fail-closed
    _TARL_IMPORT_ERROR = str(_import_error)
    _PolicyParser = None
    _TarlRuntime = None


# Canonical policy file location (bundled with the governance package
# so it ships in the wheel and resolves consistently in dev and prod).
# The policy is intentionally colocated with the package that consumes
# it; the bridge loads it from `Path(__file__).parent`.
_BUNDLED_POLICY_FILENAME: Final[str] = "project_ai_governance.tarl"

# Default-deny fallback policy (used if the bundled resource is
# missing or fails to parse). This is a minimal TARL policy that
# returns DENY for every input — it preserves fail-closed semantics
# even when the canonical policy is unavailable.
_FAIL_CLOSED_POLICY: Final[str] = (
    "// Fail-closed fallback policy\n"
    "// Used when the canonical policy is missing or unparseable.\n"
    "policy fail_closed\n"
    "when true => DENY\n"
)


@dataclass(frozen=True)
class TarlBridgeDecision:
    """The result of a TARL policy evaluation.

    `verdict` is the canonical ALLOW/DENY/ESCALATE outcome.
    `policy_hash` is the SHA-256 of the policy text that produced the
        verdict, for audit and tamper detection.
    `reason` is a human-readable explanation (TARL rule text + verdict).
    `fallback` is True if the canonical policy was unavailable and the
        fail-closed fallback was used instead.
    """

    verdict: Outcome
    policy_hash: str
    reason: str
    fallback: bool


def _load_bundled_policy() -> tuple[str, str]:
    """Load the bundled canonical policy text.

    Returns (policy_text, policy_hash). If the resource cannot be read,
    returns the fail-closed fallback text and a synthetic hash.
    """
    policy_path = Path(__file__).parent / _BUNDLED_POLICY_FILENAME
    try:
        policy_text = policy_path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        policy_text = _FAIL_CLOSED_POLICY
        return policy_text, _sha256(policy_text) + ".fallback"
    return policy_text, _sha256(policy_text)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _map_tarl_verdict(tarl_verdict: object) -> Outcome:
    """Map a TARL verdict object to the canonical Outcome enum.

    TARL verdicts are string-valued (`'ALLOW'`, `'DENY'`, `'ESCALATE'`).
    Anything else is treated as DENY (fail-closed).
    """
    name = getattr(tarl_verdict, "name", None) or str(tarl_verdict)
    normalized = name.upper()
    if normalized == "ALLOW":
        return Outcome.ALLOW
    if normalized == "DENY":
        return Outcome.DENY
    if normalized == "ESCALATE":
        return Outcome.ESCALATE
    return Outcome.DENY


def _build_context(request: ActionRequest, state: Mapping[str, object]) -> dict[str, object]:
    """Map a kernel `ActionRequest` + governance state into a TARL context dict.

    The context is intentionally a flat dict of string keys mapped to
    primitive values (str / int / float / bool). TARL's expression
    evaluator operates on these primitives; nested structures are
    flattened or stringified here.
    """
    return {
        # Action identity
        "action": str(getattr(request, "action_id", "unknown")),
        "subject": str(getattr(request, "actor", "unknown")),
        # Authorization state (best-effort from the engine state mapping)
        "authority_present": bool(state.get("authority_present", False)),
        "evidence_tier": int(str(state.get("evidence_tier", 0))),
        "capability_token_valid": bool(state.get("capability_token_valid", False)),
        "governor_consensus": bool(state.get("governor_consensus", False)),
        "audit_chain_intact": bool(state.get("audit_chain_intact", True)),
        # Verdict handoff (for the ESCALATE rule)
        "governance_verdict": str(state.get("governance_verdict", "PENDING")),
    }


def evaluate_policy(
    request: ActionRequest,
    state: Mapping[str, object],
) -> TarlBridgeDecision:
    """Evaluate the canonical TARL policy against the request.

    Returns a `TarlBridgeDecision` describing the advisory verdict,
    the policy hash, and whether the fail-closed fallback was used.

    Fail-closed semantics: every error path returns DENY with
    `fallback=True`. The engine translates this into a DENY vote.
    """
    # Import-failure case: the dep is missing entirely.
    if _TARL_IMPORT_ERROR is not None:
        return TarlBridgeDecision(
            verdict=Outcome.DENY,
            policy_hash="import-error",
            reason=(f"thirsty-lang import failed: {_TARL_IMPORT_ERROR}"),
            fallback=True,
        )

    policy_text, policy_hash = _load_bundled_policy()

    try:
        if _PolicyParser is None or _TarlRuntime is None:
            raise RuntimeError("tarl module unavailable")
        policy = _PolicyParser.parse(policy_text)
        runtime = _TarlRuntime(policy)  # type: ignore[operator]
        context = _build_context(request, state)
        decision: object = runtime.evaluate(context)
        verdict = _map_tarl_verdict(getattr(decision, "verdict", decision))
    except Exception as exc:
        return TarlBridgeDecision(
            verdict=Outcome.DENY,
            policy_hash=policy_hash,
            reason=f"tarl evaluation failed: {type(exc).__name__}: {exc}",
            fallback=True,
        )

    return TarlBridgeDecision(
        verdict=verdict,
        policy_hash=policy_hash,
        reason=f"tarl.evaluator: {verdict.value}",
        fallback=False,
    )


class TarlAdvisoryGovernor:
    """A `Governor` that consults the TARL policy and emits a vote.

    This is the integration point with the existing `GovernanceEngine`.
    Construct one with the standard `Governor` protocol name and add
    it to the engine's governors tuple. It is fail-closed: any
    internal error emits DENY.
    """

    def __init__(self, name: str = "tarl-advisory") -> None:
        if not name.strip():
            raise ValueError("name must not be empty")
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def evaluate(self, request: ActionRequest, state: Mapping[str, object]) -> Vote:
        decision = evaluate_policy(request, state)
        return Vote(
            self._name,
            decision.verdict,
            decision.reason,
        )


__all__ = [
    "TarlAdvisoryGovernor",
    "TarlBridgeDecision",
    "evaluate_policy",
]
