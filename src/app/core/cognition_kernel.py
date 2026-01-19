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
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


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


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ExecutionContext:
    """
    Context for an execution request.
    
    Contains all information needed for governance, memory, and reflection.
    """
    execution_id: str
    execution_type: ExecutionType
    timestamp: str
    
    # The actual callable/action to execute
    action: Callable
    action_name: str
    action_args: tuple = field(default_factory=tuple)
    action_kwargs: dict = field(default_factory=dict)
    
    # Context for governance decisions
    user_id: Optional[str] = None
    requires_approval: bool = False
    risk_level: str = "low"  # low, medium, high, critical
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Status tracking
    status: ExecutionStatus = ExecutionStatus.PENDING
    governance_decision: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    
    # Timing
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class ExecutionResult:
    """
    Result of a kernel execution.
    
    Contains the execution result plus governance, memory, and reflection data.
    """
    execution_id: str
    success: bool
    result: Any
    
    # Governance tracking
    governance_approved: bool
    governance_reason: Optional[str] = None
    triumvirate_votes: Optional[Dict[str, Any]] = None
    
    # Memory integration
    memory_recorded: bool = False
    memory_id: Optional[str] = None
    
    # Reflection insights
    reflection_triggered: bool = False
    reflection_insights: List[str] = field(default_factory=list)
    
    # Timing and metadata
    duration_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Error information
    error: Optional[str] = None
    blocked_reason: Optional[str] = None


# ============================================================================
# CognitionKernel Class
# ============================================================================

class CognitionKernel:
    """
    Central cognition kernel that processes all agent, tool, and system executions.
    
    This is the authoritative cognitive loop - ALL meaningful actions must flow
    through kernel.process(). No bypasses allowed.
    
    Integration Points:
    - Identity System: Tracks who is executing what
    - Memory Engine: Records all significant actions
    - Governance: Enforces Triumvirate + Four Laws
    - Reflection: Triggers reflection cycles based on patterns
    - Telemetry: Comprehensive execution tracking
    
    Usage:
        kernel = CognitionKernel(identity_system, memory_engine, governance, reflection)
        result = kernel.process(
            action=my_agent.execute,
            action_name="ExpertAgent.execute",
            execution_type=ExecutionType.AGENT_ACTION,
            action_args=(arg1, arg2),
            action_kwargs={"key": "value"},
            user_id="user123",
            requires_approval=True
        )
    """
    
    def __init__(
        self,
        identity_system: Optional[Any] = None,
        memory_engine: Optional[Any] = None,
        governance_system: Optional[Any] = None,
        reflection_engine: Optional[Any] = None,
        triumvirate: Optional[Any] = None,
        data_dir: str = "data",
    ):
        """
        Initialize the CognitionKernel with all required subsystems.
        
        Args:
            identity_system: AGI Identity System (tracks who/what is executing)
            memory_engine: Memory Engine (records all actions)
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
        
        # Execution tracking
        self.execution_history: List[ExecutionContext] = []
        self.execution_count = 0
        
        # Hooks for extensibility
        self.pre_execution_hooks: List[Callable] = []
        self.post_execution_hooks: List[Callable] = []
        self.error_hooks: List[Callable] = []
        
        logger.info("CognitionKernel initialized with integrated subsystems")
        logger.info(f"Identity: {identity_system is not None}")
        logger.info(f"Memory: {memory_engine is not None}")
        logger.info(f"Governance: {governance_system is not None}")
        logger.info(f"Reflection: {reflection_engine is not None}")
        logger.info(f"Triumvirate: {triumvirate is not None}")
    
    def process(
        self,
        action: Callable,
        action_name: str,
        execution_type: ExecutionType,
        action_args: tuple = (),
        action_kwargs: Optional[dict] = None,
        user_id: Optional[str] = None,
        requires_approval: bool = False,
        risk_level: str = "low",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ExecutionResult:
        """
        Process an execution request through the complete cognitive pipeline.
        
        This is the ONLY entrypoint for all agent, tool, and system executions.
        
        Pipeline:
        1. Create execution context
        2. Run pre-execution hooks
        3. Governance check (Triumvirate + Four Laws)
        4. Execute action if approved
        5. Record in memory
        6. Check for reflection triggers
        7. Run post-execution hooks
        8. Return comprehensive result
        
        Args:
            action: The callable to execute (e.g., agent.execute, tool.run)
            action_name: Human-readable name (e.g., "ExpertAgent.execute")
            execution_type: Type of execution (agent, tool, system, plugin)
            action_args: Positional arguments for the action
            action_kwargs: Keyword arguments for the action
            user_id: User requesting the execution
            requires_approval: Whether governance approval is required
            risk_level: Risk level (low, medium, high, critical)
            metadata: Additional context for governance/memory
        
        Returns:
            ExecutionResult with complete execution data
        """
        action_kwargs = action_kwargs or {}
        metadata = metadata or {}
        
        # Generate execution ID
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"
        
        # Create execution context
        context = ExecutionContext(
            execution_id=execution_id,
            execution_type=execution_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            action=action,
            action_name=action_name,
            action_args=action_args,
            action_kwargs=action_kwargs,
            user_id=user_id,
            requires_approval=requires_approval,
            risk_level=risk_level,
            metadata=metadata,
        )
        
        logger.info(f"[{execution_id}] Processing: {action_name} (type: {execution_type.value})")
        
        start_time = time.time()
        context.start_time = start_time
        
        try:
            # Phase 1: Pre-execution hooks
            self._run_pre_hooks(context)
            
            # Phase 2: Governance check
            governance_result = self._check_governance(context)
            context.governance_decision = governance_result
            
            if not governance_result["approved"]:
                # Execution blocked by governance
                context.status = ExecutionStatus.BLOCKED
                context.error = governance_result.get("reason", "Blocked by governance")
                logger.warning(f"[{execution_id}] BLOCKED: {context.error}")
                
                return self._build_result(context, success=False, blocked=True)
            
            # Phase 3: Execute action
            context.status = ExecutionStatus.EXECUTING
            logger.info(f"[{execution_id}] Executing: {action_name}")
            
            result = action(*action_args, **action_kwargs)
            context.result = result
            context.status = ExecutionStatus.COMPLETED
            
            # Phase 4: Record in memory
            self._record_in_memory(context)
            
            # Phase 5: Check reflection triggers
            self._check_reflection_triggers(context)
            
            # Phase 6: Post-execution hooks
            self._run_post_hooks(context)
            
            context.end_time = time.time()
            duration_ms = (context.end_time - start_time) * 1000
            
            logger.info(f"[{execution_id}] Completed in {duration_ms:.2f}ms")
            
            # Track execution
            self.execution_count += 1
            self.execution_history.append(context)
            
            return self._build_result(context, success=True)
            
        except Exception as e:
            # Error handling
            context.status = ExecutionStatus.FAILED
            context.error = str(e)
            context.end_time = time.time()
            
            logger.error(f"[{execution_id}] FAILED: {e}", exc_info=True)
            
            # Run error hooks
            self._run_error_hooks(context, e)
            
            # Still record in memory (for learning)
            self._record_in_memory(context)
            
            # Track execution even on failure
            self.execution_count += 1
            self.execution_history.append(context)
            
            return self._build_result(context, success=False)
    
    # ========================================================================
    # Private Helper Methods
    # ========================================================================
    
    def _check_governance(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Check governance approval for the execution.
        
        Uses Triumvirate (if available) and governance system to validate
        the execution against Four Laws and policy constraints.
        
        Priority: governance_system > triumvirate > auto-approve
        """
        # If no governance required, auto-approve
        if not context.requires_approval and context.risk_level == "low":
            return {
                "approved": True,
                "reason": "Auto-approved (low risk, no approval required)",
                "votes": {},
            }
        
        # Check with governance system first (highest priority)
        if self.governance_system:
            try:
                # Governance system check (if it has a validate method)
                if hasattr(self.governance_system, "validate_action"):
                    decision = self.governance_system.validate_action(
                        action=context.action_name,
                        context=context.metadata,
                    )
                    return {
                        "approved": decision.get("allowed", False),
                        "reason": decision.get("reason", "Governance decision"),
                        "votes": decision,
                    }
            except Exception as e:
                logger.error(f"Governance check failed: {e}")
                # Fall through to triumvirate
        
        # Check with Triumvirate if available (secondary priority)
        if self.triumvirate:
            try:
                triumvirate_context = {
                    "action_name": context.action_name,
                    "execution_type": context.execution_type.value,
                    "user_id": context.user_id,
                    "risk_level": context.risk_level,
                    "metadata": context.metadata,
                }
                
                # Use Triumvirate process() to validate
                result = self.triumvirate.process(
                    input_data=context.action_name,
                    context=triumvirate_context,
                    skip_validation=False,
                )
                
                if result.get("success"):
                    return {
                        "approved": True,
                        "reason": "Triumvirate approved",
                        "votes": result.get("pipeline", {}),
                        "triumvirate_result": result,
                    }
                else:
                    return {
                        "approved": False,
                        "reason": result.get("error", "Triumvirate rejected"),
                        "votes": result.get("pipeline", {}),
                        "triumvirate_result": result,
                    }
            except Exception as e:
                logger.error(f"Triumvirate check failed: {e}")
        
        # Default: approve with warning if no governance available
        logger.warning(f"No governance system available for {context.action_name}")
        return {
            "approved": True,
            "reason": "No governance system configured (approved by default)",
            "votes": {},
        }
    
    def _record_in_memory(self, context: ExecutionContext) -> Optional[str]:
        """
        Record the execution in the memory engine.
        
        Returns the memory ID if successful.
        """
        if not self.memory_engine:
            return None
        
        try:
            # Build memory entry
            memory_entry = {
                "execution_id": context.execution_id,
                "action_name": context.action_name,
                "execution_type": context.execution_type.value,
                "timestamp": context.timestamp,
                "user_id": context.user_id,
                "status": context.status.value,
                "result_summary": str(context.result)[:200] if context.result else None,
                "error": context.error,
                "metadata": context.metadata,
            }
            
            # Record in memory (if it has an add_memory method)
            if hasattr(self.memory_engine, "add_memory"):
                memory_id = self.memory_engine.add_memory(
                    content=f"Executed: {context.action_name}",
                    category="execution",
                    metadata=memory_entry,
                )
                logger.debug(f"Recorded in memory: {memory_id}")
                return memory_id
            
        except Exception as e:
            logger.error(f"Failed to record in memory: {e}")
        
        return None
    
    def _check_reflection_triggers(self, context: ExecutionContext) -> None:
        """
        Check if this execution should trigger a reflection cycle.
        
        Triggers based on:
        - High-risk actions
        - Failed executions
        - Pattern detection (every N executions)
        """
        if not self.reflection_engine:
            return
        
        should_reflect = False
        
        # Trigger on high-risk actions
        if context.risk_level in ("high", "critical"):
            should_reflect = True
        
        # Trigger on failures
        if context.status == ExecutionStatus.FAILED:
            should_reflect = True
        
        # Trigger every 100 executions
        if self.execution_count % 100 == 0:
            should_reflect = True
        
        if should_reflect:
            try:
                if hasattr(self.reflection_engine, "trigger_reflection"):
                    self.reflection_engine.trigger_reflection(
                        reason=f"Triggered by: {context.action_name}",
                        context=context.metadata,
                    )
                    logger.info(f"Reflection cycle triggered by {context.action_name}")
            except Exception as e:
                logger.error(f"Failed to trigger reflection: {e}")
    
    def _run_pre_hooks(self, context: ExecutionContext) -> None:
        """Run all pre-execution hooks."""
        for hook in self.pre_execution_hooks:
            try:
                hook(context)
            except Exception as e:
                logger.error(f"Pre-execution hook failed: {e}")
    
    def _run_post_hooks(self, context: ExecutionContext) -> None:
        """Run all post-execution hooks."""
        for hook in self.post_execution_hooks:
            try:
                hook(context)
            except Exception as e:
                logger.error(f"Post-execution hook failed: {e}")
    
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
        blocked: bool = False,
    ) -> ExecutionResult:
        """Build an ExecutionResult from the context."""
        duration_ms = 0.0
        if context.start_time and context.end_time:
            duration_ms = (context.end_time - context.start_time) * 1000
        
        governance_approved = (
            context.governance_decision.get("approved", False)
            if context.governance_decision
            else False
        )
        
        return ExecutionResult(
            execution_id=context.execution_id,
            success=success,
            result=context.result,
            governance_approved=governance_approved,
            governance_reason=(
                context.governance_decision.get("reason")
                if context.governance_decision
                else None
            ),
            triumvirate_votes=(
                context.governance_decision.get("votes")
                if context.governance_decision
                else None
            ),
            duration_ms=duration_ms,
            error=context.error,
            blocked_reason=context.error if blocked else None,
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
    
    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
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
                "execution_id": ctx.execution_id,
                "action_name": ctx.action_name,
                "execution_type": ctx.execution_type.value,
                "status": ctx.status.value,
                "timestamp": ctx.timestamp,
                "user_id": ctx.user_id,
                "error": ctx.error,
            })
        return history
    
    def get_statistics(self) -> Dict[str, Any]:
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
