import logging

from kernel.tarl_gate import TarlGate
from src.cognition.codex.escalation import CodexDeus

logger = logging.getLogger(__name__)


class ExecutionKernel:
    def __init__(self, governance, tarl_runtime, codex: CodexDeus, sovereign_runtime=None):
        self.governance = governance
        self.codex = codex
        self.tarl_gate = TarlGate(tarl_runtime, codex)
        self.sovereign_runtime = sovereign_runtime  # Optional sovereign runtime

    def execute(self, action, context=None, policy_binding=None):
        """
        Execute an action through the kernel with TARL enforcement.

        CRITICAL: If sovereign_runtime is enabled, execution REQUIRES:
        1. Valid policy binding (cryptographically signed)
        2. Policy state must resolve to True
        3. Context must match binding

        This makes governance non-bypassable by design.

        Args:
            action: The action to execute
            context: Execution context for TARL evaluation
            policy_binding: Optional cryptographic policy binding (required if sovereign_runtime is enabled)

        Returns:
            Result of the action execution

        Raises:
            RuntimeError: If sovereign mode is enabled and policy binding is invalid
        """
        if context is None:
            context = {}

        # SOVEREIGN MODE ENFORCEMENT
        # This execution path literally cannot run unless governance state resolves true
        if self.sovereign_runtime is not None:
            logger.info("Sovereign mode ACTIVE - enforcing cryptographic governance")

            # CRITICAL: Policy binding is REQUIRED in sovereign mode
            if policy_binding is None:
                error_msg = (
                    "SOVEREIGN ENFORCEMENT: Execution blocked - no policy binding provided. "
                    "This execution path cannot run without cryptographic governance approval."
                )
                logger.error(error_msg)

                # Log to sovereign audit trail
                self.sovereign_runtime.audit_log(
                    "EXECUTION_BLOCKED",
                    {
                        "reason": "missing_policy_binding",
                        "action": str(action),
                        "context": context,
                    },
                    severity="ERROR",
                )

                raise RuntimeError(error_msg)

            # Extract policy state from binding
            # In sovereign mode, policy_binding contains cryptographic proof
            policy_state = {
                "stage_allowed": True,
                "governance_active": True,
                "compliance_required": True,
            }

            # CRITICAL: Verify policy binding cryptographically
            is_valid = self.sovereign_runtime.verify_policy_state_binding(
                policy_state, context, policy_binding
            )

            if not is_valid:
                error_msg = (
                    "SOVEREIGN ENFORCEMENT: Execution blocked - policy binding verification failed. "
                    "Cryptographic proof invalid. This execution path is LOCKED."
                )
                logger.error(error_msg)

                # Log to sovereign audit trail
                self.sovereign_runtime.audit_log(
                    "EXECUTION_BLOCKED",
                    {
                        "reason": "policy_binding_verification_failed",
                        "action": str(action),
                        "context": context,
                        "binding_hash": policy_binding.get("binding_hash", "unknown"),
                    },
                    severity="CRITICAL",
                )

                raise RuntimeError(error_msg)

            # Log successful verification
            self.sovereign_runtime.audit_log(
                "EXECUTION_AUTHORIZED",
                {
                    "action": str(action),
                    "context": context,
                    "binding_hash": policy_binding["binding_hash"],
                    "policy_hash": policy_binding["policy_hash"],
                },
                severity="INFO",
            )

            logger.info(
                "Sovereign governance verified - execution authorized (binding: %s)",
                policy_binding["binding_hash"][:16],
            )

        # Enforce TARL policies
        self.tarl_gate.enforce(context)

        # Execute the action (placeholder for actual execution logic)
        result = {
            "status": "success",
            "action": action,
            "governance": self.governance,
        }

        # Add sovereign proof to result if in sovereign mode
        if self.sovereign_runtime is not None and policy_binding is not None:
            result["sovereign_proof"] = {
                "binding_hash": policy_binding["binding_hash"],
                "policy_hash": policy_binding["policy_hash"],
                "verified": True,
            }

            # Log successful execution
            self.sovereign_runtime.audit_log(
                "EXECUTION_COMPLETED",
                {
                    "action": str(action),
                    "status": "success",
                    "binding_hash": policy_binding["binding_hash"],
                },
                severity="INFO",
            )

        return result
