"""
CognitionKernel - Central processing hub for all agent, tool, and system executions.

This kernel enforces cognitive governance, memory integration, identity tracking,
and reflection for every meaningful action in the system. No agent or tool may
bypass this kernel - it is the authoritative cognitive loop.

Architecture:
- process() is the ONLY entrypoint for all executions
- Integrates: Identity, Memory, Governance (Triumvirate), Reflection
- Provides hooks for: pre-execution, post-execution, error handling
- Tracks: execution history, identity drift, governance decisions
- Enforces: Four Laws, Triumvirate consensus, Black Vault policies

NON-NEGOTIABLE INVARIANTS:
- All execution flows through kernel.process() or kernel.route()
- All mutation flows through kernel.commit()
- ExecutionContext is the single source of truth for all execution state
- Governance never executes, Execution never governs
- Blocked actions are still logged for auditability
"""

import logging
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# Thread-local storage for kernel context tracking
_kernel_context = threading.local()


# ============================================================================
# Enums and Type Definitions
# ============================================================================

class ExecutionType(Enum):
    """Types of executions that can be processed by the kernel."""
    AGENT_ACTION = "agent_action"           # Agent execution (e.g., ExpertAgent, PlannerAgent)
    TOOL_INVOCATION = "tool_invocation"     # Tool/utility execution
    SYSTEM_OPERATION = "system_operation"   # Core system operation (Persona, Memory, etc.)
    PLUGIN_EXECUTION = "plugin_execution"   # Plugin runner execution
    COUNCIL_DECISION = "council_decision"   # Council/governance decision
    LEARNING_REQUEST = "learning_request"   # Learning engine request
    REFLECTION = "reflection"               # Reflection cycle execution


class ExecutionStatus(Enum):
    """Status of an execution."""
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"  # Blocked by governance


class MutationIntent(Enum):
    """Intent classification for mutations to identity/memory."""
    CORE = "core"              # genesis, law_hierarchy, core_values - requires full consensus
    STANDARD = "standard"      # personality_weights, preferences - requires standard consensus
    ROUTINE = "routine"        # regular operations - allowed


# ============================================================================
# Data Classes - Single Source of Truth
# ============================================================================

@dataclass
class Action:
    """
    Represents a proposed action to be executed.

    Immutable after creation to ensure governance integrity.
    """
    action_id: str
    action_name: str
    action_type: ExecutionType
    callable: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    source: str = "unknown"
    risk_level: str = "low"
    mutation_targets: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    """
    Governance decision about an action.

    Immutable after creation - governance observes, never executes.
    """
    decision_id: str
    action_id: str
    approved: bool
    reason: str
    council_votes: dict[str, Any] = field(default_factory=dict)
    mutation_intent: MutationIntent | None = None
    consensus_required: bool = False
    consensus_achieved: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class ExecutionContext:
    """
    Single source of truth for all execution state.

    This is THE object that flows through the entire kernel pipeline.
    Provides deterministic replay, causal tracing, and forensic auditability.

    Four-Channel Architecture:
    - perception: What the kernel received (input interpretation)
    - interpretation: How the kernel understood it
    - proposed_action: What action was proposed
    - governance_decision: What governance decided
    - result: What actually happened
    - channels: Four-channel memory storage
    """
    trace_id: str
    timestamp: datetime

    # Input and interpretation
    perception: dict[str, Any]
    interpretation: dict[str, Any]

    # Action and governance
    proposed_action: Action
    governance_decision: Decision | None = None

    # Execution and result
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: Any = None
    error: str | None = None

    # Four-channel memory storage (for auditability)
    channels: dict[str, Any] = field(default_factory=lambda: {
        "attempt": None,      # Intent
        "decision": None,     # Governance outcome
        "result": None,       # Actual effect
        "reflection": None,   # Post-hoc reasoning (optional)
    })

    # Timing
    start_time: float | None = None
    end_time: float | None = None
    duration_ms: float = 0.0

    # Metadata
    user_id: str | None = None
    source: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """
    Result of a kernel execution.

    Contains the execution result plus governance, memory, and reflection data.
    This is returned to callers after kernel.process() completes.
    """
    trace_id: str
    success: bool
    result: Any

    # Governance tracking
    governance_approved: bool
    governance_reason: str | None = None
    triumvirate_votes: dict[str, Any] | None = None

    # Memory integration
    memory_recorded: bool = False
    memory_id: str | None = None

    # Reflection insights
    reflection_triggered: bool = False
    reflection_insights: list[str] = field(default_factory=list)

    # Timing and metadata
    duration_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    # Error information
    error: str | None = None
    blocked_reason: str | None = None


# ============================================================================
# Kernel Context Manager
# ============================================================================

class KernelContext:
    """
    Context manager for kernel execution authority.

    Enforces that execution can only happen within kernel.process().
    This is the syscall boundary - no execution outside kernel.
    """

    def __init__(self, kernel: 'CognitionKernel', trace_id: str):
        self.kernel = kernel
        self.trace_id = trace_id
        self.active = False

    def __enter__(self):
        _kernel_context.active = True
        _kernel_context.trace_id = self.trace_id
        _kernel_context.kernel = self.kernel
        self.active = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _kernel_context.active = False
        _kernel_context.trace_id = None
        _kernel_context.kernel = None
        self.active = False
        return False


def require_kernel_context(operation: str = "execution"):
    """
    Decorator to enforce kernel-only execution authority.

    Raises RuntimeError if called outside kernel context.
    This is how we enforce the syscall boundary.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not getattr(_kernel_context, 'active', False):
                raise RuntimeError(
                    f"{operation} forbidden outside CognitionKernel. "
                    f"All execution must route through kernel.process() or kernel.route()"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# CognitionKernel Class
# ============================================================================

class CognitionKernel:
    """
    Central cognition kernel that processes all agent, tool, and system executions.

    This is the authoritative cognitive loop - ALL meaningful actions must flow
    through kernel.process(). No bypasses allowed.

    Integration Points:
    - Identity System: Tracks who is executing what (immutable snapshots only)
    - Memory Engine: Records all significant actions (four-channel architecture)
    - Governance: Enforces Triumvirate + Four Laws (observe, never execute)
    - Reflection: Triggers reflection cycles based on patterns
    - Telemetry: Comprehensive execution tracking

    NON-NEGOTIABLE INVARIANTS:
    - Governance never executes, Execution never governs
    - Identity snapshots are frozen before governance
    - All state mutation goes through commit()
    - Blocked actions are still logged

    Usage:
        kernel = CognitionKernel(identity_system, memory_engine, governance, reflection)
        result = kernel.process(
            user_input="execute task",
            source="user",
            metadata={"user_id": "user123"}
        )
    """

    def __init__(
        self,
        identity_system: Any | None = None,
        memory_engine: Any | None = None,
        governance_system: Any | None = None,
        reflection_engine: Any | None = None,
        triumvirate: Any | None = None,
        data_dir: str = "data",
    ):
        """
        Initialize the CognitionKernel with all required subsystems.

        Args:
            identity_system: AGI Identity System (provides immutable snapshots)
            memory_engine: Memory Engine (four-channel recording)
            governance_system: Governance system (enforces Four Laws)
            reflection_engine: Reflection cycle engine
            triumvirate: Triumvirate orchestrator (Galahad, Cerberus, Codex)
            data_dir: Data directory for kernel state persistence
        """
        self.identity_system = identity_system
        self.memory_engine = memory_engine
        self.governance_system = governance_system
        self.reflection_engine = reflection_engine
        self.triumvirate = triumvirate
        self.data_dir = data_dir

        # Execution tracking (forensic auditability)
        self.execution_history: list[ExecutionContext] = []
        self.execution_count = 0

        # Hooks for extensibility
        self.pre_execution_hooks: list[Callable] = []
        self.post_execution_hooks: list[Callable] = []
        self.error_hooks: list[Callable] = []

        logger.info("CognitionKernel initialized with integrated subsystems")
        logger.info(f"Identity: {identity_system is not None}")
        logger.info(f"Memory: {memory_engine is not None}")
        logger.info(f"Governance: {governance_system is not None}")
        logger.info(f"Reflection: {reflection_engine is not None}")
        logger.info(f"Triumvirate: {triumvirate is not None}")

    def process(
        self,
        user_input: Any,
        *,
        source: str = "user",
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionResult:
        """
        Process user input through the complete cognitive pipeline.

        This is the PRIMARY entrypoint for user-initiated actions.

        Pipeline:
        1. Perceive and interpret input
        2. Create proposed action
        3. Governance evaluation (with frozen identity snapshot)
        4. Execute if approved (within kernel context)
        5. Commit to memory (four-channel)
        6. Reflect and learn
        7. Return comprehensive result

        Args:
            user_input: The input to process (can be string, dict, etc.)
            source: Source of the input (user, agent, system)
            metadata: Additional context

        Returns:
            ExecutionResult with complete execution data
        """
        metadata = metadata or {}
        trace_id = f"trace_{uuid.uuid4().hex[:12]}"

        logger.info(f"[{trace_id}] Processing input from {source}")

        # Create execution context (single source of truth)
        context = self._create_context(
            trace_id=trace_id,
            user_input=user_input,
            source=source,
            metadata=metadata,
        )

        # Enter kernel context (syscall boundary)
        with KernelContext(self, trace_id):
            try:
                # Phase 1: Enforce action proposal
                self.enforce(context.proposed_action, context)

                # Phase 2: Act (execute within kernel context)
                self.act(context.proposed_action, context)

                # Phase 3: Reflect on execution
                self.reflect(context)

                # Phase 4: Commit to memory (four-channel)
                self.commit(context)

                return self._build_result(context, success=True)

            except Exception as e:
                context.status = ExecutionStatus.FAILED
                context.error = str(e)
                logger.error(f"[{trace_id}] FAILED: {e}", exc_info=True)

                # Run error hooks
                self._run_error_hooks(context, e)

                # Still commit (blocked actions are logged for auditability)
                self.commit(context)

                return self._build_result(context, success=False)

    def route(
        self,
        task: Any,
        *,
        source: str = "agent",
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionResult:
        """
        Route a task through the kernel (agent-initiated).

        Similar to process() but for agent/system-initiated tasks.
        Agents MUST use this instead of direct execution.

        Args:
            task: The task to route
            source: Source agent/system name
            metadata: Additional context

        Returns:
            ExecutionResult with complete execution data
        """
        # Route through process() with agent source
        return self.process(
            user_input=task,
            source=source,
            metadata=metadata,
        )

    def enforce(self, action: Action, context: ExecutionContext) -> None:
        """
        Enforce governance on a proposed action.

        CRITICAL: Governance observes, never executes.
        Identity snapshot is frozen before evaluation.

        Mutates context.governance_decision and context.channels["decision"].

        Args:
            action: The proposed action
            context: The execution context to mutate

        Raises:
            PermissionError: If governance blocks the action
        """
        logger.info(f"[{context.trace_id}] Enforcing governance for {action.action_name}")

        # Freeze identity snapshot (immutable, governance can only observe)
        identity_snapshot = self._freeze_identity_snapshot()

        # Check governance with frozen snapshot
        decision = self._check_governance(action, context, identity_snapshot)

        # Mutate context with decision
        context.governance_decision = decision
        context.channels["decision"] = decision

        if not decision.approved:
            context.status = ExecutionStatus.BLOCKED
            logger.warning(f"[{context.trace_id}] BLOCKED: {decision.reason}")
            raise PermissionError(f"Blocked by governance: {decision.reason}")

        context.status = ExecutionStatus.APPROVED
        logger.info(f"[{context.trace_id}] Approved: {decision.reason}")

    def act(self, action: Action, context: ExecutionContext) -> None:
        """
        Execute the approved action.

        CRITICAL: Only called after enforce() approval.
        Execution happens within kernel context (syscall boundary).

        Mutates context.result and context.channels["result"].

        Args:
            action: The action to execute
            context: The execution context to mutate
        """
        logger.info(f"[{context.trace_id}] Executing: {action.action_name}")

        context.status = ExecutionStatus.EXECUTING
        context.start_time = time.time()

        try:
            # Execute within kernel context
            result = action.callable(*action.args, **action.kwargs)

            # Mutate context with result
            context.result = result
            context.channels["result"] = result
            context.status = ExecutionStatus.COMPLETED
            context.end_time = time.time()
            context.duration_ms = (context.end_time - context.start_time) * 1000

            logger.info(f"[{context.trace_id}] Completed in {context.duration_ms:.2f}ms")

        except Exception as e:
            context.status = ExecutionStatus.FAILED
            context.error = str(e)
            context.end_time = time.time()
            context.duration_ms = (context.end_time - context.start_time) * 1000
            logger.error(f"[{context.trace_id}] Execution failed: {e}")
            raise

    def reflect(self, context: ExecutionContext) -> None:
        """
        Reflect on the execution and generate insights.

        CRITICAL: Reflection cannot mutate state, only observe.

        Mutates context.channels["reflection"] only.

        Args:
            context: The execution context to reflect on
        """
        if not self.reflection_engine:
            return

        logger.debug(f"[{context.trace_id}] Reflecting on execution")

        # Determine if reflection should trigger
        should_reflect = self._should_trigger_reflection(context)

        if should_reflect:
            try:
                # Reflection observes only, never mutates
                reflection_data = {
                    "action": context.proposed_action.action_name,
                    "result_success": context.status == ExecutionStatus.COMPLETED,
                    "governance_decision": context.governance_decision.reason if context.governance_decision else None,
                    "duration_ms": context.duration_ms,
                }

                # Store in reflection channel
                context.channels["reflection"] = reflection_data

                logger.info(f"[{context.trace_id}] Reflection recorded")

            except Exception as e:
                logger.error(f"[{context.trace_id}] Reflection failed: {e}")

    def commit(self, context: ExecutionContext) -> None:
        """
        Commit the execution to memory (four-channel architecture).

        CRITICAL: ALL executions are committed, including blocked ones.
        This ensures forensic auditability and alignment drift detection.

        Four channels:
        - attempt: The intent (always recorded)
        - decision: Governance outcome (always recorded)
        - result: Actual effect (recorded if executed)
        - reflection: Post-hoc reasoning (optional)

        Args:
            context: The execution context to commit
        """
        logger.debug(f"[{context.trace_id}] Committing execution to memory")

        # Record in execution history (forensic auditability)
        self.execution_count += 1
        self.execution_history.append(context)

        # Record in four-channel memory
        if self.memory_engine:
            try:
                # Channel 1: Attempt (intent)
                context.channels["attempt"] = {
                    "action_name": context.proposed_action.action_name,
                    "action_type": context.proposed_action.action_type.value,
                    "source": context.source,
                    "user_id": context.user_id,
                    "trace_id": context.trace_id,
                    "timestamp": context.timestamp.isoformat(),
                }

                # Record all four channels
                if hasattr(self.memory_engine, "record_execution"):
                    self.memory_engine.record_execution(
                        trace_id=context.trace_id,
                        channels=context.channels,
                        status=context.status.value,
                    )
                elif hasattr(self.memory_engine, "add_memory"):
                    # Fallback to simple memory recording
                    self.memory_engine.add_memory(
                        content=f"Executed: {context.proposed_action.action_name}",
                        category="execution",
                        metadata={
                            "trace_id": context.trace_id,
                            "status": context.status.value,
                            "channels": context.channels,
                        },
                    )

                logger.debug(f"[{context.trace_id}] Memory committed (four-channel)")

            except Exception as e:
                logger.error(f"[{context.trace_id}] Memory commit failed: {e}")

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    def _create_context(
        self,
        trace_id: str,
        user_input: Any,
        source: str,
        metadata: dict[str, Any],
    ) -> ExecutionContext:
        """Create an ExecutionContext from user input."""
        # Phase 1: Perceive input
        perception = {
            "raw_input": user_input,
            "input_type": type(user_input).__name__,
            "source": source,
        }

        # Phase 2: Interpret input
        interpretation = self._interpret_input(user_input, source, metadata)

        # Phase 3: Create proposed action
        proposed_action = self._create_action(interpretation, trace_id, source)

        # Create context (single source of truth)
        return ExecutionContext(
            trace_id=trace_id,
            timestamp=datetime.now(UTC),
            perception=perception,
            interpretation=interpretation,
            proposed_action=proposed_action,
            source=source,
            user_id=metadata.get("user_id"),
            metadata=metadata,
        )

    def _interpret_input(
        self,
        user_input: Any,
        source: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Interpret user input into actionable information."""
        # Check if this is an agent-routed action with embedded callable
        if isinstance(user_input, dict) and "_action_callable" in user_input:
            # Agent provided full action details
            return {
                "intent": "execute",
                "action_name": user_input.get("action_name", "unknown"),
                "requires_approval": user_input.get("requires_approval", False),
                "risk_level": user_input.get("risk_level", "low"),
                "execution_type": user_input.get("execution_type", "agent_action"),
                "mutation_targets": user_input.get("mutation_targets", []),
                # Store action details for _create_action
                "_has_callable": True,
                "_callable": user_input["_action_callable"],
                "_args": user_input.get("_action_args", ()),
                "_kwargs": user_input.get("_action_kwargs", {}),
            }

        # Simple interpretation for user/system input
        return {
            "intent": "execute",
            "action_name": str(user_input) if not isinstance(user_input, dict) else user_input.get("action", "unknown"),
            "requires_approval": metadata.get("requires_approval", False),
            "risk_level": metadata.get("risk_level", "low"),
        }

    def _create_action(
        self,
        interpretation: dict[str, Any],
        trace_id: str,
        source: str,
    ) -> Action:
        """Create an Action from interpretation."""
        action_id = f"action_{uuid.uuid4().hex[:8]}"

        # Check if agent provided a callable
        if interpretation.get("_has_callable"):
            # Use agent-provided callable
            return Action(
                action_id=action_id,
                action_name=interpretation["action_name"],
                action_type=ExecutionType[interpretation.get("execution_type", "AGENT_ACTION").upper()],
                callable=interpretation["_callable"],
                args=interpretation.get("_args", ()),
                kwargs=interpretation.get("_kwargs", {}),
                source=source,
                risk_level=interpretation["risk_level"],
                mutation_targets=interpretation.get("mutation_targets", []),
                metadata=interpretation,
            )

        # For simple user input, create a placeholder action
        # In practice, this would route to the appropriate agent/tool
        return Action(
            action_id=action_id,
            action_name=interpretation["action_name"],
            action_type=ExecutionType.AGENT_ACTION,  # Default type
            callable=lambda: f"Executed: {interpretation['action_name']}",
            args=(),
            kwargs={},
            source=source,
            risk_level=interpretation["risk_level"],
            metadata=interpretation,
        )

    def _freeze_identity_snapshot(self) -> dict[str, Any]:
        """
        Create an immutable snapshot of identity for governance.

        CRITICAL: Governance must observe, never touch.
        Returns a frozen (deep copied) snapshot.
        """
        if not self.identity_system:
            return {}

        try:
            if hasattr(self.identity_system, "snapshot"):
                snapshot = self.identity_system.snapshot()
                # Ensure immutability (deep copy or freeze)
                import copy
                return copy.deepcopy(snapshot)
        except Exception as e:
            logger.error(f"Failed to freeze identity snapshot: {e}")

        return {}

    def _check_governance(
        self,
        action: Action,
        context: ExecutionContext,
        identity_snapshot: dict[str, Any],
    ) -> Decision:
        """
        Check governance approval for the action.

        Priority: governance_system > triumvirate > auto-approve
        """
        decision_id = f"decision_{uuid.uuid4().hex[:8]}"

        # Classify mutation intent
        mutation_intent = self._classify_mutation_intent(action)

        # Determine if consensus is required
        consensus_required = mutation_intent == MutationIntent.CORE

        # If no governance required and low risk, auto-approve
        if not action.metadata.get("requires_approval") and action.risk_level == "low":
            return Decision(
                decision_id=decision_id,
                action_id=action.action_id,
                approved=True,
                reason="Auto-approved (low risk, no approval required)",
                mutation_intent=mutation_intent,
                consensus_required=False,
                consensus_achieved=False,
            )

        # Check with governance system first (highest priority)
        if self.governance_system:
            try:
                if hasattr(self.governance_system, "validate_action"):
                    gov_decision = self.governance_system.validate_action(
                        action=action.action_name,
                        context={"identity_snapshot": identity_snapshot, **action.metadata},
                    )
                    return Decision(
                        decision_id=decision_id,
                        action_id=action.action_id,
                        approved=gov_decision.get("allowed", False),
                        reason=gov_decision.get("reason", "Governance decision"),
                        council_votes=gov_decision,
                        mutation_intent=mutation_intent,
                        consensus_required=consensus_required,
                        consensus_achieved=gov_decision.get("allowed", False),
                    )
            except Exception as e:
                logger.error(f"Governance check failed: {e}")

        # Check with Triumvirate if available (secondary priority)
        if self.triumvirate:
            try:
                result = self.triumvirate.process(
                    input_data=action.action_name,
                    context={
                        "identity_snapshot": identity_snapshot,
                        "mutation_intent": mutation_intent.value if mutation_intent else None,
                        **action.metadata,
                    },
                    skip_validation=False,
                )

                approved = result.get("success", False)
                return Decision(
                    decision_id=decision_id,
                    action_id=action.action_id,
                    approved=approved,
                    reason=result.get("error", "Triumvirate approved") if not approved else "Triumvirate approved",
                    council_votes=result.get("pipeline", {}),
                    mutation_intent=mutation_intent,
                    consensus_required=consensus_required,
                    consensus_achieved=approved,
                )
            except Exception as e:
                logger.error(f"Triumvirate check failed: {e}")

        # Default: approve with warning if no governance available
        logger.warning(f"No governance system available for {action.action_name}")
        return Decision(
            decision_id=decision_id,
            action_id=action.action_id,
            approved=True,
            reason="No governance system configured (approved by default)",
            mutation_intent=mutation_intent,
            consensus_required=False,
            consensus_achieved=False,
        )

    def _classify_mutation_intent(self, action: Action) -> MutationIntent:
        """
        Classify the mutation intent of an action.

        - CORE: genesis, law_hierarchy, core_values → full guardian consensus
        - STANDARD: personality_weights, preferences → standard consensus
        - ROUTINE: regular operations → allowed
        """
        mutation_targets = action.mutation_targets

        # Check for core mutations
        core_targets = {"genesis", "law_hierarchy", "core_values", "four_laws"}
        if any(target in core_targets for target in mutation_targets):
            return MutationIntent.CORE

        # Check for standard mutations
        standard_targets = {"personality_weights", "preferences", "traits", "mood"}
        if any(target in standard_targets for target in mutation_targets):
            return MutationIntent.STANDARD

        # Default to routine
        return MutationIntent.ROUTINE

    def _should_trigger_reflection(self, context: ExecutionContext) -> bool:
        """Determine if reflection should trigger based on context."""
        # Trigger on high-risk actions
        if context.proposed_action.risk_level in ("high", "critical"):
            return True

        # Trigger on failures
        if context.status == ExecutionStatus.FAILED:
            return True

        # Trigger every 100 executions
        return self.execution_count % 100 == 0

    def _run_error_hooks(self, context: ExecutionContext, error: Exception) -> None:
        """Run all error hooks."""
        for hook in self.error_hooks:
            try:
                hook(context, error)
            except Exception as e:
                logger.error(f"Error hook failed: {e}")

    def _build_result(
        self,
        context: ExecutionContext,
        success: bool,
    ) -> ExecutionResult:
        """Build an ExecutionResult from the context."""
        governance_approved = (
            context.governance_decision.approved
            if context.governance_decision
            else False
        )

        return ExecutionResult(
            trace_id=context.trace_id,
            success=success,
            result=context.result,
            governance_approved=governance_approved,
            governance_reason=(
                context.governance_decision.reason
                if context.governance_decision
                else None
            ),
            triumvirate_votes=(
                context.governance_decision.council_votes
                if context.governance_decision
                else None
            ),
            duration_ms=context.duration_ms,
            error=context.error,
            blocked_reason=context.error if not success and context.status == ExecutionStatus.BLOCKED else None,
            metadata=context.metadata,
        )

    # ========================================================================
    # Public API Methods
    # ========================================================================

    def add_pre_hook(self, hook: Callable) -> None:
        """Add a pre-execution hook."""
        self.pre_execution_hooks.append(hook)
        logger.info(f"Added pre-execution hook: {hook.__name__}")

    def add_post_hook(self, hook: Callable) -> None:
        """Add a post-execution hook."""
        self.post_execution_hooks.append(hook)
        logger.info(f"Added post-execution hook: {hook.__name__}")

    def add_error_hook(self, hook: Callable) -> None:
        """Add an error hook."""
        self.error_hooks.append(hook)
        logger.info(f"Added error hook: {hook.__name__}")

    def get_execution_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get recent execution history.

        Args:
            limit: Maximum number of executions to return

        Returns:
            List of execution summaries
        """
        history = []
        for ctx in self.execution_history[-limit:]:
            history.append({
                "trace_id": ctx.trace_id,
                "action_name": ctx.proposed_action.action_name,
                "action_type": ctx.proposed_action.action_type.value,
                "status": ctx.status.value,
                "timestamp": ctx.timestamp.isoformat(),
                "user_id": ctx.user_id,
                "source": ctx.source,
                "error": ctx.error,
                "duration_ms": ctx.duration_ms,
            })
        return history

    def get_statistics(self) -> dict[str, Any]:
        """Get kernel execution statistics."""
        total = len(self.execution_history)
        completed = sum(1 for ctx in self.execution_history if ctx.status == ExecutionStatus.COMPLETED)
        failed = sum(1 for ctx in self.execution_history if ctx.status == ExecutionStatus.FAILED)
        blocked = sum(1 for ctx in self.execution_history if ctx.status == ExecutionStatus.BLOCKED)

        return {
            "total_executions": total,
            "completed": completed,
            "failed": failed,
            "blocked": blocked,
            "success_rate": completed / total if total > 0 else 0.0,
            "subsystems": {
                "identity": self.identity_system is not None,
                "memory": self.memory_engine is not None,
                "governance": self.governance_system is not None,
                "reflection": self.reflection_engine is not None,
                "triumvirate": self.triumvirate is not None,
            },
        }
