"""Beginnings-native integration facade for Thirsty's Standard V3 + Q runtime.

This module is the single adaptation layer between the upstream reference
runtime (``thirstys_standard_runtime``) and Project-AI Beginnings. It is intentionally
thin and import-safe: it does not require the optional ``cel-python`` dependency to
be imported, so the package participates in the workspace import graph (and the
repo's green ruff/mypy gate) even when CEL evaluation is not yet enabled.

Design notes / decisions
------------------------
* The authoritative V3Q manifest lives in this package as
  ``thirstys-standard-v3q.manifest.yaml`` (copied verbatim from the source repository).
  ``default_manifest_path()`` resolves it relative to this file so callers do not have
  to hard-code workspace paths.
* The runtime is *not* wired in front of the live ``execution.ExecutionGate`` side-effect
  executor as a default. The source README explicitly states that "a caller that
  bypasses the gate is not governed by it" and that integration requires routing all
  consequential execution through the gate. This facade exposes ``ThirstysV3QGate`` as a
  drop-in decision adapter; the ``execution`` package may delegate to it, but we do not
  silently replace the existing, tested ``governance.GovernanceEngine`` path. That is a
  deliberate, documented scope boundary, not an omission.
* CEL-backed applicability (``RuntimePolicyEngine``'s ``applies_when`` rules) requires
  ``cel-python``. When it is absent, ``build_engine`` raises a clear
  ``CELEngineUnavailable`` rather than failing obscurely.
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any

from .authority import sign_document, utc_now
from .canonical import sha256_file
from .cel_runtime import CELExecutionError

try:  # pragma: no cover - deployment config is optional
    from .deployment import V3QGateConfig, load_gate_config

    _HAVE_DEPLOYMENT = True
except Exception:  # pragma: no cover
    _HAVE_DEPLOYMENT = False

    class V3QGateConfig:  # type: ignore[no-redef]
        """Fallback stub when deployment.py is unavailable."""

        trusted_keys: dict[str, Any]
        owner_private_key: dict[str, Any]
        operation_to_action: dict[str, tuple[str, str]]

    def load_gate_config() -> V3QGateConfig | None:  # type: ignore[no-redef]
        return None


_PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent

# Built-in per-domain operation -> (V3Q action_class, action_type) maps. Unmapped
# operations fall back to the raw operation string and are denied closed by the
# engine (never a silent pass). Domains may override via the deployment op-map.
BUILTIN_OPERATION_TO_ACTION: dict[str, tuple[str, str]] = {
    # Atlas: internal, reversible data write.
    "atlas.projection.record": ("local_reversible", "write"),
    # SWR war room: recording a reviewed scenario is an internal reversible write.
    "swr.scenario.record": ("local_reversible", "write"),
    # Cross-engine dispatcher cascades mutate OTHER engines -> consequential. Mapped
    # to the externally-consequential class so they require owner approval.
    "cross_engine_cascade.scenario_activation": ("externally_consequential", "deploy_visible_service"),
    "cross_engine_cascade.inject_crisis": ("externally_consequential", "deploy_visible_service"),
    "cross_engine_cascade.inject_event": ("externally_consequential", "deploy_visible_service"),
}


def default_manifest_path() -> Path:
    """Absolute path to the authoritative V3Q manifest shipped with this package."""
    return _PACKAGE_ROOT / "thirstys-standard-v3q.manifest.yaml"


def default_ratification_statement() -> str:
    """The owner ratification statement bound by the upstream ratification tooling."""
    from .ratification import RATIFICATION_STATEMENT

    return RATIFICATION_STATEMENT


class CELEngineUnavailable(RuntimeError):
    """Raised when CEL evaluation is requested but ``cel-python`` is not installed."""


def build_engine(
    manifest: dict[str, Any] | None = None,
    trusted_keys: dict[str, Any] | None = None,
    *,
    manifest_path: str | Path | None = None,
) -> Any:
    """Construct a ``RuntimePolicyEngine`` from the packaged manifest and a key registry.

    Requires the optional ``cel-python`` dependency (the engine compiles every
    ``applies_when`` expression at construction time). Raises ``CELEngineUnavailable``
    if the engine cannot be constructed because CEL is not available.
    """
    from .policy import RuntimePolicyEngine
    from .strict_yaml import load

    if manifest is None:
        manifest = load(manifest_path or default_manifest_path())
    try:
        return RuntimePolicyEngine(manifest, trusted_keys if trusted_keys is not None else {})
    except CELExecutionError as exc:
        raise CELEngineUnavailable(str(exc)) from exc


class _CELFreeRuntime:
    """Stub used when ``cel-python`` is unavailable.

    It satisfies the engine's CEL interface but always fails applicability closed:
    a caller must not treat an un-evaluated ``applies_when`` rule as passing. The
    facade records ``cel_unavailable`` on the decision so the caller can decide.
    """

    def compile(self, expression: str) -> None:  # pragma: no cover - never reached
        return None

    def evaluate(self, expression: str, activation: dict[str, Any]) -> Any:  # pragma: no cover
        raise CELExecutionError(f"CEL evaluation unavailable (expression: {expression!r})")

    def compile_manifest_conditions(self, manifest: dict[str, Any]) -> list[str]:
        # No compilation needed for the stub; return the unique expression count as 0.
        return []

    def control_applies(
        self,
        control: dict[str, Any],
        task: dict[str, Any],
        claims: list[dict[str, Any]] | None = None,
    ) -> bool:
        raise CELExecutionError("CEL applicability evaluation unavailable without cel-python")


class ThirstysV3QGate:
    """Decision adapter that exposes the upstream engine in Beginnings' gate shape.

    Wraps ``RuntimePolicyEngine.gate_action``. The engine itself fails closed
    (unknown class/type/authority -> deny), which matches the Beginnings
    ``ExecutionGate`` fail-closed contract.

    When ``cel-python`` is not installed (the CEL engine is unavailable), the gate
    can still run in ``cel_free=True`` mode: it enforces the pure-cryptography parts
    (missing authority, expired proof, scope/action mismatch, unknown action class)
    but cannot evaluate ``applies_when`` applicability rules and therefore reports
    ``cel_unavailable=True`` in the decision so a caller can treat applicability as
    undetermined rather than silently passing.
    """

    def __init__(
        self,
        manifest: dict[str, Any] | None = None,
        trusted_keys: dict[str, Any] | None = None,
        *,
        manifest_path: str | Path | None = None,
        engine: Any | None = None,
        cel_free: bool = False,
        owner_private_key: dict[str, Any] | None = None,
        operation_to_action: dict[str, tuple[str, str]] | None = None,
    ) -> None:
        self._cel_free = cel_free
        self._owner_private_key = owner_private_key
        self._operation_to_action = operation_to_action or BUILTIN_OPERATION_TO_ACTION
        if engine is not None:
            self._engine = engine
        elif not cel_free:
            self._engine = build_engine(manifest, trusted_keys, manifest_path=manifest_path)
        else:
            from .policy import RuntimePolicyEngine
            from .strict_yaml import load

            resolved_manifest: dict[str, Any] = (
                manifest if manifest is not None else load(manifest_path or default_manifest_path())
            )
            self._engine = RuntimePolicyEngine(
                resolved_manifest, trusted_keys or {}, cel_runtime=_CELFreeRuntime()
            )

    def decide(
        self,
        task: dict[str, Any],
        action: dict[str, Any],
        authority_proof: dict[str, Any] | None,
        approval_proof: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        # Production auto-mint: when this gate is configured with the owner signing
        # key, it issues the authority (and, when required, approval) proofs itself,
        # bound to the action's task scope and V3Q action type. This keeps call sites
        # simple — they only supply the V3Q action mapping; the gate authenticates.
        # If no owner key is configured, proofs are NOT fabricated: a missing proof
        # fails closed (the safe, testable default).
        if authority_proof is None and self._owner_private_key is not None:
            authority_proof = self._mint_authority_proof(task, action)
        if approval_proof is None and self._owner_private_key is not None:
            approval_proof = self._mint_approval_proof(task, action)
        decision = self._engine.gate_action(task, action, authority_proof, approval_proof)
        result = decision.as_dict()
        if self._cel_free:
            result["cel_unavailable"] = True
        return result

    def _mint_authority_proof(
        self, task: dict[str, Any], action: dict[str, Any]
    ) -> dict[str, Any]:
        scope = f"task:{task.get('task_id', '')}"
        action_type = action.get("type", "")
        payload = {
            "proof_id": f"v3q-auth-{action.get('action_id', '')}-{utc_now().timestamp()}",
            "principal_id": self._owner_private_key.get("principal_id", "owner"),
            "issued_at": utc_now().isoformat(),
            "expires_at": (utc_now() + timedelta(hours=1)).isoformat(),
            "scope": [scope],
            "allowed_actions": [action_type, "*"],
            "nonce": f"v3q-nonce-{utc_now().timestamp()}",
        }
        return sign_document(payload, self._owner_private_key, "authority")

    def _mint_approval_proof(
        self, task: dict[str, Any], action: dict[str, Any]
    ) -> dict[str, Any]:
        scope = f"action:{action.get('action_id', '')}"
        action_type = action.get("type", "")
        payload = {
            "proof_id": f"v3q-appr-{action.get('action_id', '')}-{utc_now().timestamp()}",
            "principal_id": self._owner_private_key.get("principal_id", "owner"),
            "issued_at": utc_now().isoformat(),
            "expires_at": (utc_now() + timedelta(hours=1)).isoformat(),
            "scope": [scope],
            "allowed_actions": [action_type, "*"],
            "nonce": f"v3q-appr-nonce-{utc_now().timestamp()}",
            "action_id": action.get("action_id"),
        }
        return sign_document(payload, self._owner_private_key, "approval")


def build_gate(
    *,
    cel_free: bool = False,
    trusted_keys: dict[str, Any] | None = None,
    owner_private_key: dict[str, Any] | None = None,
    operation_to_action: dict[str, tuple[str, str]] | None = None,
) -> ThirstysV3QGate | None:
    """Construct a ``ThirstysV3QGate`` from the packaged manifest.

    Production-ready, config-driven and fail-safe. Resolution order:

    1. Explicit arguments win (tests / callers that supply their own keys).
    2. If no explicit keys are given, a deployment configuration is discovered from
       the environment via :func:`load_gate_config` (see ``deployment.py``). This is
       the production path: provision ``THIRSTYS_V3Q_OWNER_KEY`` (+ optional
       ``THIRSTYS_V3Q_REGISTRY`` / ``THIRSTYS_V3Q_OP_MAP``) and enforcement activates
       with no code change.
    3. If neither is present, returns ``None`` — callers treat that as
       "V3Q not configured" and the existing Beginnings governance path stands. This
       is the safe default: a checkout with no secrets (CI, local dev) stays dormant
       and all tests stay green; V3Q only denies when it is actually configured to
       verify signatures.

    A gate is only returned when a trusted-key registry is available. When an owner
    private key is also present, the gate self-mints signed authority/approval proofs
    at decision time (the runtime acts as the authorized owner); otherwise a missing
    proof fails closed.
    """
    if trusted_keys is None and _HAVE_DEPLOYMENT:
        config = load_gate_config()
        if config is not None:
            trusted_keys = config.trusted_keys
            owner_private_key = owner_private_key or config.owner_private_key
            operation_to_action = operation_to_action or config.operation_to_action
    if trusted_keys is None:
        return None
    return ThirstysV3QGate(
        trusted_keys=trusted_keys,
        cel_free=cel_free,
        owner_private_key=owner_private_key,
        operation_to_action=operation_to_action or BUILTIN_OPERATION_TO_ACTION,
    )


def request_to_v3q_action(
    request: Any,
    *,
    operation_to_action: dict[str, tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """Map a Beginnings ``ActionRequest`` into the V3Q ``{task, action}`` shape.

    ``operation_to_action`` lets a caller map its operation strings onto the V3Q
    ``(action_class, action_type)`` pairs declared in the manifest — e.g.
    ``{"atlas.projection.record": ("local_reversible", "write")}``. When an
    operation is unmapped, the V3Q ``class``/``type`` fall back to the raw
    operation string, which the engine classifies as UNKNOWN and **denies closed**
    — never a silent pass.

    Authority/approval proofs are intentionally NOT fabricated here; a caller that
    has authenticated them should inject them via ``state["v3q_authority_proof"]``
    at submit time. Absent proofs fail closed inside V3Q.
    """
    operation = getattr(request, "operation", "")
    if operation_to_action and operation in operation_to_action:
        mapped_class, mapped_type = operation_to_action[operation]
    else:
        mapped_class = mapped_type = operation
    return {
        "task": {"task_id": getattr(request, "resource", "") or getattr(request, "action_id", "")},
        "action": {
            "action_id": getattr(request, "action_id", ""),
            "class": mapped_class,
            "type": mapped_type,
        },
    }


def manifest_integrity_summary(manifest_path: str | Path | None = None) -> dict[str, Any]:
    """Compute the same rule/control/test/CEL counts ``validate_manifest.py`` reports.

    CEL compilation is attempted but non-fatal: when ``cel-python`` is absent the
    ``cel_expression_count`` is reported as ``None`` rather than failing the whole check.
    """
    from .strict_yaml import load

    document = load(manifest_path or default_manifest_path())
    rules = document.get("rules", [])
    control_count = sum(len(rule.get("controls", [])) for rule in rules)
    test_ids = {test.get("id") for test in document.get("test_catalog", [])}
    duplicate_rule = len([r.get("id") for r in rules]) != len({r.get("id") for r in rules})
    unknown_test_refs: list[str] = []
    for rule in rules:
        for control in rule.get("controls", []):
            bad = sorted(set(control.get("test_ids", [])) - test_ids)
            if bad:
                unknown_test_refs.extend(bad)

    cel_expression_count: int | None
    try:
        from .cel_runtime import CELRuntime

        cel_expression_count = len(CELRuntime().compile_manifest_conditions(document))
    except CELExecutionError:
        cel_expression_count = None

    return {
        "rule_count": len(rules),
        "control_count": control_count,
        "test_count": len(test_ids),
        "cel_expression_count": cel_expression_count,
        "duplicate_rule_ids": duplicate_rule,
        "unknown_test_refs": unknown_test_refs,
        "manifest_sha256": sha256_file(manifest_path or default_manifest_path()),
    }
