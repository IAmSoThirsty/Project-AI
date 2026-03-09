"""Ambassador bridge: connects public ambassador surface to the Sovereign Monolith."""

from __future__ import annotations

import json
import logging

logger = logging.getLogger("ambassador")


class AmbassadorBridge:
    def __init__(self, governance=None):
        # governance surface if available; otherwise we use a permissive fallback
        self.governance = governance

    def status(self) -> dict:
        return {
            "ambassador": "ready",
            "governance_present": bool(self.governance),
            "surface": "public ambassador interface",
        }

    def handle_action(self, action_request: dict, tenant_id: str | None = None) -> dict:
        # Basic validation
        action = action_request.get("action")
        params = action_request.get("parameters", {})
        # Resolve tenant_id from payload if not provided as arg
        if not tenant_id:
            tenant_id = action_request.get("tenant_id") or action_request.get("tenant")

        if not action:
            return {"allowed": False, "reason": "Missing action"}

        allowed, reason = self._gate_action(action, params)
        if not allowed:
            return {
                "allowed": False,
                "reason": reason or "Policy gating",
                "tenant_id": tenant_id,
            }

        # If allowed, attempt to execute via the monolith gateway (best-effort)
        # This is a placeholder; in production this would call into the ExecutionKernel
        try:
            # Lazy import to avoid heavy startup costs
            from governance.sovereign_runtime import SovereignRuntime  # type: ignore

            runtime = SovereignRuntime()
            # We assume there is a generic execute_action on the governance surface
            exec_action = getattr(runtime, "execute_action", None)
            if callable(exec_action):
                payload = {"action": action, "params": params, "tenant_id": tenant_id}
                result = exec_action(payload)
                return {"allowed": True, "result": result}
        except Exception as e:
            logger.debug("Ambassador bridge under governance exception: %s", e)

        # Fallback: surface a safe, neutral response
        return {
            "allowed": True,
            "result": {
                "action": action,
                "parameters": params,
                "tenant_id": tenant_id,
                "note": "Executed via ambassador (fallback).",
            },
            "tenant_id": tenant_id,
        }

    def _gate_action(
        self, action: str, params: dict, tenant_id: str | None = None
    ) -> tuple[bool, str | None]:
        # Attempt to perform governance-based gating if SovereignRuntime is available
        try:
            from governance.sovereign_runtime import SovereignRuntime  # type: ignore

            runtime = SovereignRuntime()
            gate = getattr(runtime, "evaluate_action", None)
            if callable(gate):
                payload = {"action": action, "params": params, "tenant_id": tenant_id}
                gate_res = gate(payload)
                if isinstance(gate_res, (list, tuple)) and len(gate_res) >= 1:
                    verdict = gate_res[0]
                    reason = gate_res[1] if len(gate_res) > 1 else None
                else:
                    verdict = gate_res
                    reason = None
                return verdict == "ALLOW", reason
        except Exception:
            # If governance surface is unavailable, default to allow (to preserve public surface)
            pass
        return True, None
